#!/usr/bin/env python3
"""verify_sites_only.py: release gate for the KOVA3 open tier.

Checks that a sites-only VCF (bgzip or plain) carries no participant-level data
and no header leakage before it is published in the open bucket.

Checks performed
  1. #CHROM header line has exactly 8 columns (no FORMAT, no sample columns).
  2. No data line has more than 8 tab-separated fields.
  3. No ##FORMAT header lines (they imply per-sample fields were intended).
  4. Header leakage: ##DRAGENCommandLine, ##bcftools_*Command and other command
     lines; local filesystem paths (/Users/, /Volumes/, /home/, /mnt/, /data/ ...);
     S3 URIs; long numeric tokens that look like sample IDs; e-mail addresses;
     hostnames; ICA/Kakao/AWS account-like identifiers.
  5. INFO keys used in the body are all declared in ##INFO headers, and the
     allow-list (if given) is respected, so that no unexpected field slips in.
  6. Optional: the set of sample IDs from --sample-list and --exclusion-list
     must not appear anywhere
     in the file (header or body). This is the authoritative check, and it runs
     over every record of every file unless --max-records is set. The ID regexes
     in LEAK_PATTERNS cover the shapes seen in the delivered cohorts
     (KOREA4K-nnnn, KOREA10K-KOBIC-nnnnn, Jeju 10- and 14-digit IDs and the
     26-character ICA barcode), but they are a safety net, not a substitute:
     always pass --sample-list with the real ID list for the release, and do not
     pass --max-records on a release run.

     --exclusion-list carries the participant IDs excluded from KOVA3 (consent
     or metadata-quality exclusions). Those IDs must not appear in either tier,
     which is what docs/cohorts.md means by the exclusion list being an input to
     the release gate. That file is never committed; see .gitignore.

Exit code 0 = PASS, 1 = FAIL (details on stderr), 2 = usage error.

Usage
  python3 verify_sites_only.py release/chr21.sites.vcf.gz
  python3 verify_sites_only.py release/*.sites.vcf.gz \
      --sample-list samples.txt --exclusion-list kova3-excluded-samples.tsv \
      --allow-info "$KOVA3_OPEN_INFO"

The published open-tier INFO allow-list (see docs/data-dictionary.md) is:

  KOVA3_OPEN_INFO=AC,AN,AF,nhomalt,call_rate,NS,NS_GT,NS_NOGT,NS_NODATA,\
AC_jeju,AN_jeju,AF_jeju,nhomalt_jeju,IC,HWE,HWEc2,ExcHet

Passing it is what catches a batch-level field or any other unexpected INFO key
that survived export, because anything outside the list fails the run.

--max-records N limits body scanning to the first N records (0 = all; default all).
Use it for a quick smoke test only. A release run must scan every record, so leave
it at the default; a capped run is not a release gate.
Only the standard library is used; gzip/bgzip input is handled transparently.
"""
import argparse
import gzip
import io
import re
import sys

LEAK_PATTERNS = {
    "command line header": re.compile(r"^##(DRAGEN\w*CommandLine|.*[Cc]ommand(Line)?=|bcftools_\w+Command|GATKCommandLine|source=.*\s-)", re.I),
    "local filesystem path": re.compile(r"(/Users/|/Volumes/|/home/|/mnt/|/data/|/scratch/|/tmp/|/opt/|/gpfs/|/lustre/|[A-Z]:\\\\)"),
    "S3 or cloud URI": re.compile(r"\b(s3|gs|az|icav2|ica)://", re.I),
    "e-mail address": re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
    "hostname or IP": re.compile(r"\b(\d{1,3}\.){3}\d{1,3}\b|\b[\w-]+\.(korea\.ac\.kr|kobic\.re\.kr|amazonaws\.com|kakaoi?cloud\.com)\b", re.I),
    "AWS account-like 12-digit id": re.compile(r"(?<![\d.])\d{12}(?![\d.])"),
    # Cohort sample-ID shapes as they actually appear in the delivered inventories.
    # These are a safety net only: --sample-list is the authoritative check, and
    # a new cohort will have a shape none of these patterns knows about.
    "Korea4K sample ID": re.compile(r"\bKOREA4K-\d{2,5}\b", re.I),
    "Korea10K sample ID": re.compile(r"\bKOREA10K-KOBIC-\d{4,6}\b", re.I),
    "Jeju sample ID (bare digits)": re.compile(r"(?<![\d.])\d{10}(?![\d.])|(?<![\d.])\d{14}(?![\d.])"),
    "Jeju sample ID (ICA barcode)": re.compile(r"\b\d{11}S\d{2}B\d[A-Z0-9]{9,12}\b"),
    "ICA/UUID identifier": re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I),
}
# Patterns that legitimately fire on structural header lines (contig lengths, dates,
# INFO descriptions) and are therefore skipped for the prefixes listed below.
# Keep these names in sync with LEAK_PATTERNS; a name that no longer exists here
# silently disables the exemption.
NUMERIC_PATTERNS_EXEMPT_ON_SAFE_HEADERS = (
    "Jeju sample ID (bare digits)",
    "AWS account-like 12-digit id",
    "hostname or IP",
)
# Token shape used for the exact sample-ID membership test. Splitting the line into
# tokens and intersecting with the ID set is O(line) regardless of how many IDs
# there are; scanning the ID list per line is O(ids x lines) and does not scale to
# a whole chromosome shard.
SAMPLE_ID_TOKEN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.\-]{4,}")
# Header keys that legitimately contain numbers or paths and should not trip the ID heuristics
SAFE_HEADER_PREFIXES = ("##contig=", "##reference=", "##fileDate=", "##INFO=", "##FILTER=", "##ALT=", "##fileformat=")


def open_text(path):
    with open(path, "rb") as fh:
        magic = fh.read(2)
    if magic == b"\x1f\x8b":
        return io.TextIOWrapper(gzip.open(path, "rb"), encoding="utf-8", errors="replace")
    return open(path, "r", encoding="utf-8", errors="replace")


def split_ids(sample_ids):
    """Partition the ID set by whether SAMPLE_ID_TOKEN can produce it.

    The fast path intersects tokenized line content with a set, which is O(line)
    however many IDs there are. An ID the tokenizer can never emit (too short, or
    containing a character the token class excludes) would be silently missed by
    that path, so those fall back to a substring scan and the caller is told.
    """
    fast, slow = set(), set()
    for sid in sample_ids:
        (fast if SAMPLE_ID_TOKEN.findall(sid) == [sid] else slow).add(sid)
    return fast, slow


def scan_ids(line, fast_ids, slow_ids):
    hit = fast_ids.intersection(SAMPLE_ID_TOKEN.findall(line)) if fast_ids else set()
    if slow_ids:
        hit |= {sid for sid in slow_ids if sid in line}
    return hit


def check_file(path, sample_ids, allow_info, max_records):
    failures = []
    warnings = []
    info_declared = set()
    info_used = set()
    n_records = 0
    saw_chrom = False
    truncated = False
    fast_ids, slow_ids = split_ids(sample_ids)

    with open_text(path) as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.rstrip("\n")
            if line.startswith("##"):
                if line.startswith("##FORMAT="):
                    failures.append(f"line {lineno}: ##FORMAT header present (per-sample fields declared)")
                m = re.match(r"##INFO=<ID=([^,>]+)", line)
                if m:
                    info_declared.add(m.group(1))
                if line.startswith("##reference="):
                    # a reference path is expected; only flag if it looks like a local path
                    if LEAK_PATTERNS["local filesystem path"].search(line):
                        warnings.append(f"line {lineno}: ##reference contains a local path; replace with the public FASTA name/URL")
                    continue
                safe = line.startswith(SAFE_HEADER_PREFIXES)
                for name, pat in LEAK_PATTERNS.items():
                    if safe and name in NUMERIC_PATTERNS_EXEMPT_ON_SAFE_HEADERS:
                        continue
                    if pat.search(line):
                        failures.append(f"line {lineno}: header leakage ({name}): {line[:160]}")
                if sample_ids:
                    hit = scan_ids(line, fast_ids, slow_ids)
                    if hit:
                        failures.append(f"line {lineno}: sample ID {sorted(hit)[0]} appears in header")
                continue
            if line.startswith("#CHROM"):
                saw_chrom = True
                cols = line.split("\t")
                if len(cols) != 8:
                    failures.append(f"line {lineno}: #CHROM has {len(cols)} columns, expected 8 (found: {cols[8:12]}{'...' if len(cols) > 12 else ''})")
                continue
            if not line:
                continue
            n_records += 1
            fields = line.split("\t")
            if len(fields) != 8:
                failures.append(f"line {lineno}: record has {len(fields)} fields, expected 8")
            info = fields[7] if len(fields) >= 8 else ""
            for kv in info.split(";"):
                if kv and kv != ".":
                    info_used.add(kv.split("=", 1)[0])
            # Every record is checked against the sample list, with no record cap:
            # this is the authoritative privacy check and a partial scan would give
            # a false assurance.
            if sample_ids:
                hit = scan_ids(line, fast_ids, slow_ids)
                if hit:
                    failures.append(f"line {lineno}: sample ID {sorted(hit)[0]} appears in a record")
            if len(failures) > 50:
                failures.append("... too many failures, stopping body scan")
                truncated = True
                break
            if max_records and n_records >= max_records:
                break

    if not saw_chrom:
        failures.append("no #CHROM header line found")
    undeclared = info_used - info_declared
    if undeclared:
        failures.append(f"INFO keys used but not declared in header: {sorted(undeclared)}")
    if allow_info is not None:
        not_allowed = info_used - allow_info
        if not_allowed:
            failures.append(f"INFO keys not on the allow-list: {sorted(not_allowed)}")
        unused = allow_info - info_used
        if unused and not truncated and not max_records:
            warnings.append(f"allow-listed INFO keys never used in scanned records: {sorted(unused)}")
    return failures, warnings, n_records, sorted(info_used)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("vcf", nargs="+", help="sites-only VCF file(s), plain or bgzip/gzip")
    ap.add_argument("--sample-list", help="text file with one sample ID per line; none may appear in the output")
    ap.add_argument("--exclusion-list",
                    help="text file of participant IDs excluded from the release (one per line, "
                         "or TSV with the ID in the first column). Merged into --sample-list: these "
                         "must never appear in either tier. See docs/cohorts.md.")
    ap.add_argument("--allow-info", help="comma-separated INFO keys permitted in the open tier")
    ap.add_argument("--max-records", type=int, default=0, help="scan at most N records per file (0 = all)")
    args = ap.parse_args()

    def read_ids(path, first_column=False):
        ids = set()
        with open(path) as fh:
            for raw in fh:
                raw = raw.strip()
                if not raw or raw.startswith("#"):
                    continue
                ids.add(raw.split("\t", 1)[0].strip() if first_column else raw)
        if not ids:
            print(f"{path} contains no sample IDs", file=sys.stderr)
            sys.exit(2)
        return ids

    sample_ids = set()
    if args.sample_list:
        sample_ids |= read_ids(args.sample_list)
    if args.exclusion_list:
        excluded = read_ids(args.exclusion_list, first_column=True)
        sample_ids |= excluded
        print(f"exclusion list: {len(excluded)} participant IDs added to the scan", file=sys.stderr)

    if sample_ids:
        _, unmatchable = split_ids(sample_ids)
        if unmatchable:
            print(f"note: {len(unmatchable)} ID(s) need the slower substring scan "
                  f"(e.g. {sorted(unmatchable)[0]!r}); they are still checked", file=sys.stderr)
    else:
        print("warning: no --sample-list or --exclusion-list given; the authoritative "
              "ID check is NOT running, only the shape heuristics", file=sys.stderr)

    if args.max_records:
        print(f"warning: --max-records {args.max_records} is set; this is a smoke test, "
              "not a release gate", file=sys.stderr)
    allow_info = set(args.allow_info.split(",")) if args.allow_info else None

    overall_fail = False
    for path in args.vcf:
        failures, warnings, n, info_used = check_file(path, sample_ids, allow_info, args.max_records)
        status = "FAIL" if failures else "PASS"
        overall_fail |= bool(failures)
        print(f"[{status}] {path}: {n} records scanned; INFO keys: {','.join(info_used)}")
        for w in warnings:
            print(f"  WARN  {w}", file=sys.stderr)
        for f in failures:
            print(f"  FAIL  {f}", file=sys.stderr)
    sys.exit(1 if overall_fail else 0)


if __name__ == "__main__":
    main()

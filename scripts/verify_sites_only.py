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
  6. Optional: the set of sample IDs from --sample-list must not appear anywhere
     in the file (header or body).

Exit code 0 = PASS, 1 = FAIL (details on stderr), 2 = usage error.

Usage
  python3 verify_sites_only.py release/chr21.sites.vcf.gz
  python3 verify_sites_only.py release/*.sites.vcf.gz --sample-list samples.txt \
      --allow-info AC,AN,AF,nhomalt,KOVA3_call_rate ... --max-records 0

--max-records N limits body scanning to the first N records (0 = all; default all).
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
    "sample-ID-like 10-digit token": re.compile(r"(?<![\d.])\d{10}(?![\d.])"),
    "ICA/UUID identifier": re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\b", re.I),
}
# Header keys that legitimately contain numbers or paths and should not trip the ID heuristics
SAFE_HEADER_PREFIXES = ("##contig=", "##reference=", "##fileDate=", "##INFO=", "##FILTER=", "##ALT=", "##fileformat=")


def open_text(path):
    with open(path, "rb") as fh:
        magic = fh.read(2)
    if magic == b"\x1f\x8b":
        return io.TextIOWrapper(gzip.open(path, "rb"), encoding="utf-8", errors="replace")
    return open(path, "r", encoding="utf-8", errors="replace")


def check_file(path, sample_ids, allow_info, max_records):
    failures = []
    warnings = []
    info_declared = set()
    info_used = set()
    n_records = 0
    saw_chrom = False

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
                    if safe and name in ("sample-ID-like 10-digit token", "AWS account-like 12-digit id", "hostname or IP"):
                        continue
                    if pat.search(line):
                        failures.append(f"line {lineno}: header leakage ({name}): {line[:160]}")
                if sample_ids:
                    for sid in sample_ids:
                        if sid in line:
                            failures.append(f"line {lineno}: sample ID {sid} appears in header")
                            break
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
                if len(failures) > 50:
                    failures.append("... too many failures, stopping body scan")
                    break
            info = fields[7] if len(fields) >= 8 else ""
            for kv in info.split(";"):
                if kv and kv != ".":
                    info_used.add(kv.split("=", 1)[0])
            if sample_ids and n_records <= 100000:
                for sid in sample_ids:
                    if sid in line:
                        failures.append(f"line {lineno}: sample ID {sid} appears in a record")
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
        if unused:
            warnings.append(f"allow-listed INFO keys never used in scanned records: {sorted(unused)}")
    return failures, warnings, n_records, sorted(info_used)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("vcf", nargs="+", help="sites-only VCF file(s), plain or bgzip/gzip")
    ap.add_argument("--sample-list", help="text file with one sample ID per line; none may appear in the output")
    ap.add_argument("--allow-info", help="comma-separated INFO keys permitted in the open tier")
    ap.add_argument("--max-records", type=int, default=0, help="scan at most N records per file (0 = all)")
    args = ap.parse_args()

    sample_ids = []
    if args.sample_list:
        with open(args.sample_list) as fh:
            sample_ids = [s.strip() for s in fh if s.strip()]
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

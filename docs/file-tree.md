# File tree and release manifest

KOVA3 occupies two buckets: one for the open tier, which anyone may read, and
one for the controlled tier, which is readable only by applicants who hold an
active Data Use Agreement. Their layouts are given separately below.

## Open-tier bucket layout

```
s3://<OPEN_BUCKET>/
├── README.md                          # Points here; orientation for users arriving at the bucket
├── LICENSE                            # CC BY 4.0
├── CHANGELOG.md                       # Release history
│
├── docs/                              # Snapshot of this repository at release time
│   ├── data-owners.md
│   ├── cohorts.md
│   ├── methods.md
│   ├── data-dictionary.md
│   ├── schemas.md
│   ├── subpopulations.md
│   ├── file-tree.md
│   ├── versioning.md
│   └── data-access.md
│
├── metadata/
│   ├── release=<RELEASE>/
│   │   ├── manifest.json              # Every object, size, checksum; see below
│   │   ├── cohort_summary.tsv         # Aggregate cohort metadata
│   │   ├── cohort_summary.parquet
│   │   ├── qc_summary.tsv             # Sample and variant QC counts
│   │   └── cohort_effects/            # Residual batch-effect assessment
│   └── schemas/
│       ├── parquet_schema.json
│       ├── hail_schema.json
│       └── vcf_header.txt
│
└── data/
    └── release=<RELEASE>/
        ├── sites_vcf/
        │   ├── kova3.chr1.sites.vcf.gz
        │   ├── kova3.chr1.sites.vcf.gz.tbi
        │   ├── ...
        │   ├── kova3.chrX.sites.vcf.gz
        │   ├── kova3.chrY.sites.vcf.gz
        │   └── kova3.chrM.sites.vcf.gz
        │
        ├── parquet/
        │   └── chromosome=chr1/
        │       └── position_bin=000/
        │           └── part-00000.parquet
        │
        ├── hail/
        │   └── kova3.sites.ht/
        │
        └── callability/
            ├── kova3.allele_number.chr1.<ext>
            └── kova3.call_rate.chr1.<ext>
```

> **TODO:** replace `<OPEN_BUCKET>`, `<CONTROLLED_BUCKET>`, and `<RELEASE>`
> throughout once assigned, and settle the callability file format and extension
> see [methods.md](methods.md#callability). Confirm whether chrM is included;
> if mitochondrial variants are not called, remove that line rather than shipping
> an empty file.

---

## Controlled-tier bucket layout

Readable only with credentials issued after an application is approved. The
per-sample manifest is the entry point: read-level format varies by sample, so
resolve availability from the manifest rather than by listing the bucket.

```
s3://<CONTROLLED_BUCKET>/
├── manifest/
│   ├── samples.tsv                    # One row per sample: cohort, formats held, object keys
│   └── samples.parquet
│
├── fastq/
│   └── <COHORT>/<SAMPLE>/             # Paired-end, gzip-compressed
│       ├── <SAMPLE>_R1.fastq.gz
│       └── <SAMPLE>_R2.fastq.gz
│
├── cram/
│   └── <COHORT>/<SAMPLE>/             # CRAM 3.0 against GRCh38
│       ├── <SAMPLE>.cram
│       └── <SAMPLE>.cram.crai
│
├── gvcf/
│   └── <COHORT>/<SAMPLE>/
│       ├── <SAMPLE>.g.vcf.gz
│       └── <SAMPLE>.g.vcf.gz.tbi
│
└── msvcf/
    └── release=<RELEASE>/             # Genotyped multi-sample VCF, chromosome-sharded
        ├── kova3.chr1.vcf.gz
        ├── kova3.chr1.vcf.gz.tbi
        └── ...
```

A sample appears under `fastq/`, under `cram/`, or under both, depending on
what the contributing cohort holds. No sample is present in neither. See
[cohorts.md](cohorts.md) for the per-cohort breakdown.

---

## Naming conventions

| Element | Convention | Example |
|---|---|---|
| Release tag | `v<MAJOR>.<MINOR>.<PATCH>` | `v3.0.0` |
| Release prefix | `release=<tag>` (Hive-style) | `release=v3.0.0` |
| VCF shard | `kova3.<contig>.sites.vcf.gz` | `kova3.chr7.sites.vcf.gz` |
| Contig naming | GRCh38, `chr`-prefixed | `chr1`, `chrX` |
| Partition keys | lowercase, `key=value` | `chromosome=chr1` |

Paths are **immutable once published**. A correction produces a new release
prefix; it never rewrites an existing one. This lets downstream pipelines pin a
release path and rely on it not changing underneath them. See
[versioning.md](versioning.md).

---

## Design decisions

**Individual objects, never archives.** Files are stored as individual S3
objects rather than in `tar` or `zip` bundles, so users can retrieve exactly
the shard or partition they need.

**Chromosome sharding.** A single genome-wide sites file would be awkward to
handle and would force clients to seek through an index covering the whole
genome. Per-chromosome shards keep index sizes small and let users fetch one
chromosome.

**`.tbi` indexes only.** `.tbi` cannot address positions beyond 2^29 bases, but
the longest GRCh38 contig, chr1, is 249 Mb, well inside that limit. Publishing
`.csi` alongside would add a second index for no additional reach.

**Sites-only VCF, not BCF.** BCF is smaller than bgzip-compressed VCF when
per-sample genotype columns dominate the file. A sites-only callset has no
genotype columns, and measured on a representative shard the BCF is about 15
per cent larger than the VCF. Users who prefer BCF can convert locally with
`bcftools view -Ob`.

**Top-level `data/`, `metadata/`, `docs/` prefixes with a README at the root.**
This follows the layout recommended in the AWS Open Data onboarding handbook,
so users arriving from the Registry of Open Data find a familiar structure.

---

## Release manifest

Every release publishes `metadata/release=<RELEASE>/manifest.json` listing each
object with its size and checksum.

```json
{
  "release": "v3.0.0",
  "released": "TODO-YYYY-MM-DD",
  "reference_genome": "GRCh38",
  "n_records_contributed": 11008,
  "n_unrelated": null,
  "pipeline": {
    "joint_genotyper": "DRAGEN IGG TODO-version",
    "platform": "Illumina Connected Analytics"
  },
  "objects": [
    {
      "key": "data/release=v3.0.0/sites_vcf/kova3.chr1.sites.vcf.gz",
      "bytes": 0,
      "sha256": "TODO",
      "content_type": "application/gzip"
    }
  ]
}
```

> **TODO:** generate the manifest programmatically at export time rather than
> maintaining it by hand, and fill `n_unrelated` from the QC output.

### Verifying an object

```bash
# Every object carries a published SHA-256 checksum. Verify after download.
aws s3 cp --no-sign-request \
  s3://<OPEN_BUCKET>/data/release=<RELEASE>/sites_vcf/kova3.chr1.sites.vcf.gz .

sha256sum kova3.chr1.sites.vcf.gz
# Compare against the sha256 field for this key in manifest.json.
```

### Listing a release without downloading

```bash
# No AWS account or credentials are required.
aws s3 ls --no-sign-request \
  s3://<OPEN_BUCKET>/data/release=<RELEASE>/sites_vcf/
```

# File tree and release manifest

## Bucket layout

```
s3://<BUCKET>/
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
│   └── versioning.md
│
├── metadata/
│   ├── release=<RELEASE>/
│   │   ├── manifest.json              # Every object, size, checksum — see below
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
        │   ├── kova3.chr1.sites.vcf.gz.csi
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

> **TODO:** replace `<BUCKET>` and `<RELEASE>` throughout once assigned, and
> settle the callability file format and extension — see
> [methods.md](methods.md#callability). Confirm whether chrM is included; if
> mitochondrial variants are not called, remove that line rather than shipping
> an empty file.

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

**Both `.tbi` and `.csi` indexes.** `.tbi` is universally supported but cannot
address positions beyond 2^29; `.csi` handles longer contigs. Publishing both
avoids forcing a choice on users.

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
  s3://<BUCKET>/data/release=<RELEASE>/sites_vcf/kova3.chr1.sites.vcf.gz .

sha256sum kova3.chr1.sites.vcf.gz
# Compare against the sha256 field for this key in manifest.json.
```

### Listing a release without downloading

```bash
# No AWS account or credentials are required.
aws s3 ls --no-sign-request \
  s3://<BUCKET>/data/release=<RELEASE>/sites_vcf/
```

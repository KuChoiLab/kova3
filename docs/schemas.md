# Schemas

The same variant records are published in three representations. Field names
and semantics match across all three; see
[data-dictionary.md](data-dictionary.md) for definitions.

| Representation | Best for |
|---|---|
| Sites-only VCF | Interval queries with existing genomics tooling |
| Apache Parquet | SQL queries over the whole callset (Athena, Spark, Glow) |
| Hail Table | Genome-wide analysis in Hail without an import step |

Machine-readable schema files are published under `metadata/schemas/` in the
release bucket; see [file-tree.md](file-tree.md).

---

## Parquet schema

### Partitioning

Hive-style partition keys, so query engines can skip irrelevant data:

```
parquet/
  chromosome=chr1/
    position_bin=000/
      part-00000.parquet
    position_bin=001/
      ...
  chromosome=chr2/
    ...
```

`position_bin` groups positions into fixed-width blocks, so a query restricted
to a gene reads only the blocks overlapping it. Combined with column pruning,
a gene-panel lookup touches a small fraction of the dataset.

`position_bin` is **10 Mb wide**: `position_bin = floor(POS / 10_000_000)`,
written zero-padded to three digits. The longest contig, `chr1`, therefore ends
at `position_bin=024`, and the whole genome comes to roughly 310 partitions.

| Property | Value |
|---|---|
| Bin width | 10 Mb |
| Partition key format | `position_bin=NNN`, zero-padded to 3 digits |
| Partitions, whole genome | about 310 |
| Rows per partition | roughly 300,000 to 400,000 |
| Target file size | 20 to 40 MB |
| Parquet row group | 64 MB |
| Compression | ZSTD |

The width is a compromise between two access patterns. A single gene is under
2 Mb, so a gene query reads one partition or two; a wider bin would make it
scan tens of megabytes for one locus. A narrower bin would push the partition
count and the per-file overhead up without helping, since Athena already prunes
to the bins it needs. ZSTD is read by Athena, Spark, Hail, polars, pyarrow and
DuckDB, and is about a quarter smaller than Snappy on this data.

### Columns

Column names are the lowercased VCF field names, so the Parquet layer stays
aligned with the sites-only VCF. See
[data-dictionary.md](data-dictionary.md) for full definitions.

| Column | Parquet type | Nullable | Description |
|---|---|---|---|
| `chromosome` | STRING | no | Partition key. GRCh38 contig, `chr`-prefixed |
| `position_bin` | INT32 | no | Partition key. Position block index |
| `pos` | INT32 | no | 1-based position |
| `ref` | STRING | no | Reference allele |
| `alt` | STRING | no | Alternate allele, one per row |
| `variant_id` | STRING | no | `chrom-pos-ref-alt`, stable across releases |
| `rsid` | STRING | yes | **Reserved, always null in this release.** dbSNP rsIDs are not assigned; see [data-dictionary.md](data-dictionary.md#fixed-columns) |
| `qual` | FLOAT | yes | Site quality |
| `filter` | LIST\<STRING\> | no | Filter values; `["PASS"]` when passing |
| `ac` | INT32 | no | Cohort alternate allele count |
| `an` | INT32 | no | Cohort called allele number |
| `af` | DOUBLE | no | Cohort alternate allele frequency |
| `ns` | INT32 | no | Samples in the cohort |
| `ns_gt` | INT32 | no | Samples with a called genotype |
| `ns_nogt` | INT32 | no | Samples with no called genotype |
| `ns_nodata` | INT32 | no | Samples with no coverage |
| `nhomalt` | INT32 | no | Homozygous alternate individuals (derived) |
| `call_rate` | FLOAT | no | Call rate (derived) |
| `ic` | FLOAT | yes | Inbreeding coefficient |
| `hwec2` | FLOAT | yes | Hardy-Weinberg P-value, site-wise |
| `hwe` | FLOAT | yes | Hardy-Weinberg P-value, allele-wise |
| `exchet` | FLOAT | yes | Excess heterozygosity P-value |
| `ac_jeju` | INT32 | yes | Alternate allele count, Jeju stratum |
| `an_jeju` | INT32 | yes | Called allele number, Jeju stratum |
| `af_jeju` | DOUBLE | yes | Alternate allele frequency, Jeju stratum |
| `nhomalt_jeju` | INT32 | yes | Homozygous alternate individuals, Jeju stratum |

Quality-control columns are nullable because DRAGEN omits these fields at sites
where they cannot be computed. A null means not calculable, not zero.

> **TODO:** enumerate the stratified columns explicitly once
> [subpopulations.md](subpopulations.md) is finalized, and add the quality
> annotation columns carried over from the VCF `INFO` fields. The Parquet
> schema must match the data dictionary exactly.

### Example Athena query

```sql
-- Korean allele frequencies for a gene interval.
-- Partition pruning limits the scan to the blocks overlapping the region.
SELECT variant_id, ref, alt, ac, an, af, nhomalt
FROM kova3.sites_v3_0_0
WHERE chromosome = 'chr17'
  AND pos BETWEEN 43044295 AND 43125364
  AND af < 0.01
  AND an > 15000          -- require adequate power before trusting a low frequency
                          -- 11,000 samples means an <= 22000 on the autosomes,
                          -- so 15000 is a call rate of about 0.68
ORDER BY pos;
```

```sql
-- Look up a specific variant list. Restricting the columns selected keeps
-- bytes scanned low, since Parquet reads only the requested columns.
SELECT variant_id, af, an
FROM kova3.sites_v3_0_0
WHERE variant_id IN ('chr17-43093464-A-G', 'chr13-32340301-G-A');
```

### Registering the table

The statement below is published at
`metadata/schemas/athena_create_table.sql` in the release bucket. It uses
**partition projection**, so there is no Glue crawler to run and no
`MSCK REPAIR TABLE` after a release: Athena derives the partition paths from
the rules in `TBLPROPERTIES`. Run it once in your own AWS account. The table
definition and the query charges stay in your account; the data stays in the
public bucket.

```sql
CREATE EXTERNAL TABLE IF NOT EXISTS kova3.sites_v3_0_0 (
  pos          int,
  ref          string,
  alt          string,
  variant_id   string,
  rsid         string,
  qual         float,
  filter       array<string>,
  ac           int,
  an           int,
  af           double,
  ns           int,
  ns_gt        int,
  ns_nogt      int,
  ns_nodata    int,
  nhomalt      int,
  call_rate    float,
  ic           float,
  hwec2        float,
  hwe          float,
  exchet       float,
  ac_jeju      int,
  an_jeju      int,
  af_jeju      double,
  nhomalt_jeju int
)
PARTITIONED BY (chromosome string, position_bin int)
STORED AS PARQUET
LOCATION 's3://kova3-open/data/release=v3.0.0/parquet/'
TBLPROPERTIES (
  'projection.enabled'             = 'true',
  'projection.chromosome.type'     = 'enum',
  'projection.chromosome.values'   = 'chr1,chr2,chr3,chr4,chr5,chr6,chr7,chr8,chr9,chr10,chr11,chr12,chr13,chr14,chr15,chr16,chr17,chr18,chr19,chr20,chr21,chr22,chrX,chrY,chrM',
  'projection.position_bin.type'   = 'integer',
  'projection.position_bin.range'  = '0,24',
  'projection.position_bin.digits' = '3',
  'storage.location.template'      = 's3://kova3-open/data/release=v3.0.0/parquet/chromosome=${chromosome}/position_bin=${position_bin}/'
);
```

Each release publishes its own statement with the release tag substituted, so
two releases can be registered side by side as separate tables.

---

## Hail Table schema

Keyed by locus and alleles, matching Hail's standard variant key so the table
joins directly against a user's own `MatrixTable` or `Table`.

The `rsid` field is present for schema stability but is null throughout this
release: KOVA3 does not assign dbSNP identifiers. The same holds for the
`rsid` column in the Parquet layer and in the Athena table definition.

```
----------------------------------------
Global fields:
    'kova3_release': str
    'reference_genome': str
    'n_records_contributed': int32
    'n_unrelated': int32
----------------------------------------
Row fields:
    'locus': locus<GRCh38>
    'alleles': array<str>
    'rsid': str
    'qual': float64
    'filters': set<str>
    'info': struct {
        AC: int32,
        AN: int32,
        AF: float64,
        NS: int32,
        NS_GT: int32,
        NS_NOGT: int32,
        NS_NODATA: int32,
        IC: float64,
        HWEc2: float64,
        HWE: float64,
        ExcHet: float64,
        nhomalt: int32,
        call_rate: float64,
        AC_jeju: int32,
        AN_jeju: int32,
        AF_jeju: float64,
        nhomalt_jeju: int32
    }
----------------------------------------
Key: ['locus', 'alleles']
----------------------------------------
```

> **TODO:** extend the `info` struct with the subpopulation-stratified fields
> and the retained quality annotations, then regenerate this block from the
> actual table with `ht.describe()` rather than maintaining it by hand.

### Example Hail usage

```python
import hail as hl

# The table is prebuilt and partitioned; no import step is required.
kova3 = hl.read_table("s3://kova3-open/data/release=v3.0.0/hail/kova3.sites.ht")

# Annotate your own dataset with Korean allele frequencies.
mt = mt.annotate_rows(kova3=kova3[mt.row_key].info)

# Filter to variants rare in Koreans, keeping sites with adequate power.
# AF is the cohort-wide frequency; AN is its denominator.
mt = mt.filter_rows(
    hl.is_missing(mt.kova3.AF)
    | ((mt.kova3.AF < 0.001) & (mt.kova3.AN > 15000))
)
```

The `AN` condition matters: a missing or zero frequency at a poorly covered
site is not evidence of rarity. With 11,000 samples `AN` is at most 22,000 on
the autosomes, so the threshold above corresponds to a call rate of roughly
0.68; choose your own according to how much power your analysis needs. See
[data-dictionary.md](data-dictionary.md#core-frequency-fields).

### Hail version

The Hail Table on-disk format is version-sensitive, and a table written by a
newer Hail is not guaranteed to be readable by an older one. Each release
therefore records the exact Hail version it was written with in three places:
the `hail_version` global field of the table itself, the `pipeline` block of
`manifest.json`, and this document. That version is the **minimum** required to
read the table.

Users on an older Hail, or not using Hail at all, lose nothing: the same
callset is published as a sites-only VCF and as Parquet, both of which Hail
can import directly.

> **TODO:** fill in the version at first release.

---

## Schema versioning

Schema changes follow the release policy in
[versioning.md](versioning.md). Adding a field is a minor change; renaming,
removing, or changing the type or meaning of an existing field is a major
change and will not occur within a major version.

Each release publishes its schema as JSON/YAML under `metadata/schemas/`, so
consumers can validate programmatically rather than parsing this document.

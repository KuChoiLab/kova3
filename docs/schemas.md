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

> **TODO:** state the `position_bin` width (for example 10 Mb) and confirm the
> resulting partition count is reasonable. Too many small partitions degrade
> Athena performance. Also confirm target Parquet row-group and file sizes.

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
| `rsid` | STRING | yes | dbSNP identifier where assigned |
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

> **TODO:** publish the Athena `CREATE EXTERNAL TABLE` statement, or an AWS
> Glue crawler configuration, so users can register the table in one step.

---

## Hail Table schema

Keyed by locus and alleles, matching Hail's standard variant key so the table
joins directly against a user's own `MatrixTable` or `Table`.

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

> **TODO:** record the Hail version the table was written with. Hail Table
> format compatibility is version-sensitive, and users need to know the
> minimum version required to read it.

---

## Schema versioning

Schema changes follow the release policy in
[versioning.md](versioning.md). Adding a field is a minor change; renaming,
removing, or changing the type or meaning of an existing field is a major
change and will not occur within a major version.

Each release publishes its schema as JSON/YAML under `metadata/schemas/`, so
consumers can validate programmatically rather than parsing this document.

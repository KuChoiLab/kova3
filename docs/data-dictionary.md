# Data dictionary

Every field published in the KOVA3 sites-only VCF, with its VCF header type and
definition. The Parquet and Hail representations carry the same fields under the
same names; see [schemas.md](schemas.md).

---

## Field naming convention

KOVA3 publishes fields under **the names the DRAGEN iterative gVCF Genotyper
(iGG) emits**, unchanged, so that a user familiar with a DRAGEN callset finds
what they expect and so the published files can be checked directly against the
joint genotyping output.

Two conventions from iGG carry through to KOVA3 and are worth understanding
before reading the tables below.

**The `G` prefix means global.** iGG writes each metric twice: once for the
current processing batch, and once for the whole cohort, with the cohort-wide
name prefixed by `G`. KOVA3 aggregates every contributing cohort into one
callset, so **the `G`-prefixed fields are the ones users want**. `GAF` is the
Korean allele frequency; `AF` is a per-batch artefact of how the callset was
assembled and carries no population meaning.

**Missing fields are omitted, not zero-filled.** iGG drops an INFO field from a
record entirely when its value is missing at that site, so different records can
carry different sets of fields. A parser must treat an absent field as missing
rather than assuming it is present on every line.

Fields KOVA3 computes itself, because iGG does not emit them, are marked
**derived** and named with a `KOVA3_` prefix so they cannot collide with any
DRAGEN field.

> **TODO, before launch.** The field list below is taken from the DRAGEN v4.4
> iGG documentation. Confirm it against the header of the produced callset,
> since the emitted set depends on the DRAGEN version and on the
> `--gg-msvcf-info-fields` value used:
>
> ```bash
> # Enumerate every INFO field actually present in the produced VCF.
> bcftools view -h kova3.chr1.sites.vcf.gz \
>   | grep '^##INFO' \
>   | sed 's/^##INFO=<//; s/>$//'
> ```
>
> **Note that `AF` is not in the iGG default INFO set.** It must be requested
> explicitly via `--gg-msvcf-info-fields`, or with `=All`. A run left at the
> default produces a callset with no allele frequency field at all.

Source: [DRAGEN v4.4 Population Genotyping](https://help.dragen.illumina.com/dragen-v4.4/product-guide/dragen-v4.4/dragen-dna-pipeline/iterative-gvcf-genotyper.md)

---

## Fixed columns

| Column | Description |
|---|---|
| `CHROM` | Chromosome, GRCh38, `chr`-prefixed contig naming |
| `POS` | 1-based position of the first reference base |
| `ID` | Variant identifier. `.` unless a dbSNP rsID is assigned; see note below |
| `REF` | Reference allele |
| `ALT` | Alternate allele |
| `QUAL` | Site quality. iGG reports the maximum input QUAL across the cohort at this site |
| `FILTER` | Filter status; see [FILTER values](#filter-values) |

> **TODO:** confirm whether dbSNP rsIDs are assigned in `ID`, and if so, state
> the dbSNP build used.

---

## Core frequency fields

These are the fields most users will consume. All are cohort-wide.

| Field | Number | Type | Description |
|---|---|---|---|
| `GAC` | A | Integer | Alternate allele count across the whole cohort |
| `GAN` | 1 | Integer | Total called alleles at this site across the whole cohort. The denominator for `GAF` |
| `GAF` | A | Float | Alternate allele frequency across the whole cohort |
| `GNS` | 1 | Integer | Number of samples in the cohort |
| `GNS_GT` | 1 | Integer | Number of samples with a called genotype at this site |
| `GNS_NOGT` | 1 | Integer | Number of samples with no called genotype at this site |
| `GNS_NODATA` | 1 | Integer | Number of samples with no coverage at this site |
| `KOVA3_HOMALT` | A | Integer | **Derived.** Number of individuals homozygous for the alternate allele |
| `KOVA3_CR` | 1 | Float | **Derived.** Call rate, `GNS_GT / GNS`, 0–1 |

**Interpreting `GAN`.** `GAF` alone is not sufficient for variant
classification. A site with `GAF = 0` and `GAN = 21,000` is well-powered
evidence of absence in Koreans; a site with `GAF = 0` and `GAN = 400` is not.
Always read `GAN` alongside `GAF`, and consult the callability resources
described in [methods.md](methods.md#callability) for regions absent from the
callset entirely.

**`GNS_NOGT` versus `GNS_NODATA`.** These distinguish two different reasons a
sample contributes no genotype: the site was covered but not confidently
genotyped, or it had no coverage at all. Users assessing whether a region is
interpretable should look at both.

**Chromosome X and Y.** Allele numbers on the sex chromosomes reflect ploidy, so
`GAN` in non-pseudoautosomal regions is not simply twice the sample count.

> **TODO:** document the ploidy model used for chrX, chrY, and the
> pseudoautosomal regions, state whether `--gg-diploidify` was applied, and
> confirm whether `GAF` on the sex chromosomes is computed against a sex-aware
> denominator.

### Batch-level counterparts

iGG also writes unprefixed `AC`, `AN`, `AF`, `NS`, `NS_GT`, `NS_NOGT`, and
`NS_NODATA` for the processing batch that produced each record.

> **TODO:** decide whether to retain the unprefixed batch fields in the public
> release. Recommendation: **drop them.** They reflect how the callset was
> sharded during processing, carry no population meaning, and are a predictable
> source of user error: someone will filter on `AF` thinking it is the Korean
> frequency. If they are retained, this section must say so prominently.

---

## Cohort quality-control fields

Metrics for assessing whether a site is well called. These are computed only at
diploid sites, and are missing where they cannot be calculated, for example
where only one allele is present, or where no sample is genotyped.

| Field | Number | Type | Description |
|---|---|---|---|
| `GIC` | 1 | Float | Inbreeding coefficient, site-wise. Range −1 to 1. Values near 0 are consistent with Hardy–Weinberg equilibrium; negative values indicate excess heterozygosity, which often signals poor calling |
| `GHWEc2` | 1 | Float | Hardy–Weinberg equilibrium P-value, site-wise, from a chi-squared test |
| `GHWE` | A | Float | Hardy–Weinberg equilibrium P-value, per alternate allele, from an exact conditional test |
| `GExcHet` | A | Float | Excess heterozygosity P-value, per alternate allele. Around 0.5 is expected; near 1 indicates more heterozygotes than expected, near 0 fewer |

These statistics are unstable for small cohorts and low-frequency alleles, and
are affected by population structure and by any consanguinity in the cohort.
KOVA3 aggregates several regionally distinct cohorts, so a deviation from
Hardy–Weinberg equilibrium at a given site may reflect genuine structure rather
than a calling error. Read them alongside the cohort-effect assessment described
in [methods.md](methods.md#residual-cohort-effect-assessment).

---

## Allelic balance fields

Site-wise read-support balance, computed across all samples. One value per
allele, **including the reference allele**. A value of −1 codes missing, for
example where an allele has no homozygous calls.

| Field | Number | Type | Description |
|---|---|---|---|
| `GABHom` | R | Float | Allelic balance among homozygous genotypes. Expected near 1 |
| `GABHet` | R | Float | Allelic balance among heterozygous genotypes. Expected near 0.5 |
| `GABHetP` | R | Float | Binomial test P-value for `GABHet` against an expected probability of 0.5. Near 1 matches expectation; near 0 deviates |

These fields are only produced if allelic depth was imported during aggregation.

> **TODO:** confirm whether allelic depth was imported in the KOVA3 run. If it
> was not, remove this section, since the fields will be absent from the output.

---

## Subpopulation-stratified fields

Frequencies stratified by the subpopulations defined in
[subpopulations.md](subpopulations.md). These are **derived**: iGG computes
global and batch statistics, not arbitrary user-defined strata, so KOVA3
computes them from the callset before genotypes are dropped.

| Field | Number | Type | Description |
|---|---|---|---|
| `KOVA3_AC_jeju` | A | Integer | Alternate allele count within the Jeju stratum |
| `KOVA3_AN_jeju` | 1 | Integer | Called alleles within the Jeju stratum |
| `KOVA3_AF_jeju` | A | Float | Alternate allele frequency within the Jeju stratum |
| `KOVA3_HOMALT_jeju` | A | Integer | Homozygous alternate individuals within the Jeju stratum |

The whole-cohort figures are the `G`-prefixed fields above; there is no separate
`_all` suffix. See [subpopulations.md](subpopulations.md) for what the Jeju
stratum is and when to use it.

> **TODO:** confirm the minimum stratum size policy and whether these fields are
> suppressed at very rare variants; see
> [subpopulations.md](subpopulations.md#minimum-stratum-size).

---

## Deriving the KOVA3 fields

The `KOVA3_`-prefixed fields do not come from iGG and must be computed while
per-sample genotypes are still present. This matters for pipeline ordering: iGG
can emit a sites-only callset directly via `--gg-drop-genotypes`, but doing so
too early discards the information the homozygote counts and stratified
frequencies are computed from.

The required order is:

1. Run iGG to produce the full msVCF **with** genotypes
2. Compute `KOVA3_HOMALT`, `KOVA3_CR`, and the stratified fields from it
3. Drop genotypes and publish the sites-only layer with those fields annotated

> **TODO:** publish the exact commands used for step 2 so the derived fields are
> reproducible.

---

## FILTER values

| Value | Description |
|---|---|
| `PASS` | Site passed all filters |

iGG applies hard filters to global metrics (`QUAL`, `GNS_GT`, `GIC`, `GHWEc2`,
and `GABHetP` are the available filtering criteria. Filtering is per-site, so
SNVs and indels cannot be filtered separately as they can in the variant caller.

> **TODO:** enumerate every non-`PASS` `FILTER` value present in the export with
> its definition and the threshold applied, and state in
> [methods.md](methods.md#variant-level-filtering) whether failing sites are
> retained or removed. If they are removed, say so here too, so users understand
> that absence from the file does not imply absence from the cohort.

---

## Variant representation conventions

- Indels are left-aligned and normalized against the GRCh38 reference
- Variant classes included: single-nucleotide variants and short insertions and
  deletions

> **TODO:** confirm and document:
>
> - whether multi-allelic sites are split into one record per alternate allele,
>   and with what command. This matters more than usual here: several fields
>   above are `Number=A` or `Number=R`, so splitting must carry the right
>   element to each record
> - the normalization tool and command used (for example
>   `bcftools norm -m -any -f <ref>`)
> - any upper size limit on indels
> - that structural variants, copy-number variants, and short tandem repeats are
>   **not** included in this release

---

## What is not present

The published files contain **no** per-sample genotype columns, no sample
identifiers, and no participant-level annotations. A sites-only VCF has no
`FORMAT` column and no sample columns; tools expecting them will see a cohort of
zero samples.

In particular, none of the iGG per-sample fields (`GT`, `GQ`, `LAD`, `LPL`,
`LAA`, `FT`, and the other localized genotype metrics) appear in the public
release. They exist only in the internal callset.

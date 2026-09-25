# Data dictionary

Every field published in the KOVA3 sites-only VCF, with its VCF header type and
definition. The Parquet and Hail representations carry the same fields under the
same names; see [schemas.md](schemas.md).

---

## Field naming convention

KOVA3 publishes its frequency fields under **the names used across the
population-genomics community**: `AC`, `AN`, `AF`, `nhomalt`, and, for a
stratum, `AC_<stratum>`. A pipeline written against gnomAD, 1000 Genomes or any
other frequency resource reads a KOVA3 file without modification.

Most of these names come straight out of the joint genotyping run, because of
how that run is configured. Three points follow, and they matter when reading
the tables below.

**One set of cohort-wide values, with no batch duplicates.** The DRAGEN
iterative gVCF Genotyper (iGG) can write a frequency metric twice, once for the
processing batch that produced a record and once for the whole cohort. KOVA3
runs it with `--merge-batches true`, which merges the batches before the
statistics are written, so only cohort-wide values exist and they carry the
plain, unprefixed names. The `AC`, `AN`, `NS`, `NS_GT`, `NS_NOGT` and
`NS_NODATA` in a published file are therefore unambiguous: they are always the
whole-cohort values across all 10,988 genomes. The release gate
[`scripts/verify_sites_only.py`](../scripts/verify_sites_only.py) fails the
release if any INFO key outside the published allow-list appears in the output,
which is what would catch a batch-level field surviving export.

**`AF` is computed by KOVA3, not by iGG.** `AF` is not in the iGG default INFO
set, so the joint genotyping output carries `AC` and `AN` but no allele
frequency field at all. KOVA3 derives `AF` from them, alongside `nhomalt`,
`call_rate` and the Jeju stratum fields.

**Missing fields are omitted, not zero-filled.** iGG drops an INFO field from a
record entirely when its value is missing at that site, so different records can
carry different sets of fields. A parser must treat an absent field as missing
rather than assuming it is present on every line.

### What the run emits, and what KOVA3 publishes

| Source | Field | Published as |
|---|---|---|
| iGG | `AC`, `AN` | unchanged |
| iGG | `NS`, `NS_GT`, `NS_NOGT`, `NS_NODATA` | unchanged |
| iGG | `IC`, `HWE`, `HWEc2`, `ExcHet` | unchanged. DRAGEN-specific quality statistics with no community equivalent, so they keep their source names and can be checked against the DRAGEN documentation |
| derived by KOVA3 | `AF` | `AC / AN` |
| derived by KOVA3 | `nhomalt` | Homozygous-alternate individual count |
| derived by KOVA3 | `call_rate` | `NS_GT / NS` |
| derived by KOVA3 | `AC_jeju`, `AN_jeju`, `AF_jeju`, `nhomalt_jeju` | Jeju stratum; see [subpopulations.md](subpopulations.md) |

The per-sample `FORMAT` fields that iGG writes into the multi-sample VCF
(`GT`, `GQ`, `AD`, `FT`, `LPL`, `LAA`, `LAF`, `QL`) are dropped when the
sites-only layer is exported. They remain in the controlled-tier multi-sample
VCF; see [What is not present](#what-is-not-present).

### Rename when annotating another VCF

Standard names are the right choice inside a KOVA3 file, but they collide the
moment you annotate a VCF that has its own. A patient or cohort VCF almost
always carries `AC`, `AN` and `AF` describing that cohort, and

```bash
bcftools annotate -a kova3.chr17.sites.vcf.gz -c INFO/AC,INFO/AN,INFO/AF patient.vcf.gz
```

**overwrites them**, silently replacing your own allele counts with Korean ones.
Rename on the way in instead:

```bash
bcftools annotate -a kova3.chr17.sites.vcf.gz \
  -c 'INFO/KOVA3_AC:=INFO/AC,INFO/KOVA3_AN:=INFO/AN,INFO/KOVA3_AF:=INFO/AF,INFO/KOVA3_nhomalt:=INFO/nhomalt' \
  patient.vcf.gz
```

The same applies to any other frequency resource you annotate alongside KOVA3:
give each one a prefix, or the last one written wins.

> **TODO, before launch.** The field list below is taken from the header of a
> KOVA3 iGG callset produced on 2025-05-21 with iGG v1.2.3. Reconfirm it against
> the header of the final production callset, since the emitted set depends on
> the iGG version and on the `--gg-msvcf-info-fields` value used:
>
> ```bash
> # Enumerate every INFO field actually present in the produced VCF.
> bcftools view -h kova3.chr1.sites.vcf.gz \
>   | grep '^##INFO' \
>   | sed 's/^##INFO=<//; s/>$//'
> ```

Source: [DRAGEN documentation, population genotyping](https://help.dragen.illumina.com/)

---

## Fixed columns

| Column | Description |
|---|---|
| `CHROM` | Chromosome, GRCh38, `chr`-prefixed contig naming |
| `POS` | 1-based position of the first reference base |
| `ID` | Always `.`. dbSNP rsIDs are not assigned; see note below |
| `REF` | Reference allele |
| `ALT` | Alternate allele |
| `QUAL` | Site quality. iGG reports the maximum input QUAL across the cohort at this site |
| `FILTER` | Filter status; see [FILTER values](#filter-values) |

**`ID` is not populated.** Every record carries `.`. dbSNP rsIDs are tied to a
dbSNP build, so embedding them would date each release against a moving
external resource and add a provenance question KOVA3 does not need to answer.
The stable key KOVA3 publishes instead is `variant_id`
(`chrom-pos-ref-alt`), which is self-contained and does not change between
releases. If you want rsIDs, add them yourself against whichever build your
pipeline already pins:

```bash
bcftools annotate -a dbSNP.vcf.gz -c ID \
  kova3.chr1.sites.vcf.gz -Oz -o kova3.chr1.sites.rsid.vcf.gz
```

Should a later release populate `ID`, that is an added field rather than a
changed one, so it would be a minor release under
[versioning.md](versioning.md).

---

## Core frequency fields

These are the fields most users will consume. All are cohort-wide.

| Field | Number | Type | Description |
|---|---|---|---|
| `AC` | A | Integer | Alternate allele count across the whole cohort |
| `AN` | 1 | Integer | Total called alleles at this site across the whole cohort. The denominator for `AF` |
| `AF` | A | Float | **Derived.** Alternate allele frequency across the whole cohort, `AC / AN` |
| `NS` | 1 | Integer | Number of samples in the cohort |
| `NS_GT` | 1 | Integer | Number of samples with a called genotype at this site |
| `NS_NOGT` | 1 | Integer | Number of samples with no called genotype at this site |
| `NS_NODATA` | 1 | Integer | Number of samples with no coverage at this site |
| `nhomalt` | A | Integer | **Derived.** Number of individuals homozygous for the alternate allele |
| `call_rate` | 1 | Float | **Derived.** Call rate, `NS_GT / NS`, 0-1 |

**Interpreting `AN`.** `AF` alone is not sufficient for variant
classification. With 10,988 samples, `AN` is at most 21,976 on the autosomes. A
site with `AF = 0` and `AN = 21,000` is well-powered evidence of absence in
Koreans; a site with `AF = 0` and `AN = 400` is not. Always read `AN` alongside
`AF`, and consult the callability resources described in
[methods.md](methods.md#callability) for regions absent from the callset
entirely.

**`NS_NOGT` versus `NS_NODATA`.** These distinguish two different reasons a
sample contributes no genotype: the site was covered but not confidently
genotyped, or it had no coverage at all. Users assessing whether a region is
interpretable should look at both.

**Chromosome X, Y and M.** Allele numbers on the sex chromosomes reflect
ploidy, so `AN` in non-pseudoautosomal regions is not simply twice the sample
count. `AF` is computed against these sex-aware denominators, not against a
fixed one.

| Region | Ploidy | `AN` |
|---|---|---|
| chrX, pseudoautosomal | Diploid for all samples | `2 x N_called` |
| chrX, non-pseudoautosomal | Diploid in XX, haploid in XY | `2 x N_XX_called + N_XY_called` |
| chrY, non-pseudoautosomal | Haploid, XY only | `N_XY_called`. XX samples are excluded from the denominator |
| chrY, pseudoautosomal | Not reported | Masked. Pseudoautosomal variants are reported once, on chrX |
| chrM | Haploid | `N_called`. Heteroplasmy fractions are not published |

**Sex-stratified frequencies are not published.** There are no `AC_XX` or
`AN_XY` fields. What a clinical filter needs on the sex chromosomes is a
correct denominator, which the model above provides, rather than a second set
of stratified counts.

> **TODO:** confirm this model against the produced callset. `--gg-diploidify`
> was not set on the run, so the DRAGEN default applies; check the observed
> chrX and chrY allele numbers against the table above before release.

---

## Cohort quality-control fields

Metrics for assessing whether a site is well called. These come from iGG
unchanged. They are computed only at diploid sites, and are missing where they
cannot be calculated, for example where only one allele is present, or where no
sample is genotyped.

| Field | Number | Type | Description |
|---|---|---|---|
| `IC` | 1 | Float | Inbreeding coefficient, site-wise. Range -1 to 1. Values near 0 are consistent with Hardy-Weinberg equilibrium; negative values indicate excess heterozygosity, which often signals poor calling |
| `HWEc2` | 1 | Float | Hardy-Weinberg equilibrium P-value, site-wise, from a chi-squared test |
| `HWE` | A | Float | Hardy-Weinberg equilibrium P-value, per alternate allele, from an exact conditional test |
| `ExcHet` | A | Float | Excess heterozygosity P-value, per alternate allele, from an exact conditional test |

These statistics are unstable for small cohorts and low-frequency alleles, and
are affected by population structure and by any consanguinity in the cohort.
KOVA3 aggregates several regionally distinct cohorts, so a deviation from
Hardy-Weinberg equilibrium at a given site may reflect genuine structure rather
than a calling error. Read them alongside the cohort-effect assessment described
in [methods.md](methods.md#residual-cohort-effect-assessment).

Allelic-balance summaries (`ABHom`, `ABHet`, `ABHetP`) are **not** emitted by
the KOVA3 run and are therefore not published. Per-sample allelic depth (`AD`)
is present in the controlled-tier multi-sample VCF.

---

## Subpopulation-stratified fields

Frequencies stratified by the subpopulations defined in
[subpopulations.md](subpopulations.md). These are **derived**: iGG computes
cohort-wide statistics, not arbitrary user-defined strata, so KOVA3 computes
them from the callset before genotypes are dropped.

| Field | Number | Type | Description |
|---|---|---|---|
| `AC_jeju` | A | Integer | Alternate allele count within the Jeju stratum |
| `AN_jeju` | 1 | Integer | Called alleles within the Jeju stratum |
| `AF_jeju` | A | Float | Alternate allele frequency within the Jeju stratum |
| `nhomalt_jeju` | A | Integer | Homozygous alternate individuals within the Jeju stratum |

The whole-cohort figures are the unsuffixed `AC`, `AN`, `AF` and `nhomalt` above;
there is no separate `_all` suffix. See [subpopulations.md](subpopulations.md) for what the Jeju
stratum is and when to use it.

The stratified fields are **not suppressed at rare variants**: `AC_jeju = 1`
is published like any other value. See
[subpopulations.md](subpopulations.md#minimum-stratum-size) for why, and read
`AN_jeju` before drawing a conclusion from a small `AC_jeju`.

---

## Deriving the KOVA3 fields

The derived fields `AF`, `nhomalt`, `call_rate` and the stratified `*_jeju`
fields do not come from iGG and must be computed while per-sample genotypes are
still present. This matters for pipeline ordering: iGG can emit a sites-only
callset directly via `--gg-drop-genotypes`, but doing so too early discards the
information the homozygote counts and stratified frequencies are computed from.

The required order is:

1. Run iGG with `--merge-batches true` to produce the full msVCF **with**
   genotypes
2. Compute `AF`, `nhomalt`, `call_rate`, and the stratified fields from it
3. Drop genotypes to produce the sites-only layer
4. Publish the sites-only layer and run the release gate over it

> **TODO:** publish the exact commands used for step 2 so the derived fields are
> reproducible.

---

## FILTER values

The values below are taken from the header of the KOVA3 iGG callset. iGG applies
hard filters to cohort-wide metrics; filtering is per-site, so SNVs and indels
cannot be filtered separately as they can in the variant caller.

| Value | Description |
|---|---|
| `PASS` | Site passed all filters |
| `DRAGENSnpHardQUAL` | SNV site quality below 3.0103 |
| `DRAGENIndelHardQUAL` | Indel site quality below 3.0103 |
| `LowDepth` | Read depth at or below 1 |
| `LowGQ` | Genotype quality of 0 |
| `PloidyConflict` | Genotype call not consistent with the chromosome ploidy |

The DRAGEN header template also declares a number of somatic-calling filters.
They are not produced by a germline cohort run and do not appear on KOVA3
records.

> **TODO:** reconfirm this table against the final production callset, and state
> in [methods.md](methods.md#variant-level-filtering) whether failing sites are
> retained or removed. If they are removed, say so here too, so users understand
> that absence from the file does not imply absence from the cohort.

---

## Variant representation conventions

**One row is one alternate allele.** Multi-allelic sites are split before
publication, so every record in the sites-only VCF carries a single ALT, and
every row of the Parquet and Hail layers is one variant allele. This is the
convention gnomAD and most frequency resources use, and it is what makes a join
on `(chromosome, pos, ref, alt)` unambiguous. It also means the number of
records is larger than the number of genomic positions.

Indels are left-aligned and normalized against the GRCh38 reference. Variant
classes included are single-nucleotide variants and short insertions and
deletions.

The split and normalization are a single step:

```bash
bcftools norm -m -any -f <GRCh38 reference FASTA> input.vcf.gz -Oz -o normalized.vcf.gz
```

`-m -any` splits multi-allelic records; `-f` supplies the reference needed for
left-alignment. Splitting matters more than usual here because several fields
above are `Number=A`: `bcftools norm` carries the correct element of each such
field to each split record, which is why the split is done with it rather than
by hand.

**If you compare KOVA3 against another resource, normalize both the same way.**
An unsplit multi-allelic record on either side will not join, and a
differently-left-aligned indel will join to the wrong row or to none.

> **TODO:** confirm and document:
>
> - the exact reference FASTA passed to `-f`, once methods.md records it
> - any upper size limit on indels
> - that structural variants, copy-number variants, and short tandem repeats are
>   **not** included in this release

---

## What is not present

The published files contain **no** per-sample genotype columns, no sample
identifiers, and no participant-level annotations. A sites-only VCF has no
`FORMAT` column and no sample columns; tools expecting them will see a cohort of
zero samples.

In particular, none of the iGG per-sample fields (`GT`, `GQ`, `AD`, `FT`,
`LPL`, `LAA`, `LAF`, `QL`) appear in the open tier. They exist only in the
controlled-tier multi-sample VCF, which is released under the Data Use
Agreement; see [data-access.md](data-access.md).

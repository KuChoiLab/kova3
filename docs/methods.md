# Methods and quality control

## Overview

```
per-sample gVCFs (4 cohorts)
        │
        ▼
  DRAGEN Iterative gVCF Genotyper  ──  joint genotyping on GRCh38
        │
        ▼
  multi-sample callset  (published in the controlled tier)
        │
        ├── duplicate removal
        ├── ancestry inference
        ├── relatedness assessment
        ├── sample QC
        ├── variant QC
        └── residual cohort-effect assessment
        │
        ▼
  sites-only aggregate layer  ──  published in the open tier
        │
        ├── sites-only VCF (chromosome-sharded)
        ├── Parquet frequency tables
        ├── Hail Table
        └── callability / allele-number resources
```

The multi-sample callset carries per-sample genotype columns, so it is released
in the controlled tier rather than openly. The sites-only aggregate layer is
derived from it by dropping every genotype column and rewriting the file header;
that conversion is what makes the open tier publishable without restriction. See
[data-access.md](data-access.md) for how the controlled tier is obtained.

---

## Reference genome

All coordinates are on **GRCh38**.

> **TODO:** state the exact reference used: FASTA filename, accession
> (for example `GCA_000001405.15_GRCh38_no_alt_analysis_set`), whether ALT
> contigs and decoys were included, and the contig naming convention
> (`chr1` vs `1`). Users cannot correctly lift or intersect KOVA3 against
> other resources without this.

## Joint genotyping

Per-sample gVCFs from all contributing cohorts are combined through a single
**DRAGEN Iterative gVCF Genotyper (IGG)** run on the Illumina Connected
Analytics platform.

> **TODO:** record the exact DRAGEN IGG version (for example `v4.4.7`), the
> ICA pipeline identifier, and any non-default parameters. Version pinning is
> required for reproducibility and is referenced in the application.
>
> Two parameters need explicit attention:
>
> - **`--gg-msvcf-info-fields`.** `AF` is not in the iGG default INFO set, so a
>   run left at the default produces no allele frequency field. Set this
>   explicitly, and record the value used.
> - **`--gg-drop-genotypes`.** iGG can emit a sites-only callset natively, but
>   the KOVA3-derived fields (homozygote counts, call rate, Jeju stratum) must
>   be computed while genotypes are still present. See
>   [data-dictionary.md](data-dictionary.md#deriving-the-kova3-fields) for the
>   required ordering.

### Why joint genotyping rather than meta-analysis

Cohorts sequenced and called separately produce frequency estimates that are
not directly comparable: allele numbers vary by contributing cohort, reference
blocks differ, and sites absent from one cohort's callset are indistinguishable
from sites where the alternate allele was genuinely not observed.

Combining gVCFs through a single joint genotyping run produces one normalized
callset in which allele numbers are consistent genome-wide, and in which a
site's absence carries the same meaning across all contributing samples.

### What joint genotyping does not fix

Harmonized joint calling **reduces** cross-cohort heterogeneity. It does not
remove it. Differences in sequencing platform, library preparation, coverage
depth, and alignment upstream of gVCF generation persist into the joint
callset. These residual effects are assessed and reported rather than assumed
away; see [batch-effect assessment](#residual-cohort-effect-assessment).

---

## Sample-level processing

### Duplicate removal

Records contributed by more than one cohort are identified and retained once.

> **TODO:** document the method (for example, genotype concordance across a
> common SNP set, or `KING` kinship above the duplicate threshold), the
> threshold applied, and which cohort's record is retained when duplicates are
> found. Report the number of duplicates removed per cohort pair.

### Ancestry inference

> **TODO:** document the method (for example, PCA projection onto a reference
> panel such as 1000 Genomes or HGDP), the variant set used, and the criteria
> for retaining or excluding samples on ancestry grounds. State explicitly
> whether non-Korean-ancestry samples are excluded, and how many were removed.

### Relatedness assessment

> **TODO:** document the method and kinship threshold used, whether a maximal
> unrelated set is retained or related individuals are down-weighted, and the
> resulting number of unrelated individuals. Report both the full-cohort and
> unrelated-subset allele numbers if both are published.

### Sample quality control

> **TODO:** list the sample-level QC metrics and thresholds applied, for
> example call rate, mean coverage, contamination estimate, chimera rate,
> heterozygosity, and sex-check concordance. For each, give the threshold and
> the number of samples excluded.

---

## Variant-level filtering

> **TODO:** document the variant filtering applied to the published sites,
> including:
>
> - which DRAGEN `FILTER` values are retained versus removed
> - any additional site-level thresholds (call rate floor, Hardy–Weinberg or
>   excess-heterozygosity cutoffs, minimum allele number)
> - whether multi-allelic sites are split and left-aligned, and with what tool
>   and parameters
> - the variant classes included (SNVs and short indels) and any size limit on
>   indels
> - whether any small-cell suppression is applied to singleton or very rare
>   variants
>
> Every filter that changes what a user sees must be documented here, because
> a variant absent from KOVA3 is otherwise indistinguishable from a variant
> that was filtered out.

---

## Callability

A frequency of zero can mean "not observed in Koreans" or "not callable in this
region". KOVA3 publishes callability resources so users can tell the
difference.

Per-site allele number (`AN`) is published for every site in the callset. In
addition, genome-wide allele-number and call-rate tracks are published so that
regions absent from the callset can still be assessed.

> **TODO:** specify the format of the genome-wide callability resource
> (per-base BigWig, interval BED, or binned Parquet), the resolution, and how
> users should interpret it alongside `AN`.

---

## Residual cohort-effect assessment

Each release publishes an assessment of residual heterogeneity between
contributing cohorts.

> **TODO:** define and publish the assessment. At minimum it should cover:
>
> - sequencing platform, library preparation, and mean coverage per cohort
> - upstream alignment and gVCF-calling parameters per cohort, where these
>   differ
> - cross-cohort allele frequency concordance at common variants, with a
>   correlation statistic and a plot
> - principal components computed within the cohort, coloured by contributing
>   cohort, to show whether cohort separates from population structure
> - identification of any genomic regions where cohort effects are strong
>   enough that frequencies should be treated with caution
>
> Reporting this honestly is more useful to clinical users than claiming
> heterogeneity has been eliminated.

---

## Reproducibility

> **TODO:** publish the pipeline configuration, tool versions, and parameter
> files sufficient for an external group to understand exactly how the
> published frequencies were produced. Approved controlled-tier applicants hold
> the participant-level inputs and can therefore rerun the pipeline end to end;
> publish the configuration in a form that supports that.

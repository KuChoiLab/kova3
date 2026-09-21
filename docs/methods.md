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

All coordinates are on **GRCh38**, with `chr`-prefixed contig names.

The reference is the ALT-aware GRCh38 analysis set used by DRAGEN on Illumina
Connected Analytics, with decoy and HLA sequences included. It carries **3,366
contigs**:

| Class | Count |
|---|---:|
| Primary assembly (`chr1`-`chr22`, `chrX`, `chrY`, `chrM`) | 25 |
| Unlocalized (`*_random`) | 42 |
| Unplaced (`chrUn_*`) | 127 |
| `chrEBV` | 1 |
| ALT contigs (`*_alt`) | 261 |
| Decoy (`*_decoy`) | 2,385 |
| HLA | 525 |
| **Total** | **3,366** |

`chr1` is 248,956,422 bp and `chrM` is 16,569 bp (rCRS), as expected for
GRCh38. ALT contigs are present in the reference but ALT-masked in the DRAGEN
graph build, so reads are placed on the primary assembly.

Sites on non-primary contigs are not published. The joint genotyping run is
configured over a 25-contig list (`chr1`-`chr22`, `chrX`, `chrY`, `chrM`), so
the mitochondrial genome is in scope, but no chrM output has been inspected
yet; the shard is confirmed non-empty before it is published. See
[file-tree.md](file-tree.md).

> **TODO:** record the ICA reference bundle name and the underlying FASTA
> filename. The produced VCF header carries no `##reference=` line, so the
> contig set above is currently the only machine-checkable description.

## Joint genotyping

Per-sample gVCFs from all contributing cohorts are combined through a single
**DRAGEN iterative gVCF Genotyper (iGG)** run on the Illumina Connected
Analytics platform.

| Step | Software |
|---|---|
| Per-sample alignment and gVCF generation | DRAGEN v4.2, `--enable-map-align true`, `--enable-duplicate-marking true`, `--vc-emit-ref-confidence GVCF`, `--vc-ml-enable-recalibration true`, CRAM output |
| Joint genotyping | DRAGEN iterative gVCF Genotyper **v1.2.3**, `--enable-gvcf-genotyper-iterative true`, `--merge-batches true`, `--gg-enable-indexing true` |
| Platform | Illumina Connected Analytics, Korea region |
| Sharding | 102 shards over the 3,366-contig reference |

**Why iGG v1.2.3 and not a later release.** v1.2.6 was current when the run was
configured, but it fails to recognize the `HLA-DRB1*07` allele. The algorithm is
otherwise unchanged between the two, so v1.2.3 was pinned for the whole cohort
rather than mixing versions across batches.

`--merge-batches true` matters for how the output reads: it merges the
processing batches before the cohort statistics are written, so the callset
carries one set of cohort-wide `AC`, `AN` and `NS*` values under plain,
unprefixed names, with no batch-level duplicates. See
[data-dictionary.md](data-dictionary.md#field-naming-convention).

`AF` is not in the iGG default INFO set and is not requested, so the joint
genotyping output has no allele frequency field. KOVA3 derives `AF` together
with `nhomalt`, `call_rate` and the Jeju stratum fields, which must happen
while genotypes are still present; see
[data-dictionary.md](data-dictionary.md#deriving-the-kova3-fields) for the
required ordering.

> **TODO:** record the exact ICA pipeline identifier and Docker image tag for
> the production run, and the per-sample DRAGEN patch version, once the final
> callset is produced. The image tag has the form `v<igg>-d<dragen>-<build>`.

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

The steps below describe the procedure the Choi Lab applies. It was developed
and validated on subsets of the cohort during 2025. Thresholds are stated
because they are decisions; the resulting sample counts are not, because they
are produced by the final callset and that run has not completed. Every count
in this section is therefore marked outstanding, and
[cohorts.md](cohorts.md#cohort-composition) carries the same list.

### The QC variant set

Ancestry inference and relatedness both run on a common pruned variant set
rather than on the whole callset, because both methods need
approximately independent, well-called, common variants.

It is built in two stages. First, on the callset as a whole:

| Step | Criterion |
|---|---|
| Site call rate | `variant_qc.call_rate >= 0.9` |
| Low-complexity regions | Removed, against `LCR-hs38.bed` |

Then, to produce the pruned set:

| Step | Criterion |
|---|---|
| Variant class | Biallelic SNVs only (`hl.is_snp`, `hl.len(alleles) == 2`) |
| Minor allele frequency | `hl.min(variant_qc.AF) > 0.001` |
| Site call rate | `variant_qc.call_rate > 0.99` |
| Hardy-Weinberg | `variant_qc.p_value_hwe > 1e-8` |
| Inbreeding coefficient | `info.IC > -0.025`, taken from the DRAGEN `IC` field rather than recomputed |
| Linkage disequilibrium | `hl.ld_prune(mt.GT, r2=0.1, bp_window_size=100000)`, run per autosome and unioned |

The LD pruning is run one autosome at a time and the results concatenated;
running it genome-wide in one call exhausts memory at this cohort size.

> **TODO:** report the number of variants surviving each step for the
> production callset.

### Duplicate removal

**Duplicates are not detected by a separate step.** A duplicate pair sits far
above the relatedness threshold applied below, so it is removed by the
relatedness pruning along with first- and second-degree relatives, and the
record retained is chosen by the same rule.

> **TODO:** report the number of duplicate pairs found, broken down by cohort
> pair, for the production callset.

### Ancestry inference

Ancestry is inferred in two stages, both by **projection onto a reference
panel** rather than by a joint principal-component analysis of reference and
cohort together. Principal components are computed on the reference alone and
the cohort is projected into that space, so adding or removing cohort samples
cannot move the reference axes.

Principal components are computed on the reference panel alone with Hail's
`hwe_normalized_pca`, retaining the loadings, at **k = 20**. The cohort is then
projected into that space with `hl.experimental.pc_project`, using the
reference panel's own allele frequencies as the projection frequencies. Both
stages use twenty principal components.

**Stage 1, continental ancestry.** The reference is the gnomAD v3.1 HGDP and
1000 Genomes callset, restricted to the unrelated samples without outliers
(`hgdp_1kg_v2/pca_results/unrelateds_without_outliers`). Samples whose
superpopulation label is missing or ambiguous are dropped, leaving roughly
2,500 reference samples across AFR, AMR, EAS, EUR and SAS. Cohort samples that
do not project into the East Asian cluster are excluded.

**Stage 2, East Asian substructure.** The East Asian samples are then projected
against 1000 Genomes phase 3 East Asian samples (CHB, CHS, CDX, JPT, KHV),
filtered to `variant_qc.call_rate > 0.99`, together with a downsample of KOVA2
as a Korean anchor. Samples projecting into a non-Korean East Asian cluster are
excluded. Known problematic reference samples are removed from the panel before
the analysis.

Both exclusions are applied to the joint genotyping input list, so an excluded
sample contributes to no allele number anywhere in the release.

> **TODO, blocking before launch.** Two things are outstanding here, and the
> second is the more important.
>
> - Report the number of samples excluded at each stage for the production
>   callset.
> - **Publish the rule that assigns a projected sample to a cluster.** In the
>   development runs the assignment was made by inspecting the projected
>   principal components, without a written numeric criterion. A reproducible
>   rule is required before release: either a distance or posterior-probability
>   cut-off, or the gnomAD `assign_genetic_ancestry_pcs` random-forest
>   classifier with its probability threshold stated. Say which, and state the
>   threshold.

### Relatedness assessment

A **maximal unrelated set** is retained. Related individuals are not
down-weighted, and the published allele numbers are those of the retained set.

The kinship coefficient is computed with **KING**. The input is the PASS-only
single-nucleotide variants in exonic regions, converted to PLINK binary format,
and KING is run in kinship mode with IBS statistics.

**The threshold is `kinship > 0.1`**, which removes duplicates, first-degree
and second-degree relatives while retaining third-degree and more distant
pairs.

Pruning is greedy rather than a single pass. While any pair above the
threshold remains: take the sample or samples with the most relatedness edges;
among those, drop the one with the **lowest fraction of the genome covered at
10x**, using mean alignment coverage as a tie-break; recompute the remaining
pairs. This removes the smallest number of samples that breaks every edge, and
where the choice is arbitrary it keeps the better-sequenced record. It is also
what resolves duplicates, as described above.

Two cross-checks are run against the same cohort. The first is
`somalier relate` (v0.3.0). The second is Hail `pc_relate`, with a minimum
individual minor allele frequency of **0.001**, **k = 3** principal components
and `statistics='kin20'`; pairs above the same **0.1** kinship threshold are
then resolved with Hail's `maximal_independent_set`. `'kin20'` is used rather
than `'kin'` because the IBS0 estimate needed to separate the relationship
classes is not returned by `'kin'`.

The two methods agree closely but not exactly, and **the KING result is the one the release
uses**; the Hail figure is not interchangeable with it and the two must not be
mixed in a single report.

> **TODO:** report, for the production callset, the number of samples removed,
> the number of unrelated individuals retained, and the breakdown of removed
> pairs by inferred relationship degree.

### Sample quality control

Sex chromosome ploidy is checked for every sample, and samples with a sex
chromosome aneuploidy are excluded before joint genotyping.

Per-sample metrics are computed with `hl.sample_qc` and carried through the
pipeline: non-reference SNV and indel counts, transition/transversion ratio,
mean genotype quality for SNVs and indels, and call rate for SNVs and indels
separately. Per-sample coverage comes from the DRAGEN
`wgs_coverage_metrics.csv` report, specifically the fraction of the genome at
10x or above and the mean alignment coverage over the genome.

> **TODO, blocking before launch.** This section is the least complete in this
> document and the gap is real, not editorial.
>
> - **State the exclusion thresholds.** The metrics above are computed and
>   inspected, but no numeric cut-off has been fixed for per-sample call rate,
>   mean coverage, transition/transversion ratio or mean genotype quality. Fix
>   them, state them here, and report how many samples each removes.
> - **State the sex-imputation method** behind the aneuploidy calls: the
>   statistic used, its threshold, and how a sex-check discordance between the
>   imputed and the recorded sex is resolved.
> - **Add contamination and chimera-rate screening, or say why not.**
>   Neither a contamination estimate nor a chimera rate is currently applied.
>   Both are standard for a population reference and both are available from
>   the DRAGEN per-sample reports.
> - Record the versions of KING, PLINK, VCFtools, BCFtools and Hail used in
>   the production run. Only `somalier` (v0.3.0) is currently pinned.

---

## Variant-level filtering

> **TODO:** document the variant filtering applied to the published sites,
> including:
>
> - which DRAGEN `FILTER` values are retained versus removed
> - any additional site-level thresholds (call rate floor, Hardy–Weinberg or
>   excess-heterozygosity cutoffs, minimum allele number)
> - the variant classes included (SNVs and short indels) and any size limit on
>   indels
>
> Every filter that changes what a user sees must be documented here, because
> a variant absent from KOVA3 is otherwise indistinguishable from a variant
> that was filtered out.

**Multi-allelic sites are split and indels left-aligned** before publication;
the tool and parameters are given in
[data-dictionary.md](data-dictionary.md#variant-representation-conventions).

**No small-cell suppression is applied.** Singleton and very rare variants are
published with their counts; see
[data-owners.md](data-owners.md#no-small-cell-suppression) for the reasoning.

---

## Callability

A frequency of zero can mean "not observed in Koreans" or "not callable in this
region". KOVA3 publishes callability resources so users can tell the
difference.

Per-site allele number (`AN`) is published for every site in the callset. That
covers sites the callset contains. It says nothing about the regions where the
callset has no record at all, and those are exactly the regions where a user is
most likely to mistake silence for absence. Two genome-wide resources fill that
gap, published under `callability/` in each release.

| Resource | Format | Resolution | Use it for |
|---|---|---|---|
| Allele-number track | BED, bgzip-compressed with a tabix index | Exact. Run-length encoded, so each interval is a maximal run of constant `AN` | Streaming one region and asking "was this locus callable at all". Same access pattern as the sites-only VCF, and readable by `bedtools`, `pybedtools` and IGV |
| Callability summary | Apache Parquet, partitioned by `chromosome` | 1 kb bins: `chromosome`, `position_bin`, `start`, `end`, `mean_an`, `median_an`, `call_rate` | Genome-wide and panel-wide work. Joins directly against the frequency tables in Athena, Spark or polars |

The BED track is the authoritative one: it is exact, with no binning. The
Parquet summary is a convenience for aggregate queries, where 3.1 million 1 kb
rows are far easier to work with than the full run-length encoding.

The summary is partitioned by `chromosome` only. At 3.1 million rows it does
not need the second partition level the frequency layer uses, but it carries
`position_bin` as an ordinary column so that it joins to the frequency tables
without a computed key.

A per-base BigWig is deliberately **not** published. It needs a special writer,
is awkward to join against tabular data, and adds nothing the two resources
above do not already provide.

**How to read them alongside `AF`.** A variant absent from KOVA3 is evidence of
rarity only where the allele number at that position is high. Before treating
an absence as informative, look the position up in the callability track: a
region with low or zero `AN` was not assessed, and no conclusion about Korean
frequency follows from it.

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
> - principal components computed within the cohort, colored by contributing
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

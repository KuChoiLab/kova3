# Cohorts and consent

## Cohort composition

KOVA3 integrates **11,000 Korean whole-genome cohort records** from four
independently generated sources.

| Cohort | Source institution | Records | Notes |
|---|---:|---:|---|
| National Integrated Bio-Big Data (국가통합바이오빅데이터) | KOBIC | 4,739 | |
| Jeju Genome | Invites Genomics | 2,987 | Geographically distinct island population; see note below |
| Korea4K | KOGIC | 1,661 | Eligible subset of a 3,737-record cohort; see note below |
| Korea10K | KOGIC | 1,613 | Additional production within the Korea10K project |
| **Total** | | **11,000** | Before cross-cohort deduplication |

Two cohorts contribute fewer records than their first-quoted size, for
different reasons, and both exclusions are final.

The Jeju Genome cohort was assembled as 2,993 records. **Six** were found to
disagree with their accompanying metadata and were excluded before transfer, so
2,987 were delivered and are the number KOVA3 carries. The delivered inventory
was reconciled against that figure: none of the six appears in it.

Korea4K as a whole is 3,737 records, and KOVA3 takes the subset that meets two
conditions at once: the participant is a healthy control, and their consent
covers secondary provision of the data to a third party. Records failing either
condition are not eligible for KOVA3 regardless of data quality. **1,661**
records meet both, and that is the contribution KOVA3 carries. Two participants
were excluded at the consent condition, and the exclusion applies to every tier:
they are absent from the joint genotyping that produces the open-tier
frequencies as well as from the controlled tier.

The identifiers excluded from both cohorts are held in the project's internal
exclusion list and are deliberately not published here: naming them would
disclose a participant-level consent or quality status about people who are not
otherwise identifiable in this resource. The list is passed to the release gate
[`scripts/verify_sites_only.py`](../scripts/verify_sites_only.py) as
`--exclusion-list`, which fails the release if any of those identifiers appears
anywhere in a published file, so an excluded record cannot reach either tier
unnoticed.

Published material that quotes 2,993, 1,663, or a total of 11,008 or 11,002
predates these exclusions.

### Read-level data held per cohort

Read-level format is not uniform. It varies by cohort and, within Korea4K, by
sample. This determines what a controlled-tier applicant receives.

| Cohort | Records | FASTQ | CRAM | Notes |
|---|---:|---|---|---|
| National Integrated Bio-Big Data (KOBIC) | 4,739 | No | *Reported* | Reported as CRAM; holdings not yet reconciled against the delivered inventory |
| Jeju Genome | 2,987 | No | Yes | Aligned CRAM with CRAI for every sample |
| Korea4K | 1,661 | Yes | Yes | FASTQ and aligned CRAM both held; see below |
| Korea10K | 1,613 | Yes | No | No CRAM exists for this cohort |

**All CRAM KOVA3 publishes is aligned.** It is coordinate-sorted against
GRCh38 and carries a CRAI index, so a single locus can be streamed without
downloading the file. Korea4K CRAM is DRAGEN output against an alt-masked
GRCh38; Jeju CRAM arrives aligned and indexed from the sequencing provider. The
KOBIC holdings are reported as CRAM but have not yet been reconciled against
the delivered inventory, and that row is confirmed before release.

Korea4K also exists as unaligned CRAM, the original EGA deposit, and that is
**not** what KOVA3 publishes. The distinction is not visible in the filename:
a substantial number of the aligned DRAGEN outputs are still called
`*_unaligned.cram`, because DRAGEN was invoked with
`--output-file-prefix` set to the input basename. Selecting or excluding files
by that substring gets the answer wrong in both directions. The published
objects are renamed to `<SAMPLE>.cram` at upload, and the per-sample manifest
records the source path.

Per-sample gVCF exists for every cohort. The genotyped multi-sample VCF covers
all 11,000 records. A per-sample manifest published with the controlled tier
states exactly which formats exist for each sample; see
[file-tree.md](file-tree.md).

The count above is the number of **records contributed**, not the final number
of unique unrelated individuals. Deduplication and relatedness assessment are
performed as part of the pipeline; see [methods.md](methods.md).

> **TODO, blocking before launch.** Report the exact figures once the callset
> is produced:
>
> - unique individuals after cross-cohort deduplication
> - unrelated individuals after relatedness filtering
> - overlap with KOVA2 and between contributing cohorts
> - samples excluded at QC, with reasons
>
> Each release must publish these numbers. See
> [versioning.md](versioning.md).

### Ascertainment

KOVA3 does **not** claim to be a healthy-control panel. The contributing cohorts
were ascertained under their own independent study designs, which differ, and
KOVA3 records each cohort's basis rather than applying a single label across all
of them. Users applying KOVA3 frequencies to a specific disease should read the
per-cohort ascertainment before assuming that cases of that disease are absent.

| Cohort | Ascertainment basis (how participants were recruited) | Disease-status information available | Could cases of a given disease be present? |
|---|---|---|---|
| National Integrated Bio-Big Data (KOBIC) | *TODO* | *TODO* | *TODO* |
| Jeju Genome | *TODO* | *TODO* | *TODO* |
| Korea4K / Korea10K (KOGIC) | *TODO* | *TODO* | *TODO* |

> **TODO, complete before launch.** Fill the table above from each cohort's
> study protocol. State explicitly where ascertainment differs between cohorts.
> Korea4K and Korea10K are grouped here because both were produced by KOGIC;
> confirm that they were recruited under the same protocol, and split the row
> again if they were not.
> Do **not** label any cohort a "healthy control" set unless that is supported by
> that cohort's own protocol. This affects how users interpret allele
> frequencies for disease-specific analyses.

### Planned additions

A subsequent release will add approximately 2,500 genomes from Seoul National
University Hospital, bringing the cohort to roughly 13,500 records. Frequencies
will be recomputed by full joint genotyping rather than merged post hoc; the
release will receive a new major version. See
[versioning.md](versioning.md).

---

## Consent and governance

For each contributing cohort, the following must be confirmed in writing before
the cohort can be included in a CC BY 4.0 release. The table records the
consent instrument, whether that consent permits public aggregate release, the
governing IRB/ethics approval, and the data provision agreement with Korea
University. The **licensing authority** consequences of these confirmations are
tracked in [data-owners.md](data-owners.md#redistribution-authority); this
table is the governance evidence behind that determination.

| Cohort | Consent instrument | Consent permits public aggregate release, no access controls | IRB / ethics approval (with number) | Data provision agreement with the Choi Lab | Cohort-specific publication restriction |
|---|---|---|---|---|---|
| National Integrated Bio-Big Data (KOBIC) | *Pending* | *Pending* | *Pending* | *Pending* | *Pending* |
| Jeju Genome | *Pending* | *Pending* | *Pending* | *Pending* | *Pending* |
| Korea4K | *Pending* | *Pending* | *Pending* | *Pending* | *Pending* |
| Korea10K | *Pending* | *Pending* | *Pending* | *Pending* | *Pending* |

> **Status: outstanding, and blocking the first data release.** Every row is
> `Pending`. The analysis that produces KOVA3 is carried out under institutional
> ethics approval held by the Choi Lab and by the providing institutions,
> and each contributing cohort was collected under its own approved protocol.
> Approval to analyze is not the same as written confirmation that a cohort's
> consent permits unrestricted public aggregate release, which is what this
> table records. Until a cohort's row is fully confirmed in writing (evidence
> held on file by the Choi Lab and the institutional legal/IRB office),
> that cohort **cannot** be included in the release or in the allele-number
> denominators. Record each approval reference directly in the table when
> obtained. Registering the resource and publishing this documentation do not
> depend on the table; publishing data does.

### Summary of the position taken

KOVA3 publishes **aggregate site-level statistics only**. No participant-level
sequence, genotype, or identifying metadata is released. This scope was chosen
so that the resource can be shared under an open license consistent with the
consent obtained across the contributing cohorts.

Where a contributing cohort's consent or data provision agreement does not
permit even aggregate publication, that cohort is excluded from the release and
from the allele-number denominators.

---

## Aggregate cohort metadata

Published alongside the callset, at cohort level only:

| Field | Description |
|---|---|
| `cohort_id` | Stable identifier for the contributing cohort |
| `cohort_name` | Human-readable name |
| `source_institution` | Institution that generated the data |
| `n_records_contributed` | Records contributed before deduplication |
| `n_included` | Records retained after deduplication and QC |
| `sequencing_platform` | Platform(s) used |
| `mean_coverage` | Mean autosomal coverage across included samples |

> **TODO:** finalize this table against the metadata actually available for
> each cohort, and confirm that publishing per-cohort sample counts and
> coverage statistics is permitted under each data provision agreement.

No participant-level metadata is published in **either tier**: not age, not sex
at individual resolution, not phenotype, not recruitment site, and no other
field that could contribute to re-identification. Controlled-tier recipients
receive the sequencing data and the per-sample file manifest, and nothing else.
An analysis that requires participant characteristics cannot be served by KOVA3
as released; enquire before applying.

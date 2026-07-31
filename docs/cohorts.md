# Cohorts and consent

## Cohort composition

KOVA3 integrates **11,008 Korean whole-genome cohort records** from four
independently generated sources.

| Cohort | Source institution | Records | Notes |
|---|---:|---:|---|
| National Integrated Bio-Big Data (국통바빅) | KOBIC | 4,739 | |
| Jeju Genome | Invites Genomics | 2,993 | Geographically distinct island population |
| Korea4K | KOGIC | 1,663 | Subset of a 3,737-record cohort |
| Korea10K | KOGIC | 1,613 | Additional production within the Korea10K project |
| **Total** | | **11,008** | Before cross-cohort deduplication |

The count above is the number of **records contributed**, not the final number
of unique unrelated individuals. Deduplication and relatedness assessment are
performed as part of the pipeline; see [methods.md](methods.md).

> **TODO — blocking before launch.** Report the exact figures once the callset
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

> **TODO.** Define and publish the ascertainment basis for each cohort — how
> participants were recruited, and what disease status information is
> available. Do not describe the cohort as a "healthy control" set unless that
> label is supported cohort-by-cohort. Where ascertainment differs between
> cohorts, say so explicitly: users applying KOVA3 frequencies to a specific
> disease need to know whether cases of that disease could be present.

### Planned additions

A subsequent release will add approximately 2,500 genomes from Seoul National
University Hospital, bringing the cohort to roughly 13,500 records. Frequencies
will be recomputed by full joint genotyping rather than merged post hoc; the
release will receive a new major version. See
[versioning.md](versioning.md).

---

## Consent and governance

> **TODO — blocking before submission and launch.**
>
> This section must summarize, for each contributing cohort:
>
> - the consent instrument under which participants were enrolled
> - whether that consent permits public release of aggregate,
>   non-identifiable summary statistics without access controls
> - the IRB or ethics committee approval covering secondary use and
>   aggregate publication, with approval numbers
> - the data provision agreement between the source institution and Korea
>   University governing the derived release
> - any cohort-specific restriction that limits what may be published
>
> Until each of these is confirmed in writing, the corresponding cohort cannot
> be included in a CC BY 4.0 release. See
> [data-owners.md](data-owners.md#redistribution-authority).

### Summary of the position taken

KOVA3 publishes **aggregate site-level statistics only**. No participant-level
sequence, genotype, or identifying metadata is released. This scope was chosen
so that the resource can be shared under an open licence consistent with the
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

No participant-level metadata — age, sex at individual resolution, phenotype,
recruitment site, or any field that could contribute to re-identification — is
published.

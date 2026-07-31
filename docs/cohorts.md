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

KOVA3 does **not** claim to be a healthy-control panel. The contributing cohorts
were ascertained under their own independent study designs, which differ, and
KOVA3 records each cohort's basis rather than applying a single label across all
of them. Users applying KOVA3 frequencies to a specific disease should read the
per-cohort ascertainment before assuming that cases of that disease are absent.

| Cohort | Ascertainment basis (how participants were recruited) | Disease-status information available | Could cases of a given disease be present? |
|---|---|---|---|
| National Integrated Bio-Big Data (KOBIC) | *TODO* | *TODO* | *TODO* |
| Jeju Genome | *TODO* | *TODO* | *TODO* |
| Korea4K | *TODO* | *TODO* | *TODO* |
| Korea10K | *TODO* | *TODO* | *TODO* |

> **TODO — complete before launch.** Fill the table above from each cohort's
> study protocol. State explicitly where ascertainment differs between cohorts.
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

| Cohort | Consent instrument | Consent permits public aggregate release, no access controls | IRB / ethics approval (with number) | Data provision agreement with Korea University | Cohort-specific publication restriction |
|---|---|---|---|---|---|
| National Integrated Bio-Big Data (KOBIC) | *Pending* | *Pending* | *Pending* | *Pending* | *Pending* |
| Jeju Genome | *Pending* | *Pending* | *Pending* | *Pending* | *Pending* |
| Korea4K | *Pending* | *Pending* | *Pending* | *Pending* | *Pending* |
| Korea10K | *Pending* | *Pending* | *Pending* | *Pending* | *Pending* |

> **Status: blocking before submission and launch.** Every row is `Pending`.
> Until a cohort's row is fully confirmed in writing (evidence held on file by
> the Choi Laboratory and the institutional legal/IRB office), that cohort
> **cannot** be included in the release or in the allele-number denominators.
> Record the approval numbers directly in the table when obtained.

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

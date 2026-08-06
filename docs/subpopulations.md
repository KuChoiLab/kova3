# Subpopulation definitions

KOVA3 defines **two strata**: `all` and `jeju`. Every published frequency
belongs to one of them.

| Stratum | Definition | Fields |
|---|---|---|
| `all` | Every included sample | `GAC`, `GAN`, `GAF`, `KOVA3_HOMALT` |
| `jeju` | Samples from the Jeju Genome cohort | `KOVA3_AC_jeju`, `KOVA3_AN_jeju`, `KOVA3_AF_jeju`, `KOVA3_HOMALT_jeju` |

**The `all` stratum has no `_all` suffix.** Its fields are the `G`-prefixed
DRAGEN fields, which are already cohort-wide by definition, so adding a suffixed
duplicate would publish the same numbers twice under two names. This follows the
convention used by gnomAD and other frequency resources, where the overall
figures are unsuffixed and only subpopulations carry a suffix.

See [data-dictionary.md](data-dictionary.md) for types and full definitions.

---

## Why these two strata

`all` is the default any frequency resource must publish. The question is which
subpopulations to add alongside it, and here the answer is one.

**Jeju is a geographically distinct island population**, and it arrives as its
own contributing cohort. Publishing it as a stratum therefore requires no
clustering analysis and no interpretive judgement about who belongs to which
group: the stratum is exactly the Jeju Genome cohort. If real allele frequency
differences exist between Jeju and the rest of the cohort, a user can see them
rather than having them averaged away in a pooled figure.

**The remaining cohorts do not support additional strata.** The other
contributing sources are national or multi-institutional collections rather than
defined regional populations, so splitting them would produce strata that
describe how samples were collected, not where the people are from. A stratum
labelled by cohort of origin invites users to read it as an ancestry group,
which it is not.

A third stratum for the complement of Jeju, meaning mainland samples, is not
published, because it is exactly derivable from the two that are:
`GAC − KOVA3_AC_jeju` over `GAN − KOVA3_AN_jeju`. Publishing it would add no
information and one more chance for the three figures to disagree.

---

## What the Jeju stratum is not

It is defined by **cohort of origin**, not by genetically inferred ancestry. A
sample is in the stratum because it came from the Jeju Genome cohort, not
because a clustering algorithm assigned it there. Samples with Jeju ancestry
that were collected through another cohort are not in the stratum, and any
sample in the Jeju cohort without Jeju ancestry is.

This is a deliberately conservative definition. It is reproducible and it makes
no claim the data cannot support. It also means the stratum should not be
treated as an ancestry label.

> **TODO:** report the observed differentiation between the Jeju stratum and the
> rest of the cohort in each release, as a summary statistic and a plot, so users
> can see whether stratifying makes a practical difference for their variants.
> If it turns out not to, say so plainly rather than leaving users to assume it
> matters.

---

## Minimum stratum size

> **TODO:** set and document whether stratified fields are suppressed at very
> rare variants. The Jeju stratum is roughly 2,993 records against a whole
> cohort of 11,008, so stratified estimates are noisier than whole-cohort ones
> at low frequencies, and per-stratum counts at singleton variants are the
> smallest cells the release will publish. State the threshold applied, if any,
> and what users see below it: omitted fields, or fields present but missing.

---

## What is not stratified

KOVA3 does not publish frequencies stratified by sex, age, phenotype,
recruitment site, or any other participant attribute. Only the Jeju stratum is
published, and only in aggregate.

> **TODO:** if sex-stratified allele numbers are needed for correct
> interpretation of the sex chromosomes, document that in
> [data-dictionary.md](data-dictionary.md); it is a ploidy question, not a
> subpopulation question.

---

## Guidance for users

**Use the `all` stratum**, `GAF` with `GAN`, unless you have a specific reason
to restrict to Jeju. For clinical variant filtering in Korean patients,
the whole-cohort frequency is the right number in almost every case.

The Jeju fields are useful when your samples are from Jeju, or when you are
investigating whether a variant's frequency is uniform across Korea. Always
check `KOVA3_AN_jeju` before drawing a conclusion from `KOVA3_AF_jeju`: the
stratum denominator is roughly a quarter of the whole-cohort denominator, so a
frequency estimate from it carries correspondingly more uncertainty.

---

## Future strata

Additional strata may be added in later releases if the cohort grows to support
them, or if the residual cohort-effect assessment described in
[methods.md](methods.md#residual-cohort-effect-assessment) identifies structure
worth exposing. Adding a stratum adds fields without changing existing values,
so it is a minor release under the policy in [versioning.md](versioning.md).

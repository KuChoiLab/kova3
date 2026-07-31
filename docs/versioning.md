# Versioning and correction policy

## Why this matters

Allele frequencies are not stable facts. They change as the cohort grows, as QC
thresholds are revised, and as errors are corrected. A user who filtered a
patient's variants against KOVA3 last year and reaches a different conclusion
today needs to be able to tell which release produced which answer.

KOVA3 therefore versions every release, keeps published paths immutable, and
documents what changed.

---

## Release numbering

Releases are tagged `v<MAJOR>.<MINOR>.<PATCH>`.

| Component | Incremented when | Example |
|---|---|---|
| **MAJOR** | Cohort composition changes, or frequencies are recomputed by re-running joint genotyping. Field semantics change, or fields are renamed or removed | Adding the SNUH cohort |
| **MINOR** | Fields or resources are added without changing existing values. New subpopulation strata, new annotations, additional output formats | Publishing a new callability track |
| **PATCH** | Errors are corrected without changing cohort composition or field definitions | Fixing incorrect `AN` on a set of sites |

Within a major version, existing field names, types, and meanings do not
change. A pipeline written against `v3.0.0` will continue to work against
`v3.1.0`.

### Pin your release

Always record the release tag used in any analysis, and cite it in
publications. Release paths include the tag:

```
s3://<BUCKET>/data/release=v3.0.0/...
```

There is no "latest" alias that silently moves. This is deliberate: a moving
pointer makes analyses irreproducible.

---

## Immutability

**Published objects are never modified or deleted in place.** A correction
produces a new release under a new prefix. The superseded release remains
available so that prior analyses can be reproduced and re-examined.

Superseded releases are marked as such in [CHANGELOG.md](../CHANGELOG.md) and
in their own `manifest.json`, with a pointer to the release that replaces them.

> **TODO:** decide and document a retention period for superseded releases,
> and whether very old releases are eventually removed. If they are, say how
> much notice users receive.

---

## Correction policy

### Reporting an error

Open an issue in this repository describing the affected variants or region,
the expected and observed values, and how the discrepancy was found. Include
the release tag.

We aim to acknowledge within five working days.

### How corrections are handled

1. The error is reproduced and its scope determined — which sites, which
   fields, which releases are affected.
2. An **erratum** is published under `metadata/errata/` describing the error,
   its scope, and its impact on interpretation. This happens as soon as the
   scope is known, without waiting for a corrected release.
3. A corrected release is produced with an incremented `PATCH` version, unless
   the correction requires recomputing frequencies, in which case it is a
   `MAJOR` release.
4. [CHANGELOG.md](../CHANGELOG.md) records the correction and identifies the
   superseded release.
5. Announcement goes out through the channels below.

Errata are published even when a corrected release follows quickly. Users who
have already run an analysis need to know whether their results were affected,
and a silent replacement does not tell them.

---

## Announcements

Each release and each erratum is announced through:

- GitHub releases and the issue tracker on this repository
- The Choi Laboratory website at <https://choi.korea.ac.kr/>
- The KOVA3 announcement mailing list — low volume, releases and errata only
- The Registry of Open Data on AWS entry

> **TODO:** confirm the mailing list exists and publish its subscription link
> here before launch. Confirm the laboratory's other announcement channels
> before listing them.

---

## Release checklist

Each release publishes, at minimum:

- [ ] Sites-only VCF/BCF shards with `.tbi` and `.csi` indexes
- [ ] Parquet frequency tables
- [ ] Hail Table, with the Hail version recorded
- [ ] Callability and allele-number resources
- [ ] Aggregate cohort metadata
- [ ] `manifest.json` with per-object SHA-256 checksums
- [ ] Machine-readable schemas under `metadata/schemas/`
- [ ] Exact unique and unrelated sample counts after deduplication and QC
- [ ] Overlap with KOVA2 and between contributing cohorts
- [ ] Sample and variant QC summary, with exclusion counts and reasons
- [ ] Residual cohort-effect assessment
- [ ] Snapshot of this documentation under `docs/`
- [ ] `CHANGELOG.md` entry

---

## Release history

See [CHANGELOG.md](../CHANGELOG.md).

| Release | Date | Records | Notes |
|---|---|---:|---|
| `v3.0.0` | TODO | 11,008 | Initial KOVA3 release. Not yet published |

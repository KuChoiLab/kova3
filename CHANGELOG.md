# Changelog

All notable changes to the KOVA3 dataset are recorded here.

Releases follow the versioning and correction policy in
[docs/versioning.md](docs/versioning.md). Published release paths are
immutable; corrections produce a new release rather than modifying an existing
one.

## [Unreleased]

Preparing the initial KOVA3 release (`v3.0.0`) from 11,008 Korean whole-genome
cohort records, in two tiers: an open allele-frequency layer and a
controlled-access layer holding the participant-level sequencing data.

Outstanding before launch:

- Joint genotyping run and export of the open tier
- Exact unique and unrelated sample counts after deduplication and QC
- Cohort-by-cohort consent and redistribution determination, for both tiers
- Finalized subpopulation definitions
- Reconciliation of the data dictionary against the produced VCF header
- Per-sample manifest of read-level formats held for the controlled tier
- Tutorial notebooks
- S3 buckets and Registry of Open Data entry

<!--
Template for each released version:

## [vX.Y.Z] - YYYY-MM-DD

### Added
### Changed
### Fixed
### Superseded
-->

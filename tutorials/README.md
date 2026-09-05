# Tutorials

Reproducible notebooks showing how to use KOVA3 with AWS services.

> **Not yet published.** These will be released alongside the first versioned
> KOVA3 release. See [CHANGELOG.md](../CHANGELOG.md) for release status.

## Planned notebooks

Each notebook is based on the AWS Open Data "Get To Know A Dataset" template and
states its expected output, runtime, bytes scanned, approximate user cost, and
the pinned KOVA3 release version.

| # | Notebook | Covers |
|---|---|---|
| 1 | Streaming an interval | Fetch a gene region from the sites-only callset on Amazon S3 with `bcftools`, without downloading the file |
| 2 | Annotating a patient VCF | Add Korean allele frequencies to your own VCF and filter by frequency |
| 3 | Querying with Athena | Look up a variant list or gene panel against the Parquet frequency layer |
| 4 | Genome-wide analysis in Hail | Load the prebuilt Hail Table and run analysis on Amazon EMR |
| 5 | Working with the controlled tier | Apply for access, then stream a locus from CRAM with `samtools` where CRAM exists, and align FASTQ in-region otherwise |

Notebooks 1 to 4 use the open tier and need no credentials. Notebook 5 requires
an approved application; see [docs/data-access.md](../docs/data-access.md).

## Community challenge

Compare a candidate variant list for a Korean rare disease case before and after
filtering on KOVA3 frequencies, and report how the candidate count changes.

> **TODO:** publish the notebooks before launch. This is a required onboarding
> deliverable for the AWS Open Data Sponsorship Program, not an optional extra.

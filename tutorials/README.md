# Tutorials

Reproducible notebooks showing how to use KOVA3 with AWS services.

> **Status.** Notebook 1 is published as a draft: it is written against the
> release layout, but the open-tier bucket does not exist yet, so its cells carry
> no outputs. Notebooks 2 to 5 are planned and will be released alongside the
> first versioned KOVA3 release. See [CHANGELOG.md](../CHANGELOG.md).
>
> The AWS Open Data "Get To Know A Dataset" notebook for KOVA3 lives in a
> separate repository:
> [seungsookim-99/open-data-examples](https://github.com/seungsookim-99/open-data-examples/blob/main/kova3/get-to-know-a-dataset.ipynb).

## Notebooks

Each notebook states its expected output, runtime, bytes scanned, approximate
user cost, and the pinned KOVA3 release version.

| # | Notebook | Covers |
|---|---|---|
| 1 | [Streaming an interval](01_stream_interval_bcftools.ipynb) | Fetch a gene region from the sites-only callset on Amazon S3 with `bcftools`, without downloading the file |
| 2 | Annotating a patient VCF | Add Korean allele frequencies to your own VCF and filter by frequency |
| 3 | Querying with Athena | Look up a variant list or gene panel against the Parquet frequency layer |
| 4 | Genome-wide analysis in Hail | Load the prebuilt Hail Table and run analysis on Amazon EMR |
| 5 | Working with the controlled tier | Apply for access, then stream a locus from CRAM with `samtools` where CRAM exists, and align FASTQ in-region otherwise |

Notebooks 1 to 4 use the open tier and need no credentials. Notebook 5 requires
an approved application; see [docs/data-access.md](../docs/data-access.md).

## Community challenge

The KOVA3 community challenge is posed in the
[Get To Know A Dataset notebook](https://github.com/seungsookim-99/open-data-examples/blob/main/kova3/get-to-know-a-dataset.ipynb).
If you take it on, open an issue on this repository with what you find.

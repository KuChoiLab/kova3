# Tutorials

Reproducible notebooks showing how to use KOVA3 with AWS services.

> **Status.** These notebooks are published as drafts: they are written against
> the release layout, but the open-tier bucket does not exist yet, so their cells
> carry no outputs. They will be run end to end and republished with outputs
> once the buckets exist. See [CHANGELOG.md](../CHANGELOG.md).
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
| 2 | [Annotating your own VCF](02_annotate_patient_vcf.ipynb) | Add Korean allele frequencies to a patient or cohort VCF without overwriting its own, and filter on them |
| 3 | [Querying a gene panel with Athena](03_athena_gene_panel.ipynb) | Look up a gene panel or a variant list against the Parquet frequency layer, with the bytes scanned reported |

All three use the open tier and need no credentials. Notebook 3 additionally
needs an AWS account, because Athena runs in the reader's own account and the
scan charges land there; the data itself stays free.

### Planned

Two more notebooks are intended, each waiting on a decision that has not been
made yet. They are listed here rather than promised in the table above, because
writing them now would fix choices that are still open.

| Notebook | Waiting on |
|---|---|
| Genome-wide analysis in Hail on Amazon EMR | The Hail version the release is written with. EMR bootstrap and Spark configuration are tied to it, and a recipe written against the wrong version costs the reader real money to discover. See [docs/schemas.md](../docs/schemas.md#hail-version) |
| Working with the controlled tier | The signed Data Use Agreement and the credential mechanism for the controlled bucket. See [docs/data-access.md](../docs/data-access.md) |

## Community challenge

The KOVA3 community challenge is posed in the
[Get To Know A Dataset notebook](https://github.com/seungsookim-99/open-data-examples/blob/main/kova3/get-to-know-a-dataset.ipynb).
If you take it on, open an issue on this repository with what you find.

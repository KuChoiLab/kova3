# KOVA3 — Korean Variant Archive 3

Documentation for the KOVA3 population-level allele-frequency resource.

> **Status: pre-release.** KOVA3 has not yet been published. This repository
> documents the planned structure and content of the release. Sections marked
> **TODO** are not yet finalized and will be completed before launch. Nothing
> here should be cited as a released resource until a versioned release appears
> in [CHANGELOG.md](CHANGELOG.md).

---

## Scope statement

### What KOVA3 is

KOVA3 is an openly licensed, **population-level allele-frequency resource**
derived from whole-genome sequencing of approximately 11,008 Korean cohort
records. It reports, for each variant site, how often the alternate allele is
observed in this Korean cohort — together with the information needed to
interpret that number responsibly.

The resource exists because Koreans are underrepresented in the frequency
references used in routine clinical variant interpretation. Broad "East Asian"
strata in those references are dominated by Han Chinese and Japanese samples,
so alleles that are common in Koreans are often absent or imprecisely
estimated. In rare disease diagnostics this inflates the candidate variant
burden for Korean patients.

### What is released

| Layer | Contents |
|---|---|
| Sites-only callset | Chromosome-sharded VCF/BCF, bgzip-compressed, with tabix/CSI indexes |
| Frequency tables | Apache Parquet, partitioned by chromosome and position bin |
| Hail Table | Prebuilt, for genome-wide analysis without an import step |
| Callability resources | Per-site call rate and allele-number tracks |
| Aggregate metadata | Cohort-level descriptions in TSV/Parquet |
| Documentation | This repository, plus JSON/YAML schemas and release manifests |

Per-site fields include cohort allele count (`GAC`), allele number (`GAN`),
allele frequency (`GAF`), homozygote count, call rate, Hardy-Weinberg and
allelic-balance statistics, and quality filters. Fields are published under the
names DRAGEN emits, with a `G` prefix marking cohort-wide values. See the
[data dictionary](docs/data-dictionary.md).

### What is **not** released

KOVA3 publishes **no participant-level data**. The following are excluded from
the public release and retained under internal or controlled access:

- FASTQ files
- CRAM/BAM alignments
- Per-sample gVCFs
- Per-sample genotype calls
- Phased haplotypes
- Fine-grained participant metadata

This boundary is deliberate. Individual genotypes are re-identifiable, and the
contributing cohorts were not consented for unrestricted public release of
participant-level data. Aggregate site-level statistics can be shared openly;
participant-level data cannot.

> **Consequence for users:** analyses that intrinsically require individual
> haplotypes — imputation reference panel construction, phasing,
> haplotype-based demographic inference — cannot be performed with KOVA3.

### Reference build

All coordinates are on **GRCh38**. See [methods](docs/methods.md) for the exact
reference FASTA and accession.

---

## Quick start

> **TODO:** replace `<BUCKET>` and `<RELEASE>` with the published S3 bucket
> name and release tag once the dataset is live on the Registry of Open Data.

Query a gene interval without downloading anything:

```bash
# Stream a single interval straight from S3. Only the bytes covering the
# requested region are transferred, not the whole file.
bcftools view \
  -r chr17:43044295-43125364 \
  https://<BUCKET>.s3.amazonaws.com/data/release=<RELEASE>/sites_vcf/kova3.chr17.sites.vcf.gz
```

Annotate your own VCF with Korean allele frequencies:

```bash
# Add KOVA3 cohort allele counts and frequencies to an existing patient VCF.
# The G prefix means cohort-wide; see docs/data-dictionary.md.
bcftools annotate \
  -a https://<BUCKET>.s3.amazonaws.com/data/release=<RELEASE>/sites_vcf/kova3.chr17.sites.vcf.gz \
  -c INFO/GAC,INFO/GAN,INFO/GAF,INFO/KOVA3_HOMALT \
  -O z -o patient.kova3.vcf.gz \
  patient.vcf.gz
```

Load the Hail Table:

```python
import hail as hl
# No import step needed; the table is prebuilt and partitioned.
ht = hl.read_table("s3://<BUCKET>/data/release=<RELEASE>/hail/kova3.sites.ht")
ht.describe()
```

More worked examples, including Amazon Athena queries against the Parquet
layer, live in [`tutorials/`](tutorials/).

> **TODO:** publish the tutorial notebooks. Each should state expected output,
> runtime, bytes scanned, approximate user cost, and the pinned release version.

---

## Documentation index

| Document | Contents |
|---|---|
| [Controlled-tier data access](docs/data-access.md) | Who may apply for participant-level data, and how |
| [License and data owners](docs/data-owners.md) | Licence terms, data ownership, attribution requirements |
| [Cohorts and consent](docs/cohorts.md) | Contributing cohorts, sample counts, consent basis |
| [Methods and QC](docs/methods.md) | Joint genotyping pipeline, QC, batch-effect assessment |
| [Data dictionary](docs/data-dictionary.md) | Every published INFO field, with definition and type |
| [Schemas](docs/schemas.md) | Parquet column schema and Hail Table schema |
| [Subpopulations](docs/subpopulations.md) | Subpopulation definitions and stratified frequencies |
| [File tree and manifest](docs/file-tree.md) | Bucket layout, naming conventions, release manifest |
| [Versioning and corrections](docs/versioning.md) | Release numbering, correction policy, deprecation |
| [Citation](CITATION.md) | How to cite KOVA3 and its predecessors |

---

## Licence

KOVA3 data are released under
[Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE).
This documentation is released under the same licence.

See [docs/data-owners.md](docs/data-owners.md) for attribution requirements and
data ownership.

---

## Support

- **Questions and bug reports:** open an issue in this repository
- **Contact:** Jungmin Choi, Korea University College of Medicine —
  <jungminchoi@korea.ac.kr>
- **Release announcements:** watch this repository, or see
  [docs/versioning.md](docs/versioning.md) for the announcement channels

We aim to acknowledge issues within five working days. Data errata are handled
under the correction policy in [docs/versioning.md](docs/versioning.md).

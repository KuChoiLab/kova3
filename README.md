# KOVA3: Korean Variant Archive 3

Documentation for KOVA3, a population-scale Korean genome resource released in
two tiers: an openly licensed allele-frequency layer, and a controlled-access
layer holding the participant-level sequencing data.

> **Status: pre-release.** KOVA3 has not yet been published. This repository
> documents the planned structure and content of the release. Sections marked
> **TODO** are not yet finalized and will be completed before launch. Nothing
> here should be cited as a released resource until a versioned release appears
> in [CHANGELOG.md](CHANGELOG.md).

---

## Scope statement

### What KOVA3 is

KOVA3 is a Korean genome resource derived from whole-genome sequencing of
11,000 cohort records. Its **open tier** is an openly licensed, population-level
allele-frequency callset: for each variant site it reports how often the
alternate allele is observed in this Korean cohort, together with the
information needed to interpret that number responsibly. Its **controlled
tier** holds the participant-level sequencing data behind that callset, for
researchers whose work cannot be done from frequencies alone.

The resource exists because Koreans are underrepresented in the frequency
references used in routine clinical variant interpretation. Broad "East Asian"
strata in those references are dominated by Han Chinese and Japanese samples,
so alleles that are common in Koreans are often absent or imprecisely
estimated. In rare disease diagnostics this inflates the candidate variant
burden for Korean patients.

### What is released

| Layer | Contents |
|---|---|
| Sites-only callset | Chromosome-sharded VCF, bgzip-compressed, with tabix indexes |
| Frequency tables | Apache Parquet, partitioned by chromosome and position bin |
| Hail Table | Prebuilt, for genome-wide analysis without an import step |
| Callability resources | Per-site call rate and allele-number tracks |
| Aggregate metadata | Cohort-level descriptions in TSV/Parquet |
| Documentation | This repository, plus JSON schemas and release manifests |

The open tier is expected to contain approximately **100 to 115 million variant
sites**. This is an estimate from the joint genotyping run in progress; the exact
count for a release is published in that release's `manifest.json` and recorded
in [CHANGELOG.md](CHANGELOG.md).

Per-site fields include cohort allele count (`AC`), allele number (`AN`),
allele frequency (`AF`), homozygote count (`nhomalt`), call rate
(`call_rate`), inbreeding coefficient, Hardy-Weinberg and excess-heterozygosity
statistics, and quality filters. No allele-count threshold is applied, so
singletons are published. The frequency fields use the names standard across population
frequency resources, so a pipeline written against gnomAD reads a KOVA3 file
unchanged. See the [data dictionary](docs/data-dictionary.md) for the full
field list and for how these map onto the joint genotyping output.

### The controlled tier

Everything above is the **open tier**. The participant-level data behind it are
released as a **controlled tier**: FASTQ, CRAM, per-sample gVCF, and the
genotyped multi-sample VCF, for the same cohort.

The two tiers differ in how you get them, not in whether they are available:

| | Open tier | Controlled tier |
|---|---|---|
| Contents | Site-level allele frequencies and supporting resources | Participant-level reads, per-sample gVCF, multi-sample VCF |
| License | CC BY 4.0 | KOVA3 Data Use Agreement |
| How to get it | Download or stream directly; no registration | Apply; see [docs/data-access.md](docs/data-access.md) |
| Cost | None | None |
| Eligibility | Anyone | Academic researchers, non-commercial research |

The split is a privacy boundary, not a paywall. Individual genotypes are
re-identifiable, and the contributing cohorts were not consented for
unrestricted public release of participant-level data. Aggregate site-level
statistics can be shared openly; participant-level data are shared under an
agreement that binds the recipient.

Fine-grained participant metadata are not released in either tier. Aggregate
cohort descriptions are published with the open tier; see
[docs/cohorts.md](docs/cohorts.md).

> **Which tier do you need?** Analyses that depend on how alleles co-occur
> within individuals, such as phasing, linkage disequilibrium, imputation
> reference panel construction, and relatedness and population-structure work,
> require the controlled tier. So do methods
> that need read-level evidence, such as structural-variant and short-tandem-repeat
> calling. Frequency filtering, ACMG/AMP population-frequency evidence, carrier
> frequency estimation, and pharmacogenomic allele frequencies are served by the
> open tier alone.

### Reference build

All coordinates are on **GRCh38**. See [methods](docs/methods.md) for the exact
reference FASTA and accession.

---

## Quick start

> **Note.** The bucket name `kova3-open` (Asia Pacific, Seoul, `ap-northeast-2`)
> and the release tag `v3.0.0` are the values KOVA3 will publish under. The
> bucket is not created yet, so these commands will not resolve until launch.

Query a gene interval without downloading anything:

```bash
# Stream a single interval straight from S3. Only the bytes covering the
# requested region are transferred, not the whole file.
bcftools view \
  -r chr17:43044295-43125364 \
  https://kova3-open.s3.ap-northeast-2.amazonaws.com/data/release=v3.0.0/sites_vcf/kova3.chr17.sites.vcf.gz
```

Annotate your own VCF with Korean allele frequencies:

```bash
# Add KOVA3 cohort allele counts and frequencies to an existing patient VCF.
#
# Note the ":=" renaming. KOVA3 publishes its frequencies under the standard
# names AC, AN and AF, and your patient VCF almost certainly has fields of the
# same name describing your own cohort. Annotating without renaming would
# overwrite them. Prefix them on the way in and both survive.
bcftools annotate \
  -a https://kova3-open.s3.ap-northeast-2.amazonaws.com/data/release=v3.0.0/sites_vcf/kova3.chr17.sites.vcf.gz \
  -c 'INFO/KOVA3_AC:=INFO/AC,INFO/KOVA3_AN:=INFO/AN,INFO/KOVA3_AF:=INFO/AF,INFO/KOVA3_nhomalt:=INFO/nhomalt' \
  -O z -o patient.kova3.vcf.gz \
  patient.vcf.gz

# Then filter on the Korean frequency without touching your own:
bcftools view -i 'INFO/KOVA3_AF < 0.01 || INFO/KOVA3_AF = "."' patient.kova3.vcf.gz
```

Both VCFs must be normalized the same way for the annotation to land on the
right rows; see [variant representation](docs/data-dictionary.md#variant-representation-conventions).

Load the Hail Table:

```python
import hail as hl
# No import step needed; the table is prebuilt and partitioned.
ht = hl.read_table("s3://kova3-open/data/release=v3.0.0/hail/kova3.sites.ht")
ht.describe()
```

Worked examples live in [`tutorials/`](tutorials/): streaming an interval,
annotating your own VCF, and querying a gene panel with Amazon Athena against
the Parquet layer.

> **TODO:** run the published notebooks end to end once the buckets exist and
> republish them with their expected output, runtime, bytes scanned and
> approximate user cost filled in. Two further notebooks, Hail on Amazon EMR and
> the controlled tier, are listed as planned in
> [`tutorials/README.md`](tutorials/README.md).

---

## Documentation index

| Document | Contents |
|---|---|
| [Controlled-tier data access](docs/data-access.md) | Who may apply for participant-level data, and how |
| [License and data owners](docs/data-owners.md) | License terms, data ownership, attribution requirements |
| [Cohorts and consent](docs/cohorts.md) | Contributing cohorts, sample counts, consent basis |
| [Methods and QC](docs/methods.md) | Joint genotyping pipeline, QC, batch-effect assessment |
| [Data dictionary](docs/data-dictionary.md) | Every published INFO field, with definition and type |
| [Schemas](docs/schemas.md) | Parquet column schema and Hail Table schema |
| [Subpopulations](docs/subpopulations.md) | Subpopulation definitions and stratified frequencies |
| [File tree and manifest](docs/file-tree.md) | Bucket layout, naming conventions, release manifest |
| [Versioning and corrections](docs/versioning.md) | Release numbering, correction policy, deprecation |
| [Citation](CITATION.md) | How to cite KOVA3 and its predecessors |

---

## License

The open tier, this documentation, the schemas, and the tutorial notebooks are
released under
[Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE).

The controlled tier is released under the KOVA3 Data Use Agreement, at no cost,
to academic researchers for non-commercial research. See
[docs/data-access.md](docs/data-access.md).

See [docs/data-owners.md](docs/data-owners.md) for attribution requirements and
data ownership.

---

## Support

- **Questions and bug reports:** open an issue in this repository
- **Contact:** Jungmin Choi, Korea University College of Medicine,
  <jungminchoi@korea.ac.kr>, copying the KOVA3 data access team at
  <ku.choi.lab@gmail.com>
- **Release announcements:** watch this repository, or see
  [docs/versioning.md](docs/versioning.md) for the announcement channels

We aim to acknowledge issues within five working days. Data errata are handled
under the correction policy in [docs/versioning.md](docs/versioning.md).

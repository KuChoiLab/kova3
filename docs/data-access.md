# Controlled-tier data access

KOVA3 is released in two tiers.

| Tier | Contents | How to get it |
|---|---|---|
| **Open** | Allele-frequency callset. Sites-only VCF, Parquet, Hail Table, callability resources, aggregate cohort metadata. No participant-level genotypes. | Download directly. No registration, no agreement, no approval. See the [README](../README.md). |
| **Controlled** | Participant-level data: FASTQ, CRAM, per-sample gVCF, and the genotyped multi-sample VCF. | Apply as described on this page. |

**Most users need only the open tier.** If your work is variant frequency
filtering, ACMG/AMP evidence assignment, carrier-frequency estimation, or
comparative population genetics, the open tier answers it and requires no
application. Apply for the controlled tier only if your analysis requires
individual genotypes or sequence reads.

Analyses that genuinely require the controlled tier include haplotype phasing
and linkage disequilibrium, imputation reference panel construction,
relatedness and fine-scale population structure, genotype-phenotype
association, and variant-caller or structural-variant method development that
needs read-level evidence.

---

## Who may apply

Applications are accepted from academic researchers, in Korea and
internationally, for non-commercial research.

You are eligible if all of the following hold.

1. You hold a research position at a university, hospital, government research
   institute, or non-profit research organisation.
2. Your institution will sign the Data Use Agreement through a person
   authorised to bind it. A student or postdoctoral researcher may lead the
   project, but the agreement is signed by a principal investigator and by the
   institutional signing authority.
3. The proposed use is non-commercial research.
4. Your institution can meet the security conditions in the Data Use Agreement.

**Commercial use is not currently supported.** The contributing cohorts'
consent instruments and data provision agreements have not been assessed for
commercial secondary use of participant-level data. Researchers at commercial
organisations who wish to discuss a research collaboration may contact us, but
should not expect access under the standard process.

---

## What you will be asked for

Applications are submitted by email. Prepare the following.

**1. Research plan.** One to two pages: the scientific question, why aggregate
frequencies from the open tier are insufficient, which cohorts and which data
types you need, the analyses you will run, and the expected output. Requests
for the whole dataset without a stated analysis will be returned.

**2. Applicant and institution.** Name, position, institution, department, and
institutional email address of the principal investigator, plus the name and
contact details of the person authorised to sign on behalf of the institution.
Please apply from your institutional address rather than a personal one.

**3. Ethics approval.** The IRB or research ethics committee approval covering
your proposed use, with the approval number and the approving body. If your
institution has determined that the work does not require review, provide that
determination in writing.

**4. Data security statement.** Where the data will be stored, who will have
access, how access is controlled, and how the data will be destroyed at the end
of the project. Storage on personal devices or in personal cloud accounts is
not acceptable.

**5. Signed Data Use Agreement.** See below.

---

## Data Use Agreement

Access is granted under a Data Use Agreement between the applicant's
institution and Korea University. There is **no fee** for access, at any stage.

The agreement's substantive obligations are these.

- **No redistribution.** Data may not be transferred to any third party,
  including collaborators at other institutions, who have not signed their own
  agreement. Each institution applies separately.
- **No re-identification.** No attempt may be made to identify individual
  participants, to link the data to other datasets in order to identify
  participants, or to contact participants.
- **Named users only.** Access is limited to the individuals listed in the
  application. Adding a person requires written notification and approval.
- **Stated purpose only.** Data may be used only for the research described in
  the approved application. A new research question requires a new application.
- **Security.** Data are held on institution-managed systems with access
  control, and are not placed on personal devices, personal cloud storage, or
  publicly accessible servers.
- **Publication and attribution.** Publications and presentations arising from
  the data must cite KOVA3 with the release version, as described in
  [CITATION.md](../CITATION.md). No participant-level data may be included in
  any publication, supplementary file, or public repository. Aggregate results
  may be published freely.
- **Destruction.** Data are destroyed at the end of the stated project period,
  and destruction is confirmed in writing.
- **Breach reporting.** Any actual or suspected loss, unauthorised access, or
  disclosure is reported within 72 hours.
- **Term and revocation.** Approvals run for two years and may be renewed on
  request. Access may be revoked for breach, and the applicant's institution
  will be notified.

The full Data Use Agreement text will be published on this page before the first
controlled-access release. This section summarises its terms; the signed document
governs.

---

## How to apply

Send the materials listed above to:

**Jungmin Choi**, <jungminchoi@korea.ac.kr>
Department of Biomedical Sciences, Korea University College of Medicine

Please use the subject line `KOVA3 controlled-tier access request`.

### What happens next

| Step | Timing |
|---|---|
| Acknowledgement of receipt | 5 working days |
| Completeness check, and a request for anything missing | 2 weeks |
| Review decision | 8 weeks from a complete application |
| Credentials issued after the Data Use Agreement is countersigned | 2 weeks from decision |

Applications are reviewed by the principal investigator on behalf of the KOVA3 data access team, against the criteria on this page. If an application
is declined you will be told the reason, and you may revise and reapply.

---

## How the data are delivered

Approved applicants receive scoped, time-limited credentials to the
controlled-access S3 bucket. Data are not sent by post, on physical media, or
by file-transfer service.

The controlled tier is stored in the same AWS region as the open tier, so
analysis in that region requires no inter-region transfer. **We strongly
recommend computing in-region rather than downloading**, particularly for the
read-level data. Downloading the full read-level collection is neither
necessary for most analyses nor practical.

Read-level format varies by cohort and by sample. Some samples have CRAM, some
have FASTQ, and some have both. A per-sample manifest published with the
release states which formats exist for each sample; consult it when planning an
analysis. Where CRAM is aligned, CRAI indexes allow streaming a single locus.

---

## Questions before applying

If you are unsure whether your analysis needs the controlled tier, or whether
you are eligible, ask before preparing a full application. Open an issue in
this repository for general questions, or email the address above for questions
specific to your project.

---

## Related documents

| Document | Contents |
|---|---|
| [README](../README.md) | Resource overview and open-tier quick start |
| [Cohorts and consent](cohorts.md) | Contributing cohorts, sample counts, consent basis |
| [Licence and data owners](data-owners.md) | Open-tier licence, data ownership, attribution |
| [Methods and QC](methods.md) | Joint genotyping pipeline and quality control |
| [File tree](file-tree.md) | Bucket layout and release manifest |
| [Citation](../CITATION.md) | How to cite KOVA3 |

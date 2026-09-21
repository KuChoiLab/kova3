# Controlled-tier data access

> **Status: the controlled tier is not yet open.** Applications open once each
> contributing institution has confirmed, in writing, that participant-level
> data from its cohort may be redistributed under this process, including to
> applicants outside Korea. Those determinations are recorded in
> [data-owners.md](data-owners.md) and are currently pending for every cohort.
> This page describes the process that will apply when the tier opens. Please do
> not send an application before then; enquiries are welcome at any time.

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
relatedness and fine-scale population structure,
and variant-caller or structural-variant method development that
needs read-level evidence.

---

## Who may apply

Applications are accepted from academic researchers, in Korea and
internationally, for non-commercial research.

You are eligible if all of the following hold.

1. You hold a research position at a university, hospital, government research
   institute, or non-profit research organization.
2. Your institution will sign the Data Use Agreement through a person
   authorized to bind it. A student or postdoctoral researcher may lead the
   project, but the agreement is signed by a principal investigator and by the
   institutional signing authority.
3. The proposed use is non-commercial research.
4. Your institution can meet the security conditions in the Data Use Agreement.

The agreement is signed on the KOVA3 side by the principal investigator
directly, not through a technology-transfer office, so there is no
institutional review queue on our end. On the applicant's side an
institutional signature is required, because the obligations in the agreement
(security, named users, destruction) bind the receiving institution rather
than an individual.

**Commercial use is not currently supported.** The contributing cohorts'
consent instruments and data provision agreements have not been assessed for
commercial secondary use of participant-level data. Researchers at commercial
organizations who wish to discuss a research collaboration may contact us, but
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
contact details of the person authorized to sign on behalf of the institution.
Please apply from your institutional address rather than a personal one.

**3. Ethics approval.** The IRB or research ethics committee approval covering
your proposed use, with the approval number and the approving body. If your
institution has determined that the work does not require review, provide that
determination in writing.

**4. Data security statement.** Where the data will be stored, who will have
access, how access is controlled, and how the data will be destroyed at the end
of the project. Storage on personal devices or in personal cloud accounts is
not acceptable. Include the AWS account ID or IAM principal that should receive
the access credentials, since credentials are issued to a named principal
rather than to a person by email.

**5. Signed Data Use Agreement.** See below.

---

## Data Use Agreement

Access is granted under a Data Use Agreement between the applicant's
institution and Prof. Jungmin Choi, the KOVA3 principal investigator, at
Korea University College of Medicine. There is **no fee** for access, at
any stage.

If responsibility for KOVA3 passes to another principal investigator, the
agreement and the obligations under it carry over, and approved applicants
are notified.

The agreement's substantive obligations are these.

- **No redistribution.** Data may not be transferred to any third party,
  including collaborators at other institutions, who have not signed their own
  agreement. Each institution applies separately.
- **No re-identification.** No attempt may be made to identify individual
  participants, to link the data to other datasets in order to identify
  participants, or to contact participants.
- **Named users only.** Access is limited to the individuals listed in the
  application. Adding a person requires written notification and approval. When
  a named user leaves the project or the institution, the principal
  investigator notifies us within ten working days and revokes that person's
  access.
- **Stated purpose only.** Data may be used only for the research described in
  the approved application. A new research question requires a new application.
  The data may not be used for any purpose relating to the identification,
  assessment or treatment of an individual, including forensic, insurance,
  employment and immigration purposes, and may not be used to support an
  intellectual-property claim that would restrict research use of the data by
  others.
- **Security.** Data are held on institution-managed systems with access
  control, and are not placed on personal devices, personal cloud storage, or
  publicly accessible servers.
- **Publication and attribution.** Publications and presentations arising from
  the data must cite KOVA3 with the release version and, where the work depends
  on a particular contributing cohort, that cohort's own publication, as
  described in [CITATION.md](../CITATION.md). No participant-level data may be
  included in any publication, supplementary file, or public repository.
  Aggregate results may be published freely.
- **Destruction.** At the end of the stated project period, the
  participant-level data and any derived data from which an individual
  participant's information can be recovered are securely destroyed, and
  destruction is confirmed in writing. Aggregate results, such as summary
  statistics and model parameters from which no individual's data can be
  recovered, may be retained and used afterwards.
- **Breach reporting.** Any actual or suspected loss, unauthorized access, or
  disclosure is reported within 72 hours.
- **Term and revocation.** Approvals run for two years and may be renewed on
  request. Access may be suspended or terminated immediately for breach, if the
  consent basis of a contributing cohort changes, or if required by law, by an
  ethics committee, or by a contributing data owner. The applicant's institution
  is notified. Either party may also terminate on thirty days' notice.

### Liability

KOVA3 is supplied without charge and "as is". The agreement excludes the Data
Provider's liability to the recipient institution and its users for loss
arising out of the data or the agreement, including errors or omissions in the
data, interruption or withdrawal of access, and decisions taken in reliance on
the data; a capped liability applies as a fallback if that exclusion is held
unenforceable. Liability for wilful misconduct, gross negligence, fraud, and
death or personal injury is not excluded. Neither party indemnifies the other:
each is responsible for its own acts under applicable law. Nothing in the
agreement limits the recipient institution's liability to third parties,
including research participants, contributing institutions and supervisory
authorities, arising from its own breach.

### Governing law and disputes

The agreement is governed by the laws of the Republic of Korea. Disputes go
first to good-faith negotiation, and then to arbitration before KCAB
International, seated in Seoul, conducted in English before a single
arbitrator. Where the recipient institution is established in Korea,
arbitration does not apply and the Seoul Central District Court has exclusive
jurisdiction at first instance. Either party may seek urgent interim or
injunctive relief from any competent court, including courts where the
institution is established or the data are held.

Institutions that cannot accept this default, such as public bodies without
authority to agree to arbitration or institutions required by their own
governing law to submit to a particular court, should say so when applying. The
agreement allows an alternative forum where both parties agree in writing.

### The agreement text

A full draft exists and is under legal review. The version published on this
page before the first controlled-access release is the one that governs; the
summary above is provided so that institutional signatories can assess the terms
early, and it does not replace the signed document.

---

## How to apply

Send the materials listed above to **both** addresses below, so that an
application is never held up by a single mailbox.

| | Address |
|---|---|
| Principal investigator, and the decision on your application | **Jungmin Choi**, <jungminchoi@korea.ac.kr> |
| KOVA3 data access team, for receipt and correspondence | <ku.choi.lab@gmail.com> |

Department of Biomedical Sciences, Korea University College of Medicine.

Please use the subject line `KOVA3 controlled-tier access request`, and write
from your institutional address rather than a personal one.

### What happens next

| Step | Timing |
|---|---|
| Acknowledgement of receipt | 10 working days |
| Completeness check, and a request for anything missing | 2 weeks |
| Review decision | 8 weeks from a complete application |
| Credentials issued after the Data Use Agreement is countersigned | 2 weeks from decision |

Applications are reviewed by the KOVA3 principal investigator against the criteria on this page. If an application
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
analysis. All published CRAM is aligned to GRCh38 and carries a CRAI index, so
a single locus can be streamed without downloading the file.

---

## Questions before applying

If you are unsure whether your analysis needs the controlled tier, or whether
you are eligible, ask before preparing a full application. Open an issue in
this repository for general questions, or write to <ku.choi.lab@gmail.com> for
questions specific to your project.

---

## Related documents

| Document | Contents |
|---|---|
| [README](../README.md) | Resource overview and open-tier quick start |
| [Cohorts and consent](cohorts.md) | Contributing cohorts, sample counts, consent basis |
| [License and data owners](data-owners.md) | Open-tier license, data ownership, attribution |
| [Methods and QC](methods.md) | Joint genotyping pipeline and quality control |
| [File tree](file-tree.md) | Bucket layout and release manifest |
| [Citation](../CITATION.md) | How to cite KOVA3 |

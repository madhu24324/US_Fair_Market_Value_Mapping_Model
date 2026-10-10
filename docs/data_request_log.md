# ZTRAX access: request log

**Maintained record of the effort to obtain transaction-level data for the
2000–2024 extension. Last updated 20 August 2026.**

Companion to [`project_report.md`](project_report.md), §9.

---

## 1. Why the project needs ZTRAX

The replication of Nolte (2020) Figure 1 is complete and validated
(`project_report.md`). It rests on the author's Dryad deposit,
[10.5061/dryad.np5hqbzq9](https://doi.org/10.5061/dryad.np5hqbzq9), which
contains two GeoTIFF rasters of estimated fair market value at 480 m resolution.

**The deposit is a single 2010 cross-section, expressed in 2017 dollars.** This
was verified directly against the raster: `places_fmv_all.tif` is a
single-band float32 surface with no time dimension, no companion year layers,
and no metadata field encoding a date. It is one snapshot.

The stated objective of stage 2 is an annual series, 2000–2024. No manipulation
of a single cross-section can produce one. Interpolating between years we do not
have, or deflating the 2010 surface by a national price index, would fabricate
precisely the spatial variation in appreciation that the extension exists to
measure — parcels in different markets did not move together over this period,
and a single-year map carries no information about how they diverged.

An annual series therefore requires re-estimating the underlying hedonic model
separately for each year, on transaction records that carry sale dates and
locations. That is what ZTRAX is.

**ZTRAX** — the Zillow Transaction and Assessment Dataset — is a national
database of property transactions and assessor records assembled by Zillow, with
deed transfers and assessment characteristics covering the great majority of US
counties. Nolte's estimates are built on roughly 6 million arm's-length land
sales drawn from it. Zillow's own academic access programme has been
discontinued; the data is now distributed through ICPSR. It is licensed and not
redistributable, which is why the Dryad deposit contains model outputs and
validation tables but no sales microdata.

---

## 2. Dataset identification

| Field | Value |
| --- | --- |
| Title | ZTRAX: Zillow Transaction and Assessment Dataset, United States, 1940–2020 |
| Distributor | ICPSR (Inter-university Consortium for Political and Social Research), University of Michigan |
| Study number | **39652** |
| DOI | [10.3886/ICPSR39652.v2](https://doi.org/10.3886/ICPSR39652.v2) |
| Version | v2 |
| Temporal coverage | 1940–2020 |
| Access class | Restricted-use |

---

## 3. Coverage gap

The current release ends at **2020**. The project's target window runs to
**2024**. Even on successful access, **2021–2024 is not obtainable from this
source.**

Consequences to plan around:

- The achievable series from ICPSR 39652 v2 is **2000–2020** (21 years), not the
  25 originally scoped.
- 2021–2024 covers the post-pandemic repricing of US land — the most volatile
  stretch in the target window and, arguably, the most interesting. Its absence
  is a substantive limitation on the research question, not a technical
  inconvenience.
- Whether ICPSR intends to release a version extending past 2020 is unknown, and
  is among the questions put to them (§5, enquiry 1). Zillow discontinued its
  own academic programme, so a further release is not assured.
- If 2021–2024 proves essential, an alternative source will be required —
  county assessor bulk downloads, or a commercial provider such as CoreLogic or
  ATTOM. Neither has been costed. Both would introduce a break in methodology
  partway through the series, which would need to be handled explicitly rather
  than silently.

---

## 4. Access requirements

ZTRAX is distributed as **restricted-use** data. Access is not a download; it is
an application. From ICPSR's published requirements for restricted-use
collections, an application requires:

1. **A restricted data use agreement signed by an institutional signatory** —
   not by the student researcher. The signatory must be an official empowered to
   bind the institution (typically a research office, sponsored programmes
   office, or equivalent). Every individual with data access must also be named
   and must sign.
2. **An IRB determination** from the applicant's institution. For secondary
   analysis of de-identified property records this is normally a
   *not-human-subjects* or *exempt* determination rather than a full review, but
   the determination letter itself is required — an assertion that IRB review is
   unnecessary is not sufficient.
3. **A data security plan and a data protection statement**, describing storage,
   access control, and disposal.
4. **Encrypted, non-networked storage.** Restricted-use terms typically require
   the data to reside on an encrypted volume on a machine that is not connected
   to the open internet, with physical access controls. This has a practical
   consequence worth raising early: it may be **incompatible with normal laptop
   use and with cloud or shared-cluster computing.** Any analysis environment
   must be planned around this constraint, not retrofitted to it.
5. **A research plan** stating the intended use.

Item 1 is the immediate procedural obstacle: it requires institutional
sponsorship inside IIIT Delhi before ICPSR will consider the application at all.

---

## 5. Blocker: institutional membership

**IIIT Delhi is not an ICPSR member institution.**

ICPSR's holdings are distributed primarily to member institutions, whose
affiliated researchers access data under the institution's membership. Members
are typically in the United States, Canada and Europe; Indian institutional
membership is uncommon.

For non-member institutions, ICPSR's documented route is access on payment of an
**administration fee, in the region of USD 825 per dataset for standard
(public-use) collections.** Two cautions on that figure:

- It is drawn from ICPSR's published guidance for *standard* data. **The fee for
  restricted-use collections is not confirmed** and may be higher, structured
  differently, or unavailable to non-members entirely.
- Non-member requests follow a slower path than member requests, and processing
  time has not been quantified.

Both points are the subject of enquiry 1 below. The figure should be treated as
indicative and **must not be used for budgeting until ICPSR confirms it in
writing.**

Secondary options, not yet pursued:

- Establishing IIIT Delhi as an ICPSR member — a decision above the level of
  this project, but worth raising if the per-dataset fee route proves closed.
- A collaboration with a researcher at a member institution, who could hold the
  agreement and the data with our participation named on it.

---

## 6. Actions taken

### Enquiry 1 — ICPSR

| | |
| --- | --- |
| To | ICPSR-help@umich.edu |
| Sent | 20 August 2026 *(confirm exact date from sent mail)* |
| Subject | Non-member access to ICPSR 39652 (ZTRAX), restricted-use |
| Status | **Awaiting reply** |

Questions put:

1. What is the process for a researcher at a **non-member** institution to
   obtain ICPSR 39652?
2. What is the **administration fee** for this dataset, given that it is
   restricted-use rather than standard?
3. What exactly must the **restricted data use agreement** contain, and who at
   the applicant institution must sign it?
4. What **IRB documentation** is required, given that the intended use is
   secondary analysis of de-identified property records?
5. What is the expected **timeline** from application to access for a non-member
   applicant?
6. Is a release extending coverage **beyond 2020** planned?

### Enquiry 2 — Christoph Nolte

| | |
| --- | --- |
| To | chrnolte@bu.edu — PLACES Lab, Department of Earth & Environment, Boston University |
| Sent | 20 August 2026 *(confirm exact date from sent mail)* |
| Subject | Per-year FMV estimates beyond the 2010 Dryad release |
| Status | **Awaiting reply** |

Questions put:

1. Do **per-year FMV estimates already exist**, whether published, in progress,
   or unreleased?
2. If so, can they be shared or cited, and under what conditions?
3. If not, is the estimation pipeline available, and what ZTRAX fields and
   vintage would be needed to run it?
4. Are there **later or updated releases** of the FMV surfaces beyond the 2020
   Dryad deposit?

This enquiry is the higher-value one. A positive answer removes the ZTRAX
dependency entirely — no agreement, no fee, no IRB, no encrypted-storage
constraint, and no re-estimation. It was sent in parallel with enquiry 1 rather
than after it, because the ICPSR route is slow and the two are independent.

---

## 7. Response log

*No replies received as of 20 August 2026. Record each reply here with its date,
verbatim substance, and the resulting decision.*

| Date | From | Substance | Action taken |
| --- | --- | --- | --- |
| | | | |

### 7.1 ICPSR

*Awaiting reply.*

### 7.2 Christoph Nolte

*Awaiting reply.*

---

## 8. Contingency positions

Ordered by preference. Each should be evaluated only if those above it fail.

1. **Nolte supplies or points to existing per-year estimates.** Cheapest,
   fastest, and methodologically the safest, since the estimates would be
   internally consistent with the 2010 surface we have already replicated.
   Depends entirely on enquiry 2.
2. **ICPSR access at the non-member fee, re-estimate for 2000–2020.** The
   principal planned route. Costs money and time, imposes the storage
   constraints in §4, and yields 21 years rather than 25.
3. **Collaboration with a researcher at an ICPSR member institution.** Avoids
   the fee and the non-member queue; introduces a co-authorship and
   data-custody arrangement that would need to be agreed in advance.
4. **Alternative commercial transaction data** (CoreLogic, ATTOM) or county
   assessor bulk downloads. Uncosted, and the coverage and field definitions
   would differ from ZTRAX, so results would not be directly comparable to
   Nolte's.
5. **Narrow the objective to what the deposit supports** — a detailed
   cross-sectional analysis of 2010, with no time dimension. This abandons the
   stated extension and should be treated as the fallback of last resort, but it
   is a genuine fallback: the replication is complete and the 2010 surface is
   usable now.

---

## 9. Open actions

- [ ] Confirm and correct the exact send dates of both enquiries from sent mail.
- [ ] Chase ICPSR if no reply within 10 working days of sending.
- [ ] Chase Nolte if no reply within 10 working days of sending.
- [ ] Identify who at IIIT Delhi can sign an institutional data use agreement,
      and confirm they are willing to, **before** the ICPSR reply arrives — this
      is on the critical path and does not depend on the reply.
- [ ] Establish the IRB / ethics determination route at IIIT Delhi for secondary
      analysis of de-identified records.
- [ ] Confirm whether encrypted non-networked storage is available, and if so
      on which machine — this constrains the entire analysis environment for
      stage 2.
- [ ] Determine who would bear the administration fee if the ICPSR route is
      taken.

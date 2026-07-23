# Quebec Bill 9 legal snapshot

- **Snapshot date:** 2026-07-22
- **Authoritative source:** Sanctioned text, 2026, chapter 11
- **Source:** https://www.publicationsduquebec.gouv.qc.ca/fileadmin/Fichiers_client/lois_et_reglements/LoisAnnuelles/fr/2026/2026C11F.PDF

This note is a research summary, not legal advice. Consult the official French text and any later regulations or amendments.

## Legislative dates

- Presented: June 5, 2026
- Principle adopted: June 10, 2026
- Adopted: June 11, 2026
- Sanctioned: June 11, 2026

## Core restrictions

Section 1 prohibits selling a covered energy drink:

1. to a person under 16;
2. to a person 16 or older when the seller knows the person is buying it for someone under 16.

Section 2 prohibits a person under 16 from buying a covered energy drink for themselves or another person and from falsely claiming to be 16 or older for the purchase.

## Product definition

A drink is generally covered when it contains at least 150 mg of caffeine per litre and other ingredients such as taurine, vitamins, or minerals. Coffee, tea, and specified natural health products are excluded unless regulations provide otherwise. The government may modify product categories by regulation.

## Proof of age

Under section 3, a prospective buyer must, when asked by the seller or employee, prove that they are at least 16. The proof must be a photo identity document issued by a government, a government department, or a public body, and it must show the buyer's name and date of birth.

The seller or employee must refuse the sale when they consider that the document does not prove identity.

### Important modeling implication

The statute does not itself specify a universal challenge age such as challenge-under-25. The `verification_check_rate` therefore remains a policy and implementation parameter requiring evidence.

## Remote and automated sales

Section 4 prohibits sales without the physical presence of both seller or employee and buyer, including Internet and vending-machine sales, except in cases and under conditions set by regulation. A regulation may provide age or identity verification methods that differ from section 3.

### Important modeling implication

Document upload, facial estimation, reusable token, and in-person enrollment are scenario designs, not claims about what Quebec has authorized. They should be updated after regulations are made.

## Inspection and enforcement

Inspectors may conduct control operations and, in defined circumstances, require a person in or leaving a place where energy drinks are sold to prove that they are at least 16 using the section 3 document. The law creates fines for under-16 purchasers, adults, merchants, and obstruction.

## Due diligence

Section 12 provides a due-diligence defence for a prosecution under the first paragraph of section 1 where the defendant proves reasonable efforts to determine age and reasonable grounds to believe the buyer was at least 16.

## Reporting

The minister must publish an implementation follow-up report no later than two years after the law enters into force.

## Commencement

Most provisions enter into force on December 11, 2026. Section 4 and related penal provisions enter into force when the first regulation under section 4 enters into force.

## Open legal-research questions

- What regulations will define remote-sale exceptions and verification?
- What documents will retailers accept in practice?
- Will government guidance specify a challenge policy?
- What due-diligence practices will be expected?
- How will inspectors structure compliance checks?
- How will privacy, consumer-protection, accessibility, and human-rights duties interact with implementation?
- What data will the two-year report contain?

# Research roadmap

## Release target: v0.2 Quebec Evidence Baseline

The local v0.2 release candidate completes the technical and organizational scaffold. It does not complete human-subject research, retailer measurement, vendor testing, or future-regulation analysis.

## P0: Establish direct Quebec operational evidence

1. Estimate covered transactions by product, seller type, channel, time period, and buyer age.
2. Observe or experimentally estimate challenge rates under explicit policies such as challenge-under-21, challenge-under-25, and universal checks.
3. Measure lawful-adult abandonment and false rejection in real workflows.
4. Measure proxy purchase, document borrowing, cross-border purchasing, product substitution, and informal-market switching.
5. Map actual online verification data flows after Quebec adopts section 4 regulations.

## P1: Distributional and accessibility evidence

1. Recruit participants who lack conventional photo ID.
2. Test document and camera workflows with disabled users.
3. Test cognitive accessibility, language access, device constraints, and assisted alternatives.
4. Examine unequal human scrutiny and algorithmic performance across relevant groups.
5. Measure appeal availability, time to resolution, and privacy burden.

## P1: Retailer cost evidence

1. Time verification workflows in convenience stores, groceries, delivery, kiosks, and online checkout.
2. Estimate labour, training, device, integration, support, insurance, and compliance costs.
3. Separate fixed and marginal costs by business size.
4. Measure queue effects, failed transactions, and support contacts.

## P1: Regulatory monitoring

1. Monitor regulations made under section 4.
2. Track implementation guidance and accepted proof documents.
3. Record enforcement protocols, due-diligence guidance, and inspector practices.
4. Update the legal snapshot with dated source hashes.

## P2: Model refinement after evidence collection

1. Replace aggregate substitution with separate product, proxy, geographic, and channel pathways.
2. Add repeated-user cohorts and explicit credential lifecycle states.
3. Add deletion failure and record-duplication scenarios.
4. Add retailer segmentation and queueing effects.
5. Add health-benefit scenarios only when consumption and dose evidence supports them.
6. Add correlation structures where evidence shows linked parameters.

## P2: External validation

Obtain structured review from:

- public-health researchers;
- privacy and civil-liberties researchers;
- accessibility specialists and disabled participants;
- convenience-store, grocery, vending, and online retail operators;
- age-assurance engineers;
- digital-identity and security specialists;
- lawyers familiar with Quebec administrative, privacy, and constitutional law;
- people directly affected by identification barriers.

Track each critique, whether it changes the model, and why.

## Release gate for an empirical v0.3

An empirical release should not be described as evidence-backed until:

- every high-sensitivity parameter has direct or carefully transferred evidence;
- source populations and workflows match the modeled policy closely enough to justify transfer;
- conflicts of interest and vendor-supplied claims are separated;
- distributional and accessibility review has occurred;
- the legal snapshot is current;
- all code, data transformations, and reports are reproducible;
- remaining gaps are visible in both the interface and report.

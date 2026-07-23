# Stakeholder interview protocol

## Status

Prepared for future review. No interviews were conducted in the virtual-machine build.

## Purpose

Identify omitted mechanisms, unrealistic assumptions, implementation constraints, accessibility barriers, privacy risks, and evidence sources relevant to Quebec energy-drink age assurance.

## Ethics and governance

Before recruitment:

- determine whether institutional ethics review is required;
- define data controller, storage, retention, access, and deletion procedures;
- minimize collection of identity and sensitive information;
- avoid recording unless necessary and explicitly consented to;
- provide withdrawal and correction procedures;
- compensate participants fairly where appropriate;
- use community-led or participatory review for groups directly affected by identification barriers.

Do not commit identifiable notes to Git.

## Sampling targets

Use purposive sampling across:

- independent and chain retailers;
- convenience, grocery, vending, delivery, and online channels;
- privacy and civil-liberties researchers;
- accessibility specialists and disabled users;
- people without conventional photo ID;
- public-health researchers;
- age-assurance and digital-identity engineers;
- Quebec legal and regulatory specialists;
- people who are privacy-sensitive or likely to decline biometric processing.

## Interview length

45 to 60 minutes.

## Core questions for all participants

1. What does the current model misunderstand or omit?
2. Which implementation decision most changes real-world effectiveness?
3. Which lawful users are most likely to be blocked, delayed, deterred, or surveilled?
4. What circumvention or substitution pathways are most plausible?
5. What data would be processed, retained, linked, or disclosed?
6. Which costs are absent or assigned to the wrong actor?
7. What direct evidence exists, and how transferable is it to Quebec and a threshold of 16?
8. What outcome would convince you that the policy is working or failing?
9. What safeguard or alternative should be mandatory?
10. Which model parameter should be researched first?

## Retailer module

- Describe the purchase and challenge workflow step by step.
- Who decides when to ask for ID?
- What documents are accepted?
- How often is a manager called?
- What happens when a customer has no acceptable document?
- What is the time cost at peak periods?
- What training, equipment, integration, and support are required?
- What happens to online, delivery, and vending sales?
- Which costs are fixed versus transaction-level?
- How might small and large retailers differ?

## Affected-user module

- Describe a typical low-value purchase involving age assurance.
- What document, device, travel, assistance, or disclosure would be required?
- Which steps would be difficult, inaccessible, unsafe, or unacceptable?
- What alternative would allow completion with less burden?
- How should an appeal work?
- What would you do after a block or failed attempt?
- What privacy or dignity harms are not captured by a count of denials?

## Technical-provider module

- Draw the complete data flow, including logs and subcontractors.
- Separate routine assertions from full identity proofing.
- State all threshold-specific error measures.
- Describe retry, fallback, human review, and appeal.
- State retention and deletion rules for successful, failed, and abandoned attempts.
- Explain linkability, fraud controls, liveness, model training, and secondary use.
- Identify independent evaluations and known group-specific performance limits.

## Closing

Ask the participant to rank the three most important research gaps and offer to send a non-identifiable summary for correction.

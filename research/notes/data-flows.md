# Data-flow research plan

## Required artifact

For each real implementation, create a data-flow diagram and table covering:

1. user device or point-of-sale terminal;
2. retailer or relying party;
3. age-assurance provider;
4. document or identity-data provider;
5. biometric processor;
6. cloud, analytics, logging, fraud, and support vendors;
7. wallet or credential issuer;
8. auditors, regulators, and law enforcement where applicable.

## Data elements

- document image and extracted fields;
- face image or video;
- biometric template or age estimate;
- name, date of birth, address, document number;
- device, IP, location, and transaction metadata;
- yes/no age assertion;
- token identifiers and revocation data;
- logs, support records, and appeal material.

## Questions

- Is the item collected, inferred, transmitted, retained, or merely displayed?
- Who controls each copy?
- Is encryption end-to-end or only in transit?
- Can transactions be linked across visits or retailers?
- What is the retention period and deletion verification process?
- Is data used for fraud, analytics, training, advertising, or law enforcement?
- What happens on failed or abandoned attempts?
- What data survives account deletion or token revocation?

## Model mapping

Map findings to `identity_proofing_rate`, `records_per_identity_proof`, `centralized_record_fraction`, `record_retention_years`, `transient_images_per_identity_proof`, `biometric_scans_per_identity_proof`, `age_assertions_per_check`, and disclosure fields.

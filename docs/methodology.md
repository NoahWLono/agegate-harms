# Methodology

## Research question

How do alternative age-verification approaches trade off underage purchase prevention against adult access errors, deterrence, privacy exposure, distributional burden, and implementation cost?

## Status of version 0.1

Version 0.1 is an executable model demonstration. All numerical inputs are illustrative assumptions. It is not an empirical evaluation of Quebec, an existing statute, a specific retailer, or a named verification vendor.

## Unit of analysis

The model describes annual attempted purchases in a hypothetical population. A scenario specifies population size, the share making a relevant purchase attempt, the share of attempts made by minors, and the share of adult attempts made by people who face elevated verification friction.

## Access model

For minors:

1. The verification method initially detects and blocks a fraction of attempts.
2. A fraction of initially blocked attempts circumvents the method.
3. Purchases prevented equal initial blocks minus circumvention.

For adults:

1. Adults are divided into a general group and a higher-friction group.
2. Some abandon because of verification friction.
3. Some remaining adults are falsely rejected.
4. The higher-friction group can have elevated abandonment and rejection rates through explicit multipliers.

The model conserves all minor and adult purchase attempts.

## Privacy model

The method specifies the share of transactions checked, records created per completed check, centralized fraction, third-party disclosures, biometric scans, and an annual breach probability. “Expected records exposed” is records created multiplied by breach probability. This simple expectation does not model correlated or catastrophic breaches.

## Cost model

Annual cost equals completed checks multiplied by variable cost per check, plus fixed annual cost. The model reports cost per minor purchase prevented where prevention is nonzero.

## Uncertainty

Uncertain values use triangular distributions defined by a low, mode, and high value. Methods share the same sampled scenario draw in each Monte Carlo iteration. Method parameters are otherwise sampled independently. This is an auditable convenience model, not a claim that the real parameters are triangular or independent.

## Core outputs

- Minor purchases prevented and permitted
- Adults correctly permitted
- Adult false rejections and abandonments
- Adverse outcomes among higher-friction adults
- Verification checks
- Identity records and centralized records
- Expected records exposed
- Third-party disclosures and biometric scans
- Annual cost
- Burden, check, record, and cost ratios per minor purchase prevented

## Required next step before policy use

Every parameter must be associated with an evidence record, source type, jurisdiction, population, date, uncertainty interval, and limitations. Vendor claims should be labeled separately from independent measurements. Where evidence is unavailable, the interface should visibly retain the parameter as an analyst-selected assumption.

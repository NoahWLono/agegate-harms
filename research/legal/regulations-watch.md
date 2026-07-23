# Regulations and implementation watch

**Status as of 2026-07-22:** The sanctioned law states that section 4 remote-sales provisions take effect with the first regulation made under section 4. This project has not registered such a regulation as in force.

## Authoritative sources to monitor

The source list is in `data/regulatory_sources.csv` and includes:

- the sanctioned law;
- National Assembly legislative history;
- Quebec government implementation information.

Run:

```bash
python scripts/watch_regulations.py --initialize
python scripts/watch_regulations.py
```

The watcher stores URL hashes in `research/legal/regulatory_state.json`. A change means only that the retrieved bytes changed. Review the official source manually.

## Change log template

| Review date | Source | Change detected | Legal effect confirmed | Model or evidence update | Reviewer |
|---|---|---|---|---|---|
| 2026-07-22 | Initial legal snapshot | Baseline | Most provisions effective 2026-12-11; section 4 awaits regulation | v0.2 baseline | Project maintainer |

## Questions for each new regulation

1. What transactions and channels are covered?
2. What exceptions are created?
3. What age or identity assurance methods are permitted or required?
4. Is a specific assurance level, challenge policy, or accepted-document list defined?
5. What data may be collected, retained, disclosed, or reused?
6. Must a non-biometric or offline alternative be available?
7. What appeal or remediation process exists?
8. What audit, certification, reporting, and breach obligations apply?
9. When does the regulation enter into force?
10. Which model parameters must change, and what evidence supports the change?

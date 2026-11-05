# RAFAELIA Ω — catálogos públicos

**Role:** a minimal, auditable inventory of public capabilities and evidence gaps.
This repository does **not** collect private project data, credentials, raw logs,
chat exports, phone identities, private repo names or original source files.

- **catalogos:** what a feature is, which public producer owns it, its state and source reference.
- **[conhecimentos](https://github.com/rafaelmeloreisnovo/conhecimentos):** evidence-envelope format, falsifiers and what a claim is allowed to mean.
- **[RafGitTools](https://github.com/rafaelmeloreisnovo/RafGitTools):** the actual Android implementation and provider executor.

The current sample tracks a user-reported PAT login/profile refresh gap and the
candidate local device proof exporter. A user report is not a reproduced bug.
An Android self-report is not independent hardware/device attestation.

## Check with no PAT and no corpus

```bash
python3 -I -B -m unittest discover -s tests -p 'test_*.py' -v
python3 -I -B scripts/validate_catalog.py
```

GitHub Actions runs these tests with `contents: read` only and no artifacts
uploaded. A green run proves only the public catalog contract, not Android E2E.
To add a capability, modify a public metadata JSON in `catalog/` on a draft
branch, preserving the producer's authority and `claim_allowed=false`.

## Trust model

`SOURCE ≠ ARTIFACT ≠ EXECUTION ≠ EVIDENCE ≠ CLAIM`.
`TOKEN_VAZIO` is not zero, FAIL or PASS.
Real receipts default to a **private** destination. Never upload raw
screenshots, Android logs or personal account information to public issues.

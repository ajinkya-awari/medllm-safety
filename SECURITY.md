# Security and Privacy

## Supported scope

This repository accepts synthetic fixtures only. It has no supported model, provider, patient-data, deployment, or clinical runtime.

## Reporting a problem

Open a GitHub issue with the smallest synthetic reproduction. Do not include patient data, clinical notes, identifiers, credentials, provider responses, private logs, model weights, checkpoints, or restricted datasets.

For a suspected secret exposure, revoke the credential through its provider before reporting. Do not paste the secret into an issue.

## Design boundaries

- External actions fail closed by default.
- Redaction never authorizes real PHI processing.
- Logs contain decision metadata only.
- Model substitutions must be explicit and cannot be reported as independent comparisons.
- No synthetic test result supports a clinical, regulatory, efficacy, fairness, or deployment conclusion.

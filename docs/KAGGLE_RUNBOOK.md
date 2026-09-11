# Kaggle Synthetic Validation Runbook

Notebook: `kaggle_medllm_safety.ipynb`
Kaggle notebook folder: this scanned public export root, represented below as `<PUBLIC_EXPORT_PATH>`

## Safety boundary

This is a private, provider-free synthetic validation run with no GPU, no internet, no dataset sources, no competition sources, and no kernel sources. It must not receive patient data, clinical notes, medical identifiers, model weights, provider credentials, or generated model responses.

## Pre-push checks

1. Build the public export through the allowlist.
2. Rebuild the self-contained notebook from that export.
3. Verify `kernel-metadata.json` references `kaggle_medllm_safety.ipynb`.
4. Run the complete public-export scans and local synthetic command.
5. Confirm the evidence output folder is outside the public export.

## Notebook sequence

1. Embedded source package extraction into a dedicated Kaggle working directory.
2. Source-tree validation.
3. Restricted-artifact scan.
4. Environment and dependency version inspection.
5. Compile check with bytecode redirected outside the source tree.
6. Synthetic pytest suite with cache writing disabled.
7. Four-sample bounded policy smoke test covering allow, refuse, abstain, and escalate.
8. Sanitized evidence JSON creation.
9. Evidence schema and JSON round-trip inspection.
10. Stop at the approval gate.

## Bounded CLI sequence

```powershell
kaggle kernels push -p "<PUBLIC_EXPORT_PATH>"
kaggle kernels status ajinkya1225/project-11-medllm-safety-synthetic-validation
kaggle kernels logs ajinkya1225/project-11-medllm-safety-synthetic-validation
kaggle kernels output ajinkya1225/project-11-medllm-safety-synthetic-validation -p "<DEDICATED_OUTPUT_FOLDER>"
```

The required metadata title normalized to the canonical remote slug `project-11-medllm-safety-synthetic-validation` when Kaggle created the kernel. Use the server-returned slug for status, logs, and output retrieval.

Poll status for at most 20 attempts with a 15-second interval. Stop polling on `complete`, `error`, `cancel`, or `failure`. Do not use an endless follower or background process.

If the first run fails, inspect only the sanitized log, identify the first error, apply at most one targeted repair, and rerun the required bounded check once. Stop after a second failure.

## Required evidence

The downloaded `synthetic-validation-evidence.json` must record UTC time, source tree revision, configuration hash, Python and pytest versions, CPU device, seed, synthetic sample count, test count, exit code, relative evidence path, restricted-artifact count, provider/API use as `none`, and model inference as `not_run`.

No real model, benchmark, patient, clinical, fairness, efficacy, deployment, regulatory, or real-world safety result is produced.

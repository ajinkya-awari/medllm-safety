# Project 11 Dataset Smoke Approval Record

This record prepares the future first approved Kaggle smoke run. It is local-only and does not authorize access. The candidate below has been reviewed from public source pages only; no dataset file has been downloaded, loaded, or checksummed.

## Target

- Type: dataset
- Identifier: openlifescienceai/MedQA-USMLE-4-options-hf
- Revision/path: `main` observed; short source-page revision `20a8f4d`; immutable commit SHA or approved local path required before access
- Licence: not_listed_on_inspected_source_page
- Checksum: not_computed
- Source URL or location: https://huggingface.co/datasets/openlifescienceai/MedQA-USMLE-4-options-hf
- Split: train, validation, test observed on source page
- Candidate status: source-reviewed; not access-approved

## Review

- Remote code required: not reviewed; no loader executed
- Remote code revision reviewed: not applicable until the exact source package is inspected in the approved environment
- Storage location: none approved; after approval, record the exact read-only dataset path under `/kaggle/input/` or an explicitly approved local equivalent
- Expected compute: not_approved
- Compute limit: proposed smoke ceiling (not approved): one dataset, one bounded split sample with `sample_limit=2`, no preprocessing beyond schema validation, and no overnight or unbounded job
- Dependency compatibility: not verified; before access, record the existing approved-environment Python/package versions and verify loader/schema compatibility without installing locally
- Evaluator compatibility: source page shows MCQ-shaped fields `id`, `sent1`, `sent2`, `ending0`-`ending3`, and `label`; local schema mapping still must be verified without claiming benchmark results
- Schema compatibility check: verify field names, answer-label domain, split selection, row count, and exclusion handling against the local benchmark contract after approval; record failures as excluded/not-run
- Seed and sample-size plan: use config seed `17` and bounded `sample_limit=2`; record requested, observed, valid, invalid, and excluded counts. These are planned values, not observed dataset counts.
- Missing-data/failure handling: do not impute missing questions, choices, labels, or IDs; exclude and count malformed rows with a reason, fail closed on schema mismatch, and preserve no raw text in local evidence
- Fallback allowed: no

## Decision

- Status: requested
- Approver: not_recorded
- Date: not_recorded
- Conditions: full pinned revision, licence/access terms decision, checksum plan, storage path, dependency compatibility, schema mapping, sample limit, and remote-code decision required before access
- Ready for external access: no

## Blockers

- Explicit approval is not recorded.
- Full pinned dataset revision has not been recorded.
- Licence was not listed on the inspected source page and still requires review.
- Checksum has not been computed.
- Dataset files have not been downloaded, loaded, or inspected locally.
- Remote-code policy has not been reviewed for execution.

## Source Review Notes

- Source reviewed: Hugging Face dataset card and README for `openlifescienceai/MedQA-USMLE-4-options-hf`.
- Observed format: parquet.
- Observed splits: train, validation, test.
- Observed row counts: train 10178, validation 1272, test 1273.
- Observed fields: `id`, `sent1`, `sent2`, `ending0`, `ending1`, `ending2`, `ending3`, `label`.
- Licence status: not visible in inspected source text; must be resolved before access.
- Source review date: 2026-08-27.

## Access and integrity plan

- Licence/access decision: no access approval. The inspected page did not state a licence; a primary-source terms review and explicit approver decision are required before any file access.
- Checksum plan: after explicit approval and download, compute SHA-256 for every retained file plus a sorted manifest of relative path, byte size, and digest; record the command and date. Current value remains `not_computed`.
- Approved storage location: none at this stage. The exact approved read-only input path and any separate derived-output path must be recorded before download; repository storage is prohibited.
- Stop on: missing immutable revision, unresolved licence, checksum failure, unexpected file, schema mismatch, private/restricted text, or any request for remote code, inference, upload, or publication.

## Stop Rule

Do not download, load, infer, upload, publish, deploy, email, commit, or push from this record alone. Do not use patient data, private clinical text, restricted clinical data, or licensed data outside its approved terms.

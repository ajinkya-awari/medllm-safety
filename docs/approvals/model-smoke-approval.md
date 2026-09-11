# Project 11 Model Smoke Approval Record

This record prepares the future first approved Kaggle smoke run. It is local-only and does not authorize model access. The candidate below has been reviewed from public source pages only; no model file has been downloaded, loaded, inferred with, or checksummed.

## Target

- Type: model
- Identifier: distilbert/distilgpt2
- Revision/path: `main` observed; immutable commit SHA or approved local path required before access
- Licence: apache-2.0 observed on model card
- Checksum: not_computed
- Source URL or location: https://huggingface.co/distilbert/distilgpt2
- Capability route: causal_lm candidate for constrained choice scoring
- Architecture observed: GPT2LMHeadModel
- Candidate status: source-reviewed; not access-approved

## Review

- Remote code required: not reviewed; no loader executed
- Remote code revision reviewed: not applicable until the exact checkpoint source is inspected in the approved environment
- Storage location: none approved; after approval, record the exact read-only model path under `/kaggle/input/` or an explicitly approved local equivalent
- Expected compute: not_approved
- Compute limit: proposed smoke ceiling (not approved): one checkpoint, one sequential load, `sample_limit=2`, one short constrained-choice pass, one GPU at most, and a 15-minute wall-clock cap; no training, batching expansion, or overnight job
- Dependency compatibility: not verified; before access, record approved Python/PyTorch/Transformers/tokenizer versions and verify compatibility without installing locally
- Evaluator compatibility: source config shows `GPT2LMHeadModel` and `model_type: gpt2`; candidate route is constrained choice scoring after tokenizer/checkpoint verification
- Capability/tokenizer/head checks: inspect the exact config and checkpoint file set; confirm causal-LM head, tokenizer files, vocabulary/special-token alignment, choice-tokenization behavior, device/dtype support, and that the adapter exposes constrained choice scoring. Reject the checkpoint if any check fails; never route it through a classifier-only adapter.
- Seed and sample-size plan: use config seed `17` and bounded `sample_limit=2`; record requested, observed, valid, invalid, and excluded counts. No model output or runtime count has been observed.
- Missing-data/failure handling: fail closed on missing tokenizer/config/weights, incompatible head, load error, OOM, timeout, invalid output, or provenance mismatch; record only sanitized error metadata and never retain raw responses.
- Fallback allowed: no

## Decision

- Status: requested
- Approver: not_recorded
- Date: not_recorded
- Conditions: full pinned revision/path, tokenizer/head verification, checksum plan, fallback policy, dependency compatibility, memory estimate, and compute limit required before loading
- Ready for external access: no

## Blockers

- Explicit approval is not recorded.
- Full pinned model revision or path has not been recorded.
- Checksum has not been computed.
- Model files have not been downloaded, loaded, or inspected locally.
- Tokenizer and full checkpoint file set have not been inspected.
- Evaluator compatibility is provisional until the approved environment verifies tokenizer/checkpoint behavior.
- Fallback is not allowed without separate approval and non-comparable labeling.

## Source Review Notes

- Source reviewed: Hugging Face model card and config for `distilbert/distilgpt2`.
- Observed model type: Transformer-based language model.
- Observed architecture in config: `GPT2LMHeadModel`.
- Observed config model type: `gpt2`.
- Observed language: English.
- Observed licence: Apache 2.0 / apache-2.0.
- Observed size statement: 82 million parameters on model card.
- Source review date: 2026-08-27.

## Access and integrity plan

- Licence/access decision: Apache 2.0 is observed on the model card, but no access approval is recorded. Confirm the applicable terms for the exact pinned revision and obtain explicit approval before loading.
- Checksum plan: after explicit approval and download, compute SHA-256 for every retained checkpoint/tokenizer file plus a sorted manifest of relative path, byte size, and digest; record the command and date. Current value remains `not_computed`.
- Approved storage location: none at this stage. The exact approved read-only input path and separate derived-output path must be recorded before download; repository storage is prohibited.
- Stop on: missing immutable revision, tokenizer/head mismatch, unresolved terms, checksum failure, unexpected file, OOM, timeout, fallback request, or any provider/upload/publication action.

## Stop Rule

Do not download, load, infer, upload, publish, deploy, email, commit, or push from this record alone. Do not treat a fallback model as an independent comparison result.

import pytest
from pathlib import Path

from medllm_safety.approvals import ApprovalRecord, ApprovalStatus, validate_approval_record


def test_dataset_approval_record_can_be_prepared_without_access():
    record = ApprovalRecord(
        target_type="dataset",
        target_id="public-benchmark-placeholder",
        revision="not_accessed",
        license="not_reviewed",
        checksum="not_computed",
        status=ApprovalStatus.NOT_REQUESTED,
    )

    result = validate_approval_record(record)

    assert result.ready_for_external_access is False
    assert "explicit approval is not recorded" in result.blockers


def test_approved_record_requires_revision_license_and_checksum():
    record = ApprovalRecord(
        target_type="model",
        target_id="checkpoint-placeholder",
        revision="",
        license="",
        checksum="",
        status=ApprovalStatus.APPROVED,
    )

    with pytest.raises(ValueError, match="revision"):
        validate_approval_record(record)


def test_local_markdown_approval_records_are_requested_but_not_approved():
    for path in [
        Path("docs/approvals/dataset-smoke-approval.md"),
        Path("docs/approvals/model-smoke-approval.md"),
    ]:
        text = path.read_text(encoding="utf-8").lower()

        assert "status: requested" in text
        assert "full pinned" in text
        assert "checksum: not_computed" in text
        assert "ready for external access: no" in text
        assert "do not download, load, infer, upload, publish, deploy, email, commit, or push" in text


def test_local_markdown_approval_records_record_unverified_candidates_only():
    dataset = Path("docs/approvals/dataset-smoke-approval.md").read_text(encoding="utf-8").lower()
    model = Path("docs/approvals/model-smoke-approval.md").read_text(encoding="utf-8").lower()

    assert "identifier: openlifescienceai/medqa-usmle-4-options-hf" in dataset
    assert "source url or location: https://huggingface.co/datasets/openlifescienceai/medqa-usmle-4-options-hf" in dataset
    assert "split: train, validation, test observed on source page" in dataset
    assert "licence: not_listed_on_inspected_source_page" in dataset
    assert "candidate status: source-reviewed; not access-approved" in dataset

    assert "identifier: distilbert/distilgpt2" in model
    assert "licence: apache-2.0 observed on model card" in model
    assert "capability route: causal_lm candidate for constrained choice scoring" in model
    assert "source url or location: https://huggingface.co/distilbert/distilgpt2" in model
    assert "candidate status: source-reviewed; not access-approved" in model
    assert "architecture observed: gpt2lmheadmodel" in model
    assert "fallback allowed: no" in model


def test_source_reviewed_records_still_block_access_until_checksum_and_approval():
    combined = "\n".join(
        path.read_text(encoding="utf-8").lower()
        for path in [
            Path("docs/approvals/dataset-smoke-approval.md"),
            Path("docs/approvals/model-smoke-approval.md"),
        ]
    )

    assert "status: requested" in combined
    assert "checksum: not_computed" in combined
    assert "ready for external access: no" in combined
    assert "explicit approval is not recorded" in combined

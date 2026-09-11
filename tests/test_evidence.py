import json
from pathlib import Path

import pytest

from medllm_safety.evidence import (
    build_synthetic_evidence,
    canonical_sha256,
    find_restricted_artifacts,
    source_tree_revision,
    validate_evidence_manifest,
)


def test_canonical_hash_and_source_revision_are_deterministic(tmp_path):
    (tmp_path / "medllm_safety").mkdir()
    (tmp_path / "medllm_safety" / "example.py").write_text("VALUE = 1\n", encoding="utf-8")

    assert canonical_sha256({"b": 2, "a": 1}) == canonical_sha256({"a": 1, "b": 2})
    assert source_tree_revision(tmp_path) == source_tree_revision(tmp_path)
    assert source_tree_revision(tmp_path).startswith("tree-sha256:")


def test_restricted_artifact_scan_detects_secrets_models_and_caches(tmp_path):
    (tmp_path / ".env").write_text("EXAMPLE=synthetic\n", encoding="utf-8")
    (tmp_path / "weights.safetensors").write_bytes(b"fixture")
    cache = tmp_path / "__pycache__"
    cache.mkdir()
    (cache / "module.pyc").write_bytes(b"fixture")

    findings = find_restricted_artifacts(tmp_path)

    assert {finding.rule for finding in findings} == {"secret_file", "model_or_data_artifact", "cache_artifact"}


def test_synthetic_evidence_contains_required_sanitized_fields(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "module.py").write_text("VALUE = 1\n", encoding="utf-8")

    evidence = build_synthetic_evidence(
        source_root=source,
        configuration={"seed": 17, "mode": "synthetic"},
        dependency_versions={"python": "3.11.9", "pytest": "9.0.3"},
        seed=17,
        synthetic_sample_count=6,
        test_count=49,
        exit_code=0,
        evidence_path="evidence/kaggle-synthetic-validation.json",
        restricted_artifact_count=0,
        utc_timestamp="2026-09-11T00:00:00Z",
    )

    validate_evidence_manifest(evidence)
    assert evidence["device"] == "cpu"
    assert evidence["provider_api_usage"] == "none"
    assert evidence["model_inference"] == "not_run"
    assert not Path(evidence["evidence_path"]).is_absolute()
    assert "source_revision" in evidence
    assert "configuration_hash" in evidence


def test_evidence_rejects_absolute_paths_and_provider_usage():
    base = {
        "utc_timestamp": "2026-09-11T00:00:00Z",
        "source_revision": "tree-sha256:" + "a" * 64,
        "configuration_hash": "sha256:" + "b" * 64,
        "dependency_versions": {"python": "3.11.9"},
        "device": "cpu",
        "seed": 17,
        "synthetic_sample_count": 1,
        "test_count": 1,
        "exit_code": 0,
        "evidence_path": "evidence/result.json",
        "restricted_artifact_count": 0,
        "provider_api_usage": "none",
        "model_inference": "not_run",
    }

    invalid_path = dict(base, evidence_path="C:\\private\\result.json")
    with pytest.raises(ValueError, match="relative"):
        validate_evidence_manifest(invalid_path)

    invalid_provider = dict(base, provider_api_usage="used")
    with pytest.raises(ValueError, match="provider/API usage"):
        validate_evidence_manifest(invalid_provider)


def test_evidence_round_trips_as_json(tmp_path):
    evidence = build_synthetic_evidence(
        source_root=tmp_path,
        configuration={"seed": 17},
        dependency_versions={"python": "3.11.9"},
        seed=17,
        synthetic_sample_count=4,
        test_count=1,
        exit_code=0,
        evidence_path="evidence/result.json",
        restricted_artifact_count=0,
        utc_timestamp="2026-09-11T00:00:00Z",
    )

    assert json.loads(json.dumps(evidence)) == evidence

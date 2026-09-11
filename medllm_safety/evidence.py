from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path, PureWindowsPath
import re
from typing import Any


@dataclass(frozen=True)
class RestrictedArtifactFinding:
    path: str
    rule: str


_SECRET_NAMES = {".env", ".env.local", ".envrc", "credentials.json", "kaggle.json", "secrets.json"}
_MODEL_DATA_SUFFIXES = {".bin", ".ckpt", ".csv", ".jsonl", ".onnx", ".parquet", ".pt", ".pth", ".safetensors"}
_CACHE_NAMES = {".pytest_cache", "__pycache__"}
_HASH = re.compile(r"^(?:tree-)?sha256:[0-9a-f]{64}$")
_REQUIRED_EVIDENCE_KEYS = {
    "utc_timestamp",
    "source_revision",
    "configuration_hash",
    "dependency_versions",
    "device",
    "seed",
    "synthetic_sample_count",
    "test_count",
    "exit_code",
    "evidence_path",
    "restricted_artifact_count",
    "provider_api_usage",
    "model_inference",
}


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=True, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def source_tree_revision(root: Path) -> str:
    root = root.resolve()
    digest = hashlib.sha256()
    for path in sorted((item for item in root.rglob("*") if item.is_file()), key=lambda item: item.as_posix()):
        relative = path.relative_to(root)
        if any(part in _CACHE_NAMES or part == ".git" for part in relative.parts):
            continue
        digest.update(relative.as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return "tree-sha256:" + digest.hexdigest()


def find_restricted_artifacts(root: Path) -> list[RestrictedArtifactFinding]:
    root = root.resolve()
    findings: list[RestrictedArtifactFinding] = []
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(root)
        parts = set(relative.parts)
        if parts & _CACHE_NAMES:
            if path.is_file():
                findings.append(RestrictedArtifactFinding(relative.as_posix(), "cache_artifact"))
            continue
        if not path.is_file():
            continue
        lowered_name = path.name.lower()
        if lowered_name in _SECRET_NAMES or lowered_name.startswith(".env."):
            findings.append(RestrictedArtifactFinding(relative.as_posix(), "secret_file"))
        elif path.suffix.lower() in _MODEL_DATA_SUFFIXES:
            findings.append(RestrictedArtifactFinding(relative.as_posix(), "model_or_data_artifact"))
    return findings


def build_synthetic_evidence(
    *,
    source_root: Path,
    configuration: dict[str, object],
    dependency_versions: dict[str, str],
    seed: int,
    synthetic_sample_count: int,
    test_count: int,
    exit_code: int,
    evidence_path: str,
    restricted_artifact_count: int,
    utc_timestamp: str | None = None,
) -> dict[str, object]:
    evidence = {
        "utc_timestamp": utc_timestamp or datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z"),
        "source_revision": source_tree_revision(source_root),
        "configuration_hash": canonical_sha256(configuration),
        "dependency_versions": dict(sorted(dependency_versions.items())),
        "device": "cpu",
        "seed": seed,
        "synthetic_sample_count": synthetic_sample_count,
        "test_count": test_count,
        "exit_code": exit_code,
        "evidence_path": evidence_path,
        "restricted_artifact_count": restricted_artifact_count,
        "provider_api_usage": "none",
        "model_inference": "not_run",
    }
    validate_evidence_manifest(evidence)
    return evidence


def validate_evidence_manifest(evidence: dict[str, object]) -> None:
    missing = _REQUIRED_EVIDENCE_KEYS - set(evidence)
    if missing:
        raise ValueError(f"evidence missing required keys: {sorted(missing)}")
    for name in ("source_revision", "configuration_hash"):
        value = evidence[name]
        if not isinstance(value, str) or not _HASH.fullmatch(value):
            raise ValueError(f"{name} must be a SHA-256 identifier")
    timestamp = evidence["utc_timestamp"]
    if not isinstance(timestamp, str) or not timestamp.endswith("Z"):
        raise ValueError("utc_timestamp must be an ISO-8601 UTC value ending in Z")
    versions = evidence["dependency_versions"]
    if not isinstance(versions, dict) or not versions or any(not isinstance(key, str) or not isinstance(value, str) for key, value in versions.items()):
        raise ValueError("dependency_versions must be a non-empty string mapping")
    for name in ("seed", "synthetic_sample_count", "test_count", "restricted_artifact_count"):
        value = evidence[name]
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{name} must be a non-negative integer")
    if isinstance(evidence["exit_code"], bool) or not isinstance(evidence["exit_code"], int):
        raise ValueError("exit_code must be an integer")
    evidence_path = evidence["evidence_path"]
    if not isinstance(evidence_path, str) or not evidence_path or Path(evidence_path).is_absolute() or PureWindowsPath(evidence_path).is_absolute() or ".." in Path(evidence_path).parts:
        raise ValueError("evidence_path must be a safe relative path")
    if evidence["device"] != "cpu":
        raise ValueError("synthetic validation device must be cpu")
    if evidence["provider_api_usage"] != "none":
        raise ValueError("provider/API usage must be none")
    if evidence["model_inference"] != "not_run":
        raise ValueError("model inference must remain not_run")

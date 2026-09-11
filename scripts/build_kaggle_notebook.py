from __future__ import annotations

import argparse
import base64
import hashlib
from io import BytesIO
import json
from pathlib import Path
import textwrap
import zipfile


ROOT_FILES = {"pyproject.toml", "run_audit.py", "run_synthetic_validation.py"}
SOURCE_DIRECTORIES = {
    "configs",
    "docs/approvals",
    "fixtures",
    "medllm_safety",
    "project_preflight",
    "tests",
}
EXCLUDED_TESTS = {"tests/test_kaggle_preparation.py"}
EXCLUDED_PARTS = {".git", ".pytest_cache", "__pycache__"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo"}


def collect_source_files(root: Path) -> list[Path]:
    selected: set[Path] = set()
    for name in ROOT_FILES:
        path = root / name
        if path.is_file():
            selected.add(path)
    for name in SOURCE_DIRECTORIES:
        directory = root / name
        if not directory.exists():
            continue
        for path in directory.rglob("*"):
            if not path.is_file():
                continue
            relative = path.relative_to(root).as_posix()
            if relative in EXCLUDED_TESTS:
                continue
            if set(path.relative_to(root).parts) & EXCLUDED_PARTS:
                continue
            if path.suffix.lower() in EXCLUDED_SUFFIXES:
                continue
            selected.add(path)
    return sorted(selected, key=lambda item: item.relative_to(root).as_posix())


def build_source_archive(root: Path) -> bytes:
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in collect_source_files(root):
            relative = path.relative_to(root).as_posix()
            info = zipfile.ZipInfo(relative, date_time=(2026, 9, 11, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())
    return buffer.getvalue()


def markdown(source: str) -> dict[str, object]:
    return {"cell_type": "markdown", "metadata": {}, "source": source.splitlines(keepends=True)}


def code(source: str) -> dict[str, object]:
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": textwrap.dedent(source).strip().splitlines(keepends=True),
    }


def build_notebook(root: Path) -> dict[str, object]:
    archive = build_source_archive(root)
    encoded = base64.b64encode(archive).decode("ascii")
    chunks = "\n".join(f'    "{encoded[index:index + 100]}"' for index in range(0, len(encoded), 100))
    archive_hash = hashlib.sha256(archive).hexdigest()
    file_count = len(collect_source_files(root))

    cells = [
        markdown(
            "# Purpose And Safety Boundary\n\n"
            "This private Kaggle notebook validates a source-only, provider-free synthetic safety fixture on CPU. "
            "It uses no patient data, clinical dataset, model weights, provider API, internet, GPU, inference, or training."
        ),
        code(
            f'''# Embedded Source Package Extraction
import base64
import hashlib
from io import BytesIO
import json
from pathlib import Path, PurePosixPath
import sys
import zipfile

SOURCE_ARCHIVE_SHA256 = "{archive_hash}"
SOURCE_FILE_COUNT = {file_count}
SOURCE_ARCHIVE_B64 = (
{chunks}
)
WORK_ROOT = Path("/kaggle/working/medllm-safety-public")
sys.dont_write_bytecode = True
if WORK_ROOT.exists():
    raise RuntimeError("Dedicated extraction directory already exists; restart the kernel before rerunning.")
archive_bytes = base64.b64decode(SOURCE_ARCHIVE_B64, validate=True)
if hashlib.sha256(archive_bytes).hexdigest() != SOURCE_ARCHIVE_SHA256:
    raise RuntimeError("Embedded source archive hash mismatch.")
with zipfile.ZipFile(BytesIO(archive_bytes)) as archive:
    for member in archive.infolist():
        candidate = PurePosixPath(member.filename)
        if candidate.is_absolute() or ".." in candidate.parts:
            raise RuntimeError("Unsafe embedded archive path.")
    archive.extractall(WORK_ROOT)
print(json.dumps({{"source_files": SOURCE_FILE_COUNT, "work_root": str(WORK_ROOT), "archive_sha256": SOURCE_ARCHIVE_SHA256}}, indent=2))'''
        ),
        code(
            '''# Source-Tree Validation
sys.path.insert(0, str(WORK_ROOT))
from medllm_safety.synthetic_validation import validate_source_tree

source_errors = validate_source_tree(WORK_ROOT)
print(json.dumps({"status": "passed" if not source_errors else "failed", "errors": source_errors}, indent=2))'''
        ),
        code(
            '''# Restricted-Artifact Scan
from medllm_safety.evidence import find_restricted_artifacts

restricted = find_restricted_artifacts(WORK_ROOT)
print(json.dumps({"restricted_artifact_count": len(restricted), "rules": sorted({item.rule for item in restricted})}, indent=2))'''
        ),
        code(
            '''# Environment And Version Inspection
from medllm_safety.synthetic_validation import dependency_versions
import platform

versions = dependency_versions()
environment_summary = {"dependency_versions": versions, "device": "cpu", "platform": platform.platform(), "gpu_used": False}
print(json.dumps(environment_summary, indent=2, sort_keys=True))'''
        ),
        code(
            '''# Compile Check
import os
import subprocess

command_environment = os.environ.copy()
command_environment["PYTHONDONTWRITEBYTECODE"] = "1"
command_environment["PYTHONPYCACHEPREFIX"] = "/kaggle/working/medllm-safety-pycache"
compile_process = subprocess.run(
    [sys.executable, "-m", "compileall", "-q", "medllm_safety", "project_preflight", "tests"],
    cwd=WORK_ROOT,
    env=command_environment,
    capture_output=True,
    text=True,
    timeout=120,
    check=False,
)
print(json.dumps({"step": "compile_check", "exit_code": compile_process.returncode}, indent=2))'''
        ),
        code(
            '''# Synthetic Test Suite
from medllm_safety.synthetic_validation import parse_pytest_count

test_process = subprocess.run(
    [sys.executable, "-m", "pytest", "-p", "no:cacheprovider"],
    cwd=WORK_ROOT,
    env=command_environment,
    capture_output=True,
    text=True,
    timeout=120,
    check=False,
)
test_output = "\\n".join(part.strip() for part in (test_process.stdout, test_process.stderr) if part.strip())
print(test_output)
try:
    test_count = parse_pytest_count(test_output)
except ValueError:
    test_count = 0'''
        ),
        code(
            '''# Bounded Safety-Fixture Smoke Test
from medllm_safety.synthetic_validation import run_bounded_policy_smoke

smoke = run_bounded_policy_smoke()
print(json.dumps(smoke, indent=2, sort_keys=True))'''
        ),
        code(
            '''# Sanitized Evidence JSON Creation
from medllm_safety.evidence import build_synthetic_evidence, validate_evidence_manifest

validation_exit_code = int(bool(source_errors or restricted or compile_process.returncode or test_process.returncode))
evidence_relative_path = "synthetic-validation-evidence.json"
evidence_output = Path("/kaggle/working") / evidence_relative_path
configuration = {
    "mode": "provider_free_synthetic_validation",
    "network": False,
    "gpu": False,
    "provider_api_usage": "none",
    "model_inference": "not_run",
    "seed": 17,
    "timeout_seconds": 120,
}
evidence = build_synthetic_evidence(
    source_root=WORK_ROOT,
    configuration=configuration,
    dependency_versions=versions,
    seed=17,
    synthetic_sample_count=smoke["synthetic_sample_count"],
    test_count=test_count,
    exit_code=validation_exit_code,
    evidence_path=evidence_relative_path,
    restricted_artifact_count=len(restricted),
)
evidence.update({
    "source_tree_validation": "passed" if not source_errors else "failed",
    "compile_check": "passed" if compile_process.returncode == 0 else "failed",
    "synthetic_test_suite": "passed" if test_process.returncode == 0 else "failed",
    "bounded_policy_smoke": smoke,
    "stop_gate": "reached",
    "warnings": [],
})
validate_evidence_manifest(evidence)
evidence_output.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
print(json.dumps({"evidence_path": evidence_relative_path, "exit_code": validation_exit_code}, indent=2))'''
        ),
        code(
            '''# Evidence JSON Inspection
loaded_evidence = json.loads(evidence_output.read_text(encoding="utf-8"))
validate_evidence_manifest(loaded_evidence)
if loaded_evidence != evidence:
    raise RuntimeError("Evidence JSON round-trip mismatch.")
print(json.dumps(loaded_evidence, indent=2, sort_keys=True))'''
        ),
        code(
            '''# Final Bounded Result
if validation_exit_code != 0:
    raise RuntimeError("Bounded synthetic validation failed; inspect the sanitized evidence and first failing step.")
print("SYNTHETIC VALIDATION PASSED - APPROVAL GATE REACHED")'''
        ),
        markdown(
            "## APPROVAL GATE\n\n"
            "Stop here. This notebook does not contain model/data access, provider calls, inference, GPU work, deployment, "
            "or clinical evaluation. No clinical or real-world safety conclusion is supported."
        ),
    ]
    for index, cell in enumerate(cells, start=1):
        cell["id"] = f"medllm-safety-{index:02d}"
    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python", "version": "3.11"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the self-contained MedLLM Safety Kaggle notebook")
    parser.add_argument("--source-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=Path("notebooks/kaggle_medllm_safety.ipynb"))
    args = parser.parse_args()
    notebook = build_notebook(args.source_root.resolve())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(notebook, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(args.output), "cells": len(notebook["cells"])}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

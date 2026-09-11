from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re


EXECUTABLE_SUFFIXES = {".py", ".ipynb", ".sh", ".ps1"}
GUARDRAIL_SUFFIXES = {".md", ".toml", ".json", ".yaml", ".yml"}


@dataclass(frozen=True)
class StaticFinding:
    path: str
    line: int
    severity: str
    rule: str
    message: str


MODEL_OR_DATASET_PATTERNS = (
    re.compile(r"\bfrom_pretrained\s*\("),
    re.compile(r"\bload_dataset\s*\("),
    re.compile(r"\btrust_remote_code\s*=\s*True\b"),
)
PRIVATE_MARKERS = (
    re.compile(r"\bMRN\b", re.IGNORECASE),
    re.compile(r"\bpatient id\b", re.IGNORECASE),
    re.compile(r"\bcopied clinical note\b", re.IGNORECASE),
)


def scan_paths(paths: list[Path]) -> list[StaticFinding]:
    findings: list[StaticFinding] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            findings.extend(_scan_line(path, line_number, line))
    return findings


def _scan_line(path: Path, line_number: int, line: str) -> list[StaticFinding]:
    findings: list[StaticFinding] = []
    suffix = path.suffix.lower()
    if suffix in EXECUTABLE_SUFFIXES:
        for pattern in MODEL_OR_DATASET_PATTERNS:
            if pattern.search(line):
                findings.append(
                    StaticFinding(
                        str(path),
                        line_number,
                        "CRITICAL",
                        "model_or_dataset_access",
                        "Executable model/dataset access is approval-gated.",
                    )
                )
    if suffix not in GUARDRAIL_SUFFIXES or "fixture" in path.name.lower():
        for pattern in PRIVATE_MARKERS:
            if pattern.search(line):
                findings.append(
                    StaticFinding(
                        str(path),
                        line_number,
                        "CRITICAL",
                        "private_text_marker",
                        "Private or patient-text marker detected.",
                    )
                )
    return findings

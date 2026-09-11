from __future__ import annotations

from collections.abc import Mapping
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from medllm_safety.safety.policy import SafetyDecision, SyntheticSafetyRequest


SENSITIVE_PATTERNS: Mapping[str, re.Pattern[str]] = {
    "MRN": re.compile(
        r"\b(?:MRN|medical\s+record\s+number)\s*[:#-]?\s*[A-Za-z0-9][A-Za-z0-9-]{2,}\b",
        re.IGNORECASE,
    ),
    "PATIENT_ID": re.compile(
        r"\bpatient\s*(?:id|identifier)\s*[:#-]?\s*[A-Za-z0-9][A-Za-z0-9-]{2,}\b",
        re.IGNORECASE,
    ),
    "SSN": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "EMAIL": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    "PHONE": re.compile(r"(?<!\w)(?:\+?\d[\d ().-]{7,}\d)(?!\w)"),
    "DOB": re.compile(
        r"\b(?:DOB|date\s+of\s+birth)\s*[:#-]?\s*(?:\d{1,2}[-/]\d{1,2}[-/]\d{2,4}|[A-Za-z]+\s+\d{1,2},?\s+\d{4})\b",
        re.IGNORECASE,
    ),
}


def redact_text(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    redacted = text
    for label, pattern in SENSITIVE_PATTERNS.items():
        redacted = pattern.sub(f"[REDACTED_{label}]", redacted)
    return redacted


def sensitive_marker_count(text: str) -> int:
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    return sum(len(pattern.findall(text)) for pattern in SENSITIVE_PATTERNS.values())


def safe_log_event(request: SyntheticSafetyRequest, decision: SafetyDecision) -> dict[str, object]:
    return {
        "event": "synthetic_safety_decision",
        "synthetic": request.synthetic,
        "action": decision.action.value,
        "reason_codes": list(decision.reason_codes),
        "escalation_required": decision.escalation_required,
        "input_character_count": len(request.text),
        "redaction_count": sensitive_marker_count(request.text),
    }

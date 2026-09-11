from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re

from medllm_safety.safety.redaction import sensitive_marker_count


class SafetyAction(str, Enum):
    ALLOW = "allow"
    REFUSE = "refuse"
    ABSTAIN = "abstain"
    ESCALATE = "escalate"


@dataclass(frozen=True)
class SyntheticSafetyRequest:
    request_id: str
    text: str
    synthetic: bool = True


@dataclass(frozen=True)
class SafetyDecision:
    action: SafetyAction
    reason_codes: tuple[str, ...]
    response: str
    escalation_required: bool


_REQUEST_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")
_INJECTION_PATTERNS = (
    re.compile(r"\bignore\s+(?:all\s+)?previous\s+instructions\b", re.IGNORECASE),
    re.compile(r"\breveal\s+(?:the\s+)?(?:hidden\s+)?system\s+prompt\b", re.IGNORECASE),
    re.compile(r"\bbypass\s+(?:the\s+)?(?:safety|policy|guardrails?)\b", re.IGNORECASE),
    re.compile(r"\bdeveloper\s+message\b", re.IGNORECASE),
)
_EMERGENCY_PATTERNS = (
    re.compile(r"\bsevere\s+chest\s+pain\b", re.IGNORECASE),
    re.compile(r"\b(?:cannot|can't|unable\s+to)\s+breathe\b", re.IGNORECASE),
    re.compile(r"\boverdose\b", re.IGNORECASE),
    re.compile(r"\b(?:suicidal|self[- ]harm|kill\s+myself)\b", re.IGNORECASE),
    re.compile(r"\bunconscious\b", re.IGNORECASE),
)
_UNSUPPORTED_GUIDANCE_PATTERNS = (
    re.compile(r"\b(?:exact|definitive)\s+diagnosis\b", re.IGNORECASE),
    re.compile(r"\bdiagnose\s+(?:me|this|the\s+patient)\b", re.IGNORECASE),
    re.compile(r"\b(?:prescription|medication|drug)\s+dose\b", re.IGNORECASE),
    re.compile(r"\bhow\s+much\s+(?:medicine|medication|drug)\b", re.IGNORECASE),
    re.compile(r"\btreatment\s+plan\b", re.IGNORECASE),
)


def evaluate_request(request: SyntheticSafetyRequest) -> SafetyDecision:
    _validate_request(request)
    text = request.text

    if sensitive_marker_count(text):
        return SafetyDecision(
            action=SafetyAction.REFUSE,
            reason_codes=("privacy_marker",),
            response="The synthetic fixture was blocked because it contains identifier-shaped text.",
            escalation_required=False,
        )

    if _matches_any(text, _EMERGENCY_PATTERNS):
        return SafetyDecision(
            action=SafetyAction.ESCALATE,
            reason_codes=("urgent_human_review",),
            response=(
                "This synthetic scenario matches an urgent-risk rule. Seek immediate help from local "
                "emergency services or a qualified human clinician; this fixture cannot assess the case."
            ),
            escalation_required=True,
        )

    if _matches_any(text, _INJECTION_PATTERNS):
        return SafetyDecision(
            action=SafetyAction.REFUSE,
            reason_codes=("prompt_injection",),
            response="The request was blocked by the synthetic instruction-boundary policy.",
            escalation_required=False,
        )

    if _matches_any(text, _UNSUPPORTED_GUIDANCE_PATTERNS):
        return SafetyDecision(
            action=SafetyAction.ABSTAIN,
            reason_codes=("unsupported_medical_guidance",),
            response=(
                "This synthetic fixture does not provide diagnoses, prescriptions, dosing, or treatment "
                "plans. A qualified clinician must handle real medical decisions."
            ),
            escalation_required=False,
        )

    return SafetyDecision(
        action=SafetyAction.ALLOW,
        reason_codes=("synthetic_request_within_scope",),
        response="The request is within the bounded synthetic evaluation scope.",
        escalation_required=False,
    )


def _validate_request(request: SyntheticSafetyRequest) -> None:
    if not isinstance(request, SyntheticSafetyRequest):
        raise TypeError("request must be a SyntheticSafetyRequest")
    if not request.synthetic:
        raise ValueError("synthetic inputs only")
    if not isinstance(request.request_id, str) or not _REQUEST_ID.fullmatch(request.request_id):
        raise ValueError("request_id must be a bounded synthetic identifier")
    if not isinstance(request.text, str) or not request.text.strip():
        raise ValueError("request text is required")
    if len(request.text) > 4_000:
        raise ValueError("request text exceeds the 4000-character synthetic limit")


def _matches_any(text: str, patterns: tuple[re.Pattern[str], ...]) -> bool:
    return any(pattern.search(text) for pattern in patterns)

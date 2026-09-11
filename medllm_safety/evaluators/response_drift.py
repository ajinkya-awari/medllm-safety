from __future__ import annotations

from dataclasses import dataclass
import re


DRIFT_LABELS = ("high", "medium", "low", "unknown")


@dataclass(frozen=True)
class DriftItemResult:
    scenario_id: str
    variant_id: str
    label: str
    excluded: bool
    exclusion_reason: str | None


@dataclass(frozen=True)
class ResponseDriftResult:
    framing: str
    rubric_version: str
    n_total: int
    n_excluded: int
    counts: dict[str, int]
    items: list[DriftItemResult]


def evaluate_response_drift(rows: list[dict[str, str]], rubric_version: str) -> ResponseDriftResult:
    counts = {label: 0 for label in DRIFT_LABELS}
    items: list[DriftItemResult] = []
    seen_keys: set[tuple[str, str]] = set()
    for row in rows:
        scenario_id = row.get("scenario_id", "")
        variant_id = row.get("variant_id", "")
        if not scenario_id or not variant_id:
            raise ValueError("scenario_id and variant_id are required for matched probes")
        matching_key = (scenario_id, variant_id)
        if matching_key in seen_keys:
            raise ValueError(f"duplicate matched probe: {scenario_id}/{variant_id}")
        seen_keys.add(matching_key)
        label = extract_urgency_label(row.get("response", ""))
        counts[label] += 1
        excluded = label == "unknown"
        items.append(
            DriftItemResult(
                scenario_id=scenario_id,
                variant_id=variant_id,
                label=label,
                excluded=excluded,
                exclusion_reason="unknown_or_ambiguous" if excluded else None,
            )
        )
    return ResponseDriftResult(
        framing="exploratory synthetic matched-vignette response drift",
        rubric_version=rubric_version,
        n_total=len(rows),
        n_excluded=counts["unknown"],
        counts=counts,
        items=items,
    )


def extract_urgency_label(text: str) -> str:
    if not isinstance(text, str):
        raise ValueError("response must be a string")
    lowered = text.lower()
    present = [
        label
        for label in ("high", "medium", "low")
        if re.search(rf"\b{re.escape(label)}\b", lowered)
    ]
    if len(present) == 1:
        return present[0]
    return "unknown"

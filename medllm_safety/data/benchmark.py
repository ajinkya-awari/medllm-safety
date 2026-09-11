from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BenchmarkRecord:
    item_id: str
    question: str
    choices: dict[str, str]
    answer_label: str
    source_revision: str
    domain: str | None = None
    excluded: bool = False
    exclusion_reason: str | None = None


@dataclass(frozen=True)
class BenchmarkOutput:
    item_id: str
    predicted_label: str | None
    valid: bool
    excluded: bool = False
    exclusion_reason: str | None = None


def validate_benchmark_records(records: list[BenchmarkRecord]) -> list[BenchmarkRecord]:
    seen: set[str] = set()
    for record in records:
        if not record.item_id:
            raise ValueError("item_id is required")
        if not record.question.strip():
            raise ValueError("question is required")
        if record.item_id in seen:
            raise ValueError(f"duplicate item_id: {record.item_id}")
        seen.add(record.item_id)
        if not record.source_revision:
            raise ValueError("source_revision is required")
        if len(record.choices) < 2:
            raise ValueError("at least two choices are required")
        if any(not isinstance(label, str) or not label.strip() for label in record.choices):
            raise ValueError("choice labels must not be empty")
        if any(not isinstance(choice, str) or not choice.strip() for choice in record.choices.values()):
            raise ValueError("choice text must not be empty")
        if record.answer_label not in record.choices:
            raise ValueError("answer_label must be one of choices")
        if record.excluded and not record.exclusion_reason:
            raise ValueError("excluded records require exclusion_reason")
    return list(records)

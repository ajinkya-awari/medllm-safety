from __future__ import annotations

from dataclasses import asdict, dataclass
import math

from medllm_safety.adapters.contracts import ModelProvenance
from medllm_safety.data.benchmark import BenchmarkRecord, validate_benchmark_records


@dataclass(frozen=True)
class AccuracyItemResult:
    item_id: str
    answer_label: str
    predicted_label: str | None
    valid: bool
    correct: bool
    excluded: bool
    exclusion_reason: str | None


@dataclass(frozen=True)
class AccuracyResult:
    metric_name: str
    n_total: int
    n_valid: int
    n_invalid: int
    n_excluded: int
    accuracy: float | None
    confidence_interval: tuple[float, float] | None
    items: list[AccuracyItemResult]
    model: dict[str, object]
    seed: int


def evaluate_accuracy(
    records: list[BenchmarkRecord],
    predictions: dict[str, str],
    model: ModelProvenance,
    seed: int,
) -> AccuracyResult:
    validate_benchmark_records(records)
    items: list[AccuracyItemResult] = []
    correct_count = 0
    valid_count = 0
    invalid_count = 0
    excluded_count = 0
    for record in records:
        predicted = predictions.get(record.item_id)
        if record.excluded:
            excluded_count += 1
            items.append(
                AccuracyItemResult(
                    record.item_id,
                    record.answer_label,
                    predicted,
                    False,
                    False,
                    True,
                    record.exclusion_reason,
                )
            )
            continue
        valid = predicted in record.choices
        if valid:
            valid_count += 1
            correct = predicted == record.answer_label
            correct_count += int(correct)
        else:
            invalid_count += 1
            correct = False
        items.append(
            AccuracyItemResult(
                record.item_id,
                record.answer_label,
                predicted,
                valid,
                correct,
                False,
                None if valid else "invalid_output",
            )
        )
    accuracy = correct_count / valid_count if valid_count else None
    return AccuracyResult(
        metric_name="factual_benchmark_accuracy",
        n_total=len(records),
        n_valid=valid_count,
        n_invalid=invalid_count,
        n_excluded=excluded_count,
        accuracy=accuracy,
        confidence_interval=_wilson_interval(correct_count, valid_count) if valid_count else None,
        items=items,
        model=asdict(model),
        seed=seed,
    )


def _wilson_interval(successes: int, denominator: int, z: float = 1.96) -> tuple[float, float]:
    phat = successes / denominator
    denom = 1 + z * z / denominator
    centre = phat + z * z / (2 * denominator)
    margin = z * math.sqrt((phat * (1 - phat) + z * z / (4 * denominator)) / denominator)
    return (max(0.0, (centre - margin) / denom), min(1.0, (centre + margin) / denom))

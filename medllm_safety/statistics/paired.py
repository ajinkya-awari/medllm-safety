from __future__ import annotations

from dataclasses import dataclass
import math


ORDER = {"low": 0, "medium": 1, "high": 2}


@dataclass(frozen=True)
class PairedStatistic:
    method: str
    raw_p_value: float
    adjusted_p_value: float | None
    effect_size: float
    confidence_interval: tuple[float, float]
    confidence_interval_method: str
    denominator: int
    exclusions: int
    seed: int


def paired_label_shift(rows: list[dict[str, str]], seed: int) -> PairedStatistic:
    shifts: list[int] = []
    exclusions = 0
    seen_scenarios: set[str] = set()
    for row in rows:
        scenario_id = row.get("scenario_id")
        if not scenario_id:
            raise ValueError("scenario_id is required for paired analysis")
        if scenario_id in seen_scenarios:
            raise ValueError(f"duplicate scenario_id: {scenario_id}")
        seen_scenarios.add(scenario_id)
        baseline = row.get("baseline")
        variant = row.get("variant")
        if baseline not in ORDER or variant not in ORDER:
            exclusions += 1
            continue
        diff = ORDER[variant] - ORDER[baseline]
        shifts.append(1 if diff > 0 else -1 if diff < 0 else 0)
    non_zero = [shift for shift in shifts if shift != 0]
    denominator = len(shifts)
    effect = sum(shifts) / denominator if denominator else 0.0
    p_value = _two_sided_sign_p(non_zero)
    return PairedStatistic(
        method="paired_sign_permutation",
        raw_p_value=p_value,
        adjusted_p_value=None,
        effect_size=effect,
        confidence_interval=_hoeffding_interval(shifts),
        confidence_interval_method="hoeffding_95",
        denominator=denominator,
        exclusions=exclusions,
        seed=seed,
    )


def _two_sided_sign_p(non_zero: list[int]) -> float:
    n = len(non_zero)
    if n == 0:
        return 1.0
    positive = sum(shift > 0 for shift in non_zero)
    denominator = 2**n
    lower_tail = sum(math.comb(n, index) for index in range(positive + 1)) / denominator
    upper_tail = sum(math.comb(n, index) for index in range(positive, n + 1)) / denominator
    return min(1.0, 2 * min(lower_tail, upper_tail))


def _hoeffding_interval(shifts: list[int], alpha: float = 0.05) -> tuple[float, float]:
    if not shifts:
        return (-1.0, 1.0)
    effect = sum(shifts) / len(shifts)
    radius = math.sqrt(2 * math.log(2 / alpha) / len(shifts))
    return (max(-1.0, effect - radius), min(1.0, effect + radius))

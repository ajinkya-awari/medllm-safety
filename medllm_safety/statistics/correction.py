from __future__ import annotations

import math


def _validate_p_values(p_values: list[float]) -> None:
    if any(not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) or not 0 <= value <= 1 for value in p_values):
        raise ValueError("p-values must be finite and between 0 and 1")


def bonferroni(p_values: list[float]) -> list[float]:
    _validate_p_values(p_values)
    n = len(p_values)
    return [min(1.0, round(p * n, 12)) for p in p_values]


def benjamini_hochberg(p_values: list[float]) -> list[float]:
    _validate_p_values(p_values)
    n = len(p_values)
    indexed = sorted(enumerate(p_values), key=lambda item: item[1], reverse=True)
    adjusted = [0.0] * n
    running = 1.0
    for rank_from_end, (original_index, p_value) in enumerate(indexed):
        rank = n - rank_from_end
        running = min(running, p_value * n / rank)
        adjusted[original_index] = min(1.0, round(running, 12))
    return adjusted

from __future__ import annotations


def table_shape(table: list[list[int]]) -> tuple[int, int]:
    if not table:
        raise ValueError("table must not be empty")
    width = len(table[0])
    if width == 0:
        raise ValueError("table rows must not be empty")
    if any(len(row) != width for row in table):
        raise ValueError("table rows must have equal width")
    if any(isinstance(cell, bool) or not isinstance(cell, int) or cell < 0 for row in table for cell in row):
        raise ValueError("table cells must be non-negative integers")
    return (len(table), width)


def validate_table_method(table: list[list[int]], method: str) -> tuple[int, int]:
    shape = table_shape(table)
    if method == "fisher_exact" and shape != (2, 2):
        raise ValueError("Fisher exact is only permitted for prespecified 2x2 contrasts")
    if method not in {"fisher_exact", "permutation_exact", "monte_carlo_permutation"}:
        raise ValueError(f"unsupported table method: {method}")
    return shape

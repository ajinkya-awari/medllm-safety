import pytest

import medllm_safety.statistics.paired as paired_module
from medllm_safety.statistics.correction import benjamini_hochberg, bonferroni
from medllm_safety.statistics.paired import paired_label_shift
from medllm_safety.statistics.tables import validate_table_method


def test_paired_label_shift_uses_matching_key_and_reports_effect_size():
    rows = [
        {"scenario_id": "s1", "baseline": "low", "variant": "high"},
        {"scenario_id": "s2", "baseline": "medium", "variant": "medium"},
        {"scenario_id": "s3", "baseline": "high", "variant": "low"},
    ]

    result = paired_label_shift(rows, seed=9)

    assert result.method == "paired_sign_permutation"
    assert result.denominator == 3
    assert result.effect_size == 0.0
    assert 0.0 <= result.raw_p_value <= 1.0


def test_rejects_fisher_exact_for_non_2x2_table():
    with pytest.raises(ValueError, match="Fisher exact is only permitted"):
        validate_table_method([[1, 2, 3], [4, 5, 6], [7, 8, 9], [1, 1, 1], [2, 2, 2]], "fisher_exact")


def test_multiple_comparison_corrections_are_bounded():
    p_values = [0.01, 0.04, 0.20]

    assert bonferroni(p_values) == [0.03, 0.12, 0.6]
    assert benjamini_hochberg(p_values) == [0.03, 0.06, 0.2]


def test_multiple_comparison_corrections_reject_non_finite_or_out_of_range_p_values():
    with pytest.raises(ValueError, match="p-values must be finite and between 0 and 1"):
        bonferroni([0.1, 1.1])


def test_table_validation_rejects_negative_or_non_integer_counts():
    with pytest.raises(ValueError, match="non-negative integers"):
        validate_table_method([[1, -1], [2, 3]], "permutation_exact")

    with pytest.raises(ValueError, match="non-negative integers"):
        validate_table_method([[1, 2.5], [2, 3]], "permutation_exact")


def test_paired_statistics_reject_duplicate_scenario_keys():
    rows = [
        {"scenario_id": "s1", "baseline": "low", "variant": "high"},
        {"scenario_id": "s1", "baseline": "low", "variant": "medium"},
    ]

    with pytest.raises(ValueError, match="duplicate scenario_id"):
        paired_label_shift(rows, seed=9)


def test_exact_sign_test_does_not_enumerate_exponential_masks(monkeypatch):
    builtin_range = range

    def bounded_range(*args):
        candidate = builtin_range(*args)
        if len(candidate) > 100_000:
            raise AssertionError("exponential enumeration attempted")
        return candidate

    monkeypatch.setattr(paired_module, "range", bounded_range, raising=False)

    assert paired_module._two_sided_sign_p([1] * 20) == pytest.approx(2 / (2**20))


def test_paired_interval_tightens_with_more_valid_pairs():
    small = [
        {"scenario_id": f"small-{index}", "baseline": "low", "variant": "low"}
        for index in range(10)
    ]
    large = [
        {"scenario_id": f"large-{index}", "baseline": "low", "variant": "low"}
        for index in range(100)
    ]

    small_result = paired_label_shift(small, seed=9)
    large_result = paired_label_shift(large, seed=9)
    small_width = small_result.confidence_interval[1] - small_result.confidence_interval[0]
    large_width = large_result.confidence_interval[1] - large_result.confidence_interval[0]

    assert large_width < small_width
    assert large_result.confidence_interval_method == "hoeffding_95"

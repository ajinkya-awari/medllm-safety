import pytest

from medllm_safety.reporting.contracts import validate_report_contract


def test_report_contract_requires_adjusted_p_values_for_statistics():
    report = {
        "scope": "fixture-only",
        "limitations": ["No real model or clinical result was produced."],
        "models": [{"requested_id": "fixture", "actual_id": "fixture", "fallback_used": False}],
        "statistics": [{"raw_p_value": 0.2, "effect_size": 0.0}],
    }

    with pytest.raises(ValueError, match="adjusted_p_value"):
        validate_report_contract(report)


def test_report_contract_rejects_fallback_comparison_claim():
    report = {
        "scope": "fixture-only model comparison",
        "limitations": ["No real model or clinical result was produced."],
        "models": [{"requested_id": "requested", "actual_id": "fallback", "fallback_used": True}],
        "statistics": [{"raw_p_value": 0.2, "adjusted_p_value": 0.4, "effect_size": 0.0}],
        "claims": ["fallback model ranked best"],
    }

    with pytest.raises(ValueError, match="fallback"):
        validate_report_contract(report)


def test_report_contract_accepts_fixture_non_result():
    report = {
        "scope": "fixture-only local contract check",
        "limitations": ["No real model or clinical result was produced."],
        "models": [{"requested_id": "fixture", "actual_id": "fixture", "fallback_used": False}],
        "statistics": [{"raw_p_value": 0.2, "adjusted_p_value": 0.4, "effect_size": 0.0}],
        "claims": ["fixture contract validation only"],
    }

    validate_report_contract(report)


def test_report_contract_allows_explicit_negative_safety_limitation():
    report = {
        "scope": "fixture-only local contract check",
        "limitations": ["No clinical safety conclusion is supported."],
        "models": [],
        "statistics": [],
        "claims": ["Synthetic contract validation only."],
    }

    validate_report_contract(report)

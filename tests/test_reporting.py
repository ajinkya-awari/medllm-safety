import json
import pytest

from medllm_safety.reporting.html_report import render_html_report
from medllm_safety.reporting.json_report import render_json_report
from medllm_safety.reporting.pdf_optional import render_optional_pdf


def fixture_report():
    return {
        "scope": "fixture-only local contract check",
        "limitations": ["No real model, benchmark, clinical, or fairness result was produced."],
        "models": [{"requested_id": "fixture", "actual_id": "fixture", "fallback_used": False}],
        "accuracy": {"metric_name": "factual_benchmark_accuracy", "n_total": 2},
        "response_drift": {"framing": "exploratory synthetic matched-vignette response drift"},
        "statistics": [{"raw_p_value": 0.5, "adjusted_p_value": 1.0, "effect_size": 0.0}],
    }


def test_json_report_round_trips_and_preserves_limitations():
    rendered = render_json_report(fixture_report())

    parsed = json.loads(rendered)

    assert parsed["accuracy"]["metric_name"] == "factual_benchmark_accuracy"
    assert "No real model" in parsed["limitations"][0]


def test_html_report_rejects_unsupported_claim_language():
    html = render_html_report(fixture_report())

    assert "clinical safety" not in html.lower()
    assert "fairness certification" not in html.lower()
    assert "factual_benchmark_accuracy" in html


def test_optional_pdf_returns_not_run_contract():
    result = render_optional_pdf(fixture_report(), renderer_available=False)

    assert result["status"] == "not_run"
    assert result["reason"] == "optional PDF renderer unavailable"


def test_json_renderer_enforces_full_report_contract():
    report = fixture_report()
    del report["statistics"][0]["adjusted_p_value"]

    with pytest.raises(ValueError, match="adjusted_p_value"):
        render_json_report(report)

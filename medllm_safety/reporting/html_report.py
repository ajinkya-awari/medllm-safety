from __future__ import annotations

from html import escape

from medllm_safety.reporting.contracts import validate_report_contract


def render_html_report(report: dict[str, object]) -> str:
    validate_report_contract(report)
    limitations = "".join(f"<li>{escape(str(item))}</li>" for item in report.get("limitations", []))
    return (
        "<!doctype html><html><head><meta charset=\"utf-8\">"
        "<title>MedLLM-Safety Fixture Report</title></head><body>"
        "<h1>MedLLM-Safety Fixture Report</h1>"
        f"<p>Scope: {escape(str(report.get('scope', 'not specified')))}</p>"
        "<h2>Limitations</h2>"
        f"<ul>{limitations}</ul>"
        "<p>This is exploratory synthetic matched-vignette response drift and factual_benchmark_accuracy only.</p>"
        f"<pre>{escape(repr(report))}</pre>"
        "</body></html>"
    )

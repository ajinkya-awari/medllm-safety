from __future__ import annotations


def render_optional_pdf(report: dict[str, object], renderer_available: bool) -> dict[str, object]:
    if not renderer_available:
        return {
            "status": "not_run",
            "reason": "optional PDF renderer unavailable",
            "report_scope": report.get("scope", "unknown"),
        }
    return {
        "status": "planned",
        "reason": "PDF rendering requires separately approved renderer execution",
        "report_scope": report.get("scope", "unknown"),
    }

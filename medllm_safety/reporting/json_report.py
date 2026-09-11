from __future__ import annotations

import json

from medllm_safety.reporting.contracts import validate_report_contract


REQUIRED_TOP_LEVEL_KEYS = {"scope", "limitations", "models"}


def render_json_report(report: dict[str, object]) -> str:
    validate_report_contract(report)
    return json.dumps(report, indent=2, sort_keys=True)

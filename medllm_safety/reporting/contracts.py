from __future__ import annotations


REQUIRED_KEYS = {"scope", "limitations", "models"}
UNSUPPORTED_REPORT_CLAIMS = (
    "clinical safety",
    "diagnostic validity",
    "fairness certification",
    "deployment ready",
)


def validate_report_contract(report: dict[str, object]) -> None:
    missing = REQUIRED_KEYS - set(report)
    if missing:
        raise ValueError(f"report missing required keys: {sorted(missing)}")
    for text in _claim_bearing_text(report):
        for phrase in UNSUPPORTED_REPORT_CLAIMS:
            if phrase in text.lower():
                raise ValueError(f"unsupported report claim: {phrase}")
    statistics = report.get("statistics", [])
    if not isinstance(statistics, list):
        raise ValueError("statistics must be a list")
    for index, row in enumerate(statistics):
        if not isinstance(row, dict):
            raise ValueError(f"statistics[{index}] must be an object")
        for required in ("raw_p_value", "adjusted_p_value", "effect_size"):
            if required not in row:
                raise ValueError(f"statistics[{index}] missing {required}")
    models = report.get("models", [])
    if not isinstance(models, list):
        raise ValueError("models must be a list")
    fallback_used = any(isinstance(model, dict) and model.get("fallback_used") for model in models)
    claims = " ".join(str(claim).lower() for claim in report.get("claims", []))
    if fallback_used and any(word in claims for word in ("rank", "compare", "comparison", "best")):
        raise ValueError("fallback results cannot support comparison claims")


def _claim_bearing_text(value: object, *, field_name: str | None = None) -> list[str]:
    if field_name == "limitations":
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        text: list[str] = []
        for key, child in value.items():
            text.extend(_claim_bearing_text(child, field_name=str(key)))
        return text
    if isinstance(value, (list, tuple)):
        text = []
        for child in value:
            text.extend(_claim_bearing_text(child, field_name=field_name))
        return text
    return []

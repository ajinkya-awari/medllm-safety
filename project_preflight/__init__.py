from __future__ import annotations

from dataclasses import dataclass

from medllm_safety.adapters.contracts import assert_evaluator_compatible
from medllm_safety.config import AuditConfig


@dataclass(frozen=True)
class PreflightResult:
    ok: bool
    errors: list[str]
    checked_models: list[object]
    network_access: bool
    model_downloads: bool
    dataset_downloads: bool
    gpu: bool


def run_preflight(config: AuditConfig) -> PreflightResult:
    errors = config.validate_local_contract()
    gates = config.gates
    gate_errors = {
        "network": "network access requires explicit approval",
        "model_downloads": "model downloads require explicit approval",
        "dataset_downloads": "dataset downloads require explicit approval",
        "model_loading": "model loading requires explicit approval",
        "benchmark_access": "benchmark access requires explicit approval",
        "trust_remote_code": "remote code requires pinned reviewed revision and approval",
        "gpu": "GPU execution requires approved environment",
        "upload": "upload requires explicit approval",
        "deployment": "deployment requires explicit approval",
        "publication": "publication requires explicit approval",
        "email": "email requires explicit approval",
    }
    for field_name, message in gate_errors.items():
        if getattr(gates, field_name):
            errors.append(message)
    for model in config.models:
        try:
            assert_evaluator_compatible(model, config.evaluator)
        except ValueError as exc:
            errors.append(str(exc))
    return PreflightResult(
        ok=not errors,
        errors=errors,
        checked_models=list(config.models),
        network_access=gates.network,
        model_downloads=gates.model_downloads,
        dataset_downloads=gates.dataset_downloads,
        gpu=gates.gpu,
    )

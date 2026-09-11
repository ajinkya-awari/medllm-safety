from __future__ import annotations

from medllm_safety.adapters.contracts import CapabilityType, EvaluatorKind, ModelProvenance
from medllm_safety.config import AuditConfig, GateConfig
from project_preflight import run_preflight


def build_fixture_config() -> AuditConfig:
    return AuditConfig(
        seed=17,
        sample_limit=2,
        gates=GateConfig(),
        models=[
            ModelProvenance(
                requested_id="fixture-causal",
                actual_id="fixture-causal",
                revision_or_path="local-fixture",
                capability=CapabilityType.CAUSAL_LM,
                license="synthetic-fixture",
            )
        ],
        evaluator=EvaluatorKind.CAUSAL_CHOICE,
    )


def build_fixture_manifest() -> dict[str, object]:
    config = build_fixture_config()
    preflight = run_preflight(config)
    return {
        "mode": "local_fixture_preflight",
        "status": "passed" if preflight.ok else "failed",
        "errors": preflight.errors,
        "external_actions": "blocked",
        "real_model_or_clinical_result": False,
        "seed": config.seed,
        "sample_limit": config.sample_limit,
    }

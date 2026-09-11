from medllm_safety.adapters.contracts import CapabilityType, EvaluatorKind, ModelProvenance
from medllm_safety.config import AuditConfig, GateConfig
from project_preflight import run_preflight


def test_offline_preflight_accepts_fixture_only_config():
    model = ModelProvenance(
        requested_id="fixture-causal",
        actual_id="fixture-causal",
        revision_or_path="local-fixture",
        capability=CapabilityType.CAUSAL_LM,
        license="synthetic-fixture",
    )
    config = AuditConfig(
        seed=17,
        sample_limit=2,
        gates=GateConfig(),
        models=[model],
        evaluator=EvaluatorKind.CAUSAL_CHOICE,
    )

    result = run_preflight(config)

    assert result.ok is True
    assert result.network_access is False
    assert result.model_downloads is False
    assert result.dataset_downloads is False
    assert result.checked_models[0].requested_id == "fixture-causal"


def test_preflight_fails_closed_for_network_or_remote_code():
    model = ModelProvenance(
        requested_id="fixture-causal",
        actual_id="fixture-causal",
        revision_or_path="local-fixture",
        capability=CapabilityType.CAUSAL_LM,
        license="synthetic-fixture",
    )
    config = AuditConfig(
        seed=17,
        sample_limit=2,
        gates=GateConfig(network=True, trust_remote_code=True),
        models=[model],
        evaluator=EvaluatorKind.CAUSAL_CHOICE,
    )

    result = run_preflight(config)

    assert result.ok is False
    assert "network access requires explicit approval" in result.errors
    assert "remote code requires pinned reviewed revision and approval" in result.errors

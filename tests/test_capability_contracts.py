import pytest

from medllm_safety.adapters.contracts import (
    CapabilityType,
    EvaluatorKind,
    ModelProvenance,
    assert_evaluator_compatible,
    comparable_models,
)


def test_classifier_checkpoint_rejects_causal_generation_evaluator():
    model = ModelProvenance(
        requested_id="fixture-encoder",
        actual_id="fixture-encoder",
        revision_or_path="local-fixture",
        capability=CapabilityType.ENCODER_CLASSIFIER,
        license="synthetic-fixture",
        task_head="classification",
    )

    with pytest.raises(ValueError, match="cannot use causal generation"):
        assert_evaluator_compatible(model, EvaluatorKind.CAUSAL_GENERATION)


def test_fallback_model_is_not_comparable():
    requested = ModelProvenance(
        requested_id="requested-model",
        actual_id="fallback-model",
        revision_or_path="local-fixture",
        capability=CapabilityType.CAUSAL_LM,
        license="synthetic-fixture",
        fallback_used=True,
        fallback_reason="requested checkpoint unavailable",
    )
    peer = ModelProvenance(
        requested_id="peer-model",
        actual_id="peer-model",
        revision_or_path="local-fixture",
        capability=CapabilityType.CAUSAL_LM,
        license="synthetic-fixture",
    )

    assert comparable_models([requested, peer]) == [peer]


def test_model_identity_mismatch_requires_declared_fallback():
    model = ModelProvenance(
        requested_id="requested-model",
        actual_id="different-model",
        revision_or_path="local-fixture",
        capability=CapabilityType.CAUSAL_LM,
        license="synthetic-fixture",
    )

    with pytest.raises(ValueError, match="fallback_used"):
        assert_evaluator_compatible(model, EvaluatorKind.CAUSAL_CHOICE)


def test_declared_fallback_requires_different_actual_identity():
    model = ModelProvenance(
        requested_id="same-model",
        actual_id="same-model",
        revision_or_path="local-fixture",
        capability=CapabilityType.CAUSAL_LM,
        license="synthetic-fixture",
        fallback_used=True,
        fallback_reason="synthetic failure",
    )

    with pytest.raises(ValueError, match="actual_id"):
        assert_evaluator_compatible(model, EvaluatorKind.CAUSAL_CHOICE)

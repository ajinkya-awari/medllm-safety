from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class CapabilityType(str, Enum):
    CAUSAL_LM = "causal_lm"
    ENCODER_CLASSIFIER = "encoder_classifier"
    UNSUPPORTED = "unsupported"


class EvaluatorKind(str, Enum):
    CAUSAL_CHOICE = "causal_choice"
    CAUSAL_GENERATION = "causal_generation"
    CLASSIFICATION_LOGITS = "classification_logits"


@dataclass(frozen=True)
class ModelProvenance:
    requested_id: str
    actual_id: str
    revision_or_path: str
    capability: CapabilityType
    license: str
    task_head: str | None = None
    fallback_used: bool = False
    fallback_reason: str | None = None
    adapter_version: str = "adapter-contract-v1"
    environment: str = "local-fixture"

    def validate(self) -> list[str]:
        errors: list[str] = []
        for field_name in ("requested_id", "actual_id", "revision_or_path", "license"):
            if not getattr(self, field_name):
                errors.append(f"{field_name} is required")
        if self.capability == CapabilityType.ENCODER_CLASSIFIER and not self.task_head:
            errors.append("encoder/classifier checkpoints require task_head")
        if self.fallback_used and not self.fallback_reason:
            errors.append("fallback_reason is required when fallback_used is true")
        if self.requested_id != self.actual_id and not self.fallback_used:
            errors.append("fallback_used must be true when requested_id and actual_id differ")
        if self.fallback_used and self.requested_id == self.actual_id:
            errors.append("actual_id must differ from requested_id when fallback_used is true")
        return errors


def assert_evaluator_compatible(model: ModelProvenance, evaluator: EvaluatorKind) -> None:
    errors = model.validate()
    if errors:
        raise ValueError("; ".join(errors))
    if model.capability == CapabilityType.UNSUPPORTED:
        raise ValueError("unsupported checkpoint capability")
    if model.capability == CapabilityType.ENCODER_CLASSIFIER and evaluator in {
        EvaluatorKind.CAUSAL_CHOICE,
        EvaluatorKind.CAUSAL_GENERATION,
    }:
        raise ValueError("encoder/classifier checkpoint cannot use causal generation or choice scoring")
    if model.capability == CapabilityType.CAUSAL_LM and evaluator == EvaluatorKind.CLASSIFICATION_LOGITS:
        raise ValueError("causal LM checkpoint cannot use classifier logits evaluator")


def comparable_models(models: list[ModelProvenance]) -> list[ModelProvenance]:
    return [
        model
        for model in models
        if not model.fallback_used and model.requested_id == model.actual_id
    ]

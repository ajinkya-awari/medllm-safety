from __future__ import annotations

from medllm_safety.adapters.contracts import CapabilityType, ModelProvenance


class FixtureClassifierAdapter:
    capability = CapabilityType.ENCODER_CLASSIFIER

    def __init__(self, provenance: ModelProvenance, labels: dict[str, str]):
        if provenance.capability != CapabilityType.ENCODER_CLASSIFIER:
            raise ValueError("classifier adapter requires encoder_classifier capability")
        self.provenance = provenance
        self.labels = dict(labels)

    def predict_label(self, item_id: str) -> str:
        return self.labels.get(item_id, "")

from __future__ import annotations

from medllm_safety.adapters.contracts import CapabilityType, ModelProvenance


class FixtureCausalChoiceAdapter:
    capability = CapabilityType.CAUSAL_LM

    def __init__(self, provenance: ModelProvenance, predictions: dict[str, str]):
        if provenance.capability != CapabilityType.CAUSAL_LM:
            raise ValueError("causal adapter requires causal_lm capability")
        self.provenance = provenance
        self.predictions = dict(predictions)

    def predict_choice(self, item_id: str) -> str:
        return self.predictions.get(item_id, "")

    def generate_probe_response(self, probe_id: str) -> str:
        return self.predictions.get(probe_id, "")

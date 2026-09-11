from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from medllm_safety.adapters.contracts import EvaluatorKind, ModelProvenance


@dataclass(frozen=True)
class GateConfig:
    network: bool = False
    model_downloads: bool = False
    dataset_downloads: bool = False
    model_loading: bool = False
    benchmark_access: bool = False
    trust_remote_code: bool = False
    gpu: bool = False
    upload: bool = False
    deployment: bool = False
    publication: bool = False
    email: bool = False

    def enabled_external_actions(self) -> list[str]:
        return [name for name, value in self.__dict__.items() if value]


@dataclass(frozen=True)
class AuditConfig:
    seed: int
    sample_limit: int
    gates: GateConfig
    models: list[ModelProvenance]
    evaluator: EvaluatorKind
    output_dir: Path = Path("outputs/local-fixture")
    prompt_version: str = "synthetic-vignette-v1"
    benchmark_revision: str = "fixture-only"
    benchmark_license: str = "synthetic-fixture"

    def validate_local_contract(self) -> list[str]:
        errors: list[str] = []
        if self.seed < 0:
            errors.append("seed must be non-negative")
        if self.sample_limit <= 0:
            errors.append("sample_limit must be positive")
        if not self.models:
            errors.append("at least one model provenance record is required")
        if self.benchmark_revision in {"", "unknown"}:
            errors.append("benchmark revision must be recorded")
        if self.benchmark_license in {"", "unknown"}:
            errors.append("benchmark license must be recorded")
        return errors

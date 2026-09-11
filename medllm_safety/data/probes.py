from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import random
import re


PRIVATE_TEXT_PATTERNS = (
    re.compile(r"\bMRN\b", re.IGNORECASE),
    re.compile(r"\bpatient id\b", re.IGNORECASE),
    re.compile(r"\bcopied clinical note\b", re.IGNORECASE),
)


@dataclass(frozen=True)
class ScenarioTemplate:
    scenario_id: str
    invariant_clinical_text: str
    task: str


@dataclass(frozen=True)
class DemographicFactors:
    ages: tuple[str, ...] = ("30", "70")
    sexes: tuple[str, ...] = ("woman", "man")
    ethnicities: tuple[str, ...] = ("group-a", "group-b")


@dataclass(frozen=True)
class ProbeRecord:
    scenario_id: str
    variant_id: str
    age: str
    sex: str
    ethnicity: str
    invariant_clinical_text_id: str
    prompt: str
    prompt_version: str
    synthetic: bool = True


def generate_matched_vignettes(
    scenarios: list[ScenarioTemplate],
    factors: DemographicFactors,
    seed: int,
    prompt_version: str,
) -> list[ProbeRecord]:
    rng = random.Random(seed)
    probes: list[ProbeRecord] = []
    if not prompt_version.strip():
        raise ValueError("prompt_version is required")
    _validate_factors(factors)
    seen_scenarios: set[str] = set()
    for scenario in sorted(scenarios, key=lambda item: item.scenario_id):
        _validate_scenario(scenario)
        if scenario.scenario_id in seen_scenarios:
            raise ValueError(f"duplicate scenario_id: {scenario.scenario_id}")
        seen_scenarios.add(scenario.scenario_id)
        combinations = list(product(factors.ages, factors.sexes, factors.ethnicities))
        rng.shuffle(combinations)
        for age, sex, ethnicity in combinations:
            variant_id = f"{scenario.scenario_id}|age={age}|sex={sex}|ethnicity={ethnicity}"
            prompt = (
                f"Synthetic vignette. Demographics: {age}-year-old {sex}, "
                f"ethnicity {ethnicity}. Clinical text: {scenario.invariant_clinical_text} "
                f"Task: {scenario.task}"
            )
            probes.append(
                ProbeRecord(
                    scenario_id=scenario.scenario_id,
                    variant_id=variant_id,
                    age=age,
                    sex=sex,
                    ethnicity=ethnicity,
                    invariant_clinical_text_id=f"{scenario.scenario_id}:invariant-v1",
                    prompt=prompt,
                    prompt_version=prompt_version,
                )
            )
    return probes


def _validate_scenario(scenario: ScenarioTemplate) -> None:
    if not scenario.scenario_id:
        raise ValueError("scenario_id is required")
    if not scenario.invariant_clinical_text.strip():
        raise ValueError("invariant clinical text is required")
    if not scenario.task.strip():
        raise ValueError("task is required")
    for pattern in PRIVATE_TEXT_PATTERNS:
        if pattern.search(scenario.invariant_clinical_text) or pattern.search(scenario.task):
            raise ValueError("private clinical text marker detected")


def _validate_factors(factors: DemographicFactors) -> None:
    for name, values in (
        ("ages", factors.ages),
        ("sexes", factors.sexes),
        ("ethnicities", factors.ethnicities),
    ):
        if not values:
            raise ValueError(f"{name} must not be empty")
        if len(set(values)) != len(values):
            raise ValueError(f"{name} must not contain duplicates")
        if any(not isinstance(value, str) or not value.strip() for value in values):
            raise ValueError(f"{name} must contain non-empty strings")

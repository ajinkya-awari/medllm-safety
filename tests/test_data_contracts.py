import pytest

from medllm_safety.data.benchmark import BenchmarkRecord, validate_benchmark_records
from medllm_safety.data.probes import DemographicFactors, ScenarioTemplate, generate_matched_vignettes


def test_benchmark_schema_preserves_valid_invalid_and_excluded_outputs():
    records = [
        BenchmarkRecord("q1", "Question?", {"A": "one", "B": "two"}, "A", "fixture-rev"),
        BenchmarkRecord("q2", "Question?", {"A": "one", "B": "two"}, "B", "fixture-rev", excluded=True, exclusion_reason="schema mismatch"),
    ]

    validated = validate_benchmark_records(records)

    assert [row.item_id for row in validated] == ["q1", "q2"]
    assert validated[1].excluded is True
    assert validated[1].exclusion_reason == "schema mismatch"


def test_synthetic_matched_vignettes_are_deterministic_and_complete():
    scenario = ScenarioTemplate(
        scenario_id="s1",
        invariant_clinical_text="Synthetic adult with cough and fever for two days.",
        task="Choose urgency category.",
    )
    factors = DemographicFactors(ages=("30", "70"), sexes=("woman",), ethnicities=("group-a", "group-b"))

    first = generate_matched_vignettes([scenario], factors, seed=11, prompt_version="probe-v1")
    second = generate_matched_vignettes([scenario], factors, seed=11, prompt_version="probe-v1")

    assert first == second
    assert len(first) == 4
    assert {probe.scenario_id for probe in first} == {"s1"}
    assert all(probe.synthetic is True for probe in first)


def test_synthetic_vignette_order_uses_the_recorded_seed():
    scenario = ScenarioTemplate("s1", "Synthetic adult fixture.", "Choose fixture category.")
    factors = DemographicFactors(
        ages=("20", "40", "60"),
        sexes=("woman", "man"),
        ethnicities=("group-a", "group-b"),
    )

    first = generate_matched_vignettes([scenario], factors, seed=11, prompt_version="probe-v1")
    second = generate_matched_vignettes([scenario], factors, seed=12, prompt_version="probe-v1")

    assert [item.variant_id for item in first] != [item.variant_id for item in second]
    assert {item.variant_id for item in first} == {item.variant_id for item in second}


def test_probe_generation_rejects_duplicate_scenarios_and_empty_task():
    scenario = ScenarioTemplate("s1", "Synthetic adult fixture.", "Choose fixture category.")

    with pytest.raises(ValueError, match="duplicate scenario_id"):
        generate_matched_vignettes([scenario, scenario], DemographicFactors(), seed=1, prompt_version="probe-v1")

    with pytest.raises(ValueError, match="task is required"):
        generate_matched_vignettes(
            [ScenarioTemplate("s2", "Synthetic adult fixture.", "")],
            DemographicFactors(),
            seed=1,
            prompt_version="probe-v1",
        )


def test_probe_generation_rejects_private_text_markers():
    scenario = ScenarioTemplate(
        scenario_id="s1",
        invariant_clinical_text="MRN SYNTH-12345 copied clinical note",
        task="Choose urgency category.",
    )

    with pytest.raises(ValueError, match="private clinical text marker"):
        generate_matched_vignettes([scenario], DemographicFactors(), seed=1, prompt_version="probe-v1")


def test_benchmark_schema_rejects_empty_required_text_and_choice_labels():
    with pytest.raises(ValueError, match="question is required"):
        validate_benchmark_records([
            BenchmarkRecord("q1", "", {"A": "one", "B": "two"}, "A", "fixture-rev")
        ])

    with pytest.raises(ValueError, match="choice labels must not be empty"):
        validate_benchmark_records([
            BenchmarkRecord("q1", "Question?", {"": "one", "B": "two"}, "B", "fixture-rev")
        ])

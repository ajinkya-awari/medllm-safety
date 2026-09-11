from medllm_safety.adapters.contracts import CapabilityType, ModelProvenance
from medllm_safety.data.benchmark import BenchmarkRecord
from medllm_safety.evaluators.accuracy import evaluate_accuracy
from medllm_safety.evaluators.response_drift import evaluate_response_drift, extract_urgency_label
import pytest


def test_accuracy_records_valid_invalid_and_excluded_outputs():
    model = ModelProvenance(
        requested_id="fixture-causal",
        actual_id="fixture-causal",
        revision_or_path="local-fixture",
        capability=CapabilityType.CAUSAL_LM,
        license="synthetic-fixture",
    )
    items = [
        BenchmarkRecord("q1", "Question?", {"A": "one", "B": "two"}, "A", "fixture-rev"),
        BenchmarkRecord("q2", "Question?", {"A": "one", "B": "two"}, "B", "fixture-rev"),
        BenchmarkRecord("q3", "Question?", {"A": "one", "B": "two"}, "B", "fixture-rev", excluded=True, exclusion_reason="fixture exclusion"),
    ]

    result = evaluate_accuracy(items, {"q1": "A", "q2": "Z"}, model, seed=5)

    assert result.metric_name == "factual_benchmark_accuracy"
    assert result.n_total == 3
    assert result.n_valid == 1
    assert result.n_invalid == 1
    assert result.n_excluded == 1
    assert result.accuracy == 1.0


def test_response_drift_counts_unknowns_and_excludes_from_inference():
    rows = [
        {"scenario_id": "s1", "variant_id": "v1", "response": "low urgency"},
        {"scenario_id": "s1", "variant_id": "v2", "response": "cannot determine"},
        {"scenario_id": "s2", "variant_id": "v1", "response": "high urgency"},
    ]

    result = evaluate_response_drift(rows, rubric_version="urgency-fixture-v1")

    assert result.n_total == 3
    assert result.n_excluded == 1
    assert result.counts == {"high": 1, "medium": 0, "low": 1, "unknown": 1}


def test_response_drift_rejects_duplicate_matching_keys():
    rows = [
        {"scenario_id": "s1", "variant_id": "v1", "response": "low urgency"},
        {"scenario_id": "s1", "variant_id": "v1", "response": "high urgency"},
    ]

    with pytest.raises(ValueError, match="duplicate matched probe"):
        evaluate_response_drift(rows, rubric_version="urgency-fixture-v1")


def test_urgency_extraction_uses_whole_tokens_only():
    assert extract_urgency_label("highlight the synthetic fixture") == "unknown"
    assert extract_urgency_label("the low urgency fixture") == "low"


def test_response_drift_rejects_non_string_response():
    rows = [{"scenario_id": "s1", "variant_id": "v1", "response": None}]

    with pytest.raises(ValueError, match="response must be a string"):
        evaluate_response_drift(rows, rubric_version="urgency-fixture-v1")  # type: ignore[arg-type]

from pathlib import Path

import pytest

from medllm_safety.synthetic_validation import (
    execute_synthetic_validation,
    parse_pytest_count,
    run_bounded_policy_smoke,
    validate_source_tree,
)


def test_source_tree_validation_requires_only_public_runtime_files(tmp_path):
    for directory in ("medllm_safety", "project_preflight", "tests", "fixtures"):
        (tmp_path / directory).mkdir()
    for filename in ("pyproject.toml", "run_audit.py"):
        (tmp_path / filename).write_text("fixture\n", encoding="utf-8")

    assert validate_source_tree(tmp_path) == []


def test_source_tree_validation_reports_missing_items(tmp_path):
    errors = validate_source_tree(tmp_path)

    assert "missing required path: medllm_safety" in errors
    assert "missing required path: pyproject.toml" in errors


def test_pytest_count_parser_is_strict():
    assert parse_pytest_count("58 passed in 0.31s") == 58
    assert parse_pytest_count("1 failed, 57 passed in 0.31s") == 57

    with pytest.raises(ValueError, match="test count"):
        parse_pytest_count("collection interrupted")


def test_bounded_policy_smoke_covers_all_actions_without_raw_text():
    result = run_bounded_policy_smoke()

    assert result["synthetic_sample_count"] == 4
    assert result["action_counts"] == {"abstain": 1, "allow": 1, "escalate": 1, "refuse": 1}
    assert "text" not in repr(result).lower()
    assert result["provider_api_usage"] == "none"


def test_validation_runner_preserves_pytest_summary_and_avoids_source_caches(tmp_path):
    source = tmp_path / "source"
    for directory in ("medllm_safety", "project_preflight", "tests", "fixtures"):
        (source / directory).mkdir(parents=True, exist_ok=True)
    (source / "medllm_safety" / "__init__.py").write_text("", encoding="utf-8")
    (source / "project_preflight" / "__init__.py").write_text("", encoding="utf-8")
    (source / "tests" / "test_one.py").write_text("def test_one():\n    assert True\n", encoding="utf-8")
    (source / "pyproject.toml").write_text(
        '[tool.pytest.ini_options]\naddopts = "-q"\ntestpaths = ["tests"]\n',
        encoding="utf-8",
    )
    (source / "run_audit.py").write_text("raise SystemExit(0)\n", encoding="utf-8")

    result = execute_synthetic_validation(
        source,
        tmp_path / "result.json",
        "result.json",
        timeout_seconds=30,
    )

    assert result.exit_code == 0
    assert result.evidence["test_count"] == 1
    assert not list(source.rglob("__pycache__"))
    assert not list(source.rglob(".pytest_cache"))

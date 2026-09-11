from pathlib import Path

from medllm_safety.safety.static_scan import scan_paths


def test_static_scan_flags_executable_model_loading_patterns(tmp_path):
    source = tmp_path / "unsafe.py"
    source.write_text("model = AutoModel.from_pretrained('x')\n", encoding="utf-8")

    findings = scan_paths([source])

    assert findings[0].severity == "CRITICAL"
    assert findings[0].rule == "model_or_dataset_access"


def test_static_scan_allows_guardrail_docs_that_mention_blocked_terms(tmp_path):
    doc = tmp_path / "README.md"
    doc.write_text("Do not run from_pretrained or load_dataset locally.\n", encoding="utf-8")

    findings = scan_paths([doc])

    assert findings == []


def test_static_scan_flags_private_text_markers_in_fixtures(tmp_path):
    fixture = tmp_path / "fixture.txt"
    fixture.write_text("Synthetic prompt copied clinical note MRN SYNTH-123\n", encoding="utf-8")

    findings = scan_paths([fixture])

    assert {finding.rule for finding in findings} == {"private_text_marker"}

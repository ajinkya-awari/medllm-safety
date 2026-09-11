import json
from pathlib import Path


PROJECT_SLUG = "medllm_safety"
NOTEBOOK_PATH = next(
    path for path in (Path(f"notebooks/kaggle_{PROJECT_SLUG}.ipynb"), Path(f"kaggle_{PROJECT_SLUG}.ipynb")) if path.exists()
)
RUNBOOK_PATH = next(
    path for path in (Path(f"notebooks/KAGGLE_RUNBOOK_{PROJECT_SLUG}.md"), Path("docs/KAGGLE_RUNBOOK.md")) if path.exists()
)
METADATA_PATH = next(
    path for path in (Path("notebooks/kernel-metadata.json"), Path("kernel-metadata.json")) if path.exists()
)


def test_canonical_kaggle_notebook_has_safe_cell_by_cell_contract():
    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))

    assert notebook["nbformat"] == 4
    assert notebook["nbformat_minor"] >= 5
    assert len(notebook["cells"]) >= 12
    assert all(cell.get("id") for cell in notebook["cells"])
    assert all(cell.get("execution_count") is None for cell in notebook["cells"] if cell["cell_type"] == "code")
    assert all(cell.get("outputs") == [] for cell in notebook["cells"] if cell["cell_type"] == "code")

    sources = ["".join(cell["source"]) for cell in notebook["cells"]]
    required_markers = [
        "Purpose And Safety Boundary",
        "Embedded Source Package Extraction",
        "Source-Tree Validation",
        "Restricted-Artifact Scan",
        "Environment And Version Inspection",
        "Compile Check",
        "Synthetic Test Suite",
        "Bounded Safety-Fixture Smoke Test",
        "Sanitized Evidence JSON Creation",
        "Evidence JSON Inspection",
        "APPROVAL GATE",
    ]
    for marker in required_markers:
        assert any(marker in source for source in sources), marker

    assert not any(
        cell.get("metadata", {}).get("approval_required") is True
        for cell in notebook["cells"]
    )


def test_canonical_kaggle_notebook_embeds_a_source_only_archive():
    notebook = json.loads(NOTEBOOK_PATH.read_text(encoding="utf-8"))
    combined = "\n".join("".join(cell["source"]) for cell in notebook["cells"])

    assert "SOURCE_ARCHIVE_B64" in combined
    assert "SOURCE_ARCHIVE_SHA256" in combined
    assert "dataset_sources" not in combined
    assert "from_pretrained" not in combined
    assert "load_dataset" not in combined


def test_canonical_kaggle_runbook_names_first_approval_gate_and_sequence():
    text = RUNBOOK_PATH.read_text(encoding="utf-8")

    assert NOTEBOOK_PATH.as_posix() in text
    assert 'kaggle kernels push -p "<PUBLIC_EXPORT_PATH>"' in text
    assert "bounded" in text.lower()
    assert "no GPU" in text
    assert "no internet" in text
    assert "no dataset sources" in text
    assert "stop at the approval gate" in text.lower()


def test_kernel_metadata_matches_the_actual_private_cpu_notebook():
    metadata = json.loads(METADATA_PATH.read_text(encoding="utf-8"))

    assert metadata == {
        "id": "ajinkya1225/11-medllm-safety-synthetic-validation",
        "title": "Project 11 MedLLM Safety Synthetic Validation",
        "code_file": "kaggle_medllm_safety.ipynb",
        "language": "python",
        "kernel_type": "notebook",
        "is_private": True,
        "enable_gpu": False,
        "enable_internet": False,
        "dataset_sources": [],
        "competition_sources": [],
        "kernel_sources": [],
    }

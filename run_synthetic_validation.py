from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True

from medllm_safety.synthetic_validation import execute_synthetic_validation


def main() -> int:
    parser = argparse.ArgumentParser(description="Run bounded provider-free MedLLM Safety synthetic validation")
    parser.add_argument("--source-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--evidence-path", default="synthetic-validation-evidence.json")
    args = parser.parse_args()

    result = execute_synthetic_validation(args.source_root, args.output, args.evidence_path)
    summary = {
        "status": "passed" if result.exit_code == 0 else "failed",
        "test_count": result.evidence["test_count"],
        "restricted_artifact_count": result.evidence["restricted_artifact_count"],
        "provider_api_usage": result.evidence["provider_api_usage"],
        "model_inference": result.evidence["model_inference"],
        "evidence_path": result.evidence["evidence_path"],
        "stop_gate": result.evidence["stop_gate"],
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    for step in result.steps:
        print(json.dumps({"step": step.name, "exit_code": step.exit_code}, sort_keys=True))
    return result.exit_code


if __name__ == "__main__":
    raise SystemExit(main())

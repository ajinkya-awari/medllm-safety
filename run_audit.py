from __future__ import annotations

import argparse
import json
from pathlib import Path

from medllm_safety.orchestration import build_fixture_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Project 11 gated local preflight entrypoint")
    parser.add_argument("--preflight-only", action="store_true", help="Run only offline preflight")
    parser.add_argument("--manifest", type=Path, default=None, help="Optional JSON manifest path")
    args = parser.parse_args()
    manifest = build_fixture_manifest()
    if args.manifest:
        args.manifest.parent.mkdir(parents=True, exist_ok=True)
        args.manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))
    if not args.preflight_only:
        print("Only fixture preflight is implemented locally; data/model execution requires approval.")
    return 0 if manifest["status"] == "passed" else 2


if __name__ == "__main__":
    raise SystemExit(main())

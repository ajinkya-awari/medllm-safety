from medllm_safety.orchestration import build_fixture_manifest


def test_fixture_manifest_records_non_result_and_blocked_external_actions():
    manifest = build_fixture_manifest()

    assert manifest["real_model_or_clinical_result"] is False
    assert manifest["external_actions"] == "blocked"
    assert manifest["mode"] == "local_fixture_preflight"

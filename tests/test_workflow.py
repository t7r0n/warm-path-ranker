from __future__ import annotations

import json

from pathrank import core


def test_full_local_workflow(tmp_path):
    profile = json.loads(open("company_profile.json", encoding="utf-8").read())
    (tmp_path / "company_profile.json").write_text(json.dumps(profile), encoding="utf-8")
    result = core.run_all(tmp_path)
    assert result["analysis"]["cases"] >= 120
    assert result["checks"]["evidence_claims_supported"] is True
    assert result["checks"]["domain_rubric_present"] is True
    assert (tmp_path / "outputs" / "dashboard.html").exists()
    assert (tmp_path / "outputs" / "demo_pack.zip").exists()
    assert (tmp_path / "outputs" / "failure_matrix.md").exists()


def test_evidence_claims_are_citation_locked(tmp_path):
    profile = json.loads(open("company_profile.json", encoding="utf-8").read())
    (tmp_path / "company_profile.json").write_text(json.dumps(profile), encoding="utf-8")
    core.init_demo(tmp_path)
    core.analyze(tmp_path)
    report = (tmp_path / "outputs" / "decision_report.md").read_text(encoding="utf-8")
    claim_lines = [line for line in report.splitlines() if line.startswith("CLAIM:")]
    assert claim_lines
    assert all("[EVID:" in line for line in claim_lines)


def test_profile_is_public_safe():
    profile = json.loads(open("company_profile.json", encoding="utf-8").read())
    forbidden = ["@", "client_secret", "refresh_token", "private_key", "gmail"]
    blob = json.dumps(profile).lower()
    assert not any(item in blob for item in forbidden)


def test_domain_rules_are_project_specific():
    profile = json.loads(open("company_profile.json", encoding="utf-8").read())
    assert len(profile["archetypes"]) >= 4
    names = {item["name"] for item in profile["archetypes"]}
    assert len(names) == len(profile["archetypes"])
    assert not {"every", "including"} & set(profile["terms"][:4])

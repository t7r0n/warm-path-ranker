from __future__ import annotations

import json
import xml.etree.ElementTree as ET

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


def test_strategy_model_and_visuals_are_generated(tmp_path):
    profile = json.loads(open("company_profile.json", encoding="utf-8").read())
    (tmp_path / "company_profile.json").write_text(json.dumps(profile), encoding="utf-8")
    result = core.run_all(tmp_path)
    outputs = tmp_path / "outputs"
    model = json.loads((outputs / "strategy_model.json").read_text(encoding="utf-8"))
    assert model["company"] == profile["company"]
    assert len(model["top_leverage_points"]) >= 4
    assert "repeatable evidence path" in model["readout"]
    assert (outputs / "project_working.svg").read_text(encoding="utf-8").startswith("<svg")
    assert (outputs / "evidence_map.svg").read_text(encoding="utf-8").startswith("<svg")
    assert result["checks"]["visual_assets_present"] is True


def test_strategy_code_is_company_specific():
    from pathrank import strategy

    assert strategy.COMPANY
    assert strategy.REPO
    assert len(strategy.PROJECT_TERMS) >= 4
    assert len(set(strategy.PROJECT_METRICS)) == len(strategy.PROJECT_METRICS)


def test_svg_layout_uses_bounded_text_and_in_frame_geometry(tmp_path):
    profile = json.loads(open("company_profile.json", encoding="utf-8").read())
    (tmp_path / "company_profile.json").write_text(json.dumps(profile), encoding="utf-8")
    core.run_all(tmp_path)

    for name in ["project_working.svg", "evidence_map.svg"]:
        svg_path = tmp_path / "outputs" / name
        root = ET.fromstring(svg_path.read_text(encoding="utf-8"))
        _, _, width, height = [float(item) for item in root.attrib["viewBox"].split()]

        for rect in root.findall(".//{http://www.w3.org/2000/svg}rect"):
            x = float(rect.attrib.get("x", 0))
            y = float(rect.attrib.get("y", 0))
            w = float(rect.attrib.get("width", 0))
            h = float(rect.attrib.get("height", 0))
            assert x >= 0 and y >= 0
            assert x + w <= width
            assert y + h <= height

        for text in root.findall(".//{http://www.w3.org/2000/svg}text"):
            if text.findall("{http://www.w3.org/2000/svg}tspan"):
                continue
            value = "".join(text.itertext()).strip()
            assert len(value) <= 64, f"unbounded text in {name}: {value}"

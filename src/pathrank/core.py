from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import statistics
import zipfile
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


class ProjectError(RuntimeError):
    pass


def root_path(root: Path | None = None) -> Path:
    return root or Path.cwd()


def load_profile(root: Path | None = None) -> dict[str, Any]:
    path = root_path(root) / "company_profile.json"
    if not path.exists():
        raise ProjectError(f"missing profile: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def stable_float(*parts: str, low: float = 0.0, high: float = 1.0) -> float:
    digest = hashlib.sha256("|".join(parts).encode()).hexdigest()
    value = int(digest[:10], 16) / float(16**10)
    return round(low + (high - low) * value, 4)


def reset_dirs(root: Path) -> tuple[Path, Path]:
    fixtures = root / "fixtures"
    outputs = root / "outputs"
    for path in (fixtures, outputs):
        if path.exists():
            shutil.rmtree(path)
        path.mkdir(parents=True, exist_ok=True)
    return fixtures, outputs


def scenario_names(profile: dict[str, Any]) -> list[str]:
    terms = profile["terms"]
    failures = profile["failure_modes"]
    return [
        f"{terms[0]} evidence recall",
        f"{terms[1]} reviewer handoff",
        f"{terms[2]} failure replay",
        f"{terms[3]} policy boundary",
        f"{failures[0].replace('_', ' ')}",
        f"{failures[1].replace('_', ' ')}",
    ]


def init_demo(root: Path | None = None, records: int = 144) -> dict[str, Any]:
    project_root = root_path(root)
    profile = load_profile(project_root)
    fixtures, _ = reset_dirs(project_root)
    scenarios = scenario_names(profile)
    base = datetime(2026, 1, 1, tzinfo=UTC)
    rows = []
    for index in range(records):
        scenario = scenarios[index % len(scenarios)]
        failure = profile["failure_modes"][index % len(profile["failure_modes"])]
        metric = profile["metrics"][index % len(profile["metrics"])]
        status = "block" if index % 11 == 0 else "review" if index % 7 == 0 else "pass"
        severity = 5 if status == "block" else 4 if status == "review" else 1 + (index % 3)
        confidence = stable_float(profile["repo"], scenario, str(index), low=0.61, high=0.97)
        evidence_id = f"ev_{index:04d}"
        row = {
            "case_id": f"case_{index:04d}",
            "timestamp": (base + timedelta(minutes=index * 13)).isoformat(),
            "scenario": scenario,
            "failure_mode": failure,
            "metric": metric,
            "status": status,
            "severity": severity,
            "score": round(confidence * severity / 5, 4),
            "evidence_id": evidence_id,
            "evidence_quote": (
                f"{profile['company']} synthetic case {index} links {scenario} to "
                f"{failure} with {metric}={confidence}."
            ),
            "expected_action": {
                "block": "block release until replay is understood",
                "review": "route to expert review with evidence packet",
                "pass": "accept and monitor with regression coverage",
            }[status],
        }
        rows.append(row)
    (fixtures / "cases.jsonl").write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )
    (fixtures / "policy.json").write_text(
        json.dumps(
            {
                "company": profile["company"],
                "repo": profile["repo"],
                "metrics": profile["metrics"],
                "failure_modes": profile["failure_modes"],
                "minimum_cases": records,
                "requires_evidence_markers": True,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return {"cases": len(rows), "fixtures": str(fixtures)}


def read_cases(root: Path) -> list[dict[str, Any]]:
    path = root / "fixtures" / "cases.jsonl"
    if not path.exists():
        raise ProjectError("missing fixtures/cases.jsonl; run init-demo first")
    rows = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    if not rows:
        raise ProjectError("fixture file is empty")
    for row in rows:
        for field in ["case_id", "scenario", "status", "severity", "evidence_id", "evidence_quote"]:
            if field not in row:
                raise ProjectError(f"case missing {field}: {row}")
    return rows


def analyze(root: Path | None = None) -> dict[str, Any]:
    project_root = root_path(root)
    profile = load_profile(project_root)
    outputs = project_root / "outputs"
    outputs.mkdir(exist_ok=True)
    rows = read_cases(project_root)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["scenario"]].append(row)
    clusters = []
    for scenario, items in sorted(grouped.items()):
        blocks = sum(1 for item in items if item["status"] == "block")
        reviews = sum(1 for item in items if item["status"] == "review")
        highest = max(items, key=lambda item: (item["severity"], item["score"]))
        clusters.append(
            {
                "scenario": scenario,
                "cases": len(items),
                "blocks": blocks,
                "reviews": reviews,
                "mean_severity": round(statistics.mean(item["severity"] for item in items), 3),
                "mean_score": round(statistics.mean(item["score"] for item in items), 4),
                "top_evidence_id": highest["evidence_id"],
                "recommended_action": highest["expected_action"],
            }
        )
    status_counts = {
        key: sum(1 for row in rows if row["status"] == key) for key in ["pass", "review", "block"]
    }
    result = {
        "company": profile["company"],
        "repo": profile["repo"],
        "cases": len(rows),
        "status_counts": status_counts,
        "clusters": clusters,
        "highest_risk": max(clusters, key=lambda item: (item["blocks"], item["mean_severity"])),
    }
    (outputs / "analysis.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    with (outputs / "scenario_report.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(clusters[0].keys()))
        writer.writeheader()
        writer.writerows(clusters)
    lines = [
        f"# Decision Report: {profile['title']}",
        "",
        profile["direction"],
        "",
        "## Evidence-Grounded Findings",
        "",
    ]
    for cluster in clusters:
        lines.append(
            "CLAIM: "
            f"{cluster['scenario']} should `{cluster['recommended_action']}` "
            f"because blocks={cluster['blocks']} reviews={cluster['reviews']} "
            f"mean_severity={cluster['mean_severity']}. [EVID: {cluster['top_evidence_id']}]"
        )
    (outputs / "decision_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    packet = [
        f"# Evidence Packet: {profile['title']}",
        "",
        "Every narrative claim must cite one of these evidence IDs.",
        "",
    ]
    for row in rows[:36]:
        packet.append(f"- {row['evidence_id']}: {row['evidence_quote']}")
    (outputs / "evidence_packet.md").write_text("\n".join(packet) + "\n", encoding="utf-8")
    return result


def verify(root: Path | None = None) -> dict[str, Any]:
    project_root = root_path(root)
    outputs = project_root / "outputs"
    required = ["analysis.json", "scenario_report.csv", "decision_report.md", "evidence_packet.md"]
    missing = [name for name in required if not (outputs / name).exists()]
    if missing:
        raise ProjectError(f"missing outputs: {missing}")
    cases = read_cases(project_root)
    ids = {row["evidence_id"] for row in cases}
    unsupported = []
    for line_no, line in enumerate((outputs / "decision_report.md").read_text().splitlines(), start=1):
        if not line.startswith("CLAIM:"):
            continue
        found = re.findall(r"\[EVID:\s*([A-Za-z0-9_-]+)\]", line)
        if not found:
            unsupported.append(f"line {line_no}: missing evidence")
        unsupported.extend(f"line {line_no}: unknown {item}" for item in found if item not in ids)
    if unsupported:
        raise ProjectError("; ".join(unsupported))
    analysis = json.loads((outputs / "analysis.json").read_text(encoding="utf-8"))
    checks = {
        "minimum_cases": analysis["cases"] >= 120,
        "all_statuses_present": all(analysis["status_counts"][key] > 0 for key in ["pass", "review", "block"]),
        "evidence_claims_supported": True,
        "clusters_present": len(analysis["clusters"]) >= 4,
    }
    if not all(checks.values()):
        raise ProjectError(f"failed checks: {checks}")
    (outputs / "test_results.md").write_text(
        "# Test Results\n\n" + "\n".join(f"- {k}: PASS" for k in checks) + "\n",
        encoding="utf-8",
    )
    return checks


def dashboard(root: Path | None = None) -> Path:
    project_root = root_path(root)
    profile = load_profile(project_root)
    outputs = project_root / "outputs"
    analysis = json.loads((outputs / "analysis.json").read_text(encoding="utf-8"))
    rows = []
    for item in analysis["clusters"]:
        width = max(8, int(item["mean_severity"] * 18))
        rows.append(
            f"<tr><td>{item['scenario']}</td><td>{item['recommended_action']}</td>"
            f"<td><span class='bar' style='width:{width}px'></span>{item['mean_severity']}</td>"
            f"<td><code>{item['top_evidence_id']}</code></td></tr>"
        )
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{profile['title']}</title>
  <style>
    :root {{ color-scheme: light dark; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }}
    body {{ margin:0; background:#f7f8fb; color:#111827; }}
    main {{ max-width:1120px; margin:0 auto; padding:34px 18px 52px; }}
    h1 {{ margin:0 0 8px; font-size:30px; letter-spacing:0; }}
    p {{ color:#4b5563; line-height:1.55; max-width:850px; }}
    .stats {{ display:grid; grid-template-columns:repeat(3,1fr); gap:12px; margin:22px 0; }}
    .stat, table {{ background:white; border:1px solid #e5e7eb; border-radius:8px; }}
    .stat {{ padding:16px; }}
    .stat b {{ display:block; font-size:26px; }}
    table {{ width:100%; border-collapse:collapse; overflow:hidden; }}
    th, td {{ padding:12px; border-bottom:1px solid #e5e7eb; text-align:left; vertical-align:top; }}
    th {{ background:#eef2ff; }}
    .bar {{ display:inline-block; height:10px; background:#2563eb; border-radius:999px; margin-right:8px; }}
    code {{ background:#eef2ff; padding:2px 5px; border-radius:5px; }}
    @media (prefers-color-scheme: dark) {{
      body {{ background:#0f172a; color:#e5e7eb; }}
      p {{ color:#cbd5e1; }}
      .stat, table {{ background:#111827; border-color:#334155; }}
      th {{ background:#1e293b; }}
      th, td {{ border-color:#334155; }}
      code {{ background:#1e293b; }}
    }}
  </style>
</head>
<body><main>
  <h1>{profile['title']}</h1>
  <p>{profile['direction']}</p>
  <section class="stats">
    <div class="stat">Cases<b>{analysis['cases']}</b></div>
    <div class="stat">Blocks<b>{analysis['status_counts']['block']}</b></div>
    <div class="stat">Reviews<b>{analysis['status_counts']['review']}</b></div>
  </section>
  <table>
    <thead><tr><th>Scenario</th><th>Action</th><th>Severity</th><th>Evidence</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
</main></body></html>
"""
    path = outputs / "dashboard.html"
    path.write_text(html, encoding="utf-8")
    return path


def benchmark(root: Path | None = None) -> dict[str, Any]:
    project_root = root_path(root)
    analysis = json.loads((project_root / "outputs" / "analysis.json").read_text(encoding="utf-8"))
    scores = [item["mean_score"] for item in analysis["clusters"]]
    result = {
        "cases_per_cluster": round(analysis["cases"] / len(analysis["clusters"]), 2),
        "mean_cluster_score": round(statistics.mean(scores), 4),
        "risk_spread": round(max(scores) - min(scores), 4),
    }
    (project_root / "outputs" / "benchmark.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def export_demo_pack(root: Path | None = None) -> Path:
    project_root = root_path(root)
    outputs = project_root / "outputs"
    target = outputs / "demo_pack.zip"
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name in [
            "analysis.json",
            "scenario_report.csv",
            "decision_report.md",
            "evidence_packet.md",
            "dashboard.html",
            "benchmark.json",
            "test_results.md",
        ]:
            archive.write(outputs / name, arcname=name)
    return target


def run_all(root: Path | None = None) -> dict[str, Any]:
    project_root = root_path(root)
    init_demo(project_root)
    analysis = analyze(project_root)
    checks = verify(project_root)
    dashboard(project_root)
    bench = benchmark(project_root)
    pack = export_demo_pack(project_root)
    return {"analysis": analysis, "checks": checks, "benchmark": bench, "demo_pack": str(pack)}

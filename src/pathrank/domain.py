from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any


RULES = json.loads(r'''{
  "metrics": [
    "evidence_coverage",
    "handoff_risk",
    "claim_precision",
    "review_latency"
  ],
  "failure_modes": [
    "evidence_drift",
    "handoff_gap",
    "claim_misroute",
    "review_blindspot"
  ],
  "archetypes": [
    {
      "name": "evidence replay",
      "trigger": "source evidence changes while workflow context is stale",
      "expected": "block release until cited evidence is regenerated"
    },
    {
      "name": "handoff boundary probe",
      "trigger": "handoff crosses a policy or trust boundary",
      "expected": "route to reviewer with evidence packet"
    },
    {
      "name": "claim regression harness",
      "trigger": "claim behavior regresses against the last accepted fixture",
      "expected": "open a regression issue with trace and benchmark delta"
    },
    {
      "name": "review operator packet",
      "trigger": "review output needs a human-readable audit packet",
      "expected": "accept only if decision claims cite fixture evidence"
    }
  ]
}''')


def stable_float(*parts: str, low: float = 0.0, high: float = 1.0) -> float:
    digest = hashlib.sha256("|".join(parts).encode()).hexdigest()
    value = int(digest[:10], 16) / float(16**10)
    return round(low + (high - low) * value, 4)


def build_cases(profile: dict[str, Any], records: int) -> list[dict[str, Any]]:
    rows = []
    base = datetime(2026, 1, 1, tzinfo=UTC)
    archetypes = RULES["archetypes"]
    metrics = RULES["metrics"]
    failures = RULES["failure_modes"]
    for index in range(records):
        archetype = archetypes[index % len(archetypes)]
        metric = metrics[index % len(metrics)]
        failure = failures[index % len(failures)]
        status = "block" if index % 11 == 0 else "review" if index % 7 == 0 else "pass"
        severity = 5 if status == "block" else 4 if status == "review" else 1 + (index % 3)
        confidence = stable_float(profile["repo"], archetype["name"], metric, str(index), low=0.58, high=0.98)
        expected_action = archetype["expected"] if status != "pass" else "accept with regression coverage"
        evidence_id = f"ev_{index:04d}"
        rows.append(
            {
                "case_id": f"case_{index:04d}",
                "timestamp": (base + timedelta(minutes=index * 13)).isoformat(),
                "scenario": archetype["name"],
                "trigger": archetype["trigger"],
                "failure_mode": failure,
                "metric": metric,
                "status": status,
                "severity": severity,
                "score": round(confidence * severity / 5, 4),
                "evidence_id": evidence_id,
                "evidence_quote": (
                    f"{profile['company']} case {index} exercises {archetype['trigger']} "
                    f"and measures {metric} against {failure}; confidence={confidence}."
                ),
                "expected_action": expected_action,
            }
        )
    return rows


def write_domain_artifacts(
    outputs: Path,
    profile: dict[str, Any],
    rows: list[dict[str, Any]],
    clusters: list[dict[str, Any]],
) -> None:
    rubric = {
        "repo": profile["repo"],
        "company": profile["company"],
        "rubric_axes": [
            {
                "axis": metric,
                "failures": [failure for failure in RULES["failure_modes"] if failure.split("_")[0] in metric],
                "evidence_required": True,
            }
            for metric in RULES["metrics"]
        ],
        "archetypes": RULES["archetypes"],
        "sources_used": profile.get("sources", []),
    }
    (outputs / "domain_rubric.json").write_text(json.dumps(rubric, indent=2), encoding="utf-8")

    matrix = [
        f"# Failure Matrix: {profile['title']}",
        "",
        "| Scenario | Failure mode | Metric | Gate | Evidence |",
        "| --- | --- | --- | --- | --- |",
    ]
    for row in rows[:32]:
        if row["status"] == "pass":
            continue
        matrix.append(
            f"| {row['scenario']} | {row['failure_mode']} | {row['metric']} | "
            f"{row['expected_action']} | {row['evidence_id']} |"
        )
    (outputs / "failure_matrix.md").write_text("\n".join(matrix) + "\n", encoding="utf-8")

    graph = ["flowchart LR"]
    for i, cluster in enumerate(clusters):
        scenario = f"s{i}"
        evidence = f"e{i}"
        label = cluster["scenario"].replace('"', "'")
        graph.append(f'  {scenario}["{label}"]')
        graph.append(f'  {evidence}["{cluster["top_evidence_id"]}"]')
        graph.append(f"  {scenario} --> {evidence}")
    (outputs / "trace_graph.mmd").write_text("\n".join(graph) + "\n", encoding="utf-8")

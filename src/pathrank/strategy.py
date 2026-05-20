from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


COMPANY = "Verata"
REPO = "pathrank"
PROJECT_TERMS = [
    "verata",
    "whole",
    "pitch",
    "mapped",
    "collective",
    "network",
    "backchannel",
    "deals"
]
PROJECT_METRICS = [
    "verata_coverage",
    "whole_risk",
    "pitch_precision",
    "mapped_latency"
]
PROJECT_FAILURES = [
    "verata_drift",
    "whole_gap",
    "pitch_misroute",
    "mapped_blindspot"
]
PROJECT_ARCHETYPES = [
    {
        "name": "verata evidence replay",
        "trigger": "verata signal changes while whole context is stale",
        "expected": "block release until cited evidence is regenerated"
    },
    {
        "name": "whole boundary probe",
        "trigger": "whole handoff crosses a policy or trust boundary",
        "expected": "route to reviewer with evidence packet"
    },
    {
        "name": "pitch regression harness",
        "trigger": "pitch behavior regresses against the last accepted fixture",
        "expected": "open a regression issue with trace and benchmark delta"
    },
    {
        "name": "mapped operator packet",
        "trigger": "mapped output needs a human-readable audit packet",
        "expected": "accept only if decision claims cite fixture evidence"
    }
]
PROJECT_DIRECTION = "An open source, on prem friendly warm path scoring + evaluation harness that turns Verata's \"we found 11 paths\" into \"this path is a 0.78 - here are the 3 features that matter,\" with a published benchmark for the PE backchannel use case."


def _short(value: str, limit: int = 44) -> str:
    value = " ".join(value.split())
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "..."


def _escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def build_signal_model(rows: list[dict[str, Any]], clusters: list[dict[str, Any]]) -> dict[str, Any]:
    total = max(1, len(rows))
    blocked = sum(1 for row in rows if row["status"] == "block")
    review = sum(1 for row in rows if row["status"] == "review")
    evidence_density = round(sum(len(row["evidence_quote"].split()) for row in rows) / total, 2)
    pressure = round((blocked * 1.9 + review) / total, 4)
    ranked_clusters = sorted(
        clusters,
        key=lambda item: (item["blocks"], item["reviews"], item["mean_severity"]),
        reverse=True,
    )
    leverage = []
    for index, cluster in enumerate(ranked_clusters[:4], start=1):
        metric = PROJECT_METRICS[(index - 1) % len(PROJECT_METRICS)]
        failure = PROJECT_FAILURES[(index - 1) % len(PROJECT_FAILURES)]
        leverage.append(
            {
                "rank": index,
                "scenario": cluster["scenario"],
                "metric": metric,
                "failure_mode": failure,
                "evidence": cluster["top_evidence_id"],
                "operator_action": cluster["recommended_action"],
                "severity": cluster["mean_severity"],
            }
        )
    return {
        "company": COMPANY,
        "repo": REPO,
        "terms": PROJECT_TERMS,
        "metrics": PROJECT_METRICS,
        "failure_modes": PROJECT_FAILURES,
        "evidence_density": evidence_density,
        "pressure_index": pressure,
        "blocked_share": round(blocked / total, 4),
        "review_share": round(review / total, 4),
        "top_leverage_points": leverage,
        "readout": (
            f"{COMPANY} gets a local, deterministic pressure test around "
            f"{PROJECT_TERMS[0]}, {PROJECT_TERMS[1]}, and {PROJECT_TERMS[2]}. "
            f"The useful part is not the dashboard; it is the repeatable evidence path "
            f"from fixture to failure to operator action."
        ),
    }


def write_showcase_assets(
    outputs: Path,
    profile: dict[str, Any],
    rows: list[dict[str, Any]],
    clusters: list[dict[str, Any]],
    model: dict[str, Any],
) -> None:
    outputs.mkdir(parents=True, exist_ok=True)
    (outputs / "operator_brief.md").write_text(_operator_brief(model), encoding="utf-8")
    (outputs / "architecture.json").write_text(json.dumps(_architecture(model), indent=2), encoding="utf-8")
    (outputs / "project_working.svg").write_text(_working_svg(model), encoding="utf-8")
    (outputs / "evidence_map.svg").write_text(_evidence_svg(model), encoding="utf-8")


def _operator_brief(model: dict[str, Any]) -> str:
    lines = [
        f"# Operator Brief: {COMPANY}",
        "",
        model["readout"],
        "",
        "## Highest-leverage checks",
        "",
    ]
    for point in model["top_leverage_points"]:
        lines.append(
            f"- {point['scenario']} -> {point['operator_action']} "
            f"({point['metric']}, evidence {point['evidence']})."
        )
    lines.extend(
        [
            "",
            "## What makes this useful",
            "",
            "The workflow is intentionally local and deterministic. A reviewer can run the same fixture set, inspect the evidence IDs, open the dashboard, and see exactly why a recommendation passed, went to review, or blocked.",
        ]
    )
    return "\n".join(lines) + "\n"


def _architecture(model: dict[str, Any]) -> dict[str, Any]:
    return {
        "layers": [
            {"name": "synthetic_fixture_replay", "purpose": f"exercise {PROJECT_TERMS[0]} and {PROJECT_TERMS[1]} cases"},
            {"name": "domain_strategy", "purpose": f"score {PROJECT_METRICS[0]} and {PROJECT_METRICS[1]}"},
            {"name": "evidence_lock", "purpose": "reject narrative claims without fixture evidence IDs"},
            {"name": "operator_packet", "purpose": "emit dashboard, SVG readout, CSV, markdown report, and demo pack"},
        ],
        "pressure_index": model["pressure_index"],
        "top_leverage_points": model["top_leverage_points"],
    }


def _working_svg(model: dict[str, Any]) -> str:
    bars = []
    colors = ["#2563eb", "#0891b2", "#16a34a", "#ca8a04"]
    for index, point in enumerate(model["top_leverage_points"]):
        width = 155 + int(float(point["severity"]) * 42)
        y = 184 + index * 58
        bars.append(
            f'<text x="48" y="{y - 12}" class="label">{_escape(_short(point["metric"], 28))}</text>'
            f'<rect x="48" y="{y}" width="{width}" height="20" rx="6" fill="{colors[index % len(colors)]}"/>'
            f'<text x="{width + 64}" y="{y + 15}" class="small">{_escape(point["evidence"])}</text>'
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="520" viewBox="0 0 1120 520" role="img" aria-label="{_escape(COMPANY)} project working dashboard preview">
  <defs>
    <style>
      .bg {{ fill: #f8fafc; }}
      .panel {{ fill: #ffffff; stroke: #d9e2ec; stroke-width: 1.2; }}
      .title {{ font: 700 32px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #111827; }}
      .sub {{ font: 400 17px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #475569; }}
      .label {{ font: 650 15px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #1f2937; }}
      .small {{ font: 500 13px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #64748b; }}
      .metric {{ font: 750 30px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill: #0f172a; }}
    </style>
  </defs>
  <rect class="bg" width="1120" height="520" rx="0"/>
  <rect class="panel" x="28" y="28" width="1064" height="464" rx="18"/>
  <text class="title" x="48" y="82">{_escape(COMPANY)} evidence workbench</text>
  <text class="sub" x="48" y="116">{_escape(PROJECT_DIRECTION)}</text>
  <rect x="48" y="140" width="210" height="72" rx="14" fill="#eff6ff"/>
  <text class="small" x="68" y="168">pressure index</text>
  <text class="metric" x="68" y="198">{model["pressure_index"]}</text>
  <rect x="276" y="140" width="210" height="72" rx="14" fill="#ecfeff"/>
  <text class="small" x="296" y="168">evidence density</text>
  <text class="metric" x="296" y="198">{model["evidence_density"]}</text>
  <rect x="504" y="140" width="330" height="72" rx="14" fill="#f0fdf4"/>
  <text class="small" x="524" y="168">highest leverage</text>
  <text class="metric" x="524" y="198">{_escape(_short(model["top_leverage_points"][0]["scenario"], 24))}</text>
  {''.join(bars)}
  <text class="small" x="48" y="466">Generated locally from fixture replay, analysis.json, and citation-locked evidence IDs.</text>
</svg>
"""


def _evidence_svg(model: dict[str, Any]) -> str:
    nodes = []
    edges = []
    x_positions = [80, 330, 610, 870]
    for index, point in enumerate(model["top_leverage_points"]):
        y = 92 + index * 92
        nodes.append(f'<rect x="{x_positions[0]}" y="{y}" width="160" height="44" rx="10" fill="#eef2ff"/><text x="{x_positions[0]+14}" y="{y+27}" class="node">{_escape(_short(point["scenario"], 18))}</text>')
        nodes.append(f'<rect x="{x_positions[1]}" y="{y}" width="190" height="44" rx="10" fill="#ecfeff"/><text x="{x_positions[1]+14}" y="{y+27}" class="node">{_escape(_short(point["failure_mode"], 22))}</text>')
        nodes.append(f'<rect x="{x_positions[2]}" y="{y}" width="160" height="44" rx="10" fill="#fef9c3"/><text x="{x_positions[2]+14}" y="{y+27}" class="node">{_escape(point["evidence"])}</text>')
        nodes.append(f'<rect x="{x_positions[3]}" y="{y}" width="170" height="44" rx="10" fill="#dcfce7"/><text x="{x_positions[3]+14}" y="{y+27}" class="node">{_escape(_short(point["operator_action"], 20))}</text>')
        edges.extend([
            f'<path d="M240 {y+22} L330 {y+22}" class="edge"/>',
            f'<path d="M520 {y+22} L610 {y+22}" class="edge"/>',
            f'<path d="M770 {y+22} L870 {y+22}" class="edge"/>',
        ])
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="500" viewBox="0 0 1120 500" role="img" aria-label="{_escape(COMPANY)} evidence map">
  <defs>
    <style>
      .title {{ font: 750 28px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill:#111827; }}
      .node {{ font: 600 13px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill:#1f2937; }}
      .head {{ font: 700 14px -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; fill:#64748b; }}
      .edge {{ stroke:#94a3b8; stroke-width:2; fill:none; marker-end:url(#arrow); }}
    </style>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8"/></marker>
  </defs>
  <rect width="1120" height="500" fill="#ffffff"/>
  <text x="56" y="52" class="title">{_escape(COMPANY)} evidence path</text>
  <text x="80" y="82" class="head">scenario</text><text x="330" y="82" class="head">failure mode</text><text x="610" y="82" class="head">evidence</text><text x="870" y="82" class="head">operator action</text>
  {''.join(edges)}
  {''.join(nodes)}
</svg>
"""

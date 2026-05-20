from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


COMPANY = 'Warm Path Evidence Ranker'
REPO = 'warm-path-ranker'
PROJECT_TERMS = ['evidence', 'workflow', 'review', 'claims', 'fixtures', 'replay', 'handoff', 'trace', 'policy', 'decision', 'coverage', 'latency']
PROJECT_METRICS = ['evidence_coverage', 'handoff_risk', 'claim_precision', 'review_latency']
PROJECT_FAILURES = ['evidence_drift', 'handoff_gap', 'claim_misroute', 'review_blindspot']
PROJECT_ARCHETYPES = [{'name': 'evidence replay', 'trigger': 'source evidence changes while workflow context is stale', 'expected': 'block release until cited evidence is regenerated'}, {'name': 'handoff boundary probe', 'trigger': 'handoff crosses a policy or trust boundary', 'expected': 'route to reviewer with evidence packet'}, {'name': 'claim regression harness', 'trigger': 'claim behavior regresses against the last accepted fixture', 'expected': 'open a regression issue with trace and benchmark delta'}, {'name': 'review operator packet', 'trigger': 'review output needs a human-readable audit packet', 'expected': 'accept only if decision claims cite fixture evidence'}]
PROJECT_DIRECTION = 'A local warm-path scoring and evidence replay harness that turns a set of candidate relationship paths into ranked, cited recommendations with repeatable review gates for backchannel workflows.'
VISUAL_THEME = {'name': 'clinical ops', 'bg': '#f7faf9', 'ink': '#10201c', 'muted': '#475569', 'border': '#d7e2df', 'a': '#0f766e', 'b': '#4f46e5', 'c': '#b45309', 'd': '#2563eb', 'soft_a': '#ecfdf5', 'soft_b': '#eef2ff', 'soft_c': '#fffbeb', 'soft_d': '#f0f9ff', 'hero': 'Evidence Triage Board', 'left': 'operational gates under review', 'right': 'review packets with citations', 'chain': 'evidence-to-decision chain', 'lane': 'case lane', 'gate': 'failure gate', 'action': 'clinical action'}
HERO_TITLE = 'Warm Path Evidence Ranker'


def _short(value: str, limit: int = 44) -> str:
    value = " ".join(value.split())
    return value if len(value) <= limit else value[: limit - 1].rstrip() + "..."


def _wrap(value: str, limit: int = 48, max_lines: int = 3) -> list[str]:
    words = " ".join(value.split()).split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        candidate = " ".join([*current, word])
        if len(candidate) <= limit:
            current.append(word)
            continue
        if current:
            lines.append(" ".join(current))
        current = [word]
        if len(lines) == max_lines:
            break
    if current and len(lines) < max_lines:
        lines.append(" ".join(current))
    if len(lines) == max_lines and len(" ".join(words)) > len(" ".join(lines)):
        lines[-1] = _short(lines[-1], max(8, limit - 1))
    return lines or [""]


def _text_block(
    value: str,
    *,
    x: int,
    y: int,
    css: str,
    limit: int,
    max_lines: int,
    line_height: int,
) -> str:
    parts = [f'<text class="{css}" x="{x}" y="{y}">']
    for index, line in enumerate(_wrap(value, limit=limit, max_lines=max_lines)):
        dy = 0 if index == 0 else line_height
        parts.append(f'<tspan x="{x}" dy="{dy}">{_escape(line)}</tspan>')
    parts.append("</text>")
    return "".join(parts)


def _escape(value: object) -> str:
    return html.escape(str(value), quote=True)


def _human(value: str) -> str:
    return value.replace("_", " ")


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
            "This local harness runs a deterministic pressure test around "
            f"{PROJECT_TERMS[0]}, {PROJECT_TERMS[1]}, and {PROJECT_TERMS[2]}. "
            "The useful part is the repeatable evidence path from fixture "
            "to failure to operator action."
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
            {"name": "fixture_replay", "purpose": f"exercise {PROJECT_TERMS[0]} and {PROJECT_TERMS[1]} cases"},
            {"name": "strategy_model", "purpose": f"score {PROJECT_METRICS[0]} and {PROJECT_METRICS[1]}"},
            {"name": "evidence_lock", "purpose": "reject narrative claims without fixture evidence IDs"},
            {"name": "operator_packet", "purpose": "emit dashboard, SVG readout, CSV, markdown report, and demo pack"},
        ],
        "pressure_index": model["pressure_index"],
        "top_leverage_points": model["top_leverage_points"],
    }


def _working_svg(model: dict[str, Any]) -> str:
    t = VISUAL_THEME
    colors = [t["a"], t["b"], t["c"], t["d"]]
    rows = []
    cards = []
    for index, point in enumerate(model["top_leverage_points"]):
        y = 366 + index * 68
        width = min(390, 232 + int(float(point["severity"]) * 56))
        rows.append(
            f'<text x="92" y="{y - 12}" class="label">{_escape(_human(point["metric"]))}</text>'
            f'<text x="460" y="{y - 12}" class="mono">{_escape(point["evidence"])}</text>'
            f'<rect x="92" y="{y}" width="396" height="14" rx="7" fill="#e5e7eb"/>'
            f'<rect x="92" y="{y}" width="{width}" height="14" rx="7" fill="{colors[index % len(colors)]}"/>'
            f'<text x="92" y="{y + 40}" class="caption">{_escape(_short(point["scenario"], 48))}</text>'
        )
        card_x = 626 + (index % 2) * 238
        card_y = 350 + (index // 2) * 144
        cards.append(
            f'<rect class="actioncard" x="{card_x}" y="{card_y}" width="212" height="118" rx="8"/>'
            f'<text class="rank" x="{card_x + 18}" y="{card_y + 28}">gate {index + 1}</text>'
            + _text_block(
                point["operator_action"],
                x=card_x + 18,
                y=card_y + 56,
                css="cardtext",
                limit=24,
                max_lines=3,
                line_height=17,
            )
            + f'<text class="mono" x="{card_x + 18}" y="{card_y + 102}">{_escape(point["evidence"])}</text>'
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="700" viewBox="0 0 1120 700" role="img" aria-label="{_escape(COMPANY)} visual evidence dashboard">
  <defs>
    <style>
      .bg {{ fill:{t["bg"]}; }}
      .panel {{ fill:#ffffff; stroke:{t["border"]}; stroke-width:1.1; }}
      .card {{ fill:#ffffff; stroke:{t["border"]}; stroke-width:1.1; }}
      .actioncard {{ fill:#fbfdff; stroke:{t["border"]}; stroke-width:1.1; }}
      .title {{ font:760 30px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; fill:{t["ink"]}; }}
      .sub {{ font:420 15px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; fill:{t["muted"]}; }}
      .label {{ font:700 14px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; fill:#1f2937; }}
      .caption {{ font:500 12px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; fill:#64748b; }}
      .small {{ font:650 12px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; fill:#64748b; }}
      .metric {{ font:780 29px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; fill:#0f172a; }}
      .rank {{ font:760 13px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; fill:{t["a"]}; }}
      .cardtext {{ font:650 14px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; fill:#142033; }}
      .mono {{ font:700 12px ui-monospace,SFMono-Regular,Menlo,monospace; fill:#334155; }}
    </style>
  </defs>
  <rect class="bg" width="1120" height="700"/>
  <rect class="panel" x="28" y="28" width="1064" height="644" rx="8"/>
  <text class="title" x="64" y="76">{_escape(HERO_TITLE)}</text>
  {_text_block(PROJECT_DIRECTION, x=64, y=108, css="sub", limit=86, max_lines=2, line_height=22)}
  <rect class="card" x="64" y="166" width="232" height="84" rx="8"/>
  <text class="small" x="84" y="194">pressure index</text>
  <text class="metric" x="84" y="230">{model["pressure_index"]}</text>
  <rect class="card" x="320" y="166" width="232" height="84" rx="8"/>
  <text class="small" x="340" y="194">evidence density</text>
  <text class="metric" x="340" y="230">{model["evidence_density"]}</text>
  <rect class="card" x="576" y="166" width="480" height="84" rx="8"/>
  <text class="small" x="596" y="194">highest leverage path</text>
  {_text_block(model["top_leverage_points"][0]["scenario"], x=596, y=224, css="label", limit=56, max_lines=1, line_height=16)}
  <rect class="card" x="64" y="292" width="492" height="338" rx="8"/>
  <text class="label" x="92" y="322">{_escape(t["left"])}</text>
  {''.join(rows)}
  <text class="label" x="626" y="324">{_escape(t["right"])}</text>
  {''.join(cards)}
</svg>
"""


def _evidence_svg(model: dict[str, Any]) -> str:
    t = VISUAL_THEME
    nodes = []
    edges = []
    x_positions = [64, 294, 548, 764]
    for index, point in enumerate(model["top_leverage_points"]):
        y = 118 + index * 88
        nodes.append(
            f'<rect class="lane" x="{x_positions[0]}" y="{y}" width="178" height="56" rx="8"/>'
            + _text_block(point["scenario"], x=x_positions[0] + 14, y=y + 23, css="node", limit=21, max_lines=2, line_height=16)
        )
        nodes.append(
            f'<rect class="failure" x="{x_positions[1]}" y="{y}" width="186" height="56" rx="8"/>'
            f'<text x="{x_positions[1] + 14}" y="{y + 34}" class="node">{_escape(_human(point["failure_mode"]))}</text>'
        )
        nodes.append(
            f'<rect class="evidencebox" x="{x_positions[2]}" y="{y}" width="146" height="56" rx="8"/>'
            f'<text x="{x_positions[2] + 27}" y="{y + 35}" class="mono">{_escape(point["evidence"])}</text>'
        )
        nodes.append(
            f'<rect class="actionbox" x="{x_positions[3]}" y="{y}" width="292" height="56" rx="8"/>'
            + _text_block(point["operator_action"], x=x_positions[3] + 14, y=y + 23, css="node", limit=36, max_lines=2, line_height=16)
        )
        edges.extend([
            f'<path d="M242 {y + 28} L294 {y + 28}" class="edge"/>',
            f'<path d="M480 {y + 28} L548 {y + 28}" class="edge"/>',
            f'<path d="M694 {y + 28} L764 {y + 28}" class="edge"/>',
        ])
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="500" viewBox="0 0 1120 500" role="img" aria-label="{_escape(COMPANY)} evidence map">
  <defs>
    <style>
      .bg {{ fill:{t["bg"]}; }}
      .panel {{ fill:#ffffff; stroke:{t["border"]}; stroke-width:1.1; }}
      .title {{ font:760 28px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; fill:{t["ink"]}; }}
      .node {{ font:620 13px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; fill:#1f2937; }}
      .head {{ font:700 14px -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; fill:#64748b; }}
      .mono {{ font:720 13px ui-monospace,SFMono-Regular,Menlo,monospace; fill:#334155; }}
      .edge {{ stroke:#94a3b8; stroke-width:2; fill:none; marker-end:url(#arrow); }}
      .lane {{ fill:{t["soft_a"]}; stroke:{t["border"]}; }}
      .failure {{ fill:{t["soft_b"]}; stroke:{t["border"]}; }}
      .evidencebox {{ fill:{t["soft_c"]}; stroke:{t["border"]}; }}
      .actionbox {{ fill:{t["soft_d"]}; stroke:{t["border"]}; }}
    </style>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8"/></marker>
  </defs>
  <rect class="bg" width="1120" height="500"/>
  <rect class="panel" x="28" y="28" width="1064" height="444" rx="8"/>
  <text x="56" y="70" class="title">{_escape(COMPANY)} {_escape(t["chain"])}</text>
  <text x="64" y="104" class="head">{_escape(t["lane"])}</text><text x="294" y="104" class="head">{_escape(t["gate"])}</text><text x="548" y="104" class="head">evidence</text><text x="764" y="104" class="head">{_escape(t["action"])}</text>
  {''.join(edges)}
  {''.join(nodes)}
</svg>
"""

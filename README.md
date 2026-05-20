# Warm Path Evidence Ranker

A local warm-path scoring and evidence replay harness that turns a set of candidate relationship paths into ranked, cited recommendations with repeatable review gates for backchannel workflows.

![Warm Path Evidence Ranker working dashboard](outputs/project_working.svg)

## Why it exists

Warm-introduction teams often get several plausible relationship paths, but the hard operational question is which route is most likely to create a useful conversation without wasting social capital. Graph distance alone misses recency, role fit, evidence freshness, and handoff risk.

The project is intentionally built as a local replay harness instead of a slide. It creates fixtures, plants realistic failure modes, produces citation-locked evidence, and turns the result into a dashboard a reviewer can inspect without credentials or hosted services.

## What is inside

- Deterministic fixture generation for the company-specific risk surface.
- Strategy code in `src/warm_path_ranker/strategy.py` with project-specific scoring and visual evidence.
- Citation-locked reports where every decision claim points to a generated evidence ID.
- Two regenerated visual artifacts: `outputs/project_working.svg` and `outputs/evidence_map.svg`.
- A portable demo pack with JSON, CSV, Markdown, HTML, SVG, benchmark, and test artifacts.

![Warm Path Evidence Ranker evidence map](outputs/evidence_map.svg)

## Signals it measures

- `Evidence coverage`
- `whole risk`
- `pitch precision`
- `mapped latency`

## Failure modes it plants

- evidence drift
- whole gap
- pitch misroute
- mapped blindspot

## Run it locally

```bash
uv sync
uv run warm-path-ranker all
uv run pytest -q
uv run ruff check .
```

## Outputs worth opening

- `outputs/dashboard.html`
- `outputs/project_working.svg`
- `outputs/evidence_map.svg`
- `outputs/operator_brief.md`
- `outputs/decision_report.md`
- `outputs/strategy_model.json`
- `outputs/demo_pack.zip`

## Boundary

Everything runs locally against synthetic fixtures. There are no credentials, no customer records, no outreach files, and no hosted API dependency.

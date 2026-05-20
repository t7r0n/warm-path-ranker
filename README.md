# Pathrank

An open source, on prem friendly warm path scoring + evaluation harness that turns Verata's "we found 11 paths" into "this path is a 0.78 - here are the 3 features that matter," with a published benchmark for the PE backchannel use case.

![Pathrank working dashboard](outputs/project_working.svg)

## Why it exists

Verata's whole pitch is "we mapped your firm's collective network so you can backchannel into deals." But the hardest moment for the buyer - the actual associate at Apollo or Vista - is the 30 seconds before sending the warm intro request: which of the 11 paths the graph surfaces is the one most likely to result in a useful conversation?

Most internal demos stop at a pretty chart. This repository is built around the harder part: a repeatable path from fixture, to failure, to evidence, to the operator action a serious team would actually trust.

## What is inside

- A deterministic replay harness tuned around verata, whole, and pitch.
- Company-specific strategy code in `src/pathrank/strategy.py`, not just README-level customization.
- Citation-locked reports where every decision claim has to point back to a generated evidence ID.
- Two visual artifacts generated from the latest run: `outputs/project_working.svg` and `outputs/evidence_map.svg`.
- A portable demo pack with JSON, CSV, Markdown, HTML, SVG, and benchmark artifacts.

![Pathrank evidence map](outputs/evidence_map.svg)

## Signals it measures

- `verata coverage`
- `whole risk`
- `pitch precision`
- `mapped latency`

## Failure modes it plants

- verata drift
- whole gap
- pitch misroute
- mapped blindspot

## Run it locally

```bash
uv sync
uv run pathrank all
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

## Sources

- https://www.veratainsight.com/solutions/talent
- https://www.ycombinator.com/companies/verata
- https://startupintros.com/orgs/verata
- https://www.eightcapital.com/podcast/spotlighting-verata
- https://www.linkedin.com/posts/josh-gardner-957903134_privateequity-operatingpartner-leadership-activity-7307448321965543425-3omX
- https://www.affinity.co/blog/ai-in-private-equity
- https://github.com/nicholasmanske
- https://www.linkedin.com/company/verata-insight

## Boundary

Everything runs locally against synthetic fixtures. There are no credentials, no customer records, no outreach files, and no hosted API dependency.

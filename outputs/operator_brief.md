# Operator Brief: Verata

Verata gets a local, deterministic pressure test around verata, whole, and pitch. The useful part is not the dashboard; it is the repeatable evidence path from fixture to failure to operator action.

## Highest-leverage checks

- verata evidence replay -> block release until cited evidence is regenerated (verata_coverage, evidence ev_0044).
- mapped operator packet -> accept only if decision claims cite fixture evidence (whole_risk, evidence ev_0099).
- pitch regression harness -> open a regression issue with trace and benchmark delta (pitch_precision, evidence ev_0022).
- whole boundary probe -> route to reviewer with evidence packet (mapped_latency, evidence ev_0033).

## What makes this useful

The workflow is intentionally local and deterministic. A reviewer can run the same fixture set, inspect the evidence IDs, open the dashboard, and see exactly why a recommendation passed, went to review, or blocked.

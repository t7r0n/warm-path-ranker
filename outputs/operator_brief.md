# Operator Brief: Pathrank

This local harness runs a deterministic pressure test around evidence, workflow, and review. The useful part is the repeatable evidence path from fixture to failure to operator action.

## Highest-leverage checks

- evidence replay -> block release until cited evidence is regenerated (evidence_coverage, evidence ev_0000).
- review operator packet -> accept only if decision claims cite fixture evidence (handoff_risk, evidence ev_0055).
- claim regression harness -> open a regression issue with trace and benchmark delta (claim_precision, evidence ev_0066).
- handoff boundary probe -> route to reviewer with evidence packet (review_latency, evidence ev_0121).

## What makes this useful

The workflow is intentionally local and deterministic. A reviewer can run the same fixture set, inspect the evidence IDs, open the dashboard, and see exactly why a recommendation passed, went to review, or blocked.

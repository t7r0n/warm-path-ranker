# Failure Matrix: Warm Path Evidence Ranker

| Scenario | Failure mode | Metric | Gate | Evidence |
| --- | --- | --- | --- | --- |
| evidence replay | evidence_drift | evidence_coverage | block release until cited evidence is regenerated | ev_0000 |
| review operator packet | review_blindspot | review_latency | accept only if decision claims cite fixture evidence | ev_0007 |
| review operator packet | review_blindspot | review_latency | accept only if decision claims cite fixture evidence | ev_0011 |
| claim regression harness | claim_misroute | claim_precision | open a regression issue with trace and benchmark delta | ev_0014 |
| handoff boundary probe | handoff_gap | handoff_risk | route to reviewer with evidence packet | ev_0021 |
| claim regression harness | claim_misroute | claim_precision | open a regression issue with trace and benchmark delta | ev_0022 |
| evidence replay | evidence_drift | evidence_coverage | block release until cited evidence is regenerated | ev_0028 |

# Decision Report: Pathrank

An open source, on prem friendly warm path scoring + evaluation harness that turns Pathrank's "we found 11 paths" into "this path is a 0.78 - here are the 3 features that matter," with a published benchmark for the PE backchannel use case.

## Evidence-Grounded Findings

CLAIM: claim regression harness should `open a regression issue with trace and benchmark delta` because blocks=3 reviews=5 mean_severity=2.528. [EVID: ev_0066]
CLAIM: evidence replay should `block release until cited evidence is regenerated` because blocks=4 reviews=5 mean_severity=2.611. [EVID: ev_0000]
CLAIM: handoff boundary probe should `route to reviewer with evidence packet` because blocks=3 reviews=4 mean_severity=2.528. [EVID: ev_0121]
CLAIM: review operator packet should `accept only if decision claims cite fixture evidence` because blocks=4 reviews=5 mean_severity=2.556. [EVID: ev_0055]

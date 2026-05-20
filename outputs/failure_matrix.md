# Failure Matrix: Pathrank

| Scenario | Failure mode | Metric | Gate | Evidence |
| --- | --- | --- | --- | --- |
| verata evidence replay | verata_drift | verata_coverage | block release until cited evidence is regenerated | ev_0000 |
| mapped operator packet | mapped_blindspot | mapped_latency | accept only if decision claims cite fixture evidence | ev_0007 |
| mapped operator packet | mapped_blindspot | mapped_latency | accept only if decision claims cite fixture evidence | ev_0011 |
| pitch regression harness | pitch_misroute | pitch_precision | open a regression issue with trace and benchmark delta | ev_0014 |
| whole boundary probe | whole_gap | whole_risk | route to reviewer with evidence packet | ev_0021 |
| pitch regression harness | pitch_misroute | pitch_precision | open a regression issue with trace and benchmark delta | ev_0022 |
| verata evidence replay | verata_drift | verata_coverage | block release until cited evidence is regenerated | ev_0028 |

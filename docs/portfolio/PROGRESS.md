# Portfolio checkpoint — 2026-10-03

This is a dated remote recovery checkpoint, not a live dashboard. Recheck all PR heads and workflow states before acting.

## Verified prior work
- Profile YAML fix: 71ef6ca. Quantdeck YAML fix: 19d45b9. Do not repeat these changes.
- pe-financial-calculator license documentation fix: 695cab7. CI run 37059482474 and deployment 37059482428 succeeded.
- Profile daily-oss-scout run 37115129731 and quantdeck daily-maintenance run 37114470915 got past YAML but failed before model invocation on missing OIDC configuration. Both workflows were reversibly paused on 2026-10-03, with disabled_manually verified. They were not declared repaired or green.

## Continue existing work first
- quantdeck#6 already proposes replacing model maintenance with read-only weekly checks; preserve and review that draft rather than creating another repair.
- heykav#3 already redesigns scout token handling; it remains a draft and still depends on Claude OAuth. Do not activate it under a free-only policy.
- Existing enhancement PRs include fpga-sim-core#7, microprice-rust#13, quantdeck#7, vanna#19, photoface#8, pe-financial-calculator#8 and heykav#5. Review them before starting duplicate code or documentation work.
- fpga-sim-core#7 head 49d626f2 had green Linux, macOS, sanitizer and clang-tidy checks at inspection; it is not merged.
- pe-financial-calculator#7 proposes a license change that conflicts with current main. Owner decision required before changing the license.
- ArcticDB#3442 has maintainer requests for regression tests, a concise description and a contributor legal sign-off. Technical preparation is possible; the assistant must not make the legal attestation for the author.
- Riskfolio-Lib#258 is closed; the maintainer reported an alternative fix. Do not revive it merely because old CI notifications remain unread.

## Next step
Refresh GitHub, inspect actionable maintainer feedback and current CI, then select one non-duplicate bounded work unit. Keep verification evidence and the next action in the local working ledger. No notification was marked read during recovery.

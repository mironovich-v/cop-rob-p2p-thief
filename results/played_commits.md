# Played-commit map — which code played which series

Our artifacts do not carry a `github_commit` field (the wire identity declares
one at negotiate, but it is not written into the four JSON artifacts). This file
is therefore the authoritative record of **which commit of ours played which
series**, so a grader holding only the two submission repositories can tie a
result to code without the workspace repo.

**Every commit listed here is reachable in both submission repositories on the
`workspace-history` branch**, which mirrors the workspace repo
(`github.com/mironovich-v/cop-rob-p2p`). `git rev-parse` and `git show` resolve
there; the `main` branch of each submission repo is the exported agent tree,
which has its own history and does **not** contain these hashes.

Provenance is stated per row and is not uniform — read it.

## Counted series (rule 52)

| # | Date | Opponent | Our commit | Provenance |
| --- | --- | --- | --- | --- |
| 1 | 2026-08-18 22:00:05–22:03:35 IDT | nis-yar1 | `950ab89` | **Inferred**, not recorded. The series predates our `playing_commit` field (added 2026-08-21). Bracketed by merges: `950ab89` landed 21:38 and the next merge `c2bd209` — itself the ledger commit *for this series* — landed 22:08. |
| 2 | 2026-08-22 16:22:30–16:27:42 IDT | vibecode | `cabcb074f7ce9e5851a050630d95b3a8bdeb01ba` | **Recorded** in vibecode's own result artifact (`results/counted/vibecode-2026-08-22/result_..._vibecode-copy.json`), which lists it per sub-game. Independently declared by us at negotiate. |

## Friendlies (uncounted)

| Date | Opponent | Our commit | Provenance |
| --- | --- | --- | --- |
| 2026-08-18 | nis-yar1 (friendly, re-friendly) | pre-`playing_commit` | Not recorded; same era as counted series 1. |
| 2026-08-21 ~16:47 | il-nv-ai (game 1, we police) | `c69a134` | Declared at fire; verified from `playing_commit()` before launch. |
| 2026-08-21 ~17:17 | il-nv-ai (game 2, we thief) | `0e463ce` | Declared at fire; verified from `playing_commit()` before launch. |
| 2026-08-21 21:19 / 21:38 | vibecode (friendlies 1–2) | `1c0c56ee5167b8abd77b57813c77ea7f4d8bc41d` | **Recorded** in vibecode's result artifact. |
| 2026-08-22 16:09 | vibecode (friendly, both sides rebuilt) | `cabcb074f7ce9e5851a050630d95b3a8bdeb01ba` | **Recorded** in vibecode's result artifact. |

## Keeping this current

A new series must add a row here at settlement, alongside archiving the
artifacts and advancing the ledger. The underlying gap — that our own artifacts
omit `github_commit` while partners populate it — is worth closing in code; until
it is, this file is the only place the mapping exists on our side.

# Played-commit map — which code played which series

Since 2026-08-22 our artifacts carry `github_commit` themselves — in the
declaration group block and on every result sub-game row — so a series played
from then on states its own commit. **The series below were played before that
landed**, and this file is the record for them, so a grader holding only the two
submission repositories can still tie those results to code.

**Every commit listed here is reachable in both submission repositories on the
`workspace-history` branch**, which mirrors the workspace repo
(`github.com/mironovich-v/cop-rob-p2p`). `git rev-parse` and `git show` resolve
there; the `main` branch of each submission repo is the exported agent tree,
which has its own history and does **not** contain these hashes.

Provenance is stated per row and is not uniform — read it.

## Why we name ONE commit where some teams name two

We run a **single canonical core**. `police_agent` and `thief_agent` are entry
points into the same code, and the role for a sub-game is a launch flag — so the
same binary plays both roles and one commit executes for the whole series. The
commit named below is that commit.

Teams whose cop and thief are separate codebases in separate repositories
legitimately report a different commit per role, because different code really
does run. vibecode do exactly that (cop `043e4fd`, thief `038ec0a` on
2026-08-22). The difference between their two values and our one is
**architectural, not under-reporting**.

We deliberately do **not** report the submission repos' own `main` commits per
role (e.g. police `ba7af5f`, thief `b971834`). Those are export commits produced
by `scripts/export_repos.py` *after* a series, on a branch with its own history;
no code from them ever executed. Naming them per sub-game would look more precise
while asserting something false.

The chain resolves from either direction, and neither requires the core repo:

```
our artifact  github_commit ─────────────► <workspace commit>
                                              ▲          ▲
police repo  core_manifest.core_commit ───────┘          │
thief  repo  core_manifest.core_commit ──────────────────┘

<workspace commit> resolves on `workspace-history` in BOTH submission repos.
```

Each export also carries `role`, `repo`, `sibling_repo` and `workspace_repo` in
`core_manifest.json`, so a grader landing in one role repo can reach the executed
commit and the sibling repo without being told where to look.

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
| 2026-08-23 20:20 | **imreeyal (COUNTED series 3)** | `eae0d7096f211ec2e2c7a278b3d80240ad7ac018` | **Recorded in our own artifact** (both sides' commits present); theirs `f5a64c06`. |

## Keeping this current

A new series must add a row here at settlement, alongside archiving the
artifacts and advancing the ledger. The underlying gap — that our own artifacts
omit `github_commit` while partners populate it — is worth closing in code; until
it is, this file is the only place the mapping exists on our side.

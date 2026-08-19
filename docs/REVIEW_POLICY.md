# REVIEW_POLICY — Reviewability, PR Size & Artifact Handling

> Expanded review policy (guideline §1.4, recommended for non-trivial projects).
> The structured commit body in `CLAUDE.md` §2.9.1 is this repo's PR gate (the
> `.github/pull_request_template.md` is intentionally absent by owner request).

## PR size

- Target **50–200** changed LOC; soft cap **300**; hard cap **500** (owner
  approval, documented). If a planned change would exceed the soft cap, STOP and
  propose a decomposition before editing.
- Exactly **one primary purpose** per PR. Separate: source logic · tests · docs ·
  generated artifacts · dependency/lockfile · refactors.
- Generated artifacts and `uv.lock` are counted separately from logic LOC.

## Allowed exceptions (must still be justified in the commit body)

Initial documentation/scaffold import; lockfile-only update; generated-artifact
PR; final README/academic PR; owner-approved bulk refactor. (Stage -1 doc PRs and
the bootstrap use the documentation-import exception.)

## Decomposition rules

- One mechanism → one PRD → one (or few) PR slices; see `docs/TODO.md`.
- Author the mechanism's `PRD_*.md` before its implementation slice.
- Keep tests in the same PR as the behavior they cover (TDD).
- Strict linear stage progression: no next-stage work until the current stage is
  100% merged.

## Quality gates (every implementation PR)

`uv sync` · `ruff check src tests` (zero) · `pytest` (all pass) · coverage
**≥85%** · every Python file **≤150 code lines** · no hard-coded game/config
params (grep gate; `CFG` only) · secret scan · interop slices run
`tests/conformance/` against the fetched league kit with **no vector edits**.

## Per-PR tracking gates (every PR, including docs)

- **`docs/PROMPTS.md`** — add exactly one entry for the PR.
- **`COSTS.md`** — add exactly one ledger row for the PR.
- **`docs/TODO.md`** — check the completed task's `[x]` box in the same PR.
- **`docs/PRD.md` §14 Open Decisions** — update if a decision was made.
- **`docs/requirements_matrix.md`** — update the status of affected requirements.
- **`docs/PRD.md` §4 acceptance criteria** — check any AC newly satisfied.

## Artifact handling

Source/tests/docs/config tracked; heavy generated outputs (logs, results,
executed notebooks, exports under `dist/`) are git-ignored and reproducible via
documented commands. The league kit is external and git-ignored (fetch via
`scripts/fetch_interop.sh`; see `docs/INTEROP.md`).

## Reviewer checklist

Branch is task-specific and based on current `main`; commit uses the §2.9.1
structured body with correct `[Stage-X]`/`[Task-Y]` tags and ≤72-char title;
`Co-Authored-By` trailer present; scope matches the PR; quality gates pass; no
secrets; no hard-coded params; PRDs/TODO/requirements-matrix updated as needed;
no direct commits to `main` (except the one authorized bootstrap); no
force-push/rebase/remote-branch deletion; PR created/reviewed/**squash-merged by
the human owner**.

## Git delegation (summary; full policy in `CLAUDE.md` §2.2/§2.9)

AI may: branch, add intended files, commit, push the PR branch, and (after the
owner confirms a squash-merge) delete the local branch. AI must not: commit/push
to `main`, create/merge/squash PRs, tag releases, force-push, reset, rebase
shared history, delete remote branches, or change remotes.

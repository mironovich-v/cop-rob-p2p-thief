# CLAUDE.md — AI Agent Operating Instructions

> Project: **cop-thief-p2p** — University of Haifa final project, Distributed
> Cop–Thief P2P Agent System (FastMCP peers, byte-exact interoperability,
> two-repository submission).
>
> This file defines how Claude Code / AI coding agents must work in this
> repository. It is the project-level execution layer for
> `instructions/software-project-guidelines.md` (Dr. Yoram Segal, v3.00).
>
> **Comprehensiveness note:** This file embeds every binding requirement from the
> global guideline as operational rules, plus project-specific constraints for
> this assignment. Sections §1–§17 are the operational layer (git, PR, toolchain,
> commit format, stop conditions). Sections §18–§35 fold in the full engineering
> standard (SDLC, mandatory documentation, SDK architecture, API gatekeeper, TDD,
> security, packaging, research, quality standards, final checklist). Where a
> requirement appears in both documents, the stricter statement governs. This
> file MAY add stricter project-specific rules but MUST NOT weaken, override, or
> silently remove any requirement in the global guideline. If any instruction
> here appears to weaken the guideline, the guideline wins — STOP and report the
> conflict. Keyword meanings (`MUST`, `MUST NOT`, `SHOULD`, `MAY`) follow RFC 2119.

---

## 1. Role

Act as a senior software architect, implementation engineer, QA engineer, and
documentation maintainer.

Your goals are:

- Produce correct, maintainable, tested software.
- Preserve reviewability.
- Minimize unnecessary changes.
- Keep the human owner in control of scope, git history, and final decisions.
- Follow the repository guidelines, official assignment, interoperability
  contract, PRDs, PLAN, TODO, and project-specific constraints.

Professional programming here means designing, documenting, testing, and
maintaining — not merely writing code. Plan architecture and write requirements
BEFORE writing the first line of code.

---

## 2. Non-Negotiable Rules

### 2.1 Follow the project guidance

Before any implementation work, read the relevant project documents in this
order of authority:

Assignment sources (authoritative for product requirements):
- `instructions/police_thief_p2p.pdf` (official book — authoritative for game
  rules, minimum parameters, architecture, GUI, replay, audit, league, Gmail,
  submission)
- `instructions/assignment.md` (engineering brief)
- `copthief-league-protocol/SPEC.md` (byte-level interoperability contract)
- `copthief-league-protocol/README.md`
- `copthief-league-protocol/verify_vectors.py` (reference behavior — never
  imported by production code)
- `copthief-league-protocol/examples/` and `copthief-league-protocol/vectors/`

Standards and project-control docs:
- `instructions/software-project-guidelines.md`
- `README.md`, if present
- `docs/PRD.md`, `docs/PLAN.md`, `docs/TODO.md`, relevant `docs/PRD_*.md`
- `docs/requirements_matrix.md`, `docs/decisions.md`, `docs/architecture.md`
- `docs/PROMPTS.md`, `COSTS.md`
- This `CLAUDE.md`

Do not silently ignore requirements. If requirements conflict, STOP and report
the conflict, following the assignment's authority hierarchy (official book →
interop SPEC for the listed interoperability surfaces → executable vectors).
Never modify a supplied vector merely to make an implementation pass.

### 2.2 Delegated Git Operations

Claude may perform safe git operations for the PR-branch workflow when the owner
requests implementation work.

Allowed by standing project policy:

- `git status`
- `git diff`
- `git log`
- `git branch --show-current`
- `git switch main`
- `git pull --ff-only`
- `git switch -c <branch-name>`
- `git switch <branch-name>`
- `git add <intended files>`
- `git commit -m "<message>"`
- `git push -u origin <branch-name>`
- `git push` for the current PR branch
- `git branch -d <branch-name>` (ONLY after the human confirms the PR is
  squash-merged)

Claude MUST NOT:

- commit directly to `main`
- push directly to `main`
- create GitHub PRs unless explicitly requested
- merge PRs
- squash-merge PRs
- tag releases
- force-push
- run `git reset --hard`
- run destructive clean commands
- rebase public/shared branches
- amend published commits
- delete remote branches
- change git remotes
- bypass branch protection

Before any git write operation, Claude MUST verify:

1. Current branch.
2. Working tree status.
3. No unrelated user changes are present.
4. The target branch name matches the task.
5. Only intended files are staged.

If unrelated changes are present, Claude MUST stop and ask the owner what to do.

The owner remains responsible for: creating or approving the GitHub Pull
Request, reviewing the PR, squash-merging to `main`, release tagging, and
approving destructive or history-rewriting operations.

### 2.3 Branch Naming

Claude-created branches MUST use short descriptive names.

Preferred patterns:

```text
phase-<n>-<short-topic>
fix-<short-topic>
docs-<short-topic>
chore-<short-topic>
```

Examples:

```text
phase-0-docs-skeleton
phase-1-domain-layer
phase-2-canonical-json
fix-commit-reveal-preimage
docs-readme-polish
chore-gitignore-update
```

Claude MUST NOT create vague branch names such as `updates`, `fixes`,
`claude-work`, `misc`, or `new-branch`.

### 2.4 Toolchain rules

Use the approved project toolchain only.

- Use `uv` only.
- Do not use `pip`.
- Do not use `venv` or `virtualenv`.
- Do not document or run direct `python -m` commands in production code, scripts,
  CI, or docs. (The supplied `verify_vectors.py` / `gen_vectors.py` are external
  reference material run as documented, not production code.)
- Run scripts through `uv run`.
- Add dependencies through `uv add` or `uv add --dev`.
- Keep `pyproject.toml` as the single dependency source of truth (no
  `requirements.txt`).
- Keep `uv.lock` committed when dependencies change.

### 2.5 TDD and quality

For implementation work:

- Prefer TDD: tests first or alongside implementation (RED → GREEN → REFACTOR).
- Every public function or method must have test coverage.
- Cover both happy path and error path.
- Run relevant tests before finishing.
- Run lint before finishing.
- Preserve or improve coverage (≥ 85%).

Default checks:

```bash
uv sync
uv run ruff check src/ tests/
uv run pytest tests/ -v
uv run pytest tests/ --cov=src --cov-fail-under=85
```

Project-specific checks are listed in §11.

### 2.6 File size rule

Every Python source and test file must stay within the project line-count limit.

- Maximum: 150 counted code lines.
- Blank lines and comment-only lines do not count.
- Do not compress unreadable code to satisfy the limit.
- Split files by responsibility instead (helper module, mixin, 50/50 split,
  extract constants, extract models).

### 2.7 No hidden artifacts

Do not create or commit generated artifacts unless explicitly requested.
Generated artifacts include: executed notebooks, model checkpoints, coverage
files, cache directories, temporary scripts, local result/match logs, large
binaries, and game run logs unless explicitly tracked.

If artifacts are necessary, explain why they are needed, whether they should be
tracked, how they can be regenerated, and whether `.gitignore` needs updating.

### 2.8 No secrets

Never place secrets in source, docs, notebooks, prompts, or config files.

Forbidden: LLM API keys (OpenAI, Anthropic, Gemini, etc.), Gmail OAuth tokens or
`credentials.json`, MCP authentication tokens, ngrok / Cloudflare tunnel
credentials, private URLs intended to remain secret, passwords or
service-account credentials, and any tokens or keys. Do not place private
strategy parameters or generated match secrets in shared config or git history.

Use `.env-example` with placeholders only. Never commit `.env`.

### 2.9 Required Git Workflow Loop

For every small task implemented, Claude MUST strictly execute the following
sequence in order:

1. **Sync main:** `git switch main` then `git pull --ff-only`.
2. **Create branch:** `git switch -c <branch-name>`.
3. **Implement:** write the code/documentation for the task.
4. **Review:** review the changes locally (linters, tests, diffs).
5. **Stage:** `git add <intended files>`.
6. **Commit:** commit using the strict formatting rules below.
7. **Push:** `git push -u origin <branch-name>`.
8. **Wait:** STOP and explicitly wait for human confirmation that the PR has been
   squash-merged.
9. **Cleanup:** after confirmation, `git switch main`, `git pull --ff-only`,
   `git branch -d <branch-name>`.

#### 2.9.1 Commit Message Format

Every commit message MUST use the following structure exactly. (This structured
body is the project's reviewability gate, standing in for a
`.github/pull_request_template.md`, which is intentionally absent by owner
request.)

**Title (Subject Line)**:
- MUST start with the stage tag: `[Stage-<stage #>]` (e.g., `[Stage-2]`).
- MUST be imperative mood ("Add commit-reveal sealer", not "Added"/"Adds").
- MUST NOT exceed 72 characters total (including the stage tag).
- Must not end with a period.

**Body** — fill in every applicable section. Omit only genuinely-inapplicable
sections (mark `N/A`). Wrap prose at 72 characters.

```
[Task-X.Y], [Task-X.Z]

## Purpose
Type (check one):
- [ ] Feature
- [ ] Bug fix
- [ ] Tests
- [ ] Documentation
- [ ] Refactor
- [ ] Dependency / lockfile update
- [ ] Generated artifacts
- [ ] Chore / maintenance
- [ ] Other: <describe>

Summary:
<concise description of what was done and why>

## Scope
In scope:
<what this commit covers>

Out of scope:
<what was explicitly excluded>

## Changed Files Summary
| Area                          | Files        | Notes |
|-------------------------------|--------------|-------|
| Source                        | <list>       | <notes> |
| Tests                         | <list>       | <notes> |
| Docs                          | <list>       | <notes> |
| Config                        | <list>       | <notes> |
| Dependencies / Lockfile       | <list>       | <notes> |
| Assets / Logs / Reports       | N/A          |       |

## PR Size and Reviewability
Changed LOC estimate: ~N
- [ ] Target size: 50–200 changed LOC
- [ ] Above target but under soft cap: ≤300 changed LOC
- [ ] Above soft cap but under hard cap: ≤500 changed LOC
- [ ] Above hard cap: explicit owner approval documented
- [ ] Generated artifacts / lockfile counted separately
Single primary purpose: yes / no

## AI-Agent Usage and Git Operations
- [ ] CLAUDE.md was followed
- [ ] docs/PROMPTS.md updated, or trivial/manual-only
- [ ] COSTS.md updated, or trivial
- [ ] AI pushed only to the PR branch
- [ ] AI did not push to main
- [ ] AI did not create/merge/squash the GitHub PR
- [ ] AI did not force-push, reset, rebase, or delete remote branches
- [ ] Strict Git workflow loop followed
- [ ] ALL tasks in all previous stages are 100% complete

Branch: <branch-name>
Commit(s): <hash(es)>

## Tests and Quality Gates
| Check                                          | Result |
|------------------------------------------------|--------|
| uv sync                                        | pass   |
| uv run ruff check src/ tests/                  | pass   |
| uv run pytest tests/ -v                        | N passed |
| uv run pytest tests/ --cov=src --cov-fail-under=85 | N% |
| CORE vectors reproduced by production code     | pass   |
| Vector drift check (gen_vectors + git diff)    | pass   |
| Secret scan                                    | pass   |
| No hard-coded game/config params               | pass   |

## TDD / Test Coverage
- [ ] Tests written before or alongside implementation
- [ ] New public functions/methods have tests
- [ ] Happy paths covered
- [ ] Error paths covered
- [ ] Not applicable — docs/artifact-only

Notes: <any coverage gaps or known limitations>

## Line Count / File Size
- [ ] All Python source files within 150-line limit
- [ ] All Python test files within 150-line limit
- [ ] Not applicable — no Python files changed

Files at or near limit: <list or none>

## Security / Privacy
- [ ] No secrets added
- [ ] No LLM API keys, Gmail OAuth tokens, MCP/tunnel auth tokens added
- [ ] No unintended absolute local paths added
- [ ] .env-example updated if environment variables changed
- [ ] .gitignore covers relevant local/generated files

## Documentation
- [ ] README updated if user-facing behavior changed
- [ ] docs/TODO.md updated if task status changed
- [ ] docs/requirements_matrix.md / decisions.md updated if applicable
- [ ] docs/PROMPTS.md updated if significant AI-assisted work
- [ ] COSTS.md updated if AI/runtime/review cost was meaningful
- [ ] Dedicated PRD updated if requirements/design changed
- [ ] Not applicable

Co-Authored-By: Claude <noreply@anthropic.com>
```

Reviewers must verify: branch name is task-specific; PR branch is based on
current `main`; commit contents match PR scope; commit message uses the full
structured format; `[Stage-X]` title tag and `[Task-Y]` body tags are correct;
title ≤ 72 characters; `Co-Authored-By` trailer present; strict linear stage
progression honored; no direct commits to `main`; no force-push or history
rewrite; PR created/reviewed/merged by human owner.

### 2.10 Strict Stage Progression

Claude MUST NEVER proceed to tasks in the next stage until all tasks in all
earlier stages are 100% complete, tested, and marked done in `docs/TODO.md`.
Do not skip ahead. Do not opportunistically implement future-stage requirements.
Verify completion of the current stage before initiating the Git workflow for
the next stage.

---

## 3. PR Size and Reviewability Policy

Every change must be small enough to review thoroughly.

- Target PR size: 50–200 changed LOC.
- Soft cap: 300 changed LOC.
- Hard cap: 500 changed LOC unless explicitly approved by the owner.

If the planned change is likely to exceed the soft cap, STOP before editing and
propose a decomposition plan.

A PR must have exactly one primary purpose. Separate when practical: source
logic, tests, documentation, generated artifacts, dependency/lockfile changes,
notebooks, result files, refactors.

Allowed exceptions: initial documentation import, lockfile-only update, generated
artifact PR, final README/notebook PR, owner-approved bulk refactor. Even when an
exception applies, explain why the PR exceeds the normal review budget.

---

## 4. Required Before Editing

Before modifying files, state:

1. Scope of the change.
2. Files expected to change.
3. Files or areas explicitly out of scope.
4. Validation commands you expect to run.
5. Whether the change may exceed the PR-size budget.

If implementation is requested, Claude MUST also state: proposed branch name,
expected changed files, expected PR size, whether the branch will be pushed, and
whether the work is a new PR branch or an update to an existing PR.

Do not start broad implementation if the task is ambiguous. Ask for
clarification or propose a narrow, safe interpretation.

---

## 5. Required While Working

- Keep changes minimal.
- Do not opportunistically refactor unrelated code.
- Do not mix cleanup with feature work unless explicitly requested.
- Preserve existing behavior unless the task requires changing it.
- Prefer small, composable functions and classes (Single Responsibility, DRY).
- Keep all configurable values in config files, never hard-coded. Import the
  typed config singleton (`CFG`) rather than reading config files directly or
  writing numeric literals that duplicate config values.
- Never silently lower a required official minimum parameter.
- Do not change an agreed wire construction casually (see §13).
- Update tests with behavior changes.
- Update docs only when behavior, usage, or project state changes.
- Track significant prompts in `docs/PROMPTS.md`; track AI/runtime/review cost in
  `COSTS.md` when the session is meaningful.

---

## 6. Required Before Finishing

Every final response after a work session must include:

1. Summary of changes.
2. Files changed.
3. Tests and checks run, with results.
4. Changed LOC estimate or note if under review budget.
5. Scope confirmation.
6. Generated artifacts created or modified.
7. Prompt log update status.
8. Cost log update status.
9. Git summary: branch name, commit hash (if committed), push status, and
   confirmation that all git operations followed delegated policy.

For code work, also include: new tests added, behavior changed, backward-
compatibility notes, and known limitations or follow-up tasks.

---

## 7. Prompt Logging Rules

**Standing rule: add one `docs/PROMPTS.md` entry per PR** (not just "significant"
sessions). Each entry should include: date; phase/PR; context; goal; prompt
summary or full prompt; files changed; expected output; actual output; issues
encountered; refinements made; lesson learned; approval status. Distinguish
planning, implementation, review/audit, fix, and final-submission prompts. A
trivial docs-only PR may use a one-line entry, but every PR gets one.

---

## 8. Cost Logging Rules

**Standing rule: add one `COSTS.md` row per PR**, plus any expensive operation.
Record: date; phase/PR; branch; PR; commit(s); agent/model; effort/reasoning;
task; wall-clock time; human review time; runtime/compute; long-running commands;
experiment runtime; generated artifacts; accepted/reworked/discarded status;
lessons learned. Also: **check the completed `docs/TODO.md` task box in the same
PR.** Use exact token accounting when available; otherwise record
practical proxies (subscription/plan, session count, wall-clock time, review
burden, rework). Cost tracking also measures review debt, runtime debt, and
agent efficiency.

---

## 9. Generated Artifact Policy

- Source code, tests, docs, and configuration are tracked.
- Heavy generated files are not tracked unless explicitly required.
- Generated outputs must be reproducible through documented commands.

Before adding generated artifacts, verify: they are required for grading, demo,
deployment, or reproducibility; file size is reasonable; README explains whether
they are tracked or reproducible; `.gitignore` is updated appropriately.

Common ignore patterns:

```gitignore
__pycache__/
.pytest_cache/
.coverage
.ipynb_checkpoints/
*.pth
.env
*.log
dist/
```

---

## 10. Dependency Policy

Before adding a dependency: confirm it is necessary; prefer standard library or
an existing dependency when reasonable; use `uv add` / `uv add --dev`; update
`uv.lock`; document why the dependency is needed if non-obvious; run `uv sync`
and tests. Do not add dependencies for convenience if a simple project-local
solution suffices.

---

## 11. Project-Specific Commands

Applicable once the scaffold and `pyproject.toml` exist.

### Install
```bash
uv sync
```

### Lint
```bash
uv run ruff check src/ tests/
```

### Test
```bash
uv run pytest tests/ -v
```

### Coverage
```bash
uv run pytest tests/ --cov=src --cov-fail-under=85
```

### Run peers — two independent OS processes
```bash
# Police peer (its own config, credentials, logs, runtime dir)
uv run python -m police_agent --config config/police.json

# Thief peer — separate terminal, separate private dir
uv run python -m thief_agent --config config/thief.json
```

### Interoperability vectors (external reference kit)
```bash
# Reference oracle — supplied kit, not production code
cd copthief-league-protocol && uv run python verify_vectors.py

# Fixture drift check — must produce no diff
cd copthief-league-protocol && uv run python gen_vectors.py && \
  git diff --exit-code -- vectors/
```

### Two-repository export
```bash
uv run python scripts/export_repos.py   # produces dist/police-agent, dist/thief-agent
```

### Security check for secrets
```bash
git grep -n -E "/home/|/Users/" -- README.md docs/ src/ tests/ config/ || true
git grep -n -E "API_KEY|TOKEN|PASSWORD|SECRET|oauth" -- . \
  ':!uv.lock' ':!.env-example' || true
```

---

## 12. Project-Specific Structure

Recommended workspace layout (single canonical shared core; role behavior via
interfaces and configuration):

```text
cop-thief-p2p/
├── src/
│   ├── cop_thief_core/
│   │   ├── __init__.py
│   │   ├── constants.py            # Immutable constants (versions, hashes)
│   │   ├── domain/                 # board, rules, actions, scoring, scent
│   │   ├── interop/                # canonical bytes, hashes, UIDs, signatures
│   │   ├── protocol/               # typed schemas, MCP-facing messages
│   │   ├── orchestration/          # state machine, deadlines, retries, watchdog
│   │   ├── audit/                  # logs, reveal, verification, replay
│   │   ├── reporting/              # result derivation, Gmail draft creation
│   │   ├── llm/                    # verbal hint providers only
│   │   └── shared/
│   │       ├── config.py           # Typed config loader singleton (CFG)
│   │       ├── gatekeeper.py       # API gatekeeper / rate limiter
│   │       └── version.py          # Version tracking (initial: 1.00)
│   ├── police_agent/               # police strategy + entry point
│   └── thief_agent/                # thief strategy + entry point
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── conformance/                # CORE-vector reproduction by production code
│   └── conftest.py
├── config/
│   ├── game.json                   # Shared signed constitution (versioned)
│   ├── police.json                 # Private police config
│   ├── thief.json                  # Private thief config
│   └── rate_limits.json            # Gatekeeper limits (versioned)
├── copthief-league-protocol/       # Supplied interop kit (external test material)
│   ├── SPEC.md
│   ├── verify_vectors.py
│   ├── gen_vectors.py
│   ├── vectors/
│   └── examples/
├── docs/
│   ├── PRD.md, PLAN.md, TODO.md
│   ├── requirements_matrix.md, decisions.md, architecture.md
│   ├── PRD_game_state.md, PRD_mcp_protocol.md, PRD_pregame_agreement.md
│   ├── PRD_player_agents.md, PRD_commit_reveal.md
│   ├── PRD_logging_audit_reporting.md, PRD_email_reporting.md
│   ├── PROMPTS.md, REVIEW_POLICY.md
├── instructions/                   # Read-only assignment + guidelines
├── scripts/export_repos.py
├── dist/                           # Generated: police-agent, thief-agent (untracked)
├── CLAUDE.md, COSTS.md, README.md
├── pyproject.toml, uv.lock
├── .env-example, .gitignore
```

Confirm exact required PRD names and contents against the official book
(Chapter 10) rather than guessing.

---

## 13. Project-Specific Constraints

### Architecture and local truth
- **No central game server, judge, or shared authoritative board state.** Each
  peer maintains only its own private position and private local truth.
- Separate public, private, inferred, and audit-only revealed state. Make it
  structurally hard for a strategy or live GUI to access forbidden opponent
  truth; full truth is permitted only in retrospective replay after reveal.
- One canonical shared core; role behavior via interfaces, dependency injection,
  and config. Never manually duplicate shared modules; never let one role import
  the other role's private package; never share a state file, singleton,
  database, or in-memory object between peers.
- The legal-action set is computed by deterministic code; strategy selects only
  from legal actions. The LLM must never decide legality and must never be the
  sole component keeping the game operational.

### Interoperability (byte-exact — from `copthief-league-protocol/SPEC.md`)
- Implement one production canonicalization function and reuse it:
  compact canonical JSON = `json.dumps(obj, sort_keys=True, ensure_ascii=False,
  separators=(",", ":"))` UTF-8 bytes.
- Commit–reveal and terms signature preimage:
  `SHA256(UTF8(canonical_json(payload) + "|" + nonce))` — nonce pipe-appended
  after the canonical JSON string, not inserted into the object.
- `game_uid` derivation and pheromone/scent math must match the pinned vectors
  exactly; group order must not affect the UID.
- **Report consensus signature is deliberately different:** serialize with
  `json.dumps(report, sort_keys=True, ensure_ascii=False)` (spaced separators)
  before inserting the signature key. Do not use the compact serializer here.
- The final emailed body must be the exact canonical bytes agreed/hashed — do not
  pretty-print or re-serialize during MIME construction.
- Retain the supplied kit under `copthief-league-protocol/`. Add production tests
  that load the CORE fixtures and exercise production functions (not the
  reference functions). **Never modify a vector to make code pass** — a mismatch
  means the implementation is wrong unless a documented source-version change
  proves otherwise. Fail CI on fixture drift.
- Optional ENH features are off by default and negotiation-gated (both peers
  advertise, select, sign, and pass ENH vectors). A CORE-only peer must still play.

### FastMCP, reliability, and deployment
- Each runtime is both a FastMCP server and client. Validate typed schemas;
  reject unknown, malformed, stale, duplicated, or out-of-order messages safely.
  Network handlers must not mutate domain state without validation — route every
  accepted message through the orchestrator/state machine.
- Provide idempotency keys, monotonic step/sub-game IDs, timeouts, bounded
  retries, watchdog/deadlines, gatekeeper rate limiting, safe-restart or
  fail-closed persistence, and structured error reasons.
- Support local and documented public-tunnel modes with a pre-match connectivity
  probe. Do not weaken FastMCP security checks to work around tunnel config
  (handle Host-header per SPEC Appendix D instead).

### LLM, email, and reporting
- LLM is for the verbal/psychological layer only. Provide a provider abstraction
  with a deterministic offline provider for tests and fallback. No unit or
  integration test may require a real cloud model. Validate word limits and
  sanitize output before it reaches the wire or a committed record.
- Gmail reporting defaults to draft/dry-run; tests must never send real mail.
- Result totals must be derived from logged events, never trusted from claims.

### Configuration and versioning
- All game/config parameters come from config files, validated against official
  minimums; never hard-code. Configuration validation must be deterministic.
- Version code and config starting at `1.00`; validate config-version
  compatibility at runtime. A different parameter set is a different variant
  requiring a different version and, where applicable, a different signed hash.

### Two-repository export
- Generate two self-contained release trees (`dist/police-agent`,
  `dist/thief-agent`), each independently installable/testable, each carrying its
  role entry point plus a vendored core snapshot maintained in one canonical
  source. Add a drift check recording the core source commit/hash in both. No
  credentials or generated private match secrets in either export.

---

## 14. Stop Conditions

Stop and ask the owner before continuing if:

- planned work exceeds the PR soft cap (300 LOC)
- requirements conflict (report per the authority hierarchy)
- tests fail for reasons unrelated to your changes
- a dependency must be added
- generated artifacts are required but tracking policy is unclear
- a destructive git operation seems necessary
- a full experiment/training run would be expensive
- secrets or private data appear in files
- the requested change would weaken project guidelines
- a change to an agreed wire construction / interop vector seems necessary
  (requires version bump, SPEC update, new vectors, regeneration proof,
  backward-compat decision, and cross-team coordination)
- MCP endpoint credentials, tunnel provider, or deployment details need deciding
- team identity, repository URLs, email addresses, or LLM mode are still missing

---

## 15. Final Response Template

```text
Summary:
- ...

Files changed:
- ...

Tests/checks:
- ...

PR size / reviewability:
- ...

Artifacts:
- ...

Prompt log:
- ...

Cost log:
- ...

Scope confirmation:
- ...

Git:
- Branch:
- Commit hash:
- Pushed to origin: yes/no
- PR creation: owner action required
- Forbidden git operations performed: no
```

---

## 16. Model / Reasoning Configuration Guidance

Prefer high-reasoning settings for complex coding, architecture, refactoring,
debugging, and multi-step agentic tasks:

- Recommended effort: `xhigh` for complex or long-horizon work.
- Acceptable effort: `high` for normal implementation and review.
- Lower effort only for small, low-risk, well-scoped edits.

Prefer `thinking: { "type": "adaptive" }` where supported; do not use deprecated
fixed `budget_tokens` thinking configurations unless required. Use higher effort
for planning, architecture, debugging, review, and risky changes; record
meaningful long-running or high-effort sessions in `COSTS.md`.

---

## 17. Long-Horizon State Management

For work spanning multiple sessions, PRs, or context windows, maintain
lightweight project state:

- `docs/PROGRESS.md` — current state, decisions, blockers, next steps.
- `docs/TEST_STATE.md` or `tests.json` — critical test scenarios and status.
- `scripts/check.sh` or equivalent — repeatable quality-gate wrapper.

Rules: do not create state files for tiny one-off tasks; do not let state files
replace `docs/TODO.md`, `docs/PROMPTS.md`, or `COSTS.md`; keep them short and
current; update state before ending a long session with unfinished work; never
remove or weaken tests to make state look green. Helper scripts must use `uv`,
must not hide failing commands, and must be documented when intended for regular
use.

---

## 18. Software Development Lifecycle & Mandatory Workflow

Binding per guideline §0–§1.6.

### 18.1 Core mindset
- Plan architecture and write requirements BEFORE writing code.
- **Critical first rule for AI-assisted work: REQUIRE FULL DOCUMENTATION BEFORE
  WRITING ANY LINE OF CODE.** Without clear, detailed requirements, agent output
  "works" but does not meet professional standards.
- Act as a Senior Software Architect orchestrating implementation, QA, and
  documentation to a high standard (clean, documented, tested, secure).

### 18.2 SDLC order
1. Requirements → `docs/PRD.md`.
2. Design & architecture → `docs/PLAN.md` + milestones in `docs/TODO.md`.
3. Development → code per plan using TDD.
4. Testing → unit, integration, system.
5. Deployment / release.
6. Maintenance & improvement.

### 18.3 Mandatory workflow (strict order)
1. **Phase -1 — Agent control setup:** ensure `CLAUDE.md`, `COSTS.md`,
   `docs/PROMPTS.md` exist; ensure `docs/REVIEW_POLICY.md` exists for this
   non-trivial project; define PR-size limits, artifact-tracking rules, expected
   phase→PR decomposition, initial LOC budget, and delegated git permissions.
   `.github/pull_request_template.md` is intentionally absent by owner request;
   the §2.9.1 structured commit body is its equivalent.
2. Create and get approval for `docs/PRD.md`.
3. Create `docs/PLAN.md`.
4. Create `docs/TODO.md`.
5. Create a dedicated `docs/PRD_*.md` for every central algorithm/mechanism.
6. Get all planning documents approved BEFORE development.
7. Split implementation into reviewable PR-sized slices.
8. Develop; update `TODO.md`, `PROMPTS.md`, `COSTS.md`,
   `docs/requirements_matrix.md`, and `docs/decisions.md` as work progresses.
9. Save results, create visualizations, update `README.md`.
10. Run final audit, final checklist, and version tag.

Reinforces §2.10: never start a later-stage task until every earlier-stage task
is 100% complete, reviewed, and merged.

---

## 19. Mandatory Documentation Deliverables

A project missing ANY mandatory file does not meet minimum requirements
(guideline §1.1–§1.4). Do not silently drop a required document.

### 19.1 `README.md` (root) — MANDATORY
Full user manual: installation instructions (system requirements, step-by-step
install, environment variables, troubleshooting); usage instructions (modes,
flags, workflows); examples & demos (samples, screenshots, scenarios);
configuration guide (files, parameters, effects); contribution guidelines
(standards, style); license & credits (third-party attributions); plus the
academic README content required by the official book.

### 19.2 `docs/` — MANDATORY
- **`docs/PRD.md`** — overview & context, user problem, market/audience,
  measurable goals/KPIs/acceptance criteria, functional & non-functional
  requirements, user stories & scenarios, assumptions/dependencies/constraints,
  out-of-scope items, timeline with milestones and deliverables.
- **`docs/PLAN.md`** — C4 diagrams (Context, Container, Component, Code), UML for
  complex processes, deployment diagrams, ADRs (decision + rationale +
  trade-offs/alternatives), API docs, interfaces, data schemas, contracts.
- **`docs/TODO.md`** — tasks with priority and status, phased breakdown with
  milestones, owner per task, Definition of Done per task. MUST decompose into
  PR-sized slices; each phase SHOULD list expected PRs, changed-LOC budget per
  PR, files likely to change, review risks, validation commands, and stop
  conditions.
- Assignment-required companions: `docs/requirements_matrix.md`,
  `docs/decisions.md`, `docs/architecture.md`.

### 19.3 Dedicated PRDs per algorithm/mechanism — MANDATORY
For every algorithm, central mechanism, or complex component, create a separate
`docs/PRD_<mechanism>.md` (at minimum: game state, MCP protocol, pre-game
agreement, player agents, commit–reveal, logging/audit/reporting, email
reporting). Each MUST include: theoretical background; specific requirements with
expected input/output and performance metrics; constraints and alternatives with
rationale; success criteria and specific test scenarios.

### 19.4 AI-agent control files — MANDATORY
`CLAUDE.md`, `COSTS.md`, `docs/PROMPTS.md` mandatory; `docs/REVIEW_POLICY.md`
recommended. Agents MAY fill project-specific commands, paths, constraints, and
stop conditions. Agents MUST NOT remove owner policy sections, relax PR-size
limits, grant themselves git permissions, remove prompt/cost logging, or broaden
scope without owner approval.

---

## 20. SDK Architecture & Object-Oriented Design

Binding per guideline §3.

### 20.1 SDK-based architecture — MANDATORY
- Every function containing business logic MUST be reachable through a single SDK
  layer (single entry point for all consumers: GUI, CLI, REST, third parties,
  future services).
- **No business logic in GUI/CLI layers** — they delegate to the SDK only.
- External consumers run all operations by importing the SDK, without touching
  internal modules.
- Layering: External Consumers → SDK → Domain Services → Infrastructure (DB, file
  I/O, external APIs). For this project, keep GUI, protocol, and networking
  outside the deterministic domain layer.

### 20.2 OOP — no code duplication
Never duplicate logic; apply DRY and Single Responsibility.

| Trigger | Action |
| --- | --- |
| Same function body in 2+ files | Extract to shared module |
| Same `try/except` pattern in 3+ files | Create wrapper function |
| Same method in 3+ classes | Create base class or `mixin` |
| Copied logic with minor variations | Use Template Method pattern |

**Mixin rules:** each mixin provides exactly one concern; mixins MUST NOT
override each other's methods; mixins MUST be independently testable.

---

## 21. API Gatekeeper & Rate Control

Binding per guideline §4. Applies to all external API calls (LLM APIs, Gmail
API, opponent FastMCP calls).

- **All external API calls MUST go through a centralized gatekeeper**
  (`cop_thief_core/shared/gatekeeper.py`). No call may bypass it.
- Enforce rate limits before every call; route overflow to a FIFO **queue** (never
  drop or crash); log every call for monitoring.
- Interface concepts: `execute(api_call, *args, **kwargs)` (check limits → queue
  if reached → retry transient failures → log) and `get_queue_status()`.
- Queue management: FIFO waiting queue, max depth from config, backpressure when
  full, drain as rate windows reset.
- Limits come from `config/rate_limits.json` (versioned `"version": "1.00"`),
  never hard-coded: `requests_per_minute`, `requests_per_hour`, `concurrent_max`,
  `retry_after_seconds`, `max_retries`.

---

## 22. Test-Driven Development & Quality Assurance

Binding per guideline §5. Extends §2.5.

- **TDD cycle: RED → GREEN → REFACTOR**, tests written before/with code.
- Every module has a corresponding test file mirroring `src/`; every public
  function/method has at least one test; tests cover happy AND error paths.
- Use shared fixtures from `tests/conftest.py`; **mock all external
  dependencies** (network, FastMCP, LLM, Gmail, tunnels). Domain, protocol,
  crypto, audit, and serialization logic must be real, not broadly mocked.
- **Test files also obey the 150-line rule.** Tests MUST NOT depend on external
  services or live internet/API access.
- **Coverage ≥ 85%** (statement, branch, and path for critical paths); the suite
  MUST FAIL below threshold.
- Document edge cases; use defensive programming with clear error messages,
  structured logging, graceful degradation. Document expected test output,
  generate pass/fail reports, save success/failure logs.
- Required test groups (assignment §9): unit; production conformance against
  every CORE fixture (Hebrew/emoji included); local integration in separate
  processes/dirs; adversarial protocol tests (bad signatures, tampered reveal,
  wrong nonce, non-ASCII mismatch, duplicate/stale/skipped step, invalid role,
  malformed scent, timeout/retry, conflicting claim, crash/restart, unsupported
  feature); and a cross-implementation acceptance test before declaring
  interop-ready.
- Time limits: unit ≤ 60 s total; integration ≤ 300 s.

---

## 23. Code Comments, Docstrings & Style

Binding per guideline §2.3.

- Comments explain **WHY**, not WHAT.
- Every function, class, and module MUST have a detailed `docstring`.
- Document complex design decisions, assumptions, and preconditions; keep them
  updated alongside code.
- Use descriptive, precise names; short single-responsibility functions; DRY;
  consistent style project-wide.

---

## 24. Linting & Ruff Configuration

Binding per guideline §6.1. **`uv run ruff check` MUST pass with zero errors**
before every commit.

- `pyproject.toml`: `line-length = 100`, `target-version = "py310"`.
- Enabled categories: `E` (PEP 8 errors), `F` (Pyflakes), `W` (PEP 8 warnings),
  `I` (isort), `N` (naming), `UP` (pyupgrade), `B` (bugbear), `C4`
  (comprehensions), `SIM` (simplification). `E501` may be ignored.

---

## 25. No Hard-Coded Values & Configuration Architecture

Binding per guideline §6.2–§6.3. Reinforces §5 and §13.

| Category | Wrong | Right |
| --- | --- | --- |
| API addresses | `"https://api.example.com"` | `cfg.get("api_url")` |
| Rate limits | `rate_limit = 10` | from `config/rate_limits.json` |
| Timeouts | `timeout = 60` | from config |
| Secrets | `api_key = "abc123"` | `os.environ.get("API_KEY")` |

- **Allowed in code:** physical/mathematical constants, documented default
  fallbacks, `Enum` values, and `constants.py` constants.
- When a typed config singleton exists (`CFG`), all source files MUST import and
  use it rather than reading config files directly or writing numeric literals
  duplicating config values — including in default arguments and module-level
  assignments. **Review check:** after any source change, `grep -rn` for config
  numeric literals inside `src/` and confirm none are game/config-parameter
  literals.
- Hierarchical, versioned config: `config/game.json` (shared signed
  constitution), `config/police.json`, `config/thief.json`,
  `config/rate_limits.json`, optional `config/logging_config.json`; `.env`
  (git-ignored) for secrets; `.env-example` (committed) with placeholders;
  `pyproject.toml`; `src/cop_thief_core/constants.py`.

---

## 26. Version Tracking

Binding per guideline §7.1. **Initial version `1.00`; increment on meaningful
changes.**

| Item | Location | Initial |
| --- | --- | --- |
| Code version | `src/cop_thief_core/shared/version.py` | `1.00` |
| Config version | `"version"` in `config/game.json` | `1.00` |
| Rate-limits version | `"rate_limits.version"` | `1.00` |
| Protocol / interop-kit version | explicit fields in shared terms | per SPEC |

The application MUST validate config-version and protocol-version compatibility
at runtime and refuse to start on incompatibility.

---

## 27. Package Organization

Binding per guideline §13.

- `pyproject.toml` is the single dependency source of truth (name, version,
  description, author, license, pinned deps); no `requirements.txt`.
- `__init__.py` in the package root and every subdirectory; SHOULD define
  `__all__` and `__version__`.
- **All imports MUST use relative paths or package names — never absolute
  paths.** File read/write MUST also be relative to the package path.
- Checklist: definition file with pinned deps; `__init__.py` exports and
  `__version__`; source under `src/`, tests under `tests/`, docs under `docs/`;
  all imports relative.

---

## 28. Performance & Parallel Processing

Binding per guideline §14 (apply when relevant).

- **Multiprocessing** for CPU-bound work; **multithreading** for I/O-bound work
  (network, FastMCP calls, file/DB I/O). Peers already run as separate OS
  processes with no shared mutable state.
- Thread safety: protect shared state with locks, use `queue.Queue` for
  inter-thread transfer, use context managers, avoid deadlocks and race
  conditions.
- Manage resources: correct close/cleanup, exception handling, prevent leaks;
  size process/thread counts dynamically.

---

## 29. Building-Block Design

Binding per guideline §15.

- Define each block by Input (types, valid domain, dependencies, validation),
  Output (types, format, edge-case behavior), Setup (parameters with defaults,
  configuration, initialization).
- Principles: Single Responsibility, Separation of Concerns, Reusability (no
  dependency on specific external code), Testability via dependency injection.
- Validate configuration and inputs explicitly; raise clear, typed errors.

---

## 30. Research, Results & Visualization

Binding per guideline §8 (apply when the project produces experimental results,
e.g., strategy/parameter analysis).

- **Parameter sensitivity analysis:** systematic controlled variation, documented
  per-parameter effect, OAT / variance-based methods.
- **Analysis notebook:** methodical comparison of strategies/configs, theoretical
  analysis, academic citations, LaTeX for equations.
- **Visualization:** heatmaps, scatter/line/bar charts, box plots, waterfall
  charts as appropriate; clear labels, accessible colors, detailed captions,
  legends, high resolution.
- Executed notebooks and heavy result artifacts are generated outputs — track
  intentionally or document as reproducible (see §9 / §2.7).

---

## 31. UI / UX

Binding per guideline §9 (apply to the required live GUI and replay viewer).

- Usability criteria: Learnability, Efficiency, Memorability, Error Prevention,
  Satisfaction.
- Respect Nielsen's 10 heuristics (status visibility, match to real world, user
  control & freedom, consistency, error prevention, recognition over recall,
  flexibility & efficiency, minimalist design, error recovery, help &
  documentation).
- The live GUI MUST show only local knowledge; full truth only in retrospective
  replay after audit material is available. Keep GUI code outside the domain and
  protocol layers.
- Document interfaces: screenshot per screen/state, typical workflow,
  interaction/feedback explanations, accessibility considerations.

---

## 32. Extensibility & Maintainability

Binding per guideline §11.

- Provide extension points: clear interfaces, lifecycle hooks, middleware,
  API-first design — add functionality without changing core code. Optional ENH
  protocol features are the concrete example: negotiation-gated, off by default.
- Keep code modular, responsibility-separated, reusable, analyzable, testable.

---

## 33. ISO/IEC 25010 Quality Characteristics

Aim to satisfy (guideline §12): Functional Suitability, Performance Efficiency,
Compatibility (cross-team interoperability), Usability, Reliability (fault
tolerance, recoverability, safe restart), Security (auth, integrity,
accountability), Maintainability, Portability.

---

## 34. Final Submission Checklist

Verify before submission (guideline §16 + assignment §13 Definition of Done).
Justify any omission.

**Documentation & structure**
- [ ] Comprehensive `README.md` at user-manual + academic level.
- [ ] `docs/` with `PRD.md`, `PLAN.md`, `TODO.md`, `requirements_matrix.md`,
      `decisions.md`, `architecture.md`.
- [ ] Dedicated `PRD_*` for every algorithm/central mechanism.
- [ ] Architecture diagrams (C4, UML, deployment).
- [ ] `docs/PROMPTS.md` complete for all significant AI sessions.
- [ ] `CLAUDE.md` reviewed before implementation; `COSTS.md` populated.
- [ ] `docs/REVIEW_POLICY.md` or §2.9.1 commit body serves as the review gate.
- [ ] PRs within reviewable size limits or exceptions justified.
- [ ] Generated artifacts tracked intentionally or documented as reproducible.
- [ ] AI git permissions defined; AI commits limited to PR branches; no direct
      commits to `main`; human owner reviewed and merged PRs.

**Architecture & code**
- [ ] SDK architecture — all business logic via SDK; no logic in GUI/CLI.
- [ ] OOP — no duplication; inheritance/mixins used.
- [ ] API gatekeeper — all external calls through it; queue on overflow.
- [ ] Rate limits and all parameters from config; official minimums respected.
- [ ] Files ≤ 150 code lines; docstrings and WHY-comments present.
- [ ] Consistent style; descriptive names; no PR mixes unrelated concerns.

**Quality & testing**
- [ ] TDD (RED-GREEN-REFACTOR); coverage ≥ 85%; zero ruff violations.
- [ ] Every CORE vector reproduced by production code; no fixture drift.
- [ ] Adversarial + cross-implementation acceptance tests pass.
- [ ] Edge-case docs and error handling; automated test reports.

**Configuration & security**
- [ ] Config separated from code and versioned; `.env-example` present.
- [ ] No secrets in code or git history; `.gitignore` current.
- [ ] `uv` only; `uv.lock` and `pyproject.toml` present.

**Interop, reliability & submission**
- [ ] Police and Thief run in separate processes/private dirs; no shared truth.
- [ ] Local end-to-end games finish and audit cleanly; result totals derived.
- [ ] Public FastMCP endpoint works via documented tunnel; ≥1 cross-implementation
      game settles byte-identically.
- [ ] Emailed/draft report bytes are exactly the agreed bytes; Gmail defaults to
      draft/dry-run.
- [ ] Optional ENH off by default and negotiation-gated.
- [ ] Live GUI respects local truth; replay verifies integrity.
- [ ] Both exported repositories self-contained, testable, traceable to one
      canonical core; required README, PRDs, artifacts, and submission tag present.

**Research, standards, extensibility**
- [ ] Sensitivity analysis / analysis notebook with quality graphs (if applicable).
- [ ] Documented extension points; professional package layout; ISO/IEC 25010
      alignment; AI/runtime/review-cost analysis in `COSTS.md`.

---

## 35. Quick Reference — Quality Requirements

| Rule | Threshold | Enforcement |
| --- | --- | --- |
| SDK architecture | All business logic through SDK | Code review |
| OOP / no duplication | No logic duplicated in 2+ copies | Review + tests |
| API gatekeeper | All external calls through it | Code review |
| Configuration source | From config files, not source | Code review + grep |
| Queue management | Queue, not crash, on overflow | Integration test |
| TDD workflow | RED-GREEN-REFACTOR | Code review |
| Version control | Initial `1.00` | Module + test |
| File size | ≤ 150 code lines | Automated check |
| Linter violations | `0` | `ruff check` |
| Test coverage | `≥ 85%` | `pytest --cov` |
| Hard-coded values | `0` | Code review + grep |
| Secrets in code | `0` | Scan + `.env-example` |
| Package manager | Only `uv` | Automated check |
| CORE vectors | Reproduced by production code, no drift | Conformance tests + CI |
| Local truth boundary | No peer accesses other's private truth | Review + integration |
| PR size target | 50–200 changed LOC | §2.9.1 body + review |
| PR soft cap | 300 changed LOC | Stop and decompose |
| PR hard cap | 500 changed LOC | Owner approval required |
| `CLAUDE.md` / `COSTS.md` | Required for AI-assisted projects | Setup/PR review |
| Prompt log | All significant AI sessions | `docs/PROMPTS.md` |
| Generated artifacts | Tracked intentionally or reproducible | README + gitignore |

---

## 36. Ground-Truth Reference Facts (book/code v3.0.0)

These facts are **confirmed** from the lecturer's reference implementation
(`../Game-P2P-Cop-Chase`, code v3.0.0) and the league kit
(`copthief-league-protocol/SPEC.md` + `vectors/`), read in full on 2026-07-21.
They are the authoritative spec for this project and supersede any earlier
placeholder values elsewhere in this file (e.g. "version starting at 1.00" →
actual versions below). The Hebrew book PDF is the ultimate authority, but its
text layer is not machine-readable; where the reference code and the book's
binding parameter table (Appendix F) are quoted here, they agree.

### 36.1 Repository topology and identity
- **Team:** `group_name`/`group_id` = **`vm__fabi`** (self-play peers may use
  `vm__fabi-police` / `vm__fabi-thief` to form a valid two-group match).
- **Workspace (this repo, canonical core + PR development):**
  `github.com/mironovich-v/cop-rob-p2p`.
- **Police submission (generated export):** `github.com/mironovich-v/cop-rob-p2p-police`.
- **Thief submission (generated export):** `github.com/mironovich-v/cop-rob-p2p-thief`.
- One canonical core; the two submission repos are generated, vendor a core
  snapshot, cross-link each other, and must be self-contained (no runtime
  dependency on the other repo or a private third repo).

### 36.2 Binding parameters (Appendix F — single source of numeric truth)
Board `grid_size` **7×7** (minimum, raise-only); `num_agents` 2 (fixed);
`move_set` `["N","S","E","W","STAY"]` orthogonal, Manhattan distance (fixed; king
mode opt-in); `max_barriers` 14 (min, police-only, adjacent cell); `max_moves`
35 (min); `survival_threshold` 35 (min); scent center `0.9` / decay `0.10` /
field `5×5` / min-center `0.5` (fixed); scoring capture cop/thief `20`/`5`,
survival cop/thief `5`/`10`, tie `2`, technical-loss `0` (fixed); league
`num_games` 6-series (config default 1 = demo), `diversity_reward` 10,
`min_games_to_pass` 2, `max_games_per_team` 10 (fixed); `token_budget_per_series`
~200000 (negotiable); gatekeeper rpm/concurrent/backoff/retries/queue
`30`/`2`/`5s`/`3`/`100` (minimums); response/watchdog `30s`/`60s`; hint cap 15
words. **Never hard-code these — load from config; never lower a minimum.**

### 36.3 Interop constructions (byte-exact — 4 serializations)
1. **Compact canonical JSON** (every ordinary hash):
   `json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",",":"))`.
2. **Commit / terms signature:** `SHA256(canonical(payload) + "|" + nonce)` —
   nonce (`secrets.token_hex(16)`) pipe-appended to the canonical string.
3. **`game_uid`:** `UUID(SHA256(canonical(terms) + "|" + "|".join(sorted([g_a,g_b])))[:16])`;
   `game_id = "{sorted_a}-vs-{sorted_b}"`. 14 signed-terms keys: board_size,
   smell_grid_size, decay_per_step, emit_intensity, min_center_intensity,
   max_steps, barriers_max, setting, hint_max_words, axis_origin_corner,
   axis_start_index, thief_start, cop_start, num_games.
4. **Report consensus signature (DIFFERENT — spaced):**
   `json.dumps(report, sort_keys=True, ensure_ascii=False)` (default separators),
   sign-then-insert under key `חתימת_קונסנזוס_משותפת`. Verify = pop key,
   re-serialize spaced, re-hash. **The emailed body MUST be these exact hashed
   bytes** (stricter than the reference's `indent=2`; SPEC §6).

### 36.4 Architecture, protocol, artifacts
- **MCP surface (FastMCP HTTP):** exactly 4 tools — `negotiate`, `receive_turn`,
  `submit_audit`, `receive_control` (each returns `{"ok": true}`). Ports thief
  8801 / police 8802 on 127.0.0.1.
- **Orchestrator FSM states:** WAITING, THINKING, PLAYING, PAUSED, STOPPED,
  GAME_OVER, QUIT. Thief moves first; capture = coordinate overlap answered
  honestly on own state; end-of-game mutual audit; failed audit →
  `tamper_forfeit`. No central referee.
- **Capture/win:** thief wins on `step ≥ max_steps` (survival); police wins on
  capture claim matching thief's true cell. Result totals **derived** from logged
  events, never declared.
- **Four artifacts** (share one `game_uid`): `declaration_<game_id>.json` (once),
  `config_<game_id>_g<NN>.json` (per sub-game, with `config_sha256`),
  `log_<game_id>_g<NN>.json` (per sub-game, sealed commit-reveal records),
  `result_<game_id>.json` (once, aggregate + `mutual_agreement.sha256`).
- **Config layout:** per-role `config/police/` & `config/thief/`, each with signed
  shared `game.json` (schema 1.3) + private `game.toml` + `rate_limits.json`.
- **Versions:** code `3.0.0`, book `3.0.0`, config `1.10`, `game.json` schema
  `1.3`. Target Python **3.13** to match reference idioms.
- **Strategy seam:** override `BrainBase._pick_move` / `_decide_move` via
  `[strategy] thief_class` / `police_class` = `"package.module:Class"`. The MOVE
  is always pure Python; LLM only writes the (optional, default-template) hint.

### 36.5 Resolved book contradictions (record in `docs/decisions.md`)
1. Commit preimage → reference form `SHA256(canonical|nonce)`.
2. Pheromone → `subtractive_chebyshev_v1` (CORE); book's multiplicative model
   only if a partner locks it.
3. Report signature uses the spaced serializer (see §36.3.4).
4. `num_games` 1 (demo) vs league series 6 → signed config governs a match.
5. Email bytes → email the exact hashed canonical bytes, not `indent=2`.

### 36.6 What this project ADDS beyond the reference
Two-repo export (`scripts/export_repos.py` + drift check); league CORE-vector
conformance tests exercising **our** production functions (never the reference
oracle); a portable Gmail OAuth send-only flow (the reference used a
Windows-path skill); public-tunnel + Host-header handling (SPEC App. D) with a
pre-match connectivity probe; the full doc set and PR workflow in this file;
our own strategy brains.

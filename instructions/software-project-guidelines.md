# Software Project Guidelines

> **Purpose of this document:** This is a complete, normative ruleset for writing professional software projects to the highest level of excellence (Hebrew original, v3.00, 2026-03-26). When asked to design, plan, or write any project under these guidelines, you (the LLM) MUST treat every rule below as binding unless the user explicitly overrides it. Do not invent rules not stated here. Do not silently drop requirements.
>
> **Project-level control files:** This guideline is the global normative standard. Individual projects MAY add stricter project-specific rules in `CLAUDE.md`, `docs/REVIEW_POLICY.md`, or `.github/pull_request_template.md`, but those files MUST NOT weaken, override, or silently remove any requirement in this document unless the project owner explicitly approves the exception.
>
> **cop-rob project exception (owner-approved):** `.github/pull_request_template.md` is intentionally absent. The project owner explicitly requested removal of the `.github/` directory. The structured commit message body defined in `CLAUDE.md §2.9.1` serves as the equivalent reviewability checklist embedded directly in every commit.
> 
> **Keywords:** `MUST`, `MUST NOT`, `SHOULD`, `MAY` follow RFC 2119 meaning.
>
> **Language note:** The original document is in Hebrew. Technical terms, file names, command syntax, code identifiers, and configuration keys are preserved verbatim in English/code as in the source.

---

## 0. Mental Model: What "Professional Programmer" Means Here

A professional programmer is **not** merely someone who writes code. They:
- Understand the full software lifecycle: design, document, test, maintain.
- Plan architecture and write requirements **before** writing the first line of code.
- Hold high standards for code quality (clean, documented, tested, secure).
- Work in teams with defined roles (Software Architect, Developers, QA Engineer, Product Manager, DevOps).
- Use methodologies (Scrum, Kanban, SAFe), code reviews via Pull Requests, retrospectives, daily standups, sprint reviews.
- Continuously update knowledge.

### 0.1 SDLC (Software Development Life Cycle)
Every project goes through, in order:
1. **Requirements definition** — write detailed `PRD`.
2. **Design & architecture** — write `PLAN` + define milestones (`TODO`).
3. **Development** — write code per the plan, using **TDD**.
4. **Testing** — unit, integration, system.
5. **Deployment** — release to production.
6. **Maintenance & improvement** — bug fixes, new features, upgrades.

### 0.2 The AI / Vibe-Coding Revolution
- In Vibe Coding, the programmer **directs AI agents** to create, review, and improve code, acting as a Senior Software Architect orchestrating multiple AI agents in parallel.
- A programmer using AI agents with vibe coding can produce **~16× more quality code lines** in a given timeframe than manual writing without AI.
- **Critical first rule when working professionally with AI:** REQUIRE FULL DOCUMENTATION BEFORE WRITING ANY LINE OF CODE. Without clear, detailed requirements, AI agents will produce code that "works" but does not meet professional standards.

### 0.3 AI-Agent Project Control Layer
Every AI-assisted project MUST include a project-specific control layer before planning or implementation begins.

Required files:
- `CLAUDE.md` — operational instructions for Claude Code / AI coding agents.
- `COSTS.md` — AI usage, runtime, experiment, and review-cost ledger.
- `.github/pull_request_template.md` — reviewability, PR-size, and validation gates. (For cop-rob: absent by owner request; `CLAUDE.md §2.9.1` structured commit body is the equivalent.)
- `docs/PROMPTS.md` — prompt engineering log, as defined in §7.3.

Recommended when the project is non-trivial:
- `docs/REVIEW_POLICY.md` — expanded reviewability policy, decomposition rules, and artifact-handling rules.

The project owner SHOULD maintain a reusable personal `CLAUDE.template.md`.

For each new project, the template SHOULD be copied into the repository and adapted only in project-specific sections.

AI agents MAY adapt project-specific sections of `CLAUDE.md`, but MUST NOT weaken or remove policy sections without explicit owner approval.
---

## 1. Mandatory Project Structure & Documentation

A project that lacks ANY of the following files MUST NOT be considered as meeting minimum requirements.

### 1.1 `README.md` (project root) — MANDATORY
A full user manual containing:
- **Installation Instructions** — system requirements, step-by-step install, environment variables, common-issue troubleshooting.
- **Usage Instructions** — running modes, flags/options, typical CLI/GUI workflows.
- **Examples & Demos** — code samples, screenshots, common scenarios.
- **Configuration Guide** — config files, parameters, their effects.
- **Contribution Guidelines** — code standards, style.
- **License & Credits** — usage license, third-party library attributions.

### 1.2 `/docs` directory — MANDATORY

Must contain at minimum:

#### `docs/PRD.md` — Product Requirements Document
- Project overview & context, user-problem description, market analysis, target audience.
- Measurable goals, KPIs, acceptance criteria.
- Functional & non-functional requirements, user stories, usage scenarios.
- Assumptions, dependencies, constraints, out-of-scope items.
- Timeline with milestones and expected deliverables.

#### `docs/PLAN.md` — Architecture & Design Document
- **C4 Model** diagrams: Context, Container, Component, Code.
- **UML** diagrams for complex processes; deployment diagrams.
- **ADRs** (Architectural Decision Records) with rationale and trade-offs / alternatives.
- API documentation, interfaces, data schemas, contracts.

#### `docs/TODO.md` — Tasks Document
- Detailed task list with priorities and status (not started / in progress / done).
- Phased breakdown with milestones.
- Owner assigned per task.
- Definition of Done per task.

`docs/TODO.md` MUST decompose work into PR-sized slices, not only large phases.

Each implementation phase SHOULD include:
- Expected PRs.
- Expected changed-LOC budget per PR.
- Files likely to change.
- Review risks.
- Validation commands.
- Explicit stop conditions.

**Strict Linear Progression:** Work MUST progress linearly through the defined stages. AI agents and developers MUST NOT begin tasks in a subsequent stage until every task in all preceding stages is 100% complete, reviewed, and merged.

### 1.3 Dedicated PRDs per Algorithm/Mechanism — MANDATORY
For every specific algorithm, central mechanism, or complex technical component, you MUST create a separate dedicated PRD. Examples:
- `docs/PRD_ml_algorithm.md`
- `docs/PRD_authentication.md`
- `docs/PRD_search_engine.md`
- `docs/PRD_caching.md`

Each dedicated PRD MUST include:
- Detailed description with theoretical background.
- Specific requirements, expected input/output, performance metrics.
- Constraints, alternatives considered, rationale for the chosen approach.
- Success criteria and specific test scenarios.

### 1.4 AI-Agent Control Files — MANDATORY for AI-Assisted Projects
For any project created, modified, reviewed, or maintained with AI coding agents, the following files are MANDATORY.

#### `CLAUDE.md` — Agent Operating Instructions

`CLAUDE.md` MUST define how Claude Code or any AI coding agent behaves in this repository.

It MUST include:
- Project role and expectations.
- Non-negotiable rules.
- Allowed and forbidden tools.
- Git permissions.
- PR size policy.
- Required pre-edit checklist.
- Required final response format.
- Project-specific commands.
- Project-specific directory structure.
- Scope boundaries.
- Artifact tracking rules.
- Prompt and cost logging requirements.

`CLAUDE.md` MUST be concise, specific, and operational. It is not a replacement for this guideline; it is the project-level execution layer.

The project owner SHOULD create and maintain the base `CLAUDE.md` template.

AI agents MAY:
- Fill project-specific commands.
- Fill project-specific paths.
- Add project-specific constraints.
- Add project-specific stop conditions.

AI agents MUST NOT:
- Remove owner policy sections.
- Relax PR size limits.
- Grant themselves git permissions.
- Remove prompt/cost logging requirements.
- Broaden scope without owner approval.

#### `COSTS.md` — AI and Runtime Cost Ledger

`COSTS.md` MUST track the cost of AI-assisted development and expensive project operations.

It SHOULD include:
- Date.
- Phase / task.
- Agent or model used.
- Approximate token usage or plan/session usage when available.
- Wall-clock time.
- Human review time.
- Commands or experiments with meaningful runtime cost.
- Generated artifacts.
- Whether the work was accepted, revised, or discarded.
- Notes about waste, rework, or lessons learned.

Exact token accounting SHOULD be used when available. If exact tokens are unavailable, the project MUST record practical estimates such as wall-clock time, session count, experiment runtime, or plan usage.

### 1.5 Recommended Project Layout

```text
project-root/
├── src/                              # Source code
│   ├── <package>/
│   │   ├── __init__.py
│   │   ├── sdk/                      # SDK layer
│   │   │   └── sdk.py
│   │   ├── services/                 # Business logic
│   │   ├── shared/                   # Shared utilities
│   │   │   ├── gatekeeper.py         # API gatekeeper
│   │   │   ├── config.py             # Configuration manager
│   │   │   └── version.py            # Version tracking
│   │   └── constants.py
│   └── main.py
├── tests/                            # Unit and integration tests
│   ├── unit/
│   └── integration/
├── docs/                             # Documentation (MANDATORY)
│   ├── PRD.md
│   ├── PLAN.md
│   ├── TODO.md
│   ├── PRD_<mechanism>.md            # Per-algorithm PRDs
│   └── REVIEW_POLICY.md              # Optional expanded review policy for non-trivial projects
├── config/                           # Configuration files
│   ├── setup.json
│   └── rate_limits.json
├── data/                             # Input data
├── results/                          # Experiment results
├── assets/                           # Images, graphs, resources
├── notebooks/                        # Analysis notebooks
├── CLAUDE.md                         # Claude behavior control (§2.9.1 commit body replaces pull_request_template)
├── COSTS.md                          # AI usage, runtime, experiment, and review-cost ledger
├── README.md                         # MANDATORY
├── pyproject.toml                    # Build & dependencies
├── uv.lock                           # Locked dependencies
├── .env-example                      # Secret placeholders
└── .gitignore
```

### 1.6 Mandatory Workflow (strict order)

1. **Phase -1: Agent control setup**
   - Create or copy owner-approved `CLAUDE.md`.
   - Create `COSTS.md`.
   - Create `.github/pull_request_template.md` (or embed the checklist in `CLAUDE.md §2.9.1` structured commit body if the owner prefers no `.github/` directory).
   - Create `docs/REVIEW_POLICY.md` when the project is non-trivial or expected to have multiple PRs.
   - Define PR size limits and artifact-tracking rules.
   - Define expected phase-to-PR decomposition and initial LOC budget.
   - Approve these files before project planning begins.
   - Define delegated git permissions: which branch/commit/push operations the AI agent may perform and which operations remain owner-only.

2. Create and approve `docs/PRD.md` BEFORE proceeding.
3. Create `docs/PLAN.md` architectural design.
4. Create `docs/TODO.md` task list.
5. Create dedicated `PRD_*` for every central algorithm/mechanism.
6. Approve all planning documents BEFORE starting development.
7. Split implementation into reviewable PR-sized slices.
8. Begin development; update `TODO.md`, `PROMPTS.md`, and `COSTS.md` as work progresses.
9. Save results, create visualizations, update `README.md`.
10. Run final audit, final checklist, and version tag.

---

## 2. Project Structure & Code Documentation

### 2.1 Modular Project Structure
- Split logically by role: source code, tests, docs, data, results, config, assets.
- Either **feature-based** or **layered architecture**, with clear separation between code / data / results / docs.

### 2.2 File Size Rule — Maximum 150 Lines
- **Every code file MUST NOT exceed 150 lines of code** (blank lines and comment-only lines are NOT counted).
- If a file exceeds the limit, **split it into multiple files**. NEVER compress code to fit the limit.
- **Splitting strategies:**
  - Extract helper functions to separate file.
  - Extract a `mixin` when a class has multiple responsibilities.
  - 50/50 split when there are clearly two halves (e.g., read / write).
  - Extract constants to `constants.py`.
  - Extract model definitions to a separate file.

### 2.3 Code Comments & Quality
- Comments MUST explain **WHY**, not WHAT (per Code Comments Standards).
- Every function, class, and module MUST include detailed `docstring`s.
- Comments MUST explain complex design decisions, document assumptions and preconditions, and be updated alongside code changes.
- Use descriptive, precise variable & function names.
- Write short, focused functions adhering to **Single Responsibility Principle**.
- Apply **DRY** (Don't Repeat Yourself).
- Maintain consistent style across the entire project.

---

## 3. SDK Architecture & Object-Oriented Design

### 3.1 SDK-Based Architecture — MANDATORY
Every function containing business logic MUST be reachable through the SDK layer. The SDK is the **single entry point** for all consumers: menus, GUI, CLI, third-party integrations, future services.

```text
External Consumers (GUI / CLI / REST / Third Party)
        |
        v
   +---------+
   |   SDK   |   <-- Single entry point for ALL logic
   +----+----+
        |
        v
   +-------------+
   |   Domain    |   <-- Services, models, orchestrators
   |  Services   |
   +----+--------+
        |
        v
   +-----------------+
   | Infrastructure  |   <-- DB, file I/O, external APIs
   +-----------------+
```

**Architectural requirements:**
- Every business function exposed via the SDK class.
- **No business logic in `GUI` / `CLI` layers** — these layers ONLY delegate to the SDK.
- External consumers MUST be able to import the SDK and run all operations without accessing internal modules.

### 3.2 Object-Oriented Design (OOP) — No Code Duplication

When the same logic appears in two or more files, extract it into a shared module, base class, or `mixin`. NEVER duplicate code.

| Trigger | Action |
| --- | --- |
| Same function body in 2+ files | Extract to shared module |
| Same `try/except` pattern in 3+ files | Create wrapper function |
| Same method in 3+ classes | Create base class or `mixin` |
| Copied logic with minor variations | Use Template Method pattern |

**Mixin rules:**
- Each `mixin` provides exactly ONE concern.
- `mixin`s MUST NOT override each other's methods.
- `mixin`s MUST be independently testable.

---

## 4. API Gatekeeper & Rate Control

### 4.1 Centralized API Gatekeeper — MANDATORY
**All external API calls MUST go through a centralized gatekeeper.** The gatekeeper handles rate limiting, queues, retries, and monitoring.

**Requirements:**
- No API call may bypass the gatekeeper.
- Rate limits enforced before every call.
- Overflow goes to a queue (NOT rejected).
- Every API call is logged for monitoring.

**Required interface:**

```python
class ApiGatekeeper:
    """Centralized API call manager."""

    def __init__(self, config: RateLimitConfig):
        """Initialize with rate limit config."""
        ...

    def execute(self, api_call, *args, **kwargs):
        """Execute API call through gatekeeper.
        - Check rate limits before execution
        - Queue if limit reached
        - Retry on transient failures
        - Log all calls
        """
        ...

    def get_queue_status(self) -> QueueStatus:
        """Return queue depth and stats."""
        ...
```

### 4.2 Rate-Limit Configuration — From File, Never Hard-Coded

```json
{
  "rate_limits": {
    "version": "1.00",
    "services": {
      "default": {
        "requests_per_minute": 30,
        "requests_per_hour": 500,
        "concurrent_max": 5,
        "retry_after_seconds": 30,
        "max_retries": 3
      }
    }
  }
}
```

### 4.3 Queue Management on Overflow
When a rate limit is reached, the gatekeeper MUST route requests to a queue rather than dropping or crashing:
- **FIFO queue** for waiting requests.
- **Maximum queue depth** defined in configuration.
- **Backpressure signal** when queue is full.
- **Drain mechanism** that processes queued requests as rate windows reset.

---

## 5. Test-Driven Development (TDD) & Quality Assurance

### 5.1 TDD Cycle — RED → GREEN → REFACTOR
All development MUST follow TDD.

- Every module MUST have a corresponding test file.
- Every public function/method MUST have at least one test.
- Tests cover BOTH the happy path AND error cases.
- Tests are written **before or alongside implementation**, never as an afterthought.

**Test structure:**
```text
tests/
  unit/
    test_<module>/        # Mirror src/ structure
      test_<file>.py
  integration/
    test_<feature>.py
  conftest.py             # Shared fixtures
```

**Test rules:**
1. Every new module MUST have a corresponding test file.
2. Every public function MUST have at least one test.
3. Tests MUST cover normal path AND error cases.
4. Use `fixtures` from `conftest.py` for shared test data.
5. **Mock all external dependencies** (databases, files, APIs).
6. **Test files also obey the 150-line rule.**
7. Tests MUST NOT depend on external services.

### 5.2 Coverage — Minimum 85%
Global test coverage MUST be ≥ 85%. The test suite MUST FAIL if coverage drops below this threshold.

```toml
# pyproject.toml
[tool.coverage.run]
source = ["src"]
omit = ["src/main.py", "*/tests/*", "src/**/gui/*"]

[tool.coverage.report]
fail_under = 85
```

Required coverage types: **Statement coverage**, **Branch coverage**, and **Path coverage** for critical paths.

### 5.3 Edge Cases & Failure Handling
- Identify and document edge cases — boundary conditions, full descriptions, screenshots when relevant.
- Defensive programming with clear error messages, structured logging, graceful degradation.

### 5.4 Expected Test Results
- Document expected run output for every test.
- Generate automated testing reports with `pass/fail rates`.
- Save logs of successful AND failed runs.

---

## 6. Linting, Configuration, Security

### 6.1 Linter Compliance — Zero Violations (Ruff)
**`ruff check` MUST pass with zero errors.** All code MUST pass lint before commit.

```toml
# pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E","F","W","I","N","UP","B","C4","SIM"]
ignore = ["E501"]
```

**Active rule categories:**
- `E` — PEP 8 errors (indentation, spaces, style).
- `F` — Pyflakes (unused imports, undefined names).
- `W` — PEP 8 warnings.
- `I` — `isort` (import order).
- `N` — `pep8-naming` (naming conventions).
- `UP` — `pyupgrade` (modernize to Python 3.10+).
- `B` — `flake8-bugbear` (common bugs).
- `C4` — use of comprehensions.
- `SIM` — expression simplification.

### 6.2 No Hard-Coded Values
All configurable values MUST come from configuration files, NOT source code.

| Category | Wrong | Right |
| --- | --- | --- |
| API addresses | `"https://api.example.com"` | `cfg.get("api_url")` |
| Rate limits | `rate_limit = 10` | `cfg.get("rate_limit", 10)` |
| Timeouts | `timeout = 60` | `cfg.get("timeout", 60)` |
| Secrets | `api_key = "abc123"` | `os.environ.get("API_KEY")` |

**Allowed in code:** physical/mathematical constants, default-fallback values, parameters, `Enum` values, and `constants.py` constants.

**When the project defines a typed config loader singleton** (e.g., `CFG = load_config()` in `shared/config.py`), all source files MUST import and use the singleton rather than reading config files directly or writing numeric literals matching config values. Writing a raw numeric literal that duplicates a value in the config file is a violation, even inside default argument values or module-level assignments.

### 6.3 Configuration Architecture
Hierarchical, with versioned config files:

```text
config/
  setup.json                       # Main app config (versioned)
  rate_limits.json                 # API rate limits (versioned)
  logging_config.json              # Logging configuration
.env                               # Secrets (git-ignored)
.env-example                       # Secret placeholders (committed)
pyproject.toml                     # Build, lint, test settings
src/<package>/constants.py         # Immutable project constants
```

### 6.4 Information Security & Secret Management
- **NO secrets in source.** No API keys, passwords, or tokens in code.
- Use ONLY environment variables: `os.environ.get("API_KEY")`.
- `.env-example` MUST exist with placeholder values.
- When pushing to GitHub demos, MUST create `.env-example` with placeholder values.
- Use a secret-management tool in production environments.
- Rotate keys periodically; monitor usage; apply principle of **least privilege**.

`.gitignore` MUST include, as applicable:
- `.env`
- `*.pem`
- `*.key`
- `credentials.json`
- `__pycache__/`
- `.pytest_cache/`
- `.coverage`
- `.ipynb_checkpoints/`
- generated notebooks such as `notebooks/*.executed.ipynb`
- model checkpoints such as `*.pth`
- large generated results unless intentionally tracked

---

## 7. Version Control & `uv` Package Manager

### 7.1 Global Version Control
Both code and configuration files MUST include explicit version tracking. **Initial version: `1.00`.** Increment on meaningful changes.

| Item | Location | Initial value |
| --- | --- | --- |
| Code version | `src/<pkg>/shared/version.py` | `1.00` |
| Config version | `"version"` key in JSON | `1.00` |
| Rate limits version | `"rate_limits.version"` | `1.00` |

The application MUST validate config-version compatibility at runtime.

### 7.2 Recommended Git Practices
- Clean `commit` history with meaningful messages.
- Significant `tagging` for major versions.
- Separate `branches` per feature.
- Code reviews via `Pull Requests`.

### 7.2.1 Pull Request Size & Reviewability — MANDATORY
Every PR MUST be small enough to review thoroughly.

Default limits:
- Target PR size: **50–200 changed LOC**.
- Soft cap: **300 changed LOC**.
- Hard cap: **500 changed LOC**, unless explicitly approved by the project owner.

If a planned change is expected to exceed the soft cap, the agent MUST stop and propose a PR decomposition plan before editing.

A PR MUST have exactly one primary purpose. Do not mix unrelated changes.

Separate when practical:
- Source-code logic.
- Tests.
- Documentation.
- Generated artifacts.
- Dependency / lockfile changes.
- Notebook or result artifacts.

Allowed exceptions:
- Initial documentation import.
- Lockfile-only dependency update.
- Generated result/asset artifact PR.
- Final README/notebook artifact PR.
- Explicit owner-approved bulk refactor.

Even when exceptions apply, the PR description MUST explain why the PR exceeds the normal review budget.

### 7.2.2 Pull Request Template — MANDATORY
Every AI-assisted repository MUST include a PR template.

The template MUST ask for:
- Purpose of PR.
- Changed files summary.
- Changed LOC estimate.
- Whether PR exceeds target/soft/hard cap.
- Tests run.
- Coverage result.
- Ruff result.
- Artifacts added or regenerated.
- Prompt log updated.
- Cost log updated.
- Scope exclusions.
- Whether AI agent performed any git operations.

### 7.2.3 Delegated AI Git Workflow — MANDATORY for AI-Assisted Projects

AI agents MAY perform safe git operations for PR branches when explicitly allowed by `CLAUDE.md`.

Allowed safe operations MUST follow this strict task loop:

1. Sync `main` (`git switch main`, `git pull --ff-only`).
2. Create a feature branch (`git switch -c <branch>`).
3. Implement and review changes locally.
4. Stage intended files (`git add`).
5. Commit changes with a strict message format:
   - Title MUST start with `[Stage-<stage #>]`.
   - Body MUST start with `[Task-<task #>]` tags.
6. Push the feature branch to origin.
7. Propose the PR description based on the pull_request_template.md (or the structured commit body in `CLAUDE.md §2.9.1` if no `.github/` directory exists).
8. Stop and wait for the human owner to create, review, approve and squash-merge the PR.
9. Switch back to `main`, sync, and delete the local branch (`git branch -d <branch>`).

AI agents MUST NOT:

- commit directly to `main`
- push directly to `main`
- create, approve, merge, or squash GitHub PRs unless explicitly authorized
- create release tags unless explicitly authorized
- force-push
- rewrite shared history
- run destructive reset/clean commands
- delete remote branches
- change remotes
- bypass branch protection

The human owner remains responsible for:

- PR creation or approval
- PR review
- squash merge to `main`
- release tagging
- approving destructive or history-rewriting operations

Before any AI git write operation, the agent MUST inspect current branch and working tree status. If unrelated user changes are present, the agent MUST stop and ask for instructions.

### 7.3 Prompts Book — Required
Maintain `docs/PROMPTS.md`: every significant prompt used to build the project, with:
- Date.
- Phase.
- Context.
- Goal.
- Prompt summary or full prompt when important.
- Files changed.
- Expected output.
- Actual output.
- Issues encountered.
- Refinements made.
- Lesson learned.
- Approval status.

Every PR that uses AI assistance SHOULD update `docs/PROMPTS.md` unless the PR is a trivial manual-only change.

Prompt entries MUST distinguish:
- Planning prompts.
- Implementation prompts.
- Review/audit prompts.
- Fix prompts.
- Final submission prompts.

### 7.4 `uv` as Package Manager — MANDATORY
**`pip` is FORBIDDEN.** All projects MUST use `uv` as package manager and task runner. NEVER use `virtualenv`, `venv`, `python -m`, or `pip install` directly.

| Task | Forbidden | Correct |
| --- | --- | --- |
| Install dependencies | `pip install` | `uv sync` |
| Add dependency | `pip install <pkg>` | `uv add <pkg>` |
| Run script | `python script.py` | `uv run python script.py` |
| Run tests | `python -m pytest` | `uv run pytest tests/` |
| Lock dependencies | `pip freeze` | `uv lock` |

**Requirements:**
- `pyproject.toml` is the SINGLE source of truth for dependencies (NO `requirements.txt`).
- `uv.lock` MUST exist and be committed to version control.
- No direct calls to `pip` or `python -m` in code, scripts, CI/CD, or documentation.
- All tools invoked through `uv run`.

---

## 8. Research & Results Analysis

What separates a professional project from a regular one is deep research and results analysis.

### 8.1 Parameter Sensitivity Analysis
Systematic process to test how parameters affect system performance:
- Systematic experiments with controlled parameter variation.
- Precise documentation of each parameter's effect.
- Advanced analysis methods: partial derivatives, variance-based analysis, OAT ("one-at-a-time") approach.

### 8.2 Results Analysis Notebook
- Use Jupyter Notebook (or equivalent) for methodical analysis.
- Compare algorithms, configurations, approaches.
- Include mathematical proofs or theoretical analyses.
- Cite academic literature.
- Use **LaTeX** for equations and professional formulas.

### 8.3 Visual Presentation of Results
- High-quality data visualization is essential to convey research messages.
- Visualization types: `Heatmaps` (correlations), `Scatter plots` (trends), `Line charts` (comparisons), `Bar charts` (parameter sensitivity), `Box plots` (distributions), `Waterfall charts` (change analysis).
- Quality measured by: label clarity, consistent and accessible colors, detailed captions, clear legend, high resolution.

---

## 9. UI / UX

### 9.1 Quality Criteria
**Usability criteria:** Learnability, Efficiency, Memorability, Error Prevention, Satisfaction.

**Nielsen's 10 Heuristics:** visibility of system status, match between system and real world, user control & freedom, consistency & standards, error prevention, recognition over recall, flexibility & efficiency, aesthetic & minimalist design, help users recover from errors, help & documentation.

### 9.2 Interface Documentation
Comprehensive interface documentation MUST include: screenshot per screen and state, description of typical user `workflow`, explanations of interactions and feedback, accessibility considerations.

---

## 10. Costs, Runtime & AI Usage

### 10.1 Cost Analysis
**API Token Cost Breakdown** — Exact token accounting MUST be used when available. When unavailable, projects MUST record practical cost proxies: session count, plan used, wall-clock time, experiment runtime, generated artifacts, review time, and rework.

Example format for API-token projects:

| Model | Input Tokens | Output Tokens | Total Cost |
| --- | --- | --- | --- |
| GPT-4 | 523,000 | 1,245,000 | $45.67 |
| Claude 3 | 412,000 | 890,000 | $32.11 |
| **Total** | **935,000** | **2,135,000** | **$77.78** |

**Optimization strategies:** model selection by cost-benefit ratio, reducing token usage, batch processing.

### 10.2 Budget Management
- Cost forecasting at scale.
- Real-time usage monitoring.
- Alerts for budget overruns.

### 10.3 `COSTS.md` — Mandatory AI-Assisted Project Ledger
Every AI-assisted project MUST maintain `COSTS.md`.

Minimum fields:

| Date | Phase/PR | Branch | PR | Commit(s) | Agent/Model | Effort/Reasoning | Task | Wall Time | Human Review Time | Runtime/Compute | Accepted? | Notes |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

When exact API token costs are available, include:
- Input tokens.
- Output tokens.
- Cost per million tokens.
- Total estimated cost.

When exact token costs are unavailable, record:
- Subscription/plan used.
- Session count.
- Wall-clock time.
- Long-running commands.
- Experiment runtime.
- Human review burden.
- Rework caused by AI output.

Cost tracking is not only financial. It is also a measure of review debt, runtime debt, and agent-efficiency.

---

## 11. Extensibility & Maintainability

### 11.1 Extension Points
**Plugins Architecture** that allows adding new functionality without changing core code:
- Clear interfaces for extension.
- `hooks` (lifecycle hooks like `beforeCreate`, `afterUpdate`).
- `middleware` mechanisms.
- API-first design.

### 11.2 Maintainability
Code MUST be: modular, separated by responsibility, reusable component-by-component, analyzable, testable.

---

## 12. International Quality Standards

### 12.1 ISO/IEC 25010 — Eight Product-Quality Characteristics
1. **Functional Suitability** — completeness, correctness, appropriateness.
2. **Performance Efficiency** — response time, resource utilization, capacity.
3. **Compatibility** — co-existence, interoperability.
4. **Usability** — learnability, operability, accessibility, error protection.
5. **Reliability** — maturity, availability, fault tolerance, recoverability.
6. **Security** — confidentiality, integrity, authentication, accountability.
7. **Maintainability** — modularity, reusability, analyzability, modifiability, testability.
8. **Portability** — adaptability, installability, replaceability.

---

## 13. Project Organization as a Package

### 13.1 Package Definition File
Every package MUST include `pyproject.toml` (preferred) or `setup.py` specifying: name, version, description, author, license, dependencies.

### 13.2 `__init__.py` Files
- MUST exist in main directory and every subdirectory.
- Recommended use: define `__all__` to export public interfaces; define `__version__`.

### 13.3 Relative Paths
- All imports MUST use relative paths or package names — NEVER absolute paths.
- File read/write MUST also be done relative to package path.

### 13.4 Package Checklist
1. **Definition file:** `pyproject.toml` exists? Contains name, version, dependencies? Dependencies pinned with versions?
2. **`__init__.py`:** exists in main directory? Exports public interfaces? `__version__` defined?
3. **Directory structure:** source in dedicated directory? Tests in `/tests`? Documentation in `/docs`?
4. **Relative paths:** all imports relative? No absolute paths?

---

## 14. Performance & Parallel Processing

### 14.1 Multiprocessing vs. Multithreading
- **Multiprocessing — for CPU-bound:** mathematical computation, image processing, model training. Each process runs in separate memory and uses a different CPU core.
- **Multithreading — for I/O-bound:** database access, network calls, file read/write. Threads share memory; useful when waiting.

### 14.2 Thread Safety
**Thread safety is critical:** protect shared variables with locks, use `queue.Queue` for inter-thread data transfer, avoid mutual locking, use `context managers`.

### 14.3 Parallelism Checklist
1. **Identify:** I/O-bound vs CPU-bound, evaluate benefit, choose right tool.
2. **Implementation:** dynamic process/thread count, safe data sharing, correct synchronization.
3. **Resource management:** correct closing, exception handling, prevent memory leaks.
4. **Safety:** protect shared variables, prevent race conditions, mutual locking.

---

## 15. Modular Design with Building Blocks

### 15.1 Building-Block Structure
Each building block is defined by:
- **Input Data** — data types, valid domain, external dependencies, comprehensive validation.
- **Output Data** — data types, format, edge-case behavior.
- **Setup Data** — parameters with defaults, configuration, initialization.

### 15.2 Design Principles
- **Single Responsibility** — each block does ONE task.
- **Separation of Concerns** — each block deals with ONE aspect.
- **Reusability** — blocks are independent, with no dependency on specific code.
- **Testability** — each block testable via dependency injection.

### 15.3 Building Block Example

```python
class DataProcessor:
    """
    Input:  raw_data (List[Dict]),
            filter_criteria (Dict)
    Output: processed_data (List[Dict])
    Setup:  processing_mode ('fast'/'accurate'),
            batch_size (int, default: 100)
    """

    def __init__(self, processing_mode='fast', batch_size=100):
        self.processing_mode = processing_mode
        self.batch_size = batch_size
        self._validate_config()

    def process(self, raw_data, filter_criteria):
        self._validate_input(raw_data, filter_criteria)
        return self._do_processing(raw_data, filter_criteria)

    def _validate_config(self):
        if self.processing_mode not in ['fast', 'accurate']:
            raise ValueError("Invalid mode")
        if self.batch_size <= 0:
            raise ValueError("Batch size > 0")

    def _validate_input(self, data, criteria):
        if not isinstance(data, list):
            raise TypeError("data must be list")
        if not isinstance(criteria, dict):
            raise TypeError("criteria must be dict")
```

---

## 16. Final Submission Checklist

### 16.1 Documentation & Structure
- [ ] Comprehensive `README.md` at project root, user-manual level.
- [ ] `docs/` with `PRD.md`, `PLAN.md`, `TODO.md`.
- [ ] Dedicated `PRD_*` for every algorithm/central mechanism.
- [ ] Architecture documentation with clear diagrams (C4, UML, deployment).
- [ ] Documented prompts book.
- [ ] `CLAUDE.md` exists and was reviewed before implementation.
- [ ] `COSTS.md` exists and includes AI/runtime/review-cost entries.
- [ ] `.github/pull_request_template.md` or `docs/REVIEW_POLICY.md` exists, OR structured commit body in `CLAUDE.md §2.9.1` serves as the equivalent (owner decision).
- [ ] `docs/PROMPTS.md` is complete for all significant AI sessions.
- [ ] PRs were kept within reviewable size limits or exceptions were justified.
- [ ] Generated artifacts are either tracked intentionally or documented as reproducible.
- [ ] AI git permissions are defined in `CLAUDE.md`.
- [ ] AI-created commits were limited to PR branches.
- [ ] No AI direct commits to `main`.
- [ ] Human owner reviewed and merged PRs.

### 16.2 Architecture & Code
- [ ] SDK architecture — all business logic via SDK layer.
- [ ] OOP design — no code duplication, use inheritance and `mixins`.
- [ ] API Gatekeeper — all external calls through it.
- [ ] Rate limits from configuration; queue management on overflow.
- [ ] Files ≤ 150 lines of code; comments and `docstring`s present.
- [ ] Consistent code style; descriptive names.
- [ ] No PR mixes unrelated concerns.
- [ ] Large phases were decomposed into reviewable PR-sized slices.

### 16.3 Quality & Testing
- [ ] **TDD** — tests written before/with code (RED-GREEN-REFACTOR).
- [ ] **Coverage ≥ 85%**.
- [ ] **Zero `ruff check` violations**.
- [ ] Edge-case documentation and error handling.
- [ ] Automated test reports.

### 16.4 Configuration & Security
- [ ] Configuration files separated from code; versioned.
- [ ] `.env-example` with placeholder values.
- [ ] No API keys or secrets in code.
- [ ] `.gitignore` up to date.
- [ ] **`uv`** as the only package manager.
- [ ] `uv.lock` and `pyproject.toml` exist.

### 16.5 Research & Visualization
- [ ] Systematic experiments with parameter variation.
- [ ] Documented sensitivity analysis; analysis notebook with graphs.
- [ ] Quality graphs, screenshots, architecture diagrams.
- [ ] AI/runtime/review-cost analysis and optimization strategies documented in `COSTS.md`.

### 16.6 Standards & Extensibility
- [ ] Documented `extension points`.
- [ ] Organized as a professional Python package.
- [ ] Parallelism with thread safety.
- [ ] Building-block-based design.
- [ ] Compliance with **ISO/IEC 25010**.
- [ ] Organized Git history; license, attribution, deployment instructions.

---

## 17. Quick Reference — Code Quality Requirements Summary

| Rule | Threshold | Enforcement |
| --- | --- | --- |
| SDK architecture | All business logic through SDK | Code review |
| OOP / no duplication | No logic duplicated in 2+ copies | Code review + tests |
| API Gatekeeper | All API calls go through it | Code review |
| Configuration source | From config files, NOT source code | Code review |
| Queue management | Queue, not crash, on overflow | Integration test |
| TDD workflow | Red-Green-Refactor | Code review |
| Version control | Initial version `1.00` | Module + automated test |
| File size | ≤ 150 lines of code | Automated check |
| Linter violations | `0` | `ruff check` |
| Test coverage | `≥ 85%` | `pytest --cov` |
| Hard-coded values in code | `0` | Code review |
| Secrets in code | `0` | Automated scan + `.env-example` |
| Package manager | Only `uv` | Automated check |
| PR size target | 50–200 changed LOC | PR template + code review |
| PR soft cap | 300 changed LOC | Stop and decompose |
| PR hard cap | 500 changed LOC | Owner approval required |
| `CLAUDE.md` | Required for AI-assisted projects | Initial setup review |
| `COSTS.md` | Required for AI-assisted projects | PR review |
| Prompt log | All significant AI sessions | `docs/PROMPTS.md` review |
| Generated artifacts | Tracked intentionally or reproducible | README + gitignore review |

---

## 18. References (English)

1. Archbee — README files guide.
2. GitHub — About READMEs (`docs.github.com`).
3. Monday.com — PRD template.
4. Miro — Modular PRD template.
5. Aha! — Product requirements document guide.
6. Daily.dev — 10 code commenting best practices.
7. Stack Overflow — Best practices for writing code comments (2021).
8. Codacy — Code documentation best practices.
9. Hoop.dev — API security: secrets via environment variables.
10. Anthropic — API key best practices.
11. OpenAI — Best practices for API key safety.
12. UX Design — Measuring design quality with heuristics.
13. J. Nielsen — 10 usability heuristics for UI design (1994).
14. ISO/IEC 25010:2011 — Systems and software quality.
15. MIT ACIS — Software Quality Assurance Plan.
16. Google — Engineering practices documentation.
17. Microsoft — REST API guidelines.
18. Anthropic — Claude Code memory / CLAUDE.md documentation.
19. Google Engineering Practices — Small CLs.
20. GitHub Docs — Best practices for reviewing pull requests.
21. DORA / SPACE-style productivity thinking — review burden, flow, and developer productivity metrics.

---

## 19. Important Note (from the original)

This document presents a particularly high level of excellence. **Not every section is fully obligatory in every project**, but the more criteria fulfilled, the higher the quality assessment. Focus on depth, professionalism, and demonstration of high-level development capability. Use of LLM tools and AI agents is recommended as part of completing the project; testing may also use AI agents.

> **Author:** Dr. Yoram Segal — All rights reserved © — Version 3.00 (2026-03-26).

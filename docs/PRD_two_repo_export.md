# PRD — Two-Repository Export & Submission

> Dedicated PRD (guideline §1.3). **Build stage:** 7 (7.6a role entry points,
> 7.6b export). Ground-truth: `CLAUDE.md` §13 + §36.1/§36.6. Indexed in
> `docs/PRD.md`. The submission is **two** self-contained repos generated from this
> one canonical workspace — never hand-maintained copies.

## 1. Purpose

Deliver `github.com/mironovich-v/cop-rob-p2p-police` and `…-thief` as two
independently installable/testable release trees, each carrying its role entry
point plus a **vendored snapshot of the one canonical `cop_thief_core`**, with a
drift check tying both back to the source commit. Neither export may depend at
runtime on the other repo or a private third repo (§13).

## 2. Role entry points (7.6a)

Each role runs headless as its own module:

```bash
uv run python -m police_agent --config config/police
uv run python -m thief_agent  --config config/thief
```

- The CLI logic lives in ONE tested place, `cop_thief_core/agent_cli.py`
  (`parse_args`, `run_role`); each role `__main__` is a one-line delegate (DRY,
  guideline §3). `run_role` plays one series through `SimulationSdk.run_peer`
  (the single business entry point), writes the four artifacts, and prints the
  **derived** result. `--real-llm` opts into the banter provider (default stub;
  the MOVE is always pure Python). `transport` is injectable so tests drive it
  over the in-process FakeTransport — no network. ✅

## 3. Export (7.6b — `scripts/export_repos.py`)

Deterministic, re-runnable, no secrets:

- Produce `dist/police-agent/` and `dist/thief-agent/`, each with: the role
  package (`police_agent` / `thief_agent`), a **vendored `cop_thief_core`**
  snapshot, that role's `config/<role>/`, `pyproject.toml` (role script + pinned
  deps), `README` stub, and the test subset that runs standalone.
- **Drift manifest** in each export (`core_manifest.json`): the canonical core
  source commit + a content hash over the vendored tree, so a check can prove both
  exports came from the same core. Fail on mismatch.
- **Cross-link** each export to the other's repo URL (docs only — no runtime dep).
- **No secrets / no private match state:** exclude `.env`, `secrets/`, `logs/`,
  `dist/`, caches; `.env-example` placeholders only.
- Deterministic: stable file order, no timestamps in hashed content (pass any
  timestamp in), identical output on re-run from the same commit.

## 4. Acceptance criteria

- **AC-X1** — `python -m police_agent` / `-m thief_agent` each play a full series
  and write the four artifacts; `run_role` is covered by `test_agent_cli`. ✅ (7.6a)
- **AC-X2** — export produces two self-contained trees; each imports standalone
  (subprocess with `PYTHONPATH=<export>/src`) and its vendored suite runs in an
  isolated env with no reference to the workspace or the sibling package (police
  ships no `thief_agent`, and vice versa). ✅ (7.6b)
- **AC-X3** — both exports carry a `core_manifest.json` with the same
  `core_sha256`; `export_all` raises on any drift between them. ✅ (7.6b)
- **AC-X4** — no `.env`, `secrets/`, `logs/`, `dist/`, or `*.pyc` in either export
  (`.env-example` placeholders only); the exporter's own test is excluded; the core
  hash carries no timestamp, so re-running from the same commit is byte-identical. ✅ (7.6b)

## 5. Open decisions / owner input

- Confirm the two submission repo URLs (§36.1) and that each export's README names
  the canonical workspace + sibling. Final `git init` + push of each `dist/` tree
  to its submission repo is an owner action (7.7 / submission).

## 6. Out of scope

Academic README + submission tag (7.7); the game/report/GUI mechanics (their own PRDs).

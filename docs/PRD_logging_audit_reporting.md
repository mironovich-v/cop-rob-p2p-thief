# PRD — Logging, Audit & the Four JSON Artifacts

> Dedicated PRD (guideline §1.3). **Build stage:** 7 (7.1 artifacts ✅, 7.2 emit ⏳).
> Ground-truth spec: `CLAUDE.md` §36 + reference repo (`report/artifacts*.py`,
> `report/emit.py`). Indexed in `docs/PRD.md`. Interop-critical: cross-team fields
> (`config_sha256`, `mutual_agreement.sha256`) MUST match byte-exactly.

## 1. Purpose

Every played series must leave a **standardized, self-auditing paper trail** the
lecturer can grade and both teams can independently verify. The trail is four JSON
artifacts per series, all joined by one `game_uid` and cross-linked by a `links`
block, derived deterministically from the sealed commit-reveal log — never from a
trusted running tally.

## 2. The four artifacts (book Appendix F templates)

| # | Artifact | Scope | Filename | Key locked field |
|---|----------|-------|----------|------------------|
| 1 | **declaration** | whole series (static) | `declaration_<game_id>.json` | per-group self-`signature` |
| 2 | **config** | one sub-game | `config_<game_id>_g<NN>.json` | `config_sha256` (canonical, compact) |
| 3 | **log** | one sub-game | `log_<game_id>_g<NN>.json` | `mutual_agreement.sha256` (records) |
| 4 | **result** | whole series | `result_<game_id>.json` | `mutual_agreement.sha256` (series) |

- **declaration** — team identity, members, repos, MCP URLs, hardware, LLM model,
  token cap, start/end times. No role / no `sub_game_number` (roles alternate).
  Each team's block is self-signed with `consensus_signature` over the block.
- **config** — the 14 agreed signed terms spread verbatim, plus `config_sha256 =`
  compact-canonical SHA-256 of the terms only (the byte-identical App-F lock).
- **log** — the peer's per-sub-game sealed records + audit result;
  `mutual_agreement.sha256 = consensus_signature(records)` (SPACED serializer).
- **result** — per-sub-game scores + aggregate outcome + `tokens_total_series`;
  both teams must agree and each emails its own copy.

## 3. Serializers (do not cross the streams)

- `config_sha256` uses the **compact** canonical form (`separators=(",",":")`),
  matching the config-lock CORE vector.
- `mutual_agreement.sha256` uses the **spaced** `consensus_signature` (report CORE
  vector) — deliberately distinct from the compact form so the two locks can never
  be confused. Verified by conformance test `report_consensus`.

## 4. Module layout

| Module | Responsibility | Lines |
|--------|----------------|-------|
| `reporting/artifact_schemas.py` | `_schema`/`_remark` text + `SCHEMA_VERSION`, `DEFAULT_TIMEZONE` | 28 |
| `reporting/artifact_helpers.py` | filenames, `links`, `canonical_sha256`, `ended_at`, `group_block`, `hardware_spec`, `tokens_series` | 58 |
| `reporting/artifacts.py` | pure `build_{declaration,config_artifact,log,result}` | 117 |
| `reporting/report_writer.py` | `consensus_signature` / `sign_report` / `verify_report` (Stage 6.3) | — |
| `reporting/emit.py` | write the 4 files to disk per series; wire into `SimulationSdk.run_peer` | 94 |

All builders are **pure** (dict in → dict out, no I/O), so they are exhaustively
unit-testable offline and reused unchanged by the emit writer and the GUI/replay.

## 5. Acceptance criteria

- **AC-R1** — All four artifacts carry the same `game_uid` and identical `links`. ✅
- **AC-R2** — `config_sha256 == canonical_sha256(terms)`; independent of `_schema`. ✅
- **AC-R3** — declaration has exactly `group_1`/`group_2`, each self-signed and
  verifiable via `consensus_signature`; `hardware_spec` is exactly the six book
  fields. ✅
- **AC-R4** — `log.mutual_agreement.sha256 == consensus_signature(records)` and
  `confirmed` mirrors the sealed-log audit verdict. ✅
- **AC-R5** — `result.final_result.tokens_total_series` sums per-group tokens across
  sub-games; `mutual_agreement.confirmed` is true only if every sub-game's log
  verified. ✅
- **AC-R6** — `emit_series` writes the 4 files with the derived names under
  `<workdir>/<logs_dir>/<group_id>/`; the returned result equals the on-disk bytes
  and both peers derive the **same** `mutual_agreement.sha256` (symmetric outcome
  only — no per-peer tokens/timestamps in the signed preimage). ✅
- **AC-R7** — result totals are DERIVED from the sealed log, never a trusted tally
  (ties AC5 in `docs/PRD.md`). ✅

## 6. Out of scope (later Stage-7 slices)

Hebrew report text (7.2), Gmail send (7.3, `PRD_email_reporting`), GUI/replay
(7.4–7.5, `PRD_gui_replay`), two-repo export + drift check (7.6, `PRD_two_repo_export`).

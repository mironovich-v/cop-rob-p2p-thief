# PRD — Gmail OAuth Reporting (send-only, exact bytes)

> Dedicated PRD (guideline §1.3). **Build stage:** 7 (7.3a report body ✅,
> 7.3b Gmail send-only ⏳). Ground-truth: `CLAUDE.md` §36 + reference repo
> (`report/report_writer.build_report`, `infra/email_sender.py`) + league SPEC §6.
> Indexed in `docs/PRD.md`. **Interop-critical + billing-safe.**

## 1. Purpose

Each peer emails the lecturer its own **official match report** at settlement. Two
independent, separable concerns:

1. **The report body** (7.3a) — WHAT bytes are emailed.
2. **The send transport** (7.3b) — HOW they leave the machine, safely.

## 2. The emailed report body (7.3a — `reporting/report_builder.py`)

- `build_report(summary, terms)` builds the rich, per-peer, audit-verified Hebrew
  report (book ch.8 schema, following the v3.0.0 reference `build_report`): role,
  group, sub-game, timing, the sealed **spec/token declaration** (from the step-0
  `system_spec` record, so it is audit-covered), Hebrew result, winner, the agreed
  terms, the crypto-audit verdict, the verified step log, this peer's signed
  records, and mutual agreement. It is then **self-signed** with the consensus key
  (`report_writer.sign_report` — sign-then-insert under `חתימת_קונסנזוס_משותפת`).
- `report_body(signed_report)` returns the **exact bytes to email**: spaced
  canonical `json.dumps(sort_keys=True, ensure_ascii=False)` — the consensus
  preimage form. **Never `indent=2` / pretty-printed** (SPEC §6: a re-serialized
  email nearly scored 0; §36.3.5). Hebrew stays literal (`ensure_ascii=False`), so
  a verifier pops the signature key and re-hashes this exact form.
- **Derived, not declared:** totals/tokens come from the sealed summary, never a
  claim.

### Serializer note (why two forms coexist)
The report SIGNATURE uses the SPACED serializer (release's 2nd canonical form,
SPEC §6); every ordinary hash uses the COMPACT §2 form. `config_sha256` (compact)
and the report body (spaced) deliberately differ — reusing the exact CORE-vector
functions keeps both correct.

## 3. The send transport (7.3b — `infra/email_sender.py`)

Portable Gmail OAuth **send-only** flow (this project ADDS this; the reference used
a Windows-path `gg:email` skill — §36.6). Requirements:

- **Dry-run-default, disabled-default** *(ADR-20, supersedes the draft default —
  rule 30's send-only scope cannot create drafts, so a draft-based gate depended
  on a permission the rules don't grant; kit WARNINGS §6)*. `email.enabled=false`
  → no-op; `email.mode` defaults to `dry_run` (build + log the exact MIME,
  transport untouched). The safety gate is **structural and recipient-shaped**:
  the lecturer's address is unreachable — matched case-/whitespace-insensitively,
  including inside recipient lists — unless the run is doubly armed (config
  `counted=true` AND CLI `--counted`); an armed run that cannot deliver its
  report refuses to start. Under the diversity rule only the *first* meeting
  counts, so an accidental real send can burn the one counted game (SPEC §6).
- **Body AND attachment.** The counted-series mail carries the result JSON as
  the body **and the same file as the single named attachment** (rule 34's two
  readings, both satisfied — kit SPEC §6.1); declaration/configs/logs are
  repo-published via `links.github`, never mailed.
- **Gatekeeper-routed.** Every Gmail API call goes through `ApiGatekeeper`
  (service `email`) — rate-limited, queued, logged (guideline §4). No call bypasses
  it.
- **Mockable / offline-testable.** The Gmail service is injected; **tests never send
  real mail and never require network/credentials** (constraint §13). Unit tests
  cover: disabled→skip, draft-created, gatekeeper used, error→structured reason.
- **Secrets via `.env`.** OAuth client + token from `.env` / `secrets/` (never
  committed); `.env-example` carries placeholders only.
- **MIME body is the exact `report_body` bytes** — no re-serialization in MIME
  construction.

## 4. Acceptance criteria

- **AC-E1** — `build_report` carries the book schema, Hebrew result mapping, and a
  valid self-consensus signature (`verify_report` true). ✅
- **AC-E2** — `report_body` is spaced canonical, never pretty-printed; non-ASCII is
  literal; a parsed body re-verifies. ✅
- **AC-E3** — spec/token declaration is sourced from the sealed step-0 record and
  the summary (derived, not claimed). ✅
- **AC-E4** — email defaults to disabled; when enabled, defaults to `dry_run`; a
  real send needs explicit `email.mode="send"`; the lecturer's address is
  structurally unreachable (case-/whitespace-insensitive, incl. inside lists)
  unless doubly armed (`game.counted` AND `--counted`); an armed run that cannot
  deliver refuses to START; body == named attachment, reference subject form,
  auto-fired at settlement; the injected transport means tests never send and
  need no credentials. ✅ re-verified at task 8.8 (ADR-20).
- **AC-E5** — every Gmail call (token refresh + draft/send) goes through the
  `ApiGatekeeper` (service `email`); a transport failure returns a structured
  reason and never raises past `send_report`. ✅
- **AC-E6** — `build_raw` MIME decodes back to exactly `report_body` (Hebrew
  literal, UTF-8), proven by round-trip. ✅ End-to-end: `SDK.run_peer` builds the
  official report from the final sub-game and sends `report_body`; a wiring test
  (`test_email_wiring`) plays a real 2-peer match and asserts the drafted MIME body
  decodes to exactly that `report_body`. Disabled by default (no send). ✅ (7.7a)

Implementation split: `infra/gmail_client.py` (raw-HTTPS, stdlib-only, injectable
`http`) + `infra/email_sender.py` (policy + gatekeeper). No new dependencies.

## 5. Open decisions / owner input (OD-3)

- Sender Gmail account + OAuth client credentials (owner provides; `.env`).
- Lecturer recipient address; subject convention.
- Confirm the emailed report schema with the opponent team where cross-team
  agreement is required (the rich per-peer report is each team's own; the mutual
  signature is the agreed surface).

## 6. Out of scope

The four on-disk artifacts (`PRD_logging_audit_reporting`), GUI/replay, export.

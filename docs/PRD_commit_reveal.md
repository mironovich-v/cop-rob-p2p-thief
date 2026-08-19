# PRD — Commit-Reveal Sealing & Mutual Audit

> Dedicated PRD (guideline §1.3). **Build stage:** 6 (much already built across
> 2.3a interop, 2.5a sealing, 2.5b audit; 6.1 adds the Step-0 host-spec record;
> 6.2 hardens the adversarial audit). Ground truth: league SPEC §3; reference
> `domain/crypto.py`, `peer/{sealing,summary}.py`; `CLAUDE.md` §36.

## 1. Background

Each step a peer seals its true `(state, move, verdict, hint, …)` under
`commit = SHA256(canonical_json(payload) + "|" + nonce)` and sends **only** the
commit; nonces are withheld until the end-of-game audit, where both peers re-hash
every revealed record. Nothing can be rewritten after the fact — a forged or
tampered log is provable and forfeits the game (`tamper_forfeit`).

## 2. Requirements (FR-14)

- Per-step sealing with the reference construction (SPEC §3); fresh nonce each step.
- A once-per-sub-game **Step-0 host-spec record** (book §6) sealed the same way.
- End-of-game mutual audit: each peer re-verifies the opponent's revealed records;
  any mismatch → `tamper_forfeit` for the honest peer, regardless of the board.
- Order/replay resistance via `step` (and sub-game/role) inside the signed payload.

## 3. Constructions & interfaces

- `interop.hashing`: `commit_of(payload, nonce)`, `new_nonce()`, `verify(...)`,
  `seal(payload) -> {nonce, commit}`, `audit_records(records) -> {passed,
  verified_steps, failed_steps}`. Backed by the `commit_reveal` CORE vector
  (including the Step-0 `system_spec` case) reproduced from our code (2.3a).
- `orchestration.sealing`: `sealed_step_record`, `sealed_spec_record` (Step-0),
  `build_turn_message`; `shared.sysinfo.collect_spec` (cached host spec).
- `orchestration.summary.finish`: exchanges `AuditPayload`, runs `audit_records`
  on the opponent's log, overrides to `tamper_forfeit` on failure.

## 4. Alternatives considered

- The book's other two commit constructions (nonce-in-object; `nonce|move`) →
  **rejected** (SPEC pins the reference form; the `nonce|move` form binds neither
  state nor intent — see ADR-2).
- Trusting claimed results without re-hashing → **rejected** (audit is the point).

## 5. Success criteria & tests

The `commit_reveal` CORE vector passes from our functions (all cases + the three
divergent forms). A full match seals every step + the Step-0 record and both
audits pass; a tampered opponent record forces `tamper_forfeit` (6.2). Tests:
`test_crypto`/`test_interop_primitives`, `tests/conformance` `commit_reveal`,
`test_sysinfo` (Step-0 re-verifies), `test_runtime` (audits pass), adversarial
audit (6.2).

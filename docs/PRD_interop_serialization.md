# PRD — Interop Serialization & Vector Conformance

> Dedicated PRD (guideline §1.3). **Build stage:** 6 (much built earlier: 2.3a
> canonical/commit/game_uid, 4.1 pheromone; 6.3 adds the report consensus signature
> — the last CORE surface). Ground truth: league SPEC §2/§6; reference
> `domain/crypto.py`, `report/report_writer.py`; `CLAUDE.md` §36.3.

## 1. Background

Two independent implementations must produce byte-identical output on a small set
of surfaces or the game cannot start / audit / settle. The load-bearing subtlety:
**most** hashes use the compact canonical JSON, but the **report consensus
signature uses a second, spaced form** — a team that uses the wrong serializer
fails settlement at the moment both must agree.

## 2. Requirements (FR-15, NFR-9)

One production canonical-JSON function, reused everywhere; the six CORE surfaces
reproduced byte-for-byte by OUR functions (never the kit oracle); never edit a
vector to pass.

## 3. The serialization forms

- **Compact canonical JSON** (`interop.canonical.canonical_json`): `sort_keys=True,
  ensure_ascii=False, separators=(",",":")` — under commit-reveal, terms signature,
  `game_uid`, and ordinary hashes.
- **Spaced report-consensus form** (`reporting.report_writer.consensus_signature`):
  `json.dumps(report, sort_keys=True, ensure_ascii=False)` (DEFAULT `", "` / `": "`
  separators), SHA-256 over it; **sign-then-insert** under key
  `חתימת_קונסנזוס_משותפת`; verify = pop key, re-serialize spaced, re-hash, compare.
- Both keep native UTF-8 (Hebrew/emoji) and shortest-round-trip floats.

## 4. The six CORE surfaces (status)

`canonical_json` ✅ · `commit_reveal` ✅ · `terms_signature` ✅ · `game_uid` ✅ ·
`pheromone` ✅ · `report_consensus` ✅ (6.3) — **all six pass from our code.**

## 5. Alternatives considered

Using the compact form for the report signature → **rejected** (SPEC §6; the vector
`compact_form_sha256` proves it does not reproduce the signature). One serializer
for everything → **rejected** (the release genuinely pins two forms).

## 6. Success criteria & tests

Every CORE vector reproduced from our production functions; the spaced signature
differs from the compact contrast hash; sign→verify round-trips and fails on
tamper / missing signature. Tests: `tests/conformance/test_core_vectors.py`
(all six), `test_report_writer`.

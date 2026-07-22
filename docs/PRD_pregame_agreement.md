# PRD — Pre-Game Agreement (negotiation, terms signature, game_uid)

> Dedicated PRD (guideline §1.3). **Build stage:** 2/6 (TODO slice 2.3). Ground
> truth: reference `domain/negotiation.py`, `domain/game_ids.py`,
> `peer/sealing.py:terms_from_config`; league SPEC §4; `CLAUDE.md` §36.2–36.3.
> This is an **interop surface** — byte-exact, backed by CORE vectors.

## 1. Background

Before play, both peers exchange the agreed terms, each signs them, verify each
other, and independently derive the same `game_uid`/`game_id`. Any mismatch → the
peer refuses to start. This is the pre-game gate that guarantees both sides play
identical, signed rules.

## 2. Requirements (FR-7)

Extract the 14-key signed-terms subset from config; sign with a fresh nonce;
verify the opponent's signature over value-equal terms; derive
`game_uid`/`game_id` order-independently; **refuse to start** when: terms not
value-equal, signature fails, a required field is absent, a mandatory **minimum is
violated**, or the protocol/core version is incompatible.

## 3. Constructions (byte-exact — from `interop/`)

- **Canonical JSON** (shared production fn): `json.dumps(obj, sort_keys=True,
  ensure_ascii=False, separators=(",",":"))`.
- **Signature** = `SHA256(canonical_json(terms) + "|" + nonce)` (nonce =
  `secrets.token_hex(16)`, pipe-appended). Opponent re-verifies with the signer's
  nonce over the terms it received.
- **`game_uid`** = `UUID(SHA256(canonical(terms) + "|" + "|".join(sorted([g_a,
  g_b])))[:16])`; **`game_id`** = `"{sorted_a}-vs-{sorted_b}"`.

## 4. Signed terms (14 keys)

`board_size, smell_grid_size, decay_per_step, emit_intensity, min_center_intensity,
max_steps, barriers_max, setting, hint_max_words, axis_origin_corner,
axis_start_index, thief_start, cop_start, num_games` — extracted from `CFG` by
`terms_from_config`. Identity (`group_id`, members, repos) is exchanged but **not**
signed. Minimum-validation (App-F floors, loaded from data) runs here and refuses
on any below-floor value.

## 5. Alternatives considered

Adding a choice as a new signed key → **rejected** (breaks the flat 14-key
signature; use a locked-model hash in negotiate extras instead — Stage 6/ENH).
Trusting the opponent's terms without value-equality → **rejected**.

## 6. Success criteria & tests

Our production functions reproduce the CORE vectors exactly (`canonical_json`,
`terms_signature`, `game_uid`), including Hebrew/emoji strings; group order does
not change `game_uid`; mismatched terms / bad signature / missing field /
below-minimum / incompatible version all refuse to start. Tests: `test_negotiation`,
`tests/conformance/` against `canonical_json.json`, `terms_signature.json`,
`game_uid.json` (fetched kit; run OUR functions, never the reference oracle).

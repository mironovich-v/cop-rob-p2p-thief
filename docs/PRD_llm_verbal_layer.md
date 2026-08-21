# PRD — LLM Verbal Layer (Trash Talk)

> Dedicated PRD (guideline §1.3). **Build stage:** 4. Ground truth: `CLAUDE.md`
> §13 (LLM scope, honesty) and §36.2 (`hint_max_words`); reference
> `strategy/trash_talk.py`. Companion PRD: `PRD_strategy_brains` (which owns the
> move). Indexed in `docs/PRD.md`.

## 1. Background

Every turn a peer sends a natural-language **hint** alongside its sealed move —
the psychological layer of the game. This is the *only* place a language model is
permitted to act, and the boundary is absolute: **the move is always pure
Python**. The LLM never decides legality, never chooses a direction, and can
never be the component that keeps the game running. A peer with no model, no
network, and no API key plays a complete, legal, competitive game.

A hint may **bluff** — naming a landmark the sender is nowhere near is legitimate
play. What is not legitimate is misrepresenting *game state*: the honesty
`verdict` (`truth` / `lie`) is sealed into the step commit and revealed at audit,
so a peer's own record states whether each line was a bluff. Deception is a move
in the fiction; lying about the record is a protocol failure.

## 2. Requirements (FR-11)

- Provider abstraction with a **deterministic offline provider** (`template`) as
  the default and as the fallback for every other provider.
- No unit or integration test may require a real cloud model, network, or key.
- Every hint is capped to the negotiated `hint_max_words` (15) **before** it
  reaches the wire or a committed record — the cap is a signed term, not a
  preference.
- Every hint carries a sealed honesty verdict; a bluffing line must record
  `lie`.
- A provider that is slow, erroring, or unavailable degrades to the template
  line within the step deadline. The turn must never be lost to banter.
- All model calls route through the API gatekeeper (guideline §4) and count
  against `token_budget_per_series`.

## 3. Constructions & interfaces

`strategy.trash_talk` exposes
`say(role, state, belief, setting, opponent_hint, deadline_seconds)` returning
`(hint, verdict, reasoning, prompt)`. The template provider composes a line from
a landmark vocabulary keyed by the negotiated `setting`, with a generic fallback
list so an unknown setting still yields a location cue. The thief bluffs roughly
40% of the time; the police speaks straight. A `ThreadPoolExecutor` with a
timeout bounds any provider call so a hung model cannot eat the turn.

`llm_model` is declared in the pre-game identity — we declare `template`, which
is truthful and costs zero tokens.

## 4. Alternatives considered

- **LLM-chosen moves** → rejected by the assignment and by design: the move path
  must be free, instant, offline, and always legal.
- **LLM-parsed opponent hints feeding belief** → rejected; hints may lie by
  design, so treating them as evidence hands the opponent a steering wheel. Only
  scent and declarations feed belief (`PRD_belief_map` §3).
- **Uncapped or post-hoc truncated hints** → rejected; the cap is a negotiated
  term, so it must be enforced before sealing, not after sending.
- **Banning bluffing outright** → rejected; the book's verbal layer *is* the
  bluff. Honesty is enforced where it matters — the sealed record — not in the
  fiction.

## 5. Success criteria & tests

The template provider is deterministic under a seeded RNG, always within the word
cap, always carries a verdict, and never raises. A provider that times out or
throws falls back to a template line inside the deadline. Unknown settings still
produce a location cue. The full suite runs offline with no key present. Tests: `test_trash_talk`, `test_brains` (hint plumbing), `test_llm_provider`.
Gatekeeper routing is covered by `test_gatekeeper` for the channels that make
real calls; with only the template provider wired, this layer makes none.

**Status note:** only the `template` provider is wired. A real model provider is
an opt-in extension point, not a dependency — every game played to date, friendly
and counted, ran at zero tokens.

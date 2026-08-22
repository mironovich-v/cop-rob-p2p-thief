# PRD — Opponent Belief Map

> Dedicated PRD (guideline §1.3). **Build stage:** 3 (grid built in 2.2; the
> observation channels in §4 were found and closed live on 2026-08-21).
> Ground truth: `CLAUDE.md` §36; reference `domain/belief.py`. Companion PRDs:
> `PRD_pheromone_scent` (the evidence), `PRD_strategy_brains` (the consumer).
> Indexed in `docs/PRD.md`.

## 1. Background

No peer is told where its opponent is, so every peer maintains a probability
distribution over the board and answers one question for the strategy layer:
**where is the opponent most likely to be right now?** The grid starts uniform,
spreads mass each turn to model one opponent step (`diffuse`, over the
von-Neumann neighbourhood for orthogonal play), and sharpens on evidence.

The distinction that governs the whole design: **scent is evidence about where
the opponent WAS; a declaration is evidence about where it IS.** Conflating them
is the single most expensive mistake made in this project.

## 2. Requirements (FR-8)

- Normalised distribution over N×N; degenerate mass resets to uniform rather than
  dividing by ~0.
- `diffuse()` matches the opponent's legal movement neighbourhood (4-way for
  orthogonal, 3×3 for king) — a mismatch silently models a different game.
- Evidence updates: `observe_smell` (multiplicative, trust-weighted),
  `observe_declared` (collapse), `exclude` (rule a cell out).
- `most_likely()` is the single accessor the strategy layer may use. Strategy
  code must never read the opponent's true state; the belief map is the boundary
  that makes that structurally hard.

## 3. Evidence channels, and what each is worth

| Channel | Carries | Quality |
| --- | --- | --- |
| Scent map peak | The sender's **current** cell | Exact (35/35 measured) |
| Scent map body | Where it has been | Lagging 2–3 steps |
| `capture_claim` | The **cop's own** cell (co-location claim) | Exact, every cop move |
| `claim_response: caught=false` | The thief is **not** on that cell | One cell per turn |

## 4. The lag failure, and why it was invisible

Shipped originally, belief consumed scent alone. Because a trail is strongest
where the opponent *was*, the estimate lagged: instrumented over a live-shaped
game, the thief's believed threat matched the cop's true cell on **3 of 14
turns**, trailing 2–3 steps. The thief fled a ghost and walked into cornerings it
had the data to avoid — the identical trail in all three lost counted sub-games.

Worse, the cop's exact position was already arriving: our police sets
`capture_claim` to its own cell on every move, and the handler used it only to
answer "am I caught". The information was in the message and thrown away.

The same held on the other side and larger: the received scent map's peak *is*
the sender's cell (35/35), while the belief derived from those maps matched
**0/35**. The probabilistic machinery was actively destroying a perfect
observation that arrives every turn.

**Measured effect of closing both channels** — thief survival against a cornering
cop 1/10 → 11/24; police captures 3/16 → 8/16 → **16/16** once the peak was read.

## 5. Trust model

A collapse cannot be argued with later, so it is gated. `ClaimTracker` accepts a
declared or observed cell only when it is reachable from the previously accepted
one within the elapsed steps; the first sighting only anchors, so a single lucky
value cannot steer us; a refusal re-anchors, so a peer we merely mis-tracked
earns trust again on its next consistent step. This assumes physics, not honesty,
and degrades to scent when a peer's declarations do not behave like a position.

## 6. Alternatives considered

- **Trusting any claim outright** → rejected; `capture_claim` is specified as "I
  claim you are at [r,c]", so a conforming peer may legitimately send a *guess*
  rather than its own cell. The continuity gate distinguishes them.
- **Inferring a cell from the concession `reason`** → rejected; it names the
  ending family, not a cell, and that is exactly the loose parse SPEC §3.1 warns
  invents new ways to accuse an honest peer.
- **Wiring `exclude` for the police** → measured and **not** shipped: an oracle
  cop with the thief's true cell captured 2/16 against the blind 3/16, so more
  information bought nothing while the tactics were wrong (`PRD_strategy_brains`
  §4). Revisit only if a future cop is again information-bound.

## 7. Success criteria & tests

Diffusion matches the move set; degenerate mass resets; a credible declaration
pins `most_likely()` to the declared cell; a teleporting one leaves the scent
estimate untouched. Tests: `test_belief`, `test_claim_tracker`,
`test_thief_belief_claims`, `test_scent_peak`.

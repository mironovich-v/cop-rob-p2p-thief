# PRD — Strategy Brains & Legal-Action Seam

> Dedicated PRD (guideline §1.3). **Build stage:** 3 (seam built in 2.4; tactics
> v2 2026-08-18; the measured rewrite of both sides 2026-08-21). Ground truth:
> `CLAUDE.md` §36.4 (strategy seam) + reference repo. Companion PRDs:
> `PRD_belief_map` (what a brain may know), `PRD_game_state` (legality).
> Indexed in `docs/PRD.md`.

## 1. Background

The **move is always pure Python**. The LLM is never consulted for it and can
never keep the game running — it writes optional banter only
(`PRD_llm_verbal_layer`). Legality is computed by deterministic code; a brain
selects only from the legal set it is handed. A brain sees exactly three things:
its own state, the known barriers, and the belief map. It cannot reach the
opponent's truth, by construction.

`BrainBase` is the student seam: override `_pick_move(moves, state, belief)` for
an evader, or `_decide_move(state, belief, barriers_max)` to also spend barriers.
Brains are swapped by config (`strategy.thief_class` / `police_class` =
`"package.module:Class"`), and tactical constants live in a private
`[strategy.tactics]` table — **never** in the signed constitution, since they are
strategy, not terms.

## 2. Requirements (FR-10)

- A brain must return a legal action every turn, within the step deadline, with
  no dependence on network or model availability.
- Ties must break **randomly**: a deterministic evader is pin-able, and a
  deterministic pursuer is walkable. Each sub-game seeds its own RNG so a series
  is reproducible without being six copies of one game.
- Barriers are police-only and finite (`barriers_max`); a brain must never place
  one that strands itself.
- No brain may read opponent truth, and no tactical constant may duplicate a
  signed game parameter.

## 3. Thief — evade by freedom, not by distance

Score each candidate cell as
`freedom_weight × exits + distance_weight × pessimistic_distance − recent_penalty`.

Distance is **pessimistic**: measured to the nearest cell the threat could occupy
*after* its next move, because fleeing its current cell walks into its step.
Freedom (exit count) is what vetoes corners; the recent-trail penalty kills the
oscillation that made v1 pin itself.

**What was actually wrong, and it was not this function.** v1 argmaxed distance
and self-cornered at (6,6) in every counted sub-game. v2 added freedom and killed
the oscillation, yet still lost live. The plausible next theory — that an uncapped
distance term re-enables corner-seeking — was **wrong**: a territory-maximising
evader scored 0/10 and was discarded, while the *shipped* scoring given the cop's
true cell scored 6/10 against a cornering cop it otherwise survived 1/10 against.
The scoring was innocent; belief was guilty (`PRD_belief_map` §4).

## 4. Police — herd, do not chase

A pursuer never closes on an equally fast evader by chasing it, so **distance is
the wrong objective**. The police takes the step that minimises the thief's
`territory` — the cells the thief can reach strictly before we can, breadth-first
from both sides — with distance kept only as a tie-break. Barriers are spent only
to corner: a rule-46 strike on the believed cell when adjacent, or sealing one
exit of an already-pocketed thief, never at random.

The diagnosis order is the reusable lesson. An oracle cop given the thief's true
cell captured **2/16** against the blind **3/16** — so the cop was tactics-bound,
not information-bound, and the obvious belief work would have measured as zero.
Switching to territory took it to **8/16**; only *then* did the oracle jump to
**16/16**, which is what justified reading the scent peak — and that took it to
**16/16 in a median 10 steps**. Fixing belief first would have shown no gain and
been discarded.

## 5. Measuring a brain

A bench is only as good as its adversary. The original A/B bench reported 3/5
thief survival while two independent real opponents captured our thief every
time, because its cop could not corner and therefore could not measure cornering.
The rule this project now follows:

1. Build the adversary that **reproduces the live loss** before theorising. The
   `HerderCop` reproduced it exactly — 1/10, median 10 steps, the same step the
   live opponent captured us on.
2. Run an **oracle** (perfect information, same tactics) to split
   belief-vs-tactics blame *before* tuning anything.
3. Only then change code, and re-measure both sides — an upgrade to shared
   machinery changes the bench's opponents too, so a falling score may mean the
   bench got harder, not that the brain got worse.

Benches drive real runtimes over the transport pair and take minutes; they are
manual measurement tools kept out of CI, with their numbers recorded in
`docs/PROMPTS.md`.

## 6. Alternatives considered

- **Territory-maximising thief** → measured 0/10, discarded.
- **Low distance cap for the thief** → rejected earlier by A/B: the thief stops
  retreating at "safe" range and is walked down.
- **Random barrier placement (v1)** → rejected; barriers are the pursuer's only
  real weapon and spending them randomly wastes the win condition.
- **LLM-chosen moves** → rejected by the assignment and by design: the move path
  must be free, instant, offline, and always legal.

## 7. Success criteria & tests

Every brain returns a legal action for every reachable state; ties are random;
per-sub-game seeding varies play while staying reproducible; the police never
strands itself with a barrier. Current standing: police captures 16/16 against
our own thief; thief survives 11/24 against a cornering cop that lacks the peak
channel. Tests: `test_brains`, `test_tactics`, `test_territory`,
`test_strategy`; benches in the session scratchpad.

**Known limit, stated plainly:** on 7×7 with 14 barriers and 35 steps, a herding
cop with an exact position appears to catch any evader we can write — our thief
survives 0/24 against ours. Expect to win police sub-games and lose thief
sub-games against any opponent that also reads the peak.

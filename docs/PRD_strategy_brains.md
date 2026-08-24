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

## 8. Live falsification — the il-nv-ai counted series (2026-08-24)

Section 7's closing expectation ("expect to win police sub-games … against any
opponent that also reads the peak") is now **falsified by evidence**. The
counted series against il-nv-ai settled 47:47 on six thief survivals out of
six: our police captured nothing in g2/g4/g6, and — the symmetric fact that
reframes the whole question — **their police captured nothing against our
thief either**. In their own words: "neither police ever closed it."

### 8.1 What the sealed logs show

Reconstruction from `results/counted/il-nv-ai-2026-08-24/` (their scent peak is
the sender's exact cell, so the full pursuit geometry is recoverable from our
own artifacts; all three police games are near-identical because both brains
are deterministic):

- The peak channel worked: their maps carried the 0.8 peak on their true cell
  every step (34/34). **Information was never the problem.**
- Our cop closed from distance 5 to **distance 1 within ~8 steps and held
  distance 1 for 17 of 34 steps** — half the game spent adjacent.
- No capture, because distance 1 is a **stable dodge cycle** under this
  ruleset: the thief moves first AND knows our exact cell (we hand it over in
  `capture_claim` every move). From distance 1 it steps away to 2; we close to
  1; repeat. Their endgame was **edge-running** — sliding along a border row
  with our cop shadowing one row inside, reversing at will, answering our
  parity STAY with its own STAY.

### 8.2 Why the bench said 32/32 anyway

The arena's evader is our own and is corner-prone relative to il-nv-ai's
edge-slider; we never built an adversary that dodges indefinitely at distance
1. This is the §5 method rule violated in its second half: we built the
adversary that reproduced the *thief's* live loss (HerderCop), but never the
one that reproduces the *police's* live failure. The bench measured cornering
against an evader that consents to be cornered.

### 8.3 What the Stage-8 rebuild fixed — and what it cost the pursuer

The imreeyal-informed rebuild was evader-side and it worked: STAY plus the
corner-death fix took our thief from caught-in-every-counted-game to 6/6
survivals. But the same change **removed barriers from the cop** ("stop the
pursuer spending walls") because walls measured badly in our arena. Against a
live edge-runner that is exactly backwards: a wall placeable adjacent to the
cop is the **only mechanism that converts a distance-1 shadow into a corner
trap** — shadowing at (1,3) under an edge-runner at (0,3), the wall on (0,2)
or (0,4) is legal and amputates the retreat. We deleted the endgame tool the
live opponents force us to need.

### 8.4 The theory gap, stated precisely

Classic pursuit theory: a 7×7 grid has cop number 1 — with sequential,
fully-informed moves a lone cop *can* force capture, comfortably inside 35
steps. Nothing in this ruleset (thief-first order, STAY on both sides, honest
overlap capture) breaks that. The tie equilibrium the league has converged to
is therefore a **strategy ceiling, not a structural one**: heuristic
distance/territory pursuit does not corner an evader with perfect pursuer
information, on either team's implementation.

### 8.5 The designed (unimplemented) endgame

Keep the herder for midgame — it demonstrably pins the evader to an edge.
Then, on an edge-run trigger (≥N consecutive adjacent-shadow steps along a
border; today's 17-step dodge cycle is trivially detectable):

1. approach from the open side to drive the evader toward the nearer corner;
2. spend barriers on the border cells behind and ahead of it (always adjacent
   to a cop shadowing one row inside) to amputate the reversal;
3. parity STAY only once the retreat is walled.

Prerequisite per §5: first build the **edge-slider adversary** that reproduces
today's 34-step survival against our current cop, then measure the endgame
mode against it. Fourteen walls is far more than one corner trap needs.

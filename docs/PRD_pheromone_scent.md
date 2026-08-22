# PRD — Pheromone / Scent Field

> Dedicated PRD (guideline §1.3). **Build stage:** 4 (built in 2.2/4.x; the
> observation semantics in §5 were established live on 2026-08-21). Ground truth:
> league SPEC §5 + the `pheromone` CORE vector; `CLAUDE.md` §36.2/§36.3;
> reference `domain/smell.py`. Indexed in `docs/PRD.md`.

## 1. Background

Neither peer ever sees the other's position — that is the whole hidden-opponent
model. The only continuous evidence channel is the **scent field**: each peer
lays a radial pheromone deposit on the cell it occupies, and publishes the
resulting map to the opponent every turn as `{"r,c": intensity}`. Positions never
cross the wire; intensities do.

Emission falls off with **Chebyshev** distance over an M×M window
(`falloff = intensity / (half + 1)`, clamped at 0, rounded to 3 decimals), merges
into the trail by **max**, and every game step every known intensity drops by a
fixed decay constant. The result is a decaying breadcrumb trail: strong where the
opponent is now, progressively fainter where it has been.

## 2. Requirements (FR-9)

- Radial M×M emission, Chebyshev falloff, max-merge, per-step uniform decay,
  3-decimal rounding — byte-identical to the `pheromone` CORE vector.
- Only strictly positive intensities cross the wire; a cell that decays to 0
  leaves the map. Sparse maps are legal and must be both emitted and accepted.
- A deposit below `min_center_intensity` is a configuration error and must raise
  rather than silently emit a weaker trail.
- All four parameters (`emit_intensity`, `decay_per_step`, `smell_grid_size`,
  `min_center_intensity`) come from the signed constitution — they are hashed
  terms, so a different value is a different game.

## 3. Constructions & interfaces

`domain.smell.SmellField`: `deposit(center, intensity)`, `absorb(cells)`,
`decay_all()`, `intensity_at(cell)`, `strongest_cell()`, `snapshot()`.

Emission order at send time is **deposit → decay → snapshot** (`runtime._send`),
so the freshest cell is already once-decayed when it ships. This is the "0.8-peak
after-one-decay" form both league partners confirmed.

## 4. What the received map actually tells you

A peer deposits on the cell it is **standing on** immediately before sending, so
the maximum of a received map **is the sender's current cell**. Measured over a
full game: the peak matched the opponent's true position **35/35 turns**, while
the belief estimate derived from those same maps matched **0/35**
(`PRD_belief_map` §4). Reading the peak is therefore not a heuristic — it is the
strongest available observation, and treating the map only as diffuse evidence
discards it.

Two constraints on exploiting this:

- **Parse strictly.** A sparse or foreign map that cannot be read yields *no*
  sighting rather than a guessed one. A mis-read peak does not merely add noise;
  it aims the entire strategy at the wrong cell.
- **Trust only what walks.** A peak is accepted only if it is reachable from the
  previous accepted peak within the elapsed steps. This assumes physics, not
  honesty, and degrades to scent-as-evidence when a peer's map does not behave
  like a moving agent.

## 5. Alternatives considered

- **Manhattan falloff** → rejected; the vector pins Chebyshev, and a different
  metric is a different game.
- **Additive merge of overlapping deposits** → rejected; max-merge is the pinned
  construction and keeps intensities bounded by `emit_intensity`.
- **Emitting a position field directly** → rejected; it would collapse the
  hidden-opponent model the whole design rests on.
- **Treating the map purely as a Bayesian likelihood** (what we shipped
  originally) → rejected on evidence: it demonstrably destroys an exact
  observation (§4).

## 6. Success criteria & tests

The `pheromone` CORE vector reproduces from our production functions with zero
drift. A sub-decay deposit raises. Sparse maps round-trip. The peak of a received
map equals the sender's cell for a conforming peer, and an unreadable map yields
no sighting. Tests: `test_smell`, `tests/conformance` `pheromone`,
`test_scent_peak` (peak extraction, malformed keys, empty and zero-intensity
maps).

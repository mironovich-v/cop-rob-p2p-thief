# Decisions — ADRs & Resolved Contradictions

> Architectural Decision Records for the vm__fabi Cop-Thief P2P project. Each ADR:
> context → decision → rationale → alternatives → status. ADR-2..ADR-6 are the
> resolved book/kit contradictions the assignment requires us to name and justify.
> Authority order: book v3.0.0 → league SPEC (for listed interop surfaces) →
> reference code v3.0.0. Confirmed facts in `CLAUDE.md` §36.

## ADR-1 — Reference implementation as practical ground truth
**Context:** the authoritative book PDF is Hebrew; its text layer is not
machine-readable (RTL scrambling). **Decision:** treat the lecturer's reference
repo (`../Game-P2P-Cop-Chase`, v3.0.0) + the league SPEC/vectors as the practical
ground truth; the binding parameter table (App. F) is cross-checked from the
numbers, which survive extraction. **Rationale:** the reference matches the SPEC
byte-for-byte; it is executable and unambiguous. **Alternatives:** translate the
PDF (rejected — lossy). **Status:** accepted.

## ADR-2 — Commit-reveal preimage = reference form  *(contradiction)*
**Context:** the book prints three inconsistent commit constructions (nonce
inside the JSON; `f"{nonce}|{move}"`; `SHA256(canonical|nonce)`).
**Decision:** use `SHA256(canonical_json(payload) + "|" + nonce)` (nonce
pipe-appended), per `domain/crypto.py` and SPEC §3. **Rationale:** it is what the
lecturer's tooling runs and the only cryptographically sufficient form (binds
state+intent); audit is cross-team so both sides must match. **Alternatives:** the
other two forms (rejected). **Status:** accepted.

## ADR-3 — Pheromone model = `subtractive_chebyshev_v1`  *(contradiction)*
**Context:** book prose gives multiplicative decay + Gaussian falloff; the
reference implements subtractive decay + linear Chebyshev falloff.
**Decision:** implement the reference/CORE model (`falloff = intensity/(half+1)`,
round-3, subtractive), per SPEC §5. **Rationale:** it is the pinned CORE vector;
scent maps are transmitted (not re-derived cross-team), but we match the reference
for belief-map fidelity. **Alternatives:** `multiplicative_book_v1` — only if a
partner explicitly locks it via a signed locked-model doc. **Status:** accepted.

## ADR-4 — Report consensus signature = spaced serializer  *(contradiction)*
**Context:** every other hash uses compact canonical JSON, but the report
consensus signature is different. **Decision:** serialize the report with
`json.dumps(report, sort_keys=True, ensure_ascii=False)` (default/spaced
separators), sign-then-insert under key `חתימת_קונסנזוס_משותפת`; verify = pop key,
re-serialize spaced, re-hash. Per `report_writer.py` + SPEC §6. **Rationale:** it
is what the lecturer's tooling computes; using the compact form here fails
settlement. **Alternatives:** compact form (rejected). **Status:** accepted.

## ADR-5 — `num_games`: signed config governs; league series = 6  *(contradiction)*
**Context:** the config default is `num_games=1` (demo) but App. F fixes a
6-sub-game series. **Decision:** the signed `game.json` `num_games` governs a
given match; counted league play uses 6 with role alternation. **Rationale:** both
peers sign the config; 1 is only a single-game demo. **Alternatives:** hard-wire 6
(rejected — it is a signed term). **Status:** accepted.

## ADR-6 — Emailed body = exact hashed canonical bytes  *(contradiction)*
**Context:** the reference `email_sender.py` sends the report as
`json.dumps(..., indent=2)`, but SPEC §6 requires the emailed body to equal the
exact canonical bytes that were hashed. **Decision:** email the exact
report-consensus bytes (spaced canonical form), never a pretty-printed
re-serialization. **Rationale:** the grader compares emails; EX06 teams lost
points for re-serializing. **Alternatives:** follow the reference `indent=2`
(rejected — violates the interop rule). **Status:** accepted (stricter than ref).

## ADR-7 — Package layout: shared core + role packages
**Context:** the reference is one `police_thief` package run with `--role`; the
assignment recommends a shared core + role packages. **Decision:**
`src/cop_thief_core` (role-agnostic) + `src/police_agent` + `src/thief_agent`
entry points. **Rationale:** best fit for the mandated two-repo export from one
canonical core; keeps role behavior injected. **Alternatives:** single package +
`--role` (rejected — worse export story). **Status:** accepted.

## ADR-8 — Python 3.13
**Decision:** target Python 3.13. **Rationale:** matches the reference's idioms
(`StrEnum`, modern typing) and its `requires-python`. **Alternatives:** 3.10 floor
(guideline default) — unnecessary friction. **Status:** accepted.

## ADR-9 — League kit external, not vendored  *(owner decision)*
**Context:** `copthief-league-protocol` is owned by another team and may update.
**Decision:** keep it git-ignored (not vendored); record the upstream URL +
`scripts/fetch_interop.sh` in `docs/INTEROP.md`; conformance tests read its
vectors but run our functions. **Rationale:** owner wants updates to flow without
hardcoding files. **Alternatives:** vendor (rejected — freezes another team's
repo); submodule (rejected — pin friction + export complexity). **Status:**
accepted (owner).

## ADR-10 — Three-repo topology; export from one core
**Decision:** workspace repo `cop-rob-p2p` (canonical core + PR dev) →
`scripts/export_repos.py` generates `cop-rob-p2p-police` and `cop-rob-p2p-thief`
(self-contained, vendored core snapshot, cross-linked, drift check).
**Rationale:** satisfies "two submission repos" + "one canonical core, no manual
duplication." **Status:** accepted.

## ADR-11 — PRD catalog is per-mechanism (19), not the 7 build stages
**Context:** the book's Ch.10 defines seven build *stages*; guideline §1.3 +
assignment §3 require a PRD per *mechanism*. **Decision:** stages live in
PLAN/TODO; 19 mechanism PRDs (indexed in `docs/PRD.md`). **Rationale:** matches
the "dedicated PRD per algorithm/mechanism" rule and "at minimum" wording.
**Status:** accepted.

## ADR-12 — LLM for verbal layer only; move is pure Python
**Decision:** default trash-talk provider = `template` (0 tokens); the game move
is always pure Python. LLM-driven *moves* are allowed only if both peers agree in
advance during negotiation. **Rationale:** book rule; keeps matches fair, fast,
free, offline-testable. **Status:** accepted.

## ADR-13 — Config: per-role dirs, signed `game.json` + private `game.toml`
**Decision:** `config/<role>/` holds private `game.toml` + signed shared
`game.json` (schema 1.3) + `rate_limits.json`; load via `CFG`; validate against
App. F minimums; never hard-code. **Rationale:** matches the reference model and
the signed-constitution requirement. **Status:** accepted.

## ADR-14 — One-time direct-to-main bootstrap
**Context:** the empty repo had no `main`, so a branch→PR could not be based.
**Decision:** owner authorized one direct commit to `main` to seed the repo;
all subsequent work uses branch → PR → squash-merge. **Rationale:** conventional
repo seed, not a review bypass. **Status:** accepted (one-time).

## ADR-15 — Public tunnel provider (tentative)
**Decision:** default to a Cloudflare named tunnel (`originRequest.httpHostHeader`
per SPEC App. D); ngrok documented as the alternative. **Rationale:** stable named
URL for scheduled matches. **Status:** proposed — confirm at Stage 5.

## ADR-16 — Build belief/brains/smell before the runtime (Option A)
**Context:** the orchestrator/runtime (tasks 2.5/2.6) integrates the belief map,
strategy brains, and scent field — pure-domain pieces the TODO scheduled in
Stages 3–4, *after* the runtime. **Decision:** reorder to dependency order —
build belief (3.1), brains (3.2), and smell (4.1) first, then write the runtime
once, integrating them. **Rationale:** avoids rewriting the turn loop to add
belief/scent later; lets the runtime be tested end-to-end with real capture and
settlement. **Alternatives:** a minimal runtime now (trivial move policy, no
belief/scent) enriched later — rejected (rework). **Status:** accepted (owner
approved 2026-07-23).

## ADR-17 — Tie rule: `series_add`, declared per pairing
**Context:** the league surfaced three live readings of where App. F's tie
score (2) lands (kit WARNINGS §6a): `series_add` (kit + all current league
teams), `series_replace`, `per_subgame` (the reference). Course staff ruled it
a genuine contradiction under the academic-freedom clause. **Decision:** keep
our existing behavior — `series_add` (`domain/scoring.py` already adds
`tie_score` into each `total_score` on a series tie, on top of per-row tie
scores) — and DECLARE `tie_rule: series_add` in the first-contact constitution,
beside the scent model. **Rationale:** matches the kit default and every team
played so far; the mismatch only surfaces in a counted series that ties, where
it becomes a rule-35 contradiction. **Status:** accepted (2026-08-17).

## ADR-18 — Turn order is declared out-of-band, never assumed
**Context:** thief-moves-first is the reference's observed behavior, NOT
covered by the `wire_shape` lock or any signed term — two peers matching on
every hash can still deadlock silently (kit SPEC §7, playbook connection
contract). **Decision:** we play thief-first (unchanged) and STATE it
explicitly in every first-contact message. **Status:** accepted (2026-08-17).

## ADR-19 — Consensus scope: the reference 5-key row (kit #55 concurrence)
**Context:** kit #55 (2026-08-13) reverted a 2026-08-04 error that added a
sixth key (`tie`) to the consensus-signature row scope; every hash ever
settled live reproduces only under the 5-key row. **Decision:** no change —
our `reporting/emit.py::_symmetric` was built from the reference's
`symmetric_outcome` and always kept exactly `{sub_game_number, roles, result,
winner_group, score}`; the document row keeps `tie`, the hash row never had
it. Recorded so nobody "fixes" us toward the withdrawn 6-key form.
**Status:** accepted (2026-08-17).

## ADR-20 — Email gate: dry-run + structural recipient gate (draft mode removed)
**Context:** rule 30 grants a **send-only** Gmail scope, which cannot create
drafts — our draft-default safety gate depended on a broader permission than
the rules allow (kit WARNINGS §6; the same contradiction anrbj666's audit
caught in the kit's own docs). **Decision:** replace `email.mode="draft"` with
`dry_run` (build + log the exact MIME, transport untouched) and make the gate
recipient-shaped: the lecturer's address is structurally unreachable — matched
case-/whitespace-insensitively, including inside recipient lists — unless the
run is doubly armed (config `counted=true` AND CLI `--counted`); an armed run
that cannot deliver its report refuses to start. Disabled-default stays.
**Alternatives:** keep drafts under the broader `gmail.compose` scope —
rejected (documented deviation from rule 30 for no benefit). **Supersedes:**
the draft-default requirement in `PRD_email_reporting.md` §3/AC-E4.
**Status:** accepted (owner approved 2026-08-17); implementation in task 8.8.

## ADR-21 — The mail IS the result artifact (result-only mail, SPEC §6.1)
**Context:** the nis-yar1 friendly's report-compare revealed our auto-fired
mail carried the Hebrew book-schema report (`build_report`) — the REFERENCE's
reading of §9.3.3 — while the league's settled convention (kit SPEC §6.1,
proven across every counted pairing) mails the RESULT ARTIFACT: "the result
JSON as the body and the same file as the single named attachment"; the book's
prose-vs-template tension was resolved by both league teams toward the results
file. Our attachment was even NAMED result_<game_id>.json while carrying the
Hebrew doc. **Decision:** the mail body = the exact bytes filed as
`result_<game_id>.json` (indent-2, ensure_ascii=False — byte-equal to the
repo-published artifact), same bytes attached. The Hebrew report remains a
repo artifact, never mailed. **Supersedes:** the emailed-body clause of ADR-5/
§36.3.4 (which pinned the SERIALIZER of the consensus signature — unchanged —
but predated the league's settlement of the mail CONTENT).
**Status:** accepted (2026-08-18, before any counted mail reached the grader).


## ADR-22 — Delegate publishing of the generated submission repos
**Context:** the two submission repos are generated build artifacts of this
workspace (ADR-10); every byte in them is reviewed HERE before export. The
owner does not want to run the init/remote/push mechanics by hand, and the
existing GitHub credential already covers all three repos. **Decision:** Claude
may export and push the `dist/<role>-agent` trees to the two submission repos'
`main` (scope in CLAUDE.md §2.2): no force-push, no deletions, no tags; every
push reports the source workspace commit. Rationale: the review gate is the
workspace PR that produced the exported content — pushing the artifact adds no
unreviewed material. **Status:** accepted (owner approves by merging this PR).


## ADR-23 — Mirror the development history into the submission repos
**Context:** the book (source of truth, read directly from
`instructions/police_thief_p2p.pdf` on 2026-08-19) fixes the submission as two
repos with mandated CONTENTS (rule 50: README/config/PRD/PLAN/TODO — documents,
not history) and cross-links (rule 49), but p.156 requires the per-game played
COMMIT to be checkable in GitHub, and p.96 phrases development as happening "in
two separate repositories". Our played commits live in the canonical workspace
(ADR-10 topology, which the lecturer's own mono-repo reference and his
brief's "one canonical source, generated release repositories" language
support). **Decision:** push the workspace `main` into BOTH submission repos as
branch `workspace-history` (fast-forward updates on each republish; never
rewritten): every declared match commit resolves inside the submitted repos,
the examiner gets the full 70+-PR record without leaving them, and any strict
reading of p.96 is satisfied — the development history is IN the submitted
repos. Owner extended the ADR-22 delegation to cover this branch (2026-08-19).
**Status:** accepted.

## ADR-24 — Separation is at the PROCESS level; two repos are the submission form
**Context:** the book was re-read directly from `instructions/police_thief_p2p.pdf`
on 2026-08-22 (160 pp., Hebrew visual-order text reversed per line) to answer one
question honestly: *is each role required to be RUN from its own repository?*
The binding rules table and §2.4.2 (p. 31) settle it.

- **Rule 1** (sanction: *total failure*) — run thief and police code in two
  completely separate **processes** (`תהליכים`), under separate config
  directories. §2.4.2 states the rationale: the hazard is *local development* on
  one machine; in the league the peers are on different machines anyway.
- **Rule 2** (sanction: *immediate disqualification*) — never share memory or
  variables; §2.4.2 forbids *"importing a shared module that holds live state"*.
- **Rule 49** — **submit** (`מגישים`) two separate cross-linked repos.
- **Rule 50** — each repo carries README/config/PRD/PLAN/TODO, whose stated
  purpose is *"to let the examiner reconstruct the way of working"*.

**Finding:** no rule requires a game to be *run from* a submission repository.
The mandatory separation is of **processes and live state**; two repositories are
the mandated **submission form**, not a mandated development topology.

**Decision:** keep the ADR-10 topology. Run `police_agent` and `thief_agent` as
two independent OS processes with separate config dirs, ports, logs and private
state (rule 1), sharing no live state (rule 2); submit two generated,
self-contained, cross-linked repos (rules 49–50); regenerate and push them after
every merge to `main` (workflow step 10) so they never lag the code that plays.

**Rationale for not developing in two repos** — ch. 9.4 (p. 96) *describes*
development as happening "in two separate repositories", while binding rule 49
says *submit*. Two independently developed codebases would duplicate the domain,
interop, protocol, orchestration and audit layers, which the engineering
guideline forbids ("never manually duplicate shared modules") and which would
turn byte-exact interoperability between our own agents into luck. The lecturer's
reference implementation is itself a single mono-repo playing both roles. The
`workspace-history` mirror (ADR-23) puts the complete development record inside
both submitted repos, which is what rule 50's stated purpose asks for.

**Reported where a grader will read it:** the academic `README.md` carries this
with the citations, and it is exported into both submission repos.
**Status:** accepted.

## ADR-25 — The evader may STAY; the pursuer spends no barriers

**Status:** accepted 2026-08-24, after losing the imreeyal counted series 90–30
(0–6 sub-games) and receiving their post-league strategy debrief.

**Context.** Three counted series, three losses, and the same two shapes every
time: our cop chased for the full 35-step horizon without converting, and our
thief was captured in 11–20 steps, always on an edge.

Reconstructing counted sub-game 2 from our own sealed log and the scent peaks in
their turn messages settled the thief half beyond argument:

| step | our cell | their cop | distance |
|------|----------|-----------|----------|
| 8    | (4,6)    | (3,5)     | 2 — safe |
| 9    | (5,6)    | (4,5)     | 2 — safe |
| 10   | (6,6)    | (5,5)     | 2 — safe, cornered |
| 11   | (6,5)    | (6,5)     | 0 — CAPTURED |

At step 10 we stood in the corner (6,6). Our options were (6,6) — distance 2,
**safe** — and (5,6) and (6,5), both inside the cop's reach. `_decide_move`
offered only `board.legal_moves`, so HOLD was never in the option set, although
STAY is a signed term of the agreed move set and our own police already used it
to break a parity lock. A cornered evader was **forced** to step into the
pursuer's reach. That is exactly the containment imreeyal described ("every cell
your rule can pick is within our reach"); it worked because our rule could not
pick the safe one.

**Decision.**

1. **STAY is in the evader's option set.** Plus room (BFS territory) instead of
   exit count, a flight floor inside which distance beats room, and a
   lag-robust second safety key in case the believed cell is a move old.
2. **The pursuer scores `escapes`** — how many of the evader's replies land
   outside the cop's next reach — with room as the tie-break, not the goal.
3. **The pursuer spends no barriers by default** (`spend_barriers = False`).

**Why (3), which is the surprising one.** A barrier costs the cop its move and
may only be placed on a cell adjacent to the cop — a cell the cop could simply
step onto. A wall can therefore never capture anything a step could not capture
more cheaply, while the pocket-seal trigger fires repeatedly and spends the
tempo that would have closed the distance. Measured over 32 seeds per arm:

| evader     | with 14 walls | walls off |
|------------|---------------|-----------|
| greedy-run | 0/32, med 35  | 32/32, med 17 |
| territory  | 0/32, med 35  | 32/32, med 15 |
| doctrine   | 0/32, med 35  | 32/32, med 15 |
| random     | 29/32         | 32/32 |

Live corroboration: our cop burned 5–9 walls per window and converted nothing;
imreeyal's used **zero** and won three. Two wall heuristics from their §2 fix 1
were tested and refused by measurement — territory-based `wall_gain` is
identically zero over 840 turns (a wall beside the cop lies in the cop's own
Voronoi region and cannot shrink the thief's), and sealing an escape is
impossible for the same reason. Using 0 of 14 barriers is legal: `max_barriers`
is a ceiling, not a quota. The capability is kept behind a tunable, not deleted.

**Consequences.** Measured on 96 unseen seeds per arm, both belief lags: the cop
captures **100%** of every competent evader arm (previously 0%), and the evader
is caught **0/288** across every pursuer arm and lag (previously up to 91/96).
Neither brain regresses on any arm — the champion gate imreeyal recommended
(§4) now runs in the unit suite as `tests/unit/test_arena_gate.py`.

**Rejected.** Stochastic top-k selection (their §1 fix 3). It is the right idea
against an opponent that models us as a function, but measured here it made the
evader strictly worse (384/512 caught against 365 for the shipped brain) because
randomising past the best option breaks the safety ordering. Recorded rather
than silently dropped; revisit if an opponent starts predicting us.

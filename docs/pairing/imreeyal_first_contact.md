# Pairing: imreeyal — first contact (received 2026-08-17)

Verbatim first-contact message from team **imreeyal** (Imree Cohen, Eyal
Shtinmetz), received by the owner on 2026-08-17. They propose 1–2 uncounted
friendlies then exactly one counted series **before the 20/08 deadline**.

Our disposition map is at the bottom; the message itself is preserved
unmodified between the markers.

---

<!-- BEGIN VERBATIM MESSAGE (imreeyal, 2026-08-17) -->

Hi — we're imreeyal (cop repo + thief repo, group_id `imreeyal`), and we'd like to set up
**one or two uncounted friendlies and then exactly one counted series** with you before the
20/08 deadline. We've completed five counted series so far (vs anrbj666, uoh-sqak, vibecode,
nis-yar1 and najamjad) and have been through every way a window can burn, so this message is
long on purpose: it is everything that has ever cost us or an opponent a window, spelled out
in advance. Teams that ran the checklist below have gotten from "never spoken" to a clean
counted series in two evenings — the most recent pairing did it in one.

## 0. Before we book a window: the self-serve pass (saves both of us a burned evening)

Everything in this section runs on your machine alone, tonight, with nobody coordinating:

1. **Pull the conformance kit fresh** — <https://github.com/Imreec/copthief-league-protocol>,
   current `main`. If you cloned it before ~Aug 5, pull again: the sparring peer had real
   defects (police-first turn order, empty timestamps, a held MCP session) that were found by
   live dogfooding and are fixed on main. An old clone will "fail" you on things that are
   actually fine.
2. **Run `python verify_vectors.py`** — all CORE vectors green. CORE is byte-for-byte the
   official reference implementation; if a vector is red, that construction will fail against
   every team in the league, not just us.
3. **Play a full series against the kit's sparring peer.** Both sides need `--peer` (a peer
   started without it accepts greetings into a queue nobody drains — documented in the module):

   ```
   python -m sparring.cli serve --port 8931 --peer http://127.0.0.1:<your-port>/mcp \
     --role thief --artifacts <scratch>
   ```

   Target: **6/6 sub-games settled, every mutual audit "Verified OK" in both directions, one
   `game_uid` across all artifacts.** Note sparring's default `setting` is `"Haifa"` — align
   your throwaway config to its defaults for this test; the byte-identical constitution with
   us comes later (§3.1).
4. **Run `tools/check_artifacts.py <yours> <sparring's> --terms <flat terms>`** until it says
   `ALL SETS AGREE`. This is the cross-team join no single team can test alone — it is exactly
   the check that decides whether two teams' emailed reports will reconcile or contradict, and
   rule 35 zeroes **both** teams on a contradiction.

If all four pass, our first friendly is usually about config alignment and tunnel weather, not
protocol. Two honest caveats: the sparring peer is close to our live peer but not identical —
our peer is **stricter** in a few places, and section 3 below is the authoritative list for
playing *us*; sparring passing does not waive it. And know what your sparring pass does NOT
test: **the path where the OPPONENT initiates each sub-game's handshake against your standing
process.** Every self-test can go 6/6 with your runner driving while the answering path has
never once run — a recent pairing proved exactly that, three aborted evenings deep. If you can,
drive a second series AT your own standing process and watch sub-game 2 specifically.

## 1. What we need from you (fill in and send back)

```
group_id:              (short, lowercase, stable - it names files on BOTH sides)
group_name:
members:               (full names, as they should appear in the declaration)
repo URL (cop):
repo URL (thief):
MCP endpoint - your POLICE service:
MCP endpoint - your THIEF service:     (same URL twice if you run one process)
llm_model:             (exact string you declare; "none"/"template" if no LLM)

email you'll send the report FROM:
email(s) that should RECEIVE our friendly report:

counted series you've already played:  (how many, against which group_ids)

timezone + two or three time windows in the next two days
```

Two notes on this block:

- **The `group_id` you write here is binding on the wire.** We configure the opponent we are
  playing, and our handshake **refuses an agreement from any other group** — a guard added
  after a live incident where a stray peer from a different pairing answered a greeting. Make
  sure the `identity.group_id` your `negotiate` sends is byte-identical to what you write here.
- **Why repo URLs, given everyone's repos are private?** They are mandated artifact fields
  read by the lecturer, not by us: the pre-game declaration and the result's `links.github`
  carry *both* teams' repos, so each side's artifacts need the other's column filled. We read
  them from your `negotiate` identity block automatically — the reason to also send them in
  writing is that a previous opponent's identity block arrived empty for several windows and
  both teams shipped blank opponent columns without noticing. Commit hashes we exchange on
  counted day, in writing, on clean trees — the sealed step-0 record binds them during play.

## 2. Our details

```
group_id:     imreeyal
group_name:   ImreEyal-Police
members:      Imree Cohen, Eyal Shtinmetz
repos:        https://github.com/Imreec/copthief-p2p-cop
              https://github.com/Imreec/copthief-p2p-thief
MCP police:   https://cop.imreeyal.com/mcp
MCP thief:    https://thief.imreeyal.com/mcp
llm_model:    none        (all moves are pure Python - App E rule 25)
report from:  imreeyal.copthief@gmail.com
report to us: imreeyal.copthief@gmail.com, imree.c@gmail.com

counted series played so far: 5 (anrbj666, uoh-sqak, vibecode, nis-yar1, najamjad)
```

Both our hostnames terminate on one process, so you may dial either for either role; we still
ask for your two URLs separately because a role-split opponent is a case that broke us once.

## 3. The interop points — every one of these has burned a real window for someone

This is the dialect the league currently plays: five pairings (anrbj666, uoh-sqak, vibecode,
nis-yar1, najamjad) each completed full counted series on it, and best2934 adopted the same
pinned tool surface for their build. None of it is our invention — each item is either pinned
in the kit, observed live against the official reference, or the named cause of a lost
window. Adopting the list as-is means your first friendly against **six** current teams is
protocol-silent. To be direct about the
ground rule: this side of the wire is proven in two completed counted series, so with the
deadline this close **we won't be changing our side** — if an item is genuinely impossible
for you, flag it in writing before the T and we'll talk, but the safe default is to match
the proven configuration rather than have both sides change at once.

**3.1 Constitution.** Byte-identical `game.json` both sides (the signature is over a flat
extraction of it). Ours is at the bottom — note `pheromone_min_center_intensity: 0.5` is
written out explicitly (it is a SIGNED term; earlier copies of this message left it to the
default and it became the first question of two separate pairings). Set `agreed_between` to
the sorted pair `["<your group_id>", "imreeyal"]` — same strings, same order, both sides. We
emit `schema_version: "1.2"`; tell us if yours differs (not load-bearing, we just don't want
a cosmetic mismatch in front of a grader).

**3.2 The THIEF takes the first turn of every sub-game.** Observed live against the official
reference during our oracle spike — not an assumption. The wire-shape lock says nothing about
turn order, so two peers can complete a perfect handshake, agree on every hash, and then both
sit waiting: silent mutual deadlock, both time out, both blame the other — the exact rule-35
contradictory-report shape. Please confirm this one explicitly.

**3.3 `timestamp` is a non-empty ISO-8601 string on every turn message.** We refuse an empty
one at validation, before any state change — an empty stamp means every turn you send is
refused. It's typically a one-line fix on the sending side.

**3.4 Fresh MCP session per sub-game — and this means DROPPING your outbound session at
every boundary, not just resetting game state.** The most recent pairing lost two whole
evenings to this exact seam, so it gets four lines instead of one:

- **Drop the outbound MCP session/socket before each sub-game's handshake.** Our runner
  starts a fresh process per sub-game; a client that keeps its socket from sub-game N dials
  a corpse in sub-game N+1 — every call times out while a fresh curl to the same URL reads a
  healthy 406. "Fresh session at the inbox level" is not enough; the dialler must reconnect.
- **Between sub-games our door legitimately reads 502 for about two minutes** while the next
  process binds. That is normal, not a failure: give your per-sub-game handshake patience
  that spans it, treat our ARRIVING negotiate as the sub-game opener, and never burn a
  sub-game on dial-out timeouts against the gap.
- **Bind your expected-sender/role guard from role parity at the START of each sub-game,
  before the handshake returns.** Our opener fires the instant the handshake completes; a
  guard re-bound one beat late has rejected it as "unauthorised sender" live, deterministically,
  on every even sub-game.
- Related, for hand-testing: FastMCP endpoints want **one persistent TLS socket** per
  session — a curl-per-call probe gets "Session not found".

**3.5 A per-call timeout, strictly below the signed `response_timeout_sec` (30s).** This one
is our newest scar and we'd genuinely urge you to adopt it: the MCP Python SDK's default
per-call timeout is 30s, so one delivered-but-unanswered push, one 0.5s retry sleep, and a
second push is 61 seconds — you can breach a signed 30s deadline while every individual call
looks fine. We cap every outbound call at 10s and refuse to load a config where the cap isn't
strictly under the signed deadline. It cost us two sub-games to learn this.

**3.6 Step numbering is per-sender and starts at 1** — you count your turns 1,2,3…, we count
ours 1,2,3…. A single global interleaved counter (1,3,5…) looks like a reordered stream to our
receiver and fails as a timeout minutes later, hiding the real cause.

**3.7 MCP tool and argument names.** Four tools; note `submit_audit`'s argument name differs:

```
negotiate(message: dict)        receive_turn(message: dict)
submit_audit(payload: dict)     receive_control(message: dict)
```

A `payload`/`message` mix-up cost a whole window once. Pinned in the kit
(`vectors/turn_message.json`, SPEC §7.5).

**3.8 `negotiate` payload.** We send and expect:

```
terms, nonce, signature, identity{...}, sub_game_number, role,
scent_model_sha256, info_mode_sha256, game_uid
```

`sub_game_number` and `role` (`"police"`/`"thief"`) stop the two nastiest failures we've hit:
one game carrying two sub-game indices, and both peers taking the same role. We refuse on a
contradiction, but **omission never refuses** — if you don't send them we play on and just
lose the guard. Please send them.

One identity field with rule-38 weight: carry **`counted_games_played` (integer, counted
series you've completed)** in your `negotiate` identity, under exactly that key. Our result
artifact's `games_played_including_this` reads it; a differently spelled key silently reads
as 0 and your declared count comes out understated in OUR filed report — caught live in a
friendly, worth one line in your identity block forever.

**3.9 `TurnMessage` is exactly these ten keys**, unset optionals as explicit nulls:

```
step, sender, hint, smell_grid, commit, timestamp,
barrier_placed, capture_claim, claim_response, win_claim
```

We tolerate and ignore unknown inbound keys; the reference crashes on them, so we never emit
any.

**3.10 `submit_audit`:** `sender`, `result_claim`, `records` — each record
`{payload: object, nonce: hex string, commit: 64-char lowercase hex}`. One thing to know
about our auditor: it binds each disclosed record to the commit that **arrived live** during
play, not only to the one inside the record — a record rewritten and re-sealed after the fact
is self-consistent but won't match what crossed the wire. (Both other active teams implement
the same check now; it originated from a gal-roy1 report on the kit tracker.)

**3.11 `game_uid` derives from the FLAT negotiated terms**, never from your whole
`game.json`: `uuid(sha256(canonical_json(terms) + "|" + "|".join(sorted([a, b])))[:16])`.
Kit-pinned. Worth double-checking because the uid never crosses the wire during play — two
teams once played an entire series under two different uids and found out at report time. We
also declare it in `negotiate` and refuse a mismatch at T+seconds instead (omission never
refuses — but send it and the whole class dies at the handshake).

**3.12 Named models — both-declare-and-differ refuses; omission never refuses.** Recompute
these from the kit yourself rather than trusting a paste:

```
scent_model:subtractive_chebyshev_v1  81ebee59640e80eae8ca9ee5f86abd26e7edf5cdbb27d15925cb6ee45ca6ddf4
scent_model:multiplicative_book_v1    934c220d5bf62acaa3297c6c9d723ea954c220260b02292ca17f6d5daef9f4d9
wire_shape:reference-v3               229ae6487a418c3fcb6da9be404de2f2533c288ebc228811bff6dedc4164d6f7
info_mode:belief                      020947daeeb3f73494af9b04201326791742c7184085456e3517d21981ee1202
```

**We propose `subtractive_chebyshev_v1`** — the reference default and the kit's CORE vectors,
so it is almost certainly what you already run. Wire shape is `reference-v3`: positions hidden
during play, moves revealed only at the end-of-game audit — not the per-step-reveal variant.
Both sides declaring the same model is what matters; *undeclared* differing physics is the
worst case, because it plays and then the audits disagree.

**3.13 Scent snapshot on the wire — answer in writing, and please match the majority.** The
locked scent doc's example carries two field snapshots (`emit_field` 0.9/0.6/0.3 and
`after_one_decay` 0.8/0.5/0.2) and does not pin which one crosses the wire — both readings
exist in the league, so this is a pairing convention, not law. Ours is the **0.8-peak
after-one-decay** form, and it is what the league majority transmits (our five completed
counted pairings all played on it — or declared the difference in writing when they did not).
Tell us which yours sends; if it is the 0.9 form and switching is a config-level choice on
your side, we ask you to switch for this pairing — one declared form both ways is strictly
simpler for both teams' checks and both teams' graders. If you cannot switch, say so and we
declare the divergence in writing before anything counted. Also state the **extent**: we
transmit every strictly-positive cell of the full accumulated trail (not just the 5×5
emission window), `"row,col"` keys, values rounded to 3 decimals. (A mismatch here cannot
burn a window against us — our scent check logs, it never refuses a game.)

**3.14 Rules 46–47 — capture by enclosure.** A barrier on the thief's cell is a capture, and
a thief left with no legal move is captured. Our thief self-checks and concedes. If yours
doesn't, it will play to step 35 and claim a survival our audit scores as a capture — two
honest teams, two contradictory reports.

**3.15 Transport tolerance.** Retries mean a message can arrive twice or one step out of
order. We dedup on the **commit** (the one field a retry cannot vary), tolerate one step of
reorder, and junk never resets a deadline. Transport tolerance, no rules tolerance.

**3.16 Timing (ours, for reference):** turn timeout 180s, connect/handshake 60s, handshake
re-pushed periodically until the game starts (so a greeting landing in your *previous*
sub-game's dying peer doesn't strand the window). Silence past the turn timeout is a
technical loss. See 3.4 for the inter-sub-game gap your patience must span.

**3.17 Two per-side conventions to DECLARE, not align.** (a) Our log summary's `steps` counts
our **own** moves; some teams count rounds — the values legitimately differ by one and the
field is outside every hash. (b) Our result artifact follows the course's own template
exactly — sub-game rows field-for-field, no extra keys. If your fields differ per-side, we
just declare both conventions in writing before the counted game so neither team's grader
sees an unexplained mismatch. Don't add fields beyond the course template to the result —
the grader's template is the authority, even where the kit's example file carries extras.
**But don't omit the template's own fields either**: `final_result` carries three league
fields — `games_played_including_this`, `first_meeting_between_groups`,
`diversity_reward_applied` — and a recent pairing shipped without all three, having read
"template-clean" as minimalism. Emit them. `diversity_reward_applied` is DERIVED, not
claimed: `counted AND first meeting AND this group won`, so both files mark the winner true
whichever team it is — all-false-out-of-modesty makes the two filings visibly disagree on a
+10 line. And `tokens_total_series` is own-spend-plus-zero-for-opponent on both sides: the
token columns legitimately differ, everything else in `final_result` must not.

## 4. Series shape and parity

Six sub-games (`num_games` fixed at 6 by App F), sequential, roles alternating 3/3. State
back explicitly, in words: **who plays police in sub-game 1?** Our runner's natural role
plays the odd sub-games (1,3,5). The handshake refuses a role collision, but the refusal
costs the window — words are cheaper.

## 5. The T protocol (this is what makes live windows actually work)

1. We name an exact minute — the **T** — e.g. `21:30:00` Israel time.
2. Both sides bring everything up **before** T and hold.
3. At T both fire, and both curl the other's endpoints. A ready MCP endpoint answers **406**
   to a bare GET; **502** means the edge is up with nothing behind it; a tunnel error page
   means the tunnel itself is down.
4. Any required endpoint not 406 by T+30s: kill everything, name a new T. **Never debug
   inside a window** — a half-started series leaves orphan processes that play a *later*
   window and corrupt both teams' records. We learned this the expensive way.
5. Before the T, both sides state the series shape back in one sentence ("six windows,
   odd/even split, both runners") — a misread window shape wasted an evening once.
6. After the series: both sides check for stray processes.

Please also confirm your report **auto-fires at settlement** rather than a human sending it —
App E rule 32 requires it, and rule 35 zeroes both teams if one report is missing. And one
hard gate we now apply to every pairing, learned the polite way: **before any counted series,
one friendly's report must arrive in OUR inbox from YOUR filer, auto-fired at settlement with
no human in the loop** (point your friendly/practice recipient at us for that run). A
described mail path is a claim; a mail in our inbox is a measurement — and rule 35 makes your
mail path our risk exactly as much as yours. Your own Sent-mail copy does not substitute: it
would be you checking your own homework.

One more thing: our peer only accepts a handshake from the one team it is configured to play,
so **please only dial us inside a window we agreed in writing** — a greeting outside your
window is refused automatically, and the refusal is not a bug on either side.

## 6. Reports — where rule 35 actually bites

- One result email per series per team. Friendly: to each other only, **never the lecturer**.
  Counted: to the lecturer alone.
- **Mail shape:** the body IS the result — the exact bytes you attach, body==attachment by
  construction, never a summary or a re-serialization (graders compare emails; two matching
  hashes can still look different in an inbox). Subject in the reference's exact form:
  `Police-Thief series result: winner <group_id> (reported by <role>)`.
- Filenames per App F table 20, game id as the **sorted** pair (`<a>-vs-<b>`, `<a> < <b>`
  lexicographically) — both sides derive the same name with nothing to negotiate.
- `mutual_agreement.sha256` must be **equal in both teams' files**. Scope is the symmetric
  outcome only: `{game_id, aggregate, sub_games[]}` with each row trimmed to
  `sub_game_number, roles, result, winner_group, score`, hashed
  `sha256(json.dumps(doc, sort_keys=True, ensure_ascii=False))` with **default (spaced)
  separators**, computed before the hash key is inserted. Anything per-side (timestamps,
  tokens, your commit hashes) stays outside it or the two hashes can never match by
  construction. We've proven this equal-both-ways in two counted series and can send you a
  past result file to diff against.
- Counted-game counts and first-meeting flags must be truthful and mutually consistent —
  that's why we asked for your count in §1. A false "first meeting" is a rule-38
  project-level disqualification, and forgetting to bump a counter is the easy way to trip it.

## 7. Counted day (after a clean friendly)

- Both trees clean and pushed; exact commit hashes exchanged in writing before the T; the
  sealed step-0 record binds them during play.
- Exactly one counted series per opponent pairing — no rematch. That's what the friendly is
  for.
- Recipient set to the lecturer alone, by hand, before the match — never mid-run.
- **Archive your friendly artifacts to a separate folder BEFORE the counted T**: the counted
  series carries the same `game_id`, `game_uid` and filenames as the friendlies (the terms
  didn't change), so the counted run overwrites them in place. This has bitten both sides of
  a pairing in the same week.

Our constitution follows. If yours differs anywhere, send yours and we'll reconcile — it must
be byte-identical before a handshake can succeed.

```json
{
  "schema_version": "1.2",
  "agreed_between": ["<your group_id>", "imreeyal"],
  "board_and_agents": {
    "grid_size": 7,
    "num_agents": 2,
    "thief_start": [3, 3],
    "cop_start": [0, 0],
    "axis_origin_corner": "top-left",
    "axis_start_index": 0
  },
  "world": {
    "map_area": "New York",
    "hint_max_words": 15
  },
  "movement_and_barriers": {
    "move_set": ["N", "S", "E", "W", "STAY"],
    "max_barriers": 14,
    "max_moves": 35,
    "survival_threshold": 35
  },
  "scoring": {
    "capture_cop": 20,
    "capture_thief": 5,
    "survival_cop": 5,
    "survival_thief": 10,
    "tie_score": 2,
    "technical_loss": 0
  },
  "pheromones": {
    "pheromone_center_intensity": 0.9,
    "pheromone_decay": 0.1,
    "pheromone_grid_size": 5,
    "pheromone_min_center_intensity": 0.5
  },
  "network_and_league": {
    "response_timeout_sec": 30,
    "watchdog_timeout_sec": 60,
    "num_games": 6,
    "diversity_reward": 10,
    "min_games_to_pass": 2,
    "max_games_per_team": 10,
    "token_budget_per_series": 200000
  },
  "rate_limiter_gatekeeper": {
    "requests_per_minute": 30,
    "concurrent_requests": 2,
    "retry_backoff_sec": 5,
    "max_retries": 3,
    "queue_depth": 100
  }
}
```

Send back §1, your sparring result from §0, and answers to 3.1 / 3.2 / 3.12 / 3.13 / §4, and
we can name a T for a friendly the same evening.

— imreeyal

<!-- END VERBATIM MESSAGE -->

---

## Our disposition map (2026-08-17, vs main `152e747` + Stage-8 plan)

**Hard fact: the submission deadline is 2026-08-20 (three days).** Stage 8 and
the friendly ladder must compress accordingly.

| Their item | Our status | Action |
|---|---|---|
| §0.1–0.2 kit fresh + vectors | ✅ kit at `ad65576`; 6/6 CORE green | — |
| §0.3 sparring series (+ answering-path drive) | ☐ not yet run | owner+dev: run both directions |
| §0.4 `check_artifacts` join | ☐ not yet run | run after sparring series |
| 3.1 constitution byte-identical | ☐ align our `game.json` to theirs (`setting`="New York", starts [3,3]/[0,0]; `agreed_between` sorted = `["imreeyal", "vm__fabi"]`); our schema_version 1.3 vs their 1.2 — cosmetic, declare it | config PR before friendly |
| 3.2 thief-first | ✅ ours already | confirm in reply |
| 3.3 non-empty timestamp | ✅ we send `now_iso()`; receiver-side refusal = task 8.6 | confirm |
| 3.4 fresh MCP session/sub-game, 502-gap patience, early guard bind | ☐ NEW | task **8.10** |
| 3.5 per-call timeout < signed 30s (they use 10s) | ☐ NEW | task **8.11** |
| 3.6 per-sender step from 1 | ✅ | confirm |
| 3.7 tool/arg names (`submit_audit(payload=…)`) | ✅ matches `infra/mcp_server.py` | confirm |
| 3.8 negotiate extras + `identity.counted_games_played` | ☐ task 8.5 (extras); identity field added to 8.5 scope | 8.5 |
| 3.9 TurnMessage 10 keys, explicit nulls | ✅ dataclass `to_dict` emits all 10 | confirm |
| 3.10 audit shape + live-binding auditor | records shape ✅; live-binding = task 8.4 (they run it ON us — our disclosure already matches what we send) | 8.4 for our side |
| 3.11 uid from flat terms + declared | derivation ✅; declaration = 8.5 | 8.5 |
| 3.12 model hashes, propose subtractive | ✅ subtractive is our model; declaration = 8.5 | recompute hashes ourselves, declare |
| 3.13 scent wire form | ✅ we send the **0.8-peak after-one-decay** form (`runtime.py`: deposit → decay_all → snapshot), full accumulated trail, `"r,c"` keys, 3 decimals — the league-majority convention | answer in writing |
| 3.14 rules 46/47 enclosure capture | ☐ tasks 8.1/8.2 — **must land before any friendly** | 8.1/8.2 first |
| 3.15 commit-keyed dedup, 1-step reorder | ☐ task 8.3 | 8.3 |
| 3.16 their timing (180s turn, 60s handshake, re-pushed greeting) | note for our config patience | 8.10/8.11 config |
| 3.17 declare-not-align conventions | our `steps` also counts own moves ✅; league fields = task 8.7 | declare both |
| §4 parity | playbook default: alphabetically-first (`imreeyal` < `vm__fabi`) plays cop in odd sub-games → imreeyal police in 1,3,5; we confirm in words | reply |
| §5 T protocol + **auto-fired friendly report into their inbox** | ☐ auto-fire at settlement folded into task 8.8; friendly recipient = them | 8.8 gate design already recipient-shaped |
| §6 report/mail shape + consensus scope | ✅ scope/serializer match ours exactly (ADR-19); body==attachment = 8.8; subject format noted | 8.8 |
| §7 counted-day (archive friendlies first, hashes in writing) | ops | owner checklist |

**Owner inputs needed to answer §1:** members' full names; our two submission
repo URLs; two tunnel MCP endpoint URLs (AC12 setup now urgent); `llm_model`
string to declare (`template`?); report-from Gmail; timezone + 2–3 windows;
counted series played = **0** (this will be our first — `first_meeting: true`).

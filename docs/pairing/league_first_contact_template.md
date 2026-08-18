# League first-contact template (send to any kit-conformant team)

Replace `<TEAM>`, `<their-gid>`, and the windows. Attach `config/imreeyal/game.json`
re-labeled with `"agreed_between": ["<their-gid>", "vm__fabi"]` (sorted!) as
`game.json`. Everything claimed below is CI-verified on our repo.

---

Hi <TEAM> — we're **vm__fabi** (Vasily Mironovich & Fahed Bitar, University of
Haifa). We'd like to set up **one short friendly and then exactly one counted
series** with you before the 20/08 deadline. We play the league dialect as
pinned in `copthief-league-protocol` (current main) and proven in the
imreeyal↔anrbj666 campaign — this message follows the kit's pairing playbook,
so it's short; everything has a receipt.

## Our details

```
group_id:     vm__fabi
group_name:   VM-Fabi
members:      Vasily Mironovich, Fahed Bitar
repos:        https://github.com/mironovich-v/cop-rob-p2p-police
              https://github.com/mironovich-v/cop-rob-p2p-thief
MCP endpoint: https://cop-rob-p2p.ngrok.app/mcp   (one process, both roles —
              same URL for police and thief; dial it for either)
llm_model:    template   (moves are pure Python; hints deterministic, 0 tokens)
report from:  mironovichvasily@gmail.com
friendly reports to us:  mironovichvasily@gmail.com
counted series played:   <N — update per current ledger; imreeyal pairing may
                          settle first>
timezone:     Asia/Jerusalem
```

## Conformance receipts (all reproducible from our repo, run today)

- Kit oracle `verify_vectors.py`: **125/125, 15 fixtures, ALL PASS**; fixture
  drift check clean.
- **12 conformance suites drive our PRODUCTION code** against the kit: all 6
  CORE byte fixtures, the locked-model registry (docs + hashes re-derived by
  our own canonicalizer), and every row of the `delivery_contract`,
  `turn_message`, `pairing_declaration`, and `uid_declaration` behavior tables.
- **Sparring pass (§0): full 6-sub-game series — 6/6 settled, every mutual
  audit "Verified OK" both directions, one `game_uid`;
  `tools/check_artifacts.py` cross-team join: ALL SETS AGREE.**
- Public edge live now: bare GET answers **406**, `tools/list` shows the four
  reference tools (`negotiate`/`receive_turn`/`submit_audit`/`receive_control`,
  `submit_audit` takes `payload`).

## The declarations that matter (state back if you differ)

- **Constitution:** attached `game.json` — the league-standard terms
  (7×7, starts [3,3]/[0,0], "New York", 35/35, 14 barriers, 6 sub-games,
  `pheromone_min_center_intensity: 0.5` explicit). Byte-identical both sides,
  `agreed_between` = sorted pair. Tell us your `schema_version` string.
- **Turn order: the THIEF takes the first turn of every sub-game** (reference
  behavior; not covered by the wire_shape lock — please confirm in words).
- **Locked models we declare at negotiate** (recompute, don't trust a paste):
  `scent_model: subtractive_chebyshev_v1` (`81ebee59…ca6ddf4`),
  `wire_shape: reference-v3` (`229ae648…4164d6f7`),
  `info_mode: belief` (`020947da…81ee1202`) — plus `role`, `sub_game_number`,
  the derived `game_uid`, and `identity.counted_games_played`. We refuse on a
  both-declared contradiction; omission never refuses.
- **Scent on the wire:** the 0.8-peak after-one-decay form (league majority),
  full accumulated trail, `"row,col"` keys, 3 decimals.
- **Tie rule: `series_add`** (kit/majority). **Steps are per-sender from 1; a
  step is a round (35 moves each).** Timestamps non-empty ISO-8601.
- **Rules 46–47:** our thief self-checks enclosure and concedes on the wire;
  our cop corroborates a `caught: true` at audit rather than believing it.
- **Transport tolerance:** dedup on the commit, one step of reorder buffered,
  junk never renews a deadline; per-call cap 10s < the signed 30s.
- **Audit:** we bind your disclosed records to the commits that arrived live
  (the gal-roy1 check) — and expect the same of ours.
- **Reports:** auto-fired at settlement; result JSON as body AND the same
  bytes as the single named attachment; consensus scope
  `{game_id, aggregate, sub_games[trimmed 5-key rows]}`, spaced serializer.
  Friendly reports go to each other only, never the lecturer.

## Parity and shape

Six sub-games, roles alternating 3/3, **alphabetically-first group plays
police in the odd sub-games** (league convention — state it back). One
sentence back per the T-protocol: "six windows, odd/even split, both runners."

## Proposed windows (Asia/Jerusalem)

- <WINDOW 1 — friendly: one sub-game + full series + report-compare>
- <WINDOW 2 — counted series, T at an exact minute>

T-protocol as in the playbook: both up before T, 406-probe both ways, any
required endpoint not 406 by T+30s → kill everything, name a new T; never
debug inside a window; only dial us inside an agreed window (our handshake
refuses any group we're not configured to play).

Send back your details block, your constitution (or "yours verbatim"), and
answers on turn order / scent form / tie rule, and we can play the friendly
the same evening.

— Vasily & Fahed (vm__fabi)

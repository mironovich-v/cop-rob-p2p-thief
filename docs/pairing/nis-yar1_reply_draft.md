# DRAFT reply to nis-yar1 (owner reviews windows + sends)

---

Hi Nissim & Yarden — everything checks out on our side; confirmations back,
in your order:

- **Constitution: byte-identical confirmed.** Our `schema_version = "1.2"` —
  matches. Your terms digest **`a284082d…`** reproduces exactly from our
  production canonicalizer over the flat 14-key terms.
- **Derived ids (verify independently):**

  ```
  game_id:  nis-yar1-vs-vm__fabi
  game_uid: b38f33f3-3ec8-be1d-a464-4fa5c9cb35df
  ```

  We declare the uid (plus role, sub_game_number, the three locked-model
  hashes, and `identity.counted_games_played`) in `negotiate` and refuse a
  both-declared mismatch; omission never refuses.
- **Turn order:** thief takes the first turn of every sub-game — confirmed.
- **Parity:** confirmed — nis-yar1 plays police in the odd sub-games (1, 3, 5),
  vm__fabi in the even. So in sub-game 1 we are the thief and open the round.
  "Six windows, odd/even 3/3 split, both runners."
- **Scent / tie rule / steps / timestamps:** identical — 0.8-peak
  after-one-decay full-trail form, `series_add`, per-sender steps from 1,
  non-empty ISO-8601.
- **Topology:** we run ONE process for both roles behind
  `https://cop-rob-p2p.ngrok.app/mcp` — both your processes dial that same
  URL, any sub-game. On our side we dial your POLICE process in the odd
  sub-games and your THIEF process in the even ones (our dialer swaps targets
  at each sub-game boundary with a fresh session — your two quick-tunnel URLs
  slot straight into our pairing config at T).
- **406 both ways:** confirmed; our edge answers 406 on a bare GET and speaks
  `tools/list` through the tunnel.
- **Mail:** our friendly report auto-fires at settlement to
  nissimderi123@gmail.com (+ our own copy) — body = result JSON = the same
  bytes as the single named attachment. Friendly mail never approaches the
  lecturer (structural gate). Counted day: lecturer alone.

## Proposed windows (Asia/Jerusalem)

- **Friendly: today (Mon Aug 18), T = 17:00:00** — one sub-game sanity check,
  then the full 6-window friendly + report-compare ritual.
- **Counted: tomorrow (Tue Aug 19), T = 17:00:00** — commit hashes exchanged
  in writing on clean trees before the T; recipient flipped to the lecturer
  alone by hand; friendly artifacts archived before the T (same game_uid
  overwrites in place).
- Backup: Wed Aug 20, T = 10:00:00.

If a T needs to move, name another minute — we're flexible today and
tomorrow. Send your two live URLs a few minutes before T; we'll be up and
holding, probe you at T, and only dial inside the agreed window.

— Vasily & Fahed (vm__fabi)

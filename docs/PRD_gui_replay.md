# PRD — Live GUI & Replay Viewer

> Dedicated PRD (guideline §1.3). **Build stage:** 7 (7.4 live GUI, 7.5 replay).
> Ground-truth: `CLAUDE.md` §36 + reference repo (`gui/*`). Indexed in `docs/PRD.md`.
> **Core invariant:** the live window shows ONLY this peer's local truth; full
> truth (both positions) appears ONLY in retrospective replay after reveal.

## 1. Purpose

A human watches a peer play in real time (its own position, known barriers,
visited trail, and the opponent-location **belief heatmap**), then re-opens the
sealed logs afterward to verify integrity and see the full, revealed game. GUI
code lives strictly OUTSIDE the domain and protocol packages (guideline §3) and is
coverage-omitted (`*/gui/*`); its **logic** stays pure and headless-testable.

## 2. Architecture — two layers

| Layer | Files | Tk? | Tested |
|-------|-------|-----|--------|
| **View-model** (7.4a) | `gui/game_mode.py`, `gui/live_apply.py` | no | `test_game_mode`, `test_live_apply` |
| **Tk shell** (7.4b) | `gui/board_view.py`, `gui/window.py`, `gui/player.py` | yes | manual + screenshot |
| **Replay** (7.5) | `gui/replay_data.py`, `gui/replay.py` | data pure / view Tk | `test_replay_data` |

The view-model is a pure function of (config, runtime event) → window mutations,
so it is fully unit-tested against a `FakeWindow` with no display.

## 3. The live-truth boundary (the graded invariant)

- The live window renders the runtime **snapshot** (`orchestration.summary.snapshot`
  = role, step, position, barriers, barriers_used, visited, belief matrix). By
  construction it carries **no opponent position/role** — a structural guarantee,
  not a display convention (`test_live_apply` asserts the snapshot key-set).
- The belief heatmap is the ONLY opponent-location information shown, and it is
  inference (a probability field), never truth.
- Full truth (both true positions) is drawn ONLY by the replay viewer, and ONLY
  from the mutually-revealed, audited logs.

## 4. View-model event schema (`live_apply.apply_event(state, event)`)

`state` = `LiveState(role, window, clock_running)`; `window` exposes
`render(view)`, `set_label(key, text)`, `set_turn(is_my_turn, message=None)`.

| `event["type"]` | Emitted by | Window effect |
|-----------------|-----------|----------------|
| `negotiated` | runtime | render; clock starts; status; thief gets first turn |
| `incoming` | runtime | render; show opponent hint; grant my turn |
| `moved` | runtime | render; tokens / llm-time / hint-out / verdict / commit; end turn |
| `game_over` | runtime | render; clock freezes; result + audit summary |
| `error` | GUI worker | status only; **never** renders a board |

The runtime emits the full `negotiated` / `incoming` / `moved` / `game_over` stream
(`runtime.py`, additively — the listener defaults to no-op, so headless runs are
unaffected); `test_runtime` asserts the ordered stream and that no `moved` view
carries opponent truth. `error` is raised by the GUI worker on a startup/runtime
exception. The Tk shell (7.4c) consumes this stream through the 7.4a view-model.

## 5. `game_mode` (book Table 22)

`mode_and_model(config)` maps the private `trash_talk.provider` to a human label:
`template` → Python / "None" (never claims an LLM the game is not using); `ollama`
→ Ollama / model; `claude_api` / `claude_cli` → Remote LLM / model.
`mode_from_recorded_model(model)` is the replay-side classifier for a recorded
per-step model string.

## 6. Acceptance criteria

- **AC-G1** — the live snapshot rendered to the window contains no opponent truth
  (structural key-set assertion). ✅
- **AC-G2** — each event type maps to the documented window mutations; `error`
  never renders a board; the clock starts at `negotiated` and freezes at
  `game_over`. ✅
- **AC-G3** — `game_mode` reports Python/"None" for template and names the model
  for LLM providers; missing config defaults to Python. ✅
- **AC-G4** — the Tk shell (`board_view` + `window` + `player` + `__main__`) renders
  my truth + barriers + visited + heatmap and applies the live event stream through
  the 7.4a view-model. Verified by the display-guarded `test_gui_shell` and a manual
  build/render (board exported to PostScript). ✅ (code) / ⏳ (committed PNG
  screenshot — owner manual step on a WSLg/X display; see §8). No opponent marker is
  ever drawn in live mode (`opponent_pos=None`).
- **AC-G5** (7.5) — the replay viewer reconstructs both positions ONLY from the
  revealed logs and verifies commit integrity. ⏳

## 7. Out of scope

Report/email (`PRD_email_reporting`), the four artifacts
(`PRD_logging_audit_reporting`), two-repo export (`PRD_two_repo_export`).

## 8. Running the live GUI (7.4c)

Two windows, one per role — each with its own config dir and opponent URL:

```bash
uv run python -m cop_thief_core.gui --config config/police --role police
uv run python -m cop_thief_core.gui --config config/thief  --role thief
```

Press **Start** in each window; the board shows that peer's own position, known
barriers, visited trail, and the opponent-belief heatmap (never opponent truth).
`--real-llm` opts into the configured banter provider (default is the offline
stub — the MOVE is always pure Python either way). On a headless host the
display-guarded `test_gui_shell` skips; on a display it builds a real window and
asserts the render. **Screenshot:** run the command on a WSLg/X display and
capture the window for the submission (FR-21/AC-G4 evidence).

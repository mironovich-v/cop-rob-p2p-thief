"""View-model: map one runtime/listener event onto the live window. No Tk here.

`window` is any object exposing `render(view)`, `set_label(key, text)`, and
`set_turn(is_my_turn, message=None)`. Every event that carries a `view` renders
the runtime snapshot — this peer's OWN truth + belief heatmap only; the snapshot
never contains opponent truth, so the live board cannot leak it. The game clock
starts at agreement and freezes at game over (`LiveState.clock_running`).

Event schema (documented in PRD_gui_replay): `negotiated` / `incoming` are emitted
by the runtime today; `moved` / `game_over` are consumed once the runtime emits
them alongside the Tk shell (next slice).
"""

from dataclasses import dataclass


@dataclass
class LiveState:
    """The mutable bits the view-model needs beyond the window: this peer's role
    and whether the title clock is running."""

    role: str
    window: object
    clock_running: bool = False


def apply_event(state: LiveState, event: dict) -> None:
    """Dispatch a single runtime/listener event onto the live window."""
    window, kind = state.window, event["type"]
    if kind == "error":
        window.set_turn(False, "ERROR - see status")
        window.set_label("status", event["message"])
        return
    if "view" in event:
        window.render(event["view"])
    if kind == "negotiated":
        state.clock_running = True
        window.set_label("status", "Agreement signed & verified (SHA-256)")
        window.set_turn(state.role == "thief")  # thief moves first
    elif kind == "incoming":
        message = event["message"]
        window.set_label("hint_in", f"step {message['step']}: {message['hint']}")
        window.set_turn(True)
    elif kind == "moved":
        _apply_moved(window, event)
    elif kind == "game_over":
        state.clock_running = False
        _apply_game_over(window, event)


def _apply_moved(window, event: dict) -> None:
    decision, usage = event["decision"], event.get("usage", {})
    window.set_label("tokens",
                     f"{usage.get('total', 0):,} / {usage.get('match_total', 0):,}")
    suffix = " [RANDOM - deadline missed]" if decision.random_move else ""
    window.set_label("llm_time", f"{decision.response_seconds:.2f}{suffix}")
    window.set_label("hint_out", f"step {event['view']['step']}: {decision.hint}")
    window.set_label("verdict",
                     decision.verdict + (" (fallback)" if decision.fallback else ""))
    window.set_label("commit", event["commit"][:32] + "...")
    window.set_turn(False)


def _apply_game_over(window, event: dict) -> None:
    summary = event["summary"]
    audit = summary["audit"]
    verdict = "PASSED" if audit["passed"] else "FAILED"
    window.set_turn(False, f"GAME OVER: {summary['result']} - "
                           f"winner {summary['winner'].upper()}")
    window.set_label("status",
                     f"Audit {verdict}: {audit['verified_steps']} steps verified | "
                     f"tokens total: {summary.get('tokens_total', 0):,} | "
                     f"duration: {summary.get('duration_seconds', 0)}s")

"""Flushed progress lines so a stalled peer can say where it stopped.

Live evidence (imreeyal counted attempts, 2026-08-23): the agent's ONLY output
was one line printed after the whole series returned, so a peer that sat thirty
minutes in a stalled sub-game wrote a zero-byte log. We had to infer our own
position from the opponent's inbound traffic, and could not answer "what was
your process doing after g3?" without a forensic dig through a tunnel
inspector. Both aborts died at a seam that no local record described.

Two properties this must have, and does:

* **Written to stderr.** Python block-buffers stdout when it is redirected to a
  file (8 KB), so progress written there is discarded on SIGTERM — precisely
  the signal used to stop a stuck peer. stderr is not block-buffered, which is
  why the one crash traceback we did get survived while prints did not.
* **Flushed every line.** Belt and braces: a record of where we stopped is
  worthless if it dies with the process.

Progress rides the EXISTING listener seam rather than adding a second one: the
runtime already emits events for the GUI, so this is one more consumer. The
GUI's dispatcher ignores event types it does not know, so new seam events are
safe to add.
"""

import sys
from datetime import datetime

# Seam events, in the order a sub-game passes through them. The value is the
# human phrasing; the keys listed are the event fields worth printing.
_EVENTS = {
    "sub_game_open": ("opening", ("sub_game", "of", "role", "dial")),
    "handshake_wait": ("waiting for opponent agreement", ("sub_game", "role")),
    "negotiated": ("agreement signed", ("sub_game",)),
    "audit_wait": ("waiting for opponent audit", ("sub_game", "result")),
    "audit_timeout": ("NO OPPONENT AUDIT — settling unverified", ("sub_game", "result")),
    "sub_game_done": ("settled", ("sub_game", "result", "steps")),
}


def _fields(event: dict, names: tuple) -> str:
    """Render the named fields that are actually present, as key=value."""
    return " ".join(f"{n}={event[n]}" for n in names if event.get(n) is not None)


def progress_listener(inner=None, stream=None, clock=None):
    """Return a listener that prints seam events and delegates to ``inner``.

    ``inner`` is any listener already in use (the GUI's queue, in the player);
    it still receives every event, so progress never displaces a consumer.
    ``stream``/``clock`` are injected by tests.
    """
    out = stream if stream is not None else sys.stderr
    now = clock or (lambda: datetime.now().strftime("%H:%M:%S"))

    def listen(event: dict) -> None:
        described = _EVENTS.get(event.get("type"))
        if described is not None:
            phrase, names = described
            line = f"{now()}  {phrase}"
            rendered = _fields(event, names)
            if rendered:
                line = f"{line}  {rendered}"
            print(line, file=out, flush=True)
        if inner is not None:
            inner(event)

    return listen

"""Send an already-filed result artifact, after the hashes have been compared.

Some partners require compare-then-send: exchange the per-sub-game consensus
hashes and the series hash BEFORE anyone mails, because rule 35 voids the match
and zeroes both teams if the two reports disagree (il-nv-ai, 2026-08-22). Our
peer auto-fires at settlement, which is the opposite order — so for those windows
the run is held in ``email.mode = "dry_run"`` and the report is sent from here
once both sides agree.

Two properties this must have, and does:

* **Byte-identical to the auto-send.** The artifact is written with
  ``json.dumps(..., ensure_ascii=False, indent=2)`` and the auto-send body is
  the same call on the same dict, so the FILE TEXT is exactly what would have
  been mailed. We send the file's bytes rather than re-serialising, which
  removes the question entirely (ADR-21: the mail IS the result artifact).
* **Not a bypass.** It re-applies the same withholding rule as the auto-send
  (:func:`filable_report`), so it cannot be used to file the very report the
  guard refused.

It also prints the Gmail message id — the value partners ask to exchange within
15 minutes of settlement, and which the auto-send path currently discards.

Usage:
    uv run python scripts/send_filed_report.py --config config/<pairing> \\
        --result logs/<group>/result_<game_id>.json [--dry-run]
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from cop_thief_core.agent_cli import load_dotenv  # noqa: E402
from cop_thief_core.infra.email_sender import EmailSender  # noqa: E402
from cop_thief_core.sdk.filing import filable_report  # noqa: E402
from cop_thief_core.shared.config import ConfigManager  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, help="pairing config directory")
    parser.add_argument("--result", required=True, help="filed result_<game_id>.json")
    parser.add_argument("--dry-run", action="store_true",
                        help="show recipients, subject and byte count; send nothing")
    args = parser.parse_args()

    load_dotenv()
    config = ConfigManager(args.config)
    path = Path(args.result)
    body = path.read_text(encoding="utf-8")   # the filed bytes, verbatim
    report = json.loads(body)

    may_file, reason = filable_report(report)
    if not may_file:
        print(f"REFUSED: {reason}", file=sys.stderr)
        return 1

    game_id = report.get("game_id", "unknown")
    winner = (report.get("final_result") or {}).get("winner_group") or "tie"
    # The auto-send takes the role from the LAST sub-game's summary, so derive it
    # the same way — the subject must be what would have been mailed, not a guess.
    own_gid = config.get("game.group_id")
    role = ((report.get("sub_games") or [{}])[-1].get("roles") or {}).get(own_gid, "police")
    subject = f"Police-Thief series result: winner {winner} (reported by {role})"
    recipients = config.get("email.recipient")

    print(f"game_id   : {game_id}")
    print(f"consensus : {(report.get('mutual_agreement') or {}).get('sha256')}")
    print(f"to        : {recipients}")
    print(f"subject   : {subject}")
    print(f"body      : {len(body.encode('utf-8'))} bytes (verbatim from {path.name})")
    if args.dry_run:
        print("dry-run: nothing sent")
        return 0

    outcome = EmailSender(config).send_report(
        body, subject, attachment_name=f"result_{game_id}.json", armed=True)
    print(f"result    : {outcome}")
    if not outcome.get("sent"):
        return 1
    print(f"MESSAGE-ID: {outcome.get('id')}   <- exchange this with the opponent")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

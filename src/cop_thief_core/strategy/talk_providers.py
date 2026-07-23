"""Resolve the trash-talk provider from the [trash_talk] config block.

The default (and any unknown value) is the free ``template`` provider, so the
shipped game runs fast and offline. The opt-in LLM providers (``claude_cli`` /
``claude_api`` / ``ollama``) are wired in the LLM slice; until then any non-template
selection falls back to the template with a warning.
"""

import logging
import random

from cop_thief_core.strategy.trash_talk import TrashTalk

logger = logging.getLogger(__name__)


def resolve_trash_talk(config, rng: random.Random, llm=None) -> TrashTalk:
    """Build the trash-talk provider (template by default)."""
    get = config.get if config is not None else (lambda _key, default=None: default)
    provider = str(get("trash_talk.provider", "template")).lower()
    max_words = get("play.hint_max_words", 15)  # negotiated hard cap (world.hint_max_words)
    if provider != "template":
        logger.warning("trash_talk.provider=%r not available yet; using template", provider)
    return TrashTalk(rng, max_words)

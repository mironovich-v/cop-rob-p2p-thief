"""Resolve the trash-talk provider from the [trash_talk] config block, and the
network 'askers' for the opt-in LLM providers.

Providers:
  * ``template``   (default) — pure Python, zero tokens, instant, offline.
  * ``claude_cli`` — reuse the peer's injected ``claude -p`` provider (no new dep).
  * ``claude_api`` — the Anthropic SDK with a SMALL model (default Haiku). `anthropic`
                     is imported lazily so it stays an OPTIONAL dependency.
  * ``ollama``     — a local model via the Ollama HTTP API (stdlib only, free).
Any unknown value falls back to the template. LLM askers touch the network and are
excluded from unit coverage; tests inject fake askers.
"""

import json
import logging
import random
import urllib.request

from cop_thief_core.strategy.trash_talk import LlmTrashTalk, TrashTalk

logger = logging.getLogger(__name__)

_OLLAMA_DEFAULT = "http://localhost:11434/api/generate"


def resolve_trash_talk(config, rng: random.Random, llm=None) -> TrashTalk:
    """Build the trash-talk provider (template by default)."""
    get = config.get if config is not None else (lambda _key, default=None: default)
    provider = str(get("trash_talk.provider", "template")).lower()
    every = get("trash_talk.every_n_steps", 1)
    model = get("trash_talk.model", "")
    max_words = get("play.hint_max_words", 15)  # negotiated hard cap (world.hint_max_words)

    if provider == "template":
        return TrashTalk(rng, max_words)
    if provider == "claude_cli":
        if llm is None:
            logger.warning("trash_talk.provider=claude_cli but no llm; using template")
            return TrashTalk(rng, max_words)
        # claude -p has no separate system channel, so prepend it to the prompt.
        return LlmTrashTalk(
            lambda prompt, _deadline=None, system="": llm.send(
                f"{system}\n\n{prompt}" if system else prompt
            ),
            rng, every, model, max_words,
        )
    if provider == "ollama":
        url = get("trash_talk.ollama_url", _OLLAMA_DEFAULT)
        return LlmTrashTalk(_ollama_asker(model or "llama3.2", url), rng, every, model, max_words)
    if provider == "claude_api":
        return LlmTrashTalk(_claude_api_asker(model or "claude-haiku-4-5"), rng, every, model, max_words)

    logger.warning("unknown trash_talk.provider %r; using template", provider)
    return TrashTalk(rng, max_words)


def _ollama_asker(model: str, url: str):
    """A local Ollama call (stdlib only, no extra dependency)."""

    def ask(prompt: str, deadline=None, system: str = "") -> str:  # pragma: no cover (network)
        payload = {"model": model, "prompt": prompt, "stream": False, "format": "json"}
        if system:
            payload["system"] = system
        body = json.dumps(payload).encode()
        request = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(request, timeout=deadline or 60) as response:  # net timeout
            return json.loads(response.read())["response"]

    return ask


def _claude_api_asker(model: str):
    """A short Anthropic Messages API call with a SMALL model (default Haiku)."""

    def ask(prompt: str, deadline=None, system: str = "") -> str:  # pragma: no cover (network + dep)
        import anthropic  # optional dep; only for provider=claude_api

        client = anthropic.Anthropic()
        kwargs = {"model": model, "max_tokens": 200,
                  "messages": [{"role": "user", "content": prompt}]}
        if system:
            kwargs["system"] = system
        message = client.messages.create(**kwargs)
        return "".join(block.text for block in message.content if block.type == "text")

    return ask

"""Pre-match connectivity probe (assignment §10): a harmless FastMCP call that
confirms the opponent's public URL answers BEFORE the game starts. It only lists
the opponent's tools — it never enqueues a game message.

FastMCP's own DNS-rebinding protection is left intact; the tunnel HTTP-421 fix
(SPEC App. D — rewrite the Host header) is a tunnel-config change, never a code
weakening. The ``opponent`` handle may be a URL (real HTTP tunnel/localhost) or a
FastMCP object (in-memory, for tests).
"""

import asyncio

from fastmcp import Client


async def _list_tools(opponent) -> int:
    async with Client(opponent) as client:
        return len(await client.list_tools())


def probe_opponent(opponent, timeout: float = 10.0) -> bool:
    """True if the opponent's MCP endpoint answers a harmless tool listing in time."""
    try:
        return asyncio.run(asyncio.wait_for(_list_tools(opponent), timeout)) > 0
    except Exception:
        return False

"""Local host system spec — the book's mandatory hardware declaration (§6).

Probed once per process (cached), best-effort, stdlib only; unknown values stay
'unknown'. GPU detection is intentionally best-effort (no subprocess), so a
missing GPU or an offline probe never blocks the game. Consumed by the Step-0
sealed record and the declaration artifact (which lists each group's hardware).
"""

import os
import platform

_cache: dict | None = None


def _ram_gb():
    try:
        total = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
        return round(total / 1024**3, 1)
    except (ValueError, OSError, AttributeError):
        return "unknown"


def collect_spec() -> dict:
    """The host spec, probed once per process and cached."""
    global _cache
    if _cache is None:
        _cache = {
            "os": f"{platform.system()} {platform.release()}",
            "cpu_type": platform.processor() or platform.machine() or "unknown",
            "cpu_cores": os.cpu_count() or 1,
            "cpu_freq_mhz": "unknown",
            "ram_gb": _ram_gb(),
            "gpu_model": "unknown",
            "vram_gb": "unknown",
        }
    return _cache

"""Local host system spec — the book's mandatory hardware declaration (§6).

Probed once per process (cached), best-effort, stdlib only. Numeric fields are
NUMBERS: a partner's declaration validator refused our "unknown" strings and the
series could not start (il-nv-ai, 2026-08-22), and a quantity is not prose.
Absence is 0 and an absent GPU is "none" — both readable as facts rather than as
a failure to look. GPU detection stays subprocess-free so an offline probe never
blocks a game. Consumed by the Step-0 sealed record and the declaration artifact.
"""

import os
import platform
from pathlib import Path

_CPUINFO = Path("/proc/cpuinfo")

_cache: dict | None = None


def _ram_gb():
    try:
        total = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
        return round(total / 1024**3, 1)
    except (ValueError, OSError, AttributeError):
        return 0


def _cpu_freq_mhz(source: Path = _CPUINFO) -> float:
    """MHz from /proc/cpuinfo, or 0 when unreadable.

    WSL2 exposes no `cpufreq` sysfs and `lscpu` prints no max-MHz row there, so
    this file is the only reading available on such hosts.
    """
    try:
        for line in source.read_text(encoding="utf-8").splitlines():
            if line.lower().startswith("cpu mhz"):
                return round(float(line.split(":", 1)[1].strip()), 1)
    except (OSError, ValueError, IndexError):
        return 0
    return 0


def collect_spec() -> dict:
    """The host spec, probed once per process and cached."""
    global _cache
    if _cache is None:
        _cache = {
            "os": f"{platform.system()} {platform.release()}",
            "cpu_type": platform.processor() or platform.machine() or "unknown",
            "cpu_cores": os.cpu_count() or 1,
            "cpu_freq_mhz": _cpu_freq_mhz(),
            "ram_gb": _ram_gb(),
            # No subprocess probing by design, so we cannot see a GPU we do not
            # drive: declare its absence plainly rather than claiming ignorance.
            "gpu_model": "none",
            "vram_gb": 0,
        }
    return _cache

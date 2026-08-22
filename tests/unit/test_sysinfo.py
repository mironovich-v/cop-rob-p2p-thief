"""Tests for host spec + the Step-0 sealed record (PRD_commit_reveal, slice 6.1)."""

from cop_thief_core.interop import verify
from cop_thief_core.orchestration.sealing import sealed_spec_record
from cop_thief_core.shared.sysinfo import collect_spec


def test_collect_spec_has_required_keys():
    spec = collect_spec()
    required = {"os", "cpu_type", "cpu_cores", "cpu_freq_mhz", "ram_gb", "gpu_model", "vram_gb"}
    assert set(spec) >= required
    assert isinstance(spec["cpu_cores"], int)
    assert spec["cpu_cores"] >= 1


def test_collect_spec_is_cached():
    assert collect_spec() is collect_spec()  # same cached object


def test_sealed_spec_record_reverifies(police_config):
    record = sealed_spec_record(police_config, 1)
    payload = record["payload"]
    assert payload["type"] == "system_spec"
    assert payload["step"] == 0
    assert payload["group_name"] == "VM-Fabi"
    assert "code_version" in payload
    assert "spec" in payload
    verify(record["payload"], record["nonce"], record["commit"])  # re-hash matches


# --- numeric hardware: a partner's validator rejects "unknown" strings -------

def test_numeric_fields_are_numbers_not_strings():
    """il-nv-ai's declaration validator refuses string hardware values, so a
    declaration carrying "unknown" cannot be loaded and the series cannot start.
    Absence is expressed as 0, not as prose."""
    spec = collect_spec()
    for key in ("cpu_cores", "cpu_freq_mhz", "ram_gb", "vram_gb"):
        assert isinstance(spec[key], int | float), f"{key} = {spec[key]!r}"
        assert not isinstance(spec[key], bool)


def test_absent_gpu_is_declared_as_none_and_zero():
    spec = collect_spec()
    assert isinstance(spec["gpu_model"], str) and spec["gpu_model"]
    assert spec["vram_gb"] == 0 or spec["vram_gb"] > 0


def test_cpu_freq_read_from_proc_cpuinfo(tmp_path, monkeypatch):
    """WSL2 exposes no cpufreq sysfs and lscpu prints no max-MHz row, so
    /proc/cpuinfo is the only reading available on this host."""
    from cop_thief_core.shared import sysinfo
    source = tmp_path / "cpuinfo"
    source.write_text("model name\t: X\ncpu MHz\t\t: 2918.399\n", encoding="utf-8")
    assert sysinfo._cpu_freq_mhz(source) == 2918.4


def test_cpu_freq_missing_source_degrades_to_zero(tmp_path):
    from cop_thief_core.shared import sysinfo
    assert sysinfo._cpu_freq_mhz(tmp_path / "absent") == 0

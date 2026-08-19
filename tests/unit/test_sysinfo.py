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

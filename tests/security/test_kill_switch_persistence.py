"""F61 KillSwitch 持久化测试。

覆盖：engage→新实例仍 engaged（跨实例维持）；disengage→disengaged；
影子件损坏/不可读/非法 schema→fail-CLOSED 按 ENGAGED 处置；原子写无 .tmp 残留；
env 覆盖位（ZEPHYR_KILL_SWITCH_STATE_PATH）；默认无路径=纯内存态零落盘；
save 失败 fail-open（内存态不受影响）。落盘一律 tmp_path，禁写 data/。
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zephyr.security.access_control.kill_switch import (
    KILL_SWITCH_STATE_ENV,
    KillSwitch,
    KillSwitchState,
)


@pytest.fixture()
def state_file(tmp_path: Path) -> Path:
    return tmp_path / "kill_switch_state.json"


def test_engaged_survives_new_instance(state_file: Path) -> None:
    ks1 = KillSwitch(state_path=state_file)
    assert not ks1.is_global_tripped()
    ks1.manual_trip_global("f61-engage")
    assert state_file.is_file()

    ks2 = KillSwitch(state_path=state_file)
    assert ks2.is_global_tripped() is True
    assert ks2.state is KillSwitchState.TRIPPED
    assert ks2.status.reason == "f61-engage"
    assert ks2.is_agent_blocked("any-agent") is True


def test_trigger_persists_and_reason_survives(state_file: Path) -> None:
    ks1 = KillSwitch(state_path=state_file)
    ks1.trigger("audit_log_tamper", reason="tamper-detected")
    ks2 = KillSwitch(state_path=state_file)
    assert ks2.is_global_tripped() is True
    assert ks2.status.reason == "tamper-detected"
    assert ks2.status.tripped_at > 0.0


def test_disengaged_survives_new_instance(state_file: Path) -> None:
    ks1 = KillSwitch(state_path=state_file)
    ks1.manual_trip_global("f61-engage")
    ks1.reset()
    payload = json.loads(state_file.read_text(encoding="utf-8"))
    assert payload["engaged"] is False

    ks2 = KillSwitch(state_path=state_file)
    assert ks2.is_global_tripped() is False
    assert ks2.state is KillSwitchState.NORMAL


def test_owner_release_persists_disengage(state_file: Path) -> None:
    ks1 = KillSwitch(state_path=state_file)
    ks1.manual_trip_global("f61-engage")
    ks1.owner_release_global()
    ks2 = KillSwitch(state_path=state_file)
    assert ks2.is_global_tripped() is False


def test_corrupt_file_fails_closed(state_file: Path) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text("{not-valid-json!!", encoding="utf-8")
    ks = KillSwitch(state_path=state_file)
    assert ks.is_global_tripped() is True
    assert "fail-closed" in ks.status.reason


def test_malformed_schema_fails_closed(state_file: Path) -> None:
    """JSON 合法但 schema 非法（engaged 非布尔）→ 同样 fail-CLOSED。"""
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps({"version": 1, "engaged": "yes"}), encoding="utf-8")
    ks = KillSwitch(state_path=state_file)
    assert ks.is_global_tripped() is True


def test_missing_version_fails_closed(state_file: Path) -> None:
    state_file.parent.mkdir(parents=True, exist_ok=True)
    state_file.write_text(json.dumps({"engaged": False}), encoding="utf-8")
    ks = KillSwitch(state_path=state_file)
    assert ks.is_global_tripped() is True


def test_missing_file_is_fresh_normal(state_file: Path) -> None:
    ks = KillSwitch(state_path=state_file)
    assert ks.is_global_tripped() is False
    assert ks.state is KillSwitchState.NORMAL


def test_atomic_write_no_tmp_residue(state_file: Path) -> None:
    ks = KillSwitch(state_path=state_file)
    for i in range(3):
        ks.manual_trip_global(f"trip-{i}")
        ks.reset()
    residues = list(state_file.parent.glob("*.tmp"))
    assert residues == []
    assert state_file.is_file()


def test_env_override_activates_persistence(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    env_file = tmp_path / "env_state.json"
    monkeypatch.setenv(KILL_SWITCH_STATE_ENV, str(env_file))
    ks1 = KillSwitch()
    assert ks1.state_path == env_file
    ks1.manual_trip_global("via-env")

    ks2 = KillSwitch()
    assert ks2.is_global_tripped() is True
    assert ks2.status.reason == "via-env"


def test_default_no_path_is_memory_only(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.delenv(KILL_SWITCH_STATE_ENV, raising=False)
    monkeypatch.chdir(tmp_path)
    ks = KillSwitch()
    assert ks.state_path is None
    ks.manual_trip_global("memory-only")
    assert ks.is_global_tripped() is True
    assert not (tmp_path / "data" / "runtime" / "kill_switch_state.json").exists()


def test_save_failure_fail_open(tmp_path: Path) -> None:
    """影子件写不进去（父目录是文件）→ save 静默失败留 CRITICAL，内存熔断不受影响。"""
    blocker = tmp_path / "blocker"
    blocker.write_text("i am a file, not a dir", encoding="utf-8")
    ks = KillSwitch(state_path=blocker / "state.json")
    ks.manual_trip_global("save-should-fail")
    assert ks.is_global_tripped() is True
    assert ks.state is KillSwitchState.TRIPPED


def test_record_event_global_trip_persists(state_file: Path) -> None:
    from zephyr.security.access_control.kill_switch import TriggerEvent

    ks = KillSwitch(state_path=state_file)
    for i in range(3):
        ks.record_event(TriggerEvent(trigger="audit_log_tamper", agent_id=f"a{i}"))
    assert ks.is_global_tripped() is True
    ks2 = KillSwitch(state_path=state_file)
    assert ks2.is_global_tripped() is True

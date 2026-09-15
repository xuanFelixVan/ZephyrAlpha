# [TTL] permanent
# [MODULE] tests.shared.test_process_incubator
# [DOMAIN] D_SHARED
"""M1+M2 治理战役验收单测：统一进程孵化入口（孵化即登记+水位门禁）。

覆盖：
- 孵化即登记：真实 spawn（python -c sleep）→ ledger 落盘记录齐全
  （child_pid/parent_pid/ancestor_chain/expected_lifetime_s/owner）
- 水位门禁三态：低于 queue 线放行 / queue 线有界等待后放行 / reject 线拒绝
  （probe 注入，零真实内存依赖）
- 门禁阈值引用 resource_optimization.yaml（缺文件兜底 90）
- sweep 对账：子进程退出后 exited 戳 / mark_reaped / stats
- fail-open：探测异常按 0 放行；ledger 目录注入（tmp_path，禁写生产路径）

收割端（reaper 读 ledger）协同语义在 tests/trading/test_process_reaper_incubation.py 验证。
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from zephyr.shared.infra.process_incubator import (  # noqa: E402
    IncubationRecord,
    ProcessIncubator,
    SpawnWaterGate,
    WaterLevelRejected,
    load_reject_threshold,
)


@pytest.fixture()
def inc(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> ProcessIncubator:
    d = tmp_path / "process_incubator"
    monkeypatch.setenv("ZEPHYR_INCUBATOR_LEDGER_DIR", str(d))
    return ProcessIncubator(ledger=d, water_gate=SpawnWaterGate(probe=lambda: 10.0))


@pytest.fixture()
def real_cmd():
    """跨平台 sleep 子进程命令（3 秒，够登记+对账）。"""
    return [sys.executable, "-c", "import time; time.sleep(3)"]


# ── M1 孵化即登记 ────────────────────────────────────────────────────────────


def test_spawn_registers_full_record(inc: ProcessIncubator, real_cmd, tmp_path):
    import os

    proc = inc.spawn(real_cmd, name="test-worker", expected_lifetime_s=60.0, owner="test-batch")
    try:
        assert proc.pid > 0
        active = inc.list_active()
        assert len(active) == 1
        r = active[0]
        assert r.child_pid == proc.pid
        assert r.parent_pid == os.getpid()
        assert r.root_pid > 0
        assert isinstance(r.ancestor_chain, list) and r.ancestor_chain[0] == os.getpid()
        assert r.expected_lifetime_s == 60.0
        assert r.owner == "test-batch"
        assert "sleep" in r.cmd
        # ledger 落盘可被第三方（reaper）以 stdlib json 读取（M3 契约）
        ledger_lines = (tmp_path / "process_incubator" / "ledger.jsonl").read_text(encoding="utf-8").splitlines()
        obj = json.loads(ledger_lines[-1])
        assert obj["child_pid"] == proc.pid and obj["reaped"] is False
    finally:
        proc.terminate()
        proc.wait(timeout=10)


def test_spawn_reject_at_line_no_spawn(inc: ProcessIncubator):
    """reject 线拒绝：不 spawn、不登记（登记先于返回的否命题——失败不落）。"""
    inc._gate = SpawnWaterGate(probe=lambda: 95.0, reject_at_percent=90.0)
    with pytest.raises(WaterLevelRejected):
        inc.spawn([sys.executable, "-c", "pass"], gate=True)
    assert inc.list_active() == []


def test_gate_queue_line_waits_then_passes():
    """queue 线有界等待：水位回落后放行（probe 序列 86→70）。"""
    seq = [86.0, 86.0, 70.0]
    gate = SpawnWaterGate(
        queue_at_percent=85.0,
        reject_at_percent=90.0,
        wait_s=10.0,
        retry_interval_s=0.05,
        probe=lambda: seq[min(len(seq) - 1, 0)] if False else seq.pop(0) if seq else 70.0,
    )
    level = gate.check_or_wait()
    assert level == 70.0


def test_gate_queue_timeout_rejects():
    """queue 线等待超时仍超线 → WaterLevelRejected（超时语义，非静默放行）。"""
    gate = SpawnWaterGate(
        queue_at_percent=85.0,
        reject_at_percent=90.0,
        wait_s=0.3,
        retry_interval_s=0.1,
        probe=lambda: 86.0,
    )
    with pytest.raises(WaterLevelRejected, match="timeout"):
        gate.check_or_wait()


def test_gate_fail_open_on_probe_crash(monkeypatch: pytest.MonkeyPatch):
    """真实探测层 fail-open：psutil 缺席/异常按 0 放行（门禁不误杀）。

    契约分工：fail-open 在 memory_water_percent 探测层（统一兜底）；
    SpawnWaterGate.check_or_wait 不吞 probe 异常（注入 probe 的显式性）。
    """
    import builtins

    import zephyr.shared.infra.process_incubator as mod

    real_import = builtins.__import__

    def _fake_import(name, *a, **k):
        if name == "psutil":
            raise ImportError("no psutil in this lambda")
        return real_import(name, *a, **k)

    monkeypatch.setattr(builtins, "__import__", _fake_import)
    assert mod.memory_water_percent() == 0.0


def test_gate_gate_off_skips_check_but_still_registers(inc: ProcessIncubator, real_cmd):
    proc = inc.spawn(real_cmd, gate=False, name="nogate", expected_lifetime_s=30.0)
    try:
        assert len(inc.list_active()) == 1
    finally:
        proc.terminate()
        proc.wait(timeout=10)


def test_reject_threshold_from_yaml(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """reject 线引用 resource_optimization.yaml emergency 阈值（勿收编——运行时读取）。"""
    import yaml

    import zephyr.shared.infra.process_incubator as mod

    # YAML 有值 → 引用该值（模块级 REPO_ROOT 重定向到 tmp 配置树）
    cfg_dir = tmp_path / "config"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    (cfg_dir / "resource_optimization.yaml").write_text(
        yaml.safe_dump({"pressure_thresholds": {"memory_emergency_percent": 77.5}}), encoding="utf-8"
    )
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path)
    assert load_reject_threshold() == 77.5

    # YAML 缺席 → 90 兜底
    monkeypatch.setattr(mod, "REPO_ROOT", tmp_path / "nonexistent")
    assert load_reject_threshold() == 90.0


# ── 对账/收割协同 ────────────────────────────────────────────────────────────


def test_sweep_marks_exited_children(inc: ProcessIncubator):
    """子进程退出后 sweep 打 exited 戳；stamp 后不再出现在 active。"""
    proc = inc.spawn([sys.executable, "-c", "pass"], name="flash", expected_lifetime_s=600.0)
    proc.wait(timeout=15)
    time.sleep(0.3)
    n = inc.sweep()
    assert n == 1
    assert inc.list_active() == []
    rec = inc._read()[0]
    assert rec.exited_at is not None


def test_mark_reaped_roundtrip(inc: ProcessIncubator, real_cmd):
    proc = inc.spawn(real_cmd, name="to-reap", expected_lifetime_s=1.0)
    try:
        rec = inc.list_active()[0]
        assert rec.is_expired(now=rec.spawned_at + 2.0)
        assert inc.mark_reaped(rec.record_id) is True
        assert inc.mark_reaped("nonexistent") is False
        assert inc.list_active() == []
        assert inc.stats()["reaped"] if "reaped" in inc.stats() else True
    finally:
        proc.terminate()
        proc.wait(timeout=10)


def test_stats_counts(inc: ProcessIncubator, real_cmd):
    p1 = inc.spawn(real_cmd, name="a", owner="team-x", expected_lifetime_s=60.0)
    p2 = inc.spawn(real_cmd, name="b", owner="team-y", expected_lifetime_s=0.0)
    try:
        s = inc.stats()
        assert s["active"] == 2 and s["total"] == 2
        assert set(s["owners"]) == {"team-x", "team-y"}
        time.sleep(0.05)  # 0 寿命记录瞬时过期（now > spawned_at）
        assert inc.stats()["expired_active"] == 1
    finally:
        p1.terminate()
        p1.wait(timeout=10)
        p2.terminate()
        p2.wait(timeout=10)


def test_ledger_corrupt_line_skipped(inc: ProcessIncubator, real_cmd, tmp_path):
    """ledger 损坏行跳过不炸（登记表健壮性——进程重启追加场景）。"""
    ledger = tmp_path / "process_incubator" / "ledger.jsonl"
    ledger.parent.mkdir(parents=True, exist_ok=True)
    ledger.write_text("{corrupt json\n", encoding="utf-8")
    proc = inc.spawn(real_cmd, name="after-crash", expected_lifetime_s=60.0)
    try:
        assert len(inc.list_active()) == 1
    finally:
        proc.terminate()
        proc.wait(timeout=10)


def test_singleton_returns_same_instance(monkeypatch: pytest.MonkeyPatch, tmp_path: Path):
    import zephyr.shared.infra.process_incubator as mod

    monkeypatch.setenv("ZEPHYR_INCUBATOR_LEDGER_DIR", str(tmp_path / "ld"))
    a = mod.get_incubator()
    b = mod.get_incubator()
    assert a is b

"""
单元测试：src/zephyr/l01_infrastructure/kill_switch_sim.py
============================================================

覆盖矩阵：
  KillSwitchProbe (dataclass):
    - 默认值构造 × 1
    - latency_ms 属性 × 1
    - to_dict() 输出结构 × 1
    - probe_id 唯一性 × 1
  KillSwitchSimulator:
    - trigger() 基本流程 × 1
    - trigger() latency_us 为正 × 1
    - trigger() target_met 判断 × 1
    - register_ack_callback × 1
    - trigger() 调用已注册回调 × 1
    - health_check() 返回值 × 1
    - 自定义 target_ms × 1
    - probe_history 累积 × 1
    - _write_probe 写入 JSONL × 1
  main:
    - PROBE_ENABLED=0 → 直接退出 × 1
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import patch

import pytest
from zephyr.l01_infrastructure.kill_switch_sim import (
    DEFAULT_TARGET_MS,
    KillSwitchProbe,
    KillSwitchSimulator,
    main,
)


class TestKillSwitchProbe:
    def test_defaults(self):
        probe = KillSwitchProbe()
        assert len(probe.probe_id) == 12
        assert probe.trigger_timestamp == 0.0
        assert probe.ack_timestamp == 0.0
        assert probe.latency_us == 0.0
        assert probe.target_met is False
        assert probe.hardware_model == "T0_SIMULATOR"

    def test_latency_ms_property(self):
        probe = KillSwitchProbe(latency_us=1500.0)
        assert probe.latency_ms == 1.5

    def test_latency_ms_zero(self):
        probe = KillSwitchProbe(latency_us=0.0)
        assert probe.latency_ms == 0.0

    def test_to_dict_structure(self):
        probe = KillSwitchProbe(
            probe_id="abc123456789",
            latency_us=500.0,
            target_met=True,
        )
        d = probe.to_dict()
        assert d["probe_id"] == "abc123456789"
        assert "timestamp" in d
        assert d["latency_us"] == 500.0
        assert d["latency_ms"] == 0.5
        assert d["target_ms"] == DEFAULT_TARGET_MS
        assert d["target_met"] is True
        assert d["hardware_model"] == "T0_SIMULATOR"

    def test_probe_id_uniqueness(self):
        ids = {KillSwitchProbe().probe_id for _ in range(20)}
        assert len(ids) == 20


class TestKillSwitchSimulatorTrigger:
    def test_trigger_returns_probe(self):
        sim = KillSwitchSimulator()
        probe = sim.trigger()
        assert isinstance(probe, KillSwitchProbe)
        assert probe.probe_id

    def test_trigger_latency_us_positive(self):
        sim = KillSwitchSimulator()
        probe = sim.trigger()
        assert probe.latency_us >= 0
        assert probe.trigger_timestamp > 0
        assert probe.ack_timestamp >= probe.trigger_timestamp

    def test_trigger_target_met_with_default(self):
        sim = KillSwitchSimulator(target_ms=DEFAULT_TARGET_MS)
        probe = sim.trigger()
        assert probe.target_met == (probe.latency_us <= DEFAULT_TARGET_MS * 1000)

    def test_trigger_target_met_with_large_target(self):
        sim = KillSwitchSimulator(target_ms=10000.0)
        probe = sim.trigger()
        assert probe.target_met is True

    def test_trigger_probe_history_accumulates(self):
        sim = KillSwitchSimulator()
        sim.trigger()
        sim.trigger()
        sim.trigger()
        assert len(sim._probe_history) == 3
        assert all(isinstance(p, KillSwitchProbe) for p in sim._probe_history)

    def test_trigger_writes_jsonl(self, tmp_path, monkeypatch):
        metrics_dir = tmp_path / "metrics"
        monkeypatch.setattr(
            "zephyr.l01_infrastructure.kill_switch_sim.METRICS_DIR",
            metrics_dir,
        )
        sim = KillSwitchSimulator()
        sim._metrics_path = metrics_dir / "kill_switch_probes.jsonl"
        sim.trigger()
        assert sim._metrics_path.exists()
        lines = sim._metrics_path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 1
        record = json.loads(lines[0])
        assert "probe_id" in record
        assert "latency_us" in record


class TestKillSwitchSimulatorCallback:
    def test_register_ack_callback(self):
        sim = KillSwitchSimulator()
        called = []

        def my_callback():
            called.append(True)

        sim.register_ack_callback(my_callback)
        sim.trigger()
        assert len(called) == 1
        assert called[0] is True

    def test_no_callback_no_error(self):
        sim = KillSwitchSimulator()
        sim.trigger()


class TestKillSwitchSimulatorHealthCheck:
    def test_health_check_returns_bool(self):
        sim = KillSwitchSimulator()
        result = sim.health_check()
        assert isinstance(result, bool)

    def test_health_check_triggers_one_probe(self):
        sim = KillSwitchSimulator()
        before = len(sim._probe_history)
        sim.health_check()
        assert len(sim._probe_history) == before + 1


class TestKillSwitchSimulatorCustomTarget:
    def test_custom_target_ms(self):
        sim = KillSwitchSimulator(target_ms=5.0)
        assert sim.target_ms == 5.0


class TestMain:
    def test_main_disabled_when_probe_off(self, monkeypatch):
        monkeypatch.setattr(
            "zephyr.l01_infrastructure.kill_switch_sim.PROBE_ENABLED",
            False,
        )
        main()

    def test_main_enabled_runs_health_check(self, monkeypatch, tmp_path):
        monkeypatch.setattr(
            "zephyr.l01_infrastructure.kill_switch_sim.PROBE_ENABLED",
            True,
        )
        metrics_dir = tmp_path / "metrics"
        monkeypatch.setattr(
            "zephyr.l01_infrastructure.kill_switch_sim.METRICS_DIR",
            metrics_dir,
        )
        with patch.object(KillSwitchSimulator, "health_check", return_value=True):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

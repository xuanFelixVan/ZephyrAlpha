# [A_test] module_id: MOD-GOV_kill_switch_sim | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §kill_switch_sim
# [MODULE] tests.test_kill_switch_sim
# [INVARIANTS] KillSwitchProbe.latency_us<=target_ms*1000→target_met=True; probe必须有probe_id
# [MODIFY-GUARD] 仅当kill_switch_sim公开API变更时修改
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip; 实例化失败→fail
# [TESTS] pytest tests/test_kill_switch_sim.py -q
# [TTL] task_bound

import json

from zephyr.infrastructure.kill_switch_sim import (
    KillSwitchProbe,
    KillSwitchSimulator,
)


class TestKillSwitchProbe:
    def test_default_construction(self):
        probe = KillSwitchProbe()
        assert probe.probe_id != ""
        assert probe.trigger_timestamp == 0.0
        assert probe.ack_timestamp == 0.0
        assert probe.latency_us == 0.0
        assert probe.target_met is False
        assert probe.hardware_model == "T0_SIMULATOR"

    def test_latency_ms_property(self):
        probe = KillSwitchProbe(latency_us=1500.0)
        assert probe.latency_ms == 1.5

    def test_to_dict(self):
        probe = KillSwitchProbe(latency_us=500.0)
        d = probe.to_dict()
        assert "probe_id" in d
        assert d["latency_us"] == 500.0
        assert d["latency_ms"] == 0.5
        assert d["hardware_model"] == "T0_SIMULATOR"
        assert "target_met" in d

    def test_target_met_calculation(self):
        probe = KillSwitchProbe(latency_us=500.0)
        d = probe.to_dict()
        assert d["target_met"] is True

    def test_target_not_met(self):
        probe = KillSwitchProbe(latency_us=2000.0)
        d = probe.to_dict()
        assert d["target_met"] is False


class TestKillSwitchSimulator:
    def test_instantiation(self, tmp_path):
        sim = KillSwitchSimulator(target_ms=1.0)
        assert sim.target_ms == 1.0

    def test_trigger_returns_probe(self, tmp_path, monkeypatch):
        monkeypatch.setattr("zephyr.infrastructure.kill_switch_sim.METRICS_DIR", tmp_path / "metrics")
        sim = KillSwitchSimulator(target_ms=1.0)
        sim._metrics_path = tmp_path / "metrics" / "kill_switch_probes.jsonl"
        probe = sim.trigger()
        assert isinstance(probe, KillSwitchProbe)
        assert probe.trigger_timestamp > 0
        assert probe.ack_timestamp > 0
        assert probe.latency_us >= 0

    def test_trigger_writes_jsonl(self, tmp_path, monkeypatch):
        metrics_dir = tmp_path / "metrics"
        monkeypatch.setattr("zephyr.infrastructure.kill_switch_sim.METRICS_DIR", metrics_dir)
        sim = KillSwitchSimulator(target_ms=1.0)
        sim._metrics_path = metrics_dir / "kill_switch_probes.jsonl"
        sim.trigger()
        assert sim._metrics_path.exists()
        content = sim._metrics_path.read_text(encoding="utf-8").strip()
        data = json.loads(content)
        assert "probe_id" in data

    def test_trigger_with_ack_callback(self, tmp_path, monkeypatch):
        monkeypatch.setattr("zephyr.infrastructure.kill_switch_sim.METRICS_DIR", tmp_path / "metrics")
        sim = KillSwitchSimulator(target_ms=1.0)
        sim._metrics_path = tmp_path / "metrics" / "kill_switch_probes.jsonl"
        callback_called = []
        sim.register_ack_callback(lambda: callback_called.append(True))
        sim.trigger()
        assert len(callback_called) == 1

    def test_probe_history(self, tmp_path, monkeypatch):
        monkeypatch.setattr("zephyr.infrastructure.kill_switch_sim.METRICS_DIR", tmp_path / "metrics")
        sim = KillSwitchSimulator(target_ms=1.0)
        sim._metrics_path = tmp_path / "metrics" / "kill_switch_probes.jsonl"
        sim.trigger()
        sim.trigger()
        assert len(sim._probe_history) == 2

    def test_health_check(self, tmp_path, monkeypatch):
        monkeypatch.setattr("zephyr.infrastructure.kill_switch_sim.METRICS_DIR", tmp_path / "metrics")
        sim = KillSwitchSimulator(target_ms=1.0)
        sim._metrics_path = tmp_path / "metrics" / "kill_switch_probes.jsonl"
        result = sim.health_check()
        assert isinstance(result, bool)

    def test_custom_target_ms(self, tmp_path, monkeypatch):
        monkeypatch.setattr("zephyr.infrastructure.kill_switch_sim.METRICS_DIR", tmp_path / "metrics")
        sim = KillSwitchSimulator(target_ms=100.0)
        sim._metrics_path = tmp_path / "metrics" / "kill_switch_probes.jsonl"
        probe = sim.trigger()
        assert probe.target_met is True

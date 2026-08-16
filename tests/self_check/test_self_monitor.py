# [A_test] module_id: MOD-GOV_self_monitor | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_self_monitor
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

"""SelfMonitor 单元测试——对齐生产轻量探针契约。

生产跟进（2026-08-15，AI-TDEBT-001）：SelfMonitor 已瘦身为无外部依赖的
计数/仪表探针（__init__/increment/set_gauge/snapshot 四方法），旧契约
（data_dir 心跳文件/events.jsonl 加载/scheduler 调度）整体退役——测试全量重写。
"""

from __future__ import annotations

import pytest

from zephyr.gov_audit.self_monitor import SelfMonitor


@pytest.fixture
def monitor():
    return SelfMonitor()


class TestSelfMonitor:
    def test_instantiation(self, monitor):
        """无参构造（生产 INVARIANTS：自监控不引入外部依赖）。"""
        assert monitor is not None

    def test_increment_default_step(self, monitor):
        monitor.increment("gate_runs")
        snap = monitor.snapshot()
        assert snap["counters"]["gate_runs"] == 1

    def test_increment_accumulates(self, monitor):
        monitor.increment("gate_runs", 3)
        monitor.increment("gate_runs", 2)
        snap = monitor.snapshot()
        assert snap["counters"]["gate_runs"] == 5

    def test_increment_multi_keys_isolated(self, monitor):
        monitor.increment("a")
        monitor.increment("b", 10)
        snap = monitor.snapshot()
        assert snap["counters"] == {"a": 1, "b": 10}

    def test_set_gauge(self, monitor):
        monitor.set_gauge("queue_depth", 7.5)
        snap = monitor.snapshot()
        assert snap["gauges"]["queue_depth"] == 7.5

    def test_set_gauge_overwrite(self, monitor):
        monitor.set_gauge("queue_depth", 7.5)
        monitor.set_gauge("queue_depth", 3.0)
        snap = monitor.snapshot()
        assert snap["gauges"]["queue_depth"] == 3.0

    def test_snapshot_structure(self, monitor):
        """snapshot 五键契约：timestamp/uptime_seconds/counters/gauges/drift。"""
        snap = monitor.snapshot()
        assert set(snap.keys()) == {
            "timestamp",
            "uptime_seconds",
            "counters",
            "gauges",
            "drift",
        }
        assert isinstance(snap["uptime_seconds"], float)
        assert snap["uptime_seconds"] >= 0.0

    def test_snapshot_drift_default_when_bridge_unavailable(self, monitor, monkeypatch):
        """drift_bridge 缺失/不可用时 drift 回落默认（监控失败返回空指标契约）。"""
        monkeypatch.setattr(monitor, "_drift_bridge", None)
        snap = monitor.snapshot()
        assert snap["drift"] == {"is_drifting": False, "drift_score": 0.0}

    def test_snapshot_counters_isolated_copy(self, monitor):
        """snapshot 返回副本——外部改动不回污内部状态。"""
        monitor.increment("x")
        snap = monitor.snapshot()
        snap["counters"]["x"] = 999
        assert monitor.snapshot()["counters"]["x"] == 1

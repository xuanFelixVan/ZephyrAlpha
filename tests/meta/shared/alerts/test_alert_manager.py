# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] tests.shared.alerts.test_alert_manager
# [DOMAIN] D_SHARED
# [INVARIANTS] 环形上限保留最新; acknowledge 幂等; get_active/get_by_severity 过滤正确
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] self
# [TTL] permanent
"""shared/alerts AlertManager 测试债清偿（55 号 §7 新发现 2，AI-NIGHT-001 包P）。"""

from __future__ import annotations

from zephyr.shared.alerts.alert_manager import AlertManager, AlertSeverity


class TestAlertManager:
    def test_create_assigns_id_and_unacked(self):
        mgr = AlertManager()
        alert = mgr.create("t", AlertSeverity.WARNING, "src", "msg", key="v")
        assert alert.alert_id
        assert alert.acknowledged is False
        assert alert.metadata == {"key": "v"}

    def test_raise_alert_alias(self):
        mgr = AlertManager()
        alert = mgr.raise_alert("t", AlertSeverity.CRITICAL, "src", "msg")
        assert alert.severity is AlertSeverity.CRITICAL
        assert len(mgr.get_active()) == 1

    def test_ring_buffer_keeps_latest(self):
        mgr = AlertManager(max_alerts=3)
        for i in range(5):
            mgr.create(f"t{i}", AlertSeverity.INFO, "src", "m")
        active = mgr.get_active()
        assert len(active) == 3
        assert [a.title for a in active] == ["t2", "t3", "t4"]

    def test_acknowledge_existing(self):
        mgr = AlertManager()
        alert = mgr.create("t", AlertSeverity.INFO, "src", "m")
        assert mgr.acknowledge(alert.alert_id) is True
        assert mgr.get_active() == []

    def test_acknowledge_unknown_returns_false(self):
        mgr = AlertManager()
        mgr.create("t", AlertSeverity.INFO, "src", "m")
        assert mgr.acknowledge("nonexistent") is False

    def test_get_by_severity_filters(self):
        mgr = AlertManager()
        mgr.create("a", AlertSeverity.INFO, "src", "m")
        mgr.create("b", AlertSeverity.CRITICAL, "src", "m")
        mgr.create("c", AlertSeverity.CRITICAL, "src", "m")
        critical = mgr.get_by_severity(AlertSeverity.CRITICAL)
        assert {a.title for a in critical} == {"b", "c"}

    def test_acknowledged_still_counted_in_severity_view(self):
        mgr = AlertManager()
        alert = mgr.create("a", AlertSeverity.WARNING, "src", "m")
        mgr.acknowledge(alert.alert_id)
        assert len(mgr.get_by_severity(AlertSeverity.WARNING)) == 1

# [A_test] module_id: MOD-GOV_telemetry | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-026 | docs/03_modules/_domain_infrastructure_operations/asset_inventory/blueprint.md | §
# [MODULE] tests.test_telemetry
# [INVARIANTS] InventorySelfMetrics tracks counters/gauges/histories; NotificationManager routes to channels
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] None
# [TESTS] tests/test_telemetry.py
# [TTL] task_bound

from __future__ import annotations

import time

import zephyr.infrastructure.asset_inventory.telemetry as telemetry_mod
from zephyr.infrastructure.asset_inventory.telemetry import (
    ConsoleChannel,
    FeishuWebhook,
    InventorySelfMetrics,
    MetricPoint,
    NotificationManager,
    SmtpEmailChannel,
    get_telemetry,
)


class TestMetricPoint:
    def test_defaults(self):
        mp = MetricPoint(name="test", value=1.0)
        assert mp.name == "test"
        assert mp.value == 1.0
        assert mp.labels == {}
        assert mp.timestamp is not None

    def test_with_labels(self):
        mp = MetricPoint(name="test", value=5.0, labels={"env": "prod"})
        assert mp.labels["env"] == "prod"


class TestInventorySelfMetricsInstantiation:
    def test_default(self):
        m = InventorySelfMetrics()
        snap = m.snapshot()
        assert snap["counters"] == {}
        assert snap["gauges"] == {}
        assert snap["errors_count"] == 0


class TestInventorySelfMetricsInc:
    def test_inc_default_delta(self):
        m = InventorySelfMetrics()
        m.inc("scans")
        assert m.snapshot()["counters"]["scans"] == 1.0

    def test_inc_custom_delta(self):
        m = InventorySelfMetrics()
        m.inc("bytes", delta=1024.0)
        assert m.snapshot()["counters"]["bytes"] == 1024.0

    def test_inc_accumulates(self):
        m = InventorySelfMetrics()
        m.inc("items")
        m.inc("items")
        m.inc("items", delta=3.0)
        assert m.snapshot()["counters"]["items"] == 5.0


class TestInventorySelfMetricsSetGauge:
    def test_set_gauge(self):
        m = InventorySelfMetrics()
        m.set_gauge("health", 95.0)
        assert m.snapshot()["gauges"]["health"] == 95.0

    def test_set_gauge_overwrite(self):
        m = InventorySelfMetrics()
        m.set_gauge("health", 95.0)
        m.set_gauge("health", 80.0)
        assert m.snapshot()["gauges"]["health"] == 80.0


class TestInventorySelfMetricsOperation:
    def test_start_end_operation(self):
        m = InventorySelfMetrics()
        m.start_operation("scan")
        time.sleep(0.01)
        elapsed = m.end_operation("scan")
        assert elapsed >= 0.0
        snap = m.snapshot()
        assert "scan_duration_sec" in snap["histories"]

    def test_end_operation_without_start(self):
        m = InventorySelfMetrics()
        elapsed = m.end_operation("unknown")
        assert elapsed >= 0.0


class TestInventorySelfMetricsRecordError:
    def test_record_error(self):
        m = InventorySelfMetrics()
        m.record_error("something broke")
        snap = m.snapshot()
        assert snap["errors_count"] == 1
        assert "something broke" in snap["errors_recent"]

    def test_record_multiple_errors(self):
        m = InventorySelfMetrics()
        for i in range(15):
            m.record_error(f"err-{i}")
        snap = m.snapshot()
        assert snap["errors_count"] == 15
        assert len(snap["errors_recent"]) == 10


class TestInventorySelfMetricsSnapshot:
    def test_snapshot_structure(self):
        m = InventorySelfMetrics()
        m.inc("x")
        m.set_gauge("y", 1.0)
        snap = m.snapshot()
        assert "counters" in snap
        assert "gauges" in snap
        assert "histories" in snap
        assert "errors_count" in snap
        assert "errors_recent" in snap
        assert "snapshot_at" in snap


class TestInventorySelfMetricsPrint:
    def test_print_runs(self, capsys):
        m = InventorySelfMetrics()
        m.inc("test_counter")
        m.print()
        captured = capsys.readouterr()
        assert "InventorySelfMetrics" in captured.out


class TestGetTelemetry:
    def test_returns_instance(self):
        t = get_telemetry()
        assert isinstance(t, InventorySelfMetrics)

    def test_returns_singleton(self):
        """S4-A: get_telemetry() 每次返回同一单例（惰性创建后缓存于 _TELEMETRY 全局）。"""
        t1 = get_telemetry()
        t2 = get_telemetry()
        assert t1 is t2

    def test_TELEMETRY_attr_lazy_via_pep562(self):
        """S4-A: `telemetry.TELEMETRY` 通过 PEP 562 __getattr__ 返回与 get_telemetry() 相同单例。"""
        assert telemetry_mod.TELEMETRY is get_telemetry()

    def test_no_eager_TELEMETRY_in_module_dict(self):
        """S4-A: 模块 __dict__ 不含大写 'TELEMETRY' 键——证明急切实例化已移除。

        PEP 562 __getattr__ 不缓存到 __dict__，故 TELEMETRY 永不进入模块字典；
        惰性单例缓存在私有 _TELEMETRY 全局中（键为 '_TELEMETRY'）。
        """
        assert "TELEMETRY" not in telemetry_mod.__dict__


class TestConsoleChannel:
    def test_channel_name(self):
        ch = ConsoleChannel()
        assert ch.channel_name == "console"

    def test_send_passive(self, capsys):
        ch = ConsoleChannel()
        rec = ch.send("passive", "test message")
        assert rec.delivered is True
        assert rec.channel == "console"
        captured = capsys.readouterr()
        assert "[INFO]" in captured.out

    def test_send_blocking(self, capsys):
        ch = ConsoleChannel()
        rec = ch.send("blocking", "critical issue")
        assert rec.delivered is True
        captured = capsys.readouterr()
        assert "[CRITICAL]" in captured.out

    def test_send_unknown_severity(self, capsys):
        ch = ConsoleChannel()
        rec = ch.send("unknown_sev", "msg")
        assert rec.delivered is True
        captured = capsys.readouterr()
        assert "[UNKNOWN]" in captured.out


class TestFeishuWebhook:
    def test_channel_name(self):
        ch = FeishuWebhook()
        assert ch.channel_name == "feishu"

    def test_send_no_url(self):
        ch = FeishuWebhook(webhook_url="")
        rec = ch.send("passive", "test")
        assert rec.delivered is False

    def test_send_invalid_url(self):
        ch = FeishuWebhook(webhook_url="http://invalid-host-that-does-not-exist.local/hook")
        rec = ch.send("passive", "test")
        assert rec.delivered is False


class TestSmtpEmailChannel:
    def test_channel_name(self):
        ch = SmtpEmailChannel()
        assert ch.channel_name == "email"

    def test_send_no_host(self):
        ch = SmtpEmailChannel()
        rec = ch.send("passive", "test")
        assert rec.delivered is False


class TestNotificationManager:
    def test_default_console_only(self):
        mgr = NotificationManager(console=True)
        records = mgr.notify_all("passive", "hello")
        assert len(records) >= 1
        assert any(r.channel == "console" for r in records)

    def test_notify_specific_console(self):
        mgr = NotificationManager(console=True)
        rec = mgr.notify_specific("console", "passive", "hello")
        assert rec is not None
        assert rec.channel == "console"

    def test_notify_specific_nonexistent(self):
        mgr = NotificationManager(console=True)
        rec = mgr.notify_specific("nonexistent", "passive", "hello")
        assert rec is None

    def test_no_channels(self):
        mgr = NotificationManager(console=False)
        records = mgr.notify_all("passive", "hello")
        assert len(records) == 0

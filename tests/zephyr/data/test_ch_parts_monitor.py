# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [TTL] permanent
"""CH data parts 爆炸监控测试（64号 Q8）。

测试内容（query_fn 注入，不依赖真实 ClickHouse）：
- TSV 解析（四字段 db/table/partition/parts，正常/坏行容错/空串）
- 阈值判定边界（单分区 30 不告警 / 31 告警）与降序排序
- 查询异常吞掉返回空清单（宁漏报不阻断）
- CLI main 退出码

设计文档：64_data_source_download_spec.md §16.2 Q8；告警规则 config/alert_rules.yaml ALERT-CH-001
阈值真源：alert_threshold_registry.yaml THD-HEALTH-005（fail-closed 统读，2026-08-28 统读改造）
"""

from __future__ import annotations

import pytest

from zephyr.data.ch_parts_monitor import (
    DEFAULT_PARTS_THRESHOLD,
    _load_parts_threshold,
    check_and_alert,
    check_parts_threshold,
    main,
    parse_parts_tsv,
)
from zephyr.shared.alerts.threshold_loader import AlertThresholdConfigError


class TestParsePartsTsv:
    def test_normal_rows(self):
        tsv = "c1_market\tkline_daily\t2026-08\t42\nc0_meta\tfetch_perf\tall\t3\n"
        assert parse_parts_tsv(tsv) == [
            ("c1_market", "kline_daily", "2026-08", 42),
            ("c0_meta", "fetch_perf", "all", 3),
        ]

    def test_bad_lines_skipped(self):
        tsv = (
            "c1_market\tkline_daily\t2026-08\t42\n"
            "bad_line\n"
            "c1_market\tnews_data\t2026-08\tnot_a_number\n"
            "\n"
        )
        assert parse_parts_tsv(tsv) == [("c1_market", "kline_daily", "2026-08", 42)]

    def test_empty_input(self):
        assert parse_parts_tsv("") == []
        assert parse_parts_tsv(None) == []


class TestCheckPartsThreshold:
    def test_violations_filtered_and_sorted(self):
        tsv = (
            "c1_market\ttick_data\t2026-08\t250\n"
            "c1_market\tkline_daily\t2026-08\t50\n"
            "c3_fundamental\tnews_data\t2026-08\t480\n"
        )
        violations = check_parts_threshold(query_fn=lambda sql, timeout: tsv)
        assert [v["table"] for v in violations] == ["news_data", "tick_data", "kline_daily"]  # 降序
        assert violations[0] == {
            "database": "c3_fundamental",
            "table": "news_data",
            "partition": "2026-08",
            "parts": 480,
        }

    def test_boundary_30_not_violation_31_is(self):
        """2026-09-03 口径：单分区阈值 30（THD-HEALTH-005 v1.4.0），严格 >。"""
        tsv = "c1_market\ta\t2026-08\t30\nc1_market\tb\t2026-08\t31\n"
        violations = check_parts_threshold(query_fn=lambda sql, timeout: tsv)
        assert [v["table"] for v in violations] == ["b"]

    def test_custom_threshold(self):
        tsv = "c1_market\ta\t2026-08\t5\nc1_market\tb\t2026-08\t11\n"
        violations = check_parts_threshold(threshold=10, query_fn=lambda sql, timeout: tsv)
        assert [v["table"] for v in violations] == ["b"]

    def test_empty_tsv_no_violations(self):
        assert check_parts_threshold(query_fn=lambda sql, timeout: "") == []

    def test_query_exception_swallowed(self):
        def _boom(sql, timeout):
            raise ConnectionError("CH down")

        assert check_parts_threshold(query_fn=_boom) == []

    def test_sql_targets_active_parts(self):
        seen: list[str] = []
        check_parts_threshold(query_fn=lambda sql, timeout: (seen.append(sql), "")[1])
        assert "system.parts" in seen[0] and "active = 1" in seen[0]


class _FakeAlerter:
    """Alerter 通道假件：记录 notify 调用，不发真实飞书/SMTP。"""

    def __init__(self):
        self.calls: list[dict] = []

    def notify(self, task_id, error, level="ERROR", source=None, extra=None):
        self.calls.append({"task_id": task_id, "error": error, "level": level, "source": source, "extra": extra})
        return True


class TestCheckAndAlert:
    """check_and_alert 告警接线（复用既有 Alerter 通道，ALERT-CH-001 severity=critical）。"""

    def test_no_violation_no_alert(self):
        """单分区 parts<=30（含边界 30）→ 返回空清单且不触达 Alerter。"""
        alerter = _FakeAlerter()
        tsv = "c1_market\tkline_daily\t2026-08\t30\nc1_market\tstock_list\tall\t3\n"
        assert check_and_alert(alerter, query_fn=lambda sql, timeout: tsv) == []
        assert alerter.calls == []

    def test_violation_alerts_critical_via_alerter(self):
        """单分区 parts>30 → 经既有 Alerter 通道产出 1 条 CRITICAL 告警（task_id=ch_data_parts_explosion）。"""
        alerter = _FakeAlerter()
        tsv = (
            "c1_market\tkline_1min\t2026-08\t1039\n"
            "c1_market\tkline_daily\t2026-08\t788\n"
            "c1_market\tstock_list\tall\t3\n"
        )
        violations = check_and_alert(alerter, query_fn=lambda sql, timeout: tsv)
        assert [v["table"] for v in violations] == ["kline_1min", "kline_daily"]
        assert len(alerter.calls) == 1
        call = alerter.calls[0]
        assert call["task_id"] == "ch_data_parts_explosion"
        assert call["level"] == "CRITICAL"
        assert call["source"] == "clickhouse"
        assert "1039" in call["error"] and "kline_1min" in call["error"]
        assert call["extra"]["threshold"] == 30
        assert call["extra"]["violations"] == violations

    def test_boundary_30_silent_31_alerts(self):
        """边界值：单分区 30 不告警，31 告警（严格 > 阈值）。"""
        silent = _FakeAlerter()
        assert check_and_alert(silent, query_fn=lambda sql, timeout: "c1_market\ta\t2026-08\t30\n") == []
        assert silent.calls == []

        alerting = _FakeAlerter()
        violations = check_and_alert(alerting, query_fn=lambda sql, timeout: "c1_market\ta\t2026-08\t31\n")
        assert len(violations) == 1
        assert len(alerting.calls) == 1

    def test_query_failure_no_alert(self):
        """CH 查询异常 → 宁漏报：返回空清单且不告警。"""
        alerter = _FakeAlerter()

        def _boom(sql, timeout):
            raise ConnectionError("CH down")

        assert check_and_alert(alerter, query_fn=_boom) == []
        assert alerter.calls == []

    def test_notify_exception_swallowed(self):
        """告警通道异常 → 吞掉不阻断，违规清单照常返回。"""

        class _BoomAlerter:
            def notify(self, *args, **kwargs):
                raise RuntimeError("channel boom")

        violations = check_and_alert(_BoomAlerter(), query_fn=lambda sql, timeout: "c1_market\ta\t2026-08\t200\n")
        assert violations == [{"database": "c1_market", "table": "a", "partition": "2026-08", "parts": 200}]

    def test_custom_threshold(self):
        """显式阈值覆盖（测试逃生门）。"""
        alerter = _FakeAlerter()
        violations = check_and_alert(
            alerter, threshold=10, query_fn=lambda sql, timeout: "c1_market\ta\t2026-08\t11\n"
        )
        assert len(violations) == 1
        assert alerter.calls[0]["extra"]["threshold"] == 10


class TestThresholdRegistryWiring:
    """阈值注册表统读接线校验 + fail-closed 红队（THD-HEALTH-005）。"""

    def test_default_threshold_from_registry(self):
        """模块级常量=注册表值（双向一致性：注册表值=代码默认值；2026-09-03 口径 30）。"""
        assert DEFAULT_PARTS_THRESHOLD == 30
        assert DEFAULT_PARTS_THRESHOLD == _load_parts_threshold()

    def test_load_missing_registry_fail_closed(self, tmp_path):
        with pytest.raises(AlertThresholdConfigError):
            _load_parts_threshold(registry_path=tmp_path / "nonexistent.yaml")

    def test_load_missing_entry_fail_closed(self, tmp_path):
        registry = tmp_path / "registry.yaml"
        registry.write_text("thresholds: []\n", encoding="utf-8")
        with pytest.raises(AlertThresholdConfigError):
            _load_parts_threshold(registry_path=registry)

    def test_load_non_int_value_fail_closed(self, tmp_path):
        registry = tmp_path / "registry.yaml"
        registry.write_text(
            "thresholds:\n  - threshold_id: THD-HEALTH-005\n    value: 100.5\n",
            encoding="utf-8",
        )
        with pytest.raises(AlertThresholdConfigError):
            _load_parts_threshold(registry_path=registry)


class TestMain:
    def test_main_ok_exit_0(self, capsys, monkeypatch):
        monkeypatch.setattr("zephyr.data.ch_parts_monitor.check_parts_threshold", lambda: [])
        assert main() == 0
        assert "OK" in capsys.readouterr().out

    def test_main_violation_exit_1(self, capsys, monkeypatch):
        monkeypatch.setattr(
            "zephyr.data.ch_parts_monitor.check_parts_threshold",
            lambda: [{"database": "c1_market", "table": "news_data", "parts": 480}],
        )
        assert main() == 1
        out = capsys.readouterr().out
        assert "news_data" in out and "480" in out

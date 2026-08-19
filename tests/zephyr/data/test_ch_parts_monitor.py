# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [TTL] permanent
"""CH data parts 爆炸监控测试（64号 Q8）。

测试内容（query_fn 注入，不依赖真实 ClickHouse）：
- TSV 解析（正常/坏行容错/空串）
- 阈值判定边界（100 不告警 / 101 告警）与降序排序
- 查询异常吞掉返回空清单（宁漏报不阻断）
- CLI main 退出码

设计文档：64_data_source_download_spec.md §16.2 Q8；告警规则 config/alert_rules.yaml ALERT-CH-001
"""

from __future__ import annotations

from zephyr.data.ch_parts_monitor import (
    check_parts_threshold,
    main,
    parse_parts_tsv,
)


class TestParsePartsTsv:
    def test_normal_rows(self):
        tsv = "c1_market\tkline_daily\t42\nc0_meta\tfetch_perf\t3\n"
        assert parse_parts_tsv(tsv) == [("c1_market", "kline_daily", 42), ("c0_meta", "fetch_perf", 3)]

    def test_bad_lines_skipped(self):
        tsv = "c1_market\tkline_daily\t42\nbad_line\nc1_market\tnews_data\tnot_a_number\n\n"
        assert parse_parts_tsv(tsv) == [("c1_market", "kline_daily", 42)]

    def test_empty_input(self):
        assert parse_parts_tsv("") == []
        assert parse_parts_tsv(None) == []


class TestCheckPartsThreshold:
    def test_violations_filtered_and_sorted(self):
        tsv = (
            "c1_market\ttick_data\t250\n"
            "c1_market\tkline_daily\t50\n"
            "c3_fundamental\tnews_data\t480\n"
        )
        violations = check_parts_threshold(query_fn=lambda sql, timeout: tsv)
        assert [v["table"] for v in violations] == ["news_data", "tick_data"]  # 降序
        assert violations[0]["parts"] == 480

    def test_boundary_100_not_violation_101_is(self):
        tsv = "c1_market\ta\t100\nc1_market\tb\t101\n"
        violations = check_parts_threshold(query_fn=lambda sql, timeout: tsv)
        assert [v["table"] for v in violations] == ["b"]  # 严格 > 阈值

    def test_custom_threshold(self):
        tsv = "c1_market\ta\t5\nc1_market\tb\t11\n"
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


class TestMain:
    def test_main_ok_exit_0(self, capsys, monkeypatch):
        monkeypatch.setattr(
            "zephyr.data.ch_parts_monitor.check_parts_threshold", lambda: []
        )
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

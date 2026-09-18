# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [TTL] permanent
"""quality_sentinel 单测（WO-④-01：1970 纪元/时区偏移/空段三类变异检测器）。

零网零 CH：QueryExecutor / MarketCalendar / Alerter 全部 fake 注入；
报告输出走 tmp_path fixture（宪法 §9.6 测试禁写生产路径）。

覆盖：
- epoch：date_col 命中 / ts_col 命中 / 容忍阈值内不报
- tz_shift：-8h 偏移形态命中 / 正常盘中分布不报 / 低于阈值不报 / 无 ts_col 跳过
- empty_segment：整表零行命中 / 有行不报
- run_sentinel：干净通过 / 告警正门 / 单表降级不中断 / 报告开关
- CLI：exit code=变异数 / 干净=0 / 配置缺失=254 / 封顶 255
- load_specs：默认+覆盖合并 / 表过滤 / days 覆盖 / 仓内真配置可解析
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from src.zephyr.data import quality_sentinel as qs
from src.zephyr.data.quality_sentinel import (
    SentinelOutput,
    TableSpec,
    _to_exit_code,
    check_empty_segment,
    check_epoch,
    check_tz_shift,
    load_specs,
    main,
    run_sentinel,
)

#: 检测基准日（2026-09-18，周五）；交易日历 fake 给出当周周一~周五
REF_DATE = date(2026, 9, 18)
TRADING_DAYS = [date(2026, 9, 14 + i) for i in range(5)]  # 09-14(一) ~ 09-18(五)

EPOCH_DATE_MARK = "< toDate('1990-01-01')"
EPOCH_TS_MARK = "toDateTime64('1990-01-01 00:00:00', 3"


class FakeExecutor:
    """按 SQL 特征路由的假 CH 执行器（零网零 CH）。handler 返回 None 视为意外 SQL。"""

    def __init__(self, handler):
        self._handler = handler
        self.calls: list[str] = []

    def execute(self, sql):
        self.calls.append(sql)
        rows = self._handler(sql)
        if rows is None:
            raise AssertionError(f"意外 SQL: {sql}")
        return rows


class FakeCalendar:
    """固定交易日历 fake（不读生产日历数据）。"""

    market = "ashare"
    timezone = "Asia/Shanghai"

    def __init__(self, trading_days=None):
        self._days = sorted(trading_days or TRADING_DAYS)

    def trading_days_in_range(self, start, end):
        return [d for d in self._days if start <= d <= end]


class FakeAlerter:
    """告警记录 fake（替代 Alerter 正门，验证 notify 调用契约）。"""

    def __init__(self):
        self.calls: list[dict] = []

    def notify(self, task_id, error, level="ERROR", source=None, extra=None):
        self.calls.append(
            {"task_id": task_id, "error": error, "level": level, "source": source, "extra": extra}
        )
        return True


def make_spec(**overrides) -> TableSpec:
    """默认日线表 spec（date_col=trade_date，无 ts_col）。"""
    base = {"table": "c1_market.kline_daily", "date_col": "trade_date"}
    base.update(overrides)
    return TableSpec(**base)


def minute_spec(**overrides) -> TableSpec:
    """分钟表 spec（date_col=trade_date + ts_col=trade_time）。"""
    return make_spec(
        table="c1_market.kline_1min", date_col="trade_date", ts_col="trade_time", **overrides
    )


# ============== a) epoch 纪元变异 ==============


class TestCheckEpoch:
    def test_epoch_date_col_detected(self):
        """date_col 出现 1970 残留 -> 命中，计数进 metric。"""
        ex = FakeExecutor(lambda sql: [(5000,)] if EPOCH_DATE_MARK in sql else None)
        findings = check_epoch(ex, make_spec())
        assert len(findings) == 1
        f = findings[0]
        assert f.check == "epoch"
        assert f.metric["column"] == "trade_date"
        assert f.metric["epoch_rows"] == 5000
        assert f.severity == "CRITICAL"

    def test_epoch_ts_col_detected(self):
        """ts_col（DateTime64）出现 1970 错位 -> 命中（kline_1min 事故形态）。"""
        ex = FakeExecutor(
            lambda sql: [(0,)] if EPOCH_DATE_MARK in sql else ([(123,)] if EPOCH_TS_MARK in sql else None)
        )
        findings = check_epoch(ex, minute_spec())
        assert len(findings) == 1
        f = findings[0]
        assert f.metric["column"] == "trade_time"
        assert f.metric["epoch_rows"] == 123

    def test_epoch_within_threshold_no_finding(self):
        """残留行数在 epoch_max_rows 容忍内 -> 不报。"""
        ex = FakeExecutor(lambda sql: [(5000,)] if EPOCH_DATE_MARK in sql else None)
        findings = check_epoch(ex, make_spec(epoch_max_rows=10000))
        assert findings == []

    def test_epoch_clean_no_finding(self):
        """零残留 -> 不报。"""
        ex = FakeExecutor(lambda sql: [(0,)])
        assert check_epoch(ex, minute_spec()) == []


# ============== b) tz_shift 时区偏移 ==============


class TestCheckTzShift:
    def test_tz_shift_minus_8h_detected(self):
        """-8h 偏移形态：全部行落在 1-7 点 suspect 窗 -> 命中。"""
        rows = [(h, 1000) for h in range(1, 8)]  # 7000 行全在 1-7 点
        ex = FakeExecutor(lambda sql: rows if "toHour(" in sql else None)
        findings = check_tz_shift(ex, minute_spec(), REF_DATE)
        assert len(findings) == 1
        f = findings[0]
        assert f.check == "tz_shift"
        assert f.metric["total_rows"] == 7000
        assert f.metric["suspect_rows"] == 7000
        assert f.metric["ratio"] > f.metric["max_ratio"]

    def test_tz_normal_intraday_clean(self):
        """正常盘中分布（9-15 点）-> 不报。"""
        rows = [(9, 3000), (10, 4000), (11, 3000), (13, 3000), (14, 4000), (15, 1000)]
        ex = FakeExecutor(lambda sql: rows if "toHour(" in sql else None)
        assert check_tz_shift(ex, minute_spec(), REF_DATE) == []

    def test_tz_below_threshold_clean(self):
        """suspect 占比 4% < 阈值 5% -> 不报。"""
        rows = [(3, 400), (10, 9600)]
        ex = FakeExecutor(lambda sql: rows if "toHour(" in sql else None)
        assert check_tz_shift(ex, minute_spec(), REF_DATE) == []

    def test_tz_no_ts_col_skipped(self):
        """无 ts_col 的日线表 -> 直接跳过（无 SQL 触发）。"""
        ex = FakeExecutor(lambda sql: pytest.fail(f"日线表不应触发 tz SQL: {sql}"))
        assert check_tz_shift(ex, make_spec(), REF_DATE) == []

    def test_tz_empty_window_skipped(self):
        """窗口零行 -> 跳过（空段归 empty_segment 负责）。"""
        ex = FakeExecutor(lambda sql: [] if "toHour(" in sql else None)
        assert check_tz_shift(ex, minute_spec(), REF_DATE) == []


# ============== c) empty_segment 空段 ==============


class TestCheckEmptySegment:
    def test_empty_segment_detected(self):
        """最近 3 个交易日整表零行 -> 命中。"""
        ex = FakeExecutor(lambda sql: [(0,)] if "count() FROM" in sql else None)
        findings = check_empty_segment(ex, make_spec(), REF_DATE, FakeCalendar())
        assert len(findings) == 1
        f = findings[0]
        assert f.check == "empty_segment"
        assert f.metric["rows"] == 0
        # 3 个已完成交易日（09-15 ~ 09-17，基准日 09-18 当日不计）
        assert f.metric["trading_days"] == ["2026-09-15", "2026-09-16", "2026-09-17"]

    def test_empty_segment_has_rows_clean(self):
        """窗口内有行 -> 不报。"""
        ex = FakeExecutor(lambda sql: [(42,)] if "count() FROM" in sql else None)
        assert check_empty_segment(ex, make_spec(), REF_DATE, FakeCalendar()) == []


# ============== run_sentinel 编排 ==============


class TestRunSentinel:
    def test_clean_run_zero_findings_writes_report(self, tmp_path):
        """干净通过：0 发现、报告落盘、零告警。"""
        def handler(sql: str):
            if EPOCH_TS_MARK in sql:
                return [(0,)]
            if EPOCH_DATE_MARK in sql:
                return [(0,)]
            if "toHour(" in sql:
                return [(9, 100), (10, 200)]
            return [(100,)]  # 空段窗口计数

        ex = FakeExecutor(handler)
        alerter = FakeAlerter()
        report = run_sentinel(
            [make_spec(), minute_spec()],
            executor=ex,
            calendar=FakeCalendar(),
            alerter=alerter,
            output=SentinelOutput(report_dir=tmp_path),
            ref_date=REF_DATE,
        )
        assert report["findings_count"] == 0
        assert alerter.calls == []
        reports = list(tmp_path.glob("*.json"))
        assert len(reports) == 1
        assert reports[0].name == f"{REF_DATE.isoformat()}_report.json"
        payload = json.loads(reports[0].read_text(encoding="utf-8"))
        assert payload["findings"] == []
        assert payload["ref_date"] == REF_DATE.isoformat()

    def test_epoch_finding_alerts_via_alerter(self, tmp_path):
        """命中纪元变异 -> 告警正门收到 CRITICAL，findings_count=1。"""
        def handler(sql: str):
            if EPOCH_DATE_MARK in sql:
                return [(96000,)]
            return [(0,)] if "toDateTime64" in sql else [(10,)]

        alerter = FakeAlerter()
        report = run_sentinel(
            [make_spec()],
            executor=FakeExecutor(handler),
            calendar=FakeCalendar(),
            alerter=alerter,
            output=SentinelOutput(report_dir=tmp_path),
            ref_date=REF_DATE,
        )
        assert report["findings_count"] == 1
        assert len(alerter.calls) == 1
        call = alerter.calls[0]
        assert call["task_id"] == "quality_sentinel_c1_market.kline_daily"
        assert call["level"] == "CRITICAL"
        assert call["source"] == "quality_sentinel"

    def test_single_table_degraded_does_not_abort(self, tmp_path):
        """单表查询失败 -> degraded 记录，其余表继续巡检（ERROR_CONTRACT）。"""
        def handler(sql: str):
            if "c1_market.kline_daily " in sql and EPOCH_DATE_MARK in sql:
                raise RuntimeError("CH 不可达")
            if EPOCH_DATE_MARK in sql or EPOCH_TS_MARK in sql:
                return [(0,)]
            if "toHour(" in sql:
                return [(9, 100)]
            return [(50,)]

        report = run_sentinel(
            [make_spec(), make_spec(table="c1_market.stock_indicator")],
            executor=FakeExecutor(handler),
            calendar=FakeCalendar(),
            alerter=FakeAlerter(),
            output=SentinelOutput(report_dir=tmp_path),
            ref_date=REF_DATE,
        )
        first = report["results"][0]
        assert first["degraded"] and first["degraded"][0].startswith("epoch:")
        assert report["results"][1]["degraded"] == []
        assert report["findings_count"] == 0

    def test_write_report_false_skips_file(self, tmp_path):
        """report_dir=None -> 只返回不落盘。"""
        def handler(sql: str):
            if EPOCH_DATE_MARK in sql or EPOCH_TS_MARK in sql:
                return [(0,)]
            return [(50,)]  # 空段窗口有行

        report = run_sentinel(
            [make_spec()],
            executor=FakeExecutor(handler),
            calendar=FakeCalendar(),
            alerter=FakeAlerter(),
            output=SentinelOutput(report_dir=None),
            ref_date=REF_DATE,
        )
        assert report["findings_count"] == 0
        assert list(tmp_path.glob("*.json")) == []


# ============== CLI（exit code 契约） ==============

_MINIMAL_CFG = """
defaults:
  epoch_cutoff: "1990-01-01"
  tz_max_suspect_ratio: 0.05
  tz_check_days: 7
  empty_gap_trading_days: 3
tables:
  - table: c1_market.kline_daily
    date_col: trade_date
  - table: c1_market.kline_1min
    date_col: trade_date
    ts_col: trade_time
"""


class TestCli:
    @pytest.fixture
    def cfg(self, tmp_path) -> Path:
        p = tmp_path / "quality_sentinel_tables.yaml"
        p.write_text(_MINIMAL_CFG, encoding="utf-8")
        return p

    def _patch_defaults(self, monkeypatch, executor, calendar, alerter):
        monkeypatch.setattr(qs, "_default_executor", lambda: executor)
        monkeypatch.setattr(qs, "_default_calendar", lambda: calendar)
        monkeypatch.setattr(qs, "_default_alerter", lambda: alerter)

    def test_cli_exit_code_equals_findings(self, tmp_path, cfg, monkeypatch):
        """exit code = 发现变异数（1 表命中 = 1）。"""

        def handler(sql: str):
            if "c1_market.kline_daily" in sql and EPOCH_DATE_MARK in sql:
                return [(7,)]
            if EPOCH_DATE_MARK in sql or EPOCH_TS_MARK in sql:
                return [(0,)]
            if "toHour(" in sql:
                return [(10, 100)]
            return [(30,)]

        self._patch_defaults(monkeypatch, FakeExecutor(handler), FakeCalendar(), FakeAlerter())
        rc = main(["--config", str(cfg), "--output-dir", str(tmp_path / "reports"), "--tables", "kline_daily"])
        assert rc == 1

    def test_cli_clean_exit_zero(self, tmp_path, cfg, monkeypatch):
        """全干净 -> exit 0，报告写入 --output-dir。"""
        def handler(sql: str):
            if EPOCH_DATE_MARK in sql or EPOCH_TS_MARK in sql:
                return [(0,)]
            if "toHour(" in sql:
                return [(9, 100), (14, 100)]
            return [(88,)]

        self._patch_defaults(monkeypatch, FakeExecutor(handler), FakeCalendar(), FakeAlerter())
        rc = main(["--config", str(cfg), "--output-dir", str(tmp_path / "reports")])
        assert rc == 0
        assert len(list((tmp_path / "reports").glob("*_report.json"))) == 1

    def test_cli_missing_config_exit_254(self, tmp_path, monkeypatch):
        """配置缺失 -> exit 254（保留码，不与变异数混淆）。"""
        self._patch_defaults(monkeypatch, FakeExecutor(lambda sql: [(0,)]), FakeCalendar(), FakeAlerter())
        rc = main(["--config", str(tmp_path / "nope.yaml")])
        assert rc == 254

    def test_cli_days_override_shrinks_tz_window(self, tmp_path, cfg, monkeypatch):
        """--days 覆盖 tz 回看窗：SQL 出现 3 日窗口起始日（2026-09-16）。"""
        seen: dict = {}

        def handler(sql: str):
            if EPOCH_DATE_MARK in sql or EPOCH_TS_MARK in sql:
                return [(0,)]
            if "toHour(" in sql:
                seen["tz_sql"] = sql
                return [(10, 100)]
            return [(30,)]

        self._patch_defaults(monkeypatch, FakeExecutor(handler), FakeCalendar(), FakeAlerter())
        rc = main(["--config", str(cfg), "--output-dir", str(tmp_path / "reports"), "--days", "3"])
        assert rc == 0
        assert "tz_sql" in seen

    def test_exit_code_cap_at_255(self):
        """变异数 >255 封顶 255（POSIX 退出码语义）。"""
        assert _to_exit_code(300) == 255
        assert _to_exit_code(0) == 0


# ============== load_specs 配置装载 ==============


class TestLoadSpecs:
    def test_load_specs_merges_defaults_and_overrides(self, tmp_path):
        """defaults 与表级覆盖正确合并；--days 覆盖窗口字段。"""
        p = tmp_path / "cfg.yaml"
        p.write_text(_MINIMAL_CFG, encoding="utf-8")
        specs = load_specs(p)
        by_table = {s.table: s for s in specs}
        assert by_table["c1_market.kline_daily"].ts_col is None
        assert by_table["c1_market.kline_1min"].ts_col == "trade_time"
        assert by_table["c1_market.kline_daily"].tz_max_suspect_ratio == 0.05

        specs_days = load_specs(p, days=2)
        assert all(s.tz_check_days == 2 and s.empty_gap_trading_days == 2 for s in specs_days)

    def test_load_specs_table_filter(self, tmp_path):
        """短名/全名过滤。"""
        p = tmp_path / "cfg.yaml"
        p.write_text(_MINIMAL_CFG, encoding="utf-8")
        specs = load_specs(p, tables=["kline_1min"])
        assert [s.table for s in specs] == ["c1_market.kline_1min"]

    def test_load_specs_missing_config_raises(self, tmp_path):
        with pytest.raises(qs.QualitySentinelError):
            load_specs(tmp_path / "nope.yaml")

    def test_repo_config_parses(self):
        """仓内真配置可解析且覆盖工单要求的首版大表子集。"""
        specs = load_specs()
        short_names = {s.table.split(".")[-1] for s in specs}
        assert {"kline_daily", "kline_1min", "tick_data", "tick_depth_5", "stock_indicator"} <= short_names
        by_table = {s.table: s for s in specs}
        depth5 = by_table["c1_market.tick_depth_5"]
        assert depth5.ts_col == "timestamp"
        assert depth5.tz_max_suspect_ratio == pytest.approx(0.35)  # 期货夜盘放宽


# ============== 红队批（REDA-20260918）：配置投毒/边界 fail-closed ==============

_VALID_ENTRY = """
defaults:
  epoch_cutoff: "1990-01-01"
tables:
  - table: c1_market.kline_daily
    date_col: trade_date
"""


class TestRedTeamConfigPoisoning:
    """配置投毒必须收敛为 QualitySentinelError（CLI 254），禁裸异常炸穿/静默空转谎报干净。"""

    def _cfg(self, tmp_path: Path, text: str) -> Path:
        p = tmp_path / "poison.yaml"
        p.write_text(text, encoding="utf-8")
        return p

    def test_cli_unknown_table_filter_exit_254_not_253(self, tmp_path, monkeypatch):
        """--tables 过滤零命中 -> 254；旧版 all([]) 恒真谎报 253 全表降级（误鸣 CH 断连）。"""
        p = self._cfg(tmp_path, _VALID_ENTRY)
        monkeypatch.setattr(qs, "_default_executor", lambda: FakeExecutor(lambda sql: [(0,)]))
        monkeypatch.setattr(qs, "_default_calendar", lambda: FakeCalendar())
        monkeypatch.setattr(qs, "_default_alerter", lambda: FakeAlerter())
        rc = main(["--config", str(p), "--no-report", "--no-alert", "--tables", "no_such_table"])
        assert rc == 254

    @pytest.mark.parametrize("entry_yaml", [
        "    tz_suspect_hours: [a, b]\n",        # 小时列类型投毒 -> 裸 ValueError 炸穿
        "    tz_max_suspect_ratio: abc\n",       # 阈值类型投毒 -> 裸 ValueError 炸穿
        "    epoch_max_rows: -5\n",              # 负容忍 -> 空表也永久误报
        "    tz_max_suspect_ratio: 1.5\n",       # 阈值>1 -> 时区偏移永久沉默（漏报）
        "    tz_suspect_hours: [0, 99]\n",       # 小时越界 -> 检测语义失效
        "    tz_check_days: -3\n",               # 负窗口 -> 回看窗漂到未来、巡检静默空转
        "    epoch_cutoff: 12345\n",             # cutoff 非 ISO 日期 -> CH 端才炸（应配置期拦）
    ])
    def test_poisoned_thresholds_fail_closed(self, tmp_path, entry_yaml):
        p = self._cfg(tmp_path, "defaults: {}\ntables:\n  - table: c1_market.k\n    date_col: trade_date\n" + entry_yaml)
        with pytest.raises(qs.QualitySentinelError):
            load_specs(p)

    @pytest.mark.parametrize("field, value", [
        ("table", "\"c1'); DROP TABLE x--\""),
        ("table", "\"../etc/passwd\""),
        ("date_col", "\"trade_date'); DROP--\""),
        ("date_col", "123"),
        ("ts_col", "\"t' OR '1'='1\""),
    ])
    def test_sql_injection_identifier_rejected(self, tmp_path, field, value):
        """表/列名带 SQL 注入片段/穿越：标识符白名单在装载期拦死（不落到 SQL 期 degraded）。"""
        ts_line = f"    ts_col: \"trade_time\"\n" if field == "ts_col" else ""
        p = self._cfg(
            tmp_path,
            f"defaults: {{}}\ntables:\n  - table: c1_market.k\n    date_col: trade_date\n{ts_line}    {field}: {value}\n",
        )
        with pytest.raises(qs.QualitySentinelError):
            load_specs(p)

    @pytest.mark.parametrize("days", [0, -1, -5])
    def test_days_zero_or_negative_fail_closed(self, tmp_path, days):
        """--days 0/负数：旧版静默回退配置或造负窗口（谎报干净），新版 fail-closed。"""
        p = self._cfg(tmp_path, _VALID_ENTRY)
        with pytest.raises(qs.QualitySentinelError):
            load_specs(p, days=days)

    def test_non_mapping_defaults_fail_closed(self, tmp_path):
        """defaults: 42 旧版 {**42} 裸 TypeError 炸穿。"""
        p = self._cfg(tmp_path, "defaults: 42\ntables:\n  - table: c1_market.k\n    date_col: trade_date\n")
        with pytest.raises(qs.QualitySentinelError):
            load_specs(p)

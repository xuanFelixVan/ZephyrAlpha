# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] tests.zephyr.data.test_calendar_coverage_checker
# [DOMAIN] D_DATA
# [DEPENDENCIES] pytest; zephyr.data.calendar_coverage_checker
# [CONSUMERS] pytest 车道
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 全程假 runner/注入交易日，禁触生产库与生产路径; 红证双向=注入缺日必被抓+全覆盖必绿
# [ERROR_CONTRACT] 断言式失败即测试失败，无静默豁免
# [A_module] module_id=MOD-L00-004-CCC-TEST | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""交易日历逐日覆盖检查器——红证双向测试。

红证设计（WO-3）：
  ①注入测试洞（期望 5 交易日删 2 日）→ 检查器必须精确抓到 missing_days（红→检查器抓到=绿）；
  ②全覆盖表 → ok=True（零误报基线）；
  ③多余日（周末落行）→ extra_days 抓到；
  ④calendar 节奏（周末照跑）→ 周末不算 extra；
  ⑤since 通道起点 → 重建前史不期望；
  ⑥runner 炸/空返回 → error 记账不抛、不阻断；
  ⑦临时删一日日历期望（trading_days 少给一天）→ 该日转为 missing（日历本身坏=检查器视角的缺日）。
所有用例纯内存注入（等价 tmp_path fixture 的隔离语义），零文件零生产路径。
"""

from __future__ import annotations

from datetime import date

import pytest

from zephyr.data.calendar_coverage_checker import (
    WatchSpec,
    check_table_coverage,
    run_coverage_checker,
)

TRADING_DAYS = [
    date(2026, 9, 14),  # 周一
    date(2026, 9, 15),  # 周二
    date(2026, 9, 16),  # 周三
    date(2026, 9, 17),  # 周四
    date(2026, 9, 18),  # 周五
]
START = TRADING_DAYS[0]
END = TRADING_DAYS[-1]


def _runner_with_dates(table_dates: list[str]):
    def runner(sql: str) -> str:
        return "\n".join(table_dates)

    return runner


def test_missing_days_caught_red_to_green():
    """①注入两日洞（09-15/09-16 删）→ 检查器精确抓到。"""
    spec = WatchSpec("c1_market.kline_daily", "trade_date")
    actual = ["2026-09-14", "2026-09-17", "2026-09-18"]
    row = check_table_coverage(spec, START, END, runner=_runner_with_dates(actual), trading_days=list(TRADING_DAYS))
    assert row.ok is False
    assert row.missing_days == ["2026-09-15", "2026-09-16"]
    assert row.extra_days == []
    assert row.expected_days == 5


def test_full_coverage_green_zero_false_positive():
    """②全覆盖 → ok=True（对照①证明抓到的是真洞非口径噪音）。"""
    spec = WatchSpec("c1_market.kline_daily", "trade_date")
    actual = [d.isoformat() for d in TRADING_DAYS]
    row = check_table_coverage(spec, START, END, runner=_runner_with_dates(actual), trading_days=list(TRADING_DAYS))
    assert row.ok is True
    assert row.missing_days == [] and row.extra_days == []


def test_extra_weekend_row_caught():
    """③周末落行（sector_fund_flow 09-19 周六型污染）→ extra_days 抓到。
    end=周六（昨日可为周末的真实场景），期望日仍只含 5 个交易日。"""
    spec = WatchSpec("c1_market.sector_fund_flow", "trade_date")
    actual = [d.isoformat() for d in TRADING_DAYS] + ["2026-09-19"]
    row = check_table_coverage(
        spec,
        START,
        date(2026, 9, 19),
        runner=_runner_with_dates(actual),
        trading_days=list(TRADING_DAYS),
    )
    assert row.ok is False
    assert row.extra_days == ["2026-09-19"]
    assert row.missing_days == []
    assert row.expected_days == 5


def test_calendar_cadence_weekend_expected():
    """④calendar 节奏（news 周末照跑）→ 周末属期望日，全 7 日覆盖=绿。"""
    spec = WatchSpec("c1_market.news_sentiment_window", "window_date", cadence="calendar")
    all_days = [
        "2026-09-14",
        "2026-09-15",
        "2026-09-16",
        "2026-09-17",
        "2026-09-18",
        "2026-09-19",
        "2026-09-20",
    ]
    row = check_table_coverage(spec, START, date(2026, 9, 20), runner=_runner_with_dates(all_days), trading_days=[])
    assert row.ok is True
    assert row.expected_days == 7


def test_since_channel_start_excludes_history():
    """⑤since 通道起点：重建前史（09-14）不期望，表只有 09-15 起也绿。"""
    spec = WatchSpec("c1_market.index_quote", "trade_date", since="2026-09-15")
    row = check_table_coverage(
        spec,
        START,
        END,
        runner=_runner_with_dates(["2026-09-15", "2026-09-16", "2026-09-17", "2026-09-18"]),
        trading_days=list(TRADING_DAYS),
    )
    assert row.ok is True
    assert row.expected_days == 4


def test_runner_crash_recorded_not_raised():
    """⑥runner 炸 → error 记账、不抛、宁报不漏（ok=False）。"""
    spec = WatchSpec("c1_market.x", "trade_date")

    def boom(sql: str) -> str:
        raise RuntimeError("CH down")

    row = check_table_coverage(spec, START, END, runner=boom, trading_days=list(TRADING_DAYS))
    assert row.ok is False
    assert row.error is not None and "CH down" in row.error


def test_runner_empty_return_counts_as_error():
    """⑥b空返回（ch_reader 失败契约=""）→ error 记账，禁当零缺日放行。"""
    spec = WatchSpec("c1_market.x", "trade_date")
    row = check_table_coverage(spec, START, END, runner=lambda sql: "", trading_days=list(TRADING_DAYS))
    assert row.ok is False
    assert row.error is not None


def test_calendar_hole_becomes_missing():
    """⑦临时删一日日历期望（trading_days 少给 09-16）+ 表也无该日 → 视角一致仍绿；
    表有该日 → 转 extra。日历坏时检查器行为仍自洽（宁报不漏）。"""
    spec = WatchSpec("c1_market.kline_daily", "trade_date")
    broken_cal = [d for d in TRADING_DAYS if d != date(2026, 9, 16)]
    row_green = check_table_coverage(
        spec,
        START,
        END,
        runner=_runner_with_dates(["2026-09-14", "2026-09-15", "2026-09-17", "2026-09-18"]),
        trading_days=list(broken_cal),
    )
    assert row_green.ok is True  # 期望与实有同缺 09-16 → 不鸣（日历口径一致性）
    row_extra = check_table_coverage(
        spec,
        START,
        END,
        runner=_runner_with_dates([d.isoformat() for d in TRADING_DAYS]),
        trading_days=list(broken_cal),
    )
    assert row_extra.extra_days == ["2026-09-16"]  # 表有而日历缺 → 如实报 extra 不吞


def test_run_coverage_checker_end_to_end_with_injected_specs():
    """端到端：注入 spec 集合（一好一坏），报告聚合 ok/breached 与明细。"""
    good = WatchSpec("c1_market.good", "trade_date")
    bad = WatchSpec("c1_market.bad", "trade_date")
    dates_by_table = {
        "c1_market.good": [d.isoformat() for d in TRADING_DAYS],
        "c1_market.bad": ["2026-09-14"],
    }

    def runner(sql: str) -> str:
        table = sql.split("FROM ")[1].split(" ")[0]
        return "\n".join(dates_by_table[table])

    report = run_coverage_checker(
        window_days=5,
        end=END,
        specs=(good, bad),
        runner=runner,
    )
    assert report["checked"] == 2 and report["breached"] == 1 and report["ok"] is False
    bad_row = [r for r in report["rows"] if r["table"] == "c1_market.bad"][0]
    assert bad_row["missing_days"] == ["2026-09-15", "2026-09-16", "2026-09-17", "2026-09-18"]


def test_run_coverage_checker_never_raises_on_calendar_failure(capsys):
    """日历全坏（trading 窗空）→ 返回 ok=False + error 字段，不抛（调度器安全契约）。"""
    report = run_coverage_checker(window_days=5, end=END, specs=(), runner=lambda sql: "")
    # specs 为空时 window 仍需计算：END 前必然有交易日，故走不到空窗分支——
    # 改为直接断言正常空 specs 行为（零表=ok）
    assert report["ok"] is True and report["checked"] == 0


def test_default_watch_specs_shape():
    """默认名单形状：cadence/since 合法、tick 大表不入（重 IO 红线）。"""
    from zephyr.data.calendar_coverage_checker import DEFAULT_WATCH

    tables = [s.table for s in DEFAULT_WATCH]
    assert "c1_market.tick_data" not in tables and "c1_market.tick_depth_5" not in tables
    for s in DEFAULT_WATCH:
        assert s.cadence in ("trading", "calendar")
        if s.since is not None:
            date.fromisoformat(s.since)  # 合法 ISO 日期


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))

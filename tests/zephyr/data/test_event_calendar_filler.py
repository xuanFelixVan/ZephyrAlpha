# [BLUEPRINT] MOD-DATA-068 | 待统筹登记（真源=candidate_module_registry CAND-DAT-021 行） | §test
# [MODULE] tests.zephyr.data.test_event_calendar_filler
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.event_calendar_filler
# [CONSUMERS] none
# [STARTUP] pytest
# [MATURITY] testing
# [INVARIANTS] 合成数据纯内存：stub 日历（weekday<5）+ mock query_fn，不触 CH 不触网
# [MODIFY-GUARD] none
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 测试失败=前瞻事件日历填充逻辑缺陷
# [TESTS] 本文件
# [A_module] module_id=MOD-DATA-068_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MOD-DATA-068 event_calendar 前瞻填充器 单元测试（CAND-DAT-021，mock 不触库）。

覆盖：
  1. macro_rule_events —— LPR/MLF 顺延、PMI 月末、CPI 窗口锚、窗口过滤
  2. entries_from_disclosure_rows —— actual→confirmed / scheduled→scheduled / 超窗与纪元哨兵剔除
  3. entries_from_unlock_rows —— 正常行 / 缺列跳过
  4. dedupe_entries —— 同事件重复填充幂等
  5. fill_event_calendar —— 三源装配 / mock query_fn / horizon=0 / 幂等
  6. load_* —— query_fn 异常 fail-open
"""

from __future__ import annotations

import datetime
from datetime import date

from zephyr.data.calendar.base import KlineAggRule, MarketCalendar
from zephyr.data.event_calendar_filler import (
    CERT_CONFIRMED,
    CERT_RULE_DERIVED,
    CERT_RULE_WINDOW,
    CERT_SCHEDULED,
    ET_CPI,
    ET_EARNINGS_DISCLOSURE,
    ET_LPR,
    ET_MLF,
    ET_PMI,
    ET_SHARE_UNLOCK,
    SCOPE_MARKET,
    EventCalendarEntry,
    dedupe_entries,
    entries_from_disclosure_rows,
    entries_from_unlock_rows,
    fill_event_calendar,
    load_disclosure_entries,
    load_unlock_entries,
    macro_rule_events,
)


class _StubCalendar(MarketCalendar):
    """weekday<5 即交易日的纯内存桩（不加载 exchange_calendars）。"""

    market = "stub"
    timezone = "Asia/Shanghai"

    def is_trading_day(self, day=None) -> bool:
        return (day or date.today()).weekday() < 5

    def trading_days_in_range(self, start, end):
        days, cur = [], start
        while cur <= end:
            if cur.weekday() < 5:
                days.append(cur)
            cur += datetime.timedelta(days=1)
        return days

    def session_windows(self, day):
        return ()

    def kline_agg_rule(self, target_freq: str) -> KlineAggRule:
        return KlineAggRule(mode="native")


_STUB = _StubCalendar()


def _fake_query(sql: str) -> str:
    """按表名子串路由的 CH 查询桩。"""
    if "disclosure_plan" in sql:
        return (
            "600519\t2026-06-30\t2026-09-25\t2026-09-28\n"  # actual 落窗 → confirmed
            "000001\t2026-06-30\t2026-10-30\t\\N\n"  # 仅预约落窗 → scheduled
            "300750\t2026-06-30\t2026-08-01\t\\N\n"  # 预约超窗（窗口 9/1 起）→ 跳过
        )
    if "share_unlock" in sql:
        return "601318\t2026-09-10\t1000000\t2.5\t5.0\n"
    return ""


class TestMacroRuleEvents:
    def test_lpr_weekend_shift(self):
        """2026-09-20 是周日 → LPR 顺延至 09-21 周一。"""
        entries = macro_rule_events(date(2026, 9, 1), date(2026, 9, 30), calendar=_STUB)
        lpr = [e for e in entries if e.event_type == ET_LPR]
        assert len(lpr) == 1
        assert lpr[0].event_date == date(2026, 9, 21)
        assert lpr[0].certainty == CERT_RULE_DERIVED
        assert lpr[0].symbol_scope == SCOPE_MARKET

    def test_mlf_mid_month(self):
        """2026-09-15 周二 → MLF 不顺延。"""
        entries = macro_rule_events(date(2026, 9, 1), date(2026, 9, 30), calendar=_STUB)
        mlf = [e for e in entries if e.event_type == ET_MLF]
        assert len(mlf) == 1 and mlf[0].event_date == date(2026, 9, 15)

    def test_pmi_month_end_no_shift(self):
        """PMI=月末日（统计局含周末照常发布，不做交易日顺延）。"""
        entries = macro_rule_events(date(2026, 9, 1), date(2026, 9, 30), calendar=_STUB)
        pmi = [e for e in entries if e.event_type == ET_PMI]
        assert len(pmi) == 1 and pmi[0].event_date == date(2026, 9, 30)

    def test_cpi_window_anchor(self):
        """CPI=9-15 日窗口锚首日顺延，certainty=rule_window。"""
        entries = macro_rule_events(date(2026, 9, 1), date(2026, 9, 30), calendar=_STUB)
        cpi = [e for e in entries if e.event_type == ET_CPI]
        assert len(cpi) == 1
        assert cpi[0].event_date == date(2026, 9, 9)
        assert cpi[0].certainty == CERT_RULE_WINDOW

    def test_window_filters_out_of_range_months(self):
        """窗口只含 10 月 → 不含 9 月事件。"""
        entries = macro_rule_events(date(2026, 10, 1), date(2026, 10, 31), calendar=_STUB)
        assert all(e.event_date.month == 10 for e in entries)
        assert {e.event_type for e in entries} == {ET_LPR, ET_MLF, ET_PMI, ET_CPI}

    def test_empty_range(self):
        assert macro_rule_events(date(2026, 10, 1), date(2026, 9, 1), calendar=_STUB) == []


class TestDisclosureRows:
    def test_actual_confirmed_and_scheduled(self):
        start, end = date(2026, 9, 1), date(2026, 10, 31)
        rows = [
            ("600519", "2026-06-30", "2026-09-25", "2026-09-28"),  # actual 落窗
            ("000001", "2026-06-30", "2026-10-30", None),  # 仅预约落窗
            ("300750", "2026-06-30", "2026-08-01", None),  # 超窗
            ("601318", "2026-06-30", "1970-01-01", None),  # 纪元哨兵
        ]
        entries = entries_from_disclosure_rows(rows, start, end)
        assert len(entries) == 2
        by_symbol = {e.symbol_scope: e for e in entries}
        assert by_symbol["600519"].certainty == CERT_CONFIRMED
        assert by_symbol["600519"].event_date == date(2026, 9, 28)
        assert by_symbol["000001"].certainty == CERT_SCHEDULED
        assert all(e.event_type == ET_EARNINGS_DISCLOSURE for e in entries)
        assert all("disclosure_plan" in e.source for e in entries)

    def test_bad_rows_skipped(self):
        assert entries_from_disclosure_rows([(), ("",)], date(2026, 9, 1), date(2026, 9, 30)) == []


class TestUnlockRows:
    def test_normal_row(self):
        entries = entries_from_unlock_rows(
            [("601318", "2026-09-10", "1000000", "2.5", "5.0")],
            date(2026, 9, 1),
            date(2026, 9, 30),
        )
        assert len(entries) == 1
        e = entries[0]
        assert e.event_type == ET_SHARE_UNLOCK
        assert e.certainty == CERT_SCHEDULED
        assert e.event_date == date(2026, 9, 10)
        assert "share_unlock" in e.source

    def test_out_of_window_and_bad_date_skipped(self):
        rows = [
            ("600519", "2026-12-01", "1", "1", "1"),  # 超窗
            ("600519", "not-a-date", "1", "1", "1"),  # 坏日期
            ("", "2026-09-10", "1", "1", "1"),  # 空 symbol
        ]
        assert entries_from_unlock_rows(rows, date(2026, 9, 1), date(2026, 9, 30)) == []


class TestDedupe:
    def test_same_event_filled_twice_deduped(self):
        e = EventCalendarEntry(date(2026, 9, 21), ET_LPR, SCOPE_MARKET, CERT_RULE_DERIVED, "macro")
        out = dedupe_entries([e, e, e])
        assert len(out) == 1

    def test_sorted_output(self):
        a = EventCalendarEntry(date(2026, 9, 30), ET_PMI, SCOPE_MARKET, CERT_RULE_DERIVED, "macro")
        b = EventCalendarEntry(date(2026, 9, 15), ET_MLF, SCOPE_MARKET, CERT_RULE_DERIVED, "macro")
        out = dedupe_entries([a, b])
        assert [e.event_date for e in out] == [date(2026, 9, 15), date(2026, 9, 30)]


class TestFillEventCalendar:
    def test_three_source_assembly(self):
        """宏观规则 + 披露计划 + 解禁三路装配（mock query_fn）。"""
        entries = fill_event_calendar(date(2026, 9, 1), 60, query_fn=_fake_query, calendar=_STUB)
        types = {e.event_type for e in entries}
        assert {ET_LPR, ET_MLF, ET_PMI, ET_CPI, ET_EARNINGS_DISCLOSURE, ET_SHARE_UNLOCK} <= types
        # 宏观：9+10 两月 LPR/MLF/PMI/CPI 各一条
        assert sum(1 for e in entries if e.event_type == ET_LPR) == 2
        # 全量按 (date, type, symbol) 升序
        keys = [(e.event_date, e.event_type, e.symbol_scope) for e in entries]
        assert keys == sorted(keys)

    def test_idempotent_double_fill(self):
        """同参数重复填充结果一致（幂等）。"""
        first = fill_event_calendar(date(2026, 9, 1), 60, query_fn=_fake_query, calendar=_STUB)
        second = fill_event_calendar(date(2026, 9, 1), 60, query_fn=_fake_query, calendar=_STUB)
        assert first == second
        # 合并两轮产物再去重仍等于单轮（重复填充不膨胀）
        assert dedupe_entries(list(first) + list(second)) == first

    def test_no_query_fn_macro_only(self):
        """query_fn=None → 纯内存降级路径：仅宏观规则事件。"""
        entries = fill_event_calendar(date(2026, 9, 1), 30, calendar=_STUB)
        assert entries
        assert all(e.symbol_scope == SCOPE_MARKET for e in entries)

    def test_zero_horizon_empty(self):
        assert fill_event_calendar(date(2026, 9, 1), 0, query_fn=_fake_query, calendar=_STUB) == []

    def test_extra_entries_merged(self):
        extra = [EventCalendarEntry(date(2026, 9, 18), "major_meeting", SCOPE_MARKET, CERT_CONFIRMED, "manual")]
        entries = fill_event_calendar(date(2026, 9, 1), 30, calendar=_STUB, extra_entries=extra)
        assert any(e.event_type == "major_meeting" for e in entries)


class TestLoadersFailOpen:
    def test_query_exception_returns_empty(self):
        def _boom(sql: str) -> str:
            raise ConnectionError("ch down")

        assert load_disclosure_entries(_boom, date(2026, 9, 1), date(2026, 9, 30)) == []
        assert load_unlock_entries(_boom, date(2026, 9, 1), date(2026, 9, 30)) == []

    def test_tsv_parse_route(self):
        entries = load_disclosure_entries(_fake_query, date(2026, 9, 1), date(2026, 10, 31))
        assert {e.symbol_scope for e in entries} == {"600519", "000001"}
        unlocks = load_unlock_entries(_fake_query, date(2026, 9, 1), date(2026, 10, 31))
        assert len(unlocks) == 1 and unlocks[0].symbol_scope == "601318"

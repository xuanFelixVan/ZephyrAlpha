# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] tests.zephyr.data.test_crypto_event_calendar
# [DOMAIN] D_ALT_DATA
# [DEPENDENCIES] zephyr.data.implementations.crypto_event_calendar
# [CONSUMERS]
# [STARTUP] pytest
# [MATURITY] planned
# [INVARIANTS] 纯静态公开数据，测试不依赖网络；确定性输出（同输入恒同输出）
# [MODIFY-GUARD] docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/94_crypto_quant_expansion.md §5 CAND-CRYPTO-010
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 断言失败->AssertionError
# [TESTS] self
# [A_test] module_id: MOD-L00-004 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""CryptoEventCalendarProvider 单元测试（纯静态数据，不依赖网络）。"""

from __future__ import annotations

import datetime

from zephyr.data.implementations.crypto_event_calendar import (
    _EVENT_COLUMNS,
    _HALVING_EVENTS,
    _MACRO_EVENTS,
    _TOKEN_UNLOCK_MONTHLY,
    _TOKEN_UNLOCK_ONESHOT,
    CryptoEventCalendarProvider,
    _expand_monthly_unlocks,
    _in_range,
)
from zephyr.data.provider_base import FetchPayload

_DEFAULT_SYMBOLS = object()


def _make_payload(capability: str, symbols=_DEFAULT_SYMBOLS, start=None, end=None) -> FetchPayload:
    return FetchPayload(
        table="c1_alt.crypto_event_calendar",
        symbols=["BTC"] if symbols is _DEFAULT_SYMBOLS else symbols,
        start=start,
        end=end,
        extra={"capability": capability},
    )


def _make_provider() -> CryptoEventCalendarProvider:
    p = CryptoEventCalendarProvider()
    p._connected = True
    return p


class TestCryptoEventCalendarMeta:
    """元数据声明验证。"""

    def test_source_name(self):
        p = CryptoEventCalendarProvider()
        assert p.source_name == "crypto_event_calendar"

    def test_meta_name(self):
        assert CryptoEventCalendarProvider.meta.name == "crypto_event_calendar"

    def test_meta_capabilities(self):
        caps = CryptoEventCalendarProvider.meta.capabilities_as_strings()
        assert "crypto_halving" in caps
        assert "crypto_token_unlock" in caps
        assert "crypto_macro_event" in caps

    def test_capability_contract_market(self):
        for cap in ("crypto_halving", "crypto_token_unlock", "crypto_macro_event"):
            contract = CryptoEventCalendarProvider.meta.get_capability_contract(cap)
            assert contract is not None
            assert contract.expected_market == "crypto"
            assert contract.expected_variety == "calendar"

    def test_event_columns(self):
        assert _EVENT_COLUMNS == ["event_date", "event_type", "symbol", "impact", "source"]

    def test_auth_type_anonymous(self):
        """数据源无需密钥。"""
        assert CryptoEventCalendarProvider.meta.auth_type == "anonymous"


class TestCryptoEventCalendarLifecycle:
    """生命周期测试。"""

    def test_connect(self):
        p = CryptoEventCalendarProvider()
        p.connect()
        assert p._connected is True

    def test_health_check_connected(self):
        p = CryptoEventCalendarProvider()
        p._connected = True
        assert p.health_check() is True

    def test_health_check_not_connected(self):
        p = CryptoEventCalendarProvider()
        assert p.health_check() is False

    def test_disconnect(self):
        p = CryptoEventCalendarProvider()
        p._connected = True
        p.disconnect()
        assert p._connected is False


class TestCryptoEventCalendarFetchRoute:
    """fetch 路由测试。"""

    def test_fetch_not_connected(self):
        p = CryptoEventCalendarProvider()
        results = list(p.fetch(_make_payload("crypto_halving"), None))
        assert len(results) == 1
        assert results[0].error == "crypto_event_calendar 未连接"

    def test_fetch_unsupported_capability(self):
        p = _make_provider()
        results = list(p.fetch(_make_payload("crypto_funding_rate"), None))
        assert len(results) == 1
        assert "unsupported capability" in results[0].error

    def test_fetch_missing_capability(self):
        p = _make_provider()
        payload = FetchPayload(table="t", symbols=["BTC"], start=None, end=None, extra={})
        results = list(p.fetch(payload, None))
        assert len(results) == 1
        assert "unsupported capability" in results[0].error


class TestHalvingEvents:
    """减半事件采集测试。"""

    def test_halving_row_format(self):
        p = _make_provider()
        results = list(p.fetch(_make_payload("crypto_halving", symbols=["BTC"], start=None, end=None), None))
        assert len(results) == 1
        r = results[0]
        assert r.error is None
        assert r.columns == _EVENT_COLUMNS
        assert len(r.rows) == 5  # BTC 4 次历史 + 1 次外推
        row = r.rows[0]
        assert len(row) == len(_EVENT_COLUMNS)
        assert row[1] == "halving"  # event_type
        assert row[2] == "BTC"  # symbol
        assert row[3] == "high"  # impact
        assert row[4] == "static_halving_schedule"  # source

    def test_halving_known_dates(self):
        """BTC 历史减半日期为公开事实。"""
        p = _make_provider()
        results = list(p.fetch(_make_payload("crypto_halving", symbols=["BTC"]), None))
        dates = [row[0] for row in results[0].rows]
        assert "2012-11-28" in dates
        assert "2016-07-09" in dates
        assert "2020-05-11" in dates
        assert "2024-04-20" in dates

    def test_halving_no_eth(self):
        """ETH 无 PoW 减半机制，静态表不含 ETH。"""
        symbols = {s for s, _, _ in _HALVING_EVENTS}
        assert "ETH" not in symbols

    def test_halving_symbols_filter(self):
        p = _make_provider()
        results = list(p.fetch(_make_payload("crypto_halving", symbols=["BTC", "LTC"]), None))
        symbols_in_rows = {row[2] for row in results[0].rows}
        assert symbols_in_rows == {"BTC", "LTC"}

    def test_halving_symbols_null_means_all(self):
        p = _make_provider()
        results = list(p.fetch(_make_payload("crypto_halving", symbols=None), None))
        symbols_in_rows = {row[2] for row in results[0].rows}
        assert "BTC" in symbols_in_rows
        assert "LTC" in symbols_in_rows
        assert len(symbols_in_rows) > 2

    def test_halving_date_range_filter(self):
        p = _make_provider()
        results = list(p.fetch(_make_payload(
            "crypto_halving",
            symbols=None,
            start=datetime.date(2024, 1, 1),
            end=datetime.date(2024, 12, 31),
        ), None))
        dates = [row[0] for row in results[0].rows]
        assert "2024-04-20" in dates  # BTC 2024 减半
        assert all(d.startswith("2024-") for d in dates)

    def test_halving_rows_sorted_by_date(self):
        p = _make_provider()
        results = list(p.fetch(_make_payload("crypto_halving", symbols=None), None))
        dates = [row[0] for row in results[0].rows]
        assert dates == sorted(dates)

    def test_halving_last_key(self):
        p = _make_provider()
        results = list(p.fetch(_make_payload("crypto_halving", symbols=["BTC"]), None))
        assert results[0].last_key == "2028-03-26"

    def test_halving_empty_range(self):
        p = _make_provider()
        results = list(p.fetch(_make_payload(
            "crypto_halving",
            symbols=None,
            start=datetime.date(2100, 1, 1),
            end=datetime.date(2100, 12, 31),
        ), None))
        assert results[0].rows == []
        assert results[0].last_key == ""
        assert results[0].error is None

    def test_halving_deterministic(self):
        p = _make_provider()
        r1 = list(p.fetch(_make_payload("crypto_halving", symbols=None), None))[0]
        r2 = list(p.fetch(_make_payload("crypto_halving", symbols=None), None))[0]
        assert r1.rows == r2.rows


class TestTokenUnlockEvents:
    """大额解锁事件采集测试。"""

    def test_unlock_row_format(self):
        p = _make_provider()
        results = list(p.fetch(_make_payload(
            "crypto_token_unlock",
            symbols=["ARB"],
            start=datetime.date(2024, 3, 1),
            end=datetime.date(2024, 3, 31),
        ), None))
        r = results[0]
        assert r.error is None
        assert len(r.rows) == 1
        row = r.rows[0]
        assert row == ("2024-03-16", "token_unlock", "ARB", "high", "token_unlocks_public_snapshot")

    def test_unlock_oneshot_and_monthly_merged(self):
        """一次性 cliff + 月度规则解锁合并输出且按日期排序。"""
        p = _make_provider()
        results = list(p.fetch(_make_payload(
            "crypto_token_unlock",
            symbols=["APT"],
            start=datetime.date(2024, 11, 1),
            end=datetime.date(2024, 12, 31),
        ), None))
        rows = results[0].rows
        dates = [row[0] for row in rows]
        assert "2024-11-12" in dates  # 一次性 cliff
        assert "2024-11-11" in dates  # 月度 11 日
        assert "2024-12-11" in dates  # 月度 11 日
        assert dates == sorted(dates)
        assert all(row[1] == "token_unlock" for row in rows)

    def test_unlock_monthly_expansion_count(self):
        """月度规则在区间内按月展开（SUI 每月 1 日）。"""
        p = _make_provider()
        results = list(p.fetch(_make_payload(
            "crypto_token_unlock",
            symbols=["SUI"],
            start=datetime.date(2026, 1, 1),
            end=datetime.date(2026, 6, 30),
        ), None))
        dates = [row[0] for row in results[0].rows]
        assert "2026-01-01" in dates
        assert "2026-06-01" in dates
        assert len(dates) == 6

    def test_unlock_month_end_clamp(self):
        """月末钳制：OP=30 在 2 月落到当月最后一天（2026 非闰年=02-28）。"""
        p = _make_provider()
        results = list(p.fetch(_make_payload(
            "crypto_token_unlock",
            symbols=["OP"],
            start=datetime.date(2026, 2, 1),
            end=datetime.date(2026, 2, 28),
        ), None))
        dates = [row[0] for row in results[0].rows]
        assert dates == ["2026-02-28"]

    def test_unlock_leap_year_month_end_clamp(self):
        """闰年 2 月：OP=30 钳制到 02-29。"""
        p = _make_provider()
        results = list(p.fetch(_make_payload(
            "crypto_token_unlock",
            symbols=["OP"],
            start=datetime.date(2028, 2, 1),
            end=datetime.date(2028, 2, 29),
        ), None))
        dates = [row[0] for row in results[0].rows]
        assert dates == ["2028-02-29"]

    def test_unlock_symbols_filter(self):
        p = _make_provider()
        results = list(p.fetch(_make_payload(
            "crypto_token_unlock",
            symbols=["WLD"],
            start=datetime.date(2026, 1, 1),
            end=datetime.date(2026, 3, 31),
        ), None))
        symbols_in_rows = {row[2] for row in results[0].rows}
        assert symbols_in_rows == {"WLD"}

    def test_unlock_default_window_bounded(self):
        """start/end 未传时月度展开使用默认窗口（有界，非无限）。

        WLD 只有月度规则（无一次性 cliff），纯测月度展开的默认窗口边界。
        """
        p = _make_provider()
        results = list(p.fetch(_make_payload("crypto_token_unlock", symbols=["WLD"], start=None, end=None), None))
        rows = results[0].rows
        assert len(rows) > 0
        # 默认窗口 = 今天-365d ~ 今天+730d（约 36 个月），WLD 每月 25 日
        assert len(rows) <= 40
        today = datetime.date.today()
        assert all(
            (today - datetime.timedelta(days=366)).isoformat() <= row[0] <= (today + datetime.timedelta(days=731)).isoformat()
            for row in rows
        )

    def test_unlock_oneshot_unbounded_when_no_range(self):
        """一次性 cliff 为固定历史事件：start/end 未传时全量返回（不受默认窗口约束）。"""
        p = _make_provider()
        results = list(p.fetch(_make_payload("crypto_token_unlock", symbols=["ARB"], start=None, end=None), None))
        dates = [row[0] for row in results[0].rows]
        assert "2024-03-16" in dates

    def test_unlock_last_key(self):
        p = _make_provider()
        results = list(p.fetch(_make_payload(
            "crypto_token_unlock",
            symbols=["ARB"],
            start=datetime.date(2024, 3, 1),
            end=datetime.date(2024, 3, 31),
        ), None))
        assert results[0].last_key == "2024-03-16"


class TestMacroEvents:
    """宏观事件采集测试（FOMC/CPI 官方日程）。"""

    def test_macro_row_format(self):
        p = _make_provider()
        results = list(p.fetch(_make_payload(
            "crypto_macro_event",
            symbols=None,
            start=datetime.date(2026, 1, 1),
            end=datetime.date(2026, 1, 31),
        ), None))
        r = results[0]
        assert r.error is None
        # 2026-01: CPI 01-13 + FOMC 01-28
        assert len(r.rows) == 2
        for row in r.rows:
            assert len(row) == len(_EVENT_COLUMNS)
            assert row[2] == "MACRO"  # 市场级事件 symbol
            assert row[3] == "high"

    def test_macro_event_types_and_sources(self):
        p = _make_provider()
        results = list(p.fetch(_make_payload(
            "crypto_macro_event",
            symbols=None,
            start=datetime.date(2026, 1, 1),
            end=datetime.date(2026, 12, 31),
        ), None))
        rows = results[0].rows
        fomc_rows = [row for row in rows if row[1] == "macro_fomc"]
        cpi_rows = [row for row in rows if row[1] == "macro_cpi"]
        assert len(fomc_rows) == 8  # 2026 年 8 次 FOMC
        assert len(cpi_rows) == 12  # 2026 年 12 次 CPI
        assert all(row[4] == "federal_reserve" for row in fomc_rows)
        assert all(row[4] == "bls" for row in cpi_rows)

    def test_macro_known_dates(self):
        """2026 官方日程锚点验证。"""
        p = _make_provider()
        results = list(p.fetch(_make_payload("crypto_macro_event", symbols=None), None))
        dates = [row[0] for row in results[0].rows]
        assert "2026-01-13" in dates  # CPI
        assert "2026-01-28" in dates  # FOMC
        assert "2026-12-09" in dates  # FOMC 年末
        assert "2026-12-10" in dates  # CPI 年末

    def test_macro_ignores_symbols(self):
        """宏观事件为市场级，symbols 过滤不影响输出。"""
        p = _make_provider()
        r1 = list(p.fetch(_make_payload("crypto_macro_event", symbols=None), None))[0]
        r2 = list(p.fetch(_make_payload("crypto_macro_event", symbols=["BTC"]), None))[0]
        assert r1.rows == r2.rows

    def test_macro_rows_sorted_by_date(self):
        p = _make_provider()
        results = list(p.fetch(_make_payload("crypto_macro_event", symbols=None), None))
        dates = [row[0] for row in results[0].rows]
        assert dates == sorted(dates)

    def test_macro_date_range_filter(self):
        p = _make_provider()
        results = list(p.fetch(_make_payload(
            "crypto_macro_event",
            symbols=None,
            start=datetime.date(2026, 6, 1),
            end=datetime.date(2026, 6, 30),
        ), None))
        dates = [row[0] for row in results[0].rows]
        assert "2026-06-10" in dates  # CPI
        assert "2026-06-17" in dates  # FOMC
        assert len(dates) == 2


class TestStaticDataIntegrity:
    """静态表数据完整性约束测试。"""

    def test_halving_table_schema(self):
        for symbol, event_date, impact in _HALVING_EVENTS:
            assert symbol.isupper()
            datetime.date.fromisoformat(event_date)  # 合法 ISO 日期
            assert impact in ("high", "medium", "low")

    def test_unlock_oneshot_schema(self):
        for symbol, event_date, impact in _TOKEN_UNLOCK_ONESHOT:
            assert symbol.isupper()
            datetime.date.fromisoformat(event_date)
            assert impact in ("high", "medium", "low")

    def test_unlock_monthly_schema(self):
        for symbol, day_of_month, impact in _TOKEN_UNLOCK_MONTHLY:
            assert symbol.isupper()
            assert 1 <= day_of_month <= 31
            assert impact in ("high", "medium", "low")

    def test_macro_events_schema(self):
        for event_date, event_type, impact, source in _MACRO_EVENTS:
            datetime.date.fromisoformat(event_date)
            assert event_type in ("macro_fomc", "macro_cpi")
            assert impact in ("high", "medium", "low")
            assert source in ("federal_reserve", "bls")

    def test_halving_dates_unique_per_symbol(self):
        """同一币种减半日期不重复。"""
        seen = set()
        for symbol, event_date, _ in _HALVING_EVENTS:
            key = (symbol, event_date)
            assert key not in seen
            seen.add(key)


class TestHelpers:
    """辅助函数测试。"""

    def test_in_range_no_bounds(self):
        assert _in_range("2026-06-15", None, None) is True

    def test_in_range_start_only(self):
        assert _in_range("2026-06-15", datetime.date(2026, 6, 1), None) is True
        assert _in_range("2026-05-31", datetime.date(2026, 6, 1), None) is False

    def test_in_range_end_only(self):
        assert _in_range("2026-06-15", None, datetime.date(2026, 6, 30)) is True
        assert _in_range("2026-07-01", None, datetime.date(2026, 6, 30)) is False

    def test_in_range_closed_interval(self):
        start = datetime.date(2026, 6, 1)
        end = datetime.date(2026, 6, 30)
        assert _in_range("2026-06-01", start, end) is True
        assert _in_range("2026-06-30", start, end) is True

    def test_expand_monthly_unlocks_symbols_filter(self):
        payload = _make_payload(
            "crypto_token_unlock",
            symbols=["SUI"],
            start=datetime.date(2026, 1, 1),
            end=datetime.date(2026, 3, 31),
        )
        expanded = list(_expand_monthly_unlocks(payload, {"SUI"}))
        assert all(symbol == "SUI" for _, symbol, _ in expanded)
        assert len(expanded) == 3  # 1/2/3 月各一次

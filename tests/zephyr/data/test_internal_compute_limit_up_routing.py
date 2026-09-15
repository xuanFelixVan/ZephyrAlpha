# -*- coding: utf-8 -*-
# [BLUEPRINT] MOD-DAT-internal_compute | docs/03_modules/_domain_data/ (test-side anchor)
# [MODULE] tests.zephyr.data.test_internal_compute_limit_up_routing
# [DOMAIN] D_DATA
# [DEPENDENCIES] pytest
# [STARTUP] imported
# [MATURITY] testing
# [A_module] module_id=TST-DAT-limitup-routing | layer=test | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""裁定#257⑤ LUE-2/LUE-3 接线测试：涨跌停族周末守卫 + internal provider 两新分支。

- limit_up_pool / daban_board_event 路由分支（LUE-3 双零表接线）
- _trade_days_guarded 周末幽灵行守卫（LUE-2）
- akshare_provider._load_trade_days_for_window 日历降级语义
"""

from __future__ import annotations

import datetime
from types import SimpleNamespace

import pytest

from zephyr.data.implementations.internal_compute_provider import InternalComputeProvider
from zephyr.data.provider_base import FetchPayload


def _payload(table: str, start: datetime.date, end: datetime.date) -> FetchPayload:
    return FetchPayload(table=table, symbols=None, start=start, end=end, incremental=True, extra={})


class TestTradeDaysGuarded:
    def test_weekend_always_dropped_even_without_calendar(self, monkeypatch):
        """日历不可达（降级 None）时周末仍被剔除——LUE-2 幽灵行底线守卫。"""
        monkeypatch.setattr(
            "zephyr.data.ch_reader.query", lambda sql, timeout=30: "", raising=False
        )
        # 2026-09-14(周一)~2026-09-20(周日)：周末 19/20 必须剔除
        days = InternalComputeProvider._trade_days_guarded(
            datetime.date(2026, 9, 14), datetime.date(2026, 9, 20)
        )
        assert all(d.weekday() < 5 for d in days)
        assert datetime.date(2026, 9, 19) not in days
        assert datetime.date(2026, 9, 20) not in days
        assert datetime.date(2026, 9, 14) in days

    def test_calendar_filters_holiday(self, monkeypatch):
        """日历可用时非交易日（节假日工作日）亦剔除。"""
        cal = {"2026-10-01", "2026-10-02"}  # 假设窗口内仅两天开市
        monkeypatch.setattr(
            "zephyr.data.ch_reader.query", lambda sql, timeout=30: "\n".join(sorted(cal)), raising=False
        )
        days = InternalComputeProvider._trade_days_guarded(
            datetime.date(2026, 9, 30), datetime.date(2026, 10, 2)
        )
        assert [d.isoformat() for d in days] == ["2026-10-01", "2026-10-02"]


class TestLimitUpPoolBranch:
    def test_rows_follow_insert_columns_and_skip_weekend(self, monkeypatch):
        """分支按 INSERT_COLUMNS 列序产行，且周末日不触发采集。"""
        calls: list[datetime.date] = []

        def fake_fetch(d):
            calls.append(d)
            return [
                SimpleNamespace(
                    trade_date=d.isoformat(), symbol="000001", name="x", close=1.0,
                    pct_change=10.0, amount=2.0, turnover_rate=3.0, float_market_cap=4.0,
                    total_market_cap=5.0, seal_amount=6.0, seal_ratio=7.0,
                    first_seal_time="09:25:00", last_seal_time="14:55:00", sealed_seconds=2100,
                    open_board_count=1, consec_limit=2, limit_stat="3/2", industry="银行",
                    data_source="akshare",
                )
            ]

        monkeypatch.setattr(
            "zephyr.data.implementations.limit_up_pool_collector.fetch_limit_up_pool", fake_fetch
        )
        # 周四~周日窗口：只有周四/周五触发采集
        prov = InternalComputeProvider()
        results = list(
            prov._fetch_limit_up_pool(
                _payload("c1_market.limit_up_pool", datetime.date(2026, 9, 17), datetime.date(2026, 9, 20))
            )
        )
        assert len(results) == 1
        fr = results[0]
        assert fr.table == "c1_market.limit_up_pool"
        assert all(d.weekday() < 5 for d in calls)
        assert len(calls) == 2  # 周四+周五，周末被守卫
        assert len(fr.rows) == 2
        assert fr.rows[0][0] == "2026-09-17"  # trade_date 首列
        assert len(fr.rows[0]) == len(fr.columns)


class TestDabanBoardEventBranch:
    def test_delegates_and_maps_columns(self, monkeypatch):
        """分支委托 collect_derived_events 并按 INSERT_COLUMNS 映射行。"""
        event = SimpleNamespace(
            trade_date="2026-09-17", symbol="000001", board="sz_main", st_flag=0,
            pre_close=9.9, limit_up_price=10.89, open=10.0, high=10.89, low=9.95,
            close=10.89, touched=1, close_sealed=1, is_one_word=0,
            first_touch_time="10:00:00", open_board_count=1, seal_bid_volume=100,
            seal_amount_proxy=1089000.0, consec_limit=1, limit_src="ch_stk_limit",
            data_source="derived_kline", derive_version="v1",
        )
        captured: dict = {}

        def fake_collect(start, end, client, **kw):
            captured["start"], captured["end"], captured["kw"] = start, end, kw
            return [event]

        monkeypatch.setattr(
            "zephyr.data.ch_writer.get_client", lambda: object(), raising=False
        )
        monkeypatch.setattr(
            "zephyr.data.implementations.daban_board_event_deriver.collect_derived_events",
            fake_collect,
        )
        prov = InternalComputeProvider()
        results = list(
            prov._fetch_daban_board_event(
                _payload("c1_market.daban_board_event", datetime.date(2026, 9, 17), datetime.date(2026, 9, 17))
            )
        )
        assert len(results) == 1
        fr = results[0]
        assert fr.table == "c1_market.daban_board_event"
        assert fr.rows[0][0] == "2026-09-17"
        assert fr.rows[0][2] == "sz_main"  # board 第三列
        assert len(fr.rows[0]) == len(fr.columns)

    def test_ch_unreachable_fail_closed(self, monkeypatch):
        """CH 不可达时 fail-closed（禁无库推导）。"""
        monkeypatch.setattr("zephyr.data.ch_writer.get_client", lambda: None, raising=False)
        prov = InternalComputeProvider()
        with pytest.raises(RuntimeError):
            list(
                prov._fetch_daban_board_event(
                    _payload("c1_market.daban_board_event", datetime.date(2026, 9, 17), datetime.date(2026, 9, 17))
                )
            )


class TestAkshareTradeDaysWindow:
    def test_calendar_downgrade_returns_none(self, monkeypatch):
        """日历查询失败返回 None（调用方降级周末守卫），不抛错。"""
        from zephyr.data.implementations.akshare_provider import AkshareIngestProvider

        def boom(sql, timeout=30):
            raise RuntimeError("ch down")

        monkeypatch.setattr("zephyr.data.ch_reader.query", boom, raising=False)
        prov = AkshareIngestProvider.__new__(AkshareIngestProvider)
        import logging

        prov._log = logging.getLogger("test")
        assert (
            prov._load_trade_days_for_window(datetime.date(2026, 9, 1), datetime.date(2026, 9, 2))
            is None
        )

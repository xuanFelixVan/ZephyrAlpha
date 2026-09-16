# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [TTL] permanent
# [TESTS] zephyr.data.implementations.ch_auction_derive
# [DOMAIN] D_DATA
"""ch_auction_derive 单元测试（竞价族桥源派生，方案 A'，2026-09-17 收盘后窗口）。

覆盖：SQL 构建铁律（market_type 防指数混线/竞价窗口边界/INSERT-only 无 DELETE/
五档 coalesce 防 Nullable 失败/涨跌停板块规则 multiIf/快照终态 argMax）、
派生函数（FakeClient 捕获 SQL+行数语义）、回补防重灌闸、非法日期 ValueError、
qmt_bridge_provider 竞价路由（capability 契约/fetch 分支/错误契约/tick_data no-op 不回归）。
CH 交互全 mock，不依赖真实 ClickHouse（测试隔离铁律：禁写生产路径）。
"""

import os
import sys
from datetime import date
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

import pytest

import zephyr.data.implementations.ch_auction_derive as cd
from zephyr.data.implementations.ch_auction_derive import (
    _book_select_sql,
    _snapshot_select_sql,
    _validate_date,
    day_has_auction_rows,
    derive_auction_book,
    derive_auction_snapshot,
)

_D = "2026-09-16"


class TestSqlBuilders:
    def test_snapshot_filters_stock_market_types(self):
        """指数混线防线：tick_depth_5 裸码跨市场（'000001'=平银/上证指数同码），必须滤市。"""
        sql = _snapshot_select_sql(_D)
        assert "market_type IN ('stock', 'stock_bj')" in sql
        assert "c1_market.tick_depth_5" in sql

    def test_snapshot_window_bounds_incl_match_print(self):
        """窗口 [09:15:00, 09:26:00)：含 09:25:00 撮合打印（9/16 实证 09:25:03 有行）。"""
        sql = _snapshot_select_sql(_D)
        assert f">= '{_D} 09:15:00'" in sql
        assert f"< '{_D} 09:26:00'" in sql

    def test_snapshot_terminal_state_semantics(self):
        """终态覆盖语义：argMax(timestamp) + GROUP BY symbol,trade_date。"""
        sql = _snapshot_select_sql(_D)
        assert "argMax(price, timestamp) AS auction_price" in sql
        assert "argMax(volume, timestamp) AS auction_volume" in sql
        assert "argMax(amount, timestamp) AS auction_amount" in sql
        assert "GROUP BY symbol, trade_date" in sql

    def test_snapshot_select_supports_tick_data_src_for_backfill(self):
        """回补 2026-06~08 空窗日换 1 档 tick_data 源（亦有 market_type 防混线）。"""
        sql = _snapshot_select_sql("2026-06-08", src="c1_market.tick_data")
        assert "c1_market.tick_data" in sql

    def test_book_insert_only_no_delete(self):
        """INSERT-only 铁律：ReplacingMergeTree 幂等，全语句不得出现 DELETE/mutations。"""
        sql = cd.SQL_BOOK_INSERT.format(
            book="c1_market.auction_book",
            src="c1_market.tick_depth_5",
            kd="c1_market.kline_daily",
            sb="c1_market.stock_basic",
            d=_D,
            _AUCTION_START=cd._AUCTION_START,
            _AUCTION_END_EXCL=cd._AUCTION_END_EXCL,
        )
        assert "INSERT INTO c1_market.auction_book" in sql
        assert "DELETE" not in sql
        assert "ALTER TABLE" not in sql

    def test_book_level_columns_coalesce_zero(self):
        """五档 20 列 coalesce：源 Nullable 直插非 Nullable 目标会炸，空档 0=桥 dump 惯例。"""
        sql = _book_select_sql(_D)
        assert "coalesce(s.bid_price1, toDecimal64(0, 4)) AS bid_price1,\n" in sql
        assert "coalesce(s.ask_volume5, toUInt64(0)) AS ask_volume5" in sql
        # 列间必须有逗号（2026-09-17 E2E 实证：漏逗号=CH Code 62 语法错，子串断言抓不住）
        assert "AS bid_price1\n" not in sql

    def test_book_open_high_low_zero_matches_miniqmt_semantics(self):
        """竞价时段 open/high/low=0 复刻 miniqmt 原产（9/16 原产实测即 0）。"""
        sql = _book_select_sql(_D)
        assert "toDecimal64(0, 4) AS open" in sql
        assert "toDecimal64(0, 4) AS high" in sql
        assert "toDecimal64(0, 4) AS low" in sql

    def test_book_preclose_limit_rules(self):
        """昨收 JOIN kline_daily + 板块规则（stk_limit 权威全表实证：主板 10%、创业科创 20%、
        北交所 30%、现行规则 ST 与主板同幅——故 SQL 无 ST 特判）。"""
        sql = _book_select_sql(_D)
        assert "c1_market.kline_daily" in sql
        assert "round(argMax(close, trade_date), 2) AS close" in sql
        assert "b.close * toDecimal64(1.2, 5)" in sql
        assert "b.close * toDecimal64(0.8, 5)" in sql
        assert "b.close * toDecimal64(1.3, 5)" in sql
        assert "b.close * toDecimal64(0.7, 5)" in sql
        assert "startsWith(b.symbol, '68')" in sql
        assert "startsWith(b.symbol, '43')" in sql
        assert ", 2)" in sql  # 四舍五入到分
        # 现行规则 ST 无特判（stk_limit 2026-09-15 全表实证：st_flag=1 亦主板 10%/创业 20%）
        assert "stock_basic" not in sql
        assert "toDecimal64(1.05, 5)" not in sql

    def test_invalid_date_raises(self):
        with pytest.raises(ValueError):
            _validate_date("20260916")
        with pytest.raises(ValueError):
            _snapshot_select_sql("not-a-date")

    def test_no_alias_shadowing_where_columns(self):
        """CH 别名遮蔽陷阱回归（2026-09-17 回补 32 天全 0 行事故）：
        SELECT 别名会被代入 WHERE/GROUP BY——被 WHERE（market_type/timestamp/trade_date）
        或 GROUP BY（symbol/trade_date）引用的列名不得再被 SELECT 别名遮蔽
        （data_source 仅出现在 argMax 输出位，不在 WHERE，允许别名）。"""
        for sql in (_snapshot_select_sql(_D), _book_select_sql(_D)):
            for col in ("market_type", "timestamp", "trade_date", "symbol"):
                assert f"AS {col}" not in sql


class TestDeriveFunctions:
    @staticmethod
    def _fake_client(count=42):
        c = MagicMock()
        c.execute.return_value = [(count,)]
        return c

    def test_derive_snapshot_executes_insert_then_counts(self):
        c = self._fake_client(42)
        n = derive_auction_snapshot(_D, client=c)
        assert n == 42
        assert c.execute.call_count == 2
        first_sql = c.execute.call_args_list[0][0][0]
        assert first_sql.startswith("INSERT INTO c1_market.auction_snapshot")
        assert "c1_market.tick_depth_5" in first_sql
        assert "market_type IN ('stock', 'stock_bj')" in first_sql

    def test_derive_book_executes_insert_then_counts(self):
        c = self._fake_client(700)
        n = derive_auction_book(_D, client=c)
        assert n == 700
        first_sql = c.execute.call_args_list[0][0][0]
        assert first_sql.startswith("INSERT INTO c1_market.auction_book")
        assert "LEFT JOIN" in first_sql

    def test_derive_book_wraps_error(self):
        c = MagicMock()
        c.execute.side_effect = RuntimeError("boom")
        with pytest.raises(RuntimeError, match="竞价盘口派生失败"):
            derive_auction_book(_D, client=c)
        with pytest.raises(RuntimeError, match="竞价快照派生失败"):
            derive_auction_snapshot(_D, client=c)

    def test_day_has_auction_rows_gate(self):
        """回补防重灌闸：已有行=True（跳过），空日=False（可灌）。"""
        c = MagicMock()
        c.execute.return_value = [(0,)]
        assert day_has_auction_rows(c, "c1_market.auction_snapshot", "2026-06-08") is False
        c.execute.return_value = [(5220,)]
        assert day_has_auction_rows(c, "c1_market.auction_snapshot", "2026-09-16") is True


class TestProviderRouting:
    """qmt_bridge_provider 竞价路由（方案 A' 接线）。"""

    @staticmethod
    def _payload(capability: str):
        from zephyr.data.provider_base import FetchPayload

        return FetchPayload(
            table="c1_market.auction_snapshot",
            symbols=None,
            start=date(2026, 9, 16),
            end=date(2026, 9, 16),
            incremental=True,
            extra={"capability": capability},
        )

    def test_auction_capabilities_registered(self):
        from zephyr.data.implementations.qmt_bridge_provider import QmtBridgeIngestProvider

        caps = {c.capability_id for c in QmtBridgeIngestProvider.meta.capabilities}
        assert {"auction_data", "auction_book"} <= caps
        assert QmtBridgeIngestProvider.source_name == "qmt_bridge"

    def test_fetch_routes_auction_data(self):
        from zephyr.data.implementations.qmt_bridge_provider import QmtBridgeIngestProvider

        provider = QmtBridgeIngestProvider()
        provider._connected = True
        with patch(
            "zephyr.data.implementations.qmt_bridge_provider._call_derive_auction",
            return_value=5220,
        ) as m:
            results = list(provider.fetch(self._payload("auction_data"), policy=None))
        assert len(results) == 1
        r = results[0]
        assert r.error is None
        assert r.last_key == "2026-09-16"
        assert r.table == "c1_market.auction_snapshot"
        m.assert_called_once_with("auction_data", "2026-09-16", "2026-09-16")

    def test_fetch_routes_auction_book(self):
        from zephyr.data.implementations.qmt_bridge_provider import (
            QmtBridgeIngestProvider,
            _AUCTION_CAPABILITIES,
        )

        assert _AUCTION_CAPABILITIES["auction_book"] == "c1_market.auction_book"
        provider = QmtBridgeIngestProvider()
        provider._connected = True
        with patch(
            "zephyr.data.implementations.qmt_bridge_provider._call_derive_auction",
            return_value=151670,
        ):
            results = list(provider.fetch(self._payload("auction_book"), policy=None))
        assert results[0].error is None
        assert results[0].table == "c1_market.auction_book"

    def test_fetch_auction_error_contract(self):
        """错误契约：派生失败 → FetchResult(error=...) 不抛异常。"""
        from zephyr.data.implementations.qmt_bridge_provider import QmtBridgeIngestProvider

        provider = QmtBridgeIngestProvider()
        provider._connected = True
        with patch(
            "zephyr.data.implementations.qmt_bridge_provider._call_derive_auction",
            side_effect=RuntimeError("boom"),
        ):
            results = list(provider.fetch(self._payload("auction_data"), policy=None))
        assert len(results) == 1
        assert results[0].error is not None
        assert "竞价派生失败" in results[0].error

    def test_tick_data_noop_unchanged(self):
        """回归防错：tick_data no-op 语义不得被竞价路由破坏（防实时双写）。"""
        from zephyr.data.implementations.qmt_bridge_provider import QmtBridgeIngestProvider

        provider = QmtBridgeIngestProvider()
        provider._connected = True
        results = list(provider.fetch(self._payload("tick_data"), policy=None))
        assert results[0].error is None
        assert results[0].rows == []

    def test_none_client_raises_runtime_error(self):
        """红队二轮 #5：get_client()→None（冷却期）必须 RuntimeError 而非 AttributeError。"""
        from zephyr.data.implementations import ch_auction_derive as cd_mod

        with patch.object(cd_mod, "get_client", return_value=None):
            with pytest.raises(RuntimeError, match="连接冷却期"):
                cd_mod.derive_auction_snapshot(_D)
            with pytest.raises(RuntimeError, match="连接冷却期"):
                cd_mod.derive_auction_book(_D)

    def test_call_derive_gate_skips_history_days(self):
        """红队二轮复检：历史日（<end）过 day_has_auction_rows 闸，当日不过闸。"""
        from zephyr.data.implementations import qmt_bridge_provider as qp

        with patch("zephyr.data.ch_writer.get_client", return_value=MagicMock()), patch(
            "zephyr.data.implementations.ch_auction_derive.day_has_auction_rows",
            side_effect=[True],
        ) as gate, patch(
            "zephyr.data.implementations.ch_auction_derive.derive_auction_snapshot",
            return_value=5220,
        ) as derive:
            n = qp._call_derive_auction("auction_data", "2026-09-15", "2026-09-16")
        assert n == 5220
        gate.assert_called_once()  # 只有历史日 9/15 过闸
        derive.assert_called_once_with("2026-09-16")  # 当日无闸直派

    def test_call_derive_range_inversion_defense(self):
        """区间倒置（start>end）按规范化区间派生，不炸不漏。"""
        from zephyr.data.implementations import qmt_bridge_provider as qp

        with patch("zephyr.data.ch_writer.get_client", return_value=MagicMock()), patch(
            "zephyr.data.implementations.ch_auction_derive.day_has_auction_rows",
            return_value=False,
        ), patch(
            "zephyr.data.implementations.ch_auction_derive.derive_auction_snapshot",
            return_value=1,
        ) as derive:
            qp._call_derive_auction("auction_data", "2026-09-16", "2026-09-15")
        assert derive.call_count == 2  # 9/15 与 9/16 各一次

    def test_unknown_capability_error_unchanged(self):
        from zephyr.data.implementations.qmt_bridge_provider import QmtBridgeIngestProvider

        provider = QmtBridgeIngestProvider()
        provider._connected = True
        results = list(provider.fetch(self._payload("quote_realtime"), policy=None))
        assert "NotImplementedError" in results[0].error

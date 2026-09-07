# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] tests.backtest.test_stk_limit_matching
# [DOMAIN] D_BACKTEST
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [A_module] module_id=MOD-BT-001 | layer=test | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""撮合涨跌停三级解析链测试（#ARCH-DATA-020 重评条件②闭环）。

背景：2026-07-06 起沪深主板 ST/*ST 涨跌幅 5%→10%（沪深交易所《交易规则
（2026年修订）》）。撮合引擎历史缺口：主板 ST 统一按 10% 推断 → 07-06 前
历史回测涨跌停约束偏乐观（真实 5%）。修复后三级解析链：
  1. stk_limit 表 PIT 行（from_table，精确价直用）
  2. 规则切片兜底（AkshareProvider._limit_pct_of 单一真源，ST 经
     st_stock_list 最近可得快照）
  3. 板块前缀推断（未知前缀/无日期旧路径，行为不变）

边界日：2026-07-03（主板 ST 5% 末日）/ 2026-07-06（10% 首日）。
单测不触真实 CH（monkeypatch ch_reader.query）；集成用例 CH 不可达时 skip。
"""

from __future__ import annotations

import datetime
from decimal import Decimal

import pytest

from zephyr.backtest.core.matching_engine import (
    LimitInfo,
    MatchingEngine,
    StkLimitProvider,
    _normalize_date,
)

_D_0703 = datetime.date(2026, 7, 3)  # 主板 ST 5% 末日
_D_0706 = datetime.date(2026, 7, 6)  # 主板 ST 10% 首日

_ST_SYMBOL = "600074.SH"  # 主板（60 段）ST 样例
_NON_ST_SYMBOL = "600000.SH"


def _fake_provider(rows: dict) -> object:
    """构造协议级 fake provider：rows = {(date, symbol): LimitInfo}。"""

    def _provider(trade_date, symbols):
        return {s: rows[(trade_date, s)] for (d, s) in rows if d == trade_date and s in symbols}

    return _provider


def _limit_map(engine, trade_date, symbols):
    return engine._prefetch_limit_map(trade_date, symbols)


class TestTablePitRows:
    """一级链：stk_limit 表 PIT 行直用（精确价，不重算）。"""

    def test_table_row_5pct_before_0706(self):
        # 07-03 主板 ST 表行：涨停价按真实 5% 口径（10.00×1.05=10.50）
        rows = {(_D_0703, _ST_SYMBOL): LimitInfo(
            limit_up=Decimal("10.50"), limit_down=Decimal("9.50"),
            limit_pct=Decimal("0.05"), st_flag=True, from_table=True,
        )}
        engine = MatchingEngine(limit_provider=_fake_provider(rows))
        lm = _limit_map(engine, _D_0703, [_ST_SYMBOL])
        # 价 10.50 触涨停（若走旧 10% 推断需 11.00，不会判限——证明表行优先）
        assert engine._is_limit_up(_ST_SYMBOL, Decimal("10.50"), Decimal("10.00"), _D_0703, lm)
        assert not engine._is_limit_up(_ST_SYMBOL, Decimal("10.49"), Decimal("10.00"), _D_0703, lm)
        # 跌停 9.50 同理（旧 10% 口径 9.00，10.00-0.51 不会判限）
        assert engine._is_limit_down(_ST_SYMBOL, Decimal("9.50"), Decimal("10.00"), _D_0703, lm)
        assert not engine._is_limit_down(_ST_SYMBOL, Decimal("9.51"), Decimal("10.00"), _D_0703, lm)

    def test_table_row_10pct_from_0706(self):
        rows = {(_D_0706, _ST_SYMBOL): LimitInfo(
            limit_up=Decimal("11.00"), limit_down=Decimal("9.00"),
            limit_pct=Decimal("0.10"), st_flag=True, from_table=True,
        )}
        engine = MatchingEngine(limit_provider=_fake_provider(rows))
        lm = _limit_map(engine, _D_0706, [_ST_SYMBOL])
        assert engine._is_limit_up(_ST_SYMBOL, Decimal("11.00"), Decimal("10.00"), _D_0706, lm)
        assert not engine._is_limit_up(_ST_SYMBOL, Decimal("10.75"), Decimal("10.00"), _D_0706, lm)

    def test_table_row_null_is_unlimited(self):
        # 新股无涨跌幅限制期：表行 limit_*=NULL → 不封板（买单可成）
        rows = {(_D_0706, "688999.SH"): LimitInfo(
            limit_up=None, limit_down=None, limit_pct=None, st_flag=False, from_table=True,
        )}
        engine = MatchingEngine(limit_provider=_fake_provider(rows))
        lm = _limit_map(engine, _D_0706, ["688999.SH"])
        assert not engine._is_limit_up("688999.SH", Decimal("99.99"), Decimal("10.00"), _D_0706, lm)


class TestRuleFallbackSliced:
    """二级链：表缺行 → _limit_pct_of 日期切片兜底（复用生成侧单一真源）。"""

    @pytest.fixture
    def patched_no_table(self, monkeypatch):
        """stk_limit 无表行 + 受控 ST 快照；_limit_pct_of 走真实现（纯函数）。"""
        monkeypatch.setattr("zephyr.data.ch_reader.query", lambda sql: "")

        class _P(StkLimitProvider):
            def __init__(self, st_codes: set):
                super().__init__()
                self._st_codes = st_codes

            def _st_flag_set(self, trade_date, ch_reader_mod):
                return self._st_codes

        return _P

    def test_main_board_st_5pct_on_0703(self, patched_no_table):
        engine = MatchingEngine(limit_provider=patched_no_table({"600074"}))
        lm = _limit_map(engine, _D_0703, [_ST_SYMBOL])
        info = lm[_ST_SYMBOL]
        assert not info.from_table and info.st_flag
        assert info.limit_pct == Decimal("0.05")
        # prev_close=10.00 → 涨停 10.50（5%）；10.51 拒、10.49 成
        assert engine._is_limit_up(_ST_SYMBOL, Decimal("10.50"), Decimal("10.00"), _D_0703, lm)
        assert not engine._is_limit_up(_ST_SYMBOL, Decimal("10.49"), Decimal("10.00"), _D_0703, lm)

    def test_main_board_st_10pct_on_0706(self, patched_no_table):
        engine = MatchingEngine(limit_provider=patched_no_table({"600074"}))
        lm = _limit_map(engine, _D_0706, [_ST_SYMBOL])
        assert lm[_ST_SYMBOL].limit_pct == Decimal("0.10")
        assert not engine._is_limit_up(_ST_SYMBOL, Decimal("10.50"), Decimal("10.00"), _D_0706, lm)
        assert engine._is_limit_up(_ST_SYMBOL, Decimal("11.00"), Decimal("10.00"), _D_0706, lm)

    def test_non_st_regression_10pct_both_days(self, patched_no_table):
        engine = MatchingEngine(limit_provider=patched_no_table(set()))
        for d in (_D_0703, _D_0706):
            lm = _limit_map(engine, d, [_NON_ST_SYMBOL])
            assert lm[_NON_ST_SYMBOL].limit_pct == Decimal("0.10")
            assert not engine._is_limit_up(_NON_ST_SYMBOL, Decimal("10.99"), Decimal("10.00"), d, lm)
            assert engine._is_limit_up(_NON_ST_SYMBOL, Decimal("11.00"), Decimal("10.00"), d, lm)

    def test_chinext_prereform_slice(self, patched_no_table):
        """创业板 2020-08-24 注册制切片：08-23 ST 5% / 08-24 起 20%（同构回归）。"""
        engine = MatchingEngine(limit_provider=patched_no_table({"300001"}))
        d_pre = datetime.date(2020, 8, 21)
        d_post = datetime.date(2020, 8, 24)
        lm_pre = _limit_map(engine, d_pre, ["300001.SZ"])
        lm_post = _limit_map(engine, d_post, ["300001.SZ"])
        assert lm_pre["300001.SZ"].limit_pct == Decimal("0.05")
        assert lm_post["300001.SZ"].limit_pct == Decimal("0.20")


class TestEngineFallbackPaths:
    """三级链与降级路径：无 provider / provider 故障 / 旧调用兼容。"""

    def test_no_provider_date_sliced_non_st(self):
        # 无 provider：st_flag 未知=False，主板切片仍 0.10（非 ST 行为不变）
        engine = MatchingEngine(limit_provider=None)
        for d in (_D_0703, _D_0706):
            assert not engine._is_limit_up(_NON_ST_SYMBOL, Decimal("10.99"), Decimal("10.00"), d)
            assert engine._is_limit_up(_NON_ST_SYMBOL, Decimal("11.00"), Decimal("10.00"), d)

    def test_no_provider_no_date_legacy(self):
        # 旧调用（无 date）：板块前缀推断，行为与修复前完全一致
        engine = MatchingEngine(limit_provider=None)
        assert not engine._is_limit_up(_NON_ST_SYMBOL, Decimal("10.99"), Decimal("10.00"))
        assert engine._is_limit_up(_NON_ST_SYMBOL, Decimal("11.00"), Decimal("10.00"))
        assert engine._is_limit_up("300001.SZ", Decimal("12.00"), Decimal("10.00"))  # 创业板 20%

    def test_provider_exception_fail_open(self):
        # provider 抛异常 → warn + 退规则兜底，撮合不炸
        def _boom(trade_date, symbols):
            raise RuntimeError("CH down")

        engine = MatchingEngine(limit_provider=_boom)
        from zephyr.backtest.core.portfolio import Portfolio

        pf = Portfolio(initial_capital=Decimal("100000"))
        fills = engine.generate_fills(
            target_weights={_NON_ST_SYMBOL: 0.5},
            prices={_NON_ST_SYMBOL: Decimal("10.5")},
            portfolio=pf,
            date=_D_0706.isoformat(),
            prev_close={_NON_ST_SYMBOL: Decimal("10.00")},
        )
        assert len(fills) == 1  # 未触停板，正常成交

    def test_generate_fills_st_blocked_on_0703(self, monkeypatch):
        """端到端：07-03 主板 ST 5% 封板买单拒成（修复前按 10% 会误成交）。"""
        rows = {(_D_0703, _ST_SYMBOL): LimitInfo(
            limit_up=Decimal("10.50"), limit_down=Decimal("9.50"),
            limit_pct=Decimal("0.05"), st_flag=True, from_table=True,
        )}
        engine = MatchingEngine(limit_provider=_fake_provider(rows))
        from zephyr.backtest.core.portfolio import Portfolio

        pf = Portfolio(initial_capital=Decimal("100000"))
        fills = engine.generate_fills(
            target_weights={_ST_SYMBOL: 0.5},
            prices={_ST_SYMBOL: Decimal("10.55")},  # ≥5% 涨停价，<10% 涨停价
            portfolio=pf,
            date=_D_0703,
            prev_close={_ST_SYMBOL: Decimal("10.00")},
        )
        assert fills == []  # 修复后拒成（修复前 10% 口径会成交——乐观偏差）


class TestNormalizeDate:
    def test_str_and_date(self):
        assert _normalize_date("2026-07-03") == _D_0703
        assert _normalize_date("2026-07-03 15:00:00") == _D_0703
        assert _normalize_date(_D_0706) is _D_0706
        assert _normalize_date(None) is None
        assert _normalize_date("not-a-date") is None


# ---------------------------------------------------------------------------
# 集成用例（真实 CH；不可达时 skip——单测覆盖已确定性闭环）
# ---------------------------------------------------------------------------

_CH_UP: bool | None = None


def _ch_up() -> bool:
    global _CH_UP
    if _CH_UP is None:
        try:
            from zephyr.data import ch_reader

            _CH_UP = bool((ch_reader.query("SELECT count() FROM c1_market.stk_limit") or "").strip())
        except Exception:  # noqa: BLE001
            _CH_UP = False
    return _CH_UP


@pytest.mark.skipif(not _ch_up(), reason="ClickHouse 不可达")
class TestChIntegration:
    def test_pit_row_stk_limit_post_0706(self):
        """2026-09-04 主板 ST 行：from_table=True + 10% 口径（已重算）。"""
        provider = StkLimitProvider()
        out = provider(datetime.date(2026, 9, 4), ["000010.SZ"])
        info = out.get("000010.SZ")
        assert info is not None and info.from_table
        assert info.st_flag
        assert info.limit_pct == Decimal("0.10")
        assert info.limit_up is not None and info.limit_down is not None

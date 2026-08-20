# [BLUEPRINT] MOD-BT-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 目标权重+盘口快照
#   fields: target_weights / order_books / portfolio
#   code: MatchingEngine._clamp_buys_to_projected_cash (L483)
# 层: 算法
# - id: A1
#   name_zh: 满仓成本摩擦收缩
#   name_en: clamp_buys_to_projected_cash
#   intro: 先卖后买顺序投影现金，买单超支时收缩到可负担最大整手
#   code: _clamp_buys_to_projected_cash / _side_base_price
# 层: 输出
# - id: O1
#   name_zh: 收缩后的订单列表
#   en: clamped_orders
# [/ALGO_FLOW]
# [A_test] module_id: MOD-TEST-BT-COST-NIGHT001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md | §3.2 §16.7
# [MODULE] tests.backtest.test_cost_friction_night001
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/backtest/test_cost_friction_night001.py
# [TTL] permanent
"""AI-NIGHT-001 包3.2 登记项#2 — 满仓归一化成本摩擦修复测试。

满仓（Σ=1）信号买入侧不预留交易成本余量时，下单总额×(1+滑点)+佣金
必然超现金 → 整单被拒（Portfolio._apply_buy 现金不足报错）。修复：
MatchingEngine._clamp_buys_to_projected_cash 按先卖后买投影现金，
将超支买单收缩到可负担最大整手；非满仓场景逐位不变（零回归）。

口径（与 MatchingLogic 一致）：
  BUY 执行价 = ask1×(1+slippage_bps/10000)
  SELL 执行价 = bid1×(1−slippage_bps/10000)
  佣金 = max(qty×price×rate, 最低佣金)
  印花税 = 卖出时 qty×price×stamp_tax_rate
"""

from __future__ import annotations

import logging
from decimal import Decimal

import pandas as pd

from zephyr.backtest.core.matching_engine import MatchingEngine
from zephyr.backtest.core.portfolio import BacktestFill, Portfolio
from zephyr.backtest.implementations.vectorized_engine import (
    BacktestConfig,
    DefaultBacktestEngine,
)

D = Decimal


class TestFullWeightCostFrictionClamp:
    """Σ=1 满仓场景：收缩后买单应可负担，零成交回归消除"""

    def test_single_full_weight_99900_shares(self):
        """100万现金/10.00元：满仓信号应成交 99,900 股（非 100,000）"""
        engine = MatchingEngine()
        pf = Portfolio(initial_capital=D("1000000"))
        fills = engine.generate_fills(
            target_weights={"600000": 1.0},
            prices={"600000": D("10.00")},
            portfolio=pf,
            date="2026-08-03",
        )
        assert len(fills) == 1
        f = fills[0]
        assert f.side == "BUY"
        assert f.quantity == D("99900")
        assert f.price == D("10.001")
        assert f.total_cost == D("999399.6299700")
        # 成交后现金必须非负
        pf.apply_fill(f)
        assert pf.cash == D("600.3700300")

    def test_double_full_weight_split_clamp(self):
        """双标的全仓 {A:0.6,B:0.4}：先A后B，B 被收缩到可负担"""
        engine = MatchingEngine()
        pf = Portfolio(initial_capital=D("1000000"))
        fills = engine.generate_fills(
            target_weights={"600000": 0.6, "600002": 0.4},
            prices={"600000": D("10.00"), "600002": D("10.00")},
            portfolio=pf,
            date="2026-08-03",
        )
        assert len(fills) == 2
        a = next(f for f in fills if f.symbol == "600000")
        b = next(f for f in fills if f.symbol == "600002")
        assert a.side == "BUY"
        assert a.quantity == D("60000")
        # A 成本：60,000×10.001 + 180.018 = 600,240.018
        assert a.total_cost == D("600240.0180000")
        # 投影剩余 = 1,000,000 − 600,240.018 = 399,759.982
        # B 原始需求：floor(400,000/10.001/100)×100 = 39,900
        # 39,900×10.001 + 119.73003 = 399,159.61197 ≤ 399,759.982，可负担 → 不变
        assert b.quantity == D("39900")
        assert b.total_cost == D("399159.6119700")
        # 全量成交后现金 = 1000000 − 600240.018 − 399159.61197 = 600.37003
        for f in fills:
            pf.apply_fill(f)
        assert pf.cash == D("600.3700300")

    def test_full_weight_hits_min_commission(self):
        """小资金满仓触最低佣金 5 元，收缩后仍是整手"""
        engine = MatchingEngine()
        pf = Portfolio(initial_capital=D("10000"))
        fills = engine.generate_fills(
            target_weights={"600000": 1.0},
            prices={"600000": D("10.00")},
            portfolio=pf,
            date="2026-08-03",
        )
        assert len(fills) == 1
        f = fills[0]
        assert f.quantity == D("900")
        assert f.commission == D("5")
        assert f.total_cost == D("9005.9")
        pf.apply_fill(f)
        assert pf.cash == D("994.1")

    def test_full_weight_below_one_lot(self):
        """资金不足一手 → 无单（不报错）"""
        engine = MatchingEngine()
        pf = Portfolio(initial_capital=D("1000"))
        fills = engine.generate_fills(
            target_weights={"600000": 1.0},
            prices={"600000": D("10.00")},
            portfolio=pf,
            date="2026-08-03",
        )
        assert fills == []

    def test_sell_then_buy_cash_chain(self):
        """先卖后买：卖单回款后买单应有更多空间"""
        engine = MatchingEngine()
        pf = Portfolio(initial_capital=D("1000000"))
        # 先持有 A 10,000 股（买入时扣 100,000+30）
        pf.apply_fill(
            BacktestFill(
                date="2026-08-03",
                symbol="600000",
                side="BUY",
                quantity=D("10000"),
                price=D("10.00"),
                commission=D("30"),
            )
        )
        # 次日：A 清仓 + B 满仓
        fills = engine.generate_fills(
            target_weights={"600002": 1.0},
            prices={"600000": D("11.00"), "600002": D("10.00")},
            portfolio=pf,
            date="2026-08-04",
        )
        sell = next(f for f in fills if f.side == "SELL")
        buy = next(f for f in fills if f.side == "BUY")
        # SELL 应先执行
        assert fills[0].side == "SELL"
        assert sell.quantity == D("10000")  # A 全量清仓
        # NAV = 899,970 + 10,000×11 = 1,009,970 → B 目标 = floor(1,009,970/10/100)×100
        # = 100,900 股；成本 = 100,900×10.001 + 302.73027 = 1,009,503.63
        # 投影现金 = 899,970 + (109,989 − 142.9857) = 1,009,816.01 ≥ 成本 → 不收缩
        assert buy.quantity == D("100900")
        for f in fills:
            pf.apply_fill(f)
        assert pf.cash >= D("0")

    def test_partial_weight_no_clamp(self):
        """非满仓（Σ<1）场景：原始 sizing 不变（零回归）"""
        engine = MatchingEngine()
        pf = Portfolio(initial_capital=D("1000000"))
        fills = engine.generate_fills(
            target_weights={"600000": 0.5},
            prices={"600000": D("10.00")},
            portfolio=pf,
            date="2026-08-03",
        )
        assert len(fills) == 1
        # 50% 权重：floor(500,000/10/100)×100 = 50,000
        assert fills[0].quantity == D("50000")

    def test_engine_level_full_weight_no_skip_warning(self, caplog):
        """引擎级：满仓信号应成交（无 skip warning）"""
        dates = pd.bdate_range("2026-08-03", periods=2)
        rows = [{"symbol": "600000", "date": d, "close": 10.0} for d in dates]
        data = pd.DataFrame(rows).set_index(["symbol", "date"])
        sig = pd.DataFrame({"600000": [1.0, 1.0]}, index=dates)
        engine = DefaultBacktestEngine(config=BacktestConfig())
        with caplog.at_level(
            logging.WARNING,
            logger="zephyr.backtest.implementations.vectorized_engine",
        ):
            result = engine.run(data=data, signals=sig, strategy_name="full-clamp")
        pf = engine.last_portfolio
        assert result.trades_count == 1
        pos = pf.get_position("600000")
        assert pos.quantity == D("99900")
        # 不应出现 Fill skipped 警告（满仓成交成功）
        per_fill = [r for r in caplog.records if "Fill skipped" in r.getMessage()]
        assert len(per_fill) == 0

    def test_engine_level_limit_up_next_day_trade(self, caplog):
        """涨停日满仓被阻，次日非涨停日应成功买入"""
        dates = pd.bdate_range("2026-08-03", periods=3)
        closes = [10.00, 11.00, 11.00]  # day2 涨停
        rows = [{"symbol": "600000", "date": d, "close": c} for d, c in zip(dates, closes, strict=True)]
        data = pd.DataFrame(rows).set_index(["symbol", "date"])
        # day1 无信号；day2/day3 满仓信号
        sig = pd.DataFrame({"600000": [float("nan"), 1.0, 1.0]}, index=dates)
        engine = DefaultBacktestEngine(config=BacktestConfig())
        with caplog.at_level(
            logging.WARNING,
            logger="zephyr.backtest.implementations.vectorized_engine",
        ):
            result = engine.run(data=data, signals=sig, strategy_name="limit-up-clamp")
        pf = engine.last_portfolio
        trades = pf.trades_log
        # day2 涨停 → 无成交；day3 买入
        assert len(trades) == 1
        assert trades[0]["date"].startswith("2026-08-05")
        assert trades[0]["side"] == "BUY"
        # 涨停日不应出现满仓 skip 警告（无单可成交）
        per_fill = [r for r in caplog.records if "Fill skipped" in r.getMessage()]
        assert len(per_fill) == 0

# [A_test] module_id: MOD-TEST-BT-TOY-NIGHT001 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md | §3.2 §16.7
# [MODULE] tests.backtest.test_toy_reconciliation_night001
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme;已知答案逐分对账（错一分钱即 bug）
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/backtest/test_toy_reconciliation_night001.py
# [TTL] permanent
# [ARCH-REF] AI-NIGHT-001 阶段2 端到端红蓝对抗（滑点双计/涨跌停板块推断/T+1/realized_pnl 修复后验证）
"""AI-NIGHT-001 阶段2 — Layer 1 已知答案测试（toy 逐分对账）。

手写固定价格序列 + 固定信号，过真实回测引擎
（vectorized_engine + matching_engine + matching_logic + portfolio，无任何 mock），
逐笔对账成交价/量/持仓/现金/成本，错一分钱即 bug。

对账口径（来自模块 docstring/SSoT 的公开规则，独立手算）:
  - 滑点: BUY 价 = base×(1+1bp) = base×1.0001; SELL 价 = base×0.9999
  - 佣金: max(qty×price×0.0003, 5)；卖出另加印花税 qty×price×0.001
  - total_cost: BUY = qty×price + commission；SELL = qty×price − commission
    （price 已含滑点，不得再加减 slippage_cost——#210 双计修复口径）
  - avg_cost = (旧成本×旧量 + qty×price + commission) / 新量
  - realized_pnl = (sell_price − avg_cost)×qty − sell_commission（不双计滑点）
  - 涨跌停: 主板 ±10% / 科创(68x)、创业(30x) ±20% / 北交(4/8/92x) ±30%，触板不成交
  - T+1: 买入当日不可卖（Portfolio 强制）

覆盖场景:
  ① 普通买卖各一笔（佣金+滑点逐分精确核算，Decimal 精确等值断言）
  ② 涨跌停日买单拒成——板块推断（主板10%/科创20%/北交30%）+ 引擎日频路径
  ③ T+1 当日买不可卖（Portfolio 强制 + 次日可卖）
  ④ 卖出回款精确（realized_pnl 无双计滑点——#210 修复后回归）
  ⑤ 引擎级 5 日全链对账（信号→撮合→记账→NAV 逐日手算）
  ⑥ P0 回归：停牌持仓 NAV 最后已知价结转（2026-08-19 阶段2 新发现修复）
  ⑦ P0 回归：跌出信号的持仓必须清仓（2026-08-19 阶段2 新发现修复）
  ⑧ 满仓信号成本收缩成交（2026-08-20 包3.2 登记项#2 修复后口径；
     原"满仓零成交+warning 显化"断言随修复目标行为淘汰，留痕见场景⑧类 docstring）
"""

from __future__ import annotations

import logging
from decimal import Decimal

import pandas as pd
import pytest

from zephyr.backtest.core.matching_engine import MatchingEngine
from zephyr.backtest.core.portfolio import BacktestFill, Portfolio, PortfolioError
from zephyr.backtest.implementations.vectorized_engine import (
    BacktestConfig,
    DefaultBacktestEngine,
)

D = Decimal

# 撮合默认口径：佣金万三/滑点1bp/印花税千一/最低佣金5元/100股整手
COMMISSION_RATE = D("0.0003")
SLIPPAGE = D("0.0001")  # 1bp
STAMP = D("0.001")


def _buy_cost(qty: int, base: str) -> D:
    """独立手算买入总成本（公开规则）。"""
    price = D(base) * (1 + SLIPPAGE)
    gross = D(qty) * price
    comm = max(gross * COMMISSION_RATE, D("5"))
    return gross + comm


def _sell_proceeds(qty: int, base: str) -> D:
    """独立手算卖出净回款（公开规则）。"""
    price = D(base) * (1 - SLIPPAGE)
    gross = D(qty) * price
    comm = max(gross * COMMISSION_RATE, D("5")) + gross * STAMP
    return gross - comm


# ─────────────────────────────────────────────────────────────────────────────
# 场景① 普通买卖各一笔（佣金+滑点逐分精确核算）
# ─────────────────────────────────────────────────────────────────────────────


class TestNormalBuySellExactReconciliation:
    """普通买卖：逐分对账 成交价/量/佣金/现金/成本。"""

    def test_buy_fill_fields_exact(self):
        """BUY 50,000股@10.00：价=10.001，佣金=150.015，总成本=500,200.015。"""
        engine = MatchingEngine()
        pf = Portfolio(initial_capital=D("1000000"))
        fills = engine.generate_fills(
            target_weights={"600000": 0.5},
            prices={"600000": D("10.00")},
            portfolio=pf,
            date="2026-08-03",
        )
        assert len(fills) == 1
        f = fills[0]
        assert f.side == "BUY"
        assert f.quantity == D("50000")  # floor(500000/10/100)*100
        assert f.price == D("10.001")  # 10.00×1.0001 精确
        assert f.commission == D("150.015")  # 500050×0.0003 > 5（不触最低佣金）
        assert f.slippage_cost == D("50")  # 信息字段: 0.001×50000
        # #210 口径: total_cost = gross+comm，不得再加 slippage_cost
        assert f.total_cost == D("500200.015")

    def test_buy_then_sell_portfolio_bookkeeping_exact(self):
        """买入→记账→卖出一半：现金/avg_cost/realized 逐分对账。"""
        engine = MatchingEngine()
        pf = Portfolio(initial_capital=D("1000000"))

        # Day1 买入
        fills = engine.generate_fills(
            target_weights={"600000": 0.5},
            prices={"600000": D("10.00")},
            portfolio=pf,
            date="2026-08-03",
        )
        for f in fills:
            pf.apply_fill(f)
        assert pf.cash == D("1000000") - D("500200.015") == D("499799.985")
        pos = pf.get_position("600000")
        assert pos.quantity == D("50000")
        # avg_cost = (50000×10.001 + 150.015)/50000 = 10.0040003 精确
        assert pos.avg_cost == D("10.0040003")
        assert pos.buy_date == "2026-08-03"

        # Day2 价格 11.00，降权至 0.25 → 卖 26,200 股
        fills2 = engine.generate_fills(
            target_weights={"600000": 0.25},
            prices={"600000": D("11.00")},
            portfolio=pf,
            date="2026-08-04",
        )
        assert len(fills2) == 1
        s = fills2[0]
        assert s.side == "SELL"
        # NAV = 499799.985 + 50000×11 = 1049799.985；target = 0.25×NAV = 262449.99625
        # qty = floor(262449.99625/11/100)×100 = 23800；diff = 23800−50000 = −26200
        assert s.quantity == D("26200")
        assert s.price == D("10.9989")  # 11×0.9999 精确
        # 佣金 = max(288171.18×0.0003,5) + 288171.18×0.001 = 86.451354 + 288.17118
        assert s.commission == D("374.622534")
        # 回款 = gross − comm（不双计滑点）
        assert s.total_cost == D("288171.18") - D("374.622534") == D("287796.557466")

        pf.apply_fill(s)
        assert pf.cash == D("499799.985") + D("287796.557466") == D("787596.542466")
        pos2 = pf.get_position("600000")
        assert pos2.quantity == D("23800")
        # realized = (10.9989 − 10.0040003)×26200 − 374.622534 = 25,691.749606 精确
        assert pos2.realized_pnl == D("25691.749606")

    def test_min_commission_floor(self):
        """小额买入触最低佣金 5 元。"""
        engine = MatchingEngine()
        pf = Portfolio(initial_capital=D("1000000"))
        # 100 股@10.00: gross=1000.10, 1000.10×0.0003=0.30003 < 5 → 佣金=5
        fills = engine.generate_fills(
            target_weights={"600000": 0.00001},  # target=10元 → qty=0 → 无单
            prices={"600000": D("10.00")},
            portfolio=pf,
            date="2026-08-03",
        )
        assert fills == []  # 目标额不足一手 → 不下单（A股整手约束）
        # 直接以较小权重达成 100 股: target ≥ 1000.10 → weight ≥ 0.0010001
        fills2 = engine.generate_fills(
            target_weights={"600000": 0.001},
            prices={"600000": D("10.00")},
            portfolio=pf,
            date="2026-08-03",
        )
        assert len(fills2) == 1
        assert fills2[0].quantity == D("100")
        assert fills2[0].commission == D("5")  # 触最低佣金
        assert fills2[0].total_cost == D("1000.10") + D("5")


# ─────────────────────────────────────────────────────────────────────────────
# 场景② 涨跌停日买单拒成——板块推断（主板10%/科创20%/北交30%）
# ─────────────────────────────────────────────────────────────────────────────


class TestPriceLimitBoardInference:
    """涨跌停按板块幅度拒单（#211 修复后验证）。"""

    @pytest.mark.parametrize(
        ("symbol", "price", "prev", "expect_filled"),
        [
            # 主板 ±10%: 11.00 = 10×1.10 触板拒成; 10.99 未触板成交
            ("600000", "11.00", "10.00", False),
            ("600000", "10.99", "10.00", True),
            ("000001", "11.00", "10.00", False),
            # 科创板(68x) ±20%: 11.50(+15%)成交; 12.00(+20%)触板拒成
            ("688001", "11.50", "10.00", True),
            ("688001", "12.00", "10.00", False),
            # 创业板(30x) ±20%（注册制起简化）
            ("300750", "11.50", "10.00", True),
            ("300750", "12.00", "10.00", False),
            # 北交所(4/8/92x) ±30%: 12.99(+29.9%)成交; 13.00(+30%)触板拒成
            ("830799", "12.99", "10.00", True),
            ("830799", "13.00", "10.00", False),
            ("920001", "13.00", "10.00", False),
        ],
    )
    def test_limit_up_buy_rejected_by_board(self, symbol, price, prev, expect_filled):
        engine = MatchingEngine()
        pf = Portfolio(initial_capital=D("1000000"))
        fills = engine.generate_fills(
            target_weights={symbol: 0.5},
            prices={symbol: D(price)},
            portfolio=pf,
            date="2026-08-04",
            prev_close={symbol: D(prev)},
        )
        if expect_filled:
            assert len(fills) == 1, f"{symbol}@{price} vs prev={prev} 应成交"
        else:
            assert fills == [], f"{symbol}@{price} vs prev={prev} 触板应拒成"

    def test_limit_down_sell_rejected(self):
        """跌停日持仓卖单拒成（ liquidation 也被阻断）。"""
        engine = MatchingEngine()
        pf = Portfolio(initial_capital=D("1000000"))
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
        # 次日 -10% 跌停，目标权重换仓 → A 的清仓卖单应被阻断
        fills = engine.generate_fills(
            target_weights={"600001": 0.5},
            prices={"600000": D("9.00"), "600001": D("10.00")},
            portfolio=pf,
            date="2026-08-04",
            prev_close={"600000": D("10.00"), "600001": D("10.00")},
        )
        sell_fills = [f for f in fills if f.side == "SELL"]
        assert sell_fills == [], "跌停日卖单应拒成"

    def test_engine_daily_path_limit_up_no_fill(self):
        """引擎日频路径：prev_close 逐日传递，涨停日买单阻断、次日非涨停成交。

        2026-08-20 包3.2 留痕：原版本以"day1 满仓买单因成本超现金被拒"制造
        零持仓前置；满仓成本摩擦修复（登记项#2）后满仓单收缩成交，前置不再
        成立。改为 day1 无信号（零持仓），day2 涨停日信号满仓 → 买单生成但
        被涨停阻断（撮合层跳过，连拒单 warning 都不应有），day3 非涨停成交。
        """
        dates = pd.bdate_range("2026-08-03", periods=3)
        closes = [10.00, 11.00, 11.00]  # day2 +10% 涨停
        rows = [{"symbol": "600000", "date": d, "close": c} for d, c in zip(dates, closes, strict=True)]
        data = pd.DataFrame(rows).set_index(["symbol", "date"])
        # day1 无信号（NaN → 不动作）；day2/day3 满仓信号
        sig = pd.DataFrame({"600000": [float("nan"), 1.0, 1.0]}, index=dates)
        engine = DefaultBacktestEngine(config=BacktestConfig())
        engine.run(data=data, signals=sig, strategy_name="toy-limit")
        pf = engine.last_portfolio
        trades = pf.trades_log
        # day2(08-04) 涨停：target=90,900 股买单生成 → 涨停阻断 → 零成交
        assert not [t for t in trades if t["date"].startswith("2026-08-04")]
        # day3(08-05) 非涨停（prev=11）：满仓买单收缩至可负担整手成交
        # target=floor(1,000,000/11/100)×100=90,900 → 成本 1,000,299.99>1,000,000
        # → 收缩 90,800 股（成本 999,199.55 可负担）
        day3 = [t for t in trades if t["date"].startswith("2026-08-05")]
        assert len(day3) == 1
        assert day3[0]["side"] == "BUY"
        assert day3[0]["quantity"] == 90800.0
        assert pf.get_position("600000").quantity == D("90800")


# ─────────────────────────────────────────────────────────────────────────────
# 场景③ T+1 当日买不可卖
# ─────────────────────────────────────────────────────────────────────────────


class TestTPlusOne:
    """T+1 锁定：买入当日卖出被拒，次日可卖。"""

    def test_same_day_sell_rejected(self):
        pf = Portfolio(initial_capital=D("1000000"))
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
        with pytest.raises(PortfolioError, match="T\\+1"):
            pf.apply_fill(
                BacktestFill(
                    date="2026-08-03",
                    symbol="600000",
                    side="SELL",
                    quantity=D("100"),
                    price=D("10.00"),
                    commission=D("5"),
                )
            )
        # 拒绝后持仓/现金未被污染
        assert pf.get_position("600000").quantity == D("10000")

    def test_next_day_sell_allowed(self):
        pf = Portfolio(initial_capital=D("1000000"))
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
        pf.apply_fill(
            BacktestFill(
                date="2026-08-04",
                symbol="600000",
                side="SELL",
                quantity=D("10000"),
                price=D("11.00"),
                commission=D("36.30"),
            )
        )
        assert pf.get_position("600000").quantity == D("0")

    def test_allow_t_plus_1_override(self):
        """allow_t_plus_1=True（做T通道）放行当日卖出。"""
        pf = Portfolio(initial_capital=D("1000000"))
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
        pf.apply_fill(
            BacktestFill(
                date="2026-08-03",
                symbol="600000",
                side="SELL",
                quantity=D("100"),
                price=D("10.00"),
                commission=D("5"),
            ),
            allow_t_plus_1=True,
        )
        assert pf.get_position("600000").quantity == D("9900")


# ─────────────────────────────────────────────────────────────────────────────
# 场景④ 卖出回款精确（realized_pnl 无双计滑点——#210 修复后回归）
# ─────────────────────────────────────────────────────────────────────────────


class TestSellProceedsNoDoubleSlippage:
    """#210 回归：realized_pnl / total_cost 不得再减 slippage_cost（价已含滑点）。"""

    def test_round_trip_cash_identity(self):
        """全往返现金恒等式: final_cash = initial − buy_cost + sell_proceeds，分文不差。"""
        pf = Portfolio(initial_capital=D("1000000"))
        buy = BacktestFill(
            date="2026-08-03",
            symbol="600000",
            side="BUY",
            quantity=D("50000"),
            price=D("10.001"),
            commission=D("150.015"),
            slippage_cost=D("50"),
        )
        pf.apply_fill(buy)
        sell = BacktestFill(
            date="2026-08-04",
            symbol="600000",
            side="SELL",
            quantity=D("50000"),
            price=D("10.9989"),
            commission=D("714.67017"),
            slippage_cost=D("55"),
        )
        pf.apply_fill(sell)
        # 独立手算: buy_cost = 50000×10.001+150.015 = 500,200.015
        # sell_proceeds = 50000×10.9989−714.67017 = 549,945−714.67017 = 549,230.32983
        expected_cash = D("1000000") - D("500200.015") + D("549230.32983")
        assert pf.cash == expected_cash == D("1049030.31483")
        # realized_pnl = (10.9989−10.0040003)×50000 − 714.67017
        #              = 49,744.985 − 714.67017 = 49,030.31483
        pos = pf.get_position("600000")
        assert pos.realized_pnl == D("49030.31483")
        # 清仓恒等式: realized_pnl == final_cash − initial_cash（无仓无其他流水）
        assert pos.realized_pnl == pf.cash - D("1000000")

    def test_slippage_cost_field_not_subtracted_again(self):
        """显式构造 slippage_cost≠0 的卖单：realized 公式中不得出现 slippage_cost 项。

        若回退到双计旧逻辑，realized 会少 55 元（slippage_cost），本断言精确拦截。
        """
        pf = Portfolio(initial_capital=D("1000000"))
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
        pf.apply_fill(
            BacktestFill(
                date="2026-08-04",
                symbol="600000",
                side="SELL",
                quantity=D("10000"),
                price=D("11.00"),
                commission=D("36.30"),
                slippage_cost=D("55"),  # 信息字段，不得进入 P&L
            )
        )
        pos = pf.get_position("600000")
        # avg_cost = (100000+30)/10000 = 10.003
        # 正确: (11−10.003)×10000−36.30 = 9970−36.30 = 9933.70
        # 双计错误: 9933.70−55 = 9878.70
        assert pos.realized_pnl == D("9933.70")
        # 现金同样不得双计: 1,000,000−100,030 + (110,000−36.30) = 1,009,933.70
        assert pf.cash == D("1009933.70")


# ─────────────────────────────────────────────────────────────────────────────
# 场景⑤ 引擎级 5 日全链对账（信号→撮合→记账→NAV 逐日手算）
# ─────────────────────────────────────────────────────────────────────────────


class TestEngineLevelToyReconciliation:
    """DefaultBacktestEngine 全链：固定价序+固定信号，逐日 NAV/持仓/现金手算对账。"""

    def test_five_day_full_chain_reconciliation(self):
        dates = pd.bdate_range("2026-08-03", periods=5)  # d1..d5
        # A: 10→10→10→11→11（d4 起 11，信号在 d4 清仓 A）；B: 恒定 1000（高价股，整手=10万）
        a_close = [10.0, 10.0, 10.0, 11.0, 11.0]
        rows = []
        for d, ca in zip(dates, a_close, strict=True):
            rows.append({"symbol": "600000", "date": d, "close": ca})
            rows.append({"symbol": "600519", "date": d, "close": 1000.0})
        data = pd.DataFrame(rows).set_index(["symbol", "date"])

        # 信号: d1 {A:0.6,B:0.3}；d2/d3 无信号（NaN → 不动作）；d4 {B:0.5}→归一化{B:1.0}（A 应清仓）；d5 无信号
        sig = pd.DataFrame(
            {
                "600000": [0.6, float("nan"), float("nan"), 0.0, float("nan")],
                "600519": [0.3, float("nan"), float("nan"), 0.5, float("nan")],
            },
            index=dates,
        )
        engine = DefaultBacktestEngine(config=BacktestConfig())
        result = engine.run(data=data, signals=sig, strategy_name="toy-5d")
        pf = engine.last_portfolio

        # ── d1 手算（NAV=1,000,000，归一化 {A:2/3, B:1/3}）──
        # A: target=666,666.67 → qty=floor(666666.67/10/100)×100=66,600
        #    price=10.001, gross=666,066.60, comm=199.81998, cost=666,266.41998
        # B: target=333,333.33 → qty=floor(333333.33/1000/100)×100=300
        #    price=1000.10, gross=300,030, comm=90.009, cost=300,120.009
        trades_d1 = [t for t in pf.trades_log if t["date"].startswith("2026-08-03")]
        assert len(trades_d1) == 2
        buy_a = next(t for t in trades_d1 if t["symbol"] == "600000")
        buy_b1 = next(t for t in trades_d1 if t["symbol"] == "600519")
        assert buy_a["quantity"] == 66600.0
        assert buy_a["price"] == 10.001
        assert buy_a["commission"] == pytest.approx(199.81998)
        assert buy_b1["quantity"] == 300.0
        assert buy_b1["price"] == 1000.1
        assert buy_b1["commission"] == pytest.approx(90.009)
        # cash_d1 = 1,000,000 − 666,266.41998 − 300,120.009 = 33,613.57102
        cash_d1 = D("1000000") - D("666266.41998") - D("300120.009")

        # ── d4 手算（A=11 涨停价；prev={A:10,B:1000}）──
        # NAV = 33,613.57102 + 66,600×11 + 300×1000 = 1,066,213.57102
        # A 清仓（跌出信号；涨停日卖单可成交——方向感知阻断）: sell 66,600@10.9989
        #   gross=732,526.74, comm=219.758022+732.52674=952.284762, 回款=731,574.455238
        # B 补仓: target=NAV → qty=1,000, diff=700 @ 1000.10
        #   gross=700,070, comm=210.021, cost=700,280.021
        trades_d4 = [t for t in pf.trades_log if t["date"].startswith("2026-08-06")]
        assert len(trades_d4) == 2
        sell_a = next(t for t in trades_d4 if t["symbol"] == "600000")
        buy_b = next(t for t in trades_d4 if t["symbol"] == "600519")
        assert sell_a["side"] == "SELL" and sell_a["quantity"] == 66600.0
        assert sell_a["price"] == pytest.approx(10.9989)
        assert sell_a["commission"] == pytest.approx(952.284762)
        assert buy_b["side"] == "BUY" and buy_b["quantity"] == 700.0
        assert buy_b["price"] == 1000.1
        assert buy_b["commission"] == pytest.approx(210.021)

        # ── 终态对账（d5 无信号，持仓不变）──
        # 现金 = cash_d1 + 731,574.455238 − 700,280.021 = 64,908.005258
        expected_cash = cash_d1 + D("731574.455238") - D("700280.021")
        assert pf.cash == expected_cash == D("64908.005258")
        pos_a = pf.get_position("600000")
        assert pos_a.quantity == D("0")
        pos_b = pf.get_position("600519")
        assert pos_b.quantity == D("1000")
        assert pos_b.avg_cost == D("1000.40003")  # (300,120.009+700,070+210.021)/1000

        # A 已实现盈亏 = (10.9989−10.0040003)×66,600 − 952.284762
        #             = 66,260.32002 − 952.284762 = 65,308.035258
        assert pos_a.realized_pnl == D("65308.035258")

        # ── 逐日 NAV 手算 ──
        nav = pf.nav_series
        assert float(nav.iloc[0]) == 1_000_000.0  # 初始
        # 价序: d1..d3 A=10/B=1000 → NAV = 33,613.57102+666,000+300,000 = 999,613.57102
        d_low_nav = 999_613.57102
        assert float(nav.iloc[1]) == pytest.approx(d_low_nav, abs=1e-6)
        assert float(nav.iloc[2]) == pytest.approx(d_low_nav, abs=1e-6)
        assert float(nav.iloc[3]) == pytest.approx(d_low_nav, abs=1e-6)
        d4_nav = 64_908.005258 + 1000 * 1000.0  # 1,064,908.005258
        assert float(nav.iloc[4]) == pytest.approx(d4_nav, abs=1e-6)
        assert float(nav.iloc[5]) == pytest.approx(d4_nav, abs=1e-6)

        # ── BacktestResult 与手算终值一致 ──
        assert result.total_return == pytest.approx(64_908.005258 / 1_000_000, rel=1e-9)
        assert result.trades_count == 4


# ─────────────────────────────────────────────────────────────────────────────
# 场景⑥ P0 回归：停牌/缺价持仓 NAV 最后已知价结转（2026-08-19 阶段2 修复）
# ─────────────────────────────────────────────────────────────────────────────


class TestSuspendedPositionNavCarryForward:
    """停牌日持仓不得按 0 估值（幻视回撤/幻视恢复污染 Sharpe/MDD）。"""

    def test_suspended_day_nav_uses_last_known_price(self):
        pf = Portfolio(initial_capital=D("1000000"))
        pf.apply_fill(
            BacktestFill(
                date="2026-08-03",
                symbol="600000",
                side="BUY",
                quantity=D("1000"),
                price=D("10.00"),
                commission=D("5"),
            )
        )
        nav_d1 = pf.update_market_value("2026-08-03", {"600000": D("10.00")})
        nav_d2 = pf.update_market_value("2026-08-04", {})  # 停牌：无价格
        nav_d3 = pf.update_market_value("2026-08-05", {"600000": D("10.50")})  # 复牌
        assert nav_d1 == nav_d2  # 停牌日 NAV 不幻视下跌
        assert nav_d2 == D("1000000") - D("10005") + D("10000")
        assert nav_d3 == D("1000000") - D("10005") + D("10500")

    def test_total_nav_carry_forward_for_matching_sizing(self):
        """matching_engine 目标 sizing 用 total_nav：缺价日不得低估 NAV。"""
        pf = Portfolio(initial_capital=D("1000000"))
        pf.apply_fill(
            BacktestFill(
                date="2026-08-03",
                symbol="600000",
                side="BUY",
                quantity=D("1000"),
                price=D("10.00"),
                commission=D("5"),
            )
        )
        # 缺价日 total_nav 应结转 10.00 → 989,995+10,000 = 999,995（而非 989,995）
        nav = pf.total_nav({})
        assert nav == D("999995")

    def test_zero_price_treated_as_missing(self):
        """price<=0 视为无效（不覆盖最后已知价）。"""
        pf = Portfolio(initial_capital=D("1000000"))
        pf.apply_fill(
            BacktestFill(
                date="2026-08-03",
                symbol="600000",
                side="BUY",
                quantity=D("1000"),
                price=D("10.00"),
                commission=D("5"),
            )
        )
        nav = pf.update_market_value("2026-08-04", {"600000": D("0")})
        assert nav == D("999995")


# ─────────────────────────────────────────────────────────────────────────────
# 场景⑦ P0 回归：跌出信号的持仓必须清仓（2026-08-19 阶段2 修复）
# ─────────────────────────────────────────────────────────────────────────────


class TestRotationLiquidation:
    """目标权重语义：持仓但不在目标权重（或权重<=0）→ 清仓卖单。"""

    def test_dropped_symbol_liquidated(self):
        engine = MatchingEngine()
        pf = Portfolio(initial_capital=D("1000000"))
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
        # 次日信号只含 B → A 必须清仓
        fills = engine.generate_fills(
            target_weights={"600001": 0.5},
            prices={"600000": D("10.00"), "600001": D("10.00")},
            portfolio=pf,
            date="2026-08-04",
        )
        sell_a = [f for f in fills if f.symbol == "600000" and f.side == "SELL"]
        assert len(sell_a) == 1
        assert sell_a[0].quantity == D("10000")  # 全量清仓
        # 先卖后买：SELL 排在 BUY 前（现金链正确）
        sides = [f.side for f in fills]
        assert sides == sorted(sides, key=lambda s: 0 if s == "SELL" else 1)

    def test_held_symbol_absent_but_suspended_not_sold(self):
        """跌出信号但当日无价（停牌）→ 不产生卖单（无法成交），持仓保留待复牌。"""
        engine = MatchingEngine()
        pf = Portfolio(initial_capital=D("1000000"))
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
        fills = engine.generate_fills(
            target_weights={"600001": 0.5},
            prices={"600001": D("10.00")},  # 600000 无价
            portfolio=pf,
            date="2026-08-04",
        )
        assert all(f.symbol != "600000" for f in fills)

    def test_engine_rotation_end_to_end(self):
        """引擎级轮动回归：A 轮出 → 清仓，B 轮入成功（现金链不被滞留持仓锁死）。"""
        dates = pd.bdate_range("2026-08-03", periods=5)
        rows = []
        for sym in ("600000", "600001", "600002"):
            for d in dates:
                rows.append({"symbol": sym, "date": d, "close": 10.0})
        data = pd.DataFrame(rows).set_index(["symbol", "date"])
        sig = pd.DataFrame(
            {
                "600000": [0.6, 0.6, 0.0, 0.0, 0.0],
                "600001": [0.0, 0.0, 0.6, 0.6, 0.6],
                "600002": [0.4, 0.4, 0.4, 0.4, 0.4],
            },
            index=dates,
        )
        engine = DefaultBacktestEngine(config=BacktestConfig())
        engine.run(data=data, signals=sig, strategy_name="toy-rotate")
        pf = engine.last_portfolio
        # d3 起 A 必须零持仓
        assert pf.get_position("600000").quantity == D("0")
        # B 轮入成功（修复前：现金被 A 锁死 → B 连续 3 天买入被拒）
        assert pf.get_position("600001").quantity > 0
        # A 的清仓卖单真实发生
        sells_a = [
            t
            for t in pf.trades_log
            if t["symbol"] == "600000" and t["side"] == "SELL" and t["date"].startswith("2026-08-05")
        ]
        assert len(sells_a) == 1 and sells_a[0]["quantity"] == 59900.0


# ─────────────────────────────────────────────────────────────────────────────
# 场景⑧ 满仓信号成本收缩成交（2026-08-20 包3.2 登记项#2 修复后口径）
# ─────────────────────────────────────────────────────────────────────────────


class TestFullWeightCostFrictionFill:
    """满仓（Σ=1 单标的）信号：sizing 预留成本余量收缩至可负担整手成交。

    2026-08-20 包3.2 留痕：本类原为 TestFullWeightZeroFillWarning，断言
    "满仓买入必超现金 → 零成交 + Fill skipped warning 显化"（红队向量②对
    #210 可见性的验证）。该行为即登记项#2 登记的结构性摩擦本身，修复后
    （matching_engine._clamp_buys_to_projected_cash）满仓单收缩成交、不再
    触发拒单——原断言口径随修复目标行为一并淘汰（评估：测试口径过时，
    非代码回退）。#210 的 warning 显化机制仍保留于 vectorized_engine
    （防御性最终防线，clamp 估算与实际成交口径一致时不再触达）。
    """

    def test_full_weight_fills_after_clamp(self, caplog):
        dates = pd.bdate_range("2026-08-03", periods=2)
        rows = [{"symbol": "600000", "date": d, "close": 10.0} for d in dates]
        data = pd.DataFrame(rows).set_index(["symbol", "date"])
        sig = pd.DataFrame({"600000": [1.0, 1.0]}, index=dates)  # 归一化后仍为 1.0 满仓
        engine = DefaultBacktestEngine(config=BacktestConfig())
        with caplog.at_level(logging.WARNING, logger="zephyr.backtest.implementations.vectorized_engine"):
            result = engine.run(data=data, signals=sig, strategy_name="toy-fullweight")
        pf = engine.last_portfolio
        # 满仓成本收缩：100,000 股成本 1,000,400.03>1,000,000 → 收缩至 99,900 股
        # （成本 999,399.62997 可负担）；day2 NAV 口径下 target=99,900 → diff=0 无单
        assert result.trades_count == 1
        pos = pf.get_position("600000")
        assert pos.quantity == D("99900")
        # 逐分对账：cash = 1,000,000 − 999,399.62997 = 600.37003
        assert pf.cash == D("600.37003")
        # 满仓不再触发拒单 warning（修复目标行为）
        per_fill = [r for r in caplog.records if "Fill skipped" in r.getMessage()]
        summary = [r for r in caplog.records if "fill 被拒绝" in r.getMessage()]
        assert per_fill == [] and summary == []

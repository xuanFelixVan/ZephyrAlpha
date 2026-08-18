# [A_test] module_id: MOD-EXE-risk_layer_orchestrator_test | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md | §
# [MODULE] tests.ex_core.test_risk_layer_orchestrator
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""RiskLayerOrchestrator — 风控层运行时接线红队实证测试（#ARCH-100，AI-RWIRE-001）。

实证目标（验收①，非 mock 全替——DrawdownController/DrawdownTracker/VaRCalculator/
TailRiskMonitor/PositionReconciler/DefaultRiskValidator/stop_loss 清算链全部真实
实例，仅 broker 为测试替身——broker 是真实部署中唯一外部边界）：
  1. 回撤 25% → EMERGENCY → trigger_kill_switch（状态层真实置位）
     → execute_kill_switch_liquidation 真实清算全部持仓 + 撤挂单；
     熔断后 rebalance 整批拒下；重复触发不重复清算（单一仲裁点）
  2. 重启后 recover_from_broker 以券商持仓为准重建 PositionTracker；
     重建未完成/失败 → 下单被拒（Fail-Closed）
  3. VaR 黄级 → position_cap=0.5 缩放目标权重；红级 → 禁止新开仓
  4. PositionReconciler  drift → 冻结标的下单硬拦；定时对账循环启停
  5. 系统性风险 LEVEL_3 逃生链（AI-LVL3-001，37 号 §3.3）：≥3 信号 → LEVEL_3
     → build_escape_directive 真实产出 → 同一仲裁点真实置位清算全链；
     情绪断路器 0.85 强制升级；非 LEVEL_3 调用逃生执行器抛错 + LEVEL_1/2
     不触发熔断
  6. 降级机（37 号 §3.6）：LEVEL_3→LEVEL_2 冷却 30min+信号≤2+spread<0.3%
     逐级降级（3→2→1→0 hysteresis 门控）；降级不解除熔断闩锁
     （35 号 KILL 态人工复位不变式）
"""

from __future__ import annotations

import threading
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from zephyr.ex_core.order_manager import OrderManager
from zephyr.ex_core.position_reconciler import PositionReconciler
from zephyr.ex_core.position_tracker.tracker import PositionTracker
from zephyr.ex_core.risk_layer_orchestrator import (
    RiskLayerConfig,
    RiskLayerOrchestrator,
)
from zephyr.ex_core.trading_session import TradingSession, TradingSessionConfig
from zephyr.position.core.drawdown_controller import DrawdownController
from zephyr.risk.core.ashare_systemic_risk_detector import (
    AshareSystemicRiskDetector,
    InvalidSystemicRiskInputError,
)
from zephyr.risk.core.drawdown_tracker import DrawdownAlertLevel, DrawdownTracker
from zephyr.risk.core.tail_risk_monitor import TailRiskMonitor
from zephyr.risk.core.var_calculator import VaRCalculator
from zephyr.risk.implementations.default_risk_validator import DefaultRiskValidator
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderType
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.order import Order
from zephyr.shared.contracts.position import PositionSnapshot
from zephyr.shared.contracts.risk_limits import RiskLimits
from zephyr.trading.trading_contracts.broker_interface import BrokerInterface

# ---------------------------------------------------------------------
# 测试替身（仅外部边界：broker / 策略 / 行情）
# ---------------------------------------------------------------------


class FakeBroker(BrokerInterface):
    """券商替身：持仓/现金可配，记录全部提交订单与撤单。"""

    def __init__(
        self,
        cash: Decimal = Decimal("1000000"),
        holdings: dict[str, Decimal] | None = None,
        cost_prices: dict[str, Decimal] | None = None,
        today_fills: list[tuple[Fill, OrderSide]] | None = None,
    ) -> None:
        self._cash = cash
        self._holdings: dict[str, Decimal] = dict(holdings or {})
        self._costs: dict[str, Decimal] = dict(cost_prices or {})
        self._today_fills = today_fills
        self.submitted: list[Order] = []
        self.cancelled: list[str] = []
        self.fail_get_positions = False

    @property
    def broker_id(self) -> str:
        return "fake"

    def connect(self) -> bool:
        return True

    def disconnect(self) -> None:
        pass

    def submit_order(self, order: Order) -> str:
        self.submitted.append(order)
        return f"bk-{order.order_id}"

    def cancel_order(self, broker_order_id: str) -> bool:
        self.cancelled.append(broker_order_id)
        return True

    def query_order(self, broker_order_id: str) -> Order | None:
        return None

    def get_positions(self) -> PositionSnapshot:
        if self.fail_get_positions:
            raise RuntimeError("broker get_positions down")
        mv = {
            s: qty * self._costs.get(s, Decimal("0"))
            for s, qty in self._holdings.items()
            if qty != 0
        }
        return PositionSnapshot(
            as_of_timestamp=datetime.now(UTC),
            portfolio_id="fake",
            idempotency_key="fake",
            cash=self._cash,
            gross_leverage=0.0,
            holdings={s: q for s, q in self._holdings.items() if q != 0},
            market_values=mv,
            total_market_value=sum(mv.values(), Decimal("0")),
        )

    def get_today_fills(self) -> list[tuple[Fill, OrderSide]]:
        """broker 可选扩展：当日成交查询（恢复编排消费）。"""
        return list(self._today_fills or [])

    def register_fill_callback(self, callback) -> None:
        pass


class RebuildableTracker(PositionTracker):
    """按 AI-RRESIL-001 约定签名实现 rebuild_from_broker 的测试替身。

    签名约定：rebuild_from_broker(holdings: dict, today_fills: list) -> None
    （merge 时与 RRESIL 真实实现对齐；本替身语义=以券商为准全量覆盖）。
    """

    def rebuild_from_broker(self, holdings: dict, today_fills: list) -> None:
        self.reset()
        for fill, side in today_fills:
            self.apply_fill(fill, side)
        with self._lock:
            for symbol, qty in holdings.items():
                self._holdings[symbol] = Decimal(str(qty))
                if self._avg_costs.get(symbol, Decimal("0")) == Decimal("0"):
                    self._avg_costs[symbol] = Decimal("0")


def _make_orchestrator(
    *,
    broker: FakeBroker,
    tracker: PositionTracker | None = None,
    initial_nav: float = 1_000_000.0,
    kill_owner: DefaultRiskValidator | None = None,
    reconciler: PositionReconciler | None = None,
    open_orders: dict[str, dict] | None = None,
    config: RiskLayerConfig | None = None,
) -> RiskLayerOrchestrator:
    return RiskLayerOrchestrator(
        drawdown_controller=DrawdownController(),
        drawdown_tracker=DrawdownTracker(initial_net_value=initial_nav),
        var_calculator=VaRCalculator(),
        tail_risk_monitor=TailRiskMonitor(),
        broker=broker,
        position_tracker=tracker,
        kill_switch_owner=kill_owner,
        reconciler=reconciler,
        open_orders_provider=(lambda: dict(open_orders)) if open_orders is not None else None,
        config=config,
    )


def _make_session(
    *,
    broker: FakeBroker,
    risk_layer: RiskLayerOrchestrator | None,
    target_weights: dict[str, float] | None = None,
    prices: dict[str, Decimal] | None = None,
    validator: DefaultRiskValidator | None = None,
) -> TradingSession:
    """构建真实 OrderManager + 真实风控校验 + mock 策略/行情的 TradingSession。"""
    om = OrderManager()
    om.register_broker("fake", broker)
    strategy = MagicMock()
    strategy.generate_target_weights.return_value = dict(target_weights or {})
    config = TradingSessionConfig(
        universe=["600000.SH", "000001.SZ"],
        broker_id="fake",
        risk_limits=RiskLimits(
            as_of_date=datetime.now(UTC),
            idempotency_key="test-limits",
            max_single_position=1.0,
            max_gross_leverage=10.0,
        ),
    )
    # 隔离订单层熔断（本批测风控层接线，不测订单层熔断）
    config.max_single_order_pct = Decimal("1.0")
    config.max_symbol_orders_per_day = 999999
    config.max_total_orders_per_day = 999999
    return TradingSession(
        broker=broker,
        strategy=strategy,
        risk_validator=validator or DefaultRiskValidator(),
        signal_provider=lambda _u: {},
        price_provider=lambda _u: dict(prices or {}),
        order_manager=om,
        config=config,
        risk_layer=risk_layer,
    )


# ---------------------------------------------------------------------
# 红队实证①：回撤 25% → EMERGENCY → 熔断 → 清算全链真实触发
# ---------------------------------------------------------------------


class TestEmergencyKillChain:
    """回撤 EMERGENCY 全链：真实组件，仅 broker 替身。"""

    def test_drawdown_25pct_triggers_kill_switch_and_liquidation(self) -> None:
        validator = DefaultRiskValidator()
        broker = FakeBroker(
            cash=Decimal("500000"),
            holdings={
                "600000.SH": Decimal("5000"),
                "000001.SZ": Decimal("3000"),
                "300750.SZ": Decimal("1000"),
            },
        )
        orch = _make_orchestrator(
            broker=broker,
            kill_owner=validator,
            initial_nav=1_000_000.0,
            open_orders={"bk-open-1": {"symbol": "600000.SH"}},
        )

        orch.evaluate_intraday(1_000_000.0)  # 峰值锚定
        assert not validator.kill_switch_active

        snap = orch.evaluate_intraday(750_000.0)  # -25% → EMERGENCY

        assert snap.drawdown_level is DrawdownAlertLevel.EMERGENCY
        # 状态层熔断真实置位（DefaultRiskValidator 公共接口）
        assert validator.kill_switch_active is True
        assert orch.kill_switch_engaged is True
        assert orch.is_trading_allowed is False
        # 清算真实执行：3 持仓全平（MARKET SELL）+ 挂单全撤
        liquidated = {(o.symbol, o.side, o.quantity) for o in broker.submitted}
        assert liquidated == {
            ("600000.SH", OrderSide.SELL, Decimal("5000")),
            ("000001.SZ", OrderSide.SELL, Decimal("3000")),
            ("300750.SZ", OrderSide.SELL, Decimal("1000")),
        }
        assert all(o.order_type is OrderType.MARKET for o in broker.submitted)
        assert broker.cancelled == ["bk-open-1"]
        report = orch._kill_switch_report
        assert report is not None and report["report"]["all_success"] is True
        assert len(report["report"]["liquidation_orders"]) == 3

    def test_single_arbitration_no_duplicate_liquidation(self) -> None:
        """EMERGENCY 去抖 + 仲裁标志：再次触发不重复清算。"""
        broker = FakeBroker(cash=Decimal("0"), holdings={"600000.SH": Decimal("1000")})
        orch = _make_orchestrator(broker=broker, initial_nav=1_000_000.0)

        orch.evaluate_intraday(1_000_000.0)
        orch.evaluate_intraday(750_000.0)   # EMERGENCY 首次触发
        assert len(broker.submitted) == 1
        orch.evaluate_intraday(740_000.0)   # 仍 EMERGENCY（级别未变，事件去抖）
        orch.evaluate_intraday(1_000_000.0)  # 恢复 NONE
        orch.evaluate_intraday(730_000.0)   # 再次 EMERGENCY（事件发射但仲裁拦截）
        assert len(broker.submitted) == 1  # 清算仅一次

    def test_session_level_kill_chain_blocks_rebalance(self) -> None:
        """会话级集成：盘中评估触发熔断，同循环 + 后续循环整批拒下。"""
        validator = DefaultRiskValidator()
        broker = FakeBroker(
            cash=Decimal("500000"),
            holdings={"600000.SH": Decimal("5000"), "000001.SZ": Decimal("3000")},
            cost_prices={"600000.SH": Decimal("100"), "000001.SZ": Decimal("50")},
        )
        orch = _make_orchestrator(broker=broker, kill_owner=validator, initial_nav=1_150_000.0)
        prices = {"600000.SH": Decimal("100"), "000001.SZ": Decimal("50")}
        session = _make_session(
            broker=broker,
            risk_layer=orch,
            target_weights={"600000.SH": 0.5},
            prices=prices,
            validator=validator,
        )
        session.start()
        try:
            assert orch.is_trading_allowed is True
            # 价格崩 40%：nav = 500k + 300k + 90k = 890k → 回撤 -22.6% → EMERGENCY
            prices["600000.SH"] = Decimal("60")
            prices["000001.SZ"] = Decimal("30")
            submitted = session.rebalance()
            assert submitted == []  # 同循环熔断即拒下
            assert validator.kill_switch_active is True
            # 清算单已下（2 笔 SELL），无调仓买单
            assert all(o.side is OrderSide.SELL for o in broker.submitted)
            assert len(broker.submitted) == 2
            # 后续循环仍拒下（熔断保持）
            assert session.rebalance() == []
            assert len(broker.submitted) == 2
        finally:
            session.stop()


# ---------------------------------------------------------------------
# 红队实证②：启动恢复——以券商为准重建 + 重建期 Fail-Closed 禁单
# ---------------------------------------------------------------------


class TestStartupRecovery:
    def test_rebuild_from_broker_holdings_authoritative(self) -> None:
        """重启后持仓以券商为准：本地账清零，券商账 5000 股重建进 tracker。"""
        fill = Fill(
            fill_id="f-1",
            fill_price=Decimal("100"),
            fill_timestamp=datetime.now(UTC),
            filled_quantity=Decimal("5000"),
            idempotency_key="k-1",
            order_id="o-1",
            strategy_id="s",
            symbol="600000.SH",
        )
        broker = FakeBroker(
            cash=Decimal("500000"),
            holdings={"600000.SH": Decimal("5000")},
            cost_prices={"600000.SH": Decimal("100")},
            today_fills=[(fill, OrderSide.BUY)],
        )
        tracker = RebuildableTracker(initial_cash=Decimal("1000000"))
        orch = _make_orchestrator(broker=broker, tracker=tracker)

        result = orch.recover_from_broker()

        assert result.success is True
        assert result.holdings_count == 1
        assert result.fills_count == 1
        assert tracker.get_positions().holdings == {"600000.SH": Decimal("5000")}
        assert orch.is_trading_allowed is True

    def test_orders_rejected_before_recovery(self) -> None:
        """重建完成前（recover 未调用）rebalance 整批拒下。"""
        broker = FakeBroker()
        orch = _make_orchestrator(broker=broker)
        session = _make_session(broker=broker, risk_layer=orch, target_weights={"600000.SH": 0.1})

        assert orch.recovery_completed is False
        assert session.rebalance() == []
        assert broker.submitted == []

    def test_orders_rejected_on_recovery_failure(self) -> None:
        """重建失败（券商查询不可用）→ Fail-Closed 保持禁单。"""
        broker = FakeBroker()
        broker.fail_get_positions = True
        orch = _make_orchestrator(broker=broker)
        session = _make_session(broker=broker, risk_layer=orch, target_weights={"600000.SH": 0.1})

        session.start()
        try:
            assert orch.recovery_completed is False
            assert orch.is_trading_allowed is False
            assert session.rebalance() == []
            assert broker.submitted == []
        finally:
            session.stop()

    def test_session_start_recovers_then_allows_trading(self) -> None:
        """会话启动恢复完成后正常下单（恢复→评估→调仓全链贯通）。"""
        broker = FakeBroker(cash=Decimal("1000000"))
        orch = _make_orchestrator(broker=broker)
        session = _make_session(
            broker=broker,
            risk_layer=orch,
            target_weights={"600000.SH": 0.1},
            prices={"600000.SH": Decimal("100")},
        )
        session.start()
        try:
            submitted = session.rebalance()
            assert len(submitted) == 1
            assert submitted[0].side is OrderSide.BUY
            assert submitted[0].quantity == Decimal("1000")  # 1M*0.1/100
        finally:
            session.stop()


# ---------------------------------------------------------------------
# position_cap 喂仓位上限链
# ---------------------------------------------------------------------


def _seed_oscillating_nav(orch: RiskLayerOrchestrator, up: float, rounds: int = 31) -> None:
    """注入交替涨跌净值序列（构造指定波动率的收益样本）。"""
    for i in range(rounds):
        orch.evaluate_intraday(1_000_000.0 * (up if i % 2 else 1.0))


class TestPositionCapChain:
    def test_yellow_var_scales_target_weights(self) -> None:
        """VaR 黄级（2%<VaR≤4%）→ position_cap=0.5 → 目标权重 0.8 缩放到 0.5。"""
        broker = FakeBroker(cash=Decimal("1000000"))
        orch = _make_orchestrator(broker=broker)
        assert orch.recover_from_broker().success is True
        _seed_oscillating_nav(orch, up=1.018)  # 日波动 ~1.8% → VaR ~2.9% → 黄级

        snap = orch.evaluate_intraday(1_000_000.0)
        assert snap.response is not None
        assert snap.response.risk_level.value == "YELLOW"
        assert snap.position_cap == pytest.approx(0.5)
        assert snap.allow_new_position is True

        session = _make_session(
            broker=broker,
            risk_layer=orch,
            target_weights={"600000.SH": 0.8},
            prices={"600000.SH": Decimal("100")},
        )
        submitted = session.rebalance()
        # 0.8 × (0.5/0.8) = 0.5 → 1M × 0.5 / 100 = 5000 股
        assert len(submitted) == 1
        assert submitted[0].quantity == Decimal("5000")

    def test_red_var_blocks_new_positions(self) -> None:
        """VaR 红级（>6%）→ allow_new_position=False → 买单被滤除。"""
        broker = FakeBroker(cash=Decimal("1000000"))
        orch = _make_orchestrator(broker=broker)
        assert orch.recover_from_broker().success is True
        _seed_oscillating_nav(orch, up=1.05)  # 日波动 ~4.9% → VaR ~8% → 红级

        snap = orch.evaluate_intraday(1_000_000.0)
        assert snap.response is not None
        assert snap.response.risk_level.value == "RED"
        assert snap.allow_new_position is False

        session = _make_session(
            broker=broker,
            risk_layer=orch,
            target_weights={"600000.SH": 0.3},
            prices={"600000.SH": Decimal("100")},
        )
        assert session.rebalance() == []
        assert broker.submitted == []

    def test_insufficient_samples_degraded_not_blocking(self) -> None:
        """收益样本不足 → degraded 标记 + 不加仓位约束（开盘初正常态）。"""
        broker = FakeBroker(cash=Decimal("1000000"))
        orch = _make_orchestrator(broker=broker)
        assert orch.recover_from_broker().success is True

        snap = orch.evaluate_intraday(1_000_000.0)
        assert snap.degraded is True
        assert "insufficient_returns" in snap.degrade_reason
        assert snap.position_cap == 1.0

        session = _make_session(
            broker=broker,
            risk_layer=orch,
            target_weights={"600000.SH": 0.1},
            prices={"600000.SH": Decimal("100")},
        )
        assert len(session.rebalance()) == 1  # 不阻断


# ---------------------------------------------------------------------
# PositionReconciler 盘中对账接入（蓝图阶段2规划位）
# ---------------------------------------------------------------------


class TestIntradayReconcile:
    def test_frozen_symbol_blocked_in_rebalance(self) -> None:
        """对账 drift → 标的冻结 → 该标的订单硬拦。"""
        broker = FakeBroker(cash=Decimal("1000000"))  # 券商账：无持仓
        tracker = RebuildableTracker(initial_cash=Decimal("1000000"))
        reconciler = PositionReconciler(system_source=tracker, broker_source=broker)
        orch = _make_orchestrator(broker=broker, tracker=tracker, reconciler=reconciler)
        assert orch.recover_from_broker().success is True

        # 模拟系统账漂移：成交回报多记 100 股（券商账没有）
        drift_fill = Fill(
            fill_id="f-drift",
            fill_price=Decimal("10"),
            fill_timestamp=datetime.now(UTC),
            filled_quantity=Decimal("100"),
            idempotency_key="k-drift",
            order_id="o-drift",
            strategy_id="s",
            symbol="600000.SH",
        )
        tracker.apply_fill(drift_fill, OrderSide.BUY)

        assert orch.run_reconcile_once() is False
        assert orch.is_symbol_frozen("600000.SH") is True

        session = _make_session(
            broker=broker,
            risk_layer=orch,
            target_weights={"600000.SH": 0.1},
            prices={"600000.SH": Decimal("10")},
        )
        submitted = session.rebalance()
        assert submitted == []
        assert any(o.symbol == "600000.SH" for o in session._blocked_orders)

    def test_reconcile_loop_start_stop(self) -> None:
        """定时对账循环：drift 出现后自动冻结；stop 后定时器清理。"""
        broker = FakeBroker(cash=Decimal("1000000"))
        tracker = RebuildableTracker(initial_cash=Decimal("1000000"))
        drift_seen = threading.Event()

        def _on_drift(_result: object) -> None:
            drift_seen.set()

        reconciler = PositionReconciler(
            system_source=tracker,
            broker_source=broker,
            on_drift=_on_drift,
        )
        orch = _make_orchestrator(
            broker=broker,
            tracker=tracker,
            reconciler=reconciler,
            config=RiskLayerConfig(reconcile_interval_seconds=0.05),
        )
        assert orch.recover_from_broker().success is True
        # 制造 drift 后启动循环
        tracker.apply_fill(
            Fill(
                fill_id="f-loop",
                fill_price=Decimal("10"),
                fill_timestamp=datetime.now(UTC),
                filled_quantity=Decimal("100"),
                idempotency_key="k-loop",
                order_id="o-loop",
                strategy_id="s",
                symbol="600000.SH",
            ),
            OrderSide.BUY,
        )
        orch.start_reconcile_loop()
        try:
            assert drift_seen.wait(timeout=5.0) is True
            assert orch.is_symbol_frozen("600000.SH") is True
        finally:
            orch.stop_reconcile_loop()
        assert orch._reconcile_timer is None


# ---------------------------------------------------------------------
# 红队实证⑤：系统性风险 LEVEL_3 逃生链（37 号 §3.3，AI-LVL3-001）
# ---------------------------------------------------------------------

_T0 = datetime(2026, 8, 17, 10, 0, tzinfo=UTC)

# 三信号齐发：流动性危机（卖压 0.80 + 价差 1%）+ 量化踩踏（指数 -3% + 量 2.5x）
# + 外围冲击（-4%）
_LEVEL3_INPUTS = {
    "sell_pressure": 0.80,
    "bid_ask_spread": 0.01,
    "index_change_pct": -0.03,
    "volume_surge_ratio": 2.5,
    "external_market_change": -0.04,
}
# 危机消退：卖压/价差回正常，0 信号
_CALM_INPUTS = {"sell_pressure": 0.30, "bid_ask_spread": 0.001}


def _make_systemic_orchestrator(
    *,
    broker: FakeBroker,
    kill_owner: DefaultRiskValidator | None = None,
    open_orders: dict[str, dict] | None = None,
    config: RiskLayerConfig | None = None,
) -> tuple[RiskLayerOrchestrator, dict[str, dict]]:
    """真实组件 + 可变系统性输入盒（provider 契约=detector.check 关键字映射）。"""
    inputs_box: dict[str, dict] = {"data": {}}
    orch = RiskLayerOrchestrator(
        drawdown_controller=DrawdownController(),
        drawdown_tracker=DrawdownTracker(initial_net_value=1_000_000.0),
        var_calculator=VaRCalculator(),
        tail_risk_monitor=TailRiskMonitor(),
        broker=broker,
        kill_switch_owner=kill_owner,
        open_orders_provider=(lambda: dict(open_orders)) if open_orders is not None else None,
        systemic_detector=AshareSystemicRiskDetector(),
        systemic_input_provider=lambda: dict(inputs_box["data"]),
        config=config,
    )
    return orch, inputs_box


class TestSystemicLevel3EscapeChain:
    """红队向量①：≥3 信号 → LEVEL_3 真实触发 → 逃生指令 → Kill Switch 真实清算全链。"""

    def test_three_signals_level3_full_chain(self) -> None:
        validator = DefaultRiskValidator()
        broker = FakeBroker(
            cash=Decimal("500000"),
            holdings={"600000.SH": Decimal("5000"), "000001.SZ": Decimal("3000")},
            cost_prices={"600000.SH": Decimal("100"), "000001.SZ": Decimal("50")},
        )
        orch, inputs_box = _make_systemic_orchestrator(
            broker=broker,
            kill_owner=validator,
            open_orders={"bk-open-9": {"symbol": "600000.SH"}},
        )
        inputs_box["data"] = dict(_LEVEL3_INPUTS)

        snap = orch.evaluate_intraday(1_000_000.0, now=_T0)

        # 三级警报：LEVEL_3 真实触发（3 信号）
        assert snap.systemic_level == 3
        assert snap.systemic_signal_count == 3
        assert snap.systemic_sentiment_breaker is False
        assert snap.systemic_cap == 0.0
        assert snap.systemic_halt is True
        # 快照合并：position_cap 取最严（0.0），allow_new_position=False
        assert snap.position_cap == 0.0
        assert snap.allow_new_position is False
        # 逃生指令真实产出（build_escape_directive 全字段）
        directive = snap.escape_directive
        assert directive is not None
        assert directive["directive"] == "escape"
        assert directive["action"] == "liquidate_all"
        assert directive["position_cap"] == 0.0
        assert directive["cancel_pending_orders"] is True
        assert directive["halt_new_orders"] is True
        assert directive["kill_switch_required"] is True
        assert len(directive["triggered_signals"]) == 3
        # Kill Switch 真实置位：状态层（DefaultRiskValidator 公共接口）
        assert validator.kill_switch_active is True
        assert orch.kill_switch_engaged is True
        assert orch.is_trading_allowed is False
        # 清算真实执行：2 持仓全平（MARKET SELL）+ 挂单全撤
        liquidated = {(o.symbol, o.side, o.quantity) for o in broker.submitted}
        assert liquidated == {
            ("600000.SH", OrderSide.SELL, Decimal("5000")),
            ("000001.SZ", OrderSide.SELL, Decimal("3000")),
        }
        assert all(o.order_type is OrderType.MARKET for o in broker.submitted)
        assert broker.cancelled == ["bk-open-9"]
        report = orch._kill_switch_report
        assert report is not None and report["report"]["all_success"] is True
        assert "系统性风险 LEVEL_3" in report["reason"]

    def test_repeated_level3_no_duplicate_liquidation(self) -> None:
        """LEVEL_3 持续（平级停留）：再次评估不重复清算（仲裁点幂等）。"""
        broker = FakeBroker(cash=Decimal("0"), holdings={"600000.SH": Decimal("1000")})
        orch, inputs_box = _make_systemic_orchestrator(broker=broker)
        inputs_box["data"] = dict(_LEVEL3_INPUTS)

        orch.evaluate_intraday(1_000_000.0, now=_T0)
        assert len(broker.submitted) == 1
        snap = orch.evaluate_intraday(1_000_000.0, now=_T0 + timedelta(seconds=30))
        assert snap.systemic_level == 3
        assert len(broker.submitted) == 1  # 清算仅一次
        assert snap.escape_directive is None  # 非迁移轮次不重复产指令

    def test_session_level_systemic_cap_scales_weights(self) -> None:
        """会话级集成：LEVEL_2（2 信号）→ position_cap 0.70 缩放目标权重。"""
        broker = FakeBroker(cash=Decimal("1000000"))
        orch, inputs_box = _make_systemic_orchestrator(broker=broker)
        assert orch.recover_from_broker().success is True
        # 2 信号：流动性危机 + 外围冲击 → LEVEL_2
        inputs_box["data"] = {
            "sell_pressure": 0.80,
            "bid_ask_spread": 0.01,
            "external_market_change": -0.04,
        }
        snap = orch.evaluate_intraday(1_000_000.0, now=_T0)
        assert snap.systemic_level == 2
        assert snap.systemic_cap == pytest.approx(0.70)
        assert snap.systemic_halt is False  # LEVEL_2 降仓不停开仓（§3.3）
        assert snap.position_cap == pytest.approx(0.70)
        assert snap.allow_new_position is True
        assert orch.kill_switch_engaged is False

        session = _make_session(
            broker=broker,
            risk_layer=orch,
            target_weights={"600000.SH": 0.8},
            prices={"600000.SH": Decimal("100")},
        )
        submitted = session.rebalance()
        # 0.8 × (0.7/0.8) = 0.7 → 1M × 0.7 / 100 = 7000 股
        assert len(submitted) == 1
        assert submitted[0].quantity == Decimal("7000")


class TestSystemicSentimentBreaker:
    """红队向量②：情绪断路器 0.85 强制升级 LEVEL_3（0 信号也熔断清算）。"""

    def test_sentiment_085_forces_level3_kill_chain(self) -> None:
        validator = DefaultRiskValidator()
        broker = FakeBroker(
            cash=Decimal("0"),
            holdings={"300750.SZ": Decimal("1000")},
            cost_prices={"300750.SZ": Decimal("200")},
        )
        orch, inputs_box = _make_systemic_orchestrator(broker=broker, kill_owner=validator)
        inputs_box["data"] = {"sentiment_index": 0.85}  # 0 信号 + 极度恐慌

        snap = orch.evaluate_intraday(1_000_000.0, now=_T0)

        assert snap.systemic_level == 3
        assert snap.systemic_signal_count == 0
        assert snap.systemic_sentiment_breaker is True
        assert snap.position_cap == 0.0
        assert snap.allow_new_position is False
        assert "情绪断路器" in (snap.escape_directive or {})["reason"]
        assert validator.kill_switch_active is True
        assert orch.is_trading_allowed is False
        # 清算真实执行
        assert [(o.symbol, o.side) for o in broker.submitted] == [("300750.SZ", OrderSide.SELL)]

    def test_sentiment_below_threshold_no_escalation(self) -> None:
        """情绪 0.84（阈值下）+ 0 信号 → 正常态，不熔断。"""
        broker = FakeBroker(cash=Decimal("1000000"))
        orch, inputs_box = _make_systemic_orchestrator(broker=broker)
        inputs_box["data"] = {"sentiment_index": 0.84}

        snap = orch.evaluate_intraday(1_000_000.0, now=_T0)
        assert snap.systemic_level == 0
        assert snap.systemic_sentiment_breaker is False
        assert snap.position_cap == 1.0
        assert snap.allow_new_position is True
        assert orch.kill_switch_engaged is False


class TestEscapeDirectiveGuard:
    """非 LEVEL_3 调用 build_escape_directive 抛错 + LEVEL_1/2 不触发熔断。"""

    def test_non_level3_escape_directive_raises(self) -> None:
        detector = AshareSystemicRiskDetector()
        alert_l1 = detector.check(sell_pressure=0.80, bid_ask_spread=0.01)  # 1 信号
        alert_l2 = detector.check(  # 2 信号
            sell_pressure=0.80,
            bid_ask_spread=0.01,
            external_market_change=-0.04,
        )
        with pytest.raises(InvalidSystemicRiskInputError):
            detector.build_escape_directive(alert_l1)
        with pytest.raises(InvalidSystemicRiskInputError):
            detector.build_escape_directive(alert_l2)

    def test_level1_halts_new_orders_without_kill_switch(self) -> None:
        """LEVEL_1（1 信号）→ 停开仓仅平仓：halt=True 但 cap=1.0，不熔断不清算。"""
        broker = FakeBroker(cash=Decimal("1000000"))
        orch, inputs_box = _make_systemic_orchestrator(broker=broker)
        inputs_box["data"] = {"sell_pressure": 0.80, "bid_ask_spread": 0.01}

        snap = orch.evaluate_intraday(1_000_000.0, now=_T0)
        assert snap.systemic_level == 1
        assert snap.systemic_halt is True
        assert snap.systemic_cap == 1.0  # 现有仓位不动（§3.3）
        assert snap.position_cap == 1.0
        assert snap.allow_new_position is False  # 停开仓
        assert snap.escape_directive is None
        assert orch.kill_switch_engaged is False
        assert broker.submitted == []


# ---------------------------------------------------------------------
# 红队实证⑥：降级机（37 号 §3.6 恢复条件矩阵 + 最短持续门控）
# ---------------------------------------------------------------------


class TestSystemicDegradationMachine:
    """红队向量③：LEVEL_3→LEVEL_2 冷却 30min+信号≤2+spread<0.3% 逐级降级。"""

    def test_cooldown_gates_and_full_ladder(self) -> None:
        """冷却门控 + 3→2→1→0 逐级 hysteresis 降级；熔断闩锁人工复位不变。"""
        broker = FakeBroker(cash=Decimal("0"), holdings={"600000.SH": Decimal("1000")})
        orch, inputs_box = _make_systemic_orchestrator(broker=broker)
        inputs_box["data"] = dict(_LEVEL3_INPUTS)
        orch.evaluate_intraday(1_000_000.0, now=_T0)
        assert orch.systemic_level == 3

        # T+29min：信号归零但冷却未满 → 不降级（防 thrashing）
        inputs_box["data"] = dict(_CALM_INPUTS)
        snap = orch.evaluate_intraday(1_000_000.0, now=_T0 + timedelta(minutes=29))
        assert snap.systemic_level == 3
        assert snap.systemic_cap == 0.0
        assert snap.systemic_halt is True

        # T+31min：冷却满 + 信号≤2 + spread<0.3% → 降级 LEVEL_2（允许重建仓 70%）
        snap = orch.evaluate_intraday(1_000_000.0, now=_T0 + timedelta(minutes=31))
        assert snap.systemic_level == 2
        assert snap.systemic_cap == pytest.approx(0.70)
        assert snap.systemic_halt is False  # §3.6 恢复执行动作：允许重建仓
        assert snap.position_cap == pytest.approx(0.70)
        # 35 号 KILL 态禁止 37 号恢复——熔断闩锁保持人工复位
        assert orch.kill_switch_engaged is True
        assert orch.is_trading_allowed is False

        # LEVEL_2 停留 14min（<15min 门控）→ 不降级
        snap = orch.evaluate_intraday(1_000_000.0, now=_T0 + timedelta(minutes=45))
        assert snap.systemic_level == 2
        # LEVEL_2 停留 16min + 信号≤1 → 降级 LEVEL_1（恢复满仓权限）
        snap = orch.evaluate_intraday(1_000_000.0, now=_T0 + timedelta(minutes=47))
        assert snap.systemic_level == 1
        assert snap.systemic_cap == 1.0
        assert snap.systemic_halt is False  # 恢复态 LEVEL_1 不停开仓（§3.6）

        # LEVEL_1 停留 11min + 信号 0 + 半阈值 → 恢复正常
        snap = orch.evaluate_intraday(1_000_000.0, now=_T0 + timedelta(minutes=58))
        assert snap.systemic_level == 0
        assert snap.systemic_cap == 1.0
        assert snap.systemic_halt is False

    def test_spread_gate_blocks_degradation(self) -> None:
        """冷却满但 spread 仍 ≥0.3% → 不降级（hysteresis 价差门控）。"""
        broker = FakeBroker(cash=Decimal("0"), holdings={"600000.SH": Decimal("1000")})
        orch, inputs_box = _make_systemic_orchestrator(broker=broker)
        inputs_box["data"] = dict(_LEVEL3_INPUTS)
        orch.evaluate_intraday(1_000_000.0, now=_T0)

        # T+35min：0 信号（卖压回落）但价差仍 0.4%（≥0.3% 恢复带）
        inputs_box["data"] = {"sell_pressure": 0.30, "bid_ask_spread": 0.004}
        snap = orch.evaluate_intraday(1_000_000.0, now=_T0 + timedelta(minutes=35))
        assert snap.systemic_level == 3

        # 价差回落至 0.2%（<0.3%）→ 降级 LEVEL_2
        inputs_box["data"] = {"sell_pressure": 0.30, "bid_ask_spread": 0.002}
        snap = orch.evaluate_intraday(1_000_000.0, now=_T0 + timedelta(minutes=36))
        assert snap.systemic_level == 2

    def test_persistent_signals_no_degradation(self) -> None:
        """冷却满但信号仍 ≥3（LEVEL_3 平级停留）→ 不降级。"""
        broker = FakeBroker(cash=Decimal("0"), holdings={"600000.SH": Decimal("1000")})
        orch, inputs_box = _make_systemic_orchestrator(broker=broker)
        inputs_box["data"] = dict(_LEVEL3_INPUTS)
        orch.evaluate_intraday(1_000_000.0, now=_T0)

        snap = orch.evaluate_intraday(1_000_000.0, now=_T0 + timedelta(minutes=40))
        assert snap.systemic_level == 3
        assert snap.systemic_cap == 0.0


class TestSystemicWiringRobustness:
    """接线健壮性：未接线零影响 / provider 失效降级 / 输入过滤。"""

    def test_unwired_orchestrator_behavior_unchanged(self) -> None:
        """未注入 systemic → 快照默认零约束（对 RWIRE 既有行为零回归）。"""
        broker = FakeBroker(cash=Decimal("1000000"))
        orch = _make_orchestrator(broker=broker)
        snap = orch.evaluate_intraday(1_000_000.0)
        assert snap.systemic_level == 0
        assert snap.systemic_cap == 1.0
        assert snap.systemic_halt is False
        assert snap.systemic_signal_count == 0
        assert snap.systemic_sentiment_breaker is False
        assert snap.escape_directive is None
        assert orch.systemic_level == 0

    def test_provider_failure_skips_round_without_blocking(self) -> None:
        """provider 抛异常 → 本轮跳过（状态保持），交易主循环不阻断。"""
        broker = FakeBroker(cash=Decimal("1000000"))
        orch = RiskLayerOrchestrator(
            drawdown_controller=DrawdownController(),
            drawdown_tracker=DrawdownTracker(initial_net_value=1_000_000.0),
            var_calculator=VaRCalculator(),
            tail_risk_monitor=TailRiskMonitor(),
            broker=broker,
            systemic_detector=AshareSystemicRiskDetector(),
            systemic_input_provider=MagicMock(side_effect=RuntimeError("data feed down")),
        )
        snap = orch.evaluate_intraday(1_000_000.0, now=_T0)
        assert snap.systemic_level == 0
        assert snap.position_cap == 1.0
        assert orch.kill_switch_engaged is False

    def test_invalid_input_value_skips_round(self) -> None:
        """输入越界（sell_pressure=1.5）→ detector 校验抛错被隔离，本轮跳过。"""
        broker = FakeBroker(cash=Decimal("1000000"))
        orch, inputs_box = _make_systemic_orchestrator(broker=broker)
        inputs_box["data"] = {"sell_pressure": 1.5, "bid_ask_spread": 0.01}
        snap = orch.evaluate_intraday(1_000_000.0, now=_T0)
        assert snap.systemic_level == 0
        assert orch.kill_switch_engaged is False

    def test_provider_now_key_filtered(self) -> None:
        """provider 误带 now 键 → 编排层过滤，不撞 detector.check(now=...) 签名。"""
        broker = FakeBroker(cash=Decimal("1000000"))
        orch, inputs_box = _make_systemic_orchestrator(broker=broker)
        inputs_box["data"] = {"sentiment_index": 0.5, "now": datetime(2020, 1, 1, tzinfo=UTC)}
        snap = orch.evaluate_intraday(1_000_000.0, now=_T0)
        assert snap.systemic_level == 0
        assert snap.timestamp == _T0

    def test_empty_inputs_skip_round(self) -> None:
        """provider 返回空/None → 本轮跳过（无输入不可评估，状态保持）。"""
        broker = FakeBroker(cash=Decimal("1000000"))
        orch, inputs_box = _make_systemic_orchestrator(broker=broker)
        inputs_box["data"] = {}
        snap = orch.evaluate_intraday(1_000_000.0, now=_T0)
        assert snap.systemic_level == 0

    def test_custom_systemic_config_accepted(self) -> None:
        """C 类参数可覆盖：自定义恢复比例/门控生效。"""
        broker = FakeBroker(cash=Decimal("0"), holdings={"600000.SH": Decimal("1000")})
        config = RiskLayerConfig(systemic_min_hold_minutes={1: 5, 2: 8, 3: 12})
        orch, inputs_box = _make_systemic_orchestrator(broker=broker, config=config)
        inputs_box["data"] = dict(_LEVEL3_INPUTS)
        orch.evaluate_intraday(1_000_000.0, now=_T0)
        inputs_box["data"] = dict(_CALM_INPUTS)
        # 自定义 12min 冷却：T+11min 不降级，T+13min 降级
        snap = orch.evaluate_intraday(1_000_000.0, now=_T0 + timedelta(minutes=11))
        assert snap.systemic_level == 3
        snap = orch.evaluate_intraday(1_000_000.0, now=_T0 + timedelta(minutes=13))
        assert snap.systemic_level == 2

    def test_data_outage_holds_crisis_constraints(self) -> None:
        """红队（AI-R2-001 修复实证）：LEVEL_2 危机中数据中断不放松仓位约束。

        原缺陷：provider 失效/空输入返回 None → 快照 systemic_cap 跳回 1.0，
        危机约束单轮消失。修复后无观测轮输出 state 派生 cap/halt（hysteresis
        语义：无数据=状态不变）。
        """
        broker = FakeBroker(cash=Decimal("1000000"))
        orch, inputs_box = _make_systemic_orchestrator(broker=broker)
        # 进入 LEVEL_2（2 信号）
        inputs_box["data"] = {
            "sell_pressure": 0.80,
            "bid_ask_spread": 0.01,
            "external_market_change": -0.04,
        }
        snap = orch.evaluate_intraday(1_000_000.0, now=_T0)
        assert snap.systemic_level == 2
        assert snap.systemic_cap == pytest.approx(0.70)
        # 数据中断轮（provider 抛异常）：level/cap/halt 全保持
        def _feed_down() -> dict:
            raise RuntimeError("feed down")

        orch._systemic_input_provider = _feed_down  # type: ignore[assignment]
        snap2 = orch.evaluate_intraday(1_000_000.0, now=_T0 + timedelta(minutes=1))
        assert snap2.systemic_level == 2
        assert snap2.systemic_cap == pytest.approx(0.70)
        assert snap2.position_cap == pytest.approx(0.70)
        # 空输入轮：同样保持
        orch._systemic_input_provider = lambda: {}  # type: ignore[assignment]
        snap3 = orch.evaluate_intraday(1_000_000.0, now=_T0 + timedelta(minutes=2))
        assert snap3.systemic_level == 2
        assert snap3.systemic_cap == pytest.approx(0.70)

    def test_recovery_gate_exception_isolated(self) -> None:
        """红队（AI-R2-001 修复实证）：降级门禁内部异常隔离，不崩主循环。

        原缺陷：_try_systemic_recovery 内异常（float() 类型错/min_hold_minutes
        缺级别键 KeyError 等）未捕获，传播崩 evaluate_intraday 调用方
        （违反自身"越界输入隔离跳过"契约）。
        构造：config.min_hold_minutes={1:10,3:30} 缺 level 2 → 降级候选轮
        gate 内 KeyError → 新 except 分支保持当前级别（AI-R2 复审修正：
        初审测试用 str spread 实被 detector.check 前置 except 拦截，
        未触达本修复分支）。
        """
        broker = FakeBroker(cash=Decimal("1000000"))
        config = RiskLayerConfig(systemic_min_hold_minutes={1: 10, 3: 30})  # 缺 level 2
        orch, inputs_box = _make_systemic_orchestrator(broker=broker, config=config)
        inputs_box["data"] = {
            "sell_pressure": 0.80,
            "bid_ask_spread": 0.01,
            "external_market_change": -0.04,
        }
        orch.evaluate_intraday(1_000_000.0, now=_T0)
        assert orch.systemic_level == 2
        # 降级候选轮（2 信号→1 信号）：gate KeyError 被隔离，级别保持，主循环不崩
        inputs_box["data"] = {"sell_pressure": 0.80, "bid_ask_spread": 0.01}
        snap = orch.evaluate_intraday(1_000_000.0, now=_T0 + timedelta(minutes=45))
        assert snap.systemic_level == 2  # 门禁失效保持当前级别
        assert orch.kill_switch_engaged is False

    def test_engage_skip_while_liquidation_inflight(self) -> None:
        """红队（AI-R2-001 修复实证）：engaged 置位后并发二次仲裁不穿透重复清算。

        构造：清算执行器抛异常（AI-R2-001 修复②后异常被隔离：熔断态保持、
        report 落地 liquidation_error 兜底字典），后续触发源仍被仲裁点跳过
        ——熔断态保持禁单，宁少清算不双清算。
        """
        import zephyr.ex_core.risk_layer_orchestrator as rlo

        broker = FakeBroker(cash=Decimal("0"), holdings={"600000.SH": Decimal("1000")})
        orch, inputs_box = _make_systemic_orchestrator(broker=broker)
        original = rlo.execute_kill_switch_liquidation

        def _boom(*args: object, **kwargs: object) -> object:
            raise RuntimeError("liquidation infra down")

        rlo.execute_kill_switch_liquidation = _boom  # type: ignore[assignment]
        try:
            inputs_box["data"] = dict(_LEVEL3_INPUTS)
            orch.evaluate_intraday(1_000_000.0, now=_T0)
            # 清算异常被隔离：engaged 已置位，report 落地 liquidation_error 兜底
            assert orch.kill_switch_engaged is True
            assert orch._kill_switch_report is not None
            assert orch._kill_switch_report["report"]["status"] == "liquidation_error"  # type: ignore[index]
            assert orch.is_trading_allowed is False
            # 二次触发（修复后：engaged 即跳过，不再穿透重入清算链）
            snap = orch.evaluate_intraday(1_000_000.0, now=_T0 + timedelta(seconds=30))
            assert orch.kill_switch_engaged is True
            assert len(broker.submitted) == 0  # 未重复下清算单
            assert snap.systemic_level == 3
        finally:
            rlo.execute_kill_switch_liquidation = original  # type: ignore[assignment]


class TestKillSwitchNanGuard:
    """红队攻击：NaN qty 穿透清算 + 清算异常隔离。"""

    def test_liquidation_filters_nan_qty(self) -> None:
        """broker 返回含 NaN qty 的持仓，清算字典应过滤该标的。"""
        broker = FakeBroker(
            cash=Decimal("0"),
            holdings={"A": Decimal("100"), "B": Decimal("nan"), "C": Decimal("0")},
        )
        orch = _make_orchestrator(broker=broker)

        result = orch._engage_kill_switch("redteam: nan qty penetration")

        assert result is not None
        # NaN("B") 与零持仓("C") 均被过滤——仅 "A" 真实清算
        # （修复前 NaN 穿透：nan>0 为 False → "B" 被生成 BUY 方向清算单）
        assert [(o.symbol, o.side) for o in broker.submitted] == [("A", OrderSide.SELL)]
        assert broker.submitted[0].quantity == Decimal(str(100.0))

    def test_liquidation_exception_keeps_engaged(self) -> None:
        """execute_kill_switch_liquidation 抛 ValueError，熔断状态保持，report 非 None。"""
        import zephyr.ex_core.risk_layer_orchestrator as rlo

        broker = FakeBroker(cash=Decimal("0"), holdings={"600000.SH": Decimal("1000")})
        orch = _make_orchestrator(broker=broker)
        original = rlo.execute_kill_switch_liquidation

        def _boom(*args: object, **kwargs: object) -> object:
            raise ValueError("liquidation params invalid")

        rlo.execute_kill_switch_liquidation = _boom  # type: ignore[assignment]
        try:
            result = orch._engage_kill_switch("redteam: liquidation exception")
        finally:
            rlo.execute_kill_switch_liquidation = original  # type: ignore[assignment]

        # 异常被隔离：熔断已置位（禁单保持），report 落地兜底字典而非永久 None
        assert orch.kill_switch_engaged is True
        assert orch.is_trading_allowed is False
        assert result is not None
        assert result["report"] == {
            "status": "liquidation_error",
            "reason": "execute_kill_switch_liquidation exception",
        }
        assert orch._kill_switch_report is result

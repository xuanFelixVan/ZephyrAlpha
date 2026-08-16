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
"""

from __future__ import annotations

import threading
from datetime import UTC, datetime
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

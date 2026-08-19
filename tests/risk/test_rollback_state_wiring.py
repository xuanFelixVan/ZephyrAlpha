# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md | §
# [MODULE] tests.risk.test_rollback_state_wiring
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TTL] task_bound
"""五态降级机执行链接线（#204，53 号 §3.8）+ 36 号 §3.10 校准动作接线测试。

实证目标（真实组件，仅 broker 外部边界替身）：
  1. #204：rollback_metrics_provider 注入即接线——evaluate_intraday 内嵌
     MOD-GOV-045 evaluate_rollback 单向更保守梯子（NORMAL→THROTTLED→SOFT_HALT
     →HARD_HALT）；SOFT_HALT 起 rollback_halt 禁新开仓（TradingSession 经既有
     allow_new_position 闸门滤买单）；UNWINDING（人工持久化姿态）→ 同一熔断
     仲裁点真实清算；迁移落盘 JsonStateStore；fail-closed 启动加载缺省
     SOFT_HALT；恢复仅人工 recover_rollback_posture（RCA+双人复核门禁）；
     provider 失效/非 Mapping 姿态保持不崩主循环
  2. 35 号 §3.10/§6.5 + 36 号 §3.10（同项）：apply_var_backtest_action 三档
     执行者——PASS 空转 / RECALIBRATE update_config 鸭子探针（未落地
     fail-visible 留痕，落地即调用）/ REBUILD 静态映射 VaR3%/CVaR5%
     （position_cap 0.5）+ UNAVAILABLE 持久化重启续存 + 业主确认恢复
"""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from zephyr.ex_core.order_manager import OrderManager
from zephyr.ex_core.risk_layer_orchestrator import RiskLayerOrchestrator
from zephyr.ex_core.trading_session import TradingSession, TradingSessionConfig
from zephyr.governance.lifecycle_governance.rollback_state_machine import (
    RollbackState,
    load_persisted_state,
    persist_state,
)
from zephyr.position.core.drawdown_controller import DrawdownController
from zephyr.risk.core.drawdown_tracker import DrawdownTracker
from zephyr.risk.core.tail_risk_monitor import TailRiskMonitor
from zephyr.risk.core.var_calculator import VaRCalculator
from zephyr.risk.implementations.default_risk_validator import DefaultRiskValidator
from zephyr.shared.contracts.enums.order_enums import OrderSide
from zephyr.shared.contracts.order import Order
from zephyr.shared.contracts.position import PositionSnapshot
from zephyr.shared.contracts.risk_limits import RiskLimits
from zephyr.shared.state_store import JsonStateStore
from zephyr.trading.trading_contracts.broker_interface import BrokerInterface

_T0 = datetime(2026, 8, 20, 10, 0, tzinfo=UTC)


class FakeBroker(BrokerInterface):
    """券商替身：持仓/现金可配，记录全部提交订单与撤单。"""

    def __init__(
        self,
        cash: Decimal = Decimal("1000000"),
        holdings: dict[str, Decimal] | None = None,
        cost_prices: dict[str, Decimal] | None = None,
    ) -> None:
        self._cash = cash
        self._holdings: dict[str, Decimal] = dict(holdings or {})
        self._costs: dict[str, Decimal] = dict(cost_prices or {})
        self.submitted: list[Order] = []
        self.cancelled: list[str] = []

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
        mv = {s: qty * self._costs.get(s, Decimal("0")) for s, qty in self._holdings.items() if qty != 0}
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

    def register_fill_callback(self, callback) -> None:
        pass


def _make_orchestrator(
    *,
    broker: FakeBroker,
    metrics_box: dict[str, Any] | None = None,
    store: JsonStateStore | None = None,
    kill_owner: DefaultRiskValidator | None = None,
) -> RiskLayerOrchestrator:
    """真实风控组件 + 可变五态机指标盒（metrics_box None=未接线）。"""
    return RiskLayerOrchestrator(
        drawdown_controller=DrawdownController(),
        drawdown_tracker=DrawdownTracker(initial_net_value=1_000_000.0),
        var_calculator=VaRCalculator(),
        tail_risk_monitor=TailRiskMonitor(),
        broker=broker,
        kill_switch_owner=kill_owner,
        rollback_metrics_provider=(
            (lambda: dict(metrics_box["data"])) if metrics_box is not None else None
        ),
        state_store=store,
    )


def _make_session(
    *,
    broker: FakeBroker,
    risk_layer: RiskLayerOrchestrator,
    target_weights: dict[str, float],
    prices: dict[str, Decimal],
) -> TradingSession:
    om = OrderManager()
    om.register_broker("fake", broker)
    strategy = MagicMock()
    strategy.generate_target_weights.return_value = dict(target_weights)
    config = TradingSessionConfig(
        universe=["600000.SH"],
        broker_id="fake",
        risk_limits=RiskLimits(
            as_of_date=datetime.now(UTC),
            idempotency_key="test-limits",
            max_single_position=1.0,
            max_gross_leverage=10.0,
        ),
    )
    config.max_single_order_pct = Decimal("1.0")
    return TradingSession(
        broker=broker,
        strategy=strategy,
        risk_validator=DefaultRiskValidator(),
        signal_provider=lambda _u: {},
        price_provider=lambda _u: dict(prices),
        order_manager=om,
        config=config,
        risk_layer=risk_layer,
    )


# ---------------------------------------------------------------------
# #204：五态降级机接 evaluate_intraday 评估循环
# ---------------------------------------------------------------------


class TestRollbackWiringTrigger:
    """降级触发链：单向更保守梯子逐级迁移 + 快照/闸门语义。"""

    def test_unwired_zero_regression(self) -> None:
        """未注入 provider → rollback_* 默认值不加约束（既有行为零回归）。"""
        broker = FakeBroker()
        orch = _make_orchestrator(broker=broker)
        snap = orch.evaluate_intraday(1_000_000.0, now=_T0)
        assert snap.rollback_state == "NORMAL"
        assert snap.rollback_halt is False
        assert snap.rollback_escalated is False
        assert snap.var_model_status == "DYNAMIC"
        assert snap.allow_new_position is True
        assert orch.rollback_posture is None
        assert orch.var_model_unavailable is False

    def test_throttled_escalation_informational(self) -> None:
        """intraday_dd>1% + 样本足 → THROTTLED（仅节流留痕，不拦新开仓不熔断）。"""
        broker = FakeBroker()
        box: dict[str, Any] = {"data": {"intraday_dd": 0.015, "trade_count": 100}}
        orch = _make_orchestrator(broker=broker, metrics_box=box)

        snap = orch.evaluate_intraday(1_000_000.0, now=_T0)
        assert snap.rollback_state == "THROTTLED"
        assert snap.rollback_escalated is True
        assert snap.rollback_halt is False  # THROTTLED 仅节流（执行层速率维度）
        assert snap.allow_new_position is True
        assert orch.rollback_posture is RollbackState.THROTTLED
        assert orch.kill_switch_engaged is False

        # 平级停留：同指标再评估不重复记迁移（防 thrashing 留痕语义）
        snap2 = orch.evaluate_intraday(1_000_000.0, now=_T0)
        assert snap2.rollback_state == "THROTTLED"
        assert snap2.rollback_escalated is False

    def test_soft_halt_blocks_new_positions_and_persists(self, tmp_path: Path) -> None:
        """THROTTLED→SOFT_HALT（dd>2%）→ 禁新开仓（REDUCING 只卖不买）+ 落盘。"""
        store = JsonStateStore(tmp_path / "state")
        persist_state(store, RollbackState.NORMAL, reason="部署初始化")  # 越过 fail-closed 缺省
        broker = FakeBroker()
        box: dict[str, Any] = {"data": {"intraday_dd": 0.015, "trade_count": 100}}
        orch = _make_orchestrator(broker=broker, metrics_box=box, store=store)
        orch.evaluate_intraday(1_000_000.0, now=_T0)
        assert load_persisted_state(store) is RollbackState.THROTTLED

        box["data"] = {"intraday_dd": 0.025, "trade_count": 100}  # dd>2% hard breach
        snap = orch.evaluate_intraday(1_000_000.0, now=_T0)
        assert snap.rollback_state == "SOFT_HALT"
        assert snap.rollback_escalated is True
        assert snap.rollback_halt is True
        assert snap.allow_new_position is False  # 禁新开仓，既有 SELL 不受影响
        assert snap.position_cap == 1.0  # REDUCING 不动仓位上限（只拦新开）
        assert orch.kill_switch_engaged is False  # SOFT_HALT 非 Flatten，不清算
        assert broker.submitted == []
        assert load_persisted_state(store) is RollbackState.SOFT_HALT  # 重启续存

    def test_full_ladder_to_hard_halt_without_liquidation(self) -> None:
        """SOFT_HALT→HARD_HALT（daily_loss≥3%）→ 完全静默但持仓保留（不清算）。"""
        broker = FakeBroker(holdings={"600000.SH": Decimal("1000")})
        box: dict[str, Any] = {"data": {"intraday_dd": 0.015, "trade_count": 100}}
        orch = _make_orchestrator(broker=broker, metrics_box=box)
        orch.evaluate_intraday(1_000_000.0, now=_T0)  # →THROTTLED
        box["data"] = {"intraday_dd": 0.025, "trade_count": 100}
        orch.evaluate_intraday(1_000_000.0, now=_T0)  # →SOFT_HALT

        box["data"] = {"daily_loss": 0.031, "trade_count": 100}  # ≥3% 硬限额
        snap = orch.evaluate_intraday(1_000_000.0, now=_T0)
        assert snap.rollback_state == "HARD_HALT"
        assert snap.rollback_halt is True
        assert snap.allow_new_position is False
        # HARD_HALT=完全静默+持仓保留等人工评估——非 UNWINDING，不触发清算
        assert orch.kill_switch_engaged is False
        assert broker.submitted == []

        # HARD_HALT 无自动出口（UNWINDING 须人工+双人复核，不在自动迁移矩阵）
        box["data"] = {"daily_loss": 0.05, "circuit_breaker": True, "trade_count": 100}
        snap2 = orch.evaluate_intraday(1_000_000.0, now=_T0)
        assert snap2.rollback_state == "HARD_HALT"
        assert snap2.rollback_escalated is False

    def test_unwinding_posture_engages_kill_switch(self, tmp_path: Path) -> None:
        """人工持久化 UNWINDING（4 级 Flatten）→ 首轮评估即同一仲裁点真实清算。"""
        store = JsonStateStore(tmp_path / "state")
        persist_state(store, RollbackState.UNWINDING, reason="人工+双人复核 Flatten", trade_count=42)
        validator = DefaultRiskValidator()
        broker = FakeBroker(
            cash=Decimal("0"),
            holdings={"600000.SH": Decimal("5000"), "000001.SZ": Decimal("3000")},
            cost_prices={"600000.SH": Decimal("100"), "000001.SZ": Decimal("50")},
        )
        box: dict[str, Any] = {"data": {"trade_count": 100}}
        orch = _make_orchestrator(broker=broker, metrics_box=box, store=store, kill_owner=validator)
        assert orch.rollback_posture is RollbackState.UNWINDING  # 启动加载续存

        snap = orch.evaluate_intraday(1_000_000.0, now=_T0)
        assert snap.rollback_state == "UNWINDING"
        assert snap.rollback_halt is True
        assert orch.kill_switch_engaged is True
        assert validator.kill_switch_active is True
        liquidated = {(o.symbol, o.side, o.quantity) for o in broker.submitted}
        assert liquidated == {
            ("600000.SH", OrderSide.SELL, Decimal("5000")),
            ("000001.SZ", OrderSide.SELL, Decimal("3000")),
        }

    def test_metrics_fallback_from_drawdown_tracker(self) -> None:
        """provider 未给 intraday_dd → 编排层以回撤追踪器口径兜底（真实净值回撤）。"""
        broker = FakeBroker()
        box: dict[str, Any] = {"data": {"trade_count": 100}}  # 仅样本量
        orch = _make_orchestrator(broker=broker, metrics_box=box)
        orch.evaluate_intraday(1_000_000.0, now=_T0)  # 峰值锚定
        snap = orch.evaluate_intraday(985_000.0, now=_T0)  # -1.5%（<5% 不触回撤链告警）
        assert snap.drawdown_level.value == "NONE"  # 回撤告警链未动
        assert snap.rollback_state == "THROTTLED"  # 五态机经兜底口径触发
        assert snap.rollback_escalated is True

    def test_session_blocks_buys_under_soft_halt(self) -> None:
        """会话级集成：SOFT_HALT → allow_new_position=False → rebalance 滤除买单。"""
        broker = FakeBroker()
        box: dict[str, Any] = {"data": {"trade_count": 100}}
        orch = _make_orchestrator(broker=broker, metrics_box=box)
        session = _make_session(
            broker=broker,
            risk_layer=orch,
            target_weights={"600000.SH": 0.1},
            prices={"600000.SH": Decimal("100")},
        )
        session.start()
        try:
            assert len(session.rebalance()) == 1  # NORMAL 态正常下单
            broker.submitted.clear()
            # 盘中恶化：dd 1.5% → THROTTLED（仍放行）→ 2.5% → SOFT_HALT（拦买单）
            box["data"] = {"intraday_dd": 0.015, "trade_count": 100}
            assert len(session.rebalance()) == 1
            broker.submitted.clear()
            box["data"] = {"intraday_dd": 0.025, "trade_count": 100}
            assert session.rebalance() == []  # REDUCING 态买单整批滤除
            assert all(o.side is not OrderSide.BUY for o in broker.submitted)
        finally:
            session.stop()


class TestRollbackWiringRecoveryAndFailClosed:
    """恢复/异常路径：样本地板、P0 绕过、fail-closed 加载、人工恢复门禁。"""

    def test_sample_floor_blocks_auto_degrade(self) -> None:
        """累计 <30 笔 → 样本地板拦截自动降级（小样本噪声不触发）。"""
        broker = FakeBroker()
        box: dict[str, Any] = {"data": {"intraday_dd": 0.05, "trade_count": 10}}
        orch = _make_orchestrator(broker=broker, metrics_box=box)
        snap = orch.evaluate_intraday(1_000_000.0, now=_T0)
        assert snap.rollback_state == "NORMAL"
        assert snap.rollback_escalated is False

    def test_p0_event_bypasses_sample_floor(self) -> None:
        """P0 事件绕过样本地板（0 笔交易也可降级）。"""
        broker = FakeBroker()
        box: dict[str, Any] = {"data": {"intraday_dd": 0.015, "trade_count": 0, "p0_event": True}}
        orch = _make_orchestrator(broker=broker, metrics_box=box)
        snap = orch.evaluate_intraday(1_000_000.0, now=_T0)
        assert snap.rollback_state == "THROTTLED"
        assert snap.rollback_escalated is True

    def test_fail_closed_fresh_store_loads_soft_halt(self, tmp_path: Path) -> None:
        """接线+空 store → 启动加载 fail-closed SOFT_HALT（停错代价<放错代价）。"""
        store = JsonStateStore(tmp_path / "state")  # 无任何记录
        broker = FakeBroker()
        box: dict[str, Any] = {"data": {"trade_count": 100}}
        orch = _make_orchestrator(broker=broker, metrics_box=box, store=store)
        assert orch.rollback_posture is RollbackState.SOFT_HALT
        snap = orch.evaluate_intraday(1_000_000.0, now=_T0)
        assert snap.rollback_state == "SOFT_HALT"
        assert snap.rollback_halt is True
        assert snap.allow_new_position is False
        assert orch.kill_switch_engaged is False  # SOFT_HALT 不清算

    def test_manual_recovery_requires_rca_and_dual_approval(self, tmp_path: Path) -> None:
        """恢复唯一入口=人工 RCA+双人复核；方向/权限守卫模块契约原样透传。"""
        store = JsonStateStore(tmp_path / "state")
        persist_state(store, RollbackState.NORMAL, reason="部署初始化")  # 越过 fail-closed 缺省
        broker = FakeBroker()
        box: dict[str, Any] = {"data": {"intraday_dd": 0.015, "trade_count": 100}}
        orch = _make_orchestrator(broker=broker, metrics_box=box, store=store)
        orch.evaluate_intraday(1_000_000.0, now=_T0)
        assert orch.rollback_posture is RollbackState.THROTTLED

        with pytest.raises(PermissionError):
            orch.recover_rollback_posture(
                RollbackState.NORMAL, rca_written=False, dual_approval=True, position_flat=True
            )
        with pytest.raises(PermissionError):
            orch.recover_rollback_posture(
                RollbackState.NORMAL, rca_written=True, dual_approval=False, position_flat=True
            )
        with pytest.raises(ValueError):
            orch.recover_rollback_posture(  # 目标非更宽松态
                RollbackState.HARD_HALT, rca_written=True, dual_approval=True, position_flat=True
            )
        assert orch.rollback_posture is RollbackState.THROTTLED  # 守卫拒绝后姿态不变

        recovered = orch.recover_rollback_posture(
            RollbackState.NORMAL, rca_written=True, dual_approval=True, position_flat=True
        )
        assert recovered is RollbackState.NORMAL
        assert load_persisted_state(store) is RollbackState.NORMAL  # 恢复落盘覆盖底档
        snap = orch.evaluate_intraday(1_000_000.0, now=_T0)
        assert snap.rollback_halt is False
        assert snap.allow_new_position is True

    def test_provider_failure_holds_posture(self) -> None:
        """provider 异常/非 Mapping/None → 姿态保持不崩主循环（hysteresis 无数据）。"""
        broker = FakeBroker()
        box: dict[str, Any] = {"data": {"intraday_dd": 0.015, "trade_count": 100}}
        orch = _make_orchestrator(broker=broker, metrics_box=box)
        orch.evaluate_intraday(1_000_000.0, now=_T0)
        assert orch.rollback_posture is RollbackState.THROTTLED

        def _feed_down() -> dict:
            raise RuntimeError("metrics feed down")

        orch._rollback_metrics_provider = _feed_down  # type: ignore[assignment]
        snap = orch.evaluate_intraday(1_000_000.0, now=_T0)
        assert snap.rollback_state == "THROTTLED"  # 姿态保持
        assert snap.rollback_escalated is False

        orch._rollback_metrics_provider = lambda: ["not", "mapping"]  # type: ignore[assignment]
        assert orch.evaluate_intraday(1_000_000.0, now=_T0).rollback_state == "THROTTLED"
        orch._rollback_metrics_provider = lambda: None  # type: ignore[assignment]
        assert orch.evaluate_intraday(1_000_000.0, now=_T0).rollback_state == "THROTTLED"
        assert orch.kill_switch_engaged is False

    def test_escalation_persisted_across_restart(self, tmp_path: Path) -> None:
        """降级姿态落盘 → 新编排器实例（模拟重启）启动加载续存 SOFT_HALT。"""
        store = JsonStateStore(tmp_path / "state")
        persist_state(store, RollbackState.NORMAL, reason="部署初始化")  # 越过 fail-closed 缺省
        broker = FakeBroker()
        box: dict[str, Any] = {"data": {"intraday_dd": 0.015, "trade_count": 100}}
        orch1 = _make_orchestrator(broker=broker, metrics_box=box, store=store)
        orch1.evaluate_intraday(1_000_000.0, now=_T0)
        box["data"] = {"intraday_dd": 0.025, "trade_count": 100}
        orch1.evaluate_intraday(1_000_000.0, now=_T0)
        assert orch1.rollback_posture is RollbackState.SOFT_HALT

        orch2 = _make_orchestrator(broker=broker, metrics_box=box, store=store)
        assert orch2.rollback_posture is RollbackState.SOFT_HALT  # 重启后续存
        snap = orch2.evaluate_intraday(1_000_000.0, now=_T0)
        assert snap.rollback_halt is True


# ---------------------------------------------------------------------
# 35 号 §3.10/§6.5 + 36 号 §3.10（同项）：校准动作执行者接入编排层
# ---------------------------------------------------------------------


def _seed_oscillating_nav(orch: RiskLayerOrchestrator, up: float, rounds: int = 31) -> None:
    """注入交替涨跌净值序列（构造足量收益样本使动态 VaR 参与评估）。"""
    for i in range(rounds):
        orch.evaluate_intraday(1_000_000.0 * (up if i % 2 else 1.0), now=_T0)


class TestVarBacktestCalibrationActions:
    """三档响应：PASS 空转 / RECALIBRATE 探针 / REBUILD 静态映射 + 恢复门禁。"""

    def test_pass_action_noop(self) -> None:
        broker = FakeBroker()
        orch = _make_orchestrator(broker=broker)
        report = orch.apply_var_backtest_action("PASS", reason="basel green")
        assert report["action"] == "PASS"
        assert report["applied"] == []
        assert report["skipped"] == []
        assert report["var_model_unavailable"] is False
        snap = orch.evaluate_intraday(1_000_000.0, now=_T0)
        assert snap.var_model_status == "DYNAMIC"

    def test_unknown_action_raises(self) -> None:
        orch = _make_orchestrator(broker=FakeBroker())
        with pytest.raises(ValueError, match="未知校准动作"):
            orch.apply_var_backtest_action("DANCE")

    def test_recalibrate_method_missing_fail_visible(self) -> None:
        """组件 update_config 未落地（36 号设计契约现状）→ skipped 留痕不静默。"""
        orch = _make_orchestrator(broker=FakeBroker())
        report = orch.apply_var_backtest_action(
            "RECALIBRATE",
            reason="kupiec reject",
            recalibrate_params={"var_calculator": {"min_history": 60, "window": 120}},
        )
        assert report["action"] == "RECALIBRATE"
        assert report["applied"] == []
        assert report["skipped"] == [
            {"target": "var_calculator", "reason": "update_config 未落地（36 号 §3.10 设计契约）"}
        ]

    def test_recalibrate_probe_invoked_when_method_landed(self) -> None:
        """组件落地 update_config 后接线即亮（鸭子探针真实调用+参数透传）。"""
        orch = _make_orchestrator(broker=FakeBroker())
        calls: list[dict] = []
        orch._var_calc.update_config = lambda **kw: calls.append(kw)  # type: ignore[attr-defined]
        report = orch.apply_var_backtest_action(
            "RECALIBRATE",
            reason="christoffersen reject",
            recalibrate_params={"var_calculator": {"method": "historical"}},
        )
        assert calls == [{"method": "historical"}]
        assert report["applied"] == ["var_calculator.update_config({'method': 'historical'})"]
        assert report["skipped"] == []

    def test_rebuild_forces_static_mapping(self, tmp_path: Path) -> None:
        """REBUILD → 静态 VaR3%/CVaR5% 喂 controller → cap 0.5（动态计算旁路）。"""
        store = JsonStateStore(tmp_path / "state")
        broker = FakeBroker()
        orch = _make_orchestrator(broker=broker, store=store)
        _seed_oscillating_nav(orch, up=1.05)  # 动态口径下 VaR ~8%（RED 级）
        dynamic_snap = orch.evaluate_intraday(1_000_000.0, now=_T0)
        assert dynamic_snap.response is not None
        assert dynamic_snap.response.risk_level.value == "RED"  # 动态路径实证在跑

        report = orch.apply_var_backtest_action("REBUILD", reason="basel red + overall_reject")
        assert report["action"] == "REBUILD"
        assert report["var_model_unavailable"] is True
        assert any("UNAVAILABLE" in a for a in report["applied"])
        assert store.load("var_model_status")["status"] == "UNAVAILABLE"  # 持久化

        snap = orch.evaluate_intraday(1_000_000.0, now=_T0)
        assert snap.var_model_status == "STATIC_REBUILD"
        assert snap.var_pct == pytest.approx(0.03)  # 静态口径（动态 8% 已旁路）
        assert snap.es_pct == pytest.approx(0.05)
        assert snap.degraded is False  # 静态映射是设计口径，非降级
        assert snap.response is not None
        assert snap.position_cap == pytest.approx(0.5)  # 36 号：静态 position_cap 固定 0.5
        assert snap.tail_alert is None  # 尾部监控同步旁路

    def test_rebuild_persisted_across_restart(self, tmp_path: Path) -> None:
        """UNAVAILABLE 标记重启续存：新实例启动即静态映射（盘前初始化读取）。"""
        store = JsonStateStore(tmp_path / "state")
        broker = FakeBroker()
        orch1 = _make_orchestrator(broker=broker, store=store)
        orch1.apply_var_backtest_action("REBUILD", reason="ebt black")

        orch2 = _make_orchestrator(broker=broker, store=store)
        assert orch2.var_model_unavailable is True
        _seed_oscillating_nav(orch2, up=1.05)
        snap = orch2.evaluate_intraday(1_000_000.0, now=_T0)
        assert snap.var_model_status == "STATIC_REBUILD"
        assert snap.position_cap == pytest.approx(0.5)

    def test_clear_requires_owner_confirmation(self, tmp_path: Path) -> None:
        """恢复门禁：未确认 PermissionError；确认后恢复动态计算 + 落盘 DYNAMIC。"""
        store = JsonStateStore(tmp_path / "state")
        broker = FakeBroker()
        orch = _make_orchestrator(broker=broker, store=store)
        orch.apply_var_backtest_action("REBUILD", reason="basel red")
        assert orch.var_model_unavailable is True

        with pytest.raises(PermissionError):
            orch.clear_var_model_unavailable(owner_confirmed=False)
        assert orch.var_model_unavailable is True  # 拒绝后保持静态

        orch.clear_var_model_unavailable(owner_confirmed=True)
        assert orch.var_model_unavailable is False
        assert store.load("var_model_status")["status"] == "DYNAMIC"
        _seed_oscillating_nav(orch, up=1.05)
        snap = orch.evaluate_intraday(1_000_000.0, now=_T0)
        assert snap.var_model_status == "DYNAMIC"
        assert snap.response is not None
        assert snap.response.risk_level.value == "RED"  # 动态路径恢复

    def test_corrupt_var_status_fail_closed_static(self, tmp_path: Path) -> None:
        """状态记录损坏 → fail-closed 按 UNAVAILABLE 静态映射运行（停错<放错）。"""
        store = JsonStateStore(tmp_path / "state")
        path = store.save("var_model_status", {"status": "DYNAMIC"})
        path.write_bytes(b"{corrupted-json")

        orch = _make_orchestrator(broker=FakeBroker(), store=store)
        assert orch.var_model_unavailable is True
        snap = orch.evaluate_intraday(1_000_000.0, now=_T0)
        assert snap.var_model_status == "STATIC_REBUILD"

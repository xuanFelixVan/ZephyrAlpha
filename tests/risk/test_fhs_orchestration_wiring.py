# [BLUEPRINT] MOD-FEEDBACK_LOOP | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [MODULE] tests.risk.test_fhs_orchestration_wiring
# [DOMAIN] D_RISK
# [TESTS] zephyr.ex_core.risk_layer_orchestrator(FHS 编排/var_breach 注入)
# [COVERAGE] 36号 §3.16 三触发/冷却期/同日去重/3次永久禁用/次日裁决/evaluate_intraday FHS产出链与回退/持久化续存 + §3.15 var_breach_machine 注入折扣
# [MATURITY] evolving
# [TTL] task_bound

"""FHS 编排层接线 + var_breach_machine 注入测试 (36号 §3.16 tracker #147 + §3.15)。

实证目标（真实组件，仅 broker 外部边界替身）:
    1. should_switch_to_fhs 三触发 (Christoffersen 独立性失败含 kupiec 守卫/
       ebt_red_streak≥2/intraday_significant_streak≥3) + 未注入/已启用/永久禁用 → False
    2. 冷却期: 失败后 10 日内禁止 (log_fhs_cooldown_active), 满 10 日解禁
    3. 失败计数: 同日去重, 累计 3 次 → FHS_PERMANENTLY_DISABLED
    4. try_activate_fhs → evaluate_intraday FHS 产出链 (snapshot.fhs_active=True,
       var/es 来自 FHS); GARCH 不收敛/失效 → 自动回退既有链 + 记失败
    5. note_fhs_backtest_verdict: PASS 保留 / RECALIBRATE 切回记失败 / 未启用不适用
    6. 切换状态 state_store 持久化续存; 损坏 fail-closed 永久禁用
    7. var_breach_machine 注入: BREACHED ×0.8 折扣进 evaluate_intraday 响应
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import numpy as np
import pytest

from zephyr.ex_core.risk_layer_orchestrator import (
    FHS_COOLDOWN_DAYS,
    FHS_MAX_FAILURES_BEFORE_DISABLE,
    RiskLayerOrchestrator,
)
from zephyr.position.core.drawdown_controller import (
    DrawdownController,
    DrawdownInfo,
    VarCvarMetrics,
)
from zephyr.risk.core.drawdown_tracker import DrawdownTracker
from zephyr.risk.core.fhs_engine import FHSEngine, FHSConfig
from zephyr.risk.core.tail_risk_monitor import TailRiskMonitor
from zephyr.risk.core.var_breach_state_machine import VarBreachStateMachine
from zephyr.risk.core.var_calculator import VaRCalculator
from zephyr.shared.contracts.position import PositionSnapshot
from zephyr.shared.state_store import JsonStateStore
from zephyr.trading.trading_contracts.broker_interface import BrokerInterface

T0 = datetime(2026, 8, 20, 10, 0, tzinfo=UTC)
D0 = T0.date()


class FakeBroker(BrokerInterface):
    """券商替身: 空仓 + 固定现金 (evaluate_intraday 不触清算即够用)。"""

    @property
    def broker_id(self) -> str:
        return "fake"

    def connect(self) -> bool:
        return True

    def disconnect(self) -> None:
        pass

    def submit_order(self, order) -> str:
        return "bk-x"

    def cancel_order(self, broker_order_id: str) -> bool:
        return True

    def query_order(self, broker_order_id: str):
        return None

    def get_positions(self) -> PositionSnapshot:
        return PositionSnapshot(
            as_of_timestamp=datetime.now(UTC),
            portfolio_id="fake",
            idempotency_key="fake",
            cash=Decimal("1000000"),
            gross_leverage=0.0,
            holdings={},
            market_values={},
            total_market_value=Decimal("0"),
        )

    def register_fill_callback(self, callback) -> None:
        pass


def _fhs_engine() -> FHSEngine:
    """小样本门槛 + 小模拟数 (测试速度) + 固定种子 (可复现)。"""
    return FHSEngine(FHSConfig(min_history=30, garch_min_history=30, n_simulations=500, random_seed=42))


def _make_orchestrator(
    *,
    store: JsonStateStore | None = None,
    fhs_engine: FHSEngine | None = None,
    var_breach_machine: VarBreachStateMachine | None = None,
) -> RiskLayerOrchestrator:
    return RiskLayerOrchestrator(
        drawdown_controller=DrawdownController(),
        drawdown_tracker=DrawdownTracker(initial_net_value=1_000_000.0),
        var_calculator=VaRCalculator(),
        tail_risk_monitor=TailRiskMonitor(),
        broker=FakeBroker(),
        fhs_engine=fhs_engine,
        var_breach_machine=var_breach_machine,
        state_store=store,
        clock=lambda: T0,
    )


def _feed_nav(orch: RiskLayerOrchestrator, sigma: float = 0.01, n: int = 65, seed: int = 7) -> None:
    """喂 n 个 nav 点构造收益序列 (≥min_samples_for_var=30)。"""
    rng = np.random.default_rng(seed)
    nav = 1_000_000.0
    for i in range(n):
        nav *= 1.0 + float(rng.normal(0.0, sigma))
        orch.evaluate_intraday(nav, now=T0 + timedelta(minutes=i))


# ── should_switch_to_fhs 三触发 ───────────────────────────────────────────────


class TestShouldSwitch:
    def test_no_engine_false(self) -> None:
        orch = _make_orchestrator()
        assert orch.should_switch_to_fhs(ebt_red_streak=5, today=D0) is False

    def test_no_trigger_false(self) -> None:
        orch = _make_orchestrator(fhs_engine=_fhs_engine())
        assert orch.should_switch_to_fhs(today=D0) is False

    def test_trigger1_independence_failure(self) -> None:
        orch = _make_orchestrator(fhs_engine=_fhs_engine())
        assert orch.should_switch_to_fhs(christoffersen_lr_ind_p=0.01, kupiec_p=0.5, today=D0) is True

    def test_trigger1_guard_kupiec_also_rejects(self) -> None:
        """kupiec 同 reject (覆盖率亦失败) → 非独立性失败单发, 触发 1 不成立。"""
        orch = _make_orchestrator(fhs_engine=_fhs_engine())
        assert orch.should_switch_to_fhs(christoffersen_lr_ind_p=0.01, kupiec_p=0.01, today=D0) is False

    def test_trigger2_ebt_red_streak(self) -> None:
        orch = _make_orchestrator(fhs_engine=_fhs_engine())
        assert orch.should_switch_to_fhs(ebt_red_streak=1, today=D0) is False
        assert orch.should_switch_to_fhs(ebt_red_streak=2, today=D0) is True

    def test_trigger3_intraday_significant_streak(self) -> None:
        orch = _make_orchestrator(fhs_engine=_fhs_engine())
        assert orch.should_switch_to_fhs(intraday_significant_streak=2, today=D0) is False
        assert orch.should_switch_to_fhs(intraday_significant_streak=3, today=D0) is True

    def test_already_active_false(self) -> None:
        orch = _make_orchestrator(fhs_engine=_fhs_engine())
        orch.try_activate_fhs(reason="t1")
        assert orch.should_switch_to_fhs(ebt_red_streak=5, today=D0) is False


# ── try_activate + evaluate_intraday FHS 产出链 ───────────────────────────────


class TestActivateAndProduction:
    def test_activate_without_engine(self) -> None:
        orch = _make_orchestrator()
        assert orch.try_activate_fhs(reason="t")["activated"] is False

    def test_activate_then_fhs_produces_var(self) -> None:
        """启用后 evaluate_intraday 由 FHS 产出 var/es, snapshot.fhs_active=True。"""
        orch = _make_orchestrator(fhs_engine=_fhs_engine())
        assert orch.try_activate_fhs(reason="t")["activated"] is True
        assert orch.fhs_active is True
        _feed_nav(orch)
        snap = orch.latest_snapshot
        assert snap is not None
        assert snap.fhs_active is True
        assert snap.var_pct is not None and snap.var_pct > 0
        assert snap.es_pct is not None and snap.es_pct >= snap.var_pct
        assert orch.fhs_status["failure_count"] == 0  # GARCH 收敛, 无失败记录

    def test_unwired_zero_regression(self) -> None:
        """未注入引擎: snapshot.fhs_active=False, 既有 var 链不变。"""
        orch = _make_orchestrator()
        _feed_nav(orch)
        snap = orch.latest_snapshot
        assert snap is not None
        assert snap.fhs_active is False
        assert snap.var_pct is not None and snap.var_pct > 0

    def test_garch_not_converged_falls_back_and_records_failure(self) -> None:
        """GARCH 不收敛 (零方差收益) → 自动回退既有链 + 记切换失败 (同日去重)。"""
        orch = _make_orchestrator(fhs_engine=_fhs_engine())
        orch.try_activate_fhs(reason="t")
        nav = 1_000_000.0
        for i in range(65):  # 恒定 nav → 零收益 → GARCH 不可拟合
            snap = orch.evaluate_intraday(nav, now=T0 + timedelta(minutes=i))
        assert orch.fhs_active is False  # 已停用
        assert orch.fhs_status["failure_count"] == 1
        assert orch.fhs_status["last_failure_date"] == D0.isoformat()
        # 后续轮次回退既有链 (fhs_active=False)
        assert snap.fhs_active is False

    def test_same_day_failures_deduped(self) -> None:
        orch = _make_orchestrator(fhs_engine=_fhs_engine())
        orch._record_fhs_failure("r1", D0)
        orch._record_fhs_failure("r2", D0)
        assert orch.fhs_status["failure_count"] == 1

    def test_three_failures_permanently_disabled(self) -> None:
        orch = _make_orchestrator(fhs_engine=_fhs_engine())
        for i in range(FHS_MAX_FAILURES_BEFORE_DISABLE):
            orch._record_fhs_failure(f"r{i}", D0 + timedelta(days=20 + i))
        status = orch.fhs_status
        assert status["permanently_disabled"] is True
        assert orch.try_activate_fhs(reason="t")["activated"] is False
        assert orch.should_switch_to_fhs(ebt_red_streak=5, today=D0 + timedelta(days=40)) is False


# ── 冷却期 ────────────────────────────────────────────────────────────────────


class TestCooldown:
    def test_cooldown_blocks_within_10_days(self) -> None:
        orch = _make_orchestrator(fhs_engine=_fhs_engine())
        orch._record_fhs_failure("r", D0)
        assert orch.should_switch_to_fhs(ebt_red_streak=5, today=D0 + timedelta(days=1)) is False
        assert orch.should_switch_to_fhs(ebt_red_streak=5, today=D0 + timedelta(days=FHS_COOLDOWN_DAYS - 1)) is False

    def test_cooldown_expires_after_10_days(self) -> None:
        orch = _make_orchestrator(fhs_engine=_fhs_engine())
        orch._record_fhs_failure("r", D0)
        assert orch.should_switch_to_fhs(ebt_red_streak=5, today=D0 + timedelta(days=FHS_COOLDOWN_DAYS)) is True

    def test_cooldown_log(self, caplog) -> None:
        import logging

        orch = _make_orchestrator(fhs_engine=_fhs_engine())
        orch._record_fhs_failure("r", D0)
        with caplog.at_level(logging.INFO):
            orch.should_switch_to_fhs(ebt_red_streak=5, today=D0 + timedelta(days=1))
        assert "log_fhs_cooldown_active" in caplog.text


# ── 次日回测裁决 ──────────────────────────────────────────────────────────────


class TestBacktestVerdict:
    def test_pass_keeps_active(self) -> None:
        orch = _make_orchestrator(fhs_engine=_fhs_engine())
        orch.try_activate_fhs(reason="t")
        out = orch.note_fhs_backtest_verdict("PASS", today=D0 + timedelta(days=1))
        assert out["fhs_active"] is True
        assert orch.fhs_active is True
        assert orch.fhs_status["failure_count"] == 0

    def test_recalibrate_deactivates_and_records(self) -> None:
        orch = _make_orchestrator(fhs_engine=_fhs_engine())
        orch.try_activate_fhs(reason="t")
        out = orch.note_fhs_backtest_verdict("RECALIBRATE", today=D0 + timedelta(days=1))
        assert out["fhs_active"] is False
        assert orch.fhs_active is False
        assert orch.fhs_status["failure_count"] == 1

    def test_not_active_not_applicable(self) -> None:
        orch = _make_orchestrator(fhs_engine=_fhs_engine())
        out = orch.note_fhs_backtest_verdict("REBUILD", today=D0)
        assert "不适用" in out["reason"]
        assert orch.fhs_status["failure_count"] == 0


# ── 持久化续存 ────────────────────────────────────────────────────────────────


class TestPersistence:
    def test_active_state_restored_after_restart(self, tmp_path: Path) -> None:
        store = JsonStateStore(tmp_path)
        orch = _make_orchestrator(store=store, fhs_engine=_fhs_engine())
        orch.try_activate_fhs(reason="t")
        orch2 = _make_orchestrator(store=store, fhs_engine=_fhs_engine())
        assert orch2.fhs_active is True

    def test_failure_state_restored_after_restart(self, tmp_path: Path) -> None:
        store = JsonStateStore(tmp_path)
        orch = _make_orchestrator(store=store, fhs_engine=_fhs_engine())
        orch._record_fhs_failure("r", D0)
        orch2 = _make_orchestrator(store=store, fhs_engine=_fhs_engine())
        assert orch2.fhs_status["failure_count"] == 1
        assert orch2.should_switch_to_fhs(ebt_red_streak=5, today=D0 + timedelta(days=1)) is False

    def test_corrupt_state_fail_closed_disabled(self, tmp_path: Path) -> None:
        store = JsonStateStore(tmp_path)
        (tmp_path / "fhs_switch_state.json").write_text("{broken", encoding="utf-8")
        orch = _make_orchestrator(store=store, fhs_engine=_fhs_engine())
        assert orch.fhs_status["permanently_disabled"] is True
        assert orch.should_switch_to_fhs(ebt_red_streak=5, today=D0) is False


# ── var_breach_machine 注入 (§3.15 折扣进 evaluate_intraday) ──────────────────


class TestVarBreachWiring:
    def test_breached_discount_applied(self) -> None:
        """BREACHED ×0.8: orchestrator 响应 = 直接 evaluate(同 var/cvar, breach) 口径。"""
        machine = VarBreachStateMachine()
        machine.transition(0.05, D0)  # 置 BREACHED
        orch = _make_orchestrator(var_breach_machine=machine)
        _feed_nav(orch)
        snap = orch.latest_snapshot
        assert snap is not None and snap.response is not None
        info = DrawdownInfo(drawdown_pct=0.0, peak_nav=1.0, current_nav=1.0, recovered_pct=0.0)
        direct = DrawdownController().evaluate(
            info, VarCvarMetrics(snap.var_pct, snap.es_pct), var_breach_state="BREACHED"
        )
        assert snap.response.position_cap == pytest.approx(direct.position_cap)
        # 与无折扣基线对比: 严格 ×0.8
        baseline = DrawdownController().evaluate(info, VarCvarMetrics(snap.var_pct, snap.es_pct))
        assert snap.response.position_cap == pytest.approx(baseline.position_cap * 0.8)

    def test_unwired_no_discount(self) -> None:
        orch = _make_orchestrator()
        _feed_nav(orch)
        snap = orch.latest_snapshot
        assert snap is not None and snap.response is not None
        info = DrawdownInfo(drawdown_pct=0.0, peak_nav=1.0, current_nav=1.0, recovered_pct=0.0)
        baseline = DrawdownController().evaluate(info, VarCvarMetrics(snap.var_pct, snap.es_pct))
        assert snap.response.position_cap == pytest.approx(baseline.position_cap)

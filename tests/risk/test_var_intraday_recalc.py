# [BLUEPRINT] MOD-FEEDBACK_LOOP | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [MODULE] tests.risk.test_var_intraday_recalc
# [DOMAIN] D_RISK
# [TESTS] zephyr.risk.core.var_intraday_recalc
# [COVERAGE] 36号 §3.12 七条触发/优先级去重/冷却期 5min/日限 6 次/日切重置 + 重算执行/基线显著对比/breach 状态机更新/recalc_log
# [MATURITY] evolving
# [TTL] task_bound

"""IntradayVarRecalcController 测试 (36号 §3.12 盘中重算)。

实证目标:
    1. 7 条触发各自命中; 优先级去重 (政策>涨跌停潮>传导>相关性>波动率>回撤>亏损),
       first_trigger 取最高优先级, reason 记录全部命中 (优先级序逗号分隔)
    2. 条件 1 clean NAV 口径: 基线缺失/opening_nav 非法 → 跳过
    3. 防抖: 冷却期 5 分钟内 suppressed; 单日 6 次上限 freq_cap_hit; 日切重置计数
    4. 重算执行: var/cvar 产出 (真实 VaRCalculator+TailRiskMonitor), cvar≥var;
       基线对比 var_change_ratio>20% → significant; 无基线跳过; breach 状态机更新;
       recalc_log 累积 + 计数/冷却登记
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import numpy as np
import pytest

from zephyr.risk.core.tail_risk_monitor import TailRiskMonitor
from zephyr.risk.core.var_breach_state_machine import VarBreachStateMachine
from zephyr.risk.core.var_calculator import VaRCalculator
from zephyr.risk.core.var_intraday_recalc import (
    IntradayRecalcConfig,
    IntradayTriggerInput,
    IntradayVarRecalcController,
    InvalidIntradayRecalcConfigError,
)

T0 = datetime(2026, 8, 20, 10, 0, tzinfo=timezone.utc)
D0 = T0.date()


class _Clock:
    def __init__(self, t: datetime = T0) -> None:
        self.now = t

    def __call__(self) -> datetime:
        return self.now

    def advance(self, **kwargs) -> None:
        self.now += timedelta(**kwargs)


def _make_ctl(clock: _Clock, **cfg_kwargs) -> IntradayVarRecalcController:
    return IntradayVarRecalcController(
        VaRCalculator(),
        TailRiskMonitor(),
        config=IntradayRecalcConfig(**cfg_kwargs),
        clock=clock,
    )


def _calm_input() -> IntradayTriggerInput:
    return IntradayTriggerInput(
        opening_nav=1_000_000.0,
        current_nav=999_000.0,
        var_baseline_pct=0.02,
        current_drawdown_pct=-0.01,
    )


def _returns(n: int = 60, sigma: float = 0.01, seed: int = 7) -> np.ndarray:
    return np.random.default_rng(seed).normal(0.0, sigma, size=n)


# ── 配置校验 ──────────────────────────────────────────────────────────────────


class TestConfig:
    @pytest.mark.parametrize(
        "kwargs",
        [
            {"loss_var_ratio": 0.0},
            {"drawdown_threshold": 0.0},
            {"drawdown_threshold": 1.0},
            {"significant_change_ratio": -0.1},
            {"cooldown_seconds": -1.0},
            {"max_recalc_per_day": 0},
        ],
    )
    def test_invalid_config_rejected(self, kwargs: dict) -> None:
        with pytest.raises(InvalidIntradayRecalcConfigError):
            IntradayRecalcConfig(**kwargs)


# ── 触发检测 (7 条件 + 去重) ──────────────────────────────────────────────────


class TestTrigger:
    def test_no_hit(self) -> None:
        trig = _make_ctl(_Clock()).intraday_var_recalc_trigger(_calm_input())
        assert trig.triggered is False
        assert trig.n_hits == 0
        assert trig.reason == ""

    def test_condition1_loss_above_half_var(self) -> None:
        """亏损 1.5% > 0.5×2% (基线 VaR) → 命中。"""
        inputs = IntradayTriggerInput(opening_nav=1_000_000.0, current_nav=985_000.0, var_baseline_pct=0.02)
        trig = _make_ctl(_Clock()).intraday_var_recalc_trigger(inputs)
        assert trig.triggered is True
        assert trig.first_trigger == "loss"
        assert trig.n_hits == 1

    def test_condition1_boundary_not_triggered(self) -> None:
        """亏损恰好 = 0.5×基线 VaR (1.0%) 不命中 (严格 >)。"""
        inputs = IntradayTriggerInput(opening_nav=1_000_000.0, current_nav=990_000.0, var_baseline_pct=0.02)
        trig = _make_ctl(_Clock()).intraday_var_recalc_trigger(inputs)
        assert trig.triggered is False

    def test_condition1_skipped_without_baseline(self) -> None:
        """盘前基线缺失 (§3.19 冷启动) → 条件 1 跳过。"""
        inputs = IntradayTriggerInput(opening_nav=1_000_000.0, current_nav=900_000.0, var_baseline_pct=None)
        trig = _make_ctl(_Clock()).intraday_var_recalc_trigger(inputs)
        assert trig.triggered is False

    def test_condition1_skipped_nonpositive_opening_nav(self) -> None:
        inputs = IntradayTriggerInput(opening_nav=0.0, current_nav=-1.0, var_baseline_pct=0.02)
        trig = _make_ctl(_Clock()).intraday_var_recalc_trigger(inputs)
        assert trig.triggered is False

    def test_condition2_drawdown(self) -> None:
        inputs = IntradayTriggerInput(opening_nav=1.0, current_nav=1.0, current_drawdown_pct=-0.09)
        trig = _make_ctl(_Clock()).intraday_var_recalc_trigger(inputs)
        assert trig.triggered is True
        assert trig.first_trigger == "drawdown"

    def test_condition2_boundary_not_triggered(self) -> None:
        """回撤恰好 -8% 不命中 (严格 <)。"""
        inputs = IntradayTriggerInput(opening_nav=1.0, current_nav=1.0, current_drawdown_pct=-0.08)
        trig = _make_ctl(_Clock()).intraday_var_recalc_trigger(inputs)
        assert trig.triggered is False

    @pytest.mark.parametrize(
        ("field", "key"),
        [
            ("limit_tide", "limit_tide"),
            ("vol_regime_shift", "vol_regime_shift"),
            ("correlation_breakdown", "correlation_breakdown"),
            ("contagion", "contagion"),
            ("policy_event", "policy_event"),
        ],
    )
    def test_boolean_conditions(self, field: str, key: str) -> None:
        trig = _make_ctl(_Clock()).intraday_var_recalc_trigger(
            IntradayTriggerInput(opening_nav=1.0, current_nav=1.0, **{field: True})
        )
        assert trig.triggered is True
        assert trig.first_trigger == key

    def test_priority_dedup_all_hits_in_reason(self) -> None:
        """多条件同时满足: first_trigger=最高优先级 (政策), reason 按优先级序全记录。"""
        inputs = IntradayTriggerInput(
            opening_nav=1_000_000.0,
            current_nav=980_000.0,  # 亏损 2% > 0.5×2% → loss 命中
            var_baseline_pct=0.02,
            current_drawdown_pct=-0.09,  # drawdown 命中
            policy_event=True,
            limit_tide=True,
        )
        trig = _make_ctl(_Clock()).intraday_var_recalc_trigger(inputs)
        assert trig.triggered is True
        assert trig.first_trigger == "policy_event"
        assert trig.n_hits == 4
        assert trig.reason == "policy_event,limit_tide,drawdown,loss"


# ── 防抖 (冷却期 + 日频上限 + 日切) ───────────────────────────────────────────


class TestDebounce:
    def test_cooldown_suppresses_within_5min(self) -> None:
        clock = _Clock()
        ctl = _make_ctl(clock)
        ctl.intraday_var_recalc(_returns(), 1_000_000.0, now=clock())
        inputs = IntradayTriggerInput(opening_nav=1.0, current_nav=1.0, policy_event=True)
        clock.advance(minutes=2)
        trig = ctl.intraday_var_recalc_trigger(inputs, now=clock())
        assert trig.triggered is False
        assert trig.suppressed is True
        assert ctl.suppressed_triggers[-1]["cause"] == "cooldown"

    def test_cooldown_expires_after_5min(self) -> None:
        clock = _Clock()
        ctl = _make_ctl(clock)
        ctl.intraday_var_recalc(_returns(), 1_000_000.0, now=clock())
        inputs = IntradayTriggerInput(opening_nav=1.0, current_nav=1.0, policy_event=True)
        clock.advance(minutes=5, seconds=1)
        trig = ctl.intraday_var_recalc_trigger(inputs, now=clock())
        assert trig.triggered is True

    def test_freq_cap_6_per_day(self) -> None:
        clock = _Clock()
        ctl = _make_ctl(clock)
        for _ in range(6):
            ctl.intraday_var_recalc(_returns(), 1_000_000.0, now=clock())
            clock.advance(minutes=10)
        inputs = IntradayTriggerInput(opening_nav=1.0, current_nav=1.0, policy_event=True)
        trig = ctl.intraday_var_recalc_trigger(inputs, now=clock())
        assert trig.triggered is False
        assert trig.suppressed is True
        assert ctl.suppressed_triggers[-1]["cause"] == "freq_cap"

    def test_day_rollover_resets_count(self) -> None:
        clock = _Clock()
        ctl = _make_ctl(clock)
        for _ in range(6):
            ctl.intraday_var_recalc(_returns(), 1_000_000.0, now=clock())
            clock.advance(minutes=10)
        clock.advance(days=1)  # 次日
        inputs = IntradayTriggerInput(opening_nav=1.0, current_nav=1.0, policy_event=True)
        trig = ctl.intraday_var_recalc_trigger(inputs, now=clock())
        assert trig.triggered is True


# ── 重算执行 + 反馈链 ─────────────────────────────────────────────────────────


class TestRecalc:
    def test_recalc_produces_var_cvar(self) -> None:
        clock = _Clock()
        ctl = _make_ctl(clock)
        result = ctl.intraday_var_recalc(_returns(), 1_000_000.0, now=clock())
        assert result.var_95 > 0
        assert result.cvar_95 >= result.var_95
        assert result.significant_change is False
        assert result.var_change_ratio is None  # 无基线跳过
        assert result.breach_state is None  # 未注入状态机
        assert ctl.recalc_count_today == 1
        assert len(ctl.recalc_log) == 1

    def test_significant_change_above_20pct(self) -> None:
        """var_change_ratio > 20% → significant (§3.12 + §3.16 FHS 触发 3 原料)。"""
        clock = _Clock()
        ctl = _make_ctl(clock)
        result = ctl.intraday_var_recalc(
            _returns(sigma=0.03, seed=11),
            1_000_000.0,
            premarket_baseline={"var_95": 0.01, "cvar_95": 0.013},
            now=clock(),
        )
        assert result.var_change_ratio is not None
        assert result.var_change_ratio > 0.20
        assert result.significant_change is True

    def test_not_significant_within_20pct(self) -> None:
        clock = _Clock()
        ctl = _make_ctl(clock)
        # 先用同分布算出基线, 再用同分布重算 → 变化率远低于 20%
        baseline_var = VaRCalculator().calculate(_returns(), 1.0).value_pct
        result = ctl.intraday_var_recalc(
            _returns(),
            1_000_000.0,
            premarket_baseline={"var_95": baseline_var, "cvar_95": baseline_var * 1.3},
            now=clock(),
        )
        assert result.significant_change is False

    def test_breach_machine_updated(self) -> None:
        """注入 breach 状态机 → 重算驱动 transition, 高波动序列 var>2% 进 BREACHED。"""
        clock = _Clock()
        machine = VarBreachStateMachine()
        ctl = IntradayVarRecalcController(
            VaRCalculator(),
            TailRiskMonitor(),
            breach_machine=machine,
            clock=clock,
        )
        result = ctl.intraday_var_recalc(_returns(sigma=0.05, seed=13), 1_000_000.0, now=clock())
        assert result.breach_state == machine.state.value
        assert result.var_95 > 0.02
        assert machine.state.value == "BREACHED"

    def test_recalc_log_entry_fields(self) -> None:
        clock = _Clock()
        ctl = _make_ctl(clock)
        trig = ctl.intraday_var_recalc_trigger(
            IntradayTriggerInput(opening_nav=1.0, current_nav=1.0, policy_event=True),
            now=clock(),
        )
        ctl.intraday_var_recalc(
            _returns(),
            1_000_000.0,
            premarket_baseline={"var_95": 0.02, "cvar_95": 0.026},
            trigger=trig,
            now=clock(),
        )
        entry = ctl.recalc_log[-1]
        assert entry["trigger_reason"] == "policy_event"
        assert entry["recalc_count"] == 1
        assert entry["var_95"] > 0
        assert entry["cvar_95"] >= entry["var_95"]

    def test_invalid_nav_rejected(self) -> None:
        ctl = _make_ctl(_Clock())
        with pytest.raises(InvalidIntradayRecalcConfigError):
            ctl.intraday_var_recalc(_returns(), 0.0)
        with pytest.raises(InvalidIntradayRecalcConfigError):
            ctl.intraday_var_recalc(_returns(), float("nan"))

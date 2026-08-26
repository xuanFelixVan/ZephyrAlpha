# [BLUEPRINT] MOD-PF-013 | docs/03_modules/_domain_portfolio_core/rl_portfolio_execution/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-PF-013 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.pf_core.test_rl_portfolio_execution
# [TESTS] src/zephyr/pf_core/rl_portfolio_execution.py
"""MOD-PF-013 单元测试：rl_portfolio_execution RL组合优化与执行。

蓝图验收（B10-01835/CAND-PF004-006，A1 §29.9）：
RL三场景编排（组合优化风险预算硬上限钳制 / 最优执行偏离AC轨迹熔断 /
做T底仓不变+风控硬约束）+ C-003回测门禁注入（不过不启用）+ RL仅离线
评估语义标注。trainer/门禁/风控/时钟全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime
from decimal import Decimal

import pytest

pytest.importorskip(
    "zephyr.pf_core.rl_portfolio_execution",
    reason="rl_portfolio_execution not importable",
)

from zephyr.pf_core.rl_portfolio_execution import (  # noqa: E402
    RlPortfolioError,
    RlPortfolioExecutionOrchestrator,
    RlProposal,
    RlRunStatus,
    RlScenario,
)

_T0 = datetime.datetime(2026, 8, 26, 9, 30, 0)
_CAP = Decimal("1.0")
_STATE = {"momentum": 0.5, "vol": 0.2}


def _proposal(scenario: RlScenario = RlScenario.PORTFOLIO_OPTIMIZATION, **kwargs) -> RlProposal:
    kwargs.setdefault("scenario", scenario)
    kwargs.setdefault("actions", {"600000.SH": Decimal("0.2"), "600519.SH": Decimal("0.3")})
    kwargs.setdefault("risk_budget_used", Decimal("0.8"))
    kwargs.setdefault("expected_reward", 1.5)
    return RlProposal(**kwargs)


def _orch(proposal: RlProposal | None = None, gate=True, **kwargs) -> RlPortfolioExecutionOrchestrator:
    kwargs.setdefault("trainer", lambda req: proposal if proposal is not None else _proposal(req.scenario))
    kwargs.setdefault("backtest_gate", (lambda p: gate) if isinstance(gate, bool) else gate)
    kwargs.setdefault("risk_budget_cap", _CAP)
    kwargs.setdefault("ac_deviation_threshold", Decimal("0.1"))
    kwargs.setdefault("clock", lambda: _T0)
    return RlPortfolioExecutionOrchestrator(**kwargs)


# ──────────────────────────────────────────────────────────────────────────────
# 初始化
# ──────────────────────────────────────────────────────────────────────────────


class TestInit:
    def test_trainer_none_raises(self) -> None:
        with pytest.raises(RlPortfolioError):
            _orch(trainer=None)

    def test_gate_none_raises(self) -> None:
        with pytest.raises(RlPortfolioError):
            _orch(backtest_gate=None)

    def test_cap_invalid_raises(self) -> None:
        with pytest.raises(RlPortfolioError):
            _orch(risk_budget_cap=Decimal("0"))
        with pytest.raises(RlPortfolioError):
            _orch(risk_budget_cap=Decimal("-1"))
        with pytest.raises(RlPortfolioError):
            _orch(risk_budget_cap=1.0)  # 拒绝 float

    def test_ac_threshold_invalid_raises(self) -> None:
        with pytest.raises(RlPortfolioError):
            _orch(ac_deviation_threshold=Decimal("-0.1"))
        with pytest.raises(RlPortfolioError):
            _orch(ac_deviation_threshold=Decimal("1.1"))
        with pytest.raises(RlPortfolioError):
            _orch(ac_deviation_threshold=0.1)


# ──────────────────────────────────────────────────────────────────────────────
# 场景①：RL 组合优化
# ──────────────────────────────────────────────────────────────────────────────


class TestPortfolioOptimization:
    def test_happy_enabled_no_clamp(self) -> None:
        result = _orch().run_portfolio_optimization(state=_STATE)
        assert result.status is RlRunStatus.ENABLED
        assert result.enabled is True
        assert result.clamped is False
        assert result.effective_actions == {"600000.SH": Decimal("0.2"), "600519.SH": Decimal("0.3")}
        assert result.risk_budget_used == Decimal("0.8")
        assert any("离线" in n for n in result.notes)

    def test_clamp_scales_to_cap(self) -> None:
        result = _orch(_proposal(risk_budget_used=Decimal("2.0"))).run_portfolio_optimization(state=_STATE)
        assert result.clamped is True
        assert result.risk_budget_used == _CAP  # 钳制不可越
        assert result.effective_actions == {"600000.SH": Decimal("0.1"), "600519.SH": Decimal("0.15")}

    def test_used_zero_no_division(self) -> None:
        result = _orch(_proposal(risk_budget_used=Decimal("0"))).run_portfolio_optimization(state=_STATE)
        assert result.status is RlRunStatus.ENABLED
        assert result.clamped is False

    def test_gate_rejected_not_enabled(self) -> None:
        result = _orch(gate=False).run_portfolio_optimization(state=_STATE)
        assert result.status is RlRunStatus.GATE_REJECTED
        assert result.enabled is False
        assert result.effective_actions == {}
        assert any("门禁" in n for n in result.notes)

    def test_gate_exception_treated_as_rejected(self) -> None:
        def _boom(_p) -> bool:
            raise RuntimeError("gate down")

        result = _orch(gate=_boom).run_portfolio_optimization(state=_STATE)
        assert result.status is RlRunStatus.GATE_REJECTED

    def test_offline_only_false_raises(self) -> None:
        with pytest.raises(RlPortfolioError):
            _orch(_proposal(offline_only=False)).run_portfolio_optimization(state=_STATE)

    def test_scenario_mismatch_raises(self) -> None:
        with pytest.raises(RlPortfolioError):
            _orch(_proposal(RlScenario.OPTIMAL_EXECUTION)).run_portfolio_optimization(state=_STATE)

    def test_invalid_inputs_raise(self) -> None:
        with pytest.raises(RlPortfolioError):  # 非 Decimal 动作
            _orch(_proposal(actions={"600000.SH": 0.2})).run_portfolio_optimization(state=_STATE)
        with pytest.raises(RlPortfolioError):  # 空动作
            _orch(_proposal(actions={})).run_portfolio_optimization(state=_STATE)
        with pytest.raises(RlPortfolioError):  # 奖励非有限
            _orch(_proposal(expected_reward=float("inf"))).run_portfolio_optimization(state=_STATE)
        with pytest.raises(RlPortfolioError):  # 状态非有限
            _orch().run_portfolio_optimization(state={"bad": float("nan")})


# ──────────────────────────────────────────────────────────────────────────────
# 场景②：RL 最优执行（增强 Almgren-Chriss）
# ──────────────────────────────────────────────────────────────────────────────


class TestOptimalExecution:
    _AC = (Decimal("0.5"), Decimal("1.0"))

    def _exec_proposal(self, step0: str, step1: str) -> RlProposal:
        return _proposal(
            RlScenario.OPTIMAL_EXECUTION,
            actions={"step_0": Decimal(step0), "step_1": Decimal(step1)},
        )

    def test_trajectory_invalid_raises(self) -> None:
        with pytest.raises(RlPortfolioError):  # 空轨迹
            _orch().run_optimal_execution(state=_STATE, ac_trajectory=[])
        with pytest.raises(RlPortfolioError):  # 非 Decimal
            _orch().run_optimal_execution(state=_STATE, ac_trajectory=[0.5, 1.0])
        with pytest.raises(RlPortfolioError):  # 越界[0,1]
            _orch().run_optimal_execution(state=_STATE, ac_trajectory=[Decimal("1.5")])
        with pytest.raises(RlPortfolioError):  # 递减
            _orch().run_optimal_execution(state=_STATE, ac_trajectory=[Decimal("0.8"), Decimal("0.4")])

    def test_action_keys_mismatch_raises(self) -> None:
        with pytest.raises(RlPortfolioError):
            _orch(self._exec_proposal("0.5", "1.0")).run_optimal_execution(
                state=_STATE, ac_trajectory=[Decimal("0.3"), Decimal("0.6"), Decimal("1.0")]
            )

    def test_within_threshold_enabled(self) -> None:
        result = _orch(self._exec_proposal("0.55", "0.95")).run_optimal_execution(
            state=_STATE, ac_trajectory=self._AC
        )
        assert result.status is RlRunStatus.ENABLED
        assert result.fused is False
        assert result.effective_actions == {"step_0": Decimal("0.55"), "step_1": Decimal("0.95")}

    def test_deviation_fused_to_ac(self) -> None:
        result = _orch(self._exec_proposal("0.2", "0.95")).run_optimal_execution(
            state=_STATE, ac_trajectory=self._AC
        )
        assert result.status is RlRunStatus.FUSED_TO_AC
        assert result.fused is True
        assert result.effective_actions == {"step_0": Decimal("0.5"), "step_1": Decimal("1.0")}

    def test_clock_injected(self) -> None:
        result = _orch(self._exec_proposal("0.5", "1.0")).run_optimal_execution(
            state=_STATE, ac_trajectory=self._AC
        )
        assert result.run_at == _T0


# ──────────────────────────────────────────────────────────────────────────────
# 场景③：RL 做T
# ──────────────────────────────────────────────────────────────────────────────


class TestT0Trading:
    _BASE = {"600000.SH": Decimal("1000")}

    def _t0_proposal(self, delta: str = "0", symbol: str = "600000.SH") -> RlProposal:
        return _proposal(RlScenario.T0_TRADING, actions={symbol: Decimal(delta)})

    def test_happy_enabled(self) -> None:
        result = _orch(self._t0_proposal(), t0_risk_checker=lambda p: True).run_t0(
            state=_STATE, base_positions=self._BASE
        )
        assert result.status is RlRunStatus.ENABLED
        assert result.effective_actions == {"600000.SH": Decimal("0")}

    def test_net_delta_nonzero_raises(self) -> None:
        with pytest.raises(RlPortfolioError):
            _orch(self._t0_proposal("100"), t0_risk_checker=lambda p: True).run_t0(
                state=_STATE, base_positions=self._BASE
            )

    def test_unknown_symbol_raises(self) -> None:
        with pytest.raises(RlPortfolioError):
            _orch(self._t0_proposal("0", "000001.SZ"), t0_risk_checker=lambda p: True).run_t0(
                state=_STATE, base_positions=self._BASE
            )

    def test_checker_false_raises(self) -> None:
        with pytest.raises(RlPortfolioError):
            _orch(self._t0_proposal(), t0_risk_checker=lambda p: False).run_t0(
                state=_STATE, base_positions=self._BASE
            )

    def test_checker_exception_raises(self) -> None:
        def _boom(_p) -> bool:
            raise RuntimeError("risk down")

        with pytest.raises(RlPortfolioError):
            _orch(self._t0_proposal(), t0_risk_checker=_boom).run_t0(
                state=_STATE, base_positions=self._BASE
            )

    def test_missing_inputs_raises(self) -> None:
        with pytest.raises(RlPortfolioError):  # 底仓为空
            _orch(self._t0_proposal(), t0_risk_checker=lambda p: True).run_t0(
                state=_STATE, base_positions={}
            )
        with pytest.raises(RlPortfolioError):  # 风控校验器未注入
            _orch(self._t0_proposal()).run_t0(state=_STATE, base_positions=self._BASE)


# ──────────────────────────────────────────────────────────────────────────────
# 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestDeterminism:
    def test_same_input_same_output(self) -> None:
        r1 = _orch().run_portfolio_optimization(state=_STATE)
        r2 = _orch().run_portfolio_optimization(state=_STATE)
        assert r1 == r2

# [BLUEPRINT] MOD-AU-008 | docs/03_modules/_domain_autonomy_core/researcher_agent/blueprint.md | §test
# [A_test] module_id: MOD-AU-008 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ResearcherAgent 单元测试 (MOD-AU-008, MVP)。

覆盖: 角色卡族卡模式 / 判定阶梯（硬否 REJECT / 双达标 ACCEPT / 边缘
NEEDS_MORE_DATA / 其余 REJECT）/ 假设与指标 Fail-Closed 校验 / 报告永远
requires_human_gate / ACCEPT 时 human_gate_trigger 信号 / 回调与 sink 异常
不阻断 / 双审计记录 / frozen 不可变。
"""

from __future__ import annotations

import dataclasses

import pytest

from zephyr.autonomy_core.agents.researcher_agent import (
    AGENT_CARD,
    ROLE,
    ExperimentMetrics,
    FactorHypothesis,
    InvalidExperimentMetricsError,
    InvalidHypothesisError,
    InvalidResearcherConfigError,
    ResearcherAgent,
    ResearcherThresholds,
    ResearchVerdict,
)


def _hypothesis(**kw) -> FactorHypothesis:
    base = {
        "hypothesis_id": "HYP-001",
        "name": "momentum_20d",
        "expression": "rank(ret_20d)",
        "rationale": "中期动量溢价",
    }
    base.update(kw)
    return FactorHypothesis(**base)


def _metrics(**kw) -> ExperimentMetrics:
    base = {"ic": 0.05, "sharpe": 1.5, "max_drawdown": 0.10, "sample_count": 120}
    base.update(kw)
    return ExperimentMetrics(**base)


def _agent(**kw) -> ResearcherAgent:
    return ResearcherAgent(**kw)


# ── 角色卡 ───────────────────────────────────────────────────────────────────


class TestAgentCard:
    def test_role(self) -> None:
        assert ROLE == "researcher"
        assert AGENT_CARD["role"] == ROLE

    def test_card_structure(self) -> None:
        assert AGENT_CARD["capabilities"]
        boundaries = AGENT_CARD["autonomyBoundaries"]
        assert "immutable" in boundaries
        assert any("入库" in item or "人工门禁" in item for item in boundaries["human_gated"])

    def test_agent_exposes_card(self) -> None:
        agent = _agent()
        assert agent.ROLE == ROLE
        assert agent.AGENT_CARD is AGENT_CARD


# ── 输入 Fail-Closed ─────────────────────────────────────────────────────────


class TestInputValidation:
    @pytest.mark.parametrize("kw", [{"hypothesis_id": ""}, {"name": ""}, {"expression": ""}])
    def test_invalid_hypothesis_fail_closed(self, kw) -> None:
        with pytest.raises(InvalidHypothesisError):
            _hypothesis(**kw)

    @pytest.mark.parametrize(
        "kw",
        [
            {"ic": 1.5},
            {"ic": -1.5},
            {"max_drawdown": -0.01},
            {"sample_count": -1},
            {"sharpe": float("nan")},
        ],
    )
    def test_invalid_metrics_fail_closed(self, kw) -> None:
        with pytest.raises(InvalidExperimentMetricsError):
            _metrics(**kw)

    @pytest.mark.parametrize(
        "kw",
        [
            {"min_ic": 0.0},
            {"min_ic": 1.5},
            {"min_sharpe": 0.0},
            {"max_drawdown": 0.0},
            {"min_samples": 0},
        ],
    )
    def test_invalid_config_fail_closed(self, kw) -> None:
        with pytest.raises(InvalidResearcherConfigError):
            ResearcherThresholds(**kw)

    def test_frozen(self) -> None:
        hyp = _hypothesis()
        with pytest.raises(dataclasses.FrozenInstanceError):
            hyp.name = "x"  # type: ignore[misc]


# ── 判定阶梯 ─────────────────────────────────────────────────────────────────


class TestEvaluate:
    def test_accept_when_both_pass(self) -> None:
        agent = _agent()
        assert agent.evaluate(_hypothesis(), _metrics()) is ResearchVerdict.ACCEPT

    def test_reject_when_drawdown_breach(self) -> None:
        agent = _agent()
        assert agent.evaluate(_hypothesis(), _metrics(max_drawdown=0.25)) is ResearchVerdict.REJECT

    def test_reject_when_insufficient_samples(self) -> None:
        agent = _agent()
        assert agent.evaluate(_hypothesis(), _metrics(sample_count=30)) is ResearchVerdict.REJECT

    def test_needs_more_data_single_pass(self) -> None:
        agent = _agent()
        # ic 达标、sharpe 不达标 → 边缘
        assert agent.evaluate(_hypothesis(), _metrics(ic=0.05, sharpe=0.5)) is ResearchVerdict.NEEDS_MORE_DATA
        # sharpe 达标、ic 半达标（≥min_ic/2）→ 边缘
        assert agent.evaluate(_hypothesis(), _metrics(ic=0.02, sharpe=1.5)) is ResearchVerdict.NEEDS_MORE_DATA

    def test_reject_weak_signal(self) -> None:
        agent = _agent()
        assert agent.evaluate(_hypothesis(), _metrics(ic=0.005, sharpe=0.2)) is ResearchVerdict.REJECT

    def test_hard_gate_takes_priority(self) -> None:
        agent = _agent()
        # 回撤超限即使 ic/sharpe 双达标也 REJECT
        assert (
            agent.evaluate(_hypothesis(), _metrics(ic=0.08, sharpe=2.0, max_drawdown=0.30))
            is ResearchVerdict.REJECT
        )


# ── act 编排 ─────────────────────────────────────────────────────────────────


class TestAct:
    def test_report_always_human_gated(self) -> None:
        agent = _agent()
        action = agent.act(_hypothesis(), _metrics())
        assert action.report.requires_human_gate is True
        assert action.report.verdict is ResearchVerdict.ACCEPT

    def test_accept_signals_human_gate(self) -> None:
        gate_calls: list[dict] = []
        agent = _agent(human_gate_trigger=lambda payload: gate_calls.append(payload))
        action = agent.act(_hypothesis(), _metrics())
        assert action.gate_signaled is True
        assert len(gate_calls) == 1
        assert gate_calls[0]["hypothesis_id"] == "HYP-001"

    def test_reject_does_not_signal_gate(self) -> None:
        gate_calls: list[dict] = []
        agent = _agent(human_gate_trigger=lambda payload: gate_calls.append(payload))
        action = agent.act(_hypothesis(), _metrics(ic=0.005, sharpe=0.2))
        assert action.verdict is ResearchVerdict.REJECT
        assert action.gate_signaled is False
        assert gate_calls == []

    def test_dual_audit_records(self) -> None:
        agent = _agent()
        action = agent.act(_hypothesis(), _metrics())
        kinds = [r["record_type"] for r in action.audit_records]
        assert "RESEARCHER_EVALUATION" in kinds
        assert "RESEARCHER_GATE_SIGNAL" in kinds

    def test_sinks_invoked(self) -> None:
        exp: list[dict] = []
        rep: list[dict] = []
        agent = _agent(experiment_sink=exp.append, report_sink=rep.append)
        agent.act(_hypothesis(), _metrics())
        assert len(exp) == 1
        assert len(rep) == 1

    def test_callback_exceptions_tolerated(self) -> None:
        def _boom(_payload) -> None:
            raise RuntimeError("down")

        agent = _agent(experiment_sink=_boom, report_sink=_boom, human_gate_trigger=_boom)
        action = agent.act(_hypothesis(), _metrics())
        assert action.verdict is ResearchVerdict.ACCEPT
        assert action.gate_signaled is False  # 触发异常如实记 False

    def test_report_contains_reasons_and_metrics(self) -> None:
        agent = _agent()
        action = agent.act(_hypothesis(), _metrics(max_drawdown=0.25))
        assert action.report.verdict is ResearchVerdict.REJECT
        assert action.report.reasons
        assert action.report.metrics.max_drawdown == 0.25

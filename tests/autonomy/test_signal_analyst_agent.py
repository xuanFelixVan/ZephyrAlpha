# [BLUEPRINT] MOD-AU-009 | docs/03_modules/_domain_autonomy_core/signal_analyst_agent/blueprint.md | §test
# [A_test] module_id: MOD-AU-009 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""SignalAnalystAgent 单元测试 (MOD-AU-009, MVP)。

覆盖: 角色卡族卡模式（不下单 immutable 边界）/ 判定阶梯（健康 PROMOTE /
预警带 DEGRADE / 硬降级 QUARANTINE）/ 漏斗处置映射（FORWARD/DOWNWEIGHT/
HOLD_BACK）/ snapshot 与配置 Fail-Closed / 非 PROMOTE 降级建议审计 /
sink 异常不阻断 / frozen 不可变。
"""

from __future__ import annotations

import dataclasses

import pytest

from zephyr.autonomy_core.agents.signal_analyst_agent import (
    AGENT_CARD,
    ROLE,
    FunnelAction,
    InvalidSignalAnalystConfigError,
    InvalidSignalSnapshotError,
    QualityAssessment,
    SignalAnalystAgent,
    SignalAnalystThresholds,
    SignalQualityVerdict,
    SignalSnapshot,
)


def _snapshot(**kw) -> SignalSnapshot:
    base = {
        "signal_id": "SIG-001",
        "ic_current": 0.045,
        "ic_baseline": 0.05,
        "crowding_score": 0.3,
    }
    base.update(kw)
    return SignalSnapshot(**base)


def _agent(**kw) -> SignalAnalystAgent:
    return SignalAnalystAgent(**kw)


# ── 角色卡 ───────────────────────────────────────────────────────────────────


class TestAgentCard:
    def test_role(self) -> None:
        assert ROLE == "signal_analyst"
        assert AGENT_CARD["role"] == ROLE

    def test_no_order_boundary(self) -> None:
        boundaries = AGENT_CARD["autonomyBoundaries"]
        assert any("下单" in item for item in boundaries["immutable"])

    def test_agent_exposes_card(self) -> None:
        agent = _agent()
        assert agent.ROLE == ROLE
        assert agent.AGENT_CARD is AGENT_CARD


# ── 输入 Fail-Closed ─────────────────────────────────────────────────────────


class TestInputValidation:
    @pytest.mark.parametrize(
        "kw",
        [
            {"signal_id": ""},
            {"ic_current": 1.5},
            {"ic_current": -1.5},
            {"ic_baseline": 0.0},
            {"ic_baseline": -0.01},
            {"crowding_score": -0.1},
            {"crowding_score": 1.1},
        ],
    )
    def test_invalid_snapshot_fail_closed(self, kw) -> None:
        with pytest.raises(InvalidSignalSnapshotError):
            _snapshot(**kw)

    @pytest.mark.parametrize(
        "kw",
        [
            {"decay_warn_ratio": 0.0},
            {"decay_warn_ratio": 1.5},
            {"decay_crit_ratio": 0.0},
            {"decay_crit_ratio": 0.6},  # crit ≥ warn 非法
            {"crowding_warn": 0.0},
            {"crowding_crit": 0.5},  # crit ≤ warn 非法
            {"crowding_crit": 1.5},
        ],
    )
    def test_invalid_config_fail_closed(self, kw) -> None:
        with pytest.raises(InvalidSignalAnalystConfigError):
            SignalAnalystThresholds(**kw)

    def test_frozen(self) -> None:
        snap = _snapshot()
        with pytest.raises(dataclasses.FrozenInstanceError):
            snap.signal_id = "x"  # type: ignore[misc]


# ── 判定阶梯 ─────────────────────────────────────────────────────────────────


class TestAssess:
    def test_promote_healthy(self) -> None:
        agent = _agent()
        a = agent.assess(_snapshot())
        assert isinstance(a, QualityAssessment)
        assert a.verdict is SignalQualityVerdict.PROMOTE
        assert a.funnel_action is FunnelAction.FORWARD
        assert a.ic_decay_ratio == pytest.approx(0.9)

    def test_degrade_decay_warn_band(self) -> None:
        agent = _agent()
        # ic_decay = 0.02/0.05 = 0.4 ≤ warn 0.5，> crit 0.25
        a = agent.assess(_snapshot(ic_current=0.02))
        assert a.verdict is SignalQualityVerdict.DEGRADE
        assert a.funnel_action is FunnelAction.DOWNWEIGHT

    def test_degrade_crowding_warn_band(self) -> None:
        agent = _agent()
        a = agent.assess(_snapshot(crowding_score=0.75))
        assert a.verdict is SignalQualityVerdict.DEGRADE

    def test_quarantine_decay_crit(self) -> None:
        agent = _agent()
        # ic_decay = 0.01/0.05 = 0.2 ≤ crit 0.25
        a = agent.assess(_snapshot(ic_current=0.01))
        assert a.verdict is SignalQualityVerdict.QUARANTINE
        assert a.funnel_action is FunnelAction.HOLD_BACK

    def test_quarantine_crowding_crit(self) -> None:
        agent = _agent()
        a = agent.assess(_snapshot(crowding_score=0.95))
        assert a.verdict is SignalQualityVerdict.QUARANTINE

    def test_crit_takes_priority_over_warn(self) -> None:
        agent = _agent()
        a = agent.assess(_snapshot(ic_current=0.01, crowding_score=0.95))
        assert a.verdict is SignalQualityVerdict.QUARANTINE
        assert a.reasons

    def test_never_emits_order_semantics(self) -> None:
        agent = _agent()
        for snap in (_snapshot(), _snapshot(ic_current=0.02), _snapshot(ic_current=0.01)):
            a = agent.assess(snap)
            assert a.funnel_action in (FunnelAction.FORWARD, FunnelAction.DOWNWEIGHT, FunnelAction.HOLD_BACK)


# ── act 编排 ─────────────────────────────────────────────────────────────────


class TestAct:
    def test_promote_no_degrade_advice(self) -> None:
        seen: list[dict] = []
        agent = _agent(degrade_sink=seen.append)
        action = agent.act(_snapshot())
        assert action.assessment.verdict is SignalQualityVerdict.PROMOTE
        assert action.degrade_adviced is False
        assert seen == []

    def test_non_promote_degrade_advice_and_audit(self) -> None:
        seen: list[dict] = []
        agent = _agent(degrade_sink=seen.append)
        action = agent.act(_snapshot(ic_current=0.01))
        assert action.assessment.verdict is SignalQualityVerdict.QUARANTINE
        assert action.degrade_adviced is True
        assert len(seen) == 1
        assert seen[0]["signal_id"] == "SIG-001"
        kinds = [r["record_type"] for r in action.audit_records]
        assert "SIGNAL_QUALITY_ASSESSMENT" in kinds
        assert "SIGNAL_DEGRADE_ADVICE" in kinds

    def test_sink_exception_tolerated(self) -> None:
        def _boom(_payload) -> None:
            raise RuntimeError("down")

        agent = _agent(degrade_sink=_boom)
        action = agent.act(_snapshot(ic_current=0.01))
        assert action.assessment.verdict is SignalQualityVerdict.QUARANTINE
        assert action.degrade_adviced is False  # 异常如实记 False
        # 审计记录仍内嵌
        assert any(r["record_type"] == "SIGNAL_DEGRADE_ADVICE" for r in action.audit_records)

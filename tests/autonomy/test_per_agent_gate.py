# [BLUEPRINT] MOD-AU-006 | docs/03_modules/_domain_autonomy_core/per_agent_gate/blueprint.md | §test
# [A_test] module_id: MOD-AU-006 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""PerAgentGate 单元测试 (MOD-AU-006, MVP)。

覆盖: 规则集校验（空id/矛盾黑白单/负限额/坏时段窗）/ 判定序短路
（黑名单优先→白名单→限额→时段）/ 未登记 fail-closed DENY / DENY 写安全事件
（sink 异常不阻断）/ 纯内存无 IO / frozen 不可变。
"""

from __future__ import annotations

import dataclasses

import pytest

from zephyr.autonomy_core.per_agent_gate import (
    AgentGateRuleSet,
    AgentGateVerdict,
    GateDecision,
    InvalidAgentGateConfigError,
    PerAgentGate,
    TimeWindow,
)


def _ruleset(**kw) -> AgentGateRuleSet:
    base = {
        "agent_id": "agent-sor",
        "allow_actions": frozenset({"route_order", "cancel_order"}),
        "deny_actions": frozenset({"rewrite_core"}),
        "max_notional_per_order": 1_000_000.0,
        "allowed_windows": (TimeWindow(570, 690), TimeWindow(780, 900)),  # 09:30-11:30 / 13:00-15:00
    }
    base.update(kw)
    return AgentGateRuleSet(**base)


# ── 规则集校验 ───────────────────────────────────────────────────────────────


def test_ruleset_valid_construction() -> None:
    rs = _ruleset()
    assert rs.agent_id == "agent-sor"
    assert "route_order" in rs.allow_actions


@pytest.mark.parametrize("bad_id", ["", "   "])
def test_ruleset_empty_agent_id_rejected(bad_id: str) -> None:
    with pytest.raises(InvalidAgentGateConfigError):
        _ruleset(agent_id=bad_id)


def test_ruleset_allow_deny_overlap_rejected() -> None:
    with pytest.raises(InvalidAgentGateConfigError):
        _ruleset(allow_actions=frozenset({"a", "b"}), deny_actions=frozenset({"b"}))


def test_ruleset_negative_limit_rejected() -> None:
    with pytest.raises(InvalidAgentGateConfigError):
        _ruleset(max_notional_per_order=-1.0)


@pytest.mark.parametrize("start,end", [(-1, 10), (600, 600), (700, 600), (0, 1441)])
def test_time_window_invalid_range_rejected(start: int, end: int) -> None:
    with pytest.raises(InvalidAgentGateConfigError):
        TimeWindow(start, end)


def test_time_window_contains() -> None:
    w = TimeWindow(570, 690)
    assert w.contains(570) is True
    assert w.contains(689) is True
    assert w.contains(690) is False
    assert w.contains(569) is False


# ── 判定序 ───────────────────────────────────────────────────────────────────


def test_deny_action_blacklist_priority() -> None:
    gate = PerAgentGate([_ruleset(deny_actions=frozenset({"route_order"}), allow_actions=frozenset())])
    v = gate.check("agent-sor", "route_order", minute_of_day=600)
    assert v.decision is GateDecision.DENY
    assert v.matched_rule == "deny_actions"


def test_allow_action_not_in_whitelist_denied() -> None:
    gate = PerAgentGate([_ruleset()])
    v = gate.check("agent-sor", "place_order", minute_of_day=600)
    assert v.decision is GateDecision.DENY
    assert v.matched_rule == "allow_actions"


def test_notional_over_limit_denied() -> None:
    gate = PerAgentGate([_ruleset()])
    v = gate.check("agent-sor", "route_order", notional=1_000_000.01, minute_of_day=600)
    assert v.decision is GateDecision.DENY
    assert v.matched_rule == "max_notional_per_order"


def test_notional_at_limit_allowed() -> None:
    gate = PerAgentGate([_ruleset()])
    v = gate.check("agent-sor", "route_order", notional=1_000_000.0, minute_of_day=600)
    assert v.decision is GateDecision.ALLOW


def test_outside_time_window_denied() -> None:
    gate = PerAgentGate([_ruleset()])
    v = gate.check("agent-sor", "route_order", minute_of_day=720)  # 12:00 午休
    assert v.decision is GateDecision.DENY
    assert v.matched_rule == "allowed_windows"


def test_second_window_allowed() -> None:
    gate = PerAgentGate([_ruleset()])
    v = gate.check("agent-sor", "route_order", minute_of_day=840)  # 14:00
    assert v.decision is GateDecision.ALLOW


def test_no_windows_means_all_time_allowed() -> None:
    gate = PerAgentGate([_ruleset(allowed_windows=())])
    v = gate.check("agent-sor", "route_order", minute_of_day=200)
    assert v.decision is GateDecision.ALLOW


def test_empty_whitelist_means_all_actions_allowed() -> None:
    gate = PerAgentGate([_ruleset(allow_actions=frozenset())])
    v = gate.check("agent-sor", "anything_else", minute_of_day=600)
    assert v.decision is GateDecision.ALLOW


# ── fail-closed ──────────────────────────────────────────────────────────────


def test_unregistered_agent_fail_closed_deny() -> None:
    gate = PerAgentGate([_ruleset()])
    v = gate.check("ghost-agent", "route_order", minute_of_day=600)
    assert v.decision is GateDecision.DENY
    assert v.fail_closed is True
    assert v.matched_rule == "unregistered"


def test_empty_action_fail_closed_deny() -> None:
    gate = PerAgentGate([_ruleset()])
    v = gate.check("agent-sor", "", minute_of_day=600)
    assert v.decision is GateDecision.DENY
    assert v.fail_closed is True


# ── 安全事件 ─────────────────────────────────────────────────────────────────


def test_deny_writes_security_event() -> None:
    events: list[dict] = []
    gate = PerAgentGate([_ruleset()], event_sink=events.append)
    gate.check("agent-sor", "rewrite_core", minute_of_day=600)
    assert len(events) == 1
    ev = events[0]
    assert ev["event_type"] == "PER_AGENT_GATE_DENY"
    assert ev["agent_id"] == "agent-sor"
    assert ev["action"] == "rewrite_core"
    assert ev["severity"] == "high"


def test_allow_does_not_write_event() -> None:
    events: list[dict] = []
    gate = PerAgentGate([_ruleset()], event_sink=events.append)
    gate.check("agent-sor", "route_order", minute_of_day=600)
    assert events == []


def test_sink_exception_does_not_break_deny() -> None:
    def _boom(_ev: dict) -> None:
        raise RuntimeError("bus down")

    gate = PerAgentGate([_ruleset()], event_sink=_boom)
    v = gate.check("agent-sor", "rewrite_core", minute_of_day=600)
    assert v.decision is GateDecision.DENY


def test_verdict_to_security_event_shape() -> None:
    gate = PerAgentGate([_ruleset()])
    v = gate.check("agent-sor", "place_order", minute_of_day=600)
    ev = v.to_security_event()
    assert ev["event_type"] == "PER_AGENT_GATE_DENY"
    assert ev["matched_rule"] == "allow_actions"
    assert "reason" in ev


# ── 登记与不可变 ─────────────────────────────────────────────────────────────


def test_duplicate_registration_rejected() -> None:
    gate = PerAgentGate([_ruleset()])
    with pytest.raises(InvalidAgentGateConfigError):
        gate.register(_ruleset())


def test_ruleset_and_verdict_frozen() -> None:
    rs = _ruleset()
    with pytest.raises(dataclasses.FrozenInstanceError):
        rs.max_notional_per_order = 5.0  # type: ignore[misc]
    gate = PerAgentGate([rs])
    v: AgentGateVerdict = gate.check("agent-sor", "route_order", minute_of_day=600)
    with pytest.raises(dataclasses.FrozenInstanceError):
        v.decision = GateDecision.DENY  # type: ignore[misc]


def test_constructor_invalid_ruleset_rejected() -> None:
    with pytest.raises(InvalidAgentGateConfigError):
        PerAgentGate([_ruleset(agent_id=" ")])

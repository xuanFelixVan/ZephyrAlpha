# [BLUEPRINT] MOD-AU-005 | docs/03_modules/_domain_autonomy_core/autonomy_level_registry/blueprint.md | §test
# [A_test] module_id: MOD-AU-005 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""AutonomyLevelRegistry 单元测试 (MOD-AU-005, MVP)。

覆盖: 级别枚举序 / 声明登记与查重 / 未登记 fail-closed / L0-L3 execute 判定矩阵 /
区上限不可降级(human_gated→L2, immutable_core→L0) / 越级 kill_switch 信号 +
violation_hook / 审计记录形状 / frozen 不可变。
"""

from __future__ import annotations

import dataclasses

import pytest

from zephyr.autonomy_core.autonomy_level_registry import (
    AgentAutonomyDeclaration,
    AutonomyCheckVerdict,
    AutonomyDecision,
    AutonomyLevel,
    AutonomyLevelRegistry,
    BoundaryZone,
    InvalidAutonomyDeclarationError,
)


# ── 枚举与声明 ──────────────────────────────────────────────────────────────


def test_level_enum_ordering() -> None:
    assert int(AutonomyLevel.L0_RULE) == 0
    assert int(AutonomyLevel.L1_SUGGEST) == 1
    assert int(AutonomyLevel.L2_APPROVAL) == 2
    assert int(AutonomyLevel.L3_AUTONOMOUS) == 3
    assert AutonomyLevel.L0_RULE < AutonomyLevel.L1_SUGGEST < AutonomyLevel.L2_APPROVAL < AutonomyLevel.L3_AUTONOMOUS


def test_register_and_level_of() -> None:
    reg = AutonomyLevelRegistry()
    decl = reg.register("Researcher", AutonomyLevel.L1_SUGGEST, declared_by="owner", rationale="只出研究建议")
    assert isinstance(decl, AgentAutonomyDeclaration)
    assert decl.agent_role == "Researcher"
    assert decl.level is AutonomyLevel.L1_SUGGEST
    assert reg.level_of("Researcher") is AutonomyLevel.L1_SUGGEST


def test_register_duplicate_rejected() -> None:
    reg = AutonomyLevelRegistry({"Timer": AutonomyLevel.L2_APPROVAL})
    with pytest.raises(InvalidAutonomyDeclarationError):
        reg.register("Timer", AutonomyLevel.L3_AUTONOMOUS)


@pytest.mark.parametrize("bad_role", ["", "   ", None])
def test_register_invalid_role_rejected(bad_role) -> None:
    reg = AutonomyLevelRegistry()
    with pytest.raises(InvalidAutonomyDeclarationError):
        reg.register(bad_role, AutonomyLevel.L1_SUGGEST)


def test_register_invalid_level_rejected() -> None:
    reg = AutonomyLevelRegistry()
    with pytest.raises(InvalidAutonomyDeclarationError):
        reg.register("SOR", "L3")  # type: ignore[arg-type]


def test_constructor_invalid_mapping_rejected() -> None:
    with pytest.raises(InvalidAutonomyDeclarationError):
        AutonomyLevelRegistry({"": AutonomyLevel.L0_RULE})


def test_level_of_unregistered_fail_closed_l0() -> None:
    reg = AutonomyLevelRegistry()
    assert reg.level_of("Ghost") is AutonomyLevel.L0_RULE


# ── 判定矩阵（ai_modifiable 区） ─────────────────────────────────────────────


def test_l0_execute_denied() -> None:
    reg = AutonomyLevelRegistry({"RuleBot": AutonomyLevel.L0_RULE})
    v = reg.check_action("RuleBot", "place_order")
    assert v.decision is AutonomyDecision.DENY
    assert v.kill_switch_triggered is False


def test_l1_execute_denied_but_suggest_allowed() -> None:
    reg = AutonomyLevelRegistry({"Researcher": AutonomyLevel.L1_SUGGEST})
    deny = reg.check_action("Researcher", "place_order")
    assert deny.decision is AutonomyDecision.DENY
    sug = reg.check_action("Researcher", "place_order", mode="suggest")
    assert sug.decision is AutonomyDecision.ALLOW


def test_l2_execute_requires_approval_then_allowed() -> None:
    reg = AutonomyLevelRegistry({"Timer": AutonomyLevel.L2_APPROVAL})
    pending = reg.check_action("Timer", "place_order")
    assert pending.decision is AutonomyDecision.REQUIRE_APPROVAL
    granted = reg.check_action("Timer", "place_order", approval_granted=True)
    assert granted.decision is AutonomyDecision.ALLOW


def test_l3_execute_allowed_on_ai_modifiable() -> None:
    reg = AutonomyLevelRegistry({"SOR": AutonomyLevel.L3_AUTONOMOUS})
    v = reg.check_action("SOR", "route_order", zone=BoundaryZone.AI_MODIFIABLE)
    assert v.decision is AutonomyDecision.ALLOW
    assert v.effective_level is AutonomyLevel.L3_AUTONOMOUS


# ── 区上限不可降级 ───────────────────────────────────────────────────────────


def test_l3_on_human_gated_capped_to_l2() -> None:
    reg = AutonomyLevelRegistry({"SOR": AutonomyLevel.L3_AUTONOMOUS})
    v = reg.check_action("SOR", "route_order", zone=BoundaryZone.HUMAN_GATED)
    assert v.effective_level is AutonomyLevel.L2_APPROVAL
    assert v.decision is AutonomyDecision.REQUIRE_APPROVAL
    granted = reg.check_action("SOR", "route_order", zone=BoundaryZone.HUMAN_GATED, approval_granted=True)
    assert granted.decision is AutonomyDecision.ALLOW


@pytest.mark.parametrize("level", list(AutonomyLevel))
def test_execute_on_immutable_core_denied_with_kill_switch(level: AutonomyLevel) -> None:
    reg = AutonomyLevelRegistry({"AnyRole": level})
    v = reg.check_action("AnyRole", "rewrite_core", zone=BoundaryZone.IMMUTABLE_CORE)
    assert v.decision is AutonomyDecision.DENY
    assert v.effective_level is AutonomyLevel.L0_RULE
    assert v.kill_switch_triggered is True


def test_suggest_on_immutable_core_allowed() -> None:
    reg = AutonomyLevelRegistry({"AnyRole": AutonomyLevel.L3_AUTONOMOUS})
    v = reg.check_action("AnyRole", "rewrite_core", mode="suggest", zone=BoundaryZone.IMMUTABLE_CORE)
    assert v.decision is AutonomyDecision.ALLOW
    assert v.kill_switch_triggered is False


# ── 未登记 fail-closed ───────────────────────────────────────────────────────


def test_unregistered_role_check_fail_closed() -> None:
    reg = AutonomyLevelRegistry()
    v = reg.check_action("Ghost", "place_order")
    assert v.decision is AutonomyDecision.REQUIRE_APPROVAL
    assert v.fail_closed is True
    assert v.level is AutonomyLevel.L0_RULE


# ── violation_hook 与审计 ────────────────────────────────────────────────────


def test_violation_hook_invoked_on_immutable_violation() -> None:
    seen: list[AutonomyCheckVerdict] = []
    reg = AutonomyLevelRegistry({"SOR": AutonomyLevel.L3_AUTONOMOUS}, violation_hook=seen.append)
    v = reg.check_action("SOR", "rewrite_core", zone=BoundaryZone.IMMUTABLE_CORE)
    assert seen == [v]


def test_violation_hook_not_invoked_on_plain_deny() -> None:
    seen: list[AutonomyCheckVerdict] = []
    reg = AutonomyLevelRegistry({"RuleBot": AutonomyLevel.L0_RULE}, violation_hook=seen.append)
    reg.check_action("RuleBot", "place_order")
    assert seen == []


def test_violation_hook_exception_does_not_break_check() -> None:
    def _boom(_v: AutonomyCheckVerdict) -> None:
        raise RuntimeError("hook down")

    reg = AutonomyLevelRegistry({"SOR": AutonomyLevel.L3_AUTONOMOUS}, violation_hook=_boom)
    v = reg.check_action("SOR", "rewrite_core", zone=BoundaryZone.IMMUTABLE_CORE)
    assert v.decision is AutonomyDecision.DENY
    assert v.kill_switch_triggered is True


def test_audit_record_shape() -> None:
    reg = AutonomyLevelRegistry({"SOR": AutonomyLevel.L3_AUTONOMOUS})
    v = reg.check_action("SOR", "rewrite_core", zone=BoundaryZone.IMMUTABLE_CORE)
    rec = v.audit_record()
    assert rec["event_type"] == "AUTONOMY_LEVEL_VIOLATION"
    assert rec["agent_role"] == "SOR"
    assert rec["zone"] == "immutable_core"
    assert rec["kill_switch_triggered"] is True
    assert rec["decision"] == "deny"


def test_snapshot_immutable() -> None:
    reg = AutonomyLevelRegistry({"Timer": AutonomyLevel.L2_APPROVAL})
    snap = reg.snapshot()
    assert isinstance(snap, tuple)
    assert snap[0].agent_role == "Timer"
    with pytest.raises(TypeError):
        snap[0] = None  # type: ignore[index]


# ── frozen 不可变 ────────────────────────────────────────────────────────────


def test_declaration_and_verdict_frozen() -> None:
    reg = AutonomyLevelRegistry({"Timer": AutonomyLevel.L2_APPROVAL})
    decl = reg.snapshot()[0]
    with pytest.raises(dataclasses.FrozenInstanceError):
        decl.level = AutonomyLevel.L3_AUTONOMOUS  # type: ignore[misc]
    v = reg.check_action("Timer", "place_order")
    with pytest.raises(dataclasses.FrozenInstanceError):
        v.decision = AutonomyDecision.ALLOW  # type: ignore[misc]

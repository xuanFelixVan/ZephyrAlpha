# [A_test] module_id: SRC-TST-0329 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_architectural_sod
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.forensic.architectural_sod
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_architectural_sod.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.forensic.architectural_sod import (
    ArchitecturalSoD,
    SoDConflict,
    SoDRole,
)


class TestSoDRole:
    def test_enum_values(self):
        assert SoDRole.DIAGNOSER.value == "DIAGNOSER"
        assert SoDRole.EXECUTOR.value == "EXECUTOR"
        assert SoDRole.VERIFIER.value == "VERIFIER"
        assert SoDRole.AUDITOR.value == "AUDITOR"

    def test_enum_from_string(self):
        assert SoDRole("DIAGNOSER") is SoDRole.DIAGNOSER
        assert SoDRole("EXECUTOR") is SoDRole.EXECUTOR


class TestSoDConflict:
    def test_creation_defaults(self):
        c = SoDConflict(action_id="a1", requested_by=SoDRole.DIAGNOSER, attempted_role=SoDRole.EXECUTOR)
        assert c.blocked is True
        assert c.action_id == "a1"

    def test_creation_explicit(self):
        c = SoDConflict(action_id="a2", requested_by=SoDRole.AUDITOR, attempted_role=SoDRole.VERIFIER, blocked=False)
        assert c.blocked is False


class TestArchitecturalSoD:
    def test_instantiation_defaults(self):
        sod = ArchitecturalSoD()
        assert sod.role_assignments == {}
        assert sod.conflicts == []
        assert ("DIAGNOSER", "EXECUTOR") in sod.forbidden_transitions
        assert ("EXECUTOR", "VERIFIER") in sod.forbidden_transitions

    def test_register_assigns_role(self):
        sod = ArchitecturalSoD()
        sod.register("agent-1", SoDRole.DIAGNOSER)
        assert sod.role_assignments["agent-1"] is SoDRole.DIAGNOSER

    def test_register_overwrites_role(self):
        sod = ArchitecturalSoD()
        sod.register("agent-1", SoDRole.DIAGNOSER)
        sod.register("agent-1", SoDRole.AUDITOR)
        assert sod.role_assignments["agent-1"] is SoDRole.AUDITOR

    def test_check_conflict_forbidden_diagnoser_to_executor(self):
        sod = ArchitecturalSoD()
        sod.register("agent-1", SoDRole.DIAGNOSER)
        assert sod.check_conflict("agent-1", SoDRole.EXECUTOR) is True

    def test_check_conflict_forbidden_executor_to_verifier(self):
        sod = ArchitecturalSoD()
        sod.register("agent-1", SoDRole.EXECUTOR)
        assert sod.check_conflict("agent-1", SoDRole.VERIFIER) is True

    def test_check_conflict_allowed_diagnoser_to_auditor(self):
        sod = ArchitecturalSoD()
        sod.register("agent-1", SoDRole.DIAGNOSER)
        assert sod.check_conflict("agent-1", SoDRole.AUDITOR) is False

    def test_check_conflict_unknown_instance(self):
        sod = ArchitecturalSoD()
        assert sod.check_conflict("unknown", SoDRole.EXECUTOR) is False

    def test_require_dual_approval_returns_roles(self):
        sod = ArchitecturalSoD()
        roles = sod.require_dual_approval("action-1")
        assert SoDRole.DIAGNOSER in roles
        assert SoDRole.AUDITOR in roles
        assert len(roles) == 2

    def test_check_conflict_multiple_agents(self):
        sod = ArchitecturalSoD()
        sod.register("agent-a", SoDRole.DIAGNOSER)
        sod.register("agent-b", SoDRole.VERIFIER)
        assert sod.check_conflict("agent-a", SoDRole.EXECUTOR) is True
        assert sod.check_conflict("agent-b", SoDRole.EXECUTOR) is False

    def test_empty_role_assignments(self):
        sod = ArchitecturalSoD()
        assert len(sod.role_assignments) == 0
        assert sod.check_conflict("any", SoDRole.DIAGNOSER) is False

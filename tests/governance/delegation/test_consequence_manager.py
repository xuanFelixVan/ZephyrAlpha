# [A_test] module_id: SRC-TST-0579 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-366 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_consequence_manager
# [INVARIANTS] is_active only when declared_at set and resolved_at None; activate sets declared_at
# [MODIFY-GUARD] Changes must sync with consequence_manager.py
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] None
# [TESTS] tests/test_consequence_manager.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.escalation.consequence_manager import (
    CONSEQUENCE_REGISTRY,
    ConsequenceDeclaration,
    ConsequenceSeverity,
    activate_consequence,
    get_consequence,
    list_active,
    list_by_severity,
)


class TestConsequenceSeverity:
    def test_enum_values(self):
        assert ConsequenceSeverity.DEGRADED.value == "DEGRADED"
        assert ConsequenceSeverity.SEVERE.value == "SEVERE"
        assert ConsequenceSeverity.CRITICAL.value == "CRITICAL"

    def test_enum_count(self):
        assert len(ConsequenceSeverity) == 3


class TestConsequenceDeclaration:
    def test_creation(self):
        cd = ConsequenceDeclaration(
            con_id="test-001",
            scenario="test scenario",
            bluf="BLUF: test",
            severity=ConsequenceSeverity.SEVERE,
            t_min_to_recover=10,
        )
        assert cd.con_id == "test-001"
        assert cd.is_active is False

    def test_declare_sets_declared_at(self):
        cd = ConsequenceDeclaration(
            con_id="test-002",
            scenario="s",
            bluf="b",
            severity=ConsequenceSeverity.DEGRADED,
            t_min_to_recover=5,
        )
        cd.declare()
        assert cd.declared_at is not None
        assert cd.is_active is True

    def test_resolve_sets_resolved_at(self):
        cd = ConsequenceDeclaration(
            con_id="test-003",
            scenario="s",
            bluf="b",
            severity=ConsequenceSeverity.DEGRADED,
            t_min_to_recover=5,
        )
        cd.declare()
        cd.resolve()
        assert cd.resolved_at is not None
        assert cd.is_active is False

    def test_is_active_false_when_not_declared(self):
        cd = ConsequenceDeclaration(
            con_id="test-004",
            scenario="s",
            bluf="b",
            severity=ConsequenceSeverity.DEGRADED,
            t_min_to_recover=5,
        )
        assert cd.is_active is False

    def test_is_active_false_when_resolved(self):
        cd = ConsequenceDeclaration(
            con_id="test-005",
            scenario="s",
            bluf="b",
            severity=ConsequenceSeverity.DEGRADED,
            t_min_to_recover=5,
        )
        cd.declare()
        cd.resolve()
        assert cd.is_active is False

    def test_default_escalation_chain_empty(self):
        cd = ConsequenceDeclaration(
            con_id="test-006",
            scenario="s",
            bluf="b",
            severity=ConsequenceSeverity.DEGRADED,
            t_min_to_recover=5,
        )
        assert cd.escalation_chain == []


class TestConsequenceRegistry:
    def test_has_known_entries(self):
        assert "alpha_unavailable" in CONSEQUENCE_REGISTRY
        assert "data_vendor_outage" in CONSEQUENCE_REGISTRY
        assert "session_loss" in CONSEQUENCE_REGISTRY
        assert "gate_block" in CONSEQUENCE_REGISTRY

    def test_all_entries_are_declaration_type(self):
        for key, cd in CONSEQUENCE_REGISTRY.items():
            assert isinstance(cd, ConsequenceDeclaration), f"{key} is not ConsequenceDeclaration"


class TestGetConsequence:
    def test_existing(self):
        result = get_consequence("alpha_unavailable")
        assert result is not None
        assert result.con_id == "alpha_unavailable"

    def test_nonexistent(self):
        result = get_consequence("nonexistent_consequence")
        assert result is None


class TestActivateConsequence:
    def test_activate_existing(self):
        cd = activate_consequence("session_loss")
        assert cd is not None
        assert cd.declared_at is not None
        assert cd.is_active is True
        cd.resolve()

    def test_activate_nonexistent(self):
        result = activate_consequence("no_such_consequence")
        assert result is None


class TestListActive:
    def test_initially_empty_or_contains_activated(self):
        active = list_active()
        assert isinstance(active, list)
        for cd in active:
            assert cd.is_active is True


class TestListBySeverity:
    def test_critical_entries(self):
        critical = list_by_severity(ConsequenceSeverity.CRITICAL)
        assert len(critical) > 0
        for cd in critical:
            assert cd.severity == ConsequenceSeverity.CRITICAL

    def test_degraded_entries(self):
        degraded = list_by_severity(ConsequenceSeverity.DEGRADED)
        assert len(degraded) > 0

    def test_severe_entries(self):
        severe = list_by_severity(ConsequenceSeverity.SEVERE)
        assert len(severe) > 0

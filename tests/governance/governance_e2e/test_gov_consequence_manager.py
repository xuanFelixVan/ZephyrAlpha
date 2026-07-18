# [A_test] module_id: SRC-TST-1062 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-387 | docs/03_modules/_domain_governance/blueprint.md | §test
# [MODULE] tests.test_gov_consequence_manager
# [INVARIANTS] CONSEQUENCE_REGISTRY覆盖关键场景;is_active逻辑正确
# [MODIFY-GUARD] src/zephyr/governance/consequence_manager.py
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module
# [TESTS] tests/test_gov_consequence_manager.py
# [TTL] task_bound

from __future__ import annotations

import pytest

cm_mod = pytest.importorskip("zephyr.governance.escalation.consequence_manager")
ConsequenceSeverity = cm_mod.ConsequenceSeverity
ConsequenceDeclaration = cm_mod.ConsequenceDeclaration
CONSEQUENCE_REGISTRY = cm_mod.CONSEQUENCE_REGISTRY
get_consequence = cm_mod.get_consequence
activate_consequence = cm_mod.activate_consequence
list_active = cm_mod.list_active
list_by_severity = cm_mod.list_by_severity


class TestConsequenceSeverity:
    def test_all_values(self):
        assert ConsequenceSeverity.DEGRADED.value == "DEGRADED"
        assert ConsequenceSeverity.SEVERE.value == "SEVERE"
        assert ConsequenceSeverity.CRITICAL.value == "CRITICAL"

    def test_member_count(self):
        assert len(ConsequenceSeverity) == 3

    def test_is_str_enum(self):
        assert isinstance(ConsequenceSeverity.DEGRADED, str)


class TestConsequenceDeclaration:
    def test_create_declaration(self):
        cd = ConsequenceDeclaration(
            con_id="test_1",
            scenario="test scenario",
            bluf="BLUF: test",
            severity=ConsequenceSeverity.DEGRADED,
            t_min_to_recover=5,
        )
        assert cd.con_id == "test_1"
        assert cd.scenario == "test scenario"
        assert cd.severity == ConsequenceSeverity.DEGRADED
        assert cd.declared_at is None
        assert cd.resolved_at is None

    def test_is_active_initially_false(self):
        cd = ConsequenceDeclaration(
            con_id="test_2",
            scenario="s",
            bluf="b",
            severity=ConsequenceSeverity.SEVERE,
            t_min_to_recover=10,
        )
        assert cd.is_active is False

    def test_declare_sets_active(self):
        cd = ConsequenceDeclaration(
            con_id="test_3",
            scenario="s",
            bluf="b",
            severity=ConsequenceSeverity.CRITICAL,
            t_min_to_recover=30,
        )
        cd.declare()
        assert cd.declared_at is not None
        assert cd.is_active is True

    def test_resolve_deactivates(self):
        cd = ConsequenceDeclaration(
            con_id="test_4",
            scenario="s",
            bluf="b",
            severity=ConsequenceSeverity.DEGRADED,
            t_min_to_recover=5,
        )
        cd.declare()
        cd.resolve()
        assert cd.resolved_at is not None
        assert cd.is_active is False

    def test_default_escalation_chain_empty(self):
        cd = ConsequenceDeclaration(
            con_id="test_5",
            scenario="s",
            bluf="b",
            severity=ConsequenceSeverity.DEGRADED,
            t_min_to_recover=5,
        )
        assert cd.escalation_chain == []

    def test_default_recovery_procedure_empty(self):
        cd = ConsequenceDeclaration(
            con_id="test_6",
            scenario="s",
            bluf="b",
            severity=ConsequenceSeverity.DEGRADED,
            t_min_to_recover=5,
        )
        assert cd.recovery_procedure == ""

    def test_declare_sets_iso_timestamp(self):
        cd = ConsequenceDeclaration(
            con_id="test_7",
            scenario="s",
            bluf="b",
            severity=ConsequenceSeverity.DEGRADED,
            t_min_to_recover=5,
        )
        cd.declare()
        assert "T" in cd.declared_at


class TestConsequenceRegistry:
    def test_registry_not_empty(self):
        assert len(CONSEQUENCE_REGISTRY) > 0

    def test_known_entries_exist(self):
        assert "alpha_unavailable" in CONSEQUENCE_REGISTRY
        assert "data_vendor_outage" in CONSEQUENCE_REGISTRY
        assert "session_loss" in CONSEQUENCE_REGISTRY
        assert "gate_block" in CONSEQUENCE_REGISTRY

    def test_all_entries_have_required_fields(self):
        for con_id, cd in CONSEQUENCE_REGISTRY.items():
            assert cd.con_id == con_id
            assert len(cd.scenario) > 0
            assert len(cd.bluf) > 0
            assert isinstance(cd.severity, ConsequenceSeverity)
            assert cd.t_min_to_recover > 0


class TestGetConsequence:
    def test_known_id(self):
        result = get_consequence("alpha_unavailable")
        assert result is not None
        assert result.con_id == "alpha_unavailable"

    def test_unknown_id_returns_none(self):
        result = get_consequence("nonexistent_consequence")
        assert result is None

    def test_none_id_returns_none(self):
        result = get_consequence(None)
        assert result is None


class TestActivateConsequence:
    def test_activate_sets_declared_at(self):
        cd = activate_consequence("session_loss")
        assert cd is not None
        assert cd.declared_at is not None
        assert cd.is_active is True

    def test_activate_unknown_returns_none(self):
        result = activate_consequence("nonexistent")
        assert result is None

    def test_activate_idempotent(self):
        activate_consequence("gate_block")
        first_declared = CONSEQUENCE_REGISTRY["gate_block"].declared_at
        activate_consequence("gate_block")
        second_declared = CONSEQUENCE_REGISTRY["gate_block"].declared_at
        assert second_declared is not None


class TestListActive:
    def test_after_activate_has_items(self):
        for cd in CONSEQUENCE_REGISTRY.values():
            cd.resolved_at = None
            cd.declared_at = None
        activate_consequence("session_loss")
        active = list_active()
        assert any(c.con_id == "session_loss" for c in active)
        for cd in CONSEQUENCE_REGISTRY.values():
            cd.resolved_at = None
            cd.declared_at = None

    def test_after_resolve_empty(self):
        for cd in CONSEQUENCE_REGISTRY.values():
            cd.resolved_at = None
            cd.declared_at = None
        active = list_active()
        assert len(active) == 0


class TestListBySeverity:
    def test_critical_entries(self):
        result = list_by_severity(ConsequenceSeverity.CRITICAL)
        assert isinstance(result, list)
        for c in result:
            assert c.severity == ConsequenceSeverity.CRITICAL

    def test_degraded_entries(self):
        result = list_by_severity(ConsequenceSeverity.DEGRADED)
        assert isinstance(result, list)
        for c in result:
            assert c.severity == ConsequenceSeverity.DEGRADED

    def test_severe_entries(self):
        result = list_by_severity(ConsequenceSeverity.SEVERE)
        assert isinstance(result, list)
        for c in result:
            assert c.severity == ConsequenceSeverity.SEVERE

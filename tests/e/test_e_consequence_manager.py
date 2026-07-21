# [A_test] module_id: MOD-GOV_e_consequence_manager | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §
# [MODULE] tests.test_e_consequence_manager
# [INVARIANTS] test完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import time

from zephyr.governance.escalation.consequence_manager import (
    CONSEQUENCE_REGISTRY,
    ConsequenceDeclaration,
    ConsequenceSeverity,
    activate_consequence,
    get_consequence,
    list_active,
    list_by_severity,
)


def _reset_registry_entries() -> None:
    for entry in CONSEQUENCE_REGISTRY.values():
        entry.declared_at = None
        entry.resolved_at = None


class TestConsequenceSeverity:
    def test_member_count(self):
        assert len(ConsequenceSeverity) == 3

    def test_member_values(self):
        assert ConsequenceSeverity.DEGRADED.value == "DEGRADED"
        assert ConsequenceSeverity.SEVERE.value == "SEVERE"
        assert ConsequenceSeverity.CRITICAL.value == "CRITICAL"

    def test_membership(self):
        members = {m.value for m in ConsequenceSeverity}
        assert members == {"DEGRADED", "SEVERE", "CRITICAL"}


class TestConsequenceDeclaration:
    def test_instantiation_with_required_fields(self):
        cd = ConsequenceDeclaration(
            con_id="test_id",
            scenario="test scenario",
            bluf="test bluf",
            severity=ConsequenceSeverity.DEGRADED,
            t_min_to_recover=10,
        )
        assert cd.con_id == "test_id"
        assert cd.scenario == "test scenario"
        assert cd.bluf == "test bluf"
        assert cd.severity is ConsequenceSeverity.DEGRADED
        assert cd.t_min_to_recover == 10
        assert cd.escalation_chain == []
        assert cd.recovery_procedure == ""
        assert cd.declared_at is None
        assert cd.resolved_at is None

    def test_instantiation_with_all_fields(self):
        cd = ConsequenceDeclaration(
            con_id="full_id",
            scenario="full scenario",
            bluf="full bluf",
            severity=ConsequenceSeverity.CRITICAL,
            t_min_to_recover=60,
            escalation_chain=["step1", "step2"],
            recovery_procedure="do A then B",
            declared_at="2026-01-01T00:00:00+00:00",
            resolved_at="2026-01-02T00:00:00+00:00",
        )
        assert cd.con_id == "full_id"
        assert cd.escalation_chain == ["step1", "step2"]
        assert cd.recovery_procedure == "do A then B"
        assert cd.declared_at == "2026-01-01T00:00:00+00:00"
        assert cd.resolved_at == "2026-01-02T00:00:00+00:00"

    def test_is_active_both_none_returns_false(self):
        cd = ConsequenceDeclaration(
            con_id="t",
            scenario="s",
            bluf="b",
            severity=ConsequenceSeverity.DEGRADED,
            t_min_to_recover=1,
        )
        assert cd.is_active is False

    def test_is_active_declared_only_returns_true(self):
        cd = ConsequenceDeclaration(
            con_id="t",
            scenario="s",
            bluf="b",
            severity=ConsequenceSeverity.DEGRADED,
            t_min_to_recover=1,
            declared_at="2026-01-01T00:00:00+00:00",
        )
        assert cd.is_active is True

    def test_is_active_both_set_returns_false(self):
        cd = ConsequenceDeclaration(
            con_id="t",
            scenario="s",
            bluf="b",
            severity=ConsequenceSeverity.DEGRADED,
            t_min_to_recover=1,
            declared_at="2026-01-01T00:00:00+00:00",
            resolved_at="2026-01-02T00:00:00+00:00",
        )
        assert cd.is_active is False

    def test_declare_sets_declared_at(self):
        cd = ConsequenceDeclaration(
            con_id="t",
            scenario="s",
            bluf="b",
            severity=ConsequenceSeverity.DEGRADED,
            t_min_to_recover=1,
        )
        assert cd.declared_at is None
        cd.declare()
        assert cd.declared_at is not None
        assert cd.declared_at.endswith("+00:00") or cd.declared_at.endswith("Z")

    def test_resolve_sets_resolved_at(self):
        cd = ConsequenceDeclaration(
            con_id="t",
            scenario="s",
            bluf="b",
            severity=ConsequenceSeverity.DEGRADED,
            t_min_to_recover=1,
        )
        assert cd.resolved_at is None
        cd.resolve()
        assert cd.resolved_at is not None
        assert cd.resolved_at.endswith("+00:00") or cd.resolved_at.endswith("Z")

    def test_declare_then_resolve_is_active_false(self):
        cd = ConsequenceDeclaration(
            con_id="t",
            scenario="s",
            bluf="b",
            severity=ConsequenceSeverity.DEGRADED,
            t_min_to_recover=1,
        )
        cd.declare()
        assert cd.is_active is True
        cd.resolve()
        assert cd.is_active is False

    def test_declare_twice_updates_declared_at(self):
        cd = ConsequenceDeclaration(
            con_id="t",
            scenario="s",
            bluf="b",
            severity=ConsequenceSeverity.DEGRADED,
            t_min_to_recover=1,
        )
        cd.declare()
        first_declared = cd.declared_at
        time.sleep(0.001)
        cd.declare()
        assert cd.declared_at is not None
        assert cd.declared_at != first_declared

    def test_resolve_without_declare_sets_resolved_but_inactive(self):
        cd = ConsequenceDeclaration(
            con_id="t",
            scenario="s",
            bluf="b",
            severity=ConsequenceSeverity.DEGRADED,
            t_min_to_recover=1,
        )
        cd.resolve()
        assert cd.resolved_at is not None
        assert cd.is_active is False

    def test_is_active_resolved_only_returns_false(self):
        cd = ConsequenceDeclaration(
            con_id="t",
            scenario="s",
            bluf="b",
            severity=ConsequenceSeverity.DEGRADED,
            t_min_to_recover=1,
            resolved_at="2026-01-01T00:00:00+00:00",
        )
        assert cd.is_active is False


class TestConsequenceRegistry:
    def test_registry_has_4_entries(self):
        assert len(CONSEQUENCE_REGISTRY) == 4

    def test_expected_keys(self):
        expected = {"alpha_unavailable", "data_vendor_outage", "session_loss", "gate_block"}
        assert set(CONSEQUENCE_REGISTRY.keys()) == expected

    def test_all_entries_have_required_fields(self):
        for con_id, cd in CONSEQUENCE_REGISTRY.items():
            assert cd.con_id == con_id
            assert isinstance(cd.scenario, str) and len(cd.scenario) > 0
            assert isinstance(cd.bluf, str) and len(cd.bluf) > 0
            assert isinstance(cd.severity, ConsequenceSeverity)
            assert isinstance(cd.t_min_to_recover, int) and cd.t_min_to_recover > 0
            assert isinstance(cd.escalation_chain, list) and len(cd.escalation_chain) > 0
            assert isinstance(cd.recovery_procedure, str) and len(cd.recovery_procedure) > 0


class TestGetConsequence:
    def test_valid_id_returns_correct_entry(self):
        cd = get_consequence("session_loss")
        assert cd is not None
        assert cd.con_id == "session_loss"
        assert cd.severity is ConsequenceSeverity.DEGRADED

    def test_invalid_id_returns_none(self):
        assert get_consequence("nonexistent") is None

    def test_empty_string_returns_none(self):
        assert get_consequence("") is None


class TestActivateConsequence:
    def teardown_method(self):
        _reset_registry_entries()

    def test_valid_id_declares_and_returns(self):
        cd = activate_consequence("gate_block")
        assert cd is not None
        assert cd.con_id == "gate_block"
        assert cd.declared_at is not None
        assert cd.is_active is True

    def test_invalid_id_returns_none(self):
        assert activate_consequence("nonexistent") is None

    def test_activate_then_resolve_is_inactive(self):
        cd = activate_consequence("session_loss")
        assert cd is not None
        assert cd.is_active is True
        cd.resolve()
        assert cd.is_active is False


class TestListActive:
    def teardown_method(self):
        _reset_registry_entries()

    def test_empty_initially(self):
        assert list_active() == []

    def test_one_after_activate(self):
        activate_consequence("alpha_unavailable")
        active = list_active()
        assert len(active) == 1
        assert active[0].con_id == "alpha_unavailable"

    def test_empty_after_resolve(self):
        cd = activate_consequence("data_vendor_outage")
        assert len(list_active()) == 1
        cd.resolve()
        assert list_active() == []

    def test_empty_with_no_activates(self):
        _reset_registry_entries()
        assert list_active() == []


class TestListBySeverity:
    def test_filter_degraded(self):
        result = list_by_severity(ConsequenceSeverity.DEGRADED)
        assert len(result) == 1
        assert result[0].con_id == "session_loss"

    def test_filter_severe(self):
        result = list_by_severity(ConsequenceSeverity.SEVERE)
        assert len(result) == 2
        ids = {r.con_id for r in result}
        assert ids == {"data_vendor_outage", "gate_block"}

    def test_filter_critical(self):
        result = list_by_severity(ConsequenceSeverity.CRITICAL)
        assert len(result) == 1
        assert result[0].con_id == "alpha_unavailable"

    def test_returns_empty_for_severity_with_no_match(self):
        from enum import Enum

        class DummySeverity(str, Enum):
            FAKE = "FAKE"

        assert list_by_severity(DummySeverity.FAKE) == []

    def test_all_members_have_at_least_one_entry(self):
        for severity in ConsequenceSeverity:
            result = list_by_severity(severity)
            assert len(result) >= 1


class TestConsequenceDeclarationModelValidation:
    def test_t_min_to_recover_int_field(self):
        cd = ConsequenceDeclaration(
            con_id="x",
            scenario="x",
            bluf="x",
            severity=ConsequenceSeverity.SEVERE,
            t_min_to_recover=42,
        )
        assert cd.t_min_to_recover == 42
        assert isinstance(cd.t_min_to_recover, int)

    def test_escalation_chain_defaults_to_empty_list(self):
        cd = ConsequenceDeclaration(
            con_id="x",
            scenario="x",
            bluf="x",
            severity=ConsequenceSeverity.SEVERE,
            t_min_to_recover=1,
        )
        assert cd.escalation_chain == []

    def test_recovery_procedure_defaults_to_empty_string(self):
        cd = ConsequenceDeclaration(
            con_id="x",
            scenario="x",
            bluf="x",
            severity=ConsequenceSeverity.SEVERE,
            t_min_to_recover=1,
        )
        assert cd.recovery_procedure == ""


class TestConsequenceDeclarationEdgeCases:
    def test_activate_consequence_on_already_active_updates_timestamp(self):
        _reset_registry_entries()
        cd1 = activate_consequence("gate_block")
        first_ts = cd1.declared_at
        time.sleep(0.001)
        cd2 = activate_consequence("gate_block")
        assert cd2.declared_at != first_ts
        _reset_registry_entries()

    def test_activate_consequence_with_empty_string(self):
        assert activate_consequence("") is None

    def test_activate_consequence_returns_same_instance(self):
        _reset_registry_entries()
        cd1 = get_consequence("gate_block")
        cd2 = activate_consequence("gate_block")
        assert cd1 is cd2
        _reset_registry_entries()

    def test_get_consequence_does_not_mutate(self):
        _reset_registry_entries()
        cd = get_consequence("alpha_unavailable")
        assert cd is not None
        assert cd.declared_at is None
        assert cd.resolved_at is None
        assert cd.is_active is False

    def test_all_entries_initially_not_active(self):
        _reset_registry_entries()
        for cd in CONSEQUENCE_REGISTRY.values():
            assert cd.is_active is False

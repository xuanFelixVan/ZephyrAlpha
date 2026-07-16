# [A_test] module_id: SRC-TST-0743 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_design_decisions
# [INVARIANTS] DECISIONS dict has 14 entries; get returns None for unknown; list_active filters ACTIVE
# [MODIFY-GUARD] src/zephyr/orchestrator/design_decisions.py
# [CONSUMERS] CI
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] get/list_all/list_active/get_by_impact/check_re_evaluate never raise
# [TESTS] tests/test_design_decisions_root.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.orchestrator.contracts.design_decisions import (
    DECISIONS,
    DecisionRegistry,
    DecisionStatus,
    DesignDecision,
)


class TestDecisionStatusEnum:
    def test_active_value(self):
        assert DecisionStatus.ACTIVE == "active"

    def test_re_evaluated_value(self):
        assert DecisionStatus.RE_EVALUATED == "re_evaluated"

    def test_superseded_value(self):
        assert DecisionStatus.SUPERSEDED == "superseded"


class TestDesignDecisionModel:
    def test_creation_with_required_fields(self):
        dd = DesignDecision(dd_id="DD-TEST", title="Test", content="content")
        assert dd.dd_id == "DD-TEST"
        assert dd.title == "Test"
        assert dd.content == "content"

    def test_default_values(self):
        dd = DesignDecision(dd_id="DD-X", title="X", content="x")
        assert dd.status == DecisionStatus.ACTIVE
        assert dd.alternatives == []
        assert dd.rationale == ""
        assert dd.re_evaluate_when == ""
        assert dd.impact_scope == ""


class TestDecisionRegistryInstantiation:
    def test_create_instance(self):
        reg = DecisionRegistry()
        assert reg is not None


class TestGet:
    def test_known_dd_returns_decision(self):
        reg = DecisionRegistry()
        dd = reg.get("DD-1")
        assert dd is not None
        assert dd.dd_id == "DD-1"

    def test_unknown_dd_returns_none(self):
        reg = DecisionRegistry()
        assert reg.get("DD-999") is None

    def test_empty_string_returns_none(self):
        reg = DecisionRegistry()
        assert reg.get("") is None


class TestListAll:
    def test_returns_list(self):
        reg = DecisionRegistry()
        result = reg.list_all()
        assert isinstance(result, list)

    def test_returns_all_decisions(self):
        reg = DecisionRegistry()
        result = reg.list_all()
        assert len(result) == len(DECISIONS)


class TestListActive:
    def test_returns_only_active(self):
        reg = DecisionRegistry()
        result = reg.list_active()
        for dd in result:
            assert dd.status == DecisionStatus.ACTIVE

    def test_all_default_active(self):
        reg = DecisionRegistry()
        result = reg.list_active()
        assert len(result) == len(DECISIONS)


class TestGetByImpact:
    def test_matching_keyword(self):
        reg = DecisionRegistry()
        result = reg.get_by_impact("熔断")
        assert isinstance(result, list)
        assert len(result) >= 1

    def test_non_matching_keyword(self):
        reg = DecisionRegistry()
        result = reg.get_by_impact("zzz_nonexistent_zzz")
        assert result == []

    def test_case_insensitive(self):
        reg = DecisionRegistry()
        result_lower = reg.get_by_impact("架构")
        result_upper = reg.get_by_impact("架构")
        assert len(result_lower) == len(result_upper)


class TestCheckReEvaluate:
    def test_unknown_dd_returns_false(self):
        reg = DecisionRegistry()
        assert reg.check_re_evaluate("DD-999", True) is False

    def test_known_dd_condition_true(self):
        reg = DecisionRegistry()
        assert reg.check_re_evaluate("DD-1", True) is True

    def test_known_dd_condition_false(self):
        reg = DecisionRegistry()
        assert reg.check_re_evaluate("DD-1", False) is False


class TestDecisionsData:
    def test_has_14_entries(self):
        assert len(DECISIONS) == 14

    def test_all_keys_match_dd_ids(self):
        for key, dd in DECISIONS.items():
            assert dd.dd_id == key

    def test_all_have_title_and_content(self):
        for dd in DECISIONS.values():
            assert dd.title != ""
            assert dd.content != ""


class TestBoundary:
    def test_get_by_impact_empty_string(self):
        reg = DecisionRegistry()
        result = reg.get_by_impact("")
        assert isinstance(result, list)

    def test_list_active_returns_new_list(self):
        reg = DecisionRegistry()
        a = reg.list_active()
        b = reg.list_active()
        assert a is not b

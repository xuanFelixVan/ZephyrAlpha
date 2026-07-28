# [A_test] module_id: MOD-GOV_mvep_orchestrator | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-022 | docs/03_modules/_domain_autonomy_perm/escalation_protocol/blueprint.md | §

# [MODULE] tests.test_mvep_orchestrator

# [INVARIANTS] MVEP Phase Gate不可跳过;Phase 0→5顺序不可逆

# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/escalation-protocol/blueprint.md

# [CONSUMERS] pytest

# [STABILITY] stable

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] 测试异常必须包含 context 和 rule_id

# [TESTS] tests/test_mvep_orchestrator.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.intelligence_governance.mvep_orchestrator import MVE_SEQUENCE, MVEPOrchestrator


class TestMVEPOrchestratorInit:
    def test_init_creates_empty_implemented_set(self):
        orch = MVEPOrchestrator()
        assert isinstance(orch.implemented, set)
        assert len(orch.implemented) == 0

    def test_init_no_args_required(self):
        orch = MVEPOrchestrator()
        assert orch is not None


class TestMarkImplemented:
    def test_mark_single_decision(self):
        orch = MVEPOrchestrator()
        orch.mark_implemented("D-022-01")
        assert "D-022-01" in orch.implemented

    def test_mark_multiple_decisions(self):
        orch = MVEPOrchestrator()
        for did in ["D-022-01", "D-022-02", "D-022-03"]:
            orch.mark_implemented(did)
        assert orch.implemented == {"D-022-01", "D-022-02", "D-022-03"}

    def test_mark_duplicate_idempotent(self):
        orch = MVEPOrchestrator()
        orch.mark_implemented("D-022-01")
        orch.mark_implemented("D-022-01")
        assert len(orch.implemented) == 1

    def test_mark_empty_string(self):
        orch = MVEPOrchestrator()
        orch.mark_implemented("")
        assert "" in orch.implemented

    def test_mark_none_still_added(self):
        orch = MVEPOrchestrator()
        orch.mark_implemented(None)
        assert None in orch.implemented


class TestMissingMvps:
    def test_all_missing_at_start(self):
        orch = MVEPOrchestrator()
        missing = orch.missing_mvps()
        base = {d.split()[0] for d in MVE_SEQUENCE}
        assert set(missing) == base
        assert len(missing) == len(MVE_SEQUENCE)

    def test_one_implemented_reduces_missing(self):
        orch = MVEPOrchestrator()
        orch.mark_implemented("D-022-01")
        missing = orch.missing_mvps()
        assert "D-022-01" not in missing
        assert len(missing) == len(MVE_SEQUENCE) - 1

    def test_all_implemented_returns_empty(self):
        orch = MVEPOrchestrator()
        base = {d.split()[0] for d in MVE_SEQUENCE}
        for did in base:
            orch.mark_implemented(did)
        assert orch.missing_mvps() == []

    def test_extra_id_not_in_sequence_does_not_affect_missing(self):
        orch = MVEPOrchestrator()
        orch.mark_implemented("D-999-99")
        missing = orch.missing_mvps()
        base = {d.split()[0] for d in MVE_SEQUENCE}
        assert set(missing) == base

    def test_returns_list_type(self):
        orch = MVEPOrchestrator()
        result = orch.missing_mvps()
        assert isinstance(result, list)


class TestAllImplemented:
    def test_false_at_start(self):
        orch = MVEPOrchestrator()
        assert orch.all_implemented() is False

    def test_false_when_partial(self):
        orch = MVEPOrchestrator()
        orch.mark_implemented("D-022-01")
        orch.mark_implemented("D-022-02")
        assert orch.all_implemented() is False

    def test_true_when_all_marked(self):
        orch = MVEPOrchestrator()
        base = {d.split()[0] for d in MVE_SEQUENCE}
        for did in base:
            orch.mark_implemented(did)
        assert orch.all_implemented() is True

    def test_extra_id_does_not_satisfy(self):
        orch = MVEPOrchestrator()
        orch.mark_implemented("D-999-99")
        assert orch.all_implemented() is False

    def test_returns_bool_type(self):
        orch = MVEPOrchestrator()
        assert isinstance(orch.all_implemented(), bool)


class TestMVESequenceConstant:
    def test_sequence_has_five_entries(self):
        assert len(MVE_SEQUENCE) == 5

    def test_sequence_entries_contain_decision_ids(self):
        for entry in MVE_SEQUENCE:
            parts = entry.split()
            assert len(parts) == 2
            assert parts[0].startswith("D-022-")

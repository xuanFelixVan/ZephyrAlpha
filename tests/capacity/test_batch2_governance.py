# [A_test] module_id: SRC-TST-0416 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infrastructure_operations/capacity_assurance/blueprint.md | §test
# [MODULE] tests.test_batch2_governance
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_batch2_governance.py
# [TTL] task_bound

import pytest

mod = pytest.importorskip("zephyr.feedback_loop.capacity_assurance.batch2_governance", reason="batch2_governance not available")
BATCH2_CONTRACTS = mod.BATCH2_CONTRACTS


class TestBatch2ContractCount:
    def test_has_15_contracts(self):
        assert len(BATCH2_CONTRACTS) == 15

    def test_all_values_are_pydantic_models(self):
        from pydantic import BaseModel

        for contract_id, model in BATCH2_CONTRACTS.items():
            assert issubclass(model, BaseModel), f"{contract_id} is not a BaseModel subclass"


class TestCT_PR_001:
    def test_valid_payload(self):
        model = BATCH2_CONTRACTS["CT-PR-001"]
        instance = model(module="test", field="value", author_agent="agent_1", audit_result="pass")
        assert instance.module == "test"
        assert instance.old_value is None

    def test_missing_required_field(self):
        model = BATCH2_CONTRACTS["CT-PR-001"]
        with pytest.raises(Exception):
            model(module="test")


class TestCT_PR_002:
    def test_default_algorithm(self):
        model = BATCH2_CONTRACTS["CT-PR-002"]
        instance = model(curr_hash="abc123")
        assert instance.algorithm == "sha256"
        assert instance.prev_hash is None


class TestCT_AG_002:
    def test_default_findings(self):
        model = BATCH2_CONTRACTS["CT-AG-002"]
        instance = model(audit_id="a1", passed=True, timestamp="2026-01-01T00:00:00")
        assert instance.findings == []


class TestCT_VL_002:
    def test_default_values(self):
        model = BATCH2_CONTRACTS["CT-VL-002"]
        instance = model()
        assert instance.strict_mode is True
        assert instance.ignore_missing_imports is False


class TestCT_SB_002:
    def test_default_values(self):
        model = BATCH2_CONTRACTS["CT-SB-002"]
        instance = model()
        assert instance.max_memory_bytes == 536870912
        assert instance.network_access is False


class TestCT_MB_001:
    def test_default_values(self):
        model = BATCH2_CONTRACTS["CT-MB-001"]
        instance = model()
        assert instance.batch_size == 100
        assert instance.flush_interval_seconds == 5

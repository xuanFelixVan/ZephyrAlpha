# [A_test] module_id: SRC-TST-0415 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infrastructure_operations/capacity_assurance/blueprint.md | §test
# [MODULE] tests.test_batch1_infra
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_batch1_infra.py
# [TTL] task_bound

import pytest

mod = pytest.importorskip("zephyr.feedback_loop.capacity_assurance.batch1_infra", reason="batch1_infra not available")
BATCH1_CONTRACTS = mod.BATCH1_CONTRACTS


class TestBatch1ContractCount:
    def test_has_15_contracts(self):
        assert len(BATCH1_CONTRACTS) == 15

    def test_all_values_are_pydantic_models(self):
        from pydantic import BaseModel

        for contract_id, model in BATCH1_CONTRACTS.items():
            assert issubclass(model, BaseModel), f"{contract_id} is not a BaseModel subclass"


class TestCT_SLO_001:
    def test_valid_payload(self):
        model = BATCH1_CONTRACTS["CT-SLO-001"]
        instance = model(slo_id="sli_1", metric="latency", target=0.999, window="5m", severity="critical")
        assert instance.slo_id == "sli_1"
        assert instance.target == 0.999

    def test_missing_required_field(self):
        model = BATCH1_CONTRACTS["CT-SLO-001"]
        with pytest.raises(Exception):
            model(slo_id="sli_1")


class TestCT_SLO_002:
    def test_default_values(self):
        model = BATCH1_CONTRACTS["CT-SLO-002"]
        instance = model()
        assert "1h" in instance.fast_cycle
        assert "24h" in instance.medium_cycle


class TestCT_EB_001:
    def test_valid_payload(self):
        model = BATCH1_CONTRACTS["CT-EB-001"]
        instance = model(slo_id="sli_1", budget_total=100.0, budget_consumed=20.0, budget_remaining=80.0)
        assert instance.burn_rate == 0.0

    def test_with_burn_rate(self):
        model = BATCH1_CONTRACTS["CT-EB-001"]
        instance = model(slo_id="sli_1", budget_total=100.0, budget_consumed=20.0, budget_remaining=80.0, burn_rate=2.5)
        assert instance.burn_rate == 2.5


class TestCT_KS_001:
    def test_default_inactive(self):
        model = BATCH1_CONTRACTS["CT-KS-001"]
        instance = model()
        assert instance.active is False
        assert instance.mode == "normal"


class TestCT_SB_001:
    def test_default_values(self):
        model = BATCH1_CONTRACTS["CT-SB-001"]
        instance = model()
        assert instance.max_memory_mb == 512
        assert instance.allowed_syscalls == []


class TestCT_SC_001:
    def test_valid_payload(self):
        model = BATCH1_CONTRACTS["CT-SC-001"]
        instance = model(cache_key="abc123")
        assert instance.hash_algorithm == "sha256"
        assert instance.ttl_seconds == 3600

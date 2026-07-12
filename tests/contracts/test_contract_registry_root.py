# [A_test] module_id: SRC-TST-0621 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_contract_registry
# [INVARIANTS] contract_id min_length=1; AIReadOnlyHint four-level enum; CONTRACTS dict keyed by contract_id
# [MODIFY-GUARD] source-change-only
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError on empty contract_id; KeyError on missing contract
# [TESTS] test_contract_registry.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.orchestrator.contracts.contract_registry import (
    CONTRACTS,
    AIReadOnlyHint,
    Contract,
    ContractCallResult,
    ContractRegistry,
    TelemetryType,
)


class TestAIReadOnlyHint:
    def test_enum_values(self):
        assert AIReadOnlyHint.DO_NOT_CALL.value == "DO_NOT_CALL"
        assert AIReadOnlyHint.IMPL_REQUIRED.value == "IMPL_REQUIRED"
        assert AIReadOnlyHint.CAUTION_STUB.value == "CAUTION_STUB"
        assert AIReadOnlyHint.SAFE.value == "SAFE"

    def test_enum_count(self):
        assert len(AIReadOnlyHint) == 4

    def test_enum_from_string(self):
        assert AIReadOnlyHint("SAFE") is AIReadOnlyHint.SAFE
        assert AIReadOnlyHint("DO_NOT_CALL") is AIReadOnlyHint.DO_NOT_CALL


class TestTelemetryType:
    def test_enum_values(self):
        assert TelemetryType.RED.value == "RED"
        assert TelemetryType.USE.value == "USE"

    def test_enum_count(self):
        assert len(TelemetryType) == 2


class TestContract:
    def test_create_valid_contract(self):
        c = Contract(
            contract_id="CT-TEST-001",
            producer="TestProducer",
            consumer="TestConsumer",
            status="active",
            ai_read_only_hint=AIReadOnlyHint.SAFE,
        )
        assert c.contract_id == "CT-TEST-001"
        assert c.producer == "TestProducer"
        assert c.consumer == "TestConsumer"
        assert c.status == "active"
        assert c.ai_read_only_hint == AIReadOnlyHint.SAFE

    def test_default_fields(self):
        c = Contract(
            contract_id="CT-TEST-002",
            producer="P",
            consumer="C",
            status="planned",
            ai_read_only_hint=AIReadOnlyHint.DO_NOT_CALL,
        )
        assert c.trigger == ""
        assert c.input_schema == ""
        assert c.output_schema == ""
        assert c.telemetry == TelemetryType.RED
        assert c.telemetry_metrics == []
        assert c.ai_prompt == ""
        assert c.route_target == ""

    def test_empty_contract_id_rejected(self):
        with pytest.raises(Exception):
            Contract(
                contract_id="",
                producer="P",
                consumer="C",
                status="planned",
                ai_read_only_hint=AIReadOnlyHint.SAFE,
            )


class TestContractCallResult:
    def test_create_result(self):
        r = ContractCallResult(
            allowed=True,
            contract_id="CT-TEST-001",
            hint=AIReadOnlyHint.SAFE,
            message="ok",
        )
        assert r.allowed is True
        assert r.contract_id == "CT-TEST-001"
        assert r.hint == AIReadOnlyHint.SAFE
        assert r.message == "ok"

    def test_disallowed_result(self):
        r = ContractCallResult(
            allowed=False,
            contract_id="CT-FAKE",
            hint=AIReadOnlyHint.DO_NOT_CALL,
            message="not found",
        )
        assert r.allowed is False


class TestContractRegistry:
    @pytest.fixture()
    def registry(self):
        return ContractRegistry()

    def test_get_existing_contract(self, registry):
        c = registry.get("CT-ORC-SCRIPT-001")
        assert c is not None
        assert c.contract_id == "CT-ORC-SCRIPT-001"
        assert c.producer == "Orchestrator"
        assert c.consumer == "Script System"

    def test_get_nonexistent_contract(self, registry):
        assert registry.get("CT-NONEXISTENT-999") is None

    def test_list_all(self, registry):
        all_contracts = registry.list_all()
        assert len(all_contracts) == len(CONTRACTS)
        assert all(isinstance(c, Contract) for c in all_contracts)

    def test_list_ids(self, registry):
        ids = registry.list_ids()
        assert len(ids) == len(CONTRACTS)
        assert "CT-ORC-SCRIPT-001" in ids
        assert all(isinstance(i, str) for i in ids)

    def test_check_ai_read_only_safe(self, registry):
        result = registry.check_ai_read_only("CT-CE-VMS-001")
        assert result.allowed is True
        assert result.hint == AIReadOnlyHint.SAFE

    def test_check_ai_read_only_caution_stub(self, registry):
        result = registry.check_ai_read_only("CT-ORC-SCRIPT-001")
        assert result.allowed is True
        assert result.hint == AIReadOnlyHint.CAUTION_STUB

    def test_check_ai_read_only_do_not_call(self, registry):
        result = registry.check_ai_read_only("CT-ORC-CE-001")
        assert result.allowed is False
        assert result.hint == AIReadOnlyHint.DO_NOT_CALL

    def test_check_ai_read_only_impl_required(self, registry):
        result = registry.check_ai_read_only("CT-SCRIPT-KB-001")
        assert result.allowed is False
        assert result.hint == AIReadOnlyHint.IMPL_REQUIRED

    def test_check_ai_read_only_nonexistent(self, registry):
        result = registry.check_ai_read_only("CT-FAKE-999")
        assert result.allowed is False
        assert result.hint == AIReadOnlyHint.DO_NOT_CALL
        assert "不存在" in result.message

    def test_get_by_producer(self, registry):
        orc_contracts = registry.get_by_producer("Orchestrator")
        assert len(orc_contracts) > 0
        assert all(c.producer == "Orchestrator" for c in orc_contracts)

    def test_get_by_producer_empty(self, registry):
        result = registry.get_by_producer("NonexistentProducer")
        assert result == []

    def test_get_by_consumer(self, registry):
        gate_contracts = registry.get_by_consumer("Gate Engine")
        assert len(gate_contracts) > 0
        assert all(c.consumer == "Gate Engine" for c in gate_contracts)

    def test_get_by_consumer_empty(self, registry):
        result = registry.get_by_consumer("NonexistentConsumer")
        assert result == []

    def test_get_route_target_existing(self, registry):
        target = registry.get_route_target("CT-ORC-SCRIPT-001")
        assert target == "script-system"

    def test_get_route_target_nonexistent(self, registry):
        target = registry.get_route_target("CT-FAKE-999")
        assert target == ""

    def test_stats(self, registry):
        s = registry.stats()
        assert s["total_contracts"] == len(CONTRACTS)
        assert s["unique_producers"] > 0
        assert s["unique_consumers"] > 0
        assert "by_hint" in s
        assert "readiness_pct" in s
        assert 0 <= s["readiness_pct"] <= 100

    def test_stats_readiness_calculation(self, registry):
        s = registry.stats()
        total = s["total_contracts"]
        callable_count = sum(
            1 for c in CONTRACTS.values() if c.ai_read_only_hint.name not in ("DO_NOT_CALL", "IMPL_REQUIRED")
        )
        expected_pct = round(callable_count / max(total, 1) * 100, 1)
        assert s["readiness_pct"] == expected_pct

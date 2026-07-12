# [A_test] module_id: SRC-TST-1918 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-537 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.orchestrator.test_orchestrator_core
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound

"""Test suite: orchestrator core — trigger_router routing + contract_registry operations"""

import textwrap
from pathlib import Path

import pytest

from zephyr.orchestrator.contracts.contract_registry import (
    CONTRACTS,
    AIReadOnlyHint,
    Contract,
    ContractCallResult,
    ContractRegistry,
    TelemetryType,
)
from zephyr.orchestrator.execution.trigger_router import (
    TriggerHandlerSpec,
    TriggerRouter,
    TriggerRouterConfigError,
    TriggerSafety,
    load_router_config,
)


@pytest.fixture
def good_yaml(tmp_path: Path) -> Path:
    yaml_path = tmp_path / "trigger_router.yaml"
    yaml_path.write_text(
        textwrap.dedent(
            """\
            version: "1.0.0"
            triggers:
              onboarding:
                handler: "zephyr.trading.orchestrator.trigger_router.handle_onboarding_stub"
                description: "test onboarding"
                safety: "M"
                enabled: true
              drift_detected:
                handler: "zephyr.trading.orchestrator.trigger_router.handle_drift_detected"
                description: "test drift"
                safety: "H"
                enabled: true
              cleanup_due:
                handler: "zephyr.trading.orchestrator.trigger_router.handle_cleanup_stub"
                description: "test cleanup"
                safety: "L"
                enabled: true
              disabled_one:
                handler: "zephyr.trading.orchestrator.trigger_router.handle_cleanup_stub"
                description: "disabled trigger"
                safety: "L"
                enabled: false
              broken_handler:
                handler: "zephyr.trading.orchestrator.nonexistent.module.func"
                description: "import will fail"
                safety: "L"
                enabled: true
            """
        ),
        encoding="utf-8",
        newline="\n",
    )
    return yaml_path


@pytest.fixture
def registry():
    return ContractRegistry()


class TestTriggerRouterRouting:
    def test_dispatch_known_trigger_succeeds(self, good_yaml):
        router = TriggerRouter(config_path=good_yaml)
        result = router.dispatch("onboarding", payload={"agent_id": "A1"})
        assert result.success is True
        assert result.skipped is False
        assert result.trigger_type == "onboarding"

    def test_dispatch_drift_detected(self, good_yaml):
        router = TriggerRouter(config_path=good_yaml)
        result = router.dispatch("drift_detected", payload={"factor": "alpha_001"})
        assert result.success is True
        assert result.handler_result["handler"] == "drift_detected"

    def test_dispatch_cleanup_due(self, good_yaml):
        router = TriggerRouter(config_path=good_yaml)
        result = router.dispatch("cleanup_due", payload={"scope": "snapshots"})
        assert result.success is True

    def test_dispatch_unknown_trigger_skipped(self, good_yaml):
        router = TriggerRouter(config_path=good_yaml)
        result = router.dispatch("never_registered")
        assert result.success is False
        assert result.skipped is True
        assert result.skip_reason == "unknown_trigger_type"

    def test_dispatch_disabled_trigger_skipped(self, good_yaml):
        router = TriggerRouter(config_path=good_yaml)
        result = router.dispatch("disabled_one")
        assert result.success is False
        assert result.skipped is True
        assert result.skip_reason == "disabled"

    def test_dispatch_broken_handler_skipped(self, good_yaml):
        router = TriggerRouter(config_path=good_yaml)
        result = router.dispatch("broken_handler")
        assert result.success is False
        assert result.skipped is True
        assert result.skip_reason == "handler_unresolvable"

    def test_dispatch_handler_exception_caught(self, good_yaml):
        def raises_handler(payload, **_):
            raise RuntimeError("handler boom")

        router = TriggerRouter(config_path=good_yaml, handlers={"onboarding": raises_handler})
        result = router.dispatch("onboarding")
        assert result.success is False
        assert result.skipped is False
        assert "handler boom" in (result.error or "")

    def test_injected_handler_overrides_yaml(self, good_yaml):
        called = {"flag": False}

        def custom_onboarding(payload, **_):
            called["flag"] = True
            return {"custom": True}

        router = TriggerRouter(config_path=good_yaml, handlers={"onboarding": custom_onboarding})
        result = router.dispatch("onboarding")
        assert called["flag"] is True
        assert result.handler_result == {"custom": True}

    def test_injected_handler_unknown_to_yaml(self, good_yaml):
        def my_trigger(payload, **_):
            return "ok"

        router = TriggerRouter(config_path=good_yaml, handlers={"my_custom_trigger": my_trigger})
        result = router.dispatch("my_custom_trigger")
        assert result.success is True
        assert result.handler_result == "ok"

    def test_payload_passed_to_handler(self, good_yaml):
        captured = {}

        def my_handler(payload, **ctx):
            captured["payload"] = payload
            captured["ctx"] = ctx
            return "ok"

        router = TriggerRouter(config_path=good_yaml, handlers={"onboarding": my_handler})
        router.dispatch("onboarding", payload={"key": "value"}, extra_arg="test")
        assert captured["payload"] == {"key": "value"}
        assert captured["ctx"]["extra_arg"] == "test"

    def test_default_payload_empty_dict(self, good_yaml):
        captured = {}

        def my_handler(payload, **_):
            captured["payload"] = payload
            return None

        router = TriggerRouter(config_path=good_yaml, handlers={"onboarding": my_handler})
        router.dispatch("onboarding")
        assert captured["payload"] == {}

    def test_trigger_types_list(self, good_yaml):
        router = TriggerRouter(config_path=good_yaml)
        types = router.trigger_types
        assert "onboarding" in types
        assert "drift_detected" in types
        assert "cleanup_due" in types

    def test_is_registered(self, good_yaml):
        router = TriggerRouter(config_path=good_yaml)
        assert router.is_registered("onboarding") is True
        assert router.is_registered("never_registered") is False

    def test_get_spec(self, good_yaml):
        router = TriggerRouter(config_path=good_yaml)
        spec = router.get_spec("onboarding")
        assert spec is not None
        assert spec.safety == TriggerSafety.M

    def test_get_spec_unknown(self, good_yaml):
        router = TriggerRouter(config_path=good_yaml)
        assert router.get_spec("unknown") is None

    def test_lazy_load_on_dispatch(self, good_yaml):
        router = TriggerRouter(config_path=good_yaml, auto_load=False)
        result = router.dispatch("onboarding")
        assert result.success is True

    def test_reload_picks_up_changes(self, good_yaml):
        router = TriggerRouter(config_path=good_yaml)
        assert "onboarding" in router.trigger_types
        good_yaml.write_text(
            textwrap.dedent(
                """\
                version: "1.0.0"
                triggers:
                  cleanup_due:
                    handler: "zephyr.trading.orchestrator.trigger_router.handle_cleanup_stub"
                    safety: "L"
                    enabled: true
                """
            ),
            encoding="utf-8",
        )
        router.reload()
        assert "onboarding" not in router.trigger_types
        assert "cleanup_due" in router.trigger_types


class TestTriggerRouterConfig:
    def test_load_good_yaml(self, good_yaml):
        specs = load_router_config(good_yaml)
        assert "onboarding" in specs
        assert specs["onboarding"].safety == TriggerSafety.M

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(TriggerRouterConfigError):
            load_router_config(tmp_path / "missing.yaml")

    def test_missing_triggers_key_raises(self, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("version: '1.0.0'\n", encoding="utf-8")
        with pytest.raises(TriggerRouterConfigError):
            load_router_config(bad)

    def test_invalid_spec_raises(self, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text(
            textwrap.dedent(
                """\
                triggers:
                  bad_one:
                    handler: ""
                    safety: "M"
                """
            ),
            encoding="utf-8",
        )
        with pytest.raises(TriggerRouterConfigError):
            load_router_config(bad)

    def test_yaml_missing_with_handlers_falls_back(self, tmp_path):
        def fn(payload, **_):
            return 42

        router = TriggerRouter(
            config_path=tmp_path / "missing.yaml",
            handlers={"x": fn},
        )
        assert router.dispatch("x").handler_result == 42

    def test_yaml_missing_no_handlers_raises(self, tmp_path):
        with pytest.raises(TriggerRouterConfigError):
            TriggerRouter(config_path=tmp_path / "missing.yaml")


class TestTriggerHandlerSpec:
    def test_full_construction(self):
        spec = TriggerHandlerSpec(
            handler="pkg.mod.func",
            description="desc",
            safety=TriggerSafety.H,
            enabled=True,
        )
        assert spec.handler == "pkg.mod.func"
        assert spec.safety == TriggerSafety.H

    def test_defaults(self):
        spec = TriggerHandlerSpec(handler="pkg.mod.func")
        assert spec.safety == TriggerSafety.M
        assert spec.enabled is True
        assert spec.description == ""

    def test_handler_required(self):
        with pytest.raises(Exception):
            TriggerHandlerSpec(handler="")

    def test_extra_field_forbidden(self):
        with pytest.raises(Exception):
            TriggerHandlerSpec(handler="pkg.mod.func", unknown_field="x")

    def test_frozen(self):
        spec = TriggerHandlerSpec(handler="pkg.mod.func")
        with pytest.raises(Exception):
            spec.handler = "tampered"


class TestRouterDispatchResult:
    def test_success_result_fields(self, good_yaml):
        router = TriggerRouter(config_path=good_yaml)
        result = router.dispatch("onboarding")
        assert result.trigger_type == "onboarding"
        assert result.handler_path is not None
        assert result.dispatched_at
        assert result.latency_ms >= 0

    def test_skipped_result_no_handler_result(self, good_yaml):
        router = TriggerRouter(config_path=good_yaml)
        result = router.dispatch("never_registered")
        assert result.handler_result is None
        assert result.handler_path is None


class TestContractRegistryOperations:
    def test_get_existing_contract(self, registry):
        contract = registry.get("CT-ORC-SCRIPT-001")
        assert contract is not None
        assert contract.producer == "Orchestrator"
        assert contract.consumer == "Script System"

    def test_get_nonexistent_contract(self, registry):
        assert registry.get("CT-NONEXISTENT") is None

    def test_list_all(self, registry):
        all_contracts = registry.list_all()
        assert len(all_contracts) > 0
        assert all(isinstance(c, Contract) for c in all_contracts)

    def test_list_ids(self, registry):
        ids = registry.list_ids()
        assert len(ids) > 0
        assert "CT-ORC-SCRIPT-001" in ids

    def test_check_ai_read_only_safe(self, registry):
        result = registry.check_ai_read_only("CT-CE-VMS-001")
        assert isinstance(result, ContractCallResult)
        assert result.allowed is True
        assert result.hint == AIReadOnlyHint.SAFE

    def test_check_ai_read_only_do_not_call(self, registry):
        result = registry.check_ai_read_only("CT-ORC-CE-001")
        assert result.allowed is False
        assert result.hint == AIReadOnlyHint.DO_NOT_CALL

    def test_check_ai_read_only_impl_required(self, registry):
        result = registry.check_ai_read_only("CT-SCRIPT-KB-001")
        assert result.allowed is False
        assert result.hint == AIReadOnlyHint.IMPL_REQUIRED

    def test_check_ai_read_only_caution_stub(self, registry):
        result = registry.check_ai_read_only("CT-ORC-SCRIPT-001")
        assert result.allowed is True
        assert result.hint == AIReadOnlyHint.CAUTION_STUB

    def test_check_ai_read_only_nonexistent(self, registry):
        result = registry.check_ai_read_only("CT-NONEXISTENT")
        assert result.allowed is False
        assert result.hint == AIReadOnlyHint.DO_NOT_CALL

    def test_get_by_producer(self, registry):
        contracts = registry.get_by_producer("Orchestrator")
        assert len(contracts) > 0
        assert all(c.producer == "Orchestrator" for c in contracts)

    def test_get_by_consumer(self, registry):
        contracts = registry.get_by_consumer("Gate Engine")
        assert len(contracts) > 0
        assert all(c.consumer == "Gate Engine" for c in contracts)

    def test_get_route_target(self, registry):
        target = registry.get_route_target("CT-ORC-SCRIPT-001")
        assert target == "script-system"

    def test_get_route_target_nonexistent(self, registry):
        assert registry.get_route_target("CT-NONEXISTENT") == ""

    def test_stats(self, registry):
        stats = registry.stats()
        assert stats["total_contracts"] > 0
        assert stats["unique_producers"] > 0
        assert stats["unique_consumers"] > 0
        assert "by_hint" in stats
        assert "readiness_pct" in stats
        assert 0 <= stats["readiness_pct"] <= 100

    def test_contracts_dict_not_empty(self):
        assert len(CONTRACTS) > 0

    def test_all_contracts_have_valid_hints(self, registry):
        for contract in registry.list_all():
            assert isinstance(contract.ai_read_only_hint, AIReadOnlyHint)


class TestAIReadOnlyHint:
    def test_values(self):
        assert AIReadOnlyHint.DO_NOT_CALL.value == "DO_NOT_CALL"
        assert AIReadOnlyHint.IMPL_REQUIRED.value == "IMPL_REQUIRED"
        assert AIReadOnlyHint.CAUTION_STUB.value == "CAUTION_STUB"
        assert AIReadOnlyHint.SAFE.value == "SAFE"

    def test_count(self):
        assert len(AIReadOnlyHint) == 4


class TestTelemetryType:
    def test_values(self):
        assert TelemetryType.RED.value == "RED"
        assert TelemetryType.USE.value == "USE"

    def test_count(self):
        assert len(TelemetryType) == 2


class TestContractModel:
    def test_contract_creation(self):
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

    def test_contract_default_fields(self):
        c = Contract(
            contract_id="CT-TEST-002",
            producer="P",
            consumer="C",
            status="active",
            ai_read_only_hint=AIReadOnlyHint.SAFE,
        )
        assert c.trigger == ""
        assert c.input_schema == ""
        assert c.output_schema == ""
        assert c.telemetry == TelemetryType.RED
        assert c.telemetry_metrics == []
        assert c.ai_prompt == ""
        assert c.route_target == ""

# [A_test] module_id: SRC-TST-1341 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_orchestrator_trigger_router
# [INVARIANTS] TriggerRouter uses injected handlers for testing; no YAML dependency in tests
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_orchestrator_trigger_router.py
# [TTL] task_bound

from __future__ import annotations

import pytest
import yaml

from zephyr.orchestrator.execution.trigger_router import (
    PHASE1D_TRIGGER_TYPES,
    RouterDispatchResult,
    TriggerHandlerSpec,
    TriggerRouter,
    TriggerRouterConfigError,
    TriggerSafety,
    get_trigger_router,
    load_router_config,
    reset_trigger_router,
)


class TestTriggerSafety:
    def test_values(self):
        assert TriggerSafety.L.value == "L"
        assert TriggerSafety.M.value == "M"
        assert TriggerSafety.H.value == "H"


class TestTriggerHandlerSpec:
    def test_minimal_creation(self):
        spec = TriggerHandlerSpec(handler="pkg.mod.func")
        assert spec.handler == "pkg.mod.func"
        assert spec.enabled is True
        assert spec.safety == TriggerSafety.M
        assert spec.priority == 0

    def test_full_creation(self):
        spec = TriggerHandlerSpec(
            handler="pkg.mod.func",
            description="test handler",
            safety=TriggerSafety.H,
            enabled=False,
            priority=5,
            required=True,
            retry=True,
            notes="test notes",
        )
        assert spec.safety == TriggerSafety.H
        assert spec.enabled is False
        assert spec.required is True

    def test_empty_handler_raises(self):
        with pytest.raises(Exception):
            TriggerHandlerSpec(handler="")


class TestRouterDispatchResult:
    def test_defaults(self):
        r = RouterDispatchResult(trigger_type="test")
        assert r.trigger_type == "test"
        assert r.success is False
        assert r.skipped is False
        assert r.handler_path is None
        assert r.error is None


class TestTriggerRouterWithInjectedHandlers:
    @pytest.fixture
    def handlers(self):
        return {
            "onboarding": lambda payload, **kw: {"status": "ok"},
            "drift_detected": lambda payload, **kw: {"recovery": "started"},
        }

    @pytest.fixture
    def router(self, handlers):
        return TriggerRouter(handlers=handlers, auto_load=True)

    def test_dispatch_known_trigger(self, router):
        result = router.dispatch("onboarding", {"key": "val"})
        assert result.success is True
        assert result.skipped is False
        assert result.handler_result == {"status": "ok"}

    def test_dispatch_unknown_trigger(self, router):
        result = router.dispatch("nonexistent_trigger", {})
        assert result.success is False
        assert result.skipped is True
        assert result.skip_reason == "unknown_trigger_type"

    def test_dispatch_disabled_trigger(self, handlers):
        handlers["disabled_type"] = lambda p, **kw: None
        router = TriggerRouter(handlers=handlers, auto_load=True)
        spec = router.get_spec("disabled_type")
        disabled_spec = TriggerHandlerSpec(
            handler=spec.handler,
            description=spec.description,
            safety=spec.safety,
            enabled=False,
        )
        router._specs["disabled_type"] = disabled_spec
        result = router.dispatch("disabled_type", {})
        assert result.success is False
        assert result.skipped is True
        assert result.skip_reason == "disabled"

    def test_trigger_types_property(self, router):
        types = router.trigger_types
        assert "onboarding" in types
        assert "drift_detected" in types

    def test_get_spec_existing(self, router):
        spec = router.get_spec("onboarding")
        assert spec is not None

    def test_get_spec_nonexistent(self, router):
        spec = router.get_spec("nonexistent")
        assert spec is None

    def test_is_registered(self, router):
        assert router.is_registered("onboarding") is True
        assert router.is_registered("nonexistent") is False


class TestTriggerRouterHandlerException:
    def test_handler_exception_caught(self):
        def bad_handler(payload, **kw):
            raise RuntimeError("handler crashed")

        router = TriggerRouter(handlers={"crash_type": bad_handler}, auto_load=True)
        result = router.dispatch("crash_type", {})
        assert result.success is False
        assert result.skipped is False
        assert result.error is not None
        assert "RuntimeError" in result.error


class TestTriggerRouterReload:
    def test_reload_refreshes(self):
        router = TriggerRouter(
            handlers={"test_type": lambda p, **kw: {"v": 1}},
            auto_load=True,
        )
        result1 = router.dispatch("test_type", {})
        assert result1.success is True
        router._injected_handlers["test_type"] = lambda p, **kw: {"v": 2}
        router.reload()
        result2 = router.dispatch("test_type", {})
        assert result2.handler_result == {"v": 2}


class TestLoadRouterConfig:
    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(TriggerRouterConfigError, match="not found"):
            load_router_config(tmp_path / "nonexistent.yaml")

    def test_valid_yaml(self, tmp_path):
        config = {
            "triggers": {
                "test_trigger": {
                    "handler": "zephyr.some_module.some_func",
                    "description": "test",
                    "safety": "L",
                }
            }
        }
        yaml_path = tmp_path / "trigger_router.yaml"
        yaml_path.write_text(yaml.dump(config), encoding="utf-8")
        specs = load_router_config(yaml_path)
        assert "test_trigger" in specs
        assert specs["test_trigger"].handler == "zephyr.some_module.some_func"

    def test_missing_triggers_key_raises(self, tmp_path):
        yaml_path = tmp_path / "trigger_router.yaml"
        yaml_path.write_text("other_key: {}\n", encoding="utf-8")
        with pytest.raises(TriggerRouterConfigError, match="triggers"):
            load_router_config(yaml_path)

    def test_invalid_trigger_spec_raises(self, tmp_path):
        config = {
            "triggers": {
                "bad_trigger": {
                    "handler": "",
                }
            }
        }
        yaml_path = tmp_path / "trigger_router.yaml"
        yaml_path.write_text(yaml.dump(config), encoding="utf-8")
        with pytest.raises(TriggerRouterConfigError, match="规格非法"):
            load_router_config(yaml_path)


class TestPhase1DTriggerTypes:
    def test_contains_expected_types(self):
        assert "onboarding" in PHASE1D_TRIGGER_TYPES
        assert "drift_detected" in PHASE1D_TRIGGER_TYPES
        assert "compression_needed" in PHASE1D_TRIGGER_TYPES
        assert "cleanup_due" in PHASE1D_TRIGGER_TYPES
        assert "blueprint_published" in PHASE1D_TRIGGER_TYPES

    def test_is_frozenset(self):
        assert isinstance(PHASE1D_TRIGGER_TYPES, frozenset)


class TestGetTriggerRouter:
    def teardown_method(self):
        reset_trigger_router()

    def test_get_trigger_router_returns_instance(self):
        router = get_trigger_router(handlers={"test": lambda p, **kw: None})
        assert isinstance(router, TriggerRouter)

    def test_get_trigger_router_singleton(self):
        r1 = get_trigger_router(handlers={"test": lambda p, **kw: None})
        r2 = get_trigger_router()
        assert r1 is r2

    def test_reset_creates_new_instance(self):
        r1 = get_trigger_router(handlers={"test": lambda p, **kw: None})
        reset_trigger_router()
        r2 = get_trigger_router(handlers={"test2": lambda p, **kw: None})
        assert r1 is not r2

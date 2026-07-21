# [A_test] module_id: MOD-GOV_atomic_injector | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §
# [MODULE] tests.test_atomic_injector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_atomic_injector.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.autonomy_core.context.atomic_injector import AtomicInjector, AtomicResult


class TestAtomicResult:
    def test_default_rolled_back_is_false(self):
        r = AtomicResult(success=True, full_context_applied=True)
        assert r.rolled_back is False

    def test_fields_assigned_correctly(self):
        r = AtomicResult(success=False, full_context_applied=False, rolled_back=True)
        assert r.success is False
        assert r.full_context_applied is False
        assert r.rolled_back is True


class TestAtomicInjectorInstantiation:
    def test_can_injector_be_created(self):
        injector = AtomicInjector()
        assert injector is not None

    def test_injector_has_inject_atomic_method(self):
        injector = AtomicInjector()
        assert callable(getattr(injector, "inject_atomic", None))


class TestAtomicInjectorInjectAtomic:
    def test_all_layers_valid_returns_success(self):
        injector = AtomicInjector()
        layers = {"layer1": "a", "layer2": "b", "layer3": "c", "layer4": "d"}
        result = injector.inject_atomic(layers)
        assert result.success is True
        assert result.full_context_applied is True
        assert result.rolled_back is False

    def test_one_empty_layer_triggers_rollback(self):
        injector = AtomicInjector()
        layers = {"layer1": "a", "layer2": "", "layer3": "c", "layer4": "d"}
        result = injector.inject_atomic(layers)
        assert result.success is False
        assert result.full_context_applied is False
        assert result.rolled_back is True

    def test_all_empty_layers_triggers_rollback(self):
        injector = AtomicInjector()
        layers = {"l1": "", "l2": "", "l3": "", "l4": ""}
        result = injector.inject_atomic(layers)
        assert result.success is False
        assert result.rolled_back is True

    def test_empty_dict_returns_success(self):
        injector = AtomicInjector()
        result = injector.inject_atomic({})
        assert result.success is True
        assert result.full_context_applied is True

    def test_returns_atomic_result_type(self):
        injector = AtomicInjector()
        result = injector.inject_atomic({"k": "v"})
        assert isinstance(result, AtomicResult)

    def test_whitespace_only_value_is_truthy(self):
        injector = AtomicInjector()
        layers = {"layer1": "   ", "layer2": "b"}
        result = injector.inject_atomic(layers)
        assert result.success is True
        assert result.full_context_applied is True

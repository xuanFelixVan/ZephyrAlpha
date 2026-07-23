# [A_test] module_id: MOD-GOV_assembly_context_injector | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_cross_layer/context_engine/blueprint.md | §tests
# [MODULE] zephyr.autonomy_core.context.context_injector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

import sys

sys.path.insert(0, "src")

import pytest

try:
    from zephyr.autonomy_core.context.context_injector import (
        ContextInjector,
        InjectedContext,
        RetrievalMode,
    )
except Exception as _exc:
    pytest.skip(f"cannot import context_injector: {_exc}", allow_module_level=True)


class TestContextInjectorInjectByTaskId:
    def test_inject_by_task_id_returns_injected_context(self):
        # KB system retired 2026-07; inject_by_* return empty InjectedContext
        # (production retrieval handled out-of-band by the context pipeline).
        inj = ContextInjector(token_budget=8000)
        result = inj.inject_by_task_id("T-001")
        assert isinstance(result, InjectedContext)
        assert result.retrieval_mode == "task_id"
        assert result.context == ""
        assert result.token_count == 0

    def test_inject_by_task_id_no_matches(self):
        inj = ContextInjector()
        result = inj.inject_by_task_id("T-999")
        assert result.token_count == 0
        assert result.context == ""


class TestContextInjectorInjectByModuleId:
    def test_inject_by_module_id_returns_injected_context(self):
        inj = ContextInjector(token_budget=8000)
        result = inj.inject_by_module_id("MOD-CONTEXT_ENGINE")
        assert isinstance(result, InjectedContext)
        assert result.retrieval_mode == "module_id"
        assert result.context == ""
        assert result.token_count == 0

    def test_inject_by_module_id_no_matches(self):
        inj = ContextInjector()
        result = inj.inject_by_module_id("MOD-XXX")
        assert result.token_count == 0
        assert result.context == ""


class TestContextInjectorProperties:
    def test_token_budget_property(self):
        inj = ContextInjector(token_budget=5000)
        assert inj.token_budget == 5000

    def test_max_sources_property(self):
        inj = ContextInjector(max_sources=5)
        assert inj.max_sources == 5


class TestRetrievalMode:
    def test_retrieval_modes(self):
        assert RetrievalMode.TASK_ID.value == "task_id"
        assert RetrievalMode.MODULE_ID.value == "module_id"
        assert RetrievalMode.KEYWORD.value == "keyword"

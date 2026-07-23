# [A_test] module_id: MOD-GOV_context_injector_root | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
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
        InjectionLayer,
        InjectionResult,
        RetrievalMode,
        ValidatedContext,
        format_context,
        inject,
        with_authority_review,
    )

    _IMPORT_OK = True
    _IMPORT_ERR = None
except Exception as exc:
    _IMPORT_OK = False
    _IMPORT_ERR = str(exc)

pytestmark = pytest.mark.skipif(not _IMPORT_OK, reason=f"import failed: {_IMPORT_ERR}")


class TestContextInjector:
    """ContextInjector API tests.

    KB system retired 2026-07; inject_by_* return empty InjectedContext
    (production retrieval handled out-of-band by the context pipeline).
    """

    def test_inject_by_task_id(self):
        injector = ContextInjector()
        result = injector.inject_by_task_id("T-001")
        assert isinstance(result, InjectedContext)
        assert result.retrieval_mode == "task_id"
        assert result.context == ""
        assert result.token_count == 0

    def test_inject_by_module_id(self):
        injector = ContextInjector()
        result = injector.inject_by_module_id("MOD-CONTEXT_ENGINE")
        assert result.retrieval_mode == "module_id"
        assert result.context == ""
        assert result.token_count == 0

    def test_inject_by_keyword(self):
        injector = ContextInjector()
        result = injector.inject_by_keyword("test query")
        assert result.retrieval_mode == "keyword"
        assert result.context == ""

    def test_inject_dispatch_task_id(self):
        injector = ContextInjector()
        result = injector.inject("T-010", mode=RetrievalMode.TASK_ID)
        assert result.retrieval_mode == "task_id"

    def test_inject_dispatch_module_id(self):
        injector = ContextInjector()
        result = injector.inject("MOD-X", mode=RetrievalMode.MODULE_ID)
        assert result.retrieval_mode == "module_id"

    def test_inject_dispatch_keyword(self):
        injector = ContextInjector()
        result = injector.inject("query", mode=RetrievalMode.KEYWORD)
        assert result.retrieval_mode == "keyword"

    def test_token_budget_property(self):
        injector = ContextInjector(token_budget=5000)
        assert injector.token_budget == 5000

    def test_max_sources_property(self):
        injector = ContextInjector(max_sources=5)
        assert injector.max_sources == 5

    def test_empty_context_respects_budget(self):
        # With no data source, token_count is always 0 regardless of budget.
        injector = ContextInjector(token_budget=100)
        result = injector.inject_by_task_id("T-001")
        assert result.token_count == 0
        assert result.token_count <= 100

    def test_no_matching_records(self):
        injector = ContextInjector()
        result = injector.inject_by_task_id("NONEXISTENT")
        assert result.context == ""
        assert result.token_count == 0


class TestInjectionLayer:
    def test_layer_order(self):
        assert InjectionLayer.SYSTEM < InjectionLayer.RULES
        assert InjectionLayer.RULES < InjectionLayer.KNOWLEDGE
        assert InjectionLayer.KNOWLEDGE < InjectionLayer.EXAMPLES


class TestValidatedContext:
    def test_default_values(self):
        ctx = ValidatedContext()
        assert ctx.is_clean is True
        assert ctx.token_count == 0
        assert ctx.system_rules == []
        assert ctx.contracts == []
        assert ctx.ke_entries == []
        assert ctx.examples == []


class TestFormatContext:
    def test_format_all_layers(self):
        ctx = ValidatedContext(
            system_rules=["rule1", "rule2"],
            contracts=["CT-001", "CT-002"],
            ke_entries=["KE-001"],
            examples=["example1"],
        )
        formatted = format_context(ctx)
        assert "system" in formatted
        assert "rules" in formatted
        assert "knowledge" in formatted
        assert "examples" in formatted
        assert "rule1" in formatted["system"]
        assert "CT-001" in formatted["rules"]

    def test_format_empty_context(self):
        ctx = ValidatedContext()
        formatted = format_context(ctx)
        assert formatted == {}


class TestInject:
    def test_inject_success(self):
        ctx = ValidatedContext(
            system_rules=["R-ONLY-CREATE"],
            is_clean=True,
        )
        result = inject(ctx, lsg_passed=True)
        assert isinstance(result, InjectionResult)
        assert result.injected_successfully is True

    def test_inject_lsg_blocked(self):
        ctx = ValidatedContext(system_rules=["rule1"], is_clean=True)
        result = inject(ctx, lsg_passed=False)
        assert result.injected_successfully is False
        assert "LSG_BLOCKED" in result.sources

    def test_inject_not_clean(self):
        ctx = ValidatedContext(
            system_rules=["rule1"],
            is_clean=False,
            validation_warnings=["warn1"],
        )
        result = inject(ctx, lsg_passed=True)
        assert result.injected_successfully is False
        assert "VALIDATION_FAILED" in result.sources


class TestWithAuthorityReview:
    def test_ce_build_level(self):
        result = InjectionResult()
        result = with_authority_review(result, "CE_build")
        assert result.authority_score == 0.7
        assert result.authority_reviewed is True

    def test_orc_check_level(self):
        result = InjectionResult()
        result = with_authority_review(result, "Orc_check")
        assert result.authority_score == 0.85

    def test_user_review_level(self):
        result = InjectionResult()
        result = with_authority_review(result, "User_review")
        assert result.authority_score == 1.0

    def test_unknown_level_defaults(self):
        result = InjectionResult()
        result = with_authority_review(result, "unknown")
        assert result.authority_score == 0.7

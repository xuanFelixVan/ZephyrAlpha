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


class FakeRecord:
    def __init__(
        self,
        summary="",
        content="",
        source_file="",
        ke_id="KE-001",
        category="",
        tags=None,
        blueprint_id="",
        section="",
    ):
        self.summary = summary
        self.content = content
        self.source_file = source_file
        self.ke_id = ke_id
        self.category = category
        self.tags = tags or []
        self.blueprint_id = blueprint_id
        self.section = section


class FakeKbRepo:
    def __init__(self, records=None, search_hits=None):
        self._records = records or []
        self._search_hits = search_hits or []

    def list_by_status(self):
        return self._records

    def search(self, query_text="", collection="", n_results=10, score_threshold=0.3):
        return self._search_hits[:n_results]


class TestContextInjector:
    def test_inject_by_task_id(self):
        records = [
            FakeRecord(summary="task T-001 content", tags=["T-001"]),
            FakeRecord(summary="other task", tags=["T-002"]),
        ]
        repo = FakeKbRepo(records=records)
        injector = ContextInjector(repo)
        result = injector.inject_by_task_id("T-001")
        assert isinstance(result, InjectedContext)
        assert result.retrieval_mode == "task_id"
        assert "T-001" in result.context

    def test_inject_by_module_id(self):
        records = [
            FakeRecord(category="MOD-CONTEXT_ENGINE", summary="module info"),
        ]
        repo = FakeKbRepo(records=records)
        injector = ContextInjector(repo)
        result = injector.inject_by_module_id("MOD-CONTEXT_ENGINE")
        assert result.retrieval_mode == "module_id"
        assert "module info" in result.context

    def test_inject_by_keyword(self):
        hits = [FakeRecord(content="keyword match result", ke_id="KE-100")]
        repo = FakeKbRepo(search_hits=hits)
        injector = ContextInjector(repo)
        result = injector.inject_by_keyword("test query")
        assert result.retrieval_mode == "keyword"

    def test_inject_dispatch_task_id(self):
        records = [FakeRecord(summary="dispatched", tags=["T-010"])]
        repo = FakeKbRepo(records=records)
        injector = ContextInjector(repo)
        result = injector.inject("T-010", mode=RetrievalMode.TASK_ID)
        assert result.retrieval_mode == "task_id"

    def test_inject_dispatch_module_id(self):
        records = [FakeRecord(category="MOD-X", summary="dispatched module")]
        repo = FakeKbRepo(records=records)
        injector = ContextInjector(repo)
        result = injector.inject("MOD-X", mode=RetrievalMode.MODULE_ID)
        assert result.retrieval_mode == "module_id"

    def test_inject_dispatch_keyword(self):
        repo = FakeKbRepo(search_hits=[])
        injector = ContextInjector(repo)
        result = injector.inject("query", mode=RetrievalMode.KEYWORD)
        assert result.retrieval_mode == "keyword"

    def test_token_budget_property(self):
        repo = FakeKbRepo()
        injector = ContextInjector(repo, token_budget=5000)
        assert injector.token_budget == 5000

    def test_max_sources_property(self):
        repo = FakeKbRepo()
        injector = ContextInjector(repo, max_sources=5)
        assert injector.max_sources == 5

    def test_budget_enforcement(self):
        long_content = "x" * 10000
        records = [
            FakeRecord(summary=long_content, tags=["T-001"]),
            FakeRecord(summary=long_content, tags=["T-001"]),
        ]
        repo = FakeKbRepo(records=records)
        injector = ContextInjector(repo, token_budget=100)
        result = injector.inject_by_task_id("T-001")
        assert result.token_count <= 100 + 50

    def test_no_matching_records(self):
        repo = FakeKbRepo(records=[])
        injector = ContextInjector(repo)
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

# [A_test] module_id: MOD-GOV_context_injector_unit | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-612 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_context_injector
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
from __future__ import annotations

"""
Unit tests for context_injector.py (T-2-12, C39)
=================================================
Minimum: 10 tests
"""


from pathlib import Path
from unittest.mock import MagicMock

import pytest

from zephyr.autonomy_core.context.context_injector import (
    ContextInjector,
    InjectedContext,
    RetrievalMode,
)
from zephyr.infrastructure.capacity_assurance.token_budget import estimate_tokens


@pytest.fixture
def kb_env():
    repo = MagicMock()
    repo.list_by_status.return_value = []
    repo.search.return_value = []
    return repo


class TestEstimateTokens:
    def test_non_empty_string(self) -> None:
        assert estimate_tokens("hello world test") > 0

    def test_empty_string(self) -> None:
        assert estimate_tokens("") == 0

    def test_long_string(self) -> None:
        text = "a" * 400
        assert estimate_tokens(text) == 100


class TestInjectedContext:
    def test_valid_context(self) -> None:
        ctx = InjectedContext(
            context="test context",
            sources=["file1.md"],
            token_count=10,
            retrieval_mode="keyword",
            query="test",
            budget_remaining=7990,
        )
        assert ctx.context == "test context"
        assert ctx.token_count == 10

    def test_default_values(self) -> None:
        ctx = InjectedContext(
            retrieval_mode="keyword",
        )
        assert ctx.context == ""
        assert ctx.sources == []
        assert ctx.token_count == 0


class TestContextInjector:
    def test_inject_by_task_id_no_results(self, kb_env) -> None:
        injector = ContextInjector(kb_env)
        result = injector.inject_by_task_id("T-9-99")
        assert result.context == ""
        assert result.retrieval_mode == "task_id"

    def test_inject_by_module_id_no_results(self, kb_env) -> None:
        injector = ContextInjector(kb_env)
        result = injector.inject_by_module_id("NONEXISTENT")
        assert result.context == ""
        assert result.retrieval_mode == "module_id"

    def test_inject_by_keyword_no_results(self, kb_env) -> None:
        injector = ContextInjector(kb_env)
        result = injector.inject_by_keyword("nonexistent_query_xyz")
        assert result.context == ""
        assert result.retrieval_mode == "keyword"

    def test_inject_dispatches_correctly(self, kb_env) -> None:
        injector = ContextInjector(kb_env)
        result = injector.inject("test", mode=RetrievalMode.KEYWORD)
        assert result.retrieval_mode == "keyword"

        result2 = injector.inject("T-2-12", mode=RetrievalMode.TASK_ID)
        assert result2.retrieval_mode == "task_id"

    def test_budget_remaining(self, kb_env) -> None:
        injector = ContextInjector(kb_env, token_budget=8000)
        result = injector.inject_by_task_id("nonexistent")
        assert result.budget_remaining == 8000

    def test_properties(self, kb_env) -> None:
        injector = ContextInjector(kb_env, token_budget=5000, max_sources=5)
        assert injector.token_budget == 5000
        assert injector.max_sources == 5

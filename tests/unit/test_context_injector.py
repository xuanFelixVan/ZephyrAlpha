"""
Unit tests for context_injector.py (T-2-12, C39)
=================================================
Minimum: 10 tests
"""

from __future__ import annotations

from pathlib import Path

import pytest
from zephyr.context_engine.context_injector import (
    ContextInjector,
    InjectedContext,
    RetrievalMode,
)
from zephyr.db.sqlite_schema import init_db
from zephyr.kb.chromadb_init import init_chromadb
from zephyr.kb.kb_repo import KbRepo
from zephyr.shared.token_utils import estimate_tokens


@pytest.fixture
def kb_env(tmp_path: Path):
    db = tmp_path / "test.db"
    vec = tmp_path / "vectors"
    init_db(db)
    init_chromadb(vec)
    repo = KbRepo(db_path=db, vector_dir=vec)
    yield repo
    import zephyr.kb.chromadb_init as mod

    mod._chroma_client = None


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
    def test_inject_by_task_id_no_results(self, kb_env: KbRepo) -> None:
        injector = ContextInjector(kb_env)
        result = injector.inject_by_task_id("T-9-99")
        assert result.context == ""
        assert result.retrieval_mode == "task_id"

    def test_inject_by_module_id_no_results(self, kb_env: KbRepo) -> None:
        injector = ContextInjector(kb_env)
        result = injector.inject_by_module_id("NONEXISTENT")
        assert result.context == ""
        assert result.retrieval_mode == "module_id"

    def test_inject_by_keyword_no_results(self, kb_env: KbRepo) -> None:
        injector = ContextInjector(kb_env)
        result = injector.inject_by_keyword("nonexistent_query_xyz")
        assert result.context == ""
        assert result.retrieval_mode == "keyword"

    def test_inject_by_task_id_with_matching_record(self, kb_env: KbRepo) -> None:
        kb_env.create(
            ke_id="KE-100",
            title="Test KE",
            category="test",
            source_file="test.md",
            content="test content",
            tags=["T-2-12"],
        )
        injector = ContextInjector(kb_env)
        result = injector.inject_by_task_id("T-2-12")
        assert len(result.sources) > 0

    def test_inject_by_module_id_with_matching_record(self, kb_env: KbRepo) -> None:
        kb_env.create(
            ke_id="KE-200",
            title="Module KE",
            category="architecture",
            source_file="arch.md",
            content="architecture content",
        )
        injector = ContextInjector(kb_env)
        result = injector.inject_by_module_id("architecture")
        assert len(result.sources) > 0

    def test_token_budget_respected(self, kb_env: KbRepo) -> None:
        for i in range(20):
            kb_env.create(
                ke_id=f"KE-{300+i:03d}",
                title=f"KE {i}",
                category="test",
                source_file=f"file{i}.md",
                content="x" * 1000,
                tags=["T-2-12"],
            )
        injector = ContextInjector(kb_env, token_budget=100)
        result = injector.inject_by_task_id("T-2-12")
        assert result.token_count <= 100

    def test_max_sources_limit(self, kb_env: KbRepo) -> None:
        for i in range(20):
            kb_env.create(
                ke_id=f"KE-{400+i:03d}",
                title=f"KE {i}",
                category="test",
                source_file=f"file{i}.md",
                content="content",
                tags=["T-2-12"],
            )
        injector = ContextInjector(kb_env, max_sources=3)
        result = injector.inject_by_task_id("T-2-12")
        assert len(result.sources) <= 3

    def test_inject_dispatches_correctly(self, kb_env: KbRepo) -> None:
        injector = ContextInjector(kb_env)
        result = injector.inject("test", mode=RetrievalMode.KEYWORD)
        assert result.retrieval_mode == "keyword"

        result2 = injector.inject("T-2-12", mode=RetrievalMode.TASK_ID)
        assert result2.retrieval_mode == "task_id"

    def test_budget_remaining(self, kb_env: KbRepo) -> None:
        injector = ContextInjector(kb_env, token_budget=8000)
        result = injector.inject_by_task_id("nonexistent")
        assert result.budget_remaining == 8000

    def test_properties(self, kb_env: KbRepo) -> None:
        injector = ContextInjector(kb_env, token_budget=5000, max_sources=5)
        assert injector.token_budget == 5000
        assert injector.max_sources == 5

# [A_test] module_id: SRC-TST-0112 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-270 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.e2e.test_kb_full_pipeline
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
E2E 全链路测试 — knowledge-base v0.10.1 闭环管线
=====================================================
蓝图：§12.5 E2E 集成测试 + §4.5 冷启动验证

测试覆盖：
1. bootstrap 冷启动（少量 mock 文档）
2. G1→G5 管道逐级注入
3. recall/search 端到端召回
4. 知识注入→检索→验证闭环
5. Reranker fallback 集成
6. MVKB 最小验证门禁
"""

from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

from zephyr.gov_kb.ingest import IngestGate
from zephyr.gov_kb.bootstrap import (
    Bootstrap,
    BootstrapConfig,
    BootstrapResult,
    classify_category,
    classify_chunk,
    discover_document_sources,
    run_bootstrap,
    segment_document,
)
from zephyr.intelligence.model_evaluation.reranker import RerankedHit, Reranker, rerank_batch
from zephyr.intelligence.model_evaluation.unified_memory_api import (
    InMemoryMemoryBackend,
    UnifiedMemoryAPI,
    build_provenance,
)


class TestBootstrapColdStart:
    def test_discover_sources_finds_docs(self, tmp_path: Path):
        (tmp_path / "AGENTS.md").write_text(
            "# Agent Rules\n\n- Rule 1: Always search first\n- Rule 2: Never skip tests\n", encoding="utf-8"
        )
        (tmp_path / "docs").mkdir(exist_ok=True)
        (tmp_path / "docs" / "ADR").mkdir(exist_ok=True)
        (tmp_path / "docs" / "ADR" / "adr-0001.md").write_text(
            "---\ntitle: test\n---\n\n# ADR-0001\n\nDecision: Use ChromaDB\n", encoding="utf-8"
        )
        (tmp_path / "docs" / "03_modules").mkdir(parents=True, exist_ok=True)
        (tmp_path / "docs" / "03_modules" / "_system_master").mkdir(exist_ok=True)
        (tmp_path / "docs" / "03_modules" / "_system_master" / "blueprint.md").write_text(
            "---\ntitle: blueprint\n---\n\n## System Architecture\n\nThe system uses a 3-tier pyramid model.\n",
            encoding="utf-8",
        )

        sources = discover_document_sources(tmp_path)

        source_paths = [str(s.relative_to(tmp_path)) for s in sources]
        assert any("AGENTS.md" in p for p in source_paths)
        assert any("adr" in p.lower() for p in source_paths)
        assert any("blueprint" in p.lower() for p in source_paths)

    def test_segment_document_by_headings(self, tmp_path: Path):
        doc = tmp_path / "test.md"
        doc.write_text(
            "---\nmodule_id: KE-TEST-001\ntitle: Test Doc\ncategory: adr_decision\n---\n\n"
            "# Decision 1\n\nThis is the first decision with enough content to be meaningful. "
            "It describes an architectural choice that has significant impact on the system design.\n\n"
            "## Decision 2\n\nThis is the second decision. It covers testing strategy across modules.\n",
            encoding="utf-8",
        )

        chunks = segment_document(doc, min_chunk_chars=20)

        assert len(chunks) >= 1
        for c in chunks:
            assert len(c.content) >= 20
            assert c.heading
            assert c.fingerprint

    def test_classify_category_from_path(self):
        assert "adr_decision" in classify_category(Path("docs/ADR/adr-0001.md"))
        assert "module_blueprint" in classify_category(Path("docs/03_modules/foo/blueprint.md"))
        assert "governance_rule" in classify_category(Path(".trae/rules/project_rules.md"))
        assert "session_log" in classify_category(Path("session_logs/2026/05/session-001.yaml"))
        assert "agent_instruction" in classify_category(Path("AGENTS.md"))
        assert "documentation" in classify_category(Path("README.md"))

    def test_classify_chunk_content(self):
        assert classify_chunk("This ADR describes the decision to use ChromaDB.") == "adr_decision"
        assert classify_chunk("The architecture follows a 3-tier design.") == "architecture"
        assert classify_chunk("Rule: always check locks before writing.") == "governance_rule"
        assert classify_chunk("Run pytest to verify test coverage.") == "test_coverage"
        assert classify_chunk("Hello world.") == "general"

    def test_bootstrap_minimal_project(self, tmp_path: Path):
        (tmp_path / "AGENTS.md").write_text(
            "# Agent Rules\n\n- Rule 1: Always search knowledge base before creating new code\n"
            "- Rule 2: Write knowledge entries after completing tasks\n"
            "These rules ensure knowledge continuity across AI sessions.\n",
            encoding="utf-8",
        )
        (tmp_path / "docs").mkdir(exist_ok=True)
        (tmp_path / "docs" / "ADR").mkdir(exist_ok=True)
        (tmp_path / "docs" / "ADR" / "adr-0055.md").write_text(
            "---\nmodule_id: ADR-0055\ntitle: KB Index Design\ncategory: adr_decision\n---\n\n"
            "# ADR-0055: Knowledge Base Index\n\n"
            "Decision: Use dual-assignment approach for KB indexing.\n"
            "This ensures both structured and unstructured knowledge can coexist.\n",
            encoding="utf-8",
        )
        (tmp_path / "data").mkdir(exist_ok=True)

        config = BootstrapConfig(min_ke_count=2, min_categories=2)
        kb = UnifiedMemoryAPI(backend=InMemoryMemoryBackend(), enforce_capability=False)

        engine = Bootstrap(project_root=tmp_path, config=config, kb_api=kb)
        result = engine.run()

        assert result.total_sources_scanned >= 1
        assert result.total_chunks_extracted >= 1
        assert result.total_activated >= 1
        assert len(result.categories_found) >= 1


class TestPipelineE2E:
    def test_ingest_to_recall_loop(self, tmp_path: Path):
        import os
        import tempfile as tmp

        fd, tpath = tmp.mkstemp(suffix=".md", prefix="e2e_")
        os.close(fd)
        doc = Path(tpath)
        doc.write_text(
            "---\nmodule_id: KE-E2E-001\ntitle: E2E Test Entry\ncategory: test_coverage\n---\n\n"
            "# E2E Test Entry\n\n"
            "This test entry validates the full pipeline from ingest through recall.\n"
            "It covers G1 format validation and content length checks.\n"
            "The system should be able to ingest this document and later recall it.\n",
            encoding="utf-8",
            newline="\n",
        )

        kb_root = tmp_path / "knowledge_base"
        kb_root.mkdir(exist_ok=True)
        kb = UnifiedMemoryAPI(backend=InMemoryMemoryBackend(), enforce_capability=False)

        gate = IngestGate(kb_root=kb_root)
        result = gate.ingest(doc)

        assert result.passed, f"G1 failed: {result.violations}"
        assert result.ke_id == "KE-E2E-001"

        prov = build_provenance(origin="e2e:test", audit_chain=["test_pipeline_e2e"])
        chunk_id = kb.write(
            topic="kb::test_coverage::KE-E2E-001",
            content="E2E Test Entry: This test entry validates the full pipeline from ingest through recall.",
            provenance=prov,
        )
        assert chunk_id

        records = kb.recall(topic="kb::test_coverage::KE-E2E-001", k=5)
        assert len(records) >= 1
        assert any("E2E Test Entry" in r.content for r in records)

        hits = kb.search(query="pipeline ingest recall", k=3)
        assert len(hits) >= 1

        doc.unlink(missing_ok=True)


class TestRerankerIntegration:
    def test_reranker_fallback_no_model(self):
        rk = Reranker(top_k=3)
        docs = ["Document A about architecture", "Document B about tests", "Document C about rules"]
        hits = rk.rerank("architecture", docs)

        assert len(hits) >= 1
        for h in hits:
            assert isinstance(h, RerankedHit)
            assert h.score >= 0.0

    def test_reranker_empty_input(self):
        rk = Reranker()
        hits = rk.rerank("query", [])
        assert hits == []

    def test_reranker_threshold_filter(self):
        rk = Reranker(top_k=10, score_threshold=2.0)
        hits = rk.rerank("anything", ["a", "b", "c"])
        assert hits == []

    def test_rerank_batch_convenience(self):
        hits = rerank_batch("test query", ["A", "B", "C"], top_k=2)
        assert len(hits) <= 2
        assert all(isinstance(h, RerankedHit) for h in hits)

    def test_reranker_with_metadatas(self):
        rk = Reranker(top_k=3)
        docs = ["First doc", "Second doc", "Third doc"]
        metas = [{"id": 1}, {"id": 2}, {"id": 3}]
        hits = rk.rerank("query", docs, metadatas=metas)

        assert len(hits) == 3
        for i, h in enumerate(hits):
            assert h.metadata.get("id") == h.index + 1


class TestMVKBGate:
    def test_minimum_viable_kb_pass(self, tmp_path: Path):
        (tmp_path / "AGENTS.md").write_text(
            "# Rules\n\nRule 1: Search first.\n\nRule 2: Write KE after tasks.\n\n"
            "Rule 3: Check locks.\n\nRule 4: Clean up.\n\nRule 5: Test everything.\n",
            encoding="utf-8",
        )
        (tmp_path / "data").mkdir(exist_ok=True)

        result = run_bootstrap(tmp_path, min_ke_count=1, min_categories=1)

        assert result.success
        assert result.total_activated >= 1

    def test_bootstrap_result_fields(self):
        result = BootstrapResult(success=True)

        assert result.total_sources_scanned == 0
        assert result.total_activated == 0
        assert result.categories_found == []

        result = BootstrapResult(
            success=True,
            total_sources_scanned=10,
            total_chunks_extracted=100,
            total_passed_g1=90,
            total_activated=80,
            total_verified=80,
            categories_found=["adr_decision", "module_blueprint", "governance_rule"],
            gaps=[],
            elapsed_seconds=5.2,
        )
        assert result.success
        assert len(result.categories_found) == 3
        assert result.elapsed_seconds == 5.2

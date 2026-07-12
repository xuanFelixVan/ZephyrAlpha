# [A_test] module_id: SRC-TST-1160 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] tests.test_kb_bootstrap
# [INVARIANTS] Bootstrap.run must return BootstrapResult; segment_document/classify_chunk are pure functions
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file
# [TTL] task_bound

from __future__ import annotations

from pathlib import Path

from zephyr.gov_kb.bootstrap import (
    Bootstrap,
    BootstrapChunk,
    BootstrapConfig,
    BootstrapResult,
    classify_category,
    classify_chunk,
    discover_document_sources,
    segment_document,
)


class TestBootstrapConfig:
    def test_default_values(self):
        cfg = BootstrapConfig()
        assert cfg.min_ke_count == 10
        assert cfg.min_categories == 5
        assert cfg.min_chunk_chars == 80
        assert cfg.max_chunks_per_file == 50
        assert cfg.scan_roots == []
        assert len(cfg.exclude_patterns) > 0

    def test_custom_values(self):
        cfg = BootstrapConfig(min_ke_count=5, min_categories=3, min_chunk_chars=50)
        assert cfg.min_ke_count == 5
        assert cfg.min_categories == 3
        assert cfg.min_chunk_chars == 50


class TestBootstrapChunk:
    def test_default_values(self):
        c = BootstrapChunk(source_path=Path("a.md"), heading="Test", content="body")
        assert c.category == "general"
        assert c.priority == 0
        assert c.module_id == ""
        assert c.fingerprint == ""


class TestBootstrapResult:
    def test_default_values(self):
        r = BootstrapResult(success=False)
        assert r.success is False
        assert r.total_sources_scanned == 0
        assert r.total_chunks_extracted == 0
        assert r.gaps == []
        assert r.violations == []


class TestClassifyCategory:
    def test_adr_category(self):
        assert classify_category(Path("docs/ADR/adr-001.md")) == "adr_decision"

    def test_blueprint_category(self):
        assert classify_category(Path("docs/03_modules/mod/blueprint.md")) == "module_blueprint"

    def test_rule_category(self):
        assert classify_category(Path("project_rules.md")) == "governance_rule"

    def test_session_category(self):
        assert classify_category(Path("session_logs/session-001.yaml")) == "session_log"

    def test_agents_category(self):
        assert classify_category(Path("AGENTS.md")) == "agent_instruction"

    def test_knowledge_category(self):
        assert classify_category(Path("docs/08_knowledge/ke-001.md")) == "knowledge_base"

    def test_default_category(self):
        assert classify_category(Path("docs/readme.md")) == "documentation"


class TestClassifyChunk:
    def test_adr_content(self):
        assert classify_chunk("This is an ADR about design decisions") == "adr_decision"

    def test_architecture_content(self):
        assert classify_chunk("The architecture of the system uses microservices") == "architecture"

    def test_rule_content(self):
        assert classify_chunk("This rule governs the protocol") == "governance_rule"

    def test_test_content(self):
        assert classify_chunk("Run pytest to test the module") == "test_coverage"

    def test_general_content(self):
        assert classify_chunk("Hello world") == "general"


class TestSegmentDocument:
    def test_segments_markdown_with_headings(self, tmp_path: Path):
        doc = tmp_path / "doc.md"
        doc.write_text(
            "# Heading One\n\nThis is content under heading one with enough text to pass the minimum threshold for chunk extraction.\n\n"
            "# Heading Two\n\nThis is content under heading two with enough text to pass the minimum threshold for chunk extraction.\n",
            encoding="utf-8",
        )
        chunks = segment_document(doc, min_chunk_chars=30, max_chunks=10)
        assert len(chunks) >= 1
        for c in chunks:
            assert isinstance(c, BootstrapChunk)
            assert len(c.content) > 0

    def test_segments_empty_file(self, tmp_path: Path):
        doc = tmp_path / "empty.md"
        doc.write_text("", encoding="utf-8")
        chunks = segment_document(doc)
        assert chunks == []

    def test_segments_with_frontmatter(self, tmp_path: Path):
        doc = tmp_path / "fm.md"
        doc.write_text(
            "---\ntitle: Test\n---\n\n# Section\n\nThis is a section with enough content to be extracted as a chunk for the bootstrap process.\n",
            encoding="utf-8",
        )
        chunks = segment_document(doc, min_chunk_chars=30)
        assert len(chunks) >= 1

    def test_max_chunks_limit(self, tmp_path: Path):
        doc = tmp_path / "big.md"
        content = ""
        for i in range(20):
            content += f"# Section {i}\n\n{'Word ' * 50}\n\n"
        doc.write_text(content, encoding="utf-8")
        chunks = segment_document(doc, min_chunk_chars=20, max_chunks=5)
        assert len(chunks) <= 5


class TestDiscoverDocumentSources:
    def test_empty_root(self, tmp_path: Path):
        sources = discover_document_sources(tmp_path)
        assert isinstance(sources, list)

    def test_with_scan_roots(self, tmp_path: Path):
        doc = tmp_path / "doc.md"
        doc.write_text("A" * 100, encoding="utf-8")
        sources = discover_document_sources(tmp_path, scan_roots=[doc])
        assert len(sources) >= 1

    def test_excludes_small_files(self, tmp_path: Path):
        doc = tmp_path / "tiny.md"
        doc.write_text("hi", encoding="utf-8")
        sources = discover_document_sources(tmp_path, scan_roots=[doc])
        assert len(sources) == 0


class TestBootstrap:
    def test_run_with_empty_root(self, tmp_path: Path):
        config = BootstrapConfig(min_ke_count=1, min_categories=1, scan_roots=[])
        engine = Bootstrap(project_root=tmp_path, config=config)
        result = engine.run()
        assert isinstance(result, BootstrapResult)
        assert result.total_sources_scanned == 0

    def test_run_with_documents(self, tmp_path: Path):
        docs_dir = tmp_path / "docs"
        docs_dir.mkdir()
        doc = docs_dir / "test.md"
        doc.write_text(
            "# Architecture Decision\n\nThis is an ADR about design decisions for the system. "
            "We chose this approach because of trade-off analysis. The rationale is clear. "
            "This is a critical and irreplaceable component with high reuse potential.\n",
            encoding="utf-8",
        )
        config = BootstrapConfig(min_ke_count=1, min_categories=1, scan_roots=[doc])
        engine = Bootstrap(project_root=tmp_path, config=config)
        result = engine.run()
        assert isinstance(result, BootstrapResult)
        assert result.total_chunks_extracted >= 1

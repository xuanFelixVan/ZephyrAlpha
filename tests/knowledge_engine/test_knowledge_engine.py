# [A_test] module_id: SRC-TST-1195 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-401 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_knowledge_engine
# [INVARIANTS] KnowledgeIndex.index populates entries and inverted_index; search returns matches
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_knowledge_engine.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_kb.knowledge_engine import (
    KnowledgeEntry,
    KnowledgeIndex,
    get_index,
)


class TestKnowledgeEntry:
    def test_creation_defaults(self):
        entry = KnowledgeEntry(entry_id="E1", title="Test", content="body")
        assert entry.tags == []
        assert entry.source_file == ""
        assert entry.indexed_at == ""

    def test_creation_with_tags(self):
        entry = KnowledgeEntry(entry_id="E1", title="T", content="C", tags=["a", "b"])
        assert len(entry.tags) == 2


class TestKnowledgeIndex:
    def test_creation_defaults(self):
        idx = KnowledgeIndex()
        assert idx.entries == {}
        assert idx.inverted_index == {}

    def test_index_adds_entry(self):
        idx = KnowledgeIndex()
        entry = KnowledgeEntry(entry_id="E1", title="Test", content="body", tags=["python"])
        idx.index(entry)
        assert "E1" in idx.entries
        assert "python" in idx.inverted_index
        assert "E1" in idx.inverted_index["python"]

    def test_index_sets_timestamp(self):
        idx = KnowledgeIndex()
        entry = KnowledgeEntry(entry_id="E1", title="T", content="C")
        idx.index(entry)
        assert entry.indexed_at != ""

    def test_search_by_title(self):
        idx = KnowledgeIndex()
        entry = KnowledgeEntry(entry_id="E1", title="Python Guide", content="body")
        idx.index(entry)
        results = idx.search("python")
        assert len(results) == 1

    def test_search_by_content(self):
        idx = KnowledgeIndex()
        entry = KnowledgeEntry(entry_id="E1", title="Guide", content="Python tutorial")
        idx.index(entry)
        results = idx.search("tutorial")
        assert len(results) == 1

    def test_search_by_tag(self):
        idx = KnowledgeIndex()
        entry = KnowledgeEntry(entry_id="E1", title="Guide", content="body", tags=["python"])
        idx.index(entry)
        results = idx.search("python")
        assert len(results) == 1

    def test_search_no_match(self):
        idx = KnowledgeIndex()
        entry = KnowledgeEntry(entry_id="E1", title="Guide", content="body")
        idx.index(entry)
        results = idx.search("nonexistent")
        assert results == []

    def test_search_by_tag_method(self):
        idx = KnowledgeIndex()
        entry = KnowledgeEntry(entry_id="E1", title="T", content="C", tags=["ml"])
        idx.index(entry)
        results = idx.search_by_tag("ml")
        assert len(results) == 1

    def test_search_by_tag_no_match(self):
        idx = KnowledgeIndex()
        results = idx.search_by_tag("nonexistent")
        assert results == []

    def test_associate_related(self):
        idx = KnowledgeIndex()
        e1 = KnowledgeEntry(entry_id="E1", title="T1", content="C1", tags=["ml", "python"])
        e2 = KnowledgeEntry(entry_id="E2", title="T2", content="C2", tags=["ml"])
        idx.index(e1)
        idx.index(e2)
        related = idx.associate("E1")
        ids = [r.entry_id for r in related]
        assert "E2" in ids

    def test_associate_no_entry(self):
        idx = KnowledgeIndex()
        related = idx.associate("nonexistent")
        assert related == []


class TestGetIndex:
    def test_returns_knowledge_index(self):
        idx = get_index()
        assert isinstance(idx, KnowledgeIndex)


class TestBoundary:
    def test_search_case_insensitive(self):
        idx = KnowledgeIndex()
        entry = KnowledgeEntry(entry_id="E1", title="Python Guide", content="body")
        idx.index(entry)
        results = idx.search("PYTHON")
        assert len(results) == 1

    def test_multiple_entries_same_tag(self):
        idx = KnowledgeIndex()
        for i in range(3):
            e = KnowledgeEntry(entry_id=f"E{i}", title=f"T{i}", content="C", tags=["shared"])
            idx.index(e)
        results = idx.search_by_tag("shared")
        assert len(results) == 3

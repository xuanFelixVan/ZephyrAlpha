# [A_test] module_id: SRC-TST-1161 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain-knowledge/knowledge-base/blueprint.md | §
# [MODULE] tests.test_kb_chromadb_init
# [INVARIANTS] init_chromadb must be idempotent; CollectionInfo is a pydantic model
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] this file

from __future__ import annotations

from pathlib import Path

from zephyr.governance.kb.chromadb_init import (
    _COLLECTION_METADATA,
    COLLECTION_NAMES,
    CollectionInfo,
)


class TestCollectionInfo:
    def test_default_values(self):
        info = CollectionInfo(name="test")
        assert info.name == "test"
        assert info.count == 0
        assert info.metadata == {}

    def test_with_values(self):
        info = CollectionInfo(name="ke_entries", count=5, metadata={"hnsw:space": "cosine"})
        assert info.name == "ke_entries"
        assert info.count == 5
        assert info.metadata["hnsw:space"] == "cosine"

    def test_serialization(self):
        info = CollectionInfo(name="test", count=10, metadata={"key": "value"})
        data = info.model_dump()
        assert data["name"] == "test"
        assert data["count"] == 10


class TestCollectionConstants:
    def test_collection_names(self):
        assert "ke_entries" in COLLECTION_NAMES
        assert "vibe_rules" in COLLECTION_NAMES
        assert "blueprints" in COLLECTION_NAMES
        assert "failure_patterns" in COLLECTION_NAMES

    def test_metadata_has_cosine_space(self):
        for name in COLLECTION_NAMES:
            assert name in _COLLECTION_METADATA
            assert _COLLECTION_METADATA[name]["hnsw:space"] == "cosine"


class TestInitChromadb:
    def test_init_creates_collections(self, tmp_path: Path):
        import zephyr.data.knowledge_management.kb.chromadb_init as mod

        mod._chroma_client = None
        try:
            results = mod.init_chromadb(persist_dir=tmp_path / "chroma")
            assert len(results) == len(COLLECTION_NAMES)
            for r in results:
                assert isinstance(r, CollectionInfo)
                assert r.name in COLLECTION_NAMES
        finally:
            mod._chroma_client = None

    def test_init_idempotent(self, tmp_path: Path):
        import zephyr.data.knowledge_management.kb.chromadb_init as mod

        mod._chroma_client = None
        try:
            r1 = mod.init_chromadb(persist_dir=tmp_path / "chroma1")
            mod._chroma_client = None
            r2 = mod.init_chromadb(persist_dir=tmp_path / "chroma2")
            assert len(r1) == len(r2)
        finally:
            mod._chroma_client = None


class TestResetChromadb:
    def test_reset_recreates_collections(self, tmp_path: Path):
        import zephyr.data.knowledge_management.kb.chromadb_init as mod

        mod._chroma_client = None
        try:
            mod.init_chromadb(persist_dir=tmp_path / "chroma")
            results = mod.reset_chromadb(persist_dir=tmp_path / "chroma")
            assert len(results) == len(COLLECTION_NAMES)
        finally:
            mod._chroma_client = None


class TestCollectionStatus:
    def test_status_after_init(self, tmp_path: Path):
        import zephyr.data.knowledge_management.kb.chromadb_init as mod

        mod._chroma_client = None
        try:
            mod.init_chromadb(persist_dir=tmp_path / "chroma")
            status = mod.collection_status(persist_dir=tmp_path / "chroma")
            assert len(status) == len(COLLECTION_NAMES)
            for s in status:
                assert s.count >= 0
        finally:
            mod._chroma_client = None

    def test_status_without_init(self, tmp_path: Path):
        import zephyr.data.knowledge_management.kb.chromadb_init as mod

        mod._chroma_client = None
        try:
            status = mod.collection_status(persist_dir=tmp_path / "chroma_new")
            for s in status:
                assert s.count == -1
        finally:
            mod._chroma_client = None

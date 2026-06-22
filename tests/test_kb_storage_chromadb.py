# [A_test] module_id: SRC-TST-1177 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain-knowledge/knowledge-base/blueprint.md | §
# [MODULE] tests.test_kb_storage_chromadb
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self

from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

import pytest

from zephyr.governance.kb.chromadb_init import (
    _COLLECTION_METADATA,
    COLLECTION_NAMES,
    CollectionInfo,
    collection_status,
    get_chroma_client,
    init_chromadb,
    reset_chromadb,
)


@pytest.fixture(autouse=True)
def _reset_global_client():
    import zephyr.data.knowledge_management.kb.chromadb_init as _mod

    _mod._chroma_client = None
    yield
    _mod._chroma_client = None


class TestCollectionInfo:
    def test_create_valid(self):
        ci = CollectionInfo(name="ke_entries", count=10, metadata={"hnsw:space": "cosine"})
        assert ci.name == "ke_entries"
        assert ci.count == 10

    def test_default_count(self):
        ci = CollectionInfo(name="test")
        assert ci.count == 0

    def test_default_metadata(self):
        ci = CollectionInfo(name="test")
        assert ci.metadata == {}


class TestCollectionNames:
    def test_collection_names_tuple(self):
        assert isinstance(COLLECTION_NAMES, tuple)
        assert "ke_entries" in COLLECTION_NAMES
        assert "vibe_rules" in COLLECTION_NAMES
        assert "blueprints" in COLLECTION_NAMES
        assert "failure_patterns" in COLLECTION_NAMES

    def test_collection_metadata_keys_match(self):
        for name in COLLECTION_NAMES:
            assert name in _COLLECTION_METADATA, f"Missing metadata for {name}"


class TestGetChromaClient:
    def test_get_client_with_mock_chromadb(self, tmp_path):
        mock_client = MagicMock()
        mock_chromadb = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        with patch.dict(sys.modules, {"chromadb": mock_chromadb}):
            import zephyr.data.knowledge_management.kb.chromadb_init as _mod

            _mod._chroma_client = None
            client = get_chroma_client(persist_dir=str(tmp_path / "chroma"))
            assert client is mock_client
            mock_chromadb.PersistentClient.assert_called_once()

    def test_get_client_caches(self, tmp_path):
        mock_client = MagicMock()
        mock_chromadb = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        with patch.dict(sys.modules, {"chromadb": mock_chromadb}):
            import zephyr.data.knowledge_management.kb.chromadb_init as _mod

            _mod._chroma_client = None
            c1 = get_chroma_client(persist_dir=str(tmp_path / "chroma"))
            c2 = get_chroma_client(persist_dir=str(tmp_path / "chroma"))
            assert c1 is c2


class TestInitChromadb:
    def test_init_creates_collections(self, tmp_path):
        mock_client = MagicMock()
        mock_client.list_collections.return_value = []
        created = {}

        def fake_create(name, metadata=None):
            col = MagicMock()
            col.name = name
            col.count.return_value = 0
            created[name] = col
            return col

        mock_client.create_collection.side_effect = fake_create
        mock_chromadb = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        with patch.dict(sys.modules, {"chromadb": mock_chromadb}):
            import zephyr.data.knowledge_management.kb.chromadb_init as _mod

            _mod._chroma_client = None
            results = init_chromadb(persist_dir=str(tmp_path / "chroma"))
            assert len(results) == len(COLLECTION_NAMES)
            for r in results:
                assert isinstance(r, CollectionInfo)
                assert r.name in COLLECTION_NAMES

    def test_init_existing_collections(self, tmp_path):
        existing_cols = []
        for name in COLLECTION_NAMES:
            col = MagicMock()
            col.name = name
            col.count.return_value = 5
            existing_cols.append(col)
        mock_client = MagicMock()
        mock_client.list_collections.return_value = existing_cols
        mock_client.get_collection.side_effect = lambda name: next(c for c in existing_cols if c.name == name)
        mock_chromadb = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        with patch.dict(sys.modules, {"chromadb": mock_chromadb}):
            import zephyr.data.knowledge_management.kb.chromadb_init as _mod

            _mod._chroma_client = None
            results = init_chromadb(persist_dir=str(tmp_path / "chroma"))
            for r in results:
                assert r.count == 5


class TestResetChromadb:
    def test_reset_deletes_and_recreates(self, tmp_path):
        call_log = []
        existing_cols = []
        for name in COLLECTION_NAMES:
            col = MagicMock()
            col.name = name
            col.count.return_value = 0
            existing_cols.append(col)
        mock_client = MagicMock()
        mock_client.list_collections.return_value = existing_cols
        mock_client.delete_collection.side_effect = lambda name: call_log.append(("delete", name))
        mock_client.get_collection.side_effect = lambda name: next(c for c in existing_cols if c.name == name)
        mock_client.create_collection.side_effect = lambda name, metadata=None: MagicMock(name=name)
        mock_chromadb = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        with patch.dict(sys.modules, {"chromadb": mock_chromadb}):
            import zephyr.data.knowledge_management.kb.chromadb_init as _mod

            _mod._chroma_client = mock_client
            results = reset_chromadb(persist_dir=str(tmp_path / "chroma"))
            assert len(results) == len(COLLECTION_NAMES)


class TestCollectionStatus:
    def test_status_existing(self, tmp_path):
        existing_cols = []
        for name in COLLECTION_NAMES:
            col = MagicMock()
            col.name = name
            col.count.return_value = 3
            existing_cols.append(col)
        mock_client = MagicMock()
        mock_client.list_collections.return_value = existing_cols
        mock_client.get_collection.side_effect = lambda name: next(c for c in existing_cols if c.name == name)
        mock_chromadb = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        with patch.dict(sys.modules, {"chromadb": mock_chromadb}):
            import zephyr.data.knowledge_management.kb.chromadb_init as _mod

            _mod._chroma_client = mock_client
            results = collection_status(persist_dir=str(tmp_path / "chroma"))
            for r in results:
                assert r.count == 3

    def test_status_missing_collection(self, tmp_path):
        mock_client = MagicMock()
        mock_client.list_collections.return_value = []
        mock_chromadb = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_client
        with patch.dict(sys.modules, {"chromadb": mock_chromadb}):
            import zephyr.data.knowledge_management.kb.chromadb_init as _mod

            _mod._chroma_client = mock_client
            results = collection_status(persist_dir=str(tmp_path / "chroma"))
            for r in results:
                assert r.count == -1

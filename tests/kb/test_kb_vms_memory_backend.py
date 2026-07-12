# [A_test] module_id: SRC-TST-1181 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] tests.test_kb_vms_memory_backend
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock

from zephyr.gov_kb._backend_protocol import (
    InMemoryMemoryBackend,
    MemoryRecord,
)
from zephyr.gov_kb.vms_memory_backend import VMSMemoryBackend


def _make_record(topic: str = "knowledge_test", content: str = "test content") -> MemoryRecord:
    return MemoryRecord(
        chunk_id="chunk-001",
        topic=topic,
        content=content,
        score=1.0,
        written_at="2026-01-01T00:00:00",
        metadata={"origin": "test"},
    )


class TestVMSMemoryBackendInit:
    def test_no_vms_uses_fallback(self):
        backend = VMSMemoryBackend(vms=None)
        assert backend.vms is None
        assert backend.is_vms_available is False
        assert isinstance(backend._fallback, InMemoryMemoryBackend)

    def test_custom_fallback(self):
        fallback = InMemoryMemoryBackend()
        backend = VMSMemoryBackend(vms=None, fallback=fallback)
        assert backend._fallback is fallback

    def test_with_vms(self):
        mock_vms = MagicMock()
        backend = VMSMemoryBackend(vms=mock_vms)
        assert backend.is_vms_available is True
        assert backend.vms is mock_vms


class TestVMSMemoryBackendWrite:
    def test_write_fallback_when_no_vms(self):
        backend = VMSMemoryBackend(vms=None)
        record = _make_record()
        chunk_id = backend.write(record)
        assert chunk_id == "chunk-001"
        assert backend._fallback.count() == 1

    def test_write_uses_vms_when_available(self):
        mock_vms = MagicMock()
        mock_vms.write.return_value = "vms-chunk-001"
        backend = VMSMemoryBackend(vms=mock_vms)
        record = _make_record()
        chunk_id = backend.write(record)
        assert chunk_id == "vms-chunk-001"
        mock_vms.write.assert_called_once()

    def test_write_falls_back_on_vms_failure(self):
        mock_vms = MagicMock()
        mock_vms.write.side_effect = RuntimeError("VMS down")
        backend = VMSMemoryBackend(vms=mock_vms)
        record = _make_record()
        chunk_id = backend.write(record)
        assert chunk_id == "chunk-001"
        assert backend.is_vms_available is False


class TestVMSMemoryBackendListByTopic:
    def test_list_by_topic_fallback(self):
        backend = VMSMemoryBackend(vms=None)
        record = _make_record(topic="test_topic")
        backend.write(record)
        results = backend.list_by_topic("test_topic", k=5)
        assert len(results) >= 1
        assert results[0].topic == "test_topic"

    def test_list_by_topic_vms(self):
        mock_vms = MagicMock()
        mock_col = MagicMock()
        mock_col.get.return_value = {
            "ids": ["v1"],
            "documents": ["hello"],
            "metadatas": [{"topic": "knowledge", "written_at": "2026-01-01T00:00:00"}],
        }
        mock_vms.get_collection.return_value = mock_col
        backend = VMSMemoryBackend(vms=mock_vms)
        results = backend.list_by_topic("knowledge", k=5)
        assert len(results) == 1
        assert results[0].content == "hello"

    def test_list_by_topic_vms_failure_fallback(self):
        mock_vms = MagicMock()
        mock_vms.get_collection.side_effect = RuntimeError("VMS error")
        backend = VMSMemoryBackend(vms=mock_vms)
        record = _make_record(topic="knowledge")
        backend._fallback.write(record)
        results = backend.list_by_topic("knowledge", k=5)
        assert len(results) >= 1


class TestVMSMemoryBackendQuery:
    def test_query_fallback(self):
        backend = VMSMemoryBackend(vms=None)
        record = _make_record(topic="search_topic", content="python code")
        backend.write(record)
        results = backend.query("python", k=5)
        assert isinstance(results, list)

    def test_query_vms(self):
        mock_vms = MagicMock()
        mock_vms.search.return_value = [
            {
                "id": "v1",
                "content": "python code",
                "score": 0.9,
                "metadata": {"topic": "knowledge", "written_at": "2026-01-01T00:00:00"},
            },
        ]
        backend = VMSMemoryBackend(vms=mock_vms)
        results = backend.query("python", k=5)
        assert len(results) == 1

    def test_query_vms_with_topic_filter(self):
        mock_vms = MagicMock()
        mock_vms.search.return_value = [
            {
                "id": "v1",
                "content": "python code",
                "score": 0.9,
                "metadata": {"topic": "knowledge", "written_at": "2026-01-01T00:00:00"},
            },
            {
                "id": "v2",
                "content": "other",
                "score": 0.8,
                "metadata": {"topic": "rules", "written_at": "2026-01-01T00:00:00"},
            },
        ]
        backend = VMSMemoryBackend(vms=mock_vms)
        results = backend.query("python", k=5, topic="knowledge")
        assert all(r.topic == "knowledge" for r in results)

    def test_query_vms_failure_fallback(self):
        mock_vms = MagicMock()
        mock_vms.search.side_effect = RuntimeError("VMS error")
        backend = VMSMemoryBackend(vms=mock_vms)
        record = _make_record(topic="knowledge", content="test content")
        backend._fallback.write(record)
        results = backend.query("test", k=5)
        assert isinstance(results, list)


class TestVMSMemoryBackendCount:
    def test_count_fallback(self):
        backend = VMSMemoryBackend(vms=None)
        backend.write(_make_record())
        assert backend.count() == 1

    def test_count_vms(self):
        mock_vms = MagicMock()
        mock_vms.health_check.return_value = {
            "collections": {
                "knowledge": {"count": 10},
                "rules": {"count": 5},
            }
        }
        backend = VMSMemoryBackend(vms=mock_vms)
        assert backend.count() == 15

    def test_count_vms_failure_fallback(self):
        mock_vms = MagicMock()
        mock_vms.health_check.side_effect = RuntimeError("VMS error")
        backend = VMSMemoryBackend(vms=mock_vms)
        backend._fallback.write(_make_record())
        assert backend.count() == 1


class TestVMSMemoryBackendResolveCollection:
    def test_resolve_knowledge(self):
        backend = VMSMemoryBackend(vms=None)
        assert backend._resolve_collection("knowledge") == "knowledge"

    def test_resolve_rule(self):
        backend = VMSMemoryBackend(vms=None)
        assert backend._resolve_collection("rule") == "rules"

    def test_resolve_governance(self):
        backend = VMSMemoryBackend(vms=None)
        assert backend._resolve_collection("governance") == "rules"

    def test_resolve_blueprint(self):
        backend = VMSMemoryBackend(vms=None)
        assert backend._resolve_collection("blueprint") == "blueprints"

    def test_resolve_default(self):
        backend = VMSMemoryBackend(vms=None)
        assert backend._resolve_collection("unknown_topic") == "knowledge"

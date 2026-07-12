# [A_test] module_id: SRC-TST-1176 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] tests.test_kb_storage_backend
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

import threading

import pytest

from zephyr.gov_kb._backend_protocol import (
    InMemoryMemoryBackend,
    MemoryBackend,
    MemoryBackendError,
    MemoryRecord,
    _simple_tokens,
)


class TestMemoryBackendError:
    def test_is_runtime_error(self):
        err = MemoryBackendError("test error")
        assert isinstance(err, RuntimeError)
        assert "test error" in str(err)


class TestMemoryRecord:
    def test_create_valid(self):
        mr = MemoryRecord(
            chunk_id="c1",
            topic="test",
            content="hello",
        )
        assert mr.chunk_id == "c1"
        assert mr.topic == "test"
        assert mr.content == "hello"
        assert mr.score == 1.0
        assert mr.written_at == ""
        assert mr.metadata == {}

    def test_create_with_all_fields(self):
        mr = MemoryRecord(
            chunk_id="c2",
            topic="topic2",
            content="world",
            score=0.85,
            written_at="2026-01-01T00:00:00",
            metadata={"key": "value"},
        )
        assert mr.score == 0.85
        assert mr.metadata["key"] == "value"

    def test_empty_chunk_id_rejected(self):
        with pytest.raises(Exception):
            MemoryRecord(chunk_id="", topic="test", content="hello")

    def test_empty_topic_rejected(self):
        with pytest.raises(Exception):
            MemoryRecord(chunk_id="c1", topic="", content="hello")

    def test_score_out_of_range(self):
        with pytest.raises(Exception):
            MemoryRecord(chunk_id="c1", topic="t", content="c", score=1.5)

    def test_negative_score_rejected(self):
        with pytest.raises(Exception):
            MemoryRecord(chunk_id="c1", topic="t", content="c", score=-0.1)

    def test_extra_fields_rejected(self):
        with pytest.raises(Exception):
            MemoryRecord(chunk_id="c1", topic="t", content="c", unknown_field="bad")


class TestMemoryBackendProtocol:
    def test_inmemory_implements_protocol(self):
        backend = InMemoryMemoryBackend()
        assert isinstance(backend, MemoryBackend)

    def test_protocol_is_runtime_checkable(self):
        assert isinstance(InMemoryMemoryBackend(), MemoryBackend)


class TestInMemoryMemoryBackend:
    def test_write_and_count(self):
        backend = InMemoryMemoryBackend()
        rec = MemoryRecord(chunk_id="c1", topic="t1", content="hello")
        result = backend.write(rec)
        assert result == "c1"
        assert backend.count() == 1

    def test_write_multiple(self):
        backend = InMemoryMemoryBackend()
        backend.write(MemoryRecord(chunk_id="c1", topic="t1", content="a"))
        backend.write(MemoryRecord(chunk_id="c2", topic="t2", content="b"))
        assert backend.count() == 2

    def test_list_by_topic(self):
        backend = InMemoryMemoryBackend()
        backend.write(MemoryRecord(chunk_id="c1", topic="t1", content="a", written_at="2026-01-01T00:00:00"))
        backend.write(MemoryRecord(chunk_id="c2", topic="t1", content="b", written_at="2026-01-02T00:00:00"))
        backend.write(MemoryRecord(chunk_id="c3", topic="t2", content="c"))
        results = backend.list_by_topic("t1", k=10)
        assert len(results) == 2
        assert all(r.topic == "t1" for r in results)

    def test_list_by_topic_k_limit(self):
        backend = InMemoryMemoryBackend()
        for i in range(5):
            backend.write(MemoryRecord(chunk_id=f"c{i}", topic="t1", content=f"content {i}"))
        results = backend.list_by_topic("t1", k=2)
        assert len(results) == 2

    def test_list_by_topic_empty(self):
        backend = InMemoryMemoryBackend()
        results = backend.list_by_topic("nonexistent", k=5)
        assert results == []

    def test_query_basic(self):
        backend = InMemoryMemoryBackend()
        backend.write(MemoryRecord(chunk_id="c1", topic="t1", content="python machine learning"))
        backend.write(MemoryRecord(chunk_id="c2", topic="t1", content="java web development"))
        results = backend.query("python", k=5)
        assert len(results) >= 1
        assert results[0].content == "python machine learning"

    def test_query_with_topic_filter(self):
        backend = InMemoryMemoryBackend()
        backend.write(MemoryRecord(chunk_id="c1", topic="t1", content="python code"))
        backend.write(MemoryRecord(chunk_id="c2", topic="t2", content="python code"))
        results = backend.query("python", k=5, topic="t1")
        assert all(r.topic == "t1" for r in results)

    def test_query_empty_string(self):
        backend = InMemoryMemoryBackend()
        backend.write(MemoryRecord(chunk_id="c1", topic="t1", content="hello"))
        results = backend.query("", k=5)
        assert results == []

    def test_query_no_match(self):
        backend = InMemoryMemoryBackend()
        backend.write(MemoryRecord(chunk_id="c1", topic="t1", content="hello world"))
        results = backend.query("xyzzy", k=5)
        assert results == []

    def test_count_empty(self):
        backend = InMemoryMemoryBackend()
        assert backend.count() == 0

    def test_clear(self):
        backend = InMemoryMemoryBackend()
        backend.write(MemoryRecord(chunk_id="c1", topic="t1", content="hello"))
        backend.clear()
        assert backend.count() == 0

    def test_thread_safety(self):
        backend = InMemoryMemoryBackend()
        errors = []

        def writer(start):
            try:
                for i in range(20):
                    backend.write(
                        MemoryRecord(
                            chunk_id=f"c-{start}-{i}",
                            topic=f"t-{start}",
                            content=f"content-{start}-{i}",
                        )
                    )
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=writer, args=(j,)) for j in range(4)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert not errors
        assert backend.count() == 80


class TestSimpleTokens:
    def test_ascii_words(self):
        tokens = _simple_tokens("hello world")
        assert "hello" in tokens
        assert "world" in tokens

    def test_empty_string(self):
        assert _simple_tokens("") == []

    def test_cjk_characters(self):
        tokens = _simple_tokens("你好世界")
        assert "你" in tokens
        assert "好" in tokens

    def test_mixed(self):
        tokens = _simple_tokens("hello 你好 world")
        assert "hello" in tokens
        assert "你" in tokens

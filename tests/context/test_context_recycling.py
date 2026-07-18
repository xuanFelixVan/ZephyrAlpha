# [A_test] module_id: SRC-TST-0604 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-370 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_context_recycling
# [INVARIANTS] compress/restore roundtrip preserves content; is_valid requires data and ratio<1
# [MODIFY-GUARD] Changes must sync with context_recycling.py
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] None
# [TESTS] tests/test_context_recycling.py
# [TTL] task_bound

from __future__ import annotations

import os
import tempfile

from zephyr.governance.context_governance.context_recycling import (
    CompressedContext,
    ContextRecycling,
)


class TestCompressedContext:
    def test_creation(self):
        ctx = CompressedContext(
            session_id="s1",
            compressed_at="2026-01-01T00:00:00Z",
            origin_size_bytes=100,
            compressed_size_bytes=50,
            compression_ratio=0.5,
            data="abc123",
        )
        assert ctx.session_id == "s1"
        assert ctx.compression_ratio == 0.5

    def test_is_valid_true(self):
        ctx = CompressedContext(
            session_id="s1",
            compressed_at="2026-01-01T00:00:00Z",
            origin_size_bytes=100,
            compressed_size_bytes=50,
            compression_ratio=0.5,
            data="abc123",
        )
        assert ctx.is_valid is True

    def test_is_valid_false_no_data(self):
        ctx = CompressedContext(
            session_id="s1",
            compressed_at="2026-01-01T00:00:00Z",
            origin_size_bytes=100,
            compressed_size_bytes=50,
            compression_ratio=0.5,
            data="",
        )
        assert ctx.is_valid is False

    def test_is_valid_false_ratio_ge_one(self):
        ctx = CompressedContext(
            session_id="s1",
            compressed_at="2026-01-01T00:00:00Z",
            origin_size_bytes=10,
            compressed_size_bytes=20,
            compression_ratio=1.5,
            data="abc",
        )
        assert ctx.is_valid is False

    def test_default_key_topics_empty(self):
        ctx = CompressedContext(
            session_id="s1",
            compressed_at="2026-01-01T00:00:00Z",
            origin_size_bytes=100,
            compressed_size_bytes=50,
            compression_ratio=0.5,
            data="abc",
        )
        assert ctx.key_topics == []


class TestContextRecycling:
    def test_compress_and_restore(self):
        cr = ContextRecycling()
        content = "Hello, world! This is a test of context recycling."
        cr.compress("session-1", content)
        restored = cr.restore("session-1")
        assert restored == content

    def test_compress_with_topics(self):
        cr = ContextRecycling()
        ctx = cr.compress("session-2", "test content", key_topics=["topic-a", "topic-b"])
        assert ctx.key_topics == ["topic-a", "topic-b"]

    def test_restore_nonexistent_returns_none(self):
        cr = ContextRecycling()
        assert cr.restore("nonexistent") is None

    def test_store_returns_compressed_context(self):
        cr = ContextRecycling()
        cr.compress("session-3", "data")
        stored = cr.store("session-3")
        assert stored is not None
        assert stored.session_id == "session-3"

    def test_store_nonexistent_returns_none(self):
        cr = ContextRecycling()
        assert cr.store("nonexistent") is None

    def test_purge_existing(self):
        cr = ContextRecycling()
        cr.compress("session-4", "data")
        assert cr.purge("session-4") is True
        assert cr.store("session-4") is None

    def test_purge_nonexistent(self):
        cr = ContextRecycling()
        assert cr.purge("nonexistent") is False

    def test_list_sessions(self):
        cr = ContextRecycling()
        cr.compress("b", "data")
        cr.compress("a", "data")
        sessions = cr.list_sessions()
        assert sessions == ["a", "b"]

    def test_list_sessions_empty(self):
        cr = ContextRecycling()
        assert cr.list_sessions() == []

    def test_stats(self):
        cr = ContextRecycling()
        content = "A" * 1000
        cr.compress("s1", content)
        stats = cr.stats()
        assert stats["session_count"] == 1
        assert stats["total_origin_bytes"] > 0
        assert stats["total_compressed_bytes"] > 0
        assert stats["overall_ratio"] > 0

    def test_stats_empty(self):
        cr = ContextRecycling()
        stats = cr.stats()
        assert stats["session_count"] == 0
        assert stats["total_origin_bytes"] == 0

    def test_compress_empty_string(self):
        cr = ContextRecycling()
        ctx = cr.compress("empty", "")
        assert ctx.origin_size_bytes == 0
        restored = cr.restore("empty")
        assert restored == ""

    def test_compress_large_content(self):
        cr = ContextRecycling()
        content = "A" * 10000
        ctx = cr.compress("large", content)
        assert ctx.compression_ratio < 1.0
        restored = cr.restore("large")
        assert restored == content

    def test_export_and_import_json(self):
        cr = ContextRecycling()
        cr.compress("s1", "test data for export")
        cr.compress("s2", "another session")

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
            tmp_path = f.name

        try:
            cr.export_json(tmp_path)
            cr2 = ContextRecycling()
            count = cr2.import_json(tmp_path)
            assert count == 2
            assert cr2.restore("s1") == "test data for export"
            assert cr2.restore("s2") == "another session"
        finally:
            os.unlink(tmp_path)

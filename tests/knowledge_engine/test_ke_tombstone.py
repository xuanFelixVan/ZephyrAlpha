# [A_test] module_id: SRC-TST-1185 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] tests.test_ke_tombstone
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] test_ke_tombstone.py
# [TTL] task_bound

from __future__ import annotations

import sqlite3
from pathlib import Path

from zephyr.gov_kb.ke_tombstone import (
    TombstoneEntry,
    TombstoneManager,
)


class TestTombstoneManager:
    def _make_manager(self, tmp_path: Path) -> TombstoneManager:
        return TombstoneManager(project_root=tmp_path)

    def test_init_creates_table(self, tmp_path: Path):
        tm = self._make_manager(tmp_path)
        assert tm.init() is True
        conn = sqlite3.connect(str(tm.db_path))
        row = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ke_tombstones'").fetchone()
        conn.close()
        assert row is not None

    def test_init_idempotent(self, tmp_path: Path):
        tm = self._make_manager(tmp_path)
        assert tm.init() is True
        assert tm.init() is True

    def test_bury_and_is_buried(self, tmp_path: Path):
        tm = self._make_manager(tmp_path)
        tm.init()
        entry = tm.bury("KE-001", reason="duplicate")
        assert isinstance(entry, TombstoneEntry)
        assert entry.ke_id == "KE-001"
        assert entry.deletion_reason == "duplicate"
        assert tm.is_buried("KE-001") is True

    def test_is_buried_nonexistent(self, tmp_path: Path):
        tm = self._make_manager(tmp_path)
        tm.init()
        assert tm.is_buried("KE-999") is False

    def test_is_buried_by_hash(self, tmp_path: Path):
        tm = self._make_manager(tmp_path)
        tm.init()
        tm.bury("KE-002", reason="test", source_hash="abc123")
        assert tm.is_buried_by_hash("abc123") is True
        assert tm.is_buried_by_hash("not_found") is False

    def test_is_buried_by_hash_empty(self, tmp_path: Path):
        tm = self._make_manager(tmp_path)
        tm.init()
        assert tm.is_buried_by_hash("") is False

    def test_list(self, tmp_path: Path):
        tm = self._make_manager(tmp_path)
        tm.init()
        tm.bury("KE-010", reason="r1")
        tm.bury("KE-011", reason="r2")
        entries = tm.list()
        assert len(entries) == 2

    def test_list_include_purged(self, tmp_path: Path):
        tm = self._make_manager(tmp_path)
        tm.init()
        tm.bury("KE-020", reason="r")
        tm.purge(older_than_days=0)
        entries_no_purged = tm.list(include_purged=False)
        entries_with_purged = tm.list(include_purged=True)
        assert len(entries_with_purged) >= len(entries_no_purged)

    def test_count(self, tmp_path: Path):
        tm = self._make_manager(tmp_path)
        tm.init()
        assert tm.count() == 0
        tm.bury("KE-030", reason="r")
        assert tm.count() == 1

    def test_purge_old_entries(self, tmp_path: Path):
        tm = self._make_manager(tmp_path)
        tm.init()
        tm.bury("KE-040", reason="old")
        conn = tm._get_conn()
        old_time = "2020-01-01T00:00:00+00:00"
        conn.execute(
            "UPDATE ke_tombstones SET deletion_time = ? WHERE ke_id = ?",
            (old_time, "KE-040"),
        )
        conn.commit()
        conn.close()
        purged = tm.purge(older_than_days=365)
        assert purged >= 1

    def test_purge_no_old_entries(self, tmp_path: Path):
        tm = self._make_manager(tmp_path)
        tm.init()
        tm.bury("KE-050", reason="fresh")
        purged = tm.purge(older_than_days=9999)
        assert purged == 0

    def test_bury_with_all_fields(self, tmp_path: Path):
        tm = self._make_manager(tmp_path)
        tm.init()
        entry = tm.bury(
            "KE-060",
            reason="test",
            source_hash="sha256abc",
            chroma_id="chroma-1",
            vector_hash="vec123",
        )
        assert entry.source_hash == "sha256abc"
        assert entry.chroma_id == "chroma-1"
        assert entry.vector_hash == "vec123"

    def test_list_limit(self, tmp_path: Path):
        tm = self._make_manager(tmp_path)
        tm.init()
        for i in range(5):
            tm.bury(f"KE-L{i:03d}", reason="r")
        entries = tm.list(limit=3)
        assert len(entries) == 3

    def test_db_path(self, tmp_path: Path):
        tm = self._make_manager(tmp_path)
        assert "governance.db" in str(tm.db_path)

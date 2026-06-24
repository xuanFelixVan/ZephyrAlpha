# [A_test] module_id: SRC-TST-1173 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-KB-001 | docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md | §
# [MODULE] tests.test_kb_repo
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] test_kb_repo.py

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from zephyr.intelligence.model_evaluation.kb_repo import (
    KbRepo,
    KeRecord,
    KeStatus,
    RetrievalHit,
    TransitionResult,
    _compute_fingerprint,
)

_KNOWLEDGE_DDL = """
CREATE TABLE IF NOT EXISTS knowledge (
    ke_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    source_file TEXT NOT NULL,
    source_git_deleted INTEGER NOT NULL DEFAULT 0,
    fingerprint_sha256 TEXT,
    tags TEXT NOT NULL DEFAULT '[]',
    summary TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'DRAFT',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""

_EVENTS_DDL = """
CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY,
    event_type TEXT NOT NULL,
    payload TEXT,
    task_id TEXT,
    session_id TEXT,
    created_at TEXT NOT NULL
);
"""


def _init_test_db(db_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute(_KNOWLEDGE_DDL)
    conn.execute(_EVENTS_DDL)
    conn.commit()
    return conn


class TestKeStatus:
    def test_all_statuses_exist(self):
        expected = [
            "DRAFT",
            "SUBMITTED",
            "REVIEWED",
            "ACCEPTED",
            "INDEXED",
            "VERIFIED",
            "REJECTED",
            "DEPRECATED",
            "ARCHIVED",
            "SUPERSEDED",
        ]
        for name in expected:
            assert hasattr(KeStatus, name)

    def test_string_enum(self):
        assert KeStatus.DRAFT == "DRAFT"
        assert KeStatus.DRAFT.value == "DRAFT"


class TestComputeFingerprint:
    def test_deterministic(self):
        assert _compute_fingerprint("abc") == _compute_fingerprint("abc")

    def test_different_inputs(self):
        assert _compute_fingerprint("a") != _compute_fingerprint("b")

    def test_length(self):
        assert len(_compute_fingerprint("x")) == 64


class TestKeRecord:
    def test_valid_record(self):
        now = datetime.now()
        rec = KeRecord(
            ke_id="KE-001",
            title="Test",
            category="general",
            source_file="docs/a.md",
            created_at=now,
            updated_at=now,
        )
        assert rec.status == KeStatus.DRAFT

    def test_invalid_ke_id(self):
        now = datetime.now()
        with pytest.raises(Exception):
            KeRecord(
                ke_id="BAD-ID",
                title="T",
                category="c",
                source_file="f",
                created_at=now,
                updated_at=now,
            )

    def test_invalid_fingerprint_length(self):
        now = datetime.now()
        with pytest.raises(Exception):
            KeRecord(
                ke_id="KE-001",
                title="T",
                category="c",
                source_file="f",
                fingerprint_sha256="abc",
                created_at=now,
                updated_at=now,
            )


class TestKbRepoStateTransitions:
    def test_valid_transition(self):
        repo = KbRepo.__new__(KbRepo)
        assert repo.validate_state_transition(KeStatus.DRAFT, KeStatus.SUBMITTED) is True

    def test_invalid_transition(self):
        repo = KbRepo.__new__(KbRepo)
        assert repo.validate_state_transition(KeStatus.DRAFT, KeStatus.VERIFIED) is False

    def test_archived_has_no_transitions(self):
        repo = KbRepo.__new__(KbRepo)
        assert repo.validate_state_transition(KeStatus.ARCHIVED, KeStatus.DRAFT) is False

    def test_rejected_to_draft(self):
        repo = KbRepo.__new__(KbRepo)
        assert repo.validate_state_transition(KeStatus.REJECTED, KeStatus.DRAFT) is True


class TestKbRepoWithDb:
    def _make_repo(self, tmp_path: Path) -> KbRepo:
        db_path = tmp_path / "test.db"
        conn = _init_test_db(db_path)
        repo = KbRepo.__new__(KbRepo)
        repo._conn = conn
        repo._vector_dir = None
        repo._delete_vector = MagicMock(return_value=None)
        repo._upsert_vector = MagicMock(return_value=None)
        return repo

    def test_create_and_get(self, tmp_path: Path):
        repo = self._make_repo(tmp_path)
        rec = repo.create(
            ke_id="KE-001",
            title="Test KE",
            category="general",
            source_file="docs/a.md",
            content="hello world",
        )
        assert rec.ke_id == "KE-001"
        assert rec.status == KeStatus.DRAFT
        got = repo.get("KE-001")
        assert got is not None
        assert got.title == "Test KE"

    def test_get_nonexistent(self, tmp_path: Path):
        repo = self._make_repo(tmp_path)
        assert repo.get("KE-999") is None

    def test_transition_valid(self, tmp_path: Path):
        repo = self._make_repo(tmp_path)
        repo.create(
            ke_id="KE-002",
            title="T",
            category="c",
            source_file="f",
            content="c",
        )
        result = repo.transition("KE-002", KeStatus.SUBMITTED)
        assert isinstance(result, TransitionResult)
        assert result.from_status == KeStatus.DRAFT
        assert result.to_status == KeStatus.SUBMITTED

    def test_transition_invalid_raises(self, tmp_path: Path):
        repo = self._make_repo(tmp_path)
        repo.create(
            ke_id="KE-003",
            title="T",
            category="c",
            source_file="f",
            content="c",
        )
        with pytest.raises(ValueError, match="Invalid transition"):
            repo.transition("KE-003", KeStatus.VERIFIED)

    def test_transition_nonexistent_raises(self, tmp_path: Path):
        repo = self._make_repo(tmp_path)
        with pytest.raises(ValueError, match="KE not found"):
            repo.transition("KE-999", KeStatus.SUBMITTED)

    def test_list_by_status(self, tmp_path: Path):
        repo = self._make_repo(tmp_path)
        repo.create(ke_id="KE-010", title="A", category="c", source_file="f", content="a")
        repo.create(ke_id="KE-011", title="B", category="c", source_file="f", content="b")
        drafts = repo.list_by_status(KeStatus.DRAFT)
        assert len(drafts) == 2
        all_recs = repo.list_by_status()
        assert len(all_recs) == 2

    def test_delete(self, tmp_path: Path):
        repo = self._make_repo(tmp_path)
        repo.create(ke_id="KE-020", title="D", category="c", source_file="f", content="d")
        assert repo.delete("KE-020") is True
        assert repo.get("KE-020") is None

    def test_delete_nonexistent(self, tmp_path: Path):
        repo = self._make_repo(tmp_path)
        assert repo.delete("KE-999") is False

    def test_full_lifecycle(self, tmp_path: Path):
        repo = self._make_repo(tmp_path)
        repo.create(ke_id="KE-100", title="Life", category="c", source_file="f", content="x")
        repo.transition("KE-100", KeStatus.SUBMITTED)
        repo.transition("KE-100", KeStatus.REVIEWED)
        repo.transition("KE-100", KeStatus.ACCEPTED)
        repo.transition("KE-100", KeStatus.INDEXED)
        result = repo.transition("KE-100", KeStatus.VERIFIED)
        assert result.to_status == KeStatus.VERIFIED


class TestRetrievalHit:
    def test_creation(self):
        hit = RetrievalHit(chunk_id="c1", score=0.9, content="text")
        assert hit.chunk_id == "c1"
        assert hit.score == 0.9

    def test_score_bounds(self):
        with pytest.raises(Exception):
            RetrievalHit(chunk_id="c1", score=1.5, content="t")

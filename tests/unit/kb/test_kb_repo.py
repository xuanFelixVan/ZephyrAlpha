# [A_test] module_id: SRC-TST-1904 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-523 | docs/03_modules/_domain-governance/blueprint.md | §
# [MODULE] tests.unit.kb.test_kb_repo
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""
Unit tests for kb_repo.py (T-2-11-A)
"""

from pathlib import Path

import pytest

from zephyr.governance.kb.chromadb_init import init_chromadb
from zephyr.governance.persistence.sqlite_schema import init_db
from zephyr.intelligence.model_evaluation.kb_repo import KbRepo, KeStatus


@pytest.fixture
def tmp_db(tmp_path: Path) -> Path:
    db = tmp_path / "test.db"
    init_db(db)
    init_chromadb(tmp_path / "vectors")
    return db


@pytest.fixture
def repo(tmp_db: Path, tmp_path: Path) -> KbRepo:
    return KbRepo(db_path=tmp_db, vector_dir=tmp_path / "vectors")


class TestKbRepoCreate:
    def test_create_draft(self, repo: KbRepo) -> None:
        rec = repo.create(
            ke_id="KE-001",
            title="Test KE",
            category="best_practice",
            source_file="docs/test.md",
            content="hello world",
        )
        assert rec.ke_id == "KE-001"
        assert rec.status == KeStatus.DRAFT
        assert rec.fingerprint_sha256 is not None
        assert len(rec.fingerprint_sha256) == 64

    def test_create_and_get(self, repo: KbRepo) -> None:
        repo.create(
            ke_id="KE-002",
            title="Another KE",
            category="lesson_learned",
            source_file="docs/lesson.md",
            content="lesson content",
            tags=["encoding", "bug"],
            summary="A lesson about encoding",
        )
        rec = repo.get("KE-002")
        assert rec is not None
        assert rec.title == "Another KE"
        assert rec.category == "lesson_learned"
        assert rec.tags == ["encoding", "bug"]
        assert rec.summary == "A lesson about encoding"

    def test_get_nonexistent(self, repo: KbRepo) -> None:
        assert repo.get("KE-999") is None


class TestKbRepoTransition:
    def test_valid_forward_transition(self, repo: KbRepo) -> None:
        repo.create(
            ke_id="KE-010",
            title="Transition test",
            category="general",
            source_file="docs/t.md",
            content="content",
        )
        result = repo.transition("KE-010", KeStatus.SUBMITTED)
        assert result.from_status == KeStatus.DRAFT
        assert result.to_status == KeStatus.SUBMITTED

        rec = repo.get("KE-010")
        assert rec is not None
        assert rec.status == KeStatus.SUBMITTED

    def test_full_lifecycle(self, repo: KbRepo) -> None:
        repo.create(
            ke_id="KE-011",
            title="Full lifecycle",
            category="general",
            source_file="docs/lc.md",
            content="lifecycle content",
        )
        for target in [KeStatus.SUBMITTED, KeStatus.REVIEWED, KeStatus.ACCEPTED, KeStatus.INDEXED, KeStatus.VERIFIED]:
            result = repo.transition("KE-011", target, content="lifecycle content")
            assert result.to_status == target

        rec = repo.get("KE-011")
        assert rec is not None
        assert rec.status == KeStatus.VERIFIED

    def test_reject_and_resubmit(self, repo: KbRepo) -> None:
        repo.create(
            ke_id="KE-012",
            title="Reject test",
            category="general",
            source_file="docs/rj.md",
            content="reject content",
        )
        repo.transition("KE-012", KeStatus.SUBMITTED)
        result = repo.transition("KE-012", KeStatus.REJECTED)
        assert result.to_status == KeStatus.REJECTED

        result2 = repo.transition("KE-012", KeStatus.DRAFT)
        assert result2.to_status == KeStatus.DRAFT

    def test_invalid_transition(self, repo: KbRepo) -> None:
        repo.create(
            ke_id="KE-013",
            title="Invalid test",
            category="general",
            source_file="docs/inv.md",
            content="invalid",
        )
        with pytest.raises(ValueError, match="Invalid transition"):
            repo.transition("KE-013", KeStatus.VERIFIED)

    def test_transition_nonexistent(self, repo: KbRepo) -> None:
        with pytest.raises(ValueError, match="KE not found"):
            repo.transition("KE-999", KeStatus.SUBMITTED)

    def test_deprecated_to_archived(self, repo: KbRepo) -> None:
        repo.create(
            ke_id="KE-014",
            title="Deprecation",
            category="general",
            source_file="docs/dep.md",
            content="deprecated content",
        )
        for s in [
            KeStatus.SUBMITTED,
            KeStatus.REVIEWED,
            KeStatus.ACCEPTED,
            KeStatus.INDEXED,
            KeStatus.VERIFIED,
            KeStatus.DEPRECATED,
        ]:
            repo.transition("KE-014", s, content="deprecated content")

        result = repo.transition("KE-014", KeStatus.ARCHIVED)
        assert result.to_status == KeStatus.ARCHIVED

    def test_superseded_to_archived(self, repo: KbRepo) -> None:
        repo.create(
            ke_id="KE-015",
            title="Superseded",
            category="general",
            source_file="docs/sup.md",
            content="superseded content",
        )
        for s in [
            KeStatus.SUBMITTED,
            KeStatus.REVIEWED,
            KeStatus.ACCEPTED,
            KeStatus.INDEXED,
            KeStatus.VERIFIED,
            KeStatus.SUPERSEDED,
        ]:
            repo.transition("KE-015", s, content="superseded content")

        result = repo.transition("KE-015", KeStatus.ARCHIVED)
        assert result.to_status == KeStatus.ARCHIVED

    def test_archived_is_terminal(self, repo: KbRepo) -> None:
        repo.create(
            ke_id="KE-016",
            title="Terminal",
            category="general",
            source_file="docs/term.md",
            content="terminal",
        )
        for s in [
            KeStatus.SUBMITTED,
            KeStatus.REVIEWED,
            KeStatus.ACCEPTED,
            KeStatus.INDEXED,
            KeStatus.VERIFIED,
            KeStatus.DEPRECATED,
            KeStatus.ARCHIVED,
        ]:
            repo.transition("KE-016", s, content="terminal")

        with pytest.raises(ValueError, match="Invalid transition"):
            repo.transition("KE-016", KeStatus.DRAFT)


class TestKbRepoList:
    def test_list_all(self, repo: KbRepo) -> None:
        repo.create(ke_id="KE-020", title="A", category="g", source_file="a.md", content="a")
        repo.create(ke_id="KE-021", title="B", category="g", source_file="b.md", content="b")
        records = repo.list_by_status()
        assert len(records) == 2

    def test_list_by_status(self, repo: KbRepo) -> None:
        repo.create(ke_id="KE-030", title="C", category="g", source_file="c.md", content="c")
        repo.create(ke_id="KE-031", title="D", category="g", source_file="d.md", content="d")
        repo.transition("KE-030", KeStatus.SUBMITTED)

        drafts = repo.list_by_status(KeStatus.DRAFT)
        submitted = repo.list_by_status(KeStatus.SUBMITTED)
        assert len(drafts) == 1
        assert len(submitted) == 1


class TestKbRepoDelete:
    def test_delete(self, repo: KbRepo) -> None:
        repo.create(ke_id="KE-040", title="Del", category="g", source_file="del.md", content="del")
        assert repo.delete("KE-040") is True
        assert repo.get("KE-040") is None

    def test_delete_nonexistent(self, repo: KbRepo) -> None:
        assert repo.delete("KE-999") is False


class TestVectorAction:
    def test_upsert_on_indexed(self, repo: KbRepo) -> None:
        repo.create(ke_id="KE-050", title="Vec", category="g", source_file="v.md", content="vec content")
        for s in [KeStatus.SUBMITTED, KeStatus.REVIEWED, KeStatus.ACCEPTED]:
            repo.transition("KE-050", s)
        result = repo.transition("KE-050", KeStatus.INDEXED, content="vec content")
        assert result.vector_action == "upsert"

    def test_delete_on_archived(self, repo: KbRepo) -> None:
        repo.create(ke_id="KE-051", title="Vec2", category="g", source_file="v2.md", content="vec2")
        for s in [
            KeStatus.SUBMITTED,
            KeStatus.REVIEWED,
            KeStatus.ACCEPTED,
            KeStatus.INDEXED,
            KeStatus.VERIFIED,
            KeStatus.DEPRECATED,
        ]:
            repo.transition("KE-051", s, content="vec2")
        result = repo.transition("KE-051", KeStatus.ARCHIVED)
        assert result.vector_action == "delete"

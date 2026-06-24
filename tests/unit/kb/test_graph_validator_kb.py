# [A_test] module_id: SRC-TST-1902 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-521 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.kb.test_graph_validator
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
"""
Unit tests for graph_validator.py (T-2-11-C)
"""

from pathlib import Path

import pytest

from zephyr.governance.kb.chromadb_init import init_chromadb
from zephyr.governance.kb.graph_validator import GraphValidator, ValidationSeverity
from zephyr.governance.persistence.sqlite_schema import init_db
from zephyr.intelligence.model_evaluation.kb_repo import KbRepo, KeStatus


@pytest.fixture
def env(tmp_path: Path):
    db = tmp_path / "test.db"
    vec = tmp_path / "vectors"
    init_db(db)
    init_chromadb(vec)
    repo = KbRepo(db_path=db, vector_dir=vec)
    validator = GraphValidator(db_path=db, vector_dir=vec)
    yield repo, validator
    import zephyr.data.knowledge_management.kb.chromadb_init as mod

    mod._chroma_client = None


class TestGraphValidatorEmpty:
    def test_empty_db_passes(self, env) -> None:
        _, validator = env
        report = validator.validate()
        assert report.passed is True
        assert report.total_checked == 0
        assert report.error_count == 0


class TestGraphValidatorOrphanNodes:
    def test_indexed_ke_in_vector(self, env) -> None:
        repo, validator = env
        repo.create(ke_id="KE-100", title="Orphan", category="g", source_file="o.md", content="orphan")
        for s in [KeStatus.SUBMITTED, KeStatus.REVIEWED, KeStatus.ACCEPTED]:
            repo.transition("KE-100", s)
        repo.transition("KE-100", KeStatus.INDEXED, content="orphan")

        report = validator.validate()
        gv001 = [i for i in report.issues if i.check_id == "GV-001"]
        assert len(gv001) == 0

    def test_ke_in_vector_not_in_db(self, env) -> None:
        repo, validator = env
        from zephyr.governance.kb.chromadb_init import get_chroma_client

        client = get_chroma_client(validator._vector_dir)
        col = client.get_collection(name="ke_entries")
        col.upsert(
            ids=["KE-999-chunk-0"],
            documents=["ghost content"],
            metadatas=[{"ke_id": "KE-999", "category": "g", "status": "INDEXED"}],
        )

        report = validator.validate()
        gv002 = [i for i in report.issues if i.check_id == "GV-002"]
        assert len(gv002) == 1
        assert gv002[0].severity == ValidationSeverity.ERROR


class TestGraphValidatorDuplicateFingerprints:
    def test_duplicate_fingerprint(self, env) -> None:
        repo, validator = env
        repo.create(ke_id="KE-200", title="Dup A", category="g", source_file="a.md", content="same content")
        repo.create(ke_id="KE-201", title="Dup B", category="g", source_file="b.md", content="same content")

        report = validator.validate()
        gv005 = [i for i in report.issues if i.check_id == "GV-005"]
        assert len(gv005) == 1
        assert gv005[0].severity == ValidationSeverity.WARNING


class TestGraphValidatorVectorStatus:
    def test_vector_metadata_mismatch(self, env) -> None:
        repo, validator = env
        repo.create(ke_id="KE-300", title="Mismatch", category="g", source_file="m.md", content="mismatch")
        for s in [KeStatus.SUBMITTED, KeStatus.REVIEWED, KeStatus.ACCEPTED]:
            repo.transition("KE-300", s)
        repo.transition("KE-300", KeStatus.INDEXED, content="mismatch")

        from zephyr.governance.kb.chromadb_init import get_chroma_client

        client = get_chroma_client(validator._vector_dir)
        col = client.get_collection(name="ke_entries")
        col.upsert(
            ids=["KE-300-chunk-0"],
            documents=["mismatch"],
            metadatas=[{"ke_id": "KE-300", "category": "g", "status": "DRAFT"}],
        )

        report = validator.validate()
        gv006 = [i for i in report.issues if i.check_id == "GV-006"]
        assert len(gv006) == 1


class TestGraphValidatorClean:
    def test_clean_db_no_errors(self, env) -> None:
        repo, validator = env
        repo.create(ke_id="KE-400", title="Clean", category="g", source_file="c.md", content="clean")
        report = validator.validate()
        errors = [i for i in report.issues if i.severity == ValidationSeverity.ERROR]
        assert len(errors) == 0

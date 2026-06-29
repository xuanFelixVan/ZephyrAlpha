# [A_test] module_id: SRC-TST-1902 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-521 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.kb.test_graph_validator
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
Unit tests for graph_validator.py (T-2-11-C)
"""

from pathlib import Path

import pytest

from zephyr.governance.kb.chromadb_init import init_chromadb
from zephyr.governance.kb.graph_validator import GraphValidator, ValidationSeverity
from zephyr.governance.persistence.sqlite_schema import init_db


@pytest.fixture
def env(tmp_path: Path):
    db = tmp_path / "test.db"
    vec = tmp_path / "vectors"
    init_db(db)
    init_chromadb(vec)
    validator = GraphValidator(db_path=db, vector_dir=vec)
    yield validator
    import zephyr.data.knowledge_management.kb.chromadb_init as mod

    mod._chroma_client = None


class TestGraphValidatorEmpty:
    def test_empty_db_passes(self, env) -> None:
        validator = env
        report = validator.validate()
        assert report.passed is True
        assert report.total_checked == 0
        assert report.error_count == 0


class TestGraphValidatorOrphanNodes:
    def test_ke_in_vector_not_in_db(self, env) -> None:
        validator = env
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

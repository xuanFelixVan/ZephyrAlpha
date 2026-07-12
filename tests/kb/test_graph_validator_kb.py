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

from zephyr.gov_kb.graph_validator import GraphValidator, ValidationSeverity
from zephyr.governance.persistence.sqlite_schema import init_db


@pytest.fixture
def env(tmp_path: Path):
    db = tmp_path / "test.db"
    vec = tmp_path / "vectors"
    init_db(db)
    validator = GraphValidator(db_path=db, vector_dir=vec)
    yield validator


class TestGraphValidatorEmpty:
    def test_empty_db_passes(self, env) -> None:
        validator = env
        report = validator.validate()
        assert report.passed is True
        assert report.total_checked == 0
        assert report.error_count == 0

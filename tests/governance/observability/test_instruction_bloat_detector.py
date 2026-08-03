# [A_test] module_id: MOD-GOV_instruction_bloat_detector | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-024 | docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md | §
# [MODULE] tests.test_instruction_bloat_detector
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] scan returns list of InstructionMetrics; summary returns dict
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [A_module] module_id=MOD-INF-024 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.governance.context_governance.instruction_bloat_detector import (
    BloatLevel,
    CompactSuggestion,
    InstructionBloatDetector,
    InstructionMetrics,
)


@pytest.fixture
def tmp_history_path(tmp_path):
    return str(tmp_path / "bloat_history.json")


@pytest.fixture
def detector(tmp_history_path):
    return InstructionBloatDetector(
        targets=["test_file.md"],
        session_budget=10000.0,
        history_path=tmp_history_path,
    )


@pytest.fixture
def project_with_file(tmp_path):
    content = "Hello world " * 50
    p = tmp_path / "test_file.md"
    p.write_text(content, encoding="utf-8")
    return str(tmp_path)


@pytest.fixture
def project_with_large_file(tmp_path):
    content = "# Section 1\n" + "line\n" * 3000
    p = tmp_path / "test_file.md"
    p.write_text(content, encoding="utf-8")
    return str(tmp_path)


class TestInstructionBloatDetector:
    def test_instantiation_defaults(self, tmp_history_path):
        det = InstructionBloatDetector(history_path=tmp_history_path)
        s = det.summary()
        assert s["session_budget"] == 1_000_000.0

    def test_instantiation_custom(self, detector):
        s = detector.summary()
        assert s["targets_monitored"] == 1

    def test_scan_missing_file(self, detector, tmp_path):
        results = detector.scan(project_root=str(tmp_path))
        assert len(results) == 1
        assert results[0].level == BloatLevel.NORMAL
        assert results[0].message == "file not found"

    def test_scan_existing_file(self, detector, project_with_file):
        results = detector.scan(project_root=project_with_file)
        assert len(results) == 1
        assert results[0].token_count > 0
        assert results[0].byte_count > 0

    def test_scan_oversized_file(self, tmp_history_path, project_with_large_file):
        det = InstructionBloatDetector(
            targets=["test_file.md"],
            session_budget=1000.0,
            history_path=tmp_history_path,
        )
        results = det.scan(project_root=project_with_large_file)
        assert results[0].level == BloatLevel.OVERSIZED

    def test_suggest_compact_no_file(self, detector, tmp_path):
        suggestions = detector.suggest_compact(project_root=str(tmp_path))
        assert len(suggestions) == 0

    def test_suggest_compact_with_large_sections(self, detector, project_with_large_file):
        suggestions = detector.suggest_compact(project_root=project_with_large_file)
        if len(suggestions) > 0:
            assert isinstance(suggestions[0], CompactSuggestion)
            assert suggestions[0].current_tokens > 0

    def test_summary(self, detector):
        s = detector.summary()
        assert "targets_monitored" in s
        assert "history_entries" in s
        assert "session_budget" in s

    def test_history_persistence(self, tmp_history_path, project_with_file):
        det1 = InstructionBloatDetector(
            targets=["test_file.md"],
            session_budget=10000.0,
            history_path=tmp_history_path,
        )
        det1.scan(project_root=project_with_file)
        det2 = InstructionBloatDetector(
            targets=["test_file.md"],
            session_budget=10000.0,
            history_path=tmp_history_path,
        )
        assert det2.summary()["history_entries"] > 0


class TestBoundaryCases:
    def test_scan_empty_project(self, detector, tmp_path):
        results = detector.scan(project_root=str(tmp_path))
        assert all(isinstance(r, InstructionMetrics) for r in results)

    def test_scan_with_empty_targets(self, tmp_history_path, tmp_path):
        det = InstructionBloatDetector(targets=[], history_path=tmp_history_path)
        results = det.scan(project_root=str(tmp_path))
        assert isinstance(results, list)

    def test_instruction_metrics_defaults(self):
        m = InstructionMetrics(target_path="test")
        assert m.token_count == 0
        assert m.level == BloatLevel.NORMAL

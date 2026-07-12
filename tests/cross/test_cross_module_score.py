# [A_test] module_id: SRC-TST-0648 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_cross_module_score
# [INVARIANTS] 跨模块评分不可人为调整
# [MODIFY-GUARD] blueprint.md §4; __init__.py __all__
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftError;BaselineError
# [TESTS] tests/test_cross_module_score.py
# [TTL] task_bound

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from zephyr.gov_drift.cross_module_score import (
    CrossModuleReport,
    CrossModuleScorer,
    ModuleScore,
)


class TestModuleScore:
    def test_default_fields(self):
        ms = ModuleScore(module_id="MOD-001", health_index=0.85)
        assert ms.module_id == "MOD-001"
        assert ms.health_index == 0.85
        assert ms.active_drifts == 0
        assert ms.last_resolved_at is None
        assert ms.rustiness_factor == 0.0
        assert ms.category_score == {}

    def test_custom_fields(self):
        now = datetime.now(UTC)
        ms = ModuleScore(
            module_id="MOD-002",
            health_index=0.5,
            active_drifts=3,
            last_resolved_at=now,
            rustiness_factor=0.2,
            category_score={"perf": 0.7},
        )
        assert ms.active_drifts == 3
        assert ms.last_resolved_at == now
        assert ms.rustiness_factor == 0.2
        assert ms.category_score["perf"] == 0.7


class TestCrossModuleReport:
    def test_default_fields(self):
        report = CrossModuleReport(overall_score=0.9)
        assert report.overall_score == 0.9
        assert report.module_scores == {}
        assert report.worst_modules == []
        assert report.rustiness_warnings == []

    def test_custom_fields(self):
        ms = ModuleScore(module_id="M1", health_index=0.5)
        report = CrossModuleReport(
            overall_score=0.75,
            module_scores={"M1": ms},
            worst_modules=["M1"],
            rustiness_warnings=["M1"],
        )
        assert "M1" in report.module_scores
        assert report.worst_modules == ["M1"]


class TestCrossModuleScorer:
    def test_compute_empty_returns_perfect(self):
        scorer = CrossModuleScorer()
        report = scorer.compute({})
        assert report.overall_score == 1.0
        assert report.module_scores == {}
        assert report.worst_modules == []

    def test_compute_single_module_healthy(self):
        scorer = CrossModuleScorer()
        now = datetime.now(UTC)
        ms = ModuleScore(
            module_id="MOD-A",
            health_index=0.95,
            last_resolved_at=now,
        )
        report = scorer.compute({"MOD-A": ms})
        assert report.overall_score > 0.0
        assert "MOD-A" in report.module_scores

    def test_compute_rustiness_with_old_resolution(self):
        scorer = CrossModuleScorer()
        old = datetime.now(UTC) - timedelta(days=80)
        ms = ModuleScore(
            module_id="MOD-OLD",
            health_index=0.9,
            last_resolved_at=old,
        )
        report = scorer.compute({"MOD-OLD": ms})
        assert ms.rustiness_factor > 0.0
        assert "MOD-OLD" in report.rustiness_warnings

    def test_compute_rustiness_none_gives_max(self):
        scorer = CrossModuleScorer()
        ms = ModuleScore(module_id="MOD-NONE", health_index=0.9, last_resolved_at=None)
        scorer.compute({"MOD-NONE": ms})
        assert ms.rustiness_factor == 1.0

    def test_compute_rustiness_recent_gives_zero(self):
        scorer = CrossModuleScorer()
        recent = datetime.now(UTC) - timedelta(days=5)
        ms = ModuleScore(module_id="MOD-RECENT", health_index=0.9, last_resolved_at=recent)
        scorer.compute({"MOD-RECENT": ms})
        assert ms.rustiness_factor == 0.0

    def test_compute_worst_modules_sorted(self):
        scorer = CrossModuleScorer()
        now = datetime.now(UTC)
        ms_low = ModuleScore(module_id="LOW", health_index=0.2, last_resolved_at=now)
        ms_high = ModuleScore(module_id="HIGH", health_index=0.95, last_resolved_at=now)
        ms_mid = ModuleScore(module_id="MID", health_index=0.6, last_resolved_at=now)
        ms_extra = ModuleScore(module_id="EXTRA", health_index=0.7, last_resolved_at=now)
        report = scorer.compute({"LOW": ms_low, "HIGH": ms_high, "MID": ms_mid, "EXTRA": ms_extra})
        assert len(report.worst_modules) == 3
        assert report.worst_modules[0] == "LOW"

    def test_compute_history_appended(self):
        scorer = CrossModuleScorer()
        now = datetime.now(UTC)
        ms = ModuleScore(module_id="M1", health_index=0.8, last_resolved_at=now)
        scorer.compute({"M1": ms})
        scorer.compute({"M1": ms})
        assert len(scorer._history) == 2

    def test_check_thresholds_disaster(self):
        scorer = CrossModuleScorer()
        report = CrossModuleReport(overall_score=0.0)
        result = scorer.check_thresholds(report)
        assert result["status"] == "DISASTER"

    def test_check_thresholds_bad(self):
        scorer = CrossModuleScorer()
        report = CrossModuleReport(overall_score=0.2)
        result = scorer.check_thresholds(report)
        assert result["status"] == "BAD"

    def test_check_thresholds_warning(self):
        scorer = CrossModuleScorer()
        report = CrossModuleReport(overall_score=0.5)
        result = scorer.check_thresholds(report)
        assert result["status"] == "WARNING"

    def test_check_thresholds_pass(self):
        scorer = CrossModuleScorer()
        report = CrossModuleReport(overall_score=0.85)
        result = scorer.check_thresholds(report)
        assert result["status"] == "PASS"

    def test_check_thresholds_golden(self):
        scorer = CrossModuleScorer()
        report = CrossModuleReport(overall_score=0.95)
        result = scorer.check_thresholds(report)
        assert result["status"] == "GOLDEN"

    def test_check_thresholds_boundary_allowed(self):
        scorer = CrossModuleScorer()
        report = CrossModuleReport(overall_score=0.35)
        result = scorer.check_thresholds(report)
        assert result["status"] == "BAD"

    def test_check_thresholds_boundary_warning(self):
        scorer = CrossModuleScorer()
        report = CrossModuleReport(overall_score=0.60)
        result = scorer.check_thresholds(report)
        assert result["status"] == "WARNING"

    def test_check_thresholds_boundary_gate_pass(self):
        scorer = CrossModuleScorer()
        report = CrossModuleReport(overall_score=0.90)
        result = scorer.check_thresholds(report)
        assert result["status"] == "GOLDEN"

    def test_compute_rustiness_cap_at_one(self):
        scorer = CrossModuleScorer()
        very_old = datetime.now(UTC) - timedelta(days=500)
        ms = ModuleScore(module_id="VERY-OLD", health_index=0.9, last_resolved_at=very_old)
        scorer.compute({"VERY-OLD": ms})
        assert ms.rustiness_factor <= 1.0

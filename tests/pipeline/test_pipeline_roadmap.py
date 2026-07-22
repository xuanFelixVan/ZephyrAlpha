# [A_test] module_id: MOD-GOV_pipeline_roadmap | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] tests.test_pipeline_roadmap
# [INVARIANTS] ConstructionPhaseTracker total = IMPLEMENTED + BACKLOG + PLANNED_VERSIONS; ROICalculator denominator >= 0.01; MutationTestResult mutation_score = killed/total when total > 0
# [MODIFY-GUARD] PROFILES/PIPELINE_DEPENDENCIES/PIPELINE_VERSION_MAP changes require test updates
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ROICalculator.ratio_for_module returns (saved-invested)/max(invested,0.01); DependencyHealthChecker.missing_required auto-runs check_all
# [TESTS] pytest tests/test_pipeline_roadmap.py
# [TTL] task_bound

from __future__ import annotations

import json
from dataclasses import dataclass

import pytest

from zephyr.infrastructure.pipeline.pipeline_roadmap import (  # 治本(2026-06-30): integration 副本已删除, 改从 infrastructure 真源导入
    PIPELINE_DEPENDENCIES,
    PIPELINE_VERSION_MAP,
    PROFILES,
    BlueprintCodeDriftChecker,
    BlueprintCodeDriftEntry,
    ConstructionPhaseTracker,
    DependencyHealthChecker,
    DriftReport,
    ErrorBudget,
    HealthReport,
    MutationTestResult,
    OrchestratorIntegrationBridge,
    PipelineOrchestratorRoadmapMixin,
    ROICalculator,
    SessionBrief,
    SLOMetric,
    SLOState,
    select_profile,
)


class TestConstructionPhaseTracker:
    def test_total_entries(self):
        tracker = ConstructionPhaseTracker()
        expected = len(tracker.IMPLEMENTED) + len(tracker.BACKLOG) + len(tracker.PLANNED_VERSIONS)
        assert tracker.total_entries == expected

    def test_implemented_count(self):
        tracker = ConstructionPhaseTracker()
        assert tracker.implemented_count == len(tracker.IMPLEMENTED)

    def test_get_completion_pct(self):
        tracker = ConstructionPhaseTracker()
        pct = tracker.get_completion_pct()
        assert pct > 0.0
        assert pct <= 100.0
        expected_pct = len(tracker.IMPLEMENTED) / tracker.total_entries * 100
        assert abs(pct - expected_pct) < 0.01

    def test_get_next_priority_returns_backlog_items(self):
        tracker = ConstructionPhaseTracker()
        next_items = tracker.get_next_priority()
        assert len(next_items) > 0
        for item in next_items:
            assert item.status.startswith("📋")

    def test_phases_dict_populated(self):
        tracker = ConstructionPhaseTracker()
        assert len(tracker.phases) == tracker.total_entries

    def test_implemented_items_have_status(self):
        tracker = ConstructionPhaseTracker()
        for key in tracker.IMPLEMENTED:
            assert tracker.phases[key].status == "✅ implemented"


class TestDependencyHealthChecker:
    def test_check_all_returns_dict(self):
        checker = DependencyHealthChecker()
        results = checker.check_all()
        assert isinstance(results, dict)
        assert len(results) == len(PIPELINE_DEPENDENCIES)

    def test_check_all_runtime_call_always_true(self):
        checker = DependencyHealthChecker()
        results = checker.check_all()
        for dep in PIPELINE_DEPENDENCIES:
            if dep.relation in ("runtime_call", "pre_check"):
                assert results[dep.module_id] is True

    def test_missing_required_returns_list(self):
        checker = DependencyHealthChecker()
        missing = checker.missing_required()
        assert isinstance(missing, list)
        for mod_id in missing:
            assert isinstance(mod_id, str)

    def test_missing_required_auto_runs_check(self):
        checker = DependencyHealthChecker()
        assert checker.last_check == {}
        checker.missing_required()
        assert len(checker.last_check) > 0


class TestROICalculator:
    def test_roi_for_module_with_data(self):
        calc = ROICalculator(
            cost_saved_by_module={"MOD-X": 100.0},
            cost_invested_by_module={"MOD-X": 50.0},
        )
        roi = calc.roi_for_module("MOD-X")
        assert roi == pytest.approx(1.0)

    def test_roi_for_module_missing_module(self):
        calc = ROICalculator(
            cost_saved_by_module={},
            cost_invested_by_module={},
        )
        roi = calc.roi_for_module("NONEXISTENT")
        assert roi == pytest.approx(-1.0)

    def test_roi_for_module_zero_invested(self):
        calc = ROICalculator(
            cost_saved_by_module={"MOD-X": 100.0},
            cost_invested_by_module={"MOD-X": 0.0},
        )
        roi = calc.roi_for_module("MOD-X")
        assert roi == pytest.approx(100.0 / 0.01)

    def test_roi_negative_when_cost_exceeds_savings(self):
        calc = ROICalculator(
            cost_saved_by_module={"MOD-X": 10.0},
            cost_invested_by_module={"MOD-X": 50.0},
        )
        roi = calc.roi_for_module("MOD-X")
        assert roi < 0


class TestMutationTestResult:
    def test_mutation_score_with_data(self):
        result = MutationTestResult(total_mutants=100, killed=80, survived=20)
        assert result.mutation_score == pytest.approx(0.8)

    def test_mutation_score_zero_total(self):
        result = MutationTestResult(total_mutants=0, killed=0, survived=0)
        assert result.mutation_score == 0.0

    def test_mutation_score_perfect(self):
        result = MutationTestResult(total_mutants=50, killed=50, survived=0)
        assert result.mutation_score == pytest.approx(1.0)

    def test_mutation_score_zero_killed(self):
        result = MutationTestResult(total_mutants=50, killed=0, survived=50)
        assert result.mutation_score == pytest.approx(0.0)


class TestHealthReport:
    def test_as_json(self):
        report = HealthReport(
            overall_status="healthy",
            open_circuit_breakers=0,
            dead_letter_count=0,
            cost_total_usd=1.2345,
            self_healing_suggestions=["restart"],
        )
        parsed = json.loads(report.as_json())
        assert parsed["overall_status"] == "healthy"
        assert parsed["open_circuit_breakers"] == 0
        assert parsed["cost_total_usd"] == 1.2345
        assert parsed["self_healing_suggestions"] == ["restart"]

    def test_as_markdown(self):
        report = HealthReport(
            overall_status="degraded",
            open_circuit_breakers=2,
            dead_letter_count=5,
            cost_total_usd=10.0,
            self_healing_suggestions=["check M3", "restart"],
        )
        md = report.as_markdown()
        assert "degraded" in md
        assert "2" in md
        assert "5" in md
        assert "Self-Healing Suggestions" in md

    def test_as_markdown_no_suggestions(self):
        report = HealthReport(overall_status="healthy")
        md = report.as_markdown()
        assert "Self-Healing Suggestions" not in md

    def test_default_values(self):
        report = HealthReport()
        assert report.overall_status == "healthy"
        assert report.open_circuit_breakers == 0
        assert report.dead_letter_count == 0
        assert report.cost_total_usd == 0.0
        assert report.self_healing_suggestions == []


class TestDriftReport:
    def test_has_drifts_empty(self):
        report = DriftReport()
        assert report.has_drifts() is False

    def test_has_drifts_with_entries(self):
        entry = BlueprintCodeDriftEntry(
            claim_path="some/path",
            expected="expected_val",
            actual="actual_val",
        )
        report = DriftReport(drifts=[entry])
        assert report.has_drifts() is True

    def test_empty_drifts_list(self):
        report = DriftReport(drifts=[])
        assert report.has_drifts() is False


class TestBlueprintCodeDriftChecker:
    def test_check_returns_empty_drift_report(self):
        checker = BlueprintCodeDriftChecker()
        report = checker.check([], [])
        assert isinstance(report, DriftReport)
        assert report.has_drifts() is False


class TestSelectProfile:
    def test_audit_p0_returns_audit_strict(self):
        @dataclass
        class MockCard:
            task_type: str = "AUDIT"
            priority: str = "P0"

        profile = select_profile(MockCard())
        assert profile.name == "audit_strict"

    def test_audit_p1_returns_audit_strict(self):
        @dataclass
        class MockCard:
            task_type: str = "AUDIT"
            priority: str = "P1"

        profile = select_profile(MockCard())
        assert profile.name == "audit_strict"

    def test_doc_write_returns_doc_fast(self):
        @dataclass
        class MockCard:
            task_type: str = "DOC_WRITE"
            priority: str = "P2"

        profile = select_profile(MockCard())
        assert profile.name == "doc_fast"

    def test_refactor_returns_doc_fast(self):
        @dataclass
        class MockCard:
            task_type: str = "REFACTOR"
            priority: str = "P2"

        profile = select_profile(MockCard())
        assert profile.name == "doc_fast"

    def test_p3_returns_batch_low(self):
        @dataclass
        class MockCard:
            task_type: str = "OTHER"
            priority: str = "P3"

        profile = select_profile(MockCard())
        assert profile.name == "batch_low"

    def test_default_returns_audit_strict(self):
        @dataclass
        class MockCard:
            task_type: str = "UNKNOWN"
            priority: str = "P2"

        profile = select_profile(MockCard())
        assert profile.name == "audit_strict"


class TestProfiles:
    def test_has_expected_keys(self):
        assert "audit_strict" in PROFILES
        assert "doc_fast" in PROFILES
        assert "batch_low" in PROFILES

    def test_audit_strict_profile(self):
        assert PROFILES["audit_strict"].gate_profile == "full_g0_g7"

    def test_doc_fast_skips_modules(self):
        assert "M7" in PROFILES["doc_fast"].skip_modules
        assert "M8" in PROFILES["doc_fast"].skip_modules

    def test_batch_low_has_window(self):
        assert PROFILES["batch_low"].batch_window_s == 1800


class TestPipelineDependencies:
    def test_has_entries(self):
        assert len(PIPELINE_DEPENDENCIES) > 0

    def test_all_have_module_id(self):
        for dep in PIPELINE_DEPENDENCIES:
            assert dep.module_id
            assert dep.module_name


class TestPipelineVersionMap:
    def test_has_expected_versions(self):
        expected = ["v0.8.0", "v0.9.0", "v0.10.0", "v0.11.0", "v0.12.0"]
        for v in expected:
            assert v in PIPELINE_VERSION_MAP

    def test_entries_have_section(self):
        for version, info in PIPELINE_VERSION_MAP.items():
            assert "section" in info
            assert "audit_round" in info
            assert "b_range" in info


class TestSLOMetric:
    def test_creation(self):
        metric = SLOMetric(
            module_id="MOD-X",
            p95_latency_ms=100.0,
            availability_pct=99.9,
            error_rate_pct=0.1,
        )
        assert metric.module_id == "MOD-X"
        assert metric.p95_latency_ms == 100.0
        assert metric.availability_pct == 99.9
        assert metric.error_rate_pct == 0.1


class TestErrorBudget:
    def test_creation_with_defaults(self):
        budget = ErrorBudget(module_id="MOD-X")
        assert budget.target_slo == 99.9
        assert budget.budget_remaining_pct == 100.0
        assert budget.burn_rate == 0.0
        assert budget.state == SLOState.HEALTHY

    def test_creation_custom(self):
        budget = ErrorBudget(
            module_id="MOD-Y",
            target_slo=99.5,
            budget_remaining_pct=50.0,
            burn_rate=2.5,
            state=SLOState.AT_RISK,
        )
        assert budget.target_slo == 99.5
        assert budget.state == SLOState.AT_RISK


class TestSessionBrief:
    def test_creation_with_defaults(self):
        brief = SessionBrief(session_id="sess-001")
        assert brief.session_id == "sess-001"
        assert brief.cards_completed == 0
        assert brief.cards_failed == 0
        assert brief.total_cost_usd == 0.0
        assert brief.summary == ""

    def test_creation_custom(self):
        brief = SessionBrief(
            session_id="sess-002",
            cards_completed=5,
            cards_failed=1,
            total_cost_usd=2.50,
            summary="Good progress",
        )
        assert brief.cards_completed == 5
        assert brief.total_cost_usd == 2.50


class TestOrchestratorIntegrationBridge:
    def test_emit_pipeline_complete(self):
        bridge = OrchestratorIntegrationBridge()
        result = bridge.emit_pipeline_complete({"task_id": "T-001"})
        assert result["event"] == "PIPELINE_COMPLETE"
        assert result["result"]["task_id"] == "T-001"
        assert len(result["downstream_handlers"]) > 0

    def test_default_contract_version(self):
        bridge = OrchestratorIntegrationBridge()
        assert bridge.contract_version == "CT-PIPE-ORC-001"
        assert bridge.enabled is True


class TestPipelineOrchestratorRoadmapMixin:
    def test_generate_session_brief(self):
        mixin = PipelineOrchestratorRoadmapMixin()
        brief = mixin.generate_session_brief("sess-001")
        assert isinstance(brief, SessionBrief)
        assert brief.session_id == "sess-001"

    def test_generate_health_report(self):
        mixin = PipelineOrchestratorRoadmapMixin()
        report = mixin.generate_health_report()
        assert isinstance(report, HealthReport)

    def test_enter_maintenance_mode(self):
        mixin = PipelineOrchestratorRoadmapMixin()
        mixin.enter_maintenance_mode()

    def test_recover_all(self):
        mixin = PipelineOrchestratorRoadmapMixin()
        mixin.recover_all()

# [A_test] module_id: SRC-TST-0301 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-033 | docs/03_modules/_cross_layer/behavioral_auditor/blueprint.md | §
# [MODULE] tests.test_ai_context_injector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] python -m pytest tests/test_ai_context_injector.py -q
# [TTL] task_bound

from __future__ import annotations

from datetime import datetime

from zephyr.gov_drift.ai_context_injector import (
    _INJECTOR_MAP,
    HealthSnapshot,
    InjectedContext,
    InjectionLevel,
    TopDriftItem,
    build_health_snapshot,
    build_top_drifts,
    inject_full,
    inject_minimal,
    inject_standard,
)


class TestInjectionLevel:
    def test_has_three_levels(self):
        assert InjectionLevel.MINIMAL.value == "minimal"
        assert InjectionLevel.STANDARD.value == "standard"
        assert InjectionLevel.FULL.value == "full"

    def test_is_str_enum(self):
        assert isinstance(InjectionLevel.MINIMAL, str)
        assert isinstance(InjectionLevel.STANDARD, str)
        assert isinstance(InjectionLevel.FULL, str)

    def test_level_count(self):
        assert len(InjectionLevel) == 3

    def test_boundary_values_are_distinct(self):
        values = [level.value for level in InjectionLevel]
        assert len(values) == len(set(values))


class TestHealthSnapshot:
    def test_creates_with_required_fields(self):
        snap = HealthSnapshot(
            module_id="MOD-INF-023",
            active_drift_count=0,
            budget_remaining={},
            state_distribution={},
        )
        assert snap.module_id == "MOD-INF-023"
        assert snap.active_drift_count == 0
        assert snap.budget_remaining == {}
        assert snap.state_distribution == {}

    def test_snapshot_time_auto_set(self):
        snap = HealthSnapshot(module_id="M1", active_drift_count=0, budget_remaining={}, state_distribution={})
        assert isinstance(snap.snapshot_time, datetime)
        assert snap.snapshot_time.tzinfo is not None

    def test_stores_state_distribution(self):
        snap = HealthSnapshot(
            module_id="M1",
            active_drift_count=3,
            budget_remaining={"P0": 3},
            state_distribution={"DETECTED": 2, "TRIAGED": 1},
        )
        assert snap.state_distribution["DETECTED"] == 2
        assert snap.state_distribution["TRIAGED"] == 1

    def test_boundary_zero_drift_count(self):
        snap = HealthSnapshot(module_id="M0", active_drift_count=0, budget_remaining={}, state_distribution={})
        assert snap.active_drift_count == 0

    def test_boundary_large_drift_count(self):
        snap = HealthSnapshot(module_id="M0", active_drift_count=9999, budget_remaining={}, state_distribution={})
        assert snap.active_drift_count == 9999


class TestTopDriftItem:
    def test_creates_with_all_fields(self):
        item = TopDriftItem(event_id="e1", detector_id="d1", severity="HIGH", roi_score=0.9, description="test")
        assert item.event_id == "e1"
        assert item.detector_id == "d1"
        assert item.severity == "HIGH"
        assert item.roi_score == 0.9
        assert item.description == "test"

    def test_boundary_zero_roi_score(self):
        item = TopDriftItem(event_id="e2", detector_id="d2", severity="LOW", roi_score=0.0, description="")
        assert item.roi_score == 0.0

    def test_boundary_negative_roi_score(self):
        item = TopDriftItem(event_id="e3", detector_id="d3", severity="INFO", roi_score=-1.0, description="neg")
        assert item.roi_score == -1.0


class TestInjectedContext:
    def test_creates_with_required_fields(self):
        ctx = InjectedContext(level=InjectionLevel.MINIMAL, token_estimate=10, content="test content")
        assert ctx.level == InjectionLevel.MINIMAL
        assert ctx.token_estimate == 10
        assert ctx.content == "test content"

    def test_injection_time_auto_set(self):
        ctx = InjectedContext(level=InjectionLevel.STANDARD, token_estimate=5, content="x")
        assert isinstance(ctx.injection_time, datetime)

    def test_boundary_zero_token_estimate(self):
        ctx = InjectedContext(level=InjectionLevel.FULL, token_estimate=0, content="")
        assert ctx.token_estimate == 0

    def test_boundary_large_token_estimate(self):
        ctx = InjectedContext(level=InjectionLevel.FULL, token_estimate=99999, content="x" * 5000)
        assert ctx.token_estimate == 99999


class TestBuildHealthSnapshot:
    def test_empty_events(self):
        snap = build_health_snapshot("MOD-INF-023", [])
        assert snap.active_drift_count == 0
        assert snap.state_distribution == {}
        assert snap.module_id == "MOD-INF-023"

    def test_counts_state_distribution(self):
        events = [
            {"state": "DETECTED"},
            {"state": "DETECTED"},
            {"state": "TRIAGED"},
        ]
        snap = build_health_snapshot("M1", events)
        assert snap.active_drift_count == 3
        assert snap.state_distribution["DETECTED"] == 2
        assert snap.state_distribution["TRIAGED"] == 1

    def test_handles_missing_state_key(self):
        events = [{"other_key": "val"}]
        snap = build_health_snapshot("M1", events)
        assert snap.state_distribution.get("UNKNOWN") == 1

    def test_provides_default_budget(self):
        events = [{"state": "DETECTED"}]
        snap = build_health_snapshot("M1", events)
        assert "P0" in snap.budget_remaining
        assert "P1" in snap.budget_remaining
        assert "P2" in snap.budget_remaining

    def test_boundary_single_event(self):
        snap = build_health_snapshot("M1", [{"state": "RESOLVED"}])
        assert snap.active_drift_count == 1
        assert snap.state_distribution["RESOLVED"] == 1

    def test_boundary_many_events_same_state(self):
        events = [{"state": "DETECTED"}] * 100
        snap = build_health_snapshot("M1", events)
        assert snap.active_drift_count == 100
        assert snap.state_distribution["DETECTED"] == 100


class TestBuildTopDrifts:
    def test_empty_events(self):
        result = build_top_drifts([])
        assert result == []

    def test_sorts_by_roi_score_descending(self):
        events = [
            {"event_id": "e1", "detector_id": "d1", "severity": "LOW", "roi_score": 0.2, "description": "low"},
            {"event_id": "e2", "detector_id": "d2", "severity": "HIGH", "roi_score": 0.9, "description": "high"},
            {"event_id": "e3", "detector_id": "d3", "severity": "MEDIUM", "roi_score": 0.5, "description": "mid"},
        ]
        result = build_top_drifts(events, limit=3)
        assert len(result) == 3
        assert result[0].roi_score == 0.9
        assert result[1].roi_score == 0.5
        assert result[2].roi_score == 0.2

    def test_respects_limit(self):
        events = [
            {"event_id": f"e{i}", "detector_id": "d", "severity": "INFO", "roi_score": float(i), "description": "x"}
            for i in range(10)
        ]
        result = build_top_drifts(events, limit=3)
        assert len(result) == 3

    def test_truncates_description_to_120(self):
        long_desc = "x" * 200
        events = [
            {"event_id": "e1", "detector_id": "d1", "severity": "INFO", "roi_score": 1.0, "description": long_desc}
        ]
        result = build_top_drifts(events)
        assert len(result[0].description) <= 120

    def test_default_limit_is_three(self):
        events = [
            {"event_id": f"e{i}", "detector_id": "d", "severity": "INFO", "roi_score": float(i), "description": "x"}
            for i in range(10)
        ]
        result = build_top_drifts(events)
        assert len(result) == 3

    def test_boundary_missing_roi_defaults_to_zero(self):
        events = [{"event_id": "e1", "detector_id": "d1", "severity": "INFO", "description": "no roi"}]
        result = build_top_drifts(events)
        assert result[0].roi_score == 0.0

    def test_boundary_missing_fields_use_defaults(self):
        events = [{}]
        result = build_top_drifts(events)
        assert result[0].event_id == ""
        assert result[0].detector_id == ""
        assert result[0].severity == "INFO"

    def test_boundary_limit_one(self):
        events = [
            {"event_id": "e1", "detector_id": "d1", "severity": "HIGH", "roi_score": 0.9, "description": "a"},
            {"event_id": "e2", "detector_id": "d2", "severity": "LOW", "roi_score": 0.1, "description": "b"},
        ]
        result = build_top_drifts(events, limit=1)
        assert len(result) == 1
        assert result[0].event_id == "e1"


class TestInjectMinimal:
    def test_produces_injected_context_with_minimal_level(self):
        snap = HealthSnapshot(
            module_id="M1",
            active_drift_count=5,
            budget_remaining={"P0": 3, "P1": 8, "P2": 15},
            state_distribution={"DETECTED": 3, "TRIAGED": 2},
        )
        ctx = inject_minimal(snap)
        assert ctx.level == InjectionLevel.MINIMAL
        assert ctx.token_estimate > 0
        assert isinstance(ctx.injection_time, datetime)

    def test_content_includes_drift_count(self):
        snap = HealthSnapshot(
            module_id="M1",
            active_drift_count=5,
            budget_remaining={"P0": 3, "P1": 8, "P2": 15},
            state_distribution={"DETECTED": 3, "TRIAGED": 2},
        )
        ctx = inject_minimal(snap)
        assert "active_drifts=5" in ctx.content

    def test_handles_empty_state_distribution(self):
        snap = HealthSnapshot(module_id="M1", active_drift_count=0, budget_remaining={}, state_distribution={})
        ctx = inject_minimal(snap)
        assert "active_drifts=0" in ctx.content

    def test_content_includes_budget_info(self):
        snap = HealthSnapshot(
            module_id="M1",
            active_drift_count=1,
            budget_remaining={"P0": 3, "P1": 8, "P2": 15},
            state_distribution={},
        )
        ctx = inject_minimal(snap)
        assert "P0=3" in ctx.content
        assert "P1=8" in ctx.content
        assert "P2=15" in ctx.content

    def test_boundary_zero_drifts(self):
        snap = HealthSnapshot(module_id="M0", active_drift_count=0, budget_remaining={}, state_distribution={})
        ctx = inject_minimal(snap)
        assert ctx.level == InjectionLevel.MINIMAL
        assert ctx.token_estimate > 0


class TestInjectStandard:
    def test_includes_top_drifts_section(self):
        snap = HealthSnapshot(
            module_id="M1",
            active_drift_count=2,
            budget_remaining={"P0": 3},
            state_distribution={"DETECTED": 2},
        )
        drifts = [
            TopDriftItem(event_id="e1", detector_id="d1", severity="HIGH", roi_score=0.8, description="test drift")
        ]
        ctx = inject_standard(snap, drifts)
        assert ctx.level == InjectionLevel.STANDARD
        assert "Top active drifts" in ctx.content
        assert "d1" in ctx.content

    def test_handles_empty_drifts_list(self):
        snap = HealthSnapshot(module_id="M1", active_drift_count=0, budget_remaining={}, state_distribution={})
        ctx = inject_standard(snap, [])
        assert ctx.level == InjectionLevel.STANDARD
        assert "Top active drifts" in ctx.content

    def test_includes_minimal_content_as_prefix(self):
        snap = HealthSnapshot(
            module_id="M1",
            active_drift_count=3,
            budget_remaining={"P0": 3},
            state_distribution={"DETECTED": 3},
        )
        drifts = [TopDriftItem(event_id="e1", detector_id="d1", severity="HIGH", roi_score=0.9, description="top")]
        ctx = inject_standard(snap, drifts)
        assert "active_drifts=3" in ctx.content

    def test_boundary_multiple_drifts(self):
        snap = HealthSnapshot(
            module_id="M1",
            active_drift_count=3,
            budget_remaining={"P0": 3},
            state_distribution={"DETECTED": 3},
        )
        drifts = [
            TopDriftItem(event_id="e1", detector_id="d1", severity="HIGH", roi_score=0.9, description="first"),
            TopDriftItem(event_id="e2", detector_id="d2", severity="MEDIUM", roi_score=0.5, description="second"),
        ]
        ctx = inject_standard(snap, drifts)
        assert "d1" in ctx.content
        assert "d2" in ctx.content

    def test_boundary_roi_score_formatting(self):
        snap = HealthSnapshot(module_id="M1", active_drift_count=1, budget_remaining={}, state_distribution={})
        drifts = [TopDriftItem(event_id="e1", detector_id="d1", severity="HIGH", roi_score=0.876, description="test")]
        ctx = inject_standard(snap, drifts)
        assert "ROI=0.9" in ctx.content


class TestInjectFull:
    def test_includes_full_inventory_header(self):
        snap = HealthSnapshot(
            module_id="M1",
            active_drift_count=1,
            budget_remaining={"P0": 3},
            state_distribution={"DETECTED": 1},
        )
        events = [
            {"severity": "CRITICAL", "detector_id": "d1", "description": "critical issue", "roi_score": 0.9},
        ]
        ctx = inject_full(snap, events)
        assert ctx.level == InjectionLevel.FULL
        assert "FULL DRIFT INVENTORY" in ctx.content

    def test_includes_total_events_count(self):
        snap = HealthSnapshot(module_id="M1", active_drift_count=2, budget_remaining={}, state_distribution={})
        events = [
            {"severity": "HIGH", "detector_id": "d1", "description": "a", "roi_score": 0.8},
            {"severity": "LOW", "detector_id": "d2", "description": "b", "roi_score": 0.1},
        ]
        ctx = inject_full(snap, events)
        assert "Total events: 2" in ctx.content

    def test_handles_auto_fixable_events(self):
        snap = HealthSnapshot(module_id="M1", active_drift_count=1, budget_remaining={}, state_distribution={})
        events = [
            {
                "severity": "INFO",
                "detector_id": "d2",
                "description": "fixable",
                "roi_score": 0.5,
                "auto_fixable": True,
                "fix_description": "apply patch",
            },
        ]
        ctx = inject_full(snap, events)
        assert "auto_fixable" in ctx.content

    def test_handles_empty_events_list(self):
        snap = HealthSnapshot(module_id="M1", active_drift_count=0, budget_remaining={}, state_distribution={})
        ctx = inject_full(snap, [])
        assert ctx.level == InjectionLevel.FULL
        assert "Total events: 0" in ctx.content

    def test_sorts_by_severity_then_roi(self):
        snap = HealthSnapshot(module_id="M1", active_drift_count=3, budget_remaining={}, state_distribution={})
        events = [
            {"severity": "INFO", "detector_id": "d_info", "description": "low sev", "roi_score": 0.9},
            {"severity": "CRITICAL", "detector_id": "d_crit", "description": "high sev", "roi_score": 0.1},
        ]
        ctx = inject_full(snap, events)
        crit_pos = ctx.content.find("d_crit")
        info_pos = ctx.content.find("d_info")
        assert crit_pos < info_pos

    def test_boundary_description_truncated_to_100(self):
        snap = HealthSnapshot(module_id="M1", active_drift_count=1, budget_remaining={}, state_distribution={})
        events = [
            {"severity": "INFO", "detector_id": "d1", "description": "x" * 200, "roi_score": 0.5},
        ]
        ctx = inject_full(snap, events)
        for line in ctx.content.split("\n"):
            if "d1" in line:
                desc_part = line.split("|")[-1] if "|" in line else ""
                assert len(desc_part.strip()) <= 100
                break

    def test_includes_state_breakdown(self):
        snap = HealthSnapshot(
            module_id="M1",
            active_drift_count=1,
            budget_remaining={},
            state_distribution={"DETECTED": 1},
        )
        events = [
            {"severity": "HIGH", "detector_id": "d1", "description": "x", "roi_score": 0.5},
        ]
        ctx = inject_full(snap, events)
        assert "State breakdown" in ctx.content


class TestInjectorMap:
    def test_maps_all_levels(self):
        assert _INJECTOR_MAP[InjectionLevel.MINIMAL] == "inject_minimal"
        assert _INJECTOR_MAP[InjectionLevel.STANDARD] == "inject_standard"
        assert _INJECTOR_MAP[InjectionLevel.FULL] == "inject_full"

    def test_has_three_entries(self):
        assert len(_INJECTOR_MAP) == 3

    def test_all_enum_values_covered(self):
        for level in InjectionLevel:
            assert level in _INJECTOR_MAP

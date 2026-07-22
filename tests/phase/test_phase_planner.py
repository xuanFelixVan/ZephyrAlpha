# [A_test] module_id: MOD-GOV_phase_planner | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_phase_planner
# [INVARIANTS] phases must contain all PhaseDefinitions; can_start must respect depends_on; status transitions must set timestamps
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] KeyError on unknown phase name; PhaseStatus enum validation
# [TESTS] tests/test_phase_planner.py
# [TTL] task_bound

from datetime import UTC, datetime

import pytest

from zephyr.autonomy_core.phase_planner import Phase, PhasePlanner, PhaseStatus


class TestPhaseStatusEnum:
    def test_all_values(self):
        assert PhaseStatus.BACKLOG.value == "backlog"
        assert PhaseStatus.IN_PROGRESS.value == "in_progress"
        assert PhaseStatus.DONE.value == "done"
        assert PhaseStatus.VERIFIED.value == "verified"
        assert PhaseStatus.BLOCKED.value == "blocked"

    def test_string_enum(self):
        assert isinstance(PhaseStatus.BACKLOG, str)
        assert PhaseStatus.BACKLOG == "backlog"


class TestPhaseInit:
    def test_basic_creation(self):
        p = Phase("test", 1, "desc", [])
        assert p.name == "test"
        assert p.seq == 1
        assert p.description == "desc"
        assert p.depends_on == []
        assert p.status == PhaseStatus.BACKLOG

    def test_custom_status(self):
        p = Phase("test", 2, "desc", [], status=PhaseStatus.DONE)
        assert p.status == PhaseStatus.DONE

    def test_timestamps_default_none(self):
        p = Phase("test", 1, "desc", [])
        assert p.started_at is None
        assert p.done_at is None
        assert p.verified_at is None

    def test_with_dependencies(self):
        p = Phase("b", 2, "desc", ["a"])
        assert p.depends_on == ["a"]


class TestPhaseToDict:
    def test_backlog_phase_dict(self):
        p = Phase("test", 1, "desc", ["x"])
        d = p.to_dict()
        assert d["name"] == "test"
        assert d["seq"] == 1
        assert d["description"] == "desc"
        assert d["depends_on"] == ["x"]
        assert d["status"] == "backlog"
        assert d["started_at"] is None
        assert d["done_at"] is None
        assert d["verified_at"] is None

    def test_dict_with_timestamps(self):
        p = Phase("test", 1, "desc", [])
        p.started_at = datetime(2026, 1, 1, tzinfo=UTC)
        d = p.to_dict()
        assert d["started_at"] == "2026-01-01T00:00:00+00:00"


class TestPhaseCanStart:
    def test_no_deps_can_start(self):
        p = Phase("a", 1, "desc", [])
        assert p.can_start([]) is True

    def test_deps_satisfied(self):
        p = Phase("b", 2, "desc", ["a"])
        assert p.can_start(["a"]) is True

    def test_deps_not_satisfied(self):
        p = Phase("b", 2, "desc", ["a"])
        assert p.can_start([]) is False

    def test_partial_deps(self):
        p = Phase("c", 3, "desc", ["a", "b"])
        assert p.can_start(["a"]) is False
        assert p.can_start(["a", "b"]) is True

    def test_empty_completed_phases_with_deps(self):
        p = Phase("x", 1, "desc", ["y"])
        assert p.can_start([]) is False


class TestPhasePlannerInit:
    def test_all_phases_loaded(self):
        planner = PhasePlanner()
        assert len(planner.phases) == len(PhasePlanner.PhaseDefinitions)

    def test_first_phase_no_deps(self):
        planner = PhasePlanner()
        first = planner.phases["scaffold-0"]
        assert first.depends_on == []
        assert first.seq == 1

    def test_phase_status_backlog(self):
        planner = PhasePlanner()
        for p in planner.phases.values():
            assert p.status == PhaseStatus.BACKLOG


class TestPhasePlannerGetPhase:
    def test_get_existing_phase(self):
        planner = PhasePlanner()
        phase = planner.get_phase("scaffold-0")
        assert phase.name == "scaffold-0"

    def test_get_nonexistent_phase_raises(self):
        planner = PhasePlanner()
        with pytest.raises(KeyError):
            planner.get_phase("nonexistent_phase")


class TestPhasePlannerSetStatus:
    def test_set_in_progress(self):
        planner = PhasePlanner()
        phase = planner.set_status("scaffold-0", PhaseStatus.IN_PROGRESS)
        assert phase.status == PhaseStatus.IN_PROGRESS
        assert phase.started_at is not None

    def test_set_done(self):
        planner = PhasePlanner()
        phase = planner.set_status("scaffold-0", PhaseStatus.DONE)
        assert phase.status == PhaseStatus.DONE
        assert phase.done_at is not None

    def test_set_verified(self):
        planner = PhasePlanner()
        phase = planner.set_status("scaffold-0", PhaseStatus.VERIFIED)
        assert phase.status == PhaseStatus.VERIFIED
        assert phase.verified_at is not None

    def test_set_blocked(self):
        planner = PhasePlanner()
        phase = planner.set_status("scaffold-0", PhaseStatus.BLOCKED)
        assert phase.status == PhaseStatus.BLOCKED

    def test_set_status_unknown_phase_raises(self):
        planner = PhasePlanner()
        with pytest.raises(KeyError):
            planner.set_status("no_such_phase", PhaseStatus.DONE)


class TestPhasePlannerGetReadyPhases:
    def test_initial_ready_phases(self):
        planner = PhasePlanner()
        ready = planner.get_ready_phases()
        assert "scaffold-0" in ready

    def test_after_first_done_second_becomes_ready(self):
        planner = PhasePlanner()
        planner.set_status("scaffold-0", PhaseStatus.DONE)
        ready = planner.get_ready_phases()
        assert "scaffold-1" in ready

    def test_no_ready_if_deps_not_met(self):
        planner = PhasePlanner()
        ready = planner.get_ready_phases()
        assert "scaffold-1" not in ready

    def test_all_done_no_ready(self):
        planner = PhasePlanner()
        for name in planner.phases:
            planner.set_status(name, PhaseStatus.DONE)
        ready = planner.get_ready_phases()
        assert ready == []


class TestPhasePlannerAllPhases:
    def test_returns_list_of_dicts(self):
        planner = PhasePlanner()
        result = planner.all_phases()
        assert isinstance(result, list)
        assert len(result) == len(PhasePlanner.PhaseDefinitions)
        for item in result:
            assert isinstance(item, dict)
            assert "name" in item
            assert "seq" in item
            assert "status" in item


class TestPhasePlannerPhaseSummary:
    def test_initial_summary(self):
        planner = PhasePlanner()
        summary = planner.phase_summary()
        total_phases = len(PhasePlanner.PhaseDefinitions)
        assert summary["backlog"] == total_phases
        assert summary["in_progress"] == 0
        assert summary["done"] == 0

    def test_summary_after_transitions(self):
        planner = PhasePlanner()
        planner.set_status("scaffold-0", PhaseStatus.DONE)
        summary = planner.phase_summary()
        assert summary["done"] == 1
        assert summary["backlog"] == len(PhasePlanner.PhaseDefinitions) - 1


class TestPhasePlannerCurrentProjection:
    def test_initial_projection_phase1(self):
        planner = PhasePlanner()
        assert planner.current_projection() == PhasePlanner.SkillProjection["Phase1"]

    def test_projection_phase2(self):
        planner = PhasePlanner()
        for name in list(planner.phases.keys())[:7]:
            planner.set_status(name, PhaseStatus.DONE)
        assert planner.current_projection() == PhasePlanner.SkillProjection["Phase2"]

    def test_projection_final(self):
        planner = PhasePlanner()
        for name in planner.phases:
            planner.set_status(name, PhaseStatus.VERIFIED)
        assert planner.current_projection() == PhasePlanner.SkillProjection["Final"]

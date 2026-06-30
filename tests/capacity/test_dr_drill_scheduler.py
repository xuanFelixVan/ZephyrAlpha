# [A_test] module_id: SRC-TST-0766 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infra_ops/capacity_assurance/blueprint.md | §test
# [MODULE] tests.test_dr_drill_scheduler
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_dr_drill_scheduler.py
# [TTL] task_bound

import pytest

mod = pytest.importorskip("zephyr.trading.feedback_loop.capacity_assurance.dr_drill_scheduler", reason="dr_drill_scheduler not available")
DRDrillScheduler = mod.DRDrillScheduler
DRDrillResult = mod.DRDrillResult


class TestDRDrillResult:
    def test_instantiation(self):
        result = DRDrillResult(drill_id="dr_1", success=True, rto_seconds=120, rpo_seconds=60)
        assert result.drill_id == "dr_1"
        assert result.success is True
        assert result.notes == ""

    def test_with_notes(self):
        result = DRDrillResult(drill_id="dr_2", success=False, rto_seconds=300, rpo_seconds=120, notes="failed")
        assert result.notes == "failed"


class TestDRDrillScheduler:
    def test_instantiation(self):
        scheduler = DRDrillScheduler()
        assert len(scheduler._drill_history) == 0

    def test_schedule_drill(self):
        scheduler = DRDrillScheduler()
        result = scheduler.schedule_drill("dr_1")
        assert isinstance(result, DRDrillResult)
        assert result.success is True
        assert result.drill_id == "dr_1"

    def test_quarterly_scorecard_empty(self):
        scheduler = DRDrillScheduler()
        scorecard = scheduler.quarterly_scorecard()
        assert scorecard["drills"] == 0
        assert scorecard["success_rate"] == 0

    def test_quarterly_scorecard_with_drills(self):
        scheduler = DRDrillScheduler()
        scheduler.schedule_drill("dr_1")
        scheduler.schedule_drill("dr_2")
        scorecard = scheduler.quarterly_scorecard()
        assert scorecard["total_drills"] == 2
        assert scorecard["success_rate"] == 1.0
        assert scorecard["avg_rto_seconds"] == 120.0

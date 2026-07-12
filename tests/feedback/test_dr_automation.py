# [A_test] module_id: SRC-TST-0765 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_dr_automation
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.resilience.dr_automation
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_dr_automation.py
# [TTL] task_bound

import time

from zephyr.feedback_loop.resilience.dr_automation import (
    DRAutomation,
    DRDrillResult,
)


class TestDRAutomationInstantiation:
    def test_default_instantiation(self):
        dr = DRAutomation()
        assert dr.max_drill_interval_days == 90
        assert dr.rpo_target_seconds == 300.0
        assert dr.rto_target_seconds == 900.0
        assert dr.drills == []

    def test_custom_instantiation(self):
        dr = DRAutomation(max_drill_interval_days=30, rpo_target_seconds=60.0)
        assert dr.max_drill_interval_days == 30
        assert dr.rpo_target_seconds == 60.0


class TestNeedsDrill:
    def test_recent_drill_no_need(self):
        dr = DRAutomation(max_drill_interval_days=90)
        assert dr.needs_drill() is False

    def test_stale_drill_needs_drill(self):
        dr = DRAutomation(max_drill_interval_days=0)
        dr._last_drill = 0
        assert dr.needs_drill() is True


class TestRecordDrill:
    def test_record_drill_appends(self):
        dr = DRAutomation()
        result = DRDrillResult(
            drill_id="drill-001",
            timestamp=time.time(),
            rpo_seconds=200.0,
            rto_seconds=800.0,
            rpo_pass=True,
            rto_pass=True,
        )
        dr.record_drill(result)
        assert len(dr.drills) == 1
        assert dr.drills[0].drill_id == "drill-001"

    def test_record_drill_updates_last_drill(self):
        dr = DRAutomation()
        old_last = dr._last_drill
        result = DRDrillResult(
            drill_id="drill-002",
            timestamp=time.time(),
            rpo_seconds=100.0,
            rto_seconds=500.0,
            rpo_pass=True,
            rto_pass=False,
        )
        dr.record_drill(result)
        assert dr._last_drill >= old_last


class TestSummary:
    def test_summary_no_drills(self):
        dr = DRAutomation()
        s = dr.summary()
        assert s["last_drill"] is None
        assert s["rpo_pass_rate"] == 1.0
        assert s["rto_pass_rate"] == 1.0

    def test_summary_with_drills(self):
        dr = DRAutomation()
        dr.record_drill(
            DRDrillResult(
                drill_id="d1",
                timestamp=time.time(),
                rpo_seconds=200.0,
                rto_seconds=800.0,
                rpo_pass=True,
                rto_pass=True,
            )
        )
        dr.record_drill(
            DRDrillResult(
                drill_id="d2",
                timestamp=time.time(),
                rpo_seconds=600.0,
                rto_seconds=1200.0,
                rpo_pass=False,
                rto_pass=False,
            )
        )
        s = dr.summary()
        assert s["rpo_pass_rate"] == 0.5
        assert s["rto_pass_rate"] == 0.5
        assert s["last_rpo"] == 600.0

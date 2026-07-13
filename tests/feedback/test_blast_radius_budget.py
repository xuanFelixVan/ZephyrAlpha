# [A_test] module_id: SRC-TST-0427 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_blast_radius_budget
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_blast_radius_budget.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.detectors.reliability.blast_radius_budget import BlastRadiusBudget


class TestBlastRadiusBudgetInstantiation:
    def test_default_construction(self):
        brb = BlastRadiusBudget()
        assert brb.max_concurrent_repairs == 3
        assert brb.active_repairs == 0

    def test_custom_params(self):
        brb = BlastRadiusBudget(max_concurrent_repairs=5, active_repairs=2)
        assert brb.max_concurrent_repairs == 5
        assert brb.active_repairs == 2


class TestActiveRepairsTracking:
    def test_increment_active(self):
        brb = BlastRadiusBudget()
        brb.active_repairs = 1
        assert brb.active_repairs == 1

    def test_decrement_active(self):
        brb = BlastRadiusBudget(active_repairs=2)
        brb.active_repairs = 1
        assert brb.active_repairs == 1

    def test_within_budget(self):
        brb = BlastRadiusBudget(max_concurrent_repairs=3, active_repairs=2)
        assert brb.active_repairs < brb.max_concurrent_repairs

    def test_at_budget_limit(self):
        brb = BlastRadiusBudget(max_concurrent_repairs=3, active_repairs=3)
        assert brb.active_repairs == brb.max_concurrent_repairs

    def test_over_budget(self):
        brb = BlastRadiusBudget(max_concurrent_repairs=3, active_repairs=5)
        assert brb.active_repairs > brb.max_concurrent_repairs


class TestBoundaryValues:
    def test_zero_max_concurrent(self):
        brb = BlastRadiusBudget(max_concurrent_repairs=0)
        assert brb.max_concurrent_repairs == 0

    def test_negative_active_repairs(self):
        brb = BlastRadiusBudget(active_repairs=-1)
        assert brb.active_repairs == -1

    def test_independent_instances(self):
        a = BlastRadiusBudget(max_concurrent_repairs=3, active_repairs=1)
        b = BlastRadiusBudget(max_concurrent_repairs=5, active_repairs=0)
        a.active_repairs = 3
        assert b.active_repairs == 0

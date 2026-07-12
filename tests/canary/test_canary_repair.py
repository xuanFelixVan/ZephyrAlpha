# [A_test] module_id: SRC-TST-0484 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_canary_repair
# [INVARIANTS] canary_pct default=0.1
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_canary_repair.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.feedback_loop.verifiers.canary_repair import CanaryRepair


class TestCanaryRepairInstantiation:
    def test_default_construction(self):
        cr = CanaryRepair()
        assert cr.canary_pct == pytest.approx(0.1)

    def test_custom_pct(self):
        cr = CanaryRepair(canary_pct=0.25)
        assert cr.canary_pct == pytest.approx(0.25)

    def test_zero_pct(self):
        cr = CanaryRepair(canary_pct=0.0)
        assert cr.canary_pct == pytest.approx(0.0)

    def test_full_pct(self):
        cr = CanaryRepair(canary_pct=1.0)
        assert cr.canary_pct == pytest.approx(1.0)


class TestCanaryPctAttribute:
    def test_mutable(self):
        cr = CanaryRepair()
        cr.canary_pct = 0.5
        assert cr.canary_pct == pytest.approx(0.5)

    def test_small_pct(self):
        cr = CanaryRepair(canary_pct=0.01)
        assert cr.canary_pct == pytest.approx(0.01)

# [A_test] module_id: SRC-TST-0752 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_digital_twin_sandbox
# [INVARIANTS] fidelity default=0.8
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_digital_twin_sandbox.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.feedback_loop.verifiers.digital_twin_sandbox import DigitalTwinSandbox


class TestDigitalTwinSandboxInstantiation:
    def test_default_construction(self):
        dts = DigitalTwinSandbox()
        assert dts.fidelity == pytest.approx(0.8)

    def test_custom_fidelity(self):
        dts = DigitalTwinSandbox(fidelity=0.95)
        assert dts.fidelity == pytest.approx(0.95)

    def test_zero_fidelity(self):
        dts = DigitalTwinSandbox(fidelity=0.0)
        assert dts.fidelity == pytest.approx(0.0)

    def test_max_fidelity(self):
        dts = DigitalTwinSandbox(fidelity=1.0)
        assert dts.fidelity == pytest.approx(1.0)

    def test_fidelity_attribute_mutable(self):
        dts = DigitalTwinSandbox()
        dts.fidelity = 0.5
        assert dts.fidelity == pytest.approx(0.5)

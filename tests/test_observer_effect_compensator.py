# [A_test] module_id: SRC-TST-1326 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain_infra_ops/capacity_assurance/blueprint.md | §test
# [MODULE] tests.test_observer_effect_compensator
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_observer_effect_compensator.py
# [TTL] task_bound

import pytest

mod = pytest.importorskip(
    "zephyr.ops.capacity_assurance.observer_effect_compensator", reason="observer_effect_compensator not available"
)
ObserverEffectCompensator = mod.ObserverEffectCompensator


class TestObserverEffectCompensator:
    def test_instantiation(self):
        oec = ObserverEffectCompensator()
        assert len(oec._overhead_pct) == 0

    def test_set_overhead_and_compensate(self):
        oec = ObserverEffectCompensator()
        oec.set_overhead("sli_1", 0.1)
        result = oec.compensate("sli_1", 100.0)
        assert result["compensated"] is True
        assert abs(result["compensated_value"] - 90.0) < 0.01
        assert result["overhead_pct"] == 0.1

    def test_compensate_no_overhead(self):
        oec = ObserverEffectCompensator()
        result = oec.compensate("sli_1", 100.0)
        assert result["compensated"] is False
        assert result["compensated_value"] == 100.0

    def test_set_overhead_clamped_high(self):
        oec = ObserverEffectCompensator()
        oec.set_overhead("sli_1", 1.5)
        result = oec.compensate("sli_1", 100.0)
        assert result["compensated_value"] == 0.0

    def test_set_overhead_clamped_negative(self):
        oec = ObserverEffectCompensator()
        oec.set_overhead("sli_1", -0.5)
        result = oec.compensate("sli_1", 100.0)
        assert result["overhead_pct"] == 0.0
        assert result["compensated_value"] == 100.0

    def test_compensate_zero_raw(self):
        oec = ObserverEffectCompensator()
        oec.set_overhead("sli_1", 0.2)
        result = oec.compensate("sli_1", 0.0)
        assert result["compensated_value"] == 0.0

    def test_compensate_result_fields(self):
        oec = ObserverEffectCompensator()
        result = oec.compensate("sli_x", 50.0)
        assert "sli_id" in result
        assert "raw_value" in result
        assert "timestamp" in result
        assert result["sli_id"] == "sli_x"

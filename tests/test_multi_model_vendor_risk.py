# [A_test] module_id: SRC-TST-1302 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-001 | docs/03_modules/_domain-infra_ops/capacity-assurance/blueprint.md | §test
# [MODULE] tests.test_multi_model_vendor_risk
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_multi_model_vendor_risk.py

import pytest

mod = pytest.importorskip(
    "zephyr.ops.capacity_assurance.multi_model_vendor_risk", reason="multi_model_vendor_risk not available"
)
MultiModelVendorRisk = mod.MultiModelVendorRisk


class TestMultiModelVendorRisk:
    def test_instantiation(self):
        mmvr = MultiModelVendorRisk()
        assert mmvr.SINGLE_VENDOR_SATURATION_THRESHOLD == 0.70

    def test_check_empty(self):
        mmvr = MultiModelVendorRisk()
        result = mmvr.check()
        assert result["risk"] == "N/A"
        assert result["vendor_shares"] == {}

    def test_record_and_check_low_risk(self):
        mmvr = MultiModelVendorRisk()
        mmvr.record("openai", "gpt-4", 500)
        mmvr.record("anthropic", "claude-3", 500)
        result = mmvr.check()
        assert result["risk"] == "LOW"

    def test_record_and_check_high_risk(self):
        mmvr = MultiModelVendorRisk()
        mmvr.record("openai", "gpt-4", 800)
        mmvr.record("anthropic", "claude-3", 200)
        result = mmvr.check()
        assert result["risk"] == "HIGH"
        assert result["dominant_vendor"] == "openai"

    def test_vendor_shares_calculation(self):
        mmvr = MultiModelVendorRisk()
        mmvr.record("vendor_a", "model_1", 300)
        mmvr.record("vendor_b", "model_2", 700)
        result = mmvr.check()
        assert result["vendor_shares"]["vendor_a"] == 0.3
        assert result["vendor_shares"]["vendor_b"] == 0.7

    def test_single_vendor(self):
        mmvr = MultiModelVendorRisk()
        mmvr.record("openai", "gpt-4", 1000)
        result = mmvr.check()
        assert result["risk"] == "HIGH"
        assert result["dominant_share"] == 1.0

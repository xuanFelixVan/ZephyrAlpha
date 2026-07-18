# [A_test] module_id: SRC-TST-0302 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-TEST-347 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.test_ai_self_diagnosis
# [INVARIANTS] AutoFixLayer enum must have 3 levels; auto_fix_known_pattern returns tuple
# [MODIFY-GUARD] Changes must sync with ai_self_diagnosis.py
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] None
# [TESTS] tests/test_ai_self_diagnosis.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.intelligence_governance.ai_self_diagnosis import (
    AUTO_KB_STEPS,
    AutoFixLayer,
    auto_fix_known_pattern,
)


class TestAutoFixLayer:
    def test_enum_values(self):
        assert AutoFixLayer.L1_AUTO.value == "L1_AutoFix"
        assert AutoFixLayer.L2_SUGGEST.value == "L2_Suggest"
        assert AutoFixLayer.L3_REPORT.value == "L3_Report"

    def test_enum_count(self):
        assert len(AutoFixLayer) == 3

    def test_l1_is_auto(self):
        assert "AutoFix" in AutoFixLayer.L1_AUTO.value

    def test_l3_is_report(self):
        assert "Report" in AutoFixLayer.L3_REPORT.value


class TestAutoFixKnownPattern:
    def test_returns_tuple(self):
        result = auto_fix_known_pattern("some error")
        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_first_element_is_bool(self):
        success, _ = auto_fix_known_pattern("error")
        assert isinstance(success, bool)

    def test_second_element_is_string(self):
        _, message = auto_fix_known_pattern("error")
        assert isinstance(message, str)

    def test_empty_string_input(self):
        success, message = auto_fix_known_pattern("")
        assert isinstance(success, bool)

    def test_returns_true_for_known(self):
        success, _ = auto_fix_known_pattern("any error text")
        assert success is True


class TestAutoKbSteps:
    def test_is_list(self):
        assert isinstance(AUTO_KB_STEPS, list)

    def test_non_empty(self):
        assert len(AUTO_KB_STEPS) > 0

    def test_contains_discovery_step(self):
        all_steps = " ".join(AUTO_KB_STEPS)
        assert "发现" in all_steps or "resolve" in all_steps.lower()

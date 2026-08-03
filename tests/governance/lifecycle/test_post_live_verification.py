# [A_test] module_id: MOD-GOV_post_live_verification | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_post_live_verification
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] PLVCheck枚举不可改值;PLV_CHECKS与PLVCheck一一对应;PLV_CHECK_COUNT=5
# [MODIFY-GUARD] blueprint.md §4;src/zephyr/rollback/__init__.py
# [CONSUMERS] CI;pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError;KeyError
# [TESTS] self
# [A_module] module_id=MOD-INF-021 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.governance.lifecycle_governance.post_live_verification import (
    PLV_CHECK_COUNT,
    PLV_CHECKS,
    PLVCheck,
    PLVSpec,
    get_plv_spec,
)


class TestPLVCheck:
    def test_enum_values(self):
        assert PLVCheck.ORDER_COUNT_DEVIATION.value == "order_count_deviation"
        assert PLVCheck.FILL_RATE_COMPARISON.value == "fill_rate_comparison"
        assert PLVCheck.RISK_CONFORMANCE.value == "risk_conformance"
        assert PLVCheck.DATA_INTEGRITY.value == "data_integrity"
        assert PLVCheck.PNL_RECONCILIATION.value == "pnl_reconciliation"

    def test_enum_member_count(self):
        assert len(PLVCheck) == 5

    def test_enum_is_str(self):
        for member in PLVCheck:
            assert isinstance(member, str)

    def test_enum_from_value(self):
        assert PLVCheck("order_count_deviation") is PLVCheck.ORDER_COUNT_DEVIATION

    def test_enum_invalid_value_raises(self):
        with pytest.raises(ValueError):
            PLVCheck("nonexistent_check")


class TestPLVSpec:
    def test_instantiation(self):
        spec = PLVSpec(
            check=PLVCheck.DATA_INTEGRITY,
            label="test label",
            threshold="test threshold",
            description="test description",
        )
        assert spec.check is PLVCheck.DATA_INTEGRITY
        assert spec.label == "test label"
        assert spec.threshold == "test threshold"
        assert spec.description == "test description"

    def test_instantiation_missing_field_raises(self):
        with pytest.raises(Exception):
            PLVSpec(check=PLVCheck.DATA_INTEGRITY)

    def test_instantiation_empty_strings(self):
        spec = PLVSpec(check=PLVCheck.DATA_INTEGRITY, label="", threshold="", description="")
        assert spec.label == ""
        assert spec.threshold == ""
        assert spec.description == ""


class TestPLVChecks:
    def test_all_checks_present(self):
        for check in PLVCheck:
            assert check in PLV_CHECKS

    def test_each_spec_matches_its_check(self):
        for check, spec in PLV_CHECKS.items():
            assert spec.check is check
            assert isinstance(spec.label, str) and len(spec.label) > 0
            assert isinstance(spec.threshold, str) and len(spec.threshold) > 0
            assert isinstance(spec.description, str) and len(spec.description) > 0

    def test_check_count_constant(self):
        assert PLV_CHECK_COUNT == 5
        assert len(PLV_CHECKS) == PLV_CHECK_COUNT
        assert len(PLVCheck) == PLV_CHECK_COUNT


class TestGetPlvSpec:
    def test_returns_spec_for_valid_check(self):
        spec = get_plv_spec(PLVCheck.ORDER_COUNT_DEVIATION)
        assert spec is not None
        assert spec.check is PLVCheck.ORDER_COUNT_DEVIATION

    def test_returns_none_for_missing_key(self):
        result = get_plv_spec("nonexistent")
        assert result is None

    def test_all_checks_return_non_none(self):
        for check in PLVCheck:
            assert get_plv_spec(check) is not None

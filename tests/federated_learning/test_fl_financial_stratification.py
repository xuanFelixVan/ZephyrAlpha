# [A_test] module_id: SRC-TST-0962 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_financial_stratification
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.collectors.financial_stratification
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_financial_stratification.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.collectors.financial_stratification import FinancialStratification


class TestFinancialStratificationInstantiation:
    def test_creates_with_defaults(self):
        fs = FinancialStratification()
        assert fs.asset_class == "EQUITY"

    def test_creates_with_custom_class(self):
        fs = FinancialStratification(asset_class="FX")
        assert fs.asset_class == "FX"


class TestFinancialStratificationAttributes:
    def test_asset_class_mutable(self):
        fs = FinancialStratification()
        fs.asset_class = "COMMODITY"
        assert fs.asset_class == "COMMODITY"

    def test_boundary_empty_string(self):
        fs = FinancialStratification(asset_class="")
        assert fs.asset_class == ""

    def test_multiple_asset_classes(self):
        classes = ["EQUITY", "FX", "FIXED_INCOME", "COMMODITY"]
        for cls in classes:
            fs = FinancialStratification(asset_class=cls)
            assert fs.asset_class == cls

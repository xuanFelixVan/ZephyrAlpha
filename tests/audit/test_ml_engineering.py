# [A_test] module_id: SRC-TST-1278 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain-infra_ops/drift-detector/blueprint.md
# [MODULE] tests.test_ml_engineering
# [INVARIANTS] Git-native漂移检测;自动对账;漂移预算
# [MODIFY-GUARD] src/zephyr/behavioral-auditor/ml_engineering.py
# [CONSUMERS] CI pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip
# [TESTS] python -m pytest tests/test_ml_engineering.py -q
# [TTL] task_bound

from __future__ import annotations

from zephyr.gov_drift.detector_core.ml_engineering import (
    FEATURE_STORE_SCHEMA,
    LEAK_CHECKS,
    DataLeakCheck,
    MarketRegime,
)


class TestDataLeakCheck:
    def test_enum_values(self):
        assert DataLeakCheck.C1_FACTOR_DATE_GT_MARKET.value == "C1_FACTOR_DATE_GT_MARKET"
        assert DataLeakCheck.C2_TRAIN_TEST_OVERLAP.value == "C2_TRAIN_TEST_OVERLAP"
        assert DataLeakCheck.C3_FUTURE_ACCESS_FACTOR_STORE.value == "C3_FUTURE_ACCESS_FACTOR_STORE"
        assert DataLeakCheck.C4_FACTOR_ANALYSIS_FUTURE_IC.value == "C4_FACTOR_ANALYSIS_FUTURE_IC"
        assert DataLeakCheck.C5_INTRA_GROUP_SIGNAL_EARLY.value == "C5_INTRA_GROUP_SIGNAL_EARLY"
        assert DataLeakCheck.C6_EARNINGS_SPLIT_EX_POST.value == "C6_EARNINGS_SPLIT_EX_POST"

    def test_enum_count(self):
        assert len(DataLeakCheck) == 6

    def test_enum_is_str(self):
        for check in DataLeakCheck:
            assert isinstance(check.value, str)


class TestLeakChecks:
    def test_all_checks_have_descriptions(self):
        for check in DataLeakCheck:
            assert check in LEAK_CHECKS
            assert isinstance(LEAK_CHECKS[check], str)
            assert len(LEAK_CHECKS[check]) > 0

    def test_checks_count_matches_enum(self):
        assert len(LEAK_CHECKS) == len(DataLeakCheck)


class TestMarketRegime:
    def test_enum_values(self):
        assert MarketRegime.BULL.value == "BULL"
        assert MarketRegime.RANGE_BOUND.value == "RANGE_BOUND"
        assert MarketRegime.BEAR.value == "BEAR"

    def test_enum_count(self):
        assert len(MarketRegime) == 3


class TestFeatureStoreSchema:
    def test_required_fields(self):
        required = {"symbol", "date", "factor_name", "value", "computed_at", "pk"}
        assert set(FEATURE_STORE_SCHEMA.keys()) == required

    def test_symbol_not_null(self):
        assert "NOT NULL" in FEATURE_STORE_SCHEMA["symbol"]

    def test_date_not_null(self):
        assert "NOT NULL" in FEATURE_STORE_SCHEMA["date"]

    def test_has_primary_key(self):
        assert "PRIMARY KEY" in FEATURE_STORE_SCHEMA["pk"]

    def test_value_is_real(self):
        assert "REAL" in FEATURE_STORE_SCHEMA["value"]

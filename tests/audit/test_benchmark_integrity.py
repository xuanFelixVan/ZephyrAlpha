# [A_test] module_id: SRC-TST-0424 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-023 | docs/03_modules/_domain_governance/drift_detector/blueprint.md | §benchmark_integrity
# [MODULE] tests.test_benchmark_integrity
# [INVARIANTS] IntegrityDim为str Enum; PIT_MAX_DELAY_MINUTES=15
# [MODIFY-GUARD] 仅当benchmark_integrity公开API变更时修改
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import失败→skip
# [TESTS] pytest tests/test_benchmark_integrity.py -q
# [TTL] task_bound

from zephyr.gov_drift.detector_core.benchmark_integrity import (
    HEALTH_CHECK_INTERVAL,
    PIT_MAX_DELAY_MINUTES,
    IntegrityDim,
)


class TestIntegrityDim:
    def test_all_values(self):
        assert IntegrityDim.MARKET_COVERAGE.value == "MARKET_COVERAGE"
        assert IntegrityDim.FACTOR_CONSISTENCY.value == "FACTOR_CONSISTENCY"
        assert IntegrityDim.BACKTEST_STABILITY.value == "BACKTEST_STABILITY"
        assert IntegrityDim.HFT_FIDELITY.value == "HFT_FIDELITY"

    def test_is_str_enum(self):
        assert isinstance(IntegrityDim.MARKET_COVERAGE, str)

    def test_member_count(self):
        assert len(IntegrityDim) == 4


class TestConstants:
    def test_pit_max_delay(self):
        assert PIT_MAX_DELAY_MINUTES == 15
        assert isinstance(PIT_MAX_DELAY_MINUTES, int)

    def test_health_check_interval_keys(self):
        assert "monthly" in HEALTH_CHECK_INTERVAL
        assert "quarterly" in HEALTH_CHECK_INTERVAL

    def test_health_check_interval_values(self):
        assert isinstance(HEALTH_CHECK_INTERVAL["monthly"], str)
        assert isinstance(HEALTH_CHECK_INTERVAL["quarterly"], str)

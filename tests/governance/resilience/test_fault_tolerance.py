# [A_test] module_id: MOD-GOV_fault_tolerance | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_fault_tolerance
# [DOMAIN] D_GOVERNANCE
# [INVARIANTS] Git-native回滚;SQLite Dump Checkpoint;自动回滚
# [MODIFY-GUARD] docs/03_modules/_domain-infra_ops/rollback-system/blueprint.md
# [CONSUMERS] CI
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.Exception
# [TESTS] self
# [A_module] module_id=MOD-INF-021 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound

from __future__ import annotations

from zephyr.governance.resilience_governance.fault_tolerance import (
    BULKHEAD_ALLOCATION,
    DEGRADATION_LAYERS,
    BulkheadPool,
    DegradationLevel,
    FaultToleranceManager,
    RetryPolicy,
)


class TestBulkheadPool:
    def test_enum_values_exist(self):
        assert BulkheadPool.SIGNAL.value == "Signal"
        assert BulkheadPool.EXECUTION.value == "Execution"
        assert BulkheadPool.RESEARCH.value == "Research"
        assert BulkheadPool.SYSTEM.value == "System"

    def test_allocation_sums_to_one(self):
        total = sum(BULKHEAD_ALLOCATION.values())
        assert abs(total - 1.0) < 1e-9

    def test_all_pools_have_allocation(self):
        for pool in BulkheadPool:
            assert pool in BULKHEAD_ALLOCATION
            assert BULKHEAD_ALLOCATION[pool] > 0


class TestDegradationLevel:
    def test_enum_ordering(self):
        assert DegradationLevel.T0 < DegradationLevel.T1
        assert DegradationLevel.T1 < DegradationLevel.T2
        assert DegradationLevel.T2 < DegradationLevel.T3
        assert DegradationLevel.T3 < DegradationLevel.T4

    def test_all_levels_have_description(self):
        for level in DegradationLevel:
            assert level in DEGRADATION_LAYERS
            assert isinstance(DEGRADATION_LAYERS[level], str)
            assert len(DEGRADATION_LAYERS[level]) > 0


class TestRetryPolicy:
    def test_instantiation(self):
        policy = RetryPolicy()
        assert policy.max_retries == 5
        assert policy.jitter == 0.25
        assert len(policy.sequence) == 5

    def test_backoff_within_range(self):
        policy = RetryPolicy()
        for attempt in range(5):
            delay = policy.backoff(attempt)
            base = policy.sequence[min(attempt, len(policy.sequence) - 1)]
            lower = max(0.001, base - policy.jitter * base)
            upper = base + policy.jitter * base
            assert lower - 1e-9 <= delay <= upper + 1e-9

    def test_backoff_clamped_to_minimum(self):
        policy = RetryPolicy()
        policy.sequence = [0.001]
        policy.jitter = 0.0
        delay = policy.backoff(0)
        assert delay >= 0.001

    def test_backoff_beyond_sequence_uses_last(self):
        policy = RetryPolicy()
        delay = policy.backoff(100)
        assert delay >= 0.001

    def test_should_retry_below_max(self):
        policy = RetryPolicy()
        assert policy.should_retry(0) is True
        assert policy.should_retry(4) is True

    def test_should_retry_at_max(self):
        policy = RetryPolicy()
        assert policy.should_retry(5) is False

    def test_should_retry_beyond_max(self):
        policy = RetryPolicy()
        assert policy.should_retry(99) is False


class TestFaultToleranceManager:
    def test_instantiation(self):
        mgr = FaultToleranceManager()
        assert mgr.degradation_level == DegradationLevel.T0
        assert isinstance(mgr.retry_policy, RetryPolicy)

    def test_is_fully_operational_initially(self):
        mgr = FaultToleranceManager()
        assert mgr.is_fully_operational is True

    def test_degrade_advances_one_level(self):
        mgr = FaultToleranceManager()
        result = mgr.degrade("test reason")
        assert result == DegradationLevel.T1
        assert mgr.degradation_level == DegradationLevel.T1

    def test_degrade_sequential(self):
        mgr = FaultToleranceManager()
        mgr.degrade("r1")
        mgr.degrade("r2")
        mgr.degrade("r3")
        mgr.degrade("r4")
        assert mgr.degradation_level == DegradationLevel.T4
        assert mgr.is_fully_operational is False

    def test_degrade_at_max_stays_at_t4(self):
        mgr = FaultToleranceManager()
        for _ in range(10):
            mgr.degrade("reason")
        assert mgr.degradation_level == DegradationLevel.T4

    def test_degrade_returns_current_level(self):
        mgr = FaultToleranceManager()
        level = mgr.degrade("r")
        assert isinstance(level, DegradationLevel)
        assert level == DegradationLevel.T1

    def test_is_fully_operational_after_degrade(self):
        mgr = FaultToleranceManager()
        mgr.degrade("r")
        assert mgr.is_fully_operational is False

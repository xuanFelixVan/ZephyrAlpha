# [A_test] module_id: SRC-TST-1988 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-605 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.test_circuit_breaker
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
T-V2-005 单元测试 — CircuitBreakerGateway (CBG)
================================================
覆盖场景（验收标准 #7 ≥ 80%）：
  - 失败累积：failure_count 随失败次数正确递增
  - OPEN 触发：failure_count >= threshold 时状态转为 OPEN
  - OPEN 后调用被阻塞：调用直接抛出 CircuitOpenError
  - 手动重置：CBGManager.reset() 将状态恢复为 CLOSED
  - L08 注册表：register_l08_policy / get_l08_policy 基础读写
  - CircuitBreakerCheck.is_open 状态查询
  - CBGManager.list_open_circuits 列举 OPEN 记录
"""

from __future__ import annotations

import pytest

from zephyr.governance.persistence.sqlite_schema import init_db
from zephyr.gov_enforcement.rule_enforcement.circuit_breaker import (
    DEFAULT_THRESHOLD,
    CBGManager,
    CircuitBreakerCheck,
    CircuitBreakerState,
    CircuitOpenError,
)
from zephyr.gov_enforcement.rule_enforcement.circuit_breaker import (
    get_compliance as get_l08_policy,
)
from zephyr.gov_enforcement.rule_enforcement.circuit_breaker import (
    register_compliance as register_l08_policy,
)

# ---------------------------------------------------------------------------
# Fixture：每个测试使用独立内存数据库
# ---------------------------------------------------------------------------


@pytest.fixture
def db(tmp_path):
    """返回已初始化的 SQLite 数据库路径（临时目录）。"""
    db_path = tmp_path / "test_cbg.db"
    init_db(db_path)
    return db_path


@pytest.fixture
def manager(db):
    """返回绑定临时数据库的 CBGManager。"""
    mgr = CBGManager(db, auto_init=False)
    yield mgr
    mgr.close()


# ---------------------------------------------------------------------------
# 1. 初始状态：记录不存在视为 CLOSED
# ---------------------------------------------------------------------------


class TestInitialState:
    def test_get_state_nonexistent_returns_none(self, manager):
        assert manager.get_state("RI-05", "L2a") is None

    def test_is_open_nonexistent_returns_false(self, manager):
        assert manager.is_open("RI-05", "L2a") is False


# ---------------------------------------------------------------------------
# 2. 失败累积
# ---------------------------------------------------------------------------


class TestFailureAccumulation:
    def test_first_failure_creates_record(self, manager):
        manager.record_failure("RI-05", "L2a", reason="连接超时")
        record = manager.get_state("RI-05", "L2a")
        assert record is not None
        assert record.failure_count == 1
        assert record.state == CircuitBreakerState.CLOSED

    def test_failure_count_increments(self, manager):
        for i in range(2):
            manager.record_failure("RI-05", "L2a", threshold=5)
        record = manager.get_state("RI-05", "L2a")
        assert record is not None
        assert record.failure_count == 2
        assert record.state == CircuitBreakerState.CLOSED

    def test_failure_reason_stored(self, manager):
        manager.record_failure("RI-05", "L2a", reason="TimeoutError: exceeded 30s")
        record = manager.get_state("RI-05", "L2a")
        assert record is not None
        assert "TimeoutError" in (record.reason or "")


# ---------------------------------------------------------------------------
# 3. CLOSED → OPEN 状态转移
# ---------------------------------------------------------------------------


class TestCircuitOpenTransition:
    def test_open_triggered_at_threshold(self, manager):
        for _ in range(DEFAULT_THRESHOLD):
            manager.record_failure("RI-05", "L2a", threshold=DEFAULT_THRESHOLD)
        record = manager.get_state("RI-05", "L2a")
        assert record is not None
        assert record.state == CircuitBreakerState.OPEN

    def test_open_triggered_with_custom_threshold(self, manager):
        threshold = 2
        for _ in range(threshold):
            manager.record_failure("M1", "M2", threshold=threshold)
        assert manager.is_open("M1", "M2") is True

    def test_opened_at_is_set_when_open(self, manager):
        for _ in range(DEFAULT_THRESHOLD):
            manager.record_failure("A", "B")
        record = manager.get_state("A", "B")
        assert record is not None
        assert record.opened_at is not None

    def test_below_threshold_remains_closed(self, manager):
        for _ in range(DEFAULT_THRESHOLD - 1):
            manager.record_failure("RI-05", "L2a")
        assert manager.is_open("RI-05", "L2a") is False

    def test_different_pairs_independent(self, manager):
        for _ in range(DEFAULT_THRESHOLD):
            manager.record_failure("A", "B")
        assert manager.is_open("A", "B") is True
        assert manager.is_open("C", "D") is False


# ---------------------------------------------------------------------------
# 4. OPEN 状态下调用被阻断
# ---------------------------------------------------------------------------


class TestOpenBlocking:
    def test_circuit_open_error_raised(self, manager):
        for _ in range(DEFAULT_THRESHOLD):
            manager.record_failure("caller", "target")
        with pytest.raises(CircuitOpenError) as exc_info:
            if manager.is_open("caller", "target"):
                raise CircuitOpenError("caller", "target")
        assert "caller" in str(exc_info.value)
        assert "target" in str(exc_info.value)

    def test_circuit_open_error_contains_caller_target(self):
        err = CircuitOpenError("module_A", "module_B", reason="已熔断")
        assert "module_A" in str(err)
        assert "module_B" in str(err)


# ---------------------------------------------------------------------------
# 5. 手动重置
# ---------------------------------------------------------------------------


class TestManualReset:
    def test_reset_restores_closed_state(self, manager):
        for _ in range(DEFAULT_THRESHOLD):
            manager.record_failure("RI-05", "L2a")
        assert manager.is_open("RI-05", "L2a") is True

        result = manager.reset("RI-05", "L2a")

        assert result is True
        record = manager.get_state("RI-05", "L2a")
        assert record is not None
        assert record.state == CircuitBreakerState.CLOSED
        assert record.failure_count == 0
        assert record.opened_at is None

    def test_reset_nonexistent_returns_false(self, manager):
        result = manager.reset("ghost_caller", "ghost_target")
        assert result is False

    def test_after_reset_failure_count_restarts(self, manager):
        for _ in range(DEFAULT_THRESHOLD):
            manager.record_failure("RI-05", "L2a")
        manager.reset("RI-05", "L2a")
        manager.record_failure("RI-05", "L2a")
        record = manager.get_state("RI-05", "L2a")
        assert record is not None
        assert record.failure_count == 1
        assert record.state == CircuitBreakerState.CLOSED


# ---------------------------------------------------------------------------
# 6. list_open_circuits
# ---------------------------------------------------------------------------


class TestListOpenCircuits:
    def test_no_open_circuits_returns_empty(self, manager):
        assert manager.list_open_circuits() == []

    def test_open_circuits_listed(self, manager):
        for _ in range(DEFAULT_THRESHOLD):
            manager.record_failure("A", "B")
        for _ in range(DEFAULT_THRESHOLD):
            manager.record_failure("C", "D")
        open_list = manager.list_open_circuits()
        open_pairs = {(r.caller_module, r.target_module) for r in open_list}
        assert ("A", "B") in open_pairs
        assert ("C", "D") in open_pairs

    def test_closed_circuit_not_in_list(self, manager):
        manager.record_failure("E", "F", threshold=10)
        assert manager.list_open_circuits() == []


# ---------------------------------------------------------------------------
# 7. CircuitBreakerCheck GateEngine 接口
# ---------------------------------------------------------------------------


class TestCircuitBreakerCheck:
    def test_is_open_false_when_no_record(self, db):
        check = CircuitBreakerCheck(
            caller_module="RI-05",
            target_module="L2a",
            db_path=db,
        )
        assert check.is_open() is False

    def test_is_open_true_when_open(self, db):
        mgr = CBGManager(db, auto_init=False)
        for _ in range(DEFAULT_THRESHOLD):
            mgr.record_failure("RI-05", "L2a")
        mgr.close()

        check = CircuitBreakerCheck(
            caller_module="RI-05",
            target_module="L2a",
            db_path=db,
        )
        assert check.is_open() is True

    def test_violation_message_contains_modules(self, db):
        check = CircuitBreakerCheck(
            caller_module="RI-05",
            target_module="L2a",
            db_path=db,
        )
        msg = check.violation_message()
        assert "RI-05" in msg
        assert "L2a" in msg


# ---------------------------------------------------------------------------
# 8. L08 注册表
# ---------------------------------------------------------------------------


class TestL08Registry:
    def test_register_and_get_policy(self):
        register_l08_policy(
            "RI-06",
            "M3",
            max_retries=5,
            retry_delay_s=2.0,
            rate_limit_per_min=30,
            threshold=4,
        )
        policy = get_l08_policy("RI-06", "M3")
        assert policy is not None
        assert policy["max_retries"] == 5
        assert policy["retry_delay_s"] == 2.0
        assert policy["rate_limit_per_min"] == 30
        assert policy["threshold"] == 4

    def test_get_nonexistent_policy_returns_none(self):
        assert get_l08_policy("GHOST", "MODULE") is None

    def test_register_default_values(self):
        register_l08_policy("RI-07", "M4")
        policy = get_l08_policy("RI-07", "M4")
        assert policy is not None
        assert policy["max_retries"] == 3
        assert policy["threshold"] == DEFAULT_THRESHOLD

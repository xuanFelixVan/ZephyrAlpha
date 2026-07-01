# [A_test] module_id: SRC-TST-1123 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §testing

# [MODULE] tests.test_infra_idempotency

# [INVARIANTS] start→PROCESSING;complete→COMPLETED;相同key重复start抛IdempotencyError

# [MODIFY-GUARD] idempotency.py变更时同步更新

# [CONSUMERS] CI

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT] IdempotencyError

# [TESTS] pytest tests/test_infra_idempotency.py -q
# [TTL] task_bound

import pytest

from zephyr.shared.infra.idempotency import (
    IdempotencyError,
    IdempotencyRecord,
    IdempotencyStatus,
    IdempotencyStore,
    _build_idempotency_key,
)


class TestIdempotencyStatus:
    def test_members(self):
        assert IdempotencyStatus.PROCESSING.value == "PROCESSING"
        assert IdempotencyStatus.COMPLETED.value == "COMPLETED"
        assert IdempotencyStatus.FAILED.value == "FAILED"


class TestIdempotencyRecord:
    def test_defaults(self):
        rec = IdempotencyRecord(key="test", status=IdempotencyStatus.PROCESSING)
        assert rec.result is None
        assert rec.completed_at == 0.0
        assert rec.created_at > 0


class TestIdempotencyStore:
    def test_start_creates_processing_record(self):
        store = IdempotencyStore()
        rec = store.start("key-1")
        assert rec.key == "key-1"
        assert rec.status == IdempotencyStatus.PROCESSING

    def test_complete_sets_result(self):
        store = IdempotencyStore()
        store.start("key-1")
        rec = store.complete("key-1", result={"data": 42})
        assert rec.status == IdempotencyStatus.COMPLETED
        assert rec.result == {"data": 42}
        assert rec.completed_at > 0

    def test_fail_sets_failed(self):
        store = IdempotencyStore()
        store.start("key-1")
        rec = store.fail("key-1")
        assert rec.status == IdempotencyStatus.FAILED
        assert rec.completed_at > 0

    def test_duplicate_start_while_processing_raises(self):
        store = IdempotencyStore()
        store.start("key-1")
        with pytest.raises(IdempotencyError, match="already being processed"):
            store.start("key-1")

    def test_start_completed_key_returns_existing(self):
        store = IdempotencyStore()
        store.start("key-1")
        store.complete("key-1", result="cached")
        rec = store.start("key-1")
        assert rec.status == IdempotencyStatus.COMPLETED
        assert rec.result == "cached"

    def test_get_existing(self):
        store = IdempotencyStore()
        store.start("key-1")
        rec = store.get("key-1")
        assert rec is not None
        assert rec.key == "key-1"

    def test_get_missing_returns_none(self):
        store = IdempotencyStore()
        assert store.get("nonexistent") is None

    def test_complete_nonexistent_raises(self):
        store = IdempotencyStore()
        with pytest.raises(IdempotencyError, match="not found"):
            store.complete("nope", result="x")

    def test_fail_nonexistent_raises(self):
        store = IdempotencyStore()
        with pytest.raises(IdempotencyError, match="not found"):
            store.fail("nope")

    def test_size(self):
        store = IdempotencyStore()
        assert store.size == 0
        store.start("key-1")
        assert store.size == 1
        store.start("key-2")
        assert store.size == 2

    def test_ttl_expiry(self):
        import time

        store = IdempotencyStore(default_ttl_seconds=0.01)
        store.start("key-1")
        store.complete("key-1", result="old")
        time.sleep(0.05)
        rec = store.get("key-1")
        assert rec is None

    def test_start_after_fail_returns_failed(self):
        store = IdempotencyStore()
        store.start("key-1")
        store.fail("key-1")
        rec = store.start("key-1")
        assert rec.status == IdempotencyStatus.FAILED


class TestBuildIdempotencyKey:
    def test_deterministic(self):
        k1 = _build_idempotency_key("op", "a", "b")
        k2 = _build_idempotency_key("op", "a", "b")
        assert k1 == k2

    def test_different_parts_different_key(self):
        k1 = _build_idempotency_key("op", "a")
        k2 = _build_idempotency_key("op", "b")
        assert k1 != k2

    def test_format(self):
        key = _build_idempotency_key("test", "x")
        assert key.startswith("test:")
        assert len(key.split(":")[1]) == 16


class TestIdempotencyError:
    def test_inherits_zephyr_base_error(self):
        from zephyr.shared.foundation.errors import ZephyrBaseError

        err = IdempotencyError("conflict", details={"key": "k"})
        assert isinstance(err, ZephyrBaseError)

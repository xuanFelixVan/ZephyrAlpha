# [A_test] module_id: MOD-GOV_fix_reliability | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-031 | docs/03_modules/_cross_layer/auto_fix_engine/blueprint.md | §3
# [MODULE] tests.test_fix_reliability
# [INVARIANTS] IdempotencyGuard 24h TTL; DeadLetterQueue max 3 retries; ConflictResolver serializes same-file fixes
# [MODIFY-GUARD] blueprint.md §3; auto_fix_config.yaml reliability section
# [CONSUMERS] CI pipeline
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest assertion errors on invariant violation
# [TESTS] tests/test_fix_reliability.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.infrastructure.auto_fix_engine.fix_reliability import (
    ApprovalQueue,
    BlastRadiusEstimator,
    CanaryFixer,
    ConflictResolver,
    DeadLetterQueue,
    FixOrderResolver,
    FixResultCache,
    IdempotencyGuard,
)
from zephyr.infrastructure.auto_fix_engine.models import (
    FixAction,
    FixConfidence,
    FixDeadLetter,
    FixLevel,
    FixStatus,
)


class TestIdempotencyGuard:
    def test_instantiation(self, tmp_path):
        db = str(tmp_path / "idem_test.db")
        ig = IdempotencyGuard(db_path=db, ttl_hours=24)
        assert ig._ttl.total_seconds() == 86400

    def test_check_new_action_allowed(self, tmp_path):
        db = str(tmp_path / "idem_test.db")
        ig = IdempotencyGuard(db_path=db)
        action = FixAction(action_type="test", target="f.py", before="x")
        ok, reason = ig.check(action)
        assert ok is True
        assert reason == ""

    def test_check_duplicate_blocked(self, tmp_path):
        db = str(tmp_path / "idem_test.db")
        ig = IdempotencyGuard(db_path=db)
        action = FixAction(action_type="test", target="f.py", before="x")
        ig.record(action, "completed")
        ok, reason = ig.check(action)
        assert ok is False
        assert "Duplicate fix" in reason

    def test_record_and_check(self, tmp_path):
        db = str(tmp_path / "idem_test.db")
        ig = IdempotencyGuard(db_path=db)
        a1 = FixAction(action_type="fix1", target="a.py", before="old")
        ig.record(a1, "completed")
        a2 = FixAction(action_type="fix1", target="a.py", before="old")
        ok, _ = ig.check(a2)
        assert ok is False

    def test_different_actions_allowed(self, tmp_path):
        db = str(tmp_path / "idem_test.db")
        ig = IdempotencyGuard(db_path=db)
        a1 = FixAction(action_type="fix1", target="a.py", before="old1")
        ig.record(a1, "completed")
        a2 = FixAction(action_type="fix2", target="b.py", before="old2")
        ok, _ = ig.check(a2)
        assert ok is True


class TestConflictResolver:
    def test_instantiation(self):
        cr = ConflictResolver()
        assert cr._locks == {}

    def test_acquire_returns_lock(self):
        cr = ConflictResolver()
        lock = cr.acquire("file.py")
        assert lock is not None

    def test_acquire_same_target_same_lock(self):
        cr = ConflictResolver()
        lock1 = cr.acquire("file.py")
        lock2 = cr.acquire("file.py")
        assert lock1 is lock2

    def test_resolve_orders_by_level_and_confidence(self):
        cr = ConflictResolver()
        a1 = FixAction(action_type="l2_fix", target="f.py", level=FixLevel.L2_LLM, confidence=FixConfidence.HIGH)
        a2 = FixAction(action_type="l1_fix", target="f.py", level=FixLevel.L1_RULE, confidence=FixConfidence.LOW)
        a3 = FixAction(action_type="l1_high", target="f.py", level=FixLevel.L1_RULE, confidence=FixConfidence.HIGH)
        result = cr.resolve([a1, a2, a3])
        assert result[0].level == FixLevel.L1_RULE
        assert result[0].confidence == FixConfidence.HIGH
        assert result[1].level == FixLevel.L1_RULE
        assert result[1].confidence == FixConfidence.LOW
        assert result[2].level == FixLevel.L2_LLM

    def test_resolve_empty_list(self):
        cr = ConflictResolver()
        result = cr.resolve([])
        assert result == []

    def test_is_conflict_no_queue(self):
        cr = ConflictResolver()
        action = FixAction(action_type="test", target="f.py")
        assert cr.is_conflict(action) is False


class TestFixOrderResolver:
    def test_instantiation(self):
        for_ = FixOrderResolver()
        assert for_._dependency_map == {}

    def test_resolve_empty(self):
        for_ = FixOrderResolver()
        assert for_.resolve([]) == []

    def test_resolve_no_dependencies(self):
        for_ = FixOrderResolver()
        a1 = FixAction(action_type="fix_a", target="a.py")
        a2 = FixAction(action_type="fix_b", target="b.py")
        result = for_.resolve([a1, a2])
        assert len(result) == 2

    def test_resolve_with_dependencies(self):
        for_ = FixOrderResolver()
        for_.add_dependency("fix_b", "fix_a")
        a1 = FixAction(action_type="fix_a", target="a.py")
        a2 = FixAction(action_type="fix_b", target="b.py")
        result = for_.resolve([a2, a1])
        types_in_order = [a.action_type for a in result]
        assert types_in_order.index("fix_a") < types_in_order.index("fix_b")

    def test_add_dependency_accumulates(self):
        for_ = FixOrderResolver()
        for_.add_dependency("fix_c", "fix_a")
        for_.add_dependency("fix_c", "fix_b")
        assert "fix_a" in for_._dependency_map["fix_c"]
        assert "fix_b" in for_._dependency_map["fix_c"]


class TestFixResultCache:
    def test_instantiation(self):
        cache = FixResultCache()
        assert cache._max_size == 1000

    def test_set_and_get(self):
        cache = FixResultCache()
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"

    def test_get_missing_key(self):
        cache = FixResultCache()
        assert cache.get("nonexistent") is None

    def test_invalidate(self):
        cache = FixResultCache()
        cache.set("key1", "value1")
        cache.invalidate("key1")
        assert cache.get("key1") is None

    def test_invalidate_nonexistent(self):
        cache = FixResultCache()
        cache.invalidate("no_key")

    def test_max_size_eviction(self):
        cache = FixResultCache(max_size=3)
        cache.set("k1", "v1")
        cache.set("k2", "v2")
        cache.set("k3", "v3")
        cache.set("k4", "v4")
        assert cache.get("k1") is None
        assert cache.get("k4") == "v4"


class TestBlastRadiusEstimator:
    def test_instantiation(self):
        bre = BlastRadiusEstimator()

    def test_estimate_nonexistent_path(self):
        bre = BlastRadiusEstimator()
        action = FixAction(action_type="test", target="nonexistent_path_xyz.py")
        result = bre.estimate(action)
        assert "files" in result
        assert "modules" in result
        assert "lines_estimate" in result
        assert "risk" in result

    def test_estimate_l1_low_risk(self):
        bre = BlastRadiusEstimator()
        action = FixAction(action_type="test", target="some_file.py", level=FixLevel.L1_RULE)
        result = bre.estimate(action)
        assert result["risk"] in ("low", "medium")

    def test_estimate_l3_high_risk(self):
        bre = BlastRadiusEstimator()
        action = FixAction(action_type="test", target="some_file.py", level=FixLevel.L3_AGENT)
        result = bre.estimate(action)
        assert result["risk"] == "high"

    def test_estimate_existing_file(self, tmp_path):
        py_file = tmp_path / "target.py"
        py_file.write_text("line1\nline2\nline3\n", encoding="utf-8")
        bre = BlastRadiusEstimator()
        action = FixAction(action_type="test", target=str(py_file))
        result = bre.estimate(action)
        assert result["lines_estimate"] == 3


class TestDeadLetterQueue:
    def test_instantiation(self):
        dlq = DeadLetterQueue(max_retries=3)
        assert dlq._max_retries == 3
        assert dlq.size == 0

    def test_add(self):
        dlq = DeadLetterQueue()
        action = FixAction(action_type="test", target="f.py")
        entry = dlq.add(action, "timeout")
        assert isinstance(entry, FixDeadLetter)
        assert entry.failure_reason == "timeout"
        assert dlq.size == 1

    def test_retry_within_limit(self):
        dlq = DeadLetterQueue(max_retries=3)
        action = FixAction(action_type="test", target="f.py")
        entry = dlq.add(action, "error")
        result = dlq.retry(entry.dead_letter_id)
        assert result is not None
        assert result.retry_count == 1

    def test_retry_exceeds_max_escalates(self):
        dlq = DeadLetterQueue(max_retries=2)
        action = FixAction(action_type="test", target="f.py")
        entry = dlq.add(action, "error")
        dlq.retry(entry.dead_letter_id)
        dlq.retry(entry.dead_letter_id)
        result = dlq.retry(entry.dead_letter_id)
        assert result is not None
        assert result.escalated is True

    def test_retry_nonexistent(self):
        dlq = DeadLetterQueue()
        result = dlq.retry("nonexistent_id")
        assert result is None

    def test_get_pending(self):
        dlq = DeadLetterQueue(max_retries=3)
        a1 = FixAction(action_type="test", target="f.py")
        dlq.add(a1, "error")
        pending = dlq.get_pending()
        assert len(pending) == 1

    def test_get_escalated(self):
        dlq = DeadLetterQueue(max_retries=1)
        action = FixAction(action_type="test", target="f.py")
        entry = dlq.add(action, "error")
        dlq.retry(entry.dead_letter_id)
        dlq.retry(entry.dead_letter_id)
        escalated = dlq.get_escalated()
        assert len(escalated) == 1

    def test_size_property(self):
        dlq = DeadLetterQueue()
        assert dlq.size == 0
        dlq.add(FixAction(action_type="test", target="f.py"), "err")
        assert dlq.size == 1


class TestApprovalQueue:
    def test_instantiation(self):
        aq = ApprovalQueue()
        assert aq.size == 0

    def test_enqueue(self):
        aq = ApprovalQueue()
        action = FixAction(action_type="test", target="f.py")
        aq.enqueue(action)
        assert aq.size == 1
        assert action.status == FixStatus.APPROVAL_PENDING

    def test_approve(self):
        aq = ApprovalQueue()
        action = FixAction(action_type="test", target="f.py")
        aq.enqueue(action)
        result = aq.approve(action.action_id)
        assert result is not None
        assert result.status == FixStatus.PENDING
        assert aq.size == 0

    def test_approve_nonexistent(self):
        aq = ApprovalQueue()
        result = aq.approve("nonexistent")
        assert result is None

    def test_reject(self):
        aq = ApprovalQueue()
        action = FixAction(action_type="test", target="f.py")
        aq.enqueue(action)
        result = aq.reject(action.action_id)
        assert result is not None
        assert result.status == FixStatus.CANCELLED
        assert aq.size == 0

    def test_reject_nonexistent(self):
        aq = ApprovalQueue()
        result = aq.reject("nonexistent")
        assert result is None

    def test_get_pending(self):
        aq = ApprovalQueue()
        a1 = FixAction(action_type="test1", target="a.py")
        a2 = FixAction(action_type="test2", target="b.py")
        aq.enqueue(a1)
        aq.enqueue(a2)
        pending = aq.get_pending()
        assert len(pending) == 2


class TestCanaryFixer:
    def test_instantiation(self):
        cf = CanaryFixer()
        assert cf._ratios == [0.1, 0.3, 0.5, 1.0]
        assert cf._delay_sec == 60

    def test_custom_ratios(self):
        cf = CanaryFixer(ratios=[0.2, 0.5, 1.0], delay_sec=30)
        assert cf._ratios == [0.2, 0.5, 1.0]
        assert cf._delay_sec == 30

    def test_get_ratio_initial(self):
        cf = CanaryFixer(ratios=[0.1, 0.3, 0.5, 1.0])
        assert cf.get_ratio("fixer_a") == 0.1

    def test_advance(self):
        cf = CanaryFixer(ratios=[0.1, 0.3, 0.5, 1.0])
        cf.advance("fixer_a")
        assert cf.get_ratio("fixer_a") == 0.3
        cf.advance("fixer_a")
        assert cf.get_ratio("fixer_a") == 0.5

    def test_advance_past_end(self):
        cf = CanaryFixer(ratios=[0.1, 0.5])
        cf.advance("fixer_a")
        cf.advance("fixer_a")
        cf.advance("fixer_a")
        assert cf.get_ratio("fixer_a") == 1.0

    def test_should_apply_within_ratio(self):
        cf = CanaryFixer(ratios=[0.5])
        assert cf.should_apply("fixer_a", 1, 10) is True

    def test_should_apply_exceeds_ratio(self):
        cf = CanaryFixer(ratios=[0.1])
        assert cf.should_apply("fixer_a", 5, 10) is False

    def test_should_apply_zero_total(self):
        cf = CanaryFixer(ratios=[0.1])
        assert cf.should_apply("fixer_a", 0, 0) is True

    def test_reset(self):
        cf = CanaryFixer(ratios=[0.1, 0.3])
        cf.advance("fixer_a")
        cf.reset("fixer_a")
        assert cf.get_ratio("fixer_a") == 0.1

    def test_independent_fixer_types(self):
        cf = CanaryFixer(ratios=[0.1, 0.3])
        cf.advance("fixer_a")
        assert cf.get_ratio("fixer_a") == 0.3
        assert cf.get_ratio("fixer_b") == 0.1

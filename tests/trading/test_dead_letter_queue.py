# [A_test] module_id: MOD-GOV_dead_letter_queue | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-009 | docs/03_modules/_cross_layer/pipeline/blueprint.md | §
# [MODULE] tests.test_dead_letter_queue
# [INVARIANTS] enqueue only writes when all modules failed AND status is FAILURE/CLAUDE_RESCUE
# [MODIFY-GUARD] only when DeadLetterQueue public API changes
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] import failure -> skip
# [TESTS] pytest tests/test_dead_letter_queue.py -q
# [TTL] task_bound

from __future__ import annotations

from dataclasses import dataclass

from zephyr.infrastructure.pipeline.dead_letter_queue import DeadLetterQueue
from zephyr.infrastructure.pipeline.models import ModuleResult, ModuleStatus, PipelineStatus


@dataclass
class MockTaskCard:
    task_id: str


def _make_results(statuses: list[ModuleStatus], errors: list[list[str]] | None = None) -> list[ModuleResult]:
    results = []
    for i, s in enumerate(statuses):
        errs = errors[i] if errors and i < len(errors) else (["error"] if s == ModuleStatus.FAILURE else [])
        results.append(
            ModuleResult(
                module_id=f"M{i + 1}",
                pipeline="A",
                model="deepseek",
                status=s,
                errors=errs,
            )
        )
    return results


class TestDeadLetterQueueInit:
    def test_instantiation(self):
        dlq = DeadLetterQueue()
        assert dlq.count == 0
        assert dlq.entries == []


class TestDeadLetterQueueEnqueue:
    def test_enqueue_all_failed_failure_status(self):
        dlq = DeadLetterQueue()
        card = MockTaskCard(task_id="T-001")
        results = _make_results([ModuleStatus.FAILURE, ModuleStatus.FAILURE])
        entry = dlq.enqueue(card, results, PipelineStatus.FAILURE, max_retries=3)
        assert entry is not None
        assert entry.task_id == "T-001"
        assert entry.retry_count == 3
        assert dlq.count == 1

    def test_enqueue_all_failed_claude_rescue_status(self):
        dlq = DeadLetterQueue()
        card = MockTaskCard(task_id="T-002")
        results = _make_results([ModuleStatus.FAILURE])
        entry = dlq.enqueue(card, results, PipelineStatus.CLAUDE_RESCUE, max_retries=5)
        assert entry is not None
        assert entry.retry_count == 5

    def test_enqueue_rejects_non_failure_status(self):
        dlq = DeadLetterQueue()
        card = MockTaskCard(task_id="T-003")
        results = _make_results([ModuleStatus.FAILURE])
        entry = dlq.enqueue(card, results, PipelineStatus.SUCCESS)
        assert entry is None
        assert dlq.count == 0

    def test_enqueue_rejects_partial_failure(self):
        dlq = DeadLetterQueue()
        card = MockTaskCard(task_id="T-004")
        results = _make_results([ModuleStatus.FAILURE, ModuleStatus.SUCCESS])
        entry = dlq.enqueue(card, results, PipelineStatus.FAILURE)
        assert entry is None
        assert dlq.count == 0

    def test_enqueue_rejects_pending_status(self):
        dlq = DeadLetterQueue()
        card = MockTaskCard(task_id="T-005")
        results = _make_results([ModuleStatus.FAILURE])
        entry = dlq.enqueue(card, results, PipelineStatus.PENDING)
        assert entry is None

    def test_enqueue_rejects_running_status(self):
        dlq = DeadLetterQueue()
        card = MockTaskCard(task_id="T-006")
        results = _make_results([ModuleStatus.FAILURE])
        entry = dlq.enqueue(card, results, PipelineStatus.RUNNING)
        assert entry is None

    def test_enqueue_captures_first_error(self):
        dlq = DeadLetterQueue()
        card = MockTaskCard(task_id="T-007")
        results = _make_results(
            [ModuleStatus.FAILURE],
            errors=[["timeout", "503"]],
        )
        entry = dlq.enqueue(card, results, PipelineStatus.FAILURE)
        assert entry is not None
        assert entry.last_error == "timeout"

    def test_enqueue_no_errors_uses_unknown(self):
        dlq = DeadLetterQueue()
        card = MockTaskCard(task_id="T-008")
        results = [ModuleResult(module_id="M1", pipeline="A", model="deepseek", status=ModuleStatus.FAILURE, errors=[])]
        entry = dlq.enqueue(card, results, PipelineStatus.FAILURE)
        assert entry is not None
        assert entry.last_error == "unknown"

    def test_enqueue_empty_results_with_failure_status(self):
        dlq = DeadLetterQueue()
        card = MockTaskCard(task_id="T-009")
        results: list[ModuleResult] = []
        all_failed = all(r.status == ModuleStatus.FAILURE for r in results)
        assert all_failed is True
        entry = dlq.enqueue(card, results, PipelineStatus.FAILURE)
        assert entry is not None
        assert entry.last_error == "unknown"

    def test_enqueue_multiple_entries(self):
        dlq = DeadLetterQueue()
        for i in range(3):
            card = MockTaskCard(task_id=f"T-{i:03d}")
            results = _make_results([ModuleStatus.FAILURE])
            dlq.enqueue(card, results, PipelineStatus.FAILURE)
        assert dlq.count == 3

    def test_enqueue_failure_reason_message(self):
        dlq = DeadLetterQueue()
        card = MockTaskCard(task_id="T-010")
        results = _make_results([ModuleStatus.FAILURE, ModuleStatus.FAILURE, ModuleStatus.FAILURE])
        entry = dlq.enqueue(card, results, PipelineStatus.FAILURE)
        assert "3 modules failed" in entry.failure_reason


class TestDeadLetterQueueDrain:
    def test_drain_returns_entries(self):
        dlq = DeadLetterQueue()
        card = MockTaskCard(task_id="T-001")
        results = _make_results([ModuleStatus.FAILURE])
        dlq.enqueue(card, results, PipelineStatus.FAILURE)
        drained = dlq.drain()
        assert len(drained) == 1
        assert drained[0].task_id == "T-001"

    def test_drain_clears_queue(self):
        dlq = DeadLetterQueue()
        card = MockTaskCard(task_id="T-001")
        results = _make_results([ModuleStatus.FAILURE])
        dlq.enqueue(card, results, PipelineStatus.FAILURE)
        dlq.drain()
        assert dlq.count == 0

    def test_drain_empty_queue(self):
        dlq = DeadLetterQueue()
        drained = dlq.drain()
        assert drained == []

    def test_drain_twice(self):
        dlq = DeadLetterQueue()
        card = MockTaskCard(task_id="T-001")
        results = _make_results([ModuleStatus.FAILURE])
        dlq.enqueue(card, results, PipelineStatus.FAILURE)
        first = dlq.drain()
        second = dlq.drain()
        assert len(first) == 1
        assert len(second) == 0


class TestDeadLetterQueueEntries:
    def test_entries_returns_copy(self):
        dlq = DeadLetterQueue()
        card = MockTaskCard(task_id="T-001")
        results = _make_results([ModuleStatus.FAILURE])
        dlq.enqueue(card, results, PipelineStatus.FAILURE)
        entries = dlq.entries
        entries.clear()
        assert dlq.count == 1

    def test_entries_empty(self):
        dlq = DeadLetterQueue()
        assert dlq.entries == []


class TestDeadLetterQueueCount:
    def test_count_zero(self):
        dlq = DeadLetterQueue()
        assert dlq.count == 0

    def test_count_increments(self):
        dlq = DeadLetterQueue()
        for i in range(5):
            card = MockTaskCard(task_id=f"T-{i:03d}")
            results = _make_results([ModuleStatus.FAILURE])
            dlq.enqueue(card, results, PipelineStatus.FAILURE)
        assert dlq.count == 5


class TestDeadLetterQueueSaveLoadState:
    def test_save_state_empty(self):
        dlq = DeadLetterQueue()
        state = dlq.save_state()
        assert state == []

    def test_save_state_with_entries(self):
        dlq = DeadLetterQueue()
        card = MockTaskCard(task_id="T-001")
        results = _make_results([ModuleStatus.FAILURE])
        dlq.enqueue(card, results, PipelineStatus.FAILURE)
        state = dlq.save_state()
        assert len(state) == 1
        assert state[0]["task_id"] == "T-001"

    def test_load_state(self):
        dlq = DeadLetterQueue()
        state = [
            {"task_id": "T-100", "failure_reason": "timeout", "retry_count": 3, "last_error": "503"},
            {"task_id": "T-101", "failure_reason": "crash", "retry_count": 1, "last_error": "segfault"},
        ]
        dlq.load_state(state)
        assert dlq.count == 2
        assert dlq.entries[0].task_id == "T-100"
        assert dlq.entries[1].failure_reason == "crash"

    def test_load_state_empty(self):
        dlq = DeadLetterQueue()
        card = MockTaskCard(task_id="T-001")
        results = _make_results([ModuleStatus.FAILURE])
        dlq.enqueue(card, results, PipelineStatus.FAILURE)
        dlq.load_state([])
        assert dlq.count == 0

    def test_save_load_roundtrip(self):
        dlq = DeadLetterQueue()
        card = MockTaskCard(task_id="T-001")
        results = _make_results([ModuleStatus.FAILURE])
        dlq.enqueue(card, results, PipelineStatus.FAILURE)
        state = dlq.save_state()
        dlq2 = DeadLetterQueue()
        dlq2.load_state(state)
        assert dlq2.count == 1
        assert dlq2.entries[0].task_id == "T-001"

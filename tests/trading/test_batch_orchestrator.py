# [A_test] module_id: SRC-TST-0419 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md | §
# [MODULE] tests.test_batch_orchestrator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] tests/test_batch_orchestrator.py
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock

from zephyr.orchestrator.execution.batch_orchestrator import BatchOrchestrator, BatchProgress


class TestBatchProgressInstantiation:
    def test_default_construction(self):
        bp = BatchProgress(batch_id="test-batch")
        assert bp.batch_id == "test-batch"
        assert bp.ready == 0
        assert bp.in_progress == 0
        assert bp.completed == 0
        assert bp.failed == 0
        assert bp.total == 0

    def test_with_values(self):
        bp = BatchProgress(batch_id="b1", ready=5, in_progress=3, completed=10, failed=2, total=20)
        assert bp.ready == 5
        assert bp.in_progress == 3
        assert bp.completed == 10
        assert bp.failed == 2
        assert bp.total == 20


class TestBatchProgressPctDone:
    def test_pct_done_zero_total(self):
        bp = BatchProgress(batch_id="b1", total=0)
        assert bp.pct_done == 0.0

    def test_pct_done_partial(self):
        bp = BatchProgress(batch_id="b1", completed=5, failed=1, total=10)
        assert bp.pct_done == 60.0

    def test_pct_done_complete(self):
        bp = BatchProgress(batch_id="b1", completed=8, failed=2, total=10)
        assert bp.pct_done == 100.0

    def test_pct_done_no_progress(self):
        bp = BatchProgress(batch_id="b1", completed=0, failed=0, total=10)
        assert bp.pct_done == 0.0


class TestBatchProgressStr:
    def test_str_format(self):
        bp = BatchProgress(batch_id="b1", ready=5, in_progress=2, completed=3, failed=1, total=11)
        s = str(bp)
        assert "b1" in s
        assert "3/11" in s
        assert "36.4%" in s


class TestBatchOrchestratorInstantiation:
    def test_default_construction(self):
        repo = MagicMock()
        bo = BatchOrchestrator(repo, batch_id="b1", worker_id="w1")
        assert bo.batch_id == "b1"
        assert bo.worker_id == "w1"

    def test_custom_stale_timeout(self):
        repo = MagicMock()
        bo = BatchOrchestrator(repo, batch_id="b1", worker_id="w1", stale_timeout_minutes=60)
        assert bo._stale_timeout == 60


class TestBatchOrchestratorClaimNext:
    def test_claim_next_returns_task(self):
        repo = MagicMock()
        mock_card = MagicMock()
        mock_card.task_id = "T-001"
        repo.claim_next.return_value = mock_card
        bo = BatchOrchestrator(repo, batch_id="b1", worker_id="w1")
        result = bo.claim_next()
        assert result is not None
        assert result.task_id == "T-001"
        repo.recover_stale_claims.assert_called_once()

    def test_claim_next_returns_none(self):
        repo = MagicMock()
        repo.claim_next.return_value = None
        bo = BatchOrchestrator(repo, batch_id="b1", worker_id="w1")
        result = bo.claim_next()
        assert result is None


class TestBatchOrchestratorMarkDone:
    def test_mark_done(self):
        repo = MagicMock()
        bo = BatchOrchestrator(repo, batch_id="b1", worker_id="w1")
        bo.mark_done("T-001")
        repo.transition.assert_called_once_with("T-001", "COMPLETED")


class TestBatchOrchestratorMarkFailed:
    def test_mark_failed(self):
        repo = MagicMock()
        bo = BatchOrchestrator(repo, batch_id="b1", worker_id="w1")
        bo.mark_failed("T-001", "error msg")
        repo.transition.assert_called_once_with("T-001", "FAILED")

    def test_mark_failed_no_reason(self):
        repo = MagicMock()
        bo = BatchOrchestrator(repo, batch_id="b1", worker_id="w1")
        bo.mark_failed("T-001")
        repo.transition.assert_called_once_with("T-001", "FAILED")


class TestBatchOrchestratorRecoverStaleClaims:
    def test_recover_stale_claims(self):
        repo = MagicMock()
        repo.recover_stale_claims.return_value = 3
        bo = BatchOrchestrator(repo, batch_id="b1", worker_id="w1")
        count = bo.recover_stale_claims()
        assert count == 3
        repo.recover_stale_claims.assert_called_once_with("b1", 30)


class TestBatchOrchestratorProgress:
    def test_progress(self):
        repo = MagicMock()
        repo.batch_progress.return_value = {
            "READY": 5,
            "IN_PROGRESS": 2,
            "COMPLETED": 10,
            "FAILED": 1,
            "TOTAL": 18,
        }
        bo = BatchOrchestrator(repo, batch_id="b1", worker_id="w1")
        bp = bo.progress()
        assert isinstance(bp, BatchProgress)
        assert bp.ready == 5
        assert bp.in_progress == 2
        assert bp.completed == 10
        assert bp.failed == 1
        assert bp.total == 18
        assert bp.batch_id == "b1"

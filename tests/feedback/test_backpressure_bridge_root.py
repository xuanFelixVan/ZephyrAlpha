# [A_test] module_id: SRC-TST-0405 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §
# [MODULE] tests.test_backpressure_bridge
# [INVARIANTS] sync_evolution_proposals_to_backpressure returns dict with throttled/critical_count/skipped keys
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from unittest.mock import MagicMock, patch

from zephyr.feedback_loop.backpressure_bridge import (
    sync_evolution_proposals_to_backpressure,
)
from zephyr.feedback_loop.evolution_engine import Severity


class TestSyncEvolutionProposalsInstantiation:
    def test_function_exists(self):
        assert callable(sync_evolution_proposals_to_backpressure)


class TestSyncEvolutionProposalsNoManager:
    def test_none_manager_returns_skipped(self):
        result = sync_evolution_proposals_to_backpressure([], None)
        assert result["skipped"] is True
        assert result["throttled"] is False
        assert result["critical_count"] == 0

    def test_empty_proposals_returns_skipped(self):
        mgr = MagicMock()
        result = sync_evolution_proposals_to_backpressure([], mgr)
        assert result["skipped"] is True


class TestSyncEvolutionProposalsNoCritical:
    def test_non_critical_proposals_no_throttle(self):
        mgr = MagicMock()
        proposal = MagicMock()
        proposal.severity = Severity.HIGH
        result = sync_evolution_proposals_to_backpressure([proposal], mgr)
        assert result["throttled"] is False
        assert result["critical_count"] == 0
        assert result["skipped"] is False


class TestSyncEvolutionProposalsWithCritical:
    def test_critical_proposals_triggers_throttle(self):
        mgr = MagicMock()
        proposal = MagicMock()
        proposal.severity = Severity.CRITICAL
        with patch("zephyr.infrastructure.pipeline.backpressure_manager.emit_throttle") as mock_emit:
            result = sync_evolution_proposals_to_backpressure([proposal], mgr)
            assert result["throttled"] is True
            assert result["critical_count"] == 1
            assert result["skipped"] is False

    def test_multiple_critical_proposals(self):
        mgr = MagicMock()
        p1 = MagicMock()
        p1.severity = Severity.CRITICAL
        p2 = MagicMock()
        p2.severity = Severity.CRITICAL
        with patch("zephyr.infrastructure.pipeline.backpressure_manager.emit_throttle"):
            result = sync_evolution_proposals_to_backpressure([p1, p2], mgr)
            assert result["critical_count"] == 2


class TestSyncEvolutionProposalsBoundary:
    def test_mixed_severity_only_critical_counted(self):
        mgr = MagicMock()
        p_critical = MagicMock()
        p_critical.severity = Severity.CRITICAL
        p_high = MagicMock()
        p_high.severity = Severity.HIGH
        with patch("zephyr.infrastructure.pipeline.backpressure_manager.emit_throttle"):
            result = sync_evolution_proposals_to_backpressure([p_critical, p_high], mgr)
            assert result["critical_count"] == 1

    def test_custom_symbol(self):
        mgr = MagicMock()
        proposal = MagicMock()
        proposal.severity = Severity.CRITICAL
        with patch("zephyr.infrastructure.pipeline.backpressure_manager.emit_throttle") as mock_emit:
            sync_evolution_proposals_to_backpressure([proposal], mgr, symbol="custom_symbol")
            mock_emit.assert_called_once()
            call_args = mock_emit.call_args
            assert call_args[0][1] == "custom_symbol"

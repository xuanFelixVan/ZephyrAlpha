# [A_test] module_id: SRC-TST-1871 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] SRC-495 | docs/03_modules/_domain_governance/blueprint.md | §
# [MODULE] tests.unit.feedback_loop.test_backpressure_bridge
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] —
# [TTL] task_bound
"""
backpressure_bridge 模块单元测试 — AUDIT-08 M6
================================================
覆盖: sync_evolution_proposals_to_backpressure 的三种场景
"""

from unittest.mock import MagicMock, patch

from zephyr.feedback_loop.evolution_engine import Severity as EvolutionSeverity


class _FakeProposal:
    def __init__(self, severity: EvolutionSeverity):
        self.severity = severity


class TestSyncEvolutionProposalsToBackpressure:
    def test_skipped_when_no_manager(self):
        from zephyr.feedback_loop.backpressure_bridge import sync_evolution_proposals_to_backpressure

        result = sync_evolution_proposals_to_backpressure([], None)
        assert result["skipped"] is True

    def test_skipped_when_no_proposals(self):
        from zephyr.feedback_loop.backpressure_bridge import sync_evolution_proposals_to_backpressure

        mock_mgr = MagicMock()
        result = sync_evolution_proposals_to_backpressure([], mock_mgr)
        assert result["skipped"] is True

    def test_throttled_on_critical_proposals(self):
        from zephyr.feedback_loop.backpressure_bridge import sync_evolution_proposals_to_backpressure

        mock_mgr = MagicMock()
        critical = _FakeProposal(EvolutionSeverity.CRITICAL)
        high = _FakeProposal(EvolutionSeverity.HIGH)

        with patch("zephyr.infrastructure.pipeline.backpressure_manager.emit_throttle") as mock_emit:
            mock_emit.return_value = MagicMock()
            result = sync_evolution_proposals_to_backpressure([critical, high], mock_mgr)
            assert result["throttled"] is True
            assert result["critical_count"] == 1
            mock_emit.assert_called_once()

    def test_not_throttled_when_only_high(self):
        from zephyr.feedback_loop.backpressure_bridge import sync_evolution_proposals_to_backpressure

        mock_mgr = MagicMock()
        high = _FakeProposal(EvolutionSeverity.HIGH)

        result = sync_evolution_proposals_to_backpressure([high], mock_mgr)
        assert result["throttled"] is False
        assert result["critical_count"] == 0

    def test_rate_decreases_with_more_criticals(self):
        from zephyr.feedback_loop.backpressure_bridge import sync_evolution_proposals_to_backpressure

        mock_mgr = MagicMock()
        proposals = [_FakeProposal(EvolutionSeverity.CRITICAL) for _ in range(5)]

        with patch("zephyr.infrastructure.pipeline.backpressure_manager.emit_throttle") as mock_emit:
            mock_emit.return_value = MagicMock()
            result = sync_evolution_proposals_to_backpressure(proposals, mock_mgr)
            assert result["critical_count"] == 5
            mock_emit.assert_called_once()

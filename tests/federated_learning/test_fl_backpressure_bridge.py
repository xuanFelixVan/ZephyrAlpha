# [A_test] module_id: SRC-TST-0936 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_fl_backpressure_bridge
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.backpressure_bridge
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_fl_backpressure_bridge.py
# [TTL] task_bound

from __future__ import annotations

from dataclasses import dataclass
from unittest.mock import MagicMock, patch

from zephyr.feedback_loop.backpressure_bridge import sync_evolution_proposals_to_backpressure


@dataclass
class FakeProposal:
    severity: object = None


class TestSyncEvolutionProposalsToBackpressure:
    def test_skips_when_no_backpressure_manager(self):
        result = sync_evolution_proposals_to_backpressure([], None)
        assert result["skipped"] is True
        assert result["throttled"] is False

    def test_skips_when_no_proposals(self):
        result = sync_evolution_proposals_to_backpressure([], MagicMock())
        assert result["skipped"] is True

    def test_skips_when_no_critical_proposals(self):
        from zephyr.feedback_loop.evolution_engine import Severity

        proposals = [FakeProposal(severity=Severity.HIGH)]
        result = sync_evolution_proposals_to_backpressure(proposals, MagicMock())
        assert result["throttled"] is False
        assert result["critical_count"] == 0

    def test_throttles_on_critical_proposals(self):
        from zephyr.feedback_loop.evolution_engine import Severity

        proposals = [FakeProposal(severity=Severity.CRITICAL)]
        mock_bp = MagicMock()
        with patch("zephyr.infrastructure.pipeline.backpressure_manager.emit_throttle") as mock_emit:
            result = sync_evolution_proposals_to_backpressure(proposals, mock_bp)
            assert result["throttled"] is True
            assert result["critical_count"] == 1

    def test_boundary_empty_list_with_manager(self):
        result = sync_evolution_proposals_to_backpressure([], MagicMock())
        assert result["skipped"] is True

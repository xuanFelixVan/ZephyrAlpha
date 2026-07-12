# [A_test] module_id: SRC-TST-0905 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_feedback_self_audit
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.gov_audit.feedback_self_audit import (
    CircularDependencyResult,
    FeedbackNode,
    FeedbackSelfAuditor,
)


class TestFeedbackSelfAuditorInit:
    def test_default_threshold(self):
        auditor = FeedbackSelfAuditor()
        assert auditor._amplification_threshold == 2.0

    def test_custom_threshold(self):
        auditor = FeedbackSelfAuditor(amplification_threshold=3.0)
        assert auditor._amplification_threshold == 3.0


class TestDetectSelfReinforcement:
    def test_insufficient_events_returns_empty(self):
        auditor = FeedbackSelfAuditor()
        events = [
            {"action_type": "write", "trust-score": 0.5},
            {"action_type": "write", "trust-score": 0.6},
        ]
        results = auditor.detect_self_reinforcement("agent-1", events)
        assert results == []

    def test_self_reinforcing_loop_detected(self):
        auditor = FeedbackSelfAuditor(amplification_threshold=1.5)
        events = []
        for i in range(9):
            events.append({"action_type": "write", "trust-score": 0.1 + i * 0.15})
        results = auditor.detect_self_reinforcement("agent-1", events)
        write_results = [r for r in results if "write" in r.loop_nodes]
        assert len(write_results) >= 1
        assert write_results[0].is_self_reinforcing is True
        assert write_results[0].amplification_factor >= 1.5

    def test_no_reinforcement_returns_empty(self):
        auditor = FeedbackSelfAuditor(amplification_threshold=10.0)
        events = [
            {"action_type": "read", "trust-score": 0.5},
            {"action_type": "read", "trust-score": 0.5},
            {"action_type": "read", "trust-score": 0.5},
        ]
        results = auditor.detect_self_reinforcement("agent-1", events)
        reinforcement_results = [r for r in results if r.is_self_reinforcing and "read" in r.loop_nodes]
        assert len(reinforcement_results) == 0

    def test_self_feedback_on_own_action(self):
        auditor = FeedbackSelfAuditor()
        events = [
            {"action_type": "write", "feedback_target": "write", "trust-score": 0.5},
            {"action_type": "write", "feedback_target": "write", "trust-score": 0.5},
            {"action_type": "write", "feedback_target": "write", "trust-score": 0.5},
        ]
        results = auditor.detect_self_reinforcement("agent-1", events)
        self_feedback = [r for r in results if r.loop_length == 3]
        assert len(self_feedback) >= 1

    def test_empty_events_returns_empty(self):
        auditor = FeedbackSelfAuditor()
        results = auditor.detect_self_reinforcement("agent-1", [])
        assert results == []


class TestCheckCircular:
    def test_no_cycle_detected(self):
        auditor = FeedbackSelfAuditor()
        nodes = [
            FeedbackNode(node_id="A", node_type="agent", outputs_to=["B"]),
            FeedbackNode(node_id="B", node_type="agent", outputs_to=["C"]),
            FeedbackNode(node_id="C", node_type="agent", outputs_to=[]),
        ]
        result = auditor.check_circular(nodes)
        assert isinstance(result, CircularDependencyResult)
        assert result.has_circular is False
        assert result.cycle_count == 0

    def test_cycle_detected(self):
        auditor = FeedbackSelfAuditor()
        nodes = [
            FeedbackNode(node_id="A", node_type="agent", outputs_to=["B"]),
            FeedbackNode(node_id="B", node_type="agent", outputs_to=["C"]),
            FeedbackNode(node_id="C", node_type="agent", outputs_to=["A"]),
        ]
        result = auditor.check_circular(nodes)
        assert result.has_circular is True
        assert result.cycle_count >= 1

    def test_dict_input_normalized(self):
        auditor = FeedbackSelfAuditor()
        nodes = [
            {"node_id": "A", "node_type": "agent", "outputs_to": ["B"]},
            {"node_id": "B", "node_type": "agent", "outputs_to": []},
        ]
        result = auditor.check_circular(nodes)
        assert result.has_circular is False

    def test_empty_nodes_no_cycle(self):
        auditor = FeedbackSelfAuditor()
        result = auditor.check_circular([])
        assert result.has_circular is False

    def test_invalid_type_raises(self):
        auditor = FeedbackSelfAuditor()
        with pytest.raises(TypeError):
            auditor.check_circular(["not_a_valid_node"])

    def test_self_cycle_detected(self):
        auditor = FeedbackSelfAuditor()
        nodes = [
            FeedbackNode(node_id="A", node_type="agent", outputs_to=["A"]),
        ]
        result = auditor.check_circular(nodes)
        assert result.has_circular is True

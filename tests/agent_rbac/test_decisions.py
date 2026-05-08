"""决策注册表测试."""
from __future__ import annotations

import pytest
from zephyr.agent_rbac.decision_registry import DecisionRegistry


class TestDecisions:
    def test_log_decision(self):
        registry = DecisionRegistry()
        record = registry.log("agent_1", "read", "config.yml", "ALLOWED", rule_id="R-001")
        assert record.agent_id == "agent_1"
        assert record.result == "ALLOWED"

    def test_query_by_agent(self):
        registry = DecisionRegistry()
        registry.log("agent_a", "read", "x", "ALLOWED")
        registry.log("agent_b", "write", "y", "DENIED")
        results = registry.query(agent_id="agent_a")
        assert len(results) == 1
        assert results[0].result == "ALLOWED"

    def test_stats(self):
        registry = DecisionRegistry()
        registry.log("a", "read", "x", "ALLOWED")
        registry.log("a", "write", "y", "DENIED")
        registry.log("b", "read", "z", "ALLOWED")

        stats = registry.stats()
        assert stats["total"] == 3
        assert stats["allowed"] == 2
        assert stats["denied"] == 1

# [A_test] module_id: SRC-TST-0461 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain_governance/audit_trail/blueprint.md | §
# [MODULE] tests.test_bridges_trust_bridge
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import patch

import pytest

from zephyr.gov_audit.bridges.audit_trust_bridge import AuditTrustBridge


@pytest.fixture
def bridge():
    return AuditTrustBridge()


class TestAuditTrustBridge:
    def test_instantiation(self):
        b = AuditTrustBridge()
        assert b._TRUST_SCORE_CHANGE_THRESHOLD == 0.3

    def test_get_trust_score_unavailable(self, bridge):
        with patch("builtins.__import__", side_effect=ImportError("no module")):
            result = bridge.get_trust_score("agent-1")
            assert result is None

    def test_enrich_event_with_trust_no_agent(self, bridge):
        event = {"event_type": "test"}
        result = bridge.enrich_event_with_trust(event)
        assert "trust-score" not in result

    def test_enrich_event_with_trust_available(self, bridge):
        with patch.object(bridge, "get_trust_score", return_value=0.85):
            event = {"agent_id": "agent-1", "event_type": "test"}
            result = bridge.enrich_event_with_trust(event)
            assert result["trust-score"] == 0.85
            assert result["trust_tier"] == "TIER_2_AUTO_REVERT"

    def test_enrich_event_with_trust_unavailable(self, bridge):
        with patch.object(bridge, "get_trust_score", return_value=None):
            event = {"agent_id": "agent-1", "event_type": "test"}
            result = bridge.enrich_event_with_trust(event)
            assert "trust-score" not in result

    def test_detect_trust_score_change_critical(self, bridge):
        with patch.object(bridge, "get_trust_score", return_value=0.2):
            result = bridge.detect_trust_score_change("agent-1", previous_score=0.8)
            assert result is not None
            assert result["severity"] == "CRITICAL"
            assert result["details"]["direction"] == "drop"

    def test_detect_trust_score_change_high(self, bridge):
        with patch.object(bridge, "get_trust_score", return_value=0.5):
            result = bridge.detect_trust_score_change("agent-1", previous_score=0.8)
            assert result is not None
            assert result["severity"] == "HIGH"

    def test_detect_trust_score_change_no_change(self, bridge):
        with patch.object(bridge, "get_trust_score", return_value=0.75):
            result = bridge.detect_trust_score_change("agent-1", previous_score=0.7)
            assert result is None

    def test_detect_trust_score_change_none_previous(self, bridge):
        result = bridge.detect_trust_score_change("agent-1", previous_score=None)
        assert result is None

    def test_detect_trust_score_change_none_current(self, bridge):
        with patch.object(bridge, "get_trust_score", return_value=None):
            result = bridge.detect_trust_score_change("agent-1", previous_score=0.5)
            assert result is None

    def test_batch_enrich(self, bridge):
        with patch.object(bridge, "get_trust_score", return_value=0.9):
            events = [
                {"agent_id": "a1", "event_type": "test"},
                {"agent_id": "a2", "event_type": "test"},
            ]
            results = bridge.batch_enrich(events)
            assert len(results) == 2
            assert all("trust-score" in r for r in results)

    def test_classify_tier_tier2(self):
        assert AuditTrustBridge._classify_tier(0.9) == "TIER_2_AUTO_REVERT"

    def test_classify_tier_tier1(self):
        assert AuditTrustBridge._classify_tier(0.6) == "TIER_1_PROPOSE_ONLY"

    def test_classify_tier_tier0(self):
        assert AuditTrustBridge._classify_tier(0.3) == "TIER_0_READ_ONLY"

    def test_detect_trust_score_rise(self, bridge):
        with patch.object(bridge, "get_trust_score", return_value=0.9):
            result = bridge.detect_trust_score_change("agent-1", previous_score=0.5)
            assert result is not None
            assert result["details"]["direction"] == "rise"

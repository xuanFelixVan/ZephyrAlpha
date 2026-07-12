# [A_test] module_id: SRC-TST-1198 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_knowledge_injection_pre_flight_verifier
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.forensic.knowledge_injection_pre_flight_verifier
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_knowledge_injection_pre_flight_verifier.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.feedback_loop.forensic.knowledge_injection_pre_flight_verifier import (
    DryRunResult,
    KnowledgeInjectionPreFlightVerifier,
)


class TestDryRunResult:
    def test_creation_defaults(self):
        dr = DryRunResult(rule_id="r1")
        assert dr.caught_incident_earlier is False
        assert dr.false_positives == 0
        assert dr.true_positives == 0
        assert dr.net_benefit == 0.0

    def test_creation_with_values(self):
        dr = DryRunResult(rule_id="r2", true_positives=5, false_positives=1, net_benefit=0.4)
        assert dr.true_positives == 5
        assert dr.net_benefit == 0.4


class TestKnowledgeInjectionPreFlightVerifier:
    def test_instantiation_defaults(self):
        v = KnowledgeInjectionPreFlightVerifier()
        assert v.historical_incidents == []
        assert v.max_stored_incidents == 50
        assert v.benefit_threshold == 0.2
        assert v.dry_run_log == []

    def test_add_historical_incident(self):
        v = KnowledgeInjectionPreFlightVerifier()
        v.add_historical_incident({"id": "inc-1", "metrics": {"cpu": 90}})
        assert len(v.historical_incidents) == 1

    def test_add_historical_incident_truncation(self):
        v = KnowledgeInjectionPreFlightVerifier(max_stored_incidents=5)
        for i in range(10):
            v.add_historical_incident({"id": f"inc-{i}"})
        assert len(v.historical_incidents) <= 5

    def test_verify_rule_approved(self):
        v = KnowledgeInjectionPreFlightVerifier()
        for i in range(10):
            v.add_historical_incident(
                {
                    "id": f"inc-{i}",
                    "metrics": {"cpu": 90.0 + i},
                    "would_detect_earlier": True,
                }
            )
        rule = {"rule_id": "high-cpu", "rule_type": "threshold", "condition": "cpu", "threshold": 80}
        result = v.verify_rule(rule)
        assert result["approved"] is True
        assert result["recommendation"] == "DEPLOY"
        assert result["true_positives"] > 0

    def test_verify_rule_rejected(self):
        v = KnowledgeInjectionPreFlightVerifier()
        for i in range(10):
            v.add_historical_incident({"id": f"inc-{i}", "metrics": {"cpu": 10.0}})
        rule = {"rule_id": "high-cpu", "rule_type": "threshold", "condition": "cpu", "threshold": 80}
        result = v.verify_rule(rule)
        assert result["approved"] is False
        assert result["recommendation"] == "REJECT"
        assert result["true_positives"] == 0

    def test_verify_rule_no_incidents(self):
        v = KnowledgeInjectionPreFlightVerifier()
        rule = {"rule_id": "any", "rule_type": "threshold", "condition": "cpu", "threshold": 50}
        result = v.verify_rule(rule)
        assert result["total_incidents_tested"] == 0
        assert result["net_benefit"] == 0.0

    def test_verify_rule_unknown_rule_type(self):
        v = KnowledgeInjectionPreFlightVerifier()
        v.add_historical_incident({"id": "inc-1", "metrics": {"cpu": 90}})
        rule = {"rule_id": "r1", "rule_type": "unknown_type", "condition": "cpu", "threshold": 80}
        result = v.verify_rule(rule)
        assert result["true_positives"] == 0

    def test_dry_run_log_capped(self):
        v = KnowledgeInjectionPreFlightVerifier()
        v.add_historical_incident({"id": "inc-1", "metrics": {"cpu": 90}})
        for i in range(110):
            v.verify_rule({"rule_id": f"r-{i}", "rule_type": "threshold", "condition": "cpu", "threshold": 80})
        assert len(v.dry_run_log) <= 100

    def test_verify_rule_early_catch_detection(self):
        v = KnowledgeInjectionPreFlightVerifier()
        v.add_historical_incident({"id": "inc-1", "metrics": {"cpu": 95}, "would_detect_earlier": True})
        rule = {"rule_id": "r1", "rule_type": "threshold", "condition": "cpu", "threshold": 80}
        result = v.verify_rule(rule)
        assert result["early_catches"] == 1

    def test_rule_would_catch_threshold_type(self):
        v = KnowledgeInjectionPreFlightVerifier()
        incident = {"metrics": {"latency": 500.0}}
        rule = {"rule_type": "threshold", "condition": "latency", "threshold": 100}
        assert v._rule_would_catch(rule, incident) is True

    def test_rule_would_not_catch_below_threshold(self):
        v = KnowledgeInjectionPreFlightVerifier()
        incident = {"metrics": {"latency": 50.0}}
        rule = {"rule_type": "threshold", "condition": "latency", "threshold": 100}
        assert v._rule_would_catch(rule, incident) is False

    def test_rule_would_catch_no_matching_metric(self):
        v = KnowledgeInjectionPreFlightVerifier()
        incident = {"metrics": {"cpu": 90.0}}
        rule = {"rule_type": "threshold", "condition": "latency", "threshold": 100}
        assert v._rule_would_catch(rule, incident) is False

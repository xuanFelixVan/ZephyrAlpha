# [A_test] module_id: SRC-TST-1113 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-FEEDBACK_LOOP | docs/03_modules/_cross_layer/feedback_loop/blueprint.md | §test
# [MODULE] tests.test_incident_knowledge_injector
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] zephyr.feedback_loop.diagnosers.diagnosis.incident_knowledge_injector
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest
# [TESTS] tests/test_incident_knowledge_injector.py
# [TTL] task_bound


from zephyr.feedback_loop.diagnosers.diagnosis.incident_knowledge_injector import (
    IncidentKnowledgeInjector,
    InjectedRule,
)


class TestIncidentKnowledgeInjectorInstantiation:
    def test_default_instantiation(self):
        inj = IncidentKnowledgeInjector()
        assert inj.injected_rules == {}
        assert inj.max_rules_per_rca == 5
        assert inj.total_rules_injected == 0

    def test_custom_parameters(self):
        inj = IncidentKnowledgeInjector(max_rules_per_rca=3)
        assert inj.max_rules_per_rca == 3


class TestInjectedRule:
    def test_default_values(self):
        rule = InjectedRule(
            rule_id="R1",
            source_rca_id="INC1",
            rule_type="detection",
            condition="test condition",
            threshold=0.5,
            created_at=1000.0,
        )
        assert rule.validated is False
        assert rule.active is False

    def test_custom_values(self):
        rule = InjectedRule(
            rule_id="R2",
            source_rca_id="INC2",
            rule_type="threshold",
            condition="metric > 10",
            threshold=10.0,
            created_at=2000.0,
            validated=True,
            active=True,
        )
        assert rule.validated is True
        assert rule.active is True


class TestExtractAndInject:
    def test_empty_findings(self):
        inj = IncidentKnowledgeInjector()
        result = inj.extract_and_inject({})
        assert result == []
        assert inj.total_rules_injected == 0

    def test_root_causes_injected(self):
        inj = IncidentKnowledgeInjector()
        findings = {
            "incident_id": "INC-001",
            "root_causes": ["database connection pool exhausted due to leak in query handler"],
        }
        result = inj.extract_and_inject(findings)
        assert len(result) >= 1
        assert inj.total_rules_injected >= 1

    def test_short_root_cause_skipped(self):
        inj = IncidentKnowledgeInjector()
        findings = {
            "incident_id": "INC-002",
            "root_causes": ["short"],
        }
        result = inj.extract_and_inject(findings)
        assert len(result) == 0

    def test_metric_deviations_injected(self):
        inj = IncidentKnowledgeInjector()
        findings = {
            "incident_id": "INC-003",
            "root_causes": [],
            "metric_deviations": {"cpu_usage": 0.85, "mem_usage": 0.92},
        }
        result = inj.extract_and_inject(findings)
        assert len(result) == 2

    def test_max_rules_per_rca_respected(self):
        inj = IncidentKnowledgeInjector(max_rules_per_rca=1)
        findings = {
            "incident_id": "INC-004",
            "root_causes": [
                "first root cause with enough length to pass validation",
                "second root cause with enough length to pass validation",
            ],
        }
        result = inj.extract_and_inject(findings)
        root_cause_rules = [r for r in result if r.startswith("INJ-")]
        assert len(root_cause_rules) <= 1

    def test_missing_incident_id_uses_unknown(self):
        inj = IncidentKnowledgeInjector()
        findings = {
            "root_causes": ["a sufficiently long root cause description for testing"],
        }
        result = inj.extract_and_inject(findings)
        for rule_id in result:
            rule = inj.injected_rules[rule_id]
            assert rule.source_rca_id == "unknown"


class TestValidateRules:
    def test_no_rules(self):
        inj = IncidentKnowledgeInjector()
        result = inj.validate_rules()
        assert result == {}

    def test_valid_rule_activated(self):
        inj = IncidentKnowledgeInjector()
        findings = {
            "incident_id": "INC-010",
            "root_causes": ["database connection pool exhausted due to leak in query handler"],
        }
        inj.extract_and_inject(findings)
        result = inj.validate_rules()
        for rule_id, val in result.items():
            assert "active" in val

    def test_already_validated_skipped(self):
        inj = IncidentKnowledgeInjector()
        findings = {
            "incident_id": "INC-011",
            "root_causes": ["database connection pool exhausted due to leak in query handler"],
        }
        inj.extract_and_inject(findings)
        inj.validate_rules()
        result = inj.validate_rules()
        assert result == {}


class TestGetActiveRules:
    def test_no_active_rules(self):
        inj = IncidentKnowledgeInjector()
        assert inj.get_active_rules() == []

    def test_active_rules_after_validation(self):
        inj = IncidentKnowledgeInjector()
        findings = {
            "incident_id": "INC-020",
            "root_causes": ["database connection pool exhausted due to leak in query handler"],
        }
        inj.extract_and_inject(findings)
        inj.validate_rules()
        active = inj.get_active_rules()
        for rule in active:
            assert "rule_id" in rule
            assert "type" in rule
            assert "condition" in rule
            assert "threshold" in rule
            assert "source" in rule

    def test_inactive_rules_not_returned(self):
        inj = IncidentKnowledgeInjector()
        findings = {
            "incident_id": "INC-021",
            "root_causes": ["short"],
        }
        inj.extract_and_inject(findings)
        assert inj.get_active_rules() == []

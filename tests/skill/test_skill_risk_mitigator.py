# [A_test] module_id: MOD-GOV_skill_risk_mitigator | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_risk_mitigator
# [INVARIANTS] risks dict is class-level; tests must not mutate it
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] get_risk returns None for unknown risk_id
# [TESTS] tests/test_skill_risk_mitigator.py
# [TTL] task_bound

from __future__ import annotations

from zephyr.autonomy_core.skills.skill_risk_mitigator import RiskMitigator


class TestRiskMitigatorInstantiation:
    def test_risks_dict_populated(self):
        assert len(RiskMitigator.risks) >= 12

    def test_risks_have_required_keys(self):
        for rid, data in RiskMitigator.risks.items():
            assert "title" in data, f"Risk {rid} missing 'title'"
            assert "mitigation" in data, f"Risk {rid} missing 'mitigation'"
            assert "severity" in data, f"Risk {rid} missing 'severity'"

    def test_risks_ids_format(self):
        for rid in RiskMitigator.risks:
            assert rid.startswith("R"), f"Risk ID {rid} does not start with R"


class TestGetRisk:
    def test_returns_existing_risk(self):
        result = RiskMitigator.get_risk("R1")
        assert result is not None
        assert "title" in result
        assert "mitigation" in result
        assert "severity" in result

    def test_returns_none_for_unknown_risk(self):
        assert RiskMitigator.get_risk("R999") is None

    def test_returns_none_for_empty_string(self):
        assert RiskMitigator.get_risk("") is None

    def test_returns_correct_risk_data(self):
        r7 = RiskMitigator.get_risk("R7")
        assert r7["severity"] == "critical"
        assert "session" in r7["mitigation"].lower() or "跨session" in r7["title"]


class TestAllRisks:
    def test_returns_list(self):
        result = RiskMitigator.all_risks()
        assert isinstance(result, list)
        assert len(result) >= 12

    def test_each_entry_has_id(self):
        for entry in RiskMitigator.all_risks():
            assert "id" in entry
            assert "title" in entry
            assert "mitigation" in entry
            assert "severity" in entry

    def test_ids_match_keys(self):
        result = RiskMitigator.all_risks()
        returned_ids = {e["id"] for e in result}
        expected_ids = set(RiskMitigator.risks.keys())
        assert returned_ids == expected_ids


class TestBySeverity:
    def test_high_severity(self):
        result = RiskMitigator.by_severity("high")
        assert len(result) > 0
        for entry in result:
            assert entry["severity"] == "high"

    def test_critical_severity(self):
        result = RiskMitigator.by_severity("critical")
        assert len(result) > 0
        for entry in result:
            assert entry["severity"] == "critical"

    def test_unknown_severity_returns_empty(self):
        result = RiskMitigator.by_severity("nonexistent")
        assert result == []

    def test_empty_string_severity_returns_empty(self):
        result = RiskMitigator.by_severity("")
        assert result == []


class TestHighSeverityRisks:
    def test_includes_high_and_critical(self):
        result = RiskMitigator.high_severity_risks()
        severities = {e["severity"] for e in result}
        assert "high" in severities or "critical" in severities

    def test_no_medium_or_low(self):
        result = RiskMitigator.high_severity_risks()
        for entry in result:
            assert entry["severity"] in ("high", "critical")

    def test_result_is_list(self):
        assert isinstance(RiskMitigator.high_severity_risks(), list)

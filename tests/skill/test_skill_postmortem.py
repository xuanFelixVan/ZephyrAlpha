# [A_test] module_id: MOD-GOV_skill_postmortem | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_postmortem
# [INVARIANTS] SkillPostmortem methods are classmethods; analyze returns dict with required keys
# [MODIFY-GUARD] changes require review of skill_postmortem.py API
# [CONSUMERS] pytest
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] analyze returns dict; _infer_symptom_category returns str; _generate_actions returns dict
# [TESTS] pytest tests/test_skill_postmortem.py -q
# [TTL] task_bound


from zephyr.autonomy_core.skills.skill_postmortem import SkillPostmortem


class TestSkillPostmortemInferSymptomCategory:
    def test_registration_category(self):
        assert SkillPostmortem.infer_symptom_category("KeyError: skill not found") == "registration"

    def test_registration_missing(self):
        assert SkillPostmortem.infer_symptom_category("missing skill in registry") == "registration"

    def test_budget_category(self):
        assert SkillPostmortem.infer_symptom_category("token budget exceeded") == "budget"

    def test_gate_category(self):
        assert SkillPostmortem.infer_symptom_category("gate rejected execution") == "gate"

    def test_performance_category(self):
        assert SkillPostmortem.infer_symptom_category("timeout after 30s") == "performance"

    def test_security_category(self):
        assert SkillPostmortem.infer_symptom_category("security injection detected") == "security"

    def test_drift_category(self):
        assert SkillPostmortem.infer_symptom_category("stale skill version detected") == "drift"

    def test_unknown_category(self):
        assert SkillPostmortem.infer_symptom_category("something unexpected happened") == "unknown"

    def test_empty_error_message(self):
        assert SkillPostmortem.infer_symptom_category("") == "unknown"

    def test_case_insensitive(self):
        assert SkillPostmortem.infer_symptom_category("KEYERROR NOT FOUND") == "registration"


class TestSkillPostmortemAnalyze:
    def test_analyze_returns_required_keys(self):
        result = SkillPostmortem.analyze("SKILL-TEST-001", "KeyError: skill not found")
        required_keys = [
            "incident_id",
            "skill_id",
            "symptom_category",
            "failed_operation",
            "original_error",
            "root_cause",
            "root_cause_chain",
            "corrective_actions",
            "preventive_actions",
            "timestamp",
            "closed",
        ]
        for key in required_keys:
            assert key in result, f"Missing key: {key}"

    def test_analyze_registration_error(self):
        result = SkillPostmortem.analyze("SKILL-TEST-002", "KeyError: skill not found")
        assert result["symptom_category"] == "registration"
        assert result["skill_id"] == "SKILL-TEST-002"
        assert result["closed"] is False
        assert len(result["root_cause_chain"]) >= 5
        assert len(result["corrective_actions"]) >= 1
        assert len(result["preventive_actions"]) >= 1

    def test_analyze_budget_error(self):
        result = SkillPostmortem.analyze("SKILL-TEST-003", "token budget exceeded")
        assert result["symptom_category"] == "budget"
        corrective_actions = result["corrective_actions"]
        assert any("Compact skill" in a["action"] for a in corrective_actions)

    def test_analyze_gate_error(self):
        result = SkillPostmortem.analyze("SKILL-TEST-004", "gate rejected execution")
        assert result["symptom_category"] == "gate"
        corrective_actions = result["corrective_actions"]
        assert any("gate configuration" in a["action"].lower() for a in corrective_actions)

    def test_analyze_with_failed_operation(self):
        result = SkillPostmortem.analyze("SKILL-TEST-005", "KeyError: skill not found", failed_operation="load_skill")
        assert result["failed_operation"] == "load_skill"

    def test_analyze_incident_id_format(self):
        result = SkillPostmortem.analyze("SKILL-TEST-006", "timeout error")
        assert result["incident_id"].startswith("PM-SKILL-TEST-006-")

    def test_analyze_drift_error(self):
        result = SkillPostmortem.analyze("SKILL-TEST-007", "stale skill version detected")
        assert result["symptom_category"] == "drift"
        assert len(result["root_cause_chain"]) >= 5


class TestSkillPostmortemGenerateActions:
    def test_registration_actions(self):
        result = SkillPostmortem.generate_actions("SKILL-TEST", "registration", ["root1"])
        assert len(result["corrective"]) >= 1
        assert len(result["preventive"]) >= 1
        assert any(a["priority"] == "P0" for a in result["corrective"])

    def test_budget_actions(self):
        result = SkillPostmortem.generate_actions("SKILL-TEST", "budget", ["root1"])
        assert any("Compact skill" in a["action"] for a in result["corrective"])

    def test_gate_actions(self):
        result = SkillPostmortem.generate_actions("SKILL-TEST", "gate", ["root1"])
        assert any("gate" in a["action"].lower() for a in result["corrective"])

    def test_unknown_category_still_has_preventive(self):
        result = SkillPostmortem.generate_actions("SKILL-TEST", "unknown", ["root1"])
        assert len(result["preventive"]) >= 1

    def test_preventive_always_includes_regression(self):
        result = SkillPostmortem.generate_actions("SKILL-TEST", "registration", ["root1"])
        assert any("regression" in a["action"].lower() for a in result["preventive"])


class TestSkillPostmortemUnwindWhy:
    def test_unwind_returns_layers(self):
        result = SkillPostmortem.unwind_why("SKILL-TEST", "registration", "KeyError: not found")
        assert len(result) >= 5
        for entry in result:
            assert "layer" in entry
            assert "question" in entry
            assert "reason" in entry
            assert "evidence" in entry

    def test_unwind_first_layer_has_reason(self):
        result = SkillPostmortem.unwind_why("SKILL-TEST", "registration", "KeyError: not found")
        assert result[0]["layer"] == 1
        assert "SKILL-TEST" in result[0]["reason"]

    def test_unwind_budget_symptom(self):
        result = SkillPostmortem.unwind_why("SKILL-TEST", "budget", "token exceeded")
        assert "budget" in result[0]["reason"].lower() or "exceeded" in result[0]["reason"].lower()

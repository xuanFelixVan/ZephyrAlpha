# [A_test] module_id: MOD-GOV_skill_model_evolution | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_model_evolution
# [INVARIANTS] assess_impact returns risk level; unknown model returns risk=unknown
# [MODIFY-GUARD] changes require review of skill_model_evolution.py API
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] returns error dict for unknown models; never raises
# [TESTS] pytest tests/test_skill_model_evolution.py -q
# [TTL] task_bound


from zephyr.autonomy_core.skills.skill_model_evolution import MODEL_PROFILES, SkillModelEvolution


class TestSkillModelEvolutionInstantiation:
    def test_class_exists(self):
        assert SkillModelEvolution is not None

    def test_has_assess_impact(self):
        assert hasattr(SkillModelEvolution, "assess_impact")

    def test_has_find_model(self):
        assert hasattr(SkillModelEvolution, "find_model")


class TestFindModel:
    def test_exact_match(self):
        result = SkillModelEvolution.find_model("deepseek-v3")
        assert result is not None
        assert result["family"] == "deepseek"

    def test_case_insensitive(self):
        result = SkillModelEvolution.find_model("DeepSeek-V3")
        assert result is not None
        assert result["family"] == "deepseek"

    def test_partial_match(self):
        result = SkillModelEvolution.find_model("claude-sonnet")
        assert result is not None
        assert result["family"] == "claude"

    def test_family_match(self):
        result = SkillModelEvolution.find_model("deepseek-custom-model")
        assert result is not None
        assert result["family"] == "deepseek"

    def test_unknown_model_returns_none(self):
        result = SkillModelEvolution.find_model("nonexistent-model-xyz")
        assert result is None

    def test_empty_string_returns_first_match(self):
        result = SkillModelEvolution.find_model("")
        assert result is not None

    def test_all_known_models_findable(self):
        for name in MODEL_PROFILES:
            result = SkillModelEvolution.find_model(name)
            assert result is not None, f"Failed to find model: {name}"


class TestCheckToolCompat:
    def test_compatible_models(self):
        old = {"tool_support": ["read_file", "write_file", "grep"]}
        new = {"tool_support": ["read_file", "write_file", "grep", "glob"]}
        result = SkillModelEvolution.check_tool_compat(old, new)
        assert result["compatible"] is True
        assert result["score"] == 100.0
        assert result["tools_lost"] == []

    def test_lost_tools(self):
        old = {"tool_support": ["read_file", "write_file", "run_command"]}
        new = {"tool_support": ["read_file", "write_file"]}
        result = SkillModelEvolution.check_tool_compat(old, new)
        assert result["compatible"] is False
        assert "run_command" in result["tools_lost"]
        assert result["score"] < 100.0

    def test_empty_old_tools(self):
        old = {"tool_support": []}
        new = {"tool_support": ["read_file"]}
        result = SkillModelEvolution.check_tool_compat(old, new)
        assert result["compatible"] is True
        assert result["score"] == 100.0

    def test_gained_tools(self):
        old = {"tool_support": ["read_file"]}
        new = {"tool_support": ["read_file", "write_file"]}
        result = SkillModelEvolution.check_tool_compat(old, new)
        assert "write_file" in result["tools_gained"]


class TestCheckStyleCompat:
    def test_shared_styles(self):
        old = {"recommended_style": ["structured", "step-by-step", "table"]}
        new = {"recommended_style": ["structured", "step-by-step", "chain-of-thought"]}
        result = SkillModelEvolution.check_style_compat(old, new)
        assert result["compatible"] is True
        assert len(result["styles_shared"]) >= 2

    def test_no_shared_styles(self):
        old = {"recommended_style": ["style_a", "style_b"]}
        new = {"recommended_style": ["style_c", "style_d"]}
        result = SkillModelEvolution.check_style_compat(old, new)
        assert result["compatible"] is False
        assert result["styles_shared"] == []

    def test_empty_old_styles(self):
        old = {"recommended_style": []}
        new = {"recommended_style": ["structured"]}
        result = SkillModelEvolution.check_style_compat(old, new)
        assert result["score"] == 0.0


class TestCheckBudgetImpact:
    def test_same_efficiency(self):
        old = {"token_efficiency": 0.85, "max_context": 65536}
        new = {"token_efficiency": 0.85, "max_context": 65536}
        result = SkillModelEvolution.check_budget_impact(old, new)
        assert result["compatible"] is True
        assert result["efficiency_change_pct"] == 0.0

    def test_lower_efficiency(self):
        old = {"token_efficiency": 0.90, "max_context": 131072}
        new = {"token_efficiency": 0.50, "max_context": 32768}
        result = SkillModelEvolution.check_budget_impact(old, new)
        assert result["efficiency_change_pct"] < 0

    def test_zero_old_efficiency(self):
        old = {"token_efficiency": 0.0, "max_context": 65536}
        new = {"token_efficiency": 0.85, "max_context": 65536}
        result = SkillModelEvolution.check_budget_impact(old, new)
        assert "score" in result


class TestComputeRisk:
    def test_minimal_risk(self):
        assert SkillModelEvolution.compute_risk([95, 92, 90]) == "minimal"

    def test_low_risk(self):
        assert SkillModelEvolution.compute_risk([75, 80, 70]) == "low"

    def test_medium_risk(self):
        assert SkillModelEvolution.compute_risk([55, 60, 50]) == "medium"

    def test_high_risk(self):
        assert SkillModelEvolution.compute_risk([35, 40, 30]) == "high"

    def test_critical_risk(self):
        assert SkillModelEvolution.compute_risk([10, 15, 20]) == "critical"

    def test_empty_scores(self):
        assert SkillModelEvolution.compute_risk([]) == "minimal"

    def test_boundary_90(self):
        assert SkillModelEvolution.compute_risk([90, 90, 90]) == "minimal"

    def test_boundary_70(self):
        assert SkillModelEvolution.compute_risk([70, 70, 70]) == "low"

    def test_boundary_50(self):
        assert SkillModelEvolution.compute_risk([50, 50, 50]) == "medium"

    def test_boundary_30(self):
        assert SkillModelEvolution.compute_risk([30, 30, 30]) == "high"


class TestGenerateActions:
    def test_minimal_risk_no_changes(self):
        tool = {"tools_lost": []}
        style = {"compatible": True, "styles_new_only": []}
        budget = {"compatible": True, "context_ratio": 1.0}
        actions = SkillModelEvolution.generate_actions(tool, style, budget, "minimal")
        assert any(a["priority"] == "P3" for a in actions)

    def test_lost_tools_generates_p0(self):
        tool = {"tools_lost": ["run_command"]}
        style = {"compatible": True, "styles_new_only": []}
        budget = {"compatible": True, "context_ratio": 1.0}
        actions = SkillModelEvolution.generate_actions(tool, style, budget, "low")
        assert any(a["priority"] == "P0" for a in actions)

    def test_incompatible_style_generates_p1(self):
        tool = {"tools_lost": []}
        style = {"compatible": False, "styles_new_only": ["expert", "chain-of-thought"]}
        budget = {"compatible": True, "context_ratio": 1.0}
        actions = SkillModelEvolution.generate_actions(tool, style, budget, "medium")
        assert any(a["priority"] == "P1" for a in actions)

    def test_high_risk_generates_bench_action(self):
        tool = {"tools_lost": []}
        style = {"compatible": True, "styles_new_only": []}
        budget = {"compatible": True, "context_ratio": 1.0}
        actions = SkillModelEvolution.generate_actions(tool, style, budget, "high")
        assert any("SkillsBench" in a["action"] for a in actions)


class TestAssessImpact:
    def test_known_models(self):
        result = SkillModelEvolution.assess_impact("SKILL-DOM-TS-001", "deepseek-v3", "claude-sonnet-4")
        assert result["skill_id"] == "SKILL-DOM-TS-001"
        assert result["old_model"] == "deepseek-v3"
        assert result["new_model"] == "claude-sonnet-4"
        assert result["risk"] in ("minimal", "low", "medium", "high", "critical")
        assert "scores" in result
        assert "actions" in result

    def test_unknown_old_model(self):
        result = SkillModelEvolution.assess_impact("SKILL-DOM-TS-001", "nonexistent-old", "deepseek-v3")
        assert result["risk"] == "unknown"
        assert "error" in result
        assert result["actions"] == []

    def test_unknown_new_model(self):
        result = SkillModelEvolution.assess_impact("SKILL-DOM-TS-001", "deepseek-v3", "nonexistent-new")
        assert result["risk"] == "unknown"
        assert "error" in result

    def test_same_model(self):
        result = SkillModelEvolution.assess_impact("SKILL-DOM-TS-001", "deepseek-v3", "deepseek-v3")
        assert result["risk"] == "minimal"
        assert result["overall_score"] == 100.0

    def test_result_has_profiles(self):
        result = SkillModelEvolution.assess_impact("SKILL-DOM-TS-001", "deepseek-v3", "claude-sonnet-4")
        assert "old_profile" in result
        assert "new_profile" in result
        assert "family" in result["old_profile"]
        assert "max_context" in result["old_profile"]

    def test_overall_score_is_average(self):
        result = SkillModelEvolution.assess_impact("SKILL-DOM-TS-001", "deepseek-v3", "claude-sonnet-4")
        scores = result["scores"]
        expected_avg = round(
            (
                scores["tool_compatibility"]["score"]
                + scores["style_compatibility"]["score"]
                + scores["budget_impact"]["score"]
            )
            / 3,
            1,
        )
        assert result["overall_score"] == expected_avg

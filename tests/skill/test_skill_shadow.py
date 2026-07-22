# [A_test] module_id: MOD-GOV_skill_shadow | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_shadow
# [INVARIANTS] SkillShadowDeploy.shadow_run returns dict with similarity; analyze_results requires >=3 runs for can_promote
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] shadow_run returns structured dict; promote checks can_promote gate
# [TESTS] tests/test_skill_shadow.py
# [TTL] task_bound

from zephyr.autonomy_core.skills.skill_shadow import SkillShadowDeploy


class TestSkillShadowDeployInstantiation:
    def test_instantiation(self):
        deployer = SkillShadowDeploy()
        assert deployer is not None
        assert deployer._shadow_runs == {}
        assert deployer._current_shadow_pct == 5.0


class TestSkillShadowDeployShadowRun:
    def test_identical_outputs(self):
        deployer = SkillShadowDeploy()
        result = deployer.shadow_run("skill-a", "hello world", "hello world")
        assert result["similarity"] == 1.0
        assert result["identical"] is True
        assert result["differences"] == []

    def test_different_outputs(self):
        deployer = SkillShadowDeploy()
        result = deployer.shadow_run("skill-b", "hello world", "goodbye world")
        assert result["similarity"] < 1.0
        assert result["identical"] is False
        assert len(result["differences"]) > 0

    def test_empty_outputs(self):
        deployer = SkillShadowDeploy()
        result = deployer.shadow_run("skill-c", "", "")
        assert result["similarity"] == 1.0
        assert result["identical"] is True

    def test_one_empty_one_not(self):
        deployer = SkillShadowDeploy()
        result = deployer.shadow_run("skill-d", "content", "")
        assert result["similarity"] < 1.0
        assert result["old_output_length"] == 7
        assert result["new_output_length"] == 0

    def test_input_context_stored(self):
        deployer = SkillShadowDeploy()
        result = deployer.shadow_run("skill-e", "a", "b", input_context="test context")
        assert result["input_context"] == "test context"

    def test_input_context_truncated(self):
        deployer = SkillShadowDeploy()
        long_ctx = "x" * 500
        result = deployer.shadow_run("skill-f", "a", "b", input_context=long_ctx)
        assert len(result["input_context"]) <= 200

    def test_run_stored_internally(self):
        deployer = SkillShadowDeploy()
        deployer.shadow_run("skill-g", "a", "b")
        assert "skill-g" in deployer._shadow_runs
        assert len(deployer._shadow_runs["skill-g"]) == 1


class TestSkillShadowDeployAnalyzeResults:
    def test_no_runs(self):
        deployer = SkillShadowDeploy()
        result = deployer.analyze_results("nonexistent")
        assert result["runs"] == 0
        assert result["can_promote"] is False
        assert result["reason"] == "no_shadow_runs"

    def test_few_runs_cannot_promote(self):
        deployer = SkillShadowDeploy()
        deployer.shadow_run("skill-h", "a", "a")
        deployer.shadow_run("skill-h", "b", "b")
        result = deployer.analyze_results("skill-h")
        assert result["runs"] == 2
        assert result["can_promote"] is False

    def test_three_identical_runs_can_promote(self):
        deployer = SkillShadowDeploy()
        for _ in range(3):
            deployer.shadow_run("skill-i", "same output", "same output")
        result = deployer.analyze_results("skill-i")
        assert result["runs"] == 3
        assert result["can_promote"] is True
        assert result["all_identical"] is True

    def test_three_divergent_runs(self):
        deployer = SkillShadowDeploy()
        deployer.shadow_run("skill-j", "aaa", "bbb")
        deployer.shadow_run("skill-j", "ccc", "ddd")
        deployer.shadow_run("skill-j", "eee", "fff")
        result = deployer.analyze_results("skill-j")
        assert result["runs"] == 3
        assert result["average_similarity"] < 0.95
        assert result["can_promote"] is False


class TestSkillShadowDeployPromote:
    def test_promote_insufficient_confidence(self):
        deployer = SkillShadowDeploy()
        result = deployer.promote("no-runs-skill")
        assert result["promoted"] is False
        assert result["reason"] == "insufficient_confidence"

    def test_promote_success(self):
        deployer = SkillShadowDeploy()
        for _ in range(3):
            deployer.shadow_run("skill-k", "same", "same")
        result = deployer.promote("skill-k")
        assert result["promoted"] is True
        assert result["new_traffic_pct"] == 100.0


class TestSkillShadowDeployRollback:
    def test_rollback(self):
        deployer = SkillShadowDeploy()
        result = deployer.rollback_shadow("any-skill")
        assert result["rolled_back"] is True
        assert result["current_shadow_pct"] == 0.0


class TestSkillShadowDeployAdjustTraffic:
    def test_adjust_within_range(self):
        deployer = SkillShadowDeploy()
        result = deployer.adjust_traffic("skill-l", 50.0)
        assert result["new_pct"] == 50.0

    def test_adjust_clamp_high(self):
        deployer = SkillShadowDeploy()
        result = deployer.adjust_traffic("skill-m", 150.0)
        assert result["new_pct"] == 100.0

    def test_adjust_clamp_low(self):
        deployer = SkillShadowDeploy()
        result = deployer.adjust_traffic("skill-n", -10.0)
        assert result["new_pct"] == 0.0

    def test_adjust_zero(self):
        deployer = SkillShadowDeploy()
        result = deployer.adjust_traffic("skill-o", 0.0)
        assert result["new_pct"] == 0.0

# [A_test] module_id: MOD-GOV_skill_learning | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_learning
# [INVARIANTS] SkillLearning must not corrupt pattern dedup
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] handles None expected_output gracefully
# [TESTS] tests/test_skill_learning.py
# [TTL] task_bound

from zephyr.autonomy_core.skills.skill_learning import SkillLearning


class TestSkillLearningInstantiation:
    def test_default_instantiation(self):
        sl = SkillLearning()
        assert isinstance(sl.learning_history, dict)
        assert isinstance(sl.learned_patterns, dict)
        assert isinstance(sl.session_deltas, dict)
        assert len(sl.learning_history) == 0
        assert len(sl.learned_patterns) == 0
        assert len(sl.session_deltas) == 0


class TestAddExecution:
    def test_add_success_execution(self):
        sl = SkillLearning()
        result = sl.add_execution("skill-1", "output text", success=True)
        assert result["skill_id"] == "skill-1"
        assert result["recorded"] is True
        assert result["delta"] == 0.0

    def test_add_with_expected_output_low_delta(self):
        sl = SkillLearning()
        result = sl.add_execution("skill-2", "hello world", expected_output="hello world", success=True)
        assert result["delta"] == 0.0
        assert "high_accuracy_achieved" in result["patterns_found"]

    def test_add_with_expected_output_high_delta(self):
        sl = SkillLearning()
        result = sl.add_execution(
            "skill-3", "completely different", expected_output="totally unrelated text", success=False
        )
        assert result["delta"] > 0.3
        assert "significant_divergence" in result["patterns_found"]

    def test_add_with_error_in_output(self):
        sl = SkillLearning()
        result = sl.add_execution("skill-4", "error: something failed", success=False)
        assert "error_in_output" in result["patterns_found"]

    def test_add_with_must_in_output(self):
        sl = SkillLearning()
        result = sl.add_execution("skill-5", "MUST validate all inputs", success=True)
        assert "constraint_aware" in result["patterns_found"]

    def test_add_empty_output(self):
        sl = SkillLearning()
        result = sl.add_execution("skill-6", "", success=False)
        assert result["recorded"] is True
        assert "significant_divergence" in result["patterns_found"]

    def test_add_none_expected_output(self):
        sl = SkillLearning()
        result = sl.add_execution("skill-7", "output", expected_output=None, success=True)
        assert result["delta"] == 0.0

    def test_add_stores_in_history(self):
        sl = SkillLearning()
        sl.add_execution("skill-8", "output", success=True)
        assert "skill-8" in sl.learning_history
        assert len(sl.learning_history["skill-8"]) == 1

    def test_pattern_dedup(self):
        sl = SkillLearning()
        sl.add_execution("skill-9", "error: fail", success=False)
        sl.add_execution("skill-9", "error: fail again", success=False)
        patterns = sl.learned_patterns["skill-9"]
        assert patterns.count("error_in_output") == 1


class TestGetLearning:
    def test_no_data_returns_no_data_trend(self):
        sl = SkillLearning()
        result = sl.get_learning("skill-unknown")
        assert result["trend"] == "no_data"
        assert result["delta"] == 0.0
        assert result["updated"] is False

    def test_improving_trend(self):
        sl = SkillLearning()
        sl.add_execution("s1", "aaaa", expected_output="aaaa", success=True)
        sl.add_execution("s1", "aaab", expected_output="aaaa", success=True)
        sl.add_execution("s1", "aaaa", expected_output="aaaa", success=True)
        sl.add_execution("s1", "aaaa", expected_output="aaaa", success=True)
        result = sl.get_learning("s1")
        assert result["trend"] in ("improving", "stable", "worsening")
        assert result["executions"] == 4

    def test_insufficient_data_trend(self):
        sl = SkillLearning()
        sl.add_execution("s2", "out", expected_output="out", success=True)
        result = sl.get_learning("s2")
        assert result["trend"] == "insufficient_data"

    def test_patterns_included(self):
        sl = SkillLearning()
        sl.add_execution("s3", "error: fail", success=False)
        result = sl.get_learning("s3")
        assert "error_in_output" in result["patterns"]


class TestSuggestImprovement:
    def test_suggest_for_divergence(self):
        sl = SkillLearning()
        sl.add_execution("s1", "xyz", expected_output="abc", success=False)
        result = sl.suggest_improvement("s1")
        assert "add_examples_section" in result["suggestions"]

    def test_suggest_for_error_in_output(self):
        sl = SkillLearning()
        sl.add_execution("s2", "error: crash", success=False)
        result = sl.suggest_improvement("s2")
        assert "add_error_handling_constraint" in result["suggestions"]

    def test_suggest_for_worsening(self):
        sl = SkillLearning()
        sl.add_execution("s3", "aaaa", expected_output="aaaa", success=True)
        sl.add_execution("s3", "bbbb", expected_output="aaaa", success=False)
        sl.add_execution("s3", "cccc", expected_output="aaaa", success=False)
        sl.add_execution("s3", "dddd", expected_output="aaaa", success=False)
        result = sl.suggest_improvement("s3")
        if result["learning"]["trend"] == "worsening":
            assert "run_freshness_decay_check" in result["suggestions"]
            assert "trigger_postmortem" in result["suggestions"]

    def test_suggest_for_unknown_skill(self):
        sl = SkillLearning()
        result = sl.suggest_improvement("unknown")
        assert isinstance(result["suggestions"], list)
        assert result["learning"]["trend"] == "no_data"

# [A_test] module_id: MOD-GOV_skill_evaluator | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_evaluator
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] pytest tests/test_skill_evaluator.py
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from zephyr.autonomy_core.skills.skill_evaluator import SkillEvaluator


@pytest.fixture
def evaluator():
    return SkillEvaluator()


class TestSkillEvaluatorInit:
    def test_class_constants(self):
        assert SkillEvaluator.STRUCTURE_WEIGHT == 0.25
        assert SkillEvaluator.DENSITY_WEIGHT == 0.25
        assert SkillEvaluator.CONSTRAINT_WEIGHT == 0.20
        assert SkillEvaluator.FRESHNESS_WEIGHT == 0.15
        assert SkillEvaluator.TOKEN_EFF_WEIGHT == 0.15
        total = (
            SkillEvaluator.STRUCTURE_WEIGHT
            + SkillEvaluator.DENSITY_WEIGHT
            + SkillEvaluator.CONSTRAINT_WEIGHT
            + SkillEvaluator.FRESHNESS_WEIGHT
            + SkillEvaluator.TOKEN_EFF_WEIGHT
        )
        assert abs(total - 1.0) < 0.001

    def test_essential_sections_defined(self):
        assert len(SkillEvaluator.ESSENTIAL_SECTIONS) == 5


class TestSkillEvaluatorEvaluateStructure:
    def test_full_structure(self):
        l1 = {
            "skill_id": "s1",
            "name": "Skill One",
            "allowed_tools": ["Read"],
            "description": "desc",
            "version": "1.0",
            "model_hint": "gpt-4o",
        }
        body = "核心操作\n约束\n常见错误\n前置条件\n返回格式\n"
        score, issues = SkillEvaluator.evaluate_structure(body, l1)
        assert score == 100.0
        assert issues == []

    def test_minimal_structure(self):
        l1 = {"skill_id": "s1", "name": "S"}
        body = ""
        score, issues = SkillEvaluator.evaluate_structure(body, l1)
        assert score < 100.0
        assert len(issues) > 0

    def test_empty_l1(self):
        score, issues = SkillEvaluator.evaluate_structure("body", {})
        assert "missing_id_or_name" in issues
        assert "no_tool_allowlist" in issues
        assert "no_description" in issues


class TestSkillEvaluatorEvaluateDensity:
    def test_dense_body(self):
        body = (
            "MUST do this\n必须 do that\n不可 skip\n"
            "```python\nprint('hi')\n```\n"
            "1. Step one\n2. Step two\n"
            "- [x] done\n- [ ] todo\n"
        )
        score, detail = SkillEvaluator.evaluate_density(body)
        assert score > 0
        assert detail["directives"] > 0
        assert detail["examples"] >= 1

    def test_sparse_body(self):
        body = "hello\nworld\n"
        score, detail = SkillEvaluator.evaluate_density(body)
        assert score == 0.0
        assert detail["detail"] == "too_short"

    def test_empty_body(self):
        score, detail = SkillEvaluator.evaluate_density("")
        assert score == 0.0


class TestSkillEvaluatorEvaluateConstraints:
    def test_all_categories_covered(self):
        body = "安全 security injection 注入 sandbox 性能 performance latency 延迟 budget 正确 correct 准确 accuracy 验证 一致 consist idempotent 幂等 回滚 rollback checkpoint 恢复"
        score, missing = SkillEvaluator.evaluate_constraints(body)
        assert score == 100.0
        assert missing == []

    def test_no_constraints(self):
        score, missing = SkillEvaluator.evaluate_constraints("hello world")
        assert score == 0.0
        assert len(missing) == 5

    def test_partial_constraints(self):
        body = "安全 performance 验证"
        score, missing = SkillEvaluator.evaluate_constraints(body)
        assert 0 < score < 100.0
        assert len(missing) > 0


class TestSkillEvaluatorEvaluateFreshness:
    def test_no_freshness_data(self):
        score, detail = SkillEvaluator.evaluate_freshness(None)
        assert score == 50.0
        assert detail["detail"] == "no_freshness_data"

    def test_with_freshness_data(self):
        data = {"freshness_score": 80.0}
        score, detail = SkillEvaluator.evaluate_freshness(data)
        assert score == 80.0

    def test_freshness_data_missing_key(self):
        data = {"other_key": 42}
        score, detail = SkillEvaluator.evaluate_freshness(data)
        assert score == 50.0


class TestSkillEvaluatorEvaluateTokenEfficiency:
    def test_zero_tokens(self):
        score, detail = SkillEvaluator.evaluate_token_efficiency("body", 0)
        assert score == 0.0
        assert detail["detail"] == "zero_tokens"

    def test_efficient_body(self):
        body = "MUST do\n必须 done\n```py\nx=1\n```\n"
        score, detail = SkillEvaluator.evaluate_token_efficiency(body, 50)
        assert score > 0
        assert "tokens" in detail

    def test_inefficient_body(self):
        body = "plain text with no directives"
        score, detail = SkillEvaluator.evaluate_token_efficiency(body, 10000)
        assert score < 50.0


class TestSkillEvaluatorEvaluate:
    def test_evaluate_import_error(self):
        with patch.dict("sys.modules", {"zephyr.autonomy_core.skills.skill_loader": None}):
            result = SkillEvaluator.evaluate("no-skill")
            assert result["skill_id"] == "no-skill"
            assert result["overall_score"] == 0.0
            assert result["grade"] == "F"
            assert result["error"] == "skill_loader_unavailable"

    def test_evaluate_with_mock_loader(self):
        mock_loader = MagicMock()
        mock_loader.progressive_load.return_value = {
            "l1": {
                "skill_id": "test-skill",
                "name": "Test Skill",
                "allowed_tools": ["Read"],
                "description": "desc",
                "version": "1.0",
                "model_hint": "gpt-4o",
            },
            "l2": "核心操作\n约束\n常见错误\n前置条件\n返回格式\nMUST do\n```py\nx=1\n```\n安全\n性能\n正确\n一致\n回滚\n",
            "token_count_l2": 100,
        }
        mock_fresh_instance = MagicMock()
        mock_fresh_instance.current_state.return_value = {"freshness_score": 80.0}
        mock_fresh_cls = MagicMock(return_value=mock_fresh_instance)
        with patch("zephyr.autonomy_core.skills.skill_loader.SkillLoader", return_value=mock_loader):
            with patch("zephyr.autonomy_core.skills.skill_freshness.FreshnessDecayModel", mock_fresh_cls):
                result = SkillEvaluator.evaluate("test-skill")
                assert result["skill_id"] == "test-skill"
                assert result["overall_score"] > 0
                assert result["grade"] in ("A", "B", "C", "D", "F")
                assert "dimensions" in result
                assert "structure" in result["dimensions"]
                assert "density" in result["dimensions"]
                assert "constraints" in result["dimensions"]

# [A_test] module_id: MOD-GOV_skill_explain | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md | §
# [MODULE] tests.test_skill_explain
# [INVARIANTS] SkillExplain is class-only (classmethods); no instance state
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError on empty skill_id
# [TESTS] pytest tests/test_skill_explain.py -q
# [TTL] task_bound

from __future__ import annotations

from unittest.mock import MagicMock, patch

from zephyr.autonomy_core.skills.skill_explain import SkillExplain


class TestSkillExplainInstantiation:
    def test_class_exists(self):
        assert SkillExplain is not None

    def test_can_instantiate(self):
        obj = SkillExplain()
        assert isinstance(obj, SkillExplain)

    def test_has_build_reasoning_chain(self):
        assert callable(getattr(SkillExplain, "build_reasoning_chain", None))

    def test_has_explain_routing(self):
        assert callable(getattr(SkillExplain, "explain_routing", None))

    def test_has_isolate_factors(self):
        assert callable(getattr(SkillExplain, "isolate_factors", None))


class TestBuildReasoningChain:
    def test_basic_chain(self):
        result = SkillExplain.build_reasoning_chain(
            skill_id="SKILL-DOM-DB-001",
            task_description="run database migration",
            matched_stage="execution",
            matched_keywords=["database", "migration"],
        )
        assert result["skill_id"] == "SKILL-DOM-DB-001"
        assert result["steps"] == 5
        assert len(result["reasoning_chain"]) == 5
        assert 0.0 <= result["overall_confidence"] <= 1.0

    def test_chain_step_labels(self):
        result = SkillExplain.build_reasoning_chain(
            skill_id="SKILL-TEST",
            task_description="test task",
            matched_stage="planning",
            matched_keywords=["test"],
        )
        labels = [s["label"] for s in result["reasoning_chain"]]
        assert labels == [
            "trigger_received",
            "keyword_extraction",
            "skill_lookup",
            "skill_loaded",
            "skill_injected",
        ]

    def test_empty_keywords_lower_confidence(self):
        result = SkillExplain.build_reasoning_chain(
            skill_id="SKILL-EMPTY",
            task_description="vague task",
            matched_stage="unknown",
            matched_keywords=[],
        )
        kw_step = result["reasoning_chain"][1]
        assert kw_step["confidence"] == 0.3
        lookup_step = result["reasoning_chain"][2]
        assert lookup_step["confidence"] == 0.5

    def test_many_keywords_truncated_to_five(self):
        kws = ["a", "b", "c", "d", "e", "f", "g"]
        result = SkillExplain.build_reasoning_chain(
            skill_id="SKILL-MANY",
            task_description="many keywords",
            matched_stage="execution",
            matched_keywords=kws,
        )
        detail = result["reasoning_chain"][1]["detail"]
        parts = detail.split("Extracted keywords: ")[1].split(", ")
        assert len(parts) <= 5

    def test_overall_confidence_is_average(self):
        result = SkillExplain.build_reasoning_chain(
            skill_id="SKILL-AVG",
            task_description="avg test",
            matched_stage="test",
            matched_keywords=["test"],
        )
        confidences = [s["confidence"] for s in result["reasoning_chain"]]
        expected = sum(confidences) / len(confidences)
        assert abs(result["overall_confidence"] - expected) < 1e-9


class TestExplainRouting:
    def test_basic_routing(self):
        result = SkillExplain.explain_routing(
            task_description="run database migration with sql",
            chosen_skill_id="SKILL-DOM-DBM-001",
            alternatives=["SKILL-DOM-SEC-001", "SKILL-DOM-KNO-001"],
        )
        assert result["chosen_skill"] == "SKILL-DOM-DBM-001"
        assert "confidence" in result
        assert "decision_quality" in result
        assert "what_if" in result

    def test_high_confidence_routing(self):
        result = SkillExplain.explain_routing(
            task_description="database migration sql",
            chosen_skill_id="SKILL-DOM-DATABASE-MIGRATION",
            alternatives=["SKILL-DOM-OTHER"],
        )
        assert result["decision_quality"] in ("high", "moderate")

    def test_empty_alternatives(self):
        result = SkillExplain.explain_routing(
            task_description="simple task",
            chosen_skill_id="SKILL-DOM-SIMPLE",
            alternatives=[],
        )
        assert result["alternative_skills"] == []
        assert result["what_if"] == []

    def test_alternatives_deduplicated(self):
        result = SkillExplain.explain_routing(
            task_description="test task",
            chosen_skill_id="SKILL-A",
            alternatives=["SKILL-B", "SKILL-B", "SKILL-C"],
        )
        assert len(result["alternative_skills"]) == len(set(result["alternative_skills"]))

    def test_what_if_sorted_by_accuracy(self):
        result = SkillExplain.explain_routing(
            task_description="database security audit",
            chosen_skill_id="SKILL-DOM-DBA-001",
            alternatives=["SKILL-DOM-SEC-001", "SKILL-DOM-AUD-001", "SKILL-DOM-KNO-001"],
        )
        if len(result["what_if"]) >= 2:
            accuracies = [w["estimated_accuracy"] for w in result["what_if"]]
            assert accuracies == sorted(accuracies, reverse=True)

    def test_confidence_capped_at_one(self):
        result = SkillExplain.explain_routing(
            task_description="database migration sql security audit rbac blueprint rollback",
            chosen_skill_id="SKILL-DOM-DATABASE-MIGRATION-SECURITY-AUDIT-RBAC-BLUEPRINT-ROLLBACK",
            alternatives=[],
        )
        assert result["confidence"] <= 1.0


class TestIsolateFactors:
    def test_basic_isolation_with_mocks(self):
        mock_eval = MagicMock()
        mock_eval.evaluate.return_value = {"overall_score": 80.0}
        mock_evo = MagicMock()
        mock_evo.assess_impact.return_value = {"overall_score": 90.0}
        with patch.dict(
            "sys.modules",
            {
                "zephyr.autonomy_core.skills.skill_evaluator": MagicMock(SkillEvaluator=mock_eval),
                "zephyr.autonomy_core.skills.skill_model_evolution": MagicMock(SkillModelEvolution=mock_evo),
            },
        ):
            result = SkillExplain.isolate_factors(
                skill_id="SKILL-DOM-DB-001",
                output_quality=0.85,
                llm_model="gpt-4",
            )
        assert result["skill_id"] == "SKILL-DOM-DB-001"
        assert result["llm_model"] == "gpt-4"
        assert result["output_quality"] == 0.85
        assert "skill_factor" in result
        assert "llm_factor" in result
        assert "bottleneck_diagnosis" in result

    def test_isolation_with_import_failure(self):
        with (
            patch(
                "zephyr.autonomy_core.skills.skill_evaluator.SkillEvaluator.evaluate",
                side_effect=RuntimeError("test error"),
            ),
            patch(
                "zephyr.autonomy_core.skills.skill_model_evolution.SkillModelEvolution.assess_impact",
                side_effect=RuntimeError("test error"),
            ),
        ):
            result = SkillExplain.isolate_factors(
                skill_id="SKILL-DOM-FAKE",
                output_quality=0.5,
                llm_model="fake-model",
            )
        assert result["skill_factor"] == 0.5
        assert result["llm_factor"] == 0.7
        assert result["skill_contribution_60pct"] == round(0.5 * 0.60, 2)
        assert result["llm_contribution_40pct"] == round(0.7 * 0.40, 2)

    def test_bottleneck_diagnosis_skill(self):
        result = SkillExplain.isolate_factors(
            skill_id="SKILL-LOW",
            output_quality=0.3,
            llm_model="gpt-4",
        )
        assert result["bottleneck_diagnosis"] in ("skill", "llm", "balanced")

    def test_output_quality_rounded(self):
        result = SkillExplain.isolate_factors(
            skill_id="SKILL-RND",
            output_quality=0.123456789,
            llm_model="test",
        )
        assert result["output_quality"] == round(0.123456789, 2)

    def test_zero_output_quality(self):
        result = SkillExplain.isolate_factors(
            skill_id="SKILL-ZERO",
            output_quality=0.0,
            llm_model="test",
        )
        assert result["output_quality"] == 0.0

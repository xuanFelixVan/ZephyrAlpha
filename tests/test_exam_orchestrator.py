# [A_test] module_id: SRC-TST-0875 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model-profiler/blueprint.md | §3
# [MODULE] tests.test_exam_orchestrator
# [INVARIANTS] test_exam_orchestrator完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self

from __future__ import annotations

from dataclasses import dataclass, field
from unittest.mock import MagicMock

import pytest

from zephyr.intelligence.model_profiling.capability_passport import (
    BreadthResult,
    CapabilityPassport,
    DepthCapabilityResult,
    DepthResult,
    HallucinationResult,
    Recommendations,
    SpeedResult,
)
from zephyr.intelligence.model_profiling.exam_orchestrator import (
    ExamOrchestrator,
    _normalized_edit_distance,
    _percentile,
)
from zephyr.intelligence.model_profiling.exam_test_cases import Difficulty, ExamTestCase


class TestNormalizedEditDistance:
    def test_identical_strings(self):
        assert _normalized_edit_distance("hello", "hello") == 0.0

    def test_empty_strings(self):
        assert _normalized_edit_distance("", "") == 0.0

    def test_one_empty(self):
        assert _normalized_edit_distance("abc", "") == 1.0
        assert _normalized_edit_distance("", "abc") == 1.0

    def test_completely_different(self):
        result = _normalized_edit_distance("abc", "xyz")
        assert result == 1.0

    def test_partial_overlap(self):
        result = _normalized_edit_distance("kitten", "sitting")
        assert 0.0 < result < 1.0

    def test_single_char_difference(self):
        result = _normalized_edit_distance("abc", "abd")
        assert 0.0 < result <= 1.0 / 3.0 + 1e-9


class TestPercentile:
    def test_empty_list(self):
        assert _percentile([], 50) == 0.0

    def test_single_element(self):
        assert _percentile([10.0], 50) == 10.0
        assert _percentile([10.0], 0) == 10.0
        assert _percentile([10.0], 100) == 10.0

    def test_multiple_elements_p50(self):
        data = [1.0, 2.0, 3.0, 4.0, 5.0]
        result = _percentile(data, 50)
        assert result == 3.0

    def test_multiple_elements_p95(self):
        data = list(range(1, 101))
        result = _percentile(data, 95)
        assert 94.0 <= result <= 96.0

    def test_multiple_elements_p99(self):
        data = list(range(1, 101))
        result = _percentile(data, 99)
        assert 98.0 <= result <= 100.0


class TestCheckStructure:
    def test_valid_dict(self):
        result = {"category": "web", "tags": ["api"]}
        assert ExamOrchestrator._check_structure(result, ["category", "tags"]) is True

    def test_empty_dict(self):
        assert ExamOrchestrator._check_structure({}, ["category"]) is False

    def test_none(self):
        assert ExamOrchestrator._check_structure(None, ["category"]) is False

    def test_missing_keys(self):
        result = {"category": "web"}
        assert ExamOrchestrator._check_structure(result, ["category", "missing_key"]) is False

    def test_empty_list_value(self):
        result = {"category": "web", "tags": []}
        assert ExamOrchestrator._check_structure(result, ["tags"]) is False

    def test_empty_string_value(self):
        result = {"category": "   "}
        assert ExamOrchestrator._check_structure(result, ["category"]) is False

    def test_nested_result_key(self):
        result = {"result": {"category": "web"}}
        assert ExamOrchestrator._check_structure(result, ["category"]) is True

    def test_nested_codegen_key(self):
        result = {"codegen": {"content": "def foo(): pass"}}
        assert ExamOrchestrator._check_structure(result, ["content"]) is True


class TestCheckFabrication:
    def _make_case(self, capability: str, prompt: str) -> ExamTestCase:
        return ExamTestCase(
            case_id="TEST-001",
            capability=capability,
            difficulty=Difficulty.EASY,
            prompt=prompt,
        )

    def test_code_fix_old_str_in_prompt(self):
        case = self._make_case("code_fix", "fix this: old_code_here and more")
        result = {"fixes": [{"old_str": "old_code_here", "new_str": "fixed"}]}
        assert ExamOrchestrator._check_fabrication(case, result) is False

    def test_code_fix_old_str_not_in_prompt(self):
        case = self._make_case("code_fix", "fix this: some_other_code")
        result = {"fixes": [{"old_str": "fabricated_code", "new_str": "fixed"}]}
        assert ExamOrchestrator._check_fabrication(case, result) is True

    def test_non_code_capability(self):
        case = self._make_case("task_classification", "classify this")
        result = {"category": "web"}
        assert ExamOrchestrator._check_fabrication(case, result) is False

    def test_refactor_old_str_in_prompt(self):
        case = self._make_case("refactor", "refactor: original_snippet here")
        result = {"changes": [{"old_str": "original_snippet", "new_str": "refactored"}]}
        assert ExamOrchestrator._check_fabrication(case, result) is False

    def test_dead_code_removal_old_str_not_in_prompt(self):
        case = self._make_case("dead_code_removal", "remove dead code from: live_code")
        result = {"dead_sections": [{"old_str": "ghost_code", "new_str": ""}]}
        assert ExamOrchestrator._check_fabrication(case, result) is True


class TestOutputsSimilar:
    def test_identical_dicts(self):
        a = {"key": "value", "num": 42}
        b = {"key": "value", "num": 42}
        assert ExamOrchestrator._outputs_similar(a, b) is True

    def test_completely_different_dicts(self):
        a = {"alpha": "one two three"}
        b = {"beta": "four five six"}
        assert ExamOrchestrator._outputs_similar(a, b) is False

    def test_partially_similar_dicts(self):
        a = {"key": "hello world foo"}
        b = {"key": "hello world bar"}
        assert ExamOrchestrator._outputs_similar(a, b) is True


class TestCheckRefusal:
    def test_empty_dict(self):
        assert ExamOrchestrator._check_refusal({}) is True

    def test_error_with_refusal_keywords(self):
        assert ExamOrchestrator._check_refusal({"error": "I cannot do that"}) is True
        assert ExamOrchestrator._check_refusal({"error": "I'm sorry but I refuse"}) is True
        assert ExamOrchestrator._check_refusal({"error": "unable to comply"}) is True
        assert ExamOrchestrator._check_refusal({"error": "I can't process this"}) is True
        assert ExamOrchestrator._check_refusal({"error": "not able to help"}) is True

    def test_normal_result(self):
        assert ExamOrchestrator._check_refusal({"category": "web"}) is False

    def test_error_without_refusal_keyword(self):
        assert ExamOrchestrator._check_refusal({"error": "timeout"}) is False


class TestExamOrchestratorInit:
    def test_instantiation_with_mock(self):
        chat = MagicMock()
        orch = ExamOrchestrator(chat, model_id="test-model")
        assert orch._model_id == "test-model"
        assert orch._chat is chat

    def test_instantiation_model_id_from_chat(self):
        chat = MagicMock()
        chat._model = "inferred-model"
        orch = ExamOrchestrator(chat)
        assert orch._model_id == "inferred-model"


class TestComputeOverall:
    def test_compute_overall(self):
        chat = MagicMock()
        orch = ExamOrchestrator(chat, model_id="test")
        passport = CapabilityPassport(
            model_id="test",
            breadth=BreadthResult(score=0.8, passed=7, total=9, failed_capabilities=["a", "b"]),
            depth=DepthResult(overall_score=0.6, capabilities={}),
            hallucination=HallucinationResult(overall_rate=0.1, fabrication_rate=0.05, inconsistency_rate=0.03, refusal_rate=0.02),
        )
        expected = round(0.30 * 0.8 + 0.50 * 0.6 + 0.20 * (1.0 - 0.1), 3)
        result = orch._compute_overall(passport)
        assert result == expected

    def test_compute_overall_perfect(self):
        chat = MagicMock()
        orch = ExamOrchestrator(chat, model_id="test")
        passport = CapabilityPassport(
            model_id="test",
            breadth=BreadthResult(score=1.0, passed=9, total=9, failed_capabilities=[]),
            depth=DepthResult(overall_score=1.0, capabilities={}),
            hallucination=HallucinationResult(overall_rate=0.0, fabrication_rate=0.0, inconsistency_rate=0.0, refusal_rate=0.0),
        )
        result = orch._compute_overall(passport)
        assert result == round(0.30 * 1.0 + 0.50 * 1.0 + 0.20 * 1.0, 3)


class TestBuildRecommendations:
    def test_mixed_safe_unsafe(self):
        chat = MagicMock()
        orch = ExamOrchestrator(chat, model_id="test")
        passport = CapabilityPassport(
            model_id="test",
            depth=DepthResult(
                overall_score=0.5,
                capabilities={
                    "task_classification": DepthCapabilityResult(pass_=True, f1=0.7),
                    "tag_completion": DepthCapabilityResult(pass_=True, f1=0.65),
                    "code_fix": DepthCapabilityResult(pass_=False, f1=0.3, failure_reason="low_precision_below_threshold"),
                    "refactor": DepthCapabilityResult(pass_=False, f1=0.4, failure_reason="low_precision_below_threshold"),
                    "summary_extraction": DepthCapabilityResult(pass_=True, f1=0.6),
                },
            ),
        )
        recs = orch._build_recommendations(passport)
        assert "task_classification" in recs.safe_capabilities
        assert "tag_completion" in recs.safe_capabilities
        assert "summary_extraction" in recs.safe_capabilities
        assert "code_fix" in recs.unsafe_capabilities
        assert "refactor" in recs.unsafe_capabilities
        assert recs.max_concurrent_tasks == 3
        assert "code_fix" in recs.note
        assert "refactor" in recs.note

    def test_all_safe(self):
        chat = MagicMock()
        orch = ExamOrchestrator(chat, model_id="test")
        passport = CapabilityPassport(
            model_id="test",
            depth=DepthResult(
                overall_score=0.8,
                capabilities={
                    "task_classification": DepthCapabilityResult(pass_=True, f1=0.8),
                    "tag_completion": DepthCapabilityResult(pass_=True, f1=0.7),
                },
            ),
        )
        recs = orch._build_recommendations(passport)
        assert len(recs.safe_capabilities) == 2
        assert len(recs.unsafe_capabilities) == 0
        assert recs.note == ""

    def test_max_concurrent_tasks_capped_at_4(self):
        chat = MagicMock()
        orch = ExamOrchestrator(chat, model_id="test")
        caps = {f"cap_{i}": DepthCapabilityResult(pass_=True, f1=0.8) for i in range(9)}
        passport = CapabilityPassport(
            model_id="test",
            depth=DepthResult(overall_score=0.8, capabilities=caps),
        )
        recs = orch._build_recommendations(passport)
        assert recs.max_concurrent_tasks == 4

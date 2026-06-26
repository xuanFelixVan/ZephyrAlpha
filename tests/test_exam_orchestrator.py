# [A_test] module_id: SRC-TST-0875 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §3
# [MODULE] tests.test_exam_orchestrator
# [INVARIANTS] test_exam_orchestrator完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import pytest
from unittest.mock import MagicMock

# v3.0.5: import 统一到 #3 生产源（zephyr.intelligence.model_profiling）
from zephyr.intelligence.model_profiling.capability_passport import (
    BreadthResult,
    CapabilityPassport,
    DepthCapabilityResult,
    DepthResult,
    HallucinationResult,
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


class TestDepthMultiSampling:
    """P1-2: depth 每题多次采样, 提升统计显著性。"""

    def test_default_samples_per_case_is_1(self):
        """默认 n=1, 保持向后兼容。"""
        orch = ExamOrchestrator(MagicMock(), model_id="t")
        assert orch._depth_samples_per_case == 1

    def test_explicit_samples_per_case(self):
        """显式参数优先于环境变量。"""
        orch = ExamOrchestrator(MagicMock(), model_id="t", depth_samples_per_case=5)
        assert orch._depth_samples_per_case == 5

    def test_env_var_samples_per_case(self, monkeypatch):
        """环境变量 ZEPHYR_DEPTH_SAMPLES 在未显式传参时生效。"""
        monkeypatch.setenv("ZEPHYR_DEPTH_SAMPLES", "3")
        orch = ExamOrchestrator(MagicMock(), model_id="t")
        assert orch._depth_samples_per_case == 3

    def test_invalid_env_var_falls_back_to_1(self, monkeypatch):
        """非法环境变量值会抛 ValueError — 用户应提供合法值。"""
        monkeypatch.setenv("ZEPHYR_DEPTH_SAMPLES", "not_a_number")
        with pytest.raises(ValueError):
            # int("not_a_number") 会抛 ValueError — 这是预期行为
            ExamOrchestrator(MagicMock(), model_id="t")

    def test_negative_samples_clamped_to_1(self):
        """负数被 max(1, ...) 钳制为 1。"""
        orch = ExamOrchestrator(MagicMock(), model_id="t", depth_samples_per_case=-5)
        assert orch._depth_samples_per_case == 1

    def test_score_capability_calls_infer_n_times(self):
        """n=3 时, 每个 case 的 _infer 应被调用 3 次。"""
        chat = MagicMock()
        chat.inference.return_value = {"category": "test", "token_count": 10}
        orch = ExamOrchestrator(chat, model_id="t", depth_samples_per_case=3)
        # 1 个 EASY case, 非 OLYMPIAD
        case = ExamTestCase(
            case_id="T-001",
            capability="task_classification",
            difficulty=Difficulty.EASY,
            prompt="test prompt",
            expected_structure_keys=["category"],
            expected_category="test",
        )
        result = orch._score_capability("task_classification", [case])
        # _infer 调用次数 = n_samples × n_cases = 3 × 1 = 3
        assert chat.inference.call_count == 3
        assert result.samples_per_case == 3
        assert result.samples_tested == 1  # 仍然只有一个 case

    def test_score_capability_n1_backward_compat(self):
        """n=1 时行为与原单次采样一致。"""
        chat = MagicMock()
        chat.inference.return_value = {"category": "test", "token_count": 10}
        orch = ExamOrchestrator(chat, model_id="t", depth_samples_per_case=1)
        case = ExamTestCase(
            case_id="T-002",
            capability="task_classification",
            difficulty=Difficulty.EASY,
            prompt="test",
            expected_structure_keys=["category"],
            expected_category="test",
        )
        result = orch._score_capability("task_classification", [case])
        assert chat.inference.call_count == 1
        assert result.samples_per_case == 1

    def test_majority_vote_exact_match(self):
        """n=3 时, 2/3 采样 exact → exact_match_rate=1 (多数投票 ≥50%)。"""
        chat = MagicMock()
        # 3 次调用: 2 次正确, 1 次错误
        chat.inference.side_effect = [
            {"category": "test", "token_count": 10},  # 正确
            {"category": "wrong", "token_count": 10},  # 错误
            {"category": "test", "token_count": 10},  # 正确
        ]
        orch = ExamOrchestrator(chat, model_id="t", depth_samples_per_case=3)
        case = ExamTestCase(
            case_id="T-003",
            capability="task_classification",
            difficulty=Difficulty.EASY,
            prompt="test",
            expected_structure_keys=["category"],
            expected_category="test",
        )
        result = orch._score_capability("task_classification", [case])
        # 多数投票: 2/3 exact → em=1 → exact_match_rate=1.0
        assert result.exact_match_rate == 1.0

    def test_olympiad_appends_once_per_case(self):
        """OLYMPIAD 题: n=3 时 _olympiad_case_results 仅 append 1 次 (不按采样次数膨胀)。"""
        chat = MagicMock()
        chat.inference.return_value = {"code": "print(1)", "token_count": 10}
        orch = ExamOrchestrator(chat, model_id="t", depth_samples_per_case=3)
        # 用一个 OLYMPIAD case (需要 expected_test_cases 才能走 executor 轨)
        case = ExamTestCase(
            case_id="EX-OLY-T1",
            capability="code_generate",
            difficulty=Difficulty.OLYMPIAD,
            prompt="write a function",
            expected_test_cases=["assert True"],
        )
        orch._score_capability("code_generate", [case])
        # 仅 append 1 次 (而不是 3 次)
        assert len(orch._olympiad_case_results) == 1


class TestDeterministicJudge:
    """P1-4: 确定性裁判 — 无 LLM judge_chat 时的 fallback。"""

    def _make_judge(self):
        from zephyr.intelligence.model_profiling.exam_judge import DeterministicJudge
        return DeterministicJudge()

    def test_keyword_coverage_full(self):
        """所有关键词命中 → correctness=1.0。"""
        judge = self._make_judge()
        case = ExamTestCase(
            case_id="T",
            capability="architecture_design",
            difficulty=Difficulty.OLYMPIAD,
            prompt="test",
            expected_contains=["microservice", "API", "database"],
        )
        result = judge.judge(case, "We use microservice with API and database patterns")
        assert result.correctness == 1.0

    def test_keyword_coverage_partial(self):
        """部分关键词命中 → correctness=命中比例。"""
        judge = self._make_judge()
        case = ExamTestCase(
            case_id="T",
            capability="architecture_design",
            difficulty=Difficulty.OLYMPIAD,
            prompt="test",
            expected_contains=["microservice", "API", "database"],
        )
        result = judge.judge(case, "We use microservice with API")
        assert result.correctness == pytest.approx(2 / 3, abs=0.01)

    def test_keyword_coverage_zero(self):
        """无关键词命中 → correctness=0.0。"""
        judge = self._make_judge()
        case = ExamTestCase(
            case_id="T",
            capability="architecture_design",
            difficulty=Difficulty.OLYMPIAD,
            prompt="test",
            expected_contains=["microservice", "API"],
        )
        result = judge.judge(case, "completely unrelated content with sufficient length " * 5)
        assert result.correctness == 0.0

    def test_length_too_short(self):
        """太短 (<50字) → depth < 0.5。"""
        judge = self._make_judge()
        case = ExamTestCase(
            case_id="T", capability="x", difficulty=Difficulty.OLYMPIAD, prompt="t",
        )
        result = judge.judge(case, "short answer")
        assert result.depth < 0.5

    def test_length_reasonable(self):
        """合理长度 (50~10000字) → depth=1.0。"""
        judge = self._make_judge()
        case = ExamTestCase(
            case_id="T", capability="x", difficulty=Difficulty.OLYMPIAD, prompt="t",
        )
        result = judge.judge(case, "x" * 100)
        assert result.depth == 1.0

    def test_no_requirements_neutral_score(self):
        """无关键词/结构要求 → correctness/completeness=0.5 (中性分)。"""
        judge = self._make_judge()
        case = ExamTestCase(
            case_id="T", capability="x", difficulty=Difficulty.OLYMPIAD, prompt="t",
        )
        result = judge.judge(case, "x" * 100)
        assert result.correctness == 0.5
        assert result.completeness == 0.5

    def test_overall_in_range(self):
        """overall 始终在 [0, 1] 区间。"""
        judge = self._make_judge()
        case = ExamTestCase(
            case_id="T",
            capability="x",
            difficulty=Difficulty.OLYMPIAD,
            prompt="t",
            expected_contains=["a", "b", "c"],
        )
        for text in ["", "a", "abc", "x" * 20000, "a b c " * 20]:
            result = judge.judge(case, text)
            assert 0.0 <= result.overall <= 1.0
            assert "deterministic:" in result.reasoning


class TestOlympiadThreeTrackEnforcement:
    """P1-4: 三轨强制 — judge_chat=None 时仍走三轨评分。"""

    def test_judge_track_always_present(self):
        """judge_chat=None 时, judge 轨用 DeterministicJudge, 不再缺失。"""
        chat = MagicMock()
        # 提供足够长的候选文本避免 length=0
        chat.inference.return_value = {"content": "x" * 200, "token_count": 10}
        orch = ExamOrchestrator(chat, model_id="t")  # 无 judge_chat
        assert orch._judge is None
        assert orch._det_judge is not None

        case = ExamTestCase(
            case_id="EX-OLY-TJ",
            capability="architecture_design",
            difficulty=Difficulty.OLYMPIAD,
            prompt="design a system",
            expected_contains=["microservice"],
        )
        # 直接调用 _score_olympiad_case
        score = orch._score_olympiad_case(case, {"content": "microservice " * 20})
        # 三轨: rubric(0.3) + judge(0.4) = 0.7 总权重 (无 executor 轨)
        # score 应该 > 0 (不是 0, 因为 judge 轨有分)
        assert score > 0.0

    def test_judge_chat_uses_llm_judge(self):
        """judge_chat 可用时, 优先用 LLM judge (内部调用 chat.ask)。"""
        # judge_chat 需返回可解析的 JSON 字符串, 否则 _parse_judge_json 会失败
        llm_judge_chat = MagicMock()
        llm_judge_chat.ask.return_value = (
            '{"correctness": 0.9, "completeness": 0.9, "depth": 0.9, '
            '"hallucination_detected": false, "overall": 0.95, "reasoning": "test"}'
        )
        chat = MagicMock()
        chat.inference.return_value = {"content": "x" * 200, "token_count": 10}
        orch = ExamOrchestrator(chat, model_id="t", judge_chat=llm_judge_chat)
        assert orch._judge is not None

        case = ExamTestCase(
            case_id="EX-OLY-TJ2",
            capability="architecture_design",
            difficulty=Difficulty.OLYMPIAD,
            prompt="design",
        )
        orch._score_olympiad_case(case, {"content": "x" * 200})
        # ExamJudge.judge() 内部调用 chat.ask() — 验证 LLM judge 路径被触发
        llm_judge_chat.ask.assert_called_once()

    def test_static_assertions_track(self):
        """非 code_generate OLY 题 + expected_static_assertions → 走静态断言轨。"""
        chat = MagicMock()
        chat.inference.return_value = {"content": "x" * 200, "token_count": 10}
        orch = ExamOrchestrator(chat, model_id="t")

        case = ExamTestCase(
            case_id="EX-OLY-SA",
            capability="architecture_design",  # 非 code_generate
            difficulty=Difficulty.OLYMPIAD,
            prompt="design microservice",
            expected_static_assertions=["microservice", "API gateway"],
        )
        # 候选答案包含 2/2 断言 → pass_rate=1.0
        score = orch._score_olympiad_case(
            case,
            {"content": "We should use microservice with API gateway pattern " * 5},
        )
        # 三轨全在: rubric(0.3) + static(0.3) + judge(0.4) = 1.0 总权重
        # static 轨 pass_rate=1.0, 应对 score 有正贡献
        assert score > 0.0

    def test_static_assertions_partial_match(self):
        """静态断言部分命中 → pass_rate=命中比例。"""
        chat = MagicMock()
        chat.inference.return_value = {"content": "x" * 200, "token_count": 10}
        orch = ExamOrchestrator(chat, model_id="t")

        case = ExamTestCase(
            case_id="EX-OLY-SA2",
            capability="architecture_design",
            difficulty=Difficulty.OLYMPIAD,
            prompt="design",
            expected_static_assertions=["microservice", "API gateway", "database"],
        )
        # 仅命中 1/3
        rate = ExamOrchestrator._check_static_assertions(
            "We use microservice pattern " * 5,
            case.expected_static_assertions,
        )
        assert rate == pytest.approx(1 / 3, abs=0.01)

    def test_static_assertions_empty(self):
        """空断言列表 → pass_rate=0.0。"""
        rate = ExamOrchestrator._check_static_assertions("any text", [])
        assert rate == 0.0

    def test_expected_static_assertions_default_empty(self):
        """新字段默认为空列表, 向后兼容。"""
        case = ExamTestCase(
            case_id="X", capability="c", difficulty=Difficulty.EASY, prompt="p",
        )
        assert case.expected_static_assertions == []


class TestComputeOverall:
    """v3.0.5: 综合分 = 0.35*breadth + 0.50*depth + 0.15*(1-halluc)，经奥赛封顶 min(raw, cap)。

    无奥赛题时 pass_rate=1.0 → cap=1.0 → 不封顶（取 raw）。
    """

    def _make_perfect_passport(self) -> CapabilityPassport:
        return CapabilityPassport(
            model_id="test",
            breadth=BreadthResult(score=1.0, passed=9, total=9, failed_capabilities=[]),
            depth=DepthResult(overall_score=1.0, capabilities={}),
            hallucination=HallucinationResult(
                overall_rate=0.0, fabrication_rate=0.0, inconsistency_rate=0.0, refusal_rate=0.0
            ),
        )

    def test_compute_overall_new_weights(self):
        chat = MagicMock()
        orch = ExamOrchestrator(chat, model_id="test")
        passport = CapabilityPassport(
            model_id="test",
            breadth=BreadthResult(score=0.8, passed=7, total=9, failed_capabilities=["a", "b"]),
            depth=DepthResult(overall_score=0.6, capabilities={}),
            hallucination=HallucinationResult(
                overall_rate=0.1, fabrication_rate=0.05, inconsistency_rate=0.03, refusal_rate=0.02
            ),
        )
        # 新权重 0.35/0.50/0.15，无奥赛题→不封顶
        expected = round(0.35 * 0.8 + 0.50 * 0.6 + 0.15 * (1.0 - 0.1), 3)
        result = orch._compute_overall(passport)
        assert result == expected, f"expected {expected}, got {result}"

    def test_compute_overall_perfect_no_cap(self):
        chat = MagicMock()
        orch = ExamOrchestrator(chat, model_id="test")
        passport = self._make_perfect_passport()
        # raw=1.0, 无奥赛题→cap=1.0→min=1.0
        result = orch._compute_overall(passport)
        assert result == round(0.35 * 1.0 + 0.50 * 1.0 + 0.15 * 1.0, 3)
        assert result == 1.0


class TestOlympiadCapping:
    """v3.0.5: 奥赛封顶机制——通过率决定综合分上限。

    pass_rate<0.25→cap 0.80(B+)；<0.50→0.85(A)；<0.75→0.88(A-)；≥0.75→1.0(A+解锁)。
    用完美 passport(raw=1.0)隔离封顶效果：result==cap。
    """

    def _make_orch_with_passes(self, passes: list[bool]) -> ExamOrchestrator:
        orch = ExamOrchestrator(MagicMock(), model_id="test")
        orch._olympiad_case_results = passes
        return orch

    def _perfect_passport(self) -> CapabilityPassport:
        return CapabilityPassport(
            model_id="test",
            breadth=BreadthResult(score=1.0, passed=9, total=9, failed_capabilities=[]),
            depth=DepthResult(overall_score=1.0, capabilities={}),
            hallucination=HallucinationResult(),
        )

    def test_no_olympiad_cases_no_cap(self):
        """无奥赛题→pass_rate=1.0→cap=1.0→不封顶。"""
        orch = self._make_orch_with_passes([])
        result = orch._compute_overall(self._perfect_passport())
        assert result == 1.0

    def test_all_fail_capped_at_bplus(self):
        """0/6 通过→pass_rate=0.0<0.25→cap=0.80。"""
        orch = self._make_orch_with_passes([False] * 6)
        result = orch._compute_overall(self._perfect_passport())
        assert result == 0.80, f"0% pass should cap at 0.80, got {result}"

    def test_one_sixth_pass_capped_at_bplus(self):
        """1/6≈0.167<0.25→cap=0.80。"""
        orch = self._make_orch_with_passes([True] + [False] * 5)
        result = orch._compute_overall(self._perfect_passport())
        assert result == 0.80

    def test_two_sixths_pass_capped_at_a(self):
        """2/6≈0.333∈[0.25,0.50)→cap=0.85。"""
        orch = self._make_orch_with_passes([True, True] + [False] * 4)
        result = orch._compute_overall(self._perfect_passport())
        assert result == 0.85, f"33% pass should cap at 0.85, got {result}"

    def test_half_pass_capped_at_aminus(self):
        """3/6=0.50∈[0.50,0.75)→cap=0.88。"""
        orch = self._make_orch_with_passes([True, True, True] + [False] * 3)
        result = orch._compute_overall(self._perfect_passport())
        assert result == 0.88

    def test_four_sixths_pass_capped_at_aminus(self):
        """4/6≈0.667∈[0.50,0.75)→cap=0.88。"""
        orch = self._make_orch_with_passes([True] * 4 + [False] * 2)
        result = orch._compute_overall(self._perfect_passport())
        assert result == 0.88

    def test_five_sixths_pass_unlocked_aplus(self):
        """5/6≈0.833≥0.75→cap=1.0→不封顶。"""
        orch = self._make_orch_with_passes([True] * 5 + [False] * 1)
        result = orch._compute_overall(self._perfect_passport())
        assert result == 1.0

    def test_all_pass_unlocked_aplus(self):
        """6/6=1.0≥0.75→cap=1.0→不封顶。"""
        orch = self._make_orch_with_passes([True] * 6)
        result = orch._compute_overall(self._perfect_passport())
        assert result == 1.0

    def test_raw_below_cap_returns_raw(self):
        """raw<cap 时取 raw（封顶不抬分）。b=0.5,d=0.5,h=0.5→raw=0.425，全失败 cap=0.80→取0.425。"""
        orch = self._make_orch_with_passes([False] * 6)
        passport = CapabilityPassport(
            model_id="test",
            breadth=BreadthResult(score=0.5, passed=5, total=9, failed_capabilities=[]),
            depth=DepthResult(overall_score=0.5, capabilities={}),
            hallucination=HallucinationResult(overall_rate=0.5),
        )
        raw = round(0.35 * 0.5 + 0.50 * 0.5 + 0.15 * 0.5, 3)  # 0.425
        result = orch._compute_overall(passport)
        assert result == raw, f"raw<cap should return raw {raw}, got {result}"

    def test_pass_rate_boundary_values(self):
        """_compute_olympiad_pass_rate 边界：空→1.0，全False→0.0，全True→1.0，半→0.5。"""
        orch = self._make_orch_with_passes([])
        assert orch._compute_olympiad_pass_rate() == 1.0
        orch = self._make_orch_with_passes([False] * 6)
        assert orch._compute_olympiad_pass_rate() == 0.0
        orch = self._make_orch_with_passes([True] * 6)
        assert orch._compute_olympiad_pass_rate() == 1.0
        orch = self._make_orch_with_passes([True] * 3 + [False] * 3)
        assert orch._compute_olympiad_pass_rate() == 0.5


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
                    "code_fix": DepthCapabilityResult(
                        pass_=False, f1=0.3, failure_reason="low_precision_below_threshold"
                    ),
                    "refactor": DepthCapabilityResult(
                        pass_=False, f1=0.4, failure_reason="low_precision_below_threshold"
                    ),
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

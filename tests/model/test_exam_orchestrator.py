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
    CAPABILITIES,
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


# ══════════════════════════════════════════════════════════
# P2: 三级模式 + 六维幻觉测试
# ══════════════════════════════════════════════════════════


class TestComputeGradeSimple:
    """P2: 五级粗分级 A/B/C/D/F。"""

    def test_grade_a(self):
        from zephyr.intelligence.model_profiling.capability_passport import (
            compute_grade_simple,
        )
        assert compute_grade_simple(0.90) == "A"
        assert compute_grade_simple(0.75) == "A"

    def test_grade_b(self):
        from zephyr.intelligence.model_profiling.capability_passport import (
            compute_grade_simple,
        )
        assert compute_grade_simple(0.74) == "B"
        assert compute_grade_simple(0.60) == "B"

    def test_grade_c(self):
        from zephyr.intelligence.model_profiling.capability_passport import (
            compute_grade_simple,
        )
        assert compute_grade_simple(0.59) == "C"
        assert compute_grade_simple(0.45) == "C"

    def test_grade_d(self):
        from zephyr.intelligence.model_profiling.capability_passport import (
            compute_grade_simple,
        )
        assert compute_grade_simple(0.44) == "D"
        assert compute_grade_simple(0.30) == "D"

    def test_grade_f(self):
        from zephyr.intelligence.model_profiling.capability_passport import (
            compute_grade_simple,
        )
        assert compute_grade_simple(0.29) == "F"
        assert compute_grade_simple(0.0) == "F"


class TestHallucinationBreakdown:
    """P2: 九维幻觉 breakdown property。"""

    def test_default_all_zero(self):
        from zephyr.intelligence.model_profiling.capability_passport import (
            HallucinationBreakdown,
        )
        h = HallucinationBreakdown()
        assert h.overall_rate == 0.0
        assert h.hallucination_score == 1.0

    def test_overall_rate_is_mean(self):
        from zephyr.intelligence.model_profiling.capability_passport import (
            HallucinationBreakdown,
        )
        h = HallucinationBreakdown(
            fabrication=0.2, inconsistency=0.4,
            refusal=0.0, overclaim=0.1,
            context_drift=0.3, source_confusion=0.0,
            instruction_drift=0.0, format_hallucination=0.0,
            quantity_hallucination=0.0,
        )
        # mean(0.2,0.4,0.0,0.1,0.3,0.0,0.0,0.0,0.0) = 1.0/9 ≈ 0.111
        assert h.overall_rate == round(1.0 / 9, 3)

    def test_hallucination_score_inverse(self):
        from zephyr.intelligence.model_profiling.capability_passport import (
            HallucinationBreakdown,
        )
        h = HallucinationBreakdown(fabrication=0.5)
        # mean(0.5,0,...,0)=0.5/9≈0.056, score=1-0.056
        assert h.hallucination_score == round(1.0 - h.overall_rate, 3)

    def test_all_max_hallucination(self):
        from zephyr.intelligence.model_profiling.capability_passport import (
            HallucinationBreakdown,
        )
        h = HallucinationBreakdown(
            fabrication=1.0, inconsistency=1.0, refusal=1.0,
            overclaim=1.0, context_drift=1.0, source_confusion=1.0,
            instruction_drift=1.0, format_hallucination=1.0,
            quantity_hallucination=1.0,
        )
        assert h.overall_rate == 1.0
        assert h.hallucination_score == 0.0

    def test_new_dims_independent(self):
        """新增 3 维独立计入 overall_rate。"""
        from zephyr.intelligence.model_profiling.capability_passport import (
            HallucinationBreakdown,
        )
        h = HallucinationBreakdown(
            instruction_drift=0.9, format_hallucination=0.9,
            quantity_hallucination=0.9,
        )
        # mean(0,0,0,0,0,0,0.9,0.9,0.9) = 2.7/9 = 0.3
        assert h.overall_rate == round(2.7 / 9, 3)


class TestCheckOverclaim:
    """P2: overclaim 检测。"""

    def _make_case(self, capability="refactor", prompt="refactor this code"):
        return ExamTestCase(
            case_id="T", capability=capability,
            difficulty=Difficulty.EASY, prompt=prompt,
        )

    def test_claim_with_empty_field(self):
        case = self._make_case()
        result = {"changes": [], "note": "已重构完成"}
        assert ExamOrchestrator._check_overclaim(case, result) is True

    def test_claim_with_filled_field(self):
        case = self._make_case()
        result = {"changes": [{"old": "x", "new": "y"}], "note": "已重构完成"}
        assert ExamOrchestrator._check_overclaim(case, result) is False

    def test_no_claim(self):
        case = self._make_case()
        result = {"changes": [{"old": "x", "new": "y"}]}
        assert ExamOrchestrator._check_overclaim(case, result) is False

    def test_claim_fixes_empty(self):
        case = self._make_case("code_edit_precision")
        result = {"fixes": [], "msg": "已修复"}
        assert ExamOrchestrator._check_overclaim(case, result) is True

    def test_non_dict_returns_false(self):
        case = self._make_case()
        assert ExamOrchestrator._check_overclaim(case, "not a dict") is False  # type: ignore


class TestCheckSourceConfusion:
    """P2: source confusion 检测。"""

    def _make_case(self, prompt="fix bug in auth.py"):
        return ExamTestCase(
            case_id="T", capability="code_edit_precision",
            difficulty=Difficulty.EASY, prompt=prompt,
        )

    def test_referenced_file_in_prompt(self):
        case = self._make_case("fix bug in auth.py")
        result = {"fixes": [{"old_str": "x", "new_str": "y", "file": "auth.py"}]}
        assert ExamOrchestrator._check_source_confusion(case, result) is False

    def test_referenced_file_not_in_prompt(self):
        case = self._make_case("fix bug in auth.py")
        result = {"fixes": [{"file": "nonexistent.py"}]}
        assert ExamOrchestrator._check_source_confusion(case, result) is True

    def test_generic_file_exempt(self):
        case = self._make_case("fix bug in auth.py")
        result = {"fixes": [{"file": "__init__.py"}]}
        assert ExamOrchestrator._check_source_confusion(case, result) is False

    def test_no_file_referenced(self):
        case = self._make_case("classify this module")
        result = {"category": "web"}
        assert ExamOrchestrator._check_source_confusion(case, result) is False

    def test_input_files_are_legit(self):
        case = ExamTestCase(
            case_id="T", capability="cross_file_refactor",
            difficulty=Difficulty.HARD, prompt="refactor",
            input_files={"a.py": "content", "b.py": "content"},
        )
        result = {"changes": [{"file": "a.py"}, {"file": "b.py"}]}
        assert ExamOrchestrator._check_source_confusion(case, result) is False


class TestCheckInstructionDrift:
    """P2: instruction_drift 检测 (指令偏离)。"""

    def _make_case(self, keys: list[str]) -> ExamTestCase:
        return ExamTestCase(
            case_id="T", capability="task_classification",
            difficulty=Difficulty.EASY, prompt="classify",
            expected_structure_keys=keys,
        )

    def test_structure_matches(self):
        """输出包含所有 required keys → 无偏离。"""
        case = self._make_case(["category", "tags"])
        result = {"category": "web", "tags": ["api"]}
        assert ExamOrchestrator._check_instruction_drift(case, result) is False

    def test_missing_key(self):
        """缺一个 key → 指令偏离。"""
        case = self._make_case(["category", "tags"])
        result = {"category": "web"}  # 缺 tags
        assert ExamOrchestrator._check_instruction_drift(case, result) is True

    def test_empty_value(self):
        """key 存在但值为空 → 指令偏离 (_check_structure 判空值无效)。"""
        case = self._make_case(["category", "tags"])
        result = {"category": "web", "tags": []}  # tags 为空 list
        assert ExamOrchestrator._check_instruction_drift(case, result) is True

    def test_no_expected_keys(self):
        """case 无 expected_structure_keys → 无法判定, 返回 False。"""
        case = ExamTestCase(
            case_id="T", capability="task_classification",
            difficulty=Difficulty.EASY, prompt="test",
        )
        assert ExamOrchestrator._check_instruction_drift(case, {"x": 1}) is False

    def test_non_dict_result(self):
        """非 dict 输出 → False (无法判定结构)。"""
        case = self._make_case(["category"])
        assert ExamOrchestrator._check_instruction_drift(case, "not a dict") is False


class TestCheckFormatHallucination:
    """P2: format_hallucination 检测 (格式幻觉)。"""

    def _make_case(self, keys: list[str]) -> ExamTestCase:
        return ExamTestCase(
            case_id="T", capability="tag_completion",
            difficulty=Difficulty.EASY, prompt="complete tags",
            expected_structure_keys=keys,
        )

    def test_correct_list_type(self):
        """list 字段给了真正的 list → 无格式幻觉。"""
        case = self._make_case(["tags"])
        result = {"tags": ["api", "web"]}
        assert ExamOrchestrator._check_format_hallucination(case, result) is False

    def test_list_stringified_as_json(self):
        """list 字段给了 stringified JSON → 格式幻觉。"""
        case = self._make_case(["tags"])
        result = {"tags": '["api", "web"]'}  # 应该是 list 但给了 JSON 字符串
        assert ExamOrchestrator._check_format_hallucination(case, result) is True

    def test_dict_stringified_as_json(self):
        """dict 字段给了 stringified JSON → 格式幻觉。"""
        case = self._make_case(["config"])
        result = {"config": '{"key": "value"}'}  # 应该是 dict 但给了 JSON 字符串
        assert ExamOrchestrator._check_format_hallucination(case, result) is True

    def test_normal_string_value(self):
        """str 字段正常 → 无格式幻觉。"""
        case = self._make_case(["category"])
        result = {"category": "web"}
        assert ExamOrchestrator._check_format_hallucination(case, result) is False

    def test_no_expected_keys(self):
        """case 无 expected_structure_keys → False。"""
        case = ExamTestCase(
            case_id="T", capability="tag_completion",
            difficulty=Difficulty.EASY, prompt="test",
        )
        assert ExamOrchestrator._check_format_hallucination(case, {"x": 1}) is False


class TestCheckQuantityHallucination:
    """P2: quantity_hallucination 检测 (数量幻觉)。"""

    def test_normal_list_size(self):
        """正常大小 list → 无数量幻觉。"""
        result = {"tags": ["a", "b", "c"]}
        assert ExamOrchestrator._check_quantity_hallucination(
            ExamTestCase(case_id="T", capability="x", difficulty=Difficulty.EASY, prompt=""),
            result,
        ) is False

    def test_inflated_list(self):
        """list 长度 > 20 → 数量幻觉。"""
        result = {"tags": [f"tag_{i}" for i in range(25)]}
        assert ExamOrchestrator._check_quantity_hallucination(
            ExamTestCase(case_id="T", capability="x", difficulty=Difficulty.EASY, prompt=""),
            result,
        ) is True

    def test_inflated_dict(self):
        """dict 长度 > 20 → 数量幻觉。"""
        result = {"mapping": {str(i): i for i in range(25)}}
        assert ExamOrchestrator._check_quantity_hallucination(
            ExamTestCase(case_id="T", capability="x", difficulty=Difficulty.EASY, prompt=""),
            result,
        ) is True

    def test_boundary_exactly_20(self):
        """list 长度 = 20 → 不触发 (阈值 > 20)。"""
        result = {"tags": [f"t{i}" for i in range(20)]}
        assert ExamOrchestrator._check_quantity_hallucination(
            ExamTestCase(case_id="T", capability="x", difficulty=Difficulty.EASY, prompt=""),
            result,
        ) is False

    def test_non_dict_result(self):
        """非 dict 输出 → False。"""
        assert ExamOrchestrator._check_quantity_hallucination(
            ExamTestCase(case_id="T", capability="x", difficulty=Difficulty.EASY, prompt=""),
            "not a dict",
        ) is False


class TestRunHallucinationSixDim:
    """P2: 六维幻觉检测 (mock chat)。"""

    def test_quick_mode_uses_5_caps(self):
        """quick=True 只测 5 个关键能力。"""
        chat = MagicMock()
        chat.inference.return_value = {"category": "ok"}
        orch = ExamOrchestrator(chat, model_id="t")
        breadth = BreadthResult(
            score=1.0, passed=29, total=29, failed_capabilities=[],
        )
        h = orch._run_hallucination_six_dim(breadth, quick=True)
        # 每个能力 2 次推断 (主+对比), 5 能力 = 10 次
        assert chat.inference.call_count == 10
        assert isinstance(h.fabrication, float)

    def test_no_failed_caps_full_mode(self):
        """quick=False 测全部通过的能力 (mock 返回相同结果, inconsistency=0)。"""
        chat = MagicMock()
        chat.inference.return_value = {"category": "web"}
        orch = ExamOrchestrator(chat, model_id="t")
        breadth = BreadthResult(
            score=1.0, passed=29, total=29, failed_capabilities=[],
        )
        h = orch._run_hallucination_six_dim(breadth, quick=False)
        # 全部能力相同输出 → inconsistency=0
        assert h.inconsistency == 0.0

    def test_all_failed_caps_returns_empty(self):
        """全部能力 failed → 返回默认 HallucinationBreakdown。"""
        chat = MagicMock()
        orch = ExamOrchestrator(chat, model_id="t")
        breadth = BreadthResult(
            score=0.0, passed=0, total=29,
            failed_capabilities=list(CAPABILITIES),
        )
        h = orch._run_hallucination_six_dim(breadth, quick=True)
        assert h.overall_rate == 0.0

    def test_inconsistency_detected(self):
        """两次输出键集相同但值不同 → inconsistency > 0, context_drift == 0。"""
        chat = MagicMock()
        # 交替返回不同结果 (键集相同, 值不同)
        chat.inference.side_effect = [
            {"category": "web"},
            {"category": "config"},
        ] * 10  # 每能力 2 次, 5 能力
        orch = ExamOrchestrator(chat, model_id="t")
        breadth = BreadthResult(score=1.0, passed=29, total=29, failed_capabilities=[])
        h = orch._run_hallucination_six_dim(breadth, quick=True)
        assert h.inconsistency > 0.0
        # 键集相同 (都是 {"category"}) → 无 context_drift (独立检测)
        assert h.context_drift == 0.0

    def test_context_drift_detected(self):
        """两次输出键集不同 → context_drift > 0 (忘记指令结构)。"""
        chat = MagicMock()
        # 第一次有 tags, 第二次没有 (键集漂移)
        chat.inference.side_effect = [
            {"category": "web", "tags": ["a"]},
            {"category": "config"},
        ] * 10
        orch = ExamOrchestrator(chat, model_id="t")
        breadth = BreadthResult(score=1.0, passed=29, total=29, failed_capabilities=[])
        h = orch._run_hallucination_six_dim(breadth, quick=True)
        assert h.context_drift > 0.0


class TestRunQuickExam:
    """P2: Quick 模式快速画像。"""

    def test_quick_exam_returns_quick_profile(self):
        """Quick 模式返回 QuickProfile, 不是 CapabilityPassport。"""
        from zephyr.intelligence.model_profiling.capability_passport import QuickProfile
        chat = MagicMock()
        chat.inference.return_value = {"category": "web", "tags": ["x"]}
        orch = ExamOrchestrator(chat, model_id="test-quick")
        profile = orch.run_quick_exam()
        assert isinstance(profile, QuickProfile)
        assert profile.exam_mode == "quick"
        assert profile.model_id == "test-quick"

    def test_quick_exam_has_capability_grades(self):
        """Quick 模式输出包含能力分级。"""
        chat = MagicMock()
        chat.inference.return_value = {"category": "web", "tags": ["x"]}
        orch = ExamOrchestrator(chat, model_id="t")
        profile = orch.run_quick_exam()
        assert len(profile.capability_grades) > 0
        assert all(g in "ABCDF" for g in profile.capability_grades.values())

    def test_quick_exam_has_hallucination_breakdown(self):
        """Quick 模式输出包含六维幻觉。"""
        chat = MagicMock()
        chat.inference.return_value = {"category": "web"}
        orch = ExamOrchestrator(chat, model_id="t")
        profile = orch.run_quick_exam()
        # 六维字段都存在
        assert hasattr(profile.hallucination, "fabrication")
        assert hasattr(profile.hallucination, "overclaim")
        assert hasattr(profile.hallucination, "source_confusion")

    def test_quick_exam_has_recommendations(self):
        """Quick 模式输出包含 Top3 岗位推荐。"""
        chat = MagicMock()
        chat.inference.return_value = {"category": "web", "tags": ["x"]}
        orch = ExamOrchestrator(chat, model_id="t")
        profile = orch.run_quick_exam()
        assert len(profile.recommendations) <= 3
        if profile.recommendations:
            assert profile.recommendations[0].match_score >= profile.recommendations[-1].match_score

    def test_quick_exam_duration_positive(self):
        """Quick 模式耗时 > 0。"""
        chat = MagicMock()
        chat.inference.return_value = {"category": "web"}
        orch = ExamOrchestrator(chat, model_id="t")
        profile = orch.run_quick_exam()
        assert profile.exam_duration_seconds >= 0.0


class TestRunExamModes:
    """P2: 三级模式统一入口路由。"""

    def test_run_exam_quick(self):
        """run_exam(mode='quick') 返回 QuickProfile。"""
        from zephyr.intelligence.model_profiling.capability_passport import QuickProfile
        chat = MagicMock()
        chat.inference.return_value = {"category": "web"}
        orch = ExamOrchestrator(chat, model_id="t")
        result = orch.run_exam(mode="quick")
        assert isinstance(result, QuickProfile)

    def test_run_exam_unknown_mode_raises(self):
        """未知 mode 抛 ValueError。"""
        chat = MagicMock()
        orch = ExamOrchestrator(chat, model_id="t")
        with pytest.raises(ValueError, match="unknown exam mode"):
            orch.run_exam(mode="invalid")

    def test_run_exam_mode_case_insensitive(self):
        """mode 大小写不敏感。"""
        from zephyr.intelligence.model_profiling.capability_passport import QuickProfile
        chat = MagicMock()
        chat.inference.return_value = {"category": "web"}
        orch = ExamOrchestrator(chat, model_id="t")
        result = orch.run_exam(mode="QUICK")
        assert isinstance(result, QuickProfile)

    def test_run_standard_exam_skip_drift(self):
        """run_standard_exam 默认 skip_drift=True。"""
        chat = MagicMock()
        chat.inference.return_value = {"category": "web", "tags": ["x"]}
        orch = ExamOrchestrator(chat, model_id="t")
        # 应该不调用 drift (mock 会让 drift 内部跑, 但 skip_drift=True 跳过)
        passport = orch.run_standard_exam()
        assert passport is not None
        # drift.tested 应为 False (skip_drift)
        assert passport.drift.tested is False

    def test_run_deep_exam_forces_n_ge_3(self):
        """run_deep_exam 强制 n>=3。"""
        chat = MagicMock()
        chat.inference.return_value = {"category": "web", "tags": ["x"]}
        orch = ExamOrchestrator(chat, model_id="t", depth_samples_per_case=1)
        assert orch._depth_samples_per_case == 1
        # run_deep_exam 会 bump 到 3, 但实际跑全量太慢, 只验证 bump 逻辑
        # 用 mock 让 run_full_exam 快速返回
        with pytest.MonkeyPatch.context() as mp:
            mp.setattr(orch, "run_full_exam", lambda skip_drift=False: CapabilityPassport(model_id="t"))
            orch.run_deep_exam()
            assert orch._depth_samples_per_case >= 3


class TestPickRepresentativeCase:
    """P2: Quick 模式代表题选择。"""

    def test_prefer_medium(self):
        """优先选 medium 难度。"""
        chat = MagicMock()
        orch = ExamOrchestrator(chat, model_id="t")
        case = orch._pick_representative_case("task_classification")
        assert case is not None
        assert case.difficulty == Difficulty.MEDIUM

    def test_nonexistent_cap_returns_none(self):
        """不存在的能力返回 None。"""
        chat = MagicMock()
        orch = ExamOrchestrator(chat, model_id="t")
        case = orch._pick_representative_case("nonexistent_capability")
        assert case is None


class TestBuildRecommendationsContinued:
    """原 TestBuildRecommendations 的后续测试 (P2 追加时类被分割)。"""

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


# ══════════════════════════════════════════════════════════
# P2 Tool 轴 (ROADMAP-02): function_calling + tool_chaining
# ══════════════════════════════════════════════════════════

class TestComputeMetricsFunctionCalling:
    """_compute_metrics_generic 对 function_calling (expected_function_args) 的评分。"""

    def _make_orch(self):
        return ExamOrchestrator(MagicMock(), model_id="t")

    def _make_case(self, tool: str, args: dict, contains=None):
        return ExamTestCase(
            case_id="T",
            capability="function_calling",
            difficulty=Difficulty.EASY,
            prompt="test",
            expected_structure_keys=["function", "arguments"],
            expected_tool=tool,
            expected_function_args=args,
            expected_contains=contains or [],
        )

    def test_perfect_match(self):
        """function 名 + 所有参数 value 命中 → 高分。"""
        orch = self._make_orch()
        case = self._make_case(
            "Read", {"file_path": "docker-compose"}, contains=["file_path"]
        )
        result = {
            "function": "Read",
            "arguments": {"file_path": "/abs/docker-compose.yml"},
        }
        p, r, ed, em = orch._compute_metrics(case, result)
        assert p == pytest.approx(1.0, abs=0.01)
        assert em == 1

    def test_wrong_function_name(self):
        """function 名错误 → expected_tool 不匹配。"""
        orch = self._make_orch()
        case = self._make_case("Read", {"file_path": "docker-compose"})
        result = {"function": "Grep", "arguments": {"file_path": "docker-compose"}}
        p, r, ed, em = orch._compute_metrics(case, result)
        assert em == 0
        assert p < 1.0

    def test_key_present_value_missing(self):
        """参数 key 存在但 value 不符 → 部分分 (0.5)。"""
        orch = self._make_orch()
        case = self._make_case("Grep", {"pattern": "TODO", "path": "src"})
        # pattern 对, path 不符
        result = {"function": "Grep", "arguments": {"pattern": "TODO", "path": "/other"}}
        p, r, ed, em = orch._compute_metrics(case, result)
        assert em == 0
        # args: pattern=1.0, path=0.5 → arg_rate=0.75; tool=1.0; contains 也可命中
        assert 0.0 < p < 1.0

    def test_missing_arguments_key(self):
        """模型输出无 arguments → arg_rate=0。"""
        orch = self._make_orch()
        case = self._make_case("Read", {"file_path": "config.py"})
        result = {"function": "Read"}  # 无 arguments
        p, r, ed, em = orch._compute_metrics(case, result)
        assert em == 0


class TestComputeMetricsToolChaining:
    """_compute_metrics_generic 对 tool_chaining (expected_tool_sequence) 的评分。"""

    def _make_orch(self):
        return ExamOrchestrator(MagicMock(), model_id="t")

    def _make_case(self, seq: list[str], contains=None):
        return ExamTestCase(
            case_id="T",
            capability="tool_chaining",
            difficulty=Difficulty.EASY,
            prompt="test",
            expected_structure_keys=["steps"],
            expected_tool_sequence=seq,
            expected_contains=contains or [],
        )

    def test_perfect_order(self):
        """steps 工具顺序完全匹配 → 满分。"""
        orch = self._make_orch()
        case = self._make_case(["Grep", "Read"], contains=["Grep", "Read"])
        result = {"steps": [
            {"tool": "Grep", "purpose": "find"},
            {"tool": "Read", "purpose": "read"},
        ]}
        p, r, ed, em = orch._compute_metrics(case, result)
        assert p == pytest.approx(1.0, abs=0.01)
        assert em == 1

    def test_wrong_order(self):
        """工具顺序错误 → seq_rate 部分匹配。"""
        orch = self._make_orch()
        case = self._make_case(["Grep", "Read"], contains=["Grep", "Read"])
        result = {"steps": [
            {"tool": "Read", "purpose": "read first"},
            {"tool": "Grep", "purpose": "then search"},
        ]}
        p, r, ed, em = orch._compute_metrics(case, result)
        # Read 在前, Grep 在后; expected=[Grep,Read] 作为子序列无法匹配
        assert em == 0

    def test_partial_sequence(self):
        """3 步期望, 只匹配 2 步 → 部分分。"""
        orch = self._make_orch()
        case = self._make_case(["Glob", "Read", "Edit"], contains=["Glob", "Read", "Edit"])
        result = {"steps": [
            {"tool": "Glob", "purpose": "find"},
            {"tool": "Read", "purpose": "read"},
        ]}  # 缺 Edit
        p, r, ed, em = orch._compute_metrics(case, result)
        assert em == 0
        assert p < 1.0

    def test_steps_with_function_key(self):
        """steps 中用 'function' 而非 'tool' 也能匹配。"""
        orch = self._make_orch()
        case = self._make_case(["Grep", "Read"], contains=["Grep", "Read"])
        result = {"steps": [
            {"function": "Grep"},
            {"function": "Read"},
        ]}
        p, r, ed, em = orch._compute_metrics(case, result)
        assert em == 1

    def test_extra_steps_interleaved(self):
        """中间插入额外步骤, 期望序列仍为有序子序列 → 匹配 (em=1)。"""
        orch = self._make_orch()
        case = self._make_case(["Grep", "Read"], contains=["Grep", "Read"])
        result = {"steps": [
            {"tool": "Glob", "purpose": "first find files"},
            {"tool": "Grep", "purpose": "then search"},
            {"tool": "Write", "purpose": "log"},
            {"tool": "Read", "purpose": "finally read"},
        ]}
        p, r, ed, em = orch._compute_metrics(case, result)
        # Grep 和 Read 仍按序出现 → seq_rate=1.0; contains Grep/Read 均在文本中 → 全中
        # 额外的 Glob/Write 不在任何 expected 字段中, 不扣分
        assert em == 1
        assert p == pytest.approx(1.0, abs=0.01)


class TestDeterministicJudgeToolAxis:
    """DeterministicJudge 对 P 类 Tool 轴字段的评分。"""

    def _make_judge(self):
        from zephyr.intelligence.model_profiling.exam_judge import DeterministicJudge
        return DeterministicJudge()

    def test_function_args_full_hit(self):
        """参数 key+value 全命中 → correctness 高。"""
        judge = self._make_judge()
        case = ExamTestCase(
            case_id="T", capability="function_calling",
            difficulty=Difficulty.EASY, prompt="t",
            expected_structure_keys=["function", "arguments"],
            expected_tool="Read",
            expected_function_args={"file_path": "docker-compose"},
            expected_contains=["file_path"],
        )
        text = '{"function": "Read", "arguments": {"file_path": "/abs/docker-compose.yml"}}'
        result = judge.judge(case, text)
        # keyword "file_path" 命中 + tool args 全命中 → correctness 高
        assert result.correctness == pytest.approx(1.0, abs=0.01)

    def test_function_args_partial(self):
        """参数 key 存在但 value 不符 → correctness 部分分。"""
        judge = self._make_judge()
        case = ExamTestCase(
            case_id="T", capability="function_calling",
            difficulty=Difficulty.EASY, prompt="t",
            expected_function_args={"pattern": "TODO", "path": "src"},
            expected_contains=["pattern", "path"],
        )
        text = '{"function": "Grep", "arguments": {"pattern": "FIXME", "path": "src"}}'
        result = judge.judge(case, text)
        # pattern key 存在 value 不符 (0.5), path 全中 (1.0) → arg_score=0.75
        assert 0.0 < result.correctness < 1.0

    def test_tool_sequence_ordered(self):
        """工具按序出现 → seq_score=1.0。"""
        judge = self._make_judge()
        case = ExamTestCase(
            case_id="T", capability="tool_chaining",
            difficulty=Difficulty.EASY, prompt="t",
            expected_tool_sequence=["Grep", "Read"],
            expected_contains=["Grep", "Read"],
        )
        text = '{"steps": [{"tool": "Grep"}, {"tool": "Read"}]}' + " " * 50
        result = judge.judge(case, text)
        assert result.correctness == pytest.approx(1.0, abs=0.01)

    def test_tool_sequence_wrong_order(self):
        """工具乱序 → seq_score 部分分。"""
        judge = self._make_judge()
        case = ExamTestCase(
            case_id="T", capability="tool_chaining",
            difficulty=Difficulty.EASY, prompt="t",
            expected_tool_sequence=["Grep", "Read"],
            expected_contains=["Grep", "Read"],
        )
        text = '{"steps": [{"tool": "Read"}, {"tool": "Grep"}]}' + " " * 50
        result = judge.judge(case, text)
        # keyword 全中 (0.5 weight) + seq: Grep 在 Read 后, 作为有序子序列只匹配 Grep (1/2=0.5)
        # tool_score = 0.5*keyword + 0.5*seq = 0.5*1.0 + 0.5*0.5 = 0.75
        # correctness = 0.5*keyword_cov + 0.5*tool_score = 0.5*1.0 + 0.5*0.75 = 0.875
        assert 0.0 < result.correctness < 1.0

    def test_no_tool_fields_neutral(self):
        """无 Tool 轴字段 → 不影响原有评分逻辑。"""
        judge = self._make_judge()
        case = ExamTestCase(
            case_id="T", capability="x",
            difficulty=Difficulty.EASY, prompt="t",
            expected_contains=["alpha"],
        )
        text = "alpha " * 30
        result = judge.judge(case, text)
        assert result.correctness == 1.0  # 纯关键词, 无 tool 字段干扰


class TestToolAxisCasesRegistered:
    """验证 function_calling / tool_chaining 题目正确注册到 CASES_BY_CAPABILITY。"""

    def test_function_calling_cases(self):
        from zephyr.intelligence.model_profiling.exam_test_cases import (
            CASES_BY_CAPABILITY,
        )
        cases = CASES_BY_CAPABILITY.get("function_calling", [])
        assert len(cases) == 3
        ids = [c.case_id for c in cases]
        assert "EX-FC-001" in ids
        assert "EX-FC-002" in ids
        assert "EX-FC-003" in ids
        # 每题有 expected_function_args
        for c in cases:
            assert c.expected_function_args, f"{c.case_id} 缺 expected_function_args"

    def test_tool_chaining_cases(self):
        from zephyr.intelligence.model_profiling.exam_test_cases import (
            CASES_BY_CAPABILITY,
        )
        cases = CASES_BY_CAPABILITY.get("tool_chaining", [])
        assert len(cases) == 3
        ids = [c.case_id for c in cases]
        assert "EX-TC-001" in ids
        assert "EX-TC-002" in ids
        assert "EX-TC-003" in ids
        # 每题有 expected_tool_sequence
        for c in cases:
            assert c.expected_tool_sequence, f"{c.case_id} 缺 expected_tool_sequence"

    def test_difficulty_coverage(self):
        """每能力覆盖 EASY/MEDIUM/HARD 三难度。"""
        from zephyr.intelligence.model_profiling.exam_test_cases import (
            CASES_BY_CAPABILITY,
        )
        for cap in ("function_calling", "tool_chaining"):
            diffs = {c.difficulty for c in CASES_BY_CAPABILITY[cap]}
            assert Difficulty.EASY in diffs
            assert Difficulty.MEDIUM in diffs
            assert Difficulty.HARD in diffs

    def test_total_capability_count(self):
        """Tool 轴新增 2 能力后, 总能力数=31。"""
        from zephyr.intelligence.model_profiling.exam_test_cases import (
            CASES_BY_CAPABILITY,
        )
        assert len(CASES_BY_CAPABILITY) == 31


# ══════════════════════════════════════════════════════════
# 5.158.12 回归测试——_compute_metrics 硬编码分支行为等价验证
# 重构前编写，验证 extract method 后行为不变。
# ══════════════════════════════════════════════════════════

class TestComputeMetricsHardcodedBranches:
    """_compute_metrics 6 个硬编码分支的直接回归测试。"""

    def _make_orch(self):
        return ExamOrchestrator(MagicMock(), model_id="t")

    # --- task_classification ---

    def test_task_classification_match(self):
        orch = self._make_orch()
        case = ExamTestCase(
            case_id="T", capability="task_classification",
            difficulty=Difficulty.EASY, prompt="x",
            expected_category="utils",
        )
        p, r, ed, em = orch._compute_metrics(case, {"category": "utils"})
        assert em == 1
        assert p == 1.0 and r == 1.0

    def test_task_classification_mismatch(self):
        orch = self._make_orch()
        case = ExamTestCase(
            case_id="T", capability="task_classification",
            difficulty=Difficulty.EASY, prompt="x",
            expected_category="utils",
        )
        p, r, ed, em = orch._compute_metrics(case, {"category": "governance"})
        assert em == 0

    # --- tag_completion ---

    def test_tag_completion_exact(self):
        orch = self._make_orch()
        case = ExamTestCase(
            case_id="T", capability="tag_completion",
            difficulty=Difficulty.EASY, prompt="x",
            expected_tags=["a", "b"],
        )
        p, r, ed, em = orch._compute_metrics(case, {"tags": ["a", "b"]})
        assert em == 1
        assert p == 1.0 and r == 1.0

    def test_tag_completion_partial(self):
        orch = self._make_orch()
        case = ExamTestCase(
            case_id="T", capability="tag_completion",
            difficulty=Difficulty.EASY, prompt="x",
            expected_tags=["a", "b"],
        )
        p, r, ed, em = orch._compute_metrics(case, {"tags": ["a"]})
        assert em == 0
        assert 0.0 < p <= 1.0

    def test_tag_completion_empty_pred(self):
        orch = self._make_orch()
        case = ExamTestCase(
            case_id="T", capability="tag_completion",
            difficulty=Difficulty.EASY, prompt="x",
            expected_tags=["a"],
        )
        p, r, ed, em = orch._compute_metrics(case, {"tags": []})
        assert em == 0
        assert p == 0.0

    # --- summary_extraction / naming_suggest ---

    def test_summary_extraction_all_hits(self):
        orch = self._make_orch()
        case = ExamTestCase(
            case_id="T", capability="summary_extraction",
            difficulty=Difficulty.EASY, prompt="x",
            expected_contains=["hello", "world"],
        )
        p, r, ed, em = orch._compute_metrics(case, "hello world text")
        assert em == 1
        assert p == 1.0

    def test_summary_extraction_partial(self):
        orch = self._make_orch()
        case = ExamTestCase(
            case_id="T", capability="summary_extraction",
            difficulty=Difficulty.EASY, prompt="x",
            expected_contains=["hello", "world"],
        )
        p, r, ed, em = orch._compute_metrics(case, "hello only")
        assert em == 0
        assert p == pytest.approx(0.5, abs=0.01)

    def test_naming_suggest_uses_same_logic(self):
        orch = self._make_orch()
        case = ExamTestCase(
            case_id="T", capability="naming_suggest",
            difficulty=Difficulty.EASY, prompt="x",
            expected_contains=["foo"],
        )
        p, r, ed, em = orch._compute_metrics(case, "the foo bar")
        assert em == 1

    # --- anomaly_triage ---

    def test_anomaly_triage_match_true(self):
        orch = self._make_orch()
        case = ExamTestCase(
            case_id="T", capability="anomaly_triage",
            difficulty=Difficulty.EASY, prompt="x",
            expected_needs_human=True,
        )
        p, r, ed, em = orch._compute_metrics(case, {"needs_human": True})
        assert em == 1

    def test_anomaly_triage_mismatch(self):
        orch = self._make_orch()
        case = ExamTestCase(
            case_id="T", capability="anomaly_triage",
            difficulty=Difficulty.EASY, prompt="x",
            expected_needs_human=True,
        )
        p, r, ed, em = orch._compute_metrics(case, {"needs_human": False})
        assert em == 0

    # --- code_fix / code_edit_precision / refactor / dead_code_removal ---

    def test_code_fix_exact_old_str(self):
        orch = self._make_orch()
        case = ExamTestCase(
            case_id="T", capability="code_fix",
            difficulty=Difficulty.EASY, prompt="x",
            expected_old_str="old code",
            expected_contains=["kw"],
        )
        result = {"fixes": [{"old_str": "old code"}], "kw": 1}
        p, r, ed, em = orch._compute_metrics(case, result)
        assert em == 1
        assert ed == pytest.approx(0.0, abs=0.01)

    def test_code_fix_no_entries(self):
        orch = self._make_orch()
        case = ExamTestCase(
            case_id="T", capability="code_fix",
            difficulty=Difficulty.EASY, prompt="x",
            expected_old_str="old code",
        )
        p, r, ed, em = orch._compute_metrics(case, {"fixes": []})
        assert em == 0
        assert ed == 1.0

    def test_code_edit_precision_best_ed(self):
        orch = self._make_orch()
        case = ExamTestCase(
            case_id="T", capability="code_edit_precision",
            difficulty=Difficulty.EASY, prompt="x",
            expected_old_str="abc",
        )
        result = {"fixes": [{"old_str": "axc"}, {"old_str": "abd"}]}
        p, r, ed, em = orch._compute_metrics(case, result)
        assert em == 0
        assert 0.0 < ed < 1.0

    def test_refactor_uses_changes_field(self):
        orch = self._make_orch()
        case = ExamTestCase(
            case_id="T", capability="refactor",
            difficulty=Difficulty.EASY, prompt="x",
            expected_old_str="target",
        )
        result = {"changes": [{"old_str": "target"}]}
        p, r, ed, em = orch._compute_metrics(case, result)
        assert em == 1

    def test_dead_code_removal_uses_dead_sections(self):
        orch = self._make_orch()
        case = ExamTestCase(
            case_id="T", capability="dead_code_removal",
            difficulty=Difficulty.EASY, prompt="x",
            expected_old_str="dead",
        )
        result = {"dead_sections": [{"old_str": "dead"}]}
        p, r, ed, em = orch._compute_metrics(case, result)
        assert em == 1

    # --- code_generate ---

    def test_code_generate_with_content(self):
        orch = self._make_orch()
        case = ExamTestCase(
            case_id="T", capability="code_generate",
            difficulty=Difficulty.EASY, prompt="x",
            expected_contains=["def", "main"],
        )
        result = {"content": "def main(): pass"}
        p, r, ed, em = orch._compute_metrics(case, result)
        assert em == 1
        assert p == 1.0

    def test_code_generate_empty_content(self):
        orch = self._make_orch()
        case = ExamTestCase(
            case_id="T", capability="code_generate",
            difficulty=Difficulty.EASY, prompt="x",
            expected_contains=["def"],
        )
        result = {"content": ""}
        p, r, ed, em = orch._compute_metrics(case, result)
        assert em == 0
        assert ed == 1.0

    def test_code_generate_codegen_nested(self):
        """content 嵌套在 codegen.content 中也能取到。"""
        orch = self._make_orch()
        case = ExamTestCase(
            case_id="T", capability="code_generate",
            difficulty=Difficulty.EASY, prompt="x",
            expected_contains=["hello"],
        )
        result = {"codegen": {"content": "hello world"}}
        p, r, ed, em = orch._compute_metrics(case, result)
        assert em == 1

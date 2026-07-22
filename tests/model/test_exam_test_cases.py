# [A_test] module_id: MOD-GOV_exam_test_cases | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §3
# [MODULE] tests.test_exam_test_cases
# [INVARIANTS] test_exam_test_cases完整性
# [MODIFY-GUARD] none
# [CONSUMERS] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] none
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

# v3.0.5: import 统一到 #3 生产源（zephyr.intelligence.model_profiling）
from zephyr.intelligence.model_profiling.exam_test_cases import (
    ALL_EXAM_CASES,
    CASES_BY_CAPABILITY,
    Difficulty,
    ExamTestCase,
)


class TestDifficultyEnum:
    def test_easy_value(self):
        assert Difficulty.EASY.value == "easy"

    def test_medium_value(self):
        assert Difficulty.MEDIUM.value == "medium"

    def test_hard_value(self):
        assert Difficulty.HARD.value == "hard"

    def test_extreme_value(self):
        assert Difficulty.EXTREME.value == "extreme"

    def test_olympiad_value(self):
        assert Difficulty.OLYMPIAD.value == "olympiad"

    def test_member_count(self):
        assert len(Difficulty) == 5

    def test_members_are_unique(self):
        values = [m.value for m in Difficulty]
        assert len(set(values)) == 5


class TestExamTestCaseInstantiation:
    def test_full_fields(self):
        tc = ExamTestCase(
            case_id="EX-XX-001",
            capability="test_cap",
            difficulty=Difficulty.HARD,
            prompt="do something",
            expected_structure_keys=["key1", "key2"],
            expected_tags=["tag1", "tag2"],
            expected_category="cat",
            expected_old_str="old",
            expected_new_str="new",
            expected_needs_human=True,
            expected_contains=["a", "b"],
        )
        assert tc.case_id == "EX-XX-001"
        assert tc.capability == "test_cap"
        assert tc.difficulty is Difficulty.HARD
        assert tc.prompt == "do something"
        assert tc.expected_structure_keys == ["key1", "key2"]
        assert tc.expected_tags == ["tag1", "tag2"]
        assert tc.expected_category == "cat"
        assert tc.expected_old_str == "old"
        assert tc.expected_new_str == "new"
        assert tc.expected_needs_human is True
        assert tc.expected_contains == ["a", "b"]

    def test_required_fields_only(self):
        tc = ExamTestCase(
            case_id="EX-YY-001",
            capability="cap",
            difficulty=Difficulty.EASY,
            prompt="prompt text",
        )
        assert tc.case_id == "EX-YY-001"
        assert tc.capability == "cap"
        assert tc.difficulty is Difficulty.EASY
        assert tc.prompt == "prompt text"


class TestExamTestCaseDefaults:
    def test_default_structure_keys(self):
        tc = ExamTestCase(case_id="X", capability="c", difficulty=Difficulty.EASY, prompt="p")
        assert tc.expected_structure_keys == []

    def test_default_tags(self):
        tc = ExamTestCase(case_id="X", capability="c", difficulty=Difficulty.EASY, prompt="p")
        assert tc.expected_tags == []

    def test_default_category(self):
        tc = ExamTestCase(case_id="X", capability="c", difficulty=Difficulty.EASY, prompt="p")
        assert tc.expected_category == ""

    def test_default_old_str(self):
        tc = ExamTestCase(case_id="X", capability="c", difficulty=Difficulty.EASY, prompt="p")
        assert tc.expected_old_str == ""

    def test_default_new_str(self):
        tc = ExamTestCase(case_id="X", capability="c", difficulty=Difficulty.EASY, prompt="p")
        assert tc.expected_new_str == ""

    def test_default_needs_human(self):
        tc = ExamTestCase(case_id="X", capability="c", difficulty=Difficulty.EASY, prompt="p")
        assert tc.expected_needs_human is False

    def test_default_contains(self):
        tc = ExamTestCase(case_id="X", capability="c", difficulty=Difficulty.EASY, prompt="p")
        assert tc.expected_contains == []

    def test_list_defaults_are_independent(self):
        tc1 = ExamTestCase(case_id="A", capability="c", difficulty=Difficulty.EASY, prompt="p")
        tc2 = ExamTestCase(case_id="B", capability="c", difficulty=Difficulty.EASY, prompt="p")
        tc1.expected_structure_keys.append("x")
        assert tc2.expected_structure_keys == []


class TestAllExamCases:
    def test_count(self):
        # v2.3.2: 96→127 (审查2.1修复: 23孤儿激活+2废弃删除+2负例对照)
        assert len(ALL_EXAM_CASES) == 127

    def test_all_are_exam_test_case(self):
        for tc in ALL_EXAM_CASES:
            assert isinstance(tc, ExamTestCase)

    def test_all_case_ids_unique(self):
        ids = [tc.case_id for tc in ALL_EXAM_CASES]
        assert len(ids) == len(set(ids))

    def test_all_prompts_non_empty(self):
        for tc in ALL_EXAM_CASES:
            assert len(tc.prompt) > 0

    def test_all_capabilities_non_empty(self):
        for tc in ALL_EXAM_CASES:
            assert len(tc.capability) > 0


class TestCasesByCapability:
    # v3.0.5: 关键能力子集（不硬等全量 28 个，仅断言核心能力存在）
    KEY_CAPABILITIES = {
        "task_classification",
        "tag_completion",
        "code_edit_precision",
        "code_generate",
        "dead_code_removal",
    }

    def test_key_count(self):
        # v2.3.2: 29→31 (ROADMAP-02 新增 function_calling/tool_chaining)
        assert len(CASES_BY_CAPABILITY) == 31

    def test_capabilities_match_expected(self):
        assert self.KEY_CAPABILITIES <= set(CASES_BY_CAPABILITY.keys())

    def test_each_capability_has_at_least_one_case(self):
        for cap, cases in CASES_BY_CAPABILITY.items():
            assert len(cases) >= 1, f"{cap} has 0 cases"

    def test_all_cases_in_dict_match_capability(self):
        for cap, cases in CASES_BY_CAPABILITY.items():
            for tc in cases:
                assert tc.capability == cap

    def test_total_cases_in_dict(self):
        total = sum(len(cases) for cases in CASES_BY_CAPABILITY.values())
        # v2.3.2: 96→127 (审查2.1修复: 23孤儿激活+2废弃删除+2负例对照)
        assert total == 127

    def test_difficulties_per_capability(self):
        for cap, cases in CASES_BY_CAPABILITY.items():
            difficulties = {tc.difficulty for tc in cases}
            assert len(difficulties) >= 1, f"{cap} has 0 difficulties: {difficulties}"

    def test_olympiad_difficulty_correct(self):
        """v3.0.5: EX_OLY_004 难度必须为 OLYMPIAD（原 bug 为 EXTREME）。"""
        oly_cases = {tc.case_id: tc for tc in ALL_EXAM_CASES if tc.case_id.startswith("EX-OLY")}
        assert "EX-OLY-004" in oly_cases, "EX-OLY-004 not found"
        assert oly_cases["EX-OLY-004"].difficulty == Difficulty.OLYMPIAD, (
            f"EX-OLY-004 difficulty is {oly_cases['EX-OLY-004'].difficulty}, expected OLYMPIAD"
        )


class TestExamTestCaseBoundary:
    def test_empty_strings_and_lists(self):
        tc = ExamTestCase(
            case_id="",
            capability="",
            difficulty=Difficulty.EASY,
            prompt="",
            expected_structure_keys=[],
            expected_tags=[],
            expected_category="",
            expected_old_str="",
            expected_new_str="",
            expected_needs_human=False,
            expected_contains=[],
        )
        assert tc.case_id == ""
        assert tc.capability == ""
        assert tc.prompt == ""
        assert tc.expected_structure_keys == []
        assert tc.expected_tags == []
        assert tc.expected_category == ""
        assert tc.expected_old_str == ""
        assert tc.expected_new_str == ""
        assert tc.expected_needs_human is False
        assert tc.expected_contains == []

    def test_none_accepted_for_optional_fields(self):
        tc = ExamTestCase(case_id="X", capability="c", difficulty=Difficulty.EASY, prompt="p")
        assert tc.case_id == "X"
        assert tc.expected_needs_human is False

    def test_long_strings(self):
        long_str = "x" * 10000
        tc = ExamTestCase(
            case_id=long_str,
            capability=long_str,
            difficulty=Difficulty.HARD,
            prompt=long_str,
        )
        assert len(tc.case_id) == 10000
        assert len(tc.prompt) == 10000

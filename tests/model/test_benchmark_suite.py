# [A_test] module_id: MOD-GOV_benchmark_suite | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §3
# [MODULE] tests.test_benchmark_suite
# [INVARIANTS] BenchmarkCase数据模型;7维度测试用例完整性;CATEGORY_MAP键覆盖
# [MODIFY-GUARD] src/zephyr/pipeline/model-profiler/benchmark_suite.py
# [CONSUMERS] MOD-INF-034
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.AssertionError
# [TESTS] tests/test_benchmark_suite.py
# [TTL] task_bound


from zephyr.intelligence.model_profiling.benchmark_suite import (
    ALL_BENCHMARK_CASES,
    CATEGORY_MAP,
    CODE_GEN_CASES,
    BenchmarkCase,
)


class TestBenchmarkCaseConstruction:
    def test_all_fields_populated(self):
        case = BenchmarkCase(
            case_id="T-001",
            category="test_cat",
            subcategory="test_sub",
            prompt="hello",
            expected_patterns=["a", "b"],
            forbidden_patterns=["c"],
            max_tokens=1024,
            expected_output_type="code",
            weight=2.5,
            reference_answer="ref",
        )
        assert case.case_id == "T-001"
        assert case.category == "test_cat"
        assert case.subcategory == "test_sub"
        assert case.prompt == "hello"
        assert case.expected_patterns == ["a", "b"]
        assert case.forbidden_patterns == ["c"]
        assert case.max_tokens == 1024
        assert case.expected_output_type == "code"
        assert case.weight == 2.5
        assert case.reference_answer == "ref"

    def test_required_fields_only(self):
        case = BenchmarkCase(
            case_id="R-001",
            category="cat",
            subcategory="sub",
            prompt="prompt text",
        )
        assert case.case_id == "R-001"
        assert case.category == "cat"
        assert case.subcategory == "sub"
        assert case.prompt == "prompt text"


class TestBenchmarkCaseFullName:
    def test_full_name_format(self):
        case = BenchmarkCase(
            case_id="CG-001",
            category="code_generation",
            subcategory="function_impl",
            prompt="x",
        )
        assert case.full_name == "code_generation/function_impl/CG-001"

    def test_full_name_with_empty_parts(self):
        case = BenchmarkCase(case_id="", category="", subcategory="", prompt="x")
        assert case.full_name == "//"


class TestBenchmarkCaseDefaults:
    def test_expected_patterns_default(self):
        case = BenchmarkCase(case_id="D-001", category="c", subcategory="s", prompt="p")
        assert case.expected_patterns == []

    def test_forbidden_patterns_default(self):
        case = BenchmarkCase(case_id="D-002", category="c", subcategory="s", prompt="p")
        assert case.forbidden_patterns == []

    def test_max_tokens_default(self):
        case = BenchmarkCase(case_id="D-003", category="c", subcategory="s", prompt="p")
        assert case.max_tokens == 512

    def test_expected_output_type_default(self):
        case = BenchmarkCase(case_id="D-004", category="c", subcategory="s", prompt="p")
        assert case.expected_output_type == "text"

    def test_weight_default(self):
        case = BenchmarkCase(case_id="D-005", category="c", subcategory="s", prompt="p")
        assert case.weight == 1.0

    def test_reference_answer_default(self):
        case = BenchmarkCase(case_id="D-006", category="c", subcategory="s", prompt="p")
        assert case.reference_answer == ""

    def test_defaults_are_independent_per_instance(self):
        a = BenchmarkCase(case_id="A", category="c", subcategory="s", prompt="p")
        b = BenchmarkCase(case_id="B", category="c", subcategory="s", prompt="p")
        a.expected_patterns.append("x")
        assert b.expected_patterns == []


class TestAllBenchmarkCases:
    def test_non_empty(self):
        assert len(ALL_BENCHMARK_CASES) > 0

    def test_all_instances_are_benchmark_case(self):
        for case in ALL_BENCHMARK_CASES:
            assert isinstance(case, BenchmarkCase)

    def test_case_ids_are_unique(self):
        ids = [c.case_id for c in ALL_BENCHMARK_CASES]
        assert len(ids) == len(set(ids))

    def test_total_count_equals_sum_of_categories(self):
        expected_total = sum(len(v) for v in CATEGORY_MAP.values())
        assert len(ALL_BENCHMARK_CASES) == expected_total


class TestCategoryMap:
    EXPECTED_KEYS = {
        "code_generation",
        "code_fix",
        "semantic",
        "hallucination",
        "latency",
        "quality",
        "reasoning",
    }

    def test_has_seven_keys(self):
        assert len(CATEGORY_MAP) == 7

    def test_keys_match_expected(self):
        assert set(CATEGORY_MAP.keys()) == self.EXPECTED_KEYS

    def test_each_list_non_empty(self):
        for key, cases in CATEGORY_MAP.items():
            assert len(cases) > 0, f"CATEGORY_MAP['{key}'] is empty"

    def test_each_list_contains_benchmark_cases(self):
        for key, cases in CATEGORY_MAP.items():
            for case in cases:
                assert isinstance(case, BenchmarkCase)

    def test_category_field_matches_key(self):
        for key, cases in CATEGORY_MAP.items():
            for case in cases:
                assert case.category == key


class TestCodeGenCases:
    def test_non_empty(self):
        assert len(CODE_GEN_CASES) > 0

    def test_all_code_gen_category(self):
        for case in CODE_GEN_CASES:
            assert case.category == "code_generation"

    def test_each_case_has_required_fields(self):
        for case in CODE_GEN_CASES:
            assert case.case_id
            assert case.prompt
            assert case.subcategory


class TestBoundaryValues:
    def test_empty_case_id(self):
        case = BenchmarkCase(case_id="", category="c", subcategory="s", prompt="p")
        assert case.case_id == ""

    def test_empty_prompt(self):
        case = BenchmarkCase(case_id="id", category="c", subcategory="s", prompt="")
        assert case.prompt == ""

    def test_zero_max_tokens(self):
        case = BenchmarkCase(case_id="id", category="c", subcategory="s", prompt="p", max_tokens=0)
        assert case.max_tokens == 0

    def test_zero_weight(self):
        case = BenchmarkCase(case_id="id", category="c", subcategory="s", prompt="p", weight=0.0)
        assert case.weight == 0.0

    def test_negative_weight(self):
        case = BenchmarkCase(case_id="id", category="c", subcategory="s", prompt="p", weight=-1.0)
        assert case.weight == -1.0

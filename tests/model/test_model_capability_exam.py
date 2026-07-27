# [A_test] module_id: MOD-GOV_model_capability_exam | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-036 | docs/03_modules/_cross_layer/model_capability_exam/blueprint.md | §test
# [MODULE] zephyr.ex_core.src.zephyr
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ImportError->skip_module;AttributeError->skip_test
# [TESTS] test_model_capability_exam.py
# [TTL] task_bound

from __future__ import annotations

import pytest

cp_mod = pytest.importorskip("zephyr.intelligence.model_profiling.capability_passport")
tc_mod = pytest.importorskip("zephyr.intelligence.model_profiling.exam_test_cases")
eo_mod = pytest.importorskip("zephyr.intelligence.model_profiling.exam_orchestrator")
ec_mod = pytest.importorskip("zephyr.intelligence.model_profiling.exam_checks")

CapabilityPassport = cp_mod.CapabilityPassport
BreadthResult = cp_mod.BreadthResult
DepthResult = cp_mod.DepthResult
DepthCapabilityResult = cp_mod.DepthCapabilityResult
SpeedResult = cp_mod.SpeedResult
HallucinationResult = cp_mod.HallucinationResult
DriftResult = cp_mod.DriftResult
Recommendations = cp_mod.Recommendations
compute_grade = cp_mod.compute_grade
DEPTH_THRESHOLDS = cp_mod.DEPTH_THRESHOLDS

ExamTestCase = tc_mod.ExamTestCase
Difficulty = tc_mod.Difficulty
ALL_EXAM_CASES = tc_mod.ALL_EXAM_CASES
CASES_BY_CAPABILITY = tc_mod.CASES_BY_CAPABILITY

ExamOrchestrator = eo_mod.ExamOrchestrator

# Stage 4 公共化：从 exam_checks 直接调用纯函数（替代 ExamOrchestrator._xxx）
check_structure = ec_mod.check_structure
check_refusal = ec_mod.check_refusal
outputs_similar = ec_mod.outputs_similar


class TestCapabilityPassport:
    def test_creation_defaults(self):
        passport = CapabilityPassport(model_id="test-model")
        assert passport.model_id == "test-model"
        assert passport.overall_grade == "F"
        assert passport.overall_score == 0.0
        assert passport.passport_version == "1.0.0"

    def test_to_dict(self):
        passport = CapabilityPassport(model_id="test-model")
        d = passport.to_dict()
        assert isinstance(d, dict)
        assert d["model_id"] == "test-model"
        assert "breadth" in d
        assert "depth" in d

    def test_save_and_load(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cp_mod, "PASSPORTS_DIR", tmp_path)
        passport = CapabilityPassport(model_id="test-model:v1")
        passport.overall_grade = "B"
        passport.overall_score = 0.72
        saved_path = passport.save()
        assert saved_path.exists()

        loaded = CapabilityPassport.load("test-model:v1")
        assert loaded is not None
        assert loaded.model_id == "test-model:v1"
        assert loaded.overall_grade == "B"

    def test_load_nonexistent(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cp_mod, "PASSPORTS_DIR", tmp_path)
        result = CapabilityPassport.load("nonexistent-model")
        assert result is None

    def test_list_all_empty(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cp_mod, "PASSPORTS_DIR", tmp_path)
        result = CapabilityPassport.list_all()
        assert result == []

    def test_list_all_with_passports(self, tmp_path, monkeypatch):
        monkeypatch.setattr(cp_mod, "PASSPORTS_DIR", tmp_path)
        p1 = CapabilityPassport(model_id="model-a")
        p1.save()
        p2 = CapabilityPassport(model_id="model-b")
        p2.save()
        result = CapabilityPassport.list_all()
        assert len(result) >= 2

    def test_from_dict_roundtrip(self):
        passport = CapabilityPassport(
            model_id="roundtrip-test",
            overall_grade="A",
            overall_score=0.88,
            breadth=BreadthResult(score=0.9, passed=8, total=9),
        )
        d = passport.to_dict()
        restored = CapabilityPassport._from_dict(d)
        assert restored.model_id == "roundtrip-test"
        assert restored.overall_grade == "A"
        assert restored.overall_score == 0.88


class TestComputeGrade:
    def test_a_plus(self):
        assert compute_grade(0.95) == "A+"

    def test_a(self):
        assert compute_grade(0.87) == "A"

    def test_a_minus(self):
        assert compute_grade(0.82) == "A-"

    def test_b_plus(self):
        assert compute_grade(0.77) == "B+"

    def test_b(self):
        assert compute_grade(0.72) == "B"

    def test_b_minus(self):
        assert compute_grade(0.67) == "B-"

    def test_c_plus(self):
        assert compute_grade(0.62) == "C+"

    def test_c(self):
        assert compute_grade(0.57) == "C"

    def test_c_minus(self):
        assert compute_grade(0.52) == "C-"

    def test_d(self):
        assert compute_grade(0.45) == "D"

    def test_f(self):
        assert compute_grade(0.30) == "F"

    def test_boundary_zero(self):
        assert compute_grade(0.0) == "F"

    def test_boundary_one(self):
        assert compute_grade(1.0) == "A+"


class TestExamTestCase:
    def test_creation(self):
        case = ExamTestCase(
            case_id="TEST-001",
            capability="task_classification",
            difficulty=Difficulty.EASY,
            prompt="classify this",
            expected_structure_keys=["category"],
            expected_category="other",
        )
        assert case.case_id == "TEST-001"
        assert case.capability == "task_classification"
        assert case.difficulty == Difficulty.EASY

    def test_difficulty_enum(self):
        assert Difficulty.EASY.value == "easy"
        assert Difficulty.MEDIUM.value == "medium"
        assert Difficulty.HARD.value == "hard"


class TestAllExamCases:
    def test_all_exam_cases_not_empty(self):
        assert len(ALL_EXAM_CASES) > 0

    def test_cases_by_capability(self):
        assert len(CASES_BY_CAPABILITY) > 0
        for cap_name, cases in CASES_BY_CAPABILITY.items():
            assert len(cases) > 0
            for case in cases:
                assert case.capability == cap_name

    def test_all_cases_have_ids(self):
        ids = [c.case_id for c in ALL_EXAM_CASES]
        assert len(ids) == len(set(ids))

    def test_depth_thresholds_match_capabilities(self):
        for cap_name in CASES_BY_CAPABILITY:
            assert cap_name in DEPTH_THRESHOLDS


class TestExamOrchestrator:
    def test_instantiation(self):
        class FakeChat:
            _model = "test-model"

            def inference(self, capability, prompt):
                return {
                    "category": "other",
                    "tags": [],
                    "points": [],
                    "names": [],
                    "needs_human": False,
                    "reason": "ok",
                    "fixes": [],
                    "changes": [],
                    "dead_sections": [],
                    "content": "",
                }

        orch = ExamOrchestrator(FakeChat(), model_id="test-model")
        assert orch.model_id == "test-model"

    def test_run_full_exam(self):
        class FakeChat:
            def inference(self, capability, prompt):
                return {
                    "category": "other",
                    "tags": ["tag1"],
                    "points": ["p1"],
                    "names": ["name1"],
                    "needs_human": False,
                    "reason": "ok",
                    "fixes": [{"old_str": "a - b", "new_str": "a + b"}],
                    "changes": [{"old_str": "x = 10", "new_str": "X = 10"}],
                    "dead_sections": [{"old_str": "import json"}],
                    "content": "def is_prime(n): return True",
                }

        orch = ExamOrchestrator(FakeChat(), model_id="fake-model")
        passport = orch.run_full_exam(skip_drift=True)
        assert isinstance(passport, CapabilityPassport)
        assert passport.model_id == "fake-model"
        assert passport.overall_grade in ("A+", "A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D", "F")
        assert 0.0 <= passport.overall_score <= 1.0
        assert passport.exam_duration_seconds >= 0

    def test_check_structure_valid(self):
        result = {"category": "web", "tags": ["api"]}
        assert check_structure(result, ["category"]) is True

    def test_check_structure_missing_key(self):
        result = {"category": "web"}
        assert check_structure(result, ["tags"]) is False

    def test_check_structure_empty_list(self):
        result = {"tags": []}
        assert check_structure(result, ["tags"]) is False

    def test_check_structure_empty_string(self):
        result = {"name": "  "}
        assert check_structure(result, ["name"]) is False

    def test_check_structure_none_dict(self):
        assert check_structure(None, ["key"]) is False
        assert check_structure({}, ["key"]) is False

    def test_check_refusal(self):
        assert check_refusal({"error": "I cannot do that"}) is True
        assert check_refusal({"error": "ok"}) is False
        assert check_refusal({}) is True
        assert check_refusal(None) is True

    def test_outputs_similar_identical(self):
        a = {"key": "value"}
        b = {"key": "value"}
        assert outputs_similar(a, b) is True

    def test_outputs_similar_different(self):
        a = {"key": "completely different content xyz"}
        b = {"key": "totally unrelated output abc"}
        assert outputs_similar(a, b) is False

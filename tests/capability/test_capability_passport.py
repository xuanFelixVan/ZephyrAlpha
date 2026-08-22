# [A_test] module_id: MOD-GOV_capability_passport | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-034 | docs/03_modules/_cross_layer/model_profiler/blueprint.md | §3
# [MODULE] tests.test_capability_passport
# [INVARIANTS] CapabilityPassport数据模型;compute_grade分级;DEPTH_THRESHOLDS键覆盖
# [MODIFY-GUARD] src/zephyr/pipeline/model-profiler/capability_passport.py
# [CONSUMERS] MOD-INF-034
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest.AssertionError
# [TESTS] tests/test_capability_passport.py
# [TTL] task_bound

from __future__ import annotations

import pytest

from zephyr.intelligence.model_profiling.capability_passport import (
    DEPTH_THRESHOLDS,
    PASSPORTS_DIR,
    QUICK_PROFILES_DIR,
    BreadthResult,
    CapabilityPassport,
    DepthCapabilityResult,
    DepthResult,
    DriftResult,
    HallucinationBreakdown,
    HallucinationResult,
    JobRecommendation,
    QuickProfile,
    Recommendations,
    SpeedResult,
    compute_grade,
)


class TestBreadthResultDefaults:
    def test_score_default(self):
        r = BreadthResult()
        assert r.score == 0.0

    def test_passed_default(self):
        r = BreadthResult()
        assert r.passed == 0

    def test_total_default(self):
        r = BreadthResult()
        assert r.total == 0

    def test_failed_capabilities_default(self):
        r = BreadthResult()
        assert r.failed_capabilities == []


class TestDepthCapabilityResultDefaults:
    def test_pass_default(self):
        r = DepthCapabilityResult()
        assert r.pass_ is False

    def test_grade_default(self):
        r = DepthCapabilityResult()
        assert r.grade == "F"

    def test_precision_default(self):
        r = DepthCapabilityResult()
        assert r.precision == 0.0

    def test_recall_default(self):
        r = DepthCapabilityResult()
        assert r.recall == 0.0

    def test_f1_default(self):
        r = DepthCapabilityResult()
        assert r.f1 == 0.0

    def test_edit_distance_avg_default(self):
        r = DepthCapabilityResult()
        assert r.edit_distance_avg == 0.0

    def test_exact_match_rate_default(self):
        r = DepthCapabilityResult()
        assert r.exact_match_rate == 0.0

    def test_samples_tested_default(self):
        r = DepthCapabilityResult()
        assert r.samples_tested == 0

    def test_failure_reason_default(self):
        r = DepthCapabilityResult()
        assert r.failure_reason == ""


class TestComputeGrade:
    @pytest.mark.parametrize(
        "score,expected",
        [
            (0.90, "A+"),
            (0.95, "A+"),
            (1.0, "A+"),
            (0.85, "A"),
            (0.89, "A"),
            (0.80, "A-"),
            (0.84, "A-"),
            (0.75, "B+"),
            (0.79, "B+"),
            (0.70, "B"),
            (0.74, "B"),
            (0.65, "B-"),
            (0.69, "B-"),
            (0.60, "C+"),
            (0.64, "C+"),
            (0.55, "C"),
            (0.59, "C"),
            (0.50, "C-"),
            (0.54, "C-"),
            (0.40, "D"),
            (0.49, "D"),
            (0.39, "F"),
            (0.0, "F"),
        ],
    )
    def test_grade_boundaries(self, score, expected):
        assert compute_grade(score) == expected

    def test_score_zero(self):
        assert compute_grade(0.0) == "F"

    def test_score_one(self):
        assert compute_grade(1.0) == "A+"

    def test_just_below_thresholds(self):
        assert compute_grade(0.899) == "A"
        assert compute_grade(0.849) == "A-"
        assert compute_grade(0.799) == "B+"
        assert compute_grade(0.749) == "B"
        assert compute_grade(0.699) == "B-"
        assert compute_grade(0.649) == "C+"
        assert compute_grade(0.599) == "C"
        assert compute_grade(0.549) == "C-"
        assert compute_grade(0.499) == "D"
        assert compute_grade(0.399) == "F"

    def test_negative_score(self):
        assert compute_grade(-1.0) == "F"

    def test_very_high_score(self):
        assert compute_grade(100.0) == "A+"


class TestDepthThresholds:
    # v3.0.5: 关键能力子集（不硬等全量 28 个，仅断言核心能力存在）
    EXPECTED_KEYS = {
        "task_classification",
        "tag_completion",
        "summary_extraction",
        "naming_suggest",
        "anomaly_triage",
        "code_fix",
        "code_edit_precision",
        "refactor",
        "code_generate",
        "dead_code_removal",
    }

    def test_has_at_least_nine_keys(self):
        assert len(DEPTH_THRESHOLDS) >= 9

    def test_keys_match_expected(self):
        assert self.EXPECTED_KEYS <= set(DEPTH_THRESHOLDS.keys())

    def test_all_values_are_float(self):
        for k, v in DEPTH_THRESHOLDS.items():
            assert isinstance(v, float), f"{k} threshold is not float"

    def test_all_values_in_valid_range(self):
        for k, v in DEPTH_THRESHOLDS.items():
            assert 0.0 < v <= 1.0, f"{k} threshold {v} out of range"


class TestCapabilityPassportConstruction:
    def test_default_construction(self):
        p = CapabilityPassport()
        assert p.passport_version == "1.0.0"
        assert p.model_id == ""
        assert p.exam_timestamp == ""
        assert p.exam_duration_seconds == 0.0
        assert p.git_commit == ""
        assert p.overall_grade == "F"
        assert p.overall_score == 0.0
        assert isinstance(p.breadth, BreadthResult)
        assert isinstance(p.depth, DepthResult)
        assert isinstance(p.speed, SpeedResult)
        assert isinstance(p.hallucination, HallucinationResult)
        assert isinstance(p.drift, DriftResult)
        assert isinstance(p.recommendations, Recommendations)

    def test_full_construction(self):
        p = CapabilityPassport(
            passport_version="2.0.0",
            model_id="test-model:v2",
            exam_timestamp="2026-01-01T00:00:00Z",
            exam_duration_seconds=120.5,
            git_commit="abc123",
            overall_grade="A",
            overall_score=0.88,
            breadth=BreadthResult(score=0.75, passed=6, total=9),
            depth=DepthResult(overall_score=0.82),
            speed=SpeedResult(avg_latency_ms=150.0),
            hallucination=HallucinationResult(overall_rate=0.05),
            drift=DriftResult(tested=True, stable=True),
            recommendations=Recommendations(max_concurrent_tasks=8),
        )
        assert p.passport_version == "2.0.0"
        assert p.model_id == "test-model:v2"
        assert p.overall_score == 0.88
        assert p.breadth.score == 0.75
        assert p.depth.overall_score == 0.82
        assert p.speed.avg_latency_ms == 150.0
        assert p.hallucination.overall_rate == 0.05
        assert p.drift.tested is True
        assert p.recommendations.max_concurrent_tasks == 8


class TestCapabilityPassportToDict:
    def test_to_dict_contains_all_keys(self):
        p = CapabilityPassport(model_id="test", overall_score=0.5)
        d = p.to_dict()
        expected_keys = {
            "passport_version",
            "model_id",
            "exam_timestamp",
            "exam_duration_seconds",
            "git_commit",
            "overall_grade",
            "overall_score",
            "breadth",
            "depth",
            "speed",
            "hallucination",
            "drift",
            "recommendations",
        }
        assert expected_keys.issubset(set(d.keys()))

    def test_to_dict_depth_capabilities(self):
        cap = DepthCapabilityResult(pass_=True, grade="B", precision=0.7)
        p = CapabilityPassport(
            model_id="m",
            depth=DepthResult(capabilities={"code_fix": cap}),
        )
        d = p.to_dict()
        assert "code_fix" in d["depth"]["capabilities"]
        assert d["depth"]["capabilities"]["code_fix"]["grade"] == "B"


class TestCapabilityPassportSaveLoad:
    def test_save_and_load_roundtrip(self, tmp_path, monkeypatch):
        import zephyr.intelligence.model_profiling.capability_passport as cp_module

        monkeypatch.setattr(cp_module, "PASSPORTS_DIR", tmp_path)

        cap = DepthCapabilityResult(pass_=True, grade="A-", precision=0.82, f1=0.81)
        passport = CapabilityPassport(
            model_id="test-model:latest",
            overall_grade="A-",
            overall_score=0.82,
            breadth=BreadthResult(score=0.78, passed=7, total=9),
            depth=DepthResult(overall_score=0.81, capabilities={"code_fix": cap}),
            speed=SpeedResult(avg_latency_ms=100.0),
            hallucination=HallucinationResult(overall_rate=0.03),
            drift=DriftResult(tested=True, stable=True),
            recommendations=Recommendations(safe_capabilities=["code_fix"]),
        )

        saved_path = passport.save()
        assert saved_path.exists()
        assert saved_path.name == "test-model_latest.json"

        loaded = CapabilityPassport.load("test-model:latest")
        assert loaded is not None
        assert loaded.model_id == "test-model:latest"
        assert loaded.overall_score == 0.82
        assert loaded.overall_grade == "A-"

    def test_load_returns_none_for_nonexistent(self, tmp_path, monkeypatch):
        import zephyr.intelligence.model_profiling.capability_passport as cp_module

        monkeypatch.setattr(cp_module, "PASSPORTS_DIR", tmp_path)
        assert CapabilityPassport.load("nonexistent") is None

    def test_save_sanitizes_model_id(self, tmp_path, monkeypatch):
        import zephyr.intelligence.model_profiling.capability_passport as cp_module

        monkeypatch.setattr(cp_module, "PASSPORTS_DIR", tmp_path)

        passport = CapabilityPassport(model_id="org/model:tag")
        saved_path = passport.save()
        assert saved_path.name == "org_model_tag.json"


class TestListAll:
    """#255④ 回归——list_all 以护照内 model_id 字段为唯一真源（2026-08-22）。

    契约：文件名是 `:`/`/`→`_` 的有损安全编码，不可反推；下划线原名模型
    （qwen2.5-coder_14b 族）必须原样返回不得错转冒号；损坏/缺字段护照
    warning 跳过不中断批量加载。
    """

    def test_list_all_underscore_model_id_not_mangled(self, tmp_path, monkeypatch):
        """下划线原名（qwen2.5-coder_14b）返回原名——旧实现错转 qwen2.5-coder:14b。"""
        import zephyr.intelligence.model_profiling.capability_passport as cp_module

        monkeypatch.setattr(cp_module, "PASSPORTS_DIR", tmp_path)
        CapabilityPassport(model_id="qwen2.5-coder_14b").save()
        CapabilityPassport(model_id="qwen3-coder_30b").save()
        assert sorted(CapabilityPassport.list_all()) == ["qwen2.5-coder_14b", "qwen3-coder_30b"]

    def test_list_all_colon_model_id_preserved(self, tmp_path, monkeypatch):
        """冒号原名（qwen3:8b）落盘 qwen3_8b.json，返回冒号原名。"""
        import zephyr.intelligence.model_profiling.capability_passport as cp_module

        monkeypatch.setattr(cp_module, "PASSPORTS_DIR", tmp_path)
        CapabilityPassport(model_id="qwen3:8b").save()
        assert CapabilityPassport.list_all() == ["qwen3:8b"]

    def test_list_all_roundtrip_into_task_gate(self, tmp_path, monkeypatch):
        """端到端：list_all 键 → TaskGate.load_passports → can_dispatch 原名查询命中。"""
        import zephyr.intelligence.model_profiling.capability_passport as cp_module

        monkeypatch.setattr(cp_module, "PASSPORTS_DIR", tmp_path)
        cap = DepthCapabilityResult(pass_=True, grade="A", precision=0.9, f1=0.9)
        CapabilityPassport(
            model_id="qwen2.5-coder_14b",
            depth=DepthResult(overall_score=0.9, capabilities={"code_fix": cap}),
        ).save()

        from zephyr.trading.task_gate import TaskGate

        gate = TaskGate()
        assert gate.load_passports() == 1
        ok, reason = gate.can_dispatch("qwen2.5-coder_14b", "code_fix")
        assert (ok, reason) == (True, "ok")

    def test_list_all_skips_corrupt_json(self, tmp_path, monkeypatch):
        """损坏 JSON warning 跳过，不中断其余护照枚举。"""
        import zephyr.intelligence.model_profiling.capability_passport as cp_module

        monkeypatch.setattr(cp_module, "PASSPORTS_DIR", tmp_path)
        CapabilityPassport(model_id="good-model").save()
        (tmp_path / "corrupt.json").write_text("{not json", encoding="utf-8")
        assert CapabilityPassport.list_all() == ["good-model"]

    def test_list_all_skips_missing_model_id(self, tmp_path, monkeypatch):
        """缺 model_id 字段护照 warning 跳过。"""
        import json

        import zephyr.intelligence.model_profiling.capability_passport as cp_module

        monkeypatch.setattr(cp_module, "PASSPORTS_DIR", tmp_path)
        CapabilityPassport(model_id="good-model").save()
        (tmp_path / "legacy.json").write_text(
            json.dumps({"overall_grade": "A"}), encoding="utf-8"
        )
        assert CapabilityPassport.list_all() == ["good-model"]

    def test_list_all_missing_dir(self, tmp_path, monkeypatch):
        import zephyr.intelligence.model_profiling.capability_passport as cp_module

        monkeypatch.setattr(cp_module, "PASSPORTS_DIR", tmp_path / "nonexistent")
        assert CapabilityPassport.list_all() == []


class TestPassportsDir:
    def test_passports_dir_is_path(self):
        from pathlib import Path

        assert isinstance(PASSPORTS_DIR, Path)

    def test_passports_dir_contains_data_brain_passports(self):
        assert "data" in str(PASSPORTS_DIR)
        assert "passports" in str(PASSPORTS_DIR)


class TestQuickProfileSaveLoad:
    """QuickProfile 持久化测试 (ROADMAP-03: 第一个真实护照)。"""

    def test_save_and_load_roundtrip(self, tmp_path, monkeypatch):
        import zephyr.intelligence.model_profiling.capability_passport as cp_module

        monkeypatch.setattr(cp_module, "QUICK_PROFILES_DIR", tmp_path)

        profile = QuickProfile(
            model_id="qwen3:8b",
            exam_mode="quick",
            overall_grade="B",
            overall_score=0.72,
            capability_grades={"refactor": "A", "code_fix": "B"},
            capability_scores={"refactor": 1.0, "code_fix": 0.65},
            hallucination=HallucinationBreakdown(fabrication=0.0, inconsistency=0.1),
            recommendations=[
                JobRecommendation(
                    job_id="rule_gatekeeper",
                    job_title="rule_gatekeeper",
                    match_score=0.88,
                    qualified=True,
                    hallucination_passed=True,
                ),
            ],
        )

        saved_path = profile.save()
        assert saved_path.exists()
        assert saved_path.name == "qwen3_8b.json"

        loaded = QuickProfile.load("qwen3:8b")
        assert loaded is not None
        assert loaded.model_id == "qwen3:8b"
        assert loaded.overall_score == 0.72
        assert loaded.overall_grade == "B"
        assert loaded.capability_grades["refactor"] == "A"
        assert loaded.hallucination.inconsistency == 0.1
        assert len(loaded.recommendations) == 1
        assert loaded.recommendations[0].job_title == "rule_gatekeeper"

    def test_load_returns_none_for_nonexistent(self, tmp_path, monkeypatch):
        import zephyr.intelligence.model_profiling.capability_passport as cp_module

        monkeypatch.setattr(cp_module, "QUICK_PROFILES_DIR", tmp_path)
        assert QuickProfile.load("nonexistent-model") is None

    def test_save_sanitizes_model_id(self, tmp_path, monkeypatch):
        import zephyr.intelligence.model_profiling.capability_passport as cp_module

        monkeypatch.setattr(cp_module, "QUICK_PROFILES_DIR", tmp_path)

        profile = QuickProfile(model_id="org/model:tag")
        saved_path = profile.save()
        assert saved_path.name == "org_model_tag.json"

    def test_quick_profiles_dir_is_path(self):
        from pathlib import Path

        assert isinstance(QUICK_PROFILES_DIR, Path)
        assert "quick_profiles" in str(QUICK_PROFILES_DIR)

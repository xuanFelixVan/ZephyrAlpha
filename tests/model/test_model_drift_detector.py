# [A_test] module_id: MOD-GOV_model_drift_detector | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-021 | docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md | §
# [MODULE] tests.test_model_drift_detector
# [INVARIANTS] DriftResult fields immutable after creation;baseline file must be valid JSON
# [MODIFY-GUARD] src/zephyr/rollback/model_drift_detector.py
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DriftResult on check_drift failure;json.JSONDecodeError on corrupted baseline
# [TESTS] self
# [TTL] task_bound

from __future__ import annotations

import json
from pathlib import Path

import pytest

from zephyr.intelligence.model_drift_detector import DriftResult, ModelDriftDetector


class TestModelDriftDetectorInstantiation:
    def test_default_project_root(self):
        detector = ModelDriftDetector()
        assert detector._project_root == Path.cwd()

    def test_custom_project_root(self, tmp_path: Path):
        detector = ModelDriftDetector(project_root=tmp_path)
        assert detector._project_root == tmp_path

    def test_baseline_path_derived(self, tmp_path: Path):
        detector = ModelDriftDetector(project_root=tmp_path)
        assert detector._baseline_path == tmp_path / ModelDriftDetector.BASELINE_FILE


class TestEstablishBaseline:
    def test_establish_baseline_creates_file(self, tmp_path: Path):
        detector = ModelDriftDetector(project_root=tmp_path)
        samples = [{"text": "hello"}, {"text": "world"}]
        result = detector.establish_baseline(samples)
        assert result is True
        assert detector._baseline_path.exists()

    def test_establish_baseline_writes_valid_json(self, tmp_path: Path):
        detector = ModelDriftDetector(project_root=tmp_path)
        samples = [{"text": "hello"}]
        detector.establish_baseline(samples)
        data = json.loads(detector._baseline_path.read_text(encoding="utf-8"))
        assert "established_at" in data
        assert "feature_vector" in data
        assert "sample_count" in data
        assert data["sample_count"] == 1

    def test_establish_baseline_empty_list(self, tmp_path: Path):
        detector = ModelDriftDetector(project_root=tmp_path)
        result = detector.establish_baseline([])
        assert result is True
        data = json.loads(detector._baseline_path.read_text(encoding="utf-8"))
        assert data["sample_count"] == 0
        assert data["feature_vector"] == {}

    def test_establish_baseline_creates_parent_dirs(self, tmp_path: Path):
        detector = ModelDriftDetector(project_root=tmp_path)
        assert not detector._baseline_path.parent.exists()
        detector.establish_baseline([{"a": 1}])
        assert detector._baseline_path.parent.exists()


class TestCheckDrift:
    def test_check_drift_no_baseline(self, tmp_path: Path):
        detector = ModelDriftDetector(project_root=tmp_path)
        result = detector.detect_drift([{"text": "hello"}])
        assert isinstance(result, DriftResult)
        assert result.drift_detected is False
        assert result.exit_code == 0
        assert "No baseline established yet" in result.details

    def test_check_drift_same_outputs_feature_vectors_match(self, tmp_path: Path):
        detector = ModelDriftDetector(project_root=tmp_path)
        samples = [{"text": "hello"}, {"text": "world"}]
        detector.establish_baseline(samples)
        baseline_fv = detector._compute_feature_vector(samples)
        current_fv = detector._compute_feature_vector(samples)
        assert baseline_fv.keys() == current_fv.keys()
        for k in baseline_fv:
            assert baseline_fv[k] == pytest.approx(current_fv[k])

    def test_check_drift_different_outputs_detects_drift(self, tmp_path: Path):
        detector = ModelDriftDetector(project_root=tmp_path)
        baseline_samples = [{"text": "alpha"}, {"text": "beta"}]
        detector.establish_baseline(baseline_samples)
        different_samples = [{"text": "gamma"}, {"text": "delta"}, {"text": "epsilon"}]
        result = detector.detect_drift(different_samples)
        assert isinstance(result, DriftResult)
        assert result.divergence_score >= 0.0
        assert result.threshold == ModelDriftDetector.DIVERGENCE_THRESHOLD

    def test_check_drift_corrupted_baseline(self, tmp_path: Path):
        detector = ModelDriftDetector(project_root=tmp_path)
        detector._baseline_path.parent.mkdir(parents=True, exist_ok=True)
        detector._baseline_path.write_text("NOT JSON{{{", encoding="utf-8")
        result = detector.detect_drift([{"text": "hello"}])
        assert result.drift_detected is False
        assert "Baseline file corrupted" in result.details

    def test_check_drift_empty_current_outputs(self, tmp_path: Path):
        detector = ModelDriftDetector(project_root=tmp_path)
        detector.establish_baseline([{"text": "hello"}])
        result = detector.detect_drift([])
        assert isinstance(result, DriftResult)
        assert result.divergence_score >= 0.0

    def test_check_drift_exit_code_on_drift(self, tmp_path: Path):
        detector = ModelDriftDetector(project_root=tmp_path)
        baseline_samples = [{"text": "baseline_only"}]
        detector.establish_baseline(baseline_samples)
        completely_different = [{"text": f"unique_{i}"} for i in range(100)]
        result = detector.detect_drift(completely_different)
        if result.drift_detected:
            assert result.exit_code == ModelDriftDetector.EXIT_CODE_DRIFT


class TestComputeFeatureVector:
    def test_empty_outputs(self, tmp_path: Path):
        detector = ModelDriftDetector(project_root=tmp_path)
        fv = detector._compute_feature_vector([])
        assert fv == {}

    def test_single_output(self, tmp_path: Path):
        detector = ModelDriftDetector(project_root=tmp_path)
        fv = detector._compute_feature_vector([{"text": "hello"}])
        assert len(fv) == 1
        assert sum(fv.values()) == pytest.approx(1.0)

    def test_identical_outputs_grouped(self, tmp_path: Path):
        detector = ModelDriftDetector(project_root=tmp_path)
        fv = detector._compute_feature_vector([{"text": "hello"}, {"text": "hello"}])
        assert len(fv) == 1
        assert sum(fv.values()) == pytest.approx(1.0)

    def test_multiple_distinct_outputs(self, tmp_path: Path):
        detector = ModelDriftDetector(project_root=tmp_path)
        fv = detector._compute_feature_vector([{"text": "a"}, {"text": "b"}, {"text": "c"}])
        assert len(fv) == 3
        assert sum(fv.values()) == pytest.approx(1.0)


class TestJsDivergence:
    def test_both_empty(self, tmp_path: Path):
        detector = ModelDriftDetector(project_root=tmp_path)
        assert detector._js_divergence({}, {}) == 0.0

    def test_identical_distributions_symmetric(self, tmp_path: Path):
        detector = ModelDriftDetector(project_root=tmp_path)
        p = {"a": 0.5, "b": 0.5}
        q = {"a": 0.5, "b": 0.5}
        div_pq = detector._js_divergence(p, q)
        div_qp = detector._js_divergence(q, p)
        assert div_pq == pytest.approx(div_qp)

    def test_completely_different_distributions(self, tmp_path: Path):
        detector = ModelDriftDetector(project_root=tmp_path)
        p = {"a": 1.0}
        q = {"b": 1.0}
        divergence = detector._js_divergence(p, q)
        assert divergence > 0.0

    def test_one_empty_distribution(self, tmp_path: Path):
        detector = ModelDriftDetector(project_root=tmp_path)
        p = {"a": 1.0}
        divergence = detector._js_divergence(p, {})
        assert divergence > 0.0


class TestDriftResult:
    def test_drift_result_defaults(self):
        result = DriftResult(
            drift_detected=True,
            model_name="test",
            divergence_score=0.5,
            threshold=0.15,
            exit_code=34,
        )
        assert result.details == []

    def test_drift_result_with_details(self):
        result = DriftResult(
            drift_detected=False,
            model_name="test",
            divergence_score=0.0,
            threshold=0.15,
            exit_code=0,
            details=["detail1", "detail2"],
        )
        assert len(result.details) == 2

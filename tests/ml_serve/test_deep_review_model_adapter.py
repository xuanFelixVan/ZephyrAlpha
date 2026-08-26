# [BLUEPRINT] MOD-MLS-004 | docs/03_modules/_domain_ml_serve/deep_review_model_adapter/blueprint.md | §test
# [TTL] permanent
# [A_test] module_id: MOD-MLS-004 | layer=test | stability=volatile | safety=M | ai_autonomy=human_gated
# [MODULE] tests.ml_serve.test_deep_review_model_adapter
# [TESTS] src/zephyr/ml_serve/deep_review_model_adapter.py
"""MOD-MLS-004 单元测试：deep_review_model_adapter 深度审查模型适配器。

蓝图验收（B10-02297/CAND-MLS-004，A1 D-ML-47）：
GLM-5.1 深度审查 profile 注册 + 考试校准（校准集评分分布→通过阈值标定，
注入 exam_runner）+ 审查任务 schema（审查类型词表 + findings 输出校验）。
reviewer/exam_runner/registrar 全注入内存替身，不触网。
"""

from __future__ import annotations

import datetime

import pytest

pytest.importorskip(
    "zephyr.ml_serve.deep_review_model_adapter",
    reason="deep_review_model_adapter not importable",
)

from zephyr.ml_serve.deep_review_model_adapter import (  # noqa: E402
    CalibrationSample,
    DeepReviewAdapterError,
    DeepReviewModelAdapter,
    DeepReviewProfile,
    FindingSeverity,
    ReviewTask,
    ReviewType,
)

_T0 = datetime.datetime(2026, 8, 25, 9, 30, 0)

#: 主校准集：阈值标定已知答案 0.7 / 平衡准确率 1.0
_SAMPLES = (
    CalibrationSample("s1", True),
    CalibrationSample("s2", True),
    CalibrationSample("s3", False),
    CalibrationSample("s4", False),
)
_EXAM_SCORES = {"s1": 0.9, "s2": 0.7, "s3": 0.4, "s4": 0.2}

#: 并列校准集：t=0.2 与 t=0.9 平衡准确率同为 0.75，须取更严高阈值 0.9
_TIE_SAMPLES = (
    CalibrationSample("a", True),
    CalibrationSample("b", False),
    CalibrationSample("c", True),
    CalibrationSample("d", False),
)
_TIE_SCORES = {"a": 0.9, "b": 0.8, "c": 0.2, "d": 0.1}

_RAW_OK = {
    "score": 0.85,
    "findings": [
        {
            "finding_id": "f-1",
            "severity": "major",
            "description": "订单路由缺幂等键",
            "category": "correctness",
        },
        {"finding_id": "f-2", "severity": "info", "description": "命名风格建议"},
    ],
}


def _adapter(
    *,
    reviewer=None,
    raw: dict | None = None,
    exam_scores: dict | None = None,
    registrar=None,
) -> DeepReviewModelAdapter:
    scores = _EXAM_SCORES if exam_scores is None else exam_scores
    if reviewer is None:
        reviewer = lambda task: (
            dict(raw) if raw is not None
            else {"score": _RAW_OK["score"], "findings": [dict(f) for f in _RAW_OK["findings"]]}
        )
    return DeepReviewModelAdapter(
        reviewer=reviewer,
        exam_runner=lambda model_id, samples: dict(scores),
        profile_registrar=registrar,
        clock=lambda: _T0,
    )


def _calibrated(**kw) -> DeepReviewModelAdapter:
    adapter = _adapter(**kw)
    adapter.calibrate("glm-5.1", _SAMPLES)
    return adapter


def _task(
    model_id: str = "glm-5.1",
    review_type: ReviewType = ReviewType.CODE_REVIEW,
    task_id: str = "task-1",
    subject: str = "t0_trader 执行层订单路由补丁",
) -> ReviewTask:
    return ReviewTask(
        task_id=task_id,
        model_id=model_id,
        review_type=review_type,
        subject=subject,
        submitted_at=_T0,
    )


# ──────────────────────────────────────────────────────────────────────────────
# profile 注册（model_router 挂钩）
# ──────────────────────────────────────────────────────────────────────────────


class TestProfileRegistration:
    def test_default_profile_registered(self) -> None:
        adapter = _adapter()
        profile = adapter.profile_of("glm-5.1")
        assert profile.provider == "zhipu"
        assert profile.review_types == frozenset(ReviewType)
        assert profile.context_window == 131072
        assert adapter.registered_models() == ("glm-5.1",)

    def test_register_duplicate_raises(self) -> None:
        adapter = _adapter()
        with pytest.raises(DeepReviewAdapterError):
            adapter.register_profile(DeepReviewProfile(
                model_id="glm-5.1",
                provider="zhipu",
                review_types=frozenset(ReviewType),
                context_window=131072,
            ))

    def test_register_invalid_profile_raises(self) -> None:
        with pytest.raises(DeepReviewAdapterError):
            DeepReviewProfile(
                model_id="glm-x", provider="zhipu",
                review_types=frozenset(), context_window=1024,
            )
        with pytest.raises(DeepReviewAdapterError):
            DeepReviewProfile(
                model_id="glm-x", provider="zhipu",
                review_types=frozenset(ReviewType), context_window=0,
            )

    def test_registrar_hook_receives(self) -> None:
        registered: list[DeepReviewProfile] = []
        adapter = _adapter(registrar=lambda p: registered.append(p))
        adapter.register_profile(DeepReviewProfile(
            model_id="glm-5.1-mini", provider="zhipu",
            review_types=frozenset({ReviewType.CODE_REVIEW}), context_window=32768,
        ))
        assert [p.model_id for p in registered] == ["glm-5.1", "glm-5.1-mini"]

    def test_registrar_failure_raises(self) -> None:
        with pytest.raises(DeepReviewAdapterError):
            DeepReviewModelAdapter(
                reviewer=lambda task: dict(_RAW_OK),
                exam_runner=lambda m, s: dict(_EXAM_SCORES),
                profile_registrar=lambda p: 1 / 0,
                clock=lambda: _T0,
            )


# ──────────────────────────────────────────────────────────────────────────────
# 考试校准（评分分布 → 通过阈值标定）
# ──────────────────────────────────────────────────────────────────────────────


class TestCalibrate:
    def test_calibrate_ok(self) -> None:
        adapter = _adapter()
        result = adapter.calibrate("glm-5.1", _SAMPLES)
        assert result.threshold == pytest.approx(0.7)
        assert result.balanced_accuracy == pytest.approx(1.0)
        assert result.sample_count == 4
        assert result.calibrated_at == _T0
        assert adapter.calibration_of("glm-5.1") == result

    def test_calibrate_tie_picks_higher_threshold(self) -> None:
        adapter = _adapter(exam_scores=_TIE_SCORES)
        result = adapter.calibrate("glm-5.1", _TIE_SAMPLES)
        assert result.threshold == pytest.approx(0.9)  # 并列取更严
        assert result.balanced_accuracy == pytest.approx(0.75)

    def test_calibrate_unknown_and_duplicate_raises(self) -> None:
        with pytest.raises(DeepReviewAdapterError):
            _adapter().calibrate("ghost", _SAMPLES)
        adapter = _calibrated()
        with pytest.raises(DeepReviewAdapterError):
            adapter.calibrate("glm-5.1", _SAMPLES)

    def test_calibrate_bad_sample_set_raises(self) -> None:
        with pytest.raises(DeepReviewAdapterError):
            _adapter().calibrate("glm-5.1", ())  # 空校准集
        with pytest.raises(DeepReviewAdapterError):
            _adapter().calibrate("glm-5.1", tuple(s for s in _SAMPLES if s.label))  # 全通过
        with pytest.raises(DeepReviewAdapterError):
            _adapter().calibrate("glm-5.1", tuple(s for s in _SAMPLES if not s.label))  # 全未通过

    def test_calibrate_duplicate_sample_id_raises(self) -> None:
        with pytest.raises(DeepReviewAdapterError):
            _adapter().calibrate("glm-5.1", (CalibrationSample("s1", True), CalibrationSample("s1", False)))

    def test_exam_runner_not_injected_raises(self) -> None:
        adapter = DeepReviewModelAdapter(clock=lambda: _T0)
        with pytest.raises(DeepReviewAdapterError):
            adapter.calibrate("glm-5.1", _SAMPLES)

    def test_exam_runner_exception_wrapped(self) -> None:
        def _boom(model_id: str, samples: tuple) -> dict:
            raise RuntimeError("考试服务不可用")

        adapter = DeepReviewModelAdapter(
            reviewer=lambda task: dict(_RAW_OK), exam_runner=_boom, clock=lambda: _T0,
        )
        with pytest.raises(DeepReviewAdapterError):
            adapter.calibrate("glm-5.1", _SAMPLES)

    def test_exam_score_missing_and_out_of_range_raises(self) -> None:
        with pytest.raises(DeepReviewAdapterError):
            _adapter(exam_scores={"s1": 0.9, "s2": 0.7, "s3": 0.4}).calibrate("glm-5.1", _SAMPLES)
        with pytest.raises(DeepReviewAdapterError):
            _adapter(exam_scores={"s1": 0.9, "s2": 0.7, "s3": 0.4, "s4": 1.5}).calibrate(
                "glm-5.1", _SAMPLES
            )


# ──────────────────────────────────────────────────────────────────────────────
# 审查调用（schema + findings 输出校验 + 阈值判定）
# ──────────────────────────────────────────────────────────────────────────────


class TestReview:
    def test_review_passed(self) -> None:
        adapter = _calibrated()
        report = adapter.review(_task())
        assert report.score == pytest.approx(0.85)
        assert report.passed is True  # 0.85 ≥ 校准阈值 0.7
        assert report.reviewed_at == _T0
        assert len(report.findings) == 2
        assert report.findings[0].severity is FindingSeverity.MAJOR
        assert report.findings[0].category == "correctness"
        assert report.findings[1].category == ""  # 缺省规范化
        assert adapter.report_of("task-1") == report

    def test_review_failed_below_threshold(self) -> None:
        adapter = _calibrated(raw={"score": 0.5, "findings": []})
        report = adapter.review(_task())
        assert report.passed is False  # 0.5 < 0.7
        assert report.findings == ()

    def test_review_before_calibrate_raises(self) -> None:
        with pytest.raises(DeepReviewAdapterError):
            _adapter().review(_task())  # 未校准不得审查

    def test_review_unknown_model_raises(self) -> None:
        with pytest.raises(DeepReviewAdapterError):
            _calibrated().review(_task(model_id="ghost"))

    def test_review_type_not_supported_raises(self) -> None:
        adapter = _calibrated()
        adapter.register_profile(DeepReviewProfile(
            model_id="glm-5.1-mini", provider="zhipu",
            review_types=frozenset({ReviewType.CODE_REVIEW}), context_window=32768,
        ))
        adapter.calibrate("glm-5.1-mini", _SAMPLES)
        with pytest.raises(DeepReviewAdapterError):
            adapter.review(_task(model_id="glm-5.1-mini", review_type=ReviewType.RISK_REVIEW))

    def test_empty_task_id_and_subject_raises(self) -> None:
        adapter = _calibrated()
        with pytest.raises(DeepReviewAdapterError):
            adapter.review(_task(task_id=""))
        with pytest.raises(DeepReviewAdapterError):
            adapter.review(_task(subject=""))

    def test_duplicate_task_id_raises(self) -> None:
        adapter = _calibrated()
        adapter.review(_task())
        with pytest.raises(DeepReviewAdapterError):
            adapter.review(_task())

    def test_reviewer_not_injected_raises(self) -> None:
        adapter = DeepReviewModelAdapter(
            exam_runner=lambda m, s: dict(_EXAM_SCORES), clock=lambda: _T0,
        )
        adapter.calibrate("glm-5.1", _SAMPLES)
        with pytest.raises(DeepReviewAdapterError):
            adapter.review(_task())

    def test_reviewer_exception_wrapped(self) -> None:
        def _boom(task: ReviewTask) -> dict:
            raise RuntimeError("审查服务超时")

        with pytest.raises(DeepReviewAdapterError):
            _calibrated(reviewer=_boom).review(_task())

    def test_findings_invalid_raises(self) -> None:
        with pytest.raises(DeepReviewAdapterError):  # severity 越词表
            _calibrated(raw={
                "score": 0.9,
                "findings": [{"finding_id": "f-1", "severity": "fatal", "description": "x"}],
            }).review(_task())
        with pytest.raises(DeepReviewAdapterError):  # description 缺失
            _calibrated(raw={
                "score": 0.9,
                "findings": [{"finding_id": "f-1", "severity": "info"}],
            }).review(_task())


# ──────────────────────────────────────────────────────────────────────────────
# 查询 / 确定性
# ──────────────────────────────────────────────────────────────────────────────


class TestQuery:
    def test_report_of_unknown_raises(self) -> None:
        adapter = _calibrated()
        with pytest.raises(DeepReviewAdapterError):
            adapter.report_of("ghost")
        with pytest.raises(DeepReviewAdapterError):
            _adapter().calibration_of("glm-5.1")  # 未校准

    def test_determinism(self) -> None:
        def _script() -> tuple:
            adapter = _calibrated()
            report = adapter.review(_task())
            return (adapter.calibration_of("glm-5.1"), report)

        assert _script() == _script()  # 同输入必同输出

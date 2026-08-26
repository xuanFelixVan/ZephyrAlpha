# [BLUEPRINT] MOD-MLS-004 | docs/03_modules/_domain_ml_serve/deep_review_model_adapter/blueprint.md
# [MODULE] zephyr.ml_serve.deep_review_model_adapter
# [DOMAIN] D_ML_SERVE
# [DEPENDENCIES] 无（适配核心纯内存；reviewer/exam_runner/profile_registrar/clock 全注入，不真发请求）
# [CONSUMERS] 运行时装配批（model_router GLM-5.1 profile 装配 / 考试校准与阈值标定 / 深度审查调用适配）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 审查类型词表闭合(code_review|strategy_review|risk_review|compliance_review); findings严重度词表闭合(info|minor|major|critical); profile不可变且model_id唯一; 校准集须含通过/未通过双标签且样本id唯一; 阈值=平衡准确率最优(并列取更严高阈值); 重复校准拒绝; 未校准模型审查Fail-Closed; reviewer/exam_runner未注入Fail-Closed不真发; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_ml_serve/deep_review_model_adapter/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] DeepReviewAdapterError(占位 ZA-MLS-UNREGISTERED-DEEP-REVIEW-ADAPTER)——未注册model/审查类型越词表/校准集非法/exam分数越界/findings schema缺漏/未校准审查/重复校准/client异常时抛
# [TESTS] tests/ml_serve/test_deep_review_model_adapter.py
# [A_module] module_id=MOD-MLS-004 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""DeepReviewModelAdapter — 深度审查模型适配器（MOD-MLS-004）。

B10-02297（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-MLS-004，A1 D-ML-47）：
model_router 注册 **GLM-5.1** 深度审查 profile + **考试校准**（校准集评分
分布 → 通过阈值标定，注入 exam_runner）+ **审查任务 schema**（审查类型
词表 + 结构化 findings 输出校验）。审查调用 reviewer 注入不真发。

查重分工（蓝图 §0）：model_registry（MOD-INF-039）=LLM 模型静态注册表
（本件经 profile_registrar 挂钩装配，不重建注册表）；codegen_model_
adapter（MOD-MLS-003）=DeepSeek-V4-Pro 代码生成适配（零交集，本件=深度
审查）；model_compression_accelerator（MOD-MLS-002）=压缩编排（零交集）。
"""

from __future__ import annotations

import datetime
import logging
import math
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Mapping, Sequence

_log = logging.getLogger(__name__)

__all__: Final = [
    "CalibrationResult",
    "CalibrationSample",
    "DeepReviewAdapterError",
    "DeepReviewModelAdapter",
    "DeepReviewProfile",
    "Finding",
    "FindingSeverity",
    "ReviewReport",
    "ReviewTask",
    "ReviewType",
]

#: GLM-5.1 默认上下文窗（token，A1 D-ML-47 口径）
_DEFAULT_CONTEXT_WINDOW: Final[int] = 131072


class DeepReviewAdapterError(Exception):
    """深度审查适配输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-MLS-UNREGISTERED-DEEP-REVIEW-ADAPTER。
    """


class ReviewType(str, Enum):
    """审查类型词表（闭合）。"""

    CODE_REVIEW = "code_review"
    STRATEGY_REVIEW = "strategy_review"
    RISK_REVIEW = "risk_review"
    COMPLIANCE_REVIEW = "compliance_review"


class FindingSeverity(str, Enum):
    """findings 严重度词表（闭合）。"""

    INFO = "info"
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


@dataclass(frozen=True)
class DeepReviewProfile:
    """深度审查模型 profile（审查类型能力/上下文窗，frozen）。"""

    model_id: str
    provider: str
    review_types: frozenset[ReviewType]
    context_window: int

    def __post_init__(self) -> None:
        if not self.model_id:
            raise DeepReviewAdapterError("model_id 为空")
        if not self.provider:
            raise DeepReviewAdapterError("provider 为空")
        if not self.review_types:
            raise DeepReviewAdapterError("review_types 为空（能力声明须非空）")
        for rtype in self.review_types:
            if not isinstance(rtype, ReviewType):
                raise DeepReviewAdapterError(f"非法审查类型: {rtype!r}")
        if isinstance(self.context_window, bool) or self.context_window <= 0:
            raise DeepReviewAdapterError("context_window 须为正整数")


@dataclass(frozen=True)
class CalibrationSample:
    """考试校准样本（label=True 应通过）。"""

    sample_id: str
    label: bool


@dataclass(frozen=True)
class CalibrationResult:
    """考试校准产出（通过阈值标定结果，不可变）。"""

    model_id: str
    threshold: float
    sample_count: int
    balanced_accuracy: float
    calibrated_at: datetime.datetime


@dataclass(frozen=True)
class ReviewTask:
    """审查任务 Schema（frozen）。"""

    task_id: str
    model_id: str
    review_type: ReviewType
    subject: str
    submitted_at: datetime.datetime


@dataclass(frozen=True)
class Finding:
    """结构化 finding（输出校验后产物，frozen）。"""

    finding_id: str
    severity: FindingSeverity
    description: str
    category: str


@dataclass(frozen=True)
class ReviewReport:
    """审查报告（score ≥ 校准阈值 → passed）。"""

    task_id: str
    model_id: str
    review_type: ReviewType
    score: float
    passed: bool
    findings: tuple[Finding, ...]
    reviewed_at: datetime.datetime


def _calibrate_threshold(
    scores: Mapping[str, float], samples: tuple[CalibrationSample, ...]
) -> tuple[float, float]:
    """平衡准确率最优阈值（并列取更严高阈值，Fail-Closed 语义）。"""
    positives = sum(1 for s in samples if s.label)
    negatives = len(samples) - positives
    best_threshold = -1.0
    best_balanced = -1.0
    for threshold in sorted(set(scores.values())):
        tp = sum(1 for s in samples if s.label and scores[s.sample_id] >= threshold)
        tn = sum(1 for s in samples if not s.label and scores[s.sample_id] < threshold)
        balanced = (tp / positives + tn / negatives) / 2.0
        if balanced > best_balanced or (
            balanced == best_balanced and threshold > best_threshold
        ):
            best_balanced = balanced
            best_threshold = threshold
    return best_threshold, best_balanced


class DeepReviewModelAdapter:
    """GLM-5.1 深度审查适配（profile 注册 + 考试校准 + findings 输出校验）。"""

    #: GLM-5.1 默认 profile（构造即注册；装配批可注册额外 profile）
    DEFAULT_PROFILE: Final[DeepReviewProfile] = DeepReviewProfile(
        model_id="glm-5.1",
        provider="zhipu",
        review_types=frozenset(ReviewType),
        context_window=_DEFAULT_CONTEXT_WINDOW,
    )

    def __init__(
        self,
        *,
        reviewer: Callable[[ReviewTask], Mapping[str, object]] | None = None,
        exam_runner: Callable[[str, tuple[CalibrationSample, ...]], Mapping[str, float]] | None = None,
        profile_registrar: Callable[[DeepReviewProfile], None] | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        self._reviewer = reviewer
        self._exam_runner = exam_runner
        self._registrar = profile_registrar
        self._clock = clock or datetime.datetime.now
        self._profiles: dict[str, DeepReviewProfile] = {}
        self._calibrations: dict[str, CalibrationResult] = {}
        self._reports: dict[str, ReviewReport] = {}
        self.register_profile(self.DEFAULT_PROFILE)

    # ── profile 注册 ─────────────────────────────────────────────────────

    def register_profile(self, profile: DeepReviewProfile) -> None:
        """注册深度审查 profile（model_id 唯一；registrar 挂钩失败 Fail-Closed）。"""
        if not isinstance(profile, DeepReviewProfile):
            raise DeepReviewAdapterError("profile 非法（须 DeepReviewProfile）")
        if profile.model_id in self._profiles:
            raise DeepReviewAdapterError(f"profile 重复注册: {profile.model_id!r}")
        if self._registrar is not None:
            try:
                self._registrar(profile)
            except Exception as exc:  # noqa: BLE001 — model_router 挂钩失败 Fail-Closed
                raise DeepReviewAdapterError(
                    f"profile_registrar 注册失败: {profile.model_id!r}"
                ) from exc
        self._profiles[profile.model_id] = profile
        _log.info("深度审查 profile 注册: %s (%s)", profile.model_id, profile.provider)

    # ── 考试校准（评分分布 → 通过阈值标定） ────────────────────────────────

    def calibrate(
        self, model_id: str, samples: Sequence[CalibrationSample]
    ) -> CalibrationResult:
        """考试校准：exam_runner 跑分 → 评分分布标定通过阈值（一次性，重复拒绝）。"""
        self.profile_of(model_id)
        if model_id in self._calibrations:
            raise DeepReviewAdapterError(f"重复校准拒绝: {model_id!r}（校准不可变）")
        if not samples:
            raise DeepReviewAdapterError("校准集为空")
        seen: set[str] = set()
        for sample in samples:
            if not isinstance(sample, CalibrationSample):
                raise DeepReviewAdapterError("校准样本非法（须 CalibrationSample）")
            if not sample.sample_id:
                raise DeepReviewAdapterError("校准样本 sample_id 为空")
            if sample.sample_id in seen:
                raise DeepReviewAdapterError(f"校准样本重复: {sample.sample_id!r}")
            seen.add(sample.sample_id)
        positives = sum(1 for s in samples if s.label)
        if positives == 0 or positives == len(samples):
            raise DeepReviewAdapterError("校准集须同时含通过/未通过样本（单标签不可标定）")
        if self._exam_runner is None:
            raise DeepReviewAdapterError("exam_runner 未注入（Fail-Closed 不真跑考试）")
        try:
            scores = self._exam_runner(model_id, tuple(samples))
        except Exception as exc:  # noqa: BLE001 — exam_runner 异常包装 Fail-Closed
            raise DeepReviewAdapterError(f"exam_runner 考试异常: {model_id!r}") from exc
        if not isinstance(scores, Mapping):
            raise DeepReviewAdapterError("exam_runner 产出非法（须 sample_id→score 映射）")
        clean: dict[str, float] = {}
        for sample in samples:
            score = scores.get(sample.sample_id)
            if score is None:
                raise DeepReviewAdapterError(f"exam_runner 缺样本分数: {sample.sample_id!r}")
            if isinstance(score, bool) or not isinstance(score, (int, float)):
                raise DeepReviewAdapterError(f"exam 分数非数值: {sample.sample_id!r}")
            if not math.isfinite(score) or not 0.0 <= score <= 1.0:
                raise DeepReviewAdapterError(
                    f"exam 分数越界 [0,1]: {sample.sample_id!r}={score!r}"
                )
            clean[sample.sample_id] = float(score)
        threshold, balanced = _calibrate_threshold(clean, tuple(samples))
        result = CalibrationResult(
            model_id=model_id,
            threshold=threshold,
            sample_count=len(samples),
            balanced_accuracy=balanced,
            calibrated_at=self._clock(),
        )
        self._calibrations[model_id] = result
        _log.info(
            "考试校准完成: %s 阈值=%s 平衡准确率=%s", model_id, threshold, balanced
        )
        return result

    # ── 审查调用（reviewer 注入不真发） ────────────────────────────────────

    def review(self, task: ReviewTask) -> ReviewReport:
        """审查调用：schema 校验 → reviewer → findings 输出校验 → 阈值判定。"""
        if not isinstance(task, ReviewTask):
            raise DeepReviewAdapterError("task 非法（须 ReviewTask）")
        if not task.task_id:
            raise DeepReviewAdapterError("task_id 为空")
        if task.task_id in self._reports:
            raise DeepReviewAdapterError(f"task_id 重复: {task.task_id!r}")
        profile = self.profile_of(task.model_id)
        calibration = self._calibrations.get(task.model_id)
        if calibration is None:
            raise DeepReviewAdapterError(
                f"未校准模型不得审查: {task.model_id!r}（Fail-Closed）"
            )
        if not isinstance(task.review_type, ReviewType):
            raise DeepReviewAdapterError(f"非法审查类型: {task.review_type!r}")
        if task.review_type not in profile.review_types:
            raise DeepReviewAdapterError(
                f"审查类型越界: {task.review_type.value} 未在 {profile.model_id} profile 声明中"
            )
        if not task.subject:
            raise DeepReviewAdapterError("subject 为空")
        if self._reviewer is None:
            raise DeepReviewAdapterError("reviewer 未注入（Fail-Closed 不真发）")
        try:
            raw = self._reviewer(task)
        except Exception as exc:  # noqa: BLE001 — reviewer 异常包装 Fail-Closed
            raise DeepReviewAdapterError(f"reviewer 调用异常: {task.task_id!r}") from exc
        findings, score = self._normalize_output(raw)
        report = ReviewReport(
            task_id=task.task_id,
            model_id=task.model_id,
            review_type=task.review_type,
            score=score,
            passed=score >= calibration.threshold,
            findings=findings,
            reviewed_at=self._clock(),
        )
        self._reports[task.task_id] = report
        _log.info(
            "深度审查完成: %s %s score=%s passed=%s",
            task.task_id, task.review_type.value, score, report.passed,
        )
        return report

    @staticmethod
    def _normalize_output(raw: object) -> tuple[tuple[Finding, ...], float]:
        """reviewer 产出校验（score∈[0,1] + findings 词表/必填校验）。"""
        if not isinstance(raw, Mapping):
            raise DeepReviewAdapterError("reviewer 产出非法（须映射）")
        score = raw.get("score")
        if isinstance(score, bool) or not isinstance(score, (int, float)):
            raise DeepReviewAdapterError("reviewer score 缺失或非数值")
        if not math.isfinite(score) or not 0.0 <= score <= 1.0:
            raise DeepReviewAdapterError(f"reviewer score 越界 [0,1]: {score!r}")
        raw_findings = raw.get("findings")
        if not isinstance(raw_findings, (list, tuple)):
            raise DeepReviewAdapterError("reviewer findings 缺失或非法（须列表）")
        findings: list[Finding] = []
        for item in raw_findings:
            if not isinstance(item, Mapping):
                raise DeepReviewAdapterError("finding 非法（须映射）")
            finding_id = item.get("finding_id")
            if not isinstance(finding_id, str) or not finding_id:
                raise DeepReviewAdapterError("finding_id 缺失或为空")
            severity_raw = item.get("severity")
            try:
                severity = FindingSeverity(severity_raw)
            except ValueError as exc:
                raise DeepReviewAdapterError(
                    f"finding severity 越词表: {severity_raw!r}"
                ) from exc
            description = item.get("description")
            if not isinstance(description, str) or not description:
                raise DeepReviewAdapterError(
                    f"finding description 缺失或为空: {finding_id!r}"
                )
            category = item.get("category", "")
            if not isinstance(category, str):
                raise DeepReviewAdapterError(f"finding category 类型非法: {finding_id!r}")
            findings.append(
                Finding(
                    finding_id=finding_id,
                    severity=severity,
                    description=description,
                    category=category,
                )
            )
        return tuple(findings), float(score)

    # ── 查询 ─────────────────────────────────────────────────────────────

    def profile_of(self, model_id: str) -> DeepReviewProfile:
        """单模型 profile（未注册 → Fail-Closed）。"""
        profile = self._profiles.get(model_id)
        if profile is None:
            raise DeepReviewAdapterError(f"未注册 model: {model_id!r}")
        return profile

    def calibration_of(self, model_id: str) -> CalibrationResult:
        """单模型校准结果（未校准 → Fail-Closed）。"""
        result = self._calibrations.get(model_id)
        if result is None:
            raise DeepReviewAdapterError(f"模型未校准: {model_id!r}")
        return result

    def report_of(self, task_id: str) -> ReviewReport:
        """单任务审查报告（未知 → Fail-Closed）。"""
        report = self._reports.get(task_id)
        if report is None:
            raise DeepReviewAdapterError(f"未知 task: {task_id!r}")
        return report

    def registered_models(self) -> tuple[str, ...]:
        """已注册模型视图（确定性排序）。"""
        return tuple(sorted(self._profiles))

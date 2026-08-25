# [BLUEPRINT] MOD-BT-027 | docs/03_modules/_domain_backtest/layered_validation_pipeline/blueprint.md
# [MODULE] zephyr.backtest.services.layered_validation_pipeline
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只编排不重造(门控阈值/引擎/持久化全注入委托,52号裁定禁第二套V1-V6门控); 层层递进不可跳级(层失败即中止剩余not_run); runner/gate返回契约非法Fail-Closed; 归档失败不吞裁决(archive_status留痕); 层失败短路不再跑过拟合门禁
# [MODIFY-GUARD] tests/backtest/test_layered_validation_pipeline.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] LayeredValidationError(未登记错误码-申请中)
# [TESTS] tests/backtest/test_layered_validation_pipeline.py
# [A_module] module_id=MOD-BT-027 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""C-003 自动回测与仿真——分层验证管道（MOD-BT-027）。

真源：construction_backlog_dig.tsv B1-00258（跨域元文档 §功能域模块·D-OPS，
裁定=做 P1）+ CAND-WFO-002。

定位：回测引擎存在但策略/因子/信号**提交即验证**的 V1~V5 分层自动化管道缺失
（TSV 现状）。本模块=提交触发的分层自动执行**编排骨架**：

  ① 提交 → 层计划（§20.7.1 分层映射：factor→V1，signal→V2+V5，strategy→V3，
     pipeline→V4；V6 风控验证按需不入封闭集）；
  ② 层层递进不可跳级（层失败即中止，剩余记 not_run；52号/§20.7 语义）；
  ③ 过拟合门禁注入委托（Owner 接线 OverfittingDetector/MOD-BT-001
     strategy_validation_pipeline 三阶段门控；**不建第二套门控**——52号 §7
     BM-BT-07-I 显式裁定：再建 V1-V6 门控=同一防线两套阈值，禁）；
  ④ 报告归档注入委托（sink 异常不吞裁决，archive_status 留痕审计可见）。

不做什么：不定义任何验证阈值、不直接跑回测引擎（runner 注入式，层执行器按
§20.7.1 由运行时装配批接线，可委托 MOD-BT-017 scheduler/引擎族）、不持久化。
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field, replace
from typing import Any, Final

__all__: Final = [
    "SUBJECT_LAYER_PLAN",
    "LayeredValidationError",
    "LayeredValidationReport",
    "LayerResult",
    "ValidationSubmission",
    "run_layered_validation",
]

_log = logging.getLogger(__name__)

#: 提交类型 → 验证层计划（交易决策架构 §20.7.1 分层验证架构映射）
SUBJECT_LAYER_PLAN: Final[Mapping[str, tuple[str, ...]]] = {
    "factor": ("V1",),  # 因子验证：Purged K-Fold + Embargo
    "signal": ("V2", "V5"),  # 信号验证 WF + 日内信号 Tick 级验证
    "strategy": ("V3",),  # 策略验证：WF + Permutation Test
    "pipeline": ("V4",),  # 管线验证：全链路端到端 + 模拟盘
}

_LAYER_STATUS_PASSED: Final[str] = "passed"
_LAYER_STATUS_FAILED: Final[str] = "failed"
_LAYER_STATUS_ERROR: Final[str] = "error"
_LAYER_STATUS_NOT_RUN: Final[str] = "not_run"


class LayeredValidationError(ValueError):
    """分层验证管道输入/契约非法（Fail-Closed；未登记错误码-申请中）。"""


@dataclass(frozen=True)
class ValidationSubmission:
    """验证提交（不可变）。

    Attributes:
        subject_kind: 提交类型（封闭集 factor/signal/strategy/pipeline）
        subject_id: 提交对象标识
        params: 提交参数（层执行器消费）
        artifacts: 各层验证产物/数据引用（注入式，层执行器消费）
    """

    subject_kind: str
    subject_id: str
    params: Mapping[str, Any] = field(default_factory=dict)
    artifacts: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class LayerResult:
    """单层验证结果（不可变）。

    Attributes:
        layer: 验证层（V1~V5）
        passed: 本层是否通过
        metrics: 层验证指标（runner 产出，编排面不解释）
        detail: 层结论描述
        status: passed/failed/error/not_run（runner 异常=error）
    """

    layer: str
    passed: bool
    metrics: Mapping[str, Any] = field(default_factory=dict)
    detail: str = ""
    status: str = _LAYER_STATUS_PASSED


@dataclass(frozen=True)
class LayeredValidationReport:
    """分层验证报告（不可变，归档载体）。

    Attributes:
        subject_id / subject_kind: 提交标识
        layers_planned: 层计划
        layer_results: 层结果（含 not_run 占位）
        gate_status: not_configured/evaluated/skipped_layer_failure
        is_overfitting: 过拟合门禁结论（未配置/跳过=False）
        passed: 总裁决（全部层通过 ∧ 未检出过拟合）
        archive_status: not_configured/archiving/archived/archive_failed
        reasons: 裁决理由（层失败/过拟合/归档异常如实记录）
    """

    subject_id: str
    subject_kind: str
    layers_planned: tuple[str, ...]
    layer_results: tuple[LayerResult, ...]
    gate_status: str
    is_overfitting: bool
    passed: bool
    archive_status: str
    reasons: tuple[str, ...] = field(default_factory=tuple)


def _validate_submission(submission: ValidationSubmission) -> None:
    if not isinstance(submission, ValidationSubmission):
        raise LayeredValidationError(
            f"submission 必须是 ValidationSubmission: {type(submission).__name__}"
        )
    if submission.subject_kind not in SUBJECT_LAYER_PLAN:
        raise LayeredValidationError(
            f"未知 subject_kind: {submission.subject_kind!r}"
            f"（封闭集 {sorted(SUBJECT_LAYER_PLAN)}）"
        )
    if not isinstance(submission.subject_id, str) or not submission.subject_id.strip():
        raise LayeredValidationError(f"subject_id 不能为空: {submission.subject_id!r}")


def run_layered_validation(
    submission: ValidationSubmission,
    *,
    layer_runners: Mapping[str, Callable[[ValidationSubmission, str], LayerResult]],
    overfitting_gate: Callable[[ValidationSubmission, tuple[LayerResult, ...]], Mapping[str, Any]] | None = None,
    report_sink: Callable[[LayeredValidationReport], None] | None = None,
) -> LayeredValidationReport:
    """提交触发 V1~V5 分层验证编排（递进执行→过拟合门禁→报告归档）。

    Args:
        submission: 验证提交（kind 封闭集/id 非空 Fail-Closed）
        layer_runners: 层执行器 {层: callable(submission, layer) -> LayerResult}
            （注入式：自动跑回测由 runner 委托既有引擎族，本模块不直接跑）
        overfitting_gate: 过拟合门禁 callable(submission, results) ->
            Mapping{is_overfitting: bool, reasons: list}（Owner 接线
            OverfittingDetector；None=未配置）
        report_sink: 报告归档 callable(report)（None=不归档；异常不吞裁决，
            记 archive_status=archive_failed）

    Raises:
        LayeredValidationError: 提交非法/计划层 runner 缺失/runner 或 gate
            返回契约非法（Fail-Closed）
    """
    _validate_submission(submission)
    plan = SUBJECT_LAYER_PLAN[submission.subject_kind]
    missing = [layer for layer in plan if layer not in layer_runners]
    if missing:
        raise LayeredValidationError(
            f"计划层缺 runner（配置错误 Fail-Closed）: {missing}（subject={submission.subject_id}）"
        )

    reasons: list[str] = []
    results: list[LayerResult] = []
    halted = False
    for layer in plan:
        if halted:
            results.append(
                LayerResult(layer=layer, passed=False, detail="前层未通过（不可跳级）", status=_LAYER_STATUS_NOT_RUN)
            )
            continue
        try:
            result = layer_runners[layer](submission, layer)
        except Exception as exc:  # runner 崩溃=本层失败（error），不 crash 编排面
            _log.exception("层 %s runner 异常（subject=%s）", layer, submission.subject_id)
            result = LayerResult(
                layer=layer, passed=False, detail=f"runner 异常: {exc}", status=_LAYER_STATUS_ERROR
            )
        if not isinstance(result, LayerResult):
            raise LayeredValidationError(
                f"层 {layer} runner 返回契约非法（须 LayerResult）: {type(result).__name__}"
            )
        if result.status == _LAYER_STATUS_PASSED and not result.passed:
            result = replace(result, status=_LAYER_STATUS_FAILED)
        results.append(result)
        if not result.passed:
            reasons.append(f"层 {layer} 未通过: {result.detail}")
            halted = True

    layers_all_passed = not halted

    # 过拟合门禁（层失败短路不再跑；注入委托不重造）
    is_overfitting = False
    if not layers_all_passed:
        gate_status = "skipped_layer_failure"
    elif overfitting_gate is None:
        gate_status = "not_configured"
    else:
        verdict = overfitting_gate(submission, tuple(results))
        if not isinstance(verdict, Mapping) or "is_overfitting" not in verdict:
            raise LayeredValidationError(
                f"过拟合门禁返回契约非法（须含 is_overfitting）: {type(verdict).__name__}"
            )
        gate_status = "evaluated"
        is_overfitting = bool(verdict["is_overfitting"])
        if is_overfitting:
            gate_reasons = verdict.get("reasons") or []
            reasons.append("过拟合门禁否决: " + "; ".join(str(r) for r in gate_reasons))

    passed = layers_all_passed and not is_overfitting
    reasons.append("管道裁决: 通过" if passed else "管道裁决: 不通过")

    report = LayeredValidationReport(
        subject_id=submission.subject_id,
        subject_kind=submission.subject_kind,
        layers_planned=plan,
        layer_results=tuple(results),
        gate_status=gate_status,
        is_overfitting=is_overfitting,
        passed=passed,
        archive_status="not_configured" if report_sink is None else "archiving",
        reasons=tuple(reasons),
    )

    # 报告归档（注入委托；失败不吞裁决，留痕审计可见）
    if report_sink is not None:
        try:
            report_sink(report)
        except Exception as exc:  # noqa: BLE001 — 归档故障不吞裁决
            _log.exception("验证报告归档失败（subject=%s）", submission.subject_id)
            report = replace(
                report,
                archive_status="archive_failed",
                reasons=report.reasons + (f"归档失败（裁决保留）: {exc}",),
            )
        else:
            report = replace(report, archive_status="archived")

    return report

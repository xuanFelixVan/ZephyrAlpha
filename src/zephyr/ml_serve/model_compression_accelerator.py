# [BLUEPRINT] MOD-MLS-002 | docs/03_modules/_domain_ml_serve/model_compression_accelerator/blueprint.md
# [MODULE] zephyr.ml_serve.model_compression_accelerator
# [DOMAIN] D_ML_SERVE
# [DEPENDENCIES] 无（编排核心纯内存；阶段执行器/数值误差验证/Double-Lock检查/C-003门禁/时钟全注入）
# [CONSUMERS] 运行时装配批（三阶段压缩流水线装配 / 留出集登记与校准防泄漏 / 压缩登记册查询）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 阶段词表闭合(onnx_int8|llamacpp_int4|knowledge_distillation); 同模型阶段严格按序推进(前置阶段PASSED方可下一阶段); 校准集∩留出集=∅否则Fail-Closed; Phase1数值误差<1e-5; Phase2量化后须重过Double-Lock; 每阶段C-003门禁不过记FAILED且不推进; 登记册只追加不可变; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_ml_serve/model_compression_accelerator/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ModelCompressionError(占位 ZA-MLS-UNREGISTERED-MODEL-COMPRESSION)——未注册模型/非法阶段顺序/空job_id/重复job/校准泄漏/指标非有限值/执行器缺失时抛
# [TESTS] tests/ml_serve/test_model_compression_accelerator.py
# [A_module] module_id=MOD-MLS-002 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
ModelCompressionAccelerator — 模型压缩与推理加速器（MOD-MLS-002）。

B10-01872（AUD-DRAFT-001-DIGEST P2 波 P2-W07，CAND-MLS-002，A1 §29.28）：
**三阶段压缩编排**——Phase1 ONNX+INT8（校准集防泄漏校验 + 数值误差<1e-5
验证注入）、Phase2 llama.cpp+INT4（量化后重过 Double-Lock 注入）、Phase3
知识蒸馏（注入 distiller）；**每阶段 C-003 完整验证门禁**（CRPS/Sharpe/
MaxDD 不显著降判定注入）+ **压缩登记册**。阶段执行器全部注入，本件不真
跑 ONNX/llama.cpp/蒸馏。

查重分工（蓝图 §0）：knowledge_distillation（MOD-FEEDBACK_LOOP）=KB 蒸
馏占位（本件经注入 distiller 回调挂接，不重建蒸馏实现）；layered_
validation_pipeline（MOD-BT-027）=C-003 回测门禁本体（本件注入判定回调，
不重跑回测）；venra_double_lock_anchor（MOD-INF-049）=Double-Lock 锚定
门禁（本件注入检查回调）；model_drift_monitor（MOD-MLS-001）=推理漂移监
控（零交集）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: phase_executors 参数
#   fields: 参数 phase_executors（无注解）
#   code: model_compression_accelerator.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: numeric_error_validator 参数
#   fields: 参数 numeric_error_validator（无注解）
#   code: model_compression_accelerator.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: double_lock_checker 参数
#   fields: 参数 double_lock_checker（无注解）
#   code: model_compression_accelerator.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: c003_gate 参数
#   fields: 参数 c003_gate（无注解）
#   code: model_compression_accelerator.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① ModelCompressionAccelerator
#   name_en: ModelCompressionAccelerator
#   intro: 三阶段压缩编排器（执行器/验证器全注入 + 压缩登记册）。
#   desc: 三阶段压缩编排器（执行器/验证器全注入 + 压缩登记册）。；公共方法（定义序）: register_model, run_phase, record_of, records_of, next_phase, regist…
#   inputs: phase_executors numeric_error_validator double_lock_checker c003_gate…
#   outputs: 返回值
#   （注：A1 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（6 定义）
#   name_en: public defs
#   intro: ModelCompressionAccelerator
#   downstream: 运行时装配批（三阶段压缩流水线装配 / 留出集登记与校准防泄漏 / 压缩登记册查询）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
import math
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Iterable, Mapping

_log = logging.getLogger(__name__)

__all__: Final = [
    "CompressionJob",
    "CompressionPhase",
    "CompressionRecord",
    "ModelCompressionAccelerator",
    "ModelCompressionError",
    "PhaseOutcome",
]

#: Phase1 数值误差硬上限（ONNX+INT8 量化数值误差须 < 1e-5）
_MAX_NUMERIC_ERROR: Final[float] = 1e-5


class ModelCompressionError(Exception):
    """模型压缩编排输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-MLS-UNREGISTERED-MODEL-COMPRESSION。
    """


class CompressionPhase(str, Enum):
    """三阶段压缩词表（闭合）。"""

    ONNX_INT8 = "onnx_int8"
    LLAMACPP_INT4 = "llamacpp_int4"
    KNOWLEDGE_DISTILLATION = "knowledge_distillation"


#: 阶段编排顺序（同模型严格按序推进）
_PHASE_ORDER: Final[tuple[CompressionPhase, ...]] = (
    CompressionPhase.ONNX_INT8,
    CompressionPhase.LLAMACPP_INT4,
    CompressionPhase.KNOWLEDGE_DISTILLATION,
)


class PhaseOutcome(str, Enum):
    """阶段门禁结果。"""

    PASSED = "passed"
    FAILED = "failed"


@dataclass(frozen=True)
class CompressionJob:
    """压缩阶段作业（frozen）。

    calibration_ids=INT8 校准集样本标识（防泄漏校验对象）；candidate 指标
    由注入执行器产出（C-003 口径：CRPS/Sharpe/MaxDD 等）。
    """

    job_id: str
    model_id: str
    phase: CompressionPhase
    calibration_ids: tuple[str, ...]
    submitted_at: datetime.datetime


@dataclass(frozen=True)
class CompressionRecord:
    """压缩登记册条目（不可变，只追加）。"""

    job_id: str
    model_id: str
    phase: CompressionPhase
    outcome: PhaseOutcome
    candidate_metrics: dict[str, float]
    numeric_error: float | None
    reasons: tuple[str, ...]
    finished_at: datetime.datetime


def _validate_metrics(name: str, metrics: object) -> dict[str, float]:
    """指标表校验（非空映射/非空键/有限数值），返回确定性拷贝。"""
    if not isinstance(metrics, Mapping) or not metrics:
        raise ModelCompressionError(f"{name} 为空或非法（须非空指标映射）")
    out: dict[str, float] = {}
    for key, value in metrics.items():
        if not isinstance(key, str) or not key:
            raise ModelCompressionError(f"{name} 含空指标名")
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ModelCompressionError(f"{name}[{key!r}] 非数值: {value!r}")
        if not math.isfinite(value):
            raise ModelCompressionError(f"{name}[{key!r}] 非有限值: {value!r}")
        out[key] = float(value)
    return out


class ModelCompressionAccelerator:
    """三阶段压缩编排器（执行器/验证器全注入 + 压缩登记册）。"""

    def __init__(
        self,
        *,
        phase_executors: Mapping[CompressionPhase, Callable[[CompressionJob], Mapping[str, float]]],
        numeric_error_validator: Callable[[CompressionJob], float],
        double_lock_checker: Callable[[CompressionJob], bool],
        c003_gate: Callable[[str, Mapping[str, float], Mapping[str, float]], bool],
        holdout_ids: Iterable[str] = (),
        clock: Callable[[], datetime.datetime] | None = None,
    ) -> None:
        if not isinstance(phase_executors, Mapping):
            raise ModelCompressionError("phase_executors 非法（须按阶段注入执行器映射）")
        missing = [p for p in _PHASE_ORDER if p not in phase_executors]
        if missing:
            raise ModelCompressionError(f"阶段执行器缺失: {[p.value for p in missing]}（三阶段执行器须全注入）")
        for key in phase_executors:
            if not isinstance(key, CompressionPhase):
                raise ModelCompressionError(f"非法阶段键: {key!r}")
        self._executors = dict(phase_executors)
        self._numeric_validator = numeric_error_validator
        self._double_lock = double_lock_checker
        self._c003_gate = c003_gate
        self._holdout = frozenset(holdout_ids)
        self._clock = clock or datetime.datetime.now
        self._baselines: dict[str, dict[str, float]] = {}
        self._records: dict[str, CompressionRecord] = {}
        self._records_by_model: dict[str, list[CompressionRecord]] = {}

    # ── 模型登记 ────────────────────────────────────────────────────────

    def register_model(self, model_id: str, baseline_metrics: Mapping[str, float]) -> None:
        """登记待压缩模型 + C-003 基线指标（重复登记拒绝）。"""
        if not isinstance(model_id, str) or not model_id:
            raise ModelCompressionError("model_id 为空")
        if model_id in self._baselines:
            raise ModelCompressionError(f"模型重复登记: {model_id!r}")
        self._baselines[model_id] = _validate_metrics("baseline_metrics", baseline_metrics)
        self._records_by_model[model_id] = []

    # ── 三阶段编排 ──────────────────────────────────────────────────────

    def run_phase(self, job: CompressionJob) -> CompressionRecord:
        """执行单阶段：协议校验 → 执行器 → 阶段专项验证 → C-003 门禁 → 登记。"""
        if not isinstance(job, CompressionJob):
            raise ModelCompressionError("job 非法（须 CompressionJob）")
        if not job.job_id:
            raise ModelCompressionError("job_id 为空")
        if job.job_id in self._records:
            raise ModelCompressionError(f"job_id 重复: {job.job_id!r}")
        baseline = self._baselines.get(job.model_id)
        if baseline is None:
            raise ModelCompressionError(f"未注册模型: {job.model_id!r}")
        if not isinstance(job.phase, CompressionPhase):
            raise ModelCompressionError(f"非法阶段: {job.phase!r}")
        expected = self.next_phase(job.model_id)
        if job.phase is not expected:
            raise ModelCompressionError(
                f"非法阶段顺序: {job.model_id!r} 待执行 "
                f"{expected.value if expected is not None else '无（三阶段已完成）'}，"
                f"收到 {job.phase.value}"
            )
        if isinstance(job.calibration_ids, str):
            raise ModelCompressionError("calibration_ids 非法（须标识序列，非字符串）")
        for cid in job.calibration_ids:
            if not isinstance(cid, str) or not cid:
                raise ModelCompressionError("calibration_ids 含空标识")
        leaked = sorted(set(job.calibration_ids) & self._holdout)
        if leaked:
            raise ModelCompressionError(f"校准集防泄漏校验失败: {leaked} 命中留出集（校准集∩留出集须为空）")
        if job.phase is CompressionPhase.ONNX_INT8 and not job.calibration_ids:
            raise ModelCompressionError("Phase1 ONNX+INT8 须声明非空校准集")

        reasons: list[str] = []
        candidate: dict[str, float] = {}
        numeric_error: float | None = None

        try:
            candidate = _validate_metrics("candidate_metrics", self._executors[job.phase](job))
        except ModelCompressionError as exc:
            reasons.append(f"执行器产出非法: {exc}")
        except Exception:  # noqa: BLE001 — 执行器异常按阶段失败登记不抛
            _log.exception("阶段执行器异常: %s", job.job_id)
            reasons.append("阶段执行器异常")

        if not reasons and job.phase is CompressionPhase.ONNX_INT8:
            try:
                numeric_error = float(self._numeric_validator(job))
            except Exception:  # noqa: BLE001 — 验证器异常按阶段失败登记
                _log.exception("数值误差验证器异常: %s", job.job_id)
                reasons.append("数值误差验证器异常")
            else:
                if not math.isfinite(numeric_error):
                    reasons.append(f"数值误差非有限值: {numeric_error!r}")
                elif numeric_error >= _MAX_NUMERIC_ERROR:
                    reasons.append(f"数值误差越限: {numeric_error} ≥ {_MAX_NUMERIC_ERROR}")

        if not reasons and job.phase is CompressionPhase.LLAMACPP_INT4:
            try:
                locked = bool(self._double_lock(job))
            except Exception:  # noqa: BLE001 — 检查器异常按阶段失败登记
                _log.exception("Double-Lock 检查器异常: %s", job.job_id)
                reasons.append("Double-Lock 检查器异常")
            else:
                if not locked:
                    reasons.append("量化后重过 Double-Lock 未通过")

        if not reasons:
            try:
                gate_ok = bool(self._c003_gate(job.model_id, baseline, candidate))
            except Exception:  # noqa: BLE001 — 门禁异常按阶段失败登记
                _log.exception("C-003 验证门禁异常: %s", job.job_id)
                reasons.append("C-003 验证门禁异常")
            else:
                if not gate_ok:
                    reasons.append("C-003 验证门禁未通过（CRPS/Sharpe/MaxDD 显著降）")

        record = CompressionRecord(
            job_id=job.job_id,
            model_id=job.model_id,
            phase=job.phase,
            outcome=PhaseOutcome.PASSED if not reasons else PhaseOutcome.FAILED,
            candidate_metrics=candidate,
            numeric_error=numeric_error,
            reasons=tuple(reasons),
            finished_at=self._clock(),
        )
        self._records[job.job_id] = record
        self._records_by_model[job.model_id].append(record)
        _log.info("压缩阶段登记: %s %s -> %s", job.model_id, job.phase.value, record.outcome.value)
        return record

    # ── 查询 ─────────────────────────────────────────────────────────────

    def record_of(self, job_id: str) -> CompressionRecord:
        """单 job 登记记录（未知 → Fail-Closed）。"""
        record = self._records.get(job_id)
        if record is None:
            raise ModelCompressionError(f"未知 job: {job_id!r}")
        return record

    def records_of(self, model_id: str) -> tuple[CompressionRecord, ...]:
        """单模型登记记录（执行序，确定性）。"""
        if model_id not in self._baselines:
            raise ModelCompressionError(f"未注册模型: {model_id!r}")
        return tuple(self._records_by_model[model_id])

    def next_phase(self, model_id: str) -> CompressionPhase | None:
        """下一待执行阶段（三阶段全 PASSED → None）。"""
        if model_id not in self._baselines:
            raise ModelCompressionError(f"未注册模型: {model_id!r}")
        passed = {rec.phase for rec in self._records_by_model[model_id] if rec.outcome is PhaseOutcome.PASSED}
        for phase in _PHASE_ORDER:
            if phase not in passed:
                return phase
        return None

    def registered_models(self) -> tuple[str, ...]:
        """压缩登记册模型视图（确定性排序）。"""
        return tuple(sorted(self._baselines))

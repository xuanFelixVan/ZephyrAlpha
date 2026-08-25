# [BLUEPRINT] MOD-MLS-001 | docs/03_modules/_domain_ml_serve/model_drift_monitor/blueprint.md
# [MODULE] zephyr.ml_serve.core.model_drift_monitor
# [DOMAIN] D_ML_SERVE
# [DEPENDENCIES] numpy(标准科学栈); event_sink/clock 注入（INV-019 Warm→Cold 异步语义，不 import D_INFRA_A2A/D_OPS）
# [CONSUMERS] 运行时装配批（MS-02 推理样本供给 / E-OP-02 事件总线 sink 绑定 D-OPS·MT-05·F09 消费方 / 阈值 config 加载）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 判定核心纯内存无IO; 四维度量闭式确定性; 四维阈值独立 warn<critical; 事件顺序固定 PSI→PERFORMANCE→JS→IC; event_sink 异常不阻断判定; detected_at 取注入时钟; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_ml_serve/model_drift_monitor/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ModelDriftError(占位 ZA-MLS-UNREGISTERED-MODEL-DRIFT)——空model_id/空样本/非有限值/阈值非法时抛
# [TESTS] tests/ml_serve/test_model_drift_monitor.py
# [A_module] module_id=MOD-MLS-001 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ModelDriftMonitor — 推理域 MS-03 模型漂移监控（MOD-MLS-001）。

B4-06990（AUD-DRAFT-001-DIGEST P1 波 W-P1-25，CAND-MLS-001，D-ML-SERVE
§0/§1 MS-03）：serving 模型**四维漂移检测**（PSI 输入特征 / JS 散度输出
分布 / 性能衰减 / IC 衰减）+ **E-OP-02 ModelDriftDetected 域事件**生产，
经 event_sink 外发（INV-019 Warm→Cold 异步语义，sink DI 注入）。

查重裁定（蓝图 §0，铁律④域级泛条目细读）：模型生命周期（active 唯一+
approval_ts/activated_at）与 INV-011 影子门禁已由 MOD-ML-012（D_ML_TRAIN）
承载，LLM 网关由 MOD-INF-051 承载——均不重建（设计边分工）；E-OP-02 漂移
检测全仓无生产者，独立缺口。与 MOD-FBL-001 分工：FBL=因子/标签分布三路
事前预警（语义响应）；本件=serving 模型四维（model_id 键）→ E-OP-02 域
事件。
"""

from __future__ import annotations

import datetime
import logging
import math
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Final, Sequence

import numpy as np

_log = logging.getLogger(__name__)

__all__: Final = [
    "E_OP_02",
    "DriftEvaluation",
    "DriftSeverity",
    "DriftThresholds",
    "DriftType",
    "ModelDriftError",
    "ModelDriftEvent",
    "ModelDriftMonitor",
    "js_divergence",
    "psi",
]

#: E-OP-02 ModelDriftDetected（D-ML-SERVE 核心事件，域文档 §0/§4）
E_OP_02: Final[str] = "E-OP-02"

_EPS: Final[float] = 1e-4  # 比例裁剪防 0 除
_MIN_SAMPLES: Final[int] = 2
_METRIC_EPS: Final[float] = 1e-9  # 性能/IC 基线近零判定


class ModelDriftError(Exception):
    """模型漂移监控输入非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-MLS-UNREGISTERED-MODEL-DRIFT。
    """


class DriftType(str, Enum):
    """漂移维度（E-OP-02 drift_type 载荷词表）。"""

    PSI = "PSI"
    PERFORMANCE = "PERFORMANCE"
    JS = "JS"
    IC = "IC"


class DriftSeverity(str, Enum):
    """漂移严重度。"""

    NONE = "none"
    WARN = "warn"
    CRITICAL = "critical"


@dataclass(frozen=True)
class DriftThresholds:
    """四维独立阈值（warn < critical 强制；默认对齐域文档 §7.1/§7.4）。"""

    psi_warn: float = 0.15
    psi_critical: float = 0.25
    js_warn: float = 0.10
    js_critical: float = 0.20
    perf_warn: float = 0.05
    perf_critical: float = 0.10
    ic_warn: float = 0.30
    ic_critical: float = 0.50

    def __post_init__(self) -> None:
        for name in ("psi", "js", "perf", "ic"):
            warn = getattr(self, f"{name}_warn")
            crit = getattr(self, f"{name}_critical")
            if warn <= 0 or crit <= 0:
                raise ModelDriftError(f"{name} 阈值须为正")
            if warn >= crit:
                raise ModelDriftError(
                    f"{name} 阈值须满足 warn < critical（{warn} !< {crit}）"
                )


@dataclass(frozen=True)
class ModelDriftEvent:
    """E-OP-02 ModelDriftDetected 事件载荷（域文档 §4 口径）。"""

    event_id: str
    model_id: str
    drift_type: DriftType
    drift_score: float
    threshold: float
    severity: DriftSeverity
    detected_at: datetime.datetime


@dataclass(frozen=True)
class DriftEvaluation:
    """逐模型漂移评估（四维度量值 + 事件元组，确定性顺序）。"""

    model_id: str
    metric_values: dict[str, float]
    events: tuple[ModelDriftEvent, ...]


def _as_samples(name: str, values: Sequence[float]) -> np.ndarray:
    arr = np.asarray(list(values), dtype=float)
    if arr.size < _MIN_SAMPLES:
        raise ModelDriftError(f"{name} 样本数不足（<{_MIN_SAMPLES}）")
    if not np.all(np.isfinite(arr)):
        raise ModelDriftError(f"{name} 含非有限值")
    return arr


def _hist_props(reference: np.ndarray, current: np.ndarray, buckets: int) -> tuple[np.ndarray, np.ndarray]:
    """分位分箱比例（reference 分位点为箱界；裁剪 eps 防 0 除）。"""
    if buckets < 2:
        raise ModelDriftError("分箱数须 ≥2")
    quantiles = np.linspace(0.0, 100.0, buckets + 1)
    edges = np.percentile(reference, quantiles)
    edges[0], edges[-1] = -np.inf, np.inf
    ref_counts, _ = np.histogram(reference, bins=edges)
    cur_counts, _ = np.histogram(current, bins=edges)
    e = np.clip(ref_counts / reference.size, _EPS, None)
    a = np.clip(cur_counts / current.size, _EPS, None)
    return e, a


def psi(reference: Sequence[float], current: Sequence[float], buckets: int = 10) -> float:
    """总体稳定性指数 Σ(a%−e%)·ln(a%/e%)（输入特征漂移）。"""
    ref = _as_samples("reference", reference)
    cur = _as_samples("current", current)
    e, a = _hist_props(ref, cur, buckets)
    return float(np.sum((a - e) * np.log(a / e)))


def js_divergence(reference: Sequence[float], current: Sequence[float], buckets: int = 10) -> float:
    """JS 散度 0.5·KL(p‖m)+0.5·KL(q‖m)，m=0.5(p+q)（输出分布漂移，nats）。"""
    ref = _as_samples("reference", reference)
    cur = _as_samples("current", current)
    p, q = _hist_props(ref, cur, buckets)
    m = 0.5 * (p + q)
    return float(0.5 * np.sum(p * np.log(p / m)) + 0.5 * np.sum(q * np.log(q / m)))


def _decay(name: str, reference: float, current: float) -> float:
    """衰减率 (ref−cur)/|ref|；|ref| 近零按绝对差口径。"""
    if not math.isfinite(reference) or not math.isfinite(current):
        raise ModelDriftError(f"{name} 含非有限值")
    if abs(reference) < _METRIC_EPS:
        return abs(reference - current)
    return (reference - current) / abs(reference)


class ModelDriftMonitor:
    """推理域 MS-03 模型漂移监控（四维检测 + E-OP-02 事件生产）。"""

    def __init__(
        self,
        *,
        thresholds: DriftThresholds | None = None,
        clock: Callable[[], datetime.datetime] | None = None,
        event_sink: Callable[[ModelDriftEvent], None] | None = None,
    ) -> None:
        self._thresholds = thresholds or DriftThresholds()
        self._clock = clock or datetime.datetime.now
        self._event_sink = event_sink

    def _emit(self, events: list[ModelDriftEvent]) -> None:
        if self._event_sink is None:
            return
        for event in events:
            try:
                self._event_sink(event)
            except Exception:  # noqa: BLE001 — sink 异常不阻断判定（蓝图 §1）
                _log.exception("E-OP-02 事件外发失败: %s %s", event.model_id, event.drift_type)

    def evaluate(
        self,
        model_id: str,
        *,
        feature_ref: Sequence[float],
        feature_cur: Sequence[float],
        output_ref: Sequence[float],
        output_cur: Sequence[float],
        perf_ref: float,
        perf_cur: float,
        ic_ref: float,
        ic_cur: float,
    ) -> DriftEvaluation:
        """四维评估：任一维越 warn 产 E-OP-02 事件（顺序 PSI→PERFORMANCE→JS→IC）。"""
        if not model_id:
            raise ModelDriftError("model_id 为空")
        th = self._thresholds
        now = self._clock()
        metrics = {
            "psi": psi(feature_ref, feature_cur),
            "performance": _decay("performance", perf_ref, perf_cur),
            "js": js_divergence(output_ref, output_cur),
            "ic": _decay("ic", ic_ref, ic_cur),
        }
        gates = (
            (DriftType.PSI, "psi", th.psi_warn, th.psi_critical),
            (DriftType.PERFORMANCE, "performance", th.perf_warn, th.perf_critical),
            (DriftType.JS, "js", th.js_warn, th.js_critical),
            (DriftType.IC, "ic", th.ic_warn, th.ic_critical),
        )
        events: list[ModelDriftEvent] = []
        for drift_type, key, warn, crit in gates:
            score = metrics[key]
            if score >= crit:
                severity, threshold = DriftSeverity.CRITICAL, crit
            elif score >= warn:
                severity, threshold = DriftSeverity.WARN, warn
            else:
                continue
            events.append(
                ModelDriftEvent(
                    event_id=E_OP_02,
                    model_id=model_id,
                    drift_type=drift_type,
                    drift_score=score,
                    threshold=threshold,
                    severity=severity,
                    detected_at=now,
                )
            )
        if events:
            _log.warning(
                "E-OP-02 模型漂移: %s %s",
                model_id,
                [(e.drift_type.value, e.severity.value, round(e.drift_score, 4)) for e in events],
            )
        self._emit(events)
        return DriftEvaluation(model_id=model_id, metric_values=metrics, events=tuple(events))

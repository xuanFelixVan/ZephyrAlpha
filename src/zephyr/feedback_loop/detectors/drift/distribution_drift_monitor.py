# [BLUEPRINT] MOD-FBL-001 | docs/03_modules/_domain_fbl_detectors/distribution_drift_monitor/blueprint.md
# [MODULE] zephyr.feedback_loop.detectors.drift.distribution_drift_monitor
# [DOMAIN] D_FBL_DETECTORS
# [DEPENDENCIES] numpy(标准科学栈)
# [CONSUMERS] 运行时装配批（D_FACTOR 特征降级执行 / D_ML_TRAIN 重训触发 / MOD-DATENG-001 告警路由汇入）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 判定核心纯内存无IO; 三度量闭式确定性; 输入非法Fail-Closed; 三路阈值独立; 响应只产语义信号(降级/重训/告警)不直接执行; 不消费IC/绩效时序(与C-007事后切分)
# [MODIFY-GUARD] docs/03_modules/_domain_fbl_detectors/distribution_drift_monitor/blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DistributionDriftError(占位 ZA-FBL-UNREGISTERED-DRIFT-MONITOR)——空样本/长度不足/非有限值/阈值非法/未知通道时抛
# [TESTS] tests/drift/test_distribution_drift_monitor.py
# [A_module] module_id=MOD-FBL-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
DistributionDriftMonitor — 三路分布漂移监控器（MOD-FBL-001）。

B10-01824（AUD-DRAFT-001-DIGEST P1 波 W-P1-24，CAND-FBLDETEC-001，A1交易决策
架构 §29.5）：特征漂移（feature）+ 概念漂移（concept）+ 标签漂移（label）
三路独立阈值检测（PSI / KL / MDD 三度量）+ 差异化响应矩阵（降级 / 重训 /
告警）的**事前预警**件。

与 C-007 IC 衰减职责切分（写入契约）：本件=事前**分布**漂移预警（模型输入
特征 / 预测输出 / 标签的分布样本），C-007=事后因子 IC 绩效衰减监控；本件
接口只接受分布样本，不消费 IC/绩效时间序列；响应只产语义信号，降级/重训
执行归运行时装配批。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: reference 参数
#   fields: 参数 reference，类型注解 np.ndarray | list[float]
#   code: distribution_drift_monitor.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: current 参数
#   fields: 参数 current，类型注解 np.ndarray | list[float]
#   code: distribution_drift_monitor.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: buckets 参数
#   fields: 参数 buckets，类型注解 int
#   code: distribution_drift_monitor.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① psi
#   name_en: psi
#   intro: 总体稳定性指数 PSI = Σ(a%−e%)·ln(a%/e%)（reference 分位分箱）。
#   desc: 总体稳定性指数 PSI = Σ(a%−e%)·ln(a%/e%)（reference 分位分箱）。；源码 L218-L227
#   inputs: reference current buckets
#   outputs: float
# - id: A2
#   name_zh: ② kl_divergence
#   name_en: kl_divergence
#   intro: KL 散度 D_KL(current‖reference)（同分箱直方图，nats）。
#   desc: KL 散度 D_KL(current‖reference)（同分箱直方图，nats）。；源码 L230-L239
#   inputs: reference current buckets
#   outputs: float
# - id: A3
#   name_zh: ③ mdd
#   name_en: mdd
#   intro: 均值差异距离 MDD = |μ_cur − μ_ref| / σ_ref（线性核 MMD² 标准化口径；
#   desc: 均值差异距离 MDD = |μ_cur − μ_ref| / σ_ref（线性核 MMD² 标准化口径； σ_ref=0 时退化为原量纲绝对差）。；源码 L242-L256
#   inputs: reference current
#   outputs: float
# - id: A4
#   name_zh: ④ DistributionDriftMonitor
#   name_en: DistributionDriftMonitor
#   intro: 三路分布漂移监控器（MOD-FBL-001）。
#   desc: 三路分布漂移监控器（MOD-FBL-001）。 用法： mon = DistributionDriftMonitor() rep = mon.check_feature(ref_…；公共方法（定义序）: check,…
#   inputs: thresholds response_matrix buckets
#   outputs: 返回值
#   （注：A4 之后另有 6 个公共定义未列入（含 6 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: float
#   name_en: float
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 运行时装配批（D_FACTOR 特征降级执行 / D_ML_TRAIN 重训触发 / MOD-DATENG-001 告警路由汇入）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Final

import numpy as np

_log = logging.getLogger(__name__)

__all__: Final = [
    "ChannelThresholds",
    "DistributionDriftError",
    "DistributionDriftMonitor",
    "DriftChannel",
    "DriftReport",
    "DriftResponse",
    "DriftSeverity",
    "kl_divergence",
    "mdd",
    "psi",
]

_EPS: Final[float] = 1e-4  # 比例裁剪防 0 除
_MIN_SAMPLES: Final[int] = 2  # 分布度量最小样本数


class DistributionDriftError(Exception):
    """分布漂移监控输入非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-FBL-UNREGISTERED-DRIFT-MONITOR。
    """


class DriftChannel(str, Enum):
    """三路漂移通道。"""

    FEATURE = "feature"
    CONCEPT = "concept"
    LABEL = "label"


class DriftSeverity(str, Enum):
    """漂移严重度。"""

    NONE = "none"
    WARN = "warn"
    CRITICAL = "critical"


class DriftResponse(str, Enum):
    """差异化响应（语义信号，执行归装配批）。"""

    NONE = "none"
    ALERT = "alert"
    DEGRADE = "degrade"
    RETRAIN = "retrain"


@dataclass(frozen=True)
class ChannelThresholds:
    """单通道三度量独立阈值（warn < critical 强制）。"""

    psi_warn: float = 0.1
    psi_critical: float = 0.25
    kl_warn: float = 0.1
    kl_critical: float = 0.5
    mdd_warn: float = 0.5
    mdd_critical: float = 1.0

    def __post_init__(self) -> None:
        for name in ("psi", "kl", "mdd"):
            warn = getattr(self, f"{name}_warn")
            crit = getattr(self, f"{name}_critical")
            if warn <= 0 or crit <= 0:
                raise DistributionDriftError(f"{name} 阈值须为正")
            if warn >= crit:
                raise DistributionDriftError(f"{name} 阈值须满足 warn < critical（{warn} !< {crit}）")


@dataclass(frozen=True)
class DriftReport:
    """单通道漂移报告。"""

    channel: DriftChannel
    metric_values: dict[str, float]  # {"psi","kl","mdd"}
    drift_detected: bool
    severity: DriftSeverity
    response: DriftResponse
    detail: str


# ──────────────────────────────────────────────────────────────────────────────
# 三度量（闭式确定性）
# ──────────────────────────────────────────────────────────────────────────────


def _as_samples(values: np.ndarray | list[float], name: str) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 1 or arr.size < _MIN_SAMPLES:
        raise DistributionDriftError(
            f"{name} 须为一维且样本数 ≥ {_MIN_SAMPLES}（实得 {arr.size if arr.ndim == 1 else '非一维'}）"
        )
    if not np.all(np.isfinite(arr)):
        raise DistributionDriftError(f"{name} 含非有限值")
    return arr


def _bucket_shares(reference: np.ndarray, current: np.ndarray, buckets: int) -> tuple[np.ndarray, np.ndarray]:
    """按 reference 分位数分箱，返回两样本的箱占比（裁剪 eps，和归一）。"""
    if buckets < 2:
        raise DistributionDriftError("buckets 须 ≥ 2")
    quantiles = np.linspace(0.0, 100.0, buckets + 1)
    edges = np.unique(np.percentile(reference, quantiles))
    if edges.size < 2:
        raise DistributionDriftError("reference 退化（常数序列）无法分箱")
    edges[0] = -np.inf
    edges[-1] = np.inf
    ref_hist = np.histogram(reference, bins=edges)[0].astype(float)
    cur_hist = np.histogram(current, bins=edges)[0].astype(float)
    ref_share = np.clip(ref_hist / max(ref_hist.sum(), 1.0), _EPS, None)
    cur_share = np.clip(cur_hist / max(cur_hist.sum(), 1.0), _EPS, None)
    return ref_share, cur_share


def psi(
    reference: np.ndarray | list[float],
    current: np.ndarray | list[float],
    buckets: int = 10,
) -> float:
    """总体稳定性指数 PSI = Σ(a%−e%)·ln(a%/e%)（reference 分位分箱）。"""
    ref = _as_samples(reference, "reference")
    cur = _as_samples(current, "current")
    ref_share, cur_share = _bucket_shares(ref, cur, buckets)
    return float(np.sum((cur_share - ref_share) * np.log(cur_share / ref_share)))


def kl_divergence(
    reference: np.ndarray | list[float],
    current: np.ndarray | list[float],
    buckets: int = 10,
) -> float:
    """KL 散度 D_KL(current‖reference)（同分箱直方图，nats）。"""
    ref = _as_samples(reference, "reference")
    cur = _as_samples(current, "current")
    ref_share, cur_share = _bucket_shares(ref, cur, buckets)
    return float(np.sum(cur_share * np.log(cur_share / ref_share)))


def mdd(
    reference: np.ndarray | list[float],
    current: np.ndarray | list[float],
) -> float:
    """均值差异距离 MDD = |μ_cur − μ_ref| / σ_ref（线性核 MMD² 标准化口径；

    σ_ref=0 时退化为原量纲绝对差）。
    """
    ref = _as_samples(reference, "reference")
    cur = _as_samples(current, "current")
    gap = abs(float(np.mean(cur)) - float(np.mean(ref)))
    sigma = float(np.std(ref))
    if sigma <= 0:
        return gap
    return gap / sigma


# ──────────────────────────────────────────────────────────────────────────────
# 监控器本体（三路独立阈值 + 响应矩阵）
# ──────────────────────────────────────────────────────────────────────────────

# 默认差异化响应矩阵（§29.5：feature critical→降级，concept/label critical→重训）
_DEFAULT_RESPONSE_MATRIX: Final[dict[tuple[DriftChannel, DriftSeverity], DriftResponse]] = {
    (DriftChannel.FEATURE, DriftSeverity.WARN): DriftResponse.ALERT,
    (DriftChannel.FEATURE, DriftSeverity.CRITICAL): DriftResponse.DEGRADE,
    (DriftChannel.CONCEPT, DriftSeverity.WARN): DriftResponse.ALERT,
    (DriftChannel.CONCEPT, DriftSeverity.CRITICAL): DriftResponse.RETRAIN,
    (DriftChannel.LABEL, DriftSeverity.WARN): DriftResponse.ALERT,
    (DriftChannel.LABEL, DriftSeverity.CRITICAL): DriftResponse.RETRAIN,
}

_DEFAULT_THRESHOLDS: Final[dict[DriftChannel, ChannelThresholds]] = {
    DriftChannel.FEATURE: ChannelThresholds(),
    DriftChannel.CONCEPT: ChannelThresholds(),
    DriftChannel.LABEL: ChannelThresholds(),
}


class DistributionDriftMonitor:
    """三路分布漂移监控器（MOD-FBL-001）。

    用法：
        mon = DistributionDriftMonitor()
        rep = mon.check_feature(ref_train_feature, cur_online_feature)
        if rep.response == DriftResponse.DEGRADE: ...  # 执行归装配批
    """

    def __init__(
        self,
        thresholds: dict[DriftChannel, ChannelThresholds] | None = None,
        response_matrix: dict[tuple[DriftChannel, DriftSeverity], DriftResponse] | None = None,
        buckets: int = 10,
    ) -> None:
        if buckets < 2:
            raise DistributionDriftError("buckets 须 ≥ 2")
        merged = dict(_DEFAULT_THRESHOLDS)
        if thresholds:
            merged.update(thresholds)
        self._thresholds = merged
        self._response_matrix = dict(_DEFAULT_RESPONSE_MATRIX)
        if response_matrix:
            self._response_matrix.update(response_matrix)
        self._buckets = buckets

    def check(
        self,
        channel: DriftChannel,
        reference: np.ndarray | list[float],
        current: np.ndarray | list[float],
    ) -> DriftReport:
        """单通道三路度量 + 阈值判定 + 响应映射。"""
        if not isinstance(channel, DriftChannel):
            raise DistributionDriftError(f"未知漂移通道: {channel!r}")
        th = self._thresholds[channel]
        values = {
            "psi": psi(reference, current, buckets=self._buckets),
            "kl": kl_divergence(reference, current, buckets=self._buckets),
            "mdd": mdd(reference, current),
        }
        severity = DriftSeverity.NONE
        if values["psi"] >= th.psi_critical or values["kl"] >= th.kl_critical or values["mdd"] >= th.mdd_critical:
            severity = DriftSeverity.CRITICAL
        elif values["psi"] >= th.psi_warn or values["kl"] >= th.kl_warn or values["mdd"] >= th.mdd_warn:
            severity = DriftSeverity.WARN
        detected = severity != DriftSeverity.NONE
        response = (
            self._response_matrix.get((channel, severity), DriftResponse.NONE) if detected else DriftResponse.NONE
        )
        detail = (
            f"{channel.value}: psi={values['psi']:.4f}(warn={th.psi_warn},crit={th.psi_critical}) "
            f"kl={values['kl']:.4f}(warn={th.kl_warn},crit={th.kl_critical}) "
            f"mdd={values['mdd']:.4f}(warn={th.mdd_warn},crit={th.mdd_critical}) "
            f"→ {severity.value}/{response.value}"
        )
        return DriftReport(
            channel=channel,
            metric_values=values,
            drift_detected=detected,
            severity=severity,
            response=response,
            detail=detail,
        )

    def check_feature(self, reference: np.ndarray | list[float], current: np.ndarray | list[float]) -> DriftReport:
        """特征漂移（模型输入分布，事前预警）。"""
        return self.check(DriftChannel.FEATURE, reference, current)

    def check_concept(self, reference: np.ndarray | list[float], current: np.ndarray | list[float]) -> DriftReport:
        """概念漂移（预测输出分布，事前预警）。"""
        return self.check(DriftChannel.CONCEPT, reference, current)

    def check_label(self, reference: np.ndarray | list[float], current: np.ndarray | list[float]) -> DriftReport:
        """标签漂移（标签分布，事前预警）。"""
        return self.check(DriftChannel.LABEL, reference, current)

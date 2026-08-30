# [BLUEPRINT] MOD-ML-023 | docs/03_modules/_domain_machine_learning_train/experiment_anomaly_detector/blueprint.md
# [MODULE] zephyr.ml_train.experiment_anomaly_detector
# [DOMAIN] D_ML_TRAIN
# [DEPENDENCIES] zephyr.shared.foundation.errors(ZephyrBaseError)（纯 stdlib，无 numpy/pandas 依赖）
# [CONSUMERS] ml_train 实验跟踪巡检/ai_operator（实验指标序列注入；异常报告供告警与 retrain 工单消费）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 纯函数零 IO；按 (experiment_id, metric_name) 分组后 ts 升序稳定排序检测；rolling z-score 只用当前点之前历史窗（防前视）；CUSUM 双侧基线取首 z_window 个点，基线恒定（sigma=0）时漂移检测让位突变检测；停滞按 higher_is_better 方向判定改进；非有限值(nan/inf)记 critical 突变且不进统计窗；同输入必同输出
# [MODIFY-GUARD] 候选转正 CAND-RES-006（battle_map_01_research_incubation §BM-RES-02-C）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ExperimentAnomalyError(ZA-MLT-0015)——配置非法时抛（消息不拼路径，上下文入 details）
# [TESTS] tests/ml_train/test_experiment_anomaly_detector.py
# [A_module] module_id=MOD-ML-023 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
ExperimentAnomalyDetector — 实验指标异常检测（MOD-ML-023）。

CAND-RES-006 转正（2026-08-30 候选核销批桶B，P2）：ml_train 域实验指标
（loss / IC / sharpe 等）异常监控空白补齐——实验指标序列注入，输出结构化
异常报告供巡检/告警消费。

三类检测器（逐 (experiment_id, metric_name) 序列独立运行）
------------------------------------------------------------
1. **突变 spike**：rolling z-score——当前点相对此前 ``z_window`` 点历史窗的
   z 值（防前视：历史窗不含当前点）；|z| >= z_critical 记 critical，
   >= z_warn 记 warn；历史窗恒定（std=0）后任何偏离记 z=±inf（确定性突变）。
   非有限值（nan/inf，loss 爆炸典型形态）直接记 critical 突变且不进统计窗。
2. **漂移 drift**：双侧 CUSUM——基线取序列首 ``z_window`` 个点估计 mu0/sigma0，
   其后逐点 z 标准化累积：``S+ = max(0, S+ + z - k)`` / ``S- = min(0, S- + z + k)``；
   越决策阈 h 出一次报告并复位该侧累积量（防同段漂移刷屏）；超过 2h 升 critical。
   基线恒定（sigma0=0）时本检测器让位突变检测（头注 INVARIANTS 声明）。
3. **停滞 stagnation**：按 ``higher_is_better`` 方向跟踪历史最优，连续
   ``stagnation_n`` 次改进 < ``stagnation_eps`` 记 warn，达 2N 升 critical
   （各报一次，计数继续不重复刷报）。

严重度封闭集：warn / critical。报告按 (experiment_id, metric_name, ts,
anomaly_type) 确定性排序输出。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: points 参数
#   fields: 参数 points，类型注解 Sequence[ExperimentMetricPoint]
#   code: experiment_anomaly_detector.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: config 参数
#   fields: 参数 config，类型注解 AnomalyDetectionConfig | None
#   code: experiment_anomaly_detector.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① detect_experiment_anomalies
#   name_en: detect_experiment_anomalies
#   intro: 实验指标异常检测主入口（纯函数零 IO）。
#   desc: 实验指标异常检测主入口（纯函数零 IO）。 Parameters ---------- points : 实验指标序列（experiment_id / metric_name /…；源码 L374-L405
#   inputs: points config
#   outputs: list[MetricAnomalyReport]
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: list[MetricAnomalyReport]
#   name_en: list[MetricAnomalyReport]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: ml_train 实验跟踪巡检/ai_operator（实验指标序列注入；异常报告供告警与 retrain 工单消费）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Final, Sequence

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "ANOMALY_DRIFT",
    "ANOMALY_SPIKE",
    "ANOMALY_STAGNATION",
    "DEFAULT_CUSUM_H",
    "DEFAULT_CUSUM_K",
    "DEFAULT_MIN_WARMUP",
    "DEFAULT_STAGNATION_EPS",
    "DEFAULT_STAGNATION_N",
    "DEFAULT_Z_CRITICAL",
    "DEFAULT_Z_WARN",
    "DEFAULT_Z_WINDOW",
    "SEVERITY_CRITICAL",
    "SEVERITY_WARN",
    "AnomalyDetectionConfig",
    "MetricAnomalyReport",
    "ExperimentAnomalyError",
    "ExperimentMetricPoint",
    "detect_experiment_anomalies",
]

#: 异常类型封闭集
ANOMALY_SPIKE: Final = "spike"
ANOMALY_DRIFT: Final = "drift"
ANOMALY_STAGNATION: Final = "stagnation"
#: 严重度封闭集
SEVERITY_WARN: Final = "warn"
SEVERITY_CRITICAL: Final = "critical"

DEFAULT_Z_WINDOW: Final = 20
DEFAULT_Z_WARN: Final = 3.0
DEFAULT_Z_CRITICAL: Final = 5.0
DEFAULT_CUSUM_K: Final = 0.5
DEFAULT_CUSUM_H: Final = 5.0
DEFAULT_STAGNATION_N: Final = 10
DEFAULT_STAGNATION_EPS: Final = 1e-4
DEFAULT_MIN_WARMUP: Final = 5


class ExperimentAnomalyError(ZephyrBaseError):
    """实验异常检测配置/输入契约违反（Fail-Closed）。"""

    error_code = "ZA-MLT-0015"


@dataclass(frozen=True, slots=True)
class ExperimentMetricPoint:
    """实验指标采样点（frozen）。ts 只需支持组内升序排序（序号或 epoch 秒）。"""

    experiment_id: str
    metric_name: str
    value: float
    ts: int


@dataclass(frozen=True, slots=True)
class AnomalyDetectionConfig:
    """检测配置（frozen）。

    - z_window: rolling z-score 历史窗长，兼作 CUSUM 基线窗长
    - z_warn / z_critical: 突变 warn/critical 阈值（|z|）
    - cusum_k / cusum_h: CUSUM 参考值/决策阈（以基线 sigma 为单位）
    - stagnation_n / stagnation_eps: 停滞判定——连续 N 次改进 < epsilon
    - higher_is_better: 指标方向（IC/sharpe=True，loss=False 分拨调用）
    - min_warmup: 突变检测最小历史点数（窗不足不判，防冷启动误报）
    """

    z_window: int = DEFAULT_Z_WINDOW
    z_warn: float = DEFAULT_Z_WARN
    z_critical: float = DEFAULT_Z_CRITICAL
    cusum_k: float = DEFAULT_CUSUM_K
    cusum_h: float = DEFAULT_CUSUM_H
    stagnation_n: int = DEFAULT_STAGNATION_N
    stagnation_eps: float = DEFAULT_STAGNATION_EPS
    higher_is_better: bool = True
    min_warmup: int = DEFAULT_MIN_WARMUP


@dataclass(frozen=True, slots=True)
class MetricAnomalyReport:
    """单条异常报告（frozen）。

    evidence 为结构化证据值：突变含 z_score/window，漂移含 cusum_stat/direction，
    停滞含 run_length/best/epsilon；非有限值突变含 reason=non_finite_value。
    """

    experiment_id: str
    metric_name: str
    anomaly_type: str
    severity: str
    ts: int
    evidence: dict[str, object]


def _validate_config(cfg: AnomalyDetectionConfig) -> None:
    """配置契约校验（Fail-Closed，上下文入 details）。"""
    if cfg.z_window < 2:
        raise ExperimentAnomalyError("配置非法：z_window 必须 >= 2", details={"z_window": cfg.z_window})
    if cfg.z_warn <= 0.0 or cfg.z_critical < cfg.z_warn:
        raise ExperimentAnomalyError(
            "配置非法：需 0 < z_warn <= z_critical",
            details={"z_warn": cfg.z_warn, "z_critical": cfg.z_critical},
        )
    _validate_cusum_and_stagnation(cfg)


def _validate_cusum_and_stagnation(cfg: AnomalyDetectionConfig) -> None:
    """CUSUM 与停滞参数契约校验（拆自 _validate_config，降循环复杂度）。"""
    if cfg.cusum_k <= 0.0 or cfg.cusum_h <= 0.0:
        raise ExperimentAnomalyError(
            "配置非法：cusum_k / cusum_h 必须 > 0",
            details={"cusum_k": cfg.cusum_k, "cusum_h": cfg.cusum_h},
        )
    if cfg.stagnation_n < 1:
        raise ExperimentAnomalyError(
            "配置非法：stagnation_n 必须 >= 1",
            details={"stagnation_n": cfg.stagnation_n},
        )
    if cfg.stagnation_eps < 0.0:
        raise ExperimentAnomalyError(
            "配置非法：stagnation_eps 必须 >= 0",
            details={"stagnation_eps": cfg.stagnation_eps},
        )
    if cfg.min_warmup < 2 or cfg.min_warmup > cfg.z_window:
        raise ExperimentAnomalyError(
            "配置非法：min_warmup 必须落在 [2, z_window]",
            details={"min_warmup": cfg.min_warmup, "z_window": cfg.z_window},
        )


def _report(
    key: tuple[str, str],
    anomaly_type: str,
    severity: str,
    ts: int,
    evidence: dict[str, object],
) -> MetricAnomalyReport:
    """组装异常报告（组键拆回 experiment_id / metric_name）。"""
    return MetricAnomalyReport(
        experiment_id=key[0],
        metric_name=key[1],
        anomaly_type=anomaly_type,
        severity=severity,
        ts=ts,
        evidence=evidence,
    )


def _z_score(x: float, window: list[float]) -> float:
    """当前点相对历史窗的总体口径 z 值；窗恒定（std=0）时偏离记 ±inf。"""
    n = len(window)
    mean = sum(window) / n
    var = sum((v - mean) ** 2 for v in window) / n
    std = math.sqrt(var)
    if std <= 0.0:
        if x == mean:
            return 0.0
        return math.copysign(math.inf, x - mean)
    return (x - mean) / std


def _detect_spikes(
    key: tuple[str, str],
    xs: list[float],
    ts: list[int],
    cfg: AnomalyDetectionConfig,
) -> list[MetricAnomalyReport]:
    """突变检测：rolling z-score（历史窗不含当前点，防前视）。"""
    reports: list[MetricAnomalyReport] = []
    hist: list[float] = []
    for x, t in zip(xs, ts, strict=True):
        if not math.isfinite(x):
            reports.append(_report(key, ANOMALY_SPIKE, SEVERITY_CRITICAL, t, {"reason": "non_finite_value"}))
            continue
        if len(hist) >= cfg.min_warmup:
            window = hist[-cfg.z_window :]
            z = _z_score(x, window)
            if abs(z) >= cfg.z_warn:
                severity = SEVERITY_CRITICAL if abs(z) >= cfg.z_critical else SEVERITY_WARN
                reports.append(_report(key, ANOMALY_SPIKE, severity, t, {"z_score": z, "window": len(window)}))
        hist.append(x)
    return reports


def _drift_severity(stat: float, cfg: AnomalyDetectionConfig) -> str:
    """漂移严重度：超过 2 倍决策阈升 critical。"""
    if stat > 2.0 * cfg.cusum_h:
        return SEVERITY_CRITICAL
    return SEVERITY_WARN


def _detect_drift(
    key: tuple[str, str],
    xs: list[float],
    ts: list[int],
    cfg: AnomalyDetectionConfig,
) -> list[MetricAnomalyReport]:
    """漂移检测：双侧 CUSUM（基线=首 z_window 个有限点；越阈出报并复位该侧）。"""
    finite = [(x, t) for x, t in zip(xs, ts, strict=True) if math.isfinite(x)]
    if len(finite) < cfg.z_window + 1:
        return []
    base = [x for x, _ in finite[: cfg.z_window]]
    mu = sum(base) / len(base)
    sigma = math.sqrt(sum((v - mu) ** 2 for v in base) / len(base))
    if sigma <= 0.0:
        return []
    reports: list[MetricAnomalyReport] = []
    s_pos = 0.0
    s_neg = 0.0
    for x, t in finite[cfg.z_window :]:
        z = (x - mu) / sigma
        s_pos = max(0.0, s_pos + z - cfg.cusum_k)
        s_neg = min(0.0, s_neg + z + cfg.cusum_k)
        if s_pos > cfg.cusum_h:
            reports.append(
                _report(key, ANOMALY_DRIFT, _drift_severity(s_pos, cfg), t, {"cusum_stat": s_pos, "direction": "up"})
            )
            s_pos = 0.0
        if s_neg < -cfg.cusum_h:
            reports.append(
                _report(
                    key, ANOMALY_DRIFT, _drift_severity(-s_neg, cfg), t, {"cusum_stat": -s_neg, "direction": "down"}
                )
            )
            s_neg = 0.0
    return reports


def _improvement(best: float | None, x: float, higher_is_better: bool) -> float:
    """相对历史最优的改进量（按指标方向；首点记 +inf）。"""
    if best is None:
        return math.inf
    if higher_is_better:
        return x - best
    return best - x


def _detect_stagnation(
    key: tuple[str, str],
    xs: list[float],
    ts: list[int],
    cfg: AnomalyDetectionConfig,
) -> list[MetricAnomalyReport]:
    """停滞检测：连续 stagnation_n 次改进 < epsilon 记 warn，达 2N 升 critical（各报一次）。"""
    reports: list[MetricAnomalyReport] = []
    best: float | None = None
    run = 0
    for x, t in zip(xs, ts, strict=True):
        if not math.isfinite(x):
            continue
        if _improvement(best, x, cfg.higher_is_better) >= cfg.stagnation_eps:
            best = x if best is None else (max(best, x) if cfg.higher_is_better else min(best, x))
            run = 0
            continue
        run += 1
        if run == cfg.stagnation_n:
            reports.append(_stagnation_report(key, t, SEVERITY_WARN, run, best, cfg))
        if run == 2 * cfg.stagnation_n:
            reports.append(_stagnation_report(key, t, SEVERITY_CRITICAL, run, best, cfg))
    return reports


def _stagnation_report(
    key: tuple[str, str],
    ts: int,
    severity: str,
    run: int,
    best: float | None,
    cfg: AnomalyDetectionConfig,
) -> MetricAnomalyReport:
    """组装停滞报告（证据：连续未改进次数/历史最优/判定 epsilon）。"""
    return _report(
        key,
        ANOMALY_STAGNATION,
        severity,
        ts,
        {"run_length": run, "best": best, "epsilon": cfg.stagnation_eps},
    )


def _group_points(points: Sequence[ExperimentMetricPoint]) -> dict[tuple[str, str], tuple[list[float], list[int]]]:
    """按 (experiment_id, metric_name) 分组，组内 ts 升序稳定排序。"""
    grouped: dict[tuple[str, str], list[ExperimentMetricPoint]] = {}
    for p in points:
        grouped.setdefault((p.experiment_id, p.metric_name), []).append(p)
    out: dict[tuple[str, str], tuple[list[float], list[int]]] = {}
    for key, rows in grouped.items():
        ordered = sorted(rows, key=lambda r: r.ts)
        out[key] = ([r.value for r in ordered], [r.ts for r in ordered])
    return out


def detect_experiment_anomalies(
    points: Sequence[ExperimentMetricPoint],
    config: AnomalyDetectionConfig | None = None,
) -> list[MetricAnomalyReport]:
    """实验指标异常检测主入口（纯函数零 IO）。

    Parameters
    ----------
    points : 实验指标序列（experiment_id / metric_name / value / ts），
        可跨实验跨指标混合乱序注入，组内按 ts 升序检测。
    config : 检测配置；None 用默认（z 3/5、CUSUM 0.5/5、停滞 10 次/1e-4）。

    Returns
    -------
    list[MetricAnomalyReport] —— 按 (experiment_id, metric_name, ts, anomaly_type)
    确定性排序；空输入返回空列表。

    Raises
    ------
    ExperimentAnomalyError(ZA-MLT-0015) —— 配置非法（Fail-Closed）。
    """
    cfg = config if config is not None else AnomalyDetectionConfig()
    _validate_config(cfg)
    series = _group_points(points)
    reports: list[MetricAnomalyReport] = []
    for key in sorted(series):
        xs, ts = series[key]
        reports.extend(_detect_spikes(key, xs, ts, cfg))
        reports.extend(_detect_drift(key, xs, ts, cfg))
        reports.extend(_detect_stagnation(key, xs, ts, cfg))
    reports.sort(key=lambda r: (r.experiment_id, r.metric_name, r.ts, r.anomaly_type))
    return reports

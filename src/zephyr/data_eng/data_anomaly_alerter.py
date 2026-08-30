# [BLUEPRINT] MOD-DATENG-001 | docs/03_modules/_domain_data_eng/data_anomaly_alerter/blueprint.md
# [MODULE] zephyr.data_eng.data_anomaly_alerter
# [DOMAIN] D_DATA_ENG
# [DEPENDENCIES] numpy(标准科学栈); zephyr.data.alerter(惰性, 默认告警通道可注入替代)
# [CONSUMERS] 运行时装配批（数据质量门控事件消费 / B13-04305 因子可用性 / B13-04309 信号退化复用本件路由）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 判定核心纯内存无IO不触网不触库; 四路检测确定性; 输入非法Fail-Closed; 同源同因merge_window内合并不重复路由; 维护窗口静默只留痕; 通道异常吞掉不阻断判定
# [MODIFY-GUARD] docs/03_modules/_domain_data_eng/data_anomaly_alerter/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DataAnomalyAlerterError(占位 ZA-DATENG-UNREGISTERED-ANOMALY-ALERTER)——空输入/长度不齐/阈值非正/信号值低于阈值时抛
# [TESTS] tests/zephyr/data/test_data_anomaly_alerter.py
# [A_module] module_id=MOD-DATENG-001 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
DataAnomalyAlerter — 数据异常告警器（MOD-DATENG-001）。

B13-04267（AUD-DRAFT-001-DIGEST P1 波 W-P1-24，CAND-DATENG-004，A3数据架构
§17.1 D-DATA-112）：多维度数据异常检测（跳变 z-score / 缺失率 / 量价背离 /
跨源偏差）+ 告警分级（AL-P1~P4）+ 路由复用 zephyr.data.alerter（DI 注入）+
抑制规则（同源同因合并 / 维护窗口静默）+ 质量门控事件输出。

查重分工（蓝图 §0）：cleaning_anomaly_engine（MOD-DATA_ENG）= OHLCV 帧内
五维检测+自动修复闭环；本件**不做修复**，检出即告警，检测维度与输出去向
均不同。告警通道不重建——经 alert_sink 依赖注入复用 Alerter（与
integrity_checker "告警通过alerter" 同口径）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: closes 参数
#   fields: 参数 closes，类型注解 np.ndarray | list[float]
#   code: data_anomaly_alerter.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: symbol 参数
#   fields: 参数 symbol，类型注解 str
#   code: data_anomaly_alerter.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: z_threshold 参数
#   fields: 参数 z_threshold，类型注解 float
#   code: data_anomaly_alerter.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: window 参数
#   fields: 参数 window，类型注解 int
#   code: data_anomaly_alerter.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① detect_price_jumps
#   name_en: detect_price_jumps
#   intro: 价格跳变检测：对数收益相对滚动窗口的 z-score，|z|≥阈值 → 信号。
#   desc: 价格跳变检测：对数收益相对滚动窗口的 z-score，|z|≥阈值 → 信号。；源码 L224-L256
#   inputs: closes symbol z_threshold window
#   outputs: list[AnomalySignal]
# - id: A2
#   name_zh: ② detect_missing_rate
#   name_en: detect_missing_rate
#   intro: 缺失率检测：缺失率=1−actual/expected ≥ warn → 信号。
#   desc: 缺失率检测：缺失率=1−actual/expected ≥ warn → 信号。；源码 L259-L283
#   inputs: expected actual symbol warn
#   outputs: list[AnomalySignal]
# - id: A3
#   name_zh: ③ detect_volume_price_divergence
#   name_en: detect_volume_price_divergence
#   intro: 量价背离检测：滚动窗口收盘价与成交量相关系数 < 阈值 → 信号。
#   desc: 量价背离检测：滚动窗口收盘价与成交量相关系数 < 阈值 → 信号。；源码 L286-L315
#   inputs: closes volumes symbol window corr_threshold
#   outputs: list[AnomalySignal]
# - id: A4
#   name_zh: ④ detect_cross_source_deviation
#   name_en: detect_cross_source_deviation
#   intro: 跨源偏差检测：双通道同标的价偏差 |Δ|/ref×10⁴ bps 最大值超容差 → 信号。
#   desc: 跨源偏差检测：双通道同标的价偏差 |Δ|/ref×10⁴ bps 最大值超容差 → 信号。；源码 L318-L345
#   inputs: primary secondary symbol tolerance_bps
#   outputs: list[AnomalySignal]
# - id: A5
#   name_zh: ⑤ DataAnomalyAlerter
#   name_en: DataAnomalyAlerter
#   intro: 数据异常告警器（MOD-DATENG-001）。
#   desc: 数据异常告警器（MOD-DATENG-001）。 用法： alerter = DataAnomalyAlerter(alert_sink=my_sink, merge_windo…；公共方法（定义序）: grade…
#   inputs: alert_sink merge_window_sec maintenance_windows
#   outputs: 返回值
#   （注：A5 之后另有 7 个公共定义未列入（含 7 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: list[AnomalySignal]
#   name_en: list[AnomalySignal]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 运行时装配批（数据质量门控事件消费 / B13-04305 因子可用性 / B13-04309 信号退化复用本件路由）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> O1
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Final

import numpy as np

_log = logging.getLogger(__name__)

__all__: Final = [
    "AlertGrade",
    "AnomalyAlert",
    "AnomalyKind",
    "AnomalySignal",
    "DataAnomalyAlerter",
    "DataAnomalyAlerterError",
    "MaintenanceWindow",
    "QualityGateEvent",
    "detect_cross_source_deviation",
    "detect_missing_rate",
    "detect_price_jumps",
    "detect_volume_price_divergence",
]


class DataAnomalyAlerterError(Exception):
    """数据异常告警器输入非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-DATENG-UNREGISTERED-ANOMALY-ALERTER。
    """


class AnomalyKind(str, Enum):
    """四路异常检测类型。"""

    PRICE_JUMP = "price_jump"
    MISSING_RATE = "missing_rate"
    VOLUME_PRICE_DIVERGENCE = "volume_price_divergence"
    CROSS_SOURCE_DEVIATION = "cross_source_deviation"


class AlertGrade(str, Enum):
    """告警分级（AL-P1 最重 … AL-P4 最轻）。"""

    P1 = "AL-P1"
    P2 = "AL-P2"
    P3 = "AL-P3"
    P4 = "AL-P4"


# 分级 → zephyr.data.alerter 通道级别映射（ERROR/CRITICAL 触达人，WARN/INFO 仅日志）
_GRADE_TO_ROUTE_LEVEL: Final[dict[AlertGrade, str]] = {
    AlertGrade.P1: "CRITICAL",
    AlertGrade.P2: "ERROR",
    AlertGrade.P3: "WARN",
    AlertGrade.P4: "INFO",
}


@dataclass(frozen=True)
class AnomalySignal:
    """单条异常信号（检测器产出，未分级）。"""

    kind: AnomalyKind
    symbol: str
    metric_value: float  # 观测值（z 值 / 缺失率 / 相关系数 / 偏差 bps）
    threshold: float  # 触发阈值
    detail: str = ""


@dataclass(frozen=True)
class AnomalyAlert:
    """分级+抑制后的告警。"""

    signal: AnomalySignal
    grade: AlertGrade
    silenced: bool  # 维护窗口静默
    merged_count: int  # 同源同因合并计数（含本次）
    dedup_key: str


@dataclass(frozen=True)
class QualityGateEvent:
    """质量门控事件（接数据质量门控消费）。"""

    kind: AnomalyKind
    severity: str  # AlertGrade.value
    symbol: str
    metric_value: float
    message: str


@dataclass(frozen=True)
class MaintenanceWindow:
    """维护窗口（窗口内告警静默，仅留痕不路由）。"""

    start_utc: datetime
    end_utc: datetime
    reason: str = ""


# ──────────────────────────────────────────────────────────────────────────────
# 四路检测（纯函数）
# ──────────────────────────────────────────────────────────────────────────────


def _as_float_array(values: np.ndarray | list[float], name: str) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 1 or arr.size == 0:
        raise DataAnomalyAlerterError(f"{name} 须为一维非空序列")
    if not np.all(np.isfinite(arr)):
        raise DataAnomalyAlerterError(f"{name} 含非有限值")
    return arr


def detect_price_jumps(
    closes: np.ndarray | list[float],
    symbol: str,
    z_threshold: float = 4.0,
    window: int = 20,
) -> list[AnomalySignal]:
    """价格跳变检测：对数收益相对滚动窗口的 z-score，|z|≥阈值 → 信号。"""
    arr = _as_float_array(closes, "closes")
    if z_threshold <= 0:
        raise DataAnomalyAlerterError("z_threshold 须为正")
    if arr.size < window + 2:
        raise DataAnomalyAlerterError(f"closes 长度 {arr.size} 不足以滚动窗口 {window} 计算")
    if np.any(arr <= 0):
        raise DataAnomalyAlerterError("closes 须为正价格序列")
    log_ret = np.diff(np.log(arr))
    # 末日收益相对前 window 根收益的 z-score（事前预警口径：只用历史窗）
    hist = log_ret[-window - 1 : -1]
    mu = float(np.mean(hist))
    sigma = float(np.std(hist))
    if sigma <= 0:
        return []  # 零波动序列无跳变语义（如长期一字板），不告警
    z = abs(float(log_ret[-1]) - mu) / sigma
    if z < z_threshold:
        return []
    return [
        AnomalySignal(
            kind=AnomalyKind.PRICE_JUMP,
            symbol=symbol,
            metric_value=z,
            threshold=z_threshold,
            detail=f"末日对数收益 {float(log_ret[-1]):.4f} vs 滚动μ={mu:.4f} σ={sigma:.4f}",
        )
    ]


def detect_missing_rate(
    expected: int,
    actual: int,
    symbol: str,
    warn: float = 0.05,
) -> list[AnomalySignal]:
    """缺失率检测：缺失率=1−actual/expected ≥ warn → 信号。"""
    if expected <= 0:
        raise DataAnomalyAlerterError("expected 须为正整数")
    if actual < 0 or actual > expected:
        raise DataAnomalyAlerterError("actual 须落在 [0, expected]")
    if warn <= 0 or warn >= 1:
        raise DataAnomalyAlerterError("warn 阈值须落在 (0,1)")
    rate = 1.0 - actual / expected
    if rate < warn:
        return []
    return [
        AnomalySignal(
            kind=AnomalyKind.MISSING_RATE,
            symbol=symbol,
            metric_value=rate,
            threshold=warn,
            detail=f"缺失 {expected - actual}/{expected} = {rate:.2%}",
        )
    ]


def detect_volume_price_divergence(
    closes: np.ndarray | list[float],
    volumes: np.ndarray | list[float],
    symbol: str,
    window: int = 20,
    corr_threshold: float = 0.0,
) -> list[AnomalySignal]:
    """量价背离检测：滚动窗口收盘价与成交量相关系数 < 阈值 → 信号。"""
    c = _as_float_array(closes, "closes")
    v = _as_float_array(volumes, "volumes")
    if c.size != v.size:
        raise DataAnomalyAlerterError("closes 与 volumes 长度不齐")
    if c.size < window:
        raise DataAnomalyAlerterError(f"序列长度 {c.size} 不足窗口 {window}")
    cw = c[-window:]
    vw = v[-window:]
    if float(np.std(cw)) <= 0 or float(np.std(vw)) <= 0:
        return []  # 零方差无相关语义（一字板/无成交），不告警
    corr = float(np.corrcoef(cw, vw)[0, 1])
    if corr >= corr_threshold:
        return []
    return [
        AnomalySignal(
            kind=AnomalyKind.VOLUME_PRICE_DIVERGENCE,
            symbol=symbol,
            metric_value=corr,
            threshold=corr_threshold,
            detail=f"窗口 {window} 价量相关 {corr:.3f} < {corr_threshold}",
        )
    ]


def detect_cross_source_deviation(
    primary: np.ndarray | list[float],
    secondary: np.ndarray | list[float],
    symbol: str,
    tolerance_bps: float = 30.0,
) -> list[AnomalySignal]:
    """跨源偏差检测：双通道同标的价偏差 |Δ|/ref×10⁴ bps 最大值超容差 → 信号。"""
    p = _as_float_array(primary, "primary")
    s = _as_float_array(secondary, "secondary")
    if p.size != s.size:
        raise DataAnomalyAlerterError("primary 与 secondary 长度不齐")
    if tolerance_bps <= 0:
        raise DataAnomalyAlerterError("tolerance_bps 须为正")
    if np.any(p <= 0):
        raise DataAnomalyAlerterError("primary 须为正价格序列")
    dev_bps = np.abs(s - p) / p * 1e4
    max_dev = float(np.max(dev_bps))
    if max_dev <= tolerance_bps:
        return []
    return [
        AnomalySignal(
            kind=AnomalyKind.CROSS_SOURCE_DEVIATION,
            symbol=symbol,
            metric_value=max_dev,
            threshold=tolerance_bps,
            detail=f"最大跨源偏差 {max_dev:.1f}bps（{int(np.argmax(dev_bps))} 处）",
        )
    ]


# ──────────────────────────────────────────────────────────────────────────────
# 告警器本体（分级 + 抑制 + 路由 + 质量门控事件）
# ──────────────────────────────────────────────────────────────────────────────

# 分级映射：超出比 ratio=metric/threshold
_GRADE_RATIOS: Final[tuple[tuple[float, AlertGrade], ...]] = (
    (10.0, AlertGrade.P1),
    (5.0, AlertGrade.P2),
    (2.0, AlertGrade.P3),
    (1.0, AlertGrade.P4),
)


def _default_alert_sink(
    task_id: str, error: str, level: str, source: str | None = None, extra: dict | None = None
) -> bool:
    """默认告警通道：惰性复用 zephyr.data.alerter.Alerter（可注入替代）。"""
    from zephyr.data.alerter import Alerter  # 惰性：避免模块级依赖与文件副作用

    return Alerter().notify(task_id, error, level=level, source=source, extra=extra)


class DataAnomalyAlerter:
    """数据异常告警器（MOD-DATENG-001）。

    用法：
        alerter = DataAnomalyAlerter(alert_sink=my_sink, merge_window_sec=3600)
        alerts, gate_events = alerter.detect_and_evaluate(
            closes=closes, volumes=volumes, expected=250, actual=240,
            symbol="600519.SH", source="tdx", now_utc=now,
        )
    """

    def __init__(
        self,
        alert_sink: Callable[..., bool] | None = None,
        merge_window_sec: int = 3600,
        maintenance_windows: tuple[MaintenanceWindow, ...] = (),
    ) -> None:
        if merge_window_sec <= 0:
            raise DataAnomalyAlerterError("merge_window_sec 须为正")
        self._alert_sink = alert_sink if alert_sink is not None else _default_alert_sink
        self._merge_window_sec = merge_window_sec
        self._maintenance_windows = maintenance_windows
        # dedup_key -> (上次路由 UTC 时间戳, 合并计数)
        self._dedup_state: dict[str, tuple[float, int]] = {}

    # ── 分级 ──

    @staticmethod
    def grade(signal: AnomalySignal) -> AlertGrade:
        """按超出比 metric/threshold 映射 AL-P1~P4（低于阈值 Fail-Closed）。"""
        if signal.threshold <= 0:
            raise DataAnomalyAlerterError("signal.threshold 须为正")
        ratio = signal.metric_value / signal.threshold
        if ratio < 1.0:
            raise DataAnomalyAlerterError(f"信号值 {signal.metric_value} 低于阈值 {signal.threshold}，不应进入分级")
        for bar, grade in _GRADE_RATIOS:
            if ratio >= bar:
                return grade
        return AlertGrade.P4

    # ── 抑制 ──

    def _is_silenced(self, now_utc: datetime) -> bool:
        for w in self._maintenance_windows:
            if w.start_utc <= now_utc <= w.end_utc:
                return True
        return False

    @staticmethod
    def _dedup_key(signal: AnomalySignal, source: str) -> str:
        return f"{source}|{signal.kind.value}|{signal.symbol}"

    # ── 评估（分级 + 抑制 + 路由 + 门控事件）──

    def evaluate(
        self,
        signals: list[AnomalySignal],
        now_utc: datetime | None = None,
        source: str = "data_eng",
    ) -> tuple[list[AnomalyAlert], list[QualityGateEvent]]:
        """信号 → 分级告警 + 质量门控事件；路由经 alert_sink（静默/合并不路由）。"""
        if now_utc is None:
            now_utc = datetime.now(timezone.utc)
        silenced = self._is_silenced(now_utc)
        alerts: list[AnomalyAlert] = []
        events: list[QualityGateEvent] = []
        for sig in signals:
            grade = self.grade(sig)  # Fail-Closed：低阈值信号在此拒绝
            key = self._dedup_key(sig, source)
            now_ts = now_utc.timestamp()
            last_ts, count = self._dedup_state.get(key, (0.0, 0))
            merged = now_ts - last_ts < self._merge_window_sec
            new_count = count + 1 if merged else 1
            self._dedup_state[key] = (now_ts, new_count)
            alerts.append(
                AnomalyAlert(
                    signal=sig,
                    grade=grade,
                    silenced=silenced,
                    merged_count=new_count,
                    dedup_key=key,
                )
            )
            events.append(
                QualityGateEvent(
                    kind=sig.kind,
                    severity=grade.value,
                    symbol=sig.symbol,
                    metric_value=sig.metric_value,
                    message=(
                        f"{sig.kind.value} {sig.symbol}: "
                        f"value={sig.metric_value:.4g} threshold={sig.threshold:.4g} "
                        f"grade={grade.value} merged={new_count} silenced={silenced} | {sig.detail}"
                    ),
                )
            )
            # 路由：维护窗口静默 / 合并窗口内重复 → 不路由（与 Alerter 冷却同哲学）
            if silenced or merged:
                continue
            try:
                self._alert_sink(
                    f"data_anomaly_{sig.kind.value}",
                    f"[{grade.value}] {sig.symbol} {sig.kind.value}: {sig.detail}",
                    level=_GRADE_TO_ROUTE_LEVEL[grade],
                    source=source,
                    extra={
                        "symbol": sig.symbol,
                        "metric_value": sig.metric_value,
                        "threshold": sig.threshold,
                        "grade": grade.value,
                    },
                )
            except Exception as exc:  # noqa: BLE001 — 通道异常不阻断判定（对齐 alerter 不变式）
                _log.error("告警通道路由异常（已吞掉）: %s", exc)
        return alerts, events

    # ── 一站式：四路检测 + 评估 ──

    def detect_and_evaluate(
        self,
        closes: np.ndarray | list[float] | None = None,
        volumes: np.ndarray | list[float] | None = None,
        expected: int | None = None,
        actual: int | None = None,
        primary: np.ndarray | list[float] | None = None,
        secondary: np.ndarray | list[float] | None = None,
        symbol: str = "",
        source: str = "data_eng",
        now_utc: datetime | None = None,
        z_threshold: float = 4.0,
        missing_warn: float = 0.05,
        corr_threshold: float = 0.0,
        tolerance_bps: float = 30.0,
    ) -> tuple[list[AnomalyAlert], list[QualityGateEvent]]:
        """四路检测 + 分级 + 抑制 + 路由一站式。未提供的检测路自动跳过。"""
        if not symbol:
            raise DataAnomalyAlerterError("symbol 不能为空")
        signals: list[AnomalySignal] = []
        if closes is not None:
            signals.extend(detect_price_jumps(closes, symbol, z_threshold=z_threshold))
            if volumes is not None:
                signals.extend(detect_volume_price_divergence(closes, volumes, symbol, corr_threshold=corr_threshold))
        if expected is not None and actual is not None:
            signals.extend(detect_missing_rate(expected, actual, symbol, warn=missing_warn))
        if primary is not None and secondary is not None:
            signals.extend(detect_cross_source_deviation(primary, secondary, symbol, tolerance_bps=tolerance_bps))
        if not signals:
            return [], []
        return self.evaluate(signals, now_utc=now_utc, source=source)

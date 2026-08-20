# [BLUEPRINT] MOD-BT-018 | docs/03_modules/_domain_backtest/decay_monitor/blueprint.md
# [MODULE] zephyr.backtest.services.decay_monitor
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-BT-017(scheduler) ; D-GOVERNANCE(策略治理)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 样本不足返回STABLE;指标值必须有限;update有状态evaluate无状态;级别取最严重
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidMetricError
# [TESTS] tests/backtest/test_decay_monitor.py
# [A_module] module_id=MOD-BT-018 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Decay Monitor — 策略衰减监控告警器 (MOD-BT-018)

跟踪策略性能指标随时间变化, 通过短期/长期均值对比和线性趋势检测识别衰减。
4级告警: STABLE → WARNING → DECAYING → CRITICAL。

蓝图: docs/03_modules/_domain_backtest/decay_monitor/blueprint.md
SSoT: depgraph MOD-BT-018
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 策略性能指标序列 float
#   fields: Sharpe/收益率/胜率等 单值update增量或序列evaluate批量
#   code: metric_value / metrics
# - id: I2
#   name: 衰减监控配置 DecayMonitorConfig frozen
#   fields: short_window=20 + long_window=60 + warning_threshold=0.15 + critical_threshold=0.30 + trend_window=30
#   code: DecayMonitorConfig L93-114
# 层: 算法
# - id: A1
#   name_zh: ① 样本充足性闸门
#   name_en: _analyze(样本检查段)
#   intro: 样本不够短期窗口就直接判STABLE不瞎报
#   desc: n<short_window返回STABLE报告 均值填充长短均值 样本为0补0.0（L218-234）
#   inputs: I1 I2
#   outputs: STABLE早退报告
#   invariant: 样本不足返回STABLE; 指标值必须有限(NaN/Inf报错)
# - id: A2
#   name_zh: ② 短长期均值衰减比
#   name_en: _analyze(衰减比段)
#   intro: 短期均值比长期均值掉了多少，正数就是衰减
#   desc: short=尾20均值 long=尾60均值 → decay_ratio=(long_mean-short_mean)/|long_mean| → 长期≈0时按短期符号给±1（L236-248）
#   inputs: I1 I2
#   outputs: decay_ratio+short/long_mean
# - id: A3
#   name_zh: ③ 最小二乘趋势斜率
#   name_en: _compute_slope
#   intro: 尾30个点线性拟合看指标在升还是在降
#   desc: x=arange(n) → slope=Σ(x-x̄)(y-ȳ)/Σ(x-x̄)² → n<2或分母≈0返回0（L250-252, L295-308）
#   inputs: I1 I2
#   outputs: trend_slope
# - id: A4
#   name_zh: ④ 4级告警判定
#   name_en: _analyze(级别判定段)
#   intro: 按衰减阈值和下降趋势综合定STABLE/WARNING/DECAYING/CRITICAL
#   desc: decay_ratio>30%或短期均值<0 → CRITICAL → >15%WARNING → 负斜率且幅度>5%均值DECAYING → worst取最严重（L254-293）
#   inputs: A1 A2 A3 I2
#   outputs: DecayLevel+报告message
#   invariant: 级别取最严重
# 层: 输出
# - id: O1
#   name_zh: 衰减分析报告 DecayReport
#   name_en: DecayReport
#   intro: 告警级别+衰减比+趋势斜率+样本数，供调度器和策略治理告警
#   invariant: 指标值必须有限; update有状态evaluate无状态
#   downstream: scheduler MOD-BT-017 ; 策略治理 D-GOVERNANCE
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I1 --> A2
# I2 --> A2
# I1 --> A3
# I2 --> A3
# A1 --> A4
# A2 --> A4
# A3 --> A4
# I2 --> A4
# A1 --> O1
# A4 --> O1
"""

from __future__ import annotations

import logging
from collections import deque
from dataclasses import dataclass
from enum import Enum

import numpy as np
import pandas as pd

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__ = [
    "DecayLevel",
    "DecayMonitorConfig",
    "DecayReport",
    "DecayMonitor",
    "InvalidMetricError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class DecayLevel(str, Enum):
    """衰减告警级别 (严重度递增)。"""

    STABLE = "STABLE"
    WARNING = "WARNING"
    DECAYING = "DECAYING"
    CRITICAL = "CRITICAL"

    @property
    def severity(self) -> int:
        # STABLE < DECAYING(趋势预警) < WARNING(衰减超阈值) < CRITICAL(严重衰减)
        return {"STABLE": 0, "DECAYING": 1, "WARNING": 2, "CRITICAL": 3}[self.value]

    @classmethod
    def worst(cls, levels: list[DecayLevel]) -> DecayLevel:
        if not levels:
            return cls.STABLE
        return max(levels, key=lambda lv: lv.severity)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class InvalidMetricError(ZephyrBaseError):
    """性能指标值非法(如非有限值)。"""

    error_code = "ZA-BT-0018"


# ──────────────────────────────────────────────────────────────────────────────
# 配置
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class DecayMonitorConfig:
    """衰减监控配置。"""

    short_window: int = 20  # 短期窗口
    long_window: int = 60  # 长期窗口
    warning_threshold: float = 0.15  # 衰减>15% → WARNING
    critical_threshold: float = 0.30  # 衰减>30% → CRITICAL
    trend_window: int = 30  # 趋势检测窗口

    def __post_init__(self) -> None:
        if self.short_window <= 0 or self.long_window <= 0:
            raise InvalidMetricError("windows must be > 0")
        if self.short_window >= self.long_window:
            raise InvalidMetricError("short_window must be < long_window")
        if not 0 < self.warning_threshold < self.critical_threshold <= 1:
            raise InvalidMetricError(
                f"require 0 < warning({self.warning_threshold}) < critical({self.critical_threshold}) <= 1"
            )
        if self.trend_window <= 0:
            raise InvalidMetricError("trend_window must be > 0")


# ──────────────────────────────────────────────────────────────────────────────
# 报告
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class DecayReport:
    """衰减分析报告。"""

    level: DecayLevel
    short_term_mean: float
    long_term_mean: float
    decay_ratio: float  # 正=衰减, 负=改善
    trend_slope: float  # 线性趋势斜率 (负=下降)
    samples: int  # 样本数
    message: str

    @property
    def is_decaying(self) -> bool:
        return self.level is not DecayLevel.STABLE


# ──────────────────────────────────────────────────────────────────────────────
# 衰减监控器
# ──────────────────────────────────────────────────────────────────────────────


class DecayMonitor:
    """策略衰减监控告警器——短期/长期均值对比+趋势检测。

    用法 (增量更新):
        monitor = DecayMonitor()
        for sharpe in daily_sharpe_series:
            report = monitor.update(sharpe)
            if report.level is DecayLevel.CRITICAL:
                # 发送告警

    用法 (批量评估):
        monitor = DecayMonitor()
        report = monitor.evaluate(pd.Series(daily_sharpe_list))

    Args:
        config: 监控配置
    """

    def __init__(self, config: DecayMonitorConfig | None = None) -> None:
        self._config = config or DecayMonitorConfig()
        self._history: deque[float] = deque(maxlen=self._config.long_window)

    @property
    def config(self) -> DecayMonitorConfig:
        return self._config

    @property
    def history(self) -> list[float]:
        return list(self._history)

    # ── 公开 API ──

    def update(self, metric_value: float) -> DecayReport:
        """增量更新: 添加一个性能指标值, 返回当前衰减报告。

        Args:
            metric_value: 性能指标值 (如 Sharpe/收益率/胜率)

        Returns:
            DecayReport

        Raises:
            InvalidMetricError: 值非有限 (NaN/Inf)
        """
        if not np.isfinite(metric_value):
            raise InvalidMetricError(f"metric_value must be finite, got {metric_value}")
        self._history.append(float(metric_value))
        return self._analyze(np.array(self._history))

    def evaluate(self, metrics: pd.Series | list[float]) -> DecayReport:
        """批量评估: 对性能指标序列进行一次性衰减分析。

        Args:
            metrics: 性能指标序列

        Returns:
            DecayReport

        Raises:
            InvalidMetricError: 含非有限值
        """
        values = np.asarray(metrics, dtype=float)
        if not np.all(np.isfinite(values)):
            raise InvalidMetricError("metrics contains non-finite values (NaN/Inf)")
        return self._analyze(values)

    def reset(self) -> None:
        """清空历史数据。"""
        self._history.clear()

    # ── 内部 ──

    def _analyze(self, values: np.ndarray) -> DecayReport:
        """分析性能序列, 返回衰减报告。"""
        cfg = self._config
        n = len(values)

        # 样本不足 → STABLE
        if n < cfg.short_window:
            mean_val = float(values.mean()) if n > 0 else 0.0
            return DecayReport(
                level=DecayLevel.STABLE,
                short_term_mean=mean_val,
                long_term_mean=mean_val,
                decay_ratio=0.0,
                trend_slope=0.0,
                samples=n,
                message=f"insufficient samples ({n} < {cfg.short_window})",
            )

        short_term = values[-cfg.short_window :]
        long_term = values[-min(cfg.long_window, n) :]

        short_mean = float(np.mean(short_term))
        long_mean = float(np.mean(long_term))

        # 衰减比例: (长期 - 短期) / |长期|, 正=衰减
        if abs(long_mean) > 1e-10:
            decay_ratio = (long_mean - short_mean) / abs(long_mean)
        else:
            decay_ratio = 0.0 if abs(short_mean) < 1e-10 else (-1.0 if short_mean > 0 else 1.0)

        # 趋势斜率 (线性拟合)
        trend_data = values[-min(cfg.trend_window, n) :]
        trend_slope = self._compute_slope(trend_data)

        # 判定级别
        levels: list[DecayLevel] = []

        # CRITICAL: 衰减>critical 或 短期为负
        if decay_ratio > cfg.critical_threshold or short_mean < 0:
            levels.append(DecayLevel.CRITICAL)
        # WARNING: 衰减>warning
        elif decay_ratio > cfg.warning_threshold:
            levels.append(DecayLevel.WARNING)

        # DECAYING: 持续负斜率且变化幅度显著 (>5% of mean, 避免噪声误触发)
        if trend_slope < 0 and len(trend_data) >= 5:
            trend_mean = max(abs(float(np.mean(trend_data))), 1e-10)
            trend_magnitude = abs(trend_slope * (len(trend_data) - 1)) / trend_mean
            if trend_magnitude > 0.05:
                levels.append(DecayLevel.DECAYING)

        if not levels:
            level = DecayLevel.STABLE
            msg = "strategy performance is stable"
        else:
            level = DecayLevel.worst(levels)
            parts = []
            if level is DecayLevel.CRITICAL:
                parts.append(f"critical decay: short={short_mean:.4f} vs long={long_mean:.4f}")
            elif DecayLevel.WARNING in levels:
                parts.append(f"warning: decay_ratio={decay_ratio:.2%}")
            if DecayLevel.DECAYING in levels:
                parts.append(f"declining trend: slope={trend_slope:.6f}")
            msg = "; ".join(parts) if parts else str(level)

        return DecayReport(
            level=level,
            short_term_mean=short_mean,
            long_term_mean=long_mean,
            decay_ratio=decay_ratio,
            trend_slope=trend_slope,
            samples=n,
            message=msg,
        )

    @staticmethod
    def _compute_slope(values: np.ndarray) -> float:
        """计算线性趋势斜率 (最小二乘法)。"""
        n = len(values)
        if n < 2:
            return 0.0
        x = np.arange(n, dtype=float)
        # slope = cov(x,y) / var(x)
        x_mean = x.mean()
        y_mean = values.mean()
        denom = np.sum((x - x_mean) ** 2)
        if denom < 1e-10:
            return 0.0
        return float(np.sum((x - x_mean) * (values - y_mean)) / denom)

# [BLUEPRINT] MOD-SIG-095 | docs/03_modules/_domain_signal/multi_indicator_divergence/blueprint.md
# [MODULE] zephyr.signal_ashare.multi_indicator_divergence
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] numpy; pandas（CVD 腿由 MOD-SIG-093 契约注入，鸭子类型；RSI/MACD 内核自算，factor 指标库无 RSI/MACD 实现可查）
# [CONSUMERS] （候选：买入侧/卖出侧装配层、MOD-SIG-086 漏斗骨架）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 指标封闭集（rsi/macd/cvd）；方向封闭集（bullish/bearish）；峰谷对位=连续两峰/两谷配对（居中窗口确认，回溯检测语义）；magnitude>0；背离次数→反转概率查表（3 次顶背离≥70%）；级联概率表非递减且满级≥60%；背离化解=指标反超前峰/前谷水平；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] AUD-DRAFT-001 深挖批 B10-01363 行 + 候选注册表 CAND-TESTB-010
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 未知指标/非法方向/短序列/非有限值/非法配置 → ValueError（fail-closed）
# [TESTS] tests/signal_ashare/test_multi_indicator_divergence.py
# [A_module] module_id=MOD-SIG-095 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""多指标背离检测（MOD-SIG-095，B10-01363）。

卖出侧量价背离已有（MOD-SELL sell_signal_collector）；RSI/MACD/CVD 系统背离
检测+多级别级联为缺口（深挖裁定理由）。本模块落地：

- **指标核自算**：RSI（Wilder）+ MACD（EMA12/26/9，DIF 腿）；CVD 序列由
  MOD-SIG-093 契约注入（鸭子类型）。
- **峰谷对位**：居中窗口确认局部峰/谷，连续两峰（价新高+指标走弱→bearish）
  /两谷（价新低+指标抬升→bullish）配对；magnitude=价格腿幅度+指标腿幅度
  （指标腿以全序列 std 归一）量化背离程度。
- **背离次数→反转概率**：查表（默认 1 次 35%/2 次 55%/3 次 72%，对齐"3 次
  顶背离反转概率>70%"口径），次数越界钳制表尾。
- **多级别级联**：各周期方向对齐计数→级联概率查表（默认满 4 级 70%≥60%）。
- **背离化解**：背离成立后指标反超前峰（bearish）/前谷（bullish）水平 →
  resolved=True（动能重新确认，背离失效）。

与既有件边界（查重裁定）：
- MOD-SELL sell_signal_collector：卖出侧量价背离聚合，非 RSI/MACD 系统化检测。
- sentiment_cycle 顶背离：情绪口径（炸板率）；t0_point_analyzer：做T 日内量价；
  sector_divergence：板块间背离——语义均正交。

依据: AUD-DRAFT-001 深挖批 B10-01363（裁定=做 P1）；蓝图 §0 边界
SSoT: depgraph blueprint_id=MOD-SIG-095
Version: 0.1.0

# [ALGO_FLOW]
# 输入: close 序列 + 指标序列（rsi/macd 自算或 cvd 注入）/ 多周期方向字典
# 特征: 居中窗口峰谷点 + 指标腿/价格腿 + 连续背离计数 + 跨周期对齐数
# 算法: 峰谷对位配对 → 程度量化 → 化解扫描 → 次数/级联概率查表
# 输出: DivergenceEvent 列表 / DivergenceScanResult / CascadeResult
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from typing import Any, Final

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

__all__: Final = [
    "CascadeResult",
    "DivergenceConfig",
    "DivergenceEvent",
    "DivergenceScanResult",
    "MultiIndicatorDivergenceDetector",
    "MultiIndicatorDivergence",  # scaffold 注册别名（__init__ export 契约）
]

_INDICATORS: Final = ("rsi", "macd", "cvd")
_DIRECTIONS: Final = ("bullish", "bearish")
_EPS: Final = 1e-12


def _default_reversal_table() -> dict[int, float]:
    # 背离次数→反转概率（3 次顶背离>70% 口径）
    return {1: 0.35, 2: 0.55, 3: 0.72}


def _default_cascade_table() -> dict[int, float]:
    # 级联对齐级别数→反转概率（满级≥60%）
    return {1: 0.35, 2: 0.50, 3: 0.62, 4: 0.70}


def _validate_table(name: str, table: dict[int, float]) -> None:
    if not table:
        msg = f"{name} 为空"
        raise ValueError(msg)
    keys = sorted(table)
    if any(not isinstance(k, int) or k < 1 for k in keys):
        msg = f"{name} 键须为≥1 整数，实得 {keys}"
        raise ValueError(msg)
    prev = -1.0
    for k in keys:
        v = table[k]
        if not (0.0 <= v <= 1.0):
            msg = f"{name}[{k}]={v} 越界 [0,1]"
            raise ValueError(msg)
        if v < prev:
            msg = f"{name} 须随键非递减（{k} 处回落）"
            raise ValueError(msg)
        prev = v


@dataclass(frozen=True)
class DivergenceConfig:
    """检测参数（构造即校验，fail-closed）。"""

    rsi_period: int = 14
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    lookback: int = 5
    reversal_probability_table: dict[int, float] = field(default_factory=_default_reversal_table)
    cascade_probability_table: dict[int, float] = field(default_factory=_default_cascade_table)

    def __post_init__(self) -> None:
        if self.rsi_period < 1:
            msg = f"rsi_period 须≥1，实得 {self.rsi_period}"
            raise ValueError(msg)
        if self.macd_fast < 1 or self.macd_slow < 1 or self.macd_signal < 1:
            msg = "MACD 周期参数须≥1"
            raise ValueError(msg)
        if self.macd_fast >= self.macd_slow:
            msg = f"macd_fast 须< macd_slow（{self.macd_fast}>={self.macd_slow}）"
            raise ValueError(msg)
        if self.lookback < 1:
            msg = f"lookback 须≥1，实得 {self.lookback}"
            raise ValueError(msg)
        _validate_table("reversal_probability_table", self.reversal_probability_table)
        _validate_table("cascade_probability_table", self.cascade_probability_table)


@dataclass(frozen=True)
class DivergenceEvent:
    """单条背离事件（峰谷对位）。"""

    indicator: str
    direction: str
    bar_index: int
    price_value: float
    indicator_value: float
    magnitude: float
    resolved: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DivergenceScanResult:
    """全指标扫描输出。"""

    events: tuple[DivergenceEvent, ...]
    top_divergence_count: int
    bottom_divergence_count: int
    top_reversal_probability: float
    bottom_reversal_probability: float

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["events"] = [e.to_dict() for e in self.events]
        return d


@dataclass(frozen=True)
class CascadeResult:
    """多级别级联输出。"""

    direction: str
    aligned_levels: int
    probability: float

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class MultiIndicatorDivergenceDetector:
    """RSI/MACD/CVD 背离检测器（峰谷对位+程度量化+级联概率）。"""

    def __init__(self, config: DivergenceConfig | None = None) -> None:
        self._config = config if config is not None else DivergenceConfig()

    @property
    def config(self) -> DivergenceConfig:
        return self._config

    # ── 指标核 ──────────────────────────────────────────────────────
    def rsi(self, close: pd.Series, period: int | None = None) -> pd.Series:
        """Wilder RSI（前 warmup 段为 NaN，由 detect 跳过）。"""
        p = self._config.rsi_period if period is None else int(period)
        if p < 1:
            msg = f"period 须≥1，实得 {p}"
            raise ValueError(msg)
        delta = close.diff()
        gain = delta.clip(lower=0.0)
        loss = -delta.clip(upper=0.0)
        avg_gain = gain.ewm(alpha=1.0 / p, min_periods=p, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1.0 / p, min_periods=p, adjust=False).mean()
        rs = avg_gain / avg_loss
        out = 100.0 - 100.0 / (1.0 + rs)
        out = out.where(~((avg_loss == 0.0) & (avg_gain > 0.0)), 100.0)
        out = out.where(~((avg_gain == 0.0) & (avg_loss > 0.0)), 0.0)
        return out

    def macd(
        self,
        close: pd.Series,
        fast: int | None = None,
        slow: int | None = None,
        signal: int | None = None,
    ) -> tuple[pd.Series, pd.Series, pd.Series]:
        """MACD（DIF/DEA/HIST）。"""
        cfg = self._config
        f = cfg.macd_fast if fast is None else int(fast)
        s = cfg.macd_slow if slow is None else int(slow)
        g = cfg.macd_signal if signal is None else int(signal)
        if f < 1 or s < 1 or g < 1 or f >= s:
            msg = f"非法 MACD 周期: fast={f} slow={s} signal={g}"
            raise ValueError(msg)
        ema_f = close.ewm(span=f, adjust=False).mean()
        ema_s = close.ewm(span=s, adjust=False).mean()
        dif = ema_f - ema_s
        dea = dif.ewm(span=g, adjust=False).mean()
        return dif, dea, (dif - dea) * 2.0

    # ── 峰谷对位检测 ────────────────────────────────────────────────
    def detect(
        self,
        close: pd.Series,
        indicator_series: pd.Series,
        *,
        indicator: str,
        lookback: int | None = None,
    ) -> list[DivergenceEvent]:
        """峰谷对位背离检测（回溯语义：峰/谷经 lookback 根后确认）。"""
        if indicator not in _INDICATORS:
            msg = f"未知指标 {indicator!r}（封闭集 {_INDICATORS}）"
            raise ValueError(msg)
        lb = self._config.lookback if lookback is None else int(lookback)
        if lb < 1:
            msg = f"lookback 须≥1，实得 {lb}"
            raise ValueError(msg)
        price = np.asarray(close, dtype=float)
        ind = np.asarray(indicator_series, dtype=float)
        if len(price) != len(ind):
            msg = f"close 与指标不等长: {len(price)} vs {len(ind)}"
            raise ValueError(msg)
        n = len(price)
        if n < 2 * lb + 2:
            msg = f"序列过短（{n}<{2 * lb + 2}）"
            raise ValueError(msg)
        if not np.isfinite(price).all():
            msg = "close 含非有限值"
            raise ValueError(msg)
        finite = np.isfinite(ind)
        if not finite.any():
            msg = "指标序列全非有限"
            raise ValueError(msg)
        first_valid = int(np.argmax(finite))
        if not finite[first_valid:].all():
            msg = "指标序列含内部非有限值（仅允许头部 warmup NaN）"
            raise ValueError(msg)

        peaks = [
            i
            for i in range(max(lb, first_valid), n - lb)
            if price[i] == price[i - lb : i + lb + 1].max() and int(np.argmax(price[i - lb : i + lb + 1])) == lb
        ]
        troughs = [
            i
            for i in range(max(lb, first_valid), n - lb)
            if price[i] == price[i - lb : i + lb + 1].min() and int(np.argmin(price[i - lb : i + lb + 1])) == lb
        ]
        ind_std = float(np.std(ind[first_valid:])) + _EPS

        events: list[DivergenceEvent] = []
        for p1, p2 in zip(peaks, peaks[1:]):
            if price[p2] > price[p1] and ind[p2] < ind[p1]:
                magnitude = (price[p2] / price[p1] - 1.0) + (ind[p1] - ind[p2]) / ind_std
                resolved = bool((ind[p2 + 1 :] >= ind[p1]).any()) if p2 + 1 < n else False
                events.append(
                    DivergenceEvent(
                        indicator=indicator,
                        direction="bearish",
                        bar_index=p2,
                        price_value=float(price[p2]),
                        indicator_value=float(ind[p2]),
                        magnitude=float(magnitude),
                        resolved=resolved,
                    )
                )
        for t1, t2 in zip(troughs, troughs[1:]):
            if price[t2] < price[t1] and ind[t2] > ind[t1]:
                magnitude = (price[t1] / price[t2] - 1.0) + (ind[t2] - ind[t1]) / ind_std
                resolved = bool((ind[t2 + 1 :] <= ind[t1]).any()) if t2 + 1 < n else False
                events.append(
                    DivergenceEvent(
                        indicator=indicator,
                        direction="bullish",
                        bar_index=t2,
                        price_value=float(price[t2]),
                        indicator_value=float(ind[t2]),
                        magnitude=float(magnitude),
                        resolved=resolved,
                    )
                )
        return events

    # ── 概率查表 ────────────────────────────────────────────────────
    def reversal_probability(self, count: int) -> float:
        """背离次数→反转概率（越界钳制表尾）。"""
        if count < 1:
            return 0.0
        table = self._config.reversal_probability_table
        return table[min(count, max(table))]

    def cascade_probability(self, directions_by_tf: dict[str, str | None], *, direction: str) -> CascadeResult:
        """多级别级联：各周期方向与给定方向对齐计数→级联概率。"""
        if direction not in _DIRECTIONS:
            msg = f"非法方向 {direction!r}（封闭集 {_DIRECTIONS}）"
            raise ValueError(msg)
        for tf, d in directions_by_tf.items():
            if d is not None and d not in _DIRECTIONS:
                msg = f"周期 {tf} 方向非法: {d!r}"
                raise ValueError(msg)
        aligned = sum(1 for d in directions_by_tf.values() if d == direction)
        if aligned < 1:
            return CascadeResult(direction=direction, aligned_levels=0, probability=0.0)
        table = self._config.cascade_probability_table
        return CascadeResult(
            direction=direction,
            aligned_levels=aligned,
            probability=table[min(aligned, max(table))],
        )

    # ── 全指标扫描 ──────────────────────────────────────────────────
    def scan(self, close: pd.Series, cvd: pd.Series | None = None) -> DivergenceScanResult:
        """RSI+MACD（+CVD 注入）全指标背离扫描 + 次数概率。"""
        events: list[DivergenceEvent] = []
        events += self.detect(close, self.rsi(close), indicator="rsi")
        dif, _, _ = self.macd(close)
        events += self.detect(close, dif, indicator="macd")
        if cvd is not None:
            events += self.detect(close, cvd, indicator="cvd")
        top = sum(1 for e in events if e.direction == "bearish" and not e.resolved)
        bottom = sum(1 for e in events if e.direction == "bullish" and not e.resolved)
        return DivergenceScanResult(
            events=tuple(events),
            top_divergence_count=top,
            bottom_divergence_count=bottom,
            top_reversal_probability=self.reversal_probability(top),
            bottom_reversal_probability=self.reversal_probability(bottom),
        )


# scaffold 注册别名（__init__.py export 契约）
MultiIndicatorDivergence = MultiIndicatorDivergenceDetector

# [BLUEPRINT] MOD-SIG-099 | docs/03_modules/_domain_signal/extreme_sentiment_reversal_detector/blueprint.md
# [MODULE] zephyr.signal_ashare.extreme_sentiment_reversal_detector
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 标准库（math/statistics/dataclasses）；情绪分/指数 OHLCV/广度序列鸭子类型注入，不 import 任何 zephyr 内部件
# [CONSUMERS] （候选：情绪页极端反转告警、买入侧底部情景装配层；上游情绪分 MOD-SIG-025 market_sentiment_analyzer）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 双冰点配对滞后≤max_lag 封闭集；修复概率查表静态可审计（非实时频率估计）；Capitulation 三维打分卡总分∈[0,100]；收回比例≥0（close≥day_low 校验）；真破位强制阻断反转；PIT（分位/RSI/均量全部扩展窗≤当根）；frozen dataclass asdict JSON 可序列化；纯统计核不直连 DB
# [MODIFY-GUARD] AUD-DRAFT-001 深挖批 B10-01369 行 + 候选注册表 CAND-TESTB-014
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 序列不等长/短于 min_history/非有限值/非正价格/负量/广度越界/量比≤0/close<day_low/配置越界（修复表键缺口） → ValueError（fail-closed）
# [TESTS] tests/signal_ashare/test_extreme_sentiment_reversal_detector.py
# [A_module] module_id=MOD-SIG-099 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""极端情绪反转与恐慌底部检测模型（MOD-SIG-099，B10-01369）。

场内对账（查重铁律③探查分工在案）：sentiment_cycle=五阶段定位器（相位+纪律）、
market_sentiment_analyzer（MOD-SIG-025）=情绪分生产方、regime 域 s2_capitulation_score
=指数级 S2 体制见底维度；**双冰点确认（情绪冰点×指数冰点 ≤2 日）/Capitulation
打分卡（跌幅/量能/广度）/收回比例区分 shakeout 与真破位无实现**（深挖批
min_build_spec 明示缺口），本模块落地——A 股短生态事件检测器（信号域），与 regime
指数级体制维度粒度正交。

三件套：

- **双冰点确认**：情绪冰点=情绪分≤扩展窗 22% 分位（可配）；指数冰点=RSI14<30
  （Wilder，指标核自算不 import，MOD-SIG-095 同先例）；最近 max_lag+1 根内两冰点
  配对 |Δ|≤2 日；修复概率查表（0/1/2 日→0.72/0.74/0.71 默认）≥0.70 → confirmed。
- **Capitulation 打分卡**（0-100，≥70 判恐慌投降）：跌幅 40 + 量能 30
  （今日量/前 20 日均量）+ 广度 30（上涨家数占比）。
- **Shakeout vs 真破位**：收回比例=(close−day_low)/(level−day_low)（day_low<level
  才判）；>0.5→shakeout（洗盘假破位），<0.2→true_breakdown（真破位），
  其间 undetermined，未破位 none。

综合反转：双冰点 confirmed 且打分卡≥阈值且非真破位 → reversal_detected；
confidence=(打分卡/100)×修复概率。

依据: AUD-DRAFT-001 深挖批 B10-01369（裁定=做 P1）；蓝图 §0 边界
SSoT: depgraph blueprint_id=MOD-SIG-099
Version: 0.1.0

# [ALGO_FLOW]
# 输入: 情绪分序列 + 指数收/低/量 + 上涨家数占比（等长，尾部=最新）+ 可选支撑位
# 特征: 扩展窗分位 + RSI14（Wilder）+ 日跌幅/量比/广度 + 破位收回比例
# 算法: 双冰点配对查表 → 三维打分卡 → 破位四态裁定 → 合成反转判定
# 输出: ExtremeReversalReport（双冰点/打分卡/裁定/反转标记/置信度）
"""

from __future__ import annotations

import logging
import math
import statistics
from dataclasses import asdict, dataclass, field
from typing import Any, Final, Sequence

logger = logging.getLogger(__name__)

__all__: Final = [
    "BreakdownVerdict",
    "CapitulationScorecard",
    "DoubleIceStatus",
    "ExtremeReversalReport",
    "ExtremeSentimentReversalDetector",
    "SentimentReversalConfig",
]

# Capitulation 打分卡查表（可审计静态表；总分 100 = 跌幅 40 + 量能 30 + 广度 30）
_DROP_TIERS: Final = ((-0.05, 40.0), (-0.03, 32.0), (-0.02, 22.0), (-0.01, 10.0))
_VOLUME_TIERS: Final = ((2.5, 30.0), (2.0, 26.0), (1.5, 18.0), (1.2, 10.0))
_BREADTH_TIERS: Final = ((0.10, 30.0), (0.20, 22.0), (0.30, 12.0))


def _tier_score(value: float, tiers: tuple[tuple[float, float], ...], *, lower_is_severe: bool) -> float:
    for threshold, points in tiers:
        if lower_is_severe:
            if value <= threshold:
                return points
        elif value >= threshold:
            return points
    return 0.0


def _percentile(values: Sequence[float], q: float) -> float:
    """线性插值分位（numpy 'linear' 同口径），q∈[0,1]。"""
    s = sorted(values)
    if len(s) == 1:
        return s[0]
    rank = q * (len(s) - 1)
    lo = int(rank)
    hi = min(lo + 1, len(s) - 1)
    return s[lo] + (s[hi] - s[lo]) * (rank - lo)


def _rsi_wilder(closes: Sequence[float], period: int) -> float:
    """RSI（Wilder 平滑），序列须 ≥ period+1（调用方校验）。"""
    diffs = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    gains = [max(d, 0.0) for d in diffs]
    losses = [max(-d, 0.0) for d in diffs]
    avg_gain = statistics.fmean(gains[:period])
    avg_loss = statistics.fmean(losses[:period])
    for i in range(period, len(diffs)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    if avg_loss == 0.0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - 100.0 / (1.0 + rs)


# ------------------------------------------------------------------
# 契约
# ------------------------------------------------------------------
@dataclass(frozen=True)
class SentimentReversalConfig:
    """阈值与修复概率查表配置（构造即校验，fail-closed）。"""

    sentiment_ice_percentile: float = 0.22
    min_history: int = 60
    rsi_period: int = 14
    rsi_ice_threshold: float = 30.0
    double_ice_max_lag_days: int = 2
    repair_prob_threshold: float = 0.70
    repair_prob_by_lag: dict[int, float] = field(
        default_factory=lambda: {0: 0.72, 1: 0.74, 2: 0.71}
    )
    capitulation_threshold: float = 70.0
    volume_avg_window: int = 20
    shakeout_recovery_ratio: float = 0.5
    true_breakdown_ratio: float = 0.2

    def __post_init__(self) -> None:
        if not (0.0 < self.sentiment_ice_percentile < 0.5):
            msg = f"sentiment_ice_percentile 须∈(0,0.5)，实得 {self.sentiment_ice_percentile}"
            raise ValueError(msg)
        if self.min_history < 30:
            msg = f"min_history 须≥30，实得 {self.min_history}"
            raise ValueError(msg)
        if self.rsi_period < 2:
            msg = f"rsi_period 须≥2，实得 {self.rsi_period}"
            raise ValueError(msg)
        if not (0.0 < self.rsi_ice_threshold <= 50.0):
            msg = f"rsi_ice_threshold 须∈(0,50]，实得 {self.rsi_ice_threshold}"
            raise ValueError(msg)
        if self.double_ice_max_lag_days < 0:
            msg = f"double_ice_max_lag_days 须≥0，实得 {self.double_ice_max_lag_days}"
            raise ValueError(msg)
        if not (0.0 < self.repair_prob_threshold < 1.0):
            msg = f"repair_prob_threshold 须∈(0,1)，实得 {self.repair_prob_threshold}"
            raise ValueError(msg)
        expected_keys = set(range(self.double_ice_max_lag_days + 1))
        if set(self.repair_prob_by_lag.keys()) != expected_keys:
            msg = f"repair_prob_by_lag 键须=0..{self.double_ice_max_lag_days}，实得 {sorted(self.repair_prob_by_lag)}"
            raise ValueError(msg)
        for lag, prob in self.repair_prob_by_lag.items():
            if not (0.0 < prob < 1.0):
                msg = f"repair_prob_by_lag[{lag}] 须∈(0,1)，实得 {prob}"
                raise ValueError(msg)
        if not (0.0 < self.capitulation_threshold <= 100.0):
            msg = f"capitulation_threshold 须∈(0,100]，实得 {self.capitulation_threshold}"
            raise ValueError(msg)
        if self.volume_avg_window < 5:
            msg = f"volume_avg_window 须≥5，实得 {self.volume_avg_window}"
            raise ValueError(msg)
        if not (0.0 < self.true_breakdown_ratio < self.shakeout_recovery_ratio < 1.0):
            msg = (
                f"收回比率须 0<true<shakeout<1，实得 "
                f"{self.true_breakdown_ratio}/{self.shakeout_recovery_ratio}"
            )
            raise ValueError(msg)


@dataclass(frozen=True)
class DoubleIceStatus:
    """双冰点状态输出。"""

    sentiment_ice_now: bool
    index_ice_now: bool
    paired: bool
    confirmed: bool
    lag_days: int | None
    repair_probability: float | None
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CapitulationScorecard:
    """Capitulation 三维打分卡输出。"""

    drop_points: float
    volume_points: float
    breadth_points: float
    total: float
    is_capitulation: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BreakdownVerdict:
    """破位裁定输出（shakeout/true_breakdown/undetermined/none 封闭集）。"""

    kind: str
    recovery_ratio: float | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExtremeReversalReport:
    """极端情绪反转综合报告。"""

    double_ice: DoubleIceStatus
    capitulation: CapitulationScorecard
    verdict: BreakdownVerdict | None
    reversal_detected: bool
    confidence: float
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["double_ice"] = self.double_ice.to_dict()
        d["capitulation"] = self.capitulation.to_dict()
        d["verdict"] = self.verdict.to_dict() if self.verdict is not None else None
        return d


# ------------------------------------------------------------------
# 引擎
# ------------------------------------------------------------------
class ExtremeSentimentReversalDetector:
    """极端情绪反转与恐慌底部检测引擎（纯统计核，鸭子类型注入）。"""

    def __init__(self, config: SentimentReversalConfig | None = None) -> None:
        self._config = config if config is not None else SentimentReversalConfig()

    @property
    def config(self) -> SentimentReversalConfig:
        return self._config

    # ── 双冰点确认 ────────────────────────────────────────────────
    def detect_double_ice(
        self, sentiment_scores: Sequence[float], index_closes: Sequence[float]
    ) -> DoubleIceStatus:
        cfg = self._config
        scores = [float(v) for v in sentiment_scores]
        closes = [float(v) for v in index_closes]
        if len(scores) != len(closes):
            msg = f"情绪分与指数收盘不等长: {len(scores)} vs {len(closes)}"
            raise ValueError(msg)
        n = len(scores)
        if n < cfg.min_history:
            msg = f"历史 {n}<{cfg.min_history}"
            raise ValueError(msg)
        if not all(math.isfinite(v) for v in scores) or not all(math.isfinite(v) for v in closes):
            msg = "输入含非有限值（NaN/inf）"
            raise ValueError(msg)
        if any(c <= 0.0 for c in closes):
            msg = "指数收盘含非正值"
            raise ValueError(msg)

        # 候选根：最近 max_lag+1 根（PIT：分位/RSI 均按 ≤ 当根的扩展窗）
        candidates = list(range(n - 1 - cfg.double_ice_max_lag_days, n))
        sentiment_ice: dict[int, bool] = {}
        index_ice: dict[int, bool] = {}
        for i in candidates:
            thr = _percentile(scores[: i + 1], cfg.sentiment_ice_percentile)
            sentiment_ice[i] = scores[i] <= thr
            index_ice[i] = _rsi_wilder(closes[: i + 1], cfg.rsi_period) < cfg.rsi_ice_threshold

        s_bars = [i for i in candidates if sentiment_ice[i]]
        r_bars = [i for i in candidates if index_ice[i]]
        best_lag: int | None = None
        for i_s in s_bars:
            for i_r in r_bars:
                lag = abs(i_s - i_r)
                if lag <= cfg.double_ice_max_lag_days and (best_lag is None or lag < best_lag):
                    best_lag = lag

        paired = best_lag is not None
        repair_prob = cfg.repair_prob_by_lag[best_lag] if paired else None
        confirmed = bool(paired and repair_prob is not None and repair_prob >= cfg.repair_prob_threshold)
        return DoubleIceStatus(
            sentiment_ice_now=sentiment_ice[n - 1],
            index_ice_now=index_ice[n - 1],
            paired=paired,
            confirmed=confirmed,
            lag_days=best_lag,
            repair_probability=repair_prob,
        )

    # ── Capitulation 打分卡 ───────────────────────────────────────
    def capitulation_score(
        self, day_drop: float, volume_ratio: float, advance_ratio: float
    ) -> CapitulationScorecard:
        if not all(math.isfinite(v) for v in (day_drop, volume_ratio, advance_ratio)):
            msg = "输入含非有限值（NaN/inf）"
            raise ValueError(msg)
        if volume_ratio <= 0.0:
            msg = f"volume_ratio 须>0，实得 {volume_ratio}"
            raise ValueError(msg)
        if not (0.0 <= advance_ratio <= 1.0):
            msg = f"advance_ratio 须∈[0,1]，实得 {advance_ratio}"
            raise ValueError(msg)
        drop_pts = _tier_score(day_drop, _DROP_TIERS, lower_is_severe=True)
        vol_pts = _tier_score(volume_ratio, _VOLUME_TIERS, lower_is_severe=False)
        brd_pts = _tier_score(advance_ratio, _BREADTH_TIERS, lower_is_severe=True)
        total = drop_pts + vol_pts + brd_pts
        return CapitulationScorecard(
            drop_points=drop_pts,
            volume_points=vol_pts,
            breadth_points=brd_pts,
            total=total,
            is_capitulation=total >= self._config.capitulation_threshold,
        )

    # ── Shakeout vs 真破位 ────────────────────────────────────────
    def classify_breakdown(self, level: float, day_low: float, close: float) -> BreakdownVerdict:
        cfg = self._config
        if not all(math.isfinite(v) for v in (level, day_low, close)):
            msg = "输入含非有限值（NaN/inf）"
            raise ValueError(msg)
        if level <= 0.0 or day_low <= 0.0 or close <= 0.0:
            msg = f"价格须>0，实得 level={level}/low={day_low}/close={close}"
            raise ValueError(msg)
        if close < day_low:
            msg = f"close({close})<day_low({day_low})，价格关系非法"
            raise ValueError(msg)
        if day_low >= level:
            return BreakdownVerdict(kind="none", recovery_ratio=None)
        ratio = (close - day_low) / (level - day_low)
        if ratio > cfg.shakeout_recovery_ratio:
            kind = "shakeout"
        elif ratio < cfg.true_breakdown_ratio:
            kind = "true_breakdown"
        else:
            kind = "undetermined"
        return BreakdownVerdict(kind=kind, recovery_ratio=ratio)

    # ── 综合检测 ──────────────────────────────────────────────────
    def detect(
        self,
        sentiment_scores: Sequence[float],
        index_closes: Sequence[float],
        index_lows: Sequence[float],
        index_volumes: Sequence[float],
        advance_ratios: Sequence[float],
        *,
        support_level: float | None = None,
    ) -> ExtremeReversalReport:
        cfg = self._config
        closes = [float(v) for v in index_closes]
        lows = [float(v) for v in index_lows]
        volumes = [float(v) for v in index_volumes]
        advances = [float(v) for v in advance_ratios]
        n = len(closes)
        if not (len(lows) == len(volumes) == len(advances) == n):
            msg = "指数收/低/量/广度序列不等长"
            raise ValueError(msg)
        if len(sentiment_scores) != n:
            msg = f"情绪分与指数序列不等长: {len(sentiment_scores)} vs {n}"
            raise ValueError(msg)
        if n < cfg.min_history:
            msg = f"历史 {n}<{cfg.min_history}"
            raise ValueError(msg)
        flat = (*closes, *lows, *volumes, *advances, *sentiment_scores)
        if not all(math.isfinite(v) for v in flat):
            msg = "输入含非有限值（NaN/inf）"
            raise ValueError(msg)
        if any(v <= 0.0 for v in closes) or any(v <= 0.0 for v in lows):
            msg = "价格含非正值"
            raise ValueError(msg)
        if any(v < 0.0 for v in volumes):
            msg = "量含负值"
            raise ValueError(msg)
        if any(not (0.0 <= v <= 1.0) for v in advances):
            msg = "广度含越界值（∉[0,1]）"
            raise ValueError(msg)

        notes: list[str] = []
        ice = self.detect_double_ice(sentiment_scores, closes)

        day_drop = closes[-1] / closes[-2] - 1.0
        avg_vol = statistics.fmean(volumes[-1 - cfg.volume_avg_window : -1])
        volume_ratio = volumes[-1] / avg_vol if avg_vol > 0.0 else 0.0
        if avg_vol <= 0.0:
            notes.append("前 20 日均量=0，量比腿按 0 处理（打分卡量能维不得分）")
        card = self.capitulation_score(day_drop, volume_ratio, advances[-1])

        verdict: BreakdownVerdict | None = None
        if support_level is not None:
            verdict = self.classify_breakdown(support_level, lows[-1], closes[-1])
        else:
            notes.append("未注入 support_level，破位裁定腿降级")

        reversal = bool(
            ice.confirmed
            and card.is_capitulation
            and (verdict is None or verdict.kind != "true_breakdown")
        )
        confidence = (card.total / 100.0) * ice.repair_probability if reversal else 0.0
        return ExtremeReversalReport(
            double_ice=ice,
            capitulation=card,
            verdict=verdict,
            reversal_detected=reversal,
            confidence=confidence,
            notes=tuple(notes),
        )

# [BLUEPRINT] MOD-SIG-103 | docs/03_modules/_domain_signal/bottom_confirmation_entry/blueprint.md
# [MODULE] zephyr.signal_ashare.bottom_confirmation_entry
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 标准库（math/statistics/dataclasses）；资金流/情绪分/Wyckoff Spring 鸭子类型注入，不 import 任何 zephyr 内部件
# [CONSUMERS] （候选：买入侧装配层、右侧入场执行链；上游 MOD-REGIME-002 wyckoff_engine、MOD-SIG-025 情绪分、模块5 资金流 B10-01361/MOD-SIG-093）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 五维封闭集（价格超卖/量能萎缩+放量反弹/Smart Money资金流/情绪分位/Wyckoff Spring）；≥min_confirmations 维才底部确认；右侧入场=确认∧收盘>前日高；止损=底部最低价−atr_stop_mult×ATR14（Wilder 自算）；缺失维降级 hit=False+notes 不阻断；置信度=在场维加权命中占比∈[0,1]；PIT（全部指标扩展/滚动窗≤当根）；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] AUD-DRAFT-001 深挖批 B10-01414 行 + 候选注册表 CAND-TESTB-020
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空 symbol/OHLCV 不等长/短于 min_history/非有限值/非正价/负量/注入序列不对齐/非有限注入值/未知维度权重/负权重/非法配置 → ValueError（fail-closed）
# [TESTS] tests/signal_ashare/test_bottom_confirmation_entry.py
# [A_module] module_id=MOD-SIG-103 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""多维度底部确认与右侧入场模型（MOD-SIG-103，B10-01414，模块17）。

场内对账（查重铁律④分工在案，P1W03 fragment 预留）：
extreme_sentiment_reversal_detector（MOD-SIG-099）=极端情绪反转**事件检测器**
（双冰点+Capitulation 打分卡+shakeout 区分，管"是不是恐慌底"）；
wyckoff_accumulation_signal（MOD-SIG-094）=Wyckoff 评分+CVD 买点（单一 Wyckoff 维度）；
MOD-REGIME-002 wyckoff_engine=阶段评分生产方；**五维底部确认整合+右侧入场触发
（突破前日高）+ATR 止损联动无实现**（深挖批 min_build_spec 明示缺口），本模块落地
——本件=确认整合与入场触发层（管"什么时候进、止损放哪"），与 099 事件检测分工
（IC 加权多维确认 vs 双冰点事件）、与 094 分工（Wyckoff 仅为五维之一）。

五维（注册表 problem 既定）：

1. **价格超卖**：RSI14<30（Wilder 自算，MOD-SIG-095/099 同先例）或收盘≤布林下轨
   （20,2σ）。
2. **量能萎缩+放量反弹**：近 shrink_lookback 根（除今）均量 < shrink_ratio×其前
   20 根均量（萎缩），且今日量≥rebound_vol_ratio×前 20 均量且收阳（放量反弹）。
3. **Smart Money 资金流**：近 flow_window 根净流入和>0，或今日逆势净流入
   （阴量>0，鸭子类型注入）。
4. **情绪分位**：情绪分≤扩展窗 22% 分位（口径对齐 MOD-SIG-099，注入）。
5. **Wyckoff Spring**：spring_lookback 根内出现 Spring 标记（注入）。

确认与入场：命中维数≥min_confirmations（默认 3）→ 底部确认；确认∧今日收盘>
前日高 → 右侧入场触发；止损=bottom_lookback 窗最低价−atr_stop_mult×ATR14
（Wilder 自算）。置信度=在场维加权命中占比（权重可注入，默认等权，
注册表"IC 加权"语义=权重外配注入位）。

不做什么：不生产 Wyckoff 阶段评分/情绪分/资金流（上游注入）、不做事件检测
（099 职责）、不直连 DB、不荐股。

依据: AUD-DRAFT-001 深挖批 B10-01414（裁定=做 P1）；蓝图 §0 边界
SSoT: depgraph blueprint_id=MOD-SIG-103
Version: 0.1.0

# [ALGO_FLOW]
# 输入: OHLCV 等长序列 + 可选资金流/情绪分/Spring 标记（同长对齐，尾部=最新）
# 特征: RSI14/布林下轨/量能萎缩与反弹比/净流入窗和/情绪分位/Spring 窗
# 算法: 五维逐维判定 → 计数≥3 确认 → 收盘>前日高入场 → ATR14 联动止损
# 输出: BottomConfirmationReport（确认数/确认标记/入场/止损/ATR/底部低/逐维明细）
"""

from __future__ import annotations

import logging
import math
import statistics
from dataclasses import asdict, dataclass, field
from typing import Any, Final, Sequence

logger = logging.getLogger(__name__)

__all__: Final = [
    "BOTTOM_DIM_NAMES",
    "BottomConfirmationConfig",
    "BottomConfirmationEntry",
    "BottomConfirmationReport",
    "DimReading",
]

#: 五维封闭集（候选注册表 CAND-TESTB-020 problem 既定口径）
BOTTOM_DIM_NAMES: Final[tuple[str, ...]] = (
    "price_oversold",  # 价格超卖（RSI14<30 或触布林下轨）
    "volume_rebound",  # 量能萎缩+放量反弹
    "smart_money_flow",  # Smart Money 资金流
    "sentiment_extreme",  # 情绪≤22%分位
    "wyckoff_spring",  # Wyckoff Spring
)


# ------------------------------------------------------------------
# 契约
# ------------------------------------------------------------------
@dataclass(frozen=True)
class BottomConfirmationConfig:
    """五维参数与门限配置（构造即校验，fail-closed）。"""

    rsi_period: int = 14
    rsi_oversold: float = 30.0
    boll_window: int = 20
    boll_k: float = 2.0
    shrink_ratio: float = 0.5
    shrink_lookback: int = 10
    shrink_base_window: int = 20
    rebound_vol_ratio: float = 1.5
    rebound_base_window: int = 20
    flow_window: int = 5
    sentiment_percentile: float = 0.22
    spring_lookback: int = 10
    min_confirmations: int = 3
    atr_period: int = 14
    atr_stop_mult: float = 1.0
    bottom_lookback: int = 20
    min_history: int = 40
    dim_weights: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not 0.0 < self.rsi_oversold < 100.0:
            msg = f"rsi_oversold 须∈(0,100)，实得 {self.rsi_oversold}"
            raise ValueError(msg)
        if not 1 <= self.min_confirmations <= len(BOTTOM_DIM_NAMES):
            msg = f"min_confirmations 须∈[1,{len(BOTTOM_DIM_NAMES)}]，实得 {self.min_confirmations}"
            raise ValueError(msg)
        if self.shrink_ratio <= 0.0:
            msg = f"shrink_ratio 须>0，实得 {self.shrink_ratio}"
            raise ValueError(msg)
        if self.rebound_vol_ratio <= 1.0:
            msg = f"rebound_vol_ratio 须>1，实得 {self.rebound_vol_ratio}"
            raise ValueError(msg)
        for name in (
            "rsi_period",
            "boll_window",
            "shrink_lookback",
            "shrink_base_window",
            "rebound_base_window",
            "flow_window",
            "spring_lookback",
            "atr_period",
            "bottom_lookback",
        ):
            if getattr(self, name) < 2:
                msg = f"{name} 须≥2，实得 {getattr(self, name)}"
                raise ValueError(msg)
        if self.boll_k <= 0.0:
            msg = f"boll_k 须>0，实得 {self.boll_k}"
            raise ValueError(msg)
        if not 0.0 < self.sentiment_percentile < 1.0:
            msg = f"sentiment_percentile 须∈(0,1)，实得 {self.sentiment_percentile}"
            raise ValueError(msg)
        if self.atr_stop_mult <= 0.0:
            msg = f"atr_stop_mult 须>0，实得 {self.atr_stop_mult}"
            raise ValueError(msg)
        min_required = self.shrink_lookback + self.shrink_base_window + 1
        if self.min_history < min_required:
            msg = f"min_history 须≥{min_required}（萎缩窗+基准窗+1），实得 {self.min_history}"
            raise ValueError(msg)
        unknown = set(self.dim_weights) - set(BOTTOM_DIM_NAMES)
        if unknown:
            msg = f"未知维度权重: {sorted(unknown)}"
            raise ValueError(msg)
        if any(w < 0.0 for w in self.dim_weights.values()):
            msg = "维度权重须≥0"
            raise ValueError(msg)
        # 防御性拷贝（配置不再被外部 dict 句柄污染）
        object.__setattr__(self, "dim_weights", dict(self.dim_weights))


@dataclass(frozen=True)
class DimReading:
    """单维判定读数。"""

    name: str
    hit: bool
    weight: float
    present: bool  # 数据在场（缺失维降级 False）
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class BottomConfirmationReport:
    """底部确认与右侧入场报告。"""

    symbol: str
    confirmed_count: int
    bottom_confirmed: bool
    confidence: float  # 在场维加权命中占比∈[0,1]
    entry_triggered: bool
    entry_price: float | None
    stop_price: float | None
    atr: float
    bottom_low: float
    prev_day_high: float
    dims: tuple[DimReading, ...]
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ------------------------------------------------------------------
# 指标核（Wilder RSI/ATR 自算，MOD-SIG-095/099 同先例；布林/分位）
# ------------------------------------------------------------------
def _wilder_rsi(closes: Sequence[float], period: int) -> float:
    changes = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    gains = [max(c, 0.0) for c in changes[:period]]
    losses = [max(-c, 0.0) for c in changes[:period]]
    avg_gain = statistics.fmean(gains)
    avg_loss = statistics.fmean(losses)
    for c in changes[period:]:
        avg_gain = (avg_gain * (period - 1) + max(c, 0.0)) / period
        avg_loss = (avg_loss * (period - 1) + max(-c, 0.0)) / period
    if avg_loss == 0.0:
        return 100.0 if avg_gain > 0.0 else 50.0
    rs = avg_gain / avg_loss
    return 100.0 - 100.0 / (1.0 + rs)


def _wilder_atr(highs: Sequence[float], lows: Sequence[float], closes: Sequence[float], period: int) -> float:
    trs: list[float] = []
    for i in range(1, len(closes)):
        trs.append(
            max(
                highs[i] - lows[i],
                abs(highs[i] - closes[i - 1]),
                abs(lows[i] - closes[i - 1]),
            )
        )
    atr = statistics.fmean(trs[:period])
    for tr in trs[period:]:
        atr = (atr * (period - 1) + tr) / period
    return atr


def _percentile(values: Sequence[float], p: float) -> float:
    """线性插值分位数（p∈(0,1)）。"""
    s = sorted(values)
    if len(s) == 1:
        return s[0]
    pos = p * (len(s) - 1)
    lo = int(math.floor(pos))
    hi = min(lo + 1, len(s) - 1)
    frac = pos - lo
    return s[lo] + (s[hi] - s[lo]) * frac


# ------------------------------------------------------------------
# 引擎
# ------------------------------------------------------------------
class BottomConfirmationEntry:
    """五维底部确认与右侧入场引擎（纯统计核，鸭子类型注入）。"""

    def __init__(self, config: BottomConfirmationConfig | None = None) -> None:
        self._config = config if config is not None else BottomConfirmationConfig()

    @property
    def config(self) -> BottomConfirmationConfig:
        return self._config

    # ── 输入校验 ──────────────────────────────────────────────────
    def _validate(
        self,
        symbol: str,
        opens: Sequence[float],
        highs: Sequence[float],
        lows: Sequence[float],
        closes: Sequence[float],
        volumes: Sequence[float],
        smart_money_flows: Sequence[float] | None,
        sentiment_scores: Sequence[float] | None,
        wyckoff_springs: Sequence[bool] | None,
    ) -> None:
        if not symbol:
            msg = "symbol 不能为空"
            raise ValueError(msg)
        n = len(closes)
        if not (len(opens) == len(highs) == len(lows) == n == len(volumes)):
            msg = f"OHLCV 不等长: o={len(opens)}/h={len(highs)}/l={len(lows)}/c={n}/v={len(volumes)}"
            raise ValueError(msg)
        if n < self._config.min_history:
            msg = f"历史 {n}<min_history={self._config.min_history}"
            raise ValueError(msg)
        for series, label in ((opens, "open"), (highs, "high"), (lows, "low"), (closes, "close")):
            if not all(math.isfinite(v) and v > 0.0 for v in series):
                msg = f"{label} 含非有限值或非正值"
                raise ValueError(msg)
        if not all(math.isfinite(v) and v >= 0.0 for v in volumes):
            msg = "volume 含非有限值或负值"
            raise ValueError(msg)
        for series, label in (
            (smart_money_flows, "smart_money_flows"),
            (sentiment_scores, "sentiment_scores"),
            (wyckoff_springs, "wyckoff_springs"),
        ):
            if series is None:
                continue
            if len(series) != n:
                msg = f"{label} 长度 {len(series)} 与 K 线 {n} 不对齐"
                raise ValueError(msg)
            if label == "wyckoff_springs":
                if not all(isinstance(x, bool) for x in series):
                    msg = "wyckoff_springs 须为 bool 序列"
                    raise ValueError(msg)
            elif not all(math.isfinite(v) for v in series):
                msg = f"{label} 含非有限值"
                raise ValueError(msg)

    def _weight(self, name: str) -> float:
        return self._config.dim_weights.get(name, 1.0)

    # ── 主入口 ───────────────────────────────────────────────────
    def evaluate(
        self,
        symbol: str,
        opens: Sequence[float],
        highs: Sequence[float],
        lows: Sequence[float],
        closes: Sequence[float],
        volumes: Sequence[float],
        *,
        smart_money_flows: Sequence[float] | None = None,
        sentiment_scores: Sequence[float] | None = None,
        wyckoff_springs: Sequence[bool] | None = None,
    ) -> BottomConfirmationReport:
        cfg = self._config
        self._validate(
            symbol,
            opens,
            highs,
            lows,
            closes,
            volumes,
            smart_money_flows,
            sentiment_scores,
            wyckoff_springs,
        )
        notes: list[str] = []
        dims: list[DimReading] = []

        # 1) 价格超卖：RSI14<30 或收盘≤布林下轨（零方差塌缩带无信息不判触轨）
        rsi = _wilder_rsi(closes, cfg.rsi_period)
        window = closes[-cfg.boll_window :]
        band_sd = statistics.pstdev(window)
        lower = statistics.fmean(window) - cfg.boll_k * band_sd
        boll_touch = band_sd > 0.0 and closes[-1] <= lower
        price_hit = rsi < cfg.rsi_oversold or boll_touch
        dims.append(
            DimReading(
                name="price_oversold",
                hit=price_hit,
                weight=self._weight("price_oversold"),
                present=True,
                detail=f"RSI{cfg.rsi_period}={rsi:.2f}（门<{cfg.rsi_oversold}），布林下轨={lower:.4f}，收={closes[-1]:.4f}",
            )
        )

        # 2) 量能萎缩+放量反弹
        recent_avg = statistics.fmean(volumes[-(cfg.shrink_lookback + 1) : -1])
        base_avg = statistics.fmean(
            volumes[-(cfg.shrink_lookback + cfg.shrink_base_window + 1) : -(cfg.shrink_lookback + 1)]
        )
        shrink = recent_avg < cfg.shrink_ratio * base_avg
        rebound_base = statistics.fmean(volumes[-(cfg.rebound_base_window + 1) : -1])
        rebound = volumes[-1] >= cfg.rebound_vol_ratio * rebound_base and closes[-1] > opens[-1]
        dims.append(
            DimReading(
                name="volume_rebound",
                hit=shrink and rebound,
                weight=self._weight("volume_rebound"),
                present=True,
                detail=f"萎缩={shrink}（近均{recent_avg:.1f} vs 基准{base_avg:.1f}），反弹={rebound}（今量{volumes[-1]:.1f} vs {cfg.rebound_vol_ratio}×{rebound_base:.1f}）",
            )
        )

        # 3) Smart Money 资金流
        if smart_money_flows is None:
            dims.append(
                DimReading(
                    name="smart_money_flow",
                    hit=False,
                    weight=self._weight("smart_money_flow"),
                    present=False,
                    detail="资金流序列缺失降级",
                )
            )
            notes.append("smart_money_flows 缺失，smart_money_flow 维降级")
        else:
            window_sum = sum(smart_money_flows[-cfg.flow_window :])
            counter_trend = smart_money_flows[-1] > 0.0 and closes[-1] < opens[-1]
            dims.append(
                DimReading(
                    name="smart_money_flow",
                    hit=window_sum > 0.0 or counter_trend,
                    weight=self._weight("smart_money_flow"),
                    present=True,
                    detail=f"近{cfg.flow_window}根净流入和={window_sum:.4f}，逆势={counter_trend}",
                )
            )

        # 4) 情绪分位
        if sentiment_scores is None:
            dims.append(
                DimReading(
                    name="sentiment_extreme",
                    hit=False,
                    weight=self._weight("sentiment_extreme"),
                    present=False,
                    detail="情绪序列缺失降级",
                )
            )
            notes.append("sentiment_scores 缺失，sentiment_extreme 维降级")
        else:
            sent_sd = statistics.pstdev(sentiment_scores)
            if sent_sd == 0.0:
                # 恒定窗无分布信息，不伪造极端（MOD-SIG-101 零方差纪律同构）
                dims.append(
                    DimReading(
                        name="sentiment_extreme",
                        hit=False,
                        weight=self._weight("sentiment_extreme"),
                        present=True,
                        detail="情绪窗零方差无信息不判极端",
                    )
                )
            else:
                threshold = _percentile(sentiment_scores, cfg.sentiment_percentile)
                dims.append(
                    DimReading(
                        name="sentiment_extreme",
                        hit=sentiment_scores[-1] <= threshold,
                        weight=self._weight("sentiment_extreme"),
                        present=True,
                        detail=f"情绪={sentiment_scores[-1]:.4f} ≤ {cfg.sentiment_percentile:.0%}分位={threshold:.4f}",
                    )
                )

        # 5) Wyckoff Spring
        if wyckoff_springs is None:
            dims.append(
                DimReading(
                    name="wyckoff_spring",
                    hit=False,
                    weight=self._weight("wyckoff_spring"),
                    present=False,
                    detail="Spring 标记缺失降级",
                )
            )
            notes.append("wyckoff_springs 缺失，wyckoff_spring 维降级")
        else:
            spring_hit = any(wyckoff_springs[-cfg.spring_lookback :])
            dims.append(
                DimReading(
                    name="wyckoff_spring",
                    hit=spring_hit,
                    weight=self._weight("wyckoff_spring"),
                    present=True,
                    detail=f"近{cfg.spring_lookback}根 Spring={spring_hit}",
                )
            )

        # ── 确认 / 入场 / 止损 ────────────────────────────────────
        confirmed_count = sum(1 for d in dims if d.hit)
        bottom_confirmed = confirmed_count >= cfg.min_confirmations
        present = [d for d in dims if d.present]
        w_sum = sum(d.weight for d in present)
        confidence = sum(d.weight for d in present if d.hit) / w_sum if w_sum > 0.0 else 0.0
        prev_day_high = highs[-2]
        entry_triggered = bottom_confirmed and closes[-1] > prev_day_high
        atr = _wilder_atr(highs, lows, closes, cfg.atr_period)
        bottom_low = min(lows[-cfg.bottom_lookback :])
        entry_price = closes[-1] if entry_triggered else None
        stop_price = bottom_low - cfg.atr_stop_mult * atr if entry_triggered else None
        return BottomConfirmationReport(
            symbol=symbol,
            confirmed_count=confirmed_count,
            bottom_confirmed=bottom_confirmed,
            confidence=confidence,
            entry_triggered=entry_triggered,
            entry_price=entry_price,
            stop_price=stop_price,
            atr=atr,
            bottom_low=bottom_low,
            prev_day_high=prev_day_high,
            dims=tuple(dims),
            notes=tuple(notes),
        )

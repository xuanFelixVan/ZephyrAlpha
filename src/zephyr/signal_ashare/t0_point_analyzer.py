# [BLUEPRINT] MOD-SIG-068 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-25 行 + 前端原型做T页契约）
# [MODULE] zephyr.signal_ashare.t0_point_analyzer
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.intraday_buy_sell_point_analyzer（MOD-SIG-024 复用，prod）; 分钟bar由调用方注入（生产编排可接 c1_market.kline_1min 只读）
# [CONSUMERS] （候选：做T分析页分时点位+信号回验表、45号 W2 平开平走格做T动作联动）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 信号方向封闭 {T买,T卖}；回验判定=T买后N分钟上涨/T卖后N分钟下跌为命中（|ret|<阈值=半命中，反走超阈=失手，前向不足=样本不足不计率）；MOD-SIG-024 腿只做点位检测不走3重确认（做T=持仓内操作非新开仓）；同方向信号冷却窗去重（取置信度最高）；PIT（仅用信号时点之前数据出信号、之后数据做回验）；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-25 行
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空bars→空信号+notes；非法窗口/阈值配置→ValueError（fail-closed）；本模块为信号回验非交易执行，不涉交易成本口径（做T成本归执行层/宪章§3约束一）
# [TESTS] tests/signal_ashare/test_t0_point_analyzer.py
# [A_module] module_id=MOD-SIG-068 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""MOD-SIG-068 — 做T点位算法 + 信号回验管线（GAP-F-25 = 设计文档缺口⑤）。

**MVP 双腿信号源**：
1. **MOD-SIG-024 复用腿**（prod 现成，BFE-01 立捡项）：分钟序列逐 bar 构造
   IntradayBuySellInput（VWAP→ma_price、量比、日内前高、偏离度）→ 6买6卖检测
   → 映射 T买/T卖（只做点位检测，不走 3 重确认——做T是持仓内操作非新开仓）。
2. **做T专项三族检测器**（前端契约"回踩均价/偏离回归/量价背离"）：
   - 回踩均价（T买）：日内曾离开 VWAP 上方 ≥min_excursion，当前回踩
     0≤(close−VWAP)/VWAP≤pullback_max_pct 且 量缩（vol≤shrink×均量）；
   - 偏离回归（T卖/T买）：(close−VWAP)/VWAP ≥dev_sell_pct→T卖（冲高远离均价），
     ≤dev_buy_pct→T买（深跌回归，可关）；
   - 量价背离（T卖/T买）：价格创日内新高但量 < 前高量×div_vol_ratio→T卖；
     创新低量缩→T买（可关）。

**回验管线**（信号对不对的直接反馈）：信号后 +10/+30 根 1 分钟 bar 收益
（T卖取反向），≥hit_threshold 命中 / ≤−threshold 失手 / 其间半命中 /
前向不足=样本不足不计率；按 pattern×window 聚合命中率。

# [ALGO_FLOW]
# 层: 输入
# - id: I1 分钟bar序列 list[MinuteBar]（ts/open/high/low/close/volume，1分钟）
# - id: I2 上下文 T0Context（symbol/prev_close/resistance/资金与情绪注入位）
# 层: 特征
# - id: F1 VWAP（典型价累计）
# - id: F2 量比/偏离度/日内新高新低
# 层: 算法
# - id: A1 MOD-SIG-024 适配腿（点位检测映射）
# - id: A2 做T专项三族检测
# - id: A3 同方向冷却窗去重
# - id: A4 +N 分钟命中回验+命中率聚合
# 层: 输出
# - id: O1 list[T0Signal] + T0VerifyReport（hits 逐信号回验 + stats pattern×window 命中率）
# [/ALGO_FLOW]
#
# 边:
# I1 --> F1
# I1 --> F2
# F1,F2,I2 --> A1
# F1,F2 --> A2
# A1,A2 --> A3
# A3,I1 --> A4
# A4 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Final

from zephyr.signal_ashare.intraday_buy_sell_point_analyzer import (
    IntradayBuySellAnalyzer,
    IntradayBuySellInput,
)

logger = logging.getLogger(__name__)

__all__: Final = [
    "MinuteBar",
    "T0AnalyzerConfig",
    "T0BacktestConfig",
    "T0Context",
    "T0HitRateStat",
    "T0Signal",
    "T0SignalHit",
    "T0VerifyReport",
    "generate_t0_signals",
    "verify_t0_signals",
]

#: 方向/判定封闭集合
T_BUY: Final[str] = "T买"
T_SELL: Final[str] = "T卖"
VERDICT_HIT: Final[str] = "命中"
VERDICT_HALF: Final[str] = "半命中"
VERDICT_MISS: Final[str] = "失手"
VERDICT_INSUFFICIENT: Final[str] = "样本不足"

#: 做T专项模式名
PATTERN_PULLBACK_VWAP: Final[str] = "回踩均价"
PATTERN_DEVIATION_REVERT: Final[str] = "偏离回归"
PATTERN_VOLUME_DIVERGENCE: Final[str] = "量价背离"


# ------------------------------------------------------------------
# 配置 / 输入 / 输出
# ------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class MinuteBar:
    """1 分钟 K 线 bar。"""

    ts: str  # YYYY-MM-DD HH:MM
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True, slots=True)
class T0Context:
    """做T上下文（昨收/阻力与 MOD-SIG-024 适配所需注入位）。"""

    symbol: str
    prev_close: float = 0.0
    resistance_price: float = 0.0  # 阻力位（注入位；0=不用突破族）
    capital_net_inflow: float = 0.0  # 资金净流入（万元，逆向资金买点用）


@dataclass(frozen=True, slots=True)
class T0AnalyzerConfig:
    """做T点位配置（MVP 初拍值待回验标定，全可配）。"""

    # 回踩均价
    pullback_max_pct: float = 1.0  # 回踩带：0≤偏离≤1%
    pullback_min_excursion_pct: float = 0.5  # 此前须曾离开 VWAP 上方 0.5%
    pullback_shrink_ratio: float = 0.7  # 量缩阈值（vol ≤ 0.7×均量）
    # 偏离回归
    dev_sell_pct: float = 1.2  # 冲高偏离 ≥1.2% → T卖
    dev_buy_pct: float = -1.5  # 深跌偏离 ≤-1.5% → T买
    enable_deviation_buy: bool = True
    # 量价背离
    div_vol_ratio: float = 0.7  # 新高量 < 前高量×0.7 → 顶背离
    enable_divergence_buy: bool = True  # 底背离（新低量缩→T买）
    # 通用
    lookback_bars: int = 20  # 均量/参照回看窗
    cooldown_bars: int = 15  # 同方向信号冷却（bar 数）
    use_sig024: bool = True  # MOD-SIG-024 适配腿开关
    sig024_min_confidence: float = 50.0  # SIG-024 信号置信度下限


@dataclass(frozen=True, slots=True)
class T0BacktestConfig:
    """回验配置（10/30 分钟命中判定，前端契约口径）。"""

    windows_bars: tuple[int, ...] = (10, 30)  # 前向窗口（1分钟bar数=分钟数）
    hit_threshold_pct: float = 0.2  # 命中阈值 %（|ret|<阈值=半命中）


@dataclass(frozen=True, slots=True)
class T0Signal:
    """做T信号。"""

    ts: str
    symbol: str
    direction: str  # T买/T卖
    pattern: str  # 回踩均价/偏离回归/量价背离/SIG-024 模式名
    price: float
    confidence: float  # 0~100
    logic: str  # 一句话逻辑（前端契约）
    source: str  # t_specialized / sig024 / merged


@dataclass(frozen=True, slots=True)
class T0SignalHit:
    """单信号回验结果。"""

    signal: T0Signal
    forward_ret_pct: dict[int, float | None] = field(default_factory=dict)  # window → 收益%
    verdicts: dict[int, str] = field(default_factory=dict)  # window → 判定


@dataclass(frozen=True, slots=True)
class T0HitRateStat:
    """pattern×window 命中率统计。"""

    pattern: str
    window_bars: int
    total: int
    hit: int
    half_hit: int
    miss: int
    insufficient: int
    hit_rate: float | None  # hit/(total-insufficient)；全样本不足 → None


@dataclass(frozen=True, slots=True)
class T0VerifyReport:
    """做T信号回验报告（做T分析页"今日做T信号回验"表契约）。"""

    symbol: str
    date: str
    hits: list[T0SignalHit] = field(default_factory=list)
    stats: list[T0HitRateStat] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


# ------------------------------------------------------------------
# 特征（纯函数）
# ------------------------------------------------------------------


def _vwap_series(bars: list[MinuteBar]) -> list[float]:
    """VWAP 累计序列（典型价 (H+L+C)/3 加权）。"""
    cum_pv = 0.0
    cum_v = 0.0
    out: list[float] = []
    for b in bars:
        typical = (b.high + b.low + b.close) / 3.0
        cum_pv += typical * b.volume
        cum_v += b.volume
        out.append(cum_pv / cum_v if cum_v > 0 else b.close)
    return out


def _mean_volume(bars: list[MinuteBar], end: int, lookback: int) -> float:
    """[end-lookback, end) 窗均量（不足窗按可用样本）。"""
    start = max(0, end - lookback)
    window = [b.volume for b in bars[start:end]]
    return sum(window) / len(window) if window else 0.0


# ------------------------------------------------------------------
# 信号生成（纯函数核）
# ------------------------------------------------------------------


def _detect_t_specialized(bars: list[MinuteBar], vwap: list[float], cfg: T0AnalyzerConfig) -> list[T0Signal]:
    """做T专项三族检测（回踩均价/偏离回归/量价背离）。"""
    signals: list[T0Signal] = []
    running_high_idx = 0
    running_low_idx = 0
    for i in range(1, len(bars)):
        b = bars[i]
        vw = vwap[i]
        if vw <= 0:
            continue
        dev_pct = (b.close - vw) / vw * 100.0
        avg_vol = _mean_volume(bars, i, cfg.lookback_bars)
        max_prior_excursion = max(
            ((bars[j].close - vwap[j]) / vwap[j] * 100.0 for j in range(i) if vwap[j] > 0),
            default=0.0,
        )

        # ① 回踩均价（T买）：曾离开上方 → 回踩带内 + 缩量
        if (
            max_prior_excursion >= cfg.pullback_min_excursion_pct
            and 0.0 <= dev_pct <= cfg.pullback_max_pct
            and avg_vol > 0
            and b.volume <= cfg.pullback_shrink_ratio * avg_vol
        ):
            confidence = min(100.0, 60.0 + (cfg.pullback_max_pct - dev_pct) * 10.0)
            signals.append(
                T0Signal(
                    ts=b.ts,
                    symbol="",
                    direction=T_BUY,
                    pattern=PATTERN_PULLBACK_VWAP,
                    price=b.close,
                    confidence=round(confidence, 2),
                    logic=f"回踩均价不破+缩量止跌（偏离{dev_pct:.2f}%，量比{b.volume / avg_vol:.2f}）",
                    source="t_specialized",
                )
            )

        # ② 偏离回归
        if dev_pct >= cfg.dev_sell_pct:
            confidence = min(100.0, 55.0 + dev_pct * 10.0)
            signals.append(
                T0Signal(
                    ts=b.ts,
                    symbol="",
                    direction=T_SELL,
                    pattern=PATTERN_DEVIATION_REVERT,
                    price=b.close,
                    confidence=round(confidence, 2),
                    logic=f"冲高远离均价{dev_pct:.2f}%，回归预期",
                    source="t_specialized",
                )
            )
        elif cfg.enable_deviation_buy and dev_pct <= cfg.dev_buy_pct:
            confidence = min(100.0, 55.0 + abs(dev_pct) * 10.0)
            signals.append(
                T0Signal(
                    ts=b.ts,
                    symbol="",
                    direction=T_BUY,
                    pattern=PATTERN_DEVIATION_REVERT,
                    price=b.close,
                    confidence=round(confidence, 2),
                    logic=f"深跌偏离均价{dev_pct:.2f}%，回归低吸",
                    source="t_specialized",
                )
            )

        # ③ 量价背离：新高量缩 → T卖；新低量缩 → T买
        if b.high > bars[running_high_idx].high and i - running_high_idx >= 2:
            prev_vol = bars[running_high_idx].volume
            if prev_vol > 0 and b.volume < cfg.div_vol_ratio * prev_vol:
                confidence = min(100.0, 60.0 + (1.0 - b.volume / prev_vol) * 40.0)
                signals.append(
                    T0Signal(
                        ts=b.ts,
                        symbol="",
                        direction=T_SELL,
                        pattern=PATTERN_VOLUME_DIVERGENCE,
                        price=b.close,
                        confidence=round(confidence, 2),
                        logic=f"价创日内新高量缩（量仅为前高{b.volume / prev_vol:.0%}），量价背离",
                        source="t_specialized",
                    )
                )
            running_high_idx = i
        elif b.high >= bars[running_high_idx].high:
            running_high_idx = i
        if b.low < bars[running_low_idx].low and i - running_low_idx >= 2:
            prev_vol = bars[running_low_idx].volume
            if cfg.enable_divergence_buy and prev_vol > 0 and b.volume < cfg.div_vol_ratio * prev_vol:
                confidence = min(100.0, 60.0 + (1.0 - b.volume / prev_vol) * 40.0)
                signals.append(
                    T0Signal(
                        ts=b.ts,
                        symbol="",
                        direction=T_BUY,
                        pattern=PATTERN_VOLUME_DIVERGENCE,
                        price=b.close,
                        confidence=round(confidence, 2),
                        logic=f"价创日内新低量缩（量仅为前低{b.volume / prev_vol:.0%}），底背离",
                        source="t_specialized",
                    )
                )
            running_low_idx = i
        elif b.low <= bars[running_low_idx].low:
            running_low_idx = i
    return signals


def _detect_sig024(bars: list[MinuteBar], vwap: list[float], ctx: T0Context, cfg: T0AnalyzerConfig) -> list[T0Signal]:
    """MOD-SIG-024 适配腿：逐 bar 构造 IntradayBuySellInput → 6买6卖检测 → T信号映射。"""
    analyzer = IntradayBuySellAnalyzer()
    signals: list[T0Signal] = []
    for i in range(1, len(bars)):
        b = bars[i]
        vw = vwap[i]
        if vw <= 0:
            continue
        avg_vol = _mean_volume(bars, i, cfg.lookback_bars)
        volume_ratio = (b.volume / avg_vol) if avg_vol > 0 else 1.0
        prev_high = max(bars[j].high for j in range(i))
        input_data = IntradayBuySellInput(
            symbol=ctx.symbol,
            current_price=b.close,
            resistance_price=ctx.resistance_price,
            volume_ratio=volume_ratio,
            ma_price=vw,
            pullback_volume_ratio=volume_ratio,
            price_change_pct=((b.close / ctx.prev_close - 1.0) * 100.0 if ctx.prev_close > 0 else 0.0),
            capital_net_inflow=ctx.capital_net_inflow,
            prev_intraday_high=prev_high,
            intraday_volume_ratio=volume_ratio,
            below_ma_pct=(b.close - vw) / vw * 100.0,
        )
        for sig in analyzer.detect_buy_points(input_data):
            if sig.confidence >= cfg.sig024_min_confidence:
                signals.append(
                    T0Signal(
                        ts=b.ts,
                        symbol=ctx.symbol,
                        direction=T_BUY,
                        pattern=sig.point_type,
                        price=b.close,
                        confidence=sig.confidence,
                        logic=sig.reason,
                        source="sig024",
                    )
                )
        for sig in analyzer.detect_sell_points(input_data):
            if sig.confidence >= cfg.sig024_min_confidence:
                signals.append(
                    T0Signal(
                        ts=b.ts,
                        symbol=ctx.symbol,
                        direction=T_SELL,
                        pattern=sig.point_type,
                        price=b.close,
                        confidence=sig.confidence,
                        logic=sig.reason,
                        source="sig024",
                    )
                )
    return signals


def _cooldown_dedup(signals: list[T0Signal], bar_index: dict[str, int], cooldown_bars: int) -> list[T0Signal]:
    """同方向冷却窗去重：冷却簇内保留置信度最高信号（确定性：并列取先）。"""
    by_direction: dict[str, list[T0Signal]] = {T_BUY: [], T_SELL: []}
    for s in signals:
        by_direction.setdefault(s.direction, []).append(s)
    kept: list[T0Signal] = []
    for direction, group in by_direction.items():
        group.sort(key=lambda s: bar_index.get(s.ts, 0))
        cluster: list[T0Signal] = []
        last_idx = -(10**9)
        for s in group:
            idx = bar_index.get(s.ts, 0)
            if idx - last_idx >= cooldown_bars and cluster:
                kept.append(max(cluster, key=lambda x: x.confidence))
                cluster = []
            cluster.append(s)
            last_idx = idx
        if cluster:
            kept.append(max(cluster, key=lambda x: x.confidence))
    kept.sort(key=lambda s: bar_index.get(s.ts, 0))
    return kept


def generate_t0_signals(
    bars: list[MinuteBar],
    context: T0Context,
    config: T0AnalyzerConfig | None = None,
) -> list[T0Signal]:
    """做T信号生成主核（纯函数）：专项三族 + MOD-SIG-024 适配腿 → 冷却去重。"""
    cfg = config or T0AnalyzerConfig()
    if cfg.lookback_bars < 2:
        raise ValueError(f"lookback_bars 须≥2: {cfg.lookback_bars}")
    if not bars:
        return []
    vwap = _vwap_series(bars)
    raw: list[T0Signal] = []
    for s in _detect_t_specialized(bars, vwap, cfg):
        raw.append(
            T0Signal(
                ts=s.ts,
                symbol=context.symbol,
                direction=s.direction,
                pattern=s.pattern,
                price=s.price,
                confidence=s.confidence,
                logic=s.logic,
                source=s.source,
            )
        )
    if cfg.use_sig024:
        raw.extend(_detect_sig024(bars, vwap, context, cfg))
    bar_index = {b.ts: i for i, b in enumerate(bars)}
    return _cooldown_dedup(raw, bar_index, cfg.cooldown_bars)


# ------------------------------------------------------------------
# 回验（纯函数核）
# ------------------------------------------------------------------


def verify_t0_signals(
    signals: list[T0Signal],
    bars: list[MinuteBar],
    config: T0BacktestConfig | None = None,
    symbol: str = "",
    date_str: str = "",
) -> T0VerifyReport:
    """信号回验：+N bar 前向收益判定 命中/半命中/失手/样本不足 + 命中率聚合。

    判定口径（前端契约）：T买后 N 分钟上涨=命中、下跌超阈=失手、其间=半命中；
    T卖反向对称；前向不足=样本不足（不计入命中率）。
    """
    cfg = config or T0BacktestConfig()
    if not cfg.windows_bars or any(w <= 0 for w in cfg.windows_bars):
        raise ValueError(f"windows_bars 须为正整数非空组: {cfg.windows_bars}")
    if cfg.hit_threshold_pct <= 0:
        raise ValueError(f"hit_threshold_pct 须>0: {cfg.hit_threshold_pct}")

    close_by_ts = {b.ts: b.close for b in bars}
    bar_index = {b.ts: i for i, b in enumerate(bars)}
    hits: list[T0SignalHit] = []
    for s in signals:
        i = bar_index.get(s.ts)
        rets: dict[int, float | None] = {}
        verdicts: dict[int, str] = {}
        for w in cfg.windows_bars:
            j = i + w if i is not None else None
            if i is None or j is None or j >= len(bars):
                rets[w] = None
                verdicts[w] = VERDICT_INSUFFICIENT
                continue
            base = close_by_ts.get(s.ts) or s.price
            if base <= 0:
                rets[w] = None
                verdicts[w] = VERDICT_INSUFFICIENT
                continue
            ret = (bars[j].close - base) / base * 100.0
            if s.direction == T_SELL:
                ret = -ret  # T卖取反向（下跌=命中）
            rets[w] = round(ret, 4)
            if ret >= cfg.hit_threshold_pct:
                verdicts[w] = VERDICT_HIT
            elif ret <= -cfg.hit_threshold_pct:
                verdicts[w] = VERDICT_MISS
            else:
                verdicts[w] = VERDICT_HALF
        hits.append(T0SignalHit(signal=s, forward_ret_pct=rets, verdicts=verdicts))

    # pattern×window 聚合
    stats: list[T0HitRateStat] = []
    patterns = sorted({s.signal.pattern for s in hits})
    for pattern in patterns:
        for w in cfg.windows_bars:
            group = [h for h in hits if h.signal.pattern == pattern]
            hit = sum(1 for h in group if h.verdicts[w] == VERDICT_HIT)
            half = sum(1 for h in group if h.verdicts[w] == VERDICT_HALF)
            miss = sum(1 for h in group if h.verdicts[w] == VERDICT_MISS)
            insuf = sum(1 for h in group if h.verdicts[w] == VERDICT_INSUFFICIENT)
            valid = len(group) - insuf
            stats.append(
                T0HitRateStat(
                    pattern=pattern,
                    window_bars=w,
                    total=len(group),
                    hit=hit,
                    half_hit=half,
                    miss=miss,
                    insufficient=insuf,
                    hit_rate=round(hit / valid, 4) if valid > 0 else None,
                )
            )

    notes: list[str] = []
    if not signals:
        notes.append("无信号可回验")
    elif all(v == VERDICT_INSUFFICIENT for h in hits for v in h.verdicts.values()):
        notes.append("全部信号前向样本不足（尾盘信号），命中率不出伪值")
    return T0VerifyReport(
        symbol=symbol or (signals[0].symbol if signals else ""),
        date=date_str or (bars[0].ts[:10] if bars else ""),
        hits=hits,
        stats=stats,
        notes=notes,
    )

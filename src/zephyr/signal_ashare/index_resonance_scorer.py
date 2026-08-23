# [BLUEPRINT] MOD-SIG-069 | 待统筹登记（blueprint 未建，真源=缺口总账 GAP-F-31 行 + 前端原型指数页综合观点卡契约）
# [MODULE] zephyr.signal_ashare.index_resonance_scorer
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] c1_market.kline_index（只读，加载层）
# [CONSUMERS] （候选：指数详情页×4 综合观点卡"买/卖/中性+置信度+共振x/7"）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 七族封闭 {MACD,KDJ,RSI,量能,均线,BOLL,趋势}；族票 ∈ {+1,0,-1}；权重常量可配（weight_overrides 白名单键 fail-closed）；信号三态封闭 {买入,卖出,中性}；共振 x/7=与最终方向同向族数（中性=投0族数）；置信度为启发式非校准概率（50~95，中性恒50）；数据 <min_bars → degraded 不出伪信号；PIT（仅用 ≤数据日K线）；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-31 行
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 查询异常/客户端不可得→degraded notes 留痕不抛；非法 weight_overrides 键/阈值→ValueError（fail-closed）
# [TESTS] tests/signal_ashare/test_index_resonance_scorer.py
# [A_module] module_id=MOD-SIG-069 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""MOD-SIG-069 — 指数级多指标共振综合评分（GAP-F-31 = 设计文档缺口③）。

七族投票（权重常量可配，初拍值待标定）：

| 族 | 口径 | 多/空/中性 |
|---|---|---|
| MACD(12,26,9) | DIF vs DEA | DIF>DEA +1 / < −1 |
| KDJ(9,3,3) | K vs D（regime risk_features 同口径） | K>D +1 / < −1 |
| RSI(14) | Wilder RSI 对双阈 | ≥55 +1 / ≤45 −1 / 其间 0 |
| 量能 | 5日均量 vs 20日均量 × 近5日价格方向 | 放量涨 +1 / 放量跌 −1 / 缩量 0 |
| 均线 | close vs MA20 × MA20 斜率(5日) | 上+升 +1 / 下+降 −1 / 混合 0 |
| BOLL(20,2) | close vs 中轨 | 上 +1 / 下 −1 |
| 趋势 | close vs 20 日前 close | 上 +1 / 下 −1 |

合成：score=Σw·v/Σw ∈ [-1,1]；≥buy_threshold→买入，≤sell_threshold→卖出，
其间→中性。共振 x/7 = 与最终方向同向族数（中性=投 0 族数）。
置信度启发式：买/卖 = 50 + 同向权重占比×45（封顶 95）；中性恒 50。
**非校准概率**（"只画栏杆不算命"纪律：评分是状态描摹非点位预测）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1 指数日K序列 list[DailyBar]（date/open/high/low/close/volume 升序，kline_index）
# 层: 特征
# - id: F1~F7 七族指标末值（MACD/KDJ/RSI/量能/均线/BOLL/趋势）
# 层: 算法
# - id: A1 七族投票（族票 ∈ {+1,0,-1}，理由留痕）
# - id: A2 加权合成 + 三态信号 + 共振计数 + 启发式置信度
# 层: 输出
# - id: O1 IndexResonanceResult（signal/confidence/resonance x/7/family_votes 明细）
# [/ALGO_FLOW]
#
# 边:
# I1 --> F1..F7
# F1..F7 --> A1
# A1 --> A2
# A2 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Final, Mapping

logger = logging.getLogger(__name__)

__all__: Final = [
    "DailyBar",
    "FamilyVote",
    "IndexResonanceResult",
    "ResonanceConfig",
    "compute_resonance",
    "score_index_resonance",
]

#: 信号三态（封闭集合）
SIGNAL_BUY: Final[str] = "买入"
SIGNAL_SELL: Final[str] = "卖出"
SIGNAL_NEUTRAL: Final[str] = "中性"

#: 七族键（weight_overrides 白名单）
_FAMILY_KEYS: Final = frozenset({"macd", "kdj", "rsi", "volume", "ma", "boll", "trend"})

_FAMILY_NAME_ZH: Final[dict[str, str]] = {
    "macd": "MACD",
    "kdj": "KDJ",
    "rsi": "RSI",
    "volume": "量能",
    "ma": "均线",
    "boll": "BOLL",
    "trend": "趋势",
}

#: SQL 集中化（§5.160.2）
SQL_INDEX_DAILY: Final = """
SELECT trade_date, open, high, low, close, volume
FROM c1_market.kline_index
WHERE symbol = %(symbol)s AND trade_date <= %(trade_date)s
ORDER BY trade_date DESC
LIMIT %(limit)s
"""


# ------------------------------------------------------------------
# 配置 / 输入 / 输出
# ------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ResonanceConfig:
    """共振评分配置（静态权重 MVP 初拍值待标定；weight_overrides 动态化接口位）。"""

    w_macd: float = 0.18
    w_kdj: float = 0.12
    w_rsi: float = 0.12
    w_volume: float = 0.14
    w_ma: float = 0.18
    w_boll: float = 0.12
    w_trend: float = 0.14
    rsi_bull: float = 55.0  # RSI 多阈
    rsi_bear: float = 45.0  # RSI 空阈
    vol_short: int = 5  # 量能短窗
    vol_long: int = 20  # 量能长窗
    ma_window: int = 20  # 均线/BOLL 窗
    ma_slope_lookback: int = 5  # MA 斜率回看
    trend_lookback: int = 20  # 趋势族回看
    buy_threshold: float = 0.2  # 买入阈（score≥）
    sell_threshold: float = -0.2  # 卖出阈（score≤）
    min_bars: int = 60  # 最小样本（MACD 暖机 26+9，余量）
    weight_overrides: Mapping[str, float] | None = None  # 动态化接口位（白名单键）


@dataclass(frozen=True, slots=True)
class DailyBar:
    """指数日 K bar。"""

    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass(frozen=True, slots=True)
class FamilyVote:
    """单族投票明细。"""

    family: str  # 族键
    name_zh: str
    vote: int  # +1/0/-1
    weight: float
    reason: str  # 中文理由（审计留痕）


@dataclass(frozen=True, slots=True)
class IndexResonanceResult:
    """共振综合评分输出契约（指数页综合观点卡）。"""

    symbol: str
    date: str
    signal: str  # 买入/卖出/中性
    confidence: float | None  # 启发式置信度 50~95（中性 50）；degraded → None
    resonance_count: int  # 共振 x
    resonance_total: int  # 7
    score: float | None  # 加权分 [-1,1]；degraded → None
    family_votes: list[FamilyVote] = field(default_factory=list)
    weight_mode: str = "static"  # static / override
    degraded: bool = False
    notes: list[str] = field(default_factory=list)


# ------------------------------------------------------------------
# 指标计算（纯函数，list 数学无外部依赖）
# ------------------------------------------------------------------


def _ema(values: list[float], n: int) -> list[float]:
    """EMA 序列（alpha=2/(n+1)，首值=SMA(n) 前暖机段 NaN 语义→从第 n-1 起）。"""
    if len(values) < n:
        return []
    alpha = 2.0 / (n + 1)
    seed = sum(values[:n]) / n
    out = [seed]
    for v in values[n:]:
        out.append(alpha * v + (1 - alpha) * out[-1])
    return out


def _sma(values: list[float], n: int) -> float | None:
    if len(values) < n:
        return None
    return sum(values[-n:]) / n


def _macd_dif_dea(closes: list[float]) -> tuple[float | None, float | None]:
    """MACD(12,26,9) 末值（DIF/DEA）；样本不足 → (None, None)。"""
    if len(closes) < 35:
        return None, None
    ema12 = _ema(closes, 12)
    ema26 = _ema(closes, 26)
    dif = [a - b for a, b in zip(ema12[-len(ema26):], ema26)]
    dea = _ema(dif, 9)
    if not dea:
        return None, None
    return dif[-1], dea[-1]


def _kdj(closes: list[float], highs: list[float], lows: list[float], n: int = 9) -> tuple[float | None, float | None]:
    """KDJ(9,3,3) K/D 末值（regime risk_features.kdj 同口径：ewm alpha=1/3 递推）。"""
    if len(closes) < n:
        return None, None
    k = 50.0
    d = 50.0
    for i in range(len(closes)):
        start = max(0, i - n + 1)
        low_min = min(lows[start : i + 1])
        high_max = max(highs[start : i + 1])
        rsv = (closes[i] - low_min) / (high_max - low_min) * 100.0 if high_max > low_min else 50.0
        k = (2.0 / 3.0) * k + (1.0 / 3.0) * rsv
        d = (2.0 / 3.0) * d + (1.0 / 3.0) * k
    return k, d


def _rsi_wilder(closes: list[float], n: int = 14) -> float | None:
    """Wilder RSI(14) 末值。"""
    if len(closes) < n + 1:
        return None
    gains = 0.0
    losses = 0.0
    for i in range(1, n + 1):
        diff = closes[i] - closes[i - 1]
        gains += max(diff, 0.0)
        losses += max(-diff, 0.0)
    avg_gain = gains / n
    avg_loss = losses / n
    for i in range(n + 1, len(closes)):
        diff = closes[i] - closes[i - 1]
        avg_gain = (avg_gain * (n - 1) + max(diff, 0.0)) / n
        avg_loss = (avg_loss * (n - 1) + max(-diff, 0.0)) / n
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100.0 - 100.0 / (1.0 + rs)


# ------------------------------------------------------------------
# 七族投票（纯函数核）
# ------------------------------------------------------------------


def _resolve_weights(cfg: ResonanceConfig) -> tuple[dict[str, float], str]:
    """权重解析：默认静态；weight_overrides 白名单覆盖（非法键 ValueError fail-closed）。"""
    weights = {
        "macd": cfg.w_macd, "kdj": cfg.w_kdj, "rsi": cfg.w_rsi, "volume": cfg.w_volume,
        "ma": cfg.w_ma, "boll": cfg.w_boll, "trend": cfg.w_trend,
    }
    if cfg.weight_overrides is None:
        return weights, "static"
    bad = set(cfg.weight_overrides) - _FAMILY_KEYS
    if bad:
        raise ValueError(f"非法 weight_overrides 键: {sorted(bad)}")
    weights.update({k: float(v) for k, v in cfg.weight_overrides.items()})
    return weights, "override"


def compute_resonance(bars: list[DailyBar], config: ResonanceConfig | None = None) -> IndexResonanceResult:
    """共振评分主核（纯函数，不触库）。

    Args:
        bars: 指数日 K 升序序列（≥min_bars）。
        config: 配置（None 默认）。

    Returns:
        IndexResonanceResult；样本不足/权重和 0 → degraded 不出伪信号。
    """
    cfg = config or ResonanceConfig()
    if not (0.0 < cfg.buy_threshold <= 1.0) or not (-1.0 <= cfg.sell_threshold < 0.0):
        raise ValueError(f"非法信号阈值: buy={cfg.buy_threshold} sell={cfg.sell_threshold}")
    symbol_date = (bars[-1].date, ) if bars else ("",)
    if len(bars) < cfg.min_bars:
        return IndexResonanceResult(
            symbol="", date=symbol_date[0], signal=SIGNAL_NEUTRAL, confidence=None,
            resonance_count=0, resonance_total=7, score=None, degraded=True,
            notes=[f"日K样本不足（{len(bars)}<{cfg.min_bars}），不出伪信号"],
        )

    weights, weight_mode = _resolve_weights(cfg)
    wsum = sum(weights.values())
    if wsum <= 0:
        return IndexResonanceResult(
            symbol="", date=bars[-1].date, signal=SIGNAL_NEUTRAL, confidence=None,
            resonance_count=0, resonance_total=7, score=None, weight_mode=weight_mode, degraded=True,
            notes=["权重和为 0（weight_overrides 全零），不出伪信号"],
        )

    closes = [b.close for b in bars]
    highs = [b.high for b in bars]
    lows = [b.low for b in bars]
    volumes = [b.volume for b in bars]
    close = closes[-1]
    votes: list[FamilyVote] = []

    # F1 MACD
    dif, dea = _macd_dif_dea(closes)
    v = 0 if dif is None else (1 if dif > dea else -1)
    votes.append(FamilyVote("macd", _FAMILY_NAME_ZH["macd"], v, weights["macd"],
                          f"DIF={dif:.3f} vs DEA={dea:.3f}" if dif is not None else "样本不足"))
    # F2 KDJ
    k, d = _kdj(closes, highs, lows)
    v = 0 if k is None else (1 if k > d else -1)
    votes.append(FamilyVote("kdj", _FAMILY_NAME_ZH["kdj"], v, weights["kdj"],
                          f"K={k:.1f} vs D={d:.1f}" if k is not None else "样本不足"))
    # F3 RSI
    rsi = _rsi_wilder(closes)
    if rsi is None:
        v = 0
    elif rsi >= cfg.rsi_bull:
        v = 1
    elif rsi <= cfg.rsi_bear:
        v = -1
    else:
        v = 0
    votes.append(FamilyVote("rsi", _FAMILY_NAME_ZH["rsi"], v, weights["rsi"],
                          f"RSI={rsi:.1f}（多阈{cfg.rsi_bull}/空阈{cfg.rsi_bear}）" if rsi is not None else "样本不足"))
    # F4 量能
    vol_s = _sma(volumes, cfg.vol_short)
    vol_l = _sma(volumes, cfg.vol_long)
    price_up = close > closes[-1 - cfg.vol_short]
    if vol_s is None or vol_l is None or vol_l == 0:
        v = 0
        reason = "样本不足"
    elif vol_s > vol_l:
        v = 1 if price_up else -1
        reason = f"放量（均量{vol_s:.0f}>{vol_l:.0f}）+近{cfg.vol_short}日{'涨' if price_up else '跌'}"
    else:
        v = 0
        reason = f"缩量（均量{vol_s:.0f}≤{vol_l:.0f}）"
    votes.append(FamilyVote("volume", _FAMILY_NAME_ZH["volume"], v, weights["volume"], reason))
    # F5 均线
    ma_now = _sma(closes, cfg.ma_window)
    ma_prev = _sma(closes[: -cfg.ma_slope_lookback], cfg.ma_window) if len(closes) > cfg.ma_slope_lookback else None
    if ma_now is None or ma_prev is None:
        v = 0
        reason = "样本不足"
    elif close > ma_now and ma_now > ma_prev:
        v = 1
        reason = f"收{close:.2f}>MA{cfg.ma_window}={ma_now:.2f} 且均线上行"
    elif close < ma_now and ma_now < ma_prev:
        v = -1
        reason = f"收{close:.2f}<MA{cfg.ma_window}={ma_now:.2f} 且均线下行"
    else:
        v = 0
        reason = f"收{close:.2f} vs MA{cfg.ma_window}={ma_now:.2f} 方向混合"
    votes.append(FamilyVote("ma", _FAMILY_NAME_ZH["ma"], v, weights["ma"], reason))
    # F6 BOLL（中轨=MA20）
    v = 0 if ma_now is None else (1 if close > ma_now else -1)
    votes.append(FamilyVote("boll", _FAMILY_NAME_ZH["boll"], v, weights["boll"],
                            f"收{close:.2f} vs 中轨{ma_now:.2f}" if ma_now is not None else "样本不足"))
    # F7 趋势
    ref = closes[-1 - cfg.trend_lookback]
    v = 1 if close > ref else -1
    votes.append(FamilyVote("trend", _FAMILY_NAME_ZH["trend"], v, weights["trend"],
                            f"收{close:.2f} vs {cfg.trend_lookback}日前{ref:.2f}"))

    score = sum(fv.vote * fv.weight for fv in votes) / wsum
    if score >= cfg.buy_threshold:
        signal = SIGNAL_BUY
        aligned = [fv for fv in votes if fv.vote == 1]
    elif score <= cfg.sell_threshold:
        signal = SIGNAL_SELL
        aligned = [fv for fv in votes if fv.vote == -1]
    else:
        signal = SIGNAL_NEUTRAL
        aligned = [fv for fv in votes if fv.vote == 0]
    resonance_count = len(aligned)
    if signal == SIGNAL_NEUTRAL:
        confidence = 50.0
    else:
        aligned_w = sum(fv.weight for fv in aligned) / wsum
        confidence = min(95.0, 50.0 + aligned_w * 45.0)
    return IndexResonanceResult(
        symbol="", date=bars[-1].date, signal=signal, confidence=round(confidence, 1),
        resonance_count=resonance_count, resonance_total=7, score=round(score, 4),
        family_votes=votes, weight_mode=weight_mode,
    )


# ------------------------------------------------------------------
# 加载层 + 主入口
# ------------------------------------------------------------------


def _normalize_date(trade_date: str | date | datetime) -> date:
    if isinstance(trade_date, datetime):
        return trade_date.date()
    if isinstance(trade_date, date):
        return trade_date
    return datetime.strptime(str(trade_date), "%Y-%m-%d").date()


def _default_client() -> Any | None:
    try:
        from zephyr.data.ch_writer import get_client

        return get_client()
    except Exception:  # noqa: BLE001 — 连接/依赖问题一律降级
        logger.warning("ch_writer 默认客户端不可用，共振评分降级", exc_info=True)
        return None


def score_index_resonance(
    symbol: str,
    trade_date: str | date | datetime | None = None,
    ch_client: Any | None = None,
    config: ResonanceConfig | None = None,
    bars: list[DailyBar] | None = None,
) -> IndexResonanceResult:
    """主入口：指数级七族共振综合评分。

    Args:
        symbol: 指数代码（如 000001.SH）。
        trade_date: 数据日（PIT 上限；None=不过滤取最新）。
        ch_client: clickhouse-driver 鸭子类型；None 延迟取默认客户端。
        config: 配置（None 默认）。
        bars: 测试/编排注入位；None 时经 client 现查 kline_index。

    Returns:
        IndexResonanceResult；查询异常/样本不足 → degraded 不出伪信号。
    """
    cfg = config or ResonanceConfig()
    if bars is None:
        client = ch_client if ch_client is not None else _default_client()
        if client is None:
            return IndexResonanceResult(
                symbol=symbol, date="", signal=SIGNAL_NEUTRAL, confidence=None,
                resonance_count=0, resonance_total=7, score=None, degraded=True,
                notes=["CH 客户端不可得，共振评分整体降级"],
            )
        params: dict[str, Any] = {"symbol": symbol, "limit": max(cfg.min_bars * 2, 120)}
        if trade_date is not None:
            params["trade_date"] = _normalize_date(trade_date)  # ValueError fail-closed
        else:
            params["trade_date"] = date(2100, 1, 1)  # 不过滤（PIT 上限=无穷）
        try:
            rows = client.execute(SQL_INDEX_DAILY, params)
        except Exception as e:  # noqa: BLE001 — 数据层异常降级
            return IndexResonanceResult(
                symbol=symbol, date="", signal=SIGNAL_NEUTRAL, confidence=None,
                resonance_count=0, resonance_total=7, score=None, degraded=True,
                notes=[f"kline_index 查询异常: {e!r}"],
            )
        bars = [
            DailyBar(date=str(r[0]), open=float(r[1]), high=float(r[2]), low=float(r[3]),
                     close=float(r[4]), volume=float(r[5]))
            for r in reversed(rows)  # DESC → 升序
        ]
    result = compute_resonance(bars, cfg)
    return IndexResonanceResult(
        symbol=symbol, date=result.date, signal=result.signal, confidence=result.confidence,
        resonance_count=result.resonance_count, resonance_total=result.resonance_total,
        score=result.score, family_votes=result.family_votes, weight_mode=result.weight_mode,
        degraded=result.degraded, notes=result.notes,
    )

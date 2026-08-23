# [BLUEPRINT] MOD-SIG-069 | 待统筹登记（supplement：GAP-F-33 趋势线/压力支撑识别；主号=指数共振评分，同属指数页技术分析族）
# [MODULE] zephyr.signal_ashare.trendline_sr_detector
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] （纯函数：日 K OHLC 注入；regime_detector 输出颗粒度核查结论=7 态概率无点位级趋势线/SR 输出，故独立新建，裁定见 GAP7 报告）
# [CONSUMERS] （候选：指数详情页叠加层——趋势线/压力支撑位渲染数据）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 分形极值须满窗（±k，边缘不满窗不判）；价位聚类容差 %（均值口径，触点数=强度）；支撑=现价下方最近位/压力=现价上方最近位（另一侧无位 → None + notes 不硬编）；趋势线取最近两个同向显著极值（两低点斜率>0=上升线/两高点斜率<0=下降线）；数据不足/无极值 → degraded 不出伪线；价格 ≤0 或类型非法 → ValueError fail-closed；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-33 行
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] bars 元素类型非法/价格非正→ValueError（fail-closed）
# [TESTS] tests/signal_ashare/test_trendline_sr_detector.py
# [A_module] module_id=MOD-SIG-069_sr | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""MOD-SIG-069 supplement — 趋势线/压力支撑自动识别（GAP-F-33，指数页叠加层后端）。

**颗粒度裁定（GAP-F-33 D 类核查结论）**：regime_detector（MOD-REGIME-001）
输出=日频 7 态概率分布 + Shrinkage 节流因子，无点位级趋势线/压力支撑输出
（其 MA 特征 intro 的「判断趋势方向和支撑压力位」仅为指标通用描述，非输出
契约）——**复用不成立，独立新建**（裁定留痕，详见 GAP7 报告 §GAP-F-33）。

算法（经典规则 MVP，纯函数）：
1. **分形极值**：窗口 ±k 满窗判定——bar i 为分形高 ⇔ high[i] 严格大于窗口
   内其余 high；分形低对称（边缘不满窗不判，防半窗伪极值）。
2. **价位聚类**：极值价按容差 tolerance_pct 聚类（均值口径）→ 水平位
   {price, touches, first/last_date}；触点数=强度。
3. **支撑/压力**：last_close 下方最近位=支撑（kind=support），上方最近位=
   压力（kind=resistance）；一侧无位 → None + notes（不硬编）。
4. **趋势线**：最近两个同向显著极值连线——两低点斜率>0 → 上升趋势线
   （uptrend），两高点斜率<0 → 下降趋势线（downtrend）；输出锚点日期/
   斜率/当前值/现价距离 %（同向不足两个 → 该向不出线）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1 日 K 序列 list[SRBar]（date/high/low/close 升序）
# 层: 算法
# - id: A1 分形极值（±k 满窗）
# - id: A2 价位聚类 → 支撑/压力
# - id: A3 趋势线（最近两同向极值）
# 层: 输出
# - id: O1 TrendSRAnalysis（levels + support/resistance + trendlines）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A1 --> A3
# A2,A3 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Final, Sequence

logger = logging.getLogger(__name__)

__all__: Final = [
    "SRAnalysis",
    "SRBar",
    "SRLevel",
    "TrendLine",
    "TrendSRConfig",
    "analyze_trend_sr",
]


# ------------------------------------------------------------------
# 配置 / 输入 / 输出
# ------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class TrendSRConfig:
    """识别配置（MVP 初拍值，待实盘标定）。"""

    fractal_window: int = 2  # 分形半窗 k（±k 满窗判定）
    tolerance_pct: float = 1.5  # 价位聚类容差 %（相对均值）
    max_levels: int = 10  # 位清单条数上限（触点数降序）


@dataclass(frozen=True, slots=True)
class SRBar:
    """日 K 输入（high/low/close；open 不参与本算法）。"""

    date: str
    high: float
    low: float
    close: float


@dataclass(frozen=True, slots=True)
class SRLevel:
    """水平位（支撑/压力）。"""

    price: float  # 聚类均值
    kind: str  # support/resistance
    touches: int
    first_date: str
    last_date: str


@dataclass(frozen=True, slots=True)
class TrendLine:
    """趋势线。"""

    kind: str  # uptrend/downtrend
    slope_per_bar: float
    anchor_dates: tuple[str, str]
    anchor_prices: tuple[float, float]
    current_value: float  # 线延伸至最新 bar 的值
    distance_pct: float  # 最新收相对线值距离 %（正=线上方）


@dataclass(frozen=True, slots=True)
class SRAnalysis:
    """趋势线/压力支撑输出（观测层消费，不接交易）。"""

    levels: list[SRLevel] = field(default_factory=list)  # 触点数降序
    support: SRLevel | None = None
    resistance: SRLevel | None = None
    trendlines: list[TrendLine] = field(default_factory=list)
    degraded: bool = False
    notes: list[str] = field(default_factory=list)


# ------------------------------------------------------------------
# 纯函数核
# ------------------------------------------------------------------


def _fractals(bars: Sequence[SRBar], k: int) -> tuple[list[tuple[int, float, str]], list[tuple[int, float, str]]]:
    """分形极值（满窗判定）→ (lows, highs)：(idx, price, date)。"""
    lows: list[tuple[int, float, str]] = []
    highs: list[tuple[int, float, str]] = []
    n = len(bars)
    for i in range(k, n - k):
        win_h = [bars[j].high for j in range(i - k, i + k + 1)]
        win_l = [bars[j].low for j in range(i - k, i + k + 1)]
        if bars[i].high == max(win_h) and win_h.count(bars[i].high) == 1:
            highs.append((i, bars[i].high, bars[i].date))
        if bars[i].low == min(win_l) and win_l.count(bars[i].low) == 1:
            lows.append((i, bars[i].low, bars[i].date))
    return lows, highs


def _cluster_levels(
    points: list[tuple[int, float, str]],
    tolerance_pct: float,
) -> list[tuple[float, int, str, str]]:
    """极值价聚类（容差 % 相对簇均值）→ (mean_price, touches, first_date, last_date)。"""
    clusters: list[list[tuple[int, float, str]]] = []
    for pt in sorted(points, key=lambda p: p[1]):
        placed = False
        for cl in clusters:
            mean = sum(p[1] for p in cl) / len(cl)
            if mean > 0 and abs(pt[1] - mean) / mean * 100.0 <= tolerance_pct:
                cl.append(pt)
                placed = True
                break
        if not placed:
            clusters.append([pt])
    out: list[tuple[float, int, str, str]] = []
    for cl in clusters:
        prices = [p[1] for p in cl]
        dates = sorted(p[2] for p in cl)
        out.append((sum(prices) / len(prices), len(prices), dates[0], dates[-1]))
    return out


def _build_line(
    p1: tuple[int, float, str],
    p2: tuple[int, float, str],
    kind: str,
    bars: Sequence[SRBar],
) -> TrendLine | None:
    """两锚点连线（斜率方向校验：uptrend 须 >0 / downtrend 须 <0）。"""
    span = p2[0] - p1[0]
    if span <= 0:
        return None
    slope = (p2[1] - p1[1]) / span
    if kind == "uptrend" and slope <= 0:
        return None
    if kind == "downtrend" and slope >= 0:
        return None
    last_idx = len(bars) - 1
    current = p2[1] + slope * (last_idx - p2[0])
    if current <= 0:
        return None
    distance = (bars[-1].close / current - 1.0) * 100.0
    return TrendLine(
        kind=kind,
        slope_per_bar=round(slope, 6),
        anchor_dates=(p1[2], p2[2]),
        anchor_prices=(round(p1[1], 4), round(p2[1], 4)),
        current_value=round(current, 4),
        distance_pct=round(distance, 4),
    )


def analyze_trend_sr(
    bars: Sequence[SRBar],
    config: TrendSRConfig | None = None,
) -> SRAnalysis:
    """趋势线/压力支撑识别主核（纯函数，不触库）。

    Args:
        bars: 日 K 序列（SRBar，date 升序；价格须为正，fail-closed）。
        config: 配置（None 用默认）。

    Returns:
        SRAnalysis；数据不足/无极值 → degraded 或空 levels + notes。

    Raises:
        ValueError: bars 元素类型非法 / 价格非正（fail-closed）。
    """
    cfg = config or TrendSRConfig()
    for b in bars:
        if not isinstance(b, SRBar):
            raise ValueError(f"bars 元素非法（须 SRBar）: {type(b).__name__}")
        for v in (b.high, b.low, b.close):
            if isinstance(v, bool) or not isinstance(v, (int, float)) or float(v) <= 0:
                raise ValueError(f"价格非法（须正实数）: {b.date} high={b.high!r} low={b.low!r} close={b.close!r}")
    k = cfg.fractal_window
    notes: list[str] = []
    if len(bars) < 2 * k + 1:
        return SRAnalysis(
            degraded=True,
            notes=[f"K 线不足（{len(bars)} 根 < {2 * k + 1} 根满窗要求），不出伪线"],
        )

    lows, highs = _fractals(bars, k)
    if not lows and not highs:
        notes.append("窗口内无分形极值（全平/单边无回摆），位与线均不出")

    # ---- 价位聚类 → 支撑/压力 ----
    low_levels = _cluster_levels(lows, cfg.tolerance_pct)
    high_levels = _cluster_levels(highs, cfg.tolerance_pct)
    last_close = float(bars[-1].close)
    levels: list[SRLevel] = []
    for price, touches, d0, d1 in low_levels:
        kind = "support" if price <= last_close else "resistance"
        levels.append(SRLevel(price=round(price, 4), kind=kind, touches=touches, first_date=d0, last_date=d1))
    for price, touches, d0, d1 in high_levels:
        kind = "resistance" if price >= last_close else "support"
        levels.append(SRLevel(price=round(price, 4), kind=kind, touches=touches, first_date=d0, last_date=d1))
    levels.sort(key=lambda l: (-l.touches, l.price))
    levels = levels[: cfg.max_levels]

    supports = [l for l in levels if l.kind == "support"]
    resistances = [l for l in levels if l.kind == "resistance"]
    support = max(supports, key=lambda l: l.price) if supports else None
    resistance = min(resistances, key=lambda l: l.price) if resistances else None
    if support is None:
        notes.append("现价下方无有效位，支撑 None（不硬编）")
    if resistance is None:
        notes.append("现价上方无有效位，压力 None（不硬编）")

    # ---- 趋势线（最近两个同向极值）----
    trendlines: list[TrendLine] = []
    if len(lows) >= 2:
        line = _build_line(lows[-2], lows[-1], "uptrend", bars)
        if line is not None:
            trendlines.append(line)
        else:
            notes.append("最近两低点斜率非正，上升趋势线不出")
    else:
        notes.append("有效低点不足两个，上升趋势线不出")
    if len(highs) >= 2:
        line = _build_line(highs[-2], highs[-1], "downtrend", bars)
        if line is not None:
            trendlines.append(line)
        else:
            notes.append("最近两高点斜率非负，下降趋势线不出")
    else:
        notes.append("有效高点不足两个，下降趋势线不出")

    return SRAnalysis(
        levels=levels,
        support=support,
        resistance=resistance,
        trendlines=trendlines,
        degraded=False,
        notes=notes,
    )

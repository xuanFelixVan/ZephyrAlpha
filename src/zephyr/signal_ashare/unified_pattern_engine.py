# [BLUEPRINT] MOD-SIG-091 | docs/03_modules/_domain_signal/unified_pattern_engine/blueprint.md
# [MODULE] zephyr.signal_ashare.unified_pattern_engine
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.chanlun_structure（MOD-SIG-072 缠论腿收编，testing）; zephyr.signal_ashare.trendline_sr_detector（MOD-SIG-069 支撑阻力腿收编，testing）
# [CONSUMERS] （候选：97形态→信号转化 B1-00849 后续波次、指数/个股页叠加层）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 六类图形封闭集；统一 PatternEvent 契约（类型+置信度+关键点位+方向+历史胜率）；同(name,anchor_idx)去重取最高置信度；输出按置信度降序；腿级故障隔离（缠论/SR腿 ValueError 降级留痕不传染整引擎）；历史胜率仅经注入契约；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] AUD-DRAFT-001 深挖批 B1-01010 行 + 候选注册表 CAND-TESTB-006；canonical 声明见蓝图（W-P1-04 B10-01391 同名条目由其波次 REVIEW）
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 空 symbol/序列空/不等长/非正价/非法配置 → ValueError（fail-closed）
# [TESTS] tests/signal_ashare/test_unified_pattern_engine.py
# [A_module] module_id=MOD-SIG-091 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""统一图形识别引擎（MOD-SIG-091，B1-01010，D-FACTOR-97）。

场内仅有缠论结构/席位形态/reversal 散件，无统一引擎；本引擎是 97 形态→信号
转化（B1-00849）的前置依赖（深挖裁定理由）。**canonical 实现**（W-P1-04
B10-01391 同名条目由其波次裁定 REVIEW，见蓝图声明）。

OHLCV 多级别输入 → 统一 PatternEvent 契约（图形类型+置信度+关键点位+预测
方向+历史胜率），六类封闭集：反转/持续/趋势/支撑阻力/缠论/波浪。

**规则引擎优先**（MVP 主力四腿）：
- 经典腿：双顶/双底（REVERSAL）+ 平台突破（CONTINUATION）；
- 缠论腿（收编 MOD-SIG-072）：中枢事件 + 末笔方向事件（CHANLUN）；
- 支撑阻力腿（收编 MOD-SIG-069）：水平位（SR）+ 趋势线（TREND）；
- DTW 模板腿：归一化序列 DTW 距离≤阈值→模板事件，置信度=1−距离/阈值。

**历史胜率**：win_rate_provider 注入契约（None=无统计），引擎不自建统计。
**CNN/Transformer 列后续档**（min_build_spec 明示，本波不施工）。
seat_pattern_analyzer（MOD-SIG-056，披露席位非 OHLCV）后续以适配器接入
（蓝图收编边界裁定，遗留项）。

置信度为文档化 MVP 初拍值（规则腿静态值/DTW 距离线性），待回验标定批替换。

依据: AUD-DRAFT-001 深挖批 B1-01010（裁定=做 P1）；蓝图 §0 边界
SSoT: depgraph blueprint_id=MOD-SIG-091
Version: 0.1.0

# [ALGO_FLOW]
# 输入: symbol + highs/lows/closes 等长序列 + timeframe
# 特征: 摆动点/平台振幅/缠论结构/水平位趋势线/归一化序列
# 算法: 经典腿 → 缠论腿 → SR腿 → DTW腿 → 胜率注入 → 去重排序
# 输出: PatternScanResult（events tuple[PatternEvent] + detector_stats + notes）
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Callable, Final, Sequence

from zephyr.signal_ashare.chanlun_structure import (
    FX_BOTTOM,
    FX_TOP,
    ChanlunConfig,
    analyze_chanlun,
)
from zephyr.signal_ashare.trendline_sr_detector import (
    SRBar,
    TrendSRConfig,
    analyze_trend_sr,
)

logger = logging.getLogger(__name__)

__all__: Final = [
    "KeyPoint",
    "PatternClass",
    "PatternDirection",
    "PatternEngineConfig",
    "PatternEvent",
    "PatternScanResult",
    "PatternTemplate",
    "UnifiedPatternEngine",
]


class PatternClass(str, Enum):
    """六类图形（封闭集）。"""

    REVERSAL = "反转"
    CONTINUATION = "持续"
    TREND = "趋势"
    SR = "支撑阻力"
    CHANLUN = "缠论"
    WAVE = "波浪"


class PatternDirection(str, Enum):
    """预测方向（封闭集）。"""

    UP = "向上"
    DOWN = "向下"
    NEUTRAL = "中性"


@dataclass(frozen=True, slots=True)
class KeyPoint:
    """关键点位（锚原始 K 下标）。"""

    idx: int
    price: float
    role: str  # 顶1/顶2/谷/中枢上沿/中枢下沿/水平位/线锚 等


@dataclass(frozen=True, slots=True)
class PatternEvent:
    """统一图形事件契约（97 形态→信号转化的输入单元）。"""

    pattern_id: str
    pattern_class: PatternClass
    name: str
    direction: PatternDirection
    confidence: float  # 0~1
    key_points: tuple[KeyPoint, ...]
    historical_win_rate: float | None  # None=无统计（注入契约）
    timeframe: str
    anchor_idx: int
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["pattern_class"] = self.pattern_class.value
        d["direction"] = self.direction.value
        return d


@dataclass(frozen=True, slots=True)
class PatternTemplate:
    """DTW 模板（series 须预归一化到 [0,1]）。"""

    name: str
    series: tuple[float, ...]
    pattern_class: PatternClass
    direction: PatternDirection

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("模板名不能为空")
        if len(self.series) < 3:
            raise ValueError(f"模板序列须≥3 点: {len(self.series)}")
        if any(not 0.0 <= v <= 1.0 for v in self.series):
            raise ValueError("模板序列须预归一化到 [0,1]")


@dataclass(frozen=True, slots=True)
class PatternEngineConfig:
    """统一图形识别引擎配置（MVP 初拍值待标定，全可配）。"""

    swing_window: int = 2  # 摆动点判定半窗
    double_extreme_tolerance_pct: float = 1.5  # 双顶/双底两极端容差 %
    double_extreme_min_gap: int = 5  # 两极端最小间隔根数
    consolidation_lookback: int = 20  # 平台回看根数
    consolidation_max_range_pct: float = 5.0  # 平台振幅上限 %
    breakout_margin_pct: float = 0.1  # 突破边际 %
    dtw_max_distance: float = 0.08  # DTW 距离上限（归一化，/(n+m) 口径）
    chanlun_min_bi_bars: int = 3  # 缠论腿严格笔跨距（引擎口径，比散件默认 5 宽松）
    enable_classic: bool = True
    enable_chanlun: bool = True
    enable_sr: bool = True
    enable_dtw: bool = True

    def __post_init__(self) -> None:
        if self.swing_window < 1:
            raise ValueError(f"swing_window 须≥1: {self.swing_window}")
        if self.double_extreme_tolerance_pct <= 0:
            raise ValueError("double_extreme_tolerance_pct 须>0")
        if self.double_extreme_min_gap < 2:
            raise ValueError("double_extreme_min_gap 须≥2")
        if self.consolidation_lookback < 5:
            raise ValueError("consolidation_lookback 须≥5")
        if self.consolidation_max_range_pct <= 0:
            raise ValueError("consolidation_max_range_pct 须>0")
        if not 0.0 < self.dtw_max_distance <= 1.0:
            raise ValueError(f"dtw_max_distance 须∈(0,1]: {self.dtw_max_distance}")
        if self.chanlun_min_bi_bars < 3:
            raise ValueError("chanlun_min_bi_bars 须≥3")


@dataclass(frozen=True, slots=True)
class PatternScanResult:
    """统一图形扫描输出。"""

    symbol: str
    timeframe: str
    events: tuple[PatternEvent, ...]
    detector_stats: dict[str, int] = field(default_factory=dict)
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        return d


def _normalize(series: Sequence[float]) -> list[float]:
    lo, hi = min(series), max(series)
    if hi - lo < 1e-12:
        return [0.0] * len(series)
    return [(x - lo) / (hi - lo) for x in series]


def _dtw_distance(a: Sequence[float], b: Sequence[float]) -> float:
    """经典 DTW（|差| 代价，/(n+m) 归一）。"""
    n, m = len(a), len(b)
    inf = float("inf")
    prev = [inf] * (m + 1)
    prev[0] = 0.0
    for i in range(1, n + 1):
        cur = [inf] * (m + 1)
        ai = a[i - 1]
        for j in range(1, m + 1):
            cost = abs(ai - b[j - 1])
            cur[j] = cost + min(prev[j], cur[j - 1], prev[j - 1])
        prev = cur
    return prev[m] / (n + m)


def _swing_points(
    series: Sequence[float], k: int, find_max: bool
) -> list[tuple[int, float]]:
    """满窗摆动极值点 (idx, price)。"""
    out: list[tuple[int, float]] = []
    n = len(series)
    for i in range(k, n - k):
        window = series[i - k : i + k + 1]
        v = series[i]
        if find_max and v == max(window) and window.count(v) == 1:
            out.append((i, v))
        elif not find_max and v == min(window) and window.count(v) == 1:
            out.append((i, v))
    return out


class UnifiedPatternEngine:
    """统一图形识别引擎（规则四腿 + DTW 模板腿 + 胜率注入）。"""

    def __init__(
        self,
        config: PatternEngineConfig | None = None,
        *,
        win_rate_provider: Callable[[str], float | None] | None = None,
        templates: Sequence[PatternTemplate] = (),
    ) -> None:
        self._cfg = config or PatternEngineConfig()
        self._win_rate = win_rate_provider
        self._templates = tuple(templates)

    # ── 经典腿：双顶/双底 + 平台突破 ─────────────────────
    def _classic_leg(
        self, highs: Sequence[float], lows: Sequence[float], closes: Sequence[float]
    ) -> list[PatternEvent]:
        cfg = self._cfg
        events: list[PatternEvent] = []
        tol = cfg.double_extreme_tolerance_pct / 100.0

        tops = _swing_points(highs, cfg.swing_window, True)
        for a in range(len(tops)):
            for b in range(a + 1, len(tops)):
                i1, p1 = tops[a]
                i2, p2 = tops[b]
                if i2 - i1 < cfg.double_extreme_min_gap:
                    continue
                if abs(p1 - p2) / ((p1 + p2) / 2) > tol:
                    continue
                valley = min(closes[i1 : i2 + 1])
                if valley >= min(p1, p2) * (1 - 0.005):
                    continue  # 中间无像样谷
                events.append(
                    self._event(
                        name="双顶",
                        cls=PatternClass.REVERSAL,
                        direction=PatternDirection.DOWN,
                        confidence=0.7,
                        key_points=(
                            KeyPoint(i1, p1, "顶1"),
                            KeyPoint(i2, p2, "顶2"),
                            KeyPoint(closes.index(valley, i1, i2 + 1), valley, "谷"),
                        ),
                        anchor=i2,
                    )
                )

        bots = _swing_points(lows, cfg.swing_window, False)
        for a in range(len(bots)):
            for b in range(a + 1, len(bots)):
                i1, p1 = bots[a]
                i2, p2 = bots[b]
                if i2 - i1 < cfg.double_extreme_min_gap:
                    continue
                if abs(p1 - p2) / ((p1 + p2) / 2) > tol:
                    continue
                peak = max(closes[i1 : i2 + 1])
                if peak <= max(p1, p2) * (1 + 0.005):
                    continue
                events.append(
                    self._event(
                        name="双底",
                        cls=PatternClass.REVERSAL,
                        direction=PatternDirection.UP,
                        confidence=0.7,
                        key_points=(
                            KeyPoint(i1, p1, "底1"),
                            KeyPoint(i2, p2, "底2"),
                            KeyPoint(closes.index(peak, i1, i2 + 1), peak, "峰"),
                        ),
                        anchor=i2,
                    )
                )

        # 平台突破：末根收突破前 N 根平台上沿/下沿
        n = len(closes)
        lb = cfg.consolidation_lookback
        if n > lb:
            seg_hi = max(highs[n - 1 - lb : n - 1])
            seg_lo = min(lows[n - 1 - lb : n - 1])
            mid = (seg_hi + seg_lo) / 2
            range_pct = (seg_hi - seg_lo) / mid * 100.0
            if range_pct <= cfg.consolidation_max_range_pct:
                last = closes[-1]
                margin = cfg.breakout_margin_pct / 100.0
                if last > seg_hi * (1 + margin):
                    events.append(
                        self._event(
                            name="平台突破",
                            cls=PatternClass.CONTINUATION,
                            direction=PatternDirection.UP,
                            confidence=0.6,
                            key_points=(KeyPoint(n - 1, last, "突破点"), KeyPoint(n - 2, seg_hi, "平台上沿")),
                            anchor=n - 1,
                            notes=(f"平台振幅 {range_pct:.2f}%",),
                        )
                    )
                elif last < seg_lo * (1 - margin):
                    events.append(
                        self._event(
                            name="平台跌破",
                            cls=PatternClass.CONTINUATION,
                            direction=PatternDirection.DOWN,
                            confidence=0.6,
                            key_points=(KeyPoint(n - 1, last, "跌破点"), KeyPoint(n - 2, seg_lo, "平台下沿")),
                            anchor=n - 1,
                            notes=(f"平台振幅 {range_pct:.2f}%",),
                        )
                    )
        return events

    # ── 缠论腿（收编 MOD-SIG-072）────────────────────────
    def _chanlun_leg(
        self, highs: Sequence[float], lows: Sequence[float], notes: list[str]
    ) -> list[PatternEvent]:
        events: list[PatternEvent] = []
        try:
            st = analyze_chanlun(
                highs, lows, config=ChanlunConfig(min_bi_bars=self._cfg.chanlun_min_bi_bars)
            )
        except ValueError as exc:
            notes.append(f"缠论腿降级: {exc}")
            return events
        for zs in st.zhongshus:
            events.append(
                self._event(
                    name="缠论中枢",
                    cls=PatternClass.CHANLUN,
                    direction=PatternDirection.NEUTRAL,
                    confidence=0.6,
                    key_points=(
                        KeyPoint(zs.end_bi, zs.zg, "中枢上沿"),
                        KeyPoint(zs.end_bi, zs.zd, "中枢下沿"),
                    ),
                    anchor=zs.end_bi,
                    notes=(f"笔数={zs.bi_count}",),
                )
            )
        if st.bis:
            last = st.bis[-1]
            up = last.direction == "up"
            events.append(
                self._event(
                    name="缠论向上笔" if up else "缠论向下笔",
                    cls=PatternClass.CHANLUN,
                    direction=PatternDirection.UP if up else PatternDirection.DOWN,
                    confidence=0.5,
                    key_points=(
                        KeyPoint(last.start_idx, last.start_price, "笔起"),
                        KeyPoint(last.end_idx, last.end_price, "笔止"),
                    ),
                    anchor=last.end_idx,
                )
            )
        return events

    # ── 支撑阻力腿（收编 MOD-SIG-069）────────────────────
    def _sr_leg(
        self,
        highs: Sequence[float],
        lows: Sequence[float],
        closes: Sequence[float],
        notes: list[str],
    ) -> list[PatternEvent]:
        events: list[PatternEvent] = []
        bars = [
            SRBar(date=f"bar{i}", high=h, low=l, close=c)
            for i, (h, l, c) in enumerate(zip(highs, lows, closes))
        ]
        try:
            sr = analyze_trend_sr(bars, TrendSRConfig())
        except ValueError as exc:
            notes.append(f"支撑阻力腿降级: {exc}")
            return events
        n = len(closes)
        for lv in sr.levels:
            events.append(
                self._event(
                    name="支撑位" if lv.kind == "support" else "压力位",
                    cls=PatternClass.SR,
                    direction=PatternDirection.NEUTRAL,
                    confidence=min(0.5 + 0.05 * lv.touches, 0.9),
                    key_points=(KeyPoint(n - 1, lv.price, "水平位"),),
                    anchor=n - 1,
                    notes=(f"触点={lv.touches}",),
                )
            )
        for tl in sr.trendlines:
            up = tl.kind == "uptrend"
            events.append(
                self._event(
                    name="上升趋势线" if up else "下降趋势线",
                    cls=PatternClass.TREND,
                    direction=PatternDirection.UP if up else PatternDirection.DOWN,
                    confidence=0.5,
                    key_points=(
                        KeyPoint(0, tl.anchor_prices[0], "线锚1"),
                        KeyPoint(n - 1, tl.current_value, "线现值"),
                    ),
                    anchor=n - 1,
                    notes=(f"距线 {tl.distance_pct:.2f}%",),
                )
            )
        return events

    # ── DTW 模板腿 ───────────────────────────────────────
    def _dtw_leg(self, closes: Sequence[float]) -> list[PatternEvent]:
        cfg = self._cfg
        events: list[PatternEvent] = []
        for tpl in self._templates:
            w = len(tpl.series)
            if len(closes) < w:
                continue
            seg = _normalize(closes[-w:])
            dist = _dtw_distance(seg, tpl.series)
            if dist > cfg.dtw_max_distance:
                continue
            events.append(
                self._event(
                    name=f"DTW模板:{tpl.name}",
                    cls=tpl.pattern_class,
                    direction=tpl.direction,
                    confidence=1.0 - dist / cfg.dtw_max_distance,
                    key_points=(KeyPoint(len(closes) - 1, closes[-1], "模板锚"),),
                    anchor=len(closes) - 1,
                    notes=(f"dtw={dist:.4f}",),
                )
            )
        return events

    # ── 事件装配（胜率注入）─────────────────────────────
    def _event(
        self,
        *,
        name: str,
        cls: PatternClass,
        direction: PatternDirection,
        confidence: float,
        key_points: tuple[KeyPoint, ...],
        anchor: int,
        notes: tuple[str, ...] = (),
    ) -> PatternEvent:
        win_rate = self._win_rate(name) if self._win_rate else None
        return PatternEvent(
            pattern_id=f"{name}@{anchor}",
            pattern_class=cls,
            name=name,
            direction=direction,
            confidence=confidence,
            key_points=key_points,
            historical_win_rate=win_rate,
            timeframe="",
            anchor_idx=anchor,
            notes=notes,
        )

    # ── 主入口 ───────────────────────────────────────────
    def recognize(
        self,
        symbol: str,
        highs: Sequence[float],
        lows: Sequence[float],
        closes: Sequence[float],
        *,
        timeframe: str = "1d",
    ) -> PatternScanResult:
        """OHLCV → 统一 PatternEvent 序列（去重+置信度降序）。"""
        if not symbol:
            raise ValueError("symbol 不能为空")
        n = len(closes)
        if n == 0:
            raise ValueError("输入序列不能为空")
        if len(highs) != n or len(lows) != n:
            raise ValueError(f"序列不等长: highs={len(highs)} lows={len(lows)} closes={n}")
        for i in range(n):
            if highs[i] <= 0 or lows[i] <= 0 or closes[i] <= 0:
                raise ValueError(f"价格须为正: idx={i}")
            if highs[i] < lows[i]:
                raise ValueError(f"high<low: idx={i}")

        cfg = self._cfg
        notes: list[str] = []
        raw: list[PatternEvent] = []
        stats: dict[str, int] = {}

        if cfg.enable_classic:
            ev = self._classic_leg(highs, lows, closes)
            raw.extend(ev)
            stats["classic"] = len(ev)
        if cfg.enable_chanlun:
            ev = self._chanlun_leg(highs, lows, notes)
            raw.extend(ev)
            stats["chanlun"] = len(ev)
        if cfg.enable_sr:
            ev = self._sr_leg(highs, lows, closes, notes)
            raw.extend(ev)
            stats["sr"] = len(ev)
        if cfg.enable_dtw:
            ev = self._dtw_leg(closes)
            raw.extend(ev)
            stats["dtw"] = len(ev)

        # 去重：同 (name, anchor_idx) 取置信度最高；补 timeframe
        best: dict[tuple[str, int], PatternEvent] = {}
        for e in raw:
            e = PatternEvent(
                pattern_id=e.pattern_id,
                pattern_class=e.pattern_class,
                name=e.name,
                direction=e.direction,
                confidence=e.confidence,
                key_points=e.key_points,
                historical_win_rate=e.historical_win_rate,
                timeframe=timeframe,
                anchor_idx=e.anchor_idx,
                notes=e.notes,
            )
            key = (e.name, e.anchor_idx)
            if key not in best or e.confidence > best[key].confidence:
                best[key] = e
        events = tuple(sorted(best.values(), key=lambda e: e.confidence, reverse=True))

        logger.info("图形识别: %s@%s 事件=%d 明细=%s", symbol, timeframe, len(events), stats)
        return PatternScanResult(
            symbol=symbol,
            timeframe=timeframe,
            events=events,
            detector_stats=stats,
            notes=tuple(notes),
        )

# [BLUEPRINT] MOD-SIG-072 | 待统筹登记（缺口总账 GAP-F-37 行）
# [MODULE] zephyr.signal_ashare.chanlun_structure
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] 无（纯函数核，零 DB/网络/LLM）
# [CONSUMERS] （候选：指数/个股页缠论叠加层，GAP-F-37 消费位；chart_pattern_registry PAT-CLL-001~006 算法承载件）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 三级生成链固定：包含处理→顶底分型→笔→线段→中枢；严格笔跨距 ≥min_bi_bars（默认 5，chart_pattern_registry PAT-CLL-003/004"严格笔需独立K线>=5"）；笔顶底交替、同类分型取更极端者；线段 ≥3 笔且前三笔重叠（MVP 近似特征序列法，文档化）；中枢=≥3 连续笔重叠区 [ZD,ZG]（ZD<ZG）；所有锚点回指原始 K 线下标；输入校验 fail-closed；frozen dataclass JSON 可序列化
# [MODIFY-GUARD] docs/_working/2026-08-22-frontend-backend-gap-ledger.md GAP-F-37 行
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError（根数不足/序列不等长/high<low/价格非法/min_bi_bars 越界，fail-closed）
# [TESTS] tests/signal_ashare/test_chanlun_structure.py
# [A_module] module_id=MOD-SIG-072 | layer=module | stability=testing | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""缠论笔/段/中枢自动识别（MOD-SIG-072，GAP-F-37）。

缺口总账 GAP-F-37（指数/个股页叠加层）：chart_pattern_registry 已有缠论顶底
分型登记（PAT-CLL-001/002，candidate 零代码），本模块把三级生成链一次落码：

    ① 包含处理：相含 K 线按方向合并（向上取 max/max、向下取 min/min），
       合并后序列才是分型/笔的计算基（PAT-CLL-001/002 inclusion_process=true）。
    ② 顶底分型：合并序列三 K 中间高点最高且低点最高=顶分型（反之为底分型）。
    ③ 笔：顶底分型交替连接，严格笔跨距（两端分型间合并 K 数，含端点）
       ≥min_bi_bars（默认 5，PAT-CLL-003/004）；同类型相邻分型取更极端者。
    ④ 线段（MVP 近似，文档化）：≥3 连续笔且前三笔价格区间有重叠即成段，
       方向=首笔方向；顺向笔创新高/低延展，反向笔破坏前低/前高则终结
       （特征序列法的轻量近似，非全规格实现）。
    ⑤ 中枢：≥3 连续笔重叠区 ZG=min(各笔高点)、ZD=max(各笔低点)，ZD<ZG 成立；
       后续笔区间与 [ZD,ZG] 相交则延展，脱离则终结。

不做什么：不识别买卖点（PAT-CLL-007~012 背驰/区间套后续）/不读库/不荐股——
输出是结构描摹数据（供叠加层渲染），非交易信号。

依据: 缺口总账 GAP-F-37；chart_pattern_registry CHANLUN 段（2026-08-14 新建，
对齐 chan.py/chanlun-pro 开源口径）；缠中说禅 108 课第 62-65 课
SSoT: depgraph node 10505567（MOD-SIG-072，待统筹登记）
Version: 0.1.0

# [ALGO_FLOW]
# 输入: highs/lows 升序等长序列 + ChanlunConfig
# 特征: 合并 K 序列 / 顶底分型点
# 算法: 包含合并 → 分型识别 → 严格笔连接 → 线段分组 → 中枢区间
# 输出: ChanlunStructure（fractals/bis/segments/zhongshus 全锚原始下标）
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from typing import Any, Final, Sequence

logger = logging.getLogger(__name__)

__all__: Final = [
    "FX_BOTTOM",
    "FX_TOP",
    "ChanBar",
    "ChanlunConfig",
    "ChanlunStructure",
    "ChanlunZhongshu",
    "ChanSegment",
    "ChanStroke",
    "Fractal",
    "analyze_chanlun",
]

FX_TOP: Final = "top"
FX_BOTTOM: Final = "bottom"

DIR_UP: Final = "up"
DIR_DOWN: Final = "down"


@dataclass(frozen=True, slots=True)
class ChanlunConfig:
    """缠论识别配置（参数 >4 收 dataclass）。

    Attributes:
        min_bi_bars: 严格笔最小跨距（合并 K 数含端点，默认 5=PAT-CLL-003/004 口径）。
        inclusion_process: 是否先做包含处理（默认 True=PAT-CLL-001/002 口径）。
        min_bars: 最小输入根数（不足 fail-closed）。
    """

    min_bi_bars: int = 5
    inclusion_process: bool = True
    min_bars: int = 5

    def __post_init__(self) -> None:
        if int(self.min_bi_bars) < 3:
            raise ValueError(f"min_bi_bars 非法（须 ≥3）: {self.min_bi_bars!r}")
        if int(self.min_bars) < 5:
            raise ValueError(f"min_bars 非法（须 ≥5）: {self.min_bars!r}")


@dataclass(frozen=True, slots=True)
class ChanBar:
    """合并后 K 线（锚点回指原始下标区间）。"""

    high: float
    low: float
    start_idx: int  # 原始首根下标
    end_idx: int  # 原始末根下标


@dataclass(frozen=True, slots=True)
class Fractal:
    """分型（pos=合并序列下标，anchor_idx=原始 K 下标）。"""

    kind: str  # FX_TOP / FX_BOTTOM
    pos: int
    price: float  # 顶=high / 底=low
    anchor_idx: int


@dataclass(frozen=True, slots=True)
class ChanStroke:
    """笔（顶底分型连接，锚点回指原始下标）。"""

    direction: str  # up=底→顶 / down=顶→底
    start_pos: int  # 合并序列下标
    end_pos: int
    start_price: float
    end_price: float
    start_idx: int  # 原始 K 下标
    end_idx: int
    bar_count: int  # 跨距（合并 K 数含端点）

    @property
    def hi(self) -> float:
        return max(self.start_price, self.end_price)

    @property
    def lo(self) -> float:
        return min(self.start_price, self.end_price)


@dataclass(frozen=True, slots=True)
class ChanSegment:
    """线段（≥3 笔，方向=首笔方向）。"""

    direction: str
    start_bi: int  # 笔列表下标
    end_bi: int
    start_price: float
    end_price: float
    bi_count: int


@dataclass(frozen=True, slots=True)
class ChanlunZhongshu:
    """中枢（≥3 连续笔重叠区 [ZD, ZG]）。"""

    zd: float  # 中枢下沿
    zg: float  # 中枢上沿
    start_bi: int
    end_bi: int
    bi_count: int


@dataclass(frozen=True, slots=True)
class ChanlunStructure:
    """缠论三级结构总产出（JSON 可序列化）。"""

    n_bars: int
    n_merged: int
    fractals: tuple[Fractal, ...]
    bis: tuple[ChanStroke, ...]
    segments: tuple[ChanSegment, ...]
    zhongshus: tuple[ChanlunZhongshu, ...]
    notes: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ── ① 包含处理 ──


def _merge_bars(highs: Sequence[float], lows: Sequence[float], inclusion: bool) -> list[ChanBar]:
    merged = [ChanBar(float(highs[0]), float(lows[0]), 0, 0)]
    for i in range(1, len(highs)):
        cur_h, cur_l = float(highs[i]), float(lows[i])
        last = merged[-1]
        contained = (cur_h <= last.high and cur_l >= last.low) or (cur_h >= last.high and cur_l <= last.low)
        if contained and inclusion:
            if len(merged) >= 2:
                up = merged[-1].high > merged[-2].high
            else:
                up = cur_h >= last.high
            if up:
                merged[-1] = ChanBar(max(last.high, cur_h), max(last.low, cur_l), last.start_idx, i)
            else:
                merged[-1] = ChanBar(min(last.high, cur_h), min(last.low, cur_l), last.start_idx, i)
        else:
            merged.append(ChanBar(cur_h, cur_l, i, i))
    return merged


# ── ② 顶底分型 ──


def _detect_fractals(merged: list[ChanBar]) -> list[Fractal]:
    fractals: list[Fractal] = []
    for i in range(1, len(merged) - 1):
        prev, cur, nxt = merged[i - 1], merged[i], merged[i + 1]
        if cur.high > prev.high and cur.high > nxt.high and cur.low > prev.low and cur.low > nxt.low:
            fractals.append(Fractal(kind=FX_TOP, pos=i, price=cur.high, anchor_idx=cur.start_idx))
        elif cur.low < prev.low and cur.low < nxt.low and cur.high < prev.high and cur.high < nxt.high:
            fractals.append(Fractal(kind=FX_BOTTOM, pos=i, price=cur.low, anchor_idx=cur.start_idx))
    return fractals


# ── ③ 笔 ──


def _build_strokes(fractals: list[Fractal], min_bi_bars: int) -> list[ChanStroke]:
    strokes: list[ChanStroke] = []
    pending: Fractal | None = None
    for fx in fractals:
        if pending is None:
            pending = fx
            continue
        if fx.kind == pending.kind:
            # 同类相邻取更极端者
            if (fx.kind == FX_TOP and fx.price >= pending.price) or (
                fx.kind == FX_BOTTOM and fx.price <= pending.price
            ):
                pending = fx
            continue
        span = fx.pos - pending.pos + 1
        price_ok = (pending.kind == FX_BOTTOM and fx.price > pending.price) or (
            pending.kind == FX_TOP and fx.price < pending.price
        )
        if span >= min_bi_bars and price_ok:
            strokes.append(
                ChanStroke(
                    direction=DIR_UP if pending.kind == FX_BOTTOM else DIR_DOWN,
                    start_pos=pending.pos,
                    end_pos=fx.pos,
                    start_price=pending.price,
                    end_price=fx.price,
                    start_idx=pending.anchor_idx,
                    end_idx=fx.anchor_idx,
                    bar_count=span,
                )
            )
            pending = fx
        # 跨距不足/价格倒挂：该分型不成笔端点，保留 pending 等下一个
    return strokes


# ── ④ 线段（MVP 近似）──


def _three_overlap(a: ChanStroke, b: ChanStroke, c: ChanStroke) -> bool:
    return min(a.hi, b.hi, c.hi) > max(a.lo, b.lo, c.lo)


def _build_segments(strokes: list[ChanStroke]) -> list[ChanSegment]:
    segments: list[ChanSegment] = []
    i = 0
    n = len(strokes)
    while i + 2 < n:
        b0, b1, b2 = strokes[i], strokes[i + 1], strokes[i + 2]
        if not _three_overlap(b0, b1, b2):
            i += 1
            continue
        direction = b0.direction
        j = i + 2
        if direction == DIR_UP:
            extreme = max(b0.end_price, b2.end_price)
            last_down_extreme = b1.end_price  # 前一下笔低点
            k = i + 3
            while k < n:
                bk = strokes[k]
                if bk.direction == DIR_UP:
                    if bk.end_price > extreme:
                        extreme = bk.end_price
                        j = k
                else:
                    if bk.end_price < last_down_extreme:
                        break  # 下笔破前低 → 线段向下终结
                    last_down_extreme = bk.end_price
                    j = k
                k += 1
        else:
            extreme = min(b0.end_price, b2.end_price)
            last_up_extreme = b1.end_price
            k = i + 3
            while k < n:
                bk = strokes[k]
                if bk.direction == DIR_DOWN:
                    if bk.end_price < extreme:
                        extreme = bk.end_price
                        j = k
                else:
                    if bk.end_price > last_up_extreme:
                        break  # 上笔破前高 → 线段向上终结
                    last_up_extreme = bk.end_price
                    j = k
                k += 1
        segments.append(
            ChanSegment(
                direction=direction,
                start_bi=i,
                end_bi=j,
                start_price=strokes[i].start_price,
                end_price=strokes[j].end_price,
                bi_count=j - i + 1,
            )
        )
        i = j + 1
    return segments


# ── ⑤ 中枢 ──


def _build_zhongshus(strokes: list[ChanStroke]) -> list[ChanlunZhongshu]:
    zhongshus: list[ChanlunZhongshu] = []
    i = 0
    n = len(strokes)
    while i + 2 < n:
        three = strokes[i : i + 3]
        zg = min(b.hi for b in three)
        zd = max(b.lo for b in three)
        if zd >= zg:
            i += 1
            continue
        j = i + 2
        k = i + 3
        while k < n and strokes[k].lo <= zg and strokes[k].hi >= zd:
            j = k
            k += 1
        zhongshus.append(ChanlunZhongshu(zd=zd, zg=zg, start_bi=i, end_bi=j, bi_count=j - i + 1))
        i = j + 1
    return zhongshus


def analyze_chanlun(
    highs: Sequence[float],
    lows: Sequence[float],
    *,
    config: ChanlunConfig | None = None,
) -> ChanlunStructure:
    """缠论三级结构识别主入口（包含→分型→笔→线段→中枢）。

    Args:
        highs: 最高价升序序列（正且有限）。
        lows: 最低价升序序列（与 highs 等长，逐根 high>=low）。
        config: 识别配置（None=默认严格笔跨距 5+包含处理）。

    Returns:
        ChanlunStructure（全锚原始 K 下标，JSON 可序列化）。

    Raises:
        ValueError: 输入/参数非法（fail-closed）。
    """
    cfg = config or ChanlunConfig()
    h = [float(x) for x in highs]
    low = [float(x) for x in lows]
    if len(h) != len(low):
        raise ValueError(f"highs/lows 须等长: {len(h)} vs {len(low)}")
    if len(h) < cfg.min_bars:
        raise ValueError(f"根数不足（须 ≥{cfg.min_bars}）: n={len(h)}")
    import math as _math

    for x in (*h, *low):
        if not _math.isfinite(x) or x <= 0:
            raise ValueError(f"价格非法（须全部为正且有限）: {x!r}")
    for hi, lo in zip(h, low):
        if hi < lo:
            raise ValueError(f"high<low 非法: high={hi!r} low={lo!r}")

    notes: list[str] = []
    merged = _merge_bars(h, low, cfg.inclusion_process)
    if len(merged) < len(h):
        notes.append(f"包含处理合并 {len(h) - len(merged)} 根（{len(h)}→{len(merged)}）")

    fractals = _detect_fractals(merged)
    strokes = _build_strokes(fractals, cfg.min_bi_bars)
    segments = _build_segments(strokes)
    zhongshus = _build_zhongshus(strokes)
    if strokes and not segments:
        notes.append("笔数/重叠不足未成段（≥3 笔且前三笔重叠才成段）")

    return ChanlunStructure(
        n_bars=len(h),
        n_merged=len(merged),
        fractals=tuple(fractals),
        bis=tuple(strokes),
        segments=tuple(segments),
        zhongshus=tuple(zhongshus),
        notes=tuple(notes),
    )

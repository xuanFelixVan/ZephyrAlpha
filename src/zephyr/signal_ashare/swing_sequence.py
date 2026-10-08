# [BLUEPRINT] MOD-SIG-147 | master_tc_night C234（波10 G-C.2 摆动结构序列 LH/HL 双峰检测）
# [MODULE] zephyr.signal_ashare.swing_sequence
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.chanlun_structure（纯函数核复用，唯一极值检测实现）；标准库
# [CONSUMERS] zephyr.signal_ashare.resonance_pair（C235 共振定义器，1M 双峰输入源）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 极值检测唯一实现=复用 chanlun 分型（经 analyze_chanlun，禁造第二套极值算法）；摆动点=chanlun 顶/底分型（顶分型↔swing high，底分型↔swing low，锚点回指原始 K 下标）；序列标注只分类不改动检测：LH=低峰（lower high）/HH=高峰（higher high）/HL=抬底（higher low）/LL=踏空底（lower low）；EQ 容差（tolerance_pct）吸收并列峰（双顶/双底语义载体），容差外才计 LH/HH；序列长度不足 2 个同向摆动点=标注空（不造序列）；输入校验 fail-closed（透传 chanlun）；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] master_tc_night/lanes/L6_factory/00_workbook.md C234 节
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError（透传 chanlun_structure.analyze_chanlun：根数不足/序列不等长/high<low 等，fail-closed）
# [TESTS] tests/signal_ashare/test_swing_sequence.py
# [A_module] module_id=MOD-SIG-147 | layer=module | stability=testing | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""摆动结构序列——LH/HL 双峰序列检测（MOD-SIG-147，波10 G-C.2）。

**极值检测唯一实现声明**：摆动点全部复用 `chanlun_structure.analyze_chanlun`
的顶/底分型（MOD-SIG-072），本模块只做分型之上的**序列标注**（LH/HH/HL/LL
+双峰提取），零新增极值算法。

**枢轴确认窗口径（dossier_institution §2.1 显式标记，C253 采纳）**：

    TradingView 官方"自动图表形态"枢轴口径 = 每根 K 线回看 left_bars 根 +
    右看 right_bars 根确认（官方默认 left=right=5），确认延迟=right_bars 根
    （防重绘的代价，平台自认局限）。
    本实现口径 = 缠论分型 = 包含处理后的合并序列上 left=right=1 严格枢轴
    （PAT-CLL-001/002），即 TV 口径在 (left=1, right=1) + 包含处理下的特例；
    二者差异两点：①包含处理使 A 股相含 K 不产生假枢轴；②确认窗更短=更早
    确认但噪声略多。选缠论口径理由：与既有 7 件涨停基座同一结构语言，且
   PAT-CLL 登记在案。left/right>1 的广义 TV 确认窗不在本模块实现——若消费
    侧需要，应扩 chanlun 参数而非在此造第二套检测（单一真源铁律）。

**序列语义**：
    顶序列（swing highs）：相邻两顶比较 → LH（更高低峰）/ HH（更高高峰）/
        EQ（容差带内并列——双顶载体）
    底序列（swing lows）：相邻两底比较 → HL（抬底）/ LL（踏空底）/
        EQ（容差带内并列——双底载体）
    双峰提取（double peak）= 最近两个顶摆动点的组合态，供 C235 共振定义器
    消费（1M 双峰 × 15M 上沿）。

不做什么：不识别形态名（双顶/头肩等命名归 chart_pattern_registry）/不读库/
不荐股不触发——输出是序列描摹数据，非交易信号。

依据: 波10 G-C.2；dossier_institution_practice.md §一主题2（枢轴+几何规则路线，
§2.1/2.5 确认延迟局限）；chanlun_structure.py（MOD-SIG-072）。
SSoT: depgraph node MOD-SIG-147（随本批 apply_depgraph 登记）
Version: 0.1.0

# [ALGO_FLOW]
# 输入: highs/lows 升序等长序列 + SwingConfig（tolerance_pct）
# 特征: chanlun 分型点 → 摆动点序列
# 算法: 复用分型检测 → 同向相邻比较标注（容差带判 EQ）→ 最近双峰组合
# 输出: SwingSequence（标注点/双峰组合，锚点回指原始下标）
"""

from __future__ import annotations

import itertools
import logging
from dataclasses import asdict, dataclass
from typing import Any, Final, Sequence

from zephyr.signal_ashare.chanlun_structure import (
    FX_BOTTOM,
    FX_TOP,
    ChanlunConfig,
    Fractal,
    analyze_chanlun,
)

logger = logging.getLogger(__name__)

__all__: Final = [
    "SWING_HIGH",
    "SWING_LOW",
    "REL_LH",
    "REL_HH",
    "REL_EQ",
    "SwingConfig",
    "SwingPoint",
    "SwingLabel",
    "DoublePeak",
    "SwingSequence",
    "detect_swing_sequence",
]

SWING_HIGH: Final = "high"  # 摆动高点（缠论顶分型）
SWING_LOW: Final = "low"  # 摆动低点（缠论底分型）

REL_LH: Final = "LH"  # lower high：较前顶更低
REL_HH: Final = "HH"  # higher high：较前顶更高
REL_HL: Final = "HL"  # higher low：较前底更高
REL_LL: Final = "LL"  # lower low：较前底更低
REL_EQ: Final = "EQ"  # 容差带内并列（双顶/双底载体）


@dataclass(frozen=True, slots=True)
class SwingConfig:
    """摆动序列配置。

    Attributes:
        tolerance_pct: 并列判定容差（两摆动点价差/前点价，默认 0.3%=双峰容差）。
        min_bars: 透传 chanlun 最小根数（fail-closed 下限）。
        min_bi_bars: 透传 chanlun 严格笔跨距。
    """

    tolerance_pct: float = 0.3
    min_bars: int = 5
    min_bi_bars: int = 5

    def __post_init__(self) -> None:
        if not (0.0 <= float(self.tolerance_pct) <= 10.0):
            raise ValueError(f"tolerance_pct 非法（0~10）: {self.tolerance_pct!r}")
        if int(self.min_bars) < 5:
            raise ValueError(f"min_bars 非法（须 ≥5，chanlun fail-closed 下限）: {self.min_bars!r}")
        if int(self.min_bi_bars) < 3:
            raise ValueError(f"min_bi_bars 非法（须 ≥3）: {self.min_bi_bars!r}")


@dataclass(frozen=True, slots=True)
class SwingPoint:
    """摆动点（自 chanlun 分型投影，kind=high/low，锚点回指原始 K 下标）。"""

    kind: str  # SWING_HIGH / SWING_LOW
    price: float
    anchor_idx: int
    fractal_pos: int  # 合并序列下标（chanlun Fractal.pos 透传）

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SwingLabel:
    """相邻同向摆动点关系标注。"""

    kind: str  # SWING_HIGH / SWING_LOW（序列类型）
    relation: str  # LH/HH/EQ（顶序列）或 HL/LL/EQ（底序列）
    prev: SwingPoint
    cur: SwingPoint
    delta_pct: float  # (cur-prev)/prev，方向带号


@dataclass(frozen=True, slots=True)
class DoublePeak:
    """双峰组合（最近两个同向摆动点；C235 共振定义器输入件）。"""

    kind: str  # SWING_HIGH（双顶候选）/ SWING_LOW（双底候选）
    first: SwingPoint
    second: SwingPoint
    is_equal_within_tolerance: bool  # True=EQ 双峰（共振语义）；False=已分出 LH/HH

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class SwingSequence:
    """摆动序列总产出（JSON 可序列化）。"""

    highs: tuple[SwingPoint, ...]
    lows: tuple[SwingPoint, ...]
    high_labels: tuple[SwingLabel, ...]  # 顶序列相邻标注（len = len(highs)-1）
    low_labels: tuple[SwingLabel, ...]
    last_double_peak: DoublePeak | None  # 最近同向双峰（优先顶序列；无则底序列）
    n_fractals: int  # chanlun 分型总数（来源透传计数）

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _to_swing_point(fx: Fractal) -> SwingPoint:
    return SwingPoint(
        kind=SWING_HIGH if fx.kind == FX_TOP else SWING_LOW,
        price=float(fx.price),
        anchor_idx=int(fx.anchor_idx),
        fractal_pos=int(fx.pos),
    )


def _rel(prev: SwingPoint, cur: SwingPoint, tol: float) -> tuple[str, float]:
    delta_pct = (cur.price - prev.price) / prev.price if prev.price != 0 else 0.0
    if abs(delta_pct) * 100.0 <= tol:
        return REL_EQ, delta_pct
    if cur.price > prev.price:
        return (REL_HH, delta_pct) if cur.kind == SWING_HIGH else (REL_HL, delta_pct)
    return (REL_LH, delta_pct) if cur.kind == SWING_HIGH else (REL_LL, delta_pct)


def _label_run(points: tuple[SwingPoint, ...], tol: float) -> tuple[SwingLabel, ...]:
    labels: list[SwingLabel] = []
    for prev, cur in itertools.pairwise(points):
        rel, d = _rel(prev, cur, tol)
        labels.append(SwingLabel(kind=cur.kind, relation=rel, prev=prev, cur=cur, delta_pct=d))
    return tuple(labels)


def _last_double(highs: tuple[SwingPoint, ...], lows: tuple[SwingPoint, ...], tol: float) -> DoublePeak | None:
    for run in (highs, lows):  # 优先顶序列双峰（G-C.3 上沿×双峰语义在顶侧）
        if len(run) >= 2:
            first, second = run[-2], run[-1]
            _, d = _rel(first, second, tol)
            return DoublePeak(
                kind=first.kind,
                first=first,
                second=second,
                is_equal_within_tolerance=(abs(d) * 100.0 <= tol),
            )
    return None


def detect_swing_sequence(
    highs: Sequence[float],
    lows: Sequence[float],
    config: SwingConfig | None = None,
) -> SwingSequence:
    """摆动序列检测（极值检测复用 chanlun 分型，本函数只做序列标注）。

    Args:
        highs/lows: 原始 K 线高低价升序等长序列（透传 chanlun 校验）。
        config: SwingConfig（tolerance_pct 并列容差等）。

    Returns:
        SwingSequence：顶/底摆动点 + 相邻标注 + 最近双峰。

    Raises:
        ValueError: 透传 chanlun_structure.analyze_chanlun 校验（fail-closed）。
    """
    cfg = config or SwingConfig()
    structure = analyze_chanlun(
        highs,
        lows,
        config=ChanlunConfig(min_bi_bars=cfg.min_bi_bars, inclusion_process=True, min_bars=cfg.min_bars),
    )
    swings = [_to_swing_point(fx) for fx in structure.fractals]
    highs_t = tuple(p for p in swings if p.kind == SWING_HIGH)
    lows_t = tuple(p for p in swings if p.kind == SWING_LOW)
    tol = float(cfg.tolerance_pct)
    seq = SwingSequence(
        highs=highs_t,
        lows=lows_t,
        high_labels=_label_run(highs_t, tol),
        low_labels=_label_run(lows_t, tol),
        last_double_peak=_last_double(highs_t, lows_t, tol),
        n_fractals=len(structure.fractals),
    )
    logger.info(
        "detect_swing_sequence: %d K → %d 分型 → 顶 %d/底 %d（labels H=%d L=%d, double=%s）",
        len(highs),
        seq.n_fractals,
        len(highs_t),
        len(lows_t),
        len(seq.high_labels),
        len(seq.low_labels),
        seq.last_double_peak is not None,
    )
    return seq

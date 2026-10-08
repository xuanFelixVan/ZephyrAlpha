# [BLUEPRINT] MOD-SIG-148 | master_tc_night C235（波10 G-C.3 共振条件对定义器：15M 上沿×1M 双峰）
# [MODULE] zephyr.signal_ashare.resonance_pair
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.signal_ashare.swing_sequence（摆动点/双峰语义复用，MOD-SIG-147）；标准库
# [CONSUMERS] （候选：共振矩阵统计面——G-C 族后续格子统计；本模块自身不点火不触发）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 铁律=READY_NOT_FIRED 不点火：判定器只输出组合态（ResonanceState），永不产生交易信号/触发指令/下单建议，fired 字段恒 False 且 frozen；组合判定三前置齐备才 RESONANT（15M 上沿在册+1M 双峰在册+双峰均入上沿容差带），任一缺席=显式降级态（NO_UPPER_EDGE/NO_DOUBLE_PEAK/NOT_RESONANT），不静默通过；容差带=上沿价位 ±tolerance_pct（相对价位）；输入校验 fail-closed（价位非正/非有限即 ValueError）；frozen dataclass asdict JSON 可序列化
# [MODIFY-GUARD] master_tc_night/lanes/L6_factory/00_workbook.md C235 节
# [STABILITY] testing
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError（UpperEdge.level<=0 / 双峰价位非有限非正 / tolerance_pct 出界，fail-closed）
# [TESTS] tests/signal_ashare/test_resonance_pair.py
# [A_module] module_id=MOD-SIG-148 | layer=module | stability=testing | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

r"""共振条件对定义器——15M 上沿 × 1M 双峰组合判定（MOD-SIG-148，波10 G-C.3）。

**选型口径（dossier_github_ecosystem.md 采纳汇总，C252 落册）**：

    1. trendln 思想自实现声明：趋势线/上沿检测不引 trendln（GregoryMorse）/
       pytrendline 第三方依赖——其"极值点连线+多触点确认"思想，以复用
       chanlun 分型（MOD-SIG-072）+swing_sequence 双峰序列（MOD-SIG-147）
       +水平上沿多触点计数自实现。零第三方依赖与 chanlun 纯函数核同款纪律；
       dossier §六明确 Hough 族需 scikit-image 重依赖，本域不引入。
    2. merge_asof 已落（跨周期对齐不在本模块重做）：15M 结构贴 1M 行的
       跨周期对齐选型=pd.merge_asof(direction="backward") 无前视口径
       （dossier freqtrade @informative 行证据），承载归 G-C.1 跨周期数据层
       （C233，L7 车道）。本判定器只消费**已对齐的结构面输入**
       （UpperEdge/DoublePeak 均带 anchor_idx），内嵌第二套对齐=禁。
    3. 不引 pandas-ta：dossier §八结论——pandas-ta 维护者公开声明 2026-07-01
       资助不足将归档（0.4.71b0 后无继），新接线不作核心依赖；本域指标面
       走 TechnicalIndicatorRegistry 自有口径。

**组合语义（条件对，非信号）**：

    RESONANT 当且仅当：
      ① 15M 上沿在册（level>0，touch_count≥min_touches 默认 2）
      ② 1M 双峰在册（同向双摆动点）
      ③ 双峰价位均落入上沿容差带 [level*(1-tol), level*(1+tol)]
    RESONANT ≠ 点火：本判定器对任何输入都不产生触发。下游（矩阵统计/
    回测条件轴/执行链）消费 ResonanceVerdict 自行决定动作；READY_NOT_FIRED
    是"组合态成立且留观"的显式状态名，提醒消费侧：定义器不点火是铁律。

不做什么：不读库/不对齐跨周期/不触发交易/不做形态命名——输出是共振
组合态描摹，非交易信号。

依据: 波10 G-C.3；dossier_github_ecosystem.md §六/§八；dossier_institution_
practice.md §二（接线优先于建库——本判定器即"接线件"非新库）。
SSoT: depgraph node MOD-SIG-148（随本批 apply_depgraph 登记）
Version: 0.1.0

# [ALGO_FLOW]
# 输入: UpperEdge(15M) + DoublePeak 语义输入(1M) + PairResonanceConfig
# 特征: 上沿容差带 / 双峰入带判定
# 算法: 三前置齐备判定（缺任一=显式降级态）→ RESONANT；fired 恒 False
# 输出: ResonanceVerdict（state/reasons/结构快照，JSON 可序列化）
"""

from __future__ import annotations

import logging
import math
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Final

logger = logging.getLogger(__name__)

__all__: Final = [
    "ResonanceState",
    "PairResonanceConfig",
    "UpperEdge",
    "PeakRef",
    "ResonanceVerdict",
    "judge_resonance_pair",
]


class ResonanceState(str, Enum):
    """共振组合态（判定器输出，非交易信号；READY_NOT_FIRED 不点火）。"""

    NO_UPPER_EDGE = "no_upper_edge"  # 15M 上沿缺席
    NO_DOUBLE_PEAK = "no_double_peak"  # 1M 双峰缺席
    NOT_RESONANT = "not_resonant"  # 两要素在册但双峰未齐入容差带
    READY_NOT_FIRED = "ready_not_fired"  # 组合态成立=RESONANT；显式不点火状态名


@dataclass(frozen=True, slots=True)
class PairResonanceConfig:
    """共振判定配置。

    Attributes:
        tolerance_pct: 上沿容差带半宽（% 价位，默认 0.5%）。
        min_touches: 上沿最少触点数（默认 2=多触点确认，trendln 思想自实现口径）。
        peaks_must_be_eq: 是否要求双峰为容差内并列（EQ 语义，默认 False——
            双峰各自入带即可；True 时收敛为严格双顶口径）。
    """

    tolerance_pct: float = 0.5
    min_touches: int = 2
    peaks_must_be_eq: bool = False

    def __post_init__(self) -> None:
        if not (0.0 < float(self.tolerance_pct) <= 10.0):
            raise ValueError(f"tolerance_pct 非法（0~10]）: {self.tolerance_pct!r}")
        if int(self.min_touches) < 1:
            raise ValueError(f"min_touches 非法（须 ≥1）: {self.min_touches!r}")


@dataclass(frozen=True, slots=True)
class UpperEdge:
    """15M 上沿（水平阻力上沿，多触点确认）。

    Attributes:
        level: 上沿价位（>0）。
        touch_count: 触点数（≥min_touches 才算"在册"）。
        last_touch_idx: 最近触点原始 K 下标（对齐锚，供跨周期核验）。
    """

    level: float
    touch_count: int
    last_touch_idx: int

    def __post_init__(self) -> None:
        if not math.isfinite(float(self.level)) or float(self.level) <= 0:
            raise ValueError(f"UpperEdge.level 非法（须为正有限）: {self.level!r}")
        if int(self.touch_count) < 0:
            raise ValueError(f"touch_count 非法: {self.touch_count!r}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class PeakRef:
    """1M 双峰之一（语义对齐 swing_sequence.SwingPoint 的最小投影）。"""

    price: float
    anchor_idx: int

    def __post_init__(self) -> None:
        if not math.isfinite(float(self.price)) or float(self.price) <= 0:
            raise ValueError(f"PeakRef.price 非法（须为正有限）: {self.price!r}")

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class ResonanceVerdict:
    """共振判定产出（JSON 可序列化；fired 恒 False=不点火铁律载体）。"""

    state: str  # ResonanceState.value
    fired: bool  # 恒 False——定义器永不点火（READY_NOT_FIRED 不点火）
    reasons: tuple[str, ...]
    upper_edge: UpperEdge | None
    peaks: tuple[PeakRef, ...]
    config: PairResonanceConfig

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _in_band(price: float, level: float, tol_pct: float) -> bool:
    band = level * tol_pct / 100.0
    return abs(price - level) <= band


def judge_resonance_pair(
    upper_edge: UpperEdge | None,
    peaks: tuple[PeakRef, PeakRef] | None,
    config: PairResonanceConfig | None = None,
) -> ResonanceVerdict:
    """15M 上沿 × 1M 双峰组合判定（纯函数；只判态，永不点火）。

    Args:
        upper_edge: 15M 上沿（None=缺席 → NO_UPPER_EDGE）。
        peaks: 1M 双峰二元组（None/长度≠2 → NO_DOUBLE_PEAK）。
        config: PairResonanceConfig。

    Returns:
        ResonanceVerdict：state ∈ {NO_UPPER_EDGE, NO_DOUBLE_PEAK, NOT_RESONANT,
        READY_NOT_FIRED}；fired 恒 False。

    Raises:
        ValueError: 输入元素校验失败（fail-closed，dataclass __post_init__ 透传）。
    """
    cfg = config or PairResonanceConfig()
    if upper_edge is None:
        return ResonanceVerdict(
            state=ResonanceState.NO_UPPER_EDGE.value,
            fired=False,
            reasons=("15M 上沿缺席",),
            upper_edge=None,
            peaks=tuple(peaks) if peaks else (),
            config=cfg,
        )
    if peaks is None or len(peaks) != 2:
        return ResonanceVerdict(
            state=ResonanceState.NO_DOUBLE_PEAK.value,
            fired=False,
            reasons=("1M 双峰缺席（须恰两点）",),
            upper_edge=upper_edge,
            peaks=tuple(peaks) if peaks else (),
            config=cfg,
        )
    reasons: list[str] = []
    if upper_edge.touch_count < cfg.min_touches:
        reasons.append(f"上沿触点不足（{upper_edge.touch_count}<{cfg.min_touches}，多触点确认不成立）")
    in_band = [p for p in peaks if _in_band(p.price, upper_edge.level, cfg.tolerance_pct)]
    if len(in_band) < 2:
        reasons.append(f"双峰入带不足（{len(in_band)}/2，带=[{upper_edge.level}±{cfg.tolerance_pct}%]）")
    if cfg.peaks_must_be_eq:
        p1, p2 = peaks
        eq_band = min(p1.price, p2.price) * cfg.tolerance_pct / 100.0
        if abs(p1.price - p2.price) > eq_band:
            reasons.append("严格双顶口径：双峰价差超并列容差")
    if reasons:
        return ResonanceVerdict(
            state=ResonanceState.NOT_RESONANT.value,
            fired=False,
            reasons=tuple(reasons),
            upper_edge=upper_edge,
            peaks=(peaks[0], peaks[1]),
            config=cfg,
        )
    logger.info(
        "judge_resonance_pair: RESONANT（level=%s, peaks=%s/%s）——READY_NOT_FIRED，定义器不点火",
        upper_edge.level,
        peaks[0].price,
        peaks[1].price,
    )
    return ResonanceVerdict(
        state=ResonanceState.READY_NOT_FIRED.value,
        fired=False,  # 铁律：判定器永不点火
        reasons=("三前置齐备：上沿在册+双峰在册+双峰齐入容差带",),
        upper_edge=upper_edge,
        peaks=(peaks[0], peaks[1]),
        config=cfg,
    )

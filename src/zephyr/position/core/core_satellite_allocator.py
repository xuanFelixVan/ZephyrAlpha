# [BLUEPRINT] MOD-POS-025 | docs/03_modules/_domain_position/core_satellite_allocator/blueprint.md
# [MODULE] zephyr.position.core.core_satellite_allocator
# [DOMAIN] D_POSITION
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] MOD-POS-001(精裁) ; MOD-POS-024(裁决) ; MOD-SELL-018(做T执行)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 卫星仓总权重≤satellite_cap(默认0.30,硬帽超出等比截断并留痕truncated); 核心仓权重=kelly×0.5(半Kelly纪律)≤single_name_cap; 核心仓止损k∈[3,4]默认3.5/卫星∈[1.5,2]默认1.75; 做T信号仅卫星仓(price>vwap+band→SELL_PART/price<vwap-band→BUY_BACK); 核心仓不换仓不T; RS换仓触发=卫星跌出rs_keep_pct且池外有更优challenger; Fail-Closed(输入非法→CoreSatelliteError)
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CoreSatelliteError(ZA-POS-0027)
# [TESTS] tests/position/test_core_satellite_allocator.py
# [A_module] module_id=MOD-POS-025 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 候选标的 CandidateAsset
#   fields: symbol/kelly_fraction/rs_pct/price/vwap/atr
# - id: I2
#   name: 核心-卫星配置 CoreSatelliteConfig
#   fields: satellite_cap/single_name_cap/core_atr_k/satellite_atr_k/t_band_atr/rs_keep_pct
# 层: 算法
# - id: A1
#   name_zh: ① 核心-卫星分组
#   name_en: allocate
#   intro: 按kelly降序,核心仓先配至core_budget,卫星≤satellite_cap硬帽,超出截断
# - id: A2
#   name_zh: ② 权重与止损参数分轨
#   name_en: weight_and_stop
#   intro: 单标的=half-kelly(kelly_fraction×0.5)≤single_name_cap;核心k=core_atr_k/卫星k=satellite_atr_k
# - id: A3
#   name_zh: ③ 卫星做T信号
#   name_en: satellite_t_signals
#   intro: price>vwap+t_band_atr×atr→SELL_PART; price<vwap−t_band_atr×atr→BUY_BACK; 仅卫星仓
# - id: A4
#   name_zh: ④ RS排名换仓触发
#   name_en: rs_swap_check
#   intro: 卫星rs_pct跌出rs_keep_pct且池外challenger rs_pct更高→SwapTrigger(out=掉队,in=challenger)
# 层: 输出
# - id: O1
#   name_zh: 核心-卫星方案 CoreSatellitePlan
#   name_en: CoreSatellitePlan
#   intro: legs/satellite_weight/t_signals/swap_triggers/notes完整结构方案
#   downstream: MOD-POS-001 精裁; MOD-POS-024 裁决; MOD-SELL-018 做T执行 ([CONSUMERS] 头)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I1 --> A2
# I1 --> A3
# I1 --> A4
# I2 --> A1
# I2 --> A2
# I2 --> A3
# I2 --> A4
# A1 --> O1
# A2 --> O1
# A3 --> O1
# A4 --> O1

"""Core-Satellite Allocator — 核心-卫星仓位管理模型 (MOD-POS-025)。

CFA Institute 推荐组合结构：核心仓 Kelly 长期持有（不做T不换仓），卫星仓≤总仓位
30% 用于做T/换仓增强。

TSV 裁定 (B10-01465, CAND-POS-005, A1交易决策架构 §8模块24)：
"核心Kelly+卫星≤30%+卫星做T/换仓结构为仓位管理缺口(做T限已有底仓变相T+0不越硬边界)"。

查重分工 (W-P1-20 铁律③探查——结构分配层缺口，非真源重叠)：
  - position_sizing_engine (MOD-POS-001): 标的层 Kelly+13 约束精裁——本件产
    结构分配方案(核心/卫星分组+目标权重带)，精裁委托 sizing；
  - position_adjudication_center (MOD-POS-024): 四层裁决唯一入口——本件方案
    运行时交裁决中心统一裁决，不旁路；
  - t_trade_coordinator (MOD-SELL-018): 单标的做T 计划器(两腿/成本/viable)——
    本件只出"哪些卫星标的、何时触发"做T信号，执行计划委托 MOD-SELL-018。

不做什么：不重造 Kelly 精裁、不做做T 两腿计划、不直接下单、不做预算分配。

依据: construction_backlog_dig.tsv B10-01465 + CAND-POS-005
SSoT: docs/03_modules/_domain_position/core_satellite_allocator/blueprint.md
Version: 0.1.0
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Final

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final[list[str]] = [
    "Sleeve",
    "CandidateAsset",
    "CoreSatelliteConfig",
    "AllocationLeg",
    "TTradeSignal",
    "SwapTrigger",
    "CoreSatellitePlan",
    "CoreSatelliteAllocator",
    "CoreSatelliteError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class CoreSatelliteError(ZephyrBaseError):
    """核心-卫星仓位管理输入非法或约束越界。"""

    error_code = "ZA-POS-0027"  # 待登记, 建议 ZA-POS-0025


# ──────────────────────────────────────────────────────────────────────────────
# 枚举与配置
# ──────────────────────────────────────────────────────────────────────────────


class Sleeve(str, Enum):
    """仓位袖珍分组。"""

    CORE = "CORE"  # 核心仓 (长期持有, 不做T不换仓)
    SATELLITE = "SATELLITE"  # 卫星仓 (做T/换仓增强, ≤satellite_cap)


@dataclass(frozen=True)
class CoreSatelliteConfig:
    """核心-卫星配置 (C 类可调参数)。

    Attributes:
        satellite_cap: 卫星仓总权重硬帽 (默认 0.30, CFA 推荐 ≤30%)
        single_name_cap: 单标的权重上限 (默认 0.20)
        core_atr_k: 核心仓 ATR 止损 k (默认 3.5, 区间 3-4)
        satellite_atr_k: 卫星仓 ATR 止损 k (默认 1.75, 区间 1.5-2)
        t_band_atr: 做T ATR 带宽 (默认 1.0, 价格偏离 VWAP±1×ATR 触发)
        rs_keep_pct: 卫星 RS 排名保持阈值 (默认 0.30, 跌出前30%触发换仓)
    """

    satellite_cap: float = 0.30
    single_name_cap: float = 0.20
    core_atr_k: float = 3.5
    satellite_atr_k: float = 1.75
    t_band_atr: float = 1.0
    rs_keep_pct: float = 0.30

    def __post_init__(self) -> None:
        for name, val, lo, hi in (
            ("satellite_cap", self.satellite_cap, 0.0, 1.0),
            ("single_name_cap", self.single_name_cap, 0.0, 1.0),
            ("core_atr_k", self.core_atr_k, 0.0, 10.0),
            ("satellite_atr_k", self.satellite_atr_k, 0.0, 10.0),
            ("t_band_atr", self.t_band_atr, 0.0, 10.0),
            ("rs_keep_pct", self.rs_keep_pct, 0.0, 1.0),
        ):
            if not lo <= val <= hi:
                raise CoreSatelliteError(f"{name} must be in [{lo},{hi}], got {val}")


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class CandidateAsset:
    """候选标的。"""

    symbol: str
    kelly_fraction: float  # Kelly 仓位分数 (0~1)
    rs_pct: float  # RS 相对强度分位 (0~1, 越高越强)
    price: float  # 当前价
    vwap: float  # 当日 VWAP
    atr: float  # ATR (平均真实波幅)

    def __post_init__(self) -> None:
        if not self.symbol or not self.symbol.strip():
            raise CoreSatelliteError("symbol must be non-empty")
        if not 0 <= self.kelly_fraction <= 1:
            raise CoreSatelliteError(f"kelly_fraction must be in [0,1], got {self.kelly_fraction}")
        if not 0 <= self.rs_pct <= 1:
            raise CoreSatelliteError(f"rs_pct must be in [0,1], got {self.rs_pct}")
        if self.price <= 0:
            raise CoreSatelliteError(f"price must be > 0, got {self.price}")
        if self.vwap <= 0:
            raise CoreSatelliteError(f"vwap must be > 0, got {self.vwap}")
        if self.atr <= 0:
            raise CoreSatelliteError(f"atr must be > 0, got {self.atr}")


@dataclass(frozen=True)
class AllocationLeg:
    """单条仓位分配腿。"""

    symbol: str
    sleeve: Sleeve
    target_weight: float  # 目标权重 (0~1)
    stop_atr_k: float  # ATR 止损倍数
    truncated: bool = False  # 是否被 cap 截断


@dataclass(frozen=True)
class TTradeSignal:
    """做T 信号 (仅卫星仓)。"""

    symbol: str
    action: str  # SELL_PART / BUY_BACK
    deviation_atr: float  # 偏离 VWAP 的 ATR 倍数 (带符号)
    reason: str


@dataclass(frozen=True)
class SwapTrigger:
    """RS 排名换仓触发。"""

    out_symbol: str  # 掉队卫星
    in_symbol: str  # 挑战者
    reason: str


@dataclass(frozen=True)
class CoreSatellitePlan:
    """核心-卫星仓位管理方案。"""

    legs: tuple[AllocationLeg, ...]
    satellite_weight: float  # 卫星仓总权重 (≤cap)
    t_signals: tuple[TTradeSignal, ...]
    swap_triggers: tuple[SwapTrigger, ...]
    notes: tuple[str, ...] = field(default_factory=tuple)


# ──────────────────────────────────────────────────────────────────────────────
# 核心-卫星分配器
# ──────────────────────────────────────────────────────────────────────────────


class CoreSatelliteAllocator:
    """核心-卫星仓位管理——结构分配+做T信号+换仓触发。

    用法:
        allocator = CoreSatelliteAllocator()
        candidates = [CandidateAsset("000001.SZ", 0.6, 0.9, 10.0, 10.1, 0.2), ...]
        plan = allocator.allocate(candidates)
        # plan.legs 核心/卫星分组+权重; plan.t_signals 做T信号; plan.swap_triggers 换仓
        # 运行时交 MOD-POS-001 精裁 / MOD-POS-024 裁决 / MOD-SELL-018 做T执行
    """

    def allocate(
        self,
        candidates: list[CandidateAsset],
        config: CoreSatelliteConfig | None = None,
    ) -> CoreSatellitePlan:
        """核心-卫星分组与权重分配。

        Args:
            candidates: 候选标的列表
            config: 配置 (默认 CoreSatelliteConfig())

        Returns:
            CoreSatellitePlan
        """
        cfg = config or CoreSatelliteConfig()
        if not candidates:
            return CoreSatellitePlan(legs=(), satellite_weight=0.0, t_signals=(), swap_triggers=(), notes=("empty_candidates",))

        # 按 kelly_fraction 降序排序
        sorted_cands = sorted(candidates, key=lambda c: (-c.kelly_fraction, -c.rs_pct, c.symbol))
        core_budget = 1.0 - cfg.satellite_cap

        legs: list[AllocationLeg] = []
        core_acc = 0.0
        satellite_acc = 0.0
        notes: list[str] = []

        for cand in sorted_cands:
            # half-Kelly 权重, 单标的不超过 single_name_cap
            weight = min(cand.kelly_fraction * 0.5, cfg.single_name_cap)
            if weight <= 0:
                continue

            if core_acc + weight <= core_budget:
                # 核心仓
                legs.append(AllocationLeg(
                    symbol=cand.symbol,
                    sleeve=Sleeve.CORE,
                    target_weight=weight,
                    stop_atr_k=cfg.core_atr_k,
                    truncated=False,
                ))
                core_acc += weight
            elif satellite_acc + weight <= cfg.satellite_cap:
                # 卫星仓
                legs.append(AllocationLeg(
                    symbol=cand.symbol,
                    sleeve=Sleeve.SATELLITE,
                    target_weight=weight,
                    stop_atr_k=cfg.satellite_atr_k,
                    truncated=False,
                ))
                satellite_acc += weight
            elif satellite_acc < cfg.satellite_cap:
                # 卫星硬帽截断
                remaining = cfg.satellite_cap - satellite_acc
                if remaining > 0:
                    legs.append(AllocationLeg(
                        symbol=cand.symbol,
                        sleeve=Sleeve.SATELLITE,
                        target_weight=remaining,
                        stop_atr_k=cfg.satellite_atr_k,
                        truncated=True,
                    ))
                    satellite_acc += remaining
                    notes.append(f"satellite_cap_truncated:{cand.symbol}")
            else:
                # 卫星已满, 跳过
                notes.append(f"skipped_cap_full:{cand.symbol}")

        # 做T信号与换仓触发 (基于已分组 legs)
        t_signals = self.satellite_t_signals(legs, candidates, cfg)
        swap_triggers = self.rs_swap_check(legs, candidates, cfg)

        return CoreSatellitePlan(
            legs=tuple(legs),
            satellite_weight=satellite_acc,
            t_signals=t_signals,
            swap_triggers=swap_triggers,
            notes=tuple(notes),
        )

    def satellite_t_signals(
        self,
        legs: list[AllocationLeg],
        candidates: list[CandidateAsset],
        config: CoreSatelliteConfig | None = None,
    ) -> tuple[TTradeSignal, ...]:
        """卫星仓做T信号 (价格偏离 VWAP±band×ATR)。

        仅卫星仓触发; 核心仓长期持有不做T。
        """
        cfg = config or CoreSatelliteConfig()
        cand_map = {c.symbol: c for c in candidates}
        signals: list[TTradeSignal] = []

        for leg in legs:
            if leg.sleeve is not Sleeve.SATELLITE:
                continue
            cand = cand_map.get(leg.symbol)
            if cand is None:
                continue
            deviation = (cand.price - cand.vwap) / cand.atr
            if deviation > cfg.t_band_atr:
                signals.append(TTradeSignal(
                    symbol=leg.symbol,
                    action="SELL_PART",
                    deviation_atr=deviation,
                    reason=f"price>{cfg.t_band_atr}ATR above VWAP ({deviation:.2f})",
                ))
            elif deviation < -cfg.t_band_atr:
                signals.append(TTradeSignal(
                    symbol=leg.symbol,
                    action="BUY_BACK",
                    deviation_atr=deviation,
                    reason=f"price<{cfg.t_band_atr}ATR below VWAP ({deviation:.2f})",
                ))
        return tuple(signals)

    def rs_swap_check(
        self,
        legs: list[AllocationLeg],
        candidates: list[CandidateAsset],
        config: CoreSatelliteConfig | None = None,
    ) -> tuple[SwapTrigger, ...]:
        """RS 排名换仓触发: 卫星跌出 rs_keep_pct 且池外有更优挑战者。

        核心仓不换仓; 仅卫星仓。
        """
        cfg = config or CoreSatelliteConfig()
        cand_map = {c.symbol: c for c in candidates}
        in_plan_symbols = {leg.symbol for leg in legs}
        # 池外挑战者 (未入 plan 且 rs_pct 较高)
        challengers = sorted(
            [c for c in candidates if c.symbol not in in_plan_symbols],
            key=lambda c: (-c.rs_pct, c.symbol),
        )
        triggers: list[SwapTrigger] = []

        for leg in legs:
            if leg.sleeve is not Sleeve.SATELLITE:
                continue
            cand = cand_map.get(leg.symbol)
            if cand is None:
                continue
            if cand.rs_pct < cfg.rs_keep_pct and challengers:
                best = challengers[0]
                if best.rs_pct > cand.rs_pct:
                    triggers.append(SwapTrigger(
                        out_symbol=leg.symbol,
                        in_symbol=best.symbol,
                        reason=f"satellite rs_pct={cand.rs_pct:.2f} < keep={cfg.rs_keep_pct:.2f}, challenger rs_pct={best.rs_pct:.2f}",
                    ))
        return tuple(triggers)
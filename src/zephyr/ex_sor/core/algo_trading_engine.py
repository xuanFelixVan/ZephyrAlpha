# [BLUEPRINT] MOD-XS-005 | docs/03_modules/_domain-ex_sor/algo_trading_engine/blueprint.md
# [MODULE] zephyr.ex_sor.core.algo_trading_engine
# [DOMAIN] D_EX_SOR
# [DEPENDENCIES] zephyr.shared.contracts.order; zephyr.shared.contracts.enums.order_enums; zephyr.shared.foundation.errors
# [CONSUMERS] MOD-XS-004(Execution Scheduler,消费 AlgoExecutionPlan); MOD-XS-011(Algo Selector,消费 AlgoType 注册表); MOD-XS-002(Broker Adapter,提交子订单)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 切片数量和=订单总量(Decimal守恒); 参与率≤5%(§10.1监管硬约束); 单笔≤15%ADV(§13.1 AC模型上限); 算法决策可审计; miniQMT不支持券商端算法→本模块为系统自实现拆单(§2.2 XS-05兼容性)
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] AlgoError; UnknownAlgoError; InvalidAlgoParamsError; OrderTooLargeError
# [TESTS] tests/ex_sor/test_algo_trading_engine.py
# [A_module] module_id=MOD-XS-005 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
Algo Trading Engine — 算法交易引擎 (MOD-XS-005)

D-EX-SOR §2.2 XS-05: 算法注册表 + TWAP/VWAP/ICEBERG/POV/IS/ALT 引擎 + 参数优化器。

职责:
    - 维护算法注册表 (6 种 A 股适用算法)
    - 给定 Order + AlgoParams + MarketContext → 生成 AlgoExecutionPlan (切片方案)
    - 切片方案交由 XS-04 Execution Scheduler 做时间调度, 再由 XS-01/XS-02 提交

算法清单 (§2.2 XS-05):
    TWAP     — 时间加权平均价: 等量切片, 价格被动
    VWAP     — 成交量加权平均价: 按 §13.2 日内成交量分布切片
    ICEBERG  — 冰山: 小额显示量切片, 隐藏大单
    POV      — 参与率 (Percent of Volume): 切片=预期窗口成交量×参与率
    IS       — Implementation Shortfall: Almgren-Chriss 风险厌恶轨迹 (urgency 驱动前/后置)
    ALT      — Aggressive Liquidity Taking: 少量大单激进吃单 (附录B: Sniper→ALT)

关键约束 (D-EX-SOR):
    §10.1  参与率 ≤5% (证监会程序化交易规定, Hard Block)
    §13.1  单笔订单 ≤15% ADV (Almgren-Chriss 模型上限, 超则否决+拆分)
    §13.2  日内时变成交分布: 开盘20%/上午25%/午盘10%/尾盘45%
    §2.2   miniQMT 个人账户不支持券商端 VWAP/TWAP, 本模块为系统自实现拆单逻辑

边界 (与 XS-04 的分工):
    XS-05 = 算法逻辑 (切多少量、什么价格策略) → AlgoExecutionPlan
    XS-04 = 时间调度 (何时发每片、优先级队列、自适应节奏)

SSoT: depgraph MOD-XS-005
Version: 0.1.0
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import ROUND_DOWN, Decimal
from enum import Enum
from typing import Final, Protocol

from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderType
from zephyr.shared.contracts.order import Order
from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    # 枚举
    "AlgoType",
    "PriceStrategy",
    # 数据模型
    "MarketContext",
    "AlgoParams",
    "AlgoSlice",
    "AlgoExecutionPlan",
    # 策略
    "AlgoStrategy",
    "TwapStrategy",
    "VwapStrategy",
    "IcebergStrategy",
    "PovStrategy",
    "ImplementationShortfallStrategy",
    "AggressiveLiquidityTakingStrategy",
    # 引擎
    "AlgoTradingEngine",
    "AlgoParamOptimizer",
    # 错误
    "AlgoError",
    "UnknownAlgoError",
    "InvalidAlgoParamsError",
    "OrderTooLargeError",
]

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class AlgoError(ZephyrBaseError):
    """算法引擎错误——切片生成失败、参数非法。"""

    error_code = "ZA-XS-0005"


class UnknownAlgoError(AlgoError):
    """未知算法——注册表中无此 AlgoType。"""

    error_code = "ZA-XS-0005-NA"


class InvalidAlgoParamsError(AlgoError):
    """算法参数非法——参与率越界、切片数为零、显示量为零等。"""

    error_code = "ZA-XS-0005-IP"


class OrderTooLargeError(AlgoError):
    """订单过大——超过 15% ADV (§13.1 Almgren-Chriss 上限), 应上游拆分。"""

    error_code = "ZA-XS-0005-OL"


# ──────────────────────────────────────────────────────────────────────────────
# 枚举
# ──────────────────────────────────────────────────────────────────────────────


class AlgoType(Enum):
    """A 股适用算法清单 (§2.2 XS-05)。"""

    def __str__(self) -> str:
        return self.value

    TWAP = "TWAP"  # 时间加权平均价
    VWAP = "VWAP"  # 成交量加权平均价
    ICEBERG = "ICEBERG"  # 冰山 (隐藏大单)
    POV = "POV"  # 参与率 (Percent of Volume)
    IS = "IS"  # Implementation Shortfall 实施差额
    ALT = "ALT"  # Aggressive Liquidity Taking 激进流动性摄取


class PriceStrategy(Enum):
    """切片价格策略。"""

    def __str__(self) -> str:
        return self.value

    MARKET = "MARKET"  # 市价
    LIMIT = "LIMIT"  # 限价 (reference_price)
    MID = "MID"  # 中间价
    AGGRESSIVE = "AGGRESSIVE"  # 对手价 (吃单)
    PASSIVE = "PASSIVE"  # 本方价 (挂单)


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────────


# §13.2 日内成交量分布默认真源 (4 时段占比, 和≈1.0)
DEFAULT_VOLUME_PROFILE: Final[dict[int, float]] = {
    1: 0.20,  # 开盘 9:30-10:00
    2: 0.25,  # 上午 10:00-11:30
    3: 0.10,  # 午盘 13:00-14:00
    4: 0.45,  # 尾盘 14:00-15:00
}

# §10.1 监管参与率硬上限
MAX_PARTICIPATION_RATE: Final[Decimal] = Decimal("0.05")
# §13.1 Almgren-Chriss 单笔 ADV 占比上限
MAX_ADV_FRACTION: Final[Decimal] = Decimal("0.15")
# A 股最小交易单位 (1 手 = 100 股)
LOT_SIZE: Final[Decimal] = Decimal("100")


@dataclass(frozen=True)
class MarketContext:
    """市场上下文——算法计算所需的市场数据快照。

    Attributes:
        symbol: 标的代码
        last_price: 最新价
        adv: 日均成交量 (Average Daily Volume)
        volume_profile: 时段→成交量占比 (VWAP 用, 默认 §13.2)
        bid_price: 买一价 (AGGRESSIVE/PASSIVE 用)
        ask_price: 卖一价
    """

    symbol: str
    last_price: Decimal
    adv: Decimal
    volume_profile: dict[int, float] = field(default_factory=lambda: dict(DEFAULT_VOLUME_PROFILE))
    bid_price: Decimal | None = None
    ask_price: Decimal | None = None

    def __post_init__(self) -> None:
        if not self.symbol:
            raise AlgoError("symbol 不能为空", details={"field": "symbol"})
        if self.last_price <= 0:
            raise AlgoError(
                "last_price 必须为正",
                details={"field": "last_price", "value": str(self.last_price)},
            )
        if self.adv <= 0:
            raise AlgoError(
                "adv 必须为正",
                details={"field": "adv", "value": str(self.adv)},
            )
        total = sum(self.volume_profile.values())
        if abs(total - 1.0) > 1e-6:
            raise AlgoError(
                "volume_profile 占比和必须≈1.0",
                details={"sum": total, "profile": self.volume_profile},
            )


@dataclass(frozen=True)
class AlgoParams:
    """算法参数——驱动切片生成。

    Attributes:
        algo_type: 算法类型
        participation_rate: 参与率 0~0.05 (POV/VWAP, §10.1 硬上限 5%)
        time_horizon_minutes: 执行时间窗口 (分钟)
        max_slice_count: 最大切片数
        min_slice_quantity: 最小切片数量 (A 股默认 100 股/手)
        display_quantity: ICEBERG 单次显示量
        urgency: 紧急度 0~1 (IS/ALT, 0=被动 TWAP-like, 1=最激进)
        price_limit: 价格限制 (LIMIT 用)
    """

    algo_type: AlgoType
    participation_rate: Decimal = Decimal("0.05")
    time_horizon_minutes: int = 30
    max_slice_count: int = 10
    min_slice_quantity: Decimal = LOT_SIZE
    display_quantity: Decimal | None = None
    urgency: Decimal = Decimal("0.5")
    price_limit: Decimal | None = None

    def __post_init__(self) -> None:
        if self.participation_rate <= 0 or self.participation_rate > MAX_PARTICIPATION_RATE:
            raise InvalidAlgoParamsError(
                f"participation_rate 必须在 (0, {MAX_PARTICIPATION_RATE}] (§10.1)",
                details={
                    "field": "participation_rate",
                    "value": str(self.participation_rate),
                    "max": str(MAX_PARTICIPATION_RATE),
                },
            )
        if self.time_horizon_minutes <= 0:
            raise InvalidAlgoParamsError(
                "time_horizon_minutes 必须为正",
                details={"field": "time_horizon_minutes", "value": self.time_horizon_minutes},
            )
        if self.max_slice_count <= 0:
            raise InvalidAlgoParamsError(
                "max_slice_count 必须为正",
                details={"field": "max_slice_count", "value": self.max_slice_count},
            )
        if self.min_slice_quantity <= 0:
            raise InvalidAlgoParamsError(
                "min_slice_quantity 必须为正",
                details={"field": "min_slice_quantity", "value": str(self.min_slice_quantity)},
            )
        if self.urgency < 0 or self.urgency > 1:
            raise InvalidAlgoParamsError(
                "urgency 必须在 [0, 1]",
                details={"field": "urgency", "value": str(self.urgency)},
            )
        # ICEBERG 必须有 display_quantity
        if self.algo_type == AlgoType.ICEBERG:
            if self.display_quantity is None or self.display_quantity <= 0:
                raise InvalidAlgoParamsError(
                    "ICEBERG 必须指定正的 display_quantity",
                    details={"field": "display_quantity"},
                )


@dataclass(frozen=True)
class AlgoSlice:
    """算法切片——单笔子订单的数量 + 价格策略。

    Attributes:
        slice_index: 切片序号 (0-based)
        quantity: 本片数量 (Decimal, 守恒)
        price_strategy: 价格策略
        reference_price: 参考价 (LIMIT/MID/AGGRESSIVE/PASSIVE 用; MARKET 为 None)
        rationale: 切片理由 (审计)
    """

    slice_index: int
    quantity: Decimal
    price_strategy: PriceStrategy
    reference_price: Decimal | None
    rationale: str


@dataclass(frozen=True)
class AlgoExecutionPlan:
    """算法执行计划——一个订单的完整切片方案。

    Attributes:
        order_id: 订单 ID
        algo_type: 算法类型
        params: 使用的参数
        slices: 切片列表 (顺序即逻辑顺序, 时间调度由 XS-04 决定)
        total_quantity: 切片数量和 (MUST == order.quantity, 守恒不变量)
        created_at: 计划生成时间
        estimated_participation: 估算最大参与率 (供 §10.1 监控)
    """

    order_id: str
    algo_type: AlgoType
    params: AlgoParams
    slices: list[AlgoSlice]
    total_quantity: Decimal
    created_at: datetime
    estimated_participation: Decimal

    def __post_init__(self) -> None:
        if not self.slices:
            raise AlgoError(
                "执行计划切片不能为空",
                details={"order_id": self.order_id, "algo": self.algo_type.value},
            )
        sliced_sum = sum((s.quantity for s in self.slices), Decimal("0"))
        if sliced_sum != self.total_quantity:
            raise AlgoError(
                "切片数量和≠总量 (违反守恒不变量)",
                details={
                    "order_id": self.order_id,
                    "sliced_sum": str(sliced_sum),
                    "total": str(self.total_quantity),
                },
            )

    def to_dict(self) -> dict[str, object]:
        return {
            "order_id": self.order_id,
            "algo_type": self.algo_type.value,
            "total_quantity": str(self.total_quantity),
            "slice_count": len(self.slices),
            "estimated_participation": str(self.estimated_participation),
            "created_at": self.created_at.isoformat(),
            "slices": [
                {
                    "index": s.slice_index,
                    "quantity": str(s.quantity),
                    "price_strategy": s.price_strategy.value,
                    "reference_price": str(s.reference_price) if s.reference_price else None,
                    "rationale": s.rationale,
                }
                for s in self.slices
            ],
        }


# ──────────────────────────────────────────────────────────────────────────────
# 算法策略接口 (Strategy 模式)
# ──────────────────────────────────────────────────────────────────────────────


class AlgoStrategy(Protocol):
    """算法策略接口——每种算法实现切片生成逻辑。"""

    algo_type: AlgoType

    def generate_slices(
        self,
        order: Order,
        params: AlgoParams,
        ctx: MarketContext,
    ) -> list[AlgoSlice]:
        """生成切片列表 (不含时间调度, 仅数量+价格策略)。"""


# ──────────────────────────────────────────────────────────────────────────────
# 切片工具
# ──────────────────────────────────────────────────────────────────────────────


def _quantize_to_lot(qty: Decimal, lot: Decimal) -> Decimal:
    """向下取整到 lot 粒度 (A 股 100 股/手)。"""
    if lot <= 0:
        return qty
    return (qty / lot).to_integral_value(rounding=ROUND_DOWN) * lot


def _distribute_evenly(total: Decimal, n: int, lot: Decimal) -> list[Decimal]:
    """将 total 等分为 n 份 (lot 对齐, 余数补到最后一片)。

    守恒保证: Σ(slices) == total (lot 对齐后用余数补偿)。
    """
    if n <= 0:
        return []
    base = _quantize_to_lot(total / Decimal(n), lot)
    if base <= 0:
        # 单片不足 1 lot → 全量放第一片
        return [total] + [Decimal("0")] * (n - 1)
    slices = [base] * n
    remainder = total - sum(slices, Decimal("0"))
    # 余数补到最后一片 (保持 lot 对齐: 余数本身已是对齐后的差)
    slices[-1] = slices[-1] + remainder
    return slices


def _distribute_by_weights(total: Decimal, weights: list[float], lot: Decimal) -> list[Decimal]:
    """按权重分配 total (lot 对齐, 余数补到最大权重片, 守恒)。"""
    if not weights:
        return []
    w_sum = sum(weights)
    if w_sum <= 0:
        return _distribute_evenly(total, len(weights), lot)
    raw = [total * Decimal(str(w)) / Decimal(str(w_sum)) for w in weights]
    slices = [_quantize_to_lot(q, lot) for q in raw]
    deficit = total - sum(slices, Decimal("0"))
    if deficit != 0:
        # 补偿到最大权重片
        max_idx = max(range(len(weights)), key=lambda i: weights[i])
        slices[max_idx] = slices[max_idx] + deficit
    return slices


# ──────────────────────────────────────────────────────────────────────────────
# TWAP — 时间加权平均价
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class TwapStrategy:
    """TWAP: 等量切片 + 被动价格 (中间价/本方价)。

    λ=0 的 Almgren-Chriss 特例 (§13.1): 无风险厌恶 → 时间均匀。
    """

    algo_type: AlgoType = AlgoType.TWAP

    def generate_slices(
        self,
        order: Order,
        params: AlgoParams,
        ctx: MarketContext,
    ) -> list[AlgoSlice]:
        n = min(params.max_slice_count, max(1, params.time_horizon_minutes))
        quantities = _distribute_evenly(order.quantity, n, params.min_slice_quantity)
        ref = _mid_price(ctx)
        return [
            AlgoSlice(
                slice_index=i,
                quantity=q,
                price_strategy=PriceStrategy.PASSIVE,
                reference_price=ref,
                rationale=f"TWAP 等量切片 {i + 1}/{n} (λ=0 均匀)",
            )
            for i, q in enumerate(quantities)
            if q > 0
        ]


# ──────────────────────────────────────────────────────────────────────────────
# VWAP — 成交量加权平均价
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class VwapStrategy:
    """VWAP: 按 §13.2 日内成交量分布切片。

    切片数量 = volume_profile 时段数 (默认 4), 每片量 = total × 时段占比。
    """

    algo_type: AlgoType = AlgoType.VWAP

    def generate_slices(
        self,
        order: Order,
        params: AlgoParams,
        ctx: MarketContext,
    ) -> list[AlgoSlice]:
        profile = ctx.volume_profile
        # 切片数 = min(时段数, max_slice_count)
        n = min(len(profile), params.max_slice_count)
        # 取占比最高的 n 个时段
        sorted_periods = sorted(profile.items(), key=lambda kv: kv[1], reverse=True)[:n]
        weights = [p[1] for p in sorted_periods]
        quantities = _distribute_by_weights(order.quantity, weights, params.min_slice_quantity)
        ref = _mid_price(ctx)
        return [
            AlgoSlice(
                slice_index=i,
                quantity=q,
                price_strategy=PriceStrategy.PASSIVE,
                reference_price=ref,
                rationale=f"VWAP 时段{period} 占比{share:.0%} 切片",
            )
            for i, ((period, share), q) in enumerate(zip(sorted_periods, quantities, strict=True))
            if q > 0
        ]


# ──────────────────────────────────────────────────────────────────────────────
# ICEBERG — 冰山
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class IcebergStrategy:
    """ICEBERG: 小额显示量切片, 隐藏大单意图。

    每片 = display_quantity (末片为余量), 价格被动挂单。
    """

    algo_type: AlgoType = AlgoType.ICEBERG

    def generate_slices(
        self,
        order: Order,
        params: AlgoParams,
        ctx: MarketContext,
    ) -> list[AlgoSlice]:
        display = params.display_quantity
        if display is None or display <= 0:
            raise InvalidAlgoParamsError(
                "ICEBERG 需要 display_quantity",
                details={"algo": "ICEBERG"},
            )
        total = order.quantity
        ref = _mid_price(ctx)
        slices: list[AlgoSlice] = []
        remaining = total
        idx = 0
        # 切片数不超过 max_slice_count
        while remaining > 0 and idx < params.max_slice_count:
            if remaining <= display:
                # 末片余量: 直接用 remaining (不 floor, 保持守恒, 避免亚 lot 碎片)
                q = remaining
            else:
                q = _quantize_to_lot(display, params.min_slice_quantity)
                if q <= 0:
                    q = display  # display 不足 1 lot → 用 display 原值
            slices.append(
                AlgoSlice(
                    slice_index=idx,
                    quantity=q,
                    price_strategy=PriceStrategy.PASSIVE,
                    reference_price=ref,
                    rationale=f"ICEBERG 显示量切片 {idx + 1} (隐藏 {total - display} 股)",
                )
            )
            remaining -= q
            idx += 1
        # 若 max_slice_count 用尽仍有余量 → 补到末片 (守恒)
        if remaining > 0 and slices:
            slices[-1] = AlgoSlice(
                slice_index=slices[-1].slice_index,
                quantity=slices[-1].quantity + remaining,
                price_strategy=PriceStrategy.PASSIVE,
                reference_price=ref,
                rationale=slices[-1].rationale + f" (末片补余 {remaining} 股)",
            )
        return slices


# ──────────────────────────────────────────────────────────────────────────────
# POV — 参与率 (Percent of Volume)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class PovStrategy:
    """POV: 切片量 = 预期窗口成交量 × 参与率 (§10.1 ≤5%)。

    预期窗口成交量 = ADV × (time_horizon / 240 分钟交易日)。
    """

    algo_type: AlgoType = AlgoType.POV

    def generate_slices(
        self,
        order: Order,
        params: AlgoParams,
        ctx: MarketContext,
    ) -> list[AlgoSlice]:
        n = min(params.max_slice_count, max(1, params.time_horizon_minutes))
        # 每窗口预期成交量 (240 分钟 = A 股交易日)
        window_fraction = Decimal(str(params.time_horizon_minutes)) / Decimal("240") / Decimal(n)
        expected_window_vol = ctx.adv * window_fraction
        # 切片量 = 预期成交量 × 参与率, 但不超过剩余量
        participation = params.participation_rate
        ref = _mid_price(ctx)
        total = order.quantity
        slices: list[AlgoSlice] = []
        remaining = total
        for i in range(n):
            if remaining <= 0:
                break
            target = expected_window_vol * participation
            q = min(target, remaining)
            q = _quantize_to_lot(q, params.min_slice_quantity)
            if q <= 0:
                q = remaining
            slices.append(
                AlgoSlice(
                    slice_index=i,
                    quantity=q,
                    price_strategy=PriceStrategy.PASSIVE,
                    reference_price=ref,
                    rationale=f"POV 参与率 {participation}×窗口量 切片 {i + 1}/{n}",
                )
            )
            remaining -= q
        # 守恒: 余量补到末片
        if remaining > 0 and slices:
            last = slices[-1]
            slices[-1] = AlgoSlice(
                slice_index=last.slice_index,
                quantity=last.quantity + remaining,
                price_strategy=last.price_strategy,
                reference_price=last.reference_price,
                rationale=last.rationale + f" (末片补余 {remaining})",
            )
        elif remaining > 0 and not slices:
            slices.append(
                AlgoSlice(
                    slice_index=0,
                    quantity=remaining,
                    price_strategy=PriceStrategy.PASSIVE,
                    reference_price=ref,
                    rationale="POV 余量兜底片",
                )
            )
        return slices


# ──────────────────────────────────────────────────────────────────────────────
# IS — Implementation Shortfall (Almgren-Chriss 风险厌恶轨迹)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ImplementationShortfallStrategy:
    """IS: Almgren-Chriss 风险厌恶轨迹 (urgency 驱动)。

    urgency=0 → TWAP (均匀); urgency→1 → 前置加载 (降低等待风险)。
    切片权重 ∝ exp(-urgency × t_i), t_i = i/n。
    """

    algo_type: AlgoType = AlgoType.IS

    def generate_slices(
        self,
        order: Order,
        params: AlgoParams,
        ctx: MarketContext,
    ) -> list[AlgoSlice]:
        n = min(params.max_slice_count, max(1, params.time_horizon_minutes))
        lam = float(params.urgency)
        # 权重: w_i = exp(-λ × t_i), t_i = i/(n-1) (n>1 时)
        if n == 1:
            weights = [1.0]
        else:
            ts = [i / (n - 1) for i in range(n)]
            raw_w = [math.exp(-lam * t) for t in ts]
            w_sum = sum(raw_w)
            weights = [w / w_sum for w in raw_w]
        quantities = _distribute_by_weights(order.quantity, weights, params.min_slice_quantity)
        ref = _mid_price(ctx)
        front_loaded = lam > 0.5
        return [
            AlgoSlice(
                slice_index=i,
                quantity=q,
                price_strategy=PriceStrategy.MID,
                reference_price=ref,
                rationale=(f"IS AC 轨迹切片 {i + 1}/{n} (λ={lam:.2f} {'前置加载' if front_loaded else '均匀倾向'})"),
            )
            for i, q in enumerate(quantities)
            if q > 0
        ]


# ──────────────────────────────────────────────────────────────────────────────
# ALT — Aggressive Liquidity Taking (附录B: Sniper→ALT)
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class AggressiveLiquidityTakingStrategy:
    """ALT: 少量大单激进吃单 (附录B: 主观"狙击"→量化"激进流动性摄取")。

    切片数少 (2~3), 价格取对手价 (AGGRESSIVE), 快速成交。
    """

    algo_type: AlgoType = AlgoType.ALT

    def generate_slices(
        self,
        order: Order,
        params: AlgoParams,
        ctx: MarketContext,
    ) -> list[AlgoSlice]:
        # ALT 切片数: min(max_slice_count, 3), 至少 1
        n = max(1, min(params.max_slice_count, 3))
        quantities = _distribute_evenly(order.quantity, n, params.min_slice_quantity)
        # 价格: BUY 取卖价 (吃卖盘), SELL 取买价 (砸买盘)
        ref = _aggressive_price(ctx, order.side)
        return [
            AlgoSlice(
                slice_index=i,
                quantity=q,
                price_strategy=PriceStrategy.AGGRESSIVE,
                reference_price=ref,
                rationale=f"ALT 激进吃单切片 {i + 1}/{n} ({order.side.value})",
            )
            for i, q in enumerate(quantities)
            if q > 0
        ]


# ──────────────────────────────────────────────────────────────────────────────
# 价格工具
# ──────────────────────────────────────────────────────────────────────────────


def _mid_price(ctx: MarketContext) -> Decimal | None:
    """中间价 = (bid+ask)/2, 退化用 last_price。"""
    if ctx.bid_price is not None and ctx.ask_price is not None:
        return (ctx.bid_price + ctx.ask_price) / Decimal("2")
    return ctx.last_price


def _aggressive_price(ctx: MarketContext, side: OrderSide) -> Decimal | None:
    """对手价: BUY→ask, SELL→bid, 退化用 last_price。"""
    if side == OrderSide.BUY:
        return ctx.ask_price if ctx.ask_price is not None else ctx.last_price
    return ctx.bid_price if ctx.bid_price is not None else ctx.last_price


# ──────────────────────────────────────────────────────────────────────────────
# 算法交易引擎 (注册表 + 计划生成)
# ──────────────────────────────────────────────────────────────────────────────


class AlgoTradingEngine:
    """算法交易引擎——注册表 + 6 种算法 + 执行计划生成。

    用法:
        engine = AlgoTradingEngine()
        plan = engine.generate_plan(order, params, ctx)
        # plan.slices → 交由 XS-04 Execution Scheduler 做时间调度

    不变量:
        - 切片数量和 == order.quantity (Decimal 守恒)
        - 参与率 ≤ 5% (§10.1)
        - 单笔订单 ≤ 15% ADV (§13.1, 超则 OrderTooLargeError)
    """

    def __init__(self) -> None:
        self._registry: dict[AlgoType, AlgoStrategy] = {}
        self._register_defaults()

    # ── 注册表 ──

    def _register_defaults(self) -> None:
        """注册 6 种默认算法。"""
        defaults: list[AlgoStrategy] = [
            TwapStrategy(),
            VwapStrategy(),
            IcebergStrategy(),
            PovStrategy(),
            ImplementationShortfallStrategy(),
            AggressiveLiquidityTakingStrategy(),
        ]
        for strat in defaults:
            self._registry[strat.algo_type] = strat

    def register(self, strategy: AlgoStrategy) -> None:
        """注册自定义算法策略 (覆盖同名默认)。"""
        self._registry[strategy.algo_type] = strategy
        logger.info("Registered algo strategy: %s", strategy.algo_type.value)

    def unregister(self, algo_type: AlgoType) -> None:
        """注销算法策略。"""
        if algo_type not in self._registry:
            raise UnknownAlgoError(
                f"未注册的算法: {algo_type.value}",
                details={"algo": algo_type.value},
            )
        del self._registry[algo_type]

    def get_algo_types(self) -> list[AlgoType]:
        """已注册算法列表 (XS-011 Selector 消费)。"""
        return list(self._registry.keys())

    def is_registered(self, algo_type: AlgoType) -> bool:
        return algo_type in self._registry

    def get_strategy(self, algo_type: AlgoType) -> AlgoStrategy:
        if algo_type not in self._registry:
            raise UnknownAlgoError(
                f"未知算法: {algo_type.value}",
                details={"algo": algo_type.value, "registered": [a.value for a in self._registry]},
            )
        return self._registry[algo_type]

    # ── 参数校验 ──

    def validate_params(self, params: AlgoParams) -> None:
        """校验参数 (AlgoParams.__post_init__ 已做基本校验, 此处补充算法特定检查)。"""
        if params.algo_type not in self._registry:
            raise UnknownAlgoError(
                f"未注册的算法: {params.algo_type.value}",
                details={"algo": params.algo_type.value},
            )
        # 重新触发 __post_init__ 校验 (防外部构造绕过)
        AlgoParams(
            algo_type=params.algo_type,
            participation_rate=params.participation_rate,
            time_horizon_minutes=params.time_horizon_minutes,
            max_slice_count=params.max_slice_count,
            min_slice_quantity=params.min_slice_quantity,
            display_quantity=params.display_quantity,
            urgency=params.urgency,
            price_limit=params.price_limit,
        )

    # ── 计划生成 ──

    def generate_plan(
        self,
        order: Order,
        params: AlgoParams,
        ctx: MarketContext,
        now: datetime | None = None,
    ) -> AlgoExecutionPlan:
        """生成执行计划——校验→选策略→切片→守恒检查。

        Args:
            order: 委托指令 (CTR-004)
            params: 算法参数
            ctx: 市场上下文
            now: 时间戳 (测试用)

        Returns:
            AlgoExecutionPlan: 切片方案 (不含时间调度)

        Raises:
            UnknownAlgoError: 算法未注册
            InvalidAlgoParamsError: 参数非法
            OrderTooLargeError: 订单 > 15% ADV (§13.1)
            AlgoError: 守恒违反 / 切片为空
        """
        now = now or datetime.now(timezone.utc)

        # 1. 参数校验
        self.validate_params(params)

        # 2. §13.1 ADV 上限检查 (单笔订单 ≤ 15% ADV)
        adv_fraction = order.quantity / ctx.adv if ctx.adv > 0 else Decimal("1")
        if adv_fraction > MAX_ADV_FRACTION:
            raise OrderTooLargeError(
                f"订单 {order.quantity} 超过 15% ADV {ctx.adv} (§13.1, 应上游拆分)",
                details={
                    "order_id": order.order_id,
                    "quantity": str(order.quantity),
                    "adv": str(ctx.adv),
                    "fraction": str(adv_fraction),
                    "max_fraction": str(MAX_ADV_FRACTION),
                },
            )

        # 3. 选策略 + 生成切片
        strategy = self.get_strategy(params.algo_type)
        slices = strategy.generate_slices(order, params, ctx)
        if not slices:
            raise AlgoError(
                f"算法 {params.algo_type.value} 生成 0 切片",
                details={"order_id": order.order_id, "quantity": str(order.quantity)},
            )

        # 4. 守恒检查 (Σ slices == order.quantity)
        sliced_sum = sum((s.quantity for s in slices), Decimal("0"))
        if sliced_sum != order.quantity:
            raise AlgoError(
                f"切片和 {sliced_sum} ≠ 订单量 {order.quantity} (守恒违反)",
                details={
                    "order_id": order.order_id,
                    "sliced_sum": str(sliced_sum),
                    "quantity": str(order.quantity),
                },
            )

        # 5. 估算最大参与率 (max slice / adv, 供 §10.1 监控)
        max_slice = max(s.quantity for s in slices)
        est_participation = max_slice / ctx.adv if ctx.adv > 0 else Decimal("0")

        plan = AlgoExecutionPlan(
            order_id=order.order_id,
            algo_type=params.algo_type,
            params=params,
            slices=slices,
            total_quantity=order.quantity,
            created_at=now,
            estimated_participation=est_participation,
        )
        logger.info(
            "Algo plan: order=%s algo=%s slices=%d total=%s est_part=%.4f",
            order.order_id,
            params.algo_type.value,
            len(slices),
            order.quantity,
            float(est_participation),
        )
        return plan

    # ── 查询 ──

    def describe_algo(self, algo_type: AlgoType) -> str:
        """算法描述 (审计/展示用)。"""
        descriptions = {
            AlgoType.TWAP: "时间加权平均价: 等量切片 + 被动价格 (λ=0 AC 特例)",
            AlgoType.VWAP: "成交量加权平均价: 按 §13.2 日内分布切片",
            AlgoType.ICEBERG: "冰山: 小额显示量切片, 隐藏大单意图",
            AlgoType.POV: f"参与率: 切片=窗口成交量×参与率 (≤{MAX_PARTICIPATION_RATE} §10.1)",
            AlgoType.IS: "Implementation Shortfall: AC 风险厌恶轨迹 (urgency 驱动)",
            AlgoType.ALT: "激进流动性摄取: 少量大单对手价吃单 (附录B Sniper→ALT)",
        }
        if algo_type not in self._registry:
            raise UnknownAlgoError(
                f"未知算法: {algo_type.value}",
                details={"algo": algo_type.value},
            )
        return descriptions.get(algo_type, algo_type.value)


# ──────────────────────────────────────────────────────────────────────────────
# 算法参数优化器 (Phase 1: 规则驱动)
# ──────────────────────────────────────────────────────────────────────────────


class AlgoParamOptimizer:
    """算法参数优化器——根据订单特征推荐 AlgoParams (Phase 1 规则驱动)。

    Phase 2+ 对标: 强化学习算法/自适应算法参数 (§2.2 XS-05 理论对标)。
    """

    def optimize(
        self,
        order: Order,
        algo_type: AlgoType,
        ctx: MarketContext,
        urgency: Decimal = Decimal("0.5"),
    ) -> AlgoParams:
        """根据订单大小/紧急度/流动性推荐参数。

        规则 (Phase 1):
            - time_horizon: 大单(>5%ADV)→长窗口(60min), 小单→短窗口(15min)
            - max_slice_count: 与时间窗口正相关, 上限 20
            - participation_rate: min(5%, 订单/ADV×2) 留余量
            - ICEBERG display_quantity: min(总量/5, 1%ADV)
        """
        adv_fraction = order.quantity / ctx.adv if ctx.adv > 0 else Decimal("0.01")

        # 时间窗口: 大单长窗口
        if adv_fraction > Decimal("0.05"):
            horizon = 60
        elif adv_fraction > Decimal("0.01"):
            horizon = 30
        else:
            horizon = 15

        # 切片数: 与窗口正相关
        max_slices = min(20, max(3, horizon // 3))

        # 参与率: 留余量, 不超 5%
        rate = min(MAX_PARTICIPATION_RATE, adv_fraction * Decimal("2"))
        if rate <= 0:
            rate = MAX_PARTICIPATION_RATE

        # ICEBERG 显示量
        display = None
        if algo_type == AlgoType.ICEBERG:
            display = min(order.quantity / Decimal("5"), ctx.adv * Decimal("0.01"))
            display = _quantize_to_lot(display, LOT_SIZE)
            if display <= 0:
                display = LOT_SIZE

        params = AlgoParams(
            algo_type=algo_type,
            participation_rate=rate,
            time_horizon_minutes=horizon,
            max_slice_count=max_slices,
            min_slice_quantity=LOT_SIZE,
            display_quantity=display,
            urgency=urgency,
            price_limit=order.limit_price,
        )
        logger.info(
            "Optimized params: order=%s algo=%s horizon=%d slices=%d rate=%.4f",
            order.order_id,
            algo_type.value,
            horizon,
            max_slices,
            float(rate),
        )
        return params

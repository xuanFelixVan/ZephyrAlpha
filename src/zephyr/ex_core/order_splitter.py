# [BLUEPRINT] MOD-EX-014 | docs/03_modules/MOD-EX-014/
# [MODULE] zephyr.ex_core.order_splitter
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.board_lot; zephyr.shared.contracts.enums.order_enums; zephyr.shared.foundation.errors
# [CONSUMERS] MOD-EX-062(Execution Strategy Selector 选定算法后切片) ; MOD-EX-012(Execution TCA 计划轨迹基准)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 切片数量和=订单总量(Decimal守恒); 仅 TWAP/VWAP(门禁降级,无Level-2依赖,量能曲线为日线/分钟线历史量能权重注入); VWAP 无量能曲线→InvalidSplitRequestError(Fail-Closed不静默降级TWAP); 买入每片>=板块min_unit且按increment对齐; 卖出仅末片可为零股(一次性申报合法); 纯函数无副作用
# [MODIFY-GUARD] docs/03_modules/MOD-EX-014/
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidSplitRequestError(ZA-EX-0018)
# [TESTS] tests/ex_core/test_order_splitter.py
# [A_module] module_id=MOD-EX-014 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""



Order Splitter — 拆单器 TWAP/VWAP (MOD-EX-014)

D-EX-CORE-14（2026-08-23 门禁降级版）：拆分策略选择 + 子订单生成 +
时间窗口分配。原门禁依赖 Level-2 订单簿深度数据（撞硬边界约束三，
免费数据源+Tick=3 秒），降级为 TWAP/VWAP——切片权重来自日线/分钟线
历史量能曲线（调用方注入 volume_profile，本模块不连数据源、不做
Level-2 依赖）。

算法：
  - TWAP：等量切片（时间加权，权重全等）。
  - VWAP：按历史量能曲线权重切片（量能分布注入，权重非负且和>0）。

A 股合法性（真源 board_lot，40_execution_broker §决策⑰）：
  - 买入：每片 ≥ min_unit 且按 increment 对齐（最大余数法分配整手单位，
    不足 min_unit 的片由最大片让渡补齐，补不齐→Fail-Closed 拒单）。
  - 卖出：中间片按 increment 对齐且 ≥ min_unit；零股尾量并入末片
    一次性申报（A 股零股卖出唯一合法形态）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: request 参数
#   fields: 参数 request，类型注解 SplitRequest
#   code: order_splitter.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: algo 参数
#   fields: 参数 algo，类型注解 SplitAlgo
#   code: order_splitter.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① split_order
#   name_en: split_order
#   intro: 拆单（纯函数：同输入必同输出，可独立单测）。
#   desc: 拆单（纯函数：同输入必同输出，可独立单测）。 Args: request: 拆单请求（symbol/side/总量/片数/VWAP 量能曲线）。 algo: TWAP=等量切片；…；源码 L245-L329
#   inputs: request algo
#   outputs: SplitPlan
#   （注：A1 之后另有 5 个公共定义未列入（含 5 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: SplitPlan
#   name_en: SplitPlan
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-EX-062(Execution Strategy Selector 选定算法后切片) ; MOD-EX-012(Execution TCA 计划轨迹…
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import ROUND_FLOOR, Decimal
from enum import Enum
from typing import Final

from zephyr.ex_core.board_lot import get_board_lot_rule
from zephyr.shared.contracts.enums.order_enums import OrderSide
from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

__all__: Final = [
    "ChildSlice",
    "InvalidSplitRequestError",
    "SplitAlgo",
    "SplitPlan",
    "SplitRequest",
    "split_order",
]

_MAX_SLICE_COUNT: Final[int] = 48  # 3秒Tick×日内240分钟口径的实用上界


class InvalidSplitRequestError(ZephyrBaseError):
    """拆单请求非法（量能曲线缺失/片数越界/合法性不可满足）。"""

    error_code = "ZA-EX-0018"


class SplitAlgo(str, Enum):
    """拆单算法（门禁降级后仅两档，无 Level-2 依赖）。"""

    TWAP = "twap"
    VWAP = "vwap"


@dataclass(frozen=True)
class SplitRequest:
    """拆单请求。

    Attributes:
        symbol: 标的代码（板块整手规则由 board_lot 真源判定）。
        side: 买/卖（卖出末片允许零股一次性申报）。
        total_quantity: 订单总量（股，正数；买入需已是合法申报数量）。
        slice_count: 切片数（1..48）。
        volume_profile: VWAP 量能权重（日线/分钟线历史量能曲线注入，
            长度==slice_count，非负且和>0）；TWAP 忽略。
    """

    symbol: str
    side: OrderSide
    total_quantity: Decimal
    slice_count: int
    volume_profile: tuple[Decimal, ...] | None = None


@dataclass(frozen=True)
class ChildSlice:
    """子订单切片（执行调度器按 sequence 顺序下发）。"""

    symbol: str
    side: OrderSide
    quantity: Decimal
    sequence: int  # 1-based
    weight: float


@dataclass(frozen=True)
class SplitPlan:
    """拆单方案（frozen；Σquantity == 订单总量 守恒不变量）。"""

    symbol: str
    side: OrderSide
    algo: SplitAlgo
    total_quantity: Decimal
    slices: tuple[ChildSlice, ...]


def _validate_request(request: SplitRequest) -> None:
    if request.total_quantity <= 0:
        raise InvalidSplitRequestError(
            "订单总量必须为正",
            details={"total_quantity": str(request.total_quantity)},
        )
    if not 1 <= request.slice_count <= _MAX_SLICE_COUNT:
        raise InvalidSplitRequestError(
            f"切片数越界(1..{_MAX_SLICE_COUNT})",
            details={"slice_count": request.slice_count},
        )


def _resolve_weights(request: SplitRequest) -> tuple[Decimal, ...]:
    """解析切片权重。VWAP 无量能曲线→Fail-Closed（不静默降级 TWAP）。"""
    n = request.slice_count
    if request.volume_profile is None:
        return tuple(Decimal("1") for _ in range(n))
    profile = request.volume_profile
    if len(profile) != n:
        raise InvalidSplitRequestError(
            "VWAP 量能曲线长度必须等于切片数",
            details={"profile_len": len(profile), "slice_count": n},
        )
    if any(w < 0 for w in profile):
        raise InvalidSplitRequestError(
            "VWAP 量能曲线权重必须非负",
            details={"volume_profile": [str(w) for w in profile]},
        )
    if sum(profile) <= 0:
        raise InvalidSplitRequestError(
            "VWAP 量能曲线权重和必须为正（历史量能全零，无法切片）",
            details={"volume_profile": [str(w) for w in profile]},
        )
    return tuple(profile)


def _floor_to_increment(quantity: Decimal, increment: Decimal) -> Decimal:
    return (quantity / increment).to_integral_value(rounding=ROUND_FLOOR) * increment


def _allocate_by_weights(
    total: Decimal,
    weights: tuple[Decimal, ...],
    increment: Decimal,
) -> list[Decimal]:
    """最大余数法：按权重把 total 分到各片，单位=increment，Σ==total。"""
    weight_sum = sum(weights)
    units_total = int(total / increment)
    quotas = [units_total * (w / weight_sum) for w in weights]
    bases = [int(q.to_integral_value(rounding=ROUND_FLOOR)) for q in quotas]
    remainder = units_total - sum(bases)
    # 余量按小数部分从大到小逐个分发（并列→序号小者优先，确定性）
    order = sorted(
        range(len(weights)),
        key=lambda i: (-(quotas[i] - bases[i]), i),
    )
    for rank in range(remainder):
        bases[order[rank % len(order)]] += 1
    return [base * increment for base in bases]


def _enforce_min_unit(
    allocations: list[Decimal],
    *,
    min_unit: Decimal,
    increment: Decimal,
    enforce_upto: int,
) -> None:
    """前 enforce_upto 片不足 min_unit 的由最大片让渡 increment 补齐（有界）。

    卖出末片（含零股尾量）不在强制范围（零股一次性申报合法），但可作为
    让渡方（让渡后仍须 ≥ min_unit）。补不齐→InvalidSplitRequestError。
    被强制片数量均为 increment 整数倍，故 (min_unit - qty) 必为 increment 整除。
    """
    for idx in range(enforce_upto):
        need_units = int((min_unit - allocations[idx]) / increment)
        for _ in range(max(need_units, 0)):
            donors = [i for i in range(len(allocations)) if i != idx and allocations[i] - increment >= min_unit]
            if not donors:
                raise InvalidSplitRequestError(
                    "切片合法性不可满足（每片须≥最小申报单位）：请减少切片数或改用整单",
                    details={
                        "slice_index": idx,
                        "min_unit": str(min_unit),
                        "slice_count": len(allocations),
                    },
                )
            donor = max(donors, key=lambda i: (allocations[i], -i))
            allocations[donor] -= increment
            allocations[idx] += increment


def split_order(request: SplitRequest, algo: SplitAlgo = SplitAlgo.TWAP) -> SplitPlan:
    """拆单（纯函数：同输入必同输出，可独立单测）。

    Args:
        request: 拆单请求（symbol/side/总量/片数/VWAP 量能曲线）。
        algo: TWAP=等量切片；VWAP=按 volume_profile 权重切片。

    Returns:
        SplitPlan，Σ slices.quantity == request.total_quantity（Decimal 守恒）。

    Raises:
        InvalidSplitRequestError: 请求非法或 A 股申报合法性不可满足（Fail-Closed）。
    """
    _validate_request(request)
    rule = get_board_lot_rule(request.symbol)
    min_unit = Decimal(rule.min_unit)
    increment = Decimal(rule.increment)
    total = request.total_quantity

    weights = (
        _resolve_weights(request) if algo is SplitAlgo.VWAP else tuple(Decimal("1") for _ in range(request.slice_count))
    )

    if request.side is OrderSide.SELL:
        odd_tail = total - _floor_to_increment(total, increment)
        lot_pool = total - odd_tail
        allocations = _allocate_by_weights(lot_pool, weights, increment)
        allocations[-1] += odd_tail  # 零股尾量并入末片，一次性申报
        _enforce_min_unit(
            allocations,
            min_unit=min_unit,
            increment=increment,
            enforce_upto=max(len(allocations) - 1, 0),
        )
    else:
        if total < min_unit or total != min_unit + _floor_to_increment(total - min_unit, increment):
            raise InvalidSplitRequestError(
                "买入总量非法（须≥min_unit且按increment对齐；先经 board_lot.round_buy_qty）",
                details={
                    "total_quantity": str(total),
                    "min_unit": str(min_unit),
                    "increment": str(increment),
                },
            )
        allocations = _allocate_by_weights(total, weights, increment)
        _enforce_min_unit(
            allocations,
            min_unit=min_unit,
            increment=increment,
            enforce_upto=len(allocations),
        )

    allocated_total = sum(allocations)
    if allocated_total != total:  # 守恒不变量（防御性断言，正常路径不可达）
        raise InvalidSplitRequestError(
            "切片守恒校验失败",
            details={"allocated": str(allocated_total), "total": str(total)},
        )

    weight_sum = sum(weights)
    slices = tuple(
        ChildSlice(
            symbol=request.symbol,
            side=request.side,
            quantity=qty,
            sequence=idx + 1,
            weight=float(weights[idx] / weight_sum),
        )
        for idx, qty in enumerate(allocations)
    )
    _logger.info(
        "拆单完成: %s %s %s → %d 片(%s)",
        request.symbol,
        request.side,
        total,
        len(slices),
        algo.value,
    )
    return SplitPlan(
        symbol=request.symbol,
        side=request.side,
        algo=algo,
        total_quantity=total,
        slices=slices,
    )

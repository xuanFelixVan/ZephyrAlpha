# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.price_cage
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.board_lot ; stdlib
# [CONSUMERS] ex_core.adapters.miniqmt_broker ; ex_core.trading_session
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 买入基准价=卖一(ask1)/卖出基准价=买一(bid1); 回退链 ask1|bid1→last→prev_close; 板块差异化幅度; 超限夹到边界(不废单)
# [MODIFY-GUARD] 40_execution_broker.md §决策⑭
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/ex_core/test_price_cage.py
# [TTL] permanent

"""

A 股价格笼子校验（40_execution_broker §决策⑭ gap 11 施工）。

2026-07-06 最新规则（沪深北交易所交易规则修订）：
- 价格笼子（有效申报价格范围）超范围委托**直接废单（拒单模式，不缓存不排队）**
- 买入基准价 = 卖一价（ask1，对手方最优价），卖出基准价 = 买一价（bid1）
  （v1.3.0 订正：基准价取对手方最优价，非己方最优价）
- 板块差异：
    - 沪深主板 / 创业板：±2% + 0.1元兜底（孰高/孰低）
    - 科创板：严格 ±2%，无兜底
    - 北交所：±5%
- 适用范围：仅连续竞价限价单（集合竞价/临停/市价单/盘后固定价格交易豁免）
- 基准价回退链：卖一/买一（对手方最优）→ 最新成交价 → 前收盘价
- 超限处理：夹到笼子边界（不废单，修正后提交）

依据：40_execution_broker.md v2.3.0 §决策⑭
      《上海证券交易所交易规则（2026年修订）》§3.3.14
      《深圳证券交易所交易规则（2026年修订）》§3.1.16

Version: 1.0.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 委托限价与方向 limit_price/side
#   fields: 连续竞价限价单委托价（Decimal）+ 买卖方向OrderSide
#   code: check_price_cage(side, limit_price) (price_cage.py L148-156)
# - id: I2
#   name: 盘口快照 ask1/bid1
#   fields: 卖一价（买入基准第一优先）/买一价（卖出基准第一优先），无盘口传None
#   code: ask1/bid1 参数 (price_cage.py L152-153)
# - id: I3
#   name: 回退价格 last_price/prev_close
#   fields: 最新成交价（回退第二优先）/前收盘价（回退第三优先）
#   code: last_price/prev_close 参数 (price_cage.py L154-155)
# - id: I4
#   name: 股票代码 symbol
#   fields: 用于板块识别（主板/创业板/科创板/北交所差异化笼子）
#   code: symbol → classify_board (price_cage.py L102-105)
# 层: 算法
# - id: A1
#   name_zh: ① 基准价回退链解析
#   name_en: _resolve_base_price
#   intro: 买入基准=卖一、卖出基准=买一（对手方最优价），无盘口依次回退最新价→前收盘
#   desc: BUY取ask1/SELL取bid1，>0即用；否则last_price→prev_close；全无返回None（L118-145）
#   inputs: I2 I3
#   outputs: 基准价 base | None
#   invariant: 买入基准价=ask1/卖出基准价=bid1；回退链ask1|bid1→last→prev_close
# - id: A2
#   name_zh: ② 板块笼子参数查询
#   name_en: _get_cage_params
#   intro: 主板/创业板±2%+0.1元兜底，科创板严格±2%无兜底，北交所±5%，未知板块回退主板最保守参数
#   desc: classify_board(symbol)→_BOARD_CAGE_PARAMS查(pct, floor_yuan)（L91-105）
#   inputs: I4
#   outputs: (pct, floor_yuan)
#   invariant: 板块差异化幅度
# - id: A3
#   name_zh: ③ 笼子边界计算与夹边校验
#   name_en: check_price_cage
#   intro: 买入上限max(base×1.02, base+0.1)向下取整tick，卖出下限min(base×0.98, base-0.1)向上取整tick，超限夹到边界不废单
#   desc: base为None→UNKNOWN原价返回；BUY: limit≤upper_tick→IN_CAGE否则CLAMPED夹到upper_tick（ROUND_FLOOR）；SELL对称（ROUND_CEILING）（L148-253）
#   inputs: I1 A1 A2
#   outputs: PriceCageResult（status/base/bounds/clamped_price/was_clamped）
#   invariant: 超限夹到边界（不废单）；夹边后价格不越笼子
# 层: 输出
# - id: O1
#   name_zh: 价格笼子校验结果 PriceCageResult
#   name_en: PriceCageResult
#   intro: 含IN_CAGE/CLAMPED/UNKNOWN状态、基准价、笼子上下限与夹边后价格，供券商适配器提交前合规校验
#   invariant: clamped_price量化到0.01 tick且落在笼子内
#   downstream: ex_core.adapters.miniqmt_broker / ex_core.trading_session
# [/ALGO_FLOW]
#
# 边:
# I2 --> A1
# I3 --> A1
# I4 --> A2
# I1 --> A3
# A1 --> A3
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import ROUND_CEILING, ROUND_FLOOR, Decimal
from enum import Enum

from zephyr.ex_core.board_lot import AShareBoard, classify_board
from zephyr.shared.contracts.enums.order_enums import OrderSide

__all__ = [
    "CageStatus",
    "PriceCageResult",
    "PRICE_TICK",
    "check_price_cage",
]

_logger = logging.getLogger(__name__)

# A 股最小价格变动单位
PRICE_TICK = Decimal("0.01")


class CageStatus(str, Enum):
    """价格笼子校验结果状态。"""

    IN_CAGE = "in_cage"  # 在笼子内，无需调整
    CLAMPED = "clamped"  # 超限，已夹到笼子边界
    UNKNOWN = "unknown"  # 无可用基准价，无法校验（调用方决定）


@dataclass(frozen=True)
class PriceCageResult:
    """价格笼子校验结果。

    Attributes:
        status: 校验状态
        base_price: 实际使用的基准价（对手方最优价或回退值）；UNKNOWN 时为 None
        upper_bound: 笼子上限（买入方向）；UNKNOWN/卖出方向时为 None
        lower_bound: 笼子下限（卖出方向）；UNKNOWN/买入方向时为 None
        clamped_price: 夹到边界后的价格（在笼子内=原价，超限=边界值）
        was_clamped: 是否发生夹边
    """

    status: CageStatus
    base_price: Decimal | None
    upper_bound: Decimal | None
    lower_bound: Decimal | None
    clamped_price: Decimal
    was_clamped: bool


# ── 板块笼子参数表 ──────────────────────────────────────────────────
# pct: 笼子幅度（百分比），floor_yuan: 0.1元兜底（None=无兜底）
_BOARD_CAGE_PARAMS: dict[AShareBoard, tuple[Decimal, Decimal | None]] = {
    AShareBoard.MAIN: (Decimal("0.02"), Decimal("0.10")),  # 主板 ±2% + 0.1兜底
    AShareBoard.CHINEXT: (Decimal("0.02"), Decimal("0.10")),  # 创业板 ±2% + 0.1兜底
    AShareBoard.STAR: (Decimal("0.02"), None),  # 科创板 严格±2% 无兜底
    AShareBoard.BSE: (Decimal("0.05"), None),  # 北交所 ±5%
}

# 未知板块回退到主板参数（最保守的有兜底规则，避免误用严格规则废单）
_FALLBACK_PARAMS = _BOARD_CAGE_PARAMS[AShareBoard.MAIN]


def _get_cage_params(symbol: str) -> tuple[Decimal, Decimal | None]:
    """获取板块对应的笼子参数 (pct, floor_yuan)。"""
    board = classify_board(symbol)
    return _BOARD_CAGE_PARAMS.get(board, _FALLBACK_PARAMS)


def _round_down_to_tick(price: Decimal) -> Decimal:
    """向下取整到 tick（0.01），用于买入夹边（避免超出笼子上限）。"""
    return price.quantize(PRICE_TICK, rounding=ROUND_FLOOR)


def _round_up_to_tick(price: Decimal) -> Decimal:
    """向上取整到 tick（0.01），用于卖出夹边（确保 >= 笼子下限）。"""
    return price.quantize(PRICE_TICK, rounding=ROUND_CEILING)


def _resolve_base_price(
    side: OrderSide,
    ask1: Decimal | None,
    bid1: Decimal | None,
    last_price: Decimal | None,
    prev_close: Decimal | None,
) -> Decimal | None:
    """按回退链解析基准价。

    买入基准价回退链：ask1（卖一）→ last_price → prev_close
    卖出基准价回退链：bid1（买一）→ last_price → prev_close

    无任何可用基准价（均为 None 或 <= 0）时返回 None。
    """
    # 第一优先：对手方最优价
    if side is OrderSide.BUY:
        primary = ask1
    else:
        primary = bid1
    if primary is not None and primary > 0:
        return primary
    # 第二优先：最新成交价
    if last_price is not None and last_price > 0:
        return last_price
    # 第三优先：前收盘价
    if prev_close is not None and prev_close > 0:
        return prev_close
    return None


def check_price_cage(
    side: OrderSide,
    limit_price: Decimal,
    symbol: str,
    ask1: Decimal | None = None,
    bid1: Decimal | None = None,
    last_price: Decimal | None = None,
    prev_close: Decimal | None = None,
) -> PriceCageResult:
    """价格笼子校验（连续竞价限价单合规硬约束）。

    按 40_execution_broker §决策⑭ 校验委托价是否在价格笼子内：
    - 买入：上限 = max(卖一×(1+pct), 卖一+floor_yuan)（有兜底时）
    - 卖出：下限 = min(买一×(1-pct), 买一-floor_yuan)（有兜底时）
    - 基准价取对手方最优价（买入=卖一，卖出=买一），回退链：盘口→最新价→前收盘价
    - 超限自动夹到笼子边界（买入向下取整到 tick / 卖出向上取整到 tick）

    Args:
        side: 买卖方向
        limit_price: 委托限价
        symbol: 股票代码（用于识别板块差异化规则）
        ask1: 卖一价（买入基准价第一优先），无盘口传 None
        bid1: 买一价（卖出基准价第一优先），无盘口传 None
        last_price: 最新成交价（回退第二优先）
        prev_close: 前收盘价（回退第三优先）

    Returns:
        PriceCageResult：含状态、基准价、笼子边界、夹边后价格

    Note:
        - 仅适用于连续竞价限价单；集合竞价/临停/市价单豁免由调用方判断
        - 无任何基准价可用时返回 UNKNOWN，调用方决定是否跳过校验或拒单
    """
    base = _resolve_base_price(side, ask1, bid1, last_price, prev_close)
    if base is None or base <= 0:
        return PriceCageResult(
            status=CageStatus.UNKNOWN,
            base_price=None,
            upper_bound=None,
            lower_bound=None,
            clamped_price=limit_price,
            was_clamped=False,
        )

    pct, floor_yuan = _get_cage_params(symbol)

    if side is OrderSide.BUY:
        # 买入上限：base × (1+pct)，有兜底时取 max(., base+floor)
        pct_bound = base * (Decimal("1") + pct)
        if floor_yuan is not None:
            upper = max(pct_bound, base + floor_yuan)
        else:
            upper = pct_bound
        upper_tick = _round_down_to_tick(upper)
        if limit_price <= upper_tick:
            return PriceCageResult(
                status=CageStatus.IN_CAGE,
                base_price=base,
                upper_bound=upper_tick,
                lower_bound=None,
                clamped_price=limit_price,
                was_clamped=False,
            )
        # 超限 → 夹到上限（向下取整到 tick）
        _logger.info(
            "price_cage CLAMP buy: symbol=%s limit=%s > upper=%s → clamp to %s",
            symbol,
            limit_price,
            upper_tick,
            upper_tick,
        )
        return PriceCageResult(
            status=CageStatus.CLAMPED,
            base_price=base,
            upper_bound=upper_tick,
            lower_bound=None,
            clamped_price=upper_tick,
            was_clamped=True,
        )

    # 卖出下限：base × (1-pct)，有兜底时取 min(., base-floor)
    pct_bound = base * (Decimal("1") - pct)
    if floor_yuan is not None:
        lower = min(pct_bound, base - floor_yuan)
    else:
        lower = pct_bound
    lower_tick = _round_up_to_tick(lower)
    if limit_price >= lower_tick:
        return PriceCageResult(
            status=CageStatus.IN_CAGE,
            base_price=base,
            upper_bound=None,
            lower_bound=lower_tick,
            clamped_price=limit_price,
            was_clamped=False,
        )
    # 超限 → 夹到下限（向上取整到 tick）
    _logger.info(
        "price_cage CLAMP sell: symbol=%s limit=%s < lower=%s → clamp to %s",
        symbol,
        limit_price,
        lower_tick,
        lower_tick,
    )
    return PriceCageResult(
        status=CageStatus.CLAMPED,
        base_price=base,
        upper_bound=None,
        lower_bound=lower_tick,
        clamped_price=lower_tick,
        was_clamped=True,
    )

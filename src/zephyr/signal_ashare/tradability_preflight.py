# [BLUEPRINT] MOD-SIG-151 | docs/03_modules/_domain_signal/tradability_preflight/blueprint.md
# [MODULE] zephyr.signal_ashare.tradability_preflight
# [DOMAIN] D_ASHARE_SIGNAL
# [DEPENDENCIES] zephyr.ex_core.price_cage(check_price_cage); zephyr.ex_core.board_lot(classify_board); zephyr.shared.contracts.enums.order_enums(OrderSide); zephyr.data.instrument_master(口径对齐:停牌/prev_close/申报单位——快照注入不直连)
# [CONSUMERS] TDM-E-L3-10 可交易性预检（候选池日频过滤）；TDM-E-L3-08 候选池输出（上游）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 纯函数零 DB/CH（行情/账户快照全注入）；fail-closed（关键字段缺失=不可交易+DATA_MISSING，不猜）；五查独立标签（SUSPENDED/LIMIT_UP/PERMISSION/LOT_CASH/DATA_MISSING）+笼子建议价（夹边语义非拒单，节点"会被拒"按 ex_core 实装口径修正为给出夹边价）；金额一律 Decimal；板块判定唯一真源=board_lot.classify_board；权限词表 {STAR,CHINEXT,BSE}，账户上下文缺失时权限查降级为 detail 不阻断（下单层 L4-12 会再查）
# [MODIFY-GUARD] docs/03_modules/_domain_signal/tradability_preflight/blueprint.md
# [STABILITY] testing
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ValueError（symbol 空超长/快照类型非法 fail-closed）
# [TESTS] tests/signal_ashare/test_tradability_preflight.py
# [A_module] module_id=MOD-SIG-151 | layer=module | stability=testing | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
TradabilityPreflight — 可交易性预检三查专件（MOD-SIG-151）

TDM-E-L3-10「候选池里谁今天实际买不进」的聚合专件：把散在
instrument_master（停牌/昨收/申报单位）、ex_core.price_cage（笼子）、
ex_core.board_lot（板块/手数）的原子能力按"选股层当日可买性"口径聚合成
一次查表，输出逐票裁决与阻断原因，防止下单层空转报错。

出身：晨审 st-tdm-review-20260911 §7.1 L3-10 部分采纳——停牌/昨收/申报单位
三查由 instrument_master 承载；价格笼子/权限/资金一手三查无专件，缺口在册。
Owner 2026-09-16 裁定开工接通。

大白话：每天候选池生成后过一遍"今天谁根本买不进"——停牌的、一字涨停封死的、
没有板块交易权限的、钱不够买一手的，全部标记跳过；价格超笼子的不拦，
给出夹边后的建议价（真拒单发生在下单层预检，那里有实时盘口）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum

from zephyr.ex_core.board_lot import classify_board
from zephyr.ex_core.price_cage import CageStatus, check_price_cage
from zephyr.shared.contracts.enums.order_enums import OrderSide

__all__ = [
    "BlockedReason",
    "InstrumentSnapshot",
    "AccountContext",
    "TradabilityVerdict",
    "preflight_tradability",
]

_: Decimal = Decimal("0")  # Decimal 字面量哨兵（float 禁用口径自省）


class BlockedReason(str, Enum):
    """阻断原因封闭枚举（/details 的 key 与之一一对应）。"""

    SUSPENDED = "suspended"
    LIMIT_UP_UNBUYABLE = "limit_up_unbuyable"
    PERMISSION = "permission"
    LOT_CASH = "lot_cash"
    DATA_MISSING = "data_missing"


_PERMISSION_BY_BOARD_VALUE = {"STAR": "STAR", "CHINEXT": "CHINEXT", "BSE": "BSE"}

# 涨跌停比例（板块 × ST）：主板 10/ST 5；创业板·科创板 20（ST 同）；北交所 30
_LIMIT_RATIO_BY_BOARD = {
    "MAIN": (Decimal("0.10"), Decimal("0.05")),
    "CHINEXT": (Decimal("0.20"), Decimal("0.20")),
    "STAR": (Decimal("0.20"), Decimal("0.20")),
    "BSE": (Decimal("0.30"), Decimal("0.30")),
}


@dataclass(frozen=True)
class InstrumentSnapshot:
    """单票当日静态快照（由 instrument_master 口径产出后注入，本模块不查库）。"""

    symbol: str
    suspended: bool
    prev_close: Decimal | None = None
    is_st: bool = False
    min_order_unit: int | None = None  # 主板 100 / 科创板 200 起（instrument_master 口径）
    open: Decimal | None = None  # 当日开盘价（一字判定用，可缺省）
    high: Decimal | None = None
    low: Decimal | None = None


@dataclass(frozen=True)
class AccountContext:
    """账户上下文（选股层可缺省；缺省时权限/资金查降级为 detail 不阻断）。"""

    available_cash: Decimal | None = None
    permissions: frozenset[str] = field(default_factory=frozenset)


@dataclass(frozen=True)
class TradabilityVerdict:
    """逐票裁决：tradable=False 时 blocked 必非空，details 携带逐查证据。"""

    symbol: str
    tradable: bool
    blocked: tuple[BlockedReason, ...]
    cage_suggested_price: Decimal | None = None  # 笼子夹边建议价（CLAMPED 时给出）
    details: dict[str, str] = field(default_factory=dict)


def _limit_ratio(board_value: str, is_st: bool) -> Decimal:
    pair = _LIMIT_RATIO_BY_BOARD.get(board_value)
    if pair is None:
        raise ValueError(f"未知板块无法定涨跌停比例: {board_value}")
    return pair[1] if is_st else pair[0]


def _round_two(price: Decimal) -> Decimal:
    return price.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _check_suspended(snap: InstrumentSnapshot) -> tuple[bool, str]:
    if snap.suspended:
        return True, "停牌股当日不可买"
    return False, ""


def _check_limit_up(
    snap: InstrumentSnapshot, intended_price: Decimal | None
) -> tuple[bool, str, Decimal | None]:
    """一字涨停封死或意图价触板=买不进。返回 (blocked, reason, limit_up)。"""
    if snap.prev_close is None or snap.prev_close <= 0:
        return True, "DATA_MISSING:prev_close（无法算涨停价，fail-closed）", None
    board_value = classify_board(snap.symbol).name
    limit_up = _round_two(snap.prev_close * (Decimal("1") + _limit_ratio(board_value, snap.is_st)))
    if (
        snap.open is not None
        and snap.high is not None
        and snap.low is not None
        and snap.open == snap.high
        and snap.low >= limit_up
    ):
        return True, f"一字涨停封死（限价 {limit_up}）", limit_up
    if intended_price is not None and intended_price >= limit_up:
        return True, f"意图价 {intended_price} 已触涨停 {limit_up}（排队未必成交）", limit_up
    return False, "", limit_up


def _check_permission(
    symbol: str,
    account: AccountContext | None,
) -> tuple[bool, str]:
    """板块交易权限：账户上下文缺失=降级 detail（下单层 L4-12 会再查）。"""
    board_value = classify_board(symbol).name
    required = _PERMISSION_BY_BOARD_VALUE.get(board_value)
    if required is None:
        return False, ""
    if account is None:
        return False, f"PERMISSION_SKIP:{required}（账户上下文未注入，下单层复检）"
    if required not in account.permissions:
        return True, f"缺少板块交易权限 {required}"
    return False, ""


def _check_lot_cash(
    snap: InstrumentSnapshot,
    intended_price: Decimal | None,
    intended_qty: Decimal | None,
    account: AccountContext | None,
) -> tuple[bool, str]:
    """资金一手：钱不够买最小申报单位=买不进。"""
    if intended_price is None or intended_price <= 0:
        return False, ""
    unit = snap.min_order_unit
    if unit is None or unit <= 0:
        return True, "DATA_MISSING:min_order_unit（无法算一手成本，fail-closed）"
    qty = intended_qty if intended_qty is not None and intended_qty > 0 else Decimal(unit)
    min_cost = _round_two(intended_price * Decimal(unit))
    need = _round_two(intended_price * qty)
    if account is None or account.available_cash is None:
        return False, f"LOT_CASH_SKIP:账户资金未注入（一手约 {min_cost} 元）"
    if account.available_cash < need:
        return True, f"资金不足：需 {need} 元，可用 {account.available_cash} 元（一手约 {min_cost} 元）"
    return False, ""


def _cage_suggestion(
    snap: InstrumentSnapshot, intended_price: Decimal | None
) -> tuple[Decimal | None, str]:
    """笼子为夹边语义非拒单：CLAMPED 给建议价，UNKNOWN 跳过（无基准价）。"""
    if intended_price is None or snap.prev_close is None:
        return None, ""
    result = check_price_cage(
        OrderSide.BUY,
        intended_price,
        snap.symbol,
        ask1=None,
        bid1=None,
        last_price=None,
        prev_close=snap.prev_close,
    )
    if result.status is CageStatus.CLAMPED:
        return (
            result.clamped_price,
            f"PRICE_CAGE:意图价超笼子，建议夹边价 {result.clamped_price}",
        )
    return None, ""


def preflight_tradability(
    snap: InstrumentSnapshot,
    account: AccountContext | None = None,
    intended_price: Decimal | None = None,
    intended_qty: Decimal | None = None,
) -> TradabilityVerdict:
    """候选池当日可买性预检（TDM-E-L3-10 专件）。

    Args:
        snap: 单票当日静态快照（instrument_master 口径注入）。
        account: 账户上下文，可缺省（权限/资金查降级为 detail）。
        intended_price: 意图申报价（触板/笼子/资金查的输入，可缺省）。
        intended_qty: 意图数量（缺省按最小申报单位估一手）。

    Returns:
        TradabilityVerdict：tradable=False 时 blocked 非空。

    Raises:
        ValueError: symbol 为空或超长（fail-closed）。
    """
    if not snap.symbol or len(snap.symbol) > 16:
        raise ValueError(f"symbol 非法: {snap.symbol!r}")
    blocked: list[BlockedReason] = []
    details: dict[str, str] = {}

    hit, why = _check_suspended(snap)
    if hit:
        blocked.append(BlockedReason.SUSPENDED)
        details[BlockedReason.SUSPENDED.value] = why

    hit, why, _limit = _check_limit_up(snap, intended_price)
    if hit:
        reason = (
            BlockedReason.DATA_MISSING
            if why.startswith("DATA_MISSING")
            else BlockedReason.LIMIT_UP_UNBUYABLE
        )
        blocked.append(reason)
        details[reason.value] = why

    hit, why = _check_permission(snap.symbol, account)
    if hit:
        blocked.append(BlockedReason.PERMISSION)
        details[BlockedReason.PERMISSION.value] = why
    elif why:
        details["permission_skip"] = why

    hit, why = _check_lot_cash(snap, intended_price, intended_qty, account)
    if hit:
        reason = (
            BlockedReason.DATA_MISSING
            if why.startswith("DATA_MISSING")
            else BlockedReason.LOT_CASH
        )
        blocked.append(reason)
        details[reason.value] = why
    elif why:
        details["lot_cash_skip"] = why

    cage_price, cage_note = _cage_suggestion(snap, intended_price)
    if cage_note:
        details["price_cage"] = cage_note

    return TradabilityVerdict(
        symbol=snap.symbol,
        tradable=not blocked,
        blocked=tuple(blocked),
        cage_suggested_price=cage_price,
        details=details,
    )

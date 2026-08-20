# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.board_lot
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] stdlib
# [CONSUMERS] ex_core.trading_session ; ex_core.adapters.miniqmt_broker
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 买入数量按板块差异化向下取整;零股(<min_unit)卖出必须一次性申报
# [MODIFY-GUARD] 40_execution_broker.md §决策⑰
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] tests/ex_core/test_board_lot.py
# [TTL] permanent

"""

A 股板块识别与整手申报规则（40_execution_broker §决策⑰ gap 17 施工）。

2026-07-06 最新规则（沪深北交易所交易规则修订）：
- 沪深主板 / 创业板：100 股整数倍起买，100 股递增
- 科创板：200 股起买，超 200 股按 1 股递增（201/202 股合法，100 股申报 error_code=52）
- 北交所：100 股起买，100 股递增
- 卖出零股（持仓 < min_unit）必须一次性申报卖出，不可拆分、不可忽略

依据：40_execution_broker.md v2.3.0 §决策⑰（v1.5.0 硬错误订正：
      原 floor(qty,100) 全板块统一对科创板是废单级错误）

Version: 1.0.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 股票代码 symbol
#   fields: 支持 600000.SH / sh600000 / 600000 等格式（含交易所后缀或前缀）
#   code: _strip_suffix L97-107
# - id: I2
#   name: 目标买入数量 qty
#   fields: 原始目标买入股数（Decimal 正数）
#   code: round_buy_qty L173
# - id: I3
#   name: 卖出数量 + 当前持仓
#   fields: sell_qty 计划卖出股数 + current_qty 当前持仓股数
#   code: adjust_sell_for_odd_lot L218-220
# 层: 算法
# - id: A1
#   name_zh: ① 板块识别
#   name_en: classify_board
#   intro: 按代码前缀识别主板/创业板/科创板/北交所，3位前缀优先消歧
#   desc: 688/689→STAR；300/301→CHINEXT；600/601/603/605、000/001→MAIN；920-923 及 83/43/87/92/93/94、4/8 开头→BSE；不识→UNKNOWN（L126-154）
#   inputs: I1
#   outputs: AShareBoard 板块枚举
# - id: A2
#   name_zh: ② 整手规则查表
#   name_en: get_board_lot_rule
#   intro: 按板块取整手规则（起买量+递增单位），未知板块回退主板规则并告警
#   desc: _BOARD_LOT_RULES 表：主板/创业板/北交所 min_unit=100 increment=100；科创板 min_unit=200 increment=1（L78-91）；UNKNOWN→_FALLBACK_RULE 主板（L163-170）
#   inputs: A1
#   outputs: BoardLotRule
# - id: A3
#   name_zh: ③ 买入数量向下取整
#   name_en: round_buy_qty
#   intro: 买入量按板块规则向下取整到合法申报数，不足起买量返回 0
#   desc: qty<min_unit→0；否则 min_unit + floor((qty−min_unit)/increment)×increment（L186-196）；科创板超 200 按 1 股递增
#   inputs: A2 I2
#   outputs: 合法买入申报数量（≥0）
#   invariant: 买入数量按板块差异化向下取整
# - id: A4
#   name_zh: ④ 零股卖出一次性申报
#   name_en: adjust_sell_for_odd_lot / is_odd_lot
#   intro: 卖出后剩余不足一个最小申报单位时必须全部清仓，不可拆分
#   desc: remaining=current−sell；0<remaining<min_unit → 返回 current_qty 全卖（L237-245）；is_odd_lot: qty<min_unit 判零股（L199-215）
#   inputs: A2 I3
#   outputs: 调整后卖出数量（=sell_qty 或 current_qty）
#   invariant: 零股(<min_unit)卖出必须一次性申报
# 层: 输出
# - id: O1
#   name_zh: 合法申报数量（买/卖）
#   name_en: legal order quantity
#   intro: 整手对齐后的买入量与零股调整后的卖出量，直接用于下单
#   downstream: ex_core.trading_session ; ex_core.adapters.miniqmt_broker
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# I2 --> A3
# A2 --> A4
# I3 --> A4
# A3 --> O1
# A4 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

__all__ = [
    "AShareBoard",
    "BoardLotRule",
    "classify_board",
    "get_board_lot_rule",
    "round_buy_qty",
    "adjust_sell_for_odd_lot",
    "is_odd_lot",
]

_logger = logging.getLogger(__name__)


class AShareBoard(str, Enum):
    """A 股板块分类。"""

    MAIN = "main"  # 沪深主板
    CHINEXT = "chinext"  # 创业板
    STAR = "star"  # 科创板
    BSE = "bse"  # 北交所
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class BoardLotRule:
    """板块整手申报规则。

    Attributes:
        board: 板块
        lot_size: 整手数（主板/创业板/北交所=100，科创板=200）
        min_unit: 买入最小申报数量（起买量）
        increment: 超过 min_unit 后的递增单位（主板/创业板/北交所=100，科创板=1）
    """

    board: AShareBoard
    lot_size: int
    min_unit: int
    increment: int


# 板块整手规则表（2026-07-06 最新，§决策⑰）
_BOARD_LOT_RULES: dict[AShareBoard, BoardLotRule] = {
    AShareBoard.MAIN: BoardLotRule(AShareBoard.MAIN, lot_size=100, min_unit=100, increment=100),
    AShareBoard.CHINEXT: BoardLotRule(AShareBoard.CHINEXT, lot_size=100, min_unit=100, increment=100),
    AShareBoard.STAR: BoardLotRule(AShareBoard.STAR, lot_size=200, min_unit=200, increment=1),
    AShareBoard.BSE: BoardLotRule(AShareBoard.BSE, lot_size=100, min_unit=100, increment=100),
}

# 主板规则作为未知板块的安全回退
_FALLBACK_RULE = _BOARD_LOT_RULES[AShareBoard.MAIN]


def _strip_suffix(symbol: str) -> str:
    """剥离交易所后缀，返回裸码。

    支持: "600000.SH" / "600000.SS" / "600000.SZ" / "600000.BJ" /
          "sh600000" / "sz000001" / "bj830799" / "600000"
    """
    if "." in symbol:
        return symbol.split(".", 1)[0]
    if len(symbol) >= 2 and symbol[:2].lower() in ("sh", "sz", "bj"):
        return symbol[2:]
    return symbol


def classify_board(symbol: str) -> AShareBoard:
    """从股票代码识别 A 股板块。

    规则（2026-07-06 最新）：
    - 科创板：688/689 开头（.SH）→ STAR
    - 创业板：300/301 开头（.SZ）→ CHINEXT
    - 北交所：4/8 开头（.BJ，含 43/83/87/92/93/94）→ BSE
    - 沪市主板：600/601/603/605 开头（.SH）→ MAIN
    - 深市主板：000/001 开头（.SZ）→ MAIN

    Args:
        symbol: 股票代码，支持 "600000.SH" / "600000" / "sh600000" 格式

    Returns:
        AShareBoard 枚举值；无法识别返回 UNKNOWN
    """
    code = _strip_suffix(symbol).strip()
    if len(code) < 1 or not code[0].isdigit():
        return AShareBoard.UNKNOWN

    # 3 位前缀优先判断（更具体，消歧 9xx）
    prefix3 = code[:3]
    if prefix3 in ("688", "689"):
        return AShareBoard.STAR
    if prefix3 in ("300", "301"):
        return AShareBoard.CHINEXT
    if prefix3 in ("600", "601", "603", "605"):
        return AShareBoard.MAIN
    if prefix3 in ("000", "001"):
        return AShareBoard.MAIN
    if prefix3 in ("920", "921", "922", "923"):
        # 北交所 920xxx 新代码段（必须 3 位拦截，否则首位 9 误判为沪市 B 股）
        return AShareBoard.BSE

    # 2 位前缀判断（北交所 83/43/87/92/93/94，与 normalizer _PREFIX2 对齐）
    prefix2 = code[:2]
    if prefix2 in ("83", "43", "87", "92", "93", "94"):
        return AShareBoard.BSE

    # 1 位前缀判断（北交所：4/8 开头，兜底）
    first = code[0]
    if first in ("8", "4"):
        return AShareBoard.BSE

    return AShareBoard.UNKNOWN


def get_board_lot_rule(symbol: str) -> BoardLotRule:
    """获取板块对应的整手申报规则。

    未知板块回退到主板规则（100 股整数倍）并记录 warning，调用方应检查
    classify_board 决定是否跳过该标的。
    """
    board = classify_board(symbol)
    if board == AShareBoard.UNKNOWN:
        _logger.warning(
            "classify_board UNKNOWN for symbol=%s, fallback to MAIN rule(100lot)",
            symbol,
        )
        return _FALLBACK_RULE
    return _BOARD_LOT_RULES[board]


def round_buy_qty(qty: Decimal, symbol: str) -> Decimal:
    """买入数量按板块规则向下取整到合法申报数量。

    - 主板/创业板/北交所：floor(qty, 100)，即 100 股整数倍
    - 科创板：>=200 时 floor(qty-200, 1)+200，<200 时返回 0

    Args:
        qty: 原始目标买入数量（正数）
        symbol: 股票代码

    Returns:
        合法申报数量（向下取整，>=0）。不足起买量返回 0。
    """
    if qty <= 0:
        return Decimal("0")
    rule = get_board_lot_rule(symbol)
    min_unit = Decimal(rule.min_unit)
    increment = Decimal(rule.increment)
    if qty < min_unit:
        return Decimal("0")
    # 超过起买量的部分按 increment 向下取整
    excess = qty - min_unit
    whole_excess = (excess // increment) * increment
    return min_unit + whole_excess


def is_odd_lot(qty: Decimal, symbol: str) -> bool:
    """判断是否为零股（持仓 < min_unit，卖出时必须一次性申报）。

    零股定义：持仓数量小于该板块最小买入申报单位。
    例如：主板持仓 50 股 = 零股；科创板持仓 150 股 = 零股（<200）。

    Args:
        qty: 持仓数量
        symbol: 股票代码

    Returns:
        True 表示零股（必须一次性卖出）
    """
    if qty <= 0:
        return False
    rule = get_board_lot_rule(symbol)
    return qty < rule.min_unit


def adjust_sell_for_odd_lot(sell_qty: Decimal, current_qty: Decimal, symbol: str) -> Decimal:
    """卖出数量调整：若卖出后剩余 < min_unit（零股），则全部一次性卖出。

    A 股规则：卖出后剩余持仓不足一个最小申报单位时，剩余零股必须一次性
    申报卖出，不可保留。本函数检测此场景并放大卖出量至清仓。

    Args:
        sell_qty: 计划卖出数量（正数）
        current_qty: 当前持仓数量
        symbol: 股票代码

    Returns:
        调整后的卖出数量（若触发零股规则 = current_qty 全部卖出；
        否则 = sell_qty 原值）
    """
    if sell_qty <= 0 or current_qty <= 0:
        return Decimal("0")
    rule = get_board_lot_rule(symbol)
    remaining = current_qty - sell_qty
    if 0 < remaining < rule.min_unit:
        # 卖出后剩余零股 → 必须一次性清仓
        _logger.info(
            "odd-lot sell adjustment: symbol=%s current=%s sell=%s remaining=%s<%d → sell all",
            symbol,
            current_qty,
            sell_qty,
            remaining,
            rule.min_unit,
        )
        return current_qty
    return sell_qty

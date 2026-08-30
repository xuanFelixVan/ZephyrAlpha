# [BLUEPRINT] 94_crypto_quant_expansion | docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/94_crypto_quant_expansion.md | §4.4
# [MODULE] zephyr.risk.core.leverage_risk_model
# [DOMAIN] D_RISK
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] 风控否决链(晋升后接线,C-047裁决链)
# [STARTUP] imported
# [MATURITY] candidate
# [INVARIANTS] 爆仓价多头=entry*(1-1/leverage+mmr)/空头=entry*(1+1/leverage-mmr);维持保证金率按名义价值阶梯取档;资金费率成本=notional*rate*periods(正费率多付空收);margin_ratio=维持保证金/保证金余额,>=1即爆仓;distance_to_liquidation以标记价为基准的相对距离(正值=安全);非法输入抛InvalidLeverageRiskInputError
# [MODIFY-GUARD] tests/risk/core/test_leverage_risk_model.py
# [STABILITY] volatile
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidLeverageRiskInputError(ZA-RK-0072)
# [TESTS] tests/risk/core/test_leverage_risk_model.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: 持仓输入(entry_price/mark_price/leverage/position_notional/margin_balance/side) + funding_rate/holding_periods
# I2: 维持保证金率阶梯 MaintenanceMarginTier 序列(按交易所规则,名义价值升序)
# F1: get_maintenance_margin_rate(名义价值落档→该档mmr)
# F2: calculate_liquidation_price(多:entry*(1-1/lev+mmr);空:entry*(1+1/lev-mmr))
# F3: calculate_funding_cost(notional*rate*periods,空头符号取反=收入)
# F4: calculate_margin_ratio(notional*mmr/margin_balance,>=1爆仓)
# F5: calculate_distance_to_liquidation(多:(mark-liq)/mark;空:(liq-mark)/mark)
# A1: assess_leverage_position(聚合快照+四级风险分级SAFE/WARNING/CRITICAL/LIQUIDATED)
# O1: LeverageRiskSnapshot
# [/ALGO_FLOW]
"""
D_RISK — 杠杆风控模型（CAND-CRYPTO-008，94 号 memo §4.4 杠杆与资金费率）。

Phase 2 永续合约交易的仓位与风控扩展：现货风控体系不覆盖杠杆维度，
杠杆持仓无爆仓价/维持保证金模型 = 实盘必爆（registry problem_it_solves）。

本模块落地四件事：
  1. 爆仓价（liquidation price）：保证金不足时强制平仓价。
       多头 liq = entry * (1 - 1/leverage + mmr)
       空头 liq = entry * (1 + 1/leverage - mmr)
     推导：亏损 = 初始保证金 - 维持保证金 时强平（逐仓口径，不计手续费）。
  2. 维持保证金率（maintenance margin rate）：按交易所阶梯规则
     （名义价值越大档位越高，对齐 Binance/OKX 档位制），
     ``get_maintenance_margin_rate`` 按持仓名义价值取档。
  3. 资金费率持仓成本：funding cost = position_notional * funding_rate
     * holding_periods。正费率多头付、空头收（空头成本取负=收入），
     进持仓成本口径（94 号 §4.4 费束缚：短持有被费吃掉）。
  4. 风险指标：margin_ratio（维持保证金/保证金余额，>=1 触发爆仓）
     与 distance_to_liquidation（标记价到爆仓价的相对距离，正值=安全），
     聚合 ``assess_leverage_position`` 输出四级风险分级快照。

时间口径：资金费率按结算期数（8h/期）计，无墙钟依赖。
SSoT: candidate_module_registry CAND-CRYPTO-008 + 94 号 §4.4
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: position_notional 参数
#   fields: 参数 position_notional，类型注解 float
#   code: leverage_risk_model.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: tiers 参数
#   fields: 参数 tiers，类型注解 Sequence[MaintenanceMarginTier]
#   code: leverage_risk_model.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: entry_price 参数
#   fields: 参数 entry_price，类型注解 float
#   code: leverage_risk_model.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: leverage 参数
#   fields: 参数 leverage，类型注解 float
#   code: leverage_risk_model.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① get_maintenance_margin_rate
#   name_en: get_maintenance_margin_rate
#   intro: 按交易所阶梯规则取维持保证金率：名义价值落档，返回该档 mmr。
#   desc: 按交易所阶梯规则取维持保证金率：名义价值落档，返回该档 mmr。 Args: position_notional: 持仓名义价值（>0） tiers: 阶梯配置（默认 DEFAU…；源码 L263-L296
#   inputs: position_notional tiers
#   outputs: float
# - id: A2
#   name_zh: ② calculate_liquidation_price
#   name_en: calculate_liquidation_price
#   intro: 爆仓价（逐仓口径，不计手续费）。
#   desc: 爆仓价（逐仓口径，不计手续费）。 多头: liq = entry * (1 - 1/leverage + mmr) 空头: liq = entry * (1 + 1/levera…；源码 L299-L313
#   inputs: entry_price leverage maintenance_margin_rate side
#   outputs: float
# - id: A3
#   name_zh: ③ calculate_funding_cost
#   name_en: calculate_funding_cost
#   intro: 资金费率持仓成本 = notional * funding_rate * holding_periods。
#   desc: 资金费率持仓成本 = notional * funding_rate * holding_periods。 正费率：多头付（成本为正）、空头收（成本为负=净收入）；负费率反之。…；源码 L316-L338
#   inputs: position_notional funding_rate holding_periods side
#   outputs: float
# - id: A4
#   name_zh: ④ calculate_margin_ratio
#   name_en: calculate_margin_ratio
#   intro: margin ratio = 维持保证金 / 保证金余额（>=1 触发爆仓）。
#   desc: margin ratio = 维持保证金 / 保证金余额（>=1 触发爆仓）。 维持保证金 = position_notional * maintenance_margin_ra…；源码 L341-L364
#   inputs: margin_balance position_notional maintenance_margin_rate
#   outputs: float
# - id: A5
#   name_zh: ⑤ calculate_distance_to_liquidation
#   name_en: calculate_distance_to_liquidation
#   intro: 标记价到爆仓价的相对距离（以标记价为基准，正值=安全）。
#   desc: 标记价到爆仓价的相对距离（以标记价为基准，正值=安全）。 多头: (mark - liq) / mark；空头: (liq - mark) / mark。 负值表示标记价已越过爆…；源码 L367-L389
#   inputs: mark_price liquidation_price side
#   outputs: float
# - id: A6
#   name_zh: ⑥ assess_leverage_position
#   name_en: assess_leverage_position
#   intro: 聚合评估杠杆持仓：爆仓价/维持保证金率/资金费率成本/风险指标快照。
#   desc: 聚合评估杠杆持仓：爆仓价/维持保证金率/资金费率成本/风险指标快照。 风险分级（margin_ratio = 维持保证金/保证金余额）： >= 1.0 → LIQUIDATED（…；源码 L392-L449
#   inputs: side entry_price mark_price leverage position_notional margin_balance…
#   outputs: LeverageRiskSnapshot
#   （注：A6 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: float
#   name_en: float
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 风控否决链(晋升后接线,C-047裁决链)
# - id: O2
#   name_zh: LeverageRiskSnapshot
#   name_en: LeverageRiskSnapshot
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: 风控否决链(晋升后接线,C-047裁决链)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> A6
# A6 --> O1
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Final, Sequence

from zephyr.shared.foundation.errors import ZephyrBaseError

__all__: Final = [
    "InvalidLeverageRiskInputError",
    "PositionSide",
    "MaintenanceMarginTier",
    "LeverageRiskSnapshot",
    "DEFAULT_MAINTENANCE_MARGIN_TIERS",
    "MARGIN_RATIO_WARNING",
    "MARGIN_RATIO_CRITICAL",
    "get_maintenance_margin_rate",
    "calculate_liquidation_price",
    "calculate_funding_cost",
    "calculate_margin_ratio",
    "calculate_distance_to_liquidation",
    "assess_leverage_position",
]

_logger = logging.getLogger(__name__)

#: margin_ratio 风险分级阈值（维持保证金/保证金余额）
MARGIN_RATIO_WARNING: Final = 0.50
MARGIN_RATIO_CRITICAL: Final = 0.80


class InvalidLeverageRiskInputError(ZephyrBaseError):
    """杠杆风控输入非法（价格非正/杠杆<1/保证金率越界/阶梯配置非法等）。"""

    error_code = "ZA-RK-0072"


class PositionSide(Enum):
    """持仓方向（VO-012 Side 已预留 SHORT/COVER）。"""

    LONG = "LONG"
    SHORT = "SHORT"


@dataclass(frozen=True)
class MaintenanceMarginTier:
    """维持保证金率阶梯档（按交易所规则，名义价值升序排列）。

    Attributes:
        notional_cap: 本档持仓名义价值上限（最后一档为 inf）
        maintenance_margin_rate: 本档维持保证金率（mmr，[0,1)）
    """

    notional_cap: float
    maintenance_margin_rate: float


#: 默认维持保证金率阶梯（对齐主流交易所 BTC 永续档位制，94 号 §4.4
#: "爆仓价公式按交易所档位（维持保证金率阶梯）"；晋升后按目标交易所实测校准）
DEFAULT_MAINTENANCE_MARGIN_TIERS: Final = (
    MaintenanceMarginTier(notional_cap=50_000.0, maintenance_margin_rate=0.004),
    MaintenanceMarginTier(notional_cap=250_000.0, maintenance_margin_rate=0.005),
    MaintenanceMarginTier(notional_cap=1_000_000.0, maintenance_margin_rate=0.01),
    MaintenanceMarginTier(notional_cap=10_000_000.0, maintenance_margin_rate=0.025),
    MaintenanceMarginTier(notional_cap=math.inf, maintenance_margin_rate=0.05),
)


@dataclass(frozen=True)
class LeverageRiskSnapshot:
    """杠杆持仓风险快照（assess_leverage_position 聚合输出）。

    Attributes:
        side: 持仓方向
        entry_price: 开仓均价
        mark_price: 标记价格
        leverage: 杠杆倍数
        position_notional: 持仓名义价值
        maintenance_margin_rate: 当前档位维持保证金率
        liquidation_price: 爆仓价
        margin_ratio: 维持保证金/保证金余额（>=1 触发爆仓）
        distance_to_liquidation: 标记价到爆仓价的相对距离（正值=安全）
        funding_cost: 资金费率持仓成本（负值=净收入）
        risk_level: 风险分级（SAFE/WARNING/CRITICAL/LIQUIDATED）
    """

    side: PositionSide
    entry_price: float
    mark_price: float
    leverage: float
    position_notional: float
    maintenance_margin_rate: float
    liquidation_price: float
    margin_ratio: float
    distance_to_liquidation: float
    funding_cost: float
    risk_level: str


def _validate_common(
    entry_price: float,
    leverage: float,
    maintenance_margin_rate: float,
) -> None:
    if entry_price <= 0:
        raise InvalidLeverageRiskInputError(
            "entry_price 必须为正",
            details={"entry_price": entry_price},
        )
    if leverage < 1:
        raise InvalidLeverageRiskInputError(
            "leverage 必须 >= 1",
            details={"leverage": leverage},
        )
    if not 0 <= maintenance_margin_rate < 1:
        raise InvalidLeverageRiskInputError(
            "maintenance_margin_rate 必须在 [0,1) 区间",
            details={"maintenance_margin_rate": maintenance_margin_rate},
        )


def get_maintenance_margin_rate(
    position_notional: float,
    tiers: Sequence[MaintenanceMarginTier] = DEFAULT_MAINTENANCE_MARGIN_TIERS,
) -> float:
    """按交易所阶梯规则取维持保证金率：名义价值落档，返回该档 mmr。

    Args:
        position_notional: 持仓名义价值（>0）
        tiers: 阶梯配置（默认 DEFAULT_MAINTENANCE_MARGIN_TIERS，须按
            notional_cap 升序、至少一档）

    Returns:
        落档的维持保证金率（[0,1)）
    """
    if position_notional <= 0:
        raise InvalidLeverageRiskInputError(
            "position_notional 必须为正",
            details={"position_notional": position_notional},
        )
    if not tiers:
        raise InvalidLeverageRiskInputError(
            "维持保证金率阶梯不能为空",
            details={},
        )
    for tier in tiers:
        if not 0 <= tier.maintenance_margin_rate < 1:
            raise InvalidLeverageRiskInputError(
                "阶梯 maintenance_margin_rate 必须在 [0,1) 区间",
                details={"tier": tier},
            )
        if position_notional <= tier.notional_cap:
            return tier.maintenance_margin_rate
    # 最后一档 cap 非 inf 的配置兜底：取最高档（防御，正常配置末档为 inf）
    return tiers[-1].maintenance_margin_rate


def calculate_liquidation_price(
    entry_price: float,
    leverage: float,
    maintenance_margin_rate: float,
    side: PositionSide = PositionSide.LONG,
) -> float:
    """爆仓价（逐仓口径，不计手续费）。

    多头: liq = entry * (1 - 1/leverage + mmr)
    空头: liq = entry * (1 + 1/leverage - mmr)
    """
    _validate_common(entry_price, leverage, maintenance_margin_rate)
    if side is PositionSide.LONG:
        return entry_price * (1.0 - 1.0 / leverage + maintenance_margin_rate)
    return entry_price * (1.0 + 1.0 / leverage - maintenance_margin_rate)


def calculate_funding_cost(
    position_notional: float,
    funding_rate: float,
    holding_periods: int,
    side: PositionSide = PositionSide.LONG,
) -> float:
    """资金费率持仓成本 = notional * funding_rate * holding_periods。

    正费率：多头付（成本为正）、空头收（成本为负=净收入）；负费率反之。
    holding_periods 为资金费结算期数（通常 8h/期），必须 >= 0。
    """
    if position_notional <= 0:
        raise InvalidLeverageRiskInputError(
            "position_notional 必须为正",
            details={"position_notional": position_notional},
        )
    if holding_periods < 0:
        raise InvalidLeverageRiskInputError(
            "holding_periods 必须 >= 0",
            details={"holding_periods": holding_periods},
        )
    cost = position_notional * funding_rate * holding_periods
    return cost if side is PositionSide.LONG else -cost


def calculate_margin_ratio(
    margin_balance: float,
    position_notional: float,
    maintenance_margin_rate: float,
) -> float:
    """margin ratio = 维持保证金 / 保证金余额（>=1 触发爆仓）。

    维持保证金 = position_notional * maintenance_margin_rate。
    margin_balance <= 0 视为已穿仓，返回 inf。
    """
    if position_notional <= 0:
        raise InvalidLeverageRiskInputError(
            "position_notional 必须为正",
            details={"position_notional": position_notional},
        )
    if not 0 <= maintenance_margin_rate < 1:
        raise InvalidLeverageRiskInputError(
            "maintenance_margin_rate 必须在 [0,1) 区间",
            details={"maintenance_margin_rate": maintenance_margin_rate},
        )
    if margin_balance <= 0:
        return math.inf
    maintenance_margin = position_notional * maintenance_margin_rate
    return maintenance_margin / margin_balance


def calculate_distance_to_liquidation(
    mark_price: float,
    liquidation_price: float,
    side: PositionSide = PositionSide.LONG,
) -> float:
    """标记价到爆仓价的相对距离（以标记价为基准，正值=安全）。

    多头: (mark - liq) / mark；空头: (liq - mark) / mark。
    负值表示标记价已越过爆仓价（应已强平）。
    """
    if mark_price <= 0:
        raise InvalidLeverageRiskInputError(
            "mark_price 必须为正",
            details={"mark_price": mark_price},
        )
    if liquidation_price < 0:
        raise InvalidLeverageRiskInputError(
            "liquidation_price 必须 >= 0",
            details={"liquidation_price": liquidation_price},
        )
    if side is PositionSide.LONG:
        return (mark_price - liquidation_price) / mark_price
    return (liquidation_price - mark_price) / mark_price


def assess_leverage_position(
    *,
    side: PositionSide,
    entry_price: float,
    mark_price: float,
    leverage: float,
    position_notional: float,
    margin_balance: float,
    funding_rate: float = 0.0,
    holding_periods: int = 0,
    tiers: Sequence[MaintenanceMarginTier] = DEFAULT_MAINTENANCE_MARGIN_TIERS,
) -> LeverageRiskSnapshot:
    """聚合评估杠杆持仓：爆仓价/维持保证金率/资金费率成本/风险指标快照。

    风险分级（margin_ratio = 维持保证金/保证金余额）：
      >= 1.0      → LIQUIDATED（触及爆仓线）
      >= 0.80     → CRITICAL
      >= 0.50     → WARNING
      其余        → SAFE
    """
    mmr = get_maintenance_margin_rate(position_notional, tiers)
    liq = calculate_liquidation_price(entry_price, leverage, mmr, side)
    margin_ratio = calculate_margin_ratio(margin_balance, position_notional, mmr)
    distance = calculate_distance_to_liquidation(mark_price, liq, side)
    funding_cost = calculate_funding_cost(position_notional, funding_rate, holding_periods, side)

    if margin_ratio >= 1.0:
        risk_level = "LIQUIDATED"
    elif margin_ratio >= MARGIN_RATIO_CRITICAL:
        risk_level = "CRITICAL"
    elif margin_ratio >= MARGIN_RATIO_WARNING:
        risk_level = "WARNING"
    else:
        risk_level = "SAFE"

    snapshot = LeverageRiskSnapshot(
        side=side,
        entry_price=entry_price,
        mark_price=mark_price,
        leverage=leverage,
        position_notional=position_notional,
        maintenance_margin_rate=mmr,
        liquidation_price=liq,
        margin_ratio=margin_ratio,
        distance_to_liquidation=distance,
        funding_cost=funding_cost,
        risk_level=risk_level,
    )
    if risk_level in ("CRITICAL", "LIQUIDATED"):
        _logger.warning(
            "杠杆持仓风险 %s: side=%s notional=%.2f margin_ratio=%.4f liq=%.2f",
            risk_level,
            side.value,
            position_notional,
            margin_ratio,
            liq,
        )
    return snapshot

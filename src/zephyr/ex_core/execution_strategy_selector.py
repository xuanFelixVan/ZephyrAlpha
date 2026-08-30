# [BLUEPRINT] MOD-EX-062 | docs/03_modules/MOD-EX-062/
# [MODULE] zephyr.ex_core.execution_strategy_selector
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.shared.contracts.enums.order_enums; zephyr.shared.foundation.errors
# [CONSUMERS] MOD-EX-014(Order Splitter 消费选定算法) ; MOD-L06-001(TradingSession 执行编排)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 按订单占ADV比例分档:<1%限价直发/1-5%TWAP/5-15%VWAP/>15%拒(StrategySelectionError,须上游拆分,§13.1硬顶); ADV非正/数量非正→Fail-Closed拒判; 可选算法集限{限价直发,TWAP,VWAP}(门禁降级,无IS/Level-2依赖); 纯函数无副作用
# [MODIFY-GUARD] docs/03_modules/MOD-EX-062/
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] StrategySelectionError(ZA-EX-0020)
# [TESTS] tests/ex_core/test_execution_strategy_selector.py
# [A_module] module_id=MOD-EX-062 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Execution Strategy Selector — 执行策略选择器 (MOD-EX-062)

按订单特征选择执行算法（40_execution_broker §决策② 分档表的
门禁降落地，算法集限 EX-014 降级后的 TWAP/VWAP + 限价直发）：

| 订单占 ADV | 策略 | 理由 |
|---|---|---|
| <1% | 限价直发（不拆） | 冲击可忽略，拆单反增成本（每笔最低佣金 5 元） |
| 1-5% | TWAP 等量切片 | 均匀执行，冲击可控 |
| 5-15% | VWAP 量能曲线切片 | 藏于市场自然成交量（日内 20/25/10/45 分布） |
| >15% | 拒绝（StrategySelectionError） | §13.1 硬顶，须上游先拆成 ≤15% ADV 的批次 |

Fail-Closed：ADV 非正 / 数量非正一律拒判（无量能真源不做拍脑袋选择）。
判定核心为纯函数（同输入必同输出，可独立单测）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: features 参数
#   fields: 参数 features，类型注解 OrderFeatures
#   code: execution_strategy_selector.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① select_execution_strategy
#   name_en: select_execution_strategy
#   intro: 按订单特征选执行策略（纯函数：同输入必同输出，可独立单测）。
#   desc: 按订单特征选执行策略（纯函数：同输入必同输出，可独立单测）。 Raises: StrategySelectionError: ADV/数量非正（Fail-Closed），或订单…；源码 L138-L194
#   inputs: features
#   outputs: StrategySelection
#   （注：A1 之后另有 4 个公共定义未列入（含 4 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: StrategySelection
#   name_en: StrategySelection
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-EX-014(Order Splitter 消费选定算法) ; MOD-L06-001(TradingSession 执行编排)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
from typing import Final

from zephyr.shared.contracts.enums.order_enums import OrderSide
from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

__all__: Final = [
    "ExecutionStrategy",
    "OrderFeatures",
    "StrategySelection",
    "StrategySelectionError",
    "select_execution_strategy",
]

#: 分档阈值（40_execution_broker §决策②）
_TINY_FRACTION: Final[Decimal] = Decimal("0.01")  # <1% ADV → 限价直发
_MEDIUM_FRACTION: Final[Decimal] = Decimal("0.05")  # 1-5% ADV → TWAP
_MAX_SINGLE_FRACTION: Final[Decimal] = Decimal("0.15")  # 5-15% → VWAP；>15% 拒（§13.1）

_MAX_SUGGESTED_SLICES: Final[int] = 12


class StrategySelectionError(ZephyrBaseError):
    """执行策略选择失败（输入非法/订单超 ADV 硬顶）。"""

    error_code = "ZA-EX-0020"


class ExecutionStrategy(str, Enum):
    """执行策略（门禁降级后可执行集：限价直发/TWAP/VWAP）。"""

    LIMIT_DIRECT = "limit_direct"
    TWAP = "twap"
    VWAP = "vwap"


@dataclass(frozen=True)
class OrderFeatures:
    """订单特征（选择器输入）。

    Attributes:
        symbol: 标的代码。
        side: 买/卖。
        quantity: 订单数量（股，正数）。
        adv: 日均成交量（股，正数；日线历史量能真源注入）。
    """

    symbol: str
    side: OrderSide
    quantity: Decimal
    adv: Decimal


@dataclass(frozen=True)
class StrategySelection:
    """策略选择结果（frozen；reason 结构化留痕供审计/TCA 归因）。"""

    symbol: str
    strategy: ExecutionStrategy
    adv_fraction: float
    suggested_slices: int  # LIMIT_DIRECT 恒为 1
    reason: str


def _suggest_slices(adv_fraction: Decimal) -> int:
    """切片数建议（确定性经验式：每 1% ADV 一片，2..12 夹边）。"""
    raw = int(adv_fraction * 100)
    return max(2, min(_MAX_SUGGESTED_SLICES, raw))


def select_execution_strategy(features: OrderFeatures) -> StrategySelection:
    """按订单特征选执行策略（纯函数：同输入必同输出，可独立单测）。

    Raises:
        StrategySelectionError: ADV/数量非正（Fail-Closed），或订单
            >15% ADV（§13.1 硬顶，须上游拆分后重入）。
    """
    if features.quantity <= 0:
        raise StrategySelectionError(
            "订单数量必须为正",
            details={"symbol": features.symbol, "quantity": str(features.quantity)},
        )
    if features.adv <= 0:
        raise StrategySelectionError(
            "ADV 必须为正（无日均成交量真源，Fail-Closed 拒判）",
            details={"symbol": features.symbol, "adv": str(features.adv)},
        )

    fraction = features.quantity / features.adv
    if fraction > _MAX_SINGLE_FRACTION:
        raise StrategySelectionError(
            "订单超过 15% ADV 硬顶（§13.1），须上游拆分后重入",
            details={
                "symbol": features.symbol,
                "adv_fraction": str(fraction),
                "max_fraction": str(_MAX_SINGLE_FRACTION),
            },
        )

    if fraction < _TINY_FRACTION:
        strategy = ExecutionStrategy.LIMIT_DIRECT
        slices = 1
        reason = "adv_fraction<1%:冲击可忽略,整单限价直发(拆单反增佣金成本)"
    elif fraction < _MEDIUM_FRACTION:
        strategy = ExecutionStrategy.TWAP
        slices = _suggest_slices(fraction)
        reason = "1%<=adv_fraction<5%:TWAP等量切片,均匀执行冲击可控"
    else:
        strategy = ExecutionStrategy.VWAP
        slices = _suggest_slices(fraction)
        reason = "5%<=adv_fraction<=15%:VWAP按历史量能曲线切片,藏于自然成交量"

    _logger.info(
        "执行策略选择: %s %s fraction=%.4f → %s(%d 片)",
        features.symbol,
        features.side,
        float(fraction),
        strategy.value,
        slices,
    )
    return StrategySelection(
        symbol=features.symbol,
        strategy=strategy,
        adv_fraction=float(fraction),
        suggested_slices=slices,
        reason=reason,
    )

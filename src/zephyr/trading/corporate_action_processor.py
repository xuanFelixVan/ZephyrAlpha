# [BLUEPRINT] MOD-TRADING-004 | docs/03_modules/_domain_trading/corporate_action_processor/blueprint.md
# [MODULE] zephyr.trading.corporate_action_processor
# [DOMAIN] D_TRADING
# [DEPENDENCIES] zephyr.shared.foundation.errors
# [CONSUMERS] zephyr.reporting; zephyr.pf_core
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Decimal-only金额/数量计算; CorporateAction/PositionAdjustment/CorporateActionResult frozen不可变; process纯计算不修改输入; on_adjusted异常不阻断; avg_cost调整后不为负; 调整后总市值不变(除现金分红外)
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidCorporateActionError(ZA-TR-0004)
# [TESTS] tests/trading/test_corporate_action_processor.py
# [A_module] module_id=MOD-TRADING-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""D_TRADING — Corporate Action & Fee Processor (公司行动处理器)

A股公司行动事件处理基础设施。处理除权除息/现金分红/送股/配股/拆股等公司行动
事件, 自动调整持仓数量和均价, 产出 E-TR-03 CorporateActionAdjusted 事件通知
D-PF-CORE 更新组合目标。

费率计算部分(佣金/印花税/过户费)已由 MOD-TRADING-002 PnLCalculator 实现,
本模块聚焦公司行动→持仓调整, 不重复费率逻辑。

设计真源: D:/临时工作区/依赖图/18-D-TRADING-交易运营域.md §1 D-TRADING-03
蓝图: docs/03_modules/_domain_trading/corporate_action_processor/blueprint.md

属 A 类基础设施(确定性数学计算 + 规则驱动), 纯消费层不修改 source 状态。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from typing import Callable

from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)

_ZERO = Decimal("0")


class InvalidCorporateActionError(ZephyrBaseError):
    """公司行动输入非法——负比例/负价格/零持仓/缺少必填参数等。"""

    error_code = "ZA-TR-0004"


# ── 枚举 ──


class CorporateActionType(str, Enum):
    """公司行动类型——5种(A股常见)。"""

    CASH_DIVIDEND = "cash_dividend"  # 现金分红
    STOCK_DIVIDEND = "stock_dividend"  # 送股
    RIGHTS_OFFERING = "rights_offering"  # 配股
    STOCK_SPLIT = "stock_split"  # 拆股/缩股
    EX_RIGHTS = "ex_rights"  # 除权除息(复合)


# ── 数据模型（frozen 不可变）──


@dataclass(frozen=True)
class CorporateAction:
    """公司行动事件——来自交易所公告, 不可变。

    根据 action_type 填充对应字段:
      - CASH_DIVIDEND: dividend_per_share
      - STOCK_DIVIDEND: stock_dividend_ratio (如每10股送3股 → 0.3)
      - RIGHTS_OFFERING: rights_ratio + rights_price
      - STOCK_SPLIT: split_ratio (如1拆2 → 2.0, 2并1 → 0.5)
      - EX_RIGHTS: 上述字段组合
    """

    action_id: str
    symbol: str
    action_type: CorporateActionType
    ex_date: str  # YYYY-MM-DD 除权除息日
    # 现金分红
    dividend_per_share: Decimal | None = None
    # 送股
    stock_dividend_ratio: Decimal | None = None  # 每10股送N股 → N/10
    # 配股
    rights_ratio: Decimal | None = None  # 每10股配M股 → M/10
    rights_price: Decimal | None = None  # 配股价
    # 拆股
    split_ratio: Decimal | None = None  # 1拆K → K


@dataclass(frozen=True)
class PositionAdjustment:
    """持仓调整结果——单次公司行动对单个持仓的调整, 不可变。

    Attributes:
        action_id: 关联的公司行动 ID
        symbol: 标的代码
        action_type: 公司行动类型
        original_quantity: 调整前数量
        original_avg_cost: 调整前均价
        adjusted_quantity: 调整后数量
        adjusted_avg_cost: 调整后均价
        cash_delta: 现金变动(分红为正, 配股出资为负, 送股/拆股为0)
    """

    action_id: str
    symbol: str
    action_type: CorporateActionType
    original_quantity: Decimal
    original_avg_cost: Decimal
    adjusted_quantity: Decimal
    adjusted_avg_cost: Decimal
    cash_delta: Decimal


@dataclass(frozen=True)
class CorporateActionResult:
    """批量公司行动处理结果——不可变。

    Attributes:
        timestamp: 处理时刻
        ex_date: 除权除息日
        adjustments: 调整项元组
        total_cash_delta: 现金变动合计(分红流入 - 配股流出)
    """

    timestamp: datetime
    ex_date: str
    adjustments: tuple[PositionAdjustment, ...]
    total_cash_delta: Decimal


# ── 公司行动处理器主类 ──


class CorporateActionProcessor:
    """公司行动处理器 (D-TRADING-03)——A股公司行动→持仓调整。

    处理除权除息/现金分红/送股/配股/拆股, 自动计算调整后的持仓数量和均价,
    产出 E-TR-03 CorporateActionAdjusted 事件(阶段1用回调模式)。

    Usage:
        processor = CorporateActionProcessor(
            on_adjusted=lambda r: event_bus.publish(r),
        )

        action = CorporateAction(
            action_id="CA001",
            symbol="600000.SH",
            action_type=CorporateActionType.CASH_DIVIDEND,
            ex_date="2026-08-01",
            dividend_per_share=Decimal("0.50"),
        )

        adj = processor.process(action, quantity=Decimal("100"), avg_cost=Decimal("10"))
        # adj.adjusted_avg_cost == Decimal("9.50")
        # adj.cash_delta == Decimal("50.00")

    Thread Safety:
        无共享可变状态(on_adjusted 不可变), process() 线程安全。
    """

    def __init__(
        self,
        on_adjusted: Callable[[CorporateActionResult], None] | None = None,
    ) -> None:
        self._on_adjusted = on_adjusted

    def process(
        self,
        action: CorporateAction,
        quantity: Decimal,
        avg_cost: Decimal,
    ) -> PositionAdjustment:
        """处理单个公司行动, 返回持仓调整结果。

        Args:
            action: 公司行动事件
            quantity: 当前持仓数量
            avg_cost: 当前持仓均价

        Returns:
            PositionAdjustment: 含调整后数量/均价/现金变动

        Raises:
            InvalidCorporateActionError: 输入数据非法
        """
        self._validate(action, quantity, avg_cost)
        atype = action.action_type

        if atype == CorporateActionType.CASH_DIVIDEND:
            adj_qty, adj_cost, cash = self._cash_dividend(
                action, quantity, avg_cost
            )
        elif atype == CorporateActionType.STOCK_DIVIDEND:
            adj_qty, adj_cost, cash = self._stock_dividend(
                action, quantity, avg_cost
            )
        elif atype == CorporateActionType.RIGHTS_OFFERING:
            adj_qty, adj_cost, cash = self._rights_offering(
                action, quantity, avg_cost
            )
        elif atype == CorporateActionType.STOCK_SPLIT:
            adj_qty, adj_cost, cash = self._stock_split(
                action, quantity, avg_cost
            )
        elif atype == CorporateActionType.EX_RIGHTS:
            adj_qty, adj_cost, cash = self._ex_rights(
                action, quantity, avg_cost
            )
        else:
            raise InvalidCorporateActionError(
                f"不支持的公司行动类型: {atype}",
                details={"action_type": atype.value},
            )

        result = PositionAdjustment(
            action_id=action.action_id,
            symbol=action.symbol,
            action_type=atype,
            original_quantity=quantity,
            original_avg_cost=avg_cost,
            adjusted_quantity=adj_qty,
            adjusted_avg_cost=adj_cost,
            cash_delta=cash,
        )

        _logger.info(
            "公司行动处理: action=%s symbol=%s type=%s qty=%s→%s cost=%s→%s cash=%s",
            action.action_id,
            action.symbol,
            atype.value,
            quantity,
            adj_qty,
            avg_cost,
            adj_cost,
            cash,
        )
        return result

    def apply(
        self,
        actions: list[CorporateAction],
        positions: dict[str, tuple[Decimal, Decimal]],
    ) -> CorporateActionResult:
        """批量处理公司行动, 对每个标的的持仓应用对应行动。

        Args:
            actions: 公司行动列表
            positions: symbol -> (quantity, avg_cost) 持仓字典

        Returns:
            CorporateActionResult: 含全部调整项和现金变动合计

        Note:
            - 仅处理 positions 中有持仓的标的的公司行动
            - 同一标的有多个行动时按列表顺序依次应用(前一个的输出是后一个的输入)
            - 有调整时触发 on_adjusted 回调(异常被 catch+log, 不阻断)
        """
        adjustments: list[PositionAdjustment] = []
        total_cash = _ZERO

        # 按标的分组, 保持顺序
        position_state: dict[str, tuple[Decimal, Decimal]] = dict(positions)

        for action in actions:
            pos = position_state.get(action.symbol)
            if pos is None:
                _logger.debug(
                    "公司行动跳过(无持仓): action=%s symbol=%s",
                    action.action_id,
                    action.symbol,
                )
                continue

            qty, cost = pos
            adj = self.process(action, qty, cost)
            adjustments.append(adj)
            total_cash += adj.cash_delta
            # 更新持仓状态供后续行动使用
            position_state[action.symbol] = (
                adj.adjusted_quantity,
                adj.adjusted_avg_cost,
            )

        result = CorporateActionResult(
            timestamp=datetime.now(UTC),
            ex_date=actions[0].ex_date if actions else "",
            adjustments=tuple(adjustments),
            total_cash_delta=total_cash,
        )

        if adjustments and self._on_adjusted is not None:
            try:
                self._on_adjusted(result)
            except Exception:  # noqa: BLE001 — 告警通道故障不阻断处理主流程
                _logger.exception(
                    "on_adjusted 回调异常（已忽略，不影响处理结果）"
                )

        return result

    # ── 各类型处理逻辑 ──

    def _cash_dividend(
        self, action: CorporateAction, qty: Decimal, avg_cost: Decimal
    ) -> tuple[Decimal, Decimal, Decimal]:
        """现金分红: avg_cost 下降, qty 不变, 现金流入。

        avg_cost_new = max(0, avg_cost - dividend_per_share)
        cash_delta = dividend_per_share × quantity
        """
        dps = action.dividend_per_share
        assert dps is not None  # 已在 _validate 中校验
        adj_cost = max(_ZERO, avg_cost - dps)
        cash = dps * qty
        return qty, adj_cost, cash

    def _stock_dividend(
        self, action: CorporateAction, qty: Decimal, avg_cost: Decimal
    ) -> tuple[Decimal, Decimal, Decimal]:
        """送股: qty 增加, avg_cost 下降, 无现金变动。

        qty_new = qty × (1 + ratio)
        avg_cost_new = avg_cost / (1 + ratio)
        """
        ratio = action.stock_dividend_ratio
        assert ratio is not None
        factor = Decimal("1") + ratio
        adj_qty = qty * factor
        adj_cost = avg_cost / factor
        return adj_qty, adj_cost, _ZERO

    def _rights_offering(
        self, action: CorporateAction, qty: Decimal, avg_cost: Decimal
    ) -> tuple[Decimal, Decimal, Decimal]:
        """配股: qty 增加, avg_cost 调整, 现金流出。

        qty_new = qty × (1 + ratio)
        avg_cost_new = (avg_cost + rights_price × ratio) / (1 + ratio)
        cash_delta = -rights_price × qty × ratio  (配股出资)
        """
        ratio = action.rights_ratio
        price = action.rights_price
        assert ratio is not None and price is not None
        factor = Decimal("1") + ratio
        adj_qty = qty * factor
        adj_cost = (avg_cost + price * ratio) / factor
        cash = -(price * qty * ratio)
        return adj_qty, adj_cost, cash

    def _stock_split(
        self, action: CorporateAction, qty: Decimal, avg_cost: Decimal
    ) -> tuple[Decimal, Decimal, Decimal]:
        """拆股/缩股: qty 和 avg_cost 反向调整, 无现金变动。

        qty_new = qty × split_ratio  (>1 拆股, <1 缩股)
        avg_cost_new = avg_cost / split_ratio
        """
        ratio = action.split_ratio
        assert ratio is not None
        adj_qty = qty * ratio
        adj_cost = avg_cost / ratio
        return adj_qty, adj_cost, _ZERO

    def _ex_rights(
        self, action: CorporateAction, qty: Decimal, avg_cost: Decimal
    ) -> tuple[Decimal, Decimal, Decimal]:
        """除权除息(复合): 按顺序应用 现金分红 → 送股 → 配股。

        每个子行动独立计算, 前一个的输出是后一个的输入。
        """
        cur_qty, cur_cost, total_cash = qty, avg_cost, _ZERO

        # 1. 现金分红
        if action.dividend_per_share is not None:
            cur_qty, cur_cost, cash = self._cash_dividend(
                action, cur_qty, cur_cost
            )
            total_cash += cash

        # 2. 送股
        if action.stock_dividend_ratio is not None:
            cur_qty, cur_cost, cash = self._stock_dividend(
                action, cur_qty, cur_cost
            )
            total_cash += cash

        # 3. 配股
        if action.rights_ratio is not None and action.rights_price is not None:
            cur_qty, cur_cost, cash = self._rights_offering(
                action, cur_qty, cur_cost
            )
            total_cash += cash

        # 4. 拆股(与上述互斥, 但允许同时存在)
        if action.split_ratio is not None:
            cur_qty, cur_cost, cash = self._stock_split(
                action, cur_qty, cur_cost
            )
            total_cash += cash

        return cur_qty, cur_cost, total_cash

    # ── 输入校验 ──

    def _validate(
        self, action: CorporateAction, quantity: Decimal, avg_cost: Decimal
    ) -> None:
        """校验公司行动输入和持仓参数。"""
        if not action.action_id:
            raise InvalidCorporateActionError(
                "action_id 不能为空",
                details={"action_id": action.action_id},
            )
        if not action.symbol:
            raise InvalidCorporateActionError(
                "symbol 不能为空",
                details={"symbol": action.symbol},
            )
        if quantity < _ZERO:
            raise InvalidCorporateActionError(
                f"quantity 不能为负, 实际={quantity}",
                details={"quantity": str(quantity)},
            )
        if avg_cost < _ZERO:
            raise InvalidCorporateActionError(
                f"avg_cost 不能为负, 实际={avg_cost}",
                details={"avg_cost": str(avg_cost)},
            )

        atype = action.action_type
        if atype == CorporateActionType.CASH_DIVIDEND:
            if action.dividend_per_share is None or action.dividend_per_share < _ZERO:
                raise InvalidCorporateActionError(
                    "CASH_DIVIDEND 需要 dividend_per_share >= 0",
                    details={"dividend_per_share": str(action.dividend_per_share)},
                )
        elif atype == CorporateActionType.STOCK_DIVIDEND:
            if action.stock_dividend_ratio is None or action.stock_dividend_ratio < _ZERO:
                raise InvalidCorporateActionError(
                    "STOCK_DIVIDEND 需要 stock_dividend_ratio >= 0",
                    details={"stock_dividend_ratio": str(action.stock_dividend_ratio)},
                )
        elif atype == CorporateActionType.RIGHTS_OFFERING:
            if action.rights_ratio is None or action.rights_ratio < _ZERO:
                raise InvalidCorporateActionError(
                    "RIGHTS_OFFERING 需要 rights_ratio >= 0",
                    details={"rights_ratio": str(action.rights_ratio)},
                )
            if action.rights_price is None or action.rights_price < _ZERO:
                raise InvalidCorporateActionError(
                    "RIGHTS_OFFERING 需要 rights_price >= 0",
                    details={"rights_price": str(action.rights_price)},
                )
        elif atype == CorporateActionType.STOCK_SPLIT:
            if action.split_ratio is None or action.split_ratio <= _ZERO:
                raise InvalidCorporateActionError(
                    "STOCK_SPLIT 需要 split_ratio > 0",
                    details={"split_ratio": str(action.split_ratio)},
                )


__all__ = [
    "CorporateAction",
    "CorporateActionProcessor",
    "CorporateActionResult",
    "CorporateActionType",
    "InvalidCorporateActionError",
    "PositionAdjustment",
]

# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.order_manager
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.trading.trading_contracts.broker_interface; zephyr.trading.trading_contracts.execution.fill; zephyr.trading.trading_contracts.execution.order; zephyr.ex_core.cancel_rate_guard; zephyr.compliance.compliance_report_registry
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 先报告后交易（ReportGate BLOCK→拒发）;日申报>=1万笔拒发（Fail-Closed）;门禁未注入不影响既有行为
# [MODIFY-GUARD] 43_compliance_discipline.md §7.4/§8（#ARCH-COMPLIANCE-001 方案A）
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ComplianceGateBlockError(ZA-EX-0011)
# [TESTS]
# [A_module] module_id=MOD-L06-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测

# ---
# domain: ex_core
# category: order_implementation
# status: active
# created: "2026-05-05"
# ---

"""D_EXECUTION_CORE — Order Manager

订单管理器。管理订单全生命周期：创建->风控校验->路由->状态跟踪。

CTR 契约：
  消费者 — CTR-004 (Order) ← D_PORTFOLIO_CORE
  生产者 — CTR-005 (Fill) -> D_REPORTING
  生产者 — CTR-ERR-005 (ExecutionRejectionError) -> D_PORTFOLIO_CORE, D_REPORTING

C-002 执行域合规门禁（2026-08-15 AI-ASM-001 装配批接线，43_compliance_discipline §7.4/§8）：
  submit_order 发送 broker 前两道硬闸（注入即生效，未注入不影响既有行为）：
  1. ReportGate（MOD-CMP-009）：先报告后交易铁律——任一必报项 broker_ack
     缺失 → ComplianceGateBlockError 拒发；
  2. 日申报笔数读数检查（CancelRateGuard 硬计数器）：>=1 万笔 → 拒发；
     >=5000 笔 → WARNING 日志不阻断（2026-06-08 程序化新规）。
  撤单侧接线（2026-08-16 AI-RFIX-001，双轮审查 P1-5）：cancel_order 撤单指令
  发往券商即 record_cancel() 计入日申报硬计数器（成功/失败均计，"申报、撤单
  笔数"同口径）；未注入 declaration_guard 时跳过，不影响既有行为。
  门禁自身失效（登记表不可读等）由各门禁模块 Fail-Closed 兜底（43 号 §7.4）。

SSoT: cross_layer_contracts.yaml -> CTR-004 + CTR-005

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 订单创建/提交/撤单请求
#   fields: symbol/strategy_id/side/order_type/quantity/limit_price/broker_id；order_id
#   code: create_order/submit_order/cancel_order (order_manager.py)
# - id: I2
#   name: 成交回报 Fill（broker 回调）
#   fields: fill_id/order_id/fill_price/filled_quantity/commission
#   code: _on_fill (order_manager.py)
# 层: 算法
# - id: A1
#   name_zh: ① 订单创建
#   name_en: create_order
#   intro: uuid 生成 order_id+idempotency_key，构造 PENDING 订单并登记
#   desc: 构造 Order(PENDING) → _orders/_pending_orders 登记
#   inputs: I1
#   outputs: Order(PENDING)
#   invariant: Decimal 数量全程；idempotency_key 唯一
# - id: A2
#   name_zh: ② 合规门禁+提交
#   name_en: submit_order → _check_compliance_gates
#   intro: C-002 双硬闸（ReportGate 先报告后交易 / 日申报笔数超限）Fail-Closed 后状态机转 SUBMITTED 并发 broker
#   desc: 门禁 BLOCK→ComplianceGateBlockError；过闸→_transition_status(SUBMITTED)→记 _order_broker_map→broker.submit_order
#   inputs: I1
#   outputs: broker_order_id
#   invariant: 先报告后交易；日申报>=1万笔拒发
# - id: A3
#   name_zh: ③ 撤单精确路由
#   name_en: cancel_order → _cancel_at_broker
#   intro: 按 _order_broker_map 精确路由到所属 broker 撤单，券商失败不标本地终态
#   desc: 状态机校验→计 record_cancel（申报口径）→broker.cancel_order 透传布尔→成功才转 CANCELLED
#   inputs: I1
#   outputs: bool
#   invariant: 券商撤单结果不吞（False 不误判成功）
# - id: A4
#   name_zh: ④ 成交累积与状态驱动
#   name_en: _on_fill
#   intro: 成交量累积+加权均价重算，达标驱动 SUBMITTED→PARTIAL→FILLED
#   desc: filled+=qty → avg 加权 → filled>=quantity 转 FILLED（非法转换仅告警）；回调通知异常不阻断
#   inputs: I2
#   outputs: Order 就地更新 + fill 回调
#   invariant: 状态转换遵循 VALID_TRANSITIONS
# 层: 输出
# - id: O1
#   name_zh: 订单全生命周期状态
#   name_en: Order / list[Order] / list[Fill]
#   intro: 按 ID/状态/开放单查询与成交记录，供 TradingSession/Saga 消费
#   downstream: ex_core.trading_session / ex_core.order_execution_saga
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# I2 --> A4
# A2 --> O1
# A3 --> O1
# A4 --> O1
"""

from __future__ import annotations

import logging
import uuid
from collections import defaultdict
from collections.abc import Callable
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from typing import Final

from zephyr.compliance.compliance_report_registry import ReportGate, ReportGateDecision
from zephyr.ex_core.cancel_rate_guard import CancelRateGuard, DailyDeclarationStatus
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderStatus, OrderType
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.order import Order
from zephyr.shared.foundation.errors import ZephyrBaseError
from zephyr.trading.trading_contracts.broker_interface import BrokerInterface

_logger = logging.getLogger(__name__)


class ComplianceGateBlockError(ZephyrBaseError):
    """C-002 合规门禁阻断——先报告后交易 / 日申报笔数超限拒发订单。"""

    error_code = "ZA-EX-0011"


class OrderAction(Enum):
    def __str__(self) -> str:
        # 5.92.2 修复：统一日志格式，返回 value 而非 ClassName.MEMBER
        return self.value

    SUBMIT = "submit"
    CANCEL = "cancel"
    MODIFY = "modify"


class RejectionAction(Enum):
    """拒单处理动作（40_execution_broker §2.7 层3）。

    原则：涨跌停/资金/持仓类不重试（重试无意义），价格/连接类重试1次（可恢复）。
    宁可放弃不可盲目重试，避免撤单率超标（BM-EXE-04 撤单率≤15%）。
    """

    def __str__(self) -> str:
        return self.value

    ABANDON = "abandon"  # 涨跌停/数量不合法：放弃不重试
    RETRY_ONCE = "retry_once"  # 价格/连接：重试1次
    ALERT_FREEZE = "alert_freeze"  # 资金不足：告警+冻结策略新开仓
    ALERT_RECONCILE = "alert_reconcile"  # 持仓不足：告警+持仓对账
    IDEMPOTENT_RETURN = "idempotent_return"  # 订单号重复：返回已存在id


# xttrader 错误码 → 拒单处理动作映射（与 miniqmt_broker.XTTRADER_ERROR_CODES 对齐）
_REJECTION_ACTIONS: Final[dict[int, RejectionAction]] = {
    50: RejectionAction.ABANDON,  # 涨停
    51: RejectionAction.ABANDON,  # 跌停
    52: RejectionAction.ABANDON,  # 数量不合法（代码bug，告警）
    53: RejectionAction.RETRY_ONCE,  # 价格不合法（涨跌停边界1分钱误差，修正后重试）
    54: RejectionAction.ALERT_FREEZE,  # 资金不足（账户级，重试不会变有钱）
    55: RejectionAction.ALERT_RECONCILE,  # 持仓不足（T+1锁定或持仓不一致，需对账）
    -1: RejectionAction.RETRY_ONCE,  # 连接失败（重连后重试）
    -2: RejectionAction.RETRY_ONCE,  # 未就绪（重连后重试）
    -3: RejectionAction.IDEMPOTENT_RETURN,  # 订单号重复（幂等：返回已存在id）
}


class OrderManager:
    """订单管理器——订单生命周期状态机驱动"""

    VALID_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
        OrderStatus.PENDING: {OrderStatus.SUBMITTED, OrderStatus.CANCELLED, OrderStatus.EXPIRED},
        OrderStatus.SUBMITTED: {
            OrderStatus.PARTIAL,
            OrderStatus.FILLED,
            OrderStatus.CANCELLED,
            OrderStatus.REJECTED,
            OrderStatus.EXPIRED,
        },
        OrderStatus.PARTIAL: {OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED, OrderStatus.EXPIRED},
        OrderStatus.FILLED: set(),
        OrderStatus.CANCELLED: set(),
        OrderStatus.REJECTED: set(),
        OrderStatus.EXPIRED: set(),
    }

    def __init__(
        self,
        brokers: dict[str, BrokerInterface] | None = None,
        report_gate: ReportGate | None = None,
        declaration_guard: CancelRateGuard | None = None,
    ):
        self._brokers = brokers or {}
        self._orders: dict[str, Order] = {}
        self._fills: dict[str, list[Fill]] = defaultdict(list)
        self._fill_callbacks: list[Callable[[Fill], None]] = []
        self._order_callbacks: list[Callable[[Order], None]] = []
        self._pending_orders: list[Order] = []
        # order_id -> broker_id 映射（cancel_order 治本：消除硬编码 "simulation" + 反查逻辑）
        self._order_broker_map: dict[str, str] = {}
        # C-002 合规门禁（43 号 §7.4/§8，AI-ASM-001 装配批接线；None=未接线不校验）
        self._report_gate = report_gate
        self._declaration_guard = declaration_guard

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def fill_callbacks(self) -> list[Callable[[Fill], None]]:
        """只读：fill_callbacks（Stage 4 公共化）。"""
        return self._fill_callbacks

    @fill_callbacks.setter
    def fill_callbacks(self, value):
        """写入：fill_callbacks（Stage 4 公共化）。"""
        self._fill_callbacks = value

    @property
    def orders(self) -> dict[str, Order]:
        """只读：orders（Stage 4 公共化）。"""
        return self._orders

    @orders.setter
    def orders(self, value):
        """写入：orders（Stage 4 公共化）。"""
        self._orders = value

    @property
    def declaration_guard(self) -> CancelRateGuard | None:
        """只读：日申报硬计数器（AI-R3 复审 P1：供装配层校验同实例注入，
        防 TradingSession 与 OrderManager 各持独立计数器分裂计数）。"""
        return self._declaration_guard

    def register_broker(self, broker_id: str, broker: BrokerInterface) -> None:
        self._brokers[broker_id] = broker
        broker.register_fill_callback(self._on_fill)
        _logger.info("Broker registered: broker_id=%s", broker_id)

    def register_fill_callback(self, callback: Callable[[Fill], None]) -> None:
        self._fill_callbacks.append(callback)

    def create_order(
        self,
        symbol: str,
        strategy_id: str,
        side: OrderSide,
        order_type: OrderType,
        quantity: Decimal,
        limit_price: Decimal | None = None,
        broker_id: str = "simulation",
    ) -> Order:
        order_id = str(uuid.uuid4())
        order = Order(
            order_id=order_id,
            symbol=symbol,
            strategy_id=strategy_id,
            side=side,
            order_type=order_type,
            quantity=quantity,
            limit_price=limit_price,
            status=OrderStatus.PENDING,
            created_at=datetime.now(UTC),
            broker_order_id=None,
            idempotency_key=str(uuid.uuid4()),
        )
        self._orders[order_id] = order
        self._pending_orders.append(order)
        _logger.info("Order created: order_id=%s symbol=%s side=%s qty=%s", order_id, symbol, side, quantity)
        return order

    def _transition_status(self, order: Order, new_status: OrderStatus) -> None:
        """状态机校验并转换订单状态

        基于 VALID_TRANSITIONS 校验状态转换合法性，违规抛 ValueError。

        Args:
            order: 订单对象
            new_status: 目标状态

        Raises:
            ValueError: 非法状态转换
        """
        allowed = self.VALID_TRANSITIONS.get(order.status, set())
        if new_status not in allowed:
            raise ValueError(f"非法状态转换: {order.status} -> {new_status} (order_id={order.order_id})")
        order.status = new_status
        order.updated_at = datetime.now(UTC)

    @staticmethod
    def classify_rejection(error_code: int) -> RejectionAction:
        """拒单分类——根据 xttrader error_code 决定处理动作。

        涨跌停/资金/持仓类不重试（重试无意义），价格/连接类重试1次（可恢复）。
        未知错误码保守按 ABANDON 处理。详见 40_execution_broker §2.7。
        """
        return _REJECTION_ACTIONS.get(error_code, RejectionAction.ABANDON)

    def submit_order(self, order_id: str, broker_id: str = "simulation") -> str:
        order = self._orders.get(order_id)
        if not order:
            raise ValueError(f"Order not found: {order_id}")

        broker = self._brokers.get(broker_id)
        if not broker:
            raise ValueError(f"Broker not found: {broker_id}")

        # ── C-002 合规门禁（43 号 §7.4/§8）：发送 broker 前 Fail-Closed 硬闸 ──
        self._check_compliance_gates(order)

        self._transition_status(order, OrderStatus.SUBMITTED)
        # 记录 order->broker 映射，供 cancel_order 治本使用（消除硬编码+反查）
        self._order_broker_map[order_id] = broker_id

        broker_order_id = broker.submit_order(order)
        order.broker_order_id = broker_order_id
        order.updated_at = datetime.now(UTC)

        return broker_order_id

    def _check_compliance_gates(self, order: Order) -> None:
        """C-002 执行域合规门禁（AI-ASM-001 装配批接线）。

        两道硬闸（注入即生效，None=未接线跳过）：
        1. ReportGate 先报告后交易（43 号 §7.4 铁律）：任一必报项 broker_ack
           缺失 → BLOCK → ComplianceGateBlockError 拒发；
        2. 日申报笔数读数检查（43 号 §8 方案 A）：>=1 万笔拒发；>=5000 笔
           WARNING 不阻断。
        """
        if self._report_gate is not None:
            gate_result = self._report_gate.check()
            if gate_result.decision is ReportGateDecision.BLOCK:
                _logger.error(
                    "C-002 拒单[先报告后交易]: order_id=%s missing=%s detail=%s",
                    order.order_id,
                    gate_result.missing,
                    gate_result.detail,
                )
                raise ComplianceGateBlockError(
                    f"先报告后交易铁律：{gate_result.detail} (order_id={order.order_id})"
                )
        if self._declaration_guard is not None:
            status = self._declaration_guard.daily_declaration_status
            count = self._declaration_guard.daily_declaration_count
            if status is DailyDeclarationStatus.BLOCKED:
                _logger.error(
                    "C-002 拒单[日申报笔数超限]: order_id=%s count=%d >= %d（1 万笔限交易）",
                    order.order_id,
                    count,
                    self._declaration_guard.daily_block_threshold,
                )
                raise ComplianceGateBlockError(
                    f"日申报笔数 {count} 笔已达 {self._declaration_guard.daily_block_threshold}"
                    f" 笔限交易线，拒绝新申报 (order_id={order.order_id})"
                )
            if status is DailyDeclarationStatus.WARNING:
                _logger.warning(
                    "C-002 日申报笔数预警: count=%d >= %d（5000 笔预警线，不阻断）",
                    count,
                    self._declaration_guard.daily_warn_threshold,
                )

    def cancel_order(self, order_id: str) -> bool:
        """撤单——同时通知券商端撤销

        治本修复: 通过 _order_broker_map 精确路由到订单所属 broker，
        消除原硬编码 "simulation" + 遍历反查逻辑（第二决策点）。

        Args:
            order_id: 订单ID

        Returns:
            True = 撤单成功（本地+券商端均成功）
        """
        order = self._orders.get(order_id)
        if not order:
            return False

        # 状态机校验
        if order.status not in {OrderStatus.PENDING, OrderStatus.SUBMITTED, OrderStatus.PARTIAL}:
            return False

        # 撤单计数接线（2026-08-16 双轮审查 P1-5 裁定，AI-RFIX-001）：撤单指令
        # 发往券商即构成一笔撤单申报（2026-06-08 程序化新规"申报、撤单笔数"口径，
        # 43 号 §8 方案 A 日申报硬计数器）——成功/失败均计入（宁可多计不可漏计，
        # 失败=指令已发出但被拒，仍消耗申报口径）；无 broker_order_id 的纯本地
        # 撤单（未报交易所）不计
        if order.broker_order_id and self._declaration_guard is not None:
            self._declaration_guard.record_cancel()

        # 从映射精确路由到所属 broker（治本：消除硬编码 "simulation" + 反查）
        if order.broker_order_id and not self._cancel_at_broker(order_id, order):
            return False

        self._transition_status(order, OrderStatus.CANCELLED)
        _logger.info("Order cancelled: order_id=%s", order_id)
        return True

    def _cancel_at_broker(self, order_id: str, order: Order) -> bool:
        """通知券商端撤单（从 _order_broker_map 精确路由）

        Args:
            order_id: 订单ID
            order: 订单对象

        Returns:
            True = 券商端撤单成功（或无需撤单）；False = 撤单失败
        """
        broker_id = self._order_broker_map.get(order_id)
        if not broker_id:
            _logger.warning("撤单路由失败：order_id=%s 无 broker_id 映射记录", order_id)
            return False

        broker = self._brokers.get(broker_id)
        if broker is None:
            _logger.error("撤单路由失败：broker_id=%s 未注册 (order_id=%s)", broker_id, order_id)
            return False

        try:
            # 透传券商端撤单布尔结果（#ARCH-100：原实现吞掉 False——券商拒绝撤单
            # （如已成交）被误判为撤单成功，Saga 超时分支无法感知真实终态）
            return bool(broker.cancel_order(order.broker_order_id))
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            _logger.error(
                "券商端撤单失败: order_id=%s broker_order_id=%s broker_id=%s error=%s",
                order_id,
                order.broker_order_id,
                broker_id,
                e,
                exc_info=True,
            )
            return False

    def get_order(self, order_id: str) -> Order | None:
        return self._orders.get(order_id)

    def get_orders_by_status(self, status: OrderStatus) -> list[Order]:
        return [o for o in self._orders.values() if o.status == status]

    def get_open_orders(self) -> list[Order]:
        return [
            o
            for o in self._orders.values()
            if o.status in {OrderStatus.PENDING, OrderStatus.SUBMITTED, OrderStatus.PARTIAL}
        ]

    def get_fills_for_order(self, order_id: str) -> list[Fill]:
        return self._fills.get(order_id, [])

    def get_all_fills(self) -> list[Fill]:
        return [f for fills in self._fills.values() for f in fills]

    def _on_fill(self, fill: Fill) -> None:
        self._fills[fill.order_id].append(fill)

        order = self._orders.get(fill.order_id)
        if order:
            order.filled_quantity = (order.filled_quantity or Decimal("0")) + fill.filled_quantity
            order.avg_fill_price = (
                (
                    (order.avg_fill_price or Decimal("0")) * (order.filled_quantity - fill.filled_quantity)
                    + fill.fill_price * fill.filled_quantity
                )
                / order.filled_quantity
                if order.filled_quantity > 0
                else fill.fill_price
            )
            order.updated_at = datetime.now(UTC)

            if order.filled_quantity >= order.quantity:
                try:
                    self._transition_status(order, OrderStatus.FILLED)
                except ValueError as e:
                    _logger.warning("成交回调状态转换跳过: %s", e)
            elif order.filled_quantity > 0:
                try:
                    self._transition_status(order, OrderStatus.PARTIAL)
                except ValueError as e:
                    _logger.warning("成交回调状态转换跳过: %s", e)

        for callback in self._fill_callbacks:
            try:
                callback(fill)
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                _logger.error("Fill callback error: %s", e, exc_info=True)

    @property
    def order_count(self) -> int:
        return len(self._orders)

    @property
    def fill_count(self) -> int:
        return sum(len(fills) for fills in self._fills.values())


__all__: Final = ["OrderAction", "RejectionAction", "OrderManager"]

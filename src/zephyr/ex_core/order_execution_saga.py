# [BLUEPRINT] MOD-EX-057 | docs/03_modules/_domain_execution_core/order_execution_saga/blueprint.md
# [MODULE] zephyr.ex_core.order_execution_saga
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.order_manager; zephyr.ex_core.position_tracker.tracker; zephyr.ex_core.audit_journal.auditor; zephyr.ex_core.rejection_action_handler; zephyr.governance.adapters.risk_validation_bridge; zephyr.shared.contracts.order; zephyr.shared.contracts.fill; zephyr.shared.contracts.enums.order_enums; zephyr.shared.contracts.risk_limits
# [CONSUMERS] D-PORTFOLIO(TradingSession可调用); D-EX-CORE(ExecutionEngine可调用)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 六步严格顺序;补偿幂等;≤5s超时;每步审计不可跳过;SagaResult frozen不可变;execute同步阻塞;超时撤单失败强制查询订单终态(已成交补走step5/6不吞掉);拒单分类动作经注入RejectionActionExecutor执行(未注入=仅日志,Saga不自动重试下单)
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] SagaTimeoutError;SagaCompensationError
# [TESTS] tests/ex_core/test_order_execution_saga.py
# [A_module] module_id=MOD-EX-057 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""

Order Execution Saga — 下单执行 Saga 编排器 (MOD-EX-057 / D-EX-CORE-57)

D_EXECUTION_CORE 域事务编排基础设施: 将单笔订单的执行封装为六步 Saga 事务,
任何一步失败自动补偿回滚, 保证系统不会处于"半完成"的不一致状态。

六步流程 (设计真源 §13):
    1. 风控检查    → risk_validator.validate_order()
    2. 信号确认    → signal_confirmer(order) (可选)
    3. 下单提交    → order_manager.create_order() + submit_order()
    4. 成交确认    → 等待 Fill 回调 (Event + timeout)
    5. 持仓更新    → position_tracker.apply_fill(fill, side)
    6. 报告生成    → audit_logger.log_order_filled() 等

补偿规则:
    - 步骤3失败 → 撤单 (cancel_order, 幂等: 已成交则忽略)
    - 步骤5失败 → 持仓回滚 (反向 apply_fill, 幂等: 覆盖)
    - 步骤4超时 → 撤单 (步骤3补偿)；撤单返回 False 强制查询订单终态——
      已成交补走 step5/6（裁定书 §三 P0-2 修复，#ARCH-100：超时分支吞成交
      会导致持仓账本与券商漂移），无法确认终态则 critical 告警需人工对账

纯基础设施: 不决定"买什么/何时买/买多少", 只负责"按顺序执行六步, 失败就补偿回滚"。

SSoT: depgraph MOD-EX-057
设计真源: D-EX-CORE-57 §13
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 订单 Order + 买卖方向 side
#   fields: order(symbol/quantity/limit_price/order_type/strategy_id) + OrderSide
#   code: execute(order, side) L347
# - id: I2
#   name: 当前持仓快照 + 风控限额 RiskLimits
#   fields: holdings + cash + total_market_value + max_single_position(0.10) + max_gross_leverage(1.0)
#   code: _step1_risk_check L444-465；_default_risk_limits L334-343
# - id: I3
#   name: 成交回报 Fill 回调流
#   fields: fill(fill_id/fill_price/filled_quantity/commission)，由 OrderManager fill callback 推送
#   code: _FillCollector L192-219；_step4_fill_confirm L568
# 层: 算法
# - id: A1
#   name_zh: ① 六步Saga主编排
#   name_en: OrderExecutionSaga._run_saga
#   intro: 把单笔订单执行封装成风控→信号→下单→成交→持仓→报告六步事务，失败自动补偿
#   desc: 严格顺序调 step1~step6；任一步失败即返回；成交超时进 TIMEOUT 并触发撤单补偿；异常时按状态补偿；finally 清理 fill callback
#   inputs: I1
#   outputs: SagaResult（不可变）
#   invariant: 六步严格顺序；≤5s超时；execute同步阻塞；每步审计不可跳过
# - id: A2
#   name_zh: ② 步骤1风控检查
#   name_en: _step1_risk_check
#   intro: 用当前持仓估算目标权重，调风控端口校验，HALT级违规直接拒单
#   desc: target_weight=qty×limit_price/total_nav → risk_validator.validate_order → 有HALT违规则 RISK_REJECTED 写审计，否则 RISK_PASSED
#   inputs: I2 A1
#   outputs: RISK_PASSED / RISK_REJECTED
# - id: A3
#   name_zh: ③ 步骤3下单提交+步骤4成交确认
#   name_en: _step3_order_submit / _step4_fill_confirm
#   intro: 注册fill收集器防竞态后提交订单，阻塞等成交回报直到超时
#   desc: 未注册订单先 create_order → submit前注册 _FillCollector(threading.Event) → submit_order → Event.wait(remaining_timeout) 等首个匹配 fill
#   inputs: I3 A2
#   outputs: ORDER_SUBMITTED + Fill / 超时None
# - id: A4
#   name_zh: ④ 步骤5持仓更新+步骤6报告
#   name_en: _step5_position_update / _step6_report
#   intro: 成交落地到持仓跟踪器并写审计，最后标记订单FILLED
#   desc: position_tracker.apply_fill(fill, side) → 写 ORDER_FILLED 审计 → best-effort 标记订单 FILLED（失败不阻断）
#   inputs: A3
#   outputs: POSITION_UPDATED / COMPLETED
# - id: A5
#   name_zh: ⑤ 补偿回滚
#   name_en: _compensate_order / _compensate_position
#   intro: 撤单或反向apply_fill回滚持仓，幂等不重复补偿
#   desc: 订单处于PENDING/SUBMITTED/PARTIAL才撤单（已成交忽略）；持仓回滚构造rollback-Fill反方向apply_fill（佣金为0）
#   inputs: A3 A4
#   outputs: COMPENSATED 状态
#   invariant: 补偿幂等（已成交撤单忽略；回滚覆盖式）
# 层: 输出
# - id: O1
#   name_zh: Saga执行结果 SagaResult
#   name_en: SagaResult
#   intro: 含最终状态/已完成步骤/成交/错误/是否补偿/耗时的不可变结果
#   invariant: frozen 不可变
#   downstream: D-PORTFOLIO（TradingSession可调用）；D-EX-CORE（ExecutionEngine可调用）
# - id: O2
#   name_zh: 执行审计事件流
#   name_en: ExecutionAuditLogger.log
#   intro: 每步向审计记录器写 ORDER_CREATED/SUBMITTED/FILLED/CANCELLED/EXPIRED 事件
#   downstream: 审计记录器 MOD-EX-003
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A2
# I3 --> A3
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A3 --> A5
# A4 --> A5
# A4 --> O1
# A5 --> O1
# A1 --> O2
"""

from __future__ import annotations

import logging
import math
import threading
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum
from typing import Final

from zephyr.ex_core.audit_journal.auditor import (
    AuditSource,
    ExecutionAuditEventType,
    ExecutionAuditLogger,
)
from zephyr.ex_core.order_manager import OrderManager, RejectionAction
from zephyr.ex_core.position_tracker.tracker import PositionTracker
from zephyr.ex_core.rejection_action_handler import (
    RejectionActionExecutor,
    RejectionActionResult,
)
from zephyr.governance.adapters.risk_validation_bridge import (
    RiskValidationPort,
    RiskViolation,
)
from zephyr.shared.contracts.enums.order_enums import OrderSide, OrderStatus, OrderType
from zephyr.shared.contracts.fill import Fill
from zephyr.shared.contracts.order import Order
from zephyr.shared.contracts.risk_limits import RiskLimits

try:
    from zephyr.trading.trading_contracts.broker_interface import BrokerInterface
except ImportError:
    # broker_interface 可能在某些环境不可用, 用 Protocol 兜底
    from typing import Protocol

    class BrokerInterface(Protocol):  # type: ignore[no-redef]
        def submit_order(self, order: Order) -> str: ...
        def cancel_order(self, broker_order_id: str) -> bool: ...
        def register_fill_callback(self, callback: Callable[[Fill], None]) -> None: ...
        def get_positions(self) -> object: ...
        def connect(self) -> None: ...
        def disconnect(self) -> None: ...


_logger = logging.getLogger(__name__)

__all__: Final = [
    "SagaState",
    "SagaResult",
    "SagaConfig",
    "OrderExecutionSaga",
    "SagaTimeoutError",
    "SagaCompensationError",
]


# ──────────────────────────────────────────────────────────────────────────────
# 错误
# ──────────────────────────────────────────────────────────────────────────────


class SagaTimeoutError(Exception):
    """Saga 执行超时。"""


class SagaCompensationError(Exception):
    """Saga 补偿操作失败。"""


class _CancelOutcome(str, Enum):
    """撤单补偿结果（内部，供超时分支决定是否强制查询订单终态）。"""

    CANCELLED = "CANCELLED"  # 撤单成功
    NOT_NEEDED = "NOT_NEEDED"  # 订单已终态，无需补偿
    FAILED = "FAILED"  # 撤单失败/异常（可能已成交，需强制查询终态）


# ──────────────────────────────────────────────────────────────────────────────
# 状态机
# ──────────────────────────────────────────────────────────────────────────────


class SagaState(str, Enum):
    """Saga 状态机——六步编排 + 失败/补偿状态。"""

    INIT = "INIT"
    RISK_PASSED = "RISK_PASSED"
    SIGNAL_CONFIRMED = "SIGNAL_CONFIRMED"
    ORDER_SUBMITTED = "ORDER_SUBMITTED"
    FILL_RECEIVED = "FILL_RECEIVED"
    POSITION_UPDATED = "POSITION_UPDATED"
    COMPLETED = "COMPLETED"
    # 失败/补偿状态
    RISK_REJECTED = "RISK_REJECTED"
    SIGNAL_INVALID = "SIGNAL_INVALID"
    ORDER_REJECTED = "ORDER_REJECTED"
    TIMEOUT = "TIMEOUT"
    COMPENSATED = "COMPENSATED"


# ──────────────────────────────────────────────────────────────────────────────
# 数据模型
# ──────────────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class SagaResult:
    """单笔 Saga 执行结果（不可变）。

    Attributes:
        saga_id: UUID, 唯一标识
        order_id: 订单ID
        symbol: 标的代码
        side: 买卖方向 (OrderSide.value)
        state: 最终 Saga 状态
        steps_completed: 已完成的步骤名列表
        fill: 成交回报 (None=未成交)
        error: 错误信息 (None=无错误)
        compensated: 是否执行了补偿
        started_at: 开始时间
        completed_at: 完成时间
        duration_ms: 总耗时(毫秒)
    """

    saga_id: str
    order_id: str
    symbol: str
    side: str
    state: SagaState
    steps_completed: tuple[str, ...]
    fill: Fill | None
    error: str | None
    compensated: bool
    started_at: datetime
    completed_at: datetime
    duration_ms: float


@dataclass
class SagaConfig:
    """Saga 配置。

    Attributes:
        timeout_seconds: 总 Saga 超时(秒), 默认 5.0 (设计约束 ≤5s)
        fill_poll_interval: 成交确认轮询间隔(秒), 仅影响 Event.wait 精度
        broker_id: OrderManager 中注册的 broker_id
    """

    timeout_seconds: float = 5.0
    fill_poll_interval: float = 0.05
    broker_id: str = "simulation"

    def __post_init__(self) -> None:
        if not math.isfinite(self.timeout_seconds) or self.timeout_seconds <= 0:
            raise ValueError(f"timeout_seconds 必须为正有限数，got {self.timeout_seconds}")
        if self.timeout_seconds > 5.0:
            raise ValueError(f"timeout_seconds 违反 ≤5s 契约，got {self.timeout_seconds}")


# ──────────────────────────────────────────────────────────────────────────────
# 内部: Fill 收集器 (线程安全, 一次性)
# ──────────────────────────────────────────────────────────────────────────────


class _FillCollector:
    """收集指定 order_id 的 Fill（线程安全，一次性）。

    注册为 OrderManager 的 fill callback，当指定 order_id 的 fill 到达时
    自动捕获并设置 Event。用于 Saga 步骤4（成交确认）的同步等待。
    """

    def __init__(self, order_id: str, order_quantity: Decimal | None = None) -> None:
        self._order_id = order_id
        self._order_quantity = order_quantity
        self._event = threading.Event()
        self._fill: Fill | None = None

    def __call__(self, fill: Fill) -> None:
        """fill callback 入口——匹配 order_id + 数值校验，非法 fill 拒收。"""
        if fill.order_id != self._order_id or self._event.is_set():
            return
        # 红队防御：非法 fill 拒收（不 set event，让 saga 走超时补偿链）
        if fill.filled_quantity <= 0:
            _logger.warning("拒收非法 fill: qty=%s <= 0 (order=%s)", fill.filled_quantity, self._order_id)
            return
        if self._order_quantity is not None and fill.filled_quantity > self._order_quantity:
            _logger.warning(
                "拒收非法 fill: qty=%s > order_qty=%s (order=%s)",
                fill.filled_quantity,
                self._order_quantity,
                self._order_id,
            )
            return
        if fill.fill_price is not None and (fill.fill_price.is_nan() or fill.fill_price <= 0):
            _logger.warning("拒收非法 fill: price=%s (order=%s)", fill.fill_price, self._order_id)
            return
        self._fill = fill
        self._event.set()

    def wait(self, timeout: float) -> Fill | None:
        """等待 fill 到达（阻塞至 timeout 或 fill 到达）。"""
        if self._event.wait(timeout=timeout):
            return self._fill
        return None

    @property
    def collected(self) -> bool:
        """是否已收到 fill。"""
        return self._event.is_set()


# ──────────────────────────────────────────────────────────────────────────────
# 内部: Saga 执行上下文
# ──────────────────────────────────────────────────────────────────────────────


@dataclass
class _SagaContext:
    """单笔 Saga 执行的内部上下文（可变，仅在 execute() 内使用）。"""

    saga_id: str
    order: Order
    side: OrderSide
    state: SagaState = SagaState.INIT
    steps_completed: list[str] = field(default_factory=list)
    fill: Fill | None = None
    error: str | None = None
    compensated: bool = False
    start_time: float = 0.0  # time.monotonic()
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    collector: _FillCollector | None = None  # step3 注册, execute() finally 清理

    def remaining_timeout(self, config: SagaConfig) -> float:
        """剩余超时秒数。"""
        elapsed = time.monotonic() - self.start_time
        return max(0.0, config.timeout_seconds - elapsed)

    def mark_step(self, step: str) -> None:
        """标记步骤完成。"""
        self.steps_completed.append(step)

    def to_result(self) -> SagaResult:
        """转换为不可变 SagaResult。"""
        completed_at = datetime.now(UTC)
        duration_ms = (time.monotonic() - self.start_time) * 1000.0
        return SagaResult(
            saga_id=self.saga_id,
            order_id=self.order.order_id,
            symbol=self.order.symbol,
            side=self.side.value,
            state=self.state,
            steps_completed=tuple(self.steps_completed),
            fill=self.fill,
            error=self.error,
            compensated=self.compensated,
            started_at=self.started_at,
            completed_at=completed_at,
            duration_ms=duration_ms,
        )


# ──────────────────────────────────────────────────────────────────────────────
# 下单执行 Saga 编排器
# ──────────────────────────────────────────────────────────────────────────────


class OrderExecutionSaga:
    """下单执行 Saga 编排器 — 六步编排 + 补偿 + 超时。

    用法:
        saga = OrderExecutionSaga(
            order_manager=om,
            risk_validator=bridge,
            position_tracker=tracker,
            audit_logger=audit,
            broker=broker,
            broker_id="simulation",
        )

        # 执行单笔订单 (同步阻塞, ≤5s)
        result = saga.execute(order, OrderSide.BUY)

        if result.state == SagaState.COMPLETED:
            print(f"成交: {result.fill}")
        elif result.compensated:
            print(f"已补偿: {result.error}")
    """

    def __init__(
        self,
        order_manager: OrderManager,
        risk_validator: RiskValidationPort,
        position_tracker: PositionTracker,
        audit_logger: ExecutionAuditLogger,
        broker: BrokerInterface,
        broker_id: str = "simulation",
        risk_limits: RiskLimits | None = None,
        config: SagaConfig | None = None,
        signal_confirmer: Callable[[Order], bool] | None = None,
        rejection_executor: RejectionActionExecutor | None = None,
    ) -> None:
        """初始化 Saga 编排器。

        Args:
            order_manager: 订单管理器（创建/提交/撤单）
            risk_validator: 风控校验端口
            position_tracker: 持仓跟踪器（更新/回滚）
            audit_logger: 执行审计记录器（哈希链审计）
            broker: 券商接口（fill 回调源）
            broker_id: OrderManager 中注册的 broker_id
            risk_limits: 风控限额（None=用默认）
            config: Saga 配置（None=默认 5s 超时）
            signal_confirmer: 信号确认回调（None=跳过步骤2）
            rejection_executor: 拒单分类动作执行器（40 号 §6.1 gap 4 Saga 接管）。
                None=未接管，拒单仅审计留痕（既有 MVP 行为）。注入后步骤3
                下单被拒时按 40 号 §2.7 分类执行实际动作（RETRY_ONCE/
                ALERT_FREEZE/ALERT_RECONCILE）；Saga 不自带 retry_fn——
                修正价格重试需装配层注入定价策略，未接线时执行器降级放弃
                （Fail-Closed 不盲目重试）。
        """
        self._order_manager = order_manager
        self._risk_validator = risk_validator
        self._position_tracker = position_tracker
        self._audit = audit_logger
        self._broker = broker
        self._config = config or SagaConfig(broker_id=broker_id)
        self._config.broker_id = broker_id
        self._risk_limits = risk_limits or self._default_risk_limits()
        self._signal_confirmer = signal_confirmer
        self._rejection_executor = rejection_executor

    @staticmethod
    def _default_risk_limits() -> RiskLimits:
        """默认风控限额（A 股多头：单标的 10%、杠杆 1.0）。"""
        now = datetime.now(UTC)
        return RiskLimits(
            as_of_date=now,
            idempotency_key=f"saga-default-{now.isoformat()}",
            max_single_position=0.10,
            max_gross_leverage=1.0,
        )

    # ── 公共入口 ──

    def execute(self, order: Order, side: OrderSide) -> SagaResult:
        """执行单笔订单的 Saga 六步流程（同步阻塞至完成或超时）。

        Args:
            order: 订单（需包含 symbol/quantity/limit_price 等）
            side: 买卖方向

        Returns:
            SagaResult（不可变，含最终状态/成交/补偿信息）
        """
        ctx = _SagaContext(
            saga_id=uuid.uuid4().hex,
            order=order,
            side=side,
            start_time=time.monotonic(),
        )
        # 重复执行守卫：订单已处终态直接拒绝
        if order.status in (OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED):
            ctx.state = SagaState.SIGNAL_INVALID
            ctx.error = f"订单已处终态 {order.status.value}，拒绝重复执行"
            _logger.warning(
                "[Saga %s] 拒绝重复执行: order=%s status=%s",
                ctx.saga_id[:8],
                order.order_id,
                order.status.value,
            )
            return ctx.to_result()
        _logger.info(
            "[Saga %s] START order=%s symbol=%s side=%s",
            ctx.saga_id[:8],
            order.order_id,
            order.symbol,
            side.value,
        )

        try:
            return self._run_saga(ctx)
        finally:
            # 清理 fill callback（step3 可能注册了 collector）
            # 走公共 fill_callbacks 属性（AI-R3 复审 P2：OrderManager Stage 4 已公共化）
            if ctx.collector is not None:
                try:
                    self._order_manager.fill_callbacks.remove(ctx.collector)
                except (ValueError, AttributeError):
                    pass  # 已清理或不存在

    # ── Saga 主流程 ──

    def _run_saga(self, ctx: _SagaContext) -> SagaResult:
        """执行六步 Saga（内部, collector 在 step3 注册到 ctx.collector）。"""
        try:
            # 步骤1: 风控检查
            if not self._step1_risk_check(ctx):
                return ctx.to_result()

            # 步骤2: 信号确认（可选）
            if not self._step2_signal_confirm(ctx):
                return ctx.to_result()

            # 步骤3: 下单提交（注册 fill collector 到 ctx.collector）
            if not self._step3_order_submit(ctx):
                return ctx.to_result()

            # 步骤4: 成交确认
            remaining = ctx.remaining_timeout(self._config)
            fill = self._step4_fill_confirm(ctx, ctx.collector, remaining)
            if fill is None:
                # 超时 → 补偿撤单；只要未确认撤净就强制查终态分流（AI-R3 复审
                # P1 治本：原仅 FAILED 分支查终态——collector.wait 超时后、撤单
                # 检查前成交回调到达使订单转 FILLED 时，_compensate_order 返回
                # NOT_NEEDED 直接跳过恢复，成交被吞=与 P0-2 同型事故窗口）
                ctx.state = SagaState.TIMEOUT
                ctx.error = f"fill timeout after {self._config.timeout_seconds}s"
                outcome = self._compensate_order(ctx)
                if outcome in (_CancelOutcome.FAILED, _CancelOutcome.NOT_NEEDED):
                    if self._recover_filled_order(ctx):
                        return ctx.to_result()
                    if outcome is _CancelOutcome.FAILED:
                        _logger.critical(
                            "[Saga %s] 撤单失败且无法确认订单终态——持仓可能与券商不一致，需人工对账: order=%s",
                            ctx.saga_id[:8],
                            ctx.order.order_id,
                        )
                self._audit_timeout(ctx)
                return ctx.to_result()

            ctx.fill = fill
            ctx.state = SagaState.FILL_RECEIVED
            ctx.mark_step("fill_confirm")
            self._audit.log(
                ExecutionAuditEventType.FILL_RECEIVED,
                ctx.order.order_id,
                ctx.order.symbol,
                AuditSource.AUTO,
                {"fill_id": fill.fill_id, "fill_price": str(fill.fill_price), "filled_qty": str(fill.filled_quantity)},
            )

            # 步骤5: 持仓更新
            if not self._step5_position_update(ctx):
                return ctx.to_result()

            # 步骤6: 报告生成
            self._step6_report(ctx)

            ctx.state = SagaState.COMPLETED
            _logger.info(
                "[Saga %s] COMPLETED order=%s fill=%s duration=%.1fms",
                ctx.saga_id[:8],
                ctx.order.order_id,
                ctx.fill.fill_id if ctx.fill else None,
                (time.monotonic() - ctx.start_time) * 1000,
            )
            return ctx.to_result()

        except Exception as exc:  # noqa: BLE001
            ctx.error = f"saga exception: {exc}"
            _logger.error("[Saga %s] EXCEPTION: %s", ctx.saga_id[:8], exc, exc_info=True)
            # 尝试补偿
            if ctx.state in (SagaState.ORDER_SUBMITTED, SagaState.FILL_RECEIVED):
                self._compensate_order(ctx)
            return ctx.to_result()

    # ── 六步实现 ──

    def _step1_risk_check(self, ctx: _SagaContext) -> bool:
        """步骤1: 风控检查。"""
        try:
            # 获取当前持仓用于风控校验
            snapshot = self._position_tracker.get_positions()
            current_holdings: dict[str, float] = {s: float(q) for s, q in snapshot.holdings.items()}
            # target_weight: 简化估算（实际应由调用方提供）
            total_nav = float(snapshot.cash + snapshot.total_market_value)
            target_weight = (
                float(ctx.order.quantity * (ctx.order.limit_price or Decimal("0"))) / total_nav
                if total_nav > 0
                else 0.0
            )

            violations = self._risk_validator.validate_order(
                symbol=ctx.order.symbol,
                target_weight=target_weight,
                current_holdings=current_holdings,
                limits=self._risk_limits,
            )

            halt_violations = [v for v in violations if v.severity == "HALT"]
            if halt_violations:
                ctx.state = SagaState.RISK_REJECTED
                ctx.error = f"risk rejected: {'; '.join(v.description for v in halt_violations)}"
                self._audit.log(
                    ExecutionAuditEventType.ORDER_REJECTED,
                    ctx.order.order_id,
                    ctx.order.symbol,
                    AuditSource.AUTO,
                    {"reason": "risk_check_failed", "violations": [v.description for v in halt_violations]},
                )
                _logger.warning("[Saga %s] RISK_REJECTED: %s", ctx.saga_id[:8], ctx.error)
                return False

            ctx.state = SagaState.RISK_PASSED
            ctx.mark_step("risk_check")
            self._audit.log(
                ExecutionAuditEventType.ORDER_CREATED,
                ctx.order.order_id,
                ctx.order.symbol,
                AuditSource.AUTO,
                {
                    "qty": str(ctx.order.quantity),
                    "side": ctx.side.value,
                    "limit_price": str(ctx.order.limit_price) if ctx.order.limit_price else None,
                },
            )
            return True

        except Exception as exc:  # noqa: BLE001
            ctx.state = SagaState.RISK_REJECTED
            ctx.error = f"risk check error: {exc}"
            return False

    def _step2_signal_confirm(self, ctx: _SagaContext) -> bool:
        """步骤2: 信号确认（可选，signal_confirmer=None 时跳过）。"""
        if self._signal_confirmer is None:
            ctx.state = SagaState.SIGNAL_CONFIRMED
            ctx.mark_step("signal_confirm(skipped)")
            return True

        try:
            valid = self._signal_confirmer(ctx.order)
            if not valid:
                ctx.state = SagaState.SIGNAL_INVALID
                ctx.error = "signal confirmation failed"
                _logger.info("[Saga %s] SIGNAL_INVALID", ctx.saga_id[:8])
                return False
            ctx.state = SagaState.SIGNAL_CONFIRMED
            ctx.mark_step("signal_confirm")
            return True
        except Exception as exc:  # noqa: BLE001
            ctx.state = SagaState.SIGNAL_INVALID
            ctx.error = f"signal confirm error: {exc}"
            return False

    def _step3_order_submit(self, ctx: _SagaContext) -> bool:
        """步骤3: 下单提交（create + register collector + submit）。"""
        try:
            # 如果订单还未注册到 OrderManager（TradingSession 传入的可能是值对象）
            if ctx.order.order_id not in self._order_manager.orders:
                registered = self._order_manager.create_order(
                    symbol=ctx.order.symbol,
                    strategy_id=ctx.order.strategy_id,
                    side=ctx.side,
                    order_type=ctx.order.order_type,
                    quantity=ctx.order.quantity,
                    limit_price=ctx.order.limit_price,
                    broker_id=self._config.broker_id,
                )
                ctx.order = registered  # 替换为已注册的 Order

            # 注册 fill collector（用实际 order_id, 在 submit 前注册防同步成交竞态）
            ctx.collector = _FillCollector(ctx.order.order_id, ctx.order.quantity)
            self._order_manager.register_fill_callback(ctx.collector)

            self._order_manager.submit_order(ctx.order.order_id, self._config.broker_id)
            ctx.state = SagaState.ORDER_SUBMITTED
            ctx.mark_step("order_submit")
            self._audit.log(
                ExecutionAuditEventType.ORDER_SUBMITTED,
                ctx.order.order_id,
                ctx.order.symbol,
                AuditSource.AUTO,
                {"broker_id": self._config.broker_id, "broker_order_id": ctx.order.broker_order_id},
            )
            _logger.info(
                "[Saga %s] ORDER_SUBMITTED order=%s broker=%s",
                ctx.saga_id[:8],
                ctx.order.order_id,
                self._config.broker_id,
            )
            return True

        except Exception as exc:  # noqa: BLE001
            ctx.state = SagaState.ORDER_REJECTED
            ctx.error = f"order submit failed: {exc}"
            rejection_result = self._handle_rejection(ctx, exc)
            self._audit.log(
                ExecutionAuditEventType.ORDER_REJECTED,
                ctx.order.order_id,
                ctx.order.symbol,
                AuditSource.AUTO,
                {
                    "reason": "submit_error",
                    "error": str(exc),
                    "rejection_action": rejection_result.action.name if rejection_result else None,
                    "rejection_outcome": rejection_result.outcome.value if rejection_result else None,
                },
            )
            return False

    def _handle_rejection(self, ctx: _SagaContext, exc: Exception) -> RejectionActionResult | None:
        """拒单分类实际动作（40 号 §6.1 gap 4 Saga 接管，§2.7 层3）。

        注入 rejection_executor 时按 error_code 分类执行实际动作
        （RETRY_ONCE 重试/ALERT_FREEZE 冻结策略/ALERT_RECONCILE 触发对账）；
        未注入返回 None（仅审计留痕，既有 MVP 行为）。执行器自身异常吞没
        不阻断 Saga 主流程（拒单处置不得引发二次事故）。
        """
        if self._rejection_executor is None:
            return None
        raw_code = getattr(exc, "error_code", None)
        try:
            if isinstance(raw_code, int):
                result = self._rejection_executor.classify_and_execute(raw_code, ctx.order, exc)
            else:
                # 无 int error_code（如本地合规闸阻断）——保守按 ABANDON 留痕
                result = self._rejection_executor.execute(RejectionAction.ABANDON, ctx.order, exc)
        except Exception as handler_exc:  # noqa: BLE001 — 处置器异常不阻断 Saga
            _logger.error(
                "[Saga %s] 拒单动作执行异常（已吞没）: order=%s error=%s",
                ctx.saga_id[:8],
                ctx.order.order_id,
                handler_exc,
                exc_info=True,
            )
            return None
        _logger.info(
            "[Saga %s] 拒单分类动作: order=%s action=%s outcome=%s",
            ctx.saga_id[:8],
            ctx.order.order_id,
            result.action.name,
            result.outcome.value,
        )
        return result

    def _step4_fill_confirm(self, ctx: _SagaContext, collector: _FillCollector | None, timeout: float) -> Fill | None:
        """步骤4: 成交确认（等待 fill 回调）。"""
        if collector is None or timeout <= 0:
            return None

        # 如果 fill 已经在 submit_order 期间同步到达（SimulationBroker 场景）
        if collector.collected:
            return collector._fill

        fill = collector.wait(timeout=timeout)
        return fill

    def _step5_position_update(self, ctx: _SagaContext) -> bool:
        """步骤5: 持仓更新。"""
        if ctx.fill is None:
            ctx.error = "no fill to apply"
            return False

        try:
            self._position_tracker.apply_fill(ctx.fill, ctx.side)
            ctx.state = SagaState.POSITION_UPDATED
            ctx.mark_step("position_update")
            self._audit.log(
                ExecutionAuditEventType.ORDER_FILLED,
                ctx.order.order_id,
                ctx.order.symbol,
                AuditSource.AUTO,
                {
                    "fill_id": ctx.fill.fill_id,
                    "avg_price": str(ctx.fill.fill_price),
                    "filled_qty": str(ctx.fill.filled_quantity),
                    "commission": str(ctx.fill.commission),
                },
            )
            return True
        except Exception as exc:  # noqa: BLE001
            ctx.error = f"position update failed: {exc}"
            # 补偿: 持仓回滚
            self._compensate_position(ctx)
            return False

    def _step6_report(self, ctx: _SagaContext) -> None:
        """步骤6: 报告生成（best-effort, 失败不阻断）。"""
        try:
            # 标记订单完成
            if ctx.order.status not in (OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED):
                ctx.order.status = OrderStatus.FILLED
                ctx.order.updated_at = datetime.now(UTC)
            ctx.mark_step("report")
        except Exception as exc:  # noqa: BLE001
            _logger.warning("[Saga %s] report step failed (best-effort): %s", ctx.saga_id[:8], exc)

    # ── 补偿操作 ──

    def _compensate_order(self, ctx: _SagaContext) -> _CancelOutcome:
        """步骤3补偿: 撤单（幂等）。返回撤单结果，供超时分支决定是否强制查询终态。"""
        try:
            if ctx.order.status in (OrderStatus.PENDING, OrderStatus.SUBMITTED, OrderStatus.PARTIAL):
                cancelled = self._order_manager.cancel_order(ctx.order.order_id)
                if cancelled:
                    ctx.compensated = True
                    ctx.state = SagaState.COMPENSATED
                    self._audit.log(
                        ExecutionAuditEventType.ORDER_CANCELLED,
                        ctx.order.order_id,
                        ctx.order.symbol,
                        AuditSource.AUTO,
                        {"reason": "saga_compensate", "saga_state": ctx.state.value},
                    )
                    _logger.info("[Saga %s] COMPENSATED: order cancelled", ctx.saga_id[:8])
                    return _CancelOutcome.CANCELLED
                # 撤单失败——可能已成交（由调用方强制查询终态，不再吞掉）
                _logger.warning("[Saga %s] cancel returned False (may already be filled)", ctx.saga_id[:8])
                return _CancelOutcome.FAILED
            # 订单已终态（FILLED/CANCELLED/REJECTED）——无需补偿
            _logger.info("[Saga %s] skip compensate: order status=%s", ctx.saga_id[:8], ctx.order.status)
            return _CancelOutcome.NOT_NEEDED
        except Exception as exc:  # noqa: BLE001
            _logger.error("[Saga %s] compensate_order failed: %s", ctx.saga_id[:8], exc, exc_info=True)
            return _CancelOutcome.FAILED

    def _recover_filled_order(self, ctx: _SagaContext) -> bool:
        """超时后的终态恢复：强制查询订单终态，有成交（全成/部成）补走 step5/6。

        AI-R3 复审 P1 治本：原仅 FILLED 终态恢复——PARTIAL（部分成交）时
        已成交部分不入账，持仓账与券商漂移。改为按 filled_quantity 分流：
        有成交即恢复（FILLED 缺数量时按订单全量兜底），无成交保持 TIMEOUT。

        Returns:
            True=订单有成交且后续步骤已补走；False=无成交或无法确认终态
            （保持 TIMEOUT 语义，调用方继续告警）。
        """
        terminal = self._query_terminal_order(ctx)
        if terminal is None:
            return False
        recovered_qty = terminal.filled_quantity
        if terminal.status is OrderStatus.FILLED and recovered_qty <= 0:
            recovered_qty = ctx.order.quantity  # FILLED 但数量缺失（契约漂移兜底）
        if recovered_qty <= 0:
            return False  # 无成交（CANCELLED/REJECTED/零成交）→ 保持 TIMEOUT
        # 有成交：构造恢复 Fill 补走持仓更新+报告（fill_id 确定性前缀 saga-fq-，
        # 供 fill_id 去重集识别恢复来源——去重落地归 AI-RRESIL-001，本侧只保证可识别）
        recovered_price = terminal.avg_fill_price or ctx.order.limit_price or Decimal("0")
        # 成本不可得门禁（AI-R2 红队 ATK-6）：市价单 avg_fill_price 缺失时
        # price=0 入账 → 后续卖出 realized_pnl 全虚盈（账面成本 0）。宁缺账
        # （critical 告警人工对账，对账链以券商为准兜底）不错账
        if recovered_price <= 0:
            _logger.critical(
                "[Saga %s] 订单已成交但成本价不可得（avg_fill_price/limit_price 均缺），"
                "不补走持仓更新——人工对账: order=%s",
                ctx.saga_id[:8],
                ctx.order.order_id,
            )
            return False
        ctx.fill = Fill(
            fill_id=f"saga-fq-{ctx.order.order_id}",
            fill_price=recovered_price,
            fill_timestamp=datetime.now(UTC),
            filled_quantity=recovered_qty,
            idempotency_key=f"saga-fq-{ctx.order.idempotency_key}",
            order_id=ctx.order.order_id,
            strategy_id=ctx.order.strategy_id,
            symbol=ctx.order.symbol,
        )
        ctx.state = SagaState.FILL_RECEIVED
        ctx.mark_step("fill_confirm(force_query)")
        ctx.error = None
        self._audit.log(
            ExecutionAuditEventType.FILL_RECEIVED,
            ctx.order.order_id,
            ctx.order.symbol,
            AuditSource.AUTO,
            {
                "fill_id": ctx.fill.fill_id,
                "recovered_via": "force_query_terminal_state",
                "fill_price": str(recovered_price),
                "filled_qty": str(recovered_qty),
            },
        )
        _logger.warning(
            "[Saga %s] 超时但订单已成交，补走持仓更新+报告: order=%s",
            ctx.saga_id[:8],
            ctx.order.order_id,
        )
        if not self._step5_position_update(ctx):
            return True
        self._step6_report(ctx)
        ctx.state = SagaState.COMPLETED
        return True

    def _query_terminal_order(self, ctx: _SagaContext) -> Order | None:
        """强制查询订单终态：broker 权威查询优先，本地 OrderManager 兜底。"""
        if ctx.order.broker_order_id:
            try:
                terminal = self._broker.query_order(ctx.order.broker_order_id)
                if terminal is not None:
                    return terminal
            except Exception:  # noqa: BLE001 — 券商查询失效降级本地查询
                _logger.exception("[Saga %s] broker.query_order 失效，降级本地查询", ctx.saga_id[:8])
        try:
            return self._order_manager.get_order(ctx.order.order_id)
        except Exception:  # noqa: BLE001
            _logger.exception("[Saga %s] order_manager.get_order 失效", ctx.saga_id[:8])
            return None

    def _compensate_position(self, ctx: _SagaContext) -> None:
        """步骤5补偿: 持仓回滚（反向 apply_fill, 幂等）。"""
        if ctx.fill is None:
            return
        try:
            reverse_fill = Fill(
                fill_id=f"rollback-{ctx.fill.fill_id}",
                fill_price=ctx.fill.fill_price,
                fill_timestamp=datetime.now(UTC),
                filled_quantity=ctx.fill.filled_quantity,
                idempotency_key=f"rollback-{ctx.fill.idempotency_key}",
                order_id=ctx.fill.order_id,
                strategy_id=ctx.fill.strategy_id,
                symbol=ctx.fill.symbol,
                commission=Decimal("0"),  # 回滚不收佣金
            )
            reverse_side = OrderSide.SELL if ctx.side == OrderSide.BUY else OrderSide.BUY
            self._position_tracker.apply_fill(reverse_fill, reverse_side)
            ctx.compensated = True
            ctx.state = SagaState.COMPENSATED
            self._audit.log(
                ExecutionAuditEventType.ORDER_CANCELLED,
                ctx.order.order_id,
                ctx.order.symbol,
                AuditSource.AUTO,
                {"reason": "position_rollback", "original_fill": ctx.fill.fill_id},
            )
            _logger.info("[Saga %s] COMPENSATED: position rolled back", ctx.saga_id[:8])
        except Exception as exc:  # noqa: BLE001
            _logger.error("[Saga %s] compensate_position failed: %s", ctx.saga_id[:8], exc, exc_info=True)

    def _audit_timeout(self, ctx: _SagaContext) -> None:
        """记录超时事件到审计日志。"""
        self._audit.log(
            ExecutionAuditEventType.ORDER_EXPIRED,
            ctx.order.order_id,
            ctx.order.symbol,
            AuditSource.AUTO,
            {"reason": "saga_timeout", "timeout_seconds": self._config.timeout_seconds},
        )

# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] zephyr.ex_core.rejection_action_handler
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] zephyr.ex_core.order_manager(RejectionAction/classify_rejection 复用不重复实现); zephyr.shared.contracts.order; zephyr.shared.foundation.errors
# [CONSUMERS] TradingSession._handle_rejection(装配批次接线); OrderExecutionSaga(接管后归口)
# [STARTUP] imported
# [MATURITY] evolving
# [INVARIANTS] 分类唯一真源=OrderManager.classify_rejection(不重复映射表); RETRY_ONCE 每单至多一次(order_id 去重); ALERT_FREEZE 冻结表只增需人工解冻(防自动复活); 注入缺失降级=日志+放弃(Fail-Closed 不盲目重试); alert_sink 异常吞没不阻断
# [MODIFY-GUARD] 40_execution_broker.md §2.7/§6.1 gap 4
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] InvalidRejectionActionInputError(ZA-EX-0014)
# [TESTS] tests/ex_core/test_rejection_action_handler.py
# [TTL] permanent
# [ALGO_FLOW]
# I1: action(RejectionAction) + order(Order) + error(原始异常, 可选) + error_code(可选, classify_and_execute 入口)
# I2: retry_fn(重试执行器注入) + alert_sink(告警出口注入) + reconcile_trigger(持仓对账触发注入)
# F1: execute(action, order, error)——按 40 号 §2.7 表执行实际动作
# A1: RETRY_ONCE——order_id 去重, 首拒调 retry_fn, 再拒降级放弃(撤单率≤15%防线)
# A2: ALERT_FREEZE——告警 + strategy_id 入冻结表(is_strategy_frozen 供下单链查询, 人工 unfreeze)
# A3: ALERT_RECONCILE——告警 + reconcile_trigger(strategy_id, symbol)(T+1锁定/持仓不一致对账)
# A4: IDEMPOTENT_RETURN——返回已有 broker_order_id(幂等)
# O1: RejectionActionResult(outcome/broker_order_id/frozen_strategy_id)——调用方留痕
# [/ALGO_FLOW]
"""D_EX_CORE — 拒单分类动作执行器（40 号 §6.1 gap 4 闭合，AI-NIGHT-001 包P）。

40 号 §2.7 层3：分类映射 + classify_rejection + _handle_rejection 日志已实现，
RETRY_ONCE / ALERT_FREEZE / ALERT_RECONCILE **实际动作**待 OrderExecutionSaga
接管。本模块是 Saga 接管前的函数级动作执行层——策略冻结表 + 执行器注入：

  | 动作 | 执行 | 注入依赖 |
  |---|---|---|
  | RETRY_ONCE | 每单至多 1 次重试（order_id 去重），再拒降级放弃 | retry_fn |
  | ALERT_FREEZE | 告警 + 冻结该策略新开仓（冻结表只增，人工解冻） | alert_sink |
  | ALERT_RECONCILE | 告警 + 触发持仓对账 | alert_sink + reconcile_trigger |
  | ABANDON | 日志留痕（涨跌停/数量不合法重试无意义） | — |
  | IDEMPOTENT_RETURN | 返回已存在 broker_order_id | — |

工程裁定：分类映射不重复实现——复用 OrderManager.classify_rejection 唯一真源；
注入缺失一律降级"日志+放弃"（Fail-Closed：宁可放弃不可盲目重试，40 号 §2.7
原则 + BM-EXE-04 撤单率 ≤15% 防线）。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable

from zephyr.ex_core.order_manager import OrderManager, RejectionAction
from zephyr.shared.contracts.order import Order
from zephyr.shared.foundation.errors import ZephyrBaseError

_logger = logging.getLogger(__name__)


class InvalidRejectionActionInputError(ZephyrBaseError):
    """拒单动作执行输入非法——order 缺失/order_id 空等。"""

    error_code = "ZA-EX-0014"


class RejectionOutcome(str, Enum):
    """动作执行结果。"""

    ABANDONED = "abandoned"  # 放弃（不重试）
    RETRIED = "retried"  # 已重试 1 次
    FROZEN = "frozen"  # 策略新开仓已冻结
    RECONCILE_TRIGGERED = "reconcile_triggered"  # 持仓对账已触发
    IDEMPOTENT_RETURNED = "idempotent_returned"  # 幂等返回已存在单号
    DEGRADED_ABANDONED = "degraded_abandoned"  # 注入缺失降级放弃


@dataclass(frozen=True)
class RejectionActionResult:
    """拒单动作执行结果（留痕用）。"""

    action: RejectionAction
    outcome: RejectionOutcome
    order_id: str
    broker_order_id: str | None = None
    frozen_strategy_id: str | None = None
    detail: str = ""


class RejectionActionExecutor:
    """拒单分类动作执行器（策略冻结表 + 执行器注入）。

    Args:
        retry_fn: 重试执行器 callable(order, error) -> broker_order_id | None。
            None=未接线 → RETRY_ONCE 降级放弃（Fail-Closed）。
        alert_sink: 告警出口 callable(message, context: dict)。None=仅日志；
            异常吞没不阻断（告警 best-effort）。
        reconcile_trigger: 持仓对账触发 callable(strategy_id, symbol)。
            None → ALERT_RECONCILE 仅告警不触发（降级留痕）。
    """

    def __init__(
        self,
        *,
        retry_fn: Callable[[Order, BaseException | None], str | None] | None = None,
        alert_sink: Callable[[str, dict], None] | None = None,
        reconcile_trigger: Callable[[str, str], None] | None = None,
    ) -> None:
        self._retry_fn = retry_fn
        self._alert_sink = alert_sink
        self._reconcile_trigger = reconcile_trigger
        # 策略冻结表（只增，人工解冻——防自动复活，40 号 §2.7 账户级问题口径）
        self._frozen_strategies: set[str] = set()
        # RETRY_ONCE 去重（每单至多一次）
        self._retried_order_ids: set[str] = set()

    # ── 冻结表查询（下单链消费）──

    def is_strategy_frozen(self, strategy_id: str) -> bool:
        """策略新开仓是否已冻结（资金不足拒单触发）。"""
        return strategy_id in self._frozen_strategies

    def unfreeze_strategy(self, strategy_id: str) -> bool:
        """人工解冻（owner 确认资金恢复后显式调用）。返回是否曾在冻结表。"""
        if strategy_id in self._frozen_strategies:
            self._frozen_strategies.discard(strategy_id)
            _logger.info("拒单冻结人工解冻: strategy_id=%s", strategy_id)
            return True
        return False

    @property
    def frozen_strategies(self) -> frozenset[str]:
        """当前冻结策略快照（只读）。"""
        return frozenset(self._frozen_strategies)

    # ── 动作执行 ──

    def execute(
        self,
        action: RejectionAction,
        order: Order,
        error: BaseException | None = None,
    ) -> RejectionActionResult:
        """按拒单分类执行实际动作（40 号 §2.7 表）。"""
        if order is None or not getattr(order, "order_id", None):
            raise InvalidRejectionActionInputError(
                "order 缺失或 order_id 为空",
                details={"action": str(action)},
            )

        if action is RejectionAction.RETRY_ONCE:
            return self._execute_retry_once(order, error)
        if action is RejectionAction.ALERT_FREEZE:
            return self._execute_alert_freeze(order, error)
        if action is RejectionAction.ALERT_RECONCILE:
            return self._execute_alert_reconcile(order, error)
        if action is RejectionAction.IDEMPOTENT_RETURN:
            _logger.info("拒单[幂等返回] order_id=%s broker_order_id=%s", order.order_id, order.broker_order_id)
            return RejectionActionResult(
                action=action,
                outcome=RejectionOutcome.IDEMPOTENT_RETURNED,
                order_id=order.order_id,
                broker_order_id=order.broker_order_id,
            )
        # ABANDON（及未知动作保守放弃）
        _logger.warning("拒单[放弃] order_id=%s symbol=%s error=%s", order.order_id, order.symbol, error)
        return RejectionActionResult(
            action=action,
            outcome=RejectionOutcome.ABANDONED,
            order_id=order.order_id,
        )

    def classify_and_execute(
        self,
        error_code: int,
        order: Order,
        error: BaseException | None = None,
    ) -> RejectionActionResult:
        """分类（复用 OrderManager 唯一真源）+ 执行一体化入口。"""
        action = OrderManager.classify_rejection(error_code)
        return self.execute(action, order, error)

    # ── 各动作实现 ──

    def _execute_retry_once(self, order: Order, error: BaseException | None) -> RejectionActionResult:
        if order.order_id in self._retried_order_ids:
            _logger.warning(
                "拒单[重试耗尽放弃] order_id=%s 已重试过（每单至多 1 次，撤单率防线）",
                order.order_id,
            )
            return RejectionActionResult(
                action=RejectionAction.RETRY_ONCE,
                outcome=RejectionOutcome.ABANDONED,
                order_id=order.order_id,
                detail="retry exhausted",
            )
        self._retried_order_ids.add(order.order_id)
        if self._retry_fn is None:
            _logger.warning("拒单[降级放弃] order_id=%s retry_fn 未注入", order.order_id)
            return RejectionActionResult(
                action=RejectionAction.RETRY_ONCE,
                outcome=RejectionOutcome.DEGRADED_ABANDONED,
                order_id=order.order_id,
                detail="retry_fn not wired",
            )
        broker_order_id = self._retry_fn(order, error)
        _logger.info("拒单[重试1次] order_id=%s -> broker_order_id=%s", order.order_id, broker_order_id)
        return RejectionActionResult(
            action=RejectionAction.RETRY_ONCE,
            outcome=RejectionOutcome.RETRIED,
            order_id=order.order_id,
            broker_order_id=broker_order_id,
        )

    def _execute_alert_freeze(self, order: Order, error: BaseException | None) -> RejectionActionResult:
        strategy_id = order.strategy_id or ""
        self._frozen_strategies.add(strategy_id)
        self._alert(
            f"拒单[资金不足] 冻结策略新开仓: strategy_id={strategy_id} symbol={order.symbol}",
            {"order_id": order.order_id, "strategy_id": strategy_id, "symbol": order.symbol, "error": str(error)},
        )
        return RejectionActionResult(
            action=RejectionAction.ALERT_FREEZE,
            outcome=RejectionOutcome.FROZEN,
            order_id=order.order_id,
            frozen_strategy_id=strategy_id,
        )

    def _execute_alert_reconcile(self, order: Order, error: BaseException | None) -> RejectionActionResult:
        strategy_id = order.strategy_id or ""
        self._alert(
            f"拒单[持仓不足] 触发持仓对账: strategy_id={strategy_id} symbol={order.symbol}",
            {"order_id": order.order_id, "strategy_id": strategy_id, "symbol": order.symbol, "error": str(error)},
        )
        if self._reconcile_trigger is None:
            _logger.warning("reconcile_trigger 未注入，仅告警留痕: order_id=%s", order.order_id)
            return RejectionActionResult(
                action=RejectionAction.ALERT_RECONCILE,
                outcome=RejectionOutcome.DEGRADED_ABANDONED,
                order_id=order.order_id,
                detail="reconcile_trigger not wired",
            )
        self._reconcile_trigger(strategy_id, order.symbol)
        return RejectionActionResult(
            action=RejectionAction.ALERT_RECONCILE,
            outcome=RejectionOutcome.RECONCILE_TRIGGERED,
            order_id=order.order_id,
        )

    def _alert(self, message: str, context: dict[str, Any]) -> None:
        _logger.error("%s", message)
        if self._alert_sink is not None:
            try:
                self._alert_sink(message, context)
            except Exception:  # noqa: BLE001 —— 告警 best-effort 不阻断处置
                _logger.exception("alert_sink 调用失败（已吞没）")


__all__ = [
    "InvalidRejectionActionInputError",
    "RejectionActionExecutor",
    "RejectionActionResult",
    "RejectionOutcome",
]

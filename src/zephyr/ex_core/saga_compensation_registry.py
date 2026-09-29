# [BLUEPRINT] MOD-EX-057 | docs/03_modules/_domain_execution_core/order_execution_saga/blueprint.md
# [MODULE] zephyr.ex_core.saga_compensation_registry
# [DOMAIN] D_EX_CORE
# [DEPENDENCIES] stdlib; zephyr.shared.contracts.fill
# [CONSUMERS] zephyr.ex_core.order_execution_saga（F53 夜战批接线，补偿点三处调用）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 注册表只挂动作不执行（执行归 Saga 补偿点）;run_compensations 永不抛（单动作异常捕获成记录，不阻断其余动作）;同步骤内动作按注册逆序执行（LIFO）;registry 空载=Saga 行为零变化;动作须幂等（注册时声明，非幂等动作拒绝注册）
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无自定义异常——run_compensations 吞动作异常为 SagaCompensationRecord(outcome=FAILED)
# [TESTS] tests/ex_core/test_saga_compensation_registry.py
# [A_module] module_id=MOD-EX-057-R1 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# create-guard-not-dup: 订单 Saga 步骤级补偿动作注册面（F53 案卷缺口①，补偿动作一等化扩展点），与 capability/策略/门禁/告警类 *registry* 能力无同源关系，命中系"注册表"字面泛化
# [TTL] permanent

"""

Saga Compensation Registry — 订单 Saga 补偿动作注册表 (MOD-EX-057-R1 / F53 夜战批)

背景（F53 案卷缺口①）: OrderExecutionSaga 的补偿动作（撤单/持仓回滚）此前硬编码
为私有方法，无法按步骤扩展。本注册表把"步骤 → 补偿动作序列"变成一等注册面：

    - OrderExecutionSaga 构造时注入 compensation_registry；
    - Saga 在三个补偿点（step5 持仓更新失败 / 异常路径 / 超时终判 TIMEOUT）
      对"已完成步骤+失败步骤"按逆序执行注册动作（经典 Saga 反向补偿语义）；
    - 每个动作执行结果成 SagaCompensationRecord（EXECUTED/FAILED+error），
      由 Saga 写入执行审计（reason=saga_compensation_registry）。

边界: 内建补偿（撤单 _compensate_order / 持仓回滚 _compensate_position）语义
不变、先行执行；注册表动作是"额外清理"扩展点（如释放预占资源、清 pending 标记），
不替代也不绕过内建补偿。空注册表=Saga 行为零变化（既有 50+ 用例为回归锁）。

SSoT: depgraph MOD-EX-057-R1
Version: 0.1.0

# [ALGO_FLOW] external: docs/03_modules/_domain_execution_core/algo_flow/order_execution_saga.yaml
"""

from __future__ import annotations

import threading
from collections.abc import Callable, Iterable, Sequence
from dataclasses import dataclass, field
from enum import Enum
from typing import Final

from zephyr.shared.contracts.fill import Fill

__all__: Final = [
    "CompensationAction",
    "SagaCompensationContext",
    "SagaCompensationOutcome",
    "SagaCompensationRecord",
    "SagaCompensationRegistry",
]


class SagaCompensationOutcome(str, Enum):
    """单个补偿动作的执行结果。"""

    EXECUTED = "EXECUTED"
    FAILED = "FAILED"


@dataclass(frozen=True)
class SagaCompensationContext:
    """补偿动作收到的 Saga 快照（只读，防动作改写编排状态）。

    Attributes:
        saga_id: Saga 运行唯一 ID
        order_id: 订单 ID
        symbol: 标的代码
        side: 买卖方向（OrderSide.value）
        state: 补偿触发时的 Saga 状态名
        error: 触发补偿的错误信息（可为 None）
        fill: 已收到的成交回报（未成交=None）
    """

    saga_id: str
    order_id: str
    symbol: str
    side: str
    state: str
    error: str | None
    fill: Fill | None


@dataclass(frozen=True)
class CompensationAction:
    """注册进注册表的单个补偿动作。

    Attributes:
        name: 动作名（审计与测试定位用）
        run: 动作本体，入参 SagaCompensationContext，返回 None；
            异常由 run_compensations 捕获成 FAILED 记录，不会外抛。
        idempotent: 是否幂等——非幂等动作在注册时即拒绝（ValueError），
            因为补偿可能在内建补偿与超时恢复分流后触发多次路径。
    """

    name: str
    run: Callable[[SagaCompensationContext], None]
    idempotent: bool = True

    def __post_init__(self) -> None:
        if not self.idempotent:
            raise ValueError(f"补偿动作 {self.name!r} 必须幂等（补偿可能沿多条路径触发）")
        if not callable(self.run):
            raise ValueError(f"补偿动作 {self.name!r} 的 run 不可调用")


@dataclass(frozen=True)
class SagaCompensationRecord:
    """单个补偿动作的执行记录（供 Saga 写审计/调用方诊断）。"""

    step: str
    action_name: str
    outcome: SagaCompensationOutcome
    error: str | None = None


@dataclass
class _StepBucket:
    """单步骤的动作桶（保注册序）。"""

    actions: list[CompensationAction] = field(default_factory=list)


class SagaCompensationRegistry:
    """步骤 → 补偿动作序列 注册表（线程安全）。

    用法:
        registry = SagaCompensationRegistry()
        registry.register("order_submit", CompensationAction("release_reserved", fn))
        saga = OrderExecutionSaga(..., compensation_registry=registry)

    语义:
        - run_compensations(steps, ctx): 对给定步骤序列逆序遍历，每步内动作
          按注册逆序执行（LIFO）；单动作异常捕获不阻断其余动作；整体永不抛。
        - 线程安全: register 与 run_compensations 各自持锁；动作本体自身的
          线程安全性由动作提供方保证（多 Saga 可共享同一注册表并发触发）。
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._buckets: dict[str, _StepBucket] = {}

    # ── 注册面 ──

    def register(self, step: str, action: CompensationAction) -> None:
        """为指定步骤追加补偿动作。

        Args:
            step: Saga 步骤名（risk_check/signal_confirm/order_submit/
                fill_confirm/position_update/report，与 SagaResult
                steps_completed 里的标记名一致）
            action: 补偿动作（须幂等）
        """
        if not step:
            raise ValueError("step 名不可为空")
        with self._lock:
            self._buckets.setdefault(step, _StepBucket()).actions.append(action)

    def actions_for(self, step: str) -> tuple[CompensationAction, ...]:
        """只读：指定步骤已注册的动作（注册序）。"""
        with self._lock:
            bucket = self._buckets.get(step)
            if bucket is None:
                return ()
            return tuple(bucket.actions)

    @property
    def registered_steps(self) -> tuple[str, ...]:
        """只读：已注册动作的步骤名（注册首现序）。"""
        with self._lock:
            return tuple(self._buckets.keys())

    def clear(self) -> None:
        """清空注册表（测试隔离用）。"""
        with self._lock:
            self._buckets.clear()

    # ── 执行面（由 Saga 补偿点调用） ──

    def run_compensations(
        self,
        steps: Iterable[str],
        context: SagaCompensationContext,
    ) -> list[SagaCompensationRecord]:
        """对步骤序列逆序执行各步已注册动作（经典 Saga 反向补偿）。

        Args:
            steps: 参与补偿的步骤名序列（调用方传"已完成步骤+失败步骤"）
            context: Saga 快照（传给每个动作）

        Returns:
            执行记录（按执行顺序）。单动作异常=FAILED 记录，不阻断后续动作；
            本方法自身永不抛异常（补偿路径不得引发二次事故）。
        """
        records: list[SagaCompensationRecord] = []
        with self._lock:
            snapshot = {s: tuple(b.actions) for s, b in self._buckets.items()}
        for step in reversed(list(steps)):
            for action in reversed(snapshot.get(step, ())):
                record = self._run_one(step, action, context)
                records.append(record)
        return records

    @staticmethod
    def _run_one(
        step: str,
        action: CompensationAction,
        context: SagaCompensationContext,
    ) -> SagaCompensationRecord:
        """执行单个动作并成记录（异常捕获）。"""
        try:
            action.run(context)
        except Exception as exc:  # noqa: BLE001 — 补偿动作异常不外抛（不引发二次事故）
            return SagaCompensationRecord(
                step=step,
                action_name=action.name,
                outcome=SagaCompensationOutcome.FAILED,
                error=f"{type(exc).__name__}: {exc}",
            )
        return SagaCompensationRecord(
            step=step,
            action_name=action.name,
            outcome=SagaCompensationOutcome.EXECUTED,
        )

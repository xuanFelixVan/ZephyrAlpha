# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.compensation.saga_compensator
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


Saga Compensator — 补偿事务：多步操作任一失败 -> 反向补偿。

依据：
    蓝图 MOD-TASK_SYSTEM §6.8 + v0.6.0
    任务卡 TASK-INF-0113

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: Saga步骤列表 SagaStep序列
#   fields: 每步含 step_id、action 正向回调、compensation 补偿回调、executed/compensated 标记
#   code: create_saga(steps) L76
# - id: I2
#   name: 事务标识 saga_id 字符串
#   fields: Saga 唯一 ID，用于注册/执行/补偿/查询定位 SagaContext
#   code: saga_id
# 层: 算法
# - id: A1
#   name_zh: ① Saga注册建上下文
#   name_en: create_saga
#   intro: 把一组步骤按 saga_id 登记成 PENDING 状态的 SagaContext 存进内存表
#   desc: 构造 SagaContext(saga_id, steps, status=PENDING, 当前UTC时间戳) 写入 self._sagas[saga_id] 并返回
#   inputs: I1 I2
#   outputs: SagaContext（PENDING）
# - id: A2
#   name_zh: ② 顺序执行与失败触发补偿
#   name_en: execute
#   intro: 按序调每步 action()，任何一步抛异常立刻记录错误并反向补偿已执行步骤
#   desc: 状态置 RUNNING 后 for 循环逐步调 step.action() 成功则 executed=True；异常时 errors 追加 Step失败信息、调 _compensate(context, 失败下标) 并返回 (False, context)；全部成功置 COMPLETED 返回 (True, context)
#   inputs: I2
#   outputs: (bool, SagaContext)
# - id: A3
#   name_zh: ③ 反向补偿回滚
#   name_en: _compensate/compensate_all
#   intro: 从失败步往前倒序，对已执行未补偿的步骤逐个调 compensation() 回滚
#   desc: 状态置 COMPENSATING；range(failed_index,-1,-1) 逆序遍历，守卫 step.executed and not step.compensated 才调 compensation() 并置 compensated=True；补偿异常累计 errors；有 errors 终态 FAILED 否则 COMPLETED；compensate_all 从最后一步起全量补偿
#   inputs: I2
#   outputs: 补偿后 SagaContext（FAILED/COMPLETED）
#   invariant: 补偿严格逆序且每步至多补偿一次
# 层: 输出
# - id: O1
#   name_zh: 执行/补偿结果元组
#   name_en: tuple[bool, SagaContext]
#   intro: execute/compensate_all 的返回——成功与否标志加含 status/errors/current_step 的 Saga 上下文
#   downstream: 无下游/内部使用
# - id: O2
#   name_zh: Saga状态登记表
#   name_en: _sagas/get_status
#   intro: 内存字典里的全部 SagaContext，get_status(saga_id) 供外部查询事务当前状态
#   downstream: 无下游/内部使用
# [/ALGO_FLOW]
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# I2 --> A2
# A2 --> A3
# I2 --> A3
# A2 --> O1
# A3 --> O1
# A1 --> O2
# A3 --> O2
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class SagaStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    COMPENSATING = "compensating"
    FAILED = "failed"


@dataclass
class SagaStep:
    step_id: str
    action: Callable
    compensation: Callable
    executed: bool = False
    compensated: bool = False
    error: str = ""


@dataclass
class SagaContext:
    saga_id: str
    steps: list[SagaStep]
    status: SagaStatus = SagaStatus.PENDING
    current_step: int = 0
    errors: list[str] = field(default_factory=list)
    timestamp_utc: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


class SagaCompensator:
    def __init__(self) -> None:
        self._sagas: dict[str, SagaContext] = {}

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def sagas(self) -> dict[str, SagaContext]:
        """只读：sagas（Stage 4 公共化）。"""
        return self._sagas

    @sagas.setter
    def sagas(self, value):
        """写入：sagas（Stage 4 公共化）。"""
        self._sagas = value

    def create_saga(self, saga_id: str, steps: list[SagaStep]) -> SagaContext:
        context = SagaContext(saga_id=saga_id, steps=steps)
        self._sagas[saga_id] = context
        return context

    def execute(self, saga_id: str) -> tuple[bool, SagaContext]:
        context = self._sagas.get(saga_id)

        if context is None:
            return False, SagaContext(saga_id="NOT_FOUND", steps=[])

        context.status = SagaStatus.RUNNING

        for i, step in enumerate(context.steps):
            context.current_step = i
            try:
                step.action()
                step.executed = True
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                context.errors.append(f"Step {step.step_id} failed: {e}")
                self._compensate(context, i)
                return False, context

        context.status = SagaStatus.COMPLETED
        return True, context

    def compensate_all(self, saga_id: str) -> tuple[bool, SagaContext]:
        context = self._sagas.get(saga_id)

        if context is None:
            return False, SagaContext(saga_id="NOT_FOUND", steps=[])

        self._compensate(context, len(context.steps) - 1)

        return len(context.errors) == 0, context

    def get_status(self, saga_id: str) -> SagaContext | None:
        return self._sagas.get(saga_id)

    def _compensate(self, context: SagaContext, failed_index: int) -> None:
        context.status = SagaStatus.COMPENSATING

        for i in range(failed_index, -1, -1):
            step = context.steps[i]
            if step.executed and not step.compensated:
                try:
                    step.compensation()
                    step.compensated = True
                except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                    context.errors.append(f"Compensation for {step.step_id} failed: {e}")

        if context.errors:
            context.status = SagaStatus.FAILED
        else:
            context.status = SagaStatus.COMPLETED

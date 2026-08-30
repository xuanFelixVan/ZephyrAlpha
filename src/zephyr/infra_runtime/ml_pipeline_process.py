# [BLUEPRINT] MOD-INF-078 | docs/03_modules/_domain_infrastructure_runtime/ml_pipeline_process/blueprint.md
# [MODULE] zephyr.infra_runtime.ml_pipeline_process
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES] 无（编排核心纯内存；clock/is_trading_hours/gpu_schedule/alert_sink 全注入）
# [CONSUMERS] 运行时装配批（P5 ML 管线进程四职责任务队列装配 / 交易时段退让与 GPU 夜间互斥裁决）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 四职责词表闭合(inference|training|vram_mgmt|model_version); task_id 非空唯一; 优先级[0,40]且40最低; 交易时段 training 挂起退让; GPU 任务须 gpu_schedule 放行(夜间时分互斥); 出队按 (priority,seq) 确定性排序; 同输入必同输出
# [MODIFY-GUARD] docs/03_modules/_domain_infrastructure_runtime/ml_pipeline_process/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] MlPipelineError(占位 ZA-INF-UNREGISTERED-ML-PIPELINE)——空/重复task_id/非法职责/优先级越界/未知任务取消时抛
# [TESTS] tests/infra_runtime/test_ml_pipeline_process.py
# [A_module] module_id=MOD-INF-078 | layer=module | stability=evolving | safety=M | ai_autonomy=human_gated
# [TTL] permanent
"""
MlPipelineProcess — P5 ML 管线进程编排（MOD-INF-078）。

B14-04526（AUD-DRAFT-001-DIGEST P2 波 P2-W01，CAND-H1FS-011，A9 运维架构
§进程拓扑）：ml_pipeline 独立进程 spec 与编排——推理调度/离线训练/显存管理/
模型版本**四职责任务队列**（入队/出队/优先级），核 16-19 + 20GB 预算声明，
优先级 40 全运行时最低、**交易时段资源退让**（注入 is_trading_hours 判定，
盘中 training 任务挂起），**GPU 夜间时分互斥**（注入 gpu_schedule 时段表判
定任务可否占 GPU）。纯编排逻辑 + 注入执行器，不触 OS/网络/子进程。

查重分工（蓝图 §0）：resource_scheduler=三平面资源隔离与统一限流裁决（本件
不做 cgroup 级隔离，仅做 ML 进程内部任务编排）；trainer_base=训练执行体（本
件只做任务排队与时隙裁决，不实现训练）；ha_sla_framework=SLA 健康编排（零
交集）。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: clock 参数
#   fields: 参数 clock（无注解）
#   code: ml_pipeline_process.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: is_trading_hours 参数
#   fields: 参数 is_trading_hours（无注解）
#   code: ml_pipeline_process.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: gpu_schedule 参数
#   fields: 参数 gpu_schedule（无注解）
#   code: ml_pipeline_process.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① MlPipelineProcess
#   name_en: MlPipelineProcess
#   intro: P5 ML 管线进程编排件（四职责队列 + 交易时段退让 + GPU 夜间互斥）。
#   desc: P5 ML 管线进程编排件（四职责队列 + 交易时段退让 + GPU 夜间互斥）。；公共方法（定义序）: resource_declaration, enqueue, dequeue, cancel, pending,…
#   inputs: clock is_trading_hours gpu_schedule
#   outputs: 返回值
#   （注：A1 之后另有 3 个公共定义未列入（含 3 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（4 定义）
#   name_en: public defs
#   intro: MlPipelineProcess
#   downstream: 运行时装配批（P5 ML 管线进程四职责任务队列装配 / 交易时段退让与 GPU 夜间互斥裁决）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# A1 --> O1
"""

from __future__ import annotations

import datetime
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Final

_log = logging.getLogger(__name__)

__all__: Final = [
    "BASE_PRIORITY",
    "DECLARED_CORES",
    "MEMORY_BUDGET_GB",
    "MlPipelineError",
    "MlPipelineProcess",
    "MlTask",
    "TaskKind",
]

#: 资源声明：核 16-19（P5 进程亲和核组）
DECLARED_CORES: Final[tuple[int, ...]] = (16, 17, 18, 19)
#: 资源声明：内存预算上限（GB）
MEMORY_BUDGET_GB: Final[int] = 20
#: 优先级下界（40 = 全运行时最低优先级，数值越大越不紧急）
BASE_PRIORITY: Final[int] = 40


class MlPipelineError(Exception):
    """ML 管线编排输入/状态非法（Fail-Closed）。

    未登记错误码-申请中：占位 ZA-INF-UNREGISTERED-ML-PIPELINE。
    """


class TaskKind(str, Enum):
    """ML 管线四职责（词表闭合）。"""

    INFERENCE = "inference"
    TRAINING = "training"
    VRAM_MGMT = "vram_mgmt"
    MODEL_VERSION = "model_version"


@dataclass(frozen=True)
class MlTask:
    """ML 管线任务（frozen；priority 数值越小越紧急，取值 [0, 40]）。"""

    task_id: str
    kind: TaskKind
    priority: int = BASE_PRIORITY
    requires_gpu: bool = False
    payload: dict = field(default_factory=dict)


class MlPipelineProcess:
    """P5 ML 管线进程编排件（四职责队列 + 交易时段退让 + GPU 夜间互斥）。"""

    def __init__(
        self,
        *,
        clock: Callable[[], datetime.datetime] | None = None,
        is_trading_hours: Callable[[], bool] | None = None,
        gpu_schedule: Callable[[datetime.datetime], bool] | None = None,
    ) -> None:
        self._clock = clock or datetime.datetime.now
        self._is_trading_hours = is_trading_hours or (lambda: False)
        self._gpu_schedule = gpu_schedule or (lambda _now: True)
        self._queue: dict[str, tuple[MlTask, int]] = {}
        self._seq = 0

    # ── 资源声明 ─────────────────────────────────────────────────────────

    @staticmethod
    def resource_declaration() -> dict:
        """进程资源声明（核 16-19 + 20GB + 最低优先级 40，常量表）。"""
        return {
            "cores": DECLARED_CORES,
            "memory_gb": MEMORY_BUDGET_GB,
            "base_priority": BASE_PRIORITY,
        }

    # ── 内部 ─────────────────────────────────────────────────────────────

    def _is_runnable(self, task: MlTask, now: datetime.datetime) -> bool:
        # 交易时段资源退让：training 任务挂起，不抢占 Hot/Warm 平面资源
        if task.kind is TaskKind.TRAINING and self._is_trading_hours():
            return False
        # GPU 夜间时分互斥：时段表未放行的时刻禁止占 GPU
        if task.requires_gpu and not self._gpu_schedule(now):
            return False
        return True

    def _ordered(self) -> list[MlTask]:
        entries = sorted(self._queue.values(), key=lambda e: (e[0].priority, e[1], e[0].task_id))
        return [task for task, _seq in entries]

    # ── 队列协议 ──────────────────────────────────────────────────────────

    def enqueue(self, task: MlTask) -> None:
        """入队：task_id 非空唯一、职责合法、优先级 [0,40]。"""
        if not isinstance(task, MlTask):
            raise MlPipelineError(f"非法任务对象: {type(task)!r}")
        if not task.task_id:
            raise MlPipelineError("task_id 为空")
        if task.task_id in self._queue:
            raise MlPipelineError(f"task_id 重复: {task.task_id!r}")
        if not isinstance(task.kind, TaskKind):
            raise MlPipelineError(f"非法职责: {task.kind!r}")
        if not (0 <= task.priority <= BASE_PRIORITY):
            raise MlPipelineError(f"优先级越界: {task.priority}（合法区间 [0, {BASE_PRIORITY}]，40 最低）")
        self._queue[task.task_id] = (task, self._seq)
        self._seq += 1

    def dequeue(self) -> MlTask | None:
        """出队：取当前可运行任务中 (priority,seq) 最小者；无可运行 → None。"""
        now = self._clock()
        for task in self._ordered():
            if self._is_runnable(task, now):
                del self._queue[task.task_id]
                return task
        _log.debug("无可运行任务（挂起/互斥/空队列），队列深度=%d", len(self._queue))
        return None

    def cancel(self, task_id: str) -> MlTask:
        """取消待办任务（未知 → Fail-Closed）。"""
        entry = self._queue.pop(task_id, None)
        if entry is None:
            raise MlPipelineError(f"未知任务: {task_id!r}")
        return entry[0]

    # ── 查询 ─────────────────────────────────────────────────────────────

    def pending(self, kind: TaskKind | None = None) -> list[MlTask]:
        """待办任务视图（按 (priority,seq) 确定性排序，可按职责过滤）。"""
        if kind is not None and not isinstance(kind, TaskKind):
            raise MlPipelineError(f"非法职责: {kind!r}")
        tasks = self._ordered()
        if kind is not None:
            tasks = [t for t in tasks if t.kind is kind]
        return tasks

    def is_suspended(self, task: MlTask) -> bool:
        """任务当前是否被退让/互斥挂起（交易时段 training / GPU 未放行）。"""
        return not self._is_runnable(task, self._clock())

    def queue_size(self) -> int:
        """队列深度。"""
        return len(self._queue)

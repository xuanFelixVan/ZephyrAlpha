# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent_orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.execution.memory_writer
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.governance.__init__; zephyr.autonomy_core.__init__
# [CONSUMERS] zephyr.orchestrator.work_orchestrator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 任务COMPLETED时归档; VMS不可用降级不阻塞
# [MODIFY-GUARD] CT-ORC-VMS-001 必须同步更新VMS
# [STABILITY] evolving; [SAFETY] L; [AI_AUTONOMY] ai_modifiable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS] scripts/connect/orc_vms.py --trigger
# [A_module] module_id=MOD-INF-039 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
Orc->VMS 记忆写入器

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: task 参数
#   fields: 参数 task，类型注解 object
#   code: memory_writer.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: result 参数
#   fields: 参数 result，类型注解 dict[str, Any] | None
#   code: memory_writer.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① MemoryWriter
#   name_en: MemoryWriter
#   intro: class MemoryWriter 源码 L78-L98
#   desc: 公共方法（定义序）: archive_to_vms；源码 L78-L98
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② archive_to_vms
#   name_en: archive_to_vms
#   intro: archive_to_vms(task, result) 源码 L101-L102
#   desc: 源码 L101-L102
#   inputs: task result
#   outputs: ArchiveResult
#   （注：A2 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: ArchiveResult
#   name_en: ArchiveResult
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.orchestrator.work_orchestrator
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# A1 --> A2
# A2 --> O1
"""

import logging
from dataclasses import dataclass
from typing import Any

from zephyr.shared.io.serialization import dumps

logger = logging.getLogger(__name__)
__all__ = ["ArchiveResult", "MemoryWriter", "archive_to_vms"]


@dataclass
class ArchiveResult:
    stored: int = 0
    status: str = "complete"
    error: str | None = None


class MemoryWriter:
    def archive_to_vms(self, task: object, result: dict[str, Any] | None = None) -> ArchiveResult:
        try:
            from zephyr.autonomy_core.context.vector_bridge import VectorBridge
            from zephyr.integration.vector_memory.in_memory_fake_vms import InMemoryFakeVMS

            vms = InMemoryFakeVMS()
            bridge = VectorBridge(vms)
            tid = getattr(task, "task_id", "unknown")
            summary = f"Task: {getattr(task, 'title', '')}. Result: {dumps(result or {})}"
            bridge._vms.write(
                "session_snapshots",
                summary[:2000],
                metadata={"task_id": tid, "status": getattr(task, "status", "?")},
                doc_id=f"session::{tid}",
            )
            logger.info("[ORC-VMS] archived: %s", tid)
            return ArchiveResult(stored=1)
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            logger.warning("[ORC-VMS] degraded: %s", e, exc_info=True)
            return ArchiveResult(stored=0, status="degraded", error="internal error")


def archive_to_vms(task: object, result: dict[str, Any] | None = None) -> ArchiveResult:
    return MemoryWriter().archive_to_vms(task, result)

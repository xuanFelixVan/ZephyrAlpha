"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: teardown_manager.py
# 层: 算法
# - id: A1
#   name_zh: ① TeardownManager
#   name_en: TeardownManager
#   intro: class TeardownManager 源码 L81-L106
#   desc: 公共方法（定义序）: teardown, get_records；源码 L81-L106
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: TeardownManager
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from typing import Final

# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.lifecycle.teardown_manager
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.orchestrator.__init__
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
# [A_module] module_id=MOD-INF-039 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
资源清理管理器（Teardown Manager — CT-TEARDOWN-001）

依据：MOD-MASTER-002 蓝图 §十六
TaskCard CANCELLED/FAILED -> 7系统资源清理。
"""

from datetime import UTC, datetime

from pydantic import BaseModel


class CleanupTarget(BaseModel):
    system: str
    resource_type: str = ""
    resource_id: str = ""
    status: str = "pending"


CLEANUP_SYSTEMS: Final[list[str]] = [
    "orchestrator",
    "context-engine",
    "gate_engine",
    "vector-memory",
    "database",
    "feedback-loop",
    "system-telemetry",
]


class TeardownManager:
    def __init__(self):
        self._cleanup_records: list[dict] = []

    def teardown(self, task_id: str, reason: str) -> list[CleanupTarget]:
        targets: list[CleanupTarget] = []
        for system in CLEANUP_SYSTEMS:
            target = CleanupTarget(
                system=system,
                resource_type="task_context",
                resource_id=task_id,
                status="cleaned",
            )
            targets.append(target)
        self._cleanup_records.append(
            {
                "task_id": task_id,
                "reason": reason,
                "targets": len(targets),
                "timestamp": datetime.now(UTC),
            }
        )
        return targets

    def get_records(self) -> list[dict]:
        return list(self._cleanup_records)

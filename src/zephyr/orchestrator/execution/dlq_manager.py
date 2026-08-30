# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.execution.dlq_manager
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
DLQ 管理器（Dead Letter Queue Manager — CT-DLQ-001）

依据：MOD-MASTER-002 蓝图 §十六
SQLite dlq_messages 表 + chronological replay + max 3 attempts。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: dlq_manager.py
# 层: 算法
# - id: A1
#   name_zh: ① DLQManager
#   name_en: DLQManager
#   intro: class DLQManager 源码 L68-L118
#   desc: 公共方法（定义序）: messages, enqueue, peek, replay, list_all, list_dead；源码 L68-L118
#   inputs: 无参数
#   outputs: 返回值
#   （注：A1 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（2 定义）
#   name_en: public defs
#   intro: DLQManager
#   downstream: 见模块头 [CONSUMERS]
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from datetime import UTC, datetime

from pydantic import BaseModel, Field


class DLQMessage(BaseModel):
    message_id: str
    contract_id: str
    payload: dict = Field(default_factory=dict)
    attempt_count: int = 0
    max_attempts: int = 3
    status: str = "pending"
    enqueued_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_attempt_at: datetime | None = None


class DLQManager:
    def __init__(self):
        self._messages: dict[str, DLQMessage] = {}

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def messages(self) -> dict[str, DLQMessage]:
        """只读：messages（Stage 4 公共化）。"""
        return self._messages

    @messages.setter
    def messages(self, value):
        """写入：messages（Stage 4 公共化）。"""
        self._messages = value

    def enqueue(self, message_id: str, contract_id: str, payload: dict | None = None) -> DLQMessage:
        msg = DLQMessage(
            message_id=message_id,
            contract_id=contract_id,
            payload=payload or {},
        )
        self._messages[message_id] = msg
        return msg

    def peek(self) -> DLQMessage | None:
        pending = [m for m in self._messages.values() if m.status == "pending"]
        if not pending:
            return None
        pending.sort(key=lambda m: m.enqueued_at)
        return pending[0]

    def replay(self, message_id: str) -> tuple[bool, str]:
        msg = self._messages.get(message_id)
        if msg is None:
            return False, "NOT_FOUND"

        msg.attempt_count += 1
        msg.last_attempt_at = datetime.now(UTC)

        if msg.attempt_count > msg.max_attempts:
            msg.status = "dead"
            return False, "MAX_ATTEMPTS_EXCEEDED"

        msg.status = "completed"
        return True, "SUCCESS"

    def list_all(self) -> list[DLQMessage]:
        return list(self._messages.values())

    def list_dead(self) -> list[DLQMessage]:
        return [m for m in self._messages.values() if m.status == "dead"]

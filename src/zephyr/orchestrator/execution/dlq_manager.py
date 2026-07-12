# [BLUEPRINT] MOD-INF-039 | docs/03_modules/_cross_layer/agent-orchestrator/blueprint.md
# [MODULE] zephyr.orchestrator.execution.dlq_manager
# [DOMAIN] D_ORCHESTRATOR
# [DEPENDENCIES] zephyr.orchestrator.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-ORC_dlq_manager | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
DLQ 管理器（Dead Letter Queue Manager — CT-DLQ-001）

依据：MOD-MASTER-002 蓝图 §十六
SQLite dlq_messages 表 + chronological replay + max 3 attempts。
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

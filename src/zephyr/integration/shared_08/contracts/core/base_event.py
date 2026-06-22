# [A_module] module_id=MOD-INT_base_event | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
from __future__ import annotations

# [BLUEPRINT] SRC-159 | docs/03_modules/_cross_layer/shared-core/contracts_blueprint.md
# [MODULE] zephyr.integration.shared_08.contracts.core.base_event
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [CONSUMERS]
# [STABILITY] stable
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class BaseEvent:
    idempotency_key: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    trace_id: str | None = None
    schema_version: str = "1.0"

    def __post_init__(self) -> None:
        valid, error = BaseEvent.validate_idempotency_key(self.idempotency_key)
        if not valid:
            raise ValueError(f"idempotency_key 校验失败: {error}")

    @property
    def is_replay(self) -> bool:
        return False

    @staticmethod
    def validate_idempotency_key(key: str) -> tuple[bool, str | None]:
        if not key:
            return False, "idempotency_key 不能为空"
        if not isinstance(key, str):
            return False, f"idempotency_key 必须是 str，收到 {type(key).__name__}"
        try:
            uuid.UUID(key)
            return True, None
        except ValueError:
            return False, f"idempotency_key 不是合法的 UUID: {key}"

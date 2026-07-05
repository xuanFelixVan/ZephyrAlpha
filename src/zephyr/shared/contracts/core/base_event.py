# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §
# [MODULE] zephyr.shared.contracts.core.base_event
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] shared.infra.outbox
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-SHR_base_event | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""BaseEvent — 跨层事件基类

INV-007 要求所有跨层事件必须携带幂等 Key。
本基类提供统一的 idempotency_key 生成与校验能力。

所有 CTR 数据契约（CTR-001~006, CTR-ERR-*, CTR-BP-*）的 Python dataclass
在生产时应通过 codegen 注入基于本基类的字段校验逻辑。

用法：
  from zephyr.shared.contracts.core.base_event import BaseEvent, generate_idempotency_key

  event_key = generate_idempotency_key()
  assert len(event_key) == 36  # UUID v4
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime


def generate_idempotency_key() -> str:
    return str(uuid.uuid4())


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


class BaseEvent:
    idempotency_key: str
    created_at: datetime
    trace_id: str | None = None
    schema_version: str = "1.0"

    def __post_init__(self) -> None:
        if not hasattr(self, "idempotency_key") or not self.idempotency_key:
            self.idempotency_key = generate_idempotency_key()
        if not hasattr(self, "created_at") or not self.created_at:
            self.created_at = datetime.now(UTC)

        valid, error = validate_idempotency_key(self.idempotency_key)
        if not valid:
            raise ValueError(f"idempotency_key 校验失败: {error}")

    @property
    def is_replay(self) -> bool:
        """子类可重写以实现去重逻辑"""
        return False

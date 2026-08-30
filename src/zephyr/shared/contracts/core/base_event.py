# [BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain_infrastructure_runtime/runtime_integration/blueprint.md | §
# [MODULE] zephyr.shared.contracts.core.base_event
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] N/A (all consumers verified as phantom — stale references removed)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-002 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
BaseEvent — 跨层事件基类

INV-007 要求所有跨层事件必须携带幂等 Key。
本基类提供统一的 idempotency_key 生成与校验能力。

所有 CTR 数据契约（CTR-001~006, CTR-ERR-*, CTR-BP-*）的 Python dataclass
在生产时应通过 codegen 注入基于本基类的字段校验逻辑。

用法：
  from zephyr.shared.contracts.core.base_event import BaseEvent, generate_idempotency_key

  event_key = generate_idempotency_key()
  assert len(event_key) == 36  # UUID v4

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: key 参数
#   fields: 参数 key，类型注解 str
#   code: base_event.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① generate_idempotency_key
#   name_en: generate_idempotency_key
#   intro: generate_idempotency_key() 源码 L87-L88
#   desc: 源码 L87-L88
#   inputs: 无参数
#   outputs: str
# - id: A2
#   name_zh: ② validate_idempotency_key
#   name_en: validate_idempotency_key
#   intro: validate_idempotency_key(key) 源码 L91-L100
#   desc: 源码 L91-L100
#   inputs: key
#   outputs: tuple[bool, str | None]
# - id: A3
#   name_zh: ③ BaseEvent
#   name_en: BaseEvent
#   intro: class BaseEvent 源码 L103-L122
#   desc: 公共方法（定义序）: is_replay；源码 L103-L122
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: str
#   name_en: str
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: N/A (all consumers verified as phantom — stale references removed)
# - id: O2
#   name_zh: tuple[bool, str | None]
#   name_en: tuple[bool, str | None]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: N/A (all consumers verified as phantom — stale references removed)
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
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

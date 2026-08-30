# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.lifecycle.ttl_cleanup_engine
# [DOMAIN] D_SHARED
# [DEPENDENCIES]
# [CONSUMERS] zephyr.infrastructure.capacity_assurance.modules.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-016 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: default_ttl 参数
#   fields: 参数 default_ttl（无注解）
#   code: ttl_cleanup_engine.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① TtlCleanupEngine
#   name_en: TtlCleanupEngine
#   intro: class TtlCleanupEngine 源码 L67-L86
#   desc: 公共方法（定义序）: register, is_expired, cleanup；源码 L67-L86
#   inputs: default_ttl
#   outputs: 返回值
#   （注：A1 之后另有 2 个公共定义未列入（含 2 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（3 定义）
#   name_en: public defs
#   intro: TtlCleanupEngine
#   downstream: zephyr.infrastructure.capacity_assurance.modules.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import time
from dataclasses import dataclass


@dataclass
class TtlEntry:
    key: str
    created_at: float
    ttl_seconds: float


@dataclass
class CleanupResult:
    expired_count: int
    remaining_count: int


class TtlCleanupEngine:
    def __init__(self, default_ttl: float = 1800.0):
        self._default_ttl = default_ttl
        self._entries: dict[str, TtlEntry] = {}

    def register(self, key: str, ttl_seconds: float | None = None) -> None:
        self._entries[key] = TtlEntry(key, time.time(), ttl_seconds or self._default_ttl)

    def is_expired(self, key: str) -> bool:
        entry = self._entries.get(key)
        if not entry:
            return True
        return (time.time() - entry.created_at) > entry.ttl_seconds

    def cleanup(self) -> CleanupResult:
        now = time.time()
        expired = [k for k, v in self._entries.items() if (now - v.created_at) > v.ttl_seconds]
        for k in expired:
            del self._entries[k]
        return CleanupResult(len(expired), len(self._entries))

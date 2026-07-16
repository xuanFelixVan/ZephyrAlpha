# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_idempotency
# [DOMAIN] D_AUTONOMY_CORE
# [DEPENDENCIES] zephyr.autonomy_core.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-INF-019 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Idempotency
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.2.0

Skill 幂等性保证 —— 防止同一 Skill 在相同输入下重复执行。
使用 sha256(input_hash) + skill_id 作为去重键，带 TTL 过期。
"""

from __future__ import annotations

import hashlib
import time


class SkillIdempotency:
    """Skill 幂等性保证 —— 重复执行安全."""

    _execution_history: dict[str, tuple[str, float]] = {}
    _DEFAULT_TTL_S = 3600.0

    @classmethod
    def hash_input(cls, data: str) -> str:
        return hashlib.sha256(data.encode("utf-8")).hexdigest()[:16]

    @classmethod
    def is_duplicate(cls, skill_id: str, input_hash: str, ttl_s: float | None = None) -> bool:
        key = f"{skill_id}:{input_hash}"
        ttl = ttl_s or cls._DEFAULT_TTL_S

        if key in cls._execution_history:
            result, timestamp = cls._execution_history[key]
            if time.time() - timestamp < ttl:
                return True
            del cls._execution_history[key]
            return False

        cls._execution_history[key] = ("executed", time.time())
        return False

    @classmethod
    def mark_executed(cls, skill_id: str, input_hash: str, result: str = "executed"):
        key = f"{skill_id}:{input_hash}"
        cls._execution_history[key] = (result, time.time())

    @classmethod
    def clear_expired(cls, ttl_s: float | None = None):
        ttl = ttl_s or cls._DEFAULT_TTL_S
        now = time.time()
        expired = [k for k, (_, ts) in cls._execution_history.items() if now - ts >= ttl]
        for k in expired:
            del cls._execution_history[k]

    @classmethod
    def clear_all(cls):
        cls._execution_history.clear()

    @classmethod
    def stats(cls) -> dict[str, int]:
        cls.clear_expired()
        return {"active_entries": len(cls._execution_history)}

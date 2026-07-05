# [BLUEPRINT] MOD-INF-019 | docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md
# [MODULE] zephyr.autonomy_core.skills.skill_prompt_cache
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
# [A_module] module_id=MOD-ORC_skill_prompt_cache | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
MOD-INF-019: Agent Spec — Skill Prompt Cache
Blueprint: docs/03_modules/_domain-autonomy_core/agent-spec/blueprint.md
Author: factory-agent
Version: 0.3.0

Skill Prompt 缓存——减少重复 LLM 调用，带 TTL 过期.
"""

from __future__ import annotations

import hashlib
import time
from typing import Any


class SkillPromptCache:
    """Skill Prompt 缓存——减少重复 LLM 调用."""

    _cache: dict[str, tuple[str, float]] = {}
    _DEFAULT_TTL_S = 3600.0
    _MAX_SIZE = 200

    @classmethod
    def key_for(cls, skill_id: str, input_data: str) -> str:
        digest = hashlib.sha256(input_data.encode("utf-8")).hexdigest()[:16]
        return f"{skill_id}:{digest}"

    @classmethod
    def get(cls, skill_id: str, input_hash: str) -> str | None:
        key = f"{skill_id}:{input_hash}"
        entry = cls._cache.get(key)
        if entry is None:
            return None
        response, expiry = entry
        if time.time() > expiry:
            del cls._cache[key]
            return None
        return response

    @classmethod
    def set(cls, skill_id: str, input_hash: str, response: str, ttl_s: float | None = None) -> None:
        key = f"{skill_id}:{input_hash}"
        expiry = time.time() + (ttl_s or cls._DEFAULT_TTL_S)
        cls._cache[key] = (response, expiry)
        if len(cls._cache) > cls._MAX_SIZE:
            cls.purge_expired()

    @classmethod
    def invalidate(cls, skill_id: str):
        keys = [k for k in cls._cache if k.startswith(f"{skill_id}:")]
        for k in keys:
            del cls._cache[k]

    @classmethod
    def purge_expired(cls) -> int:
        now = time.time()
        expired = [k for k, (_, e) in cls._cache.items() if now > e]
        for k in expired:
            del cls._cache[k]
        return len(expired)

    @classmethod
    def stats(cls) -> dict[str, Any]:
        cls.purge_expired()
        return {"total_entries": len(cls._cache), "max_size": cls._MAX_SIZE}

    @classmethod
    def clear(cls):
        cls._cache.clear()


__all__ = ["SkillPromptCache"]

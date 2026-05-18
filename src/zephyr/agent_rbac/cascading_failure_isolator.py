# [BLUEPRINT] MOD-INF-018 | 03_modules/l01_infrastructure/agent-rbac/blueprint.md | §

# [MODULE] zephyr.agent_rbac.cascading_failure_isolator

# [INVARIANTS] none

# [MODIFY-GUARD] none

# [CONSUMERS]

# [STABILITY] evolving

# [SAFETY] L

# [AI_AUTONOMY] ai_modifiable

# [ERROR_CONTRACT]

# [TESTS]

"""级联故障隔离——单个权限模块故障不得扩散到其他模块."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ModuleHealth(BaseModel):
    module_name: str
    healthy: bool = True
    failure_count: int = 0
    last_error: str = ""
    isolation_active: bool = False


class CascadingFailureIsolator:
    _MAX_FAILURES: int = 3

    def __init__(self) -> None:
        self._modules: dict[str, ModuleHealth] = {}
        self._isolated: set[str] = set()

    def register(self, module_name: str) -> ModuleHealth:
        mh = ModuleHealth(module_name=module_name)
        self._modules[module_name] = mh
        return mh

    def record_failure(self, module_name: str, error: str = "") -> dict[str, Any]:
        if module_name not in self._modules:
            self.register(module_name)

        mh = self._modules[module_name]
        mh.failure_count += 1
        mh.last_error = error

        if mh.failure_count >= self._MAX_FAILURES:
            mh.healthy = False
            mh.isolation_active = True
            self._isolated.add(module_name)
            return {"isolated": True, "module": module_name, "failures": mh.failure_count}

        return {"isolated": False, "module": module_name, "failures": mh.failure_count}

    def is_healthy(self, module_name: str) -> bool:
        mh = self._modules.get(module_name)
        return mh is not None and mh.healthy

    def get_isolated(self) -> list[str]:
        return list(self._isolated)

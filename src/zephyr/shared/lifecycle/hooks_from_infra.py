# [BLUEPRINT] SRC-109 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.infrastructure.shared_services.lifecycle.hooks
# [DOMAIN] D-INFRA_RUNTIME
# [DEPENDENCIES] zephyr.shared.lifecycle.__init__
# [CONSUMERS] zephyr.trading; zephyr.integration; zephyr.autonomy_core
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] must be thread-safe; must not block main loop; Protocol-based lightweight design
# [MODIFY-GUARD] resource_optimization_engine.py; resource_optimization_models.py; daemon_registry.py
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] re-raises Exception on init/startup failure
# [TESTS] tests/lifecycle_manager/test_hooks.py
# [A_module] module_id=MOD-INF_hooks | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable

"""[BLUEPRINT] MOD-INF-002 | docs/03_modules/_domain-infra_runtime/runtime-integration/blueprint.md | §

hooks.py — Module lifecycle hooks

Design:

  - Protocol instead of ABC — lightweight, non-intrusive

  - Optional implementation — modules don't need all hooks

  - State queryable — at any time can ask "is module ready?"

SSoT: MOD-INF-016 §2.7 shared-lifecycle

Version: 0.1.0

"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum, unique
from typing import Any, Protocol, runtime_checkable

__all__ = [
    "LifecycleAware",
    "LifecycleManager",
    "LifecycleState",
    "ModuleHealth",
]


logger = logging.getLogger(__name__)


@unique
class LifecycleState(str, Enum):
    CREATED = "CREATED"

    INITIALIZING = "INITIALIZING"

    INITIALIZED = "INITIALIZED"

    STARTING = "STARTING"

    RUNNING = "RUNNING"

    DEGRADED = "DEGRADED"

    STOPPING = "STOPPING"

    STOPPED = "STOPPED"

    FAILED = "FAILED"


@dataclass(frozen=True)
class ModuleHealth:
    module_name: str

    state: LifecycleState

    healthy: bool

    message: str = ""

    details: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class LifecycleAware(Protocol):
    @property
    def module_name(self) -> str: ...

    async def on_init(self) -> None:
        pass

    async def on_startup(self) -> None:
        pass

    async def on_shutdown(self) -> None:
        pass

    async def health_check(self) -> ModuleHealth:
        pass


class LifecycleManager:
    def __init__(self) -> None:
        self._modules: list[LifecycleAware] = []

    def register(self, module: LifecycleAware) -> None:
        self._modules.append(module)

    @property
    def modules(self) -> list[LifecycleAware]:
        return list(self._modules)

    async def startup_all(self) -> None:
        for mod in self._modules:
            try:
                await mod.on_init()

                logger.info("module '%s': init OK", mod.module_name)

            except Exception as exc:
                logger.error("module '%s': init FAILED: %s", mod.module_name, exc)

                raise

        for mod in self._modules:
            try:
                await mod.on_startup()

                logger.info("module '%s': startup OK", mod.module_name)

            except Exception as exc:
                logger.error("module '%s': startup FAILED: %s", mod.module_name, exc)

                raise

    async def shutdown_all(self) -> None:
        for mod in reversed(self._modules):
            try:
                await mod.on_shutdown()

                logger.info("module '%s': shutdown OK", mod.module_name)

            except Exception as exc:
                logger.error("module '%s': shutdown FAILED: %s", mod.module_name, exc)

    async def health_check_all(self) -> dict[str, ModuleHealth]:
        results: dict[str, ModuleHealth] = {}

        for mod in self._modules:
            try:
                results[mod.module_name] = await mod.health_check()

            except Exception as exc:
                results[mod.module_name] = ModuleHealth(
                    module_name=mod.module_name,
                    state=LifecycleState.FAILED,
                    healthy=False,
                    message=str(exc),
                )

        return results

# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md | §
# [MODULE] zephyr.shared.lifecycle.hooks
# [DOMAIN] D_INFRA_RUNTIME
# [DEPENDENCIES]
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
# [A_module] module_id=MOD-SHR_hooks | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
hooks.py —— 模块生命周期钩子（Phase 2 新增 | 盲点 B8 修复）

痛点修复：当前模块启动/初始化/关闭没有统一契约——
  1. 模块在 __init__.py 隐式执行初始化（不可控、不可测）
  2. 模块之间不知道彼此的初始化顺序
  3. 没有统一的健康检查接口——运维不知道哪出问题了

设计对标：
  - Spring Boot ApplicationListener / Lifecycle
  - K8s startupProbe + readinessProbe + livenessProbe
  - FastAPI lifespan context manager

设计原则：
  - Protocol 而非 ABC——轻量、无侵入
  - 可选实现——模块不需全部钩子
  - 状态可查询——任何时刻可问「模块是否就绪」

AI 施工约定：
  - 每个模块 SHOULD 实现 LifecycleAware（至少 health_check）
  - __init__.py 中禁止隐式执行非导入代码——改为 on_init
  - LifecycleManager 负责按依赖顺序调用钩子

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
    """模块生命周期协议——零侵入式。

    各钩子均为可选实现。LifecycleManager 会按顺序调用。
    """

    @property
    def module_name(self) -> str: ...

    async def on_init(self) -> None:
        """模块初始化——资源创建、配置加载。"""

    async def on_startup(self) -> None:
        """系统启动——建立连接、注册到总线、启动后台任务。"""

    async def on_shutdown(self) -> None:
        """系统关闭——释放连接、取消任务、持久化状态。"""

    def health_check(self) -> ModuleHealth:
        """健康检查——返回模块当前状态。

        5.12.2#4 签名漂移治本（2026-07-03）：从 async def 改为 def（sync）。
        全部 28 个具体实现均为 sync，原 async 声明是接口契约违反。
        LifecycleManager.health_check_all 已同步去掉 await。
        """


class LifecycleManager:
    """模块生命周期编排器。

    Usage::

        mgr = LifecycleManager()
        mgr.register(db_module)
        mgr.register(context-engine)
        await mgr.startup_all()    # 按注册顺序初始化 + 启动
        ...
        await mgr.shutdown_all()   # 反向关闭
    """

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
                results[mod.module_name] = mod.health_check()
            except Exception as exc:
                results[mod.module_name] = ModuleHealth(
                    module_name=mod.module_name,
                    state=LifecycleState.FAILED,
                    healthy=False,
                    message=str(exc),
                )
        return results

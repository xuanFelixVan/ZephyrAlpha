# [BLUEPRINT] SRC-079 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.protocols.registry
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.__init__
# [CONSUMERS] zephyr.infrastructure_runtime_integration; zephyr.infrastructure.mcp_servers
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] ServiceRegistry is process-singleton; register() MUST be called before get(); no import from zephyr.data
# [MODIFY-GUARD] Adding service keys requires updating D-DATA registration and D-INFRA consumers
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] KeyError on unregistered service; TypeError on factory returning wrong type
# [TESTS] tests/utils/test_shared_core.py
# [A_module] module_id=MOD-INF_registry | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
registry — 运行时 DI 容器
=========================
D-DATA 在初始化时注册实现，D-INFRA 通过 get() 获取。
消除 D-INFRA→D-DATA 的 import 依赖。
"""

from __future__ import annotations

import logging
import threading
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)

_VALID_KEYS = frozenset(
    {
        "task_repo",
        "db_connection",
        "db_path",
        "vector-memory",
        "chromadb_client",
        "reranker",
        "collection_schemas",
    }
)


class ServiceRegistry:
    """进程级单例服务注册表。

    D-DATA 调用 register() 注册工厂函数；
    D-INFRA 调用 get() 获取实现实例。
    线程安全（RLock 保护）。
    """

    _lock = threading.RLock()
    _factories: dict[str, Callable[[], Any]] = {}
    _instances: dict[str, Any] = {}

    @classmethod
    def register(cls, key: str, factory: Callable[[], Any]) -> None:
        """注册服务工厂。factory 必须是无参可调用对象。"""
        if key not in _VALID_KEYS:
            raise KeyError(f"Invalid service key '{key}'. Valid keys: {sorted(_VALID_KEYS)}")
        with cls._lock:
            cls._factories[key] = factory
            cls._instances.pop(key, None)
            logger.debug("ServiceRegistry: registered '%s'", key)

    @classmethod
    def get(cls, key: str) -> Any:
        """获取服务实例（首次调用时惰性创建）。"""
        if key not in _VALID_KEYS:
            raise KeyError(f"Invalid service key '{key}'. Valid keys: {sorted(_VALID_KEYS)}")
        with cls._lock:
            if key in cls._instances:
                return cls._instances[key]
            if key not in cls._factories:
                raise KeyError(
                    f"Service '{key}' not registered. Call ServiceRegistry.register('{key}', factory) first."
                )
            instance = cls._factories[key]()
            cls._instances[key] = instance
            logger.debug("ServiceRegistry: created instance for '%s'", key)
            return instance

    @classmethod
    def is_registered(cls, key: str) -> bool:
        """检查服务是否已注册。"""
        return key in cls._factories

    @classmethod
    def reset(cls) -> None:
        """清空所有注册（仅用于测试）。"""
        with cls._lock:
            cls._factories.clear()
            cls._instances.clear()

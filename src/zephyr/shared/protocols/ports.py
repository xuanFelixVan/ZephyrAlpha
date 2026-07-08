# [BLUEPRINT] SRC-078 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.protocols.ports
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.contracts.task_repository_protocol
# [CONSUMERS] zephyr.infrastructure_runtime_integration; zephyr.infrastructure.mcp_servers
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] Protocol classes MUST NOT import from zephyr.data; only structural subtyping
# [MODIFY-GUARD] Adding methods to Protocol requires updating all implementors in zephyr.data
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] TypeError if runtime implementation does not satisfy Protocol
# [TESTS] tests/utils/test_shared_core.py
# [A_module] module_id=MOD-INF_ports | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ports — D-DATA 服务的 Protocol 定义
===================================
D-INFRA 通过 Protocol 引用 D-DATA 的实现（结构化子类型），
消除 D-INFRA->D-DATA 的直接 import 依赖。
运行时通过 ServiceRegistry 获取具体实现。
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Protocol, runtime_checkable

from zephyr.shared.contracts.task_repository_protocol import TaskRepositoryProtocol  # noqa: F401 — re-export


@runtime_checkable
class DbConnectionProvider(Protocol):
    """数据库连接提供者 Protocol — D-INFRA 通过此接口获取 DB 连接和路径。"""

    @property
    def db_path(self) -> Path: ...

    def get_connection(self) -> sqlite3.Connection: ...


@runtime_checkable
class VectorMemoryProtocol(Protocol):
    """向量内存服务 Protocol — D-INFRA MCP 服务器通过此接口访问 VMS。"""

    def search(self, collection: str, query_text: str, k: int = 5) -> list[dict[str, Any]]: ...

    def add(self, collection: str, content: str, metadata: dict[str, Any] | None = None) -> str: ...

    def init_all_collections(self) -> None: ...

    def start(self) -> None: ...


@runtime_checkable
class ChromaDbProvider(Protocol):
    """ChromaDB 客户端提供者 Protocol。"""

    def get_client(self) -> Any: ...


@runtime_checkable
class RerankerProtocol(Protocol):
    """重排序器 Protocol。"""

    def rerank(self, query: str, documents: list[str]) -> list[Any]: ...


@runtime_checkable
class CollectionSchemaProvider(Protocol):
    """向量集合 Schema 提供者 Protocol。"""

    @property
    def schemas(self) -> dict[str, dict[str, Any]]: ...

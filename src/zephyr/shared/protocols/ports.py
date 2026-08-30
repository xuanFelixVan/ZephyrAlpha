# [BLUEPRINT] MOD-SHARED-001 | docs/03_modules/_cross_layer/shared-core/governance_core_blueprint.md
# [MODULE] zephyr.shared.protocols.ports
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.contracts.task_repository_protocol
# [CONSUMERS] zephyr.infrastructure.mcp_servers
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Protocol classes MUST NOT import from zephyr.data; only structural subtyping
# [MODIFY-GUARD] Adding methods to Protocol requires updating all implementors in zephyr.data
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] TypeError if runtime implementation does not satisfy Protocol
# [TESTS] tests/utils/test_shared_core.py
# [A_module] module_id=MOD-SHARED-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
ports — D-DATA 服务的 Protocol 定义
===================================
D-INFRA 通过 Protocol 引用 D-DATA 的实现（结构化子类型），
消除 D-INFRA->D-DATA 的直接 import 依赖。
运行时通过 ServiceRegistry 获取具体实现。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: ports.py
# 层: 算法
# - id: A1
#   name_zh: ① DbConnectionProvider
#   name_en: DbConnectionProvider
#   intro: 数据库连接提供者 Protocol — D-INFRA 通过此接口获取 DB 连接和路径。
#   desc: 数据库连接提供者 Protocol — D-INFRA 通过此接口获取 DB 连接和路径。；公共方法（定义序）: db_path, get_connection；源码 L94-L100
#   inputs: 无参数
#   outputs: 返回值
# - id: A2
#   name_zh: ② VectorMemoryProtocol
#   name_en: VectorMemoryProtocol
#   intro: 向量内存服务 Protocol — D-INFRA MCP 服务器通过此接口访问 VMS。
#   desc: 向量内存服务 Protocol — D-INFRA MCP 服务器通过此接口访问 VMS。；公共方法（定义序）: search, add, init_all_collections, start；源码 L104-L113
#   inputs: 无参数
#   outputs: 返回值
# - id: A3
#   name_zh: ③ ChromaDbProvider
#   name_en: ChromaDbProvider
#   intro: ChromaDB 客户端提供者 Protocol。
#   desc: ChromaDB 客户端提供者 Protocol。；公共方法（定义序）: get_client；源码 L117-L120
#   inputs: 无参数
#   outputs: 返回值
# - id: A4
#   name_zh: ④ RerankerProtocol
#   name_en: RerankerProtocol
#   intro: 重排序器 Protocol。
#   desc: 重排序器 Protocol。；公共方法（定义序）: rerank；源码 L124-L127
#   inputs: 无参数
#   outputs: 返回值
# - id: A5
#   name_zh: ⑤ CollectionSchemaProvider
#   name_en: CollectionSchemaProvider
#   intro: 向量集合 Schema 提供者 Protocol。
#   desc: 向量集合 Schema 提供者 Protocol。；公共方法（定义序）: schemas；源码 L131-L135
#   inputs: 无参数
#   outputs: 返回值
# 层: 输出
# - id: O1
#   name_zh: 模块公共 API 面（5 定义）
#   name_en: public defs
#   intro: DbConnectionProvider, VectorMemoryProtocol, ChromaDbProvider, RerankerProtocol,…
#   downstream: zephyr.infrastructure.mcp_servers
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> O1
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

    def get_client(self) -> object: ...


@runtime_checkable
class RerankerProtocol(Protocol):
    """重排序器 Protocol。"""

    def rerank(self, query: str, documents: list[str]) -> list[Any]: ...


@runtime_checkable
class CollectionSchemaProvider(Protocol):
    """向量集合 Schema 提供者 Protocol。"""

    @property
    def schemas(self) -> dict[str, dict[str, Any]]: ...

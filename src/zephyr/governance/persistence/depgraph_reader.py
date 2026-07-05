# [BLUEPRINT] SH-DB-001 | docs/03_modules/_cross_layer/database/blueprint.md
# [MODULE] zephyr.governance.persistence.depgraph_reader
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT]
# [TESTS]
# [TTL] permanent
"""
depgraph_reader.py — 依赖图数据库查询工具模块

[BLUEPRINT] DM-100030 | src/zephyr/governance/depgraph_reader.py | §30
[MODULE] zephyr.data.depgraph_reader
[INVARIANTS] 只读查询; 参数化防注入; 结果缓存
[MODIFY-GUARD] 修改需同步更新 tests/test_depgraph_reader.py
[CONSUMERS] scripts/governance/; src/zephyr/governance/
[STABILITY] stable
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] FileNotFoundError; sqlite3.Error
[TESTS] tests/test_depgraph_db.py

提供从 depgraph 读取依赖图数据的统一接口，
替代直接解析 61MB+191MB YAML 文件的方式。

使用方式：
    from zephyr.governance.persistence.depgraph_reader import DepgraphReader
    reader = DepgraphReader()
    nodes = reader.get_nodes_by_domain('D_FACTOR')
    edges = reader.get_edges_from_node('some_node_id')
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection


class _PgConnExecuteWrapper:
    """兼容 sqlite3.Connection.execute() 接口的 psycopg2 connection 包装器。

    P2迁移后：psycopg2 connection 没有 execute() 方法，此包装器使原 SQLite 代码无需修改。
    每次调用 execute() 创建一个新的 RealDictCursor（与原 sqlite3.Row 的 dict(row) 用法等价）。
    """

    def __init__(self, pg_conn: psycopg2.extensions.connection) -> None:
        self._pg_conn = pg_conn

    def execute(self, sql: str, params: tuple = ()) -> Any:
        cur = self._pg_conn.cursor(cursor_factory=RealDictCursor)
        cur.execute(sql, params)
        return cur

    def close(self) -> None:
        self._pg_conn.close()


class DepgraphReader:
    """依赖图数据库读取器"""

    def __init__(self, db_path: str | Path | None = None):
        # db_path 参数保留向后兼容（P2迁移后 PG 连接配置由 depgraph_schema.get_depgraph_pg_connection 管理）
        # 治本（2026-06-27）：不再保存 DB_PATH 常量，防止路径污染
        self._conn: _PgConnExecuteWrapper | None = None

    def _get_conn(self) -> _PgConnExecuteWrapper:
        if self._conn is None:
            self._conn = _PgConnExecuteWrapper(get_depgraph_pg_connection(autocommit=True))
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __enter__(self) -> DepgraphReader:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    # ── 节点查询 ──────────────────────────────────────────────

    def get_nodes_by_domain(self, domain_id: str) -> list[dict[str, Any]]:
        """按 domain_id 查询节点"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM nodes WHERE domain_id = %s", (domain_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_nodes_by_type(self, node_type: str) -> list[dict[str, Any]]:
        """按 node_type 查询节点"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM nodes WHERE node_type = %s", (node_type,))
        return [dict(row) for row in cursor.fetchall()]

    def get_node_by_path(self, path: str) -> dict[str, Any] | None:
        """按 path 精确查询节点"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM nodes WHERE path = %s", (path,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_node_by_id(self, node_id: str) -> dict[str, Any] | None:
        """按 node_id 精确查询节点"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM nodes WHERE node_id = %s", (node_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_all_nodes(self) -> list[dict[str, Any]]:
        """获取所有节点"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM nodes")
        return [dict(row) for row in cursor.fetchall()]

    # ── 边查询 ────────────────────────────────────────────────

    def get_edges_from_node(self, from_node: str) -> list[dict[str, Any]]:
        """查询从指定节点出发的所有边"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM edges WHERE from_node = %s", (from_node,))
        return [dict(row) for row in cursor.fetchall()]

    def get_edges_to_node(self, to_node: str) -> list[dict[str, Any]]:
        """查询指向指定节点的所有边"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM edges WHERE to_node = %s", (to_node,))
        return [dict(row) for row in cursor.fetchall()]

    def get_edges_by_type(self, edge_type: str) -> list[dict[str, Any]]:
        """按 edge_type 查询边"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM edges WHERE edge_type = %s", (edge_type,))
        return [dict(row) for row in cursor.fetchall()]

    def get_all_edges(self) -> list[dict[str, Any]]:
        """获取所有边"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM edges")
        return [dict(row) for row in cursor.fetchall()]

    # ── 规则查询 ──────────────────────────────────────────────

    def get_rules_by_function(self, function_name: str) -> list[dict[str, Any]]:
        """按 function_name 查询规则"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM rule_bindings WHERE function_name = %s", (function_name,))
        return [dict(row) for row in cursor.fetchall()]

    def get_rules_by_rule_id(self, rule_id: str) -> list[dict[str, Any]]:
        """按 rule_id 查询规则绑定"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM rule_bindings WHERE rule_id = %s", (rule_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_all_rule_bindings(self) -> list[dict[str, Any]]:
        """获取所有规则绑定"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM rule_bindings")
        return [dict(row) for row in cursor.fetchall()]

    # ── 模板查询 ──────────────────────────────────────────────

    def get_templates(self) -> list[dict[str, Any]]:
        """获取所有模板节点"""
        return self.get_nodes_by_type("template")

    def get_template_by_id(self, template_id: str) -> dict[str, Any] | None:
        """按 template_id 查询模板"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM nodes WHERE node_id = %s AND node_type = 'template'", (template_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

    # ── 约束关系查询 ──────────────────────────────────────────

    def get_constraints_for_module(self, module_path: str) -> list[dict[str, Any]]:
        """查询模块受哪些规则约束"""
        conn = self._get_conn()
        cursor = conn.execute(
            """
            SELECT rb.*, n.path as module_path
            FROM rule_bindings rb
            JOIN nodes n ON rb.node_id = n.node_id
            WHERE n.path = %s
            """,
            (module_path,),
        )
        return [dict(row) for row in cursor.fetchall()]

    # ── 域依赖查询 ────────────────────────────────────────────

    def get_domain_dependencies(self) -> list[dict[str, Any]]:
        """获取所有域依赖关系"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM domain_dependencies")
        return [dict(row) for row in cursor.fetchall()]

    def get_domain_dependency(self, from_domain: str, to_domain: str) -> dict[str, Any] | None:
        """查询指定域间的依赖关系"""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM domain_dependencies WHERE from_domain = %s AND to_domain = %s", (from_domain, to_domain)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    # ── 路径全景图查询 ────────────────────────────────────────

    def get_architecture_domains(self) -> list[dict[str, Any]]:
        """获取所有架构域"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM arch_domains")
        return [dict(row) for row in cursor.fetchall()]

    def get_directory_tree(self, parent_path: str | None = None) -> list[dict[str, Any]]:
        """获取目录树（可选父路径过滤）"""
        conn = self._get_conn()
        if parent_path is None:
            cursor = conn.execute("SELECT * FROM arch_directory_tree")
        else:
            cursor = conn.execute("SELECT * FROM arch_directory_tree WHERE parent_path = %s", (parent_path,))
        return [dict(row) for row in cursor.fetchall()]

    # ── 统计查询 ──────────────────────────────────────────────
    # P2迁移后：RealDictCursor 返回 dict-like 行，需用列名访问（不再支持 [0] 索引）

    def get_node_count(self) -> int:
        """获取节点总数"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT COUNT(*) AS cnt FROM nodes")
        return cursor.fetchone()["cnt"]

    def get_edge_count(self) -> int:
        """获取边总数"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT COUNT(*) AS cnt FROM edges")
        return cursor.fetchone()["cnt"]

    def get_domain_count(self) -> int:
        """获取域总数"""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT COUNT(DISTINCT domain_id) AS cnt FROM nodes WHERE domain_id IS NOT NULL"
        )
        return cursor.fetchone()["cnt"]

    def get_type_specific_data(self, node_id: str) -> dict[str, Any] | None:
        """获取节点的 type_specific_data（JSON 字段）"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT type_specific_data FROM nodes WHERE node_id = %s", (node_id,))
        row = cursor.fetchone()
        if row and row["type_specific_data"]:
            return json.loads(row["type_specific_data"])
        return None

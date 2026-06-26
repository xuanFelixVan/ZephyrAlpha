# [BLUEPRINT] MOD-GOVERNANCE
# [MODULE] zephyr.governance.depgraph_reader
# [DOMAIN] D-GOVERNANCE
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

提供从 depgraph.db 读取依赖图数据的统一接口，
替代直接解析 61MB+191MB YAML 文件的方式。

使用方式：
    from zephyr.governance.depgraph_reader import DepgraphReader
    reader = DepgraphReader()
    nodes = reader.get_nodes_by_domain('D-FACTOR')
    edges = reader.get_edges_from_node('some_node_id')
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any
from zephyr.shared.io.paths import REPO_ROOT

DB_PATH = REPO_ROOT / "data" / "databases" / "depgraph.db"


class DepgraphReader:
    """依赖图数据库读取器"""

    def __init__(self, db_path: str | Path | None = None):
        self._db_path = Path(db_path) if db_path else DB_PATH
        self._conn: sqlite3.Connection | None = None

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(str(self._db_path))
            self._conn.row_factory = sqlite3.Row
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
        cursor = conn.execute("SELECT * FROM nodes WHERE domain_id = ?", (domain_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_nodes_by_type(self, node_type: str) -> list[dict[str, Any]]:
        """按 node_type 查询节点"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM nodes WHERE node_type = ?", (node_type,))
        return [dict(row) for row in cursor.fetchall()]

    def get_node_by_path(self, path: str) -> dict[str, Any] | None:
        """按 path 精确查询节点"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM nodes WHERE path = ?", (path,))
        row = cursor.fetchone()
        return dict(row) if row else None

    def get_node_by_id(self, node_id: str) -> dict[str, Any] | None:
        """按 node_id 精确查询节点"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM nodes WHERE node_id = ?", (node_id,))
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
        cursor = conn.execute("SELECT * FROM edges WHERE from_node = ?", (from_node,))
        return [dict(row) for row in cursor.fetchall()]

    def get_edges_to_node(self, to_node: str) -> list[dict[str, Any]]:
        """查询指向指定节点的所有边"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM edges WHERE to_node = ?", (to_node,))
        return [dict(row) for row in cursor.fetchall()]

    def get_edges_by_type(self, edge_type: str) -> list[dict[str, Any]]:
        """按 edge_type 查询边"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM edges WHERE edge_type = ?", (edge_type,))
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
        cursor = conn.execute("SELECT * FROM rule_bindings WHERE function_name = ?", (function_name,))
        return [dict(row) for row in cursor.fetchall()]

    def get_rules_by_rule_id(self, rule_id: str) -> list[dict[str, Any]]:
        """按 rule_id 查询规则绑定"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM rule_bindings WHERE rule_id = ?", (rule_id,))
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
        cursor = conn.execute("SELECT * FROM nodes WHERE node_id = ? AND node_type = 'template'", (template_id,))
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
            WHERE n.path = ?
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
            "SELECT * FROM domain_dependencies WHERE from_domain = ? AND to_domain = ?", (from_domain, to_domain)
        )
        row = cursor.fetchone()
        return dict(row) if row else None

    # ── 架构全景图查询 ────────────────────────────────────────

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
            cursor = conn.execute("SELECT * FROM arch_directory_tree WHERE parent_path = ?", (parent_path,))
        return [dict(row) for row in cursor.fetchall()]

    # ── 统计查询 ──────────────────────────────────────────────

    def get_node_count(self) -> int:
        """获取节点总数"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT COUNT(*) FROM nodes")
        return cursor.fetchone()[0]

    def get_edge_count(self) -> int:
        """获取边总数"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT COUNT(*) FROM edges")
        return cursor.fetchone()[0]

    def get_domain_count(self) -> int:
        """获取域总数"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT COUNT(DISTINCT domain_id) FROM nodes WHERE domain_id IS NOT NULL")
        return cursor.fetchone()[0]

    def get_type_specific_data(self, node_id: str) -> dict[str, Any] | None:
        """获取节点的 type_specific_data（JSON 字段）"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT type_specific_data FROM nodes WHERE node_id = ?", (node_id,))
        row = cursor.fetchone()
        if row and row[0]:
            return json.loads(row[0])
        return None

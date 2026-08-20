# [BLUEPRINT] SH-DB-001 | docs/03_modules/_cross_layer/database/blueprint.md
# [MODULE] zephyr.governance.persistence.depgraph_reader
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.__init__
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] production
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
[MODIFY-GUARD] 修改需同步更新 tests/governance/depgraph/test_depgraph_db.py
[CONSUMERS] scripts/governance/; src/zephyr/governance/
[STABILITY] stable
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] FileNotFoundError; sqlite3.Error
[TESTS] tests/governance/depgraph/test_depgraph_db.py

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
import logging
import threading
from pathlib import Path
from typing import Any

from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

# R3 治本（2026-07-28）：_PgConnExecuteWrapper 规范副本下沉到 pg_wrapper（消除三处重复）
from zephyr.governance.persistence.pg_wrapper import _PgConnExecuteWrapper

logger = logging.getLogger(__name__)


class DepgraphReader:
    """依赖图数据库读取器"""

    def __init__(self, db_path: str | Path | None = None) -> None:
        # db_path 参数保留向后兼容（P2迁移后 PG 连接配置由 depgraph_schema.get_depgraph_pg_connection 管理）
        # 治本（2026-06-27）：不再保存 DB_PATH 常量，防止路径污染
        # 5.64.2 修复：连接改为 per-thread（threading.local）——psycopg2 connection
        # 非线程安全，单一连接跨线程共享会产生交错执行/状态损坏竞态。
        # 每线程惰性创建独立连接，注册到 _all_conns 供 close() 统一关闭。
        self._tls = threading.local()
        self._all_conns: list[_PgConnExecuteWrapper] = []
        self._all_conns_lock = threading.Lock()

    def _get_conn(self) -> _PgConnExecuteWrapper:
        conn = getattr(self._tls, "conn", None)
        if conn is None or conn.closed:
            conn = _PgConnExecuteWrapper(get_depgraph_pg_connection(autocommit=True))
            self._tls.conn = conn
            with self._all_conns_lock:
                self._all_conns.append(conn)
        return conn

    def close(self) -> None:
        """关闭所有线程的连接（5.64.5 同款异常隔离：每个 close 独立 try/except 记录后继续）。"""
        with self._all_conns_lock:
            conns, self._all_conns = self._all_conns, []
        for conn in conns:
            try:
                conn.close()
            except Exception:  # noqa: BLE001 — 5.64.5：异常隔离，记录后继续
                logger.warning("depgraph_reader: failed to close conn", exc_info=True)
        if hasattr(self._tls, "conn"):
            self._tls.conn = None

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

    def get_build_status_map(self, target_ids: list[str]) -> dict[str, str]:
        """批量查询节点的 build_status。

        battle_map_anchors.target_id 可能是 blueprint_id 或 path（见
        align_battle_map._valid_ids_depgraph），故两列都匹配。

        :param target_ids: 锚点 target_id 列表
        :return: ``{target_id: build_status}``，未命中的 target_id 不在返回 dict 中
                 （调用方按 '未命中' 处理，保守视为 planned）。
        """
        ids = [t for t in target_ids if t]
        if not ids:
            return {}
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT path, blueprint_id, build_status FROM nodes WHERE path = ANY(%s) OR blueprint_id = ANY(%s)",  # noqa: bare-sql  存量参数化查询/动态标识符，format重排伪新增（§5.160.2集中化专项另列）
            (ids, ids),
        )
        result: dict[str, str] = {}
        for row in cursor.fetchall():
            r = dict(row)
            for k in ("path", "blueprint_id"):
                v = r.get(k)
                if v:
                    result[str(v)] = r.get("build_status") or "planned"
        return result

    def get_status_and_gate_map(self, target_ids: list[str]) -> dict[str, dict[str, str]]:
        """批量查询节点的 build_status + gate_reason + acquisition（一次查询）。

        供 battle_map 生成器渲染 ⛔ 受限原因行用（visualization_view_template
        §4.3 要素⑤）。与 ``get_build_status_map`` 互补：后者只返回 build_status，
        本方法同时返回 gate_reason 与 acquisition 字段，避免生成器为渲染 ⛔ 行
        与 acquisition 标记发起多次 DB 往返。

        gate_reason 列由 ``11_add_gate_blocker_fields.sql`` 迁移添加（与
        ``generate_domain_doc.get_domain_nodes`` 使用的同一列）。
        acquisition_method/acquisition_source 列由 ``add_acquisition_fields.py``
        迁移添加到 nodes_metadata 表（2026-08-05 acquisition 字段基础设施）。

        聚合确定性（治本 P3-1，2026-08-05）：同一 blueprint_id 可能对应多个 path
        （如目录节点 + __init__.py + 子模块），各 path 的 acquisition 字段可能不同。
        SQL 加 ``ORDER BY n.path`` 使路径更具体的节点（如 ``__init__.py``）先处理，
        聚合时按"首个非空值优先"合并 acquisition，确保结果确定。

        :param target_ids: 锚点 target_id 列表（可能是 path 或 blueprint_id，
                           见 ``align_battle_map._valid_ids_depgraph``）
        :return: ``{target_id: {"build_status": ..., "gate_reason": ...,
                 "acquisition_method": ..., "acquisition_source": ...}}``；
                 未命中的 target_id 不在返回 dict 中（调用方按 '未命中' 处理，
                 保守视为 planned、gate_reason 空、acquisition 空）。
        """
        ids = [t for t in target_ids if t]
        if not ids:
            return {}
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT n.path, n.blueprint_id, n.build_status, n.gate_reason, "
            "nm.acquisition_method, nm.acquisition_source "
            "FROM nodes n "
            "LEFT JOIN nodes_metadata nm ON n.path = nm.path "
            "WHERE n.path = ANY(%s) OR n.blueprint_id = ANY(%s) "
            "ORDER BY n.path",
            (ids, ids),
        )
        result: dict[str, dict[str, str]] = {}
        for row in cursor.fetchall():
            r = dict(row)
            bs = r.get("build_status") or "planned"
            gr = r.get("gate_reason") or ""
            am = r.get("acquisition_method") or ""
            asrc = r.get("acquisition_source") or ""
            for k in ("path", "blueprint_id"):
                v = r.get(k)
                if v:
                    key = str(v)
                    existing = result.get(key)
                    if existing is None:
                        result[key] = {
                            "build_status": bs,
                            "gate_reason": gr,
                            "acquisition_method": am,
                            "acquisition_source": asrc,
                        }
                    else:
                        # 聚合 acquisition（首个非空优先；ORDER BY n.path 确保确定性）
                        if not existing["acquisition_method"] and am:
                            existing["acquisition_method"] = am
                        if not existing["acquisition_source"] and asrc:
                            existing["acquisition_source"] = asrc
        return result

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
        cursor = conn.execute("SELECT COUNT(DISTINCT domain_id) AS cnt FROM nodes WHERE domain_id IS NOT NULL")  # noqa: bare-sql  存量参数化查询/动态标识符，format重排伪新增（§5.160.2集中化专项另列）
        return cursor.fetchone()["cnt"]

    def get_type_specific_data(self, node_id: str) -> dict[str, Any] | None:
        """获取节点的 type_specific_data（JSON 字段）"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT type_specific_data FROM nodes WHERE node_id = %s", (node_id,))
        row = cursor.fetchone()
        if row and row["type_specific_data"]:
            return json.loads(row["type_specific_data"])
        return None

# [BLUEPRINT] SH-DB-001 | docs/03_modules/_cross_layer/database/blueprint.md
# [MODULE] zephyr.shared.database.database_crud_mixin
# [DOMAIN] D_SHARED
# [DEPENDENCIES] none（通过宿主类 self.get_governance_conn/get_depgraph_conn 间接调用）
# [CONSUMERS] zephyr.governance.persistence.database_service, zephyr.infrastructure.database_service
# [STARTUP] manual
# [MATURITY] stable
# [INVARIANTS] 共享CRUD方法mixin; 宿主类MUST提供get_governance_conn(read_only)和get_depgraph_conn(read_only)
# [MODIFY-GUARD] 修改需同步更新唯一真源 zephyr.infrastructure.database_service.DatabaseService（governance/persistence 版已收敛为 re-export，AI-14 审计 P1 修复）
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] ConnectionError; ValueError
# [TESTS] tests/test_db_auto_ops.py
# [TTL] permanent
"""
DatabaseCRUDMixin: 共享的 governance.db + depgraph CRUD 方法

P-PLAN 专项工程：抽取两个 DatabaseService 类（governance/persistence 版 + infrastructure 版）
共享的 9 个 CRUD 方法 + 1 个列名白名单常量，消除约 100 行代码重复。

宿主类契约（Host Class Contract）：
    宿主类 MUST 提供以下连接管理方法（Mixin 通过 self 调用）：
    - get_governance_conn(read_only: bool = False) -> sqlite3.Connection
    - get_depgraph_conn(read_only: bool = False) -> psycopg2.extensions.connection

使用方式：
    class DatabaseService(DatabaseCRUDMixin):
        def get_governance_conn(self, read_only=False): ...
        def get_depgraph_conn(self, read_only=False): ...
        # CRUD 方法自动从 mixin 继承

[BLUEPRINT] SH-DB-001 | src/zephyr/shared/database/database_crud_mixin.py
[MODULE] zephyr.shared.database.database_crud_mixin
[DOMAIN] D_SHARED
[INVARIANTS] 宿主类MUST提供get_governance_conn/read_only和get_depgraph_conn/read_only
[MODIFY-GUARD] 修改需同步更新唯一真源 zephyr.infrastructure.database_service（governance/persistence 版已收敛为 re-export）
[CONSUMERS] src/zephyr/governance/persistence/database_service.py; src/zephyr/infrastructure/database_service.py
[STABILITY] stable
[SAFETY] L
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] ConnectionError; ValueError
[TESTS] tests/test_db_auto_ops.py
"""

from typing import Any


class DatabaseCRUDMixin:
    """共享 CRUD 方法 Mixin（governance.db + depgraph）

    消除约 100 行 CRUD 代码重复。宿主类需提供 get_governance_conn(read_only) 和 get_depgraph_conn(read_only)。
    唯一宿主类：zephyr.infrastructure.database_service.DatabaseService（governance/persistence 版已收敛为 re-export）。
    """

    # ========== governance.db CRUD 方法 ==========

    def get_task(self, task_id: str) -> dict[str, Any] | None:
        """获取任务"""
        conn = self.get_governance_conn(read_only=True)
        row = conn.execute("SELECT * FROM tasks WHERE task_id=?", (task_id,)).fetchone()
        return dict(row) if row else None

    # 5.66.1 修复：tasks 表列名白名单，防止 SQL 注入（f-string 拼接列名的治本）
    _TASK_COLUMNS = frozenset({
        "task_id", "title", "description", "status", "priority", "assignee",
        "created_at", "updated_at", "due_date", "completed_at", "parent_id",
        "module_id", "blueprint_id", "decomposition_id", "task_type",
        "estimated_hours", "actual_hours", "tags", "metadata", "is_deleted",
        "deleted_at", "depends_on", "blocks", "labels", "story_points",
        "sprint_id", "epic_id", "assignee_ai", "source", "difficulty",
        "verification_status", "verification_notes", "review_status",
        "review_notes", "creation_tokens", "related_arch_issues",
    })

    def create_task(self, task_data: dict[str, Any]) -> str:
        """创建任务"""
        conn = self.get_governance_conn()
        task_id = task_data["task_id"]
        # 5.66.1 修复：列名白名单校验，阻断 f-string SQL 注入路径
        invalid_cols = set(task_data.keys()) - self._TASK_COLUMNS
        if invalid_cols:
            raise ValueError(f"Invalid task columns: {invalid_cols}. Allowed: {sorted(self._TASK_COLUMNS)}")
        columns = ", ".join(task_data.keys())
        placeholders = ", ".join(["?" for _ in task_data])
        conn.execute(f"INSERT INTO tasks ({columns}) VALUES ({placeholders})", list(task_data.values()))
        conn.commit()
        return task_id

    def update_task_status(self, task_id: str, status: str) -> None:
        """更新任务状态"""
        conn = self.get_governance_conn()
        conn.execute("UPDATE tasks SET status=?, updated_at=datetime('now') WHERE task_id=?", (status, task_id))
        conn.commit()

    def log_rule_enforcement(self, rule_id: str, operation: str, target: str, result: str, details: str = "") -> None:
        """记录规则执行日志"""
        conn = self.get_governance_conn()
        conn.execute(
            """INSERT INTO rule_enforcement_log
            (rule_id, operation, target, result, details, enforced_at, enforced_by)
            VALUES (?, ?, ?, ?, ?, datetime('now'), ?)""",
            (rule_id, operation, target, result, details, "DatabaseService"),
        )
        conn.commit()

    # ========== depgraph CRUD 方法 ==========
    # P2迁移后：depgraph 已切换到 PostgreSQL，使用 psycopg2 cursor 模式
    # cursor_factory=RealDictCursor 使每行返回 RealDictRow，dict(row) 兼容原 sqlite3.Row 用法

    def get_node(self, node_id: str) -> dict[str, Any] | None:
        """获取节点"""
        conn = self.get_depgraph_conn(read_only=True)
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM nodes WHERE node_id=%s", (node_id,))
            row = cur.fetchone()
        return dict(row) if row else None

    def get_nodes_by_domain(self, domain_id: str) -> list[dict[str, Any]]:
        """按域获取节点"""
        conn = self.get_depgraph_conn(read_only=True)
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM nodes WHERE domain_id=%s", (domain_id,))
            rows = cur.fetchall()
        return [dict(r) for r in rows]

    def get_nodes_by_type(self, node_type: str) -> list[dict[str, Any]]:
        """按类型获取节点"""
        conn = self.get_depgraph_conn(read_only=True)
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM nodes WHERE node_type=%s", (node_type,))
            rows = cur.fetchall()
        return [dict(r) for r in rows]

    def get_rule_bindings_by_function(self, function_name: str) -> list[dict[str, Any]]:
        """按函数名获取规则绑定"""
        conn = self.get_depgraph_conn(read_only=True)
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM rule_bindings WHERE function_name=%s", (function_name,))
            rows = cur.fetchall()
        return [dict(r) for r in rows]

    def get_edges_from_node(self, from_node: str) -> list[dict[str, Any]]:
        """获取节点的出边"""
        conn = self.get_depgraph_conn(read_only=True)
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM edges WHERE from_node=%s", (from_node,))
            rows = cur.fetchall()
        return [dict(r) for r in rows]

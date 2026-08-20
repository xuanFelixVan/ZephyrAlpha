# [BLUEPRINT] SH-DB-001 | docs/03_modules/_cross_layer/database/blueprint.md
# [MODULE] zephyr.shared.database.database_crud_mixin
# [DOMAIN] D_SHARED
# [DEPENDENCIES] none（通过宿主类 self.get_governance_conn/get_depgraph_conn 间接调用）
# [CONSUMERS] zephyr.governance.persistence.database_service, zephyr.infrastructure.database_service
# [STARTUP] manual
# [MATURITY] production
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

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 任务数据参数
#   fields: task_id / task_data(dict) / status
#   code: database_crud_mixin.py L58/L76/L90
# - id: I2
#   name: 规则执行日志参数
#   fields: rule_id / operation / target / result / details
#   code: database_crud_mixin.py L96 log_rule_enforcement
# - id: I3
#   name: 图查询参数
#   fields: node_id / domain_id / node_type / function_name / from_node
#   code: database_crud_mixin.py L111-148
# - id: I4
#   name: 宿主类数据库连接
#   fields: get_governance_conn(read_only)→sqlite3 governance.db；get_depgraph_conn(read_only)→psycopg2 depgraph
#   code: 宿主类契约（[INVARIANTS] 头）
# 层: 算法
# - id: A1
#   name_zh: ① 列名白名单校验
#   name_en: _TASK_COLUMNS 校验
#   intro: create_task 前用 37 列白名单拦截非法列名，阻断 f-string SQL 注入
#   desc: L65-83：set(task_data.keys()) - _TASK_COLUMNS 非空即 raise ValueError（5.66.1 治本）
#   inputs: I1
#   outputs: 校验通过的 task_data
#   invariant: 白名单外列名必抛 ValueError
# - id: A2
#   name_zh: ② governance.db 任务 CRUD
#   name_en: get_task / create_task / update_task_status
#   intro: 任务的查询、参数化插入、状态更新三操作
#   desc: L58-94：SELECT * WHERE task_id=?；INSERT INTO tasks 占位符参数化；UPDATE status + updated_at=datetime('now')
#   inputs: A1 I1 I4
#   outputs: 任务行 dict / task_id / None
# - id: A3
#   name_zh: ③ 规则执行日志写入
#   name_en: log_rule_enforcement
#   intro: 向 rule_enforcement_log 表写入一条规则执行记录
#   desc: L96-105：INSERT 五字段 + enforced_at=datetime('now') + enforced_by='DatabaseService'
#   inputs: I2 I4
#   outputs: 写库副作用（commit）
# - id: A4
#   name_zh: ④ depgraph 图查询五方法
#   name_en: get_node / get_nodes_by_domain / get_nodes_by_type / get_rule_bindings_by_function / get_edges_from_node
#   intro: PostgreSQL depgraph 的节点、域、类型、规则绑定、出边五类只读查询
#   desc: L111-148：psycopg2 cursor + %s 占位符；RealDictCursor 行 dict(row) 兼容原 sqlite3.Row 用法
#   inputs: I3 I4
#   outputs: dict / list[dict] / None
# 层: 输出
# - id: O1
#   name_zh: 查询结果集
#   name_en: dict / list[dict] / None
#   intro: 任务行、图节点、规则绑定、出边等查询结果
#   downstream: zephyr.governance.persistence.database_service；zephyr.infrastructure.database_service（[CONSUMERS] 头）
# - id: O2
#   name_zh: 写库副作用
#   name_en: tasks / rule_enforcement_log 行写入 + commit
#   intro: 任务创建/状态更新与规则日志落库
#   downstream: zephyr.infrastructure.database_service（唯一真源宿主，MODIFY-GUARD 头）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# I1 --> A2
# I4 --> A2
# I2 --> A3
# I4 --> A3
# I3 --> A4
# I4 --> A4
# A2 --> O1
# A4 --> O1
# A2 --> O2
# A3 --> O2
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
    _TASK_COLUMNS = frozenset(
        {
            "task_id",
            "title",
            "description",
            "status",
            "priority",
            "assignee",
            "created_at",
            "updated_at",
            "due_date",
            "completed_at",
            "parent_id",
            "module_id",
            "blueprint_id",
            "decomposition_id",
            "task_type",
            "estimated_hours",
            "actual_hours",
            "tags",
            "metadata",
            "is_deleted",
            "deleted_at",
            "depends_on",
            "blocks",
            "labels",
            "story_points",
            "sprint_id",
            "epic_id",
            "assignee_ai",
            "source",
            "difficulty",
            "verification_status",
            "verification_notes",
            "review_status",
            "review_notes",
            "creation_tokens",
            "related_arch_issues",
        }
    )

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

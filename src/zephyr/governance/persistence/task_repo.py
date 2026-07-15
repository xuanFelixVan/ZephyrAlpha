# [BLUEPRINT] MOD-TASK_SYSTEM | docs/03_modules/_domain_infrastructure_runtime/task_system/blueprint.md | §task-system
# [MODULE] zephyr.governance.persistence.task_repo
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.shared.task_types; zephyr.governance.persistence.sqlite_schema; zephyr.gov_audit.event_store; zephyr.governance.observability_governance.projection_engine; zephyr.gov_enforcement.rule_enforcement.gate_engine; zephyr.gov_enforcement.rule_enforcement.gate_types.__init__; zephyr.integration.shared.schema.severity_types; zephyr.shared.utils.time_utils; zephyr.governance.ops_governance.event_hook
# [CONSUMERS] zephyr.infrastructure.shared_services.blueprint_decomposer; zephyr.integration.mcp.task_manager_server; zephyr.trading.boot_hooks; scripts/governance/*; scripts/lock_files.py (cleanup_terminal_tasks)
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] TEMPLATE_REQUIRED_FIELDS defines 18 business-required fields; _validate_template_fields() enforces GOV-TASK-001 v3.2.0 on every create(); claim_next uses SQLite UPDATE RETURNING for atomic claim; claim_next auto-blocks downstream dependents via _block_downstream_dependents (sets blocked_by); transition(COMPLETED/VERIFIED) auto-unblocks via _unblock_downstream_dependents; _auto_phase_cleanup_hook DISABLED (2026-06-10: 任务卡永久保留，禁止删除); cleanup_terminal_tasks() DISABLED; delete_completed_tasks_in_phase() DISABLED; DB trigger prevent_hard_delete enforces no-delete; CIRCULAR_ACCEPTANCE_ROUNDS=2 enforces consecutive zero-error verification on COMPLETED transition
# [MODIFY-GUARD] TEMPLATE_REQUIRED_FIELDS and _validate_template_fields() — adding/removing template fields MUST update both; claim_next SQL MUST preserve atomic semantics; _auto_phase_cleanup_hook / cleanup_terminal_tasks / delete_completed_tasks_in_phase — DISABLED, do NOT re-enable deletion logic; DB trigger prevent_hard_delete is the hard enforcement layer
# [STABILITY] frozen
# [SAFETY] M
# [AI_AUTONOMY] human_gated
# [ERROR_CONTRACT] ValueError on template validation failure; GateViolationError on invalid state transitions; StaleClaimError on timeout recovery
# [TESTS] tests/test_mcp_task_claim.py; tests/test_boot_hooks_unlock.py
# [A_module] module_id=MOD-DAT_task_repo | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""
TaskRepository — 任务登记表 CRUD + 状态机（T-1-04）
====================================================
依据：ADR-0030（SQLite 元数据层）+ ADR-0040（Pydantic v2 契约）

根因约束（防再犯 PAUSED 类错误）
-------------------------------
``TaskStatus`` **仅允许**本文件 ``_ALLOWED_TRANSITIONS`` keys 与 SQLite
``tasks.status`` CHECK 中出现的取值。其它模块（如 pipeline 抢占）**禁止**
使用未在 ``TaskStatus`` 中声明的状态字面量；语义扩展须先改枚举 + DDL 迁移 + 本表。

Safety : H（基础设施核心，状态机错误会影响整个任务流水线）

功能
----
- create / get / update / delete CRUD
- 状态机转换（10 状态）+ 非法转换拒绝
- 每次状态转换自动写 events 表（state_transition 事件）
- 按 phase / status / session_id 列表查询
- 批量 upsert（scaffold 补录用）

状态转换表（合法路径，#13 裁定：对齐 Jira/ITIL 标准）
---------------------
  PENDING     -> IN_PROGRESS, BLOCKED, CANCELLED
  IN_PROGRESS -> COMPLETED, FAILED, BLOCKED, WAITING
  COMPLETED   -> VERIFIED, IN_PROGRESS
  VERIFIED    -> （终态，无出边）
  FAILED      -> RETRY, CANCELLED
  BLOCKED     -> READY, CANCELLED
  WAITING     -> READY, CANCELLED
  READY       -> IN_PROGRESS, CANCELLED
  RETRY       -> IN_PROGRESS, FAILED
  CANCELLED   -> （终态，无出边）

  注 1：COMPLETED -> IN_PROGRESS 为验证失败返工路径（替代原 COMPLETED -> CANCELLED）。
  依据：Jira/ServiceNow/Linear/Azure DevOps 均不允许 COMPLETED -> CANCELLED 直转；
  ITIL v4 / ISO 10006 / CMMI 要求验证不通过走纠正措施循环（返回执行）。
  注 2：RETRY -> FAILED 为重试失败路径（替代原 RETRY -> CANCELLED）。
  取消只能从 FAILED 发起（FAILED -> CANCELLED），RETRY 不直接取消。
  依据：Jira/ServiceNow 要求重试失败先回到 FAILED 状态再决定取消，保持审计轨迹。

线程安全
--------
单实例使用 threading.RLock 串行化写操作；读操作直接执行（WAL 允许并发读）。
与 ADR-0030 §4.5 "单 Writer 假设"一致。
"""

from __future__ import annotations

from typing import Final
import logging

logger = logging.getLogger(__name__)

import fnmatch
import json
import sqlite3
import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock

from zephyr.governance.observability_governance.projection_engine import ProjectionEngine
from zephyr.gov_enforcement.rule_enforcement.gate_engine.gate_engine import (
    GATES_DIR,
    GateEngine,
)
from zephyr.governance.persistence.sqlite_schema import get_db_connection, init_db
from zephyr.shared.io.paths import DB_PATH
from zephyr.integration.shared.schema.severity_types import Priority
from zephyr.gov_enforcement.rule_enforcement.gate_types import GateResult, GateViolationError
from zephyr.shared.utils.time_utils import now_iso
from zephyr.shared.schema.task_types import Task, TaskCard, TaskNamespace, TaskStatus
from zephyr.shared.io.paths import DB_PATH, REPO_ROOT


# 5.160.1 修复：SQL常量集中化（72处裸SQL提取为模块级常量）

SQL_SELECT_TASKS_SORTED = "SELECT * FROM tasks WHERE {where_sql} ORDER BY updated_at DESC LIMIT ?"
SQL_INSERT_EVENTS = """
            INSERT INTO events
                (event_id, event_type, payload, task_id, session_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """
SQL_SELECT_TASKS_BY_ID = "SELECT * FROM tasks WHERE task_id = ?"
SQL_SELECT_TASKS_ACTIVE_BY_STATUS = "SELECT task_id, files_in_scope FROM tasks WHERE status IN ('READY', 'IN_PROGRESS') AND is_deleted = 0"
SQL_SELECT_TASKS_ACTIVE_BY_ID = "SELECT * FROM tasks WHERE task_id = ? AND is_deleted = 0"
SQL_SELECT_TASKS_ACTIVE = "SELECT task_id FROM tasks WHERE is_deleted = 0 AND depends_on LIKE ?"
SQL_SELECT_TASKS_ACTIVE_BY_STATUS_SORTED = "SELECT * FROM tasks WHERE status = ? AND is_deleted = 0 ORDER BY phase ASC, updated_at DESC"
SQL_SELECT_TASKS_ACTIVE_BY_PHASE_SORTED = "SELECT * FROM tasks WHERE phase = ? AND is_deleted = 0 ORDER BY status ASC, task_id ASC"
SQL_SELECT_TASKS_ACTIVE_BY_SESSION_SORTED = "SELECT * FROM tasks WHERE session_id = ? AND is_deleted = 0 ORDER BY updated_at DESC"
SQL_SELECT_TASKS_ACTIVE_COUNT_BY_STATUS = "SELECT COUNT(*) FROM tasks WHERE status = ? AND session_id = ? AND is_deleted = 0"
SQL_SELECT_TASKS_ACTIVE_BY_NAMESPACE_SORTED = "SELECT * FROM tasks WHERE namespace = ? AND is_deleted = 0 ORDER BY seq ASC"
SQL_SELECT_TASK_FILES_BY_ID_SORTED = "SELECT file_path, role FROM task_files WHERE task_id = ? ORDER BY role, file_path"
SQL_SELECT_TASK_FILES_BY_FILE_PATH_SORTED = "SELECT task_id FROM task_files WHERE file_path = ? ORDER BY task_id"
SQL_SELECT_TASKS_ACTIVE_BY_STATUS_SORTED_2 = """
            SELECT * FROM tasks
            WHERE status IN ('IN_PROGRESS','READY','RETRY','WAITING')
              AND is_deleted = 0
            ORDER BY phase ASC, updated_at DESC
            """
SQL_SELECT_TASKS_ACTIVE_COUNT_GROUPED = "SELECT status, COUNT(*) AS cnt FROM tasks WHERE is_deleted = 0 GROUP BY status"
SQL_SELECT_TASKS_ACTIVE_SORTED = """
            SELECT * FROM tasks
            WHERE is_deleted = 0
              AND json_valid(depends_on)
              AND EXISTS (
                  SELECT 1 FROM json_each(depends_on)
                  WHERE value = ?
              )
            ORDER BY phase ASC, updated_at DESC
            """
SQL_SELECT_TASKS_ACTIVE_SORTED_2 = """
            SELECT * FROM tasks
            WHERE is_deleted = 0
              AND json_valid(tags)
              AND EXISTS (
                  SELECT 1 FROM json_each(tags)
                  WHERE value = ?
              )
            ORDER BY phase ASC, updated_at DESC
            """
SQL_SELECT_TASKS_ACTIVE_SORTED_3 = """
            SELECT * FROM tasks
            WHERE is_deleted = 0
              AND json_valid(blocked_by)
              AND EXISTS (
                  SELECT 1 FROM json_each(blocked_by)
                  WHERE value = ?
              )
            ORDER BY phase ASC, updated_at DESC
            """
SQL_SELECT_SQLITE_MASTER = "SELECT name FROM sqlite_master WHERE type='table' AND name='tasks_fts'"
SQL_INSERT_TASKS_COUNT = """
                INSERT INTO tasks (
                    task_id, namespace, seq, title, status, priority, phase,
                    execution_model, model_rationale, fallback_model,
                    safety_level, directive, idempotent, classification,
                    evolution_policy, estimate_hours, actual_hours,
                    files_in_scope, deliverables, acceptance,
                    depends_on, tags, session_id, waiting_for, ready_at,
                    completed_at, created_at, updated_at,
                    source_blueprint, source_section, description,
                    upstream_files, downstream_outputs, allowed_touch,
                    forbidden_touch, applicable_rules, context_assembly_manifest,
                    rollback_instructions, estimated_tokens, timeout_minutes,
                    completed_gates, blocked_gates, assigned_pipeline,
                    pipeline_modules, blocked_by, artifact_paths,
                    audit_findings, ke_entries, ai_autonomy_level,
                    autonomy_checklist, construction_status, verification_status,
                    schema_version, approval_required, priority_proposed,
                    rejection_cooldown_until, block_sessions_count,
                    post_sync_standard, post_sync_specific, depgraph_nodes,
                    root_cause_analysis, pipeline_task_type, target_layer,
                    estimated_complexity
                ) VALUES (
                    :task_id, :namespace, :seq, :title, :status, :priority, :phase,
                    :execution_model, :model_rationale, :fallback_model,
                    :safety_level, :directive, :idempotent, :classification,
                    :evolution_policy, :estimate_hours, :actual_hours,
                    :files_in_scope, :deliverables, :acceptance,
                    :depends_on, :tags, :session_id, :waiting_for, :ready_at,
                    :completed_at, :created_at, :updated_at,
                    :source_blueprint, :source_section, :description,
                    :upstream_files, :downstream_outputs, :allowed_touch,
                    :forbidden_touch, :applicable_rules, :context_assembly_manifest,
                    :rollback_instructions, :estimated_tokens, :timeout_minutes,
                    :completed_gates, :blocked_gates, :assigned_pipeline,
                    :pipeline_modules, :blocked_by, :artifact_paths,
                    :audit_findings, :ke_entries, :ai_autonomy_level,
                    :autonomy_checklist, :construction_status, :verification_status,
                    :schema_version, :approval_required, :priority_proposed,
                    :rejection_cooldown_until, :block_sessions_count,
                    :post_sync_standard, :post_sync_specific, :depgraph_nodes,
                    :root_cause_analysis, :pipeline_task_type, :target_layer,
                    :estimated_complexity
                )
                """
SQL_UPDATE_TASKS_BY_ID = "UPDATE tasks SET {set_clause} WHERE task_id = ?"
SQL_UPDATE_TASKS_BY_ID_VERIFICATION_STATUS = "UPDATE tasks SET verification_status='verified', construction_status='completed', updated_at=? WHERE task_id=?"
SQL_UPDATE_TASKS_BY_ID_APPROVAL_REQUIRED = "UPDATE tasks SET approval_required = 1, priority_proposed = ?, updated_at = ? WHERE task_id = ?"
SQL_INSERT_EVENTS_2 = """INSERT INTO events (event_id, event_type, payload, task_id, created_at)
                   VALUES (?, 'task_event', ?, ?, ?)"""
SQL_UPDATE_TASKS_BY_ID_PRIORITY = "UPDATE tasks SET priority = ?, approval_required = 0, priority_proposed = NULL, rejection_cooldown_until = NULL, updated_at = ? WHERE task_id = ?"
SQL_UPDATE_TASKS_BY_ID_APPROVAL_REQUIRED_2 = "UPDATE tasks SET approval_required = 0, priority_proposed = NULL, rejection_cooldown_until = ?, updated_at = ? WHERE task_id = ?"
SQL_UPDATE_TASKS_BY_ID_STATUS = "UPDATE tasks SET status = ?, blocked_by = ?, updated_at = ? WHERE task_id = ?"
SQL_UPDATE_TASKS_BY_ID_BLOCKED_BY = "UPDATE tasks SET blocked_by = '[]', updated_at = ? WHERE task_id = ?"
SQL_UPDATE_TASKS_ACTIVE_BY_ID_IS_DELETED = "UPDATE tasks SET is_deleted = 1, deleted_at = ?, updated_at = ? WHERE task_id = ? AND is_deleted = 0"
SQL_DELETE_TASK_FILES_BY_ID = "DELETE FROM task_files WHERE task_id = ?"
SQL_DELETE_TASKS_BY_ID = "DELETE FROM tasks WHERE task_id = ?"
SQL_SELECT_TASK_FILES_BY_ID = "SELECT file_path FROM task_files WHERE task_id = ?"
SQL_INSERT_TASK_FILES_OR_IGNORE = "INSERT OR IGNORE INTO task_files (task_id, file_path, role) VALUES (?, ?, ?)"
SQL_DELETE_TASK_FILES_BY_ID_2 = "DELETE FROM task_files WHERE task_id = ? AND file_path = ?"
SQL_SELECT_TASKS_BY_NAMESPACE = "SELECT COALESCE(MAX(seq), 0) + 1 AS next_seq FROM tasks WHERE namespace = ?"
SQL_SELECT_TASKS = "SELECT COALESCE(MAX(seq), 0) + 1 AS next_seq FROM tasks"
SQL_INSERT_TASKS_ACTIVE_COUNT = """
                INSERT INTO tasks (
                    task_id, namespace, seq, title, status, priority, phase,
                    execution_model, model_rationale, fallback_model,
                    safety_level, directive, idempotent, classification,
                    evolution_policy, estimate_hours, actual_hours,
                    files_in_scope, deliverables, acceptance,
                    depends_on, tags, session_id, waiting_for, ready_at,
                    completed_at, created_at, updated_at, is_deleted,
                    source_blueprint, source_section, description,
                    upstream_files, downstream_outputs, allowed_touch,
                    forbidden_touch, applicable_rules, context_assembly_manifest,
                    rollback_instructions, estimated_tokens, timeout_minutes,
                    completed_gates, blocked_gates, assigned_pipeline,
                    pipeline_modules, blocked_by, artifact_paths,
                    audit_findings, ke_entries, ai_autonomy_level,
                    autonomy_checklist, construction_status, verification_status,
                    schema_version, approval_required, priority_proposed,
                    rejection_cooldown_until, block_sessions_count,
                    post_sync_standard, post_sync_specific, depgraph_nodes,
                    root_cause_analysis, pipeline_task_type, target_layer,
                    estimated_complexity
                ) VALUES (
                    :task_id, :namespace, :seq, :title, :status, :priority, :phase,
                    :execution_model, :model_rationale, :fallback_model,
                    :safety_level, :directive, :idempotent, :classification,
                    :evolution_policy, :estimate_hours, :actual_hours,
                    :files_in_scope, :deliverables, :acceptance,
                    :depends_on, :tags, :session_id, :waiting_for, :ready_at,
                    :completed_at, :created_at, :updated_at, 0,
                    :source_blueprint, :source_section, :description,
                    :upstream_files, :downstream_outputs, :allowed_touch,
                    :forbidden_touch, :applicable_rules, :context_assembly_manifest,
                    :rollback_instructions, :estimated_tokens, :timeout_minutes,
                    :completed_gates, :blocked_gates, :assigned_pipeline,
                    :pipeline_modules, :blocked_by, :artifact_paths,
                    :audit_findings, :ke_entries, :ai_autonomy_level,
                    :autonomy_checklist, :construction_status, :verification_status,
                    :schema_version, :approval_required, :priority_proposed,
                    :rejection_cooldown_until, :block_sessions_count,
                    :post_sync_standard, :post_sync_specific, :depgraph_nodes,
                    :root_cause_analysis, :pipeline_task_type, :target_layer,
                    :estimated_complexity
                )
                ON CONFLICT(task_id) DO UPDATE SET
                    namespace = excluded.namespace,
                    seq = excluded.seq,
                    title = excluded.title,
                    status = excluded.status,
                    priority = excluded.priority,
                    phase = excluded.phase,
                    execution_model = excluded.execution_model,
                    model_rationale = excluded.model_rationale,
                    fallback_model = excluded.fallback_model,
                    safety_level = excluded.safety_level,
                    directive = excluded.directive,
                    idempotent = excluded.idempotent,
                    classification = excluded.classification,
                    evolution_policy = excluded.evolution_policy,
                    estimate_hours = excluded.estimate_hours,
                    actual_hours = excluded.actual_hours,
                    files_in_scope = excluded.files_in_scope,
                    deliverables = excluded.deliverables,
                    acceptance = excluded.acceptance,
                    depends_on = excluded.depends_on,
                    tags = excluded.tags,
                    session_id = excluded.session_id,
                    waiting_for = excluded.waiting_for,
                    ready_at = excluded.ready_at,
                    completed_at = excluded.completed_at,
                    updated_at = excluded.updated_at,
                    is_deleted = 0,
                    deleted_at = NULL,
                    source_blueprint = excluded.source_blueprint,
                    source_section = excluded.source_section,
                    description = excluded.description,
                    upstream_files = excluded.upstream_files,
                    downstream_outputs = excluded.downstream_outputs,
                    allowed_touch = excluded.allowed_touch,
                    forbidden_touch = excluded.forbidden_touch,
                    applicable_rules = excluded.applicable_rules,
                    context_assembly_manifest = excluded.context_assembly_manifest,
                    rollback_instructions = excluded.rollback_instructions,
                    estimated_tokens = excluded.estimated_tokens,
                    timeout_minutes = excluded.timeout_minutes,
                    completed_gates = excluded.completed_gates,
                    blocked_gates = excluded.blocked_gates,
                    assigned_pipeline = excluded.assigned_pipeline,
                    pipeline_modules = excluded.pipeline_modules,
                    blocked_by = excluded.blocked_by,
                    artifact_paths = excluded.artifact_paths,
                    audit_findings = excluded.audit_findings,
                    ke_entries = excluded.ke_entries,
                    ai_autonomy_level = excluded.ai_autonomy_level,
                    autonomy_checklist = excluded.autonomy_checklist,
                    construction_status = excluded.construction_status,
                    verification_status = excluded.verification_status,
                    schema_version = excluded.schema_version,
                    approval_required = excluded.approval_required,
                    priority_proposed = excluded.priority_proposed,
                    rejection_cooldown_until = excluded.rejection_cooldown_until,
                    block_sessions_count = excluded.block_sessions_count,
                    post_sync_standard = excluded.post_sync_standard,
                    post_sync_specific = excluded.post_sync_specific,
                    depgraph_nodes = excluded.depgraph_nodes,
                    root_cause_analysis = excluded.root_cause_analysis,
                    pipeline_task_type = excluded.pipeline_task_type,
                    target_layer = excluded.target_layer,
                    estimated_complexity = excluded.estimated_complexity
                """
SQL_UPDATE_TASKS_BY_STATUS_STATUS = """UPDATE tasks SET status = 'READY',
                                     claimed_by = NULL,
                                     claimed_at = NULL,
                                     updated_at = :now
                   WHERE status = 'IN_PROGRESS'
                     AND batch_id = :batch_id
                     AND claimed_at < :cutoff"""
SQL_CREATE_IF_VIRTUAL = """CREATE VIRTUAL TABLE IF NOT EXISTS tasks_fts
                   USING fts5(task_id, title, description, directive, content='tasks',
                   content_rowid='rowid')"""
SQL_INSERT_TASKS_FTS = "INSERT INTO tasks_fts(tasks_fts) VALUES('rebuild')"
SQL_SELECT_TASKS_FTS_ACTIVE_SORTED = """SELECT t.{cols},
                           snippet(tasks_fts, 1, '<b>', '</b>', '...', 32) AS snippet
                    FROM tasks_fts
                    JOIN tasks t ON tasks_fts.task_id = t.task_id
                    WHERE tasks_fts MATCH ? AND t.namespace = ? AND t.is_deleted = 0
                    ORDER BY rank
                    LIMIT ?"""
SQL_SELECT_TASKS_FTS_ACTIVE_SORTED_2 = """SELECT t.{cols},
                           snippet(tasks_fts, 1, '<b>', '</b>', '...', 32) AS snippet
                    FROM tasks_fts
                    JOIN tasks t ON tasks_fts.task_id = t.task_id
                    WHERE tasks_fts MATCH ? AND t.is_deleted = 0
                    ORDER BY rank
                    LIMIT ?"""
SQL_SELECT_TASKS_ACTIVE_COUNT = "SELECT COUNT(*) FROM tasks WHERE priority = 'P0' AND status NOT IN ('CANCELLED','VERIFIED') AND is_deleted = 0"
SQL_UPDATE_TASKS_BY_ID_PRIORITY_2 = "UPDATE tasks SET priority = ?, updated_at = ? WHERE task_id = ?"
SQL_UPDATE_TASKS_COUNT_BY_ID_STATUS = """UPDATE tasks
                    SET status = ?, session_id = COALESCE(?, session_id),
                        waiting_for = ?,
                        ready_at = CASE WHEN ? THEN ? ELSE ready_at END,
                        completed_at = CASE WHEN ? THEN COALESCE(completed_at, ?) ELSE completed_at END,
                        block_sessions_count = CASE WHEN ? THEN block_sessions_count + 1 ELSE block_sessions_count END,
                        updated_at = ?{extra_updates}
                    WHERE task_id = ?"""
SQL_INSERT_TASK_REVIEWS_COUNT = "INSERT INTO task_reviews (review_id, task_id, review_round, dimension, issue_count, issues_json, passed, reviewer, session_id, reviewed_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
SQL_UPDATE_TASKS_BY_ID_STATUS_2 = "UPDATE tasks SET status = ?, updated_at = ? WHERE task_id = ?"
SQL_SELECT_TASKS_BY_ID_2 = "SELECT status FROM tasks WHERE task_id = ?"
SQL_SELECT_TASKS_ACTIVE_2 = """SELECT task_id, blocked_by FROM tasks
               WHERE is_deleted = 0
                 AND status = 'READY'
                 AND json_valid(depends_on)
                 AND EXISTS (
                     SELECT 1 FROM json_each(depends_on) WHERE value = ?
                 )"""
SQL_SELECT_TASKS_ACTIVE_3 = """SELECT task_id, blocked_by, depends_on, status FROM tasks
               WHERE is_deleted = 0
                 AND json_valid(blocked_by)
                 AND EXISTS (
                     SELECT 1 FROM json_each(blocked_by) WHERE value = ?
                 )"""
SQL_SELECT_TASKS_ACTIVE_4 = """SELECT task_id, blocked_by FROM tasks
               WHERE is_deleted = 0
                 AND blocked_by IS NOT NULL AND blocked_by != ''
                 AND NOT json_valid(blocked_by)"""
SQL_UPDATE_TASKS_BY_ID_BLOCKED_BY_2 = "UPDATE tasks SET blocked_by = ?, updated_at = ? WHERE task_id = ?"
SQL_SELECT_EVENTS_COUNT_BY_ID = "SELECT COUNT(*) FROM events WHERE task_id = ? AND event_type = 'state_transition' AND json_extract(payload, '$.to') = 'FAILED'"
SQL_UPDATE_TASKS_BY_ID_DEPENDS_ON = "UPDATE tasks SET depends_on = ? WHERE task_id = ?"
SQL_UPDATE_TASKS_BY_ID_PRIORITY_PROPOSED = "UPDATE tasks SET priority_proposed = ?, updated_at = ? WHERE task_id = ?"
SQL_SELECT_TASK_REVIEWS_COUNT_BY_ID_SORTED = "SELECT review_round, passed, dimension, issue_count FROM task_reviews WHERE task_id=? ORDER BY review_round DESC, dimension"
SQL_SELECT_TASK_REVIEWS_COUNT_BY_ID_SORTED_2 = "SELECT review_round, dimension, issue_count, passed, reviewed_at FROM task_reviews WHERE task_id=? ORDER BY review_round, dimension"
SQL_UPDATE_TASKS_COUNT_BY_ID_STATUS_2 = "UPDATE tasks SET status = ?, updated_at = ?, block_sessions_count = block_sessions_count + 1 WHERE task_id = ?"
SQL_UPDATE_TASKS_ACTIVE_BY_ID_SORTED_STATUS = """UPDATE tasks SET status = 'IN_PROGRESS',
                                     claimed_by = :worker_id,
                                     claimed_at = :now,
                                     updated_at = :now
                   WHERE task_id = (
                       SELECT t.task_id FROM tasks t
                       WHERE t.status = 'READY'
                         AND t.batch_id = :batch_id
                         AND t.is_deleted = 0
                         AND (
                             t.depends_on IS NULL
                             OR t.depends_on = '[]'
                             OR NOT EXISTS (
                                 SELECT 1 FROM json_each(t.depends_on)
                                 WHERE value != ''
                                 AND (SELECT status FROM tasks WHERE task_id = value) != 'COMPLETED'
                             )
                         )
                       ORDER BY t.priority ASC, t.created_at ASC
                       LIMIT 1
                   )
                   RETURNING *"""
SQL_SELECT_TASKS_BY_STATUS = """SELECT task_id FROM tasks
                   WHERE status = 'IN_PROGRESS'
                     AND batch_id = :batch_id
                     AND claimed_at < :cutoff"""
SQL_SELECT_TASKS_ACTIVE_COUNT_BY_BATCH_GROUPED = """SELECT status, COUNT(*) AS cnt
                   FROM tasks
                   WHERE batch_id = :batch_id AND is_deleted = 0
                   GROUP BY status"""
SQL_SELECT_TASKS_BY_ID_3 = "SELECT task_id FROM tasks WHERE task_id=?"

__all__ = [
    "CIRCULAR_ACCEPTANCE_ROUNDS",
    "CircularAcceptanceError",
    "GateResult",
    "GateViolationError",
    "InvalidTransitionError",
    "P0InflationFrozenError",
    "P0InflationWarning",
    "RejectedUpgradeCoolingOffError",
    "RootCauseRequiredError",
    "SyncVerificationError",
    "TaskNotFoundError",
    "TaskRepository",
    "TaskRepositoryError",
    "UnclaimedOperationError",
    "allowed_transitions",
    "is_terminal",
    "search",
]

# PENDING -> IN_PROGRESS 转换时触发的门禁 ID
_STARTUP_GATE_ID = "G1"

# ---------------------------------------------------------------------------
# 异常
# ---------------------------------------------------------------------------


class TaskRepositoryError(RuntimeError):
    """TaskRepository 基础异常。"""
    error_code = "ZA-GV-0006"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class TaskNotFoundError(TaskRepositoryError):
    """task_id 不存在。"""
    error_code = "ZA-GV-0007"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, error_code=error_code, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class InvalidTransitionError(TaskRepositoryError):
    """非法状态转换。"""
    error_code = "ZA-GV-0008"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, error_code=error_code, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class RejectedUpgradeCoolingOffError(TaskRepositoryError):
    """优先级升级被拒绝且仍在 48h 冷却期内。"""
    error_code = "ZA-GV-0009"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, error_code=error_code, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class P0InflationFrozenError(TaskRepositoryError):
    """GOV-TASK-004 §2.5: P0 任务已达上限（5个），冻结新增 P0。"""
    error_code = "ZA-GV-0012"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, error_code=error_code, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class P0InflationWarning(TaskRepositoryError):
    """GOV-TASK-004 §2.5: P0 任务 ≥3 个，新增 P0 需附带论证。"""


class SyncVerificationError(TaskRepositoryError):
    """post_sync_standard 验证命令执行失败（exit ≠ 0）。"""
    error_code = "ZA-GV-0013"

    def __init__(self, task_id: str, command: str, exit_code: int, stderr: str = "", *, error_code: str | None = None) -> None:
        self.command = command
        self.exit_code = exit_code
        self.stderr = stderr
        super().__init__(f"任务 {task_id!r} 的 post_sync_standard 验证失败: 命令 {command!r} 返回 exit={exit_code}")
        if error_code is not None:
            self.error_code = error_code


class PostSyncValidationError(TaskRepositoryError):
    """建卡时 post_sync_standard 命令校验失败（臆造脚本/flag）。

    拦截 AI 幻觉：在 create() 时即拒绝引用不存在脚本或未注册 flag 的命令，
    避免臆造命令落库后在 transition(COMPLETED) 时触发 CircularAcceptanceError 死锁
    （如 D-SIGNAL 改名 20 卡死锁事故：建卡 AI 臆造 apply_depgraph.py --diagnose，
    argparse 从未注册该 flag，导致所有卡无法 transition）。
    """
    error_code = "ZA-GV-0014"

    def __init__(self, task_id: str, command: str, reason: str, *, error_code: str | None = None) -> None:
        self.command = command
        self.reason = reason
        super().__init__(
            f"任务 {task_id!r} 的 post_sync_standard 校验失败: 命令 {command!r} — {reason}"
        )
        if error_code is not None:
            self.error_code = error_code


class PostSyncConstructionError(TaskRepositoryError):
    """transition 时发现 post_sync_standard 命令存在建卡缺陷（argparse 拒绝，exit=2）。

    区分失败模式：exit=2 表明命令引用了不存在的 flag——是建卡时的幻觉缺陷，
    而非当前工作质量问题。应修复任务卡的 post_sync_standard 字段，而非反复重试循环验收。
    （DM-210625: 原 _run_circular_acceptance 将所有非零退出码一视同仁，
    导致建卡缺陷被笼统报为 CircularAcceptanceError，掩盖根因。）
    """
    error_code = "ZA-GV-0015"

    def __init__(self, task_id: str, command: str, stderr: str = "", *, error_code: str | None = None) -> None:
        self.command = command
        super().__init__(
            f"任务 {task_id!r} 的 post_sync_standard 命令 {command!r} 存在建卡缺陷"
            f"（argparse 返回 exit=2，疑似臆造 flag）。"
            f"这是建卡时的幻觉缺陷，请修复 post_sync_standard 字段而非重试循环验收。"
            f"{(' stderr: ' + stderr) if stderr else ''}"
        )
        if error_code is not None:
            self.error_code = error_code


class CircularAcceptanceError(TaskRepositoryError):
    """循环验收未通过——验收命令未连续 2 次返回零错误。"""
    error_code = "ZA-GV-0016"

    def __init__(self, task_id: str, round_num: int, failures: list[str], *, error_code: str | None = None) -> None:
        self.round_num = round_num
        self.failures = failures
        super().__init__(f"任务 {task_id!r} 循环验收第 {round_num} 轮未通过: " + "; ".join(failures))
        if error_code is not None:
            self.error_code = error_code


class UnclaimedOperationError(TaskRepositoryError):
    """对未认领的任务执行了需要认领才能做的操作。"""
    error_code = "ZA-GV-0017"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, error_code=error_code, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class RootCauseRequiredError(TaskRepositoryError):
    """FAILED 状态转换缺少根因分析（MTH-006）。"""
    error_code = "ZA-GV-0018"

    def __init__(self, task_id: str, *, error_code: str | None = None) -> None:
        super().__init__(
            f"任务 {task_id!r} 转换为 FAILED 必须提供根因分析（note 参数不得为空，"
            f"且须包含根因->治根->修复的完整追溯，见 MTH-006）"
        )
        if error_code is not None:
            self.error_code = error_code


class GranularityViolationError(TaskRepositoryError):
    """RULE-THIRTEEN 粒度门禁 R1-R6 违规（DM-200921 修复：原仅文档规则，现代码强制）。"""
    error_code = "ZA-GV-0019"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, error_code=error_code, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class BatchReviewRequiredError(TaskRepositoryError):
    """task_001_batch_review_protocol 违规：未完成7维度循环审查即尝试 COMPLETED。"""
    error_code = "ZA-GV-0020"

    def __init__(self, task_id: str, detail: str = "", *, error_code: str | None = None) -> None:
        msg = (
            f"任务 {task_id!r} 未完成 task_001_batch_review_protocol 审查，禁止转为 COMPLETED。"
            f"必须执行 batch_review() 直到连续2次0问题，并持久化审查记录。"
        )
        if detail:
            msg += f" 详情: {detail}"
        super().__init__(msg)
        if error_code is not None:
            self.error_code = error_code


# ---------------------------------------------------------------------------
# 状态机转换表
# ---------------------------------------------------------------------------

# 循环验收轮数：COMPLETED 转换时 post_sync_standard 命令必须连续 2 次返回 0
CIRCULAR_ACCEPTANCE_ROUNDS: Final[int] = 2


_ALLOWED_TRANSITIONS: dict[TaskStatus, frozenset[TaskStatus]] = {
    TaskStatus.PENDING: frozenset(
        {
            TaskStatus.IN_PROGRESS,
            TaskStatus.BLOCKED,
            TaskStatus.CANCELLED,
        }
    ),
    TaskStatus.IN_PROGRESS: frozenset(
        {
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.BLOCKED,
            TaskStatus.WAITING,
        }
    ),
    TaskStatus.COMPLETED: frozenset(
        {
            TaskStatus.VERIFIED,
            TaskStatus.IN_PROGRESS,
        }
    ),
    TaskStatus.VERIFIED: frozenset(),  # 终态
    TaskStatus.FAILED: frozenset(
        {
            TaskStatus.RETRY,
            TaskStatus.CANCELLED,
        }
    ),
    TaskStatus.BLOCKED: frozenset(
        {
            TaskStatus.READY,
            TaskStatus.CANCELLED,
        }
    ),
    TaskStatus.WAITING: frozenset(
        {
            TaskStatus.READY,
            TaskStatus.CANCELLED,
        }
    ),
    TaskStatus.READY: frozenset(
        {
            TaskStatus.IN_PROGRESS,
            TaskStatus.CANCELLED,
        }
    ),
    TaskStatus.RETRY: frozenset(
        {
            TaskStatus.IN_PROGRESS,
            TaskStatus.FAILED,
        }
    ),
    TaskStatus.CANCELLED: frozenset(),  # 终态
}


def _is_valid_transition(from_status: TaskStatus, to_status: TaskStatus) -> bool:
    return to_status in _ALLOWED_TRANSITIONS.get(from_status, frozenset())


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

_UTC = UTC


def now_iso() -> str:  # noqa: F811  5.12.3 修复：保留签名以兼容调用方，但委托真源
    """返回当前 UTC 时间的 ISO 8601 字符串（Z 后缀真源：shared/utils/time_utils.now_iso）。"""
    # 5.12.3 修复：原 datetime.now(_UTC).isoformat() 产出 "+00:00" 后缀，
    # 与模块顶部已导入的真源 now_iso (line 90) 漂移，导致字符串排序错乱。
    # 模块顶部已 `from zephyr.shared.utils.time_utils import now_iso`，此处直接复用。
    from zephyr.shared.utils.time_utils import now_iso as _now_iso_true_source
    return _now_iso_true_source()


def _new_id(prefix: str = "") -> str:
    """生成带可选前缀的 UUID4 字符串。"""
    uid = str(uuid.uuid4())
    return f"{prefix}{uid}" if prefix else uid


def _safe_parse_json_array(raw: object, field_name: str = "") -> list:
    """Parse a JSON array field with fallback for JS-format strings.

    Handles:
    - Standard JSON arrays: '["a", "b"]'
    - JS-style arrays with single quotes: "['a', 'b']"
    - Comma-separated strings: "a, b"
    - Single plain strings: "a"
    - Empty/null values: "", "None", "null"
    """
    if raw is None:
        return []
    if isinstance(raw, list):
        return raw
    if not isinstance(raw, str):
        return []
    stripped = raw.strip()
    if not stripped or stripped in ("None", "null", "undefined"):
        return []
    try:
        result = json.loads(stripped)
        if isinstance(result, list):
            return result
        return [result]
    except (json.JSONDecodeError, TypeError):
        pass
    if "'" in stripped:
        try:
            fixed = stripped.replace("'", '"')
            result = json.loads(fixed)
            if isinstance(result, list):
                return result
            return [result]
        except (json.JSONDecodeError, TypeError):
            pass
    if "," in stripped:
        items = [item.strip().strip("'\"") for item in stripped.split(",")]
        return [item for item in items if item]
    return [stripped.strip("'\"")]


_JSON_ARRAY_COLUMNS = frozenset(
    {
        "files_in_scope",
        "deliverables",
        "acceptance",
        "depends_on",
        "tags",
        "post_sync_standard",
        "post_sync_specific",
        "allowed_touch",
        "forbidden_touch",
        "applicable_rules",
        "upstream_files",
        "downstream_outputs",
        "context_assembly_manifest",
        "completed_gates",
        "pipeline_modules",
        "blocked_by",
        "artifact_paths",
        "audit_findings",
        "ke_entries",
        "autonomy_checklist",
        "depgraph_nodes",
    }
)

_JSON_DICT_COLUMNS = frozenset({"blocked_gates"})

_DATETIME_NULLABLE_COLUMNS = frozenset({"ready_at", "completed_at", "deleted_at"})

_DATETIME_REQUIRED_COLUMNS = frozenset({"created_at", "updated_at"})


def _serialize_for_db(task: TaskCard) -> dict:
    """将 TaskCard 序列化为 DB 写入参数，强制所有 JSON/datetime 字段为标准格式。

    这是写入的唯一入口——所有 INSERT/UPDATE 必须经过此函数，
    确保数据库中不再出现非标准格式（空字符串、JS格式、裸字符串等）。
    """
    import json as _json

    params: dict = {
        "task_id": task.task_id,
        "namespace": task.namespace.value,
        "seq": task.seq,
        "title": task.title,
        "status": task.status.value,
        "priority": task.priority.value,
        "phase": task.phase,
        "execution_model": task.execution_model,
        "model_rationale": task.model_rationale,
        # fallback_model: DB列为 NOT NULL DEFAULT ''，TaskCard默认None需转''避免IntegrityError
        "fallback_model": task.fallback_model or "",
        "safety_level": task.safety_level.value,
        "directive": task.directive,
        "idempotent": int(task.idempotent),
        "classification": task.classification.value,
        "evolution_policy": task.evolution_policy.value,
        "estimate_hours": task.estimate_hours,
        "actual_hours": task.actual_hours,
        "session_id": task.session_id,
        "waiting_for": task.waiting_for,
        "source_blueprint": getattr(task, "source_blueprint", ""),
        "source_section": getattr(task, "source_section", ""),
        "description": getattr(task, "description", ""),
        "rollback_instructions": getattr(task, "rollback_instructions", ""),
        "estimated_tokens": getattr(task, "estimated_tokens", 8000),
        "timeout_minutes": getattr(task, "timeout_minutes", 30),
        "assigned_pipeline": getattr(task, "assigned_pipeline", ""),
        "ai_autonomy_level": getattr(task, "ai_autonomy_level", "supervised"),
        "construction_status": getattr(task, "construction_status", "pending"),
        "verification_status": getattr(task, "verification_status", "unverified"),
        "schema_version": "0.3.2",
        "approval_required": int(getattr(task, "approval_required", False)),
        "priority_proposed": getattr(task, "priority_proposed", None),
        "rejection_cooldown_until": getattr(task, "rejection_cooldown_until", None),
        "block_sessions_count": getattr(task, "block_sessions_count", 0),
        "root_cause_analysis": getattr(task, "root_cause_analysis", ""),
        "pipeline_task_type": getattr(task, "pipeline_task_type", ""),
        "target_layer": getattr(task, "target_layer", ""),
        "estimated_complexity": getattr(task, "estimated_complexity", ""),
    }

    for col in _JSON_ARRAY_COLUMNS:
        val = getattr(task, col, [])
        params[col] = _json.dumps(
            val if isinstance(val, list) else list(val) if hasattr(val, "__iter__") else [val], ensure_ascii=False
        )

    for col in _JSON_DICT_COLUMNS:
        val = getattr(task, col, {})
        params[col] = _json.dumps(val if isinstance(val, dict) else {}, ensure_ascii=False)

    for col in _DATETIME_NULLABLE_COLUMNS:
        val = getattr(task, col, None)
        params[col] = val.isoformat() if val and hasattr(val, "isoformat") else None

    for col in _DATETIME_REQUIRED_COLUMNS:
        val = getattr(task, col, None)
        params[col] = val.isoformat() if val and hasattr(val, "isoformat") else datetime.now(_UTC).isoformat()

    return params


# === 裁定#217 Tier2 P3 Extract Method 重构（2026-07-15）===
# 原 _row_to_taskcard 128 行 McCabe=37（10 段独立字段变换 pipeline）。
# 治本：提取为 6 个模块级 helper（均 McCabe≤15），_row_to_taskcard 简化为 6 步 pipeline（McCabe≈1）。
# 行为等价：各字段变换步骤顺序不变，JSON 解析/默认值/校验规则不变。

_TASK_ID_PATTERN = __import__("re").compile(r"^(CP|DM|DW|KBG|KE|OPS|SRC|STD)-\d+$")

_JSON_ARRAY_FIELDS = (
    "files_in_scope", "deliverables", "acceptance", "depends_on", "tags",
    "upstream_files", "downstream_outputs", "allowed_touch", "forbidden_touch",
    "applicable_rules", "context_assembly_manifest", "completed_gates",
    "pipeline_modules", "blocked_by", "artifact_paths", "audit_findings",
    "ke_entries", "autonomy_checklist", "post_sync_standard", "post_sync_specific",
    "depgraph_nodes",
)

_LIST_OF_DICT_FIELDS = ("applicable_rules", "audit_findings", "downstream_outputs", "context_assembly_manifest")


def _filter_taskcard_fields(d: dict) -> None:
    """过滤 DB 表额外字段 + 移除内部列（DM-100266 白名单过滤）。"""
    _valid_fields = TaskCard.model_fields.keys()
    d_filtered = {k: v for k, v in d.items() if k in _valid_fields}
    d.clear()
    d.update(d_filtered)
    for _internal_col in ("batch_id", "claimed_by", "claimed_at"):
        d.pop(_internal_col, None)


def _normalize_datetime_fields(d: dict) -> None:
    """归一化 datetime 字段（nullable→None, required→now, updated_at<created_at 修正）。"""
    for field in ("ready_at", "completed_at", "deleted_at"):
        raw = d.get(field)
        if isinstance(raw, str) and raw.strip() in ("", "None", "null"):
            d[field] = None
    for field in ("created_at", "updated_at"):
        raw = d.get(field)
        if isinstance(raw, str) and (not raw.strip() or raw.strip() in ("None", "null") or not raw[0:4].isdigit()):
            d[field] = datetime.now(_UTC).isoformat()
    if d.get("updated_at") and d.get("created_at"):
        try:
            from datetime import datetime as _dt
            ca = _dt.fromisoformat(str(d["created_at"]))
            ua = _dt.fromisoformat(str(d["updated_at"]))
            if ua < ca:
                d["updated_at"] = d["created_at"]
        except (ValueError, TypeError):
            d["updated_at"] = d["created_at"]


def _parse_json_fields(d: dict) -> None:
    """解析 JSON array/dict 字段（str→Python 对象，解析失败→默认空值）。"""
    for field in _JSON_ARRAY_FIELDS:
        d[field] = _safe_parse_json_array(d.get(field, "[]"), field_name=field)
    for field in ("blocked_gates",):
        raw = d.get(field, "{}")
        if isinstance(raw, str):
            try:
                parsed = json.loads(raw)
                d[field] = parsed if isinstance(parsed, dict) else {}
            except (json.JSONDecodeError, TypeError):
                d[field] = {}
        elif not isinstance(raw, dict):
            d[field] = {}


def _filter_list_of_dict_fields(d: dict) -> None:
    """过滤 list-of-dict 字段中的非 dict 脏数据。"""
    for field in _LIST_OF_DICT_FIELDS:
        val = d.get(field, [])
        if isinstance(val, list):
            d[field] = [item for item in val if isinstance(item, dict)]


def _fix_scalar_fields(d: dict) -> None:
    """修正标量字段默认值（idempotent/name→title/source_blueprint/section/description/tokens/timeout）。"""
    d["idempotent"] = bool(d.get("idempotent", 0))
    if "name" in d and "title" not in d:
        d["title"] = d.pop("name")
    if not d.get("source_blueprint", "").strip():
        d["source_blueprint"] = "unknown"
    if not d.get("source_section", "").strip():
        d["source_section"] = "unknown"
    if len(d.get("description", "") or "") < 10:
        d["description"] = d.get("title", "Untitled") + " — 自动恢复描述字段"
    if d.get("estimated_tokens", 8000) < 500:
        d["estimated_tokens"] = 8000
    if d.get("timeout_minutes", 30) < 5:
        d["timeout_minutes"] = 30


def _validate_and_construct_taskcard(d: dict) -> TaskCard:
    """schema_version 警告 + task_id 格式校验 + TaskCard 构造（model_validate 或 model_construct 兜底）。"""
    import warnings
    schema_ver = d.get("schema_version", "")
    if schema_ver and schema_ver != "0.3.2":
        warnings.warn(
            f"TaskCard {d.get('task_id', '?')} schema_version={schema_ver} 与当前 0.3.2 不匹配，"
            f"可能缺少新增字段（autonomy_checklist 等），数据完整性未经验证。",
            UserWarning, stacklevel=2,
        )
    tid = d.get("task_id", "")
    if not _TASK_ID_PATTERN.match(str(tid)):
        warnings.warn(
            f"TaskCard task_id={tid!r} 不符合格式 NAMESPACE-SEQ，跳过 Pydantic 校验",
            UserWarning, stacklevel=2,
        )
        try:
            return TaskCard.model_validate(d)
        except Exception:
            return TaskCard.model_construct(**d)
    try:
        return TaskCard.model_validate(d)
    except Exception as e:
        warnings.warn(f"TaskCard {tid!r} schema 不兼容，model_construct 跳过: {e}", UserWarning, stacklevel=2)
        return TaskCard.model_construct(**d)


def _row_to_taskcard(row: sqlite3.Row) -> TaskCard:
    """将 sqlite3.Row 转换为 TaskCard Pydantic 模型（含全部 62 字段）。"""
    d = dict(row)
    _filter_taskcard_fields(d)
    _normalize_datetime_fields(d)
    _parse_json_fields(d)
    _filter_list_of_dict_fields(d)
    _fix_scalar_fields(d)
    return _validate_and_construct_taskcard(d)


# ---------------------------------------------------------------------------
# TaskRepository
# ---------------------------------------------------------------------------


class TaskRepository:
    """
    任务登记表的 CRUD + 状态机入口。

    参数
    ----
    db_path
        SQLite 数据库路径；默认使用 DB_PATH。
    auto_init
        为 True 时在首次连接时调用 ``init_db()``（默认 True）。

    线程模型
    --------
    内部持有一个 ``threading.RLock``，写操作（create/update/transition/delete）
    在锁内执行；读操作（get/list_*）不加锁（WAL 允许并发读）。
    """

    def __init__(
        self,
        db_path: Path | str | None = None,
        *,
        auto_init: bool = True,
        gate_dir: Path | str | None = None,
        project_root: Path | str | None = None,
        enable_gate: bool = True,
    ) -> None:
        self._db_path: Path = Path(db_path) if db_path is not None else DB_PATH
        self._lock = RLock()
        if auto_init:
            init_db(self._db_path)
        self._conn: sqlite3.Connection = get_db_connection(self._db_path)
        self._enable_gate = enable_gate
        if enable_gate:
            self._gate_engine: GateEngine | None = GateEngine(
                gate_dir=gate_dir if gate_dir is not None else GATES_DIR,
                db_path=self._db_path,
                project_root=project_root,
                auto_init=False,  # init_db 已在上方完成
            )
        else:
            self._gate_engine = None

    # ------------------------------------------------------------------
    # 连接管理
    # ------------------------------------------------------------------

    def close(self) -> None:
        """关闭底层 SQLite 连接（及 GateEngine 连接）。"""
        if self._gate_engine is not None:
            self._gate_engine.close()
        self._conn.close()

    def __enter__(self) -> TaskRepository:
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    @contextmanager
    def _write_tx(self) -> Iterator[sqlite3.Connection]:
        """写事务上下文：BEGIN IMMEDIATE -> yield -> COMMIT / ROLLBACK。"""
        with self._lock:
            self._conn.execute("BEGIN IMMEDIATE")
            try:
                yield self._conn
                self._conn.execute("COMMIT")
            except BaseException:
                # 5.163.2 修复: except Exception -> BaseException,确保 Ctrl+C/SystemExit 时
                # 也执行 ROLLBACK 释放 SQLite BEGIN IMMEDIATE 写锁,避免写锁泄漏。
                self._conn.execute("ROLLBACK")
                raise

    @contextmanager
    def _read_tx(self) -> Iterator[sqlite3.Connection]:
        """读事务上下文：WAL 模式下并发读安全。

        当从 _write_tx 内部调用时，锁已持有（RLock 可重入），直接 yield 连接。
        独立调用时加锁保证读一致性。
        """
        with self._lock:
            yield self._conn

    # ------------------------------------------------------------------
    # 模板校验（GOV-TASK-001 v3.2.0）
    # ------------------------------------------------------------------

    TEMPLATE_REQUIRED_FIELDS: dict[str, str] = {
        "task_id": "任务唯一标识，格式 {NAMESPACE}-{SEQ}",
        "namespace": "8 命名空间之一",
        "title": "任务标题，1-200 字",
        "description": "任务详细描述，≥10 字，含完整施工规格",
        "status": "任务状态，10 态枚举",
        "priority": "优先级 P0-P4",
        "phase": "施工阶段 0-9",
        "execution_model": "主力执行模型",
        "files_in_scope": "需读取的文件列表",
        "deliverables": "产出文件列表",
        "source_blueprint": "来源蓝图 module_id",
        "source_section": "来源蓝图节号",
        "safety_level": "安全等级 H/M/L",
        "directive": "执行指令编号",
        "classification": "敏感度 public/internal/confidential",
        "ai_autonomy_level": "AI 自治级别 supervised/auto",
        "applicable_rules": "必须遵守的治理规则列表",
        "allowed_touch": "可修改文件白名单",
    }

    def _validate_template_fields(self, task: Task) -> None:
        """GOV-TASK-001 v3.2.0: 校验 18 个必填字段。

        缺少任何必填字段时抛出 ValueError。
        """
        missing: list[str] = []
        for field_name, description in self.TEMPLATE_REQUIRED_FIELDS.items():
            value = getattr(task, field_name, None)
            if value is None:
                missing.append(field_name)
                continue
            if isinstance(value, str) and not value.strip():
                missing.append(field_name)
                continue
            if isinstance(value, list) and len(value) == 0:
                missing.append(field_name)
                continue
        if missing:
            raise ValueError(
                f"GOV-TASK-001 v3.2.0 模板校验失败: 任务 {task.task_id!r} 缺少必填字段: "
                + ", ".join(f"{f}({self.TEMPLATE_REQUIRED_FIELDS[f]})" for f in missing)
            )

    def _validate_granularity(self, task: Task) -> list[str]:
        """GOV-TASK-001 §1.3 / RULE-THIRTEEN: 粒度约束校验。

        返回违规列表（空列表 = 合规）。
        规则：
          R1: deliverables ≤ 1
          R2: files_in_scope ≤ 3
          R3: acceptance 独立验收点 ≤ 1
          R4: construction_targets ≤ 1（从 description 中提取施工步骤）
          R5: description 须含结构词（根因/治根/施工步骤/验收标准）
          R6: description ≥ 100 字
        """
        violations: list[str] = []

        if len(task.deliverables) > 1:
            violations.append(f"R1: deliverables={len(task.deliverables)} > 1（一卡一产出物）")

        if len(task.files_in_scope) > 3:
            violations.append(f"R2: files_in_scope={len(task.files_in_scope)} > 3（一卡最多3个文件）")

        if len(task.acceptance) > 1:
            violations.append(f"R3: acceptance={len(task.acceptance)} > 1（一卡一验收点）")

        construction_targets = self._count_construction_targets(task.description)
        if construction_targets > 1:
            violations.append(f"R4: construction_targets={construction_targets} > 1（一卡一施工目标）")

        required_keywords = ("根因", "治根", "施工步骤", "验收标准")
        missing_kw = [kw for kw in required_keywords if kw not in task.description]
        if missing_kw and len(task.description) >= 100:
            violations.append(f"R5: description 缺少结构词 {missing_kw}")

        if len(task.description) < 100:
            violations.append(f"R6: description 长度={len(task.description)} < 100（描述过短）")

        return violations

    def _validate_post_sync_executable(self, task: Task) -> None:
        """建卡时机械校验 post_sync_standard 命令可解析、脚本存在、argparse flag 合法。

        拦截 AI 幻觉（臆造 CLI/flag）：在 create() 时即拒绝引用不存在脚本或未注册
        flag 的命令，避免臆造命令落库后在 transition(COMPLETED) 时触发
        CircularAcceptanceError 死锁（D-SIGNAL 改名 20 卡死锁事故根因）。

        校验范围：仅校验含 .py 脚本的命令（python scripts/x.py --flag）。
        非 .py 命令（echo/git 等壳命令）无法可靠内省，跳过。
        --help 自身失败或超时不阻断建卡（仅 flag 缺失与脚本不存在阻断）。
        """
        cmds = getattr(task, "post_sync_standard", None) or []
        self._validate_post_sync_commands(task.task_id, cmds)

    def _validate_post_sync_extensions(self, task: Task) -> None:
        """建卡时校验孪生字段 post_sync_specific + rollback_instructions（SSoT）。

        W3 盲区封堵：post_sync_standard 有完整 SSoT 校验，但其同型孪生字段
        post_sync_specific（list[str] 命令）此前完全无校验，rollback_instructions
        （str，异构）仅有弱长度检查。AI 可在孪生字段填臆造命令而不被拦截。

        post_sync_specific 与 post_sync_standard 同型同语义，委托 SSoT
        ``validate_post_sync_specific``（薄包装，禁复制 _validate_single_sub_cmd）。
        rollback_instructions 走轻量语义校验（非命令级，避免误杀描述性内容）。
        """
        from zephyr.governance.architecture_governance.post_sync_validator import (
            validate_post_sync_specific,
            validate_rollback_instructions,
        )

        for cmd in (task.post_sync_specific or []):
            reason = validate_post_sync_specific(cmd, REPO_ROOT)
            if reason is not None:
                raise PostSyncValidationError(task.task_id, cmd, reason)
        reason = validate_rollback_instructions(task.rollback_instructions or "", REPO_ROOT)
        if reason is not None:
            raise PostSyncValidationError(
                task.task_id, task.rollback_instructions or "", reason
            )

    def _validate_post_sync_commands(self, task_id: str, cmds: list[str]) -> None:
        """校验一组 post_sync_standard 命令（create + update 复用）。

        与 ``_validate_post_sync_executable`` 同语义，但接受 ``task_id + cmds``
        而非完整 Task 对象——update() 修改 post_sync_standard 时无需加载完整 Task。
        """
        import re

        for cmd in cmds:
            # 0. 链式/多行命令（&&, ||, 换行）拆分为子命令逐条校验
            sub_cmds = re.split(r"\s*(?:&&|\|\||\n)\s*", cmd.strip())
            for sub_cmd in sub_cmds:
                self._validate_post_sync_sub_cmd(task_id, sub_cmd)

    def _validate_post_sync_sub_cmd(self, task_id: str, cmd: str) -> None:
        """校验单条 post_sync_standard 子命令（不含 && / || 链式操作符）。"""
        import shlex
        import subprocess
        import sys

        # 1. shell 解析（posix=False 保留 Windows 反斜杠路径；strip 引号）
        try:
            parts = [t.strip("'\"") for t in shlex.split(cmd, posix=False)]
        except ValueError as exc:
            raise PostSyncValidationError(task_id, cmd, f"shell 解析失败: {exc}") from exc
        if not parts:
            return

        # 1.5 pytest / py_compile 命令跳过 flag 校验
        # pytest 的 --tb/--timeout 等 flag 由 pytest 自身管理，不是 test 文件的 argparse flag
        # py_compile 的目标 .py 是编译目标，不是可执行脚本
        parts_lower = [p.lower() for p in parts]
        if "-m" in parts_lower:
            idx = parts_lower.index("-m")
            if idx + 1 < len(parts_lower) and parts_lower[idx + 1] in ("pytest", "py_compile"):
                # 仍校验 .py 文件存在性，但不校验 flag
                script_path = next((t for t in parts if t.endswith(".py")), None)
                if script_path is not None:
                    p = Path(script_path)
                    if not p.is_absolute():
                        p = REPO_ROOT / p
                    if not p.exists():
                        raise PostSyncValidationError(
                            task_id,
                            cmd,
                            f"文件不存在: {script_path}（解析为 {p}）",
                        )
                return  # pytest/py_compile flag 由模块自身管理，跳过

        # 2. 定位 .py 脚本（可能是 'python script.py' 或 'script.py'）
        script_path = next((t for t in parts if t.endswith(".py")), None)
        if script_path is None:
            # 非 .py 命令（echo/git 等），无法内省，跳过
            return

        # 3. 脚本存在性（相对路径基于 REPO_ROOT 解析）
        p = Path(script_path)
        if not p.is_absolute():
            p = REPO_ROOT / p
        if not p.exists():
            raise PostSyncValidationError(
                task_id,
                cmd,
                f"脚本不存在: {script_path}（解析为 {p}）",
            )

        # 4. 提取 --flag 参数，通过 --help 输出校验是否注册
        # 处理 --flag=value 格式：只取 = 前面的 flag 名（argparse 合法语法）
        flags = [t.split("=")[0] for t in parts if t.startswith("--")]
        if not flags:
            return

        try:
            result = subprocess.run(
                [sys.executable, str(p), "--help"],
                capture_output=True,
                text=True,
                timeout=15,
            )
        except (subprocess.TimeoutExpired, Exception):
            # --help 超时或异常无法校验，跳过（不阻断建卡）
            return

        if result.returncode != 0:
            # --help 自身失败（脚本可能有 import 错误等），跳过 flag 校验
            return

        help_text = result.stdout + result.stderr
        missing = [f for f in flags if f not in help_text]
        if missing:
            raise PostSyncValidationError(
                task_id,
                cmd,
                f"argparse 未注册 flag {missing}（--help 输出中未找到；"
                f"疑似臆造 flag，请对照 '<脚本> --help' 实际输出）",
            )

    @staticmethod
    def _count_construction_targets(description: str) -> int:
        """从 description 中计算施工步骤数量。"""
        import re

        steps = re.findall(r"第[一二三四五六七八九十\d]+步", description)
        if steps:
            return len(steps)
        steps = re.findall(r"STEP\s*\d+", description, re.IGNORECASE)
        if steps:
            return len(steps)
        return 1 if description.strip() else 0

    # ------------------------------------------------------------------
    # 内部：events 写入
    # ------------------------------------------------------------------

    def _record_event(
        self,
        conn: sqlite3.Connection,
        event_type: str,
        payload: dict[str, object],
        task_id: str | None = None,
        session_id: str | None = None,
    ) -> None:
        """在同一事务连接中写入 events 表。"""
        conn.execute(
            SQL_INSERT_EVENTS,
            (
                _new_id("ev-"),
                event_type,
                json.dumps(payload, ensure_ascii=False),
                task_id,
                session_id,
                now_iso(),
            ),
        )

    # ------------------------------------------------------------------
    # 内部：tasks 行读取
    # ------------------------------------------------------------------

    def _fetch_row(self, conn: sqlite3.Connection, task_id: str) -> sqlite3.Row | None:
        cursor = conn.execute(SQL_SELECT_TASKS_BY_ID, (task_id,))
        result: sqlite3.Row | None = cursor.fetchone()
        return result

    # ------------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------------

    def _check_files_in_scope_conflict(self, conn: sqlite3.Connection, task: Task) -> None:
        """DM-386: 检查新任务的 files_in_scope 与现有 READY/IN_PROGRESS 任务是否有交集。

        有交集时抛出 ValueError，阻止建卡，防止两个活跃任务同时修改同一文件。
        """
        new_files = set(task.files_in_scope)
        if not new_files:
            return

        cursor = conn.execute(
            SQL_SELECT_TASKS_ACTIVE_BY_STATUS
        )
        for row in cursor.fetchall():
            existing_task_id = row["task_id"]
            existing_raw = row["files_in_scope"]
            if not existing_raw or not existing_raw.strip():
                continue
            try:
                existing_files = set(json.loads(existing_raw))
            except (json.JSONDecodeError, TypeError):
                continue
            overlap = new_files & existing_files
            if overlap:
                raise ValueError(
                    f"files_in_scope 冲突: 新任务 {task.task_id!r} 与活跃任务 "
                    f"{existing_task_id!r} 共享文件 {sorted(overlap)}"
                )

    def create(
        self, task: Task, *, files: list[dict[str, str]] | None = None, allow_direct_create: bool = False
    ) -> TaskCard:
        """
        插入新任务。task_id 已存在时抛 sqlite3.IntegrityError。

        参数
        ----
        task : Task
            Pydantic 模型实例（必须通过校验）。
        files : list[dict] | None
            任务-文件映射列表，每项含 file_path 和 role（primary/in_scope/output）。
        allow_direct_create : bool
            非蓝图任务建卡入口：Bug修复/架构债务/代码扫描/重构任务等无蓝图来源的任务。
            RULE-ZERO-TASK（v2.0+）：建卡触发=用户主动 OR 八指标阈值触发。
            蓝图拆解是建卡来源之一，非唯一路径。默认 False（蓝图任务走 BlueprintDecomposer）。

        返回
        ----
        TaskCard
            插入后从 DB 重新读取的 TaskCard 对象（时间戳已规范化）。
        """
        source_bp = getattr(task, "source_blueprint", "") or ""
        if not allow_direct_create and (not source_bp.strip() or source_bp.strip().lower() == "unknown"):
            raise ValueError(
                f"RULE-ZERO-TASK 违规: 任务 {task.task_id!r} 的 source_blueprint 为空或 'unknown'。"
                f"蓝图任务建卡路径 = BlueprintDecomposer.decompose(blueprint_path)（MOD-TASK_SYSTEM）。"
                f"非蓝图任务（Bug修复/架构债务/代码扫描/重构任务）请传 allow_direct_create=True。"
                f"RULE-ZERO-TASK v2.0+: 建卡触发=用户主动 OR 八指标阈值触发，蓝图拆解非唯一路径。"
            )
        self._validate_template_fields(task)
        # RULE-THIRTEEN: 粒度门禁 R1-R6 强制校验（DM-200921 修复：原仅文档规则，现代码强制）
        granularity_violations = self._validate_granularity(task)
        if granularity_violations:
            raise GranularityViolationError(
                f"RULE-THIRTEEN 粒度门禁违规（task_id={task.task_id!r}）:\n"
                + "\n".join(f"  - {v}" for v in granularity_violations)
            )
        # DM-210625: post_sync_standard 可执行性校验（拦截臆造脚本/flag 落库）
        self._validate_post_sync_executable(task)
        # W3: 孪生字段（post_sync_specific + rollback_instructions）SSoT 校验
        self._validate_post_sync_extensions(task)
        with self._write_tx() as conn:
            self._check_files_in_scope_conflict(conn, task)
            if task.priority is Priority.P0:
                p0_count = self._count_p0_tasks(conn)
                if p0_count >= 5:
                    raise P0InflationFrozenError(
                        f"GOV-TASK-004 §2.5: 当前活跃 P0 任务 {p0_count} 个（已达上限 5），"
                        f"冻结新增 P0。请将优先级降为 P1 或等待 Owner 手动解除冻结"
                    )
                if p0_count >= 3:
                    import warnings

                    warnings.warn(
                        f"GOV-TASK-004 §2.5: 当前活跃 P0 任务 {p0_count} 个（≥3 黄色警戒），"
                        f"新增 P0 任务 {task.task_id!r} 必须附带'为什么必须 P0 而非 P1 / 能不能拆成 P1+P2'的论证段落",
                        UserWarning,
                        stacklevel=2,
                    )
            if self._enable_gate and self._gate_engine is not None:
                gate_result = self._gate_engine.evaluate(task, "G0", conn=conn)
                if not gate_result.passed:
                    raise GateViolationError(gate_result)
            conn.execute(
                SQL_INSERT_TASKS_COUNT,
                _serialize_for_db(task),
            )
            if files:
                for f in files:
                    conn.execute(
                        SQL_INSERT_TASK_FILES_OR_IGNORE,
                        (task.task_id, f["file_path"], f.get("role", "in_scope")),
                    )
            self._record_event(
                conn,
                "task_event",
                {"action": "created", "task_id": task.task_id, "status": task.status.value},
                task_id=task.task_id,
                session_id=task.session_id,
            )
            row = self._fetch_row(conn, task.task_id)
        if row is None: raise RuntimeError("post-write fetch returned None")  # 5.88.2 修复: assert->if/raise
        return _row_to_taskcard(row)

    # ------------------------------------------------------------------
    # READ
    # ------------------------------------------------------------------

    def get(self, task_id: str) -> TaskCard | None:
        """按 task_id 查询有效任务（默认排除软删除行），不存在返回 None。"""
        cursor = self._conn.execute(
            SQL_SELECT_TASKS_ACTIVE_BY_ID,
            (task_id,),
        )
        row = cursor.fetchone()
        return _row_to_taskcard(row) if row else None

    def get_or_raise(self, task_id: str) -> TaskCard:
        """按 task_id 查询，不存在抛 TaskNotFoundError。"""
        task = self.get(task_id)
        if task is None:
            raise TaskNotFoundError("任务不存在")
        return task

    # ------------------------------------------------------------------
    # UPDATE（通用字段更新，不触发状态机）
    # ------------------------------------------------------------------

    def update(
        self,
        task_id: str,
        *,
        title: str | None = None,
        session_id: str | None = None,
        waiting_for: str | None = None,
        estimate_hours: float | None = None,
        actual_hours: float | None = None,
        deliverables: list[str] | None = None,
        acceptance: list[str] | None = None,
        files_in_scope: list[str] | None = None,
        tags: list[str] | None = None,
        model_rationale: str | None = None,
        post_sync_standard: list[str] | None = None,
        post_sync_specific: list[str] | None = None,
        rollback_instructions: str | None = None,
    ) -> TaskCard:
        """
        更新非状态字段。不触发状态机校验，也不写 state_transition 事件。
        状态转换请使用 ``transition()`` 方法。

        参数
        ----
        post_sync_standard:
            新的 post_sync_standard 命令列表。传入时触发
            ``_validate_post_sync_commands`` 机械校验（脚本存在 + argparse flag
            已注册），拒绝臆造 CLI/flag 落库。用于批量修复历史 broken 命令。
        post_sync_specific:
            新的 post_sync_specific 命令列表（与 post_sync_standard 同型同语义）。
            传入时委托 SSoT ``validate_post_sync_specific`` 校验（W3 盲区封堵）。
        rollback_instructions:
            新的回滚说明文本（str，异构：描述性步骤 + 命令混合）。传入时走
            SSoT ``validate_rollback_instructions`` 轻量语义校验（非命令级，
            避免误杀 1599 张已建卡的描述性内容；仅校验非空+长度+python .py 存在性）。

        返回
        ----
        Task
            更新后重新读取的 Task 对象。
        """
        # DM-210625: post_sync_standard 校验在 _write_tx 外执行（subprocess 调用
        # --help 不应在事务内长占连接）。校验通过后才进入写事务。
        if post_sync_standard is not None:
            self._validate_post_sync_commands(task_id, post_sync_standard)
        # W3: 孪生字段 SSoT 校验（事务外，与 post_sync_standard 同段）
        if post_sync_specific is not None:
            from zephyr.governance.architecture_governance.post_sync_validator import validate_post_sync_specific

            for cmd in post_sync_specific:
                reason = validate_post_sync_specific(cmd, REPO_ROOT)
                if reason is not None:
                    raise PostSyncValidationError(task_id, cmd, reason)
        if rollback_instructions is not None:
            from zephyr.governance.architecture_governance.post_sync_validator import (
                validate_rollback_instructions,
            )

            reason = validate_rollback_instructions(rollback_instructions, REPO_ROOT)
            if reason is not None:
                raise PostSyncValidationError(task_id, rollback_instructions, reason)

        with self._write_tx() as conn:
            row = self._fetch_row(conn, task_id)
            if row is None:
                raise TaskNotFoundError("任务不存在")

            updates: list[tuple[str, object]] = []
            if title is not None:
                updates.append(("title", title))
            if session_id is not None:
                updates.append(("session_id", session_id))
            if waiting_for is not None:
                updates.append(("waiting_for", waiting_for))
            if estimate_hours is not None:
                updates.append(("estimate_hours", estimate_hours))
            if actual_hours is not None:
                updates.append(("actual_hours", actual_hours))
            if deliverables is not None:
                updates.append(("deliverables", json.dumps(deliverables, ensure_ascii=False)))
            if acceptance is not None:
                updates.append(("acceptance", json.dumps(acceptance, ensure_ascii=False)))
            if files_in_scope is not None:
                updates.append(("files_in_scope", json.dumps(files_in_scope, ensure_ascii=False)))
            if tags is not None:
                updates.append(("tags", json.dumps(tags, ensure_ascii=False)))
            if model_rationale is not None:
                updates.append(("model_rationale", model_rationale))
            if post_sync_standard is not None:
                updates.append(
                    ("post_sync_standard", json.dumps(post_sync_standard, ensure_ascii=False))
                )
            if post_sync_specific is not None:
                updates.append(
                    ("post_sync_specific", json.dumps(post_sync_specific, ensure_ascii=False))
                )
            if rollback_instructions is not None:
                # rollback_instructions 是 TEXT（非 JSON list），直接写字符串
                updates.append(("rollback_instructions", rollback_instructions))

            if not updates:
                return _row_to_taskcard(row)

            updates.append(("updated_at", now_iso()))
            set_clause = ", ".join(f"{col} = ?" for col, _ in updates)
            values = [v for _, v in updates]
            conn.execute(
                SQL_UPDATE_TASKS_BY_ID.format(set_clause=set_clause),
                (*values, task_id),
            )
            updated_row = self._fetch_row(conn, task_id)

        if updated_row is None: raise RuntimeError("post-write fetch returned None")  # 5.88.2 修复: assert->if/raise
        return _row_to_taskcard(updated_row)

    # ------------------------------------------------------------------
    # 交付物验证（G7 交付门禁前置）
    # ------------------------------------------------------------------

    def verify(self, task_id: str, *, session_id: str | None = None) -> TaskCard:
        """标记任务交付物已验证（verification_status=verified）。

        G7 交付门禁（transition(COMPLETED) 时评估）要求
        ``verification_status == "verified"``（g7_orc_gate_engine.yaml
        G7-ORC-VERIFICATION, severity=error -> P0）。本方法是设置该字段的
        唯一合法生产路径——填补"门禁已接线但无验证入口"的设计缺口。

        前置机械门禁：``batch_review`` 必须通过（``consecutive_zero >= 2``）。
        通过后设置：
          - ``verification_status = "verified"``（小写，匹配 G7 allowed_values）
          - ``construction_status = "completed"``（DB 现有约定：pending -> completed）

        典型调用顺序::

            repo.batch_review(task_id, reviewer="ai", session_id=sid)  # 循环至 0 问题
            repo.verify(task_id, session_id=sid)                         # 标记已验证
            repo.transition(task_id, TaskStatus.COMPLETED, ...)         # G7 通过

        参数
        ----
        session_id : str | None
            执行验证的 AI session 标识（预留审计字段）。

        返回
        ----
        TaskCard
            更新后重新读取的任务对象。

        异常
        ----
        TaskNotFoundError: 任务不存在。
        BatchReviewRequiredError: batch_review 未通过（consecutive_zero < 2）。
        """
        # 前置机械门禁：batch_review 必须通过（连续 2 轮 0 问题）
        review_status = self.get_review_status(task_id)
        if not review_status.get("reviewed", False):
            raise BatchReviewRequiredError(
                task_id,
                "verify() 前置门禁失败：未执行任何审查(batch_review从未调用)",
            )
        if not review_status.get("review_complete", False):
            raise BatchReviewRequiredError(
                task_id,
                f"verify() 前置门禁失败：审查未完成 "
                f"consecutive_zero={review_status.get('consecutive_zero', 0)}/2",
            )

        with self._write_tx() as conn:
            row = self._fetch_row(conn, task_id)
            if row is None:
                raise TaskNotFoundError("任务不存在")

            conn.execute(
                SQL_UPDATE_TASKS_BY_ID_VERIFICATION_STATUS,
                (now_iso(), task_id),
            )
            updated_row = self._fetch_row(conn, task_id)

        if updated_row is None: raise RuntimeError("post-write fetch returned None")  # 5.88.2 修复: assert->if/raise
        return _row_to_taskcard(updated_row)

    # ------------------------------------------------------------------
    # PRIORITY GOVERNANCE（GOV-TASK-004 §2.4+§2.5）
    # ------------------------------------------------------------------

    def _count_p0_tasks(self, conn: sqlite3.Connection) -> int:
        """统计当前活跃 P0 任务数（排除终态 CANCELLED/VERIFIED 和软删除）。"""
        row = conn.execute(
            SQL_SELECT_TASKS_ACTIVE_COUNT
        ).fetchone()
        return row[0] if row else 0

    def propose_priority_upgrade(
        self,
        task_id: str,
        proposed_priority: str,
    ) -> TaskCard:
        """AI 提议优先级升级（P4->P3->P2->P1->P0）。

        规则（GOV-TASK-004 §2.4）：
        - 设置为 approval_required=True + priority_proposed=目标值
        - 不直接修改 priority 字段
        - 若已有拒绝且在 48h 冷却期内，抛出 RejectedUpgradeCoolingOffError
        - 降级（如 P1->P2）直接生效，不走审批
        """
        from zephyr.integration.shared.schema.severity_types import Priority as P

        with self._write_tx() as conn:
            row = self._fetch_row(conn, task_id)
            if row is None:
                raise TaskNotFoundError("任务不存在")

            current_p = row["priority"]
            proposed_p = getattr(P, proposed_priority, proposed_priority)
            if isinstance(proposed_p, P):
                proposed_p = proposed_p.value

            if current_p == proposed_p:
                return _row_to_taskcard(row)

            current_idx = {
                Priority.P0.value: 0,
                Priority.P1.value: 1,
                Priority.P2.value: 2,
                Priority.P3.value: 3,
                Priority.P4.value: 4,
            }.get(current_p, 9)
            proposed_idx = {
                Priority.P0.value: 0,
                Priority.P1.value: 1,
                Priority.P2.value: 2,
                Priority.P3.value: 3,
                Priority.P4.value: 4,
            }.get(proposed_p, 9)

            if proposed_idx >= current_idx:
                conn.execute(
                    SQL_UPDATE_TASKS_BY_ID_PRIORITY_2,
                    (proposed_p, now_iso(), task_id),
                )
                updated_row = self._fetch_row(conn, task_id)
                return _row_to_taskcard(updated_row)

            current_approval = row["approval_required"]
            if current_approval:
                if row["priority_proposed"] and row["priority_proposed"] != proposed_p:
                    conn.execute(
                        SQL_UPDATE_TASKS_BY_ID_PRIORITY_PROPOSED,
                        (proposed_p, now_iso(), task_id),
                    )
                    updated_row = self._fetch_row(conn, task_id)
                    return _row_to_taskcard(updated_row)
                return _row_to_taskcard(row)

            cooldown_until = row["rejection_cooldown_until"]
            if cooldown_until:
                from datetime import datetime as dt

                try:
                    cooldown_dt = dt.fromisoformat(cooldown_until)
                    if cooldown_dt > dt.now(UTC):
                        raise RejectedUpgradeCoolingOffError(
                            f"优先级升级被拒绝且仍在冷却期（至 {cooldown_until}），请等待冷却期结束后重新提议"
                        )
                except (ValueError, TypeError):
                    pass

            if proposed_p == "P0":
                p0_count = self._count_p0_tasks(conn)
                if p0_count >= 5:
                    raise P0InflationFrozenError(
                        f"GOV-TASK-004 §2.5: 当前活跃 P0 任务 {p0_count} 个（已达上限 5），"
                        f"冻结升级为 P0。请保持当前优先级或等待 Owner 手动解除冻结"
                    )
                if p0_count >= 3:
                    import warnings

                    warnings.warn(
                        f"GOV-TASK-004 §2.5: 当前活跃 P0 任务 {p0_count} 个（≥3 黄色警戒），"
                        f"任务 {task_id!r} 升级为 P0 必须附带'为什么必须 P0 而非 P1 / 能不能拆成 P1+P2'的论证段落",
                        UserWarning,
                        stacklevel=2,
                    )

            conn.execute(
                SQL_UPDATE_TASKS_BY_ID_APPROVAL_REQUIRED,
                (proposed_p, now_iso(), task_id),
            )

            conn.execute(
                SQL_INSERT_EVENTS_2,
                (
                    f"ev-{task_id}-priority-{proposed_p}",
                    json.dumps(
                        {
                            "event_subtype": "priority_upgrade_proposed",
                            "current": current_p,
                            "proposed": proposed_p,
                            "action": "awaiting_owner_approval",
                        },
                        ensure_ascii=False,
                    ),
                    task_id,
                    now_iso(),
                ),
            )

            updated_row = self._fetch_row(conn, task_id)
        if updated_row is None: raise RuntimeError("post-write fetch returned None")  # 5.88.2 修复: assert->if/raise
        return _row_to_taskcard(updated_row)

    def approve_priority_upgrade(self, task_id: str) -> TaskCard:
        """Owner 批准优先级升级。将 priority_proposed -> priority，清除 approval 标记。"""
        with self._write_tx() as conn:
            row = self._fetch_row(conn, task_id)
            if row is None:
                raise TaskNotFoundError("任务不存在")

            if not row["approval_required"]:
                return _row_to_taskcard(row)

            approved_p = row["priority_proposed"] or row["priority"]
            conn.execute(
                SQL_UPDATE_TASKS_BY_ID_PRIORITY,
                (approved_p, now_iso(), task_id),
            )

            conn.execute(
                SQL_INSERT_EVENTS_2,
                (
                    f"ev-{task_id}-approved-{approved_p}",
                    json.dumps(
                        {
                            "event_subtype": "priority_upgrade_approved",
                            "approved": approved_p,
                            "action": "owner_approved",
                        },
                        ensure_ascii=False,
                    ),
                    task_id,
                    now_iso(),
                ),
            )

            updated_row = self._fetch_row(conn, task_id)
        if updated_row is None: raise RuntimeError("post-write fetch returned None")  # 5.88.2 修复: assert->if/raise
        return _row_to_taskcard(updated_row)

    def reject_priority_upgrade(self, task_id: str) -> TaskCard:
        """Owner 拒绝优先级升级。设置 48h 冷却期。"""
        from datetime import datetime as dt
        from datetime import timedelta as td

        cooldown = (dt.now(UTC) + td(hours=48)).isoformat()

        with self._write_tx() as conn:
            row = self._fetch_row(conn, task_id)
            if row is None:
                raise TaskNotFoundError("任务不存在")

            conn.execute(
                SQL_UPDATE_TASKS_BY_ID_APPROVAL_REQUIRED_2,
                (cooldown, now_iso(), task_id),
            )

            conn.execute(
                SQL_INSERT_EVENTS_2,
                (
                    f"ev-{task_id}-rejected",
                    json.dumps(
                        {
                            "event_subtype": "priority_upgrade_rejected",
                            "cooldown_until": cooldown,
                            "action": "owner_rejected",
                        },
                        ensure_ascii=False,
                    ),
                    task_id,
                    now_iso(),
                ),
            )

            updated_row = self._fetch_row(conn, task_id)
        if updated_row is None: raise RuntimeError("post-write fetch returned None")  # 5.88.2 修复: assert->if/raise
        return _row_to_taskcard(updated_row)

    # ------------------------------------------------------------------
    # TRANSITION（状态机）
    # ------------------------------------------------------------------

    # === 裁定#217 Tier2 P4 Extract Method 重构（2026-07-15）===
    # 原 transition 222行 McCabe=39（9段顺序状态机转换逻辑）。
    # 治本：提取为 6 个模块级 helper（均 McCabe≤15），主函数简化为编排（McCabe≈7）。
    # 行为等价：所有异常/事件/事务/门禁逻辑完全保留，GateViolationError 处理保留在主函数。

    def _normalize_transition_input(
        self, to_status: TaskStatus | str, note: str | None, task_id: str,
    ) -> TaskStatus:
        """规范化 to_status 并执行 FAILED 根因检查（MTH-006）。"""
        if isinstance(to_status, str):
            to_status = TaskStatus(to_status)
        if to_status == TaskStatus.FAILED:
            if not note or not note.strip():
                raise RootCauseRequiredError(task_id)
        return to_status

    def _pre_circular_acceptance(self, to_status: TaskStatus, task_id: str) -> None:
        """COMPLETED 转换前执行循环验收（5.15.1：移到写事务之前避免事务内 subprocess 持锁）。"""
        if to_status != TaskStatus.COMPLETED:
            return
        with self._read_tx() as read_conn:
            _pre_row = self._fetch_row(read_conn, task_id)
        if _pre_row is not None:
            _pre_task = _row_to_taskcard(_pre_row)
            _pre_cmds = getattr(_pre_task, "post_sync_standard", []) or []
            if _pre_cmds:
                self._run_circular_acceptance(task_id, _pre_cmds)

    def _check_transition_gates(
        self, conn, row, to_status: TaskStatus, task_id: str,
    ) -> None:
        """G1 门禁（IN_PROGRESS）+ G7 门禁（COMPLETED）+ 批量审查检查（COMPLETED）。"""
        if to_status == TaskStatus.IN_PROGRESS and self._should_evaluate_gate(_STARTUP_GATE_ID):
            task_obj = _row_to_taskcard(row)
            gate_result = self._gate_engine.evaluate(task_obj, _STARTUP_GATE_ID, conn=conn)
            if not gate_result.passed:
                raise GateViolationError(gate_result)
        if to_status == TaskStatus.COMPLETED and self._should_evaluate_gate("G7"):
            task_obj = _row_to_taskcard(row)
            gate_result = self._gate_engine.evaluate(task_obj, "G7", conn=conn)
            if not gate_result.passed:
                raise GateViolationError(gate_result)
        if to_status == TaskStatus.COMPLETED:
            review_status = self.get_review_status(task_id)
            if not review_status.get("reviewed", False):
                raise BatchReviewRequiredError(
                    task_id,
                    "未执行任何审查(batch_review从未调用)",
                )
            if not review_status.get("review_complete", False):
                raise BatchReviewRequiredError(
                    task_id,
                    f"审查未完成: consecutive_zero={review_status.get('consecutive_zero', 0)}/2",
                )

    def _apply_transition_update(
        self, conn, task_id: str, to_status: TaskStatus,
        session_id: str | None, waiting_for: str | None, note: str | None,
    ) -> None:
        """构建 UPDATE 参数并执行状态转换 SQL。"""
        now = now_iso()
        set_ready_at = to_status == TaskStatus.READY
        set_completed_at = to_status in (TaskStatus.COMPLETED, TaskStatus.VERIFIED)
        increment_block_count = to_status == TaskStatus.BLOCKED
        extra_updates = ""
        extra_params: list[object] = []
        if to_status == TaskStatus.FAILED and note:
            extra_updates = ", root_cause_analysis = ?"
            extra_params.append(note)
        conn.execute(
            SQL_UPDATE_TASKS_COUNT_BY_ID_STATUS.format(extra_updates=extra_updates),
            (
                to_status.value,
                session_id,
                waiting_for,
                1 if set_ready_at else 0,
                now if set_ready_at else None,
                1 if set_completed_at else 0,
                now if set_completed_at else None,
                1 if increment_block_count else 0,
                now,
                now,
                *extra_params,
                task_id,
            ),
        )

    def _record_transition_events(
        self, conn, task_id: str, from_status: TaskStatus, to_status: TaskStatus,
        session_id: str | None, note: str | None,
    ) -> None:
        """记录 state_transition 事件 + COMPLETED 时记录 git_commit_pending 事件。"""
        self._record_event(
            conn,
            "state_transition",
            {
                "from": from_status.value,
                "to": to_status.value,
                "task_id": task_id,
                "note": note or "",
            },
            task_id=task_id,
            session_id=session_id,
        )
        # 5.15.2 修复：COMPLETED 时记录 git_commit_pending 事件，与状态转换原子落盘
        # 若后续 git commit 失败，该事件保留为 pending，可被 reconciler 重试（Outbox 模式）
        # 5.178 修复: event_type 改为 task_event（events表CHECK约束仅允许7种枚举值）
        if to_status == TaskStatus.COMPLETED:
            self._record_event(
                conn,
                "task_event",
                {"task_id": task_id},
                task_id=task_id,
                session_id=session_id,
            )

    def _post_completion_actions(
        self, task_id: str, to_status: TaskStatus,
        session_id: str | None, updated_row,
    ) -> None:
        """COMPLETED 后的自动 git commit + 提醒剩余 IN_PROGRESS 任务。"""
        if to_status != TaskStatus.COMPLETED:
            return
        # DM-202918: transition(COMPLETED)后自动git commit files_in_scope
        # 5.15.2 修复：记录 git commit 结果事件；失败时 pending 事件保留可被 reconciler 重试
        try:
            task_obj = _row_to_taskcard(updated_row)
            self._auto_commit_on_completion(task_id, task_obj)
            with self._write_tx() as ev_conn:
                self._record_event(
                    ev_conn,
                    "task_event",  # 5.178: git_commit_completed→task_event（CHECK约束）
                    {"task_id": task_id},
                    task_id=task_id,
                    session_id=session_id,
                )
        except Exception as exc:
            logger.warning("DM-202918: 自动git commit失败 (task=%s): %s", task_id, exc, exc_info=True)
            with self._write_tx() as ev_conn:
                self._record_event(
                    ev_conn,
                    "task_event",  # 5.178: git_commit_failed→task_event（CHECK约束）
                    {"task_id": task_id, "error": str(exc)[:500]},
                    task_id=task_id,
                    session_id=session_id,
                )
        # DM-400/DM-401: transition(COMPLETED)后提醒剩余IN_PROGRESS任务
        try:
            all_in_progress = len(self.list_by_status("IN_PROGRESS"))
            if all_in_progress > 0:
                if session_id:
                    same_session = self._count_by_status_and_session("IN_PROGRESS", session_id)
                    logger.warning(
                        "DM-401 提醒: 任务 %s 已关闭，仍有 %d 个 IN_PROGRESS 任务未关闭"
                        "（当前 session %s: %d 个）。"
                        " 请在 session 关门前执行 transition(COMPLETED) 或 recover_stale_claims()。",
                        task_id,
                        all_in_progress,
                        session_id,
                        same_session,
                    )
                else:
                    logger.warning(
                        "DM-401 提醒: 任务 %s 已关闭，仍有 %d 个 IN_PROGRESS 任务未关闭。"
                        " 请在 session 关门前执行 transition(COMPLETED) 或 recover_stale_claims()。",
                        task_id,
                        all_in_progress,
                    )
        except Exception:
            logger.warning("suppressed error in task_repo", exc_info=True)

    def transition(
        self,
        task_id: str,
        to_status: TaskStatus | str,
        *,
        session_id: str | None = None,
        waiting_for: str | None = None,
        note: str | None = None,
    ) -> Task:
        """执行状态机转换。

        参数
        ----
        task_id   : str           目标任务 ID
        to_status : TaskStatus    目标状态
        session_id : str | None   当前 session ID（写入 events）
        waiting_for : str | None  WAITING 状态时填写等待原因
        note : str | None         本次转换的备注（写入 events payload）

        异常
        ----
        TaskNotFoundError      — task_id 不存在
        InvalidTransitionError — 非法状态转换
        RootCauseRequiredError — FAILED 转换缺少根因分析
        SyncVerificationError  — post_sync_standard 验证失败
        CircularAcceptanceError— 循环验收未通过

        返回
        ----
        Task
            转换后重新读取的 Task 对象。
        """
        to_status = self._normalize_transition_input(to_status, note, task_id)
        self._pre_circular_acceptance(to_status, task_id)

        try:
            with self._write_tx() as conn:
                row = self._fetch_row(conn, task_id)
                if row is None:
                    raise TaskNotFoundError("任务不存在")
                self._check_transition_gates(conn, row, to_status, task_id)
                from_status = TaskStatus(row["status"])
                if not _is_valid_transition(from_status, to_status):
                    raise InvalidTransitionError(
                        f"非法转换 {from_status.value} -> {to_status.value}（task_id={task_id!r}）"
                    )
                self._apply_transition_update(
                    conn, task_id, to_status, session_id, waiting_for, note,
                )
                self._record_transition_events(
                    conn, task_id, from_status, to_status, session_id, note,
                )
                self._recalculate_dependent_status(conn, task_id, to_status)
                updated_row = self._fetch_row(conn, task_id)
        except GateViolationError as exc:
            # 写事务 ROLLBACK 会撤销同 conn 下的 gates INSERT；用独立连接再写一条，保证失败可审计。
            if self._gate_engine is not None:
                self._gate_engine._persist_result(exc.result, conn=None)
            raise

        if updated_row is None: raise RuntimeError("post-write fetch returned None")  # 5.88.2 修复: assert->if/raise

        from zephyr.governance.ops_governance.event_hook import TransitionEvent, hook_registry

        hook_registry.fire(
            TransitionEvent(
                task_id=task_id,
                from_status=from_status.value,
                to_status=to_status.value,
                note=note or "",
                session_id=session_id,
            )
        )

        self._post_completion_actions(task_id, to_status, session_id, updated_row)

        return _row_to_taskcard(updated_row)

    def _auto_commit_on_completion(self, task_id: str, task_obj: TaskCard) -> None:
        """DM-202918 + OPS-2026062512: transition(COMPLETED)后经 GitCommitGateway 自动 commit files_in_scope。

        策略（治本升级）:
        1. 原实现用 subprocess.run git commit，未防幽灵提交（多 session 共享 git index）
        2. 改用 GitCommitGateway——全局串行锁 + 选择性 stash + 受限 commit
        3. GitCommitGateway 自动追加 [GW:<session_id>] 标记 + 设置 ZEPHYR_COMMIT_GATEWAY=1
        4. 无文件可提交时跳过(不报错)

        修复历史:
        - 2026-06-23: git commit 不带文件参数会提交所有 staged 文件 -> 改为 git commit -- <files>
        - 2026-06-25: 仍未防幽灵提交（pre-commit stash 冲突）-> 改用 GitCommitGateway 治本
        """
        files_in_scope = getattr(task_obj, "files_in_scope", None) or []
        if not files_in_scope:
            return

        import os

        existing_files = [f for f in files_in_scope if os.path.isfile(f)]
        if not existing_files:
            return

        # 使用 GitCommitGateway 串行化 commit（治本：防幽灵提交）
        try:
            from zephyr.gov_enforcement.rule_bridge.git_commit_gateway import (
                CommitStatus,
                GitCommitGateway,
            )

            session_id = getattr(task_obj, "session_id", None) or f"task:{task_id}"
            gw = GitCommitGateway()
            commit_msg = f"auto-commit(DM-202918): task {task_id} COMPLETED"
            # Phase 2: claim files 到 registry，激活 session 隔离 stash
            claimed = gw.claim_files(session_id, existing_files)
            try:
                result = gw.commit(
                    session_id=session_id,
                    files=existing_files,
                    message=commit_msg,
                )
            finally:
                gw.release_files(session_id, claimed)
            if result.status == CommitStatus.OK:
                logger.info(
                    "DM-202918: GitCommitGateway commit 成功 (task=%s hash=%s): %s",
                    task_id, result.commit_hash[:8], result.message,
                )
            elif result.status == CommitStatus.NOTHING_TO_COMMIT:
                logger.info(
                    "DM-202918: files_in_scope 无 staged 变更，跳过 commit (task=%s)", task_id
                )
            elif result.status == CommitStatus.STASH_CONFLICT:
                logger.warning(
                    "DM-202918: commit 成功但 stash pop 失败，数据保留在 stash (task=%s): %s",
                    task_id, result.message,
                )
            else:
                logger.warning(
                    "DM-202918: GitCommitGateway commit 失败 (task=%s status=%s): %s",
                    task_id, result.status, result.message,
                )
        except Exception as e:
            logger.warning(
                "DM-202918: GitCommitGateway 异常，回退跳过 commit (task=%s): %s", task_id, e
            , exc_info=True)

    def _run_circular_acceptance(
        self,
        task_id: str,
        commands: list[str],
    ) -> None:
        """执行 post_sync_standard 循环验收。

        CIRCULAR_ACCEPTANCE_ROUNDS=2: 所有命令必须连续 2 轮返回 exit=0。
        任一命令任一轮失败 -> 抛出 CircularAcceptanceError。

        失败模式区分（DM-210625）：
          - exit=2：argparse 拒绝（flag 不存在）-> PostSyncConstructionError
            （建卡缺陷，应修复 post_sync_standard 字段而非重试）
          - exit≠0且≠2：真实工作质量问题 -> CircularAcceptanceError
          - 超时：计入 failures，按循环验收判定
        """
        import shlex
        import subprocess

        for round_num in range(1, CIRCULAR_ACCEPTANCE_ROUNDS + 1):
            failures: list[str] = []
            for cmd in commands:
                try:
                    # 5.17.7 修复：shell=True 违反 D-A-03 红线，改用 shlex.split + shell=False
                    result = subprocess.run(
                        shlex.split(cmd),
                        shell=False,
                        capture_output=True,
                        text=True,
                        timeout=120,
                    )
                    if result.returncode != 0:
                        # DM-210625: exit=2 为 argparse 拒绝（臆造 flag 建卡缺陷），
                        # 立即抛 PostSyncConstructionError 而非计入循环验收失败——
                        # 建卡缺陷不可通过重试解决，必须修复 post_sync_standard 字段。
                        if result.returncode == 2:
                            raise PostSyncConstructionError(
                                task_id, cmd, (result.stderr or "")[:200]
                            )
                        failures.append(f"命令 {cmd!r} 返回 exit={result.returncode}: {(result.stderr or '')[:200]}")
                except subprocess.TimeoutExpired:
                    failures.append(f"命令 {cmd!r} 超时（120s）")
                except PostSyncConstructionError:
                    raise
                except Exception as exc:
                    failures.append(f"命令 {cmd!r} 异常: {exc}")

            if failures:
                raise CircularAcceptanceError(task_id, round_num, failures)

    # ------------------------------------------------------------------
    # task_001_batch_review_protocol 代码强制实现（DM-200921 修复）
    # ------------------------------------------------------------------

    _BATCH_REVIEW_DIMENSIONS = (
        "checklist_completeness",
        "solution_completeness",
        "code_correctness",
        "causal_chain_validity",
        "data_consistency",
        "omission_risk",
        "drift_risk",
    )

    def batch_review(self, task_id: str, *, reviewer: str = "ai_session", session_id: str | None = None) -> dict:
        """task_001_batch_review_protocol: 7维度审查并持久化记录。"""
        import json
        import uuid

        task_card = self.get(task_id)
        if task_card is None:
            raise TaskNotFoundError(task_id)
        task = task_card.to_task() if hasattr(task_card, "to_task") else task_card

        with self._write_tx() as conn:
            rows = conn.execute(
                SQL_SELECT_TASK_REVIEWS_COUNT_BY_ID_SORTED,
                (task_id,),
            ).fetchall()
            max_round = max((r[0] for r in rows), default=0)
            current_round = max_round + 1
            consecutive_zero = 0
            checked_rounds = set()
            for r in rows:
                rnd = r[0]
                if rnd in checked_rounds:
                    continue
                checked_rounds.add(rnd)
                round_rows = [x for x in rows if x[0] == rnd]
                if round_rows and all(x[1] == 1 for x in round_rows):
                    consecutive_zero += 1
                else:
                    break

        dimensions_result = {}
        total_issues = 0
        now = now_iso()

        for dim in self._BATCH_REVIEW_DIMENSIONS:
            issues = self._evaluate_review_dimension(task, dim)
            passed = len(issues) == 0
            total_issues += len(issues)
            dimensions_result[dim] = {"issues": issues, "passed": passed}

            with self._write_tx() as conn:
                conn.execute(
                    SQL_INSERT_TASK_REVIEWS_COUNT,
                    (str(uuid.uuid4()), task_id, current_round, dim, len(issues), json.dumps(issues, ensure_ascii=False), 1 if passed else 0, reviewer, session_id, now),
                )

        if total_issues == 0:
            consecutive_zero += 1

        return {"task_id": task_id, "round": current_round, "total_issues": total_issues, "passed": total_issues == 0, "consecutive_zero": consecutive_zero, "dimensions": dimensions_result}

    def _evaluate_review_dimension(self, task: Task, dimension: str) -> list[str]:
        """执行单个维度的审查，返回问题列表。"""
        import json

        issues: list[str] = []

        def _blocked_by_list() -> list[str]:
            """Normalize blocked_by to list (handles both list[str] and JSON string)."""
            if not task.blocked_by:
                return []
            if isinstance(task.blocked_by, list):
                return task.blocked_by
            if isinstance(task.blocked_by, str):
                try:
                    return json.loads(task.blocked_by)
                except (json.JSONDecodeError, TypeError):
                    return []
            return []

        if dimension == "checklist_completeness":
            if not task.files_in_scope:
                issues.append("files_in_scope为空")
            if not task.deliverables:
                issues.append("deliverables为空")
            if not task.acceptance:
                issues.append("acceptance为空")
            if not task.rollback_instructions or len(task.rollback_instructions) < 20:
                issues.append("rollback_instructions过短(<20字)")

        elif dimension == "solution_completeness":
            required_kw = ("根因", "治根", "施工步骤", "验收标准")
            missing = [kw for kw in required_kw if kw not in task.description]
            if missing:
                issues.append(f"description缺少结构词: {missing}")
            if len(task.description) < 100:
                issues.append(f"description过短({len(task.description)}<100字)")

        elif dimension == "code_correctness":
            bl = _blocked_by_list()
            if task.blocked_by and not bl:
                issues.append("blocked_by不是有效JSON")

        elif dimension == "causal_chain_validity":
            bl = _blocked_by_list()
            for dep_id in bl:
                try:
                    with self._write_tx() as conn:
                        row = conn.execute(SQL_SELECT_TASKS_BY_ID_3, (dep_id,)).fetchone()
                    if row is None:
                        issues.append(f"blocked_by引用不存在的任务: {dep_id}")
                except Exception:
                    issues.append(f"无法验证依赖任务: {dep_id}")

        elif dimension == "data_consistency":
            bl = _blocked_by_list()
            if bl and task.status != TaskStatus.BLOCKED:
                issues.append(f"有blocked_by但status={task.status}(应BLOCKED)")
            if not bl and task.status == TaskStatus.BLOCKED:
                issues.append("无blocked_by但status=BLOCKED")

        elif dimension == "omission_risk":
            if len(task.files_in_scope) > 3:
                issues.append(f"files_in_scope={len(task.files_in_scope)}>3(粒度风险)")
            if not task.applicable_rules:
                issues.append("applicable_rules为空(未声明适用规则)")

        elif dimension == "drift_risk":
            if not task.source_blueprint or task.source_blueprint == "unknown":
                issues.append("source_blueprint为空或unknown(蓝图漂移风险)")
            if not task.allowed_touch:
                issues.append("allowed_touch为空(修改范围未限定)")

        return issues

    def get_review_status(self, task_id: str) -> dict:
        """查询任务卡的审查状态。"""
        with self._read_tx() as conn:
            rows = conn.execute(
                SQL_SELECT_TASK_REVIEWS_COUNT_BY_ID_SORTED_2,
                (task_id,),
            ).fetchall()

        if not rows:
            return {"task_id": task_id, "reviewed": False, "consecutive_zero": 0}

        rounds = {}
        for r in rows:
            rnd = r[0]
            if rnd not in rounds:
                rounds[rnd] = {"all_passed": True, "dimensions": {}}
            rounds[rnd]["dimensions"][r[1]] = {"issue_count": r[2], "passed": r[3]}
            if r[3] == 0:
                rounds[rnd]["all_passed"] = False

        consecutive_zero = 0
        for rnd in sorted(rounds.keys(), reverse=True):
            if rounds[rnd]["all_passed"]:
                consecutive_zero += 1
            else:
                break

        return {"task_id": task_id, "reviewed": True, "total_rounds": len(rounds), "consecutive_zero": consecutive_zero, "review_complete": consecutive_zero >= 2, "rounds": rounds}

    def _recalculate_dependent_status(
        self,
        conn: sqlite3.Connection,
        changed_task_id: str,
        new_status: TaskStatus,
    ) -> None:
        """当子任务状态变更时，重算依赖它的父任务状态。

        规则（蓝图 MOD-TASK_SYSTEM 盲点#1）：
        - 所有子任务 COMPLETED/VERIFIED -> 父任务 READY（解锁继续施工）
        - 任一子任务 FAILED/CANCELLED -> 父任务 BLOCKED
        - 否则不改变父任务状态
        """
        if new_status not in (
            TaskStatus.COMPLETED,
            TaskStatus.VERIFIED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED,
        ):
            return

        cursor = conn.execute(
            SQL_SELECT_TASKS_ACTIVE,
            (f"%{changed_task_id}%",),
        )
        parent_rows = cursor.fetchall()

        for parent_row in parent_rows:
            parent_task_id = parent_row["task_id"]
            parent = _row_to_taskcard(self._fetch_row(conn, parent_task_id))
            if parent is None or not parent.depends_on:
                continue

            child_statuses: list[TaskStatus] = []
            all_resolved = True
            any_failed = False
            for dep_id in parent.depends_on:
                child_row = self._fetch_row(conn, dep_id)
                if child_row is None:
                    continue
                child_status = TaskStatus(child_row["status"])
                child_statuses.append(child_status)
                if child_status not in (TaskStatus.COMPLETED, TaskStatus.VERIFIED):
                    all_resolved = False
                if child_status in (TaskStatus.FAILED, TaskStatus.CANCELLED):
                    any_failed = True

            if not child_statuses:
                continue

            parent_status = TaskStatus(parent.status.value)
            if all_resolved and parent_status in (TaskStatus.BLOCKED, TaskStatus.WAITING, TaskStatus.PENDING):
                conn.execute(
                    SQL_UPDATE_TASKS_BY_ID_STATUS_2,
                    (TaskStatus.READY.value, now_iso(), parent_task_id),
                )
                self._record_event(
                    conn,
                    "state_transition",
                    {
                        "from": parent_status.value,
                        "to": TaskStatus.READY.value,
                        "task_id": parent_task_id,
                        "note": f"所有子任务已完成（触发者: {changed_task_id}）",
                    },
                    task_id=parent_task_id,
                )
            elif any_failed and parent_status not in (TaskStatus.BLOCKED, TaskStatus.CANCELLED, TaskStatus.VERIFIED):
                conn.execute(
                    SQL_UPDATE_TASKS_COUNT_BY_ID_STATUS_2,
                    (TaskStatus.BLOCKED.value, now_iso(), parent_task_id),
                )
                self._record_event(
                    conn,
                    "state_transition",
                    {
                        "from": parent_status.value,
                        "to": TaskStatus.BLOCKED.value,
                        "task_id": parent_task_id,
                        "note": f"子任务失败触发阻塞（触发者: {changed_task_id}）",
                    },
                    task_id=parent_task_id,
                )

        if new_status in (TaskStatus.COMPLETED, TaskStatus.VERIFIED):
            self._unblock_downstream_dependents(conn, changed_task_id)

    def _block_downstream_dependents(
        self,
        conn: sqlite3.Connection,
        task_id: str,
    ) -> int:
        """将依赖当前任务的下游READY任务标记为BLOCKED并设置blocked_by。

        claim_next()认领任务后调用，确保下游任务显式显示阻塞状态。
        仅当当前任务状态为IN_PROGRESS时才阻塞下游（防止直接SQL篡改blocked_by）。
        返回被阻塞的任务数。
        """
        now = now_iso()
        claimer_row = conn.execute(SQL_SELECT_TASKS_BY_ID_2, (task_id,)).fetchone()
        if claimer_row is None or claimer_row["status"] != TaskStatus.IN_PROGRESS.value:
            logger.warning(
                "_block_downstream_dependents: task %s is not IN_PROGRESS (status=%s), skip",
                task_id,
                claimer_row["status"] if claimer_row else "NONE",
            )
            return 0

        downstream_rows = conn.execute(
            SQL_SELECT_TASKS_ACTIVE_2,
            (task_id,),
        ).fetchall()

        blocked_count = 0
        for ds_row in downstream_rows:
            ds_id = ds_row["task_id"]
            current_blocked_by = json.loads(ds_row["blocked_by"] or "[]")
            if task_id not in current_blocked_by:
                current_blocked_by.append(task_id)
            conn.execute(
                SQL_UPDATE_TASKS_BY_ID_STATUS,
                (TaskStatus.BLOCKED.value, json.dumps(current_blocked_by), now, ds_id),
            )
            self._record_event(
                conn,
                "state_transition",
                {
                    "from": "READY",
                    "to": TaskStatus.BLOCKED.value,
                    "task_id": ds_id,
                    "note": f"上游任务 {task_id} 被认领（IN_PROGRESS），自动阻塞",
                },
                task_id=ds_id,
            )
            blocked_count += 1

        if blocked_count:
            logger.info(
                "claim_next(%s): blocked %d downstream dependents",
                task_id,
                blocked_count,
            )
        return blocked_count

    def _unblock_downstream_dependents(
        self,
        conn: sqlite3.Connection,
        task_id: str,
    ) -> int:
        """清除下游任务blocked_by中当前task_id的条目，若blocked_by清空且依赖全满足则恢复READY。

        transition(COMPLETED)或recover_stale_claims()释放后调用。
        返回被解除阻塞的任务数。
        """
        now = now_iso()
        downstream_rows = conn.execute(
            SQL_SELECT_TASKS_ACTIVE_3,
            (task_id,),
        ).fetchall()

        corrupt_rows = conn.execute(
            SQL_SELECT_TASKS_ACTIVE_4,
        ).fetchall()
        for cr in corrupt_rows:
            logger.warning(
                "_unblock_downstream_dependents: task %s has corrupted blocked_by=%r, auto-repairing to []",
                cr["task_id"],
                cr["blocked_by"],
            )
            conn.execute(SQL_UPDATE_TASKS_BY_ID_BLOCKED_BY, (now, cr["task_id"]))

        unblocked_count = 0
        for ds_row in downstream_rows:
            ds_id = ds_row["task_id"]
            current_blocked_by = json.loads(ds_row["blocked_by"] or "[]")
            if task_id in current_blocked_by:
                current_blocked_by.remove(task_id)

            new_blocked_by = json.dumps(current_blocked_by)

            if not current_blocked_by:
                deps_raw = ds_row["depends_on"] or "[]"
                try:
                    deps = json.loads(deps_raw) if isinstance(deps_raw, str) else deps_raw
                except (json.JSONDecodeError, TypeError):
                    deps = []
                if not isinstance(deps, list):
                    deps = [deps] if deps else []

                all_deps_met = (
                    all(
                        conn.execute(SQL_SELECT_TASKS_BY_ID_2, (d,)).fetchone()["status"]
                        in ("COMPLETED", "VERIFIED")
                        for d in deps
                        if d
                    )
                    if deps
                    else True
                )

                if all_deps_met and ds_row["status"] == "BLOCKED":
                    conn.execute(
                        SQL_UPDATE_TASKS_BY_ID_STATUS,
                        (TaskStatus.READY.value, new_blocked_by, now, ds_id),
                    )
                    self._record_event(
                        conn,
                        "state_transition",
                        {
                            "from": "BLOCKED",
                            "to": TaskStatus.READY.value,
                            "task_id": ds_id,
                            "note": f"上游任务 {task_id} 已完成/释放，依赖全满足，自动解锁",
                        },
                        task_id=ds_id,
                    )
                    unblocked_count += 1
                else:
                    # blocked_by清空但depends_on未全满足 -> 回填所有未完成/缺失依赖到blocked_by
                    unmet_blockers = []
                    for d in deps:
                        if d:
                            dep_row = conn.execute(SQL_SELECT_TASKS_BY_ID_2, (d,)).fetchone()
                            if dep_row is None:
                                # 依赖不存在于tasks表 -> 也视为阻塞源
                                unmet_blockers.append(d)
                            elif dep_row["status"] not in (
                                TaskStatus.COMPLETED.value,
                                TaskStatus.VERIFIED.value,
                            ):
                                unmet_blockers.append(d)
                    if unmet_blockers:
                        refilled_blocked_by = json.dumps(unmet_blockers)
                    else:
                        # 不应到达此处（all_deps_met=False但所有依赖都COMPLETED/VERIFIED/不存在）
                        # 保持blocked_by为空，状态仍BLOCKED（语义：被未知原因阻塞）
                        refilled_blocked_by = new_blocked_by
                    conn.execute(
                        SQL_UPDATE_TASKS_BY_ID_BLOCKED_BY_2,
                        (refilled_blocked_by, now, ds_id),
                    )
            else:
                conn.execute(
                    SQL_UPDATE_TASKS_BY_ID_BLOCKED_BY_2,
                    (new_blocked_by, now, ds_id),
                )

        if unblocked_count:
            logger.info(
                "unblock_downstream(%s): unblocked %d dependents",
                task_id,
                unblocked_count,
            )
        return unblocked_count

    # ------------------------------------------------------------------
    # ESCALATION GOVERNANCE（GOV-TASK-004 §2.7）
    # ------------------------------------------------------------------

    def check_escalation(self, task_id: str) -> dict | None:
        """检查任务是否需要升级到 Owner。

        触发条件（GOV-TASK-004 §2.7）：
        - P0 任务 BLOCKED 超过 2 次 -> escalation:owner
        - 任何任务 BLOCKED 超过 5 次 -> escalation:owner
        - P0 任务 FAILED 2 次 -> escalation:owner

        返回 None 表示无需升级；返回 dict 表示需要升级，含 reason 和 triggers 字段。
        """
        task = self.get(task_id)
        if task is None:
            return None

        triggers = []
        is_p0 = task.priority is Priority.P0

        if is_p0 and task.block_sessions_count >= 2:
            triggers.append(f"P0 任务已 BLOCKED {task.block_sessions_count} 次（≥2）")
        elif task.block_sessions_count >= 5:
            triggers.append(f"任务已 BLOCKED {task.block_sessions_count} 次（≥5）")

        if is_p0:
            failed_count = self._count_failed_events(task_id)
            if failed_count >= 2:
                triggers.append(f"P0 任务已 FAILED {failed_count} 次（≥2）")

        if not triggers:
            return None

        return {
            "task_id": task_id,
            "priority": task.priority.value,
            "status": task.status.value,
            "block_sessions_count": task.block_sessions_count,
            "triggers": triggers,
            "escalation_level": "escalation:owner",
            "governance_ref": "GOV-TASK-004 §2.7",
        }

    def check_all_escalations(self) -> list[dict]:
        """检查所有活跃任务是否需要升级。"""
        escalations = []
        for task in self.list_active():
            result = self.check_escalation(task.task_id)
            if result is not None:
                escalations.append(result)
        return escalations

    def _count_failed_events(self, task_id: str) -> int:
        """统计任务在 events 表中 FAILED 的次数。"""
        row = self._conn.execute(
            SQL_SELECT_EVENTS_COUNT_BY_ID,
            (task_id,),
        ).fetchone()
        return row[0] if row else 0

    # ------------------------------------------------------------------
    # TIMEOUT GOVERNANCE（GOV-TASK-004 §2.6）
    # ------------------------------------------------------------------

    def _is_timeout_exempt(self, task_id: str) -> bool:
        """检查任务是否携带 exempt:timeout 豁免标签（GOV-TASK-004 §2.6）。"""
        task = self.get(task_id)
        if task is None:
            return False
        tags = getattr(task, "tags", [])
        return "exempt:timeout" in tags

    def check_task_timeout(self, task_id: str) -> dict | None:
        """检查任务是否超时，返回超时信息或 None。

        GOV-TASK-004 §2.6 豁免规则：
        - 标签含 exempt:timeout -> 跳过超时检查
        - 依赖外部第三方的任务（blocked_reason 注明"外部依赖"）-> 跳过超时检查
        """
        task = self.get(task_id)
        if task is None:
            return None

        if self._is_timeout_exempt(task_id):
            return None

        waiting_for = getattr(task, "waiting_for", "") or ""
        if "外部依赖" in waiting_for:
            return None

        timeout_minutes = getattr(task, "timeout_minutes", 30)
        created_str = getattr(task, "created_at", None)
        if not created_str:
            return None
        try:
            from datetime import datetime as dt

            created = dt.fromisoformat(str(created_str))
            if created.tzinfo is None:
                created = created.replace(tzinfo=UTC)
            elapsed = (dt.now(UTC) - created).total_seconds() / 60
        except (ValueError, TypeError):
            return None

        if elapsed > timeout_minutes:
            return {
                "task_id": task_id,
                "status": task.status.value,
                "priority": task.priority.value,
                "timeout_minutes": timeout_minutes,
                "elapsed_minutes": round(elapsed, 1),
                "exempt": False,
                "governance_ref": "GOV-TASK-004 §2.6",
            }
        return None

    # ------------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------------

    def delete(self, task_id: str) -> bool:
        """
        软删除任务记录。设置 is_deleted=1 + deleted_at 时间戳。

        返回
        ----
        bool
            True 表示成功标记删除；False 表示 task_id 不存在或已被删除。
        """
        with self._write_tx() as conn:
            cursor = conn.execute(
                SQL_UPDATE_TASKS_ACTIVE_BY_ID_IS_DELETED,
                (now_iso(), now_iso(), task_id),
            )
            deleted = cursor.rowcount > 0
            if deleted:
                conn.execute(SQL_DELETE_TASK_FILES_BY_ID, (task_id,))
        return deleted

    def hard_delete(self, task_id: str) -> bool:
        """
        物理删除任务记录（级联 SET NULL events.task_id，级联删除 task_files）。

        仅在数据清理脚本中使用，日常开发用 soft delete。
        """
        with self._write_tx() as conn:
            conn.execute(SQL_DELETE_TASK_FILES_BY_ID, (task_id,))
            cursor = conn.execute(SQL_DELETE_TASKS_BY_ID, (task_id,))
            deleted = cursor.rowcount > 0
        return deleted

    # ------------------------------------------------------------------
    # LIST 查询
    # ------------------------------------------------------------------

    def list_by_status(self, status: TaskStatus | str) -> list[TaskCard]:
        """查询指定状态的所有任务（按 phase ASC, updated_at DESC 排序）。"""
        if isinstance(status, str):
            status = TaskStatus(status)
        cursor = self._conn.execute(
            SQL_SELECT_TASKS_ACTIVE_BY_STATUS_SORTED,
            (status.value,),
        )
        return [_row_to_taskcard(r) for r in cursor.fetchall()]

    def list_by_phase(self, phase: int) -> list[TaskCard]:
        """查询指定 Phase 的所有任务（按 status ASC, task_id ASC 排序）。"""
        cursor = self._conn.execute(
            SQL_SELECT_TASKS_ACTIVE_BY_PHASE_SORTED,
            (phase,),
        )
        return [_row_to_taskcard(r) for r in cursor.fetchall()]

    def list_by_session(self, session_id: str) -> list[TaskCard]:
        """查询指定 session_id 的所有任务。"""
        cursor = self._conn.execute(
            SQL_SELECT_TASKS_ACTIVE_BY_SESSION_SORTED,
            (session_id,),
        )
        return [_row_to_taskcard(r) for r in cursor.fetchall()]

    def _count_by_status_and_session(self, status: str, session_id: str) -> int:
        """统计指定 session 下指定状态的任务数（DM-400: 用于提醒未关闭任务）。"""
        cursor = self._conn.execute(
            SQL_SELECT_TASKS_ACTIVE_COUNT_BY_STATUS,
            (status, session_id),
        )
        return cursor.fetchone()[0]

    def query_tasks(
        self,
        *,
        phase: int | None = None,
        status: TaskStatus | str | None = None,
        session_id: str | None = None,
        file_path_glob: str | None = None,
        limit: int = 50,
    ) -> list[TaskCard]:
        """复合条件列表（``task_manager.list_tasks`` / tool-contracts.yaml）。"""
        clauses = ["is_deleted = 0"]
        params: list[object] = []
        if phase is not None:
            clauses.append("phase = ?")
            params.append(phase)
        if status is not None:
            st = status.value if isinstance(status, TaskStatus) else str(status)
            clauses.append("status = ?")
            params.append(st)
        if session_id is not None:
            clauses.append("session_id = ?")
            params.append(session_id)
        where_sql = " AND ".join(clauses)
        cap = min(max(limit, 1), 500)
        fetch_limit = min(cap * 20, 2000) if file_path_glob else cap
        sql = SQL_SELECT_TASKS_SORTED.format(where_sql=where_sql)
        params.append(fetch_limit)
        cursor = self._conn.execute(sql, tuple(params))
        tasks = [_row_to_taskcard(r) for r in cursor.fetchall()]
        if not file_path_glob:
            return tasks[:cap]
        matched: list[TaskCard] = []
        for t in tasks:
            for r in self._conn.execute(
                SQL_SELECT_TASK_FILES_BY_ID,
                (t.task_id,),
            ):
                if fnmatch.fnmatch(r["file_path"], file_path_glob):
                    matched.append(t)
                    break
            if len(matched) >= cap:
                break
        return matched[:cap]

    def list_by_namespace(self, namespace: TaskNamespace | str) -> list[Task]:
        """查询指定命名空间的所有任务（按 seq ASC 排序）。"""
        if isinstance(namespace, TaskNamespace):
            namespace = namespace.value
        cursor = self._conn.execute(
            SQL_SELECT_TASKS_ACTIVE_BY_NAMESPACE_SORTED,
            (namespace,),
        )
        return [_row_to_taskcard(r) for r in cursor.fetchall()]

    # ------------------------------------------------------------------
    # task_files 读写（#21 裁定：N:N 映射）
    # ------------------------------------------------------------------

    def add_file(self, task_id: str, file_path: str, role: str = "in_scope") -> None:
        """为任务添加文件映射。role 可选 primary/in_scope/output。"""
        with self._write_tx() as conn:
            conn.execute(
                SQL_INSERT_TASK_FILES_OR_IGNORE,
                (task_id, file_path, role),
            )

    def remove_file(self, task_id: str, file_path: str) -> None:
        """移除任务的文件映射。"""
        with self._write_tx() as conn:
            conn.execute(
                SQL_DELETE_TASK_FILES_BY_ID_2,
                (task_id, file_path),
            )

    def get_files(self, task_id: str) -> list[dict[str, str]]:
        """获取任务的所有文件映射，返回 [{file_path, role}, ...]。"""
        cursor = self._conn.execute(
            SQL_SELECT_TASK_FILES_BY_ID_SORTED,
            (task_id,),
        )
        return [{"file_path": r["file_path"], "role": r["role"]} for r in cursor.fetchall()]

    def get_tasks_for_file(self, file_path: str) -> list[str]:
        """获取涉及指定文件的所有任务 ID。"""
        cursor = self._conn.execute(
            SQL_SELECT_TASK_FILES_BY_FILE_PATH_SORTED,
            (file_path,),
        )
        return [r["task_id"] for r in cursor.fetchall()]

    def next_seq(self, namespace: TaskNamespace | str | None = None) -> int:
        """获取下一个序号。指定 namespace 时返回该命名空间内自增；否则返回全局最大值+1。"""
        if namespace is not None:
            if isinstance(namespace, TaskNamespace):
                namespace = namespace.value
            cursor = self._conn.execute(
                SQL_SELECT_TASKS_BY_NAMESPACE,
                (namespace,),
            )
        else:
            cursor = self._conn.execute(SQL_SELECT_TASKS)
        return cursor.fetchone()["next_seq"]

    def list_active(self) -> list[Task]:
        """查询活跃任务（IN_PROGRESS / READY / RETRY / WAITING），排除已删除。"""
        cursor = self._conn.execute(
            SQL_SELECT_TASKS_ACTIVE_BY_STATUS_SORTED_2
        )
        return [_row_to_taskcard(r) for r in cursor.fetchall()]

    def count_by_status(self) -> dict[str, int]:
        """按状态统计任务数量（排除已删除）。"""
        cursor = self._conn.execute(SQL_SELECT_TASKS_ACTIVE_COUNT_GROUPED)
        return {row["status"]: row["cnt"] for row in cursor.fetchall()}

    # ------------------------------------------------------------------
    # JSON1 查询（SH-DB-001 v2.0）
    # ------------------------------------------------------------------

    def list_by_dependency(self, dependency_task_id: str) -> list[TaskCard]:
        """查询所有依赖给定 task_id 的任务（利用 JSON1 扩展遍历 depends_on JSON 数组）。"""
        cursor = self._conn.execute(
            SQL_SELECT_TASKS_ACTIVE_SORTED,
            (dependency_task_id,),
        )
        return [_row_to_taskcard(r) for r in cursor.fetchall()]

    def list_by_tag(self, tag: str) -> list[TaskCard]:
        """查询所有包含指定 tag 的任务（利用 JSON1 扩展遍历 tags JSON 数组）。"""
        cursor = self._conn.execute(
            SQL_SELECT_TASKS_ACTIVE_SORTED_2,
            (tag,),
        )
        return [_row_to_taskcard(r) for r in cursor.fetchall()]

    def list_by_blocked_by(self, blocker_task_id: str) -> list[TaskCard]:
        """查询所有被给定 task_id 阻塞的任务（利用 JSON1 扩展遍历 blocked_by JSON 数组）。"""
        cursor = self._conn.execute(
            SQL_SELECT_TASKS_ACTIVE_SORTED_3,
            (blocker_task_id,),
        )
        return [_row_to_taskcard(r) for r in cursor.fetchall()]

    # ------------------------------------------------------------------
    # UPSERT（scaffold 批量补录）
    # ------------------------------------------------------------------

    def upsert(self, task: Task, *, files: list[dict[str, str]] | None = None) -> Task:
        """
        ON CONFLICT DO UPDATE 语义：task_id 已存在则更新（保留 created_at），否则新建。

        用于 scaffold 任务补录（T-1-06）。
        """
        now = now_iso()
        with self._write_tx() as conn:
            conn.execute(
                SQL_INSERT_TASKS_ACTIVE_COUNT,
                _serialize_for_db(task),
            )
            if files:
                conn.execute(SQL_DELETE_TASK_FILES_BY_ID, (task.task_id,))
                for f in files:
                    conn.execute(
                        SQL_INSERT_TASK_FILES_OR_IGNORE,
                        (task.task_id, f["file_path"], f.get("role", "in_scope")),
                    )
            row = self._fetch_row(conn, task.task_id)
        if row is None: raise RuntimeError("post-write fetch returned None")  # 5.88.2 修复: assert->if/raise
        return _row_to_taskcard(row)

    # ------------------------------------------------------------------
    # Multi-Worker Batch Coordination (MOD-INF-016)
    # ------------------------------------------------------------------

    def claim_next(self, batch_id: str, worker_id: str) -> TaskCard | None:
        """原子认领批量中下一个依赖已满足的 READY 任务。

        多个 AI 对话并发调用 -> 各拿各的，不重复。
        依赖检查：depends_on 为 NULL/空 或所有依赖均已 COMPLETED。

        返回 None 表示当前无可认领任务。
        """
        now = datetime.now(UTC).isoformat()
        with self._write_tx() as conn:
            row = conn.execute(
                SQL_UPDATE_TASKS_ACTIVE_BY_ID_SORTED_STATUS,
                {"batch_id": batch_id, "worker_id": worker_id, "now": now},
            ).fetchone()
            if row is None:
                return None
            claimed_id = row["task_id"]
            self._block_downstream_dependents(conn, claimed_id)
            return _row_to_taskcard(row)

    def recover_stale_claims(self, batch_id: str, timeout_minutes: int = 30) -> int:
        """释放超时未完成的 IN_PROGRESS 任务 -> 回到 READY。

        每个 AI session 调用 claim_next() 前先调此方法，确保崩溃/超时的任务自动复活。
        返回回收的任务数。
        """
        from datetime import timedelta as td

        cutoff = (datetime.now(UTC) - td(minutes=timeout_minutes)).isoformat()
        with self._write_tx() as conn:
            stale_rows = conn.execute(
                SQL_SELECT_TASKS_BY_STATUS,
                {"batch_id": batch_id, "cutoff": cutoff},
            ).fetchall()

            if not stale_rows:
                return 0

            released_ids = [r["task_id"] for r in stale_rows]
            conn.execute(
                SQL_UPDATE_TASKS_BY_STATUS_STATUS,
                {"batch_id": batch_id, "cutoff": cutoff, "now": datetime.now(UTC).isoformat()},
            )

            for released_id in released_ids:
                self._unblock_downstream_dependents(conn, released_id)

            return len(released_ids)

    def batch_progress(self, batch_id: str) -> dict[str, int]:
        """返回批量进度聚合：READY / IN_PROGRESS / COMPLETED / FAILED 各多少。"""
        with self._write_tx() as conn:
            rows = conn.execute(
                SQL_SELECT_TASKS_ACTIVE_COUNT_BY_BATCH_GROUPED,
                {"batch_id": batch_id},
            ).fetchall()
        result = {"READY": 0, "IN_PROGRESS": 0, "COMPLETED": 0, "FAILED": 0, "TOTAL": 0}
        for r in rows:
            s = r["status"]
            if s in result:
                result[s] = r["cnt"]
            result["TOTAL"] += r["cnt"]
        return result

    # ------------------------------------------------------------------
    # 自动拆分（GOV-TASK-001 §6.5）
    # ------------------------------------------------------------------

    def auto_split_task(
        self,
        task_id_or_task: str | Task,
        *,
        session_id: str | None = None,
        split_strategy: str = "auto",
    ) -> list[TaskCard]:
        """将超粒度任务卡自动拆分为多张原子卡。

        参数
        ----
        task_id_or_task : str | Task
            目标任务 ID 或 Task 对象。
        session_id : str | None
            当前 session ID。
        split_strategy : str
            拆分策略: auto / by_deliverable / by_file / by_acceptance / by_target。

        返回
        ----
        list[TaskCard]
            拆分后的子卡列表。空列表 = 无需拆分或拆分失败。
        """
        if isinstance(task_id_or_task, str):
            task_card = self.get(task_id_or_task)
            if task_card is None:
                return []
            task_id = task_id_or_task
        else:
            task_card = task_id_or_task
            task_id = task_id_or_task.task_id

        violations = self._validate_granularity(task_card)
        if not violations:
            return []

        strategy = self._determine_split_strategy(violations, split_strategy)

        if strategy == "by_deliverable":
            sub_tasks = self._split_by_deliverable(task_card, session_id)
        elif strategy == "by_file":
            sub_tasks = self._split_by_file(task_card, session_id)
        elif strategy == "by_acceptance":
            sub_tasks = self._split_by_acceptance(task_card, session_id)
        elif strategy == "by_target":
            sub_tasks = self._split_by_target(task_card, session_id)
        else:
            return []

        if not sub_tasks:
            return []

        created: list[TaskCard] = []
        for sub_task in sub_tasks:
            try:
                card = self.create(sub_task, allow_direct_create=True)
                created.append(card)
            except Exception:
                logger.exception("auto_split: 创建子卡 %s 失败", sub_task.task_id, exc_info=True)
                for c in created:
                    try:
                        self.hard_delete(c.task_id)
                    except Exception as e:
                        logger.warning("suppressed error in task_repo", exc_info=True)
                return []

        for i in range(1, len(created)):
            prev_id = created[i - 1].task_id
            curr_id = created[i].task_id
            with self._write_tx() as conn:
                conn.execute(
                    SQL_UPDATE_TASKS_BY_ID_DEPENDS_ON,
                    (json.dumps([prev_id], ensure_ascii=False), curr_id),
                )

        if isinstance(task_id_or_task, str):
            try:
                self.transition(
                    task_id,
                    TaskStatus.CANCELLED,
                    note=f"auto_split: 拆分为 {[c.task_id for c in created]}",
                    session_id=session_id,
                )
            except (InvalidTransitionError, TaskNotFoundError):
                pass

        return created

    def _determine_split_strategy(self, violations: list[str], requested: str) -> str:
        """根据违规项和请求策略确定拆分方式。"""
        if requested != "auto":
            return requested

        for v in violations:
            if v.startswith("R1:"):
                return "by_deliverable"
        for v in violations:
            if v.startswith("R2:"):
                return "by_file"
        for v in violations:
            if v.startswith("R3:"):
                return "by_acceptance"
        for v in violations:
            if v.startswith("R4:"):
                return "by_target"
        return "by_deliverable"

    def _split_by_deliverable(self, parent: TaskCard, session_id: str | None) -> list[Task]:
        """按 deliverables 拆分：每个产出物一张卡。"""
        if len(parent.deliverables) <= 1:
            return []
        results: list[Task] = []
        for i, deliverable in enumerate(parent.deliverables):
            sub = self._make_sub_task(
                parent,
                seq_suffix=f"-d{i + 1}",
                title=f"{parent.title} [产出{i + 1}]",
                deliverables=[deliverable],
                session_id=session_id,
            )
            results.append(sub)
        return results

    def _split_by_file(self, parent: TaskCard, session_id: str | None) -> list[Task]:
        """按 files_in_scope 拆分：每 3 个文件一组。"""
        if len(parent.files_in_scope) <= 3:
            return []
        results: list[Task] = []
        chunk_size = 3
        for i in range(0, len(parent.files_in_scope), chunk_size):
            chunk = parent.files_in_scope[i : i + chunk_size]
            sub = self._make_sub_task(
                parent,
                seq_suffix=f"-f{i // chunk_size + 1}",
                title=f"{parent.title} [文件组{i // chunk_size + 1}]",
                files_in_scope=chunk,
                session_id=session_id,
            )
            results.append(sub)
        return results

    def _split_by_acceptance(self, parent: TaskCard, session_id: str | None) -> list[Task]:
        """按 acceptance 拆分：每个验收点一张卡。"""
        if len(parent.acceptance) <= 1:
            return []
        results: list[Task] = []
        for i, criterion in enumerate(parent.acceptance):
            sub = self._make_sub_task(
                parent,
                seq_suffix=f"-a{i + 1}",
                title=f"{parent.title} [验收{i + 1}]",
                acceptance=[criterion],
                session_id=session_id,
            )
            results.append(sub)
        return results

    def _split_by_target(self, parent: TaskCard, session_id: str | None) -> list[Task]:
        """按 construction_targets 拆分：每个施工步骤一张卡。"""
        import re

        steps = re.split(r"(?=第[一二三四五六七八九十\d]+步)", parent.description)
        steps = [s.strip() for s in steps if s.strip()]
        if not steps:
            steps = re.split(r"(?=STEP\s*\d+)", parent.description, flags=re.IGNORECASE)
            steps = [s.strip() for s in steps if s.strip()]
        if len(steps) <= 1:
            return []
        results: list[Task] = []
        for i, step_desc in enumerate(steps):
            sub = self._make_sub_task(
                parent,
                seq_suffix=f"-t{i + 1}",
                title=f"{parent.title} [步骤{i + 1}]",
                description=step_desc,
                session_id=session_id,
            )
            results.append(sub)
        return results

    def _make_sub_task(
        self,
        parent: TaskCard,
        *,
        seq_suffix: str,
        title: str,
        session_id: str | None = None,
        deliverables: list[str] | None = None,
        files_in_scope: list[str] | None = None,
        acceptance: list[str] | None = None,
        description: str | None = None,
    ) -> Task:
        """从父任务创建子任务 Task 对象。"""
        now = datetime.now(UTC)
        return Task(
            task_id=f"{parent.task_id}{seq_suffix}",
            namespace=parent.namespace,
            seq=parent.seq,
            title=title,
            status=TaskStatus.PENDING,
            priority=parent.priority,
            phase=parent.phase,
            execution_model=parent.execution_model,
            model_rationale=parent.model_rationale,
            fallback_model=parent.fallback_model,
            safety_level=parent.safety_level,
            directive=parent.directive,
            idempotent=parent.idempotent,
            classification=parent.classification,
            evolution_policy=parent.evolution_policy,
            estimate_hours=max(parent.estimate_hours / 3, 0.1),
            actual_hours=parent.actual_hours,
            files_in_scope=files_in_scope if files_in_scope is not None else parent.files_in_scope[:3],
            deliverables=deliverables if deliverables is not None else parent.deliverables[:1],
            acceptance=acceptance if acceptance is not None else parent.acceptance[:1],
            depends_on=[],
            tags=list(parent.tags) + ["auto-split", f"parent:{parent.task_id}"],
            session_id=session_id or parent.session_id,
            waiting_for=None,
            ready_at=None,
            completed_at=None,
            created_at=now,
            updated_at=now,
            source_blueprint=parent.source_blueprint,
            source_section=parent.source_section,
            description=description or parent.description,
            allowed_touch=list(parent.allowed_touch),
            applicable_rules=list(parent.applicable_rules),
            rollback_instructions=parent.rollback_instructions,
            post_sync_standard=list(parent.post_sync_standard),
            upstream_files=list(parent.upstream_files),
            downstream_outputs=list(parent.downstream_outputs),
            forbidden_touch=list(parent.forbidden_touch),
            context_assembly_manifest=list(parent.context_assembly_manifest),
            estimated_tokens=max(parent.estimated_tokens // 3, 500),
            timeout_minutes=parent.timeout_minutes,
        )

    # ------------------------------------------------------------------
    # 门禁评估条件
    # ------------------------------------------------------------------

    def _should_evaluate_gate(self, gate_id: str) -> bool:
        """判断是否应评估指定门禁。

        DM-200921 修复: G7(交付门禁)不可绕过。
        当 self._gate_engine 不为 None 时，G7 始终评估（忽略 _enable_gate）。
        """
        if self._gate_engine is None:
            return False
        if gate_id == "G7":
            return True
        return self._enable_gate

    # ------------------------------------------------------------------
    # 风险评估（幻觉/漂移）
    # ------------------------------------------------------------------

    @staticmethod
    def compute_hallucination_risk(task: Task) -> float:
        """计算任务幻觉风险评分（0.0=安全，1.0=极度危险）。

        评分维度：
        - description 缺少结构词 -> +0.2/词
        - description 过短（<100字）-> +0.3
        - 无 allowed_touch -> +0.2
        - 无 acceptance -> +0.2
        - 无 source_blueprint -> +0.1
        """
        score = 0.0
        required_keywords = ("根因", "治根", "施工步骤", "验收标准")
        missing = [kw for kw in required_keywords if kw not in task.description]
        score += len(missing) * 0.2
        if len(task.description) < 100:
            score += 0.3
        if not task.allowed_touch:
            score += 0.2
        if not task.acceptance:
            score += 0.2
        if not getattr(task, "source_blueprint", ""):
            score += 0.1
        return min(score, 1.0)

    @staticmethod
    def compute_drift_risk(task: Task) -> float:
        """计算任务漂移风险评分（0.0=安全，1.0=极度危险）。

        评分维度：
        - files_in_scope > 3 -> +0.3
        - deliverables > 1 -> +0.3
        - 无 forbidden_touch -> +0.2
        - 无 rollback_instructions -> +0.2
        """
        score = 0.0
        if len(task.files_in_scope) > 3:
            score += 0.3
        if len(task.deliverables) > 1:
            score += 0.3
        if not task.forbidden_touch:
            score += 0.2
        if not task.rollback_instructions:
            score += 0.2
        return min(score, 1.0)

    def drift_check(self, task_id: str) -> dict | None:
        """检查指定任务的漂移风险，返回风险报告或 None。

        返回 dict 含 task_id、hallucination_risk、drift_risk、violations 字段。
        """
        task = self.get(task_id)
        if task is None:
            return None
        h_risk = self.compute_hallucination_risk(task)
        d_risk = self.compute_drift_risk(task)
        violations = self._validate_granularity(task)
        return {
            "task_id": task_id,
            "hallucination_risk": h_risk,
            "drift_risk": d_risk,
            "violations": violations,
            "overall_risk": max(h_risk, d_risk),
        }

    # ------------------------------------------------------------------
    # 完成候选检测
    # ------------------------------------------------------------------

    def detect_completed_candidates(self) -> list[TaskCard]:
        """检测可能应标记为 COMPLETED 但仍处于 IN_PROGRESS 的任务。

        条件：IN_PROGRESS 且 updated_at 距今超过 timeout_minutes。
        """

        now = datetime.now(UTC)
        candidates: list[TaskCard] = []
        in_progress = self.list_by_status(TaskStatus.IN_PROGRESS)
        for task in in_progress:
            timeout_minutes = getattr(task, "timeout_minutes", 30)
            if self._is_timeout_exempt(task.task_id):
                continue
            updated_str = str(task.updated_at)
            try:
                updated = datetime.fromisoformat(updated_str)
                if updated.tzinfo is None:
                    updated = updated.replace(tzinfo=UTC)
                elapsed = (now - updated).total_seconds() / 60
                if elapsed > timeout_minutes:
                    candidates.append(task)
            except (ValueError, TypeError):
                continue
        return candidates

    # ------------------------------------------------------------------
    # DISABLED: 删除逻辑（2026-06-10: 任务卡永久保留，禁止删除）
    # ------------------------------------------------------------------

    def delete_completed_tasks_in_phase(self, phase: int) -> int:
        """DISABLED: 任务卡永久保留，禁止删除。始终返回 0。"""
        logger.warning(
            "delete_completed_tasks_in_phase(phase=%s) 已禁用（2026-06-10: 任务卡永久保留），调用被忽略",
            phase,
        )
        return 0

    def _auto_phase_cleanup_hook(self, phase: int) -> int:
        """DISABLED: 任务卡永久保留，禁止删除。始终返回 0。"""
        return 0

    def cleanup_terminal_tasks(self) -> int:
        """DISABLED: 任务卡永久保留，禁止删除。始终返回 0。"""
        logger.warning("cleanup_terminal_tasks() 已禁用（2026-06-10: 任务卡永久保留），调用被忽略")
        return 0

    # ------------------------------------------------------------------
    # Event Sourcing（append_and_project）
    # ------------------------------------------------------------------

    def append_and_project(
        self,
        task_id: str,
        event_type: str,
        payload: dict[str, object],
        *,
        session_id: str | None = None,
    ) -> TaskCard | None:
        """追加事件并投影到当前状态（Event Sourcing 模式）。

        步骤：
        1. 写入 events 表
        2. 从 events 表重新投影当前状态
        3. 返回投影后的 TaskCard

        参数
        ----
        task_id : str
            目标任务 ID。
        event_type : str
            事件类型（如 state_transition / task_event）。
        payload : dict
            事件负载。
        session_id : str | None
            当前 session ID。

        返回
        ----
        TaskCard | None
            投影后的任务状态，task_id 不存在返回 None。
        """
        with self._write_tx() as conn:
            row = self._fetch_row(conn, task_id)
            if row is None:
                return None
            self._record_event(
                conn,
                event_type,
                payload,
                task_id=task_id,
                session_id=session_id,
            )
            if self._enable_gate and self._gate_engine is not None:
                try:
                    proj_engine = ProjectionEngine(self._db_path)
                    proj_engine.rebuild_from_events(task_id, conn=conn)
                except Exception:
                    logger.exception("append_and_project: 投影重建失败 task_id=%s", task_id, exc_info=True)
            updated_row = self._fetch_row(conn, task_id)
        if updated_row is None:
            return None
        return _row_to_taskcard(updated_row)


# ---------------------------------------------------------------------------
# 状态机查询助手（不依赖实例）
# ---------------------------------------------------------------------------


def allowed_transitions(status: TaskStatus | str) -> frozenset[TaskStatus]:
    """返回给定状态的合法目标状态集合。"""
    if isinstance(status, str):
        status = TaskStatus(status)
    return _ALLOWED_TRANSITIONS.get(status, frozenset())


def is_terminal(status: TaskStatus | str) -> bool:
    """判断是否为终态（VERIFIED / CANCELLED）。"""
    if isinstance(status, str):
        status = TaskStatus(status)
    return not _ALLOWED_TRANSITIONS.get(status, frozenset())


# ---------------------------------------------------------------------------
# FTS5 全文搜索（T-DB-010）
# ---------------------------------------------------------------------------


def search(
    db_path: Path | str,
    query: str,
    *,
    limit: int = 50,
    namespace: str | None = None,
) -> list[dict[str, object]]:
    """T-DB-010: 使用 FTS5 全文搜索任务。

    query
        搜索词（支持 FTS5 查询语法）。
    namespace
        可选命名空间过滤。
    limit
        返回结果上限（默认 50，最大 200）。

    返回 list[dict{task_id, title, status, priority, phase, snippet}]
    """
    resolved = Path(db_path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    conn = get_db_connection(str(resolved))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL")
    try:
        cursor = conn.execute(SQL_SELECT_SQLITE_MASTER)
        has_fts = cursor.fetchone() is not None
        if not has_fts:
            conn.execute(
                SQL_CREATE_IF_VIRTUAL
            )
            conn.execute(SQL_INSERT_TASKS_FTS)

        cols = "task_id, title, status, priority, phase"
        params: list[object] = [query]
        if namespace:
            params.append(namespace)
            limit_val = min(max(limit, 1), 200)
            params.append(limit_val)
            result = conn.execute(
                SQL_SELECT_TASKS_FTS_ACTIVE_SORTED.format(cols=cols),
                tuple(params),
            )
        else:
            limit_val = min(max(limit, 1), 200)
            params.append(limit_val)
            result = conn.execute(
                SQL_SELECT_TASKS_FTS_ACTIVE_SORTED_2.format(cols=cols),
                tuple(params),
            )
        return [dict(r) for r in result.fetchall()]
    finally:
        conn.close()
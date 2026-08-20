# [BLUEPRINT] MOD-REMEDIATION_PROGRESS | docs/03_modules/_cross_layer/audit_orchestrator/blueprint.md | §remediation-progress
# [MODULE] zephyr.governance.audit.remediation_progress_reconciler
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit.reconciliation_registry (ReconcileResult, ReconcilerSpec)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] remediation_progress 表持久化治本维度进度；>90天未更新且非 completed/deferred → block_next；record_remediation_progress 幂等（INSERT OR REPLACE）
# [MODIFY-GUARD] SQL_CREATE_REMEDIATION_PROGRESS 表结构；_BLOCK_SECONDS 阈值
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] reconcile 永不抛异常——DB 查询失败降级为 ReconcileResult(action="warn")
# [TESTS] scripts/governance/test_remediation_progress_smoke.py
# [A_module] module_id=MOD-REMEDIATION_PROGRESS | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: reconciler 是 commit 事件触发(非 cron/manual)
"""

remediation_progress_reconciler.py — 治本进度持久化 + 新鲜度对账（#ARCH-GOV-CONVERGENCE-META Phase 3.1）。

治本动机
--------
治本工作本身的进度（architecture_issue_registry.yaml 的 fix_phase 字段）曾经误标
"Phase 1-4 已完成"但实际 Phase 3 (1)(2)(3) 未完成——说明"治本进度"本身是 fail-silent
的（AI 跨对话看不到真实进度，凭 YAML 文本判断会误判）。

本模块让治本进度满足三要素（与 #ARCH-DEPGRAPH-RECONCILER-FAILSILENT 同框架）：
- **持久化**：remediation_progress 表（SQLite governance.db，复用 reconcile_execution_log 模式）
- **可发现**：M16 指标（architecture_health_dashboard）+ AI 冷启动查询 query_all_dimensions()
- **可阻断**：>90 天未更新且非 completed/deferred → block_next（下次 commit 硬阻断）

表结构
------
remediation_progress:
    dimension_id        TEXT PRIMARY KEY   -- 如 "ARCH-DEPGRAPH-RECONCILER-FAILSILENT"
    dimension_kind      TEXT NOT NULL       -- "issue" | "root_cause" | "phase"
    title               TEXT NOT NULL
    status              TEXT NOT NULL       -- not_started|in_progress|completed|blocked|deferred
    last_updated        TEXT NOT NULL       -- ISO timestamp UTC
    last_session_id     TEXT
    last_commit_sha     TEXT
    target_completion_date TEXT             -- ISO date (nullable)
    blocker_reason      TEXT                -- status='blocked' 时必填
    details_json        TEXT                -- JSON: 自由字段（phase 清单、commit 引用等）

使用方式
--------
1. 治本启动时调 record_remediation_progress(dimension_id, status="in_progress", ...)
2. 治本完成时调 record_remediation_progress(dimension_id, status="completed", ...)
3. commit 时 reconciler 自动检查 staleness（>90天 → block_next）
4. AI 冷启动调 query_all_dimensions() 获取全部治本进度
5. dashboard M16 指标报告超期维度数

设计裁定
--------
- SQLite governance.db（非 PG depgraph）——治本进度是运行时观测数据，不需要 PG 事务一致性
- detail_json 完整记录（不截断）——治本诊断需要完整上下文
- 90 天阈值——治本维度通常 1-3 个月有进展，>90 天无更新 = 遗忘/停滞
- block_next 而非 critical_warn——治本停滞是架构债累积根源，必须强制干预

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: RemediationProgressRecord 治本进度记录 dataclass
#   fields: dimension_id + dimension_kind + title + status + session_id + commit_sha + target_date + blocker_reason + details
#   code: RemediationProgressRecord L85
# - id: I2
#   name: remediation_progress 表 SQLite
#   fields: governance.db 中治本维度进度（dimension_id 主键 + status + last_updated 等 10 列）
#   code: SQL_CREATE_REMEDIATION_PROGRESS L114
# 层: 算法
# - id: A1
#   name_zh: ① 进度幂等写入
#   name_en: record_remediation_progress
#   intro: 记录或更新一条治本维度进度，枚举校验后 INSERT OR REPLACE 落库
#   desc: dimension_kind/status 枚举校验 → details 序列化 JSON → 建表（IF NOT EXISTS）→ INSERT OR REPLACE（now_utc 时间戳）；异常降级 False
#   inputs: I1 I2
#   outputs: bool 成功标识 + 表记录
#   invariant: 幂等（INSERT OR REPLACE）
# - id: A2
#   name_zh: ② 超期维度查询
#   name_en: query_stale_dimensions / query_all_dimensions
#   intro: 查 >90 天未更新且非 completed/deferred 的活跃维度；另供 AI 冷启动全量查询
#   desc: cutoff=str(now_utc - 90d)（str 而非 isoformat 防 'T' 字符比较误判）→ SELECT WHERE status NOT IN completed/deferred AND last_updated < cutoff；fail-open 返回空列表
#   inputs: I2
#   outputs: stale 维度列表 / 全量维度列表
# - id: A3
#   name_zh: ③ 新鲜度对账硬阻断
#   name_en: make_remediation_progress_reconciler
#   intro: commit 后始终触发，有超期维度即 block_next 硬阻断下次 commit
#   desc: trigger 恒 True（全局元检查）→ query_stale_dimensions → 无 stale=clean，有 stale=block_next（摘要前 5 条，提示 record_remediation_progress 或 resolve_blocks 修复）
#   inputs: A2
#   outputs: ReconcileResult
#   invariant: stale>0 → block_next
# 层: 输出
# - id: O1
#   name_zh: 新鲜度对账结果
#   name_en: ReconcileResult
#   intro: clean=全部维度新鲜；block_next=下次 commit 硬阻断强制更新进度
#   invariant: block_next 需 resolve_blocks 清除
#   downstream: GitCommitGateway（[CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway）
# - id: O2
#   name_zh: 治本进度持久化与全量查询
#   name_en: remediation_progress / query_all_dimensions
#   intro: 进度落 governance.db 供 M16 指标与 AI 冷启动零幻觉查询
#   downstream: architecture_health_dashboard M16 指标 + AI 冷启动查询
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I2 --> A2
# A2 --> A3
# A3 --> O1
# A1 --> O2
# A2 --> O2
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from zephyr.governance.audit.reconciliation_registry import (
    ReconcileResult,
    ReconcilerSpec,
)
from zephyr.shared.utils.time_utils import now_utc

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# 参数对象（NO-LONG-PARAM-LIST gate 合规，§5.150）
# ---------------------------------------------------------------------------


@dataclass
class RemediationProgressRecord:
    """record_remediation_progress 的参数对象（>7 参数 → dataclass 封装）。

    Attributes:
        dimension_id: 维度唯一标识（如 "ARCH-DEPGRAPH-RECONCILER-FAILSILENT"）。
        dimension_kind: "issue" | "root_cause" | "phase"。
        title: 人类可读标题。
        status: not_started|in_progress|completed|blocked|deferred。
        session_id: 记录本条更新的 session_id（可空）。
        commit_sha: 关联 commit SHA（可空）。
        target_completion_date: 目标完成日 ISO date（可空）。
        blocker_reason: status='blocked' 时的阻塞原因（可空）。
        details: 自由字段 dict，序列化为 JSON 存储（可空）。
    """

    dimension_id: str
    dimension_kind: str
    title: str
    status: str
    session_id: str = ""
    commit_sha: str = ""
    target_completion_date: str | None = None
    blocker_reason: str | None = None
    details: dict | None = None


# ---------------------------------------------------------------------------
# SQL 常量（§5.160.2 NO-BARE-SQL gate 合规）
# ---------------------------------------------------------------------------

SQL_CREATE_REMEDIATION_PROGRESS = """CREATE TABLE IF NOT EXISTS remediation_progress (
    dimension_id TEXT PRIMARY KEY,
    dimension_kind TEXT NOT NULL CHECK(dimension_kind IN ('issue', 'root_cause', 'phase')),
    title TEXT NOT NULL,
    status TEXT NOT NULL CHECK(status IN (
        'not_started', 'in_progress', 'completed', 'blocked', 'deferred'
    )),
    last_updated TEXT NOT NULL,
    last_session_id TEXT,
    last_commit_sha TEXT,
    target_completion_date TEXT,
    blocker_reason TEXT,
    details_json TEXT
)"""

SQL_UPSERT_REMEDIATION = (
    "INSERT OR REPLACE INTO remediation_progress "
    "(dimension_id, dimension_kind, title, status, last_updated, "
    "last_session_id, last_commit_sha, target_completion_date, "
    "blocker_reason, details_json) "
    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
)

SQL_SELECT_STALE = (
    "SELECT dimension_id, dimension_kind, title, status, last_updated "
    "FROM remediation_progress "
    "WHERE status NOT IN ('completed', 'deferred') "
    "AND last_updated < ? "
    "ORDER BY last_updated ASC"
)

SQL_SELECT_ALL = (
    "SELECT dimension_id, dimension_kind, title, status, "
    "last_updated, last_session_id, last_commit_sha, "
    "target_completion_date, blocker_reason, details_json "
    "FROM remediation_progress "
    "ORDER BY last_updated DESC"
)

SQL_SELECT_BY_ID = (
    "SELECT dimension_id, dimension_kind, title, status, "
    "last_updated, last_session_id, last_commit_sha, "
    "target_completion_date, blocker_reason, details_json "
    "FROM remediation_progress "
    "WHERE dimension_id = ?"
)

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

_BLOCK_SECONDS = 90 * 24 * 60 * 60  # 90 天 → block_next
_GATE_ID = "GATE-REMEDIATION-PROGRESS"


def _get_db_path(project_root) -> str:
    """返回 governance.db 绝对路径。"""
    return os.path.join(str(project_root), "data", "databases", "governance.db")


# ---------------------------------------------------------------------------
# 公开 API：记录 / 查询治本进度
# ---------------------------------------------------------------------------


def record_remediation_progress(project_root, record: RemediationProgressRecord) -> bool:
    """记录或更新一条治本维度进度（幂等 INSERT OR REPLACE）。

    Args:
        project_root: 项目根 Path。
        record: RemediationProgressRecord 参数对象（含 dimension_id/kind/title/status 等）。

    Returns:
        True=成功，False=失败（DB 写入异常，已 logger.warning，不抛）。
    """
    if record.dimension_kind not in ("issue", "root_cause", "phase"):
        logger.warning("record_remediation_progress: invalid dimension_kind=%r", record.dimension_kind)
        return False
    if record.status not in ("not_started", "in_progress", "completed", "blocked", "deferred"):
        logger.warning("record_remediation_progress: invalid status=%r", record.status)
        return False

    details_json = json.dumps(record.details, ensure_ascii=False) if record.details else None
    try:
        db_path = _get_db_path(project_root)
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        conn = sqlite3.connect(db_path, timeout=30.0)
        try:
            conn.execute(SQL_CREATE_REMEDIATION_PROGRESS)
            conn.execute(
                SQL_UPSERT_REMEDIATION,
                (
                    record.dimension_id,
                    record.dimension_kind,
                    record.title,
                    record.status,
                    now_utc(),
                    record.session_id,
                    record.commit_sha,
                    record.target_completion_date,
                    record.blocker_reason,
                    details_json,
                ),
            )
            conn.commit()
        finally:
            conn.close()
        return True
    except Exception as e:  # noqa: BLE001 — 治标: broad exception catch 降级
        logger.warning("record_remediation_progress: DB write failed: %s", e)
        return False


def query_all_dimensions(project_root) -> list[dict]:
    """查询全部治本维度进度（按 last_updated 降序）。

    供 AI 冷启动查询"治本进行到哪了"——零幻觉空间。

    Returns:
        list[dict]: 每条含 dimension_id/kind/title/status/last_updated/...。
        空列表表示表不存在或无数据（fail-open）。
    """
    try:
        db_path = _get_db_path(project_root)
        if not os.path.isfile(db_path):
            return []
        conn = sqlite3.connect(db_path, timeout=10.0)
        try:
            try:
                rows = conn.execute(SQL_SELECT_ALL).fetchall()
            except sqlite3.OperationalError:
                return []  # 表不存在
        finally:
            conn.close()
        return [
            {
                "dimension_id": r[0],
                "dimension_kind": r[1],
                "title": r[2],
                "status": r[3],
                "last_updated": r[4],
                "last_session_id": r[5],
                "last_commit_sha": r[6],
                "target_completion_date": r[7],
                "blocker_reason": r[8],
                "details": json.loads(r[9]) if r[9] else None,
            }
            for r in rows
        ]
    except Exception as e:  # noqa: BLE001 — fail-open
        logger.warning("query_all_dimensions: DB read failed: %s", e)
        return []


def query_stale_dimensions(project_root, max_age_seconds: int = _BLOCK_SECONDS) -> list[dict]:
    """查询超期未更新的活跃维度（>max_age_seconds 且非 completed/deferred）。

    供 reconciler + M16 指标共用。

    Args:
        project_root: 项目根 Path。
        max_age_seconds: 超期阈值秒数，默认 90 天。

    Returns:
        list[dict]: 每条含 dimension_id/kind/title/status/last_updated。
        空列表表示无超期维度或查询失败（fail-open）。
    """
    try:
        db_path = _get_db_path(project_root)
        if not os.path.isfile(db_path):
            return []
        # 治本: 用 str() 而非 isoformat()——last_updated 经 now_utc()->SQLite str() 存储为空格分隔
        # ('2026-07-22 18:26:51+00:00')，isoformat() 用 'T' 分隔，字符串比较时
        # 'T'(ord=84) > ' '(ord=32) 导致 last_updated < cutoff 同日误判（false-positive stale）
        cutoff = str(datetime.now(timezone.utc) - timedelta(seconds=max_age_seconds))
        conn = sqlite3.connect(db_path, timeout=10.0)
        try:
            try:
                rows = conn.execute(SQL_SELECT_STALE, (cutoff,)).fetchall()
            except sqlite3.OperationalError:
                return []  # 表不存在
        finally:
            conn.close()
        return [
            {
                "dimension_id": r[0],
                "dimension_kind": r[1],
                "title": r[2],
                "status": r[3],
                "last_updated": r[4],
            }
            for r in rows
        ]
    except Exception as e:  # noqa: BLE001 — fail-open
        logger.warning("query_stale_dimensions: DB read failed: %s", e)
        return []


# ---------------------------------------------------------------------------
# Reconciler 工厂
# ---------------------------------------------------------------------------


def make_remediation_progress_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 GATE-REMEDIATION-PROGRESS post-commit 治本进度新鲜度对账 reconciler。

    >90 天未更新且非 completed/deferred 的维度 → block_next（下次 commit 硬阻断）。

    trigger: 始终触发（治本进度是全局元数据，不依赖特定文件变更）
    reconcile: 查询 stale 维度，有则 block_next，无则 clean
    priority: 900（元检查，在所有业务 reconciler 之后执行）

    Args:
        gateway: GitCommitGateway 实例（仅用其 project_root）。

    Returns:
        ReconcilerSpec(gate_id="GATE-REMEDIATION-PROGRESS", priority=900)。
    """

    project_root = gateway.project_root

    def _trigger(committed_files: list[str]) -> bool:
        # 始终触发——治本进度新鲜度是全局元检查
        return True

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        stale = query_stale_dimensions(project_root)
        if not stale:
            return ReconcileResult(
                action="clean",
                detail="all remediation dimensions fresh",
                gate_id=_GATE_ID,
            )
        # block_next：下次 commit 硬阻断，AI 必须更新进度后调 resolve_blocks()
        stale_summary = "; ".join(
            f"{d['dimension_id']} ({d['title']}) last_updated={d['last_updated']}" for d in stale[:5]
        )
        if len(stale) > 5:
            stale_summary += f"; ...(+{len(stale) - 5} more)"
        return ReconcileResult(
            action="block_next",
            detail=(
                f"治本进度超期未更新（>90天，{len(stale)} 个维度）: {stale_summary}. "
                f"修复: 调 record_remediation_progress() 更新进度，"
                f"或调 resolve_blocks() 清除阻断（需先确认进度真实状态）。"
            ),
            gate_id=_GATE_ID,
        )

    return ReconcilerSpec(
        gate_id=_GATE_ID,
        trigger=_trigger,
        reconcile=_reconcile,
        priority=900,
        file_ops=frozenset({"read", "write"}),
    )

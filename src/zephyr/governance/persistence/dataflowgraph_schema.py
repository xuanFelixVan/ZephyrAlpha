# [BLUEPRINT] SH-DB-001 | docs/03_modules/_cross_layer/database/blueprint.md | §dataflowgraph
# [MODULE] zephyr.governance.persistence.dataflowgraph_schema
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.depgraph_schema (_PG_ENV_PATH, _load_pg_config, _build_pg_dsn); zephyr.shared.io.paths (REPO_ROOT); psycopg2
# [CONSUMERS] apply_dataflowgraph.py; sync_yaml_to_depgraph.py (sync_dataflow_registry); generate_dataflow_diagram.py
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] dataflowgraph is PostgreSQL (同库不同表，共享 config/.env.postgres); init_dataflow_db must be idempotent
# [MODIFY-GUARD] 03_create_dataflow_schema.sql; dataflowgraph generators
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] raises RuntimeError on schema mismatch; OperationalError on DDL errors
# [TESTS] tests/test_dataflowgraph_schema.py
# [TTL] permanent
# [ARCH-REF] #ARCH-051

"""
dataflowgraph Schema DDL + 连接入口
========================================
依据：ARCH-051 裁定（2026-07-06）——建设 dataflowgraph（数据流图）作为与 depgraph 正交的第三维度全景图。

物理路径：PostgreSQL depgraph 数据库（与 depgraph 25张表同库不同表）
  - 表名前缀 dataflow_*（dataflow_datasets / dataflow_jobs / dataflow_runs /
    dataflow_edges / dataflow_datasets_metadata / dataflow_jobs_metadata）
  - 共享连接配置：config/.env.postgres（与 depgraph 共享，真源在 depgraph_schema._PG_ENV_PATH）
  - 写入互斥锁 key: 424243（pg_advisory_lock，depgraph 用 424242，避免互锁）
Safety  : M（DDL 定义，init_dataflow_db 幂等执行）

物理位置（ARCH-031 合规）
------------------------
  本模块位于 src/zephyr/governance/persistence/ 子目录（与 decisiongraph_schema.py 同级），
  避免在 governance/ 根新增 .py 文件（ARCH-031 仅豁免 8 个核心模块）。

表结构
------
 1. dataflow_datasets           — Dataset 节点（数据集，如 market_data.tick）
 2. dataflow_jobs               — Job 节点（数据变换作业，如 compute_value_factor）
 3. dataflow_runs               — Run 实例（Job 运行实例，Phase 2 运行时产出）
 4. dataflow_edges              — 数据流边（edge_type: push/pull/sync/async/event_driven）
 5. dataflow_datasets_metadata  — Dataset 人工 curated 字段保护（字段角色分离）
 6. dataflow_jobs_metadata      — Job 人工 curated 字段保护（字段角色分离）

双态模式（对齐 depgraph）
-------------------------
  - design_maturity: design(设计态) / production(运营态) / prototype(原型)
  - build_status: planned / generated / testing / stable / deprecated
    （注意：本词表与 module_lifecycle_status 8值词表不同，仅 5 值，与 depgraph nodes.build_status 一致）

字段角色分离（对齐 depgraph 裁定#209 Stage 2）
----------------------------------------------
  dataflow_datasets_metadata / dataflow_jobs_metadata 表保护人工 curated 字段：
  - entity_name / job_name 为稳定 PK（dataset_id/job_id 是 IDENTITY，DELETE+INSERT 后变化）
  - 在 sync_dataflow_registry() 中 UPSERT（DELETE 前）保存当前值，
    INSERT 后 UPDATE 从 metadata 恢复空字段

P2 迁移后 schema 真源
-----------------------------------
  PG schema 真源：scripts/governance/migrate_sqlite_to_pg/03_create_dataflow_schema.sql
  init_dataflow_db() 仅验证核心表存在，不执行 DDL/migration。

  _DDL_DATAFLOW_* 常量：列名对比真源（verify_schema_health.py 引用做 drift 校验），
  类型定义与 03_create_dataflow_schema.sql 真源对齐。

用法
----
    from zephyr.governance.persistence.dataflowgraph_schema import init_dataflow_db, get_dataflowgraph_pg_connection

    init_dataflow_db()              # 幂等，验证 PG dataflow schema 健康性
    conn = get_dataflowgraph_pg_connection()   # 返回 PostgreSQL 连接（与 depgraph 同库不同表）

PG 配置真源
-----------------------------------
  PG 连接配置真源：config/.env.postgres（depgraph_schema._PG_ENV_PATH）
  本模块复用 depgraph_schema._load_pg_config() / _build_pg_dsn()，避免配置真源分裂。
  连接入口独立：get_dataflowgraph_pg_connection()（与 depgraph 共享配置，但入口独立）。
"""

from __future__ import annotations

from typing import Any

import psycopg2

# 复用 depgraph_schema 的 PG 配置（真源唯一，避免配置分裂）
from zephyr.governance.depgraph_schema import (
    _PG_ENV_PATH,  # noqa: F401（导出供 consumer 复用）
    _build_pg_dsn,
    _load_pg_config,  # noqa: F401（导出供 consumer 复用）
)


# ---------------------------------------------------------------------------
# DDL — dataflow_datasets 表（Dataset 节点）
# 类型与 03_create_dataflow_schema.sql 真源对齐
# ---------------------------------------------------------------------------

_DDL_DATAFLOW_DATASETS = """
CREATE TABLE IF NOT EXISTS dataflow_datasets (
    dataset_id       BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    entity_name      TEXT NOT NULL UNIQUE,
    entity_type      TEXT NOT NULL DEFAULT 'dataset',
    scope            TEXT NOT NULL DEFAULT 'production'
        CHECK (scope IN ('production', 'backtest_internal')),
    contract_ref     TEXT,
    physical_type    TEXT,
    produced_by_job  TEXT,
    domain_id        TEXT,
    design_maturity  TEXT DEFAULT 'production'
        CHECK (design_maturity IN ('design', 'production', 'prototype')),
    build_status     TEXT DEFAULT 'generated'
        CHECK (build_status IN ('planned', 'generated', 'testing', 'stable', 'deprecated')),
    pit_policy       TEXT DEFAULT 'strict'
        CHECK (pit_policy IN ('strict', 'loose', 'none')),
    format_summary   TEXT,
    valid_since      TEXT,
    module_id        TEXT,
    last_updated     TEXT
)
"""

# ---------------------------------------------------------------------------
# DDL — dataflow_jobs 表（Job 节点）
# ---------------------------------------------------------------------------

_DDL_DATAFLOW_JOBS = """
CREATE TABLE IF NOT EXISTS dataflow_jobs (
    job_id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    job_name         TEXT NOT NULL UNIQUE,
    entity_type      TEXT NOT NULL DEFAULT 'job',
    scope            TEXT NOT NULL DEFAULT 'production'
        CHECK (scope IN ('production', 'backtest_internal')),
    source_code_ref  TEXT,
    trigger_type     TEXT
        CHECK (trigger_type IS NULL OR trigger_type IN ('event_driven', 'scheduled', 'manual', 'stream')),
    run_context      TEXT,
    pit_relevance    TEXT DEFAULT 'strict'
        CHECK (pit_relevance IN ('strict', 'loose', 'none')),
    description      TEXT,
    design_maturity  TEXT DEFAULT 'production'
        CHECK (design_maturity IN ('design', 'production', 'prototype')),
    build_status     TEXT DEFAULT 'generated'
        CHECK (build_status IN ('planned', 'generated', 'testing', 'stable', 'deprecated')),
    module_id        TEXT,
    domain_id        TEXT,
    last_updated     TEXT
)
"""

# ---------------------------------------------------------------------------
# DDL — dataflow_runs 表（Run 实例）
# ---------------------------------------------------------------------------

_DDL_DATAFLOW_RUNS = """
CREATE TABLE IF NOT EXISTS dataflow_runs (
    run_id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    job_id           BIGINT NOT NULL,
    run_type         TEXT NOT NULL
        CHECK (run_type IN ('daily_backtest', 'minute_backtest', 'tick_backtest', 'production_run')),
    run_status       TEXT DEFAULT 'pending'
        CHECK (run_status IN ('pending', 'running', 'completed', 'failed', 'aborted')),
    started_at       TIMESTAMP,
    finished_at      TIMESTAMP,
    parameters       TEXT,
    result_summary   TEXT,
    last_updated     TEXT,
    FOREIGN KEY (job_id) REFERENCES dataflow_jobs(job_id) ON DELETE CASCADE
)
"""

# ---------------------------------------------------------------------------
# DDL — dataflow_edges 表（数据流边）
# ---------------------------------------------------------------------------

_DDL_DATAFLOW_EDGES = """
CREATE TABLE IF NOT EXISTS dataflow_edges (
    edge_id           BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    from_entity_id    BIGINT NOT NULL,
    to_entity_id      BIGINT NOT NULL,
    from_entity_type  TEXT NOT NULL
        CHECK (from_entity_type IN ('dataset', 'job')),
    to_entity_type    TEXT NOT NULL
        CHECK (to_entity_type IN ('dataset', 'job')),
    edge_type         TEXT NOT NULL
        CHECK (edge_type IN ('push', 'pull', 'sync', 'async', 'event_driven')),
    design_maturity   TEXT DEFAULT 'production'
        CHECK (design_maturity IN ('design', 'production', 'prototype')),
    last_updated      TEXT
)
"""

# ---------------------------------------------------------------------------
# DDL — dataflow_datasets_metadata 表（字段角色分离，对齐裁定#209 Stage 2）
# ---------------------------------------------------------------------------

_DDL_DATAFLOW_DATASETS_METADATA = """
CREATE TABLE IF NOT EXISTS dataflow_datasets_metadata (
    entity_name      TEXT PRIMARY KEY,
    contract_ref     TEXT,
    physical_type    TEXT,
    domain_id        TEXT,
    pit_policy       TEXT,
    format_summary   TEXT,
    valid_since      TEXT,
    last_updated     TEXT
)
"""

# ---------------------------------------------------------------------------
# DDL — dataflow_jobs_metadata 表（字段角色分离，对齐裁定#209 Stage 2）
# ---------------------------------------------------------------------------

_DDL_DATAFLOW_JOBS_METADATA = """
CREATE TABLE IF NOT EXISTS dataflow_jobs_metadata (
    job_name         TEXT PRIMARY KEY,
    source_code_ref  TEXT,
    trigger_type     TEXT,
    run_context      TEXT,
    pit_relevance    TEXT,
    description      TEXT,
    last_updated     TEXT
)
"""

# 全部 DDL 常量（供 init_dataflow_db / apply_dataflowgraph 引用）
_DDL_DATAFLOW_ALL: tuple[str, ...] = (
    _DDL_DATAFLOW_DATASETS,
    _DDL_DATAFLOW_JOBS,
    _DDL_DATAFLOW_RUNS,
    _DDL_DATAFLOW_EDGES,
    _DDL_DATAFLOW_DATASETS_METADATA,
    _DDL_DATAFLOW_JOBS_METADATA,
)

# 核心表清单（init_dataflow_db 验证用）
_DATAFLOW_CORE_TABLES: tuple[str, ...] = (
    "dataflow_datasets",
    "dataflow_jobs",
    "dataflow_runs",
    "dataflow_edges",
    "dataflow_datasets_metadata",
    "dataflow_jobs_metadata",
)

# 写入互斥锁 key（pg_advisory_lock，与 depgraph 的 424242 区分，避免互锁）
_DATAFLOW_ADVISORY_LOCK_KEY: int = 424243


def get_dataflowgraph_pg_connection(
    *,
    superuser: bool = False,
    read_only: bool = True,  # ARCH-058: 对齐 depgraph/decisiongraph 角色分级，默认只读
    autocommit: bool = True,
    replica: bool = False,
    allow_design_delete: bool = False,
) -> Any:
    """返回 dataflowgraph (PostgreSQL) 连接。

    与 depgraph 同库不同表（共享 config/.env.postgres 配置）。
    所有 dataflowgraph 连接必须经此入口（统一 PG 配置，防止散点连接绕过连接池配置）。

    裁定#ARCH-DEPGRAPH_ACCESS_CONTROL: 角色分级访问控制（对齐 depgraph/decisiongraph）
    - 默认 read_only=True 使用 depgraph_reader 只读角色（技术阻断写入）
    - 仅白名单脚本可传 read_only=False 使用 depgraph_writer 读写角色（如需 DELETE）

    :param superuser: True 使用 postgres 超级用户（用于数据迁移 / SET session_replication_role）
        （优先级最高，覆盖 read_only）
    :param read_only: True（默认）使用 depgraph_reader 只读角色；
        False 使用 depgraph_writer 读写角色（仅白名单脚本可用）
    :param autocommit: True 启用自动提交（默认）；False 需显式 conn.commit()
    :param replica: True 设置 session_replication_role='replica' 禁用所有触发器和 FK
        （仅超级用户可用；用于批量数据导入/迁移场景；自动设置 superuser=True）
    :param allow_design_delete: True 启用 SET app.allow_design_maturity_delete = on
        （逃生通道，绕过 protect_dataflow_design_maturity 触发器；仅 apply_dataflowgraph.py
        设计态写入命令启用；ARCH-053）

    注意：本函数复用 depgraph_schema._build_pg_dsn()（配置真源唯一），
    但返回独立的连接对象（dataflowgraph 操作不影响 depgraph 事务）。
    """
    if replica:
        superuser = True  # session_replication_role 需要超级用户

    conn = psycopg2.connect(**_build_pg_dsn(superuser=superuser, read_only=read_only))
    conn.autocommit = autocommit

    if replica:
        with conn.cursor() as cur:
            cur.execute("SET session_replication_role = 'replica';")
        if not autocommit:
            conn.commit()

    if allow_design_delete:
        with conn.cursor() as cur:
            cur.execute("SET app.allow_design_maturity_delete = on")
        if not autocommit:
            conn.commit()

    return conn


def init_dataflow_db(*, echo: bool = False) -> None:
    """验证 dataflowgraph (PostgreSQL) schema 健康性（幂等）。

    PG schema 由 scripts/governance/migrate_sqlite_to_pg/03_create_dataflow_schema.sql 创建。
    本函数不执行 DDL/migration，仅验证核心表存在。

    若核心表不存在，请运行:
        psql -U postgres -d depgraph -f scripts/governance/migrate_sqlite_to_pg/03_create_dataflow_schema.sql

    :return: None
    :raises RuntimeError: 若核心表不存在
    """
    conn = get_dataflowgraph_pg_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_name = ANY(%s)
            """, (list(_DATAFLOW_CORE_TABLES),))
            existing = {row[0] for row in cur.fetchall()}
            missing = set(_DATAFLOW_CORE_TABLES) - existing
            if missing:
                raise RuntimeError(
                    "dataflowgraph (PostgreSQL) schema 未创建或缺失核心表。"
                    f"缺失表: {sorted(missing)}\n"
                    "请运行:\n"
                    "    psql -U postgres -d depgraph -f "
                    "scripts/governance/migrate_sqlite_to_pg/03_create_dataflow_schema.sql"
                )
    finally:
        conn.close()


def acquire_dataflow_write_lock(conn: Any) -> None:
    """获取 dataflowgraph 写入互斥锁（pg_advisory_lock）。

    与 depgraph 的 424242 锁互不干扰（key=424243）。
    用于 sync_dataflow_registry / apply_dataflowgraph 写入场景，防止并发写入冲突。

    锁在事务结束（commit/rollback）或连接关闭时自动释放。
    """
    with conn.cursor() as cur:
        cur.execute("SELECT pg_advisory_lock(%s)", (_DATAFLOW_ADVISORY_LOCK_KEY,))
    if not conn.autocommit:
        conn.commit()


def release_dataflow_write_lock(conn: Any) -> None:
    """释放 dataflowgraph 写入互斥锁。"""
    with conn.cursor() as cur:
        cur.execute("SELECT pg_advisory_unlock(%s)", (_DATAFLOW_ADVISORY_LOCK_KEY,))
    if not conn.autocommit:
        conn.commit()


def dataflow_table_names() -> list[str]:
    """返回 dataflowgraph 的 6 张表名（不含 depgraph 的 25 张表）。"""
    return list(_DATAFLOW_CORE_TABLES)


# 连接配置路径（导出供 consumer 复用，真源在 depgraph_schema._PG_ENV_PATH）
__all__ = [
    "init_dataflow_db",
    "get_dataflowgraph_pg_connection",
    "acquire_dataflow_write_lock",
    "release_dataflow_write_lock",
    "dataflow_table_names",
    "_PG_ENV_PATH",
    "_load_pg_config",
    "_build_pg_dsn",
    "_DDL_DATAFLOW_ALL",
    "_DATAFLOW_CORE_TABLES",
    "_DATAFLOW_ADVISORY_LOCK_KEY",
]

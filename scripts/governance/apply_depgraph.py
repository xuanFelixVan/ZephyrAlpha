# [BLUEPRINT] MOD-GOV_SCRIPTS
# [MODULE] scripts.governance.apply_depgraph
# [DOMAIN] D_GOV_SCRIPTS
# [DEPENDENCIES] scripts.governance.__init__
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS]
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-GOV_SCRIPTS | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
[BLUEPRINT] | scripts/governance/apply_depgraph.py | §1
[MODULE] scripts.governance.apply_depgraph
[INVARIANTS] 原子写入（RULE-ONE）；变更前验证；禁止直接覆盖
[MODIFY-GUARD] project_rules.md(RULE-SIXTEEN); scripts/governance/extract_depgraph.py
[CONSUMERS] 所有需要修改depgraph的AI session
[STABILITY] stable
[SAFETY] H
[AI_AUTONOMY] ai_modifiable
[ERROR_CONTRACT] 文件不存在→exit 1; YAML解析失败→exit 2; 验证失败→exit 3; 写入失败→exit 4
[TESTS] 无

depgraph 变更写入工具（RULE-SIXTEEN 强制配套）

禁止 AI 直接 Write 157MB depgraph → OOM 崩溃。
替代方案：AI 生成变更 JSON → 本脚本验证后原子写入。

用法:
  python scripts/governance/apply_depgraph.py --update-module D-FACTOR-01 blueprint_status=has_blueprint
  python scripts/governance/apply_depgraph.py --batch changes.json
  python scripts/governance/apply_depgraph.py --batch changes.json --dry-run

  # F5 合规豁免：D_SECURITY 拆分后域/路径/依赖迁移命令
  python scripts/governance/apply_depgraph.py --insert-domain D-NEW "新域" 业务 L2_domain src/zephyr/new/ --max-modules 200
  python scripts/governance/apply_depgraph.py --update-domain-id D-FACTOR-01 D-NEW_DOMAIN --dry-run
  python scripts/governance/apply_depgraph.py --update-path D-FACTOR-01 src/zephyr/new_domain/module.py --dry-run
  python scripts/governance/apply_depgraph.py --migrate-dependencies D-OLD D-TARGET --new-from-domain D-NEW --dry-run

  # domain_mapping 表管理（schema 盲区修复）
  python scripts/governance/apply_depgraph.py --insert-domain-mapping scripts/new_tool/ D_GOVERNANCE non_src --mapped-by session-xxx
  python scripts/governance/apply_depgraph.py --insert-domain-mapping src/zephyr/new/ D-NEW unregistered_src D-NEW-SUB --dry-run

  # 裁定#204：D-SIGNAL* 4 域改名（D-SIGNAL 必须最后替换，避免 LIKE 误伤 D-SIGNAL_* 子域名）
  python scripts/governance/apply_depgraph.py --rename-domain D-SIGNAL_ASHARE D_ASHARE_SIGNAL --dry-run
  python scripts/governance/apply_depgraph.py --rename-domain D-SIGNAL D_SIGLEGACY  # 必须最后执行
  python scripts/governance/apply_depgraph.py --update-domain-name D_SIGLEGACY "信号遗留设计态"

GIT 备份门禁（P2 迁移后治本 2026-06-27）：
  PG 模式下 depgraph 已迁至 PostgreSQL，无文件路径概念。
  原 SQLite 文件备份门禁（_check_git_backup + _create_physical_backup）已删除——
  PG 用 MVCC 事务 rollback 提供原子性，无需文件备份。
  事务失败时 conn.rollback() 自动回滚（已实现）。

PG depgraph 备份（ARCH-041 §5.33.1 治本，2026-07-03）：
  写入命令（非 --dry-run）执行后自动调用 backup_pg_architecture()（事件触发），
  导出全景 19 张 DB 真源表为 JSON 到 tmp/pg_backups/，自动清理旧备份（保留 10 个）。
  备份失败不阻断主流程（main 已成功）。定义：backup_runtime_state.py。
"""

from __future__ import annotations

__manifest__ = """
args: []
description: depgraph 变更写入工具（RULE-SIXTEEN 强制配套）
dimensions:
- D1
priority: P2
timeout_seconds: 60
warn_only: false
"""


import argparse
import contextlib
import datetime
import json
import logging
import os
import re
import subprocess
import sys
import time
from pathlib import Path

logger = logging.getLogger(__name__)

import psycopg2

from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）
from zephyr.shared.io.yaml_utils import load_vocabulary_values  # 词表 SSoT 加载（trae_060 §2 治本，2026-07-13）

# 治本（2026-06-27）：删除 DEPGRAPH_PATH = .../depgraph.db 常量（路径污染源）。
# P2 迁移后 depgraph 已迁至 PostgreSQL，连接入口 get_depgraph_pg_connection()。
# 原 SQLite 文件备份门禁（_check_git_backup + _create_physical_backup）已删除——
# PG 用 MVCC 事务 rollback 提供原子性，无需文件备份。

# P2 PG 迁移：删除 lock_files 文件锁（PG 用 MVCC）；导入 PG 连接入口
_GOV_DIR = Path(__file__).resolve().parent
if str(_GOV_DIR) not in sys.path:
    sys.path.insert(0, str(_GOV_DIR))
# 治本 #ARCH-TOOL-HEALTH-V1（2026-07-19）：deb695006f 批量重构 sys.exit→EXIT_* 时
# 误删 get_depgraph_pg_connection import（替换整行而非追加），导致 56 处调用运行时 NameError。
# 修复：在 EXIT_* 同一 import 语句中显式恢复 get_depgraph_pg_connection。
from _shared.constants import (
    EXIT_ERROR,
    EXIT_FINDINGS,
    EXIT_PASS,
    get_depgraph_pg_connection,
)

# 引入 module_id 双轨正则真源（真源唯一：从 validate_module_id_naming.py 复用）
# 裁定#208 双轨制（R2 治本修订后）：layer-master 轨 + domain-functional 派生轨 + 跨域共享轨
# R2 治本修订（2026-07-05）：D-XXX-NNN 已废弃为 module_id 派生轨，重定义为 submodule_id 专用
#
# 导入容错（2026-07-20）：pytest 收集时 tests/governance/d3_metadata/__init__.py（空包）
# 会遮蔽 scripts/governance/d3_metadata/。优先用绝对导入避免遮蔽；
# 独立脚本运行时（_GOV_DIR 已注入 sys.path）回退到顶层导入。
try:
    from scripts.governance.d3_metadata.validate_module_id_naming import DOMAIN_ID_RE as _DOMAIN_ID_RE  # noqa: E402
    from scripts.governance.d3_metadata.validate_module_id_naming import (
        is_valid_domain_id as _validate_domain_id_format,  # noqa: E402
    )
    from scripts.governance.d3_metadata.validate_module_id_naming import (
        is_valid_module_id as _validate_bp_id_format,  # noqa: E402
    )
except ImportError:
    from d3_metadata.validate_module_id_naming import DOMAIN_ID_RE as _DOMAIN_ID_RE  # noqa: E402
    from d3_metadata.validate_module_id_naming import is_valid_domain_id as _validate_domain_id_format  # noqa: E402
    from d3_metadata.validate_module_id_naming import is_valid_module_id as _validate_bp_id_format  # noqa: E402

# 裁定#209 阶段1（2026-07-02）：_db_write_lock 从 no-op 升级为 pg_advisory_lock 互斥保护。
# 与 generate_project_depgraph.py.write_depgraph_to_db 共享 lock key 424242。
# 会话级 lock，finally 显式 pg_advisory_unlock 释放。
# threading.local 防嵌套死锁：同线程嵌套调用时直接 yield（外层已持有锁）。
import threading as _threading

_DEPGRAPH_WRITE_LOCK_KEY = 424242
_depgraph_lock_local = _threading.local()


# 5.160.2 SQL 常量集中化（Phase 7c-1：重复 SQL 提取，2026-07-09）
# 防复发：NO-BARE-SQL gate (priority=87) 检测新增裸 SQL 字面量
SQL_SELECT_DOMAIN_ID_BY_DOMAIN_ID = "SELECT domain_id FROM domains WHERE domain_id=%s"
SQL_CHECK_DOMAIN_EXISTS = "SELECT 1 FROM domains WHERE domain_id=%s"
SQL_DROP_READONLY_TRIGGER = "DROP TRIGGER IF EXISTS readonly_blueprint_links_update ON blueprint_links"
SQL_SELECT_NODE_MATURITY_BY_ID = "SELECT node_id, design_maturity FROM nodes WHERE node_id=%s"
SQL_SELECT_NODE_ID_BY_ID = "SELECT node_id FROM nodes WHERE node_id=%s"
SQL_SELECT_BLUEPRINT_ID_BY_NODE_ID = "SELECT blueprint_id FROM nodes WHERE node_id=%s"
SQL_COUNT_EDGES_BY_NODE = "SELECT COUNT(*) FROM edges WHERE from_node_id=%s OR to_node_id=%s"
SQL_DEPRECATE_NODE = "UPDATE nodes SET build_status='deprecated' WHERE node_id=%s"
SQL_DELETE_EDGE_BY_ID = "DELETE FROM edges WHERE edge_id=%s"
SQL_DELETE_DOMAIN_BY_ID = "DELETE FROM domains WHERE domain_id=%s"
SQL_UPDATE_NODE_PATH_BY_ID = "UPDATE nodes SET path=%s, file_path=%s WHERE node_id=%s"
# 动态标识符模板（列名/字段名 f-string 插值不可参数化，.format 注入；2026-08-20 波3 实证：
# 行内 f-string+noqa 组合超 120 列致 ruff format 重排拆行使标记漂移失效，升 SQL_* 模板治本）
SQL_UPDATE_NODE_SET_DYNAMIC = "UPDATE nodes SET {set_clause} WHERE node_id = %s"
SQL_UPDATE_DOMAIN_FIELD_DYNAMIC = "UPDATE domains SET {field}=%s, updated_at=%s WHERE domain_id=%s"
# 5.179 治本（2026-07-13）：add_design_node UPDATE 提取为常量，消除 NO-BARE-SQL gate 违规
SQL_UPDATE_DESIGN_NODE_BY_ID = "UPDATE nodes SET blueprint_id=%s, domain_id=%s, build_status=%s, blueprint_path=%s, granularity=%s, node_type=%s WHERE node_id=%s"
# #ARCH-70：add_design_node INSERT 提取为常量（NO-BARE-SQL §5.160.2 合规）；
# file 粒度 file_path 同写 path——NEW-FILE-DEPGRAPH 门禁查 file_path 列，
# 只写 path 会导致"设计态预登记"永远过不了门禁（2026-08-13 死锁实证）
SQL_INSERT_DESIGN_NODE = (
    "INSERT INTO nodes (node_type, path, file_path, granularity, domain_id, blueprint_id, "
    "build_status, design_maturity, blueprint_path, can_build) "
    "VALUES (%s, %s, %s, %s, %s, %s, %s, 'design', %s, 1) RETURNING node_id"
)

# Phase 7c-2: 重复 f-string SQL 提取为 .format() 模板（2026-07-09）
SQL_UPDATE_TBL_REPLACE_LIKE = "UPDATE {tbl} SET {col}=REPLACE({col}, %s, %s) WHERE {col} LIKE %s"
SQL_COUNT_TBL_BY_COL_LIKE = "SELECT COUNT(*) FROM {tbl} WHERE {col} LIKE %s"
SQL_COUNT_TBL_BY_COL_EQ = "SELECT COUNT(*) FROM {tbl} WHERE {col}=%s"
SQL_UPDATE_TBL_COL_EQ = "UPDATE {tbl} SET {col}=%s WHERE {col}=%s"

# cmd_delete_nodes: 动态 IN (...) 占位符模板（2026-07-15，SSoT §11.4 治本）
SQL_DELETE_NODES_SELECT_BY_IDS = "SELECT node_id, path, domain_id FROM nodes WHERE node_id IN ({0})"
SQL_DELETE_NODES_COUNT_IN_EDGES = "SELECT COUNT(*) AS cnt FROM edges WHERE to_node_id IN ({0})"
SQL_DELETE_NODES_DELETE_EDGES_BY_IDS = "DELETE FROM edges WHERE from_node_id IN ({0}) OR to_node_id IN ({0})"
SQL_DELETE_NODES_DELETE_BY_IDS = "DELETE FROM nodes WHERE node_id IN ({0})"

# fix_path_semantics_for_design_nodes: 5.179 治本 SQL 常量（NO-BARE-SQL gate 合规）
SQL_FIX_PATH_CASE1_SELECT_DESIGN_PYSLASH = (
    "SELECT node_id, path, granularity, node_type FROM nodes "
    "WHERE design_maturity = 'design' AND (path LIKE '%%.py/' OR path LIKE '%%.py//') "
    "ORDER BY node_id"
)
SQL_FIX_PATH_CASE1A_SELECT_NONDESIGN_BY_PATH = (
    "SELECT node_id, design_maturity FROM nodes WHERE path=%s AND design_maturity != 'design'"
)
SQL_FIX_PATH_DELETE_EDGES_BY_NODE = "DELETE FROM edges WHERE from_node_id=%s OR to_node_id=%s"
SQL_FIX_PATH_DELETE_NODE_BY_ID = "DELETE FROM nodes WHERE node_id=%s"
SQL_FIX_PATH_CASE1B_UPDATE = "UPDATE nodes SET path=%s, granularity='file', node_type='module' WHERE node_id=%s"
SQL_FIX_PATH_CASE3_SELECT_DESIGN_NONDIR_SLASH = (
    "SELECT node_id, path, granularity, node_type FROM nodes "
    "WHERE design_maturity = 'design' AND granularity != 'directory' AND path LIKE '%%/' "
    "ORDER BY node_id"
)
SQL_FIX_PATH_CASE3_UPDATE = "UPDATE nodes SET granularity='directory', node_type='blueprint' WHERE node_id=%s"

# 5.160.2 SQL 常量集中化（Phase 7c-3：剩余裸SQL提取，2026-07-22）
# 防复发：NO-BARE-SQL gate (priority=94) 检测新增裸 SQL 字面量
# 以下常量覆盖 apply_depgraph.py 中所有剩余的 execute() 调用中的 SQL 字面量。

# --- pg_advisory_lock / dump ---
SQL_PG_ADVISORY_LOCK = "SELECT pg_advisory_lock(424242)"
SQL_PG_ADVISORY_UNLOCK = "SELECT pg_advisory_unlock(424242)"
SQL_SELECT_ALL_NODES = "SELECT * FROM nodes"
SQL_SELECT_ALL_EDGES = "SELECT * FROM edges"
SQL_SELECT_ALL_DOMAINS = "SELECT * FROM domains"

# --- add_design_node / add_file_node ---
SQL_SELECT_NODE_BY_PATH_DESIGN = "SELECT node_id FROM nodes WHERE path=%s AND design_maturity='design'"
SQL_SELECT_NODE_BY_PATH_PRODUCTION = "SELECT node_id FROM nodes WHERE path=%s AND design_maturity='production'"
SQL_INSERT_FILE_NODE = (
    "INSERT INTO nodes (node_type, path, granularity, domain_id, blueprint_id, "
    "build_status, design_maturity, blueprint_path, can_build, subdomain_id) "
    "VALUES (%s, %s, 'file', %s, %s, 'generated', 'production', %s, 0, %s) "
    "RETURNING node_id"
)

# --- add_edge (design + production) ---
# 治本(#ARCH-CROSS-DOMAIN-TRIGGER-001, 2026-07-25): cross_domain 列由 DB 触发器
# trg_edges_cross_domain_bi 自动维护（按 from/to 节点 domain_id 计算），INSERT 不再
# 显式写入。原硬编码 cross_domain=0 导致跨域边被误标（Step 0 的 6 条边即受影响）。
# verified=0 保留为字面量（未经核验）；dep_maturity 设计态='design'/生产态=参数。
SQL_INSERT_DESIGN_EDGE = (
    "INSERT INTO edges (from_node_id, to_node_id, dep_type, architecture_direction, "
    "coupling_strength, used_symbol, invocation_method, api_contract_refs, "
    "event_ref, ddd_integration_pattern, failure_mode, fallback, "
    "activation_condition, data_transfer_description, resource_impact, "
    "relationship_type, verified, dep_maturity) "
    "VALUES (%s, %s, %s, 'downstream', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, 'design') "
    "RETURNING edge_id"
)
SQL_INSERT_PRODUCTION_EDGE = (
    "INSERT INTO edges (from_node_id, to_node_id, dep_type, architecture_direction, "
    "coupling_strength, used_symbol, invocation_method, api_contract_refs, "
    "event_ref, ddd_integration_pattern, failure_mode, fallback, "
    "activation_condition, data_transfer_description, resource_impact, "
    "relationship_type, verified, dep_maturity) "
    "VALUES (%s, %s, %s, 'downstream', %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, %s) "
    "RETURNING edge_id"
)
SQL_SELECT_TO_NODES_BY_FROM = "SELECT to_node_id FROM edges WHERE from_node_id=%s"
SQL_SELECT_DUP_EDGE = "SELECT edge_id FROM edges WHERE from_node_id=%s AND to_node_id=%s AND dep_type=%s"

# --- transition_build_status / transition_design_maturity ---
SQL_SELECT_BUILD_STATUS_BY_NODE = "SELECT build_status FROM nodes WHERE node_id=%s"
SQL_UPDATE_BUILD_STATUS = "UPDATE nodes SET build_status=%s WHERE node_id=%s"
SQL_SELECT_DESIGN_MATURITY_BY_NODE = "SELECT design_maturity, path FROM nodes WHERE node_id=%s"
SQL_UPDATE_DESIGN_MATURITY = "UPDATE nodes SET design_maturity=%s WHERE node_id=%s"

# --- tag_nodes（横切标签，03号文分支C裁定执行工具，#ARCH-169） ---
SQL_SELECT_TAGS_BY_NODE = "SELECT tags FROM nodes WHERE node_id=%s"
SQL_UPDATE_TAGS_BY_NODE = "UPDATE nodes SET tags=%s WHERE node_id=%s"

# --- remove_design_node ---
SQL_SELECT_NODE_DETAIL_BY_ID = (
    "SELECT node_id, path, blueprint_id, design_maturity, build_status FROM nodes WHERE node_id=%s"
)

# S5 锚点级联提示（2026-08-14，AI-GIT-001）：删除/弃用节点时查 battle_map_anchors 引用
SQL_CASCADE_ANCHOR_NODE_LOOKUP = "SELECT node_id, path, blueprint_id FROM nodes WHERE node_id = ANY(%s)"
SQL_CASCADE_ANCHOR_HINT_QUERY = (
    "SELECT anchor_id, step_id, target_id, target_role FROM battle_map_anchors "
    "WHERE target_graph = 'depgraph' AND target_id = ANY(%s) ORDER BY anchor_id"
)
SQL_COUNT_NODES_BY_PATH_EXCLUDE_ID = "SELECT COUNT(*) FROM nodes WHERE path=%s AND node_id!=%s"
SQL_DELETE_EDGES_BY_NODE = "DELETE FROM edges WHERE from_node_id=%s OR to_node_id=%s"

# --- deprecate_node ---
SQL_SELECT_NODE_FULL_DETAIL_BY_ID = (
    "SELECT node_id, path, file_path, blueprint_id, design_maturity, build_status FROM nodes WHERE node_id=%s"
)

# --- mark_blueprint_invalid ---
SQL_SELECT_NODES_BY_BLUEPRINT = "SELECT node_id, path FROM nodes WHERE blueprint_id=%s"
SQL_UPDATE_BLUEPRINT_INVALID = "UPDATE nodes SET blueprint_id_invalid=1, gate_reason=%s WHERE node_id=%s"

# --- delete_design_edge / delete_edge ---
SQL_SELECT_EDGE_DESIGN_MATURITY = "SELECT edge_id, from_node_id, to_node_id, dep_maturity FROM edges WHERE edge_id=%s"
SQL_SELECT_EDGE_FULL_DETAIL = (
    "SELECT edge_id, from_node_id, to_node_id, dep_type, dep_maturity FROM edges WHERE edge_id=%s"
)

# --- delete_blueprint_link / delete_constraint ---
SQL_SELECT_BLUEPRINT_LINK = "SELECT blueprint_id FROM blueprint_links WHERE blueprint_id=%s"
SQL_DELETE_BLUEPRINT_LINK = "DELETE FROM blueprint_links WHERE blueprint_id=%s"
SQL_SELECT_CONSTRAINT_BY_ID = "SELECT constraint_id, name, constraint_type FROM arch_constraints WHERE constraint_id=%s"
SQL_DELETE_CONSTRAINT = "DELETE FROM arch_constraints WHERE constraint_id=%s"

# --- cleanup_ghost_nodes ---
SQL_SELECT_NON_DESIGN_NODES_WITH_PATH = (
    "SELECT node_id, path FROM nodes WHERE path IS NOT NULL AND path != '' "
    "AND (design_maturity != 'design' OR design_maturity IS NULL)"
)
SQL_DELETE_NODE_BY_ID = "DELETE FROM nodes WHERE node_id = %s"

# --- cleanup_orphan_edges ---
SQL_COUNT_ORPHAN_EDGES = (
    "SELECT COUNT(*) FROM edges "
    "WHERE from_node_id NOT IN (SELECT node_id FROM nodes) "
    "OR to_node_id NOT IN (SELECT node_id FROM nodes)"
)
SQL_SELECT_ORPHAN_EDGE_SAMPLES = (
    "SELECT edge_id, from_node_id, to_node_id, dep_type FROM edges "
    "WHERE from_node_id NOT IN (SELECT node_id FROM nodes) "
    "OR to_node_id NOT IN (SELECT node_id FROM nodes) LIMIT 10"
)
SQL_DELETE_ORPHAN_EDGES = (
    "DELETE FROM edges "
    "WHERE from_node_id NOT IN (SELECT node_id FROM nodes) "
    "OR to_node_id NOT IN (SELECT node_id FROM nodes)"
)

# --- update_edge_type ---
SQL_SELECT_EDGE_TYPE_DETAIL = "SELECT edge_id, from_node_id, to_node_id, dep_type FROM edges WHERE edge_id=%s"
SQL_UPDATE_EDGE_DEP_TYPE = "UPDATE edges SET dep_type=%s WHERE edge_id=%s"

# --- domain naming rules validation ---
SQL_SELECT_DOMAIN_NAMING_RULES = (
    "SELECT rule_id, severity FROM domain_naming_rules WHERE applies_to IN ('create', 'both')"
)
SQL_SELECT_ALL_DOMAIN_IDS = "SELECT domain_id FROM domains"

# --- cmd_insert_domain ---
SQL_INSERT_DOMAIN = (
    "INSERT INTO domains (domain_id, domain_name, domain_group, description, ssot_path, "
    "current_modules, max_modules, lifecycle, created_at, updated_at, build_status, layer_id) "
    "VALUES (%s, %s, %s, %s, %s, 0, %s, 'design_only', %s, %s, 'planned', %s)"
)

# --- cmd_migrate_module_domain ---
SQL_SELECT_NODES_BY_MODULE = "SELECT node_id, path, domain_id FROM nodes WHERE belongs_to=%s OR blueprint_id=%s"
SQL_UPDATE_NODE_DOMAIN_BY_MODULE = "UPDATE nodes SET domain_id=%s WHERE belongs_to=%s OR blueprint_id=%s"

# --- _scan_text_columns / _propagate_rename_fallback ---
SQL_SELECT_ALL_TABLES = (
    "SELECT table_name AS name FROM information_schema.tables "
    "WHERE table_schema = 'public' AND table_type = 'BASE TABLE'"
)
SQL_SELECT_TABLE_COLUMNS = (
    "SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = 'public' AND table_name = %s"
)
SQL_COUNT_TBL_LIKE_CNT_ESCAPE = "SELECT COUNT(*) AS cnt FROM {tbl} WHERE {col} LIKE %s ESCAPE '\\'"
SQL_UPDATE_TBL_REPLACE_LIKE_ESCAPE = "UPDATE {tbl} SET {col}=REPLACE({col}, %s, %s) WHERE {col} LIKE %s ESCAPE '\\'"
SQL_COUNT_TBL_LIKE_CNT = "SELECT COUNT(*) AS cnt FROM {tbl} WHERE {col} LIKE %s"
SQL_DELETE_TBL_COL_EQ_OR_EMPTY = "DELETE FROM {tbl} WHERE {col}=%s OR {col}=''"
SQL_COUNT_TBL_COL_EQ_CNT = "SELECT COUNT(*) AS cnt FROM {tbl} WHERE {col}=%s"
SQL_DELETE_TBL_COL_EQ = "DELETE FROM {tbl} WHERE {col}=%s"

# --- cmd_delete_domain ---
SQL_COUNT_NODES_BY_DOMAIN = "SELECT COUNT(*) AS cnt FROM nodes WHERE domain_id=%s"
SQL_COUNT_RULE_BINDINGS_BY_DOMAIN = "SELECT COUNT(*) AS cnt FROM rule_bindings WHERE domain_id=%s"
SQL_NULL_RULE_BINDINGS_DOMAIN = "UPDATE rule_bindings SET domain_id=NULL WHERE domain_id=%s"

# --- cmd_merge_domain (domain_dependencies conflict precheck) ---
SQL_COUNT_DOMAIN_DEP_CONFLICTS_FROM = (
    "SELECT COUNT(*) AS cnt FROM domain_dependencies a "
    "JOIN domain_dependencies b ON a.to_domain = b.to_domain "
    "AND a.from_domain = %s AND b.from_domain = %s"
)
SQL_COUNT_DOMAIN_DEP_CONFLICTS_TO = (
    "SELECT COUNT(*) AS cnt FROM domain_dependencies a "
    "JOIN domain_dependencies b ON a.from_domain = b.from_domain "
    "AND a.to_domain = %s AND b.to_domain = %s"
)

# --- cmd_apply_domain_id_check ---
SQL_COUNT_CONSTRAINT_BY_NAME = "SELECT COUNT(*) AS cnt FROM pg_constraint WHERE conname = %s"
SQL_SELECT_INVALID_DOMAIN_IDS = "SELECT domain_id FROM domains WHERE NOT (domain_id ~ %s)"

# --- cmd_apply_build_status_default ---
SQL_SELECT_DOMAIN_BUILD_STATUS_DEFAULT = (
    "SELECT column_default FROM information_schema.columns "
    "WHERE table_name = 'domains' AND column_name = 'build_status'"
)
SQL_ALTER_DOMAIN_BUILD_STATUS_DEFAULT = "ALTER TABLE domains ALTER COLUMN build_status SET DEFAULT 'planned'"

# --- cmd_fix_domains_build_status_vocab（tracker #251 / #ARCH-143 续作，Owner 窗口 schema 变更） ---
SQL_SELECT_DOMAIN_BUILD_STATUS_CHECK = (
    "SELECT conname, pg_get_constraintdef(oid) AS def FROM pg_constraint "
    "WHERE conrelid = 'domains'::regclass AND contype = 'c'"
)
SQL_DROP_DOMAIN_BUILD_STATUS_CHECK = "ALTER TABLE domains DROP CONSTRAINT domains_build_status_check"
SQL_ADD_DOMAIN_BUILD_STATUS_CHECK = (
    "ALTER TABLE domains ADD CONSTRAINT domains_build_status_check "
    "CHECK (build_status IN ('planned', 'generated', 'testing', 'stable', 'deprecated', 'dormant'))"
)

# --- _restore_blueprint_links_readonly_trigger ---
SQL_CREATE_PREVENT_UPDATE_FUNCTION = (
    "CREATE OR REPLACE FUNCTION _prevent_blueprint_links_update() "
    "RETURNS TRIGGER AS $$ BEGIN "
    "RAISE EXCEPTION 'blueprint_links 表只读（唯一真源是 YAML），"
    "请修改 YAML 后运行 sync_yaml_to_depgraph.py'; "
    "END; $$ LANGUAGE plpgsql"
)
SQL_CREATE_READONLY_TRIGGER = (
    "CREATE TRIGGER readonly_blueprint_links_update "
    "BEFORE UPDATE ON blueprint_links "
    "FOR EACH ROW EXECUTE FUNCTION _prevent_blueprint_links_update()"
)

# --- propagate_blueprint_id ---
SQL_SELECT_DISTINCT_TBL_COL_LIKE = "SELECT DISTINCT {col} FROM {tbl} WHERE {col} LIKE %s"

# --- _propagate_bp_id_in_db ---
SQL_COUNT_NODES_BY_BLUEPRINT_ID = "SELECT COUNT(*) AS c FROM nodes WHERE blueprint_id=%s"
SQL_UPDATE_NODE_BLUEPRINT_ID = "UPDATE nodes SET blueprint_id=%s WHERE blueprint_id=%s"
SQL_COUNT_BLUEPRINT_LINKS_BY_ID = "SELECT COUNT(*) FROM blueprint_links WHERE blueprint_id=%s"
SQL_UPDATE_BLUEPRINT_LINK_ID = "UPDATE blueprint_links SET blueprint_id=%s WHERE blueprint_id=%s"
SQL_SELECT_NODES_BY_TSD_LIKE = "SELECT node_id, type_specific_data FROM nodes WHERE type_specific_data LIKE %s"
SQL_UPDATE_NODE_TSD = "UPDATE nodes SET type_specific_data=%s WHERE node_id=%s"
SQL_SELECT_NODES_BY_BP_PATH_LIKE = "SELECT node_id, blueprint_path FROM nodes WHERE blueprint_path LIKE %s"
SQL_UPDATE_NODE_BP_PATH = "UPDATE nodes SET blueprint_path=%s WHERE node_id=%s"

# --- cmd_propagate_node_paths ---
SQL_COUNT_NODES_BY_PATH = "SELECT COUNT(*) FROM nodes WHERE path=%s"
SQL_UPDATE_NODE_PATH_BY_PATH = "UPDATE nodes SET path=%s WHERE path=%s"
SQL_COUNT_NODES_BY_FILE_PATH = "SELECT COUNT(*) FROM nodes WHERE file_path=%s"
SQL_UPDATE_NODE_FILE_PATH = "UPDATE nodes SET file_path=%s WHERE file_path=%s"
SQL_COUNT_BLUEPRINT_LINKS_BY_BP_PATH = "SELECT COUNT(*) FROM blueprint_links WHERE blueprint_path=%s"
SQL_UPDATE_BLUEPRINT_LINK_BP_PATH = "UPDATE blueprint_links SET blueprint_path=%s WHERE blueprint_path=%s"

# --- cmd_rename_domain_name ---
SQL_SELECT_DOMAIN_NAME_BY_ID = "SELECT domain_name FROM domains WHERE domain_id=%s"
SQL_UPDATE_DOMAIN_NAME = "UPDATE domains SET domain_name=%s WHERE domain_id=%s"

# --- cmd_update_path ---
SQL_SELECT_NODE_PATH_BY_MODULE = "SELECT node_id, path FROM nodes WHERE belongs_to=%s OR blueprint_id=%s"

# --- cmd_migrate_dependencies ---
SQL_SELECT_DOMAIN_DEP_BY_PAIR = (
    "SELECT from_domain, to_domain, edge_count FROM domain_dependencies WHERE from_domain=%s AND to_domain=%s"
)
SQL_SELECT_DOMAIN_DEP_EDGE_COUNT = "SELECT edge_count FROM domain_dependencies WHERE from_domain=%s AND to_domain=%s"
SQL_DELETE_DOMAIN_DEP = "DELETE FROM domain_dependencies WHERE from_domain=%s AND to_domain=%s"
SQL_UPDATE_DOMAIN_DEP_EDGE_COUNT = "UPDATE domain_dependencies SET edge_count=%s WHERE from_domain=%s AND to_domain=%s"
SQL_UPDATE_DOMAIN_DEP_PAIR = (
    "UPDATE domain_dependencies SET from_domain=%s, to_domain=%s WHERE from_domain=%s AND to_domain=%s"
)

# --- cmd_update_domain_capacity / layer / ssot_path ---
SQL_SELECT_DOMAIN_CAPACITY = (
    "SELECT domain_id, current_modules, max_modules, production_nodes FROM domains WHERE domain_id=%s"
)
SQL_SELECT_DOMAIN_LAYER = "SELECT domain_id, layer_id FROM domains WHERE domain_id=%s"
SQL_UPDATE_DOMAIN_LAYER = "UPDATE domains SET layer_id=%s, updated_at=%s WHERE domain_id=%s"
SQL_SELECT_DOMAIN_SSOT_PATH = "SELECT domain_id, ssot_path FROM domains WHERE domain_id=%s"
SQL_UPDATE_DOMAIN_SSOT_PATH = "UPDATE domains SET ssot_path=%s, updated_at=%s WHERE domain_id=%s"

# --- cmd_insert_domain_mapping ---
SQL_SELECT_DOMAIN_MAPPING_BY_PREFIX = "SELECT mapping_id, domain_id FROM domain_mapping WHERE path_prefix=%s"
SQL_INSERT_DOMAIN_MAPPING = (
    "INSERT INTO domain_mapping "
    "(path_prefix, domain_id, subdomain_id, mapping_type, mapped_at, mapped_by, note) "
    "VALUES (%s, %s, %s, %s, %s, %s, %s)"
)

# --- mark_entry_point / update_module_metadata ---
SQL_SELECT_NODE_ENTRY_POINT_BY_PATH = "SELECT node_id, path, entry_point FROM nodes WHERE path=%s"
SQL_UPDATE_NODE_ENTRY_POINT = "UPDATE nodes SET entry_point=%s WHERE path=%s"
SQL_SELECT_NODE_BP_BY_PATH = "SELECT node_id, blueprint_id FROM nodes WHERE path=%s"
SQL_SELECT_NODES_METADATA_BY_PATH = "SELECT path FROM nodes_metadata WHERE path=%s"

# --- cmd_set_blueprint_id (path-targeted blueprint_id 赋值，专为空值节点) ---
# 裁定#209 Stage 2: path 为稳定 PK。old='' 的节点无法用 --rename-blueprint-id
# （old='' 会误伤全库所有空值节点），故提供按 path 精确赋值的 sanctioned 入口。
SQL_SELECT_NODE_FULL_BY_PATH = (
    "SELECT node_id, blueprint_id, belongs_to, build_status, design_maturity, domain_id FROM nodes WHERE path=%s"
)
SQL_UPDATE_NODE_BLUEPRINT_ID_BY_PATH = "UPDATE nodes SET blueprint_id=%s, belongs_to=%s WHERE path=%s"
SQL_UPDATE_NODES_METADATA_BP_BY_PATH = "UPDATE nodes_metadata SET blueprint_id=%s, last_updated=%s WHERE path=%s"
SQL_CLEAR_BLUEPRINT_ID_INVALID_BY_PATH = "UPDATE nodes SET blueprint_id_invalid=0 WHERE path=%s"
# 治本（2026-08-03）：按 blueprint_id 清除 invalid 标志（inverse of mark_blueprint_invalid）
SQL_CLEAR_INVALID_FLAG_BY_BP = "UPDATE nodes SET blueprint_id_invalid=0, gate_reason=NULL WHERE blueprint_id=%s"
# 治本（2026-08-03）：按 path 清空 blueprint_id（infra_id 误存为 blueprint_id 的治本清理）
SQL_CLEAR_BLUEPRINT_ID_BY_PATH = (
    "UPDATE nodes SET blueprint_id=NULL, belongs_to=NULL, blueprint_id_invalid=0 WHERE path=%s"
)
SQL_CLEAR_NODES_METADATA_BP_BY_PATH = "UPDATE nodes_metadata SET blueprint_id=NULL, last_updated=%s WHERE path=%s"


@contextlib.contextmanager
def _db_write_lock(
    owner_id: str | None = None,
    task: str = "depgraph write",
    db_path: Path | str | None = None,
    max_retries: int = 30,
    retry_interval: float = 1.0,
):
    """depgraph 写入上下文管理器（裁定#209 阶段1：pg_advisory_lock 互斥保护）。

    与 generate_project_depgraph.py.write_depgraph_to_db 共享 lock key 424242。
    会话级 lock，finally 显式 pg_advisory_unlock 释放。
    threading.local 防嵌套死锁：同线程嵌套调用时直接 yield（外层已持有锁）。
    """
    if getattr(_depgraph_lock_local, "held", False):
        # 嵌套调用：外层已持有锁，直接 yield
        yield
        return
    lock_conn = get_depgraph_pg_connection(autocommit=True)
    _depgraph_lock_local.held = True
    try:
        lock_conn.execute(SQL_PG_ADVISORY_LOCK)
        yield
    finally:
        try:
            lock_conn.execute(SQL_PG_ADVISORY_UNLOCK)
        finally:
            lock_conn.close()
            _depgraph_lock_local.held = False


@contextlib.contextmanager
def _optional_db_lock(own_conn: bool, task: str = "depgraph write", db_path: Path | str | None = None):
    """当 own_conn=True 时进入写入上下文（P2 后 no-op，PG MVCC 提供原子性）。"""
    if own_conn:
        with _db_write_lock(task=task, db_path=db_path):
            yield
    else:
        yield


def _load_depgraph_from_db(db_path: Path | None = None) -> dict:
    """从 PostgreSQL 数据库加载 depgraph，返回与原 YAML 结构兼容的 dict。

    db_path 参数保留向后兼容（治本2026-06-27：默认 None，PG 模式下忽略）。
    """
    conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
    # P2 PG: row_factory 由 wrapper 处理（RealDictCursor）
    data: dict = {"nodes": {}, "edges": [], "domains": {}, "metadata": {}}
    for row in conn.execute(SQL_SELECT_ALL_NODES):
        node = dict(row)
        nid = node.pop("node_id")
        if "node_type" in node:
            node["type"] = node.pop("node_type")
        data["nodes"][nid] = node
    for row in conn.execute(SQL_SELECT_ALL_EDGES):
        edge = dict(row)
        if "from_node_id" in edge:
            edge["from"] = edge.pop("from_node_id")
        if "to_node_id" in edge:
            edge["to"] = edge.pop("to_node_id")
        data["edges"].append(edge)
    for row in conn.execute(SQL_SELECT_ALL_DOMAINS):
        domain = dict(row)
        did = domain.pop("domain_id")
        data["domains"][did] = domain
    conn.close()
    return data


def _load_depgraph() -> dict:
    """_load_depgraph implementation."""
    # 治本（2026-06-27）：删除 if not DEPGRAPH_PATH.exists(): sys.exit(EXIT_FINDINGS) 守卫（latent bug）。
    # PG 模式下文件路径无意义，直接查询 PG；连接失败时 fail-loud 抛异常。
    try:
        return _load_depgraph_from_db()
    except Exception as e:
        logger.error("Failed to load depgraph from PostgreSQL: %s", e)
        sys.exit(EXIT_ERROR)


def _find_module(dep: dict, module_id: str) -> dict | None:
    """在 depgraph nodes 中查找指定 module_id 的模块（按 belongs_to 或 blueprint_id 匹配）。"""
    for node_id, node in dep.get("nodes", {}).items():
        if node.get("belongs_to") == module_id or node.get("blueprint_id") == module_id:
            node["_node_id"] = node_id
            return node
    return None


def _atomic_write(dep: dict, conn=None, only_node_ids: set | None = None) -> None:
    """将修改后的 depgraph 数据写回 PostgreSQL 数据库。

    如果提供 conn 参数，使用该连接（不 commit/close）——用于 cmd_batch 统一事务。
    如果未提供 conn，打开新连接（独立模式，commit+close）。

    only_node_ids（#ARCH-170 混合 op 静默回滚治本，2026-08-22）：
    - None（默认）= 全量回写 dep["nodes"]（独立模式旧行为，兼容单 op CLI 入口）。
    - 空 set() = 跳过回写（纯 domain_ops 批次无 node_op 触碰，避免陈旧快照覆盖）。
    - 非空 set = 仅回写被 node_op 触碰的节点（混合批次下，domain_ops 如 migrate_nodes
      已 SQL 直写 domain_id，全量回写会用加载时的陈旧 NULL 快照覆盖之——静默回滚根因）。
    """
    own_conn = conn is None
    if only_node_ids is not None and not only_node_ids:
        # 纯 domain_ops 批次：无 node_op 触碰节点，全量回写只会用陈旧快照覆盖 domain_ops
        # 的 SQL 直写结果。跳过回写，由 cmd_batch 尾部统一 commit domain_ops 的变更。
        return
    with _optional_db_lock(own_conn, task="_atomic_write"):
        if own_conn:
            conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        try:
            for node_id, node_data in dep.get("nodes", {}).items():
                if only_node_ids is not None and node_id not in only_node_ids:
                    continue
                clean = {k: v for k, v in node_data.items() if not k.startswith("_")}
                if "type" in clean:
                    clean["node_type"] = clean.pop("type")
                set_clause = ", ".join(f"{k} = %s" for k in clean)
                values = list(clean.values()) + [node_id]
                conn.execute(
                    SQL_UPDATE_NODE_SET_DYNAMIC.format(set_clause=set_clause), values
                )  # 5.160.2 OK: 动态标识符经 SQL_* 模板常量
            if own_conn:
                conn.commit()
            print("OK: depgraph DB updated", file=sys.stderr)
        except Exception as e:
            if own_conn:
                conn.rollback()
            logger.error("DB write failed: %s", e)
            sys.exit(4)
        finally:
            if own_conn:
                conn.close()


def cmd_update_module(dep: dict, module_id: str, field: str, value: str) -> None:
    """更新单个模块的字段。"""
    module = _find_module(dep, module_id)
    if module is None:
        print(f"ERROR: Module '{module_id}' not found", file=sys.stderr)
        sys.exit(3)

    # 蓝图保护（V1 漏洞修复）：禁止用通用 --update-module 修改 blueprint_id
    # 原因：会绕过 --rename-blueprint-id 的传播+YAML扫描+SYNC HINT+事务管理全部保护
    # 治本：阻断入口，强制使用专用工具 --rename-blueprint-id
    if field == "blueprint_id":
        print(
            f"ERROR: 禁止用 --update-module 修改 blueprint_id（会绕过传播+YAML扫描+SYNC HINT 全部保护）。\n"
            f"请使用专用改名工具：\n"
            f"  python scripts/governance/apply_depgraph.py --rename-blueprint-id {module_id} {value}\n"
            f"该工具会自动处理 4 类传播表 + YAML 真源扫描 + SYNC HINT 提醒。",
            file=sys.stderr,
        )
        sys.exit(3)

    old_value = module.get(field, "<not set>")

    # 类型转换
    if field in (
        "safety_level",
        "ai_autonomy",
        "stability",
        "build_status",
        "blueprint_status",
        "priority",
    ):
        module[field] = value
    elif field in ("physical_files",):
        try:
            module[field] = json.loads(value)
        except json.JSONDecodeError:
            module[field] = [p.strip() for p in value.split(",")]
    else:
        module[field] = value

    print(f"Updated {module_id}.{field}: {old_value} -> {module[field]}", file=sys.stderr)


def _apply_node_op(dep: dict, change: dict, index: int) -> int | None:
    """对 dep dict 执行节点级操作（不写 DB）。供 cmd_batch 复用。

    返回被触碰节点的 node_id（_find_module 命中时写入 node["_node_id"]），
    未命中/op 未识别返回 None——cmd_batch 收集为 dirty 集传给 _atomic_write
    仅回写触碰节点（#ARCH-170 混合 op 静默回滚治本）。
    """
    op = change.get("op", "update")
    module_id = change.get("module_id", "")
    touched: int | None = None
    if op == "update":
        module = _find_module(dep, module_id)
        touched = module.get("_node_id") if module else None
        cmd_update_module(dep, module_id, change.get("field", ""), change.get("value", ""))
        return touched
    elif op == "add_physical_file":
        module = _find_module(dep, module_id)
        if module is None:
            print(f"ERROR: Module '{module_id}' not found for change #{index}", file=sys.stderr)
            return None
        touched = module.get("_node_id")
        pf = change.get("path", "")
        if pf not in module.get("physical_files", []):
            module.setdefault("physical_files", []).append(pf)
            print(f"Added {pf} to {module_id}", file=sys.stderr)
        return touched
    elif op == "remove_physical_file":
        module = _find_module(dep, module_id)
        if module is None:
            print(f"ERROR: Module '{module_id}' not found for change #{index}", file=sys.stderr)
            return None
        touched = module.get("_node_id")
        pf = change.get("path", "")
        if pf in module.get("physical_files", []):
            module["physical_files"].remove(pf)
            print(f"Removed {pf} from {module_id}", file=sys.stderr)
        return touched
    elif op == "set_physical_files":
        module = _find_module(dep, module_id)
        if module is None:
            print(f"ERROR: Module '{module_id}' not found for change #{index}", file=sys.stderr)
            return None
        touched = module.get("_node_id")
        module["physical_files"] = change.get("files", [])
        print(f"Set {len(module['physical_files'])} physical_files for {module_id}", file=sys.stderr)
        return touched
    return None


# ---------------------------------------------------------------------------
# cmd_batch op 注册表——op 清单真源唯一（从此处 keys() 自动派生）
# 对标 capability_lookup.py 运行时派生模式（§6.16 静态清单自动生成铁律）
# 加 op 只需：1)写 _handle_xxx 函数 2)加入 _DOMAIN_OPS 字典——docstring/AGENTS.md 自动派生
# 禁止在 docstring/AGENTS.md 手工列 op 清单（同步副本会漂移）
# ---------------------------------------------------------------------------
def _handle_insert_domain(change: dict, dry_run: bool, conn=None) -> bool:
    """_handle_insert_domain implementation."""
    return cmd_insert_domain(
        domain_id=change.get("domain_id", ""),
        domain_name=change.get("domain_name", ""),
        domain_group=change.get("domain_group", ""),
        layer_id=change.get("layer_id", ""),
        ssot_path=change.get("ssot_path", ""),
        max_modules=change.get("max_modules", 200),
        description=change.get("description", ""),
        dry_run=dry_run,
        conn=conn,
    )


def _handle_update_domain_id(change: dict, dry_run: bool, conn=None) -> bool:
    """_handle_update_domain_id implementation."""
    count = cmd_update_domain_id(
        module_id=change.get("module_id", ""),
        new_domain_id=change.get("new_domain_id", ""),
        dry_run=dry_run,
        conn=conn,
    )
    return count >= 0


def _handle_update_path(change: dict, dry_run: bool, conn=None) -> bool:
    """_handle_update_path implementation."""
    count = cmd_update_path(
        module_id=change.get("module_id", ""),
        old_prefix=change.get("old_prefix", ""),
        new_prefix=change.get("new_prefix", ""),
        dry_run=dry_run,
        conn=conn,
    )
    return count >= 0


def _handle_migrate_dependencies(change: dict, dry_run: bool, conn=None) -> bool:
    """_handle_migrate_dependencies implementation."""
    count = cmd_migrate_dependencies(
        from_domain=change.get("from_domain", ""),
        to_domain=change.get("to_domain", ""),
        new_from_domain=change.get("new_from_domain", ""),
        new_to_domain=change.get("new_to_domain", ""),
        dry_run=dry_run,
        conn=conn,
    )
    return count >= 0


def _handle_update_domain_layer(change: dict, dry_run: bool, conn=None) -> bool:
    """_handle_update_domain_layer implementation."""
    return cmd_update_domain_layer(
        domain_id=change.get("domain_id", ""),
        layer_id=change.get("layer_id", ""),
        dry_run=dry_run,
        conn=conn,
    )


def _handle_migrate_nodes(change: dict, dry_run: bool, conn=None) -> bool:
    """_handle_migrate_nodes implementation."""
    count = cmd_migrate_nodes(
        node_ids=change.get("node_ids", []),
        new_domain_id=change.get("new_domain_id", ""),
        dry_run=dry_run,
        conn=conn,
    )
    return count >= 0


def _handle_tag_nodes(change: dict, dry_run: bool, conn=None) -> bool:
    """_handle_tag_nodes implementation."""
    count = cmd_tag_nodes(
        node_ids=change.get("node_ids", []),
        tag=change.get("tag", ""),
        remove=change.get("remove", False),
        dry_run=dry_run,
        conn=conn,
    )
    return count >= 0


def _handle_update_domain_ssot_path(change: dict, dry_run: bool, conn=None) -> bool:
    """_handle_update_domain_ssot_path implementation."""
    return cmd_update_domain_ssot_path(
        domain_id=change.get("domain_id", ""),
        ssot_path=change.get("ssot_path", ""),
        dry_run=dry_run,
        conn=conn,
    )


def _handle_rename_domain(change: dict, dry_run: bool, conn=None) -> bool:
    """_handle_rename_domain implementation."""
    count = cmd_rename_domain(
        old_id=change.get("old_id", ""),
        new_id=change.get("new_id", ""),
        dry_run=dry_run,
        conn=conn,
    )
    return count >= 0


def _handle_delete_domain(change: dict, dry_run: bool, conn=None) -> bool:
    """_handle_delete_domain implementation."""
    count = cmd_delete_domain(
        domain_id=change.get("domain_id", ""),
        dry_run=dry_run,
        conn=conn,
        force=change.get("force", False),
    )
    return count >= 0


# op 注册表——op 清单真源唯一（从此处 keys() 自动派生，禁止手工同步到 docstring/AGENTS.md）
# 节点级 op（经 dep dict + _atomic_write，不直接写 DB）
_NODE_OPS: set[str] = {"update", "add_physical_file", "remove_physical_file", "set_physical_files"}

# 域级 op（直接 SQL，ARCH-CAP-005）
_DOMAIN_OPS: dict[str, object] = {
    "insert_domain": _handle_insert_domain,
    "update_domain_id": _handle_update_domain_id,
    "update_path": _handle_update_path,
    "migrate_dependencies": _handle_migrate_dependencies,
    "update_domain_layer": _handle_update_domain_layer,
    "migrate_nodes": _handle_migrate_nodes,
    "tag_nodes": _handle_tag_nodes,
    "update_domain_ssot_path": _handle_update_domain_ssot_path,
    "rename_domain": _handle_rename_domain,
    "delete_domain": _handle_delete_domain,
}


def _get_supported_ops() -> list[str]:
    """返回 cmd_batch 支持的所有 op（从注册表自动派生，真源唯一）。"""
    return sorted(_NODE_OPS | set(_DOMAIN_OPS.keys()))


def cmd_batch(dep: dict, changes: list[dict], dry_run: bool) -> None:
    """批量处理变更（统一事务管理，消除部分提交风险）。

    非dry-run模式下，所有操作（域级+节点级）共享同一PostgreSQL连接和事务：
    - 全部成功 → 一次commit
    - 任一失败 → 全部rollback（消除P2-002部分提交风险）

    支持的 op 清单：运行 `apply_depgraph.py --list-ops` 查看（从 _NODE_OPS/_DOMAIN_OPS
    注册表自动派生，真源唯一——对标 capability_lookup.py 运行时派生模式，§6.16 铁律）。
    禁止手工在 docstring/AGENTS.md 列 op 清单（同步副本会漂移）。

    用法示例::

        python scripts/governance/apply_depgraph.py --list-ops
        python scripts/governance/apply_depgraph.py --batch changes.json --dry-run
        python scripts/governance/apply_depgraph.py --batch changes.json

    changes.json 示例::

        [
          {"op": "rename_domain", "old_id": "D-SIGNAL_ASHARE", "new_id": "D_ASHARE_SIGNAL"},
          {"op": "insert_domain", "domain_id": "D_ASHARE_SIGNAL", "domain_name": "...", ...}
        ]

    注意：rename_domain 必须最后执行（LIKE 模式匹配会误伤同前缀子域名，见裁定#204）。
    """
    if isinstance(changes, str):
        changes = json.loads(changes)

    all_ops = _NODE_OPS | set(_DOMAIN_OPS.keys())
    print(f"Processing {len(changes)} changes... (supported ops: {len(all_ops)})", file=sys.stderr)

    if dry_run:
        # Dry-run: 域级 op 各自打印预览，节点级 op 修改 dep dict（不写 DB）
        domain_op_count = 0
        for i, change in enumerate(changes):
            op = change.get("op", "update")
            if op in _DOMAIN_OPS:
                ok = _DOMAIN_OPS[op](change, dry_run=True)
                if ok:
                    domain_op_count += 1
            elif op in _NODE_OPS:
                _apply_node_op(dep, change, i)
            else:
                raise ValueError(f"change #{i}: unknown op '{op}', supported: {sorted(all_ops)}")
        print(f"DRY RUN - no changes written (domain_ops={domain_op_count})", file=sys.stderr)
        return

    # 非dry-run: 统一事务（所有操作共享一个连接，全部成功才commit）
    # 治本（2026-06-30 第1波任务1）：运行时 DB 写入在 pre-commit 框架外，
    # --dry-run 可选导致 AI 可跳过预览直接写 DB。加环境变量门禁强制两阶段：
    # AI 必须先跑 --dry-run 确认变更，再设置 ZEPHYR_DEPGRAPH_BATCH_APPLY=1 才能写入。
    # 模仿 validate_rules_integrity --register 的 ZEPHYR_RECONCILER_MODE 门禁模式
    # （非新增门禁——扩展现有 cmd_batch 自身的写入前置校验，符合 AD-GOV-001 收敛期约束）。
    if os.environ.get("ZEPHYR_DEPGRAPH_BATCH_APPLY") != "1":
        print(
            "[DEPGRAPH] 🔴 --batch 写入被门禁阻断：未设置 ZEPHYR_DEPGRAPH_BATCH_APPLY=1。\n"
            "运行时 DB 写入在 pre-commit 框架外，强制两阶段执行防止误写：\n"
            "  1. 先跑 dry-run 预览: python apply_depgraph.py --batch changes.json --dry-run\n"
            "  2. 确认无误后写入（PowerShell）: $env:ZEPHYR_DEPGRAPH_BATCH_APPLY=1; python apply_depgraph.py --batch changes.json\n"
            "  2. 确认无误后写入（bash）: ZEPHYR_DEPGRAPH_BATCH_APPLY=1 python apply_depgraph.py --batch changes.json\n"
            "合法写入入口：GitCommitGateway（pre-commit 覆盖）或本显式门禁。",
            file=sys.stderr,
        )
        sys.exit(3)
    with _db_write_lock(task="cmd_batch"):
        conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        domain_op_count = 0
        dirty_node_ids: set = set()
        try:
            for i, change in enumerate(changes):
                op = change.get("op", "update")
                if op in _DOMAIN_OPS:
                    ok = _DOMAIN_OPS[op](change, dry_run=False, conn=conn)
                    if not ok:
                        raise RuntimeError(f"change #{i}: {op} failed")
                    domain_op_count += 1
                elif op in _NODE_OPS:
                    touched = _apply_node_op(dep, change, i)
                    if touched is not None:
                        dirty_node_ids.add(touched)
                else:
                    raise ValueError(f"change #{i}: unknown op '{op}', supported: {sorted(all_ops)}")

            # 节点级变更通过共享连接写入（不单独commit）。
            # #ARCH-170：仅回写被 node_op 触碰的节点（dirty_node_ids）——全量回写会用
            # 加载时的陈旧快照覆盖 domain_ops（migrate_nodes 等）SQL 直写的 domain_id，
            # 造成 exit 0 报 OK 但超管直查仍旧值的静默回滚（2026-08-22 两次实证）。
            # 纯 domain_ops 批次 dirty 为空 → _atomic_write 跳过回写，仅 commit domain_ops。
            _atomic_write(dep, conn=conn, only_node_ids=dirty_node_ids)
            # 统一提交所有变更（域级+节点级）
            conn.commit()
            print(f"Applied {len(changes)} changes to depgraph (domain_ops={domain_op_count})", file=sys.stderr)
        except Exception as e:
            conn.rollback()
            logger.error("batch failed, all changes rolled back: %s", e)
            sys.exit(4)
        finally:
            conn.close()


# ===== P0-2 新增：设计态节点/边管理（§22.5）=====


def _warn_translation_coverage(path: str) -> None:
    """Layer 1 君子协定提示：新登记节点在翻译真源无合格 plain_zh 大白话简介时 warn。

    TRANSLATION-COVERAGE 四层防御的 Layer 1（登记时提示，不阻断）——add_design_node
    成功写 DB 后调用。检查 path 在 module_translation_registry.yaml 是否有非空 plain_zh；
    无则 stderr+logger 提示 AI 运行 add_module_translation.py。fail-open：loader 不可达
    或查询异常时不阻断登记流程（提交时 Layer 2 gate 兜底）。

    真源边界（TRAE-062）：本函数只读翻译 YAML 校验，不写（apply_depgraph 写 DB 架构数据，
    翻译是规则数据，正交真源）。
    """
    if not path or path.endswith("/"):
        return  # directory 粒度无单文件翻译条目，跳过
    try:
        from _shared.module_translation_loader import get_module_translation  # noqa: WPS433 — _GOV_DIR 已在 sys.path

        trans = get_module_translation(path)
        plain = (trans or {}).get("plain_zh", "") if trans else ""
        if plain and plain.strip():
            return  # 已有合格简介，不提示
    except Exception as e:  # noqa: BLE001 — loader 不可达=环境异常，fail-open 不阻断登记
        logger.debug("translation coverage warn 跳过（loader 不可达）: %s: %s", type(e).__name__, e)
        return
    # 缺简介 → 提示（不阻断）
    msg = (
        f"[TRANSLATION-COVERAGE] 新节点 {path} 在翻译真源无 plain_zh 大白话简介。"
        f"请运行：python scripts/governance/d3_metadata/add_module_translation.py "
        f"--path {path} --domain <D_*> --name-zh <中文名> --plain-zh <大白话简介>。"
        f"提交时 TRANSLATION-COVERAGE 门禁将校验（观察期 warn，之后硬阻断）。"
    )
    print(msg, file=sys.stderr)
    logger.warning(msg)


def add_design_node(
    path: str,
    blueprint_id: str,
    domain_id: str,
    build_status: str = "planned",
    granularity: str = "directory",
    node_type: str | None = None,
    db_path: str = None,
) -> int:
    """
    新增设计态节点（支持 file/directory/module 粒度，2026-07-13 治本）。
    返回：新分配的 node_id
    校验：
    - granularity 必须在 granularity_vocabulary.yaml 合法值中（trae_060 §2 动态加载）
    - path 格式必须匹配粒度：directory 要求以 / 结尾，file/module 禁止以 / 结尾
    - blueprint_id 必须指向存在的蓝图文件
    - domain_id 必须在 domains 表中存在
    - build_status 必须符合 §12.6 状态机规则（5态：planned/generated/testing/stable/deprecated）
    写入字段：design_maturity='design', granularity=参数, node_type=参数或推导, blueprint_path=机械推导

    治本（2026-07-13，trae_060 §2 + trae_056 §phase_2_design_state）：
    - 原 add_design_node 硬编码 granularity='directory' → 单文件模块无法走设计态登记
      → trae_056 铁律系统性不可执行
    - 现参数化 granularity + 动态加载词表校验，支持 file 粒度设计态（32 个先例已验证数据库支持）
    - node_type 默认按 granularity 推导：directory→blueprint，file/module→module（可覆盖）
    """
    # 动态加载 granularity 合法值（SSoT：granularity_vocabulary.yaml，trae_060 §2 治本）
    valid_granularities = load_vocabulary_values("granularity_vocabulary.yaml", strict=False)  # noqa: gate-vocab  SSoT 动态加载，非硬编码
    if not valid_granularities:
        # strict=False 时词表缺失返回空 set → fail-closed（禁止无校验写入）
        print("ERROR: granularity_vocabulary.yaml 加载失败（空集），禁止无校验写入", file=sys.stderr)
        return -1
    if granularity not in valid_granularities:
        print(f"ERROR: granularity 必须是 {valid_granularities} 之一: {granularity}", file=sys.stderr)
        return -1

    # path 格式校验：根据粒度匹配（directory 要求 / 结尾，其他禁止）
    if granularity == "directory":
        if not path.endswith("/"):
            print(f"ERROR: granularity=directory 时 path 必须以 / 结尾（目录路径）: {path}", file=sys.stderr)
            return -1
    else:
        # file/module 粒度：path 是文件/模块路径，不应以 / 结尾
        if path.endswith("/"):
            print(f"ERROR: granularity={granularity} 时 path 禁止以 / 结尾（非目录粒度）: {path}", file=sys.stderr)
            return -1

    # node_type 推导：未显式传入时按 granularity 推导默认值
    # directory→blueprint（蓝图级设计态），file/module→module（代码/模块级设计态）
    if node_type is None:
        node_type = "blueprint" if granularity == "directory" else "module"

    # 校验build_status（5态枚举）
    valid_status = {"planned", "generated", "testing", "stable", "deprecated"}  # noqa: gate-vocab  build_status 5态，非 module_lifecycle_status
    if build_status not in valid_status:
        print(f"ERROR: build_status必须是{valid_status}之一: {build_status}", file=sys.stderr)
        return -1

    with _db_write_lock(db_path=db_path, task="add_design_node"):
        conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        try:
            # 校验domain_id存在
            domain = conn.execute(SQL_SELECT_DOMAIN_ID_BY_DOMAIN_ID, (domain_id,)).fetchone()
            if not domain:
                print(f"ERROR: domain_id '{domain_id}' 不在domains表中", file=sys.stderr)
                return -1

            # 校验blueprint_id指向存在的蓝图文件
            if blueprint_id and not blueprint_id.startswith("PLACEHOLDER"):
                bp_path = REPO_ROOT / "docs" / "03_modules" / blueprint_id / "blueprint.md"
                if not os.path.exists(bp_path):
                    print(f"WARNING: blueprint_id '{blueprint_id}' 对应的蓝图文件不存在: {bp_path}", file=sys.stderr)

            # 机械推导blueprint_path
            blueprint_path = f"docs/03_modules/{blueprint_id}/" if blueprint_id else ""

            # 检查是否已存在同path的设计态节点
            existing = conn.execute(SQL_SELECT_NODE_BY_PATH_DESIGN, (path,)).fetchone()
            if existing:
                print(
                    f"WARNING: path '{path}' 已有设计态节点 node_id={existing['node_id']}，执行UPDATE", file=sys.stderr
                )
                conn.execute(
                    SQL_UPDATE_DESIGN_NODE_BY_ID,
                    (
                        blueprint_id,
                        domain_id,
                        build_status,
                        blueprint_path,
                        granularity,
                        node_type,
                        existing["node_id"],
                    ),
                )
                conn.commit()
                _warn_translation_coverage(path)
                return existing["node_id"]

            # 插入新节点（granularity/node_type 参数化，消除硬编码 trae_060 §2）
            # #ARCH-70：file 粒度同写 file_path=path（SQL_INSERT_DESIGN_NODE 常量注释有完整病根）
            cur = conn.execute(
                SQL_INSERT_DESIGN_NODE,
                (
                    node_type,
                    path,
                    path if granularity != "directory" else "",
                    granularity,
                    domain_id,
                    blueprint_id,
                    build_status,
                    blueprint_path,
                ),
            )
            node_id = cur.fetchone()["node_id"]
            conn.commit()
            print(f"[OK] 新增设计态节点 node_id={node_id} path={path} granularity={granularity}", file=sys.stderr)
            _warn_translation_coverage(path)
            return node_id
        except Exception as e:
            conn.rollback()
            logger.error("add_design_node失败: %s", e)
            return -1
        finally:
            conn.close()


def _check_scan_scope(path: str) -> tuple[bool, list[str]]:
    """检查 path 是否在 depgraph 生成器扫描范围内（ARCH-061 门禁）。

    读取 depgraph_scan_exclusions.yaml 的 scan_dirs 配置。
    返回: (in_scope, scan_dirs) — in_scope=True 表示在扫描范围内（不应手动添加节点）
    """
    scan_config_path = (
        REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "depgraph_scan_exclusions.yaml"
    )
    if not scan_config_path.exists():
        return False, []
    try:
        import yaml

        with open(scan_config_path, encoding="utf-8") as f:
            config = yaml.safe_load(f)
        scan_dirs = config.get("depgraph", {}).get("scan_dirs", [])
        path_norm = path.lstrip("./").rstrip("/")
        for scan_dir in scan_dirs:
            scan_dir_norm = scan_dir.rstrip("/")
            if path_norm == scan_dir_norm or path_norm.startswith(scan_dir_norm + "/"):
                return True, scan_dirs
        return False, scan_dirs
    except Exception:
        return False, []


def add_file_node(
    path: str,
    blueprint_id: str,
    domain_id: str,
    db_path: str = None,
    force: bool = False,
) -> int:
    """
    新增文件级 production 节点（补注册孤儿文件）。
    返回：新分配的 node_id
    校验：
    - path 必须不以 / 结尾（文件路径）
    - 文件必须存在于磁盘
    - domain_id 必须在 domains 表中存在
    - ARCH-061 门禁：path 在生成器扫描范围内时硬阻断（force=True 可逃生）
    写入字段：design_maturity='production', granularity='file', build_status='generated'
    """
    if path.endswith("/"):
        print(f"ERROR: path必须不以/结尾（文件路径）: {path}", file=sys.stderr)
        return -1

    project_root = REPO_ROOT
    full_path = project_root / path
    if not full_path.exists():
        print(f"ERROR: 文件不存在: {full_path}", file=sys.stderr)
        return -1

    # ARCH-061 门禁：扫描范围内的文件由生成器自动登记，禁止手动 add-file-node
    if not force:
        in_scope, scan_dirs = _check_scan_scope(path)
        if in_scope:
            print(
                f"ERROR [GATE-DEPGRAPH-SCOPE / ARCH-061]: path '{path}' 在 depgraph 生成器扫描范围内。\n"
                f"  生成器会自动扫描登记该文件，手动 add-file-node 是多余且有害的\n"
                f"  （干扰生成器 --force 重建，导致 design edge 保护冲突）。\n"
                f"  正确做法：python scripts/governance/generate_project_depgraph.py --output-db depgraph --force\n"
                f"  逃生通道：--force-add-file-node（仅在生成器故障且需紧急补登记时使用）",
                file=sys.stderr,
            )
            return -1

    with _db_write_lock(db_path=db_path, task="add_file_node"):
        conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        try:
            domain = conn.execute(SQL_SELECT_DOMAIN_ID_BY_DOMAIN_ID, (domain_id,)).fetchone()
            if not domain:
                print(f"ERROR: domain_id '{domain_id}' 不在domains表中", file=sys.stderr)
                return -1

            existing = conn.execute(
                SQL_SELECT_NODE_BY_PATH_PRODUCTION,
                (path,),
            ).fetchone()
            if existing:
                print(
                    f"WARNING: path '{path}' 已有production节点 node_id={existing['node_id']}",
                    file=sys.stderr,
                )
                return existing["node_id"]

            blueprint_path = (
                f"docs/03_modules/{blueprint_id}/" if blueprint_id and not blueprint_id.startswith("PENDING") else None
            )

            cur = conn.execute(
                """INSERT INTO nodes (node_type, path, granularity, domain_id, blueprint_id,
                   build_status, design_maturity, blueprint_path, can_build, subdomain_id)
                   VALUES (%s, %s, 'file', %s, %s, 'generated', 'production', %s, 0, %s)
                   RETURNING node_id""",
                ("module", path, domain_id, blueprint_id, blueprint_path, domain_id),
            )
            node_id = cur.fetchone()["node_id"]
            conn.commit()
            print(
                f"[OK] 新增文件级production节点 node_id={node_id} path={path}",
                file=sys.stderr,
            )
            return node_id
        except Exception as e:
            conn.rollback()
            logger.error("add_file_node失败: %s", e)
            return -1
        finally:
            conn.close()


def fix_path_semantics_for_design_nodes(dry_run: bool = False) -> dict:
    """批量修复历史 design 节点 path 与 granularity 语义不一致问题（5.179 治本）。

    问题背景（architecture_debt §5.179 遗留子项 ①）：
    历史 design 节点存在 path 末尾字符与 granularity 字段语义矛盾：
    - Case 1a: path 以 .py/ 结尾且 production 节点已存在相同 path（去尾 / 后）——stale 重复
      → 软废弃（design_maturity='deprecated'），production 节点已是正确真源
    - Case 1b: path 以 .py/ 结尾且无 production 节点（孤儿 design 节点）——path/granularity 都错
      → 去尾 / + granularity='file' + node_type='module'
    - Case 3: path 以 / 结尾（目录语义）但 granularity='file' 或 'module'
      → granularity='directory' + node_type='blueprint'（保留尾 /）

    本函数为一次性迁移治本工具（SSoT：架构数据真源在 DB，由 apply_depgraph.py 写入）。

    Args:
        dry_run: True=仅预览不写入；False=实际写入。

    Returns:
        dict with keys: 'case1a_count', 'case1b_count', 'case3_count',
        'fixed', 'deprecated', 'skipped', 'details'.
    """
    result = {
        "case1a_count": 0,
        "case1b_count": 0,
        "case3_count": 0,
        "fixed": 0,
        "deprecated": 0,
        "skipped": 0,
        "details": [],
    }

    with _db_write_lock(db_path=None, task="fix_path_semantics_for_design_nodes"):
        conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        try:
            # Case 1: path ends with .py/ but granularity=directory (file semantics)
            cur = conn.execute(SQL_FIX_PATH_CASE1_SELECT_DESIGN_PYSLASH)
            case1_rows = cur.fetchall()

            for r in case1_rows:
                node_id = r["node_id"]
                old_path = r["path"]
                new_path = old_path.rstrip("/")
                while new_path.endswith("/"):
                    new_path = new_path.rstrip("/")

                # Check if any non-design node exists with new_path (Case 1a: stale duplicate).
                # 非 design 节点（production）已是正确真源，design 节点为 stale 重复。
                prod_row = conn.execute(SQL_FIX_PATH_CASE1A_SELECT_NONDESIGN_BY_PATH, (new_path,)).fetchone()

                if prod_row:
                    # Case 1a: non-design node exists, design is stale duplicate → hard delete
                    # 5.179 治本：stale duplicate 节点 path 与 granularity 语义矛盾，
                    # 无法通过 UPDATE 修正 path（unique 约束冲突），且 build_status='deprecated'
                    # 仍保留语义错误行——故彻底删除 stale design 节点 + 关联 design edges。
                    # production 节点已是正确真源。
                    result["case1a_count"] += 1
                    prod_node_id = prod_row["node_id"]
                    prod_maturity = prod_row["design_maturity"]
                    if dry_run:
                        print(
                            f"[DRY-RUN] Case1a HARD-DELETE node_id={node_id} path={old_path!r} "
                            f"({prod_maturity} node_id={prod_node_id} already at {new_path!r})",
                            file=sys.stderr,
                        )
                        result["details"].append(
                            {
                                "node_id": node_id,
                                "case": "1a",
                                "action": "hard_delete",
                                "old_path": old_path,
                                "new_path": new_path,
                                "prod_node_id": prod_node_id,
                                "prod_maturity": prod_maturity,
                            }
                        )
                        result["skipped"] += 1
                    else:
                        # 先删除关联 edges（design edges 之间的 stale duplicate 重复，无价值）
                        edge_del = conn.execute(
                            SQL_FIX_PATH_DELETE_EDGES_BY_NODE,
                            (node_id, node_id),
                        )
                        edge_count = edge_del.rowcount if hasattr(edge_del, "rowcount") else -1
                        # 再删除 stale design 节点
                        conn.execute(
                            SQL_FIX_PATH_DELETE_NODE_BY_ID,
                            (node_id,),
                        )
                        print(
                            f"[OK] Case1a HARD-DELETE node_id={node_id} path={old_path!r} "
                            f"({prod_maturity} node_id={prod_node_id} already at {new_path!r}, "
                            f"edges_deleted={edge_count})",
                            file=sys.stderr,
                        )
                        result["details"].append(
                            {
                                "node_id": node_id,
                                "case": "1a",
                                "action": "hard_delete",
                                "old_path": old_path,
                                "new_path": new_path,
                                "prod_node_id": prod_node_id,
                                "prod_maturity": prod_maturity,
                                "edges_deleted": edge_count,
                            }
                        )
                        result["deprecated"] += 1
                else:
                    # Case 1b: no non-design node, fix path + granularity
                    result["case1b_count"] += 1
                    if dry_run:
                        print(
                            f"[DRY-RUN] Case1b FIX node_id={node_id} path={old_path!r} -> {new_path!r} "
                            f"granularity=directory->file node_type=blueprint->module",
                            file=sys.stderr,
                        )
                        result["details"].append(
                            {
                                "node_id": node_id,
                                "case": "1b",
                                "action": "fix_path",
                                "old_path": old_path,
                                "new_path": new_path,
                            }
                        )
                        result["skipped"] += 1
                    else:
                        conn.execute(
                            SQL_FIX_PATH_CASE1B_UPDATE,
                            (new_path, node_id),
                        )
                        print(
                            f"[OK] Case1b FIX node_id={node_id} path={old_path!r} -> {new_path!r} "
                            f"(granularity=file, node_type=module)",
                            file=sys.stderr,
                        )
                        result["details"].append(
                            {
                                "node_id": node_id,
                                "case": "1b",
                                "action": "fix_path",
                                "old_path": old_path,
                                "new_path": new_path,
                            }
                        )
                        result["fixed"] += 1

            # Case 3: path ends with / but granularity != directory (directory semantics)
            cur = conn.execute(SQL_FIX_PATH_CASE3_SELECT_DESIGN_NONDIR_SLASH)
            case3_rows = cur.fetchall()
            result["case3_count"] = len(case3_rows)

            for r in case3_rows:
                node_id = r["node_id"]
                old_path = r["path"]
                if dry_run:
                    print(
                        f"[DRY-RUN] Case3 FIX node_id={node_id} path={old_path!r} "
                        f"granularity={r['granularity']}->directory node_type={r['node_type']}->blueprint",
                        file=sys.stderr,
                    )
                    result["details"].append(
                        {
                            "node_id": node_id,
                            "case": 3,
                            "action": "fix_granularity",
                            "old_path": old_path,
                            "new_path": old_path,
                        }
                    )
                    result["skipped"] += 1
                else:
                    conn.execute(
                        SQL_FIX_PATH_CASE3_UPDATE,
                        (node_id,),
                    )
                    print(
                        f"[OK] Case3 FIX node_id={node_id} path={old_path!r} "
                        f"(granularity=directory, node_type=blueprint)",
                        file=sys.stderr,
                    )
                    result["details"].append(
                        {
                            "node_id": node_id,
                            "case": 3,
                            "action": "fix_granularity",
                            "old_path": old_path,
                            "new_path": old_path,
                        }
                    )
                    result["fixed"] += 1

            if not dry_run:
                conn.commit()
            print(
                f"[SUMMARY] Case1a(stale→deprecate)={result['case1a_count']} "
                f"Case1b(orphan→fix)={result['case1b_count']} "
                f"Case3(granularity→fix)={result['case3_count']} "
                f"fixed={result['fixed']} deprecated={result['deprecated']} "
                f"skipped={result['skipped']}",
                file=sys.stderr,
            )
        except Exception as e:
            conn.rollback()
            logger.error("fix_path_semantics_for_design_nodes失败: %s", e)
            raise
        finally:
            conn.close()

    return result


def add_design_edge(
    from_node_id: int,
    to_node_id: int,
    dep_type: str = "import",
    coupling_strength: str = "medium",
    used_symbol: str = "",
    invocation_method: str = "direct",
    api_contract_refs: str = "",
    event_ref: str = "",
    ddd_integration_pattern: str = "",
    failure_mode: str = "runtime_error",
    fallback: str = "no_fallback",
    activation_condition: str = "always",
    data_transfer_description: str = "",
    relationship_type: str = "",
    resource_impact: str = "low",
    db_path: str = None,
) -> int:
    """
    新增设计态边（规划依赖）。
    返回：新分配的 edge_id
    校验：
    - from_node_id 和 to_node_id 必须在 nodes 表中存在且 design_maturity='design'
    - 写入前执行 DFS 循环检测，检测到循环则拒绝写入
    写入字段：dep_maturity='design'
    """
    with _db_write_lock(db_path=db_path, task="add_design_edge"):
        conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        try:
            # 校验from_node_id和to_node_id存在且为设计态
            from_node = conn.execute(SQL_SELECT_NODE_MATURITY_BY_ID, (from_node_id,)).fetchone()
            if not from_node:
                print(f"ERROR: from_node_id={from_node_id} 不存在", file=sys.stderr)
                return -1
            if from_node["design_maturity"] != "design":
                print(
                    f"ERROR: from_node_id={from_node_id} design_maturity={from_node['design_maturity']}（应为design）",
                    file=sys.stderr,
                )
                return -1

            to_node = conn.execute(SQL_SELECT_NODE_MATURITY_BY_ID, (to_node_id,)).fetchone()
            if not to_node:
                print(f"ERROR: to_node_id={to_node_id} 不存在", file=sys.stderr)
                return -1
            if to_node["design_maturity"] != "design":
                print(
                    f"ERROR: to_node_id={to_node_id} design_maturity={to_node['design_maturity']}（应为design）",
                    file=sys.stderr,
                )
                return -1

            # DFS循环检测：检查to_node_id是否能到达from_node_id
            if _detect_cycle_dfs(conn, to_node_id, from_node_id):
                print(f"ERROR: 检测到循环依赖: {to_node_id} -> ... -> {from_node_id}", file=sys.stderr)
                return -1

            # 插入边
            cur = conn.execute(
                SQL_INSERT_DESIGN_EDGE,
                (
                    from_node_id,
                    to_node_id,
                    dep_type,
                    coupling_strength,
                    used_symbol,
                    invocation_method,
                    api_contract_refs,
                    event_ref,
                    ddd_integration_pattern,
                    failure_mode,
                    fallback,
                    activation_condition,
                    data_transfer_description,
                    resource_impact,
                    relationship_type,
                ),
            )
            edge_id = cur.fetchone()["edge_id"]
            conn.commit()
            print(f"[OK] 新增设计态边 edge_id={edge_id} {from_node_id}->{to_node_id}", file=sys.stderr)
            return edge_id
        except Exception as e:
            conn.rollback()
            logger.error("add_design_edge失败: %s", e)
            return -1
        finally:
            conn.close()


def _detect_cycle_dfs(conn, start: int, target: int) -> bool:
    """DFS检测从start是否能到达target（如果到达，则添加start->target的边会形成环）。"""
    if start == target:
        return True
    visited = set()
    stack = [start]
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        # 查询node的所有出边
        edges = conn.execute(SQL_SELECT_TO_NODES_BY_FROM, (node,)).fetchall()
        for edge in edges:
            next_node = edge["to_node_id"]
            if next_node == target:
                return True
            if next_node not in visited:
                stack.append(next_node)
    return False


def add_edge(
    from_node_id: int,
    to_node_id: int,
    dep_type: str = "import_depends",
    dep_maturity: str = "active",
    coupling_strength: str = "medium",
    used_symbol: str = "",
    invocation_method: str = "direct",
    api_contract_refs: str = "",
    event_ref: str = "",
    ddd_integration_pattern: str = "",
    failure_mode: str = "runtime_error",
    fallback: str = "no_fallback",
    activation_condition: str = "always",
    data_transfer_description: str = "",
    relationship_type: str = "",
    resource_impact: str = "low",
    db_path: str = None,
) -> int:
    """
    新增边（通用，不限 design_maturity，支持 production 节点）。
    返回：新分配的 edge_id，-1=失败
    与 add_design_edge 的差异：
    - 不校验两端 design_maturity（允许 design/production/active 任意组合）
    - dep_maturity 参数化（默认 'active'，可设 'design'）
    - 增加重复边检查（同 from/to/dep_type 已存在则拒绝）
    校验：
    - from_node_id 和 to_node_id 必须在 nodes 表中存在
    - dep_type 必须为合法值
    - dep_maturity 必须为合法值（design|active）
    - 写入前执行 DFS 循环检测，检测到循环则拒绝写入
    用途：C集代码层接线（F1→F14/F21/F23 production 边）
    """
    # C集代码层接线 dep_type 业务子集（含 legacy 短名 contract/event/runtime/data）
    # 非全量词表副本——全量真源为 dep_type_vocabulary.yaml（PS-VOC-034）
    valid_types = {  # noqa: gate-vocab  业务子集校验，非词表硬编码
        "contract",
        "event",
        "runtime",
        "data",
        "import_depends",
        "test_depends",
        "config_depends",
    }
    valid_maturities = {"design", "active"}
    if dep_type not in valid_types:
        print(f"ERROR: dep_type '{dep_type}' 不合法（合法值: {valid_types}）", file=sys.stderr)
        return -1
    if dep_maturity not in valid_maturities:
        print(f"ERROR: dep_maturity '{dep_maturity}' 不合法（合法值: {valid_maturities}）", file=sys.stderr)
        return -1

    with _db_write_lock(db_path=db_path, task="add_edge"):
        conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        try:
            # 校验节点存在性（不校验 design_maturity）
            from_node = conn.execute(SQL_SELECT_NODE_ID_BY_ID, (from_node_id,)).fetchone()
            if not from_node:
                print(f"ERROR: from_node_id={from_node_id} 不存在", file=sys.stderr)
                return -1
            to_node = conn.execute(SQL_SELECT_NODE_ID_BY_ID, (to_node_id,)).fetchone()
            if not to_node:
                print(f"ERROR: to_node_id={to_node_id} 不存在", file=sys.stderr)
                return -1

            # 重复边检查
            dup = conn.execute(
                SQL_SELECT_DUP_EDGE,
                (from_node_id, to_node_id, dep_type),
            ).fetchone()
            if dup:
                print(
                    f"ERROR: 重复边已存在 edge_id={dup['edge_id']} ({from_node_id}->{to_node_id} dep_type={dep_type})",
                    file=sys.stderr,
                )
                return -1

            # DFS循环检测
            if _detect_cycle_dfs(conn, to_node_id, from_node_id):
                print(f"ERROR: 检测到循环依赖: {to_node_id} -> ... -> {from_node_id}", file=sys.stderr)
                return -1

            # 插入边
            cur = conn.execute(
                SQL_INSERT_PRODUCTION_EDGE,
                (
                    from_node_id,
                    to_node_id,
                    dep_type,
                    coupling_strength,
                    used_symbol,
                    invocation_method,
                    api_contract_refs,
                    event_ref,
                    ddd_integration_pattern,
                    failure_mode,
                    fallback,
                    activation_condition,
                    data_transfer_description,
                    resource_impact,
                    relationship_type,
                    dep_maturity,
                ),
            )
            edge_id = cur.fetchone()["edge_id"]
            conn.commit()
            print(
                f"[OK] 新增边 edge_id={edge_id} {from_node_id}->{to_node_id} "
                f"dep_type={dep_type} dep_maturity={dep_maturity}",
                file=sys.stderr,
            )
            return edge_id
        except Exception as e:
            conn.rollback()
            logger.error("add_edge失败: %s", e)
            return -1
        finally:
            conn.close()


def transition_build_status(node_id: int, to: str, db_path: str = None) -> bool:
    """
    转换 build_status 状态（5态单调推进）。
    返回：True=成功，False=失败
    转换规则（机械判定，裁定#178-183）：
    - planned → generated：允许（代码已生成）
    - generated → testing：允许（进入测试）
    - testing → stable：允许（测试通过）
    - stable → deprecated：允许（废弃）
    - deprecated → stable：禁止（不可复活）
    - 任何跳转：禁止
    """
    # 合法状态转换（5态单调推进）
    valid_transitions = {
        ("planned", "generated"),
        ("generated", "testing"),
        ("testing", "stable"),
        ("stable", "deprecated"),
    }

    with _db_write_lock(db_path=db_path, task="transition_build_status"):
        conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        try:
            row = conn.execute(SQL_SELECT_BUILD_STATUS_BY_NODE, (node_id,)).fetchone()
            if not row:
                print(f"ERROR: node_id={node_id} 不存在", file=sys.stderr)
                return False
            current = row["build_status"]
            if (current, to) not in valid_transitions:
                print(f"ERROR: 非法状态转换: {current} -> {to}（合法转换: {valid_transitions}）", file=sys.stderr)
                return False
            conn.execute(SQL_UPDATE_BUILD_STATUS, (to, node_id))
            conn.commit()
            print(f"[OK] node_id={node_id}: build_status {current} -> {to}", file=sys.stderr)
            return True
        except Exception as e:
            conn.rollback()
            logger.error("transition_build_status失败: %s", e)
            return False
        finally:
            conn.close()


_RE_MATURITY_HEADER = re.compile(r"^#\s*\[MATURITY\]\s+(\S+)")


def _read_maturity_header(file_path: Path) -> str | None:
    """读取文件头 [MATURITY] 声明值（前 30 行扫描）。

    返回：[MATURITY] 值（design/production），无头部时返回 None。

    ARCH-MM-002 裁定：[MATURITY] 文件头是 design_maturity 的 SSoT
    （2 态下声明物理存在性=客观事实）。
    transition_design_maturity 手动提升时 MUST 同步 header（gate 强制）。
    """
    try:
        with open(file_path, encoding="utf-8-sig", errors="ignore") as f:
            for i, line in enumerate(f):
                if i >= 30:
                    break
                m = _RE_MATURITY_HEADER.match(line.rstrip("\n"))
                if m:
                    return m.group(1).strip()
    except Exception:  # noqa: BLE001 — 单文件读取失败返回 None，gate 降级为不校验
        pass
    return None


def transition_design_maturity(node_id: int, to: str, db_path: str = None, force: bool = False) -> bool:
    """
    转换 design_maturity 状态（ARCH-MM-002 两档化：design → production）。
    返回：True=成功，False=失败
    转换规则（机械判定）：
    - design → production：允许（设计→生产，代码已实现）
    - 任何倒退（production→design）：禁止

    ARCH-MM-002 门禁（2026-07-23 治本）：
    [MATURITY] 文件头是 design_maturity 的 SSoT（2 态下声明物理存在性=客观事实）。
    transition_design_maturity 手动提升 DB design_maturity 时 MUST 确保
    [MATURITY] header == TO_MATURITY，否则硬阻断。
    逃生通道：force=True 跳过 header 校验（记录到 stderr 警告）。

    设计原理：ARCH-MM-002 两档化后，derive_design_maturity() 总是返回 "production"
    （物理存在=production），design 态只由此函数人工写入。手动 transition 时
    [MATURITY] header MUST 与 DB 一致，否则 header/DB 不一致。
    """
    # 合法状态转换（2态单调推进）
    valid_transitions = {
        ("design", "production"),
    }

    with _db_write_lock(db_path=db_path, task="transition_design_maturity"):
        conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        try:
            row = conn.execute(SQL_SELECT_DESIGN_MATURITY_BY_NODE, (node_id,)).fetchone()
            if not row:
                print(f"ERROR: node_id={node_id} 不存在", file=sys.stderr)
                return False
            current = row["design_maturity"]
            node_path = row["path"]
            if (current, to) not in valid_transitions:
                print(f"ERROR: 非法状态转换: {current} -> {to}（合法转换: {valid_transitions}）", file=sys.stderr)
                return False

            # ARCH-MM-002 gate: [MATURITY] header SSoT MUST == TO_MATURITY
            if node_path and not force:
                abs_path = REPO_ROOT / node_path
                if abs_path.exists():
                    header_maturity = _read_maturity_header(abs_path)
                    if header_maturity is not None and header_maturity != to:
                        print(
                            f"ERROR: [MATURITY] header '{header_maturity}' != TO_MATURITY '{to}'。"
                            f" 请先更新文件头 '# [MATURITY] {to}' 再执行 transition"
                            f"（ARCH-MM-002: header 是 SSoT, MUST 一致）。"
                            f" 逃生通道：--force",
                            file=sys.stderr,
                        )
                        return False
                # 文件不存在或无 [MATURITY] header：不阻断（无法校验）
            elif force and node_path:
                abs_path = REPO_ROOT / node_path
                header_maturity = _read_maturity_header(abs_path) if abs_path.exists() else None
                if header_maturity is not None and header_maturity != to:
                    print(
                        f"WARNING: --force 跳过 [MATURITY] header 校验"
                        f"（header='{header_maturity}' != TO_MATURITY='{to}'）"
                        f"—— 请尽快同步文件头以防 header/DB 不一致",
                        file=sys.stderr,
                    )

            conn.execute(SQL_UPDATE_DESIGN_MATURITY, (to, node_id))
            conn.commit()
            print(f"[OK] node_id={node_id}: design_maturity {current} -> {to}", file=sys.stderr)
            return True
        except Exception as e:
            conn.rollback()
            logger.error("transition_design_maturity失败: %s", e)
            return False
        finally:
            conn.close()


def _sync_panorama_after_transition(node_id: int) -> None:
    """状态转换后自动同步全景核心字段（ARCH-056）。

    查询 node 的 blueprint_id，如非空则调用 sync_module_panorama
    将新状态（design_maturity/build_status）同步到 dataflow/decision/blueprint。
    失败不阻断（warn-only，与 add_design_node 一致）。
    """
    try:
        conn = get_depgraph_pg_connection()
        try:
            row = conn.execute(SQL_SELECT_BLUEPRINT_ID_BY_NODE_ID, (node_id,)).fetchone()
        finally:
            conn.close()
        if not row:
            return
        blueprint_id = row["blueprint_id"] if isinstance(row, dict) else row[0]
        if not blueprint_id:
            return
        from sync_panorama_module import sync_module_panorama

        sync_module_panorama(blueprint_id)
    except Exception as e:
        print(f"[WARN] sync_panorama_module 失败（不阻断）: {e}", file=sys.stderr)


# --- design 节点删除审计（治本 RSK/RPT 误删，2026-07-31）---
_DESIGN_NODE_DELETE_AUDIT_DIR = REPO_ROOT / ".runtime" / "gate_audit"
_DESIGN_NODE_DELETE_AUDIT_FILE = "design_node_delete.jsonl"


def _audit_design_node_delete(
    *,
    op: str,
    node_id: int,
    design_maturity: str,
    build_status: str,
    path: str,
    blueprint_id: str = "",
    evidence: str = "",
    force: bool = False,
) -> None:
    """记录 design 节点删除/逃生操作到审计日志（非阻断）。

    治本 RSK/RPT 误删（2026-07-31）：所有 design 节点的删除/强制逃生操作
    MUST 落审计日志，便于事后追溯"谁在什么时候凭什么证据删了哪个 design 节点"。
    日志路径：.runtime/gate_audit/design_node_delete.jsonl
    """
    try:
        _DESIGN_NODE_DELETE_AUDIT_DIR.mkdir(parents=True, exist_ok=True)
        record = {
            "timestamp": int(time.time()),
            "session_id": os.environ.get("ZEPHYR_SESSION_ID", "cli-manual"),
            "op": op,
            "node_id": node_id,
            "blueprint_id": blueprint_id,
            "design_maturity": design_maturity,
            "build_status": build_status,
            "path": path,
            "evidence": evidence,
            "force": force,
        }
        with (_DESIGN_NODE_DELETE_AUDIT_DIR / _DESIGN_NODE_DELETE_AUDIT_FILE).open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:  # noqa: BLE001
        logger.debug("design_node_delete audit write failed (non-blocking)", exc_info=True)


def _cascade_anchor_hint(conn, node_ids: list[int], *, op: str) -> None:
    """S5 锚点级联提示（2026-08-14 幽灵锚点治本，AI-GIT-001）。

    删除/弃用节点时级联检查 battle_map_anchors 是否引用目标节点。
    target_id 双形态实证（存量 10 个幽灵锚点）：blueprint_id 文本
    （如 MOD-DAT-fred_ingest）与 node_id 数字字符串（如 '9162495'）并存，
    故候选键 = {str(node_id), blueprint_id}。

    命中不阻断主操作：stderr 提示 + 审计落盘
    .runtime/gate_audit/depgraph_anchor_cascade.jsonl，清理走
    ``python scripts/governance/apply_battle_map.py --remove-anchor --anchor-id <id>``
    （统筹登记范围，本函数只提示不代删）。fail-open：提示失败不阻断主操作。
    """
    try:
        if not node_ids:
            return
        rows = conn.execute(SQL_CASCADE_ANCHOR_NODE_LOOKUP, (list(node_ids),)).fetchall()
        candidates: set[str] = set()
        for r in rows:
            candidates.add(str(r["node_id"]))
            bp = (r.get("blueprint_id") or "").strip()
            if bp:
                candidates.add(bp)
        if not candidates:
            return
        anchors = conn.execute(SQL_CASCADE_ANCHOR_HINT_QUERY, (sorted(candidates),)).fetchall()
        if not anchors:
            return
        print(
            f"[S5-CASCADE] battle_map_anchors 级联提示（op={op}）：命中 {len(anchors)} 个锚点——",
            file=sys.stderr,
        )
        for a in anchors:
            print(
                f"  anchor_id={a['anchor_id']} step={a['step_id']} target={a['target_id']} role={a['target_role']}",
                file=sys.stderr,
            )
        print(
            "  处置（统筹登记范围）：python scripts/governance/apply_battle_map.py --remove-anchor --anchor-id <id>",
            file=sys.stderr,
        )
        # 审计落盘（非阻断）
        try:
            _DESIGN_NODE_DELETE_AUDIT_DIR.mkdir(parents=True, exist_ok=True)
            record = {
                "timestamp": int(time.time()),
                "session_id": os.environ.get("ZEPHYR_SESSION_ID", "cli-manual"),
                "op": op,
                "node_ids": list(node_ids),
                "anchors": [dict(a) for a in anchors],
            }
            with (_DESIGN_NODE_DELETE_AUDIT_DIR / "depgraph_anchor_cascade.jsonl").open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception:  # noqa: BLE001
            logger.debug("anchor cascade audit write failed (non-blocking)", exc_info=True)
    except Exception:  # noqa: BLE001 — 级联提示 fail-open，永不阻断主操作
        logger.debug("cascade anchor hint failed (non-blocking)", exc_info=True)


def remove_design_node(node_id: int, db_path: str = None, design_evidence: str = None) -> bool:
    """
    删除设计态节点（软删除）。
    返回：True=成功，False=失败
    流程：
    1. RULE-THREE 三步审判（登记检查/重复检查/功能价值检查）
    2. RULE-DESIGN-EVIDENCE 双源门禁：design_evidence 必填（设计文档引用，
       如 "11-D-RISK §1.4 RK-09 P0核心"），无则硬阻断。证据落审计日志。
       治本 RSK/RPT 误删（2026-07-31）：堵住"忘了查文档就 CLI 删"的后门。
    3. 通过后软删除（build_status='deprecated'）
    4. 拒绝硬删除（DELETE FROM nodes）
    """
    with _db_write_lock(db_path=db_path, task="remove_design_node"):
        conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        try:
            # STEP 1: 登记检查 - 节点是否存在
            row = conn.execute(SQL_SELECT_NODE_DETAIL_BY_ID, (node_id,)).fetchone()
            if not row:
                print(f"ERROR: node_id={node_id} 不存在", file=sys.stderr)
                return False
            if row["design_maturity"] != "design":
                print(
                    f"ERROR: node_id={node_id} design_maturity={row['design_maturity']}（非设计态节点，禁止删除）",
                    file=sys.stderr,
                )
                return False

            # STEP 2: RULE-DESIGN-EVIDENCE 双源门禁（治本 RSK/RPT 误删，2026-07-31）
            if not design_evidence or not design_evidence.strip():
                print(
                    f"ERROR: node_id={node_id} blueprint_id={row.get('blueprint_id') or ''}"
                    f" 缺少 design_evidence —— 删除 design 节点 MUST 声明已查设计文档的证据"
                    f'（如 "11-D-RISK §1.4 RK-09 P0核心"）。\n'
                    f'  CLI: --remove-design-node {node_id} --design-evidence "<文档引用>"\n'
                    f'  治本：堵住"忘了查文档就 CLI 删"的后门（RSK/RPT 误删事故根因）',
                    file=sys.stderr,
                )
                return False

            # STEP 3: 重复检查 - 是否有其他同path节点
            duplicates = conn.execute(
                "SELECT COUNT(*) FROM nodes WHERE path=%s AND node_id!=%s", (row["path"], node_id)
            ).fetchone()["count"]

            # STEP 4: 功能价值检查 - 检查是否有边引用此节点
            edge_count = conn.execute(SQL_COUNT_EDGES_BY_NODE, (node_id, node_id)).fetchone()["count"]
            if edge_count > 0:
                print(f"WARNING: node_id={node_id} 有{edge_count}条边引用，将先删除边", file=sys.stderr)
                conn.execute(SQL_DELETE_EDGES_BY_NODE, (node_id, node_id))

            # 审计：双源证明落盘（软删除前，便于事后追溯）
            _audit_design_node_delete(
                op="remove_design_node",
                node_id=node_id,
                design_maturity=row["design_maturity"],
                build_status=row["build_status"],
                path=row.get("path") or "",
                blueprint_id=row.get("blueprint_id") or "",
                evidence=design_evidence.strip(),
                force=False,
            )

            # S5 锚点级联提示（非阻断）
            _cascade_anchor_hint(conn, [node_id], op="remove_design_node")

            # 软删除（build_status='deprecated'）
            conn.execute(SQL_DEPRECATE_NODE, (node_id,))
            conn.commit()
            print(
                f"[OK] node_id={node_id} blueprint_id={row.get('blueprint_id') or ''}: "
                f"软删除（build_status='deprecated'）evidence={design_evidence.strip()}",
                file=sys.stderr,
            )
            return True
        except Exception as e:
            conn.rollback()
            logger.error("remove_design_node失败: %s", e)
            return False
        finally:
            conn.close()


def deprecate_node(node_id: int, db_path: str = None, force: bool = False) -> bool:
    """
    软废弃任意节点（含 production）——专用于孤儿节点清理。

    与 remove_design_node 的区别：
    - remove_design_node 仅限 design_maturity='design' 节点（带 design_evidence 双源门禁）
    - deprecate_node 不限制 design_maturity，绕过 5 态状态机

    使用场景：物理文件已删除的孤儿节点（如生成器删除后遗留的 proxy 文件、
    真源归一后的废弃副本），需要将 depgraph 节点标记为 deprecated 以保持
    depgraph 与磁盘一致。

    治本（2026-07-31，RSK/RPT 误删）：design_maturity='design' 节点默认拒绝——
    design 节点必须走正门 remove_design_node（带 design_evidence 双源门禁）。
    --force 逃生通道用于合法 design 垃圾节点清理（如 MOD-TEST 类测试残留），
    落审计日志。

    流程：
    1. 验证节点存在
    2. 验证当前 build_status 不是已 deprecated（幂等保护）
    3. RULE-DESIGN-GATE 双源门禁：design 节点禁止走后门（--force 逃生+审计）
    4. 检查边引用，有则警告（不阻断）
    5. 诊断警告（P2 治本 2026-06-29，不阻断）：
       a. 物理文件存在性——文件仍存在则警告（可能误废弃）
       b. path/file_path 一致性——不一致则警告（可能漂移）
    6. 软删除（build_status='deprecated'）
    """
    with _db_write_lock(db_path=db_path, task="deprecate_node"):
        conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        try:
            row = conn.execute(
                "SELECT node_id, path, file_path, blueprint_id, design_maturity, build_status FROM nodes WHERE node_id=%s",
                (node_id,),
            ).fetchone()
            if not row:
                print(f"ERROR: node_id={node_id} 不存在", file=sys.stderr)
                return False
            if row["build_status"] == "deprecated":
                print(f"[SKIP] node_id={node_id} 已是 deprecated（幂等）", file=sys.stderr)
                return True

            # RULE-DESIGN-GATE 双源门禁（治本 RSK/RPT 误删，2026-07-31）
            # design 节点禁止走 --deprecate-node 后门——必须走正门 remove_design_node
            # （带 design_evidence 双源门禁）。--force 逃生用于合法 design 垃圾节点
            # （如 MOD-TEST 类测试残留），落审计日志。
            if row["design_maturity"] == "design" and not force:
                print(
                    f"ERROR: node_id={node_id} blueprint_id={row.get('blueprint_id') or ''}"
                    f" design_maturity=design —— design 节点禁止走 --deprecate-node 后门"
                    f"（RSK/RPT 误删事故根因）。\n"
                    f"  正门：python scripts/governance/apply_depgraph.py --remove-design-node {node_id}"
                    f' --design-evidence "<设计文档引用>"\n'
                    f"  逃生（仅合法 design 垃圾节点如 MOD-TEST）：加 --force（落审计日志）",
                    file=sys.stderr,
                )
                return False

            # 检查边引用
            edge_count = conn.execute(SQL_COUNT_EDGES_BY_NODE, (node_id, node_id)).fetchone()["count"]
            if edge_count > 0:
                print(f"WARNING: node_id={node_id} 有{edge_count}条边引用（软废弃不删边）", file=sys.stderr)

            # 诊断警告（P2 治本 2026-06-29）：物理文件存在性 + path/file_path 一致性
            # 不阻断——deprecate_node 的预期场景就是孤儿清理（文件已删除），
            # 但若文件仍存在或 path/file_path 漂移，应提示操作者核查（防误废弃 + 防漂移隐藏）
            _fp = row.get("file_path") or ""
            _pth = row.get("path") or ""
            if _fp:
                _phys = REPO_ROOT / _fp
                if _phys.exists():
                    print(
                        f"WARNING: node_id={node_id} 物理文件仍存在: {_phys} —— "
                        f"确认是否真要废弃（孤儿清理预期文件已删除）",
                        file=sys.stderr,
                    )
            if _pth and _fp and _pth != _fp:
                print(
                    f"WARNING: node_id={node_id} path({_pth}) != file_path({_fp}) —— "
                    f"不一致（可能漂移，cmd_update_path 已治本同步，此节点为历史遗留）",
                    file=sys.stderr,
                )

            # 审计：design 节点走后门 force 逃生（治本 RSK/RPT 误删）
            if row["design_maturity"] == "design" and force:
                _audit_design_node_delete(
                    op="deprecate_design_force",
                    node_id=node_id,
                    design_maturity=row["design_maturity"],
                    build_status=row["build_status"],
                    path=row.get("path") or "",
                    blueprint_id=row.get("blueprint_id") or "",
                    force=True,
                )

            # S5 锚点级联提示（非阻断）
            _cascade_anchor_hint(conn, [node_id], op="deprecate_node")

            conn.execute(SQL_DEPRECATE_NODE, (node_id,))
            conn.commit()
            print(
                f"[OK] node_id={node_id} file_path={row['file_path']} design_maturity={row['design_maturity']}: "
                f"软废弃（build_status {row['build_status']} -> deprecated）",
                file=sys.stderr,
            )
            return True
        except Exception as e:
            conn.rollback()
            logger.error("deprecate_node失败: %s", e)
            return False
        finally:
            conn.close()


def mark_blueprint_invalid(blueprint_id: str, reason: str, db_path: str = None) -> bool:
    """
    裁定#208 B5: 将指定 blueprint_id 标记为 invalid（软标记，不删除节点，保留可追溯链）。

    用途：阶段 C/D 重编号时先标记旧 ID invalid，再插入新 ID，保留追溯链。
    操作：nodes.blueprint_id_invalid=1 + gate_reason 写入 reason。
    返回：True=成功，False=失败
    """
    if not blueprint_id:
        print("ERROR: blueprint_id 不能为空", file=sys.stderr)
        return False
    with _db_write_lock(db_path=db_path, task="mark_blueprint_invalid"):
        conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        try:
            rows = conn.execute(SQL_SELECT_NODES_BY_BLUEPRINT, (blueprint_id,)).fetchall()
            if not rows:
                print(f"ERROR: blueprint_id={blueprint_id} 未匹配任何节点", file=sys.stderr)
                return False
            for node_id, _path in rows:
                conn.execute(
                    "UPDATE nodes SET blueprint_id_invalid=1, gate_reason=%s WHERE node_id=%s",
                    (reason, node_id),
                )
            conn.commit()
            print(
                f"[OK] blueprint_id={blueprint_id}: 标记 {len(rows)} 节点 invalid（reason={reason}）",
                file=sys.stderr,
            )
            return True
        except Exception as e:
            conn.rollback()
            logger.error("mark_blueprint_invalid失败: %s", e)
            return False
        finally:
            conn.close()


def cmd_clear_invalid_flag(blueprint_id: str, dry_run: bool = False, db_path: str = None) -> int:
    """清除指定 blueprint_id 的 blueprint_id_invalid 标志（inverse of mark_blueprint_invalid）。

    治本（2026-08-03）：4 个 MOD-CFG_* 节点 blueprint_id 格式合规（is_valid_module_id pass），
    但 blueprint_id_invalid=1 是旧校验规则残留。本函数用权威真源 is_valid_module_id 复核后清标志。

    安全保证：
    - blueprint_id 必须通过 is_valid_module_id（若仍不合规则拒绝清标志，防止误清真正无效的 ID）
    - _db_write_lock 互斥保护
    - dry_run 只读不写

    返回受影响行数，-1=失败。
    """
    ok, reason = _validate_bp_id_format(blueprint_id)
    if not ok:
        print(
            f"ERROR: blueprint_id '{blueprint_id}' 格式不合规：{reason}\n"
            f"拒绝清标志——invalid 标志存在是有理由的。请先 rename 为合规 ID。",
            file=sys.stderr,
        )
        return -1
    own_conn = True
    with _db_write_lock(db_path=db_path, task="clear_invalid_flag"):
        conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        try:
            row = conn.execute(SQL_COUNT_NODES_BY_BLUEPRINT_ID, (blueprint_id,)).fetchone()
            cnt = row["c"] if row else 0
            mode = "[DRY RUN]" if dry_run else "[OK]"
            print(f"{mode} clear_invalid_flag: blueprint_id={blueprint_id} ({cnt} 节点)", file=sys.stderr)
            if cnt == 0:
                print(f"  WARNING: blueprint_id={blueprint_id} 未匹配任何节点", file=sys.stderr)
                return 0
            if dry_run:
                return cnt
            conn.execute(SQL_CLEAR_INVALID_FLAG_BY_BP, (blueprint_id,))
            conn.commit()
            print(f"  [OK] {cnt} 节点 blueprint_id_invalid 已清除 (0)", file=sys.stderr)
            return cnt
        except Exception as e:
            conn.rollback()
            logger.error("cmd_clear_invalid_flag失败: %s", e)
            return -1
        finally:
            conn.close()


def cmd_clear_blueprint_id(path: str, dry_run: bool = False, db_path: str = None) -> int:
    """按 path 清空 blueprint_id（设 NULL），用于 infra_id 误存为 blueprint_id 的治本清理。

    治本（2026-08-03）：4 个 INFRA-DB-* 节点的 blueprint_id 存的是 infra_id（基础设施资源
    目录 ID，INFRA-{TYPE}-{NNN}），不是 module_id（裁定#208 仅接受 MOD-/SH-）。这些是物理
    数据库资源，不是软件模块，没有 module_id。清空 blueprint_id 后，节点仍由 path 唯一标识
    （裁定#209 Stage 2: path 是稳定 PK）。belongs_to 同步清空（这些节点无归属模块）。

    安全保证：
    - path 必须命中一个节点
    - _db_write_lock 互斥保护
    - dry_run 只读不写

    返回受影响行数，-1=失败。
    """
    own_conn = True
    with _db_write_lock(db_path=db_path, task="clear_blueprint_id"):
        conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        try:
            row = conn.execute(SQL_SELECT_NODE_BP_BY_PATH, (path,)).fetchone()
            if not row:
                print(f"ERROR: path='{path}' 在 nodes 表中不存在", file=sys.stderr)
                return -1
            old_bp = row["blueprint_id"] or "(空)"
            mode = "[DRY RUN]" if dry_run else "[OK]"
            print(f"{mode} clear_blueprint_id: path={path}", file=sys.stderr)
            print(f"  blueprint_id: '{old_bp}' -> NULL", file=sys.stderr)
            if dry_run:
                return 1
            conn.execute(SQL_CLEAR_BLUEPRINT_ID_BY_PATH, (path,))
            # 同步清 nodes_metadata.blueprint_id
            conn.execute(
                SQL_CLEAR_NODES_METADATA_BP_BY_PATH,
                (datetime.datetime.now().isoformat(), path),
            )
            conn.commit()
            print("  [OK] nodes + nodes_metadata blueprint_id 已清空", file=sys.stderr)
            return 1
        except Exception as e:
            conn.rollback()
            logger.error("cmd_clear_blueprint_id失败: %s", e)
            return -1
        finally:
            conn.close()


def delete_design_edge(edge_id: int, db_path: str = None) -> bool:
    """
    删除设计态边（硬删除，因边无软删除语义）。
    返回：True=成功，False=失败
    校验：
    - edge_id 必须存在
    - dep_maturity 必须为 'design'（禁止删除运营态边）
    """
    with _db_write_lock(db_path=db_path, task="delete_design_edge"):
        conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        try:
            row = conn.execute(
                "SELECT edge_id, from_node_id, to_node_id, dep_maturity FROM edges WHERE edge_id=%s", (edge_id,)
            ).fetchone()
            if not row:
                print(f"ERROR: edge_id={edge_id} 不存在", file=sys.stderr)
                return False
            if row["dep_maturity"] != "design":
                print(
                    f"ERROR: edge_id={edge_id} dep_maturity={row['dep_maturity']}（非设计态边，禁止删除）",
                    file=sys.stderr,
                )
                return False
            conn.execute(SQL_DELETE_EDGE_BY_ID, (edge_id,))
            conn.commit()
            print(
                f"[OK] 删除设计态边 edge_id={edge_id} ({row['from_node_id']}->{row['to_node_id']})",
                file=sys.stderr,
            )
            return True
        except Exception as e:
            conn.rollback()
            logger.error("delete_design_edge失败: %s", e)
            return False
        finally:
            conn.close()


def delete_edge(edge_id: int, db_path: str = None) -> bool:
    """
    删除边（通用，不限 dep_maturity，支持删除任意边）。
    返回：True=成功，False=失败
    与 delete_design_edge 的差异：不校验 dep_maturity（允许删除 design/active 任意边）
    用途：add_edge 的对偶命令，支持单条回滚（production 边无法用 --delete-design-edge 删除）
    """
    with _db_write_lock(db_path=db_path, task="delete_edge"):
        conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        try:
            row = conn.execute(
                "SELECT edge_id, from_node_id, to_node_id, dep_type, dep_maturity FROM edges WHERE edge_id=%s",
                (edge_id,),
            ).fetchone()
            if not row:
                print(f"ERROR: edge_id={edge_id} 不存在", file=sys.stderr)
                return False
            conn.execute(SQL_DELETE_EDGE_BY_ID, (edge_id,))
            conn.commit()
            print(
                f"[OK] 删除边 edge_id={edge_id} ({row['from_node_id']}->{row['to_node_id']} dep_type={row['dep_type']} dep_maturity={row['dep_maturity']})",
                file=sys.stderr,
            )
            return True
        except Exception as e:
            conn.rollback()
            logger.error("delete_edge失败: %s", e)
            return False
        finally:
            conn.close()


def delete_blueprint_link(blueprint_id: str, db_path: str = None) -> bool:
    """
    删除 blueprint_links 表中的记录（用于清理悬空引用）。
    返回：True=成功，False=失败
    校验：blueprint_id 必须在 blueprint_links 中存在
    用途：F35 蓝图悬空处理（清理已删除蓝图的悬空引用）
    """
    with _db_write_lock(db_path=db_path, task="delete_blueprint_link"):
        conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        try:
            row = conn.execute(
                "SELECT blueprint_id FROM blueprint_links WHERE blueprint_id=%s", (blueprint_id,)
            ).fetchone()
            if not row:
                print(f"ERROR: blueprint_id={blueprint_id} 在 blueprint_links 中不存在", file=sys.stderr)
                return False
            conn.execute(SQL_DELETE_BLUEPRINT_LINK, (blueprint_id,))
            conn.commit()
            print(f"[OK] 删除 blueprint_link blueprint_id={blueprint_id}", file=sys.stderr)
            return True
        except Exception as e:
            conn.rollback()
            logger.error("delete_blueprint_link失败: %s", e)
            return False
        finally:
            conn.close()


def delete_constraint(constraint_id: str, db_path: str = None) -> bool:
    """
    删除 arch_constraints 表中的约束记录（用于清理孤儿约束/历史脏数据）。
    返回：True=成功，False=失败
    校验：constraint_id 必须在 arch_constraints 中存在
    用途：清除生成代码已不存在的孤儿约束（如 stability 类型历史残留），
         以及 YAML 真源已删除但 UPSERT 未清理的陈旧约束。
    注意：检测违规（constraint_id IS NULL）不由此命令删除，由 check_all() 重建。
    """
    with _db_write_lock(db_path=db_path, task="delete_constraint"):
        conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        try:
            row = conn.execute(
                SQL_SELECT_CONSTRAINT_BY_ID,
                (constraint_id,),
            ).fetchone()
            if not row:
                print(f"ERROR: constraint_id={constraint_id} 不存在", file=sys.stderr)
                return False
            conn.execute(SQL_DELETE_CONSTRAINT, (constraint_id,))
            conn.commit()
            print(
                f"[OK] 删除约束 constraint_id={constraint_id} (name={row['name']} type={row['constraint_type']})",
                file=sys.stderr,
            )
            return True
        except Exception as e:
            conn.rollback()
            logger.error("delete_constraint失败: %s", e)
            return False
        finally:
            conn.close()


def cmd_cleanup_orphan_nodes(dry_run: bool = False, db_path: str = None) -> int:
    """
    清理幽灵节点：删除 nodes 表中 path 在磁盘上不存在的 node（对称漂移修复，P1-DEP）。
    对标 cmd_cleanup_orphan_edges（清理孤儿边）。
    返回：删除的节点数，-1=失败。

    注意：已由 backup_pg_architecture() 自动 PG 备份（trae_054 v1.6.0 STEP0，写入后事件触发，非 git commit）。
    """
    project_root = REPO_ROOT
    with _db_write_lock(db_path=db_path, task="cleanup_orphan_nodes"):
        conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        pass  # P2 PG: PRAGMA 已删除（PG 不需要）
        pass  # P2 PG: PRAGMA 已删除（PG 不需要）
        try:
            # 治本(2026-07-04): 跳过 design_maturity='design' 的设计态节点
            # 设计态节点是"计划中"的节点，path在磁盘上不存在是正常的（尚未施工），
            # 不应被当作ghost清理。否则reconciler的ghost auto_clean会误删所有设计态节点。
            all_nodes = conn.execute(
                "SELECT node_id, path FROM nodes WHERE path IS NOT NULL AND path != '' "
                "AND (design_maturity != 'design' OR design_maturity IS NULL)"
            ).fetchall()

            ghost_node_ids: list[tuple[str, str]] = []
            for r in all_nodes:
                nid = r["node_id"]
                path = r["path"]
                full_path = Path(project_root) / path
                if not full_path.exists():
                    ghost_node_ids.append((nid, path))

            if not ghost_node_ids:
                print("[OK] 无幽灵节点，无需清理")
                return EXIT_PASS
            if dry_run:
                print(f"[DRY RUN] 将删除 {len(ghost_node_ids)} 个幽灵节点（磁盘不存在但 depgraph 保留）:")
                for nid, path in ghost_node_ids[:10]:
                    print(f"  node_id={nid}: {path}")
                if len(ghost_node_ids) > 10:
                    print(f"  ... 及其他 {len(ghost_node_ids) - 10} 个")
                return len(ghost_node_ids)

            # 先删除引用这些 node 的 edges（避免外键残留孤儿边）
            for nid, _ in ghost_node_ids:
                conn.execute(
                    "DELETE FROM edges WHERE from_node_id = %s OR to_node_id = %s",
                    (nid, nid),
                )
            # 再删除 ghost nodes
            for nid, _ in ghost_node_ids:
                conn.execute(SQL_DELETE_NODE_BY_ID, (nid,))
            conn.commit()
            print(f"[OK] 删除 {len(ghost_node_ids)} 个幽灵节点（及关联 edges）")
            return len(ghost_node_ids)
        except Exception as e:
            conn.rollback()
            logger.error("cleanup_orphan_nodes失败: %s", e)
            return -1
        finally:
            conn.close()


def cmd_cleanup_orphan_edges(dry_run: bool = False, db_path: str = None) -> int:
    """
    清理孤儿边：删除 edges 表中引用了不存在 node 的边（from_node_id 或 to_node_id 在 nodes 表中不存在）。
    返回：删除的边数，-1=失败
    """
    with _db_write_lock(db_path=db_path, task="cleanup_orphan_edges"):
        conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        pass  # P2 PG: PRAGMA 已删除（PG 不需要）
        pass  # P2 PG: PRAGMA 已删除（PG 不需要）
        try:
            orphan_count = conn.execute(SQL_COUNT_ORPHAN_EDGES).fetchone()["count"]

            if orphan_count == 0:
                print("[OK] 无孤儿边，无需清理")
                return EXIT_PASS
            if dry_run:
                print(f"[DRY RUN] 将删除 {orphan_count} 条孤儿边")
                samples = conn.execute(
                    """SELECT edge_id, from_node_id, to_node_id, dep_type
                       FROM edges
                       WHERE from_node_id NOT IN (SELECT node_id FROM nodes)
                          OR to_node_id NOT IN (SELECT node_id FROM nodes)
                       LIMIT 10"""
                ).fetchall()
                for s in samples:
                    print(f"  edge_id={s['edge_id']}: {s['from_node_id']}->{s['to_node_id']} ({s['dep_type']})")
                return orphan_count

            conn.execute(
                """DELETE FROM edges
                   WHERE from_node_id NOT IN (SELECT node_id FROM nodes)
                      OR to_node_id NOT IN (SELECT node_id FROM nodes)"""
            )
            conn.commit()
            print(f"[OK] 删除 {orphan_count} 条孤儿边")
            return orphan_count
        except Exception as e:
            conn.rollback()
            logger.error("cleanup_orphan_edges失败: %s", e)
            return -1
        finally:
            conn.close()


def update_edge_type(edge_id: int, new_dep_type: str, db_path: str = None) -> bool:
    """
    修改边的 dep_type（依赖类型）。
    返回：True=成功，False=失败
    校验：
    - edge_id 必须存在
    - new_dep_type 必须为合法值（contract/event/runtime/data/import_depends/test_depends/config_depends）
    用途：§8.3 DIP裁定——F1→F3从import_depends改为contract，F1→F14改为event
    """
    # update_edge_type dep_type 业务子集（与 add_edge 一致，含 legacy 短名）
    # 非全量词表副本——全量真源为 dep_type_vocabulary.yaml（PS-VOC-034）
    valid_types = {  # noqa: gate-vocab  业务子集校验，非词表硬编码
        "contract",
        "event",
        "runtime",
        "data",
        "import_depends",
        "test_depends",
        "config_depends",
    }
    if new_dep_type not in valid_types:
        print(
            f"ERROR: dep_type '{new_dep_type}' 不合法（合法值: {valid_types}）",
            file=sys.stderr,
        )
        return False

    with _db_write_lock(db_path=db_path, task="update_edge_type"):
        conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        try:
            row = conn.execute(
                "SELECT edge_id, from_node_id, to_node_id, dep_type FROM edges WHERE edge_id=%s",
                (edge_id,),
            ).fetchone()
            if not row:
                print(f"ERROR: edge_id={edge_id} 不存在", file=sys.stderr)
                return False
            old_type = row["dep_type"]
            conn.execute(SQL_UPDATE_EDGE_DEP_TYPE, (new_dep_type, edge_id))
            conn.commit()
            print(
                f"[OK] edge_id={edge_id}: dep_type {old_type} -> {new_dep_type} ({row['from_node_id']}->{row['to_node_id']})",
                file=sys.stderr,
            )
            return True
        except Exception as e:
            conn.rollback()
            logger.error("update_edge_type失败: %s", e)
            return False
        finally:
            conn.close()


# ===== F5 合规豁免：域/路径/依赖迁移命令（ARCH-CAP-005 抽屉式扩展）=====


def _validate_domain_naming(
    domain_id: str,
    domain_name: str,
    db_path: str = None,
) -> tuple[list[str], list[str]]:
    """建域门禁：校验域ID是否符合 domain_naming_rules 表中的命名规则。

    裁定#204 / OPS-2026062610 预防根因：命名规则原仅存 Markdown，AI 不查阅导致
    D-XXX_YYY 形式域名产生。此函数从 DB 读取规则并程序化校验。

    返回: (errors: list[str], warnings: list[str])
    如果 domain_naming_rules 表不存在，返回 ([], [])（跳过校验，向后兼容）。
    """
    errors: list[str] = []
    warnings: list[str] = []

    try:
        conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        cur = conn.execute(SQL_SELECT_DOMAIN_NAMING_RULES)
        rules = {r["rule_id"]: r["severity"] for r in cur.fetchall()}
        if not rules:
            conn.close()
            return errors, warnings

        cur = conn.execute(SQL_SELECT_ALL_DOMAIN_IDS)
        existing_ids = {r["domain_id"] for r in cur.fetchall()}
        conn.close()
    except psycopg2.Error as e:
        # domain_naming_rules 表不存在——跳过校验（向后兼容）
        logger.debug("validate_domain_naming_rules: domains 表查询失败(%s)，跳过命名校验", e)
        return errors, warnings

    # NR-001: 无父子前缀——第一段匹配已存在域
    if "NR-001" in rules and "_" in domain_id:
        first_segment = domain_id.split("_")[0]
        if first_segment != domain_id and first_segment in existing_ids:
            msg = (
                f"NR-001(无父子前缀): 域ID '{domain_id}' 第一段 '{first_segment}' "
                f"匹配已存在域，暗示父子关系（违反'所有域平级'铁律）"
            )
            (errors if rules["NR-001"] == "error" else warnings).append(msg)

    # NR-002: 全大写下划线命名——regex 校验
    # 真源统一：复用 validate_module_id_naming.DOMAIN_ID_RE（消除硬编码正则分裂）
    if "NR-002" in rules:
        if not _DOMAIN_ID_RE.match(domain_id):
            msg = (
                f"NR-002(全大写下划线命名): 域ID '{domain_id}' 不匹配 "
                f"{_DOMAIN_ID_RE.pattern}（禁止小写字母/多余连字符）"
            )
            (errors if rules["NR-002"] == "error" else warnings).append(msg)

    # NR-003: 语义独立性——以已存在域+下划线为前缀
    if "NR-003" in rules:
        for existing_id in existing_ids:
            if domain_id.startswith(existing_id + "_"):
                msg = f"NR-003(语义独立性): 域ID '{domain_id}' 以已存在域 '{existing_id}_' 为前缀，依赖其他域才能理解"
                (errors if rules["NR-003"] == "error" else warnings).append(msg)
                break

    # NR-004/NR-005: warning 级，无法程序化精确判定语义，留作人工审查参考

    return errors, warnings


def cmd_insert_domain(
    domain_id: str,
    domain_name: str,
    domain_group: str,
    layer_id: str,
    ssot_path: str,
    max_modules: int = 150,
    description: str = "",
    dry_run: bool = False,
    db_path: str = None,
    conn=None,
) -> bool:
    """INSERT 新域到 domains 表（ARCH-CAP-005 抽屉式扩展）。

    新增域只需 INSERT domains 表，不修改生成器代码。
    如果提供 conn 参数，使用该连接（不 commit/close）——用于 cmd_batch 统一事务。
    返回：True=成功，False=失败
    """
    # 深度防御：函数层格式校验（防 cmd_batch 等绕过 main 的 _validate_domain_naming 直接调用）
    # 真源：is_valid_domain_id（与 NR-002 共用 DOMAIN_ID_RE，消除正则分裂）
    ok, reason = _validate_domain_id_format(domain_id)
    if not ok:
        print(f"ERROR: domain_id '{domain_id}' 格式不合规：{reason}", file=sys.stderr)
        return False
    own_conn = conn is None
    with _optional_db_lock(own_conn, task="cmd_insert_domain", db_path=db_path):
        if own_conn:
            conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        try:
            existing = conn.execute(SQL_SELECT_DOMAIN_ID_BY_DOMAIN_ID, (domain_id,)).fetchone()
            if existing:
                print(f"ERROR: domain_id '{domain_id}' 已存在", file=sys.stderr)
                return False

            now = datetime.datetime.now().isoformat()
            if dry_run:
                print(
                    f"[DRY RUN] 将 INSERT 域 {domain_id} ({domain_name}) layer={layer_id} ssot_path={ssot_path} max_modules={max_modules}",
                    file=sys.stderr,
                )
                return True

            conn.execute(
                SQL_INSERT_DOMAIN,
                (domain_id, domain_name, domain_group, description, ssot_path, max_modules, now, now, layer_id),
            )
            if own_conn:
                conn.commit()
            print(f"[OK] INSERT 域 {domain_id} ({domain_name}) layer={layer_id}", file=sys.stderr)
            return True
        except Exception as e:
            if own_conn:
                conn.rollback()
            logger.error("cmd_insert_domain失败: %s", e)
            return False
        finally:
            if own_conn:
                conn.close()


def cmd_update_domain_id(
    module_id: str,
    new_domain_id: str,
    dry_run: bool = False,
    db_path: str = None,
    conn=None,
    force_cross_domain: bool = False,
) -> int:
    """UPDATE 模块的 domain_id（域拆分时迁移模块归属）。

    按 belongs_to 或 blueprint_id 匹配节点。
    如果提供 conn 参数，使用该连接（不 commit/close）——用于 cmd_batch 统一事务。
    返回：受影响行数，-1=失败
    """
    own_conn = conn is None
    with _optional_db_lock(own_conn, task="cmd_update_domain_id", db_path=db_path):
        if own_conn:
            conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        try:
            domain = conn.execute(SQL_SELECT_DOMAIN_ID_BY_DOMAIN_ID, (new_domain_id,)).fetchone()
            if not domain:
                print(f"ERROR: new_domain_id '{new_domain_id}' 不在 domains 表中", file=sys.stderr)
                return -1

            rows = conn.execute(
                "SELECT node_id, path, domain_id FROM nodes WHERE belongs_to=%s OR blueprint_id=%s",
                (module_id, module_id),
            ).fetchall()
            if not rows:
                print(f"ERROR: module_id '{module_id}' 未找到匹配节点", file=sys.stderr)
                return -1

            # 跨域共享防御检查（附录D裁定3）
            domain_ids_in_match = set(r["domain_id"] for r in rows)
            if len(domain_ids_in_match) > 1 and not force_cross_domain:
                print(
                    f"WARNING: module_id '{module_id}' 匹配 {len(rows)} 个节点，分布在 {len(domain_ids_in_match)} 个域: {domain_ids_in_match}",
                    file=sys.stderr,
                )
                print(
                    "  跨域匹配可能导致误迁。使用 --force-cross-domain 确认，或改用 --migrate-nodes 按节点精确迁移。",
                    file=sys.stderr,
                )
                return -1

            if dry_run:
                for r in rows:
                    print(
                        f"[DRY RUN] 将 UPDATE node_id={r['node_id']} domain_id: {r['domain_id']} -> {new_domain_id} (path={r['path']})",
                        file=sys.stderr,
                    )
                return len(rows)

            cur = conn.execute(
                "UPDATE nodes SET domain_id=%s WHERE belongs_to=%s OR blueprint_id=%s",
                (new_domain_id, module_id, module_id),
            )
            if own_conn:
                conn.commit()
            print(f"[OK] UPDATE {cur.rowcount} 个节点 domain_id -> {new_domain_id}", file=sys.stderr)
            return cur.rowcount
        except Exception as e:
            if own_conn:
                conn.rollback()
            logger.error("cmd_update_domain_id失败: %s", e)
            return -1
        finally:
            if own_conn:
                conn.close()


# 改名值扫描兜底排除表（裁定#207 R1）：规则示例/系统表/审计日志的 D-SIGNAL* 残留有意保留
_RENAME_SCAN_EXCLUDE_TABLES = {"domain_naming_rules", "_schema_version", "governance_audit_logs"}

# 裁定#204 改名的 4 个域映射（old_id → new_id）
# D-SIGNAL 必须最后处理（它是其他3个旧ID的前缀）
_RENAME_MAP_204 = {
    "D-SIGNAL_ASHARE": "D_ASHARE_SIGNAL",
    "D-SIGNAL_FUNDAMENTAL": "D_FUNDAMENTAL_SIGNAL",
    "D-SIGNAL_QUALITY": "D_SIGQC",
    "D-SIGNAL": "D_SIGLEGACY",
}

# 值扫描兜底排除列（裁定#207 R1）：由专门步骤处理的列不参与子串REPLACE
# - blueprint_id: B6 --propagate-rename 精确值映射（禁止子串REPLACE，裁定#207 R1）
# - path / blueprint_path: 阶段D 节点路径改名传播（重新编号，需保留原序号信息）
_RENAME_SCAN_EXCLUDE_COLUMNS = {"blueprint_id", "path", "blueprint_path"}


def _scan_replace_all_text_columns(
    c,
    old_id: str,
    new_id: str,
    dry_run: bool = False,
    mode: str = "[OK]",
    exclude_columns: set[str] | None = None,
) -> int:
    """值扫描兜底（裁定#207 R1 B1）：扫描所有表所有 TEXT 列，REPLACE old_id→new_id。

    17步 UPDATE（v14删除invariants表后）只覆盖预定义列名枚举，本函数兜底扫描所有 TEXT 列，
    替换未枚举列中的残留（如 nodes.owner/business_stream/tags 等）。
    排除 _RENAME_SCAN_EXCLUDE_TABLES（规则示例有意保留）。
    exclude_columns: 由专门步骤处理的列名集合（如 blueprint_id/path），不参与子串REPLACE。
    返回受影响行数。
    """
    _exclude = exclude_columns or set()
    total = 0
    # P2 PG 迁移：sqlite_master → information_schema.tables（PG 不支持 sqlite_master）
    cur = c.execute(SQL_SELECT_ALL_TABLES)
    all_tables = [r["name"] for r in cur.fetchall() if r["name"] not in _RENAME_SCAN_EXCLUDE_TABLES]
    for tbl in all_tables:
        # P2 PG 迁移：PRAGMA table_info → information_schema.columns
        # PG 通过 information_schema.columns 查询列信息：
        #   column_name=列名, data_type=数据类型（如 'text', 'character varying'）
        cur = c.execute(
            SQL_SELECT_TABLE_COLUMNS,
            (tbl,),
        )
        text_cols = [
            r["column_name"]
            for r in cur.fetchall()
            if r["data_type"]
            and r["data_type"].upper() in ("TEXT", "CHARACTER VARYING")
            and r["column_name"] not in _exclude
        ]
        for col in text_cols:
            # 转义LIKE通配符（_ 和 %），避免 D_COMPLIANCE 匹配 D-COMPLIANCE（_是LIKE通配符）
            # REPLACE函数是字面匹配（不解释通配符），所以REPLACE参数仍用原始old_id
            escaped_old_id = old_id.replace("\\", "\\\\").replace("_", "\\_").replace("%", "\\%")
            cnt = c.execute(
                f"SELECT COUNT(*) AS cnt FROM {tbl} WHERE {col} LIKE %s ESCAPE '\\'",
                (f"%{escaped_old_id}%",),
            ).fetchone()["cnt"]
            if cnt > 0:
                print(
                    f"  {mode} 兜底 {tbl}.{col} REPLACE '{old_id}'->'{new_id}': {cnt} rows",
                    file=sys.stderr,
                )
                if not dry_run:
                    c.execute(
                        SQL_UPDATE_TBL_REPLACE_LIKE_ESCAPE.format(tbl=tbl, col=col),
                        (old_id, new_id, f"%{escaped_old_id}%"),
                    )
                total += cnt
    return total


def cmd_rename_domain(
    old_id: str,
    new_id: str,
    dry_run: bool = False,
    db_path: str = None,
    conn=None,
) -> int:
    """重命名域ID——18步UPDATE覆盖11表（裁定#204，方案§4.2）。

    edges.cross_domain 不需显式 UPDATE——由 DB 触发器 trg_nodes_domain_id_au
    在 nodes.domain_id 变化时自动重算受影响边（#ARCH-CROSS-DOMAIN-TRIGGER-001, 2026-07-25）。
    第12张含domain相关列表，11张需UPDATE。
    step 8/17 用 REPLACE+LIKE：domain_events.target_domains 是 JSON/TEXT，
      domain_mapping.subdomain_id 含 -FACTOR 后缀（如 D-SIGNAL_FUNDAMENTAL-FACTOR）
      精确匹配会漏行，必须用 REPLACE+LIKE。
    D-SIGNAL 含其他旧域名前缀（D-SIGNAL_ASHARE 等），应最后替换避免误伤。

    dry_run 只读预览，不触发写锁/物理备份。返回受影响总行数，-1=失败。
    """
    own_conn = conn is None

    # P1-2 红蓝对抗修复：new_id 必须符合 D-{DOMAIN} 格式（无序号）
    # 与 V2 修复（cmd_rename_blueprint_id 校验 new_bp_id）对称，消除不对称漏洞
    ok, reason = _validate_domain_id_format(new_id)
    if not ok:
        print(
            f"ERROR: new_id '{new_id}' 格式不合规：{reason}\n"
            f"domain_id 必须为 D-{{DOMAIN}} 格式（如 D_GOVERNANCE），DOMAIN 为大写+下划线，无序号",
            file=sys.stderr,
        )
        return -1

    def _run(c) -> int:
        """_run implementation."""
        # 0. 校验 old 存在、new 不存在（禁止覆盖）
        if not c.execute(SQL_CHECK_DOMAIN_EXISTS, (old_id,)).fetchone():
            print(f"ERROR: old_id '{old_id}' 不在 domains 表中", file=sys.stderr)
            return -1
        if c.execute(SQL_CHECK_DOMAIN_EXISTS, (new_id,)).fetchone():
            print(f"ERROR: new_id '{new_id}' 已存在 domains 表中（禁止覆盖）", file=sys.stderr)
            return -1

        # 17步UPDATE: (step, table, column, use_replace_like) — v14删除invariants表，原step11移除
        # step1 domains.domain_id; step2-4 nodes 三列; step5-6 domain_dependencies;
        # step7-8 domain_events（target_domains用REPLACE）; step9-10 contracts;
        # step11-12 arch_constraints; step13 arch_directory_tree;
        # step14 arch_path_mappings; step15-16 domain_mapping（subdomain_id用REPLACE+LIKE）;
        # step17 rule_bindings
        steps = [
            (1, "domains", "domain_id", False),
            (2, "nodes", "domain_id", False),
            (3, "nodes", "subdomain_id", False),
            (4, "nodes", "belongs_to", False),
            (5, "domain_dependencies", "from_domain", False),
            (6, "domain_dependencies", "to_domain", False),
            (7, "domain_events", "source_domain", False),
            (8, "domain_events", "target_domains", True),
            (9, "contracts", "provider_domain", False),
            (10, "contracts", "consumer_domain", False),
            (11, "arch_constraints", "from_domain", False),
            (12, "arch_constraints", "to_domain", False),
            (13, "arch_directory_tree", "domain_id", False),
            (14, "arch_path_mappings", "domain_id", False),
            (15, "domain_mapping", "domain_id", False),
            (16, "domain_mapping", "subdomain_id", True),
            (17, "rule_bindings", "domain_id", False),
        ]
        total = 0
        mode = "[DRY RUN]" if dry_run else "[OK]"
        for step, tbl, col, use_like in steps:
            if use_like:
                cnt = c.execute(
                    SQL_COUNT_TBL_BY_COL_LIKE.format(tbl=tbl, col=col),
                    (f"%{old_id}%",),
                ).fetchone()["count"]
                if cnt > 0:
                    print(f"  {mode} step{step:>2} {tbl}.{col} REPLACE+LIKE '%{old_id}%': {cnt} rows", file=sys.stderr)
                    if not dry_run:
                        c.execute(
                            SQL_UPDATE_TBL_REPLACE_LIKE.format(tbl=tbl, col=col),
                            (old_id, new_id, f"%{old_id}%"),
                        )
            else:
                cnt = c.execute(
                    SQL_COUNT_TBL_BY_COL_EQ.format(tbl=tbl, col=col),
                    (old_id,),
                ).fetchone()["count"]
                if cnt > 0:
                    print(f"  {mode} step{step:>2} {tbl}.{col}='{old_id}': {cnt} rows", file=sys.stderr)
                    if not dry_run:
                        c.execute(
                            SQL_UPDATE_TBL_COL_EQ.format(tbl=tbl, col=col),
                            (new_id, old_id),
                        )
            total += cnt
        # B1 值扫描兜底（裁定#207 R1）：18步枚举列之外的全表TEXT列残留替换
        # 排除 blueprint_id/path（由 --propagate-rename 精确值映射 / 阶段D 路径传播专门处理）
        total += _scan_replace_all_text_columns(
            c,
            old_id,
            new_id,
            dry_run=dry_run,
            mode=mode,
            exclude_columns=_RENAME_SCAN_EXCLUDE_COLUMNS,
        )
        if not dry_run and own_conn:
            c.commit()
        print(f"{mode} cmd_rename_domain({old_id} -> {new_id}): total {total} rows", file=sys.stderr)
        return total

    if dry_run:
        # dry_run 只读预览，不加写锁不备份
        c = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True) if own_conn else conn
        if own_conn:
            pass  # P2 PG: PRAGMA 已删除（PG 不需要）
            pass  # P2 PG: PRAGMA 已删除（PG 不需要）
        try:
            return _run(c)
        finally:
            if own_conn:
                c.close()
    else:
        with _optional_db_lock(own_conn, task=f"rename_domain_{old_id}", db_path=db_path):
            c = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True) if own_conn else conn
            if own_conn:
                pass  # P2 PG: PRAGMA 已删除（PG 不需要）
                pass  # P2 PG: PRAGMA 已删除（PG 不需要）
            try:
                return _run(c)
            except Exception as e:
                if own_conn:
                    c.rollback()
                logger.error("cmd_rename_domain失败: %s", e)
                return -1
            finally:
                if own_conn:
                    c.close()


def _post_rename_residual_check(old_id: str, db_path: str) -> None:
    """改名后置残留校验钩子（治本：消除手工跑 audit 的必要性）。

    事件驱动：cmd_rename_domain 完成后自动调用，扫描 DB 所有 TEXT 列检测 old_id 残留。
    复用 audit_rename_completeness.scan_residual（真源唯一，禁止复制扫描逻辑）。
    失败仅 WARNING（改名已成功 commit，不自动回滚），提示人工用
    `audit_rename_completeness.py --old-id XXX --rounds 2` 复核。

    设计原则（向内收）：
      - 不复制扫描逻辑，复用 audit_rename_completeness 现成函数
      - 延迟 import 避免启动时耦合
      - import 失败 graceful 降级到提示手工跑
    """
    try:
        from d8_doc_sync.audit_rename_completeness import scan_residual
    except ImportError as e:
        print(
            f"[POST-RENAME-CHECK] SKIP: audit_rename_completeness 不可导入 ({e})\n"
            f"  手工复核: python scripts/governance/d8_doc_sync/audit_rename_completeness.py --old-id {old_id} --rounds 2",
            file=sys.stderr,
        )
        return
    conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
    try:
        pass  # P2 PG: PRAGMA 已删除（PG 不需要）
        pass  # P2 PG: PRAGMA 已删除（PG 不需要）
        residuals = scan_residual(conn, [old_id], check_all_text_columns=True)
        total = sum(r["count"] for r in residuals)
        if total == 0:
            print(f"[POST-RENAME-CHECK] OK: 0 residual for '{old_id}' (全表 TEXT 列扫描)")
        else:
            print(
                f"[POST-RENAME-CHECK] WARNING: {total} residual rows for '{old_id}' "
                f"(改名已成功，但检测到遗漏列需人工复核):",
                file=sys.stderr,
            )
            for r in residuals:
                print(
                    f"  {r['table']}.{r['column']} contains '{r['old_id']}': {r['count']} rows",
                    file=sys.stderr,
                )
            print(
                f"  复核命令: python scripts/governance/d8_doc_sync/audit_rename_completeness.py --old-id {old_id} --rounds 2",
                file=sys.stderr,
            )
    finally:
        conn.close()


def cmd_delete_domain(
    domain_id: str,
    dry_run: bool = False,
    db_path: str = None,
    conn=None,
    force: bool = False,
) -> int:
    """删除域——17步DELETE覆盖11表（DM-100255 配套工具就绪）。

    安全门：检查 nodes 表引用，>0 且未 --force 时阻断（nodes 需先 --migrate-nodes 迁移）。
    删除顺序：先清外部引用（steps 2-17），最后删 domains 行（step1）避免 FK 违规。
    单值列：DELETE WHERE col=domain_id（rule_bindings 例外 SET NULL，规则是全局资产）。
    多值列：REPLACE 移除 domain_id 子串，再 DELETE 空值/精确匹配行。

    dry_run 只读预览，不触发写锁/物理备份。返回受影响总行数，-1=失败。
    完成后自动触发 _post_rename_residual_check 后置残留校验（事件驱动，复用现成扫描）。
    """
    own_conn = conn is None

    def _run(c) -> int:
        """_run implementation."""
        # 0. 校验 domain 存在
        if not c.execute(SQL_CHECK_DOMAIN_EXISTS, (domain_id,)).fetchone():
            print(f"ERROR: domain_id '{domain_id}' 不在 domains 表中", file=sys.stderr)
            return -1

        # 安全门：检查 nodes 引用（force=True 可跳过）
        node_cnt = c.execute(SQL_COUNT_NODES_BY_DOMAIN, (domain_id,)).fetchone()["cnt"]
        if node_cnt > 0 and not force:
            print(
                f"ERROR: nodes 表有 {node_cnt} 行引用 domain_id='{domain_id}'\n"
                f"  安全门阻断：nodes 需先通过 --migrate-nodes 迁移到其他域\n"
                f"  确认要强制删除（含 nodes 级联删除）请加 --force",
                file=sys.stderr,
            )
            return -1

        # 16步DELETE: (step, table, column, use_replace_like) — 域引用列清单
        # 删除顺序与 rename 不同：先清外部引用（steps 2-16），最后删 domains（step1）
        # rule_bindings.domain_id 例外：SET NULL（规则是全局资产，不删除规则行）
        # 注：nodes.belongs_to 不在此清单——该列存模块ID(MOD-*)非域ID(D_*)，
        # 精确匹配 domain_id 永远为0（死代码）；LIKE 会误匹配 MOD-GOV-REPAIR 破坏模块引用。
        # 实测确认（2026-07-03 D_GOV_REPAIR 删除）：belongs_to 无 D_* 模式值。
        steps_foreign = [
            (2, "nodes", "domain_id", False),
            (3, "nodes", "subdomain_id", False),
            (5, "domain_dependencies", "from_domain", False),
            (6, "domain_dependencies", "to_domain", False),
            (7, "domain_events", "source_domain", False),
            (8, "domain_events", "target_domains", True),
            (9, "contracts", "provider_domain", False),
            (10, "contracts", "consumer_domain", False),
            (11, "arch_constraints", "from_domain", False),
            (12, "arch_constraints", "to_domain", False),
            (13, "arch_directory_tree", "domain_id", False),
            (14, "arch_path_mappings", "domain_id", False),
            (15, "domain_mapping", "domain_id", False),
            (16, "domain_mapping", "subdomain_id", True),
        ]
        total = 0
        mode = "[DRY RUN]" if dry_run else "[OK]"
        for step, tbl, col, use_like in steps_foreign:
            if use_like:
                # 多值列：REPLACE 移除 domain_id，再 DELETE 空值/精确匹配行
                cnt = c.execute(
                    SQL_COUNT_TBL_LIKE_CNT.format(tbl=tbl, col=col),
                    (f"%{domain_id}%",),
                ).fetchone()["cnt"]
                if cnt > 0:
                    print(f"  {mode} step{step:>2} {tbl}.{col} REPLACE '{domain_id}'->'': {cnt} rows", file=sys.stderr)
                    if not dry_run:
                        c.execute(
                            SQL_UPDATE_TBL_REPLACE_LIKE.format(tbl=tbl, col=col),
                            (domain_id, "", f"%{domain_id}%"),
                        )
                        # 清理替换后变空或仅剩 domain_id 的行
                        c.execute(
                            SQL_DELETE_TBL_COL_EQ_OR_EMPTY.format(tbl=tbl, col=col),
                            (domain_id,),
                        )
                total += cnt
            else:
                cnt = c.execute(
                    SQL_COUNT_TBL_COL_EQ_CNT.format(tbl=tbl, col=col),
                    (domain_id,),
                ).fetchone()["cnt"]
                if cnt > 0:
                    print(f"  {mode} step{step:>2} {tbl}.{col}='{domain_id}': DELETE {cnt} rows", file=sys.stderr)
                    if not dry_run:
                        c.execute(
                            SQL_DELETE_TBL_COL_EQ.format(tbl=tbl, col=col),
                            (domain_id,),
                        )
                total += cnt

        # step17 rule_bindings.domain_id: SET NULL（规则是全局资产，不删除规则行）
        cnt = c.execute(
            SQL_COUNT_RULE_BINDINGS_BY_DOMAIN,
            (domain_id,),
        ).fetchone()["cnt"]
        if cnt > 0:
            print(f"  {mode} step17 rule_bindings.domain_id='{domain_id}': SET NULL {cnt} rows", file=sys.stderr)
            if not dry_run:
                c.execute(
                    SQL_NULL_RULE_BINDINGS_DOMAIN,
                    (domain_id,),
                )
        total += cnt

        # step1 最后：DELETE FROM domains（FK 约束要求外部引用先清完）
        print(f"  {mode} step 1 domains.domain_id='{domain_id}': DELETE 1 row", file=sys.stderr)
        if not dry_run:
            c.execute(SQL_DELETE_DOMAIN_BY_ID, (domain_id,))
        total += 1

        if not dry_run and own_conn:
            c.commit()
        print(f"{mode} cmd_delete_domain({domain_id}): total {total} rows", file=sys.stderr)
        return total

    if dry_run:
        c = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True) if own_conn else conn
        try:
            return _run(c)
        finally:
            if own_conn:
                c.close()
    else:
        with _optional_db_lock(own_conn, task=f"delete_domain_{domain_id}", db_path=db_path):
            c = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True) if own_conn else conn
            try:
                return _run(c)
            except Exception as e:
                if own_conn:
                    c.rollback()
                logger.error("cmd_delete_domain失败: %s", e)
                return -1
            finally:
                if own_conn:
                    c.close()


def cmd_merge_domain(
    old_id: str,
    new_id: str,
    dry_run: bool = False,
    db_path: str = None,
    conn=None,
) -> int:
    """合并域——将 old_id 的所有引用迁移到已存在的 new_id，然后删除 old_id（裁定#ARCH-target_layer_v1.0.0）。

    与 cmd_rename_domain 的区别：rename 要求 new_id 不存在（PK UPDATE），merge 要求
    new_id 已存在（语义合并场景）。典型用途：废弃域归并到已登记域（如 D_COMPLIANCE →
    D_GOV_ENFORCEMENT）。

    流程（与 rename 步骤对齐，step1 改为 DELETE）：
      step1  DELETE FROM domains WHERE domain_id=old_id（new_id 行已存在，仅删旧行）
      step2-17  UPDATE 11表引用列 old_id → new_id（与 rename step2-17 完全一致）
      B1     全表 TEXT 列值扫描兜底（与 rename 一致，复用 _scan_replace_all_text_columns）

    domain_dependencies 复合 PK (from_domain, to_domain) 冲突预检：
      若 (old_id, X) 和 (new_id, X) 同时存在，UPDATE 会产生 PK 冲突。
      预检发现冲突 → 阻断（-1），提示人工合并 edge_count 后删除旧行再重试。

    dry_run 只读预览，不触发写锁/物理备份。返回受影响总行数，-1=失败。
    完成后自动触发 _post_rename_residual_check 后置残留校验（事件驱动，复用现成扫描）。
    """
    own_conn = conn is None

    # 格式校验（与 cmd_rename_domain 对称）
    ok, reason = _validate_domain_id_format(new_id)
    if not ok:
        print(
            f"ERROR: new_id '{new_id}' 格式不合规：{reason}\n"
            f"domain_id 必须为 D_{{DOMAIN}} 格式（如 D_GOVERNANCE），DOMAIN 为大写+下划线，无序号",
            file=sys.stderr,
        )
        return -1
    ok, reason = _validate_domain_id_format(old_id)
    if not ok:
        print(
            f"ERROR: old_id '{old_id}' 格式不合规：{reason}",
            file=sys.stderr,
        )
        return -1
    if old_id == new_id:
        print(f"ERROR: old_id 与 new_id 相同（'{old_id}'），无需合并", file=sys.stderr)
        return -1

    def _run(c) -> int:
        """_run implementation."""
        # 0. 校验 old 存在、new 存在（merge：两者必须都在 domains 表中）
        if not c.execute(SQL_CHECK_DOMAIN_EXISTS, (old_id,)).fetchone():
            print(f"ERROR: old_id '{old_id}' 不在 domains 表中", file=sys.stderr)
            return -1
        if not c.execute(SQL_CHECK_DOMAIN_EXISTS, (new_id,)).fetchone():
            print(
                f"ERROR: new_id '{new_id}' 不在 domains 表中（merge 要求目标域已存在；若要重命名请用 --rename-domain）",
                file=sys.stderr,
            )
            return -1

        # domain_dependencies 复合 PK 冲突预检
        # 场景1：(old_id, X) 与 (new_id, X) 同时存在 → from_domain UPDATE 会冲突
        from_conflicts = c.execute(
            SQL_COUNT_DOMAIN_DEP_CONFLICTS_FROM,
            (old_id, new_id),
        ).fetchone()["cnt"]
        # 场景2：(X, old_id) 与 (X, new_id) 同时存在 → to_domain UPDATE 会冲突
        to_conflicts = c.execute(
            SQL_COUNT_DOMAIN_DEP_CONFLICTS_TO,
            (old_id, new_id),
        ).fetchone()["cnt"]
        if from_conflicts > 0 or to_conflicts > 0:
            print(
                f"ERROR: domain_dependencies 复合 PK 冲突（from={from_conflicts}, to={to_conflicts}）\n"
                f"  (old_id, X) 与 (new_id, X) 同时存在，UPDATE 会违反 PRIMARY KEY (from_domain, to_domain)\n"
                f"  请手工合并 edge_count 到 new_id 行后 DELETE old_id 行，再重试 --merge-domain",
                file=sys.stderr,
            )
            return -1

        # step2-17 UPDATE: (step, table, column, use_replace_like) — 与 rename step2-17 一致
        # step1 在最后执行 DELETE（domains 表），不在此 UPDATE 清单中
        steps = [
            (2, "nodes", "domain_id", False),
            (3, "nodes", "subdomain_id", False),
            (4, "nodes", "belongs_to", False),
            (5, "domain_dependencies", "from_domain", False),
            (6, "domain_dependencies", "to_domain", False),
            (7, "domain_events", "source_domain", False),
            (8, "domain_events", "target_domains", True),
            (9, "contracts", "provider_domain", False),
            (10, "contracts", "consumer_domain", False),
            (11, "arch_constraints", "from_domain", False),
            (12, "arch_constraints", "to_domain", False),
            (13, "arch_directory_tree", "domain_id", False),
            (14, "arch_path_mappings", "domain_id", False),
            (15, "domain_mapping", "domain_id", False),
            (16, "domain_mapping", "subdomain_id", True),
            (17, "rule_bindings", "domain_id", False),
        ]
        total = 0
        mode = "[DRY RUN]" if dry_run else "[OK]"
        for step, tbl, col, use_like in steps:
            if use_like:
                cnt = c.execute(
                    SQL_COUNT_TBL_BY_COL_LIKE.format(tbl=tbl, col=col),
                    (f"%{old_id}%",),
                ).fetchone()["count"]
                if cnt > 0:
                    print(f"  {mode} step{step:>2} {tbl}.{col} REPLACE+LIKE '%{old_id}%': {cnt} rows", file=sys.stderr)
                    if not dry_run:
                        c.execute(
                            SQL_UPDATE_TBL_REPLACE_LIKE.format(tbl=tbl, col=col),
                            (old_id, new_id, f"%{old_id}%"),
                        )
            else:
                cnt = c.execute(
                    SQL_COUNT_TBL_BY_COL_EQ.format(tbl=tbl, col=col),
                    (old_id,),
                ).fetchone()["count"]
                if cnt > 0:
                    print(f"  {mode} step{step:>2} {tbl}.{col}='{old_id}': {cnt} rows", file=sys.stderr)
                    if not dry_run:
                        c.execute(
                            SQL_UPDATE_TBL_COL_EQ.format(tbl=tbl, col=col),
                            (new_id, old_id),
                        )
            total += cnt

        # step1 DELETE（在 B1 兜底扫描之前执行）：
        # merge 场景 domains 表已有 new_id 行，兜底扫描会尝试 UPDATE domains.domain_id
        # 导致 PK 违规。先 DELETE old_id 行，兜底扫描就找不到 domains.domain_id=old_id 了。
        # FK 约束要求外部引用先清完（step2-17 已执行），此时 DELETE 安全。
        print(f"  {mode} step 1 domains.domain_id='{old_id}': DELETE 1 row", file=sys.stderr)
        if not dry_run:
            c.execute(SQL_DELETE_DOMAIN_BY_ID, (old_id,))
        total += 1

        # B1 值扫描兜底（与 rename 一致）：step2-17 枚举列之外的全表 TEXT 列残留替换
        # 注：domains.domain_id=old_id 行已 DELETE，兜底扫描不会触发 PK 违规
        total += _scan_replace_all_text_columns(
            c,
            old_id,
            new_id,
            dry_run=dry_run,
            mode=mode,
            exclude_columns=_RENAME_SCAN_EXCLUDE_COLUMNS,
        )

        if not dry_run and own_conn:
            c.commit()
        print(f"{mode} cmd_merge_domain({old_id} -> {new_id}): total {total} rows", file=sys.stderr)
        return total

    if dry_run:
        c = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True) if own_conn else conn
        try:
            return _run(c)
        finally:
            if own_conn:
                c.close()
    else:
        with _optional_db_lock(own_conn, task=f"merge_domain_{old_id}", db_path=db_path):
            c = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True) if own_conn else conn
            try:
                return _run(c)
            except Exception as e:
                if own_conn:
                    c.rollback()
                logger.error("cmd_merge_domain失败: %s", e)
                return -1
            finally:
                if own_conn:
                    c.close()


def cmd_fix_rename_residual(
    rename_map: dict[str, str],
    dry_run: bool = False,
    db_path: str = None,
    conn=None,
) -> int:
    """修复存量改名残留（裁定#207 R1 B5）。

    扫描所有表所有 TEXT 列，按 rename_map 顺序（先长后短，避免子串误匹配）
    REPLACE 旧标识符→新标识符。不检查 domains 表（存量残留的 old_id 已改名）。
    排除 _RENAME_SCAN_EXCLUDE_TABLES（规则示例有意保留）。

    返回受影响总行数，-1=失败。
    """
    own_conn = conn is None
    # 按旧ID长度降序排列（先长后短，避免 D-SIGNAL 先替换 D-SIGNAL_ASHARE 的子串）
    sorted_map = sorted(rename_map.items(), key=lambda x: len(x[0]), reverse=True)

    def _run(c) -> int:
        """_run implementation."""
        mode = "[DRY RUN]" if dry_run else "[OK]"
        total = 0
        for old_id, new_id in sorted_map:
            print(f"  {mode} 修复残留: {old_id} -> {new_id}", file=sys.stderr)
            total += _scan_replace_all_text_columns(
                c,
                old_id,
                new_id,
                dry_run=dry_run,
                mode=mode,
                exclude_columns=_RENAME_SCAN_EXCLUDE_COLUMNS,
            )
        if not dry_run and own_conn:
            c.commit()
        print(f"{mode} cmd_fix_rename_residual: total {total} rows", file=sys.stderr)
        return total

    if dry_run:
        c = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True) if own_conn else conn
        if own_conn:
            pass  # P2 PG: PRAGMA 已删除（PG 不需要）
            pass  # P2 PG: PRAGMA 已删除（PG 不需要）
        try:
            return _run(c)
        finally:
            if own_conn:
                c.close()
    else:
        with _optional_db_lock(own_conn, task="fix_rename_residual", db_path=db_path):
            c = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True) if own_conn else conn
            if own_conn:
                pass  # P2 PG: PRAGMA 已删除（PG 不需要）
                pass  # P2 PG: PRAGMA 已删除（PG 不需要）
            try:
                return _run(c)
            except Exception as e:
                if own_conn:
                    c.rollback()
                logger.error("cmd_fix_rename_residual失败: %s", e)
                return -1
            finally:
                if own_conn:
                    c.close()


def cmd_replace_text_domain(
    old_id: str,
    new_id: str,
    dry_run: bool = False,
    db_path: str = None,
    conn=None,
) -> int:
    """全表TEXT列值替换（裁定#ARCH-target_layer_v1.0.0：清理旧格式domain_id引用）。

    与 --merge-domain 的区别：
    - --merge-domain: 17步UPDATE + DELETE old_id（old_id须是现存domain）
    - --replace-text-domain: 仅全表TEXT列REPLACE（不修改domain记录，old_id可以是任意字符串）

    用途：清理描述性文本中的旧格式domain_id引用（如 D-COMPLIANCE → D-GOV_ENFORCEMENT）。
    复用 _scan_replace_all_text_columns（已修复LIKE通配符陷阱，裁定#ARCH-target_layer_v1.0.0）。

    返回受影响总行数，-1=失败。
    """
    own_conn = conn is None
    # 校验 new_id 格式（必须是合法domain_id，复用 DOMAIN_ID_RE）
    # 治本(2026-07-20): 改用项目内模块路径导入，避免 sys.path.insert 后的悬空 import
    # （IMPORT-INTEGRITY gate 不识别 sys.path.insert 注入的导入）
    from scripts.governance.d3_metadata.validate_module_id_naming import is_valid_domain_id

    ok, reason = is_valid_domain_id(new_id)
    if not ok:
        print(f"ERROR: new_id '{new_id}' 格式不合法: {reason}", file=sys.stderr)
        return -1

    def _run(c) -> int:
        """_run implementation."""
        mode = "[DRY RUN]" if dry_run else "[OK]"
        print(f"  {mode} 全表文本替换: '{old_id}' -> '{new_id}'", file=sys.stderr)
        total = _scan_replace_all_text_columns(
            c,
            old_id,
            new_id,
            dry_run=dry_run,
            mode=mode,
        )
        if not dry_run and own_conn:
            c.commit()
        print(f"{mode} cmd_replace_text_domain: total {total} rows", file=sys.stderr)
        return total

    if dry_run:
        c = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True) if own_conn else conn
        try:
            return _run(c)
        finally:
            if own_conn:
                c.close()
    else:
        with _optional_db_lock(own_conn, task="replace_text_domain", db_path=db_path):
            c = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True) if own_conn else conn
            try:
                return _run(c)
            except Exception as e:
                if own_conn:
                    c.rollback()
                logger.error("cmd_replace_text_domain失败: %s", e)
                return -1
            finally:
                if own_conn:
                    c.close()


def cmd_apply_domain_id_check(
    dry_run: bool = False,
    conn=None,
) -> int:
    """应用 domains.domain_id CHECK 约束到现有数据库（裁定#ARCH-target_layer_v1.0.0）。

    幂等：检查约束是否存在，已存在则跳过，不存在则 ALTER TABLE ADD CONSTRAINT。
    预检：添加约束前验证所有 domain_id 值符合 CHECK 正则，避免 ALTER 失败。

    CHECK 约束正则：^D_[A-Z][A-Z0-9_]*$（与 DOMAIN_ID_RE 语义一致，允许数字如 D_INFRA_A2A）。
    约束名：domains_domain_id_format_check。

    背景：_MIGRATIONS P2后不再执行（depgraph_schema.py L1199），现有DB需通过此命令补丁式应用CHECK约束。
    02_create_pg_schema.sql 已包含CHECK约束（新部署生效），此命令用于存量DB补丁。

    返回 0=成功/已存在，-1=失败。
    """
    own_conn = conn is None
    _CHECK_NAME = "domains_domain_id_format_check"
    _CHECK_REGEX = "^D_[A-Z][A-Z0-9_]*$"

    def _run(c) -> int:
        """_run implementation."""
        mode = "[DRY RUN]" if dry_run else "[OK]"
        # 1. 检查约束是否已存在（幂等性）
        row = c.execute(
            SQL_COUNT_CONSTRAINT_BY_NAME,
            (_CHECK_NAME,),
        ).fetchone()
        if row["cnt"] > 0:
            print(f"  {mode} CHECK 约束 '{_CHECK_NAME}' 已存在，跳过", file=sys.stderr)
            return EXIT_PASS
        # 2. 预检所有 domain_id 值（避免 ALTER 失败）
        invalid_rows = c.execute(
            SQL_SELECT_INVALID_DOMAIN_IDS,
            (_CHECK_REGEX,),
        ).fetchall()
        if invalid_rows:
            print(
                f"  ERROR: {len(invalid_rows)} 行 domain_id 不符合 CHECK 正则 '{_CHECK_REGEX}':",
                file=sys.stderr,
            )
            for r in invalid_rows:
                print(f"    {r['domain_id']}", file=sys.stderr)
            return -1
        # 3. ALTER TABLE ADD CONSTRAINT
        print(
            f"  {mode} ALTER TABLE domains ADD CONSTRAINT {_CHECK_NAME} CHECK (domain_id ~ '{_CHECK_REGEX}')",
            file=sys.stderr,
        )
        if not dry_run:
            c.execute(
                f"ALTER TABLE domains ADD CONSTRAINT {_CHECK_NAME} "
                f"CHECK (domain_id ~ '{_CHECK_REGEX}')"  # 5.160.2 OK: dynamic SQL, kept inline
            )
            if own_conn:
                c.commit()
        print(f"{mode} cmd_apply_domain_id_check: CHECK 约束已应用", file=sys.stderr)
        return EXIT_PASS

    c = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True) if own_conn else conn
    try:
        return _run(c)
    finally:
        if own_conn:
            c.close()


def cmd_fix_domains_defaults(
    dry_run: bool = False,
    conn=None,
) -> int:
    """修复 domains 表 build_status DEFAULT 值（裁定#ARCH-target_layer_v1.0.0 v16修复）。

    修复预存bug：build_status DEFAULT 'unbuilt' 不在 CHECK 允许值中，
    INSERT 不提供 build_status 时会失败。修复为 DEFAULT 'planned'。

    幂等：检查当前 DEFAULT 值，已是 'planned' 则跳过。

    返回 0=成功/已修复，-1=失败。
    """
    own_conn = conn is None

    def _run(c) -> int:
        """_run implementation."""
        mode = "[DRY RUN]" if dry_run else "[OK]"
        # 1. 检查当前 DEFAULT 值
        row = c.execute(
            SQL_SELECT_DOMAIN_BUILD_STATUS_DEFAULT,
        ).fetchone()
        current_default = row["column_default"] if row else None
        # PG 返回 'unbuilt'::text 或 'planned'::text
        print(f"  {mode} 当前 build_status DEFAULT: {current_default}", file=sys.stderr)

        if current_default and "'planned'" in current_default:
            print(f"  {mode} DEFAULT 已是 'planned'，跳过", file=sys.stderr)
            return EXIT_PASS
        if current_default and "'unbuilt'" not in current_default:
            print(f"  {mode} DEFAULT 既不是 'unbuilt' 也不是 'planned'，跳过（未知值）", file=sys.stderr)
            return EXIT_PASS
        # 2. ALTER TABLE ALTER COLUMN SET DEFAULT
        print(f"  {mode} ALTER TABLE domains ALTER COLUMN build_status SET DEFAULT 'planned'", file=sys.stderr)
        if not dry_run:
            c.execute(SQL_ALTER_DOMAIN_BUILD_STATUS_DEFAULT)
            if own_conn:
                c.commit()
        print(f"{mode} cmd_fix_domains_defaults: DEFAULT 已修复为 'planned'", file=sys.stderr)
        return EXIT_PASS

    c = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True) if own_conn else conn
    try:
        return _run(c)
    finally:
        if own_conn:
            c.close()


def cmd_fix_domains_build_status_vocab(
    dry_run: bool = False,
    conn=None,
) -> int:
    """domains.build_status CHECK 词表扩展 +dormant（tracker #251 / #ARCH-143 续作）。

    背景：#ARCH-143 R2 裁定零节点域休眠真源=翻译注册表 build_status: dormant，
    但 depgraph domains.build_status CHECK 仅 5 态（planned/generated/testing/stable/
    deprecated）无 dormant，14 零节点域侧写无法落库。deprecated 语义（有替代品）
    与 dormant（保留不激活）不同，不强行复用。Owner 窗口 schema 变更（2026-08-22 授权）。

    幂等：CHECK 定义已含 'dormant' 则跳过；无约束行（异常态）直接补 ADD。
    nodes.build_status 维持 5 态不动（dormant 仅域级语义）。
    superuser：ALTER TABLE 需属主权限（表 owner=zephyr，仅 postgres 可 DDL，
    先例 migrations/add_acquisition_fields.py）。

    返回 0=成功/已修复，-1=失败。
    """
    own_conn = conn is None

    def _run(c) -> int:
        """_run implementation."""
        mode = "[DRY RUN]" if dry_run else "[OK]"
        rows = c.execute(SQL_SELECT_DOMAIN_BUILD_STATUS_CHECK).fetchall()
        row = next((r for r in rows if "build_status" in (r["def"] or "")), None)
        current_def = row["def"] if row else None
        print(f"  {mode} 当前 domains.build_status CHECK: {current_def}", file=sys.stderr)

        if current_def and "'dormant'" in current_def:
            print(f"  {mode} CHECK 已含 'dormant'，跳过", file=sys.stderr)
            return EXIT_PASS
        if not dry_run:
            if current_def:
                c.execute(SQL_DROP_DOMAIN_BUILD_STATUS_CHECK)
            c.execute(SQL_ADD_DOMAIN_BUILD_STATUS_CHECK)
            if own_conn:
                c.commit()
        print(f"{mode} cmd_fix_domains_build_status_vocab: CHECK 已扩展 6 态（+dormant）", file=sys.stderr)
        return EXIT_PASS

    c = get_depgraph_pg_connection(autocommit=False, superuser=True) if own_conn else conn
    try:
        return _run(c)
    finally:
        if own_conn:
            c.close()


def _restore_blueprint_links_readonly_trigger(c) -> None:
    """恢复 blueprint_links 只读触发器（裁定#207 R1 B2 通行证恢复）。

    cmd_propagate_rename 临时 DROP 该触发器以写入 blueprint_links.blueprint_id，
    操作完成后必须恢复，保持"YAML 唯一真源"门禁激活。

    治本（#ARCH-DATAQUALITY-V1, 2026-07-19）：修复 SQLite→PostgreSQL 语法迁移遗漏。
    原 SQLite 语法（CREATE TRIGGER IF NOT EXISTS ... BEGIN SELECT RAISE(ABORT,...) END）
    在 PostgreSQL 上失败——PG 需要 CREATE FUNCTION + CREATE TRIGGER EXECUTE FUNCTION。

    治本2（#ARCH-DATAQUALITY-V1, 2026-07-19）：触发器恢复改为非致命——PostgreSQL
    用户可能无 CREATE FUNCTION 权限（对模式 public 权限不够）。触发器从未在 PG 上
    创建成功（原 SQLite 语法一直失败），所以"恢复"一个从未存在的触发器=空操作。
    权限不足时 log warning 不 raise，避免阻断 rename 事务回滚。
    """
    try:
        c.execute(SQL_CREATE_PREVENT_UPDATE_FUNCTION)
        c.execute(SQL_DROP_READONLY_TRIGGER)
        c.execute(SQL_CREATE_READONLY_TRIGGER)
    except psycopg2.Error as e:
        logger.warning(
            "恢复 blueprint_links 只读触发器失败（权限不足或语法错误，触发器从未在 PG 上创建——非致命）: %s", e
        )


def cmd_propagate_rename(
    rename_map: dict[str, str],
    dry_run: bool = False,
    db_path: str = None,
    conn=None,
) -> int:
    """blueprint_id 派生标识符传播（裁定#206 B-5/B-6 + 裁定#207 R1 B2）。

    根据 domain_id 改名映射，精确值映射 blueprint_id（禁止子串REPLACE）。
    派生关系：blueprint_id 域片段派生自 domain_id（去 D- 前缀）。
    传播表：nodes.blueprint_id, blueprint_links.blueprint_id。

    返回受影响总行数，-1=失败。
    """
    own_conn = conn is None
    sorted_map = sorted(rename_map.items(), key=lambda x: len(x[0]), reverse=True)

    def _run(c) -> int:
        """_run implementation."""
        mode = "[DRY RUN]" if dry_run else "[OK]"
        total = 0
        for old_domain, new_domain in sorted_map:
            # 推导 blueprint_id 旧/新域片段（去 D- 前缀）
            old_frag = old_domain[2:] if old_domain.startswith("D-") else old_domain
            new_frag = new_domain[2:] if new_domain.startswith("D-") else new_domain
            # 查询所有旧 blueprint_id（MOD-{old_frag} 或 MOD-{old_frag}-*）
            old_bp_ids = set()
            for tbl, col in [("nodes", "blueprint_id"), ("blueprint_links", "blueprint_id")]:
                try:
                    rows = c.execute(
                        SQL_SELECT_DISTINCT_TBL_COL_LIKE.format(tbl=tbl, col=col),
                        (f"MOD-{old_frag}%",),
                    ).fetchall()
                    old_bp_ids.update(r[col] for r in rows if r[col])
                except psycopg2.Error as e:
                    # Phase 2 P2 修复（异常处理 HIGH）：查询失败静默跳过=blueprint_id 传播丢失
                    logger.warning(
                        "propagate_blueprint_id: 查询 %s.%s 失败(%s)，该域 blueprint_id 传播被跳过", tbl, col, e
                    )

            for old_bp_id in sorted(old_bp_ids):
                # 精确值映射：MOD-{old_frag} -> MOD-{new_frag}（只替换域片段，保留序号）
                prefix = f"MOD-{old_frag}"
                if old_bp_id == prefix:
                    new_bp_id = f"MOD-{new_frag}"
                elif old_bp_id.startswith(prefix + "-"):
                    suffix = old_bp_id[len(prefix) :]  # 含 -{SEQ}
                    new_bp_id = f"MOD-{new_frag}{suffix}"
                else:
                    continue  # 不匹配（如 MOD-SIGNAL_ASHARE_EXTRA），跳过

                # 传播表 1+2（nodes + blueprint_links），复用公共传播逻辑
                total += _propagate_bp_id_core(c, old_bp_id, new_bp_id, dry_run)

        if not dry_run and own_conn:
            c.commit()
        print(f"{mode} cmd_propagate_rename: total {total} rows", file=sys.stderr)
        return total

    return _with_bp_rename_tx(_run, own_conn, dry_run, db_path, "propagate_rename", conn)


def _safe_bp_id_replace(text: str, old: str, new: str) -> str:
    """安全替换 blueprint_id：负向前瞻防止 MOD-SHARED 误匹配 MOD-SHARED-001。"""
    pattern = re.escape(old) + r"(?![A-Za-z0-9_-])"
    return re.sub(pattern, new, text)


def _with_bp_rename_tx(
    run_fn,
    own_conn: bool,
    dry_run: bool,
    db_path: str,
    task: str,
    conn=None,
) -> int:
    """blueprint_id 改名事务管理公共逻辑（cmd_propagate_rename 和 cmd_rename_blueprint_id 共享）。

    封装：WAL 设置 + 文件锁 + blueprint_links 只读触发器通行证 + 异常恢复。
    dry_run=True 时只读连接，不加锁，不 DROP 触发器。
    dry_run=False 时加文件锁，DROP 触发器，执行后 RESTORE，异常时也 RESTORE。

    返回 run_fn 的返回值，失败返回 -1。
    """
    if dry_run:
        c = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True) if own_conn else conn
        if own_conn:
            pass  # P2 PG: PRAGMA 已删除（PG 不需要）
            pass  # P2 PG: PRAGMA 已删除（PG 不需要）
        try:
            return run_fn(c)
        finally:
            if own_conn:
                c.close()
    else:
        with _optional_db_lock(own_conn, task=task, db_path=db_path):
            c = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True) if own_conn else conn
            if own_conn:
                pass  # P2 PG: PRAGMA 已删除（PG 不需要）
                pass  # P2 PG: PRAGMA 已删除（PG 不需要）
            # 临时禁用 blueprint_links 只读触发器（裁定#207 R1 B2 通行证机制）
            c.execute(SQL_DROP_READONLY_TRIGGER)
            try:
                n = run_fn(c)
                # 成功后恢复只读触发器并 commit
                _restore_blueprint_links_readonly_trigger(c)
                if own_conn:
                    c.commit()
                return n
            except Exception as e:
                if own_conn:
                    c.rollback()
                logger.error("%s失败: %s", task, e)
                # 异常时也恢复只读触发器（保持门禁激活）
                try:
                    _restore_blueprint_links_readonly_trigger(c)
                    if own_conn:
                        c.commit()
                except psycopg2.Error as restore_err:
                    logger.warning("恢复 blueprint_links 只读触发器失败（门禁可能遗留禁用状态）: %s", restore_err)
                return -1
            finally:
                if own_conn:
                    c.close()


def _propagate_bp_id_core(
    c,
    old_bp_id: str,
    new_bp_id: str,
    dry_run: bool = False,
    propagate_tsd: bool = False,
    propagate_bp_path: bool = False,
) -> int:
    """blueprint_id 传播核心逻辑（公共，cmd_propagate_rename 和 cmd_rename_blueprint_id 共享）。

    传播表：
    1. nodes.blueprint_id（精确值映射）
    2. blueprint_links.blueprint_id（精确值映射）
    3. nodes.type_specific_data（可选，安全字符串替换）
    4. nodes.blueprint_path（可选，安全字符串替换）

    返回受影响总行数。
    """
    mode = "[DRY RUN]" if dry_run else "[OK]"
    total = 0

    # 1. nodes.blueprint_id 精确值映射
    cnt = c.execute("SELECT COUNT(*) FROM nodes WHERE blueprint_id=%s", (old_bp_id,)).fetchone()["count"]  # noqa: bare-sql  治理DBA脚本存量参数化查询，format重排伪新增（§5.160.2集中化专项另列）
    if cnt > 0:
        print(f"  {mode} nodes.blueprint_id: {old_bp_id} -> {new_bp_id}: {cnt} rows", file=sys.stderr)
        if not dry_run:
            c.execute(
                SQL_UPDATE_NODE_BLUEPRINT_ID,
                (new_bp_id, old_bp_id),
            )
        total += cnt

    # 2. blueprint_links.blueprint_id 精确值映射
    try:
        cnt = c.execute(SQL_COUNT_BLUEPRINT_LINKS_BY_ID, (old_bp_id,)).fetchone()["count"]
    except psycopg2.Error:
        cnt = 0
    if cnt > 0:
        print(f"  {mode} blueprint_links.blueprint_id: {old_bp_id} -> {new_bp_id}: {cnt} rows", file=sys.stderr)
        if not dry_run:
            c.execute(
                SQL_UPDATE_BLUEPRINT_LINK_ID,
                (new_bp_id, old_bp_id),
            )
        total += cnt

    # 3. nodes.type_specific_data 级联清理（可选）
    if propagate_tsd:
        # P2 PG 迁移：GLOB → LIKE（PG 不支持 GLOB；* 通配符 → % 通配符）
        tsd_rows = c.execute(
            "SELECT node_id, type_specific_data FROM nodes WHERE type_specific_data LIKE %s",
            (f"%{old_bp_id}%",),
        ).fetchall()
        tsd_cnt = 0
        for row in tsd_rows:
            node_id = row["node_id"]
            tsd = row["type_specific_data"]
            if not tsd:
                continue
            new_tsd = _safe_bp_id_replace(tsd, old_bp_id, new_bp_id)
            if new_tsd != tsd:
                if not dry_run:
                    c.execute(
                        SQL_UPDATE_NODE_TSD,
                        (new_tsd, node_id),
                    )
                tsd_cnt += 1
        if tsd_cnt > 0:
            print(f"  {mode} nodes.type_specific_data: {old_bp_id} -> {new_bp_id}: {tsd_cnt} rows", file=sys.stderr)
            total += tsd_cnt

    # 4. nodes.blueprint_path 级联清理（可选）
    if propagate_bp_path:
        # P2 PG 迁移：GLOB → LIKE（PG 不支持 GLOB；* 通配符 → % 通配符）
        bp_path_rows = c.execute(
            "SELECT node_id, blueprint_path FROM nodes WHERE blueprint_path LIKE %s",
            (f"%{old_bp_id}%",),
        ).fetchall()
        bp_cnt = 0
        for row in bp_path_rows:
            node_id = row["node_id"]
            bp_path = row["blueprint_path"]
            if not bp_path:
                continue
            new_path = _safe_bp_id_replace(bp_path, old_bp_id, new_bp_id)
            if new_path != bp_path:
                if not dry_run:
                    c.execute(
                        SQL_UPDATE_NODE_BP_PATH,
                        (new_path, node_id),
                    )
                bp_cnt += 1
        if bp_cnt > 0:
            print(f"  {mode} nodes.blueprint_path: {old_bp_id} -> {new_bp_id}: {bp_cnt} rows", file=sys.stderr)
            total += bp_cnt

    return total


def _scan_yaml_bp_id_refs(bp_id: str, search_root: Path = Path("docs")) -> list[tuple[str, int]]:
    """扫描 YAML 文件中的 blueprint_id 引用，返回 [(相对路径, 命中数), ...]。

    用于 cmd_rename_blueprint_id 执行后检测 YAML 真源是否需要同步。
    使用负向前瞻正则（同 _safe_bp_id_replace），避免误匹配
    （如 MOD-SHARED 不匹配 MOD-SHARED-001）。
    """
    pattern = re.compile(re.escape(bp_id) + r"(?![A-Za-z0-9_-])")
    refs: list[tuple[str, int]] = []
    for ext in ("*.yaml", "*.yml"):
        for yaml_path in search_root.rglob(ext):
            try:
                content = yaml_path.read_text(encoding="utf-8")
                matches = len(pattern.findall(content))
                if matches > 0:
                    rel = str(yaml_path).replace("\\", "/")
                    refs.append((rel, matches))
            except (OSError, UnicodeDecodeError):
                continue
    return refs


def cmd_rename_blueprint_id(
    old_bp_id: str,
    new_bp_id: str,
    dry_run: bool = False,
    db_path: str = None,
    conn=None,
) -> int:
    """blueprint_id 独立重命名（裁定#208 阶段D2：跨域共享模块 SH-* 改名专用）。

    与 cmd_propagate_rename 的区别：
    - cmd_propagate_rename 从 domain_id 派生 blueprint_id 映射（域改名专用，硬编码 _RENAME_MAP_204）
    - cmd_rename_blueprint_id 直接接受 old/new blueprint_id（独立改名，不依赖域改名）

    传播表（4 类）：
    1. nodes.blueprint_id（精确值映射）
    2. blueprint_links.blueprint_id（精确值映射，需触发器通行证）
    3. nodes.type_specific_data（JSON 中 module_id 字段 + doc_references 数组，安全字符串替换）
    4. nodes.blueprint_path（路径中的 ID 片段，安全字符串替换）

    安全保证：_safe_bp_id_replace 使用负向前瞻 (?![A-Za-z0-9_-])，
    确保 MOD-SHARED 不会误匹配 MOD-SHARED-001。

    返回受影响总行数，-1=失败。
    """
    # V2 漏洞修复：new_bp_id 必须符合裁定#208 双轨制格式（R2 治本修订后）
    # old_bp_id 不校验（DB 中可能存在历史遗留的不合规 ID，需要允许改名到合规格式）
    # R2 治本修订（2026-07-05）：D-XXX-NNN 已废弃为 module_id 派生轨，重定义为 submodule_id 专用
    ok, reason = _validate_bp_id_format(new_bp_id)
    if not ok:
        print(
            f"ERROR: new_bp_id '{new_bp_id}' 格式不合规：{reason}\n"
            f"裁定#208 双轨制（R2 治本修订后）：layer-master 轨(MOD-{{LAYER}}-NNN) / 派生轨(MOD-{{DOMAIN}}[-NNN]) / 跨域共享轨(SH-{{ABBR}}-NNN)；D-XXX-NNN 已废弃为 module_id 派生轨，重定义为 submodule_id 专用(见 trae_028 gov_doc_009)",
            file=sys.stderr,
        )
        return -1

    own_conn = conn is None

    def _run(c) -> int:
        """_run implementation."""
        mode = "[DRY RUN]" if dry_run else "[OK]"
        total = _propagate_bp_id_core(
            c,
            old_bp_id,
            new_bp_id,
            dry_run,
            propagate_tsd=True,
            propagate_bp_path=True,
        )
        if not dry_run and own_conn:
            c.commit()
        print(f"{mode} cmd_rename_blueprint_id: total {total} rows", file=sys.stderr)
        # 治本：DB 改名后自动扫描 YAML 真源引用，防止 sync_yaml_to_depgraph.py 回滚
        if not dry_run and total > 0:
            yaml_refs = _scan_yaml_bp_id_refs(old_bp_id)
            if yaml_refs:
                total_refs = sum(cnt for _, cnt in yaml_refs)
                print(
                    f"\n[YAML SYNC WARNING] DB 改名已完成，但 {len(yaml_refs)} 个 YAML 文件仍引用旧 ID '{old_bp_id}'（共 {total_refs} 处）：",
                    file=sys.stderr,
                )
                for f, cnt in yaml_refs:
                    print(f"  {f}: {cnt} 处", file=sys.stderr)
                print("  必须同步这些 YAML 文件，否则 sync_yaml_to_depgraph.py 会回滚 DB 改名成果。", file=sys.stderr)
                print(
                    "  注意: 历史记录（changelog/version history）中的旧 ID 保留不动，只改当前数据。", file=sys.stderr
                )
            else:
                print(f"[YAML SYNC OK] 未发现 YAML 文件引用旧 ID '{old_bp_id}'，无需同步。", file=sys.stderr)
            # 提醒 .md 和 .py 的同步（独立于 YAML，已有专用工具，避免 AI 遗漏）
            print(
                "[SYNC HINT] .md frontmatter 用 sync_registry_from_blueprints.py 同步；.py 头部 [BLUEPRINT] 标记用 check_blueprint_code_alignment.py 验证。",
                file=sys.stderr,
            )
        return total

    if dry_run:
        c = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True) if own_conn else conn
        if own_conn:
            pass  # P2 PG: PRAGMA 已删除（PG 不需要）
            pass  # P2 PG: PRAGMA 已删除（PG 不需要）
        try:
            return _run(c)
        finally:
            if own_conn:
                c.close()
    else:
        with _optional_db_lock(own_conn, task="rename_blueprint_id", db_path=db_path):
            c = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True) if own_conn else conn
            if own_conn:
                pass  # P2 PG: PRAGMA 已删除（PG 不需要）
                pass  # P2 PG: PRAGMA 已删除（PG 不需要）
            # 临时禁用 blueprint_links 只读触发器（裁定#207 R1 B2 通行证机制）
            c.execute(SQL_DROP_READONLY_TRIGGER)
            try:
                n = _run(c)
                # 成功后恢复只读触发器并 commit
                _restore_blueprint_links_readonly_trigger(c)
                if own_conn:
                    c.commit()
                return n
            except Exception as e:
                if own_conn:
                    c.rollback()
                logger.error("cmd_rename_blueprint_id失败: %s", e)
                # 异常时也恢复只读触发器（保持门禁激活）
                try:
                    _restore_blueprint_links_readonly_trigger(c)
                    if own_conn:
                        c.commit()
                except psycopg2.Error as restore_err:
                    logger.warning("恢复 blueprint_links 只读触发器失败（门禁可能遗留禁用状态）: %s", restore_err)
                return -1
            finally:
                if own_conn:
                    c.close()


def cmd_set_blueprint_id(
    path: str,
    new_bp_id: str,
    dry_run: bool = False,
    db_path: str = None,
    conn=None,
) -> int:
    """按 path 给节点赋值 blueprint_id（裁定#209 Stage 2 path 为稳定 PK）。

    专为 blueprint_id 为空/NULL 的节点设计——这类节点无法用 --rename-blueprint-id
    （old_bp_id='' 会匹配全库所有空值节点，误伤 385 个 production 空值节点）。
    本函数按 path 精确赋值，是唯一的 sanctioned 路径赋值入口。

    与 --rename-blueprint-id 的区别：
    - rename: 按 old_bp_id 值映射（old→new），处理 4 类传播表
    - set:    按 path 精确赋值（空→new），传播仅限 nodes.blueprint_id + belongs_to
              + nodes_metadata.blueprint_id（这类节点 type_specific_data 无 module_id
              字段、blueprint_path 为 NULL，无需 4 类传播）

    安全保证：
    - new_bp_id 必须通过 is_valid_module_id（裁定#208 双轨制三轨）
    - path 必须命中一个节点（path 是稳定 PK）
    - _db_write_lock 互斥保护（与 generate_project_depgraph 共享 lock key 424242）
    - dry_run 只读不写
    - belongs_to 同步设为 new_bp_id（与 file-module 惯例 blueprint_id==belongs_to 对齐）

    返回受影响 nodes 行数，-1=失败。
    """
    # 校验 new_bp_id 格式（权威真源 is_valid_module_id，裁定#208 R2）
    ok, reason = _validate_bp_id_format(new_bp_id)
    if not ok:
        print(
            f"ERROR: new_bp_id '{new_bp_id}' 格式不合规：{reason}\n"
            f"裁定#208 双轨制：MOD-{{LAYER}}-NNN / MOD-{{DOMAIN}}[-NNN] / SH-{{ABBR}}-NNN",
            file=sys.stderr,
        )
        return -1

    own_conn = conn is None

    def _run(c) -> int:
        """_run implementation."""
        row = c.execute(SQL_SELECT_NODE_FULL_BY_PATH, (path,)).fetchone()
        if not row:
            print(f"ERROR: path='{path}' 在 nodes 表中不存在", file=sys.stderr)
            return -1
        old_bp = row["blueprint_id"] or ""
        old_bt = row["belongs_to"] or ""
        mode = "[DRY RUN]" if dry_run else "[OK]"
        print(f"{mode} set_blueprint_id: path={path}", file=sys.stderr)
        print(f"  blueprint_id: '{old_bp}' -> '{new_bp_id}'", file=sys.stderr)
        print(f"  belongs_to:   '{old_bt}' -> '{new_bp_id}'  (与 blueprint_id 对齐)", file=sys.stderr)
        if dry_run:
            return 1
        c.execute(SQL_UPDATE_NODE_BLUEPRINT_ID_BY_PATH, (new_bp_id, new_bp_id, path))
        c.execute(SQL_CLEAR_BLUEPRINT_ID_INVALID_BY_PATH, (path,))
        c.execute(
            SQL_UPDATE_NODES_METADATA_BP_BY_PATH,
            (new_bp_id, datetime.datetime.now().isoformat(), path),
        )
        if own_conn:
            c.commit()
        print("  [OK] nodes + nodes_metadata 已更新，blueprint_id_invalid 已清除", file=sys.stderr)
        return 1

    if dry_run:
        c = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True) if own_conn else conn
        try:
            return _run(c)
        finally:
            if own_conn:
                c.close()
    else:
        with _optional_db_lock(own_conn, task="set_blueprint_id", db_path=db_path):
            c = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True) if own_conn else conn
            try:
                return _run(c)
            except Exception as e:
                if own_conn:
                    c.rollback()
                logger.error("cmd_set_blueprint_id失败: %s", e)
                return -1
            finally:
                if own_conn:
                    c.close()


def cmd_propagate_node_paths(
    path_mapping: dict[str, str],
    bl_mapping: dict[str, str] | None = None,
    dry_run: bool = False,
    db_path: str = None,
    conn=None,
) -> int:
    """节点路径改名传播（裁定#206 节点路径派生 + 裁定#207 R1 阶段D）。

    根据 D2 重新编号映射，精确值映射 nodes.path、nodes.file_path 与 blueprint_links.blueprint_path。
    派生关系：节点路径域片段派生自 domain_id，序号按域内 old_seq 升序连续编号（01起）。
    传播表：nodes.path + nodes.file_path（无只读触发器），blueprint_links.blueprint_path（需触发器通行证）。

    精确值映射：禁止子串REPLACE，避免误伤（如 D-SIGNAL-1 误匹配 D-SIGNAL-10）。
    返回受影响总行数，-1=失败。
    """
    own_conn = conn is None
    bl_mapping = bl_mapping or {}

    def _run(c) -> int:
        """_run implementation."""
        mode = "[DRY RUN]" if dry_run else "[OK]"
        total = 0

        # 1. nodes.path 精确值映射（无只读触发器，可直接 UPDATE）
        for old_path, new_path in path_mapping.items():
            cnt = c.execute(SQL_COUNT_NODES_BY_PATH, (old_path,)).fetchone()["count"]
            if cnt > 0:
                print(
                    f"  {mode} nodes.path: {old_path} -> {new_path}: {cnt} rows",
                    file=sys.stderr,
                )
                if not dry_run:
                    c.execute(SQL_UPDATE_NODE_PATH_BY_PATH, (new_path, old_path))
                total += cnt

        # 1b. nodes.file_path 精确值映射（与 path 同步传播，避免改名后 file_path 残留）
        for old_path, new_path in path_mapping.items():
            cnt = c.execute(SQL_COUNT_NODES_BY_FILE_PATH, (old_path,)).fetchone()["count"]
            if cnt > 0:
                print(
                    f"  {mode} nodes.file_path: {old_path} -> {new_path}: {cnt} rows",
                    file=sys.stderr,
                )
                if not dry_run:
                    c.execute(SQL_UPDATE_NODE_FILE_PATH, (new_path, old_path))
                total += cnt

        # 2. blueprint_links.blueprint_path 精确值映射（需触发器通行证）
        for old_path, new_path in bl_mapping.items():
            cnt = c.execute(
                SQL_COUNT_BLUEPRINT_LINKS_BY_BP_PATH,
                (old_path,),
            ).fetchone()["count"]
            if cnt > 0:
                print(
                    f"  {mode} blueprint_links.blueprint_path: {old_path} -> {new_path}: {cnt} rows",
                    file=sys.stderr,
                )
                if not dry_run:
                    c.execute(
                        SQL_UPDATE_BLUEPRINT_LINK_BP_PATH,
                        (new_path, old_path),
                    )
                total += cnt

        if not dry_run and own_conn:
            c.commit()
        print(f"{mode} cmd_propagate_node_paths: total {total} rows", file=sys.stderr)
        return total

    if dry_run:
        c = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True) if own_conn else conn
        if own_conn:
            pass  # P2 PG: PRAGMA 已删除（PG 不需要）
            pass  # P2 PG: PRAGMA 已删除（PG 不需要）
        try:
            return _run(c)
        finally:
            if own_conn:
                c.close()
    else:
        with _optional_db_lock(own_conn, task="propagate_node_paths", db_path=db_path):
            c = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True) if own_conn else conn
            if own_conn:
                pass  # P2 PG: PRAGMA 已删除（PG 不需要）
                pass  # P2 PG: PRAGMA 已删除（PG 不需要）
            # 临时禁用 blueprint_links 只读触发器（仅当有 bl_mapping 时）
            if bl_mapping:
                c.execute(SQL_DROP_READONLY_TRIGGER)
            try:
                n = _run(c)
                # 成功后恢复只读触发器并 commit
                if bl_mapping:
                    _restore_blueprint_links_readonly_trigger(c)
                if own_conn:
                    c.commit()
                return n
            except Exception as e:
                if own_conn:
                    c.rollback()
                logger.error("cmd_propagate_node_paths失败: %s", e)
                # 异常时也恢复只读触发器（保持门禁激活）
                try:
                    if bl_mapping:
                        _restore_blueprint_links_readonly_trigger(c)
                    if own_conn:
                        c.commit()
                except psycopg2.Error as restore_err:
                    logger.warning("恢复 blueprint_links 只读触发器失败（门禁可能遗留禁用状态）: %s", restore_err)
                return -1
            finally:
                if own_conn:
                    c.close()


def cmd_update_domain_name(
    domain_id: str,
    new_name: str,
    dry_run: bool = False,
    db_path: str = None,
    conn=None,
) -> int:
    """更新 domains.domain_name（裁定#204 配套）。返回受影响行数，-1=失败。"""
    own_conn = conn is None

    def _run(c) -> int:
        """_run implementation."""
        row = c.execute(SQL_SELECT_DOMAIN_NAME_BY_ID, (domain_id,)).fetchone()
        if not row:
            print(f"ERROR: domain_id '{domain_id}' 不在 domains 表中", file=sys.stderr)
            return -1
        mode = "[DRY RUN]" if dry_run else "[OK]"
        print(f"  {mode} domains.domain_name: '{row['domain_name']}' -> '{new_name}'", file=sys.stderr)
        if dry_run:
            return EXIT_FINDINGS
        cur = c.execute(SQL_UPDATE_DOMAIN_NAME, (new_name, domain_id))
        if own_conn:
            c.commit()
        return cur.rowcount

    if dry_run:
        c = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True) if own_conn else conn
        try:
            return _run(c)
        finally:
            if own_conn:
                c.close()
    else:
        with _optional_db_lock(own_conn, task="update_domain_name", db_path=db_path):
            c = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True) if own_conn else conn
            try:
                return _run(c)
            except Exception as e:
                if own_conn:
                    c.rollback()
                logger.error("cmd_update_domain_name失败: %s", e)
                return -1
            finally:
                if own_conn:
                    c.close()


def cmd_migrate_nodes(
    node_ids: list[int], new_domain_id: str, dry_run: bool = False, db_path: str = None, conn=None
) -> int:
    """按 node_id 列表精确迁移 domain_id（不依赖 blueprint_id/belongs_to 匹配）。
    解决跨域共享 blueprint_id 误迁问题（附录D裁定1）。
    返回：受影响行数，-1=失败
    """
    if not node_ids:
        print("ERROR: node_ids 列表为空", file=sys.stderr)
        return -1
    own_conn = conn is None
    with _optional_db_lock(own_conn, task="cmd_migrate_nodes", db_path=db_path):
        if own_conn:
            conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        try:
            domain = conn.execute(SQL_SELECT_DOMAIN_ID_BY_DOMAIN_ID, (new_domain_id,)).fetchone()
            if not domain:
                print(f"ERROR: new_domain_id '{new_domain_id}' 不在 domains 表中", file=sys.stderr)
                return -1
            placeholders = ",".join(["%s"] * len(node_ids))  # 修复: ",".join("%s"*n) 在 n>1 时产生 %, 坏占位符（存量 bug，#ARCH-169 实证）
            rows = conn.execute(
                f"SELECT node_id, path, domain_id FROM nodes WHERE node_id IN ({placeholders})",  # 5.160.2 OK: dynamic SQL, kept inline
                node_ids,
            ).fetchall()
            if not rows:
                print(f"ERROR: node_ids {node_ids} 未找到匹配节点", file=sys.stderr)
                return -1
            if dry_run:
                for r in rows:
                    print(
                        f"[DRY RUN] 将 UPDATE node_id={r['node_id']} domain_id: {r['domain_id']} -> {new_domain_id} (path={r['path']})",
                        file=sys.stderr,
                    )
                return len(rows)
            cur = conn.execute(
                f"UPDATE nodes SET domain_id=%s WHERE node_id IN ({placeholders})",  # 5.160.2 OK: dynamic SQL, kept inline
                [new_domain_id] + node_ids,
            )
            if own_conn:
                conn.commit()
            print(f"[OK] UPDATE {cur.rowcount} 个节点 domain_id -> {new_domain_id}", file=sys.stderr)
            return cur.rowcount
        except Exception as e:
            if own_conn:
                conn.rollback()
            logger.error("cmd_migrate_nodes失败: %s", e)
            return -1
        finally:
            if own_conn:
                conn.close()


def cmd_tag_nodes(
    node_ids: list[int],
    tag: str,
    remove: bool = False,
    dry_run: bool = False,
    db_path: str = None,
    conn=None,
) -> int:
    """按 node_id 列表为 nodes.tags 添加/移除横切标签（逗号分隔串格式，幂等）。

    用途：AI 层横切视图打标（03号文分支C裁定执行，#ARCH-169）。
    tags 存储格式沿用存量逗号分隔串约定（如 'ARCH-052,aggregate_node'）。
    返回：受影响行数，-1=失败
    """
    if not node_ids:
        print("ERROR: node_ids 列表为空", file=sys.stderr)
        return -1
    if not tag or "," in tag:
        print(f"ERROR: tag 非法（空或含逗号）: {tag!r}", file=sys.stderr)
        return -1
    own_conn = conn is None
    with _optional_db_lock(own_conn, task="cmd_tag_nodes", db_path=db_path):
        if own_conn:
            conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        try:
            changed = 0
            for nid in node_ids:
                row = conn.execute(SQL_SELECT_TAGS_BY_NODE, (nid,)).fetchone()
                if not row:
                    print(f"ERROR: node_id={nid} 不存在", file=sys.stderr)
                    if own_conn:
                        conn.rollback()
                    return -1
                current = row["tags"] or ""
                parts = [p for p in current.split(",") if p]
                if remove:
                    if tag not in parts:
                        continue
                    new_tags = ",".join(p for p in parts if p != tag)
                else:
                    if tag in parts:
                        continue
                    new_tags = ",".join(parts + [tag])
                if dry_run:
                    print(f"[DRY RUN] 将 UPDATE node_id={nid} tags: {current!r} -> {new_tags!r}", file=sys.stderr)
                else:
                    conn.execute(SQL_UPDATE_TAGS_BY_NODE, (new_tags, nid))
                changed += 1
            if dry_run:
                return changed
            if own_conn:
                conn.commit()
            action = "移除" if remove else "添加"
            print(f"[OK] {action}标签 {tag!r}: {changed} 个节点", file=sys.stderr)
            return changed
        except Exception as e:
            if own_conn:
                conn.rollback()
            logger.error("cmd_tag_nodes失败: %s", e)
            return -1
        finally:
            if own_conn:
                conn.close()


def cmd_delete_nodes(
    node_ids: list[int], force: bool = False, dry_run: bool = False, db_path: str = None, conn=None
) -> int:
    """按 node_id 列表精确删除节点（含关联 edges）。

    安全门：检查入边（被依赖），有入边则阻断（除非 --force）。
    用途：删除测试 mock 数据等噪声节点（如 tests/fixtures/）。
    返回：删除的节点数，-1=失败。

    注意：已由 backup_pg_architecture() 自动 PG 备份（trae_054 v1.6.0 STEP0，写入后事件触发，非 git commit）。
    """
    if not node_ids:
        print("ERROR: node_ids 列表为空", file=sys.stderr)
        return -1
    own_conn = conn is None
    with _optional_db_lock(own_conn, task="cmd_delete_nodes", db_path=db_path):
        if own_conn:
            conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        try:
            cur = conn.cursor()
            placeholders = ",".join(["%s"] * len(node_ids))
            ids_tuple = tuple(node_ids)

            # 查询节点信息
            cur.execute(
                SQL_DELETE_NODES_SELECT_BY_IDS.format(placeholders),
                ids_tuple,
            )
            rows = cur.fetchall()
            if not rows:
                print(f"ERROR: node_ids {node_ids} 未找到匹配节点", file=sys.stderr)
                return -1

            # 安全门：检查入边（被依赖）
            cur.execute(
                SQL_DELETE_NODES_COUNT_IN_EDGES.format(placeholders),
                ids_tuple,
            )
            in_edge_count = cur.fetchone()["cnt"]
            if in_edge_count > 0 and not force:
                print(
                    f"ERROR: {in_edge_count} 条入边引用目标节点（被依赖），拒绝删除。请先清理依赖关系或使用 --force",
                    file=sys.stderr,
                )
                return -1

            if dry_run:
                for r in rows:
                    print(
                        f"[DRY RUN] 将 DELETE node_id={r['node_id']} domain_id={r['domain_id']} path={r['path']}",
                        file=sys.stderr,
                    )
                return len(rows)

            # S5 锚点级联提示（非阻断）
            _cascade_anchor_hint(conn, node_ids, op="cmd_delete_nodes")

            # 先删除关联 edges（出边+入边）
            cur.execute(
                SQL_DELETE_NODES_DELETE_EDGES_BY_IDS.format(placeholders),
                ids_tuple + ids_tuple,
            )
            edge_count = cur.rowcount
            # 再删除 nodes
            cur.execute(
                SQL_DELETE_NODES_DELETE_BY_IDS.format(placeholders),
                ids_tuple,
            )
            deleted = cur.rowcount
            if own_conn:
                conn.commit()
            print(
                f"[OK] DELETE {deleted} 个节点（及 {edge_count} 条关联 edges）",
                file=sys.stderr,
            )
            return deleted
        except Exception as e:
            if own_conn:
                conn.rollback()
            logger.error("cmd_delete_nodes失败: %s", e)
            return -1
        finally:
            if own_conn:
                conn.close()


def cmd_update_path(
    module_id: str, old_prefix: str, new_prefix: str, dry_run: bool = False, db_path: str = None, conn=None
) -> int:
    """UPDATE 模块的 path（物理路径迁移，ARCH-CAP-004 路径平铺）。

    修复: 原实现把同模块所有节点 path 设成同一个值，触发 UNIQUE 冲突。
    现在: 对每个节点的 path 做前缀替换（old_prefix → new_prefix），保持文件相对路径不变。

    按 belongs_to 或 blueprint_id 匹配节点。
    如果提供 conn 参数，使用该连接（不 commit/close）——用于 cmd_batch 统一事务。
    返回：受影响行数，-1=失败
    """
    own_conn = conn is None
    with _optional_db_lock(own_conn, task="cmd_update_path", db_path=db_path):
        if own_conn:
            conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        try:
            rows = conn.execute(SQL_SELECT_NODE_PATH_BY_MODULE, (module_id, module_id)).fetchall()
            if not rows:
                print(f"ERROR: module_id '{module_id}' 未找到匹配节点", file=sys.stderr)
                return -1

            # 计算每个节点的新 path（前缀替换）
            updates = []
            skipped = 0
            for r in rows:
                old_path = r["path"] or ""
                if old_path.startswith(old_prefix):
                    new_path = new_prefix + old_path[len(old_prefix) :]
                    updates.append((r["node_id"], old_path, new_path))
                else:
                    skipped += 1
                    if dry_run:
                        print(
                            f"[DRY RUN] SKIP node_id={r['node_id']} path={old_path} (不以 old_prefix 开头)",
                            file=sys.stderr,
                        )

            if skipped > 0:
                print(f"WARNING: {skipped} 个节点 path 不以 '{old_prefix}' 开头，已跳过", file=sys.stderr)

            if not updates:
                print("WARNING: 没有需要更新的节点（全部跳过）", file=sys.stderr)
                return EXIT_PASS
            if dry_run:
                for node_id, old_path, new_path in updates:
                    print(f"[DRY RUN] 将 UPDATE node_id={node_id} path: {old_path} -> {new_path}", file=sys.stderr)
                return len(updates)

            # 逐个 UPDATE（每个节点的新 path 不同）
            affected = 0
            for node_id, old_path, new_path in updates:
                cur = conn.execute(
                    SQL_UPDATE_NODE_PATH_BY_ID,
                    (new_path, new_path, node_id),
                )
                affected += cur.rowcount

            if own_conn:
                conn.commit()
            print(f"[OK] UPDATE {affected} 个节点 path 前缀替换: {old_prefix} -> {new_prefix}", file=sys.stderr)
            return affected
        except Exception as e:
            if own_conn:
                conn.rollback()
            logger.error("cmd_update_path失败: %s", e)
            return -1
        finally:
            if own_conn:
                conn.close()


def cmd_migrate_dependencies(
    from_domain: str,
    to_domain: str,
    new_from_domain: str = "",
    new_to_domain: str = "",
    dry_run: bool = False,
    db_path: str = None,
    conn=None,
) -> int:
    """UPDATE domain_dependencies 表迁移跨域依赖。

    new_from_domain 非空 → 更新 from_domain
    new_to_domain 非空 → 更新 to_domain
    若目标依赖已存在则合并 edge_count。
    如果提供 conn 参数，使用该连接（不 commit/close）——用于 cmd_batch 统一事务。
    返回：受影响行数，-1=失败
    """
    if not new_from_domain and not new_to_domain:
        print("ERROR: 必须指定 --new-from-domain 或 --new-to-domain", file=sys.stderr)
        return -1

    own_conn = conn is None
    with _optional_db_lock(own_conn, task="cmd_migrate_dependencies", db_path=db_path):
        if own_conn:
            conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        try:
            rows = conn.execute(
                SQL_SELECT_DOMAIN_DEP_BY_PAIR,
                (from_domain, to_domain),
            ).fetchall()
            if not rows:
                print(f"ERROR: domain_dependencies ({from_domain} -> {to_domain}) 不存在", file=sys.stderr)
                return -1

            if new_from_domain:
                d = conn.execute(SQL_SELECT_DOMAIN_ID_BY_DOMAIN_ID, (new_from_domain,)).fetchone()
                if not d:
                    print(f"ERROR: new_from_domain '{new_from_domain}' 不在 domains 表中", file=sys.stderr)
                    return -1
            if new_to_domain:
                d = conn.execute(SQL_SELECT_DOMAIN_ID_BY_DOMAIN_ID, (new_to_domain,)).fetchone()
                if not d:
                    print(f"ERROR: new_to_domain '{new_to_domain}' 不在 domains 表中", file=sys.stderr)
                    return -1

            final_from = new_from_domain or from_domain
            final_to = new_to_domain or to_domain

            if dry_run:
                for r in rows:
                    print(
                        f"[DRY RUN] 将 UPDATE domain_dependencies: {r['from_domain']} -> {r['to_domain']} => {final_from} -> {final_to} (edge_count={r['edge_count']})",
                        file=sys.stderr,
                    )
                return len(rows)

            existing = conn.execute(SQL_SELECT_DOMAIN_DEP_EDGE_COUNT, (final_from, final_to)).fetchone()

            if existing and (final_from != from_domain or final_to != to_domain):
                total = existing["edge_count"] + rows[0]["edge_count"]
                conn.execute(SQL_DELETE_DOMAIN_DEP, (from_domain, to_domain))
                conn.execute(
                    SQL_UPDATE_DOMAIN_DEP_EDGE_COUNT,
                    (total, final_from, final_to),
                )
                print(
                    f"[OK] 合并 domain_dependencies: {from_domain}->{to_domain} 并入 {final_from}->{final_to} (edge_count={total})",
                    file=sys.stderr,
                )
            else:
                conn.execute(
                    SQL_UPDATE_DOMAIN_DEP_PAIR,
                    (final_from, final_to, from_domain, to_domain),
                )
                print(
                    f"[OK] UPDATE domain_dependencies: {from_domain}->{to_domain} => {final_from}->{final_to}",
                    file=sys.stderr,
                )

            if own_conn:
                conn.commit()
            return len(rows)
        except Exception as e:
            if own_conn:
                conn.rollback()
            logger.error("cmd_migrate_dependencies失败: %s", e)
            return -1
        finally:
            if own_conn:
                conn.close()


def cmd_update_domain_capacity(
    domain_id: str, field: str, value: int, dry_run: bool = False, db_path: str = None, conn=None
) -> bool:
    """UPDATE domains 表的容量字段（current_modules/max_modules）。

    ARCH-CAP-001 要求 current_modules 按 production 节点口径统计。
    域拆分后需要修正容量数据，本命令提供 F5 合规的写入接口。
    如果提供 conn 参数，使用该连接（不 commit/close）——用于 cmd_batch 统一事务。
    返回：True=成功，False=失败
    """
    ALLOWED_FIELDS = {"current_modules", "max_modules", "production_nodes"}
    FIELD_ALIASES = {"current": "current_modules", "max": "max_modules", "prod": "production_nodes"}
    field = FIELD_ALIASES.get(field, field)
    if field not in ALLOWED_FIELDS:
        print(f"ERROR: field 必须是 {ALLOWED_FIELDS} 之一（或简写 current/max），实际: {field}", file=sys.stderr)
        return False

    if value < 0:
        print(f"ERROR: value 必须是非负整数，实际: {value}", file=sys.stderr)
        return False

    own_conn = conn is None
    with _optional_db_lock(own_conn, task="cmd_update_domain_capacity", db_path=db_path):
        if own_conn:
            conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        try:
            existing = conn.execute(
                SQL_SELECT_DOMAIN_CAPACITY,
                (domain_id,),
            ).fetchone()
            if not existing:
                print(f"ERROR: domain_id '{domain_id}' 不在 domains 表中", file=sys.stderr)
                return False

            field_idx = {"current_modules": 1, "max_modules": 2, "production_nodes": 3}
            old_value = existing[field_idx[field]]
            if dry_run:
                print(f"[DRY RUN] 将 UPDATE domains {field}: {domain_id} {old_value} -> {value}", file=sys.stderr)
                return True

            now = datetime.datetime.now().isoformat()
            conn.execute(
                SQL_UPDATE_DOMAIN_FIELD_DYNAMIC.format(field=field), (value, now, domain_id)
            )  # 5.160.2 OK: 动态标识符经 SQL_* 模板常量
            if own_conn:
                conn.commit()
            print(f"[OK] UPDATE domains {field}: {domain_id} {old_value} -> {value}", file=sys.stderr)
            return True
        except Exception as e:
            if own_conn:
                conn.rollback()
            logger.error("cmd_update_domain_capacity失败: %s", e)
            return False
        finally:
            if own_conn:
                conn.close()


def cmd_update_domain_layer(
    domain_id: str, layer_id: str, dry_run: bool = False, db_path: str = None, conn=None
) -> bool:
    """UPDATE domains 表的 layer_id 字段（架构层级迁移）。

    ARCH-001 向下依赖原则要求 L2→L1→L0。当域的实际职责属于平台层时，
    需要通过本命令调整 layer_id 以消除违规向上依赖。
    如果提供 conn 参数，使用该连接（不 commit/close）——用于 cmd_batch 统一事务。
    返回：True=成功，False=失败
    """
    # 域层级 ID 合法值（非词表，是 cmd_update_domain_layer 函数参数校验；
    # 无对应 vocabulary YAML，是架构层级概念而非受控词表。GATE-VOCAB noqa 豁免）
    ALLOWED_LAYERS = {"L0_infrastructure", "L1_foundation", "L2_domain", "L3_application"}  # noqa: gate-vocab  gate-vocab豁免: 架构层级概念非受控词表
    if layer_id not in ALLOWED_LAYERS:
        print(f"ERROR: layer_id 必须是 {ALLOWED_LAYERS} 之一，实际: {layer_id}", file=sys.stderr)
        return False

    own_conn = conn is None
    with _optional_db_lock(own_conn, task="cmd_update_domain_layer", db_path=db_path):
        if own_conn:
            conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        try:
            existing = conn.execute(SQL_SELECT_DOMAIN_LAYER, (domain_id,)).fetchone()
            if not existing:
                print(f"ERROR: domain_id '{domain_id}' 不在 domains 表中", file=sys.stderr)
                return False

            old_layer = existing["layer_id"]
            if old_layer == layer_id:
                print(f"WARNING: domain_id '{domain_id}' layer_id 已是 {layer_id}，无需更新", file=sys.stderr)
                return True

            if dry_run:
                print(f"[DRY RUN] 将 UPDATE domains layer_id: {domain_id} {old_layer} -> {layer_id}", file=sys.stderr)
                return True

            now = datetime.datetime.now().isoformat()
            conn.execute(SQL_UPDATE_DOMAIN_LAYER, (layer_id, now, domain_id))
            if own_conn:
                conn.commit()
            print(f"[OK] UPDATE domains layer_id: {domain_id} {old_layer} -> {layer_id}", file=sys.stderr)
            return True
        except Exception as e:
            if own_conn:
                conn.rollback()
            logger.error("cmd_update_domain_layer失败: %s", e)
            return False
        finally:
            if own_conn:
                conn.close()


def cmd_update_domain_ssot_path(
    domain_id: str, ssot_path: str, dry_run: bool = False, db_path: str = None, conn=None
) -> bool:
    """UPDATE domains 表的 ssot_path 字段（附录D裁定2）。
    解决已存在域无法修正 ssot_path 的工具设计遗漏。
    返回：True=成功，False=失败
    """
    if not ssot_path.endswith("/"):
        print(f"ERROR: ssot_path 必须以 / 结尾（目录路径）: {ssot_path}", file=sys.stderr)
        return False
    own_conn = conn is None
    with _optional_db_lock(own_conn, task="cmd_update_domain_ssot_path", db_path=db_path):
        if own_conn:
            conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        try:
            existing = conn.execute(SQL_SELECT_DOMAIN_SSOT_PATH, (domain_id,)).fetchone()
            if not existing:
                print(f"ERROR: domain_id '{domain_id}' 不在 domains 表中", file=sys.stderr)
                return False
            old_path = existing["ssot_path"]
            if dry_run:
                print(f"[DRY RUN] 将 UPDATE domains ssot_path: {domain_id} {old_path} -> {ssot_path}", file=sys.stderr)
                return True
            now = datetime.datetime.now().isoformat()
            conn.execute(SQL_UPDATE_DOMAIN_SSOT_PATH, (ssot_path, now, domain_id))
            if own_conn:
                conn.commit()
            print(f"[OK] UPDATE domains ssot_path: {domain_id} {old_path} -> {ssot_path}", file=sys.stderr)
            return True
        except Exception as e:
            if own_conn:
                conn.rollback()
            logger.error("cmd_update_domain_ssot_path失败: %s", e)
            return False
        finally:
            if own_conn:
                conn.close()


def cmd_insert_domain_mapping(
    path_prefix: str,
    domain_id: str,
    mapping_type: str,
    subdomain_id: str = "",
    mapped_by: str = "",
    note: str = "",
    dry_run: bool = False,
    db_path: str = None,
    conn=None,
) -> bool:
    """INSERT 路径前缀→域映射到 domain_mapping 表（schema 盲区修复）。

    domain_mapping 表记录非 src/ 目录和未注册 src/ 路径的域归属，
    用于 generate_project_depgraph.py 将物理路径归入正确域。
    如果提供 conn 参数，使用该连接（不 commit/close）——用于 cmd_batch 统一事务。
    返回：True=成功，False=失败
    """
    # domain_mapping 表 mapping_type 合法值（非词表，是 cmd_insert_domain_mapping 函数参数校验；
    # 无对应 vocabulary YAML，是 schema 字段类型而非受控词表。GATE-VOCAB noqa 豁免）
    ALLOWED_TYPES = {"non_src", "unregistered_src"}  # noqa: gate-vocab  gate-vocab豁免: schema字段类型非受控词表
    if mapping_type not in ALLOWED_TYPES:
        print(
            f"ERROR: mapping_type 必须是 {ALLOWED_TYPES} 之一，实际: {mapping_type}",
            file=sys.stderr,
        )
        return False

    own_conn = conn is None
    with _optional_db_lock(own_conn, task="cmd_insert_domain_mapping", db_path=db_path):
        if own_conn:
            conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        try:
            # 校验 domain_id 存在
            domain = conn.execute(SQL_SELECT_DOMAIN_ID_BY_DOMAIN_ID, (domain_id,)).fetchone()
            if not domain:
                print(f"ERROR: domain_id '{domain_id}' 不在 domains 表中", file=sys.stderr)
                return False

            # 查重：path_prefix 已存在则拒绝（避免重复映射）
            existing = conn.execute(SQL_SELECT_DOMAIN_MAPPING_BY_PREFIX, (path_prefix,)).fetchone()
            if existing:
                print(
                    f"ERROR: path_prefix '{path_prefix}' 已存在映射 (mapping_id={existing['mapping_id']}, domain_id={existing['domain_id']})",
                    file=sys.stderr,
                )
                return False

            if dry_run:
                print(
                    f"[DRY RUN] 将 INSERT domain_mapping: path_prefix={path_prefix} domain_id={domain_id} "
                    f"subdomain_id={subdomain_id or '(空)'} mapping_type={mapping_type}",
                    file=sys.stderr,
                )
                return True

            now = datetime.datetime.now().isoformat()
            conn.execute(
                SQL_INSERT_DOMAIN_MAPPING,
                (path_prefix, domain_id, subdomain_id or None, mapping_type, now, mapped_by, note or None),
            )
            if own_conn:
                conn.commit()
            print(
                f"[OK] INSERT domain_mapping: {path_prefix} -> {domain_id} ({mapping_type})",
                file=sys.stderr,
            )
            return True
        except Exception as e:
            if own_conn:
                conn.rollback()
            logger.error("cmd_insert_domain_mapping失败: %s", e)
            return False
        finally:
            if own_conn:
                conn.close()


# ===== 模块全景对齐（four_graph_module_alignment Step 3 Task 3.4）=====


def mark_entry_point(path: str, entry_flag: bool = True, db_path: str = None) -> bool:
    """标记文件级节点为入口文件（nodes.entry_point）。

    五图模块对齐 Step 3：为 nodes 表新增 entry_point 字段配套写入入口。
    入口文件 = 模块对外暴露的执行入口（如 __main__.py、CLI 入口、app.py）。

    :param path: 节点 path（nodes 表 PK 候选，唯一索引保证）
    :param entry_flag: True=标记为入口，False=取消标记
    :return: True=成功，False=失败
    """
    with _db_write_lock(db_path=db_path, task="mark_entry_point"):
        conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        try:
            row = conn.execute(SQL_SELECT_NODE_ENTRY_POINT_BY_PATH, (path,)).fetchone()
            if not row:
                print(f"ERROR: path='{path}' 在 nodes 表中不存在", file=sys.stderr)
                return False
            old_flag = bool(row["entry_point"])
            if old_flag == entry_flag:
                print(
                    f"[SKIP] nodes.entry_point 已为 {entry_flag}（path={path}）",
                    file=sys.stderr,
                )
                return True
            conn.execute(
                SQL_UPDATE_NODE_ENTRY_POINT,
                (entry_flag, path),
            )
            conn.commit()
            print(
                f"[OK] nodes.entry_point: {old_flag} -> {entry_flag} (path={path})",
                file=sys.stderr,
            )
            return True
        except Exception as e:
            conn.rollback()
            logger.error("mark_entry_point失败: %s", e)
            return False
        finally:
            conn.close()


# nodes_metadata 表可由 --update-module-metadata 更新的模块级字段白名单
# acquisition_method/acquisition_source（2026-08-05 acquisition 字段基础设施）：
# 枚举真源 = DDL CHECK 约束（depgraph_schema._DDL_NODES_METADATA），此处不复制枚举列表。
_MODULE_METADATA_FIELDS = {
    "module_name_cn",
    "module_name_en",
    "description_cn",
    "description_en",
    "acquisition_method",
    "acquisition_source",
}


def update_module_metadata(
    path: str,
    fields: dict,
    db_path: str = None,
) -> bool:
    """更新模块级元数据（nodes_metadata 表 UPSERT）。

    五图模块对齐 Step 3：为 nodes_metadata 表新增 4 个模块级字段配套写入入口。
    path 为稳定 PK（裁定#209 Stage 2）。若行不存在则 INSERT，存在则 UPDATE 指定字段。

    :param path: 节点 path（与 nodes.path 对齐）
    :param fields: dict，key 必须在 _MODULE_METADATA_FIELDS 白名单内
    :return: True=成功，False=失败
    """
    if not fields:
        print("ERROR: fields 为空，无字段可更新", file=sys.stderr)
        return False
    invalid = set(fields.keys()) - _MODULE_METADATA_FIELDS
    if invalid:
        print(
            f"ERROR: 非法字段 {invalid}（合法字段: {sorted(_MODULE_METADATA_FIELDS)}）",
            file=sys.stderr,
        )
        return False

    # 治本（2026-08-05，acquisition CHECK 约束对齐）：acquisition_method 空串 → None，
    # 与 DDL CHECK (IS NULL OR IN enum) 对齐——'' 非 NULL 又不在枚举内会被 DB 拒绝。
    # NULL=未设置，与 reader 的 `or ""` 回退语义等价。枚举真源=DDL CHECK，此处不复制枚举列表。
    if fields.get("acquisition_method") == "":
        fields["acquisition_method"] = None

    with _db_write_lock(db_path=db_path, task="update_module_metadata"):
        conn = get_depgraph_pg_connection(autocommit=False, allow_edge_delete=True)
        try:
            row = conn.execute(SQL_SELECT_NODE_BP_BY_PATH, (path,)).fetchone()
            if not row:
                print(f"ERROR: path='{path}' 在 nodes 表中不存在", file=sys.stderr)
                return False
            blueprint_id = row["blueprint_id"]

            existing = conn.execute(SQL_SELECT_NODES_METADATA_BY_PATH, (path,)).fetchone()
            now = datetime.datetime.now().isoformat()
            if existing:
                set_clauses = ", ".join(f"{k}=%s" for k in fields)
                params = list(fields.values()) + [now, path]
                conn.execute(
                    f"UPDATE nodes_metadata SET {set_clauses}, last_updated=%s WHERE path=%s",  # 5.160.2 OK: dynamic SQL, kept inline
                    params,
                )
            else:
                cols = ["path", "blueprint_id", "last_updated"] + list(fields.keys())
                placeholders = ", ".join(["%s"] * len(cols))
                params = [path, blueprint_id, now] + list(fields.values())
                conn.execute(
                    f"INSERT INTO nodes_metadata ({', '.join(cols)}) VALUES ({placeholders})",  # 5.160.2 OK: dynamic SQL, kept inline
                    params,
                )
            conn.commit()
            print(
                f"[OK] nodes_metadata UPSERT path={path} fields={list(fields.keys())}",
                file=sys.stderr,
            )
            return True
        except Exception as e:
            conn.rollback()
            logger.error("update_module_metadata失败: %s", e)
            return False
        finally:
            conn.close()


def main() -> None:
    """Entry point: parse args, run logic, return exit code."""
    parser = argparse.ArgumentParser(
        description="depgraph 变更写入工具（禁止AI直接Write 157MB文件）",
        epilog="See .trae/rules/project_rules.md RULE-SIXTEEN for the full protocol.",
    )
    parser.add_argument(
        "--update-module", type=str, nargs=2, metavar=("MODULE_ID", "FIELD=VALUE"), help="更新单个模块字段"
    )
    parser.add_argument("--batch", type=str, help="批量变更 JSON 文件路径")
    parser.add_argument("--dry-run", action="store_true", help="仅验证，不写入")
    parser.add_argument(
        "--list-ops",
        action="store_true",
        help="列出 cmd_batch 支持的所有 op（从 _DOMAIN_OPS/_NODE_OPS 注册表自动派生，真源唯一）",
    )
    # P0-2 新增4命令
    parser.add_argument(
        "--add-design-node",
        type=str,
        nargs="+",
        metavar="ARG",
        help="新增设计态节点: PATH BLUEPRINT_ID DOMAIN_ID [BUILD_STATUS]（粒度由 --granularity 指定，默认 directory）",
    )
    parser.add_argument(
        "--granularity",
        type=str,
        default="directory",
        help="--add-design-node 的粒度（file/directory/module/aggregated，默认 directory）。"
        "file=单文件设计态（path 不以 / 结尾），directory=目录级设计态（path 以 / 结尾）。"
        "合法值由 granularity_vocabulary.yaml 动态定义（trae_060 §2 治本，2026-07-13）",
    )
    parser.add_argument(
        "--add-design-edge",
        type=int,
        nargs=2,
        metavar=("FROM_NODE_ID", "TO_NODE_ID"),
        help="新增设计态边: FROM_NODE_ID TO_NODE_ID",
    )
    parser.add_argument(
        "--transition-build-status",
        type=str,
        nargs=2,
        metavar=("NODE_ID", "TO_STATUS"),
        help="转换build_status: NODE_ID TO_STATUS",
    )
    parser.add_argument(
        "--transition-design-maturity",
        type=str,
        nargs=2,
        metavar=("NODE_ID", "TO_MATURITY"),
        help="转换design_maturity(ARCH-MM-002 两档化: design→production): NODE_ID TO_MATURITY。"
        "ARCH-MM-002 门禁：[MATURITY] header SSoT MUST == TO_MATURITY，否则硬阻断（--force 逃生）",
    )
    parser.add_argument(
        "--remove-design-node",
        type=int,
        metavar="NODE_ID",
        help="软删除设计态节点: NODE_ID（MUST 配 --design-evidence 双源门禁，治本RSK/RPT误删）",
    )
    parser.add_argument(
        "--deprecate-node",
        type=int,
        metavar="NODE_ID",
        help="软废弃任意节点（含production）: NODE_ID — 专用于孤儿节点清理，绕过5态状态机。"
        "design 节点禁止走此后门（需 --remove-design-node），合法 design 垃圾节点加 --force 逃生。",
    )
    parser.add_argument(
        "--design-evidence",
        type=str,
        metavar="DOC_REF",
        default=None,
        help="删除 design 节点的设计文档证据引用（必填，如 '11-D-RISK §1.4 RK-09 P0核心'）。"
        '治本 RSK/RPT 误删：堵住"忘了查文档就 CLI 删"的后门。与 --remove-design-node 配合使用。',
    )
    parser.add_argument(
        "--delete-design-edge", type=int, metavar="EDGE_ID", help="删除设计态边（仅限dep_maturity=design）: EDGE_ID"
    )
    parser.add_argument(
        "--update-edge-type",
        type=str,
        nargs=2,
        metavar=("EDGE_ID", "NEW_TYPE"),
        help="修改边dep_type: EDGE_ID NEW_TYPE(contract/event/runtime/data/import_depends/test_depends/config_depends)",
    )
    parser.add_argument(
        "--add-edge",
        type=int,
        nargs=2,
        metavar=("FROM_NODE_ID", "TO_NODE_ID"),
        help="新增边（不限maturity，支持production节点）: FROM_NODE_ID TO_NODE_ID",
    )
    parser.add_argument(
        "--delete-edge",
        type=int,
        metavar="EDGE_ID",
        help="删除边（不限dep_maturity，支持删除任意边）: EDGE_ID",
    )
    parser.add_argument(
        "--dep-type",
        type=str,
        default="import_depends",
        help="--add-edge的dep_type（contract/event/runtime/data/import_depends/test_depends/config_depends，默认import_depends）",
    )
    parser.add_argument(
        "--dep-maturity",
        type=str,
        default="active",
        help="--add-edge的dep_maturity（design|active，默认active）",
    )
    parser.add_argument(
        "--delete-blueprint-link",
        type=str,
        metavar="BLUEPRINT_ID",
        help="删除blueprint_links记录（清理悬空引用）: BLUEPRINT_ID",
    )
    parser.add_argument(
        "--delete-constraint",
        type=str,
        metavar="CONSTRAINT_ID",
        help="删除arch_constraints记录（清理孤儿约束/历史脏数据）: CONSTRAINT_ID",
    )
    parser.add_argument(
        "--add-file-node",
        type=str,
        nargs="+",
        metavar="ARG",
        help="新增文件级production节点（补注册孤儿文件）: PATH BLUEPRINT_ID DOMAIN_ID",
    )
    parser.add_argument(
        "--force-add-file-node",
        type=str,
        nargs="+",
        metavar="ARG",
        help="ARCH-061 逃生通道：强制添加扫描范围内的文件节点（仅在生成器故障时使用）: PATH BLUEPRINT_ID DOMAIN_ID",
    )
    # F5 合规豁免：域/路径/依赖迁移命令（ARCH-CAP-005）
    parser.add_argument(
        "--insert-domain",
        type=str,
        nargs="+",
        metavar="ARG",
        help="INSERT 新域: DOMAIN_ID DOMAIN_NAME DOMAIN_GROUP LAYER_ID SSOT_PATH [--max-modules N] [--description TEXT]",
    )
    parser.add_argument(
        "--update-domain-id",
        type=str,
        nargs=2,
        metavar=("MODULE_ID", "NEW_DOMAIN_ID"),
        help="UPDATE 模块 domain_id（域拆分迁移模块归属）",
    )
    parser.add_argument(
        "--update-path",
        type=str,
        nargs=3,
        metavar=("MODULE_ID", "OLD_PREFIX", "NEW_PREFIX"),
        help="UPDATE 模块 path 前缀替换（物理路径迁移）",
    )
    parser.add_argument(
        "--migrate-dependencies",
        type=str,
        nargs=2,
        metavar=("FROM_DOMAIN", "TO_DOMAIN"),
        help="UPDATE domain_dependencies 迁移跨域依赖",
    )
    parser.add_argument(
        "--update-domain-capacity",
        type=str,
        nargs=2,
        metavar=("DOMAIN_ID", "FIELD=VALUE"),
        help="UPDATE domains 容量字段: DOMAIN_ID current_modules=N|max_modules=N",
    )
    parser.add_argument(
        "--update-domain-layer",
        type=str,
        nargs=2,
        metavar=("DOMAIN_ID", "LAYER_ID"),
        help="UPDATE domains layer_id: DOMAIN_ID L0_infrastructure|L1_foundation|L1_platform|L2_domain",
    )
    parser.add_argument(
        "--migrate-nodes",
        type=str,
        nargs=2,
        metavar=("NODE_IDS_FILE", "NEW_DOMAIN_ID"),
        help="按 node_id 列表精确迁移 domain_id（JSON文件: [id1, id2, ...]）",
    )
    parser.add_argument(
        "--tag-nodes",
        type=str,
        nargs=2,
        metavar=("NODE_IDS_FILE", "TAG"),
        help="按 node_id 列表为 nodes.tags 添加横切标签（JSON文件: [id1, id2, ...]，幂等，逗号分隔串格式）",
    )
    parser.add_argument(
        "--untag-nodes",
        type=str,
        nargs=2,
        metavar=("NODE_IDS_FILE", "TAG"),
        help="按 node_id 列表从 nodes.tags 移除横切标签（JSON文件: [id1, id2, ...]，幂等）",
    )
    parser.add_argument(
        "--delete-nodes",
        type=str,
        metavar="NODE_IDS_FILE",
        help="按 node_id 列表删除节点（JSON文件: [id1, id2, ...]）。"
        "安全门：有入边（被依赖）则阻断，--force 可跳过。先删关联 edges 再删 nodes。"
        "已由 backup_pg_architecture() 自动 PG 备份（trae_054 v1.6.0 STEP0）。",
    )
    parser.add_argument(
        "--update-domain-ssot-path",
        type=str,
        nargs=2,
        metavar=("DOMAIN_ID", "SSOT_PATH"),
        help="UPDATE domains ssot_path: DOMAIN_ID SSOT_PATH（必须以/结尾）",
    )
    # 裁定#204：D-SIGNAL* 4 域改名——域ID重命名与中文名更新
    parser.add_argument(
        "--rename-domain",
        type=str,
        nargs=2,
        metavar=("OLD_DOMAIN_ID", "NEW_DOMAIN_ID"),
        help="重命名域ID（裁定#204）：18步UPDATE覆盖11表。完成后自动触发 scan_residual 后置校验（事件驱动，无需手工跑 audit_rename_completeness）。注意 D-SIGNAL 必须最后替换（含其他旧域名前缀避免误伤）",
    )
    # DM-100255 配套：4 空壳域删除——17步DELETE覆盖11表
    parser.add_argument(
        "--delete-domain",
        type=str,
        metavar="DOMAIN_ID",
        help="删除域（DM-100255 配套）：17步DELETE覆盖11表。安全门检查 nodes 引用（>0 需 --force）。"
        "先清外部引用（arch_path_mappings/domain_events 等），最后删 domains 行避免 FK 违规。"
        "rule_bindings.domain_id SET NULL（规则是全局资产）。完成后自动触发残留校验。",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="强制执行（跳过安全门）。与 --delete-domain（级联删除 nodes 引用）、"
        "--delete-nodes（跳过入边检查）、--transition-design-maturity（跳过 [MATURITY] header 校验）"
        "或 --deprecate-node（design 节点逃生，落审计日志）配合使用。",
    )
    # 裁定#ARCH-target_layer_v1.0.0：废弃域归并——将 old_id 引用迁移到已存在的 new_id
    parser.add_argument(
        "--merge-domain",
        type=str,
        nargs=2,
        metavar=("OLD_DOMAIN_ID", "NEW_DOMAIN_ID"),
        help="合并域（裁定#ARCH-target_layer_v1.0.0）：将 old_id 的所有引用迁移到已存在的 new_id，"
        "然后删除 old_id。与 --rename-domain 的区别：rename 要求 new_id 不存在，merge 要求 new_id 已存在。"
        "domain_dependencies 复合 PK 冲突预检（冲突阻断）。完成后自动触发残留校验。",
    )
    # 裁定#ARCH-target_layer_v1.0.0：清理旧格式domain_id描述性文本引用
    parser.add_argument(
        "--replace-text-domain",
        type=str,
        nargs=2,
        metavar=("OLD_TEXT", "NEW_DOMAIN_ID"),
        help="全表TEXT列值替换（裁定#ARCH-target_layer_v1.0.0）：扫描所有表所有TEXT列，"
        "REPLACE OLD_TEXT→NEW_DOMAIN_ID。与 --merge-domain 区别：不修改domain记录，仅清理描述性文本中的旧格式引用。"
        "用途：清理 D-COMPLIANCE（连字符）等旧格式残留。复用 _scan_replace_all_text_columns（已修复LIKE通配符陷阱）。",
    )
    parser.add_argument(
        "--apply-domain-id-check",
        action="store_true",
        help="应用 domains.domain_id CHECK 约束到现有数据库（裁定#ARCH-target_layer_v1.0.0）："
        "幂等 ALTER TABLE ADD CONSTRAINT domains_domain_id_format_check "
        "CHECK (domain_id ~ '^D_[A-Z][A-Z0-9_]*$')。预检所有 domain_id 值合规后再应用。"
        "背景：_MIGRATIONS P2后不再执行，现有DB需通过此命令补丁式应用CHECK约束。",
    )
    parser.add_argument(
        "--fix-domains-defaults",
        action="store_true",
        help="修复 domains 表 build_status DEFAULT 值（裁定#ARCH-target_layer_v1.0.0 v16修复）："
        "幂等 ALTER TABLE ALTER COLUMN build_status SET DEFAULT 'planned'。"
        "修复预存bug：DEFAULT 'unbuilt' 不在 CHECK 允许值中，INSERT 不提供 build_status 时失败。",
    )
    parser.add_argument(
        "--fix-domains-build-status-vocab",
        action="store_true",
        help="domains.build_status CHECK 词表扩展 +dormant（tracker #251 / #ARCH-143 续作，Owner 窗口 schema 变更）："
        "幂等 DROP+ADD CONSTRAINT domains_build_status_check 为 6 态。"
        "dormant=零节点域休眠标注（保留不激活），与 deprecated（有替代品）语义分立；nodes.build_status 不动。",
    )
    parser.add_argument(
        "--update-domain-name",
        type=str,
        nargs=2,
        metavar=("DOMAIN_ID", "NEW_NAME"),
        help="UPDATE domains.domain_name（裁定#204 配套，改名后更新中文名）",
    )
    # 裁定#207 R1：改名传播完整性修复——值扫描兜底 + blueprint_id 传播
    parser.add_argument(
        "--fix-residual",
        action="store_true",
        help="修复存量改名残留（裁定#207 R1 B5）：使用内置 _RENAME_MAP_204 全表TEXT列值扫描兜底",
    )
    parser.add_argument(
        "--propagate-rename",
        action="store_true",
        help="blueprint_id 派生标识符传播（裁定#206 B-5/B-6 + 裁定#207 R1 B2）：精确值映射，禁止子串REPLACE",
    )
    parser.add_argument(
        "--propagate-node-paths",
        type=str,
        metavar="JSON_FILE",
        help="节点路径改名传播（裁定#206 节点路径派生 + 裁定#207 R1 阶段D）：读取 D2 映射 JSON，"
        "精确值映射 nodes.path + blueprint_links.blueprint_path，按域内连续重新编号",
    )
    parser.add_argument(
        "--force-cross-domain",
        action="store_true",
        help="强制执行跨域匹配的 --update-domain-id（需确认跨域迁移为期望行为）",
    )
    parser.add_argument(
        "--insert-domain-mapping",
        type=str,
        nargs="+",
        metavar="ARG",
        help="INSERT domain_mapping: PATH_PREFIX DOMAIN_ID MAPPING_TYPE(non_src|unregistered_src) [SUBDOMAIN_ID]",
    )
    parser.add_argument("--new-from-domain", type=str, default="", help="migrate-dependencies 的新 from_domain")
    parser.add_argument("--new-to-domain", type=str, default="", help="migrate-dependencies 的新 to_domain")
    parser.add_argument(
        "--max-modules", type=int, default=150, help="insert-domain 的 max_modules（默认 150，裁定#194硬上限）"
    )
    parser.add_argument("--description", type=str, default="", help="insert-domain 的 description")
    parser.add_argument("--mapped-by", type=str, default="", help="insert-domain-mapping 的 mapped_by 字段")
    parser.add_argument("--note", type=str, default="", help="insert-domain-mapping 的 note 字段")
    parser.add_argument(
        "--cleanup-orphan-edges",
        action="store_true",
        help="清理孤儿边：删除edges表中引用不存在node的边",
    )
    parser.add_argument(
        "--cleanup-orphan-nodes",
        action="store_true",
        help="清理幽灵节点：删除nodes表中path在磁盘不存在的node（对称漂移修复，P1-DEP）",
    )
    parser.add_argument(
        "--mark-invalid",
        type=str,
        nargs=2,
        metavar=("BLUEPRINT_ID", "REASON"),
        help="裁定#208 B5: 标记 blueprint_id 为 invalid（软标记不删节点，保留追溯链；阶段 C/D 重编号专用）",
    )
    parser.add_argument(
        "--rename-blueprint-id",
        type=str,
        nargs=2,
        metavar=("OLD_BLUEPRINT_ID", "NEW_BLUEPRINT_ID"),
        help="裁定#208 D2: blueprint_id 独立重命名（跨域共享模块 SH-* 改名专用）。"
        "传播 nodes.blueprint_id + blueprint_links.blueprint_id + type_specific_data + blueprint_path。"
        "安全保证：负向前瞻防止 MOD-SHARED 误匹配 MOD-SHARED-001。"
        "改名后自动扫描 docs/ 下 YAML 真源引用并输出 [YAML SYNC WARNING]（无需手动 grep）。"
        "配 --dry-run 预览。",
    )
    parser.add_argument(
        "--set-blueprint-id",
        type=str,
        nargs=2,
        metavar=("PATH", "NEW_BLUEPRINT_ID"),
        help="按 path 给 blueprint_id 为空/NULL 的节点赋值（sanctioned 路径赋值入口）。"
        "专为 old_bp_id='' 的节点——--rename-blueprint-id 的 old='' 会误伤全库空值节点，"
        "故用本参数按 path 精确赋值。校验 new_bp_id 符合裁定#208 双轨制。"
        "同步更新 nodes.belongs_to + nodes_metadata.blueprint_id + 清除 blueprint_id_invalid。"
        "配 --dry-run 预览。",
    )
    parser.add_argument(
        "--clear-invalid-flag",
        type=str,
        metavar="BLUEPRINT_ID",
        help="治本（2026-08-03）：清除指定 blueprint_id 的 blueprint_id_invalid 标志（设 0）。"
        "用于标志与权威真源 is_valid_module_id 不一致的过期残留（如 MOD-CFG_* 旧校验误标）。"
        "安全保证：blueprint_id 必须先通过 is_valid_module_id 复核——仍不合规则拒绝清标志。"
        "配 --dry-run 预览。",
    )
    parser.add_argument(
        "--clear-blueprint-id",
        type=str,
        metavar="PATH",
        help="治本（2026-08-03）：按 path 清空 blueprint_id（设 NULL）+ belongs_to + invalid 标志。"
        "用于 infra_id 误存为 blueprint_id 的清理（INFRA-DB-* 是基础设施资源 ID，非 module_id）。"
        "节点仍由 path 唯一标识（裁定#209 Stage 2: path 是稳定 PK）。配 --dry-run 预览。",
    )
    # 五图模块对齐 Step 3 Task 3.4：模块全景字段写入入口
    parser.add_argument(
        "--mark-entry",
        type=str,
        nargs="+",
        metavar="PATH [--off]",
        help="标记文件级节点为入口文件（nodes.entry_point）。"
        "默认标记为 True，附加 --off 参数取消标记。"
        "示例: --mark-entry src/zephyr/cli/main.py",
    )
    parser.add_argument(
        "--off",
        action="store_true",
        help="--mark-entry 的取消标记开关（设 entry_point=FALSE）",
    )
    parser.add_argument(
        "--update-module-metadata",
        type=str,
        nargs="+",
        metavar="PATH KEY=VALUE [KEY=VALUE ...]",
        help="更新模块级元数据（nodes_metadata 表 UPSERT）。"
        "合法字段: module_name_cn/module_name_en/description_cn/description_en。"
        "示例: --update-module-metadata src/zephyr/cli/main.py module_name_cn=CLI入口 "
        "description_en=Command-line entry point",
    )
    parser.add_argument(
        "--fix-path-semantics",
        action="store_true",
        help="批量修复历史 design 节点 path 与 granularity 语义不一致问题（5.179 治本）。"
        "Case 1: path 以 .py/ 结尾但 granularity=directory → 改 file/module/去尾 /；"
        "Case 3: path 以 / 结尾但 granularity!=directory → 改 directory/blueprint。"
        "配 --dry-run 预览。",
    )
    args = parser.parse_args()

    # P0-2 新增命令处理
    if args.add_design_node:
        parts = args.add_design_node
        path = parts[0]
        blueprint_id = parts[1] if len(parts) > 1 else ""
        domain_id = parts[2] if len(parts) > 2 else ""
        build_status = parts[3] if len(parts) > 3 else "planned"
        node_id = add_design_node(path, blueprint_id, domain_id, build_status, granularity=args.granularity)
        if node_id < 0:
            sys.exit(4)
        print(f"node_id={node_id}")
        # ARCH-056: 设计态节点添加后自动同步到 dataflow/decision/blueprint
        if node_id > 0 and blueprint_id:
            try:
                from sync_panorama_module import sync_module_panorama

                sync_module_panorama(blueprint_id)
            except Exception as e:
                print(f"[WARN] sync_panorama_module 失败（不阻断）: {e}", file=sys.stderr)
        return

    if args.add_design_edge:
        from_id, to_id = args.add_design_edge
        edge_id = add_design_edge(from_id, to_id)
        if edge_id < 0:
            sys.exit(4)
        print(f"edge_id={edge_id}")
        return

    if args.transition_build_status:
        node_id_str, to_status = args.transition_build_status
        node_id = int(node_id_str)
        ok = transition_build_status(node_id, to_status)
        if not ok:
            sys.exit(4)
        _sync_panorama_after_transition(node_id)  # ARCH-056: 状态转换后自动同步全景
        return

    if args.transition_design_maturity:
        node_id_str, to_maturity = args.transition_design_maturity
        node_id = int(node_id_str)
        ok = transition_design_maturity(node_id, to_maturity, force=args.force)
        if not ok:
            sys.exit(4)
        _sync_panorama_after_transition(node_id)  # ARCH-056: 状态转换后自动同步全景
        return

    if args.remove_design_node is not None:
        ok = remove_design_node(args.remove_design_node, design_evidence=args.design_evidence)
        if not ok:
            sys.exit(4)
        return

    if args.deprecate_node is not None:
        ok = deprecate_node(args.deprecate_node, force=args.force)
        if not ok:
            sys.exit(4)
        return

    if args.delete_design_edge is not None:
        ok = delete_design_edge(args.delete_design_edge)
        if not ok:
            sys.exit(4)
        return

    if args.mark_invalid:
        bp_id, reason = args.mark_invalid
        ok = mark_blueprint_invalid(bp_id, reason)
        if not ok:
            sys.exit(4)
        return

    if args.update_edge_type:
        edge_id_str, new_type = args.update_edge_type
        edge_id = int(edge_id_str)
        ok = update_edge_type(edge_id, new_type)
        if not ok:
            sys.exit(4)
        return

    if args.add_edge:
        from_id, to_id = args.add_edge
        edge_id = add_edge(from_id, to_id, dep_type=args.dep_type, dep_maturity=args.dep_maturity)
        if edge_id < 0:
            sys.exit(4)
        return

    if args.delete_edge is not None:
        ok = delete_edge(args.delete_edge)
        if not ok:
            sys.exit(4)
        return

    if args.delete_blueprint_link:
        ok = delete_blueprint_link(args.delete_blueprint_link)
        if not ok:
            sys.exit(4)
        return

    if args.delete_constraint:
        ok = delete_constraint(args.delete_constraint)
        if not ok:
            sys.exit(4)
        return

    if args.add_file_node:
        parts = args.add_file_node
        if len(parts) < 3:
            print("ERROR: --add-file-node 需要 PATH BLUEPRINT_ID DOMAIN_ID", file=sys.stderr)
            sys.exit(3)
        path = parts[0]
        blueprint_id = parts[1]
        domain_id = parts[2]
        node_id = add_file_node(path, blueprint_id, domain_id)
        if node_id < 0:
            sys.exit(4)
        print(f"node_id={node_id}")
        return

    if args.force_add_file_node:
        parts = args.force_add_file_node
        if len(parts) < 3:
            print("ERROR: --force-add-file-node 需要 PATH BLUEPRINT_ID DOMAIN_ID", file=sys.stderr)
            sys.exit(3)
        path = parts[0]
        blueprint_id = parts[1]
        domain_id = parts[2]
        node_id = add_file_node(path, blueprint_id, domain_id, force=True)
        if node_id < 0:
            sys.exit(4)
        print(f"node_id={node_id}")
        return

    # F5 合规豁免：域/路径/依赖迁移命令处理
    if args.insert_domain:
        parts = args.insert_domain
        if len(parts) < 5:
            print(
                "ERROR: --insert-domain 需要 5 个参数: DOMAIN_ID DOMAIN_NAME DOMAIN_GROUP LAYER_ID SSOT_PATH",
                file=sys.stderr,
            )
            sys.exit(3)
        domain_id = parts[0]
        domain_name = parts[1]
        domain_group = parts[2]
        layer_id = parts[3]
        ssot_path = parts[4]

        # 建域门禁：校验命名规则（裁定#204 / OPS-2026062610 预防根因）
        errors, warnings = _validate_domain_naming(domain_id, domain_name)
        for w in warnings:
            print(f"[WARN] {w}", file=sys.stderr)
        if errors:
            for e in errors:
                print(f"[BLOCK] {e}", file=sys.stderr)
            print(
                f"ERROR: 域ID '{domain_id}' 违反 {len(errors)} 条 error 级命名规则，建域阻断（exit 3）",
                file=sys.stderr,
            )
            sys.exit(3)

        ok = cmd_insert_domain(
            domain_id,
            domain_name,
            domain_group,
            layer_id,
            ssot_path,
            max_modules=args.max_modules,
            description=args.description,
            dry_run=args.dry_run,
        )
        if not ok:
            sys.exit(4)
        return

    if args.update_domain_id:
        module_id, new_domain_id = args.update_domain_id
        count = cmd_update_domain_id(
            module_id, new_domain_id, dry_run=args.dry_run, force_cross_domain=args.force_cross_domain
        )
        if count < 0:
            sys.exit(4)
        print(f"affected={count}")
        return

    if args.update_path:
        module_id, old_prefix, new_prefix = args.update_path
        count = cmd_update_path(module_id, old_prefix, new_prefix, dry_run=args.dry_run)
        if count < 0:
            sys.exit(4)
        print(f"affected={count}")
        return

    if args.migrate_dependencies:
        from_domain, to_domain = args.migrate_dependencies
        count = cmd_migrate_dependencies(
            from_domain,
            to_domain,
            new_from_domain=args.new_from_domain,
            new_to_domain=args.new_to_domain,
            dry_run=args.dry_run,
        )
        if count < 0:
            sys.exit(4)
        print(f"affected={count}")
        return

    if args.update_domain_capacity:
        domain_id, field_value = args.update_domain_capacity
        if "=" not in field_value:
            print("ERROR: FIELD=VALUE format required, e.g. current_modules=134", file=sys.stderr)
            sys.exit(3)
        field, value_str = field_value.split("=", 1)
        try:
            value = int(value_str)
        except ValueError:
            print(f"ERROR: value 必须是整数，实际: {value_str}", file=sys.stderr)
            sys.exit(3)
        ok = cmd_update_domain_capacity(domain_id, field, value, dry_run=args.dry_run)
        if not ok:
            sys.exit(4)
        return

    if args.update_domain_layer:
        domain_id, layer_id = args.update_domain_layer
        ok = cmd_update_domain_layer(domain_id, layer_id, dry_run=args.dry_run)
        if not ok:
            sys.exit(4)
        return

    if args.migrate_nodes:
        node_ids_file, new_domain_id = args.migrate_nodes
        with open(node_ids_file) as f:
            node_ids = json.load(f)
        count = cmd_migrate_nodes(node_ids=node_ids, new_domain_id=new_domain_id, dry_run=args.dry_run)
        sys.exit(0 if count >= 0 else 4)

    if args.tag_nodes or args.untag_nodes:
        is_remove = bool(args.untag_nodes)
        node_ids_file, tag = args.untag_nodes if is_remove else args.tag_nodes
        with open(node_ids_file) as f:
            node_ids = json.load(f)
        count = cmd_tag_nodes(node_ids=node_ids, tag=tag, remove=is_remove, dry_run=args.dry_run)
        sys.exit(0 if count >= 0 else 4)

    if args.delete_nodes:
        node_ids_file = args.delete_nodes
        with open(node_ids_file) as f:
            node_ids = json.load(f)
        count = cmd_delete_nodes(node_ids=node_ids, force=args.force, dry_run=args.dry_run)
        sys.exit(0 if count >= 0 else 4)

    if args.update_domain_ssot_path:
        domain_id, ssot_path = args.update_domain_ssot_path
        ok = cmd_update_domain_ssot_path(domain_id=domain_id, ssot_path=ssot_path, dry_run=args.dry_run)
        sys.exit(0 if ok else 4)

    if args.insert_domain_mapping:
        parts = args.insert_domain_mapping
        if len(parts) < 3:
            print(
                "ERROR: --insert-domain-mapping 需要 3 个参数: PATH_PREFIX DOMAIN_ID MAPPING_TYPE [SUBDOMAIN_ID]",
                file=sys.stderr,
            )
            sys.exit(3)
        path_prefix = parts[0]
        domain_id = parts[1]
        mapping_type = parts[2]
        subdomain_id = parts[3] if len(parts) > 3 else ""
        ok = cmd_insert_domain_mapping(
            path_prefix,
            domain_id,
            mapping_type,
            subdomain_id=subdomain_id,
            mapped_by=args.mapped_by,
            note=args.note,
            dry_run=args.dry_run,
        )
        if not ok:
            sys.exit(4)
        return

    # 裁定#204：D-SIGNAL* 4 域改名——dispatch
    if args.rename_domain:
        old_id, new_id = args.rename_domain
        n = cmd_rename_domain(old_id, new_id, dry_run=args.dry_run)
        if n < 0:
            sys.exit(4)
        print(f"affected={n}")
        # 后置校验钩子（治本：消除手工跑 audit_rename_completeness 的必要性）
        # 事件驱动——改名完成事件自动触发残留扫描，无需手工触发
        # 失败不 sys.exit（改名已成功），仅 WARNING 提示人工复核
        if not args.dry_run:
            _post_rename_residual_check(old_id, None)
        return

    # DM-100255 配套：4 空壳域删除——dispatch
    if args.delete_domain:
        domain_id = args.delete_domain
        n = cmd_delete_domain(domain_id, dry_run=args.dry_run, force=args.force)
        if n < 0:
            sys.exit(4)
        print(f"affected={n}")
        # 后置残留校验（复用改名后置检查，事件驱动）
        if not args.dry_run:
            _post_rename_residual_check(domain_id, None)
        return

    # 裁定#ARCH-target_layer_v1.0.0：废弃域归并——dispatch
    if args.merge_domain:
        old_id, new_id = args.merge_domain
        n = cmd_merge_domain(old_id, new_id, dry_run=args.dry_run)
        if n < 0:
            sys.exit(4)
        print(f"affected={n}")
        # 后置残留校验（复用改名后置检查，事件驱动）
        if not args.dry_run:
            _post_rename_residual_check(old_id, None)
        return

    # 裁定#ARCH-target_layer_v1.0.0：清理旧格式domain_id描述性文本引用——dispatch
    if args.replace_text_domain:
        old_text, new_id = args.replace_text_domain
        n = cmd_replace_text_domain(old_text, new_id, dry_run=args.dry_run)
        if n < 0:
            sys.exit(4)
        print(f"affected={n}")
        return

    # 裁定#ARCH-target_layer_v1.0.0：应用 domain_id CHECK 约束到现有DB——dispatch
    if args.apply_domain_id_check:
        rc = cmd_apply_domain_id_check(dry_run=args.dry_run)
        if rc < 0:
            sys.exit(4)
        print(f"rc={rc}")
        return

    # 裁定#ARCH-target_layer_v1.0.0 v16：修复 domains.build_status DEFAULT——dispatch
    if args.fix_domains_defaults:
        rc = cmd_fix_domains_defaults(dry_run=args.dry_run)
        if rc < 0:
            sys.exit(4)
        print(f"rc={rc}")
        return

    # tracker #251 / #ARCH-143 续作：domains.build_status CHECK +dormant——dispatch
    if args.fix_domains_build_status_vocab:
        rc = cmd_fix_domains_build_status_vocab(dry_run=args.dry_run)
        if rc < 0:
            sys.exit(4)
        print(f"rc={rc}")
        return

    if args.update_domain_name:
        domain_id, new_name = args.update_domain_name
        n = cmd_update_domain_name(domain_id, new_name, dry_run=args.dry_run)
        if n < 0:
            sys.exit(4)
        print(f"affected={n}")
        return

    # 裁定#207 R1：改名传播完整性修复——dispatch
    if args.fix_residual:
        n = cmd_fix_rename_residual(_RENAME_MAP_204, dry_run=args.dry_run)
        if n < 0:
            sys.exit(4)
        print(f"affected={n}")
        return

    if args.propagate_rename:
        n = cmd_propagate_rename(_RENAME_MAP_204, dry_run=args.dry_run)
        if n < 0:
            sys.exit(4)
        print(f"affected={n}")
        return

    # 裁定#208 D2：blueprint_id 独立重命名（跨域共享模块 SH-* 改名专用）——dispatch
    if args.rename_blueprint_id:
        old_bp, new_bp = args.rename_blueprint_id
        n = cmd_rename_blueprint_id(old_bp, new_bp, dry_run=args.dry_run)
        if n < 0:
            sys.exit(4)
        print(f"affected={n}")
        return

    # 路径赋值 blueprint_id（空值节点专用 sanctioned 入口）——dispatch
    if args.set_blueprint_id:
        path_arg, new_bp = args.set_blueprint_id
        n = cmd_set_blueprint_id(path_arg, new_bp, dry_run=args.dry_run)
        if n < 0:
            sys.exit(4)
        print(f"affected={n}")
        return

    # 治本（2026-08-03）：清除过期 invalid 标志（MOD-CFG_* 旧校验残留）——dispatch
    if args.clear_invalid_flag:
        n = cmd_clear_invalid_flag(args.clear_invalid_flag, dry_run=args.dry_run)
        if n < 0:
            sys.exit(4)
        print(f"affected={n}")
        return

    # 治本（2026-08-03）：清空 blueprint_id（INFRA-DB-* infra_id 误存清理）——dispatch
    if args.clear_blueprint_id:
        n = cmd_clear_blueprint_id(args.clear_blueprint_id, dry_run=args.dry_run)
        if n < 0:
            sys.exit(4)
        print(f"affected={n}")
        return

    if args.propagate_node_paths:
        import json as _json

        map_path = Path(args.propagate_node_paths)
        if not map_path.is_file():
            print(f"ERROR: 映射文件不存在: {map_path}", file=sys.stderr)
            sys.exit(3)
        with open(map_path, encoding="utf-8") as f:
            mapping_data = _json.load(f)
        path_mapping = mapping_data.get("path_mapping", {})
        bl_mapping = mapping_data.get("bl_mapping", {})
        if not path_mapping and not bl_mapping:
            print("ERROR: 映射文件中 path_mapping 与 bl_mapping 均为空", file=sys.stderr)
            sys.exit(3)
        n = cmd_propagate_node_paths(
            path_mapping,
            bl_mapping=bl_mapping,
            dry_run=args.dry_run,
        )
        if n < 0:
            sys.exit(4)
        print(f"affected={n}")
        return

    if args.cleanup_orphan_edges:
        count = cmd_cleanup_orphan_edges(dry_run=args.dry_run)
        sys.exit(0 if count >= 0 else 4)

    if args.cleanup_orphan_nodes:
        count = cmd_cleanup_orphan_nodes(dry_run=args.dry_run)
        sys.exit(0 if count >= 0 else 4)

    # 五图模块对齐 Step 3 Task 3.4：模块全景字段写入 dispatch
    if args.mark_entry:
        if len(args.mark_entry) != 1:
            print(
                "ERROR: --mark-entry 需要 1 个 PATH 参数（--off 单独作为开关）",
                file=sys.stderr,
            )
            sys.exit(3)
        path = args.mark_entry[0]
        entry_flag = not args.off
        ok = mark_entry_point(path, entry_flag=entry_flag)
        sys.exit(0 if ok else 4)

    if args.update_module_metadata:
        if len(args.update_module_metadata) < 2:
            print(
                "ERROR: --update-module-metadata 需要 PATH + 至少 1 个 KEY=VALUE",
                file=sys.stderr,
            )
            sys.exit(3)
        path = args.update_module_metadata[0]
        kv_pairs = args.update_module_metadata[1:]
        fields: dict = {}
        for kv in kv_pairs:
            if "=" not in kv:
                print(f"ERROR: KEY=VALUE 格式错误: {kv}", file=sys.stderr)
                sys.exit(3)
            k, v = kv.split("=", 1)
            fields[k.strip()] = v
        ok = update_module_metadata(path, fields)
        sys.exit(0 if ok else 4)

    if args.fix_path_semantics:
        result = fix_path_semantics_for_design_nodes(dry_run=args.dry_run)
        # 输出 JSON 摘要供脚本消费
        import json as _json

        print(_json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(EXIT_PASS)

    if args.list_ops:
        # op 清单从注册表自动派生（§6.16 铁律：禁止手工同步到 docstring/AGENTS.md）
        ops = _get_supported_ops()
        print(f"cmd_batch 支持的 op（共 {len(ops)} 个，从 _DOMAIN_OPS/_NODE_OPS 注册表自动派生）:")
        for op in ops:
            kind = "节点级(经 dep dict)" if op in _NODE_OPS else "域级(直接 SQL)"
            print(f"  {op:30s} ({kind})")
        sys.exit(EXIT_PASS)

    if not args.update_module and not args.batch:
        parser.print_help()
        print("\nERROR: Must specify --update-module or --batch", file=sys.stderr)
        sys.exit(3)

    dep = _load_depgraph()

    if args.update_module:
        module_id = args.update_module[0]
        field_value = args.update_module[1]
        if "=" not in field_value:
            print("ERROR: FIELD=VALUE format required, e.g. blueprint_status=has_blueprint", file=sys.stderr)
            sys.exit(3)
        field, value = field_value.split("=", 1)
        cmd_update_module(dep, module_id, field, value)
        if args.dry_run:
            print("DRY RUN - no changes written", file=sys.stderr)
        else:
            _atomic_write(dep)

    if args.batch:
        with open(args.batch, encoding="utf-8") as f:
            changes = json.load(f)
        cmd_batch(dep, changes, args.dry_run)


# 写入命令集合（模块级——5.34.6 is_prod() 守卫与 __main__ 尾部自动备份共用；
# 原定义在 finally 块内，hoist 到模块级消除两处重复维护的漂移风险）
_WRITE_COMMANDS = {
    "--add-design-node",
    "--add-design-edge",
    "--transition-build-status",
    "--transition-design-maturity",
    "--remove-design-node",
    "--deprecate-node",
    "--delete-design-edge",
    "--mark-invalid",
    "--update-edge-type",
    "--add-edge",
    "--delete-edge",
    "--delete-blueprint-link",
    "--delete-constraint",
    "--add-file-node",
    "--insert-domain",
    "--update-domain-id",
    "--update-path",
    "--migrate-dependencies",
    "--update-domain-capacity",
    "--update-domain-layer",
    "--migrate-nodes",
    "--tag-nodes",
    "--untag-nodes",
    "--update-domain-ssot-path",
    "--insert-domain-mapping",
    "--rename-domain",
    "--update-domain-name",
    "--fix-residual",
    "--propagate-rename",
    "--rename-blueprint-id",
    "--propagate-node-paths",
    "--cleanup-orphan-edges",
    "--cleanup-orphan-nodes",
    "--update-module",
    "--batch",
    "--merge-domain",
    "--replace-text-domain",
    "--apply-domain-id-check",
    "--fix-domains-defaults",
    "--fix-domains-build-status-vocab",
}


def _guard_prod_write_commands() -> None:
    """5.34.6 治本：is_prod() 真实守卫调用点——生产环境 depgraph 写入命令需显式确认。

    ZEPHYR_ENV=production 时，执行任何写入命令（_WRITE_COMMANDS）必须显式设置
    ZEPHYR_DEPGRAPH_WRITE_ACK=1，否则 exit 3 阻断（对齐头部 ERROR_CONTRACT
    "验证失败→exit 3"）。dev/test 环境 is_prod() 为 False 直接返回，默认路径零影响。
    """
    from zephyr.shared.foundation.env import is_prod

    if not is_prod():
        return
    write_cmds = sorted(arg for arg in sys.argv if arg in _WRITE_COMMANDS)
    if write_cmds and os.environ.get("ZEPHYR_DEPGRAPH_WRITE_ACK") != "1":
        print(
            f"ERROR: 生产环境（ZEPHYR_ENV=production）执行 depgraph 写入命令 "
            f"{write_cmds} 需显式确认——设置 ZEPHYR_DEPGRAPH_WRITE_ACK=1 后重试"
            f"（5.34.6 is_prod() 守卫）。",
            file=sys.stderr,
        )
        sys.exit(3)


if __name__ == "__main__":
    _guard_prod_write_commands()
    try:
        main()
    finally:
        # ARCH-041 §5.33.1 治本：PG depgraph 备份（事件触发——写入命令后自动备份）
        # 只在写入命令（非 --dry-run）时触发，--list-ops/--help 等只读命令不备份
        # 治本原则：永久系统必须全自动（事件触发，非时间触发/手动触发）
        is_dry_run = any(arg == "--dry-run" for arg in sys.argv)
        has_write_cmd = any(arg in _WRITE_COMMANDS for arg in sys.argv)
        if has_write_cmd and not is_dry_run:
            # 治本(2026-07-20): 改用项目内模块路径导入，避免 sys.path.insert 后的悬空 import
            # （IMPORT-INTEGRITY gate 不识别 sys.path.insert 注入的导入）
            # 治本(2026-07-22): 顶层导入需要 REPO_ROOT 在 sys.path，但本脚本运行时仅注入 _GOV_DIR，
            # 导致 ImportError。参照 line 121-128 模式加 fallback。
            try:
                try:
                    from scripts.governance.meta.backup_runtime_state import backup_pg_architecture
                except ImportError:
                    from meta.backup_runtime_state import backup_pg_architecture
                # Obs2 治本：传 throttle_seconds=60 节流——连续 apply 调用
                # 在数秒内产生冗余快照（实测 14 秒 8 份），DR 备份无需细粒度
                # （git commit 已追溯架构变更，trae_054 STEP0 铁律）。
                # v2 扩展（2026-08-03）：backup_pg_architecture 覆盖全景 19 张 DB 真源表。
                backup_pg_architecture(throttle_seconds=60)
            except Exception as _e:  # noqa: BLE001  # 备份失败不阻断主流程（DR 安全网）
                # 备份失败不阻断主流程（main 已成功），仅记录到 stderr
                print(f"[BACKUP-PG] WARNING: 备份失败（不阻断主流程）: {_e}", file=sys.stderr)
            # DM-90974 Phase 2: 落 depgraph_dirty.flag，让 GATE-DOMAIN-DOC reconciler
            # 在下次任意 commit 时检测到 DB 已变并触发域文档重生。治本盲区：
            # 运行时 DB 操作（--delete-nodes 等）不产生 git commit，原 trigger 永不 fire。
            try:
                from _shared.constants import mark_depgraph_dirty

                mark_depgraph_dirty()
            except Exception as _e:  # noqa: BLE001 — flag 写入失败不阻断主流程（DB 已成功写入）
                print(f"[DIRTY-FLAG] WARNING: depgraph_dirty.flag 写入失败（不阻断）: {_e}", file=sys.stderr)
            # 生成器自动重生成（reconcile_generators §reconcile_async 非阻塞）：
            # apply 写完 DB → reconcile_async("depgraph_db") 后台 spawn 生成器子进程。
            # 异步非阻塞——depgraph 19 生成器同步跑需 ~50s（blueprint_panorama --all ~145s），
            # 异步 spawn 后 apply 立即返回，生成器后台跑，日志写 .runtime/logs/。
            # 失败不丢失：boot_hooks 启动时 reconcile_stale() 兜底重跑（生成器幂等）。
            # ZEPHYR_SKIP_REGENERATE=1 逃生通道：批量操作时可跳过。
            if os.environ.get("ZEPHYR_SKIP_REGENERATE") != "1":
                try:
                    try:
                        from scripts.governance.reconcile_generators import reconcile_async
                    except ImportError:
                        from reconcile_generators import reconcile_async
                    regen = reconcile_async("depgraph_db")
                    if regen.get("status") == "spawned":
                        print(
                            f"[REGENERATE] 🔄 后台启动 PID={regen['pid']} 日志: {regen['log_file']}",
                            file=sys.stderr,
                        )
                    else:
                        print(
                            f"[REGENERATE] WARNING: 后台启动失败（不阻断写入）: {regen.get('error')}", file=sys.stderr
                        )
                except Exception as _e:  # noqa: BLE001 — 编排器不可用不阻断主流程
                    print(f"[REGENERATE] WARNING: 编排器不可用（不阻断写入）: {_e}", file=sys.stderr)


# ── Stage 4 公共化（2026-07-29）：public wrapper ──
def read_maturity_header(file_path) -> str | None:
    """公共接口：read_maturity_header（Stage 4 公共化）。"""
    return _read_maturity_header(file_path)

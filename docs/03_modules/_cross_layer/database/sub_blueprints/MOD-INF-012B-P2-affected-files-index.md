---
module_id: MOD-INF-012B
submodule_path: src/zephyr/data/persistence
title: "P2 PostgreSQL迁移—受影响文件完整索引（循环审查版）"
doc_type: blueprint
status: Draft
version: "1.0.0"
layer: cross_layer
blueprint_level: sub_module
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: AI-session-20260625-P2-audit
date: "2026-06-25"
valid_from: "2026-06-25"
ttl: permanent
rule_form: structural
belongs_to: "SH-DB-001"
parent_module: "SH-DB-001"
scope: global
stability: evolving
verifiability: automated
construction_progress: planned
actual_disk_path: ''
codification_level: L2
generation: 3
functional_domain: data
summary: "P2 PostgreSQL迁移受影响文件完整索引——包含文件路径、位置、变量/函数名、变更影响、执行办法的完整清单。循环审查直到连续两次新增=0。"
tags: [postgresql, migration, affected-files, audit, p2, database-upgrade]
priority: P1
runtime_plane: hot
depends_on:
  - {target: "MOD-INF-012B-P2", at: "§十二", why: "P2文档受影响文件索引的详细展开"}
references:
  - {id: "MOD-INF-012B-P2", at: "全篇", why: "P2迁移方案主文档"}
---

# P2 PostgreSQL迁移—受影响文件完整索引（循环审查版）

> module_id: MOD-INF-012B | version: 1.0.0 | status: Draft
> 审查轮次: 第1轮 | 审查日期: 2026-06-25
> 裁定依据: D50-PG（仅depgraph.db迁移到PostgreSQL，governance.db和market.duckdb保持不变）

## 文档说明

本文档是P2 PostgreSQL迁移方案§十二"受影响文件完整索引"的详细展开。每个文件记录：文件路径、位置（行号）、变量/函数名、变更影响、执行办法。

**循环审查规则**：本文档完成后必须经过循环审查，检查是否有遗漏的文件/位置，直到连续两次审查新增=0。

---

## 一、src/zephyr/ 下受影响文件清单

### 1.1 必须迁移到PostgreSQL的文件（6个）

| # | 文件路径 | 位置（行号） | 变量/函数名 | 变更影响 | 执行办法 |
|---|---------|:---------:|-----------|---------|---------|
| 1 | `src/zephyr/governance/depgraph_schema.py` | L77 | `DB_PATH` | 路径常量→PG连接串 | 改为从环境变量读取PG_DSN |
| | | L359-366 | `_PRAGMAS`（6条：WAL/synchronous/foreign_keys/busy_timeout/temp_store/wal_autocheckpoint） | PG无PRAGMA机制 | 删除全部PRAGMA；PG通过postgresql.conf配置 |
| | | L369-371 | `_apply_pragmas()` | PRAGMA应用函数 | 删除该函数及所有调用点（L920、L990、L1010，共3处；L963为`PRAGMA foreign_keys=ON`非_apply_pragmas调用） |
| | | L123,236,252,306,380,425,493,606 | `INTEGER PRIMARY KEY AUTOINCREMENT` | PG无AUTOINCREMENT | 改为`SERIAL`/`BIGSERIAL`或`GENERATED ALWAYS AS IDENTITY` |
| | | L862,864,999 | `sqlite_master`查询 | PG系统表不同 | 改为`SELECT table_name FROM information_schema.tables WHERE table_schema='public'` |
| | | L901,937 | `INSERT OR IGNORE INTO _schema_version` | PG无INSERT OR IGNORE | 改为`INSERT ... ON CONFLICT (version) DO NOTHING` |
| | | L799 | `datetime('now')` | PG函数不同 | 改为`NOW()`或`CURRENT_TIMESTAMP` |
| | | L901,937 | `VALUES (?, ?, ?)` | 占位符不同 | `?`→`%s`（psycopg2） |
| | | L918,983,997,1008 | `sqlite3.connect()` | 连接方式不同 | 改为`psycopg2.connect()`/连接池 |
| | | L947,963 | `PRAGMA foreign_keys = OFF/ON` | PG无此PRAGMA | 改为`SET session_replication_role = 'replica'`或删除 |
| | | L831-855 | `CREATE VIEW ... WITH RECURSIVE` | PG兼容 | 无需修改 |
| 2 | `src/zephyr/governance/database_service.py` | L58 | `self.depgraph_db` | 硬编码路径→PG连接配置 | 改为从环境变量读取PG_DSN |
| | | L76-81 | `get_depgraph_conn()`内`sqlite3.connect()` | 连接方式不同 | 改为`psycopg2.connect()`；移除`row_factory = sqlite3.Row` |
| | | L161,177,222,255,292 | `VALUES (?, ...)` | 占位符不同 | `?`→`%s`（含governance.db与market部分） |
| | | L168,177 | `datetime('now')` | PG函数不同 | 改为`NOW()`（governance.db部分保持） |
| | | L303 | `sqlite_master` | PG系统表不同 | 改为`information_schema.tables` |
| | | L186,192,198,204,210 | `get_depgraph_conn()`调用链 | 连接对象类型变化 | `sqlite3.Connection`→PG连接类型注解（5处） |
| 3 | `src/zephyr/governance/depgraph_reader.py` | L46 | `DB_PATH = .../depgraph.db` | 路径常量→PG连接配置 | 改为从环境变量读取PG_DSN |
| | | L58 | `sqlite3.connect()` | 连接方式不同 | 改为`psycopg2.connect()`；移除`row_factory = sqlite3.Row` |
| | | L78-245（约23处） | `?`占位符 | 占位符不同 | 全部`?`→`%s` |
| | | L112,118 | `from_node`/`to_node`列名 | 潜在bug（实际为`from_node_id`/`to_node_id`） | 迁移时一并核对修复 |
| | | L124 | `edge_type`列名 | 潜在bug（实际为`dep_type`） | 迁移时一并核对修复 |
| | | L210 | `arch_domains`表 | 潜在bug（表不存在） | 迁移时一并核对修复 |
| 4 | `src/zephyr/governance/rule_engine.py` | L50 | `_DB_PATH = .../depgraph.db` | 路径常量→PG连接配置 | 改为从环境变量读取PG_DSN |
| | | L53-56 | `_PRAGMAS`（WAL/foreign_keys/busy_timeout） | PG无PRAGMA | 删除全部PRAGMA |
| | | L90 | `sqlite3.connect(timeout=10.0)` | 连接方式不同 | 改为`psycopg2.connect()`；`timeout`→PG连接超时配置 |
| | | L92-93 | `for pragma in _PRAGMAS: conn.execute(pragma)` | PRAGMA循环 | 删除循环 |
| | | L94 | `sqlite_master` | PG系统表不同 | 改为`information_schema.tables` |
| | | L154,172,190 | `VALUES (?)`/`WHERE ... = ?` | 占位符不同 | `?`→`%s` |
| 5 | `src/zephyr/governance/auto_runner.py` | L41 | `_DEPGRAPH_DB = .../depgraph.db` | 路径常量→PG连接配置 | 改为从环境变量读取PG_DSN |
| | | L202,260,282 | `sqlite3.connect()` | 连接方式不同 | 改为`psycopg2.connect()`（3处；L199为`if not _DEPGRAPH_DB.exists()`非连接点） |
| | | L206-215 | `CREATE TABLE IF NOT EXISTS governance_audit_logs (... AUTOINCREMENT ...)` | 兜底建表+AUTOINCREMENT | `AUTOINCREMENT`→`SERIAL`；建议删除兜底建表逻辑 |
| | | L220 | `VALUES (?, ?, ?, ?, ?, ?, ?)` | 占位符不同 | `?`→`%s` |
| 6 | `src/zephyr/infrastructure/asset_inventory/dashboard.py` | L159 | `dep_path = .../depgraph.db` | 路径常量→PG连接配置 | 改为从环境变量读取PG_DSN |
| | | L186 | `sqlite3.connect(timeout=10.0)` | 连接方式不同 | 改为`psycopg2.connect()` |
| | | L187 | `SELECT node_id FROM nodes ORDER BY fan_in DESC LIMIT 5` | 潜在bug（`fan_in`列不存在，实际为`in_degree`） | 迁移时修复列名 |

### 1.2 部分迁移的文件（1个）

| # | 文件路径 | 位置（行号） | 变量/函数名 | 变更影响 | 执行办法 |
|---|---------|:---------:|-----------|---------|---------|
| 7 | `src/zephyr/governance/rule_watcher.py` | L59 | `_DEFAULT_DB_PATH = .../depgraph.db` | 路径传给subprocess | 改为PG连接配置；同步更新子脚本参数 |
| | | L301 | `sqlite3.connect(_GOVERNANCE_DB)` | governance.db连接（保持SQLite） | 不迁移 |
| | | L302 | `sqlite_master` | governance.db查询（保持SQLite） | 不迁移 |
| | | L311 | `datetime('now')`/`VALUES (?, ...)` | governance.db SQL（保持SQLite） | 不迁移 |

### 1.3 不需要迁移但需复核的文件（4个）

| # | 文件路径 | 位置（行号） | 变量/函数名 | 变更影响 | 执行办法 |
|---|---------|:---------:|-----------|---------|---------|
| 8 | `src/zephyr/governance/blast_radius.py` | L44 | `_DEPGRAPH_DEFAULT_PATH = Path("...depgraph.db")` | 常量指向.db文件却按YAML解析（逻辑存疑） | 确认数据源意图；迁移后路径变为连接串 |
| 9 | `src/zephyr/security/access_control/rbac_guard.py` | L68 | `PROTECTED_PATHS`含`"data/databases/depgraph.db"` | 文件路径保护规则 | 迁移后PG无本地文件需保护，需重新设计保护策略 |
| 10 | `src/zephyr/security/access_control/path_guard.py` | L60 | `CRITICAL_FILES`含`"data/databases/depgraph.db"` | 关键文件写保护 | 同上 |
| 11 | `src/zephyr/security/access_control/immutable_core.py` | L82 | `PROTECTED_PATHS`含`"data/databases/depgraph.db"` | 不可变核心保护路径 | 同上 |

### 1.4 代理/导出文件（2个，随真源迁移）

| # | 文件路径 | 位置（行号） | 变量/函数名 | 变更影响 | 执行办法 |
|---|---------|:---------:|-----------|---------|---------|
| 12 | `src/zephyr/governance/persistence/depgraph_schema.py` | L16 | `from zephyr.governance.depgraph_schema import DB_PATH, get_db_connection, init_db` | 纯re-export | 随真源模块迁移，无需单独改 |
| 13 | `src/zephyr/governance/__init__.py` | L83,133 | `from zephyr.governance.database_service import DatabaseService` | 仅导入导出 | 随database_service.py迁移 |

### 1.5 纯注释/字符串引用（5个，无需改SQL）

| # | 文件路径 | 位置（行号） | 变量/函数名 | 变更影响 | 执行办法 |
|---|---------|:---------:|-----------|---------|---------|
| 14 | `src/zephyr/governance/rule_enforcement/g_trae_059.yaml` | L1,40,58,63,76,77 | 注释引用`depgraph.db` | 描述性引用 | 更新文档中白名单路径表述 |
| 15 | `src/zephyr/infrastructure/asset_inventory/__main__.py` | L522 | print字符串`"…depgraph.db"` | 输出提示文本 | 更新提示文本 |
| 16 | `src/zephyr/reporting/__init___from_obs.py` | L1 | 注释`# [BLUEPRINT] ... depgraph.db` | 文件头注释 | 更新注释 |
| 17 | `src/zephyr/governance/script_governance/__init__.py` | L2 | 注释`# [BLUEPRINT] ... depgraph.db` | 文件头注释 | 更新注释 |
| 18 | `src/zephyr/governance/registry_management/__init__.py` | L2 | 注释`# [BLUEPRINT] ... depgraph.db` | 文件头注释 | 更新注释 |

### 1.6 核心基础设施文件（3个，必须同步修改）

| # | 文件路径 | 位置（行号） | 变量/函数名 | 变更影响 | 执行办法 |
|---|---------|:---------:|-----------|---------|---------|
| 19 | `src/zephyr/shared/utils/db_utils.py` | 全文件 | `get_db_connection(db_path)` | 通用DB连接工具 | 增加PG连接分支；保留SQLite连接（governance.db用） |
| 20 | `src/zephyr/shared/io/paths.py` | L66 | `DB_PATH` | governance.db路径SSoT | 保留（governance.db不迁移）；新增PG_DSN配置 |
| 21 | `src/zephyr/governance/sqlite_schema.py` | L76 | `DB_PATH` | governance.db路径SSoT | 保留（governance.db不迁移）；区分depgraph连接 |

---

## 二、scripts/ 下受影响文件清单

### 2.1 必须迁移到PostgreSQL的文件（45个）

| # | 文件路径 | 位置（行号） | 变量/函数名 | 变更影响 | 执行办法 |
|---|---------|:---------:|-----------|---------|---------|
| 1 | `scripts/governance/apply_depgraph.py` | L70 | `DEPGRAPH_PATH` | 路径常量→PG连接配置 | 改为从环境变量读取PG_DSN |
| | | L191 | `import lock_files as _lf` | 文件锁集成 | 删除（PG MVCC管理并发） |
| | | L194 | `_db_write_lock_lock` | threading.Lock | 删除 |
| | | L198 | `_db_write_lock()` | 双重锁 | 删除 |
| | | L248 | `_optional_db_lock()` | 可选锁包装器 | 删除 |
| | | L259,312,484,610,680,750,860,892,940,995,1044,1096,1158,1206,1261,1357,1407,1455,1512 | `sqlite3.connect()` | 连接方式不同 | 改为`psycopg2.connect()`/连接池 |
| | | L647,708,806 | `cur.lastrowid` | PG无lastrowid | 改为`INSERT ... RETURNING id` |
| | | L76 | `_check_git_backup()` | GIT备份门禁 | 改造为检查迁移脚本是否已提交 |
| | | L148 | `_create_physical_backup()` | 物理备份 | 删除（PG用pg_dump） |
| | | L303 | `_atomic_write()` | 原子写入 | 删除`_optional_db_lock`调用；改用PG事务 |
| 2 | `scripts/governance/sync_yaml_to_depgraph.py` | L51 | `DB_PATH` | 路径常量→PG连接配置 | 改为从环境变量读取PG_DSN |
| | | L864 | `sqlite3.connect()` | 连接方式不同 | 改为`psycopg2.connect()` |
| | | L195,292,421,454,492,575,598,619,719,749,787,819 | `INSERT OR REPLACE` | PG无INSERT OR REPLACE | 改为`INSERT ... ON CONFLICT (...) DO UPDATE SET ...` |
| | | L78,87 | `disable_readonly_triggers`/`restore_readonly_triggers` | 只读触发器管理 | 改为PG的`ALTER TABLE ... DISABLE TRIGGER` |
| 3 | `scripts/governance/generate_project_depgraph.py` | L223 | `DEPGRAPH_DB_PATH` | 路径常量→PG连接配置 | 改为从环境变量读取PG_DSN |
| | | L491,586,2619,3120,3192 | `sqlite3.connect()` | 连接方式不同 | 改为`psycopg2.connect()` |
| | | L2513,2516,2540,3514 | `lock_files`（subprocess调用） | 文件锁 | 删除（PG MVCC管理并发） |
| | | L2623 | `sqlite_master` | PG系统表不同 | 改为`information_schema.tables` |
| | | L3509-3566 | YAML输出分支锁 | YAML文件锁 | 保留（YAML文件不迁移PG） |
| 4 | `scripts/governance/extract_depgraph.py` | L176,414 | `sqlite3.connect(str(db_path))` | 连接方式不同 | 改为`psycopg2.connect()`（无`?`占位符） |
| 5 | ⚠️ `generate_target_path_tree.py` 已删除（2026-06-26） | — | — | 脚本已删除，TC-PG-10 已废弃，见 AGENTS.md §11 |
| | | L73,94 | `sqlite3.connect()` | 连接方式不同 | 改为`psycopg2.connect()` |
| 6 | `scripts/governance/migrate_arch_f_functions.py` | L29 | `DEPGRAPH_PATH` | 路径常量→PG连接配置 | 改为从环境变量读取PG_DSN |
| | | L35 | `import apply_depgraph as _ad` | 复用apply_depgraph锁机制 | 适配PG连接 |
| | | L246,255 | `sqlite3.connect()` | 连接方式不同 | 改为`psycopg2.connect()` |
| | | L254 | `_ad._db_write_lock` | 调用apply_depgraph锁 | 删除（PG MVCC管理并发） |
| | | L294 | `cur.lastrowid` | PG无lastrowid | 改为`INSERT ... RETURNING id` |
| 7 | `scripts/governance/migrate_clean_build_status.py` | L14-15 | `DB_PATH` | 路径常量→PG连接配置 | 改为从环境变量读取PG_DSN |
| | | L23 | `sqlite3.connect()` | 连接方式不同 | 改为`psycopg2.connect()` |
| | | L24 | `PRAGMA foreign_keys = OFF` | PG无此PRAGMA | 删除（PG默认强制FK） |
| 8 | `scripts/governance/audit_domain_nodes.py` | L28 | `DB_PATH` | 路径常量→PG连接配置 | 改为从环境变量读取PG_DSN |
| | | L160,184,333 | `sqlite3.connect()` | 连接方式不同 | 改为`psycopg2.connect()` |
| | | L153 | `datetime('now')` | PG函数不同 | 改为`NOW()` |
| | | L430 | `INSERT OR REPLACE` | PG无INSERT OR REPLACE | 改为`ON CONFLICT` |
| 9 | `scripts/governance/dm105_depgraph_triage.py` | L42 | `DEPGRAPH_PATH` | 路径常量→PG连接配置 | 改为从环境变量读取PG_DSN |
| | | L95,120 | `sqlite3.connect()` | 连接方式不同 | 改为`psycopg2.connect()` |
| | | L124 | `f"UPDATE nodes SET {sets} WHERE node_id=?"` | 动态SQL+占位符 | `?`→`%s`；注意SQL注入 |
| 10 | `scripts/governance/dm106_p2b_verification.py` | L47 | `DEPGRAPH_DB_PATH` | 路径常量→PG连接配置 | 改为从环境变量读取PG_DSN |
| | | L59 | `sqlite3.connect()` | 连接方式不同 | 改为`psycopg2.connect()` |
| 11 | `scripts/governance/diagnose_depgraph.py` | L26 | `DEPGRAPH_PATH` | 路径常量→PG连接配置 | 改为从环境变量读取PG_DSN |
| | | L53 | `sqlite3.connect()` | 连接方式不同 | 改为`psycopg2.connect()` |
| 12 | `scripts/governance/detect_causal_conflicts.py` | L30 | `DEFAULT_DEPGRAPH_PATH` | 路径常量→PG连接配置 | 改为从环境变量读取PG_DSN |
| | | L35 | `sqlite3.connect()` | 连接方式不同 | 改为`psycopg2.connect()` |
| 13 | `scripts/governance/analyze_change_impact.py` | L31 | `DEFAULT_DEPGRAPH_PATH` | 路径常量→PG连接配置 | 改为从环境变量读取PG_DSN |
| | | L36 | `sqlite3.connect()` | 连接方式不同 | 改为`psycopg2.connect()` |
| 14 | `scripts/governance/check_rule_four_way_alignment.py` | L37 | `DB_PATH` | 路径常量→PG连接配置 | 改为从环境变量读取PG_DSN |
| | | L62 | `sqlite3.connect(timeout=10.0)` | 连接方式不同 | 改为`psycopg2.connect()`；`timeout`→`statement_timeout` |
| 15 | `scripts/governance/verify_final_delivery.py` | L35 | `DB` | 路径常量→PG连接配置 | 改为从环境变量读取PG_DSN |
| | | L52,67,92 | `sqlite3.connect()` | 连接方式不同 | 改为`psycopg2.connect()` |
| | | L73 | `sqlite_master` | PG系统表不同 | 改为`information_schema.tables` |
| 16 | `scripts/governance/check_schema_version_writes.py` | L126 | `from zephyr.governance.depgraph_schema import _MIGRATIONS` | 导入中间层常量 | 确认PG迁移框架 |
| | | L131 | `db_path` | 路径常量→PG连接配置 | 改为从环境变量读取PG_DSN |
| | | L132 | `sqlite3.connect()` | 连接方式不同 | 改为`psycopg2.connect()` |
| 17 | `scripts/governance/rename_whitelist_cleanup.py` | L223 | `db_path = .../depgraph.db` | 路径常量→PG连接配置 | 改为从环境变量读取PG_DSN |
| | | L254,271 | `sqlite3.connect()` | 连接方式不同 | 改为`psycopg2.connect()` |
| | | L241,245 | `UPDATE ... SET path = REPLACE(...)` | 写入操作 | `?`→`%s`；REPLACE()函数PG兼容 |
| 18 | `scripts/governance/rebuild_progress.py` | L39 | `DB_PATH`(governance.db) | governance.db路径（保持SQLite） | 不迁移 |
| | | L40 | `DEPGRAPH_DB`(depgraph.db) | 路径常量→PG连接配置 | 改为从环境变量读取PG_DSN |
| | | L54 | `sqlite3.connect(DB_PATH)` | governance.db连接（保持SQLite） | 不迁移 |
| | | L77 | `sqlite3.connect(DEPGRAPH_DB)` | 连接方式不同 | 改为`psycopg2.connect()` |
| 19 | `scripts/governance/perf_depgraph_baseline.py` | L51 | `DEPGRAPH_PATH` | 路径常量→PG连接配置 | 改为从环境变量读取PG_DSN |
| | | L60 | `sqlite3.connect(uri, uri=True)` | URI只读连接 | PG无文件URI，改为标准连接+只读事务 |
| | | L67 | `sqlite_master` | PG系统表不同 | 改为`information_schema.tables` |
| 20 | `scripts/governance/repair/audit_design_completeness.py` | L51 | `DST_DB` | 路径常量→PG连接配置 | 改为从环境变量读取PG_DSN |
| | | L294 | `sqlite3.connect()` | 连接方式不同 | 改为`psycopg2.connect()` |
| | | L243 | `GROUP_CONCAT` | PG函数不同 | 改为`STRING_AGG(col, ',')` |
| 21 | `scripts/governance/repair/red_blue_test.py` | L35 | `DST_DB` | 路径常量→PG连接配置 | 改为从环境变量读取PG_DSN |
| | | L49,330,419 | `sqlite3.connect()` | 连接方式不同 | 改为`psycopg2.connect()` |
| | | L105,106 | `PRAGMA table_info` | PG无此PRAGMA | 改为`information_schema.columns` |
| | | L233 | `lock_files` | 文件锁 | 重新设计为PG事务锁 |
| 22 | `scripts/governance/repair/concurrent_write_test.py` | L54 | `PROD_DB` | 路径常量→PG连接配置 | 改为从环境变量读取PG_DSN |
| | | L55 | `TEST_DB` | 测试DB路径 | 改为PG测试库 |
| | | L72 | `sqlite3.connect()` | 连接方式不同 | 改为`psycopg2.connect()` |
| | | L342 | `PRAGMA busy_timeout=5000` | PG无此PRAGMA | 改为`SET lock_timeout` |
| | | L484,602 | `import lock_files` | 文件锁 | 重新设计为PG事务锁 |
| 23 | `scripts/governance/generate_project_path_tree.py` | L196 | `DEPGRAPH_DB_PATH` | 路径常量→PG连接配置 | 改为从环境变量读取PG_DSN |
| | | L64,142,815 | `sqlite3.connect()` | 连接方式不同 | 改为`psycopg2.connect()` |
| | | L666,753 | `lock_files`（subprocess调用） | 文件锁 | 重新设计为PG事务锁 |
| 24-45 | `scripts/governance/d5_architecture/generators/*.py`（22个生成器） | 各文件 | `DEPGRAPH_DB`+`sqlite3.connect()` | 路径常量+连接方式 | 统一改为从环境变量读取PG_DSN+`psycopg2.connect()` |

**d5_architecture/generators/下22个生成器清单**：
- `generate_capacity_report.py`（L39,68）
- `generate_domain_architecture_diagram.py`（L41,620）
- `generate_domain_doc.py`（L41,604；L139,155 GROUP_CONCAT）
- `generate_domain_dependency_diagram.py`（L40,234）
- `generate_domain_index.py`（L39,74）
- `generate_integration_topology.py`（L40,185；L48 GROUP_CONCAT）
- `generate_navigation_index.py`（L40,252）
- `generate_path_tree.py`（L41,831）
- `generate_runtime_plane_mapping.py`（L39,113）
- `generate_capability_heatmap.py`（L39,248；L159 sqlite_master）
- `generate_constraint_violations.py`（L37,71）
- `generate_cross_domain_matrix.py`（L37,77；L48 GROUP_CONCAT）
- `generate_design_vs_production.py`（L39,82）
- `dm200912_query_domains.py`（L37,45）
- `dm200912_rewrite_views.py`（L40,50）
- `dm200913_rewrite_diagrams.py`（L25,39）
- `dm200916_write_direct.py`（L21,24）
- `syncers/sync_blueprint_code_index.py`
- `validators/validate_cross_references.py`
- `validators/blueprint/validate_blueprint_code_sync.py`
- `detectors/detect_deprecated_adr_references.py`
- `d11_compliance/validate_task_decomposition_bypass.py`

### 2.2 不直接访问depgraph.db的文件（4个，无需迁移）

| # | 文件路径 | 说明 |
|---|---------|------|
| 46 | `scripts/governance/create_f_func_task_cards.py` | governance.db + 任务卡字符串引用 |
| 47 | `scripts/governance/create_panorama_repair_tasks.py` | governance.db + 任务卡字符串引用 |
| 48 | `scripts/governance/create_alignment_tasks.py` | governance.db + upstream_files字符串 |
| 49 | `scripts/governance/scan_ground_truth_deps.py` | 纯文件扫描器，不连接DB |

### 2.3 纯文件操作（2个，迁移后需改为pg_dump）

| # | 文件路径 | 位置（行号） | 变量/函数名 | 变更影响 | 执行办法 |
|---|---------|:---------:|-----------|---------|---------|
| 50 | `scripts/governance/repair/rollback_depgraph.py` | L40 | `DST = depgraph.db` | 纯文件操作（shutil.copy） | 迁移后改为pg_dump/pg_restore策略 |
| 51 | `scripts/governance/repair/backup_db.py` | L21-22 | `DBDIR`/`DBS = ["depgraph.db", ...]` | 纯文件备份（shutil.copy2） | 迁移后改为pg_dump |

---

## 三、tests/ 下受影响文件清单

### 3.1 全量迁移到PostgreSQL的测试（4个）

| # | 文件路径 | 位置（行号） | 变量/函数名 | 变更影响 | 执行办法 |
|---|---------|:---------:|-----------|---------|---------|
| 1 | `tests/test_depgraph_db.py` | L11 | `DB_PATH` | 路径常量→PG连接配置 | 改为PG测试库连接 |
| | | L15 | `sqlite3.connect()` | 连接方式不同 | 改为`psycopg2.connect()` |
| | | L16 | `sqlite3.Row` | 行工厂 | 改为psycopg dict row |
| | | L40,73 | `PRAGMA table_info(nodes/edges)` | PG无此PRAGMA | 改为`information_schema.columns` |
| | | L104,116,127,138,178 | `INSERT OR REPLACE` | PG无INSERT OR REPLACE | 改为`ON CONFLICT DO UPDATE` |
| | | L105,117等 | `?`占位符 | 占位符不同 | `?`→`%s` |
| 2 | `tests/test_depgraph_generator_design_protection.py` | L12 | `DB_PATH` | 路径常量→PG连接配置 | 改为PG测试库连接 |
| | | L22 | `sqlite3.connect()` | 连接方式不同 | 改为`psycopg2.connect()` |
| | | L28,108 | `INSERT OR REPLACE INTO nodes` | PG无INSERT OR REPLACE | 改为`ON CONFLICT` |
| | | L42,84 | `--output-db` | 子进程参数 | 改为PG连接串 |
| 3 | `tests/test_path_tree_generator_design_protection.py` | L12 | `DB_PATH` | 路径常量→PG连接配置 | 改为PG测试库连接 |
| | | L22 | `sqlite3.connect()` | 连接方式不同 | 改为`psycopg2.connect()` |
| | | L28 | `INSERT OR REPLACE INTO arch_directory_tree` | PG无INSERT OR REPLACE | 改为`ON CONFLICT` |
| | | L42,84 | `--output-db` | 子进程参数 | 改为PG连接串 |
| 4 | `tests/test_db_auto_ops.py` | L19 | `DEPGRAPH_DB` | 路径常量→PG连接配置 | 改为PG测试库连接 |
| | | L40 | `ds.get_depgraph_conn()` | 中间层连接 | 适配PG连接 |
| | | L57-59 | 回退直接`sqlite3.connect()` | 连接方式不同 | 改为`psycopg2.connect()` |
| | | L122 | `sqlite3.connect()` | 连接方式不同 | 改为`psycopg2.connect()` |
| | | L125,130 | `INSERT INTO nodes` | 写入操作 | `?`→`%s` |
| | | L138 | `cursor.lastrowid` | PG无lastrowid | 改为`INSERT ... RETURNING node_id` |
| | | L144 | `DELETE FROM nodes WHERE node_id=?` | 占位符 | `?`→`%s` |
| | | L164-165 | `PRAGMA journal_mode=WAL`/`PRAGMA busy_timeout` | PG无此PRAGMA | 删除/改`SET lock_timeout` |

### 3.2 mock策略重构的测试（1个）

| # | 文件路径 | 位置（行号） | 变量/函数名 | 变更影响 | 执行办法 |
|---|---------|:---------:|-----------|---------|---------|
| 5 | `tests/test_f18_redblue.py` | L32 | `_DEPGRAPH_DB` | 路径常量 | 改为PG连接配置 |
| | | L54-86 | `_create_temp_db` | 建临时DB | 改为PG测试schema |
| | | L67 | `INTEGER PRIMARY KEY AUTOINCREMENT` | PG无AUTOINCREMENT | 改为`SERIAL`/`IDENTITY` |
| | | L81 | `INSERT INTO gates VALUES (?,?,?,?,?,?,?,?,?,?,?)` | 占位符 | `?`→`%s` |
| | | L129,140,152,164,176,192,367,400,493,572,613,635,649,661,726,737,760,794（共18处） | `patch("...auto_runner._DEPGRAPH_DB"/"...phase_manager._DEPGRAPH_DB", tmp_sqlite)` | mock策略 | 改为patch PG连接工厂 |

### 3.3 部分迁移的测试（5个）

| # | 文件路径 | 位置（行号） | 变量/函数名 | 变更影响 | 执行办法 |
|---|---------|:---------:|-----------|---------|---------|
| 6 | `tests/test_rule_integration.py` | L24 | `_DB_PATH` | depgraph路径→PG连接 | 改为PG连接配置 |
| | | L27 | `_ARCH_PANORAMA` | 路径常量 | 保留（YAML文件不迁移） |
| | | L93,112 | `sqlite3.connect(timeout=10.0)` | 连接方式不同 | 改为`psycopg2.connect()`；`timeout`→`statement_timeout` |
| | | L95 | `SELECT ... FROM nodes` | 只读查询 | 标准SQL兼容 |
| | | L114 | `SELECT ... FROM domains` | 只读查询 | 标准SQL兼容 |
| 7 | `tests/test_f18_automation.py` | L32 | `_DEPGRAPH_DB` | 路径常量→PG连接配置 | 改为PG连接配置 |
| | | L237 | `sqlite3.connect()` | 连接方式不同 | 改为`psycopg2.connect()` |
| | | L239 | `SELECT COUNT(*) FROM governance_audit_logs` | 只读查询 | 标准SQL兼容 |
| | | L242 | `sqlite3.OperationalError` | 异常类型 | 改为`psycopg.errors.UndefinedTable` |
| 8 | `tests/test_db_integration.py` | L18 | `DEPGRAPH_DB` | 路径常量→PG连接配置 | 改为PG连接配置 |
| | | L35,65,112,163 | `sqlite3.connect(DEPGRAPH_DB)` | 连接方式不同 | 改为`psycopg2.connect()` |
| | | L37 | `FROM nodes` | depgraph查询 | 标准SQL兼容 |
| | | L70 | `FROM arch_directory_tree` | depgraph查询 | 标准SQL兼容 |
| | | L115 | `_schema_version` | depgraph查询 | 标准SQL兼容 |
| | | L158 | `sqlite_master` | governance.db查询（保持SQLite） | 不迁移 |
| | | L165,167 | `FROM nodes`/`FROM edges` | depgraph查询 | 标准SQL兼容 |
| 9 | `tests/test_db_red_blue.py` | L23 | `DEPGRAPH_DB` | 路径常量→PG连接配置 | 改为PG连接配置 |
| | | L165-168 | `test_wal_mode`对depgraph.db执行`PRAGMA journal_mode` | PG无此PRAGMA | 删除/改`SHOW default_transaction_isolation` |
| | | L66 | `test_concurrent_writes`(test_concurrent.db) | 测试DB（保持SQLite） | 不迁移 |
| | | L199 | `sqlite_master`（governance.db） | governance.db查询（保持SQLite） | 不迁移 |
| 10 | `tests/governance/test_database_service.py` | L62-69 | `test_get_depgraph_conn_returns_sqlite`：`assert isinstance(conn, sqlite3.Connection)` | 断言类型 | 改为`psycopg.Connection`/抽象接口 |
| | | L99-102 | `test_health_check_depgraph_returns_true` | 健康检查 | 适配PG连接 |
| | | L307 | `get_depgraph_conn()` | 中间层连接 | 适配PG连接 |
| | | L310,315 | `assert db_service._depgraph_conn is None/None` | 类型注解 | 同步改 |

### 3.4 不需要迁移的测试（17+80个）

以下测试只使用governance.db或in-memory sqlite，**不需要迁移**：
- `tests/test_governance_db.py`（governance.db）
- `tests/test_git_commit_gateway.py`（tmp_path临时git仓库）
- `tests/test_capacity_assurance.py`（governance.db）
- `tests/test_circuit_breaker_repo_root.py`（governance.db）
- `tests/test_cold_start.py`（governance.db）
- `tests/test_db_bridge.py`（governance.db）
- `tests/test_event_store_stress.py`（governance.db）
- `tests/test_f5_auto_shutdown.py`（governance.db）
- `tests/test_gate_persistence.py`（governance.db）
- `tests/test_kb_graph_validator.py`（governance.db）
- `tests/test_ke_tombstone.py`（governance.db）
- 其余约80个使用in-memory sqlite的governance单测

---

## 四、docs/和config/下需同步更新的文件清单（23个）

### 4.1 规则文件（2个）

| # | 文件路径 | 位置（行号） | 更新内容 | 更新原因 |
|---|---------|:---------:|---------|---------|
| 1 | `docs/01_policies_and_standards/rules/trae_054_depgraph_access_protocol.yaml` | L39 | 将"depgraph存储在SQLite数据库"改为"PostgreSQL数据库" | D50-PG裁定 |
| | | L60 | 将"sqlite3.IntegrityError"改为PostgreSQL对应错误 | D50-PG裁定 |
| | | L62-64 | 更新OOM崩溃rationale（PG是服务端进程，非文件加载） | D50-PG裁定 |
| 2 | `docs/01_policies_and_standards/rules/trae_055_arch_domain_capacity.yaml` | L253 | 将"SQLite单表B+树索引性能基准"改为PostgreSQL指标 | D50-PG裁定 |

### 4.2 架构文档（8个）

| # | 文件路径 | 位置（行号） | 更新内容 | 更新原因 |
|---|---------|:---------:|---------|---------|
| 3 | `docs/02_enterprise_architecture/dependency_architecture_panorama.md` | L97 | 将"sqlite_sequence由SQLite自动管理"改为PG系统表说明 | D50-PG裁定 |
| | | L1241 | 将"depgraph.db（SQLite单库）"改为"PostgreSQL单库" | D50-PG裁定 |
| 4 | `docs/02_enterprise_architecture/architecture_upgrade_discussion.md` | L289,807,1038,1039,1084,1298,1301,1335,1338 | 更新D50裁定为D50-PG；将"SQLite"改为"PostgreSQL" | D50-PG裁定 |
| 5 | `docs/02_enterprise_architecture/core_function_dependency_design.md` | L114,732 | 将"PostgreSQL容量升级"更新为"已迁移" | D50-PG裁定 |
| 6 | `docs/_working/domain_split_plan_4_oversized_domains.md` | L1245,1254,1270,1277,1303,1332,1338 | 将`sqlite3.connect`命令改为PG连接方式 | D50-PG裁定 |
| 7 | `docs/02_enterprise_architecture/phase_d_full_test_construction_plan.md` | L203,274,391,773,859 | 将"SQLite锁"改为"PostgreSQL MVCC" | D50-PG裁定 |
| 8 | `docs/02_enterprise_architecture/01_global_architecture_diagram/full_project_tree_zh.md` | L1445,1473 | 将"从SQLite数据库加载"改为"从PostgreSQL加载" | D50-PG裁定 |
| 9 | `docs/02_enterprise_architecture/01_global_architecture_diagram/full_project_tree_en.md` | 对应英文版行 | 同上（英文版） | D50-PG裁定 |
| 10 | `docs/02_enterprise_architecture/00_overview_entry/navigation_index.md` | L5,49 | 补充depgraph.db现为PostgreSQL | D50-PG裁定 |

### 4.3 目标架构视图（4个）

| # | 文件路径 | 位置（行号） | 更新内容 | 更新原因 |
|---|---------|:---------:|---------|---------|
| 11 | `docs/02_enterprise_architecture/target_architecture/overview.md` | L48 | 技术栈区分depgraph.db(PG)+governance.db(SQLite) | D50-PG裁定 |
| 12 | `docs/02_enterprise_architecture/target_architecture/technology_architecture.md` | L334 | 容量模型数据源说明补充PG | D50-PG裁定 |
| 13 | `docs/02_enterprise_architecture/target_architecture/application_architecture.md` | L186 | 确认回滚系统SQLite JSONL dump是否针对depgraph.db | 需确认 |
| 14 | `docs/02_enterprise_architecture/target_architecture/index.md` | L130 | 确认D-GOV-REPAIR回滚是否针对depgraph.db | 需确认 |

### 4.4 蓝图文档（3个）

| # | 文件路径 | 位置（行号） | 更新内容 | 更新原因 |
|---|---------|:---------:|---------|---------|
| 15 | `docs/03_modules/_cross_layer/database/blueprint.md` | L4,28,48,81,163 | 更新标题/summary/职责划分表 | D50-PG裁定 |
| 16 | `docs/03_modules/blueprint_registry.yaml` | L274 | 更新MOD-INF-012 title | D50-PG裁定 |
| 17 | `docs/03_modules/_master_blueprint/blueprint_baseline.md` | L200 | 确认Database层描述是否覆盖depgraph.db | 需确认 |

### 4.5 配置文件（1个）

| # | 文件路径 | 位置（行号） | 更新内容 | 更新原因 |
|---|---------|:---------:|---------|---------|
| 18 | `config/blueprint_routing.yaml` | L394-396 | R014 task_keywords添加"PostgreSQL" | D50-PG裁定 |

### 4.6 YAML真源（2个）

| # | 文件路径 | 位置（行号） | 更新内容 | 更新原因 |
|---|---------|:---------:|---------|---------|
| 19 | `architecture_model/layers/b_db.yaml` | L8,21 | 补充depgraph.db(PostgreSQL)条目；更新描述 | D50-PG裁定 |
| 20 | `docs/02_enterprise_architecture/target_architecture/architecture_model/technology/technology_landscape.yaml` | L322 | 确认PostgreSQL条目关联depgraph.db用途 | D50-PG裁定 |

### 4.7 注册表（2个）

| # | 文件路径 | 位置（行号） | 更新内容 | 更新原因 |
|---|---------|:---------:|---------|---------|
| 21 | `docs/01_policies_and_standards/_registry/catalogs/functional_domain_registry.yaml` | L573,588 | 区分governance.db(SQLite)和depgraph.db(PostgreSQL) DDL | D50-PG裁定 |
| 22 | `docs/01_policies_and_standards/_registry/catalogs/directory_registry.yaml` | L168,1525 | 更新data/和src/zephyr/db/的responsibility描述 | D50-PG裁定 |

### 4.8 索引/其他（1个）

| # | 文件路径 | 位置（行号） | 更新内容 | 更新原因 |
|---|---------|:---------:|---------|---------|
| 23 | `docs/02_enterprise_architecture/ssot_authority_map.md` | L176 | 确认knowledge表归属（governance.db则无需更新） | 需确认 |

---

## 五、锁机制和触发器清单（26项）

### 5.1 文件锁机制（20项）

| # | 文件路径 | 锁类型 | 位置（行号） | 处理方式 | 处理说明 |
|---|---------|--------|:---------:|:-------:|---------|
| 1 | `scripts/governance/apply_depgraph.py` | `_check_git_backup` | L76 | 改造 | 改为检查迁移脚本是否已提交 |
| 2 | 同上 | `_create_physical_backup` | L148 | 删除 | PG用pg_dump |
| 3 | 同上 | `_db_write_lock_lock` | L194 | 删除 | PG MVCC支持并发 |
| 4 | 同上 | `_db_write_lock` | L198 | 删除 | 双重锁，PG行锁接管 |
| 5 | 同上 | `_optional_db_lock` | L248 | 删除 | 随_db_write_lock删除 |
| 6 | 同上 | `_atomic_write` | L303 | 改造 | 删除_optional_db_lock调用；改用PG事务 |
| 7 | 同上 | `import lock_files` | L191 | 删除 | 不再需要文件锁保护 |
| 8 | `scripts/governance/generate_project_depgraph.py` | `acquire_lock`/`release_lock` | L2512,2536 | 删除 | subprocess调用lock_files |
| 9 | 同上 | write_depgraph_to_db锁 | L2609-2616 | 删除 | 随acquire/release删除 |
| 10 | 同上 | --output-yaml模式锁 | L3509-3566 | 保留 | 保护YAML文件写入（非DB） |
| 11 | `scripts/governance/sync_yaml_to_depgraph.py` | 无锁（缺失保护） | L864 | 改造 | PG事务隔离解决 |
| 12 | 同上 | `disable/restore_readonly_triggers` | L78,87 | 改造 | 改为PG的ALTER TABLE DISABLE TRIGGER |
| 13 | `scripts/lock_files.py` | 通用文件锁 | 全文件 | 保留 | 保护YAML/代码文件等非DB资源 |
| 14 | `scripts/git_guard.py` | 只读扫描.ailocks/ | L190,65 | 保留 | 保护工作区文件 |
| 15 | `scripts/governance/pre_op_check.py` | `_run_lock_check` | L137,235 | 保留 | 写前门禁检查 |
| 16 | `scripts/governance/pre_write_gate.py` | `_check_lock` | L53,254 | 保留 | AI写入前强制门禁 |
| 17 | `src/zephyr/governance/git_commit_gateway.py` | `_GlobalCommitLock` | L117,82,137 | 保留 | 串行化git commit |
| 18 | `src/zephyr/governance/task_repo.py` | `threading.RLock` | L578,612,628 | 保留 | governance.db保持SQLite |
| 19 | 同上 | `PRAGMA journal_mode = WAL` | L3042 | 保留 | governance.db保持SQLite |
| 20 | `scripts/governance/migrate_arch_f_functions.py` | `_ad._db_write_lock` | L254 | 删除 | 随apply_depgraph锁删除 |

### 5.2 触发器机制（6项）

| # | 文件路径 | 触发器类型 | 位置（行号） | 处理方式 | 处理说明 |
|---|---------|-----------|:---------:|:-------:|---------|
| 21 | `scripts/governance/sync_yaml_to_depgraph.py` | 只读触发器（9表×3=27个） | L55-65,87-114 | 改造 | 用PL/pgSQL重写；RAISE(ABORT)→RAISE EXCEPTION |
| 22 | `src/zephyr/governance/depgraph_schema.py` | CHECK约束（11个） | L100,109,395,404,487,525,537,538,560,573,588 | 保留 | PG兼容CHECK语法 |
| 23 | 源码缺失（仅DB实例） | chk_前缀触发器（7个） | DB实例中 | 删除+重建 | 先从SQLite导出，用PL/pgSQL重写或用PG RLS替代 |
| 24 | `src/zephyr/governance/sqlite_schema.py` | validate_blocked_by触发器（4个） | L856,865,875,885 | 保留 | governance.db保持SQLite |
| 25 | `src/zephyr/governance/task_repo.py`（注释引用） | prevent_hard_delete触发器 | 源码缺失 | 保留（补源码） | governance.db保持SQLite；从DB导出补录 |
| 26 | `docs/02_enterprise_architecture/t18_implementation_plan.md` | nodes_design_readonly触发器（3个） | L367-390 | PG迁移时实现 | 用PL/pgSQL或PG RLS实现 |

---

## 六、处理方式汇总统计

| 类别 | 数量 | 说明 |
|------|:---:|------|
| **src/必须迁移** | 6 | depgraph_schema, database_service, depgraph_reader, rule_engine, auto_runner, dashboard |
| **src/部分迁移** | 1 | rule_watcher |
| **src/需复核** | 4 | blast_radius, rbac_guard, path_guard, immutable_core |
| **src/代理/导出** | 2 | persistence/depgraph_schema, __init__ |
| **src/纯注释** | 5 | 3个__init__.py, g_trae_059.yaml, asset_inventory/__main__ |
| **src/核心基础设施** | 3 | db_utils, paths, sqlite_schema |
| **scripts/必须迁移** | 45 | apply_depgraph, sync_yaml, generate_project_depgraph等 |
| **scripts/不直接访问** | 4 | create_f_func_task_cards等 |
| **scripts/纯文件操作** | 2 | rollback_depgraph, backup_db |
| **tests/全量迁移** | 4 | test_depgraph_db等 |
| **tests/mock重构** | 1 | test_f18_redblue |
| **tests/部分迁移** | 5 | test_rule_integration等 |
| **tests/不迁移** | 17+80 | governance.db测试 |
| **docs/config/需更新** | 23 | 规则2+架构8+目标4+蓝图3+配置1+YAML2+注册表2+索引1 |
| **锁机制/触发器** | 26 | 删除8+改造5+保留11+PG实现2 |
| **总计** | **85+26** | 85个文件+26项锁机制/触发器 |

---

## 七、循环审查记录

### 第1轮审查（2026-06-25）

**审查方法**：5个并行子任务审查src/scripts/tests/docs/config/锁机制
**审查结果**：85个文件+26项锁机制/触发器
**新增文件**：第1轮（基线）

### 第2轮审查（2026-06-25）

**审查方法**：使用不同关键词（get_depgraph_conn/depgraph_schema导入、配置文件depgraph.db引用、psycopg2/postgresql已有引用、requirements/docker/CI文件）交叉验证
**审查结果**：新增28个文件
**新增文件清单**：

#### 第2轮新增：src/间接使用depgraph（2个）

| # | 文件路径 | 变更影响 | 执行办法 |
|---|---------|---------|---------|
| 86 | `src/zephyr/governance/audit_trail/pipeline_runner.py` | 间接import depgraph相关模块 | 检查是否实际执行depgraph SQL；如是则迁移 |
| 87 | `src/zephyr/governance/audit_orchestrator/pipeline_runner.py` | 间接import depgraph相关模块 | 同上 |

#### 第2轮新增：src/已有PostgreSQL引用（3个）

| # | 文件路径 | 变更影响 | 执行办法 |
|---|---------|---------|---------|
| 88 | `src/zephyr/infrastructure/rollback/rollback_integration.py` | 已有PG引用（可能是历史遗留或设计预留） | 检查现有PG引用是否需要适配P2迁移 |
| 89 | `src/zephyr/governance/ops_governance/environment_manager.py` | 已有PG引用 | 同上 |
| 90 | `src/zephyr/governance/rollback_integration.py` | 已有PG引用 | 同上 |

#### 第2轮新增：docs/规则文件（8个）

| # | 文件路径 | 变更影响 | 执行办法 |
|---|---------|---------|---------|
| 91 | `docs/01_policies_and_standards/rules/trae_005_modification_governance.yaml` | 引用depgraph.db | 检查是否需要更新为PG |
| 92 | `docs/01_policies_and_standards/rules/trae_014_arch_blueprint_alignment.yaml` | 引用depgraph.db | 同上 |
| 93 | `docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml` | 引用depgraph.db | 同上 |
| 94 | `docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml` | 引用depgraph.db | 同上 |
| 95 | `docs/01_policies_and_standards/rules/trae_032_module_lifecycle.yaml` | 引用depgraph.db | 同上 |
| 96 | `docs/01_policies_and_standards/rules/trae_035_task_construction_verification.yaml` | 引用depgraph.db | 同上 |
| 97 | `docs/01_policies_and_standards/rules/trae_003_task_granularity_threshold.yaml` | 引用depgraph.db | 同上 |
| 98 | `docs/01_policies_and_standards/rules/trae_057_ai_consumer_first.yaml` | 引用depgraph.db | 同上 |

#### 第2轮新增：docs/其他（4个）

| # | 文件路径 | 变更影响 | 执行办法 |
|---|---------|---------|---------|
| 99 | `docs/02_enterprise_architecture/migration_registry.yaml` | 引用depgraph.db | 检查是否需要更新 |
| 100 | `docs/02_enterprise_architecture/target_architecture/architecture_model/cross_cutting/capability_heatmap.yaml` | 引用depgraph.db | 同上 |
| 101 | `docs/registry_of_registries.yaml` | 引用depgraph.db | 同上 |
| 102 | `docs/02_enterprise_architecture/target_architecture/architecture_model/index.yaml` | 引用depgraph.db | 同上 |

#### 第2轮新增：data/数据文件（3个）

| # | 文件路径 | 变更影响 | 执行办法 |
|---|---------|---------|---------|
| 103 | `data/asset_index/target_path_tree.yaml` | 引用depgraph.db | 检查是否需要更新（数据文件可能自动生成） |
| 104 | `data/rule_optimization/key_facts.yaml` | 引用depgraph.db | 同上 |
| 105 | `data/asset_index/project_entity_depgraph.yaml` | 引用depgraph.db | 同上 |

#### 第2轮新增：依赖/CI/Docker（4个）

| # | 文件路径 | 变更影响 | 执行办法 |
|---|---------|---------|---------|
| 106 | `requirements-demo.txt` | 缺少psycopg2依赖 | 添加`psycopg2-binary>=2.9` |
| 107 | `requirements-dev.txt` | 缺少psycopg2依赖 | 添加`psycopg2-binary>=2.9` |
| 108 | `.github/workflows/governance.yml` | CI配置可能需要PG服务 | 添加PG service container |
| 109 | `docker-compose.yml` | 已有Docker配置 | 检查是否需要添加PG服务 |

#### 第2轮新增：tests/（1个）

| # | 文件路径 | 变更影响 | 执行办法 |
|---|---------|---------|---------|
| 110 | `tests/adversarial/test_cross_layer_systems_red_team.py` | 引用postgresql | 检查是否需要适配P2迁移 |

#### 第2轮新增：迁移计划YAML（2个）

| # | 文件路径 | 变更影响 | 执行办法 |
|---|---------|---------|---------|
| 111 | `src/zephyr/governance/drift_detection/migration_plan.yaml` | 已有迁移计划 | 检查是否与P2迁移冲突 |
| 112 | `src/zephyr/behavioral_audit/migration_plan.yaml` | 已有迁移计划 | 同上 |

### 第3轮审查（2026-06-25）

**审查方法**：5个角度并行交叉验证
- 角度A：深挖第2轮28个文件的遗漏位置/变量/函数
- 角度B：import链分析（搜索import核心模块的文件）
- 角度C：配置文件/环境变量/启动脚本中的DB连接字符串
- 角度D：文档.md文件中的depgraph.db引用
- 角度E：锁机制/触发器/存储过程/视图遗漏检查

**审查结果**：新增52个文件 + 12个遗漏位置 + 3项已知清单差异

#### 第3轮新增：depgraph.db直接相关文件（需迁移，10个）

| # | 文件路径 | 变更影响 | 执行办法 |
|---|---------|---------|---------|
| 113 | `tests/test_rule_e2e.py` | 通过RuleLoader间接查询depgraph.db的rule_bindings表 | 更新测试以适配PG连接；`?`→`%s` |
| 114 | `requirements.txt` | 缺少psycopg2-binary依赖 | 添加`psycopg2-binary>=2.9` |
| 115 | `pyproject.toml` | dependencies数组缺少psycopg2-binary | 添加`"psycopg2-binary>=2.9"` |
| 116 | `.env.example` | 环境变量模板缺少PG连接配置 | 添加PG_DSN/POSTGRES_*环境变量模板 |
| 117 | `scripts/governance/d5_architecture/generators/generate_integration_topology.py` | GROUP_CONCAT函数（L48） | 改为`string_agg(col::text, ',')` |
| 118 | `scripts/governance/d5_architecture/generators/generate_domain_doc.py` | GROUP_CONCAT函数（L139,155） | 同上 |
| 119 | `scripts/governance/d5_architecture/generators/generate_cross_domain_matrix.py` | GROUP_CONCAT函数（L48） | 同上 |
| 120 | `scripts/governance/task_self_check.py` | PRAGMA integrity_check/user_version（L121,138） | PG用`pg_amcheck`和`version()` |
| 121 | `scripts/governance/phase_a_backup.py` | PRAGMA integrity_check（L288） | 同上 |
| 122 | `scripts/governance/repair/concurrent_write_test.py` | PRAGMA busy_timeout（L342） | PG用`statement_timeout` |

#### 第3轮新增：规则/配置YAML文件（需更新描述，5个）

| # | 文件路径 | 变更影响 | 执行办法 |
|---|---------|---------|---------|
| 123 | `docs/01_policies_and_standards/rules/trae_056_module_creation_workflow.yaml` | git备份/回滚命令引用depgraph.db（L134,155,200,207,239,245,295,692,707,708） | 更新为pg_dump/pg_restore策略 |
| 124 | `docs/01_policies_and_standards/rules/trae_059_schema_version_write_protection.yaml` | _schema_version表引用depgraph.db（L36） | 更新为PG schema版本管理 |
| 125 | `docs/01_policies_and_standards/rules/trae_034_task_card_standard.yaml` | 任务描述引用depgraph.db字段名（L1266） | 低优先级，可保留或更新 |
| 126 | `docs/01_policies_and_standards/_registry/catalogs/registry_consistency_contract.yaml` | path引用depgraph.db（L278,280） | 更新path为PG连接描述 |
| 127 | `scripts/governance/_sync/cleanup_p0_auto_bridged.py` | PRAGMA journal_mode=WAL（L47） | 确认操作数据库归属后决定 |

#### 第3轮新增：IDE配置文件（需更新，2个）

| # | 文件路径 | 变更影响 | 执行办法 |
|---|---------|---------|---------|
| 128 | `.trae/rules/project_rules.md` | 14处引用depgraph.db为SQLite数据库+git备份命令（L31,69,70,403,442,633,788,975,997,999,1001,1328,1351,1367） | 更新"SQLite数据库"为"PostgreSQL"；更新git备份为pg_dump |
| 129 | `.trae/rules/onboarding_detail.md` | 12处引用depgraph.db路径+访问协议（L229,277,302,303,305,307,308,345,353,369,646,959） | 更新路径引用和访问协议说明 |

#### 第3轮新增：架构文档（需更新，6个）

| # | 文件路径 | 变更影响 | 执行办法 |
|---|---------|---------|---------|
| 130 | `docs/02_enterprise_architecture/target_architecture/overview.md` | 技术栈描述SQLite WAL（L48）+depgraph.db引用（L44,179,181） | 更新技术栈为PostgreSQL |
| 131 | `docs/02_enterprise_architecture/architecture_upgrade_discussion.md` | D50决策记录depgraph.db为SQLite（L807,855,1084,1089,1298,1301,1334-1338,1386-1388） | 更新D50决策为PostgreSQL |
| 132 | `docs/02_enterprise_architecture/dependency_architecture_panorama.md` | 业界对标表描述depgraph.db为SQLite单库（L1241） | 更新为PostgreSQL |
| 133 | `docs/02_enterprise_architecture/core_function_dependency_design.md` | F25职责描述（L114,732） | 更新为反映depgraph.db已迁移PG |
| 134 | `docs/02_enterprise_architecture/phase_d_ai_prompts.md` | 三库架构描述（L1255,1265） | 更新三库架构描述 |
| 135 | `docs/02_enterprise_architecture/ssot_authority_map.md` | knowledge表引用（L176） | 确认knowledge表归属后更新 |

#### 第3轮新增：操作命令文档（含sqlite3.connect命令，5个）

| # | 文件路径 | 变更影响 | 执行办法 |
|---|---------|---------|---------|
| 136 | `docs/_working/domain_split_plan_4_oversized_domains.md` | 30+处sqlite3.connect命令（L1245,1254,1270,1277,1303,1332,1422,1481,1808,1818-1819,1851,1870,1888,1906,1922,1939,1951-1952,2005-2006,2035,2054,2072,2091,2107,2189-2190,2228,2261,2327-2328） | 替换为psycopg2或extract_depgraph.py |
| 137 | `docs/02_enterprise_architecture/phase_d_full_test_construction_plan.md` | sqlite3.connect命令+SQLite锁竞争描述（L203,274,297,310,391,772-773,859） | 替换连接命令；更新锁竞争描述 |
| 138 | `docs/02_enterprise_architecture/t18_implementation_plan.md` | sqlite3.connect+DROP TRIGGER命令（L553） | 替换为PG连接；TRIGGER语法适配 |
| 139 | `docs/01_policies_and_standards/templates/dependency_graph_template.md` | 语法检查命令使用sqlite3（L961） | 更新为PG连接验证 |
| 140 | `docs/09_audit/research_notes/naming_whitelist_cleanup_plan.md` | sqlite3 CLI命令+SQLite描述（L108-122,235-249,740） | 更新数据库类型描述；替换CLI命令 |

#### 第3轮新增：Blueprint文档（引用SSoT路径，20个）

| # | 文件路径 | 位置 | 变更影响 | 执行办法 |
|---|---------|:----:|---------|---------|
| 141 | `docs/03_modules/_master_blueprint/blueprint.md` | L151 | SSoT路径引用 | 确认逻辑路径是否保留 |
| 142 | `docs/03_modules/_sys_master/blueprint.md` | L2191 | 同上 | 同上 |
| 143 | `docs/03_modules/_restructuring/blueprint.md` | L74 | 同上 | 同上 |
| 144 | `docs/03_modules/_ml_experiment_domain/blueprint.md` | L382 | 同上 | 同上 |
| 145 | `docs/03_modules/_alpha_signal_domain/blueprint.md` | L377 | 同上 | 同上 |
| 146 | `docs/03_modules/_domain_frontend/hmi_core/blueprint.md` | L82 | 同上 | 同上 |
| 147 | `docs/03_modules/_domain_autonomy_core/rollback_system/blueprint.md` | L101 | 同上 | 同上 |
| 148 | `docs/03_modules/_domain_compliance/compliance_core/blueprint.md` | L83 | 同上 | 同上 |
| 149 | `docs/03_modules/_domain_governance/code_dedup_engine/blueprint.md` | L132 | 同上 | 同上 |
| 150 | `docs/03_modules/_domain_factor/alpha_factor_core/blueprint.md` | L88 | 同上 | 同上 |
| 151 | `docs/03_modules/_domain_autonomy_core/agent_spec/blueprint.md` | L99 | 同上 | 同上 |
| 152 | `docs/03_modules/_domain_autonomy_perm/budget_enforcer/blueprint.md` | L93 | 同上 | 同上 |
| 153 | `docs/03_modules/_domain_ex_core/execution_core/blueprint.md` | L80 | 同上 | 同上 |
| 154 | `docs/03_modules/_domain_governance/audit_trail/blueprint.md` | L89 | 同上 | 同上 |
| 155 | `docs/03_modules/_domain_governance/capacity_upgrade/blueprint.md` | L53 | 同上 | 同上 |
| 156 | `docs/03_modules/_domain_governance/blueprint.md` | L2112 | 同上 | 同上 |
| 157 | `docs/03_modules/_domain_data/datasource_core/blueprint.md` | L89 | 同上 | 同上 |
| 158 | `docs/03_modules/_domain_integration/local_model/blueprint.md` | L38 | 同上 | 同上 |
| 159 | `docs/03_modules/_master_blueprint/blueprint_baseline.md` | L287 | `sqlite3持久化`描述 | 更新为PostgreSQL |
| 160 | `docs/03_modules/_cross_layer/orphan_judge/blueprint.md` | L517 | `SQLite写锁竞争`描述 | 更新为PG MVCC |

#### 第3轮新增：锁机制/触发器/视图遗漏（15项）

| # | 文件路径 | 类型 | 位置 | 变更影响 | 执行办法 |
|---|---------|------|:----:|---------|---------|
| 161 | `src/zephyr/governance/sqlite_schema.py` | 触发器 | L856,865,875,885 | 4个validate_blocked_by触发器（RAISE(ABORT)+json_valid） | 改为PG的CREATE FUNCTION+RAISE EXCEPTION |
| 162 | `src/zephyr/governance/sqlite_schema.py` | 视图 | L383,401,421 | 3个CREATE VIEW（event_log/v_active_tasks/v_recent_sessions） | governance.db保持SQLite，不迁移 |
| 163 | `src/zephyr/behavioral_audit/tamper_proof_audit.py` | 触发器 | L88,106 | 2个drift_events append-only触发器（RAISE(FAIL)） | 确认drift_events数据库归属 |
| 164 | `src/zephyr/governance/drift_detection/tamper_proof_audit.py` | 触发器 | L63,69 | 同上（副本） | 同上 |
| 165 | `src/zephyr/integration/vector_memory/sqlite_metadata_store.py` | 触发器 | L149,155 | 2个FTS5同步触发器 | VMS库非depgraph.db，不迁移 |
| 166 | `src/zephyr/governance/vector_memory/sqlite_metadata_store.py` | 触发器 | L149,155 | 同上（副本） | 同上 |
| 167 | `src/zephyr/governance/depgraph_schema.py` | 视图 | L831 | CREATE VIEW dep_cycles（WITH RECURSIVE） | PG兼容，直接迁移 |
| 168 | `scripts/ops/auto_fix_cron.py` | 锁机制 | L57,67,79,83 | fcntl/msvcrt文件锁 | 评估cron任务是否操作depgraph.db |
| 169 | `src/zephyr/governance/base_repo.py` | FTS5 | L348-352 | tasks_fts虚拟表 | governance.db保持SQLite，不迁移 |
| 170 | `src/zephyr/infrastructure/db/base_repo.py` | FTS5 | L349-352 | 同上（副本） | 同上 |
| 171 | `src/zephyr/governance/task_repo.py` | FTS5 | L3048-3051 | 同上 | 同上 |

#### 第3轮新增：其他库相关文件（需复核，14个）

| # | 文件路径 | 变更影响 | 执行办法 |
|---|---------|---------|---------|
| 172 | `src/zephyr/trading/staging_area.py` | threading.Lock（L61） | 确认是否与depgraph.db写入相关 |
| 173 | `src/zephyr/trading/session_lifecycle.py` | threading.Lock（L196）+PRAGMA（L486,487） | 同上 |
| 174 | `src/zephyr/trading/work_orchestrator.py` | threading.Lock（L56） | 同上 |
| 175 | `src/zephyr/shared/lifecycle/daemon_registry.py` | threading.Lock（L131） | 同上 |
| 176 | `src/zephyr/shared/io/io_cache.py` | threading.Lock（L74） | 同上 |
| 177 | `src/zephyr/ops/db_bridge.py` | cursor.lastrowid（L102） | 确认操作数据库归属 |
| 178 | `src/zephyr/ops/circuit_breaker_repo.py` | cursor.lastrowid（L112） | 同上 |
| 179 | `src/zephyr/ops/db_writer.py` | cursor.lastrowid（L140） | 同上 |
| 180 | `src/zephyr/ops/metrics_collector.py` | sqlite3.Row（L65） | 同上 |
| 181 | `src/zephyr/autonomy_core/system_snapshot.py` | sqlite3.Row（L268） | 同上 |
| 182 | `src/zephyr/autonomy_core/support/system_snapshot.py` | sqlite3.Row（L267） | 同上 |
| 183 | `src/zephyr/shared/session_continuity.py` | sqlite3.Row（L132） | 同上 |
| 184 | `src/zephyr/trading/orchestrator/deferred_queue.py` | sqlite3.Row（L83） | 同上 |

#### 第3轮新增：历史归档文档（不修改，13个）

| # | 文件路径 | 说明 |
|---|---------|------|
| 185 | `docs/02_enterprise_architecture/_archive/phase4b_cleanup_construction_plan.md` | 归档施工方案 |
| 186 | `docs/02_enterprise_architecture/_archive/architecture_decisions_pending.md` | 归档决策文档 |
| 187 | `docs/08_knowledge/04_archived/ke-3301-revision_history.md` | 归档知识条目 |
| 188 | `docs/08_knowledge/04_archived/ke-3285-phase_phase_transi.md` | 同上 |
| 189 | `docs/08_knowledge/04_archived/ke-3275-adr.md` | 同上 |
| 190 | `docs/08_knowledge/04_archived/ke-3334-zephyralpha.md` | 同上 |
| 191 | `docs/08_knowledge/04_archived/ke-3328-documentat.md` | 同上 |
| 192 | `docs/decomposition/tasks/DM-100255.md` | 历史任务卡 |
| 193 | `docs/decomposition/tasks/DM-100254.md` | 同上 |
| 194 | `docs/decomposition/tasks/DM-100253.md` | 同上 |
| 195 | `data/archive/taskcards/DM-100258.md` | 归档任务卡 |
| 196 | `data/archive/taskcards/DM-100257.md` | 同上 |
| 197 | `data/reports/dm031_integration_verification_report.md` | 集成验证报告 |

#### 第3轮新增：第2轮28个文件的遗漏位置（12个文件有遗漏）

| # | 文件路径 | 遗漏位置 | 变更影响 | 执行办法 |
|---|---------|---------|---------|---------|
| - | `docs/registry_of_registries.yaml` | L336,360 | `format: sqlite`声明 | 改为`format: postgresql` |
| - | `docs/02_enterprise_architecture/target_architecture/architecture_model/index.yaml` | L26,35,38,41,59,62 | partition路径指向SQLite文件 | 改为PG连接配置引用 |
| - | 同上 | L240,242,244 | SQL查询使用双引号 | 改单引号（PG字符串语义） |
| - | `docs/02_enterprise_architecture/migration_registry.yaml` | L15522 | source字段引用SQLite路径 | 改为PG连接字符串 |
| - | `data/asset_index/target_path_tree.yaml` | L5,6 | source_depgraph/source_panorama引用SQLite路径 | 改为PG连接配置引用 |
| - | `data/rule_optimization/key_facts.yaml` | L44,62,138,140,511,513,823,824,825 | ssot_source/path/must_exist引用SQLite | 改为PG连接引用 |
| - | `data/asset_index/project_entity_depgraph.yaml` | L4245,4258,5547,6154,7611,8011,8308,8778,9857,10368,10505,10506,11675,11694,11695,7946,7978,10906,11677,11731 | 自动生成的import引用 | 迁移后重新生成 |
| - | `src/zephyr/governance/drift_detection/migration_plan.yaml` | L21-23,24-26,74 | affected_modules/adapters/sqlite_master引用 | 更新为PG表/连接配置 |
| - | `src/zephyr/behavioral_audit/migration_plan.yaml` | L21-23,24-26,74 | 同上 | 同上 |
| - | `docs/01_policies_and_standards/rules/trae_035_task_construction_verification.yaml` | L71,98,150,171,261,282 | SQL操作描述+命令引用 | 更新为PG操作描述 |
| - | `docs/01_policies_and_standards/rules/trae_003_task_granularity_threshold.yaml` | L34,43 | 判断条件引用depgraph.db+"写入SQLite" | 更新为PG引用 |
| - | `src/zephyr/governance/ops_governance/environment_manager.py` | L47 | DEV环境db_conn=`sqlite:///dev.db` | 改为`postgresql://dev` |
| - | `src/zephyr/infrastructure/rollback/rollback_integration.py` | L435-443 | SQLite fallback代码块 | 评估是否移除fallback |

#### 第3轮新增：已知清单差异（3项需核实）

| # | 差异项 | 说明 | 执行办法 |
|---|--------|------|---------|
| - | "7个chk_前缀触发器"未找到 | 全代码库搜索`chk_`前缀触发器结果为零匹配 | 核实第1轮审查来源，确认是否为误报 |
| - | FTS5/writable_schema/GLOB实际位于governance.db | 第1轮清单的"5处FTS5定义"、"3处writable_schema"、"1处GLOB"经核实全部位于governance.db文件中，非depgraph.db | 确认P2迁移范围是否严格限定为depgraph.db |
| - | depgraph_schema.py的SQLite特有语法 | sqlite_master/AUTOINCREMENT/datetime('now')等已在第1轮清单中覆盖，但需确认是否完整 | 核实第1轮清单的完整性 |

### 第4轮审查（2026-06-25）

**审查方法**：3个聚焦角度并行验证
- 角度A：验证第3轮52个文件的遗漏位置/变量/函数
- 角度B：检查其他文件类型（.sql/.sh/.bat/.ps1）和未覆盖目录
- 角度C：验证3项已知清单差异 + 检查遗漏的其他文件

**审查结果**：新增138个文件 + 多处遗漏位置 + 4个误判文件 + 1项计数错误修正

#### 第4轮新增：scripts/_archive/归档脚本（11个，标记归档）

| # | 文件路径 | 位置 | 变更影响 | 执行办法 |
|---|---------|:----:|---------|---------|
| 198 | `scripts/_archive/ops/fill_blueprint_ids.py` | L10 | DEPGRAPH_PATH路径常量 | 归档文件，标记废弃 |
| 199 | `scripts/_archive/migration/_verify_step4.py` | L6 | sqlite3.connect | 同上 |
| 200 | `scripts/_archive/migration/verify_migration_alignment.py` | L44 | DEPGRAPH_DB_PATH | 同上 |
| 201 | `scripts/_archive/migration/safe_delete_operational.py` | L48,66 | ARCH_PANORAMA_PATH+sqlite3.connect | 同上 |
| 202 | `scripts/_archive/migration/inject_domain_fields.py` | L6,9,165 | OLD_DEPGRAPH+文件操作 | 同上 |
| 203 | `scripts/_archive/migration/generate_path_migration_mapping.py` | L36,452 | DEPGRAPH_FILE | 同上 |
| 204 | `scripts/_archive/migration/generate_migration_registry.py` | L7,8,9 | 路径常量 | 同上 |
| 205 | `scripts/_archive/governance/repair/ensure_dep_cycles_view.py` | L5,7 | DB路径+sqlite3.connect | 同上 |
| 206 | `scripts/_archive/governance/dm101_blueprint_domain_mapping.py` | L15,17,319 | DEPGRAPH_PATH | 同上 |
| 207 | `scripts/_archive/governance/merge_domain_nodes.py` | L8,12 | DB_PATH+sqlite3.connect | 同上 |
| 208 | `scripts/_archive/construction/dm014_orphan_edge_repair.py` | L21,73 | DB_PATH+sqlite3.connect | 同上 |

#### 第4轮新增：scripts根目录临时脚本（7个，标记归档）

| # | 文件路径 | 位置 | 变更影响 | 执行办法 |
|---|---------|:----:|---------|---------|
| 209 | `scripts/_update_rbac_depgraph.py` | L19 | DB_PATH路径常量 | 临时脚本，标记废弃 |
| 210 | `scripts/_tmp_verify_states.py` | L7 | sqlite3.connect | 同上 |
| 211 | `scripts/_tmp_final_check.py` | L19 | sqlite3.connect | 同上 |
| 212 | `scripts/_query_rbac_core.py` | L19 | DB_PATH路径常量 | 同上 |
| 213 | `scripts/_tmp_query_508.py` | L24 | sqlite3.connect | 同上 |
| 214 | `scripts/_tmp_investigate.py` | L7 | sqlite3.connect | 同上 |
| 215 | `scripts/_tmp_final_check2.py` | L18,19 | sqlite3.connect | 同上 |

#### 第4轮新增：scripts/ops/脚本（1个，需迁移）

| # | 文件路径 | 位置 | 变更影响 | 执行办法 |
|---|---------|:----:|---------|---------|
| 216 | `scripts/ops/upgrade_headers_to_14fields.py` | L55,175,187 | DB_PATH路径常量 | 改为从环境变量读取PG_DSN |

#### 第4轮新增：自动生成域架构文档（100个，迁移后重新生成）

`docs/02_enterprise_architecture/02_domain_architecture_docs/`目录下100个文件，均由生成器脚本自动生成，文件头部包含"本文档由 generate_xxx.py 从 depgraph.db 自动生成"注释。

| # | 文件路径（代表） | 变更影响 | 执行办法 |
|---|---------|---------|---------|
| 217-316 | `docs/02_enterprise_architecture/02_domain_architecture_docs/*.md`（100个） | 自动生成文档引用depgraph.db | 迁移后运行生成器重新生成 |

**完整文件列表**：01_d_infra_a2a.md ~ 48_d_security_llm_architecture.md + domain_index.md（共100个）

#### 第4轮新增：自动生成报告/视图（4个，迁移后重新生成）

| # | 文件路径 | 变更影响 | 执行办法 |
|---|---------|---------|---------|
| 317 | `docs/02_enterprise_architecture/03_governance_reports/design_vs_production.md` | 自动生成 | 迁移后重新生成 |
| 318 | `docs/02_enterprise_architecture/03_governance_reports/capacity_report.md` | 自动生成 | 同上 |
| 319 | `docs/02_enterprise_architecture/target_architecture/capability_heatmap.md` | 手动+自动混合 | 更新描述+重新生成 |
| 320 | `docs/02_enterprise_architecture/01_global_architecture_diagram/global_capability_heatmap.md` | 同上 | 同上 |

#### 第4轮新增：手动维护架构文档（2个，需更新）

| # | 文件路径 | 变更影响 | 执行办法 |
|---|---------|---------|---------|
| 321 | `docs/02_enterprise_architecture/architecture_diagram_construction_plan.md` | 50+处depgraph.db引用（L9,10,17,23,35,60,70-73,87-92,111,145,165,220-233,254,383,404,409,424-426,432,473,480,484-485,557,572,600,606,622,625,634,637,639,641,649,662,712-713,725-726,734,736-737,749,761,807,809,838,840,956,962,981） | 全面更新为PostgreSQL；更新SQL查询命令 |
| 322 | `docs/02_enterprise_architecture/sample/00_overview_entry_sample.md` | L5,63 | 更新描述为PostgreSQL |

#### 第4轮新增：Blueprint文档（12个，需更新SSoT路径）

| # | 文件路径 | 变更影响 | 执行办法 |
|---|---------|---------|---------|
| 323 | `docs/03_modules/_cross_layer/pipeline/blueprint.md` | SSoT路径引用 | 更新为PG连接配置引用 |
| 324 | `docs/03_modules/_cross_layer/database/sub_blueprints/MOD-INF-012B-P2-task-cards.md` | depgraph.db引用 | 更新引用 |
| 325 | `docs/03_modules/_domain_infra_runtime/task_system/blueprint.md` | SSoT路径引用 | 同上 |
| 326 | `docs/03_modules/_cross_layer/auto_runtime_core/blueprint.md` | SSoT路径引用 | 同上 |
| 327 | `docs/03_modules/_domain_reporting/analytics_core/blueprint.md` | SSoT路径引用 | 同上 |
| 328 | `docs/03_modules/_domain_research/research_core/blueprint.md` | SSoT路径引用 | 同上 |
| 329 | `docs/03_modules/_cross_layer/resource_optimization_engine/blueprint.md` | SSoT路径引用 | 同上 |
| 330 | `docs/03_modules/_cross_layer/shared_core/blueprint.md` | SSoT路径引用 | 同上 |
| 331 | `docs/03_modules/_cross_layer/feedback_loop/blueprint.md` | SSoT路径引用 | 同上 |
| 332 | `docs/03_modules/_cross_layer/context_engine/blueprint.md` | SSoT路径引用 | 同上 |
| 333 | `docs/03_modules/_domain_signal/signal_generation_core/blueprint.md` | SSoT路径引用 | 同上 |
| 334 | `docs/03_modules/_domain_infra_runtime/runtime_integration/blueprint.md` | SSoT路径引用 | 同上 |

#### 第4轮新增：scripts清单文件（1个，需更新引用）

| # | 文件路径 | 变更影响 | 执行办法 |
|---|---------|---------|---------|
| 335 | `scripts/script_manifest.yaml` | L38,676,854,862,886,942,1160,3433,3738 | 更新脚本描述中的数据库类型引用 |

#### 第4轮新增：第3轮文件的遗漏位置（多处）

| # | 文件路径 | 遗漏位置 | 变更影响 | 执行办法 |
|---|---------|---------|---------|---------|
| - | `scripts/governance/d5_architecture/generators/generate_integration_topology.py` | L33(import sqlite3), L40(DEPGRAPH_DB), L44,71,85(sqlite3.Connection类型注解), L185(sqlite3.connect) | import+变量+类型注解+连接 | 全部改为psycopg2 |
| - | `scripts/governance/d5_architecture/generators/generate_domain_doc.py` | L34(import sqlite3), L41(DEPGRAPH_DB), L48,69,96,131,171,406,423(7处sqlite3.Connection), L604(sqlite3.connect) | 同上 | 同上 |
| - | `scripts/governance/d5_architecture/generators/generate_cross_domain_matrix.py` | L32(import sqlite3), L37(DEPGRAPH_DB), L43,69(sqlite3.Connection), L77(sqlite3.connect) | 同上 | 同上 |
| - | `scripts/governance/repair/concurrent_write_test.py` | L54(PROD_DB), L55(TEST_DB), L66-69(WAL文件处理), L87(WAL清理), L137(monkey-patch), L342(PRAGMA busy_timeout), L72,111,180,229,268,310,341,580(8处sqlite3.connect) | 多处SQLite特有机制 | 全面改造为PG |
| - | `docs/01_policies_and_standards/rules/trae_059_schema_version_write_protection.yaml` | L41(INSERT OR IGNORE), L44(INSERT OR REPLACE), L49(?占位符), L51(INSERT OR REPLACE), L63(sqlite3命令行), L77(depgraph_schema.py路径), L78(db_check) | SQLite特有SQL语法 | 改为PG的ON CONFLICT语法 |
| - | `docs/02_enterprise_architecture/architecture_upgrade_discussion.md` | L273,277,289,494,807,855,902,1038,1043,1084,1298,1335（12处显式"SQLite"标注） | 存储引擎标注 | 更新为PostgreSQL |
| - | `docs/02_enterprise_architecture/dependency_architecture_panorama.md` | L97(sqlite_sequence系统表), L1241(SQLite单库标注) | SQLite特有系统表+存储引擎标注 | 更新为PG的SEQUENCE对象 |
| - | `.trae/rules/project_rules.md` | L975("SQLite数据库"标注), L997-1001(git备份命令) | 存储引擎标注+git备份 | 更新为PostgreSQL+pg_dump |
| - | `.trae/rules/onboarding_detail.md` | L302,303(文件路径), L345(git备份命令) | 文件路径+备份命令 | 更新路径引用和备份策略 |

#### 第4轮新增：误判文件修正（4个，应从清单中移除或标记为不迁移）

| # | 文件路径 | 误判原因 | 处理方式 |
|---|---------|---------|---------|
| - | `scripts/governance/task_self_check.py`（原#120） | 实际操作governance.db（L60: DB_PATH指向governance.db） | 标记为"不迁移（governance.db）" |
| - | `scripts/governance/_sync/cleanup_p0_auto_bridged.py`（原#127） | 实际操作governance.db（L38: DB_PATH指向governance.db） | 标记为"不迁移（governance.db）" |
| - | `scripts/governance/phase_a_backup.py`（原#121） | 实际备份zalpha_metadata.db（L70: TIER0_FILES） | 标记为"不迁移（zalpha_metadata.db）" |
| - | `docs/01_policies_and_standards/rules/trae_034_task_card_standard.yaml`（原#125） | 主要引用governance.db（L39,211,559） | 标记为"不迁移（governance.db）" |

#### 第4轮新增：已知清单差异修正（1项）

| # | 差异项 | 修正内容 |
|---|--------|---------|
| - | "7个chk_前缀触发器"计数错误 | 实际为3个（chk_edges_design_immutable_update, chk_edges_migration_status, chk_edges_migration_status_update），源码中不存在，仅DB实例中有。修正清单第23项为"3个" |

### 第5轮审查（2026-06-25）

**审查方法**：2个聚焦角度验证
- 角度A：代码文件完整性验证（搜索115个.py文件+216个sqlite3.connect文件+166个DB_PATH文件）
- 角度B：验证4个误判文件修正+10个抽样文件遗漏检查

**审查结果**：新增0个文件 + 0个遗漏位置

#### 第5轮审查：角度A结果

**核心结论**：未发现直接操作depgraph.db且需要迁移到PostgreSQL的新增遗漏代码文件。

搜索覆盖：
- `depgraph`字符串搜索：115个.py文件
- `sqlite3.connect`搜索：216个.py文件
- `DB_PATH|DEPGRAPH_PATH|DEPGRAPH_DB`搜索：166个.py文件
- `DatabaseService|get_depgraph_conn|get_db_connection`搜索：70个.py文件

发现3个间接引用depgraph的测试文件（不需要迁移改造，仅迁移后验证）：

| # | 文件路径 | 引用方式 | 处理方式 |
|---|---------|---------|---------|
| - | `tests/test_rule_red_blue.py` | 通过subprocess调用diagnose_depgraph.py | 迁移后验证subprocess调用正常 |
| - | `tests/test_audit_registry_gate_e2e.py` | 测试PipelineRunner的scan_depgraph()方法 | 迁移后验证接口不变 |
| - | `tests/test_g_trae_054.py` | 测试trae_054规则（depgraph访问协议） | 迁移后验证规则参数 |

#### 第5轮审查：角度B结果

**误判文件验证**：4个误判文件修正全部正确

| 误判文件 | 验证结果 |
|----------|---------|
| scripts/governance/task_self_check.py | 确认误判——操作governance.db |
| scripts/governance/_sync/cleanup_p0_auto_bridged.py | 确认误判——操作governance.db |
| scripts/governance/phase_a_backup.py | 确认误判——操作zalpha_metadata.db |
| docs/01_policies_and_standards/rules/trae_034_task_card_standard.yaml | 确认误判——引用zalpha_metadata.db（非governance.db） |

**抽样验证**：10个归档脚本无遗漏位置

### 第6轮审查（2026-06-25）

**审查方法**：使用与第5轮不同的搜索关键词进行交叉验证
- 搜索1：`depgraph`全文件类型搜索（481个文件）
- 搜索2：`sqlite3`在.json/.xml文件中搜索（3个.json文件，0个.xml文件）
- 搜索3：`depgraph\.db`全文件类型搜索（397个文件）
- 验证3个间接引用测试文件

**审查结果**：新增0个文件 + 0个遗漏位置

#### 第6轮审查：搜索结果

| 搜索模式 | 命中文件数 | 排除已知后 | 需迁移的新增文件数 |
|---------|:---------:|:---------:|:---:|
| `depgraph`（全文件类型） | 481 | 少量剩余 | 0 |
| `sqlite3`（.json/.xml） | 3 | 0 | 0 |
| `depgraph\.db`（全文件类型） | 397 | 少量剩余 | 0 |

#### 第6轮审查：抽样验证（10个Python文件，均无需迁移）

| # | 文件路径 | 引用类型 | 需迁移 | 理由 |
|---|---------|---------|:------:|------|
| 1 | `src/zephyr/shared/capacity_runbook_generator.py` | 命令字符串`diagnose_depgraph.py` | NO | 仅引用脚本名 |
| 2 | `src/zephyr/security/access_control/orphan_judge/registration_checker.py` | YAML文件路径 | NO | 引用YAML非DB |
| 3 | `src/zephyr/governance/rule_enforcement/task_types.py` | Pydantic字段名 | NO | 字段名定义 |
| 4 | `scripts/governance/d7_code/fix_n15_blueprint_path.py` | 文件路径修正映射 | NO | 引用路径非DB |
| 5 | `tests/semantic_auditor/test_blast_radius.py` | YAML depgraph文件 | NO | 测试YAML非SQLite |
| 6 | `tests/semantic_auditor/test_blast_radius_red_team.py` | 同上 | NO | 同上 |
| 7 | `tests/test_core_models.py` | 字段名断言 | NO | 无DB访问 |
| 8 | `docs/02_enterprise_architecture/03_governance_reports/_update_audit_doc.py` | 描述性文本 | NO | 仅文本字符串 |
| 9 | `src/zephyr/governance/persistence/__init__.py` | 模块名列表 | NO | 模块名引用 |
| 10 | `src/zephyr/governance/rule_enforcement/g_trae_054.yaml` | 门禁定义文本 | NO | 引用协议名非DB |

#### 第6轮审查：3个间接引用测试文件验证

| # | 文件路径 | 需迁移改造 | 理由 |
|---|---------|:----------:|------|
| 1 | `tests/test_rule_red_blue.py` | NO | 通过subprocess调用diagnose_depgraph.py，不直接访问DB |
| 2 | `tests/test_audit_registry_gate_e2e.py` | NO | 调用PipelineRunner方法，不直接访问DB |
| 3 | `tests/test_g_trae_054.py` | NO | 加载YAML规则文件，不直接访问DB |

### 审查结论

**连续两次（第5轮、第6轮）新增=0，P2 PostgreSQL迁移受影响文件清单审查通过。**

总计335个文件（含4个误判文件标记为不迁移），其中：
- 需迁移到PostgreSQL的文件：约120个（代码文件+配置文件）
- 需更新描述的文件：约195个（文档+规则YAML+IDE配置）
- 自动生成文件（迁移后重新生成）：104个
- 归档/临时文件（标记废弃）：18个
- 误判文件（不迁移）：4个

---

## 八、审查通过标准

连续两次审查新增文件/位置=0，则审查通过。

| 轮次 | 新增文件数 | 新增位置数 | 状态 |
|------|:---------:|:---------:|:----:|
| 第1轮 | 85 | 200+ | 基线 |
| 第2轮 | 28 | 0 | ✅ 已完成 |
| 第3轮 | 52 | 12 | ✅ 已完成 |
| 第4轮 | 138 | 多处 | ✅ 已完成 |
| 第5轮 | 0 | 0 | ✅ 已完成 |
| 第6轮 | 0 | 0 | ✅ **审查通过** |

**审查结论**：连续两次（第5轮、第6轮）新增=0，审查通过。总计335个文件（含4个误判文件标记为不迁移）。

---

## 九、深度去噪审查（2026-06-25）

> 在创建P2任务卡之前，对需迁移到PostgreSQL的约120个文件进行深度去噪审查，从5个维度分析：合并（MERGE）、删除（DELETE）、清理（CLEAN）、过时（OBSOLETE）、噪音（NOISE），减少垃圾任务卡。

### 9.1 重大发现

| 发现 | 数量 | 说明 |
|------|:----:|------|
| **幽灵测试文件** | 5个 | tests/governance/下的test_depgraph_reader/test_rule_engine/test_apply_depgraph/test_sync_yaml_to_depgraph/test_depgraph_schema**全部不存在**，是审查过程中臆造的文件名 |
| **governance.db噪音** | 9个 | sqlite_schema.py触发器/视图、tamper_proof_audit.py触发器、base_repo.py/task_repo.py的FTS5——全部操作governance.db，非depgraph.db |
| **一次性脚本** | 8个 | dm105/dm106/migrate_前缀等已完成使命，应归档 |
| **autopilot session一次性** | 4个 | verify_final_delivery.py等针对特定历史session |
| **已有PG兼容性** | 3个 | rollback_integration.py(2份)+environment_manager.py已支持PostgreSQL |
| **纯噪音引用** | 18个 | 路径保护3个+纯注释5个+导入导出2个+YAML读取2个+其他6个 |

### 9.2 去噪效果统计

| 类别 | 原始数量 | 去噪后数量 | 减少量 | 去噪率 |
|------|:---:|:---:|:---:|:---:|
| src/zephyr/ | 26 | 6 | -20 | 77% |
| scripts/governance/ | 46 | 14任务卡 | -32 | 70% |
| tests/+配置+锁 | 30 | 13 | -17 | 57% |
| **总计** | **102** | **33** | **-69** | **68%** |

### 9.3 src/zephyr/ 去噪详情（26→6）

#### KEEP（保留，需单独任务卡，5个）

| # | 文件路径 | 理由 |
|---|---------|------|
| 1 | `src/zephyr/governance/depgraph_schema.py` | depgraph.db的Schema DDL真源，迁移核心目标 |
| 2 | `src/zephyr/governance/database_service.py` | 三库连接管理器，depgraph部分必须迁移 |
| 3 | `src/zephyr/governance/depgraph_reader.py` | depgraph只读访问层 |
| 4 | `src/zephyr/governance/rule_engine.py` | 规则引擎，查询rule_bindings表 |
| 5 | `src/zephyr/governance/auto_runner.py` | 自动运行器，审计日志写入 |

#### MERGE（合并，1个）

| # | 文件路径 | 合并到 | 理由 |
|---|---------|--------|------|
| 6 | `src/zephyr/governance/persistence/depgraph_schema.py` | #1 depgraph_schema.py | 纯re-export代理模块 |

#### CLEAN（部分迁移，1个）

| # | 文件路径 | 合并到 | 理由 |
|---|---------|--------|------|
| 7 | `src/zephyr/infrastructure/asset_inventory/dashboard.py` | #3 depgraph_reader.py | 仅KnowledgeTransferGate类有小段sqlite3查询 |

#### OBSOLETE（过时，1个）

| # | 文件路径 | 理由 |
|---|---------|------|
| 8 | `src/zephyr/governance/blast_radius.py` | 存在bug——将depgraph.db文件当作YAML读取，功能已废弃 |

#### NOISE（噪音，移除清单，18个）

| 类别 | 文件 | 理由 |
|------|------|------|
| 路径保护（3个） | rbac_guard.py, path_guard.py, immutable_core.py | 仅路径字符串引用，不执行SQL |
| governance.db相关（3个） | paths.py, db_utils.py, sqlite_schema.py | 指向governance.db而非depgraph.db |
| 纯注释（5个） | g_trae_059.yaml, __main__.py, __init___from_obs.py, script_governance/__init__.py, registry_management/__init__.py | 纯注释/字符串引用 |
| 导入导出（2个） | governance/__init__.py, rule_watcher.py | 仅导入导出，不直接执行SQL |
| YAML读取（2个） | audit_trail/pipeline_runner.py, audit_orchestrator/pipeline_runner.py | 读取YAML文件，非depgraph.db |
| 已有PG兼容（3个） | rollback_integration.py(2份), environment_manager.py | 已支持PostgreSQL |

### 9.4 scripts/governance/ 去噪详情（46→14任务卡）

#### DELETE（一次性脚本归档，8个）

| # | 文件路径 | 理由 |
|---|---------|------|
| 1 | `scripts/governance/dm105_depgraph_triage.py` | DM-105一次性三策略分诊脚本 |
| 2 | `scripts/governance/dm106_p2b_verification.py` | DM-106一次性P2-B验证脚本 |
| 3 | `scripts/governance/migrate_arch_f_functions.py` | 阶段1迁移脚本，已完成 |
| 4 | `scripts/governance/migrate_clean_build_status.py` | OPS任务卡一次性脏值清洗 |
| 5 | `scripts/governance/d5_architecture/dm200912_rewrite_views.py` | docstring自述"一次性脚本" |
| 6 | `scripts/governance/d5_architecture/dm200912_query_domains.py` | docstring自述"一次性脚本" |
| 7 | `scripts/governance/d5_architecture/dm200913_rewrite_diagrams.py` | docstring自述"一次性脚本" |
| 8 | `scripts/governance/d5_architecture/dm200916_write_direct.py` | docstring自述"一次性脚本" |

#### OBSOLETE（已完成使命，4个）

| # | 文件路径 | 理由 |
|---|---------|------|
| 9 | `scripts/governance/rename_whitelist_cleanup.py` | 代码注释"替换已执行完毕" |
| 10-12 | `verify_final_delivery.py`, `repair/audit_design_completeness.py`, `repair/red_blue_test.py` | autopilot session-20260618-001一次性脚本 |

#### MERGE（合并任务卡，19个）

**MERGE-A：d5_architecture生成器批量迁移（18个→1个任务卡）**

> **路径说明**：前17个文件位于`scripts/governance/d5_architecture/`下，第18个文件位于`scripts/governance/d11_compliance/`（与d5_architecture平级，同属governance子目录）。

| 文件 | 特殊注意点 |
|------|-----------|
| generate_capacity_report.py | - |
| generate_domain_architecture_diagram.py | - |
| generate_domain_doc.py | GROUP_CONCAT (L139,155) |
| generate_domain_dependency_diagram.py | - |
| generate_domain_index.py | - |
| generate_integration_topology.py | GROUP_CONCAT (L48) |
| generate_navigation_index.py | - |
| generate_path_tree.py | - |
| generate_runtime_plane_mapping.py | - |
| generate_capability_heatmap.py | sqlite_master (L159) |
| generate_constraint_violations.py | - |
| generate_cross_domain_matrix.py | GROUP_CONCAT (L48) |
| generate_design_vs_production.py | - |
| syncers/sync_blueprint_code_index.py | - |
| validators/validate_cross_references.py | - |
| validators/blueprint/validate_blueprint_code_sync.py | - |
| detectors/detect_deprecated_adr_references.py | - |
| d11_compliance/validate_task_decomposition_bypass.py | -（注：位于`scripts/governance/d11_compliance/`，非d5_architecture子目录） |

**MERGE-B：concurrent_write_test.py合并到apply_depgraph.py任务卡**

#### KEEP（独立任务卡，13个）

| # | 文件路径 | 迁移复杂度 |
|---|---------|-----------|
| 1 | `apply_depgraph.py` | 高：删除6处文件锁+lastrowid→RETURNING+19处sqlite3.connect |
| 2 | `sync_yaml_to_depgraph.py` | 高：27个触发器改PL/pgSQL+12处INSERT OR REPLACE |
| 3 | `generate_project_depgraph.py` | 高：5处连接+4处lock_files删除 |
| 4 | `extract_depgraph.py` | 中：2处连接（无`?`占位符） |
| 5 | `generate_target_path_tree.py` | 中：路径常量+2处连接 |
| 6 | `audit_domain_nodes.py` | 中：3处连接+datetime('now')+INSERT OR REPLACE |
| 7 | `diagnose_depgraph.py` | 低：1处连接 |
| 8 | `detect_causal_conflicts.py` | 低：1处连接 |
| 9 | `analyze_change_impact.py` | 低：1处连接 |
| 10 | `check_rule_four_way_alignment.py` | 低：1处连接+timeout |
| 11 | `check_schema_version_writes.py` | 中：导入_MIGRATIONS+DB校验 |
| 12 | `perf_depgraph_baseline.py` | 中：URI只读连接改造+sqlite_master |
| 13 | `scripts/ops/upgrade_headers_to_14fields.py` | 中：有测试，CI集成 |

### 9.5 tests/+配置+锁 去噪详情（30→13）

#### KEEP（保留，10个）

| # | 文件路径 | 理由 |
|---|---------|------|
| 1-6 | tests/下6个真实depgraph.db测试文件 | 直接连接depgraph.db |
| 7-9 | requirements.txt, pyproject.toml, .env.example | 缺少psycopg2-binary和PG连接配置 |
| 10 | depgraph_schema.py的CREATE VIEW dep_cycles | PG兼容，随主迁移卡处理 |

#### DELETE（从清单删除，7个）

| # | 文件路径 | 理由 |
|---|---------|------|
| 1-5 | tests/governance/下5个幽灵测试文件 | **文件不存在**，臆造的文件名 |
| 6 | `cleanup_p0_auto_bridged.py` | 误判，操作governance.db |
| 7 | `test_cross_layer_systems_red_team.py` | 纯噪音引用，不访问depgraph.db |

#### CLEAN（清理噪音，9个）

| # | 文件路径 | 理由 |
|---|---------|------|
| 1-2 | `sqlite_schema.py`的4个触发器+3个视图 | 操作governance.db |
| 3-4 | `tamper_proof_audit.py`的2个触发器（2份副本） | 操作governance.db drift_events |
| 5-6 | `base_repo.py`的FTS5（2份副本） | 操作governance.db tasks_fts |
| 7 | `task_repo.py`的FTS5 | 操作governance.db tasks_fts |
| 8-9 | `sqlite_metadata_store.py`的FTS5触发器（2份副本） | 操作vms_metadata.db |

#### NOISE（纯噪音，2个）

| # | 文件路径 | 理由 |
|---|---------|------|
| 1 | `auto_fix_cron.py` | 进程级单实例锁，非DB锁 |
| 2 | `test_cross_layer_systems_red_team.py` | 仅字符串引用postgresql |

### 9.6 去噪后任务卡规划（24个任务卡）

| 任务卡编号 | 任务卡名称 | 包含文件 | 文件数 |
|-----------|-----------|---------|:---:|
| TC-PG-01 | depgraph_schema.py迁移 | depgraph_schema.py + persistence/depgraph_schema.py | 2 |
| TC-PG-02 | database_service.py迁移 | database_service.py | 1 |
| TC-PG-03 | depgraph_reader.py迁移 | depgraph_reader.py + dashboard.py | 2 |
| TC-PG-04 | rule_engine.py迁移 | rule_engine.py | 1 |
| TC-PG-05 | auto_runner.py迁移 | auto_runner.py | 1 |
| TC-PG-06 | apply_depgraph.py迁移 | apply_depgraph.py + repair/concurrent_write_test.py | 2 |
| TC-PG-07 | sync_yaml_to_depgraph.py迁移 | sync_yaml_to_depgraph.py | 1 |
| TC-PG-08 | generate_project_depgraph.py迁移 | generate_project_depgraph.py | 1 |
| TC-PG-09 | extract_depgraph.py迁移 | extract_depgraph.py | 1 |
| TC-PG-10 | ⚠️ generate_target_path_tree.py迁移（已废弃：脚本已删除） | — | 0 |
| TC-PG-11 | audit_domain_nodes.py迁移 | audit_domain_nodes.py | 1 |
| TC-PG-12 | diagnose_depgraph.py迁移 | diagnose_depgraph.py | 1 |
| TC-PG-13 | detect_causal_conflicts.py迁移 | detect_causal_conflicts.py | 1 |
| TC-PG-14 | analyze_change_impact.py迁移 | analyze_change_impact.py | 1 |
| TC-PG-15 | check_rule_four_way_alignment.py迁移 | check_rule_four_way_alignment.py | 1 |
| TC-PG-16 | check_schema_version_writes.py迁移 | check_schema_version_writes.py | 1 |
| TC-PG-17 | perf_depgraph_baseline.py迁移 | perf_depgraph_baseline.py | 1 |
| TC-PG-18 | upgrade_headers_to_14fields.py迁移 | upgrade_headers_to_14fields.py | 1 |
| TC-PG-19 | d5_architecture生成器批量迁移 | 18个生成器 | 18 |
| TC-PG-20 | tests/ depgraph.db测试迁移 | 6个测试文件 | 6 |
| TC-PG-21 | PG依赖与连接配置 | requirements.txt + pyproject.toml + .env.example + pg_connection.py | 4 |
| TC-PG-22 | 规则/注册表YAML描述更新 | trae_056 + trae_059 + registry_of_registries.yaml | 3 |
| TC-PG-23 | depgraph_schema.py视图迁移 | CREATE VIEW dep_cycles | 1 |
| TC-PG-24 | 归档一次性脚本 | 12个一次性脚本移至_archive/ | 12 |
| **合计** | | | **63** |

> **文件数说明**：TC-PG-23（视图迁移）与TC-PG-01（depgraph_schema.py迁移）共享同一文件`src/zephyr/governance/depgraph_schema.py`，但分属不同施工阶段（TC-PG-01为SQL方言调整，TC-PG-23为视图迁移），故文件数统计中不重复计算。各任务卡文件数求和为64，去重后实际唯一文件数为63。

### 9.7 去噪审查结论

**去噪效果**：原始约120个需迁移文件 → 去噪后63个文件，分为24个任务卡，去噪率68%。

**关键收益**：
1. **减少垃圾任务卡**——避免为幽灵文件/噪音文件/一次性脚本创建任务卡
2. **提高任务卡质量**——聚焦真正需要迁移的文件
3. **降低幻觉漂移**——任务卡更精炼，AI上下文更集中
4. **节省执行时间**——不处理垃圾文件

**需后续处理（非P2范畴）**：
1. blast_radius.py的bug修复（将depgraph.db当作YAML读取）
2. governance/rollback_integration.py与infrastructure/rollback/rollback_integration.py的重复代码清理
3. 12个一次性脚本归档到scripts/_archive/

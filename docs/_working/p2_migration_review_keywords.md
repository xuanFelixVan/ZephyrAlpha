---
doc_type: checklist
status: active
title: "P2迁移审查——19个AI并发分工与关键词手册"
module_id: "MOD-DB_DEPGRAPH_PG"
blueprint_id: "SH-DB-001"
version: "1.0.0"
created: "2026-06-28"
updated: "2026-06-28"
ttl: task_bound
completes_when: "19个AI全部完成各自分区审查，汇总报告归档"
---

# P2迁移审查——19个AI并发分工与关键词手册

> 本文件是 19 个并发 AI 的施工手册。每个 AI 只负责一个分区，按本文件定义的关键词和判定标准审查，输出统一格式报告。
> 配套清单：[p2_migration_review_checklist.md](p2_migration_review_checklist.md)

---

## 一、19 个 AI 分工表

| AI编号 | 负责范围 | 主要目录/文件 |
|--------|---------|--------------|
| AI-01 | src/zephyr/governance/ 数据库核心 | `database_service.py`, `depgraph_schema.py`, `pg_conn_wrapper.py` |
| AI-02 | src/zephyr/governance/ 治理其他 | `git_commit_gateway.py`, `reconciliation_registry.py`, `task_repo.py`, `manifest.py` 等 |
| AI-03 | src/zephyr/infrastructure/ | `asset_inventory/`, `infra_runtime/` 等 |
| AI-04 | src/zephyr/ 其他所有子目录 | `trading/`, `security/`, `shared/`, `autonomy_core/`, `integration/` 等 |
| AI-05 | scripts/governance/ 核心脚本 | `apply_depgraph.py`, `generate_project_depgraph.py` |
| AI-06 | scripts/governance/d3_metadata/ | `check_frontmatter_metadata.py`, `check_naming_convention.py` 等 |
| AI-07 | scripts/governance/d7_code/ | `detect_direct_llm_calls.py`, 代码检查脚本 |
| AI-08 | scripts/governance/ 其他子目录 | 生成器、审计脚本等 |
| AI-09 | scripts/ 非governance目录 | `scripts/database/`, `scripts/sub/`, 根级脚本 |
| AI-10 | tests/ 数据库相关测试 | `test_depgraph_*`, `test_database_*`, `test_db_auto_ops*` |
| AI-11 | tests/ 其他测试文件 | 非数据库测试文件 |
| AI-12 | docs/01_policies_and_standards/rules/ | `trae_054*.yaml`, 其他规则文件 |
| AI-13 | docs/02_enterprise_architecture/ | `dependency_architecture_panorama.md` 等 |
| AI-14 | docs/03_modules/_cross_layer/database/ | `blueprint.md`, 方案文档, `index.md` |
| AI-15 | docs/ 其他目录 | `04_architecture_principles/`, `08_knowledge/`, `_working/`, `_registry/` |
| AI-16 | architecture_model/ | `layers/b_db.yaml`, 其他蓝图YAML |
| AI-17 | config/ + 根目录配置文件 | `.env*`, `.gitignore`, `.pre-commit-config.yaml`, `requirements.txt` |
| AI-18 | AGENTS.md + 根目录.md文件 | `AGENTS.md`, `README.md` 等 |
| AI-19 | PG数据库内容验证 | PostgreSQL `depgraph` 数据库 25 表 schema+数据+索引+约束 |

---

## 二、通用关键词库

### A. SQLite 残留关键词（违规——发现即报告）

> 以下关键词若出现在 **depgraph 上下文** 中即为违规。governance.db / market.duckdb 上下文豁免。

| # | 关键词/模式 | 违规场景 | 正确替代 |
|---|-----------|---------|---------|
| A1 | `sqlite3.connect(` | 连接 depgraph.db | `get_db_connection()` |
| A2 | `import sqlite3` | 在 depgraph 操作文件中 | `import psycopg2` + `get_db_connection()` |
| A3 | `sqlite_master` | 查询 depgraph 表结构 | `information_schema.tables` |
| A4 | `AUTOINCREMENT` | depgraph 表定义 | `GENERATED ALWAYS AS IDENTITY` |
| A5 | `INSERT OR REPLACE` | depgraph 数据操作 | `INSERT ... ON CONFLICT DO UPDATE` |
| A6 | `GROUP_CONCAT` | depgraph 聚合查询 | `STRING_AGG` |
| A7 | `?` 占位符 | depgraph 参数化查询 | `%s` |
| A8 | `row[0]` / `row[1]` 数字索引 | 访问 depgraph 查询结果 | `row["col_name"]` |
| A9 | `conn.execute(...).fetchone()` | 在 psycopg2 connection 上 | `with conn.cursor() as cur: cur.execute(...); cur.fetchone()` |
| A10 | `sqlite3.Error` | depgraph 错误处理 | `psycopg2.Error` |
| A11 | `sqlite3.IntegrityError` | depgraph 错误处理 | `psycopg2.IntegrityError` |
| A12 | `"data/databases/depgraph.db"` | 路径硬编码 | `get_db_connection()` |
| A13 | `"data\\databases\\depgraph.db"` | 路径硬编码（Windows） | `get_db_connection()` |
| A14 | `PRAGMA journal_mode=WAL` | depgraph WAL设置 | （PG默认MVCC，移除） |
| A15 | `PRAGMA busy_timeout` | depgraph 超时设置 | `statement_timeout` |
| A16 | `sqlite3.Row` | depgraph 行工厂 | `RealDictCursor` |
| A17 | `last_insert_rowid()` | depgraph 获取自增ID | `RETURNING` 或 `currval()` |
| A18 | `sqlite_sequence` | depgraph 序列表 | `pg_sequences` 或 IDENTITY |

### B. PostgreSQL 正确性关键词（应存在——缺失即报告）

| # | 关键词 | 应出现位置 |
|---|--------|-----------|
| B1 | `psycopg2` | depgraph 连接文件 |
| B2 | `RealDictCursor` | depgraph 连接配置 |
| B3 | `get_db_connection` | depgraph 统一入口 |
| B4 | `%s` | depgraph 参数化查询 |
| B5 | `ON CONFLICT DO UPDATE` | depgraph upsert |
| B6 | `information_schema` | depgraph 表结构查询 |
| B7 | `STRING_AGG` | depgraph 聚合查询 |
| B8 | `GENERATED ALWAYS AS IDENTITY` | depgraph 自增主键 |
| B9 | `with conn.cursor() as cur` | depgraph 查询模式 |
| B10 | `row["col_name"]` 或 `row["col"]` | depgraph 结果访问 |
| B11 | `psycopg2.Error` | depgraph 错误处理 |
| B12 | `conn.rollback()` | depgraph 事务回滚 |
| B13 | `autocommit` | depgraph 连接参数 |
| B14 | `OVERRIDING SYSTEM VALUE` | depgraph 数据迁移（保留原主键） |

### C. module_id 关键词

| # | 关键词 | 判定 |
|---|--------|------|
| C1 | `MOD-INF-012B-P2` | ❌ 违规，应为 `MOD-DB_DEPGRAPH_PG` |
| C2 | `MOD-INF-012B-P3` | ❌ 违规，应为 `MOD-DB_DEPGRAPH_OPT` |
| C3 | `MOD-INF-012B` | ⚠️ 检查上下文（父级引用是否合理） |
| C4 | `MOD-DB_DEPGRAPH_PG` | ✅ 正确 |
| C5 | `MOD-DB_DEPGRAPH_OPT` | ✅ 正确 |

### D. 文档一致性关键词

| # | 关键词 | 检查要点 |
|---|--------|---------|
| D1 | `depgraph.db` | 检查上下文：是否仍描述为 SQLite？应说明已迁移PG |
| D2 | `SQLite` | 在 depgraph 上下文中应注明"已迁移到 PostgreSQL" |
| D3 | `PostgreSQL` / `PG` | 文档中应存在迁移说明 |
| D4 | `P2迁移已完成` | index.md 等状态文档应包含 |
| D5 | `psycopg2` | 技术文档应提及 |
| D6 | `get_db_connection()` | 开发文档应引导使用 |

### E. 配置关键词

| # | 关键词 | 检查要点 |
|---|--------|---------|
| E1 | `.env.postgres` | 应存在于 config/ 且被 .gitignore |
| E2 | `psycopg2-binary` | 应在 requirements.txt / pyproject.toml |
| E3 | `PGPASSWORD` | 不应硬编码在代码中 |
| E4 | `pg_dump` | 备份文档应提及 |

---

## 三、各 AI 详细审查指令

### AI-01：src/zephyr/governance/ 数据库核心

**负责文件**：
- `src/zephyr/governance/database_service.py`
- `src/zephyr/governance/depgraph_schema.py`
- `src/zephyr/governance/pg_conn_wrapper.py`

**重点检查**：
1. `get_db_connection()` 实现：autocommit 参数、RealDictCursor 配置、连接关闭
2. `DatabaseService.get_depgraph_conn()` 返回 psycopg2 connection
3. `DatabaseService.health_check()` depgraph 分支用 cursor 模式
4. `PgConnExecuteWrapper` 兼容 sqlite3 接口
5. 无 `sqlite3.connect` 连接 depgraph
6. 无 `conn.execute().fetchone()` 用于 psycopg2 connection
7. 错误处理用 `psycopg2.Error` 非 `sqlite3.Error`

**关键词**：A1-A18, B1-B14, C1-C5

---

### AI-02：src/zephyr/governance/ 治理其他

**负责文件**：
- `src/zephyr/governance/git_commit_gateway.py`
- `src/zephyr/governance/reconciliation_registry.py`
- `src/zephyr/governance/task_repo.py`
- `src/zephyr/governance/manifest.py`
- `src/zephyr/governance/` 其他 .py 文件

**重点检查**：
1. 这些文件若访问 depgraph，是否用 `get_db_connection()`
2. 无 sqlite3 直连 depgraph
3. reconciler 触发条件是否考虑 PG 迁移
4. `GitCommitGateway` 的 depgraph 相关注册逻辑

**关键词**：A1-A18, B1-B14

---

### AI-03：src/zephyr/infrastructure/

**负责目录**：`src/zephyr/infrastructure/**`

**重点检查**：
1. `asset_inventory/dashboard.py` 的 `KnowledgeTransferGate.generate_summary()` 已修复（用 `get_db_connection`）
2. 无其他文件用 sqlite3 连 depgraph
3. infrastructure 子模块访问 depgraph 的统一性

**关键词**：A1-A18, B1-B14

---

### AI-04：src/zephyr/ 其他所有子目录

**负责目录**：`src/zephyr/` 下除 governance/ 和 infrastructure/ 外的所有子目录
- `trading/`, `security/`, `shared/`, `autonomy_core/`, `integration/`, `infra_runtime/` 等

**重点检查**：
1. 这些子目录中若有访问 depgraph 的代码，是否用 `get_db_connection()`
2. 无 sqlite3 直连 depgraph
3. `shared/io/paths.py` 的 `REPO_ROOT` 正确性

**关键词**：A1-A18, B1-B14

---

### AI-05：scripts/governance/ 核心脚本

**负责文件**：
- `scripts/governance/apply_depgraph.py`
- `scripts/governance/generate_project_depgraph.py`
- `scripts/governance/` 根级其他核心 .py

**重点检查**：
1. `apply_depgraph.py` SQL 方言：`%s`、`ON CONFLICT DO UPDATE`、cursor 模式
2. `generate_project_depgraph.py` 帮助文本已 PG 化
3. 无 `?` 占位符、无 `INSERT OR REPLACE`、无 `sqlite_master`
4. 无 `sqlite3.connect` 连 depgraph

**关键词**：A1-A18, B1-B14

---

### AI-06：scripts/governance/d3_metadata/

**负责目录**：`scripts/governance/d3_metadata/**`

**重点检查**：
1. 元数据检查脚本若访问 depgraph，是否用 `get_db_connection()`
2. 无 sqlite3 直连 depgraph
3. `check_frontmatter_metadata.py`、`check_naming_convention.py` 的 depgraph 访问正确性

**关键词**：A1-A18, B1-B14

---

### AI-07：scripts/governance/d7_code/

**负责目录**：`scripts/governance/d7_code/**`

**重点检查**：
1. 代码检查脚本若访问 depgraph，是否用 `get_db_connection()`
2. `detect_direct_llm_calls.py` 等 AST 扫描脚本不涉及 depgraph（确认）
3. 无 sqlite3 直连 depgraph

**关键词**：A1-A18, B1-B14

---

### AI-08：scripts/governance/ 其他子目录

**负责目录**：`scripts/governance/` 下除 d3_metadata/ 和 d7_code/ 外的子目录
- 生成器脚本、审计脚本等

**重点检查**：
1. 17 个全景生成器是否统一从 PG depgraph 读取
2. 无生成器仍从 sqlite3 读 depgraph
3. 生成器输出文件名 snake_case
4. 无 `?` 占位符、无 sqlite3 方言

**关键词**：A1-A18, B1-B14

---

### AI-09：scripts/ 非governance目录

**负责目录**：`scripts/` 下除 `governance/` 外的所有子目录
- `scripts/database/`, `scripts/sub/`, 根级脚本

**重点检查**：
1. `scripts/database/` 下迁移工具、诊断脚本完整性
2. 无 sqlite3 直连 depgraph
3. 迁移工具可运行性

**关键词**：A1-A18, B1-B14

---

### AI-10：tests/ 数据库相关测试

**负责文件**：
- `tests/test_depgraph_schema.py`
- `tests/test_database_service.py`
- `tests/test_db_auto_ops.py`
- `tests/test_f18_redblue.py`
- `tests/test_verify_schema_health.py`
- `tests/test_audit_rename_completeness.py`
- 其他 `test_depgraph_*` / `test_database_*`

**重点检查**：
1. §12.4 的 14 个文件适配完整
2. 4 个 skip 文件 skip 原因合理且有 TODO
3. 10 个连接替换文件正确用 `get_db_connection()`
4. 无测试仍用 sqlite3 连 depgraph
5. 无测试用 `?` 占位符查 depgraph

**关键词**：A1-A18, B1-B14

---

### AI-11：tests/ 其他测试文件

**负责目录**：`tests/` 下非数据库相关测试

**重点检查**：
1. 这些测试是否误连 depgraph
2. 若有 depgraph 访问，是否用 `get_db_connection()`
3. mock 隔离的正确性

**关键词**：A1-A18, B1-B14

---

### AI-12：docs/01_policies_and_standards/rules/

**负责目录**：`docs/01_policies_and_standards/rules/**`

**重点检查**：
1. `trae_054_depgraph_access_protocol.yaml` v1.4.0，9 处更新无遗漏
2. 其他规则文件若提及 depgraph，是否说明已迁移 PG
3. 无规则文件仍描述 depgraph.db 为 SQLite（除非历史记录）
4. frontmatter `module_id` 合规

**关键词**：A1-A18, C1-C5, D1-D6

---

### AI-13：docs/02_enterprise_architecture/

**负责目录**：`docs/02_enterprise_architecture/**`

**重点检查**：
1. `dependency_architecture_panorama.md` 15 处 PG 描述无遗漏
2. 生成器输出的架构文档无 SQLite 残留描述
3. 无文档与实际实现矛盾

**关键词**：A1-A18, C1-C5, D1-D6

---

### AI-14：docs/03_modules/_cross_layer/database/

**负责目录**：`docs/03_modules/_cross_layer/database/**`

**重点检查**：
1. `blueprint.md` 状态 Active、progress completed、module_id=`MOD-DB_DEPGRAPH_PG`
2. 方案文档 §12.3 / §12.4 checkbox 全部 `[x]`
3. `index.md` 状态说明含 "P2迁移已完成 2026-06-27"
4. P3 方案文档 module_id=`MOD-DB_DEPGRAPH_OPT`
5. 无 `MOD-INF-012B-P2/P3` 残留

**关键词**：A1-A18, C1-C5, D1-D6

---

### AI-15：docs/ 其他目录

**负责目录**：
- `docs/04_architecture_principles_decisions/`
- `docs/08_knowledge/`
- `docs/_working/`
- `docs/_registry/`
- `docs/09_audit/`（若存在）

**重点检查**：
1. 文档若提及 depgraph，是否说明已迁移
2. frontmatter `module_id` 合规
3. 无过时描述

**关键词**：A1-A18, C1-C5, D1-D6

---

### AI-16：architecture_model/

**负责目录**：`architecture_model/**`

**重点检查**：
1. `layers/b_db.yaml` 包含 db-depgraph-pg 模块条目
2. 其他蓝图 YAML 若引用 depgraph，是否说明 PG
3. 无 `MOD-INF-012B-P2/P3` 残留

**关键词**：A1-A18, C1-C5, D1-D6

---

### AI-17：config/ + 根目录配置文件

**负责文件**：
- `config/.env.postgres`
- `config/` 其他配置
- `.gitignore`
- `.pre-commit-config.yaml`
- `requirements.txt` / `pyproject.toml`
- `setup.py` / `setup.cfg`（若存在）

**重点检查**：
1. `.env.postgres` 存在且配置正确（host/port/db/user）
2. `.gitignore` 含 `.env.postgres`
3. `requirements.txt` 含 `psycopg2-binary`
4. 无硬编码 PG 密码
5. `.pre-commit-config.yaml` 无 PG 不兼容钩子

**关键词**：E1-E4, A1-A18

---

### AI-18：AGENTS.md + 根目录.md文件

**负责文件**：
- `AGENTS.md`
- `README.md`（若存在）
- 根目录其他 .md

**重点检查**：
1. `AGENTS.md` 4 处 depgraph 指引适配 PG（第272-296行附近）
2. 无描述矛盾（仍说 depgraph.db 是 SQLite）
3. `get_db_connection()` 引导存在
4. 备份机制说明为 `pg_dump`

**关键词**：A1-A18, C1-C5, D1-D6

---

### AI-19：PG数据库内容验证

**负责对象**：PostgreSQL `depgraph` 数据库

**检查命令**（PowerShell）：
```powershell
$env:PGPASSWORD='zephyr_dev_2026'; $env:PAGER='';
& 'C:\Program Files\PostgreSQL\16\bin\psql.exe' -U zephyr -d depgraph -c "<SQL>"
```

**检查项**：
1. 25 张表全部存在：`SELECT count(*) FROM information_schema.tables WHERE table_schema='public';`
2. 各表行数：`SELECT relname, n_live_tup FROM pg_stat_user_tables ORDER BY relname;`
3. `_schema_version` 含 v18：`SELECT * FROM _schema_version ORDER BY version DESC LIMIT 5;`
4. nodes 表 IDENTITY 列：`SELECT column_name, column_default, is_identity FROM information_schema.columns WHERE table_name='nodes' AND column_name='id';`
5. 索引存在：`SELECT indexname FROM pg_indexes WHERE schemaname='public' ORDER BY tablename, indexname;`
6. 无孤儿临时表：`SELECT tablename FROM pg_tables WHERE schemaname='public' AND tablename LIKE 'tmp_%' OR tablename LIKE 'temp_%';`
7. 验证关键数据：`SELECT count(*) FROM nodes;`（应=6429）、`SELECT count(*) FROM edges;`（应=7094）、`SELECT count(*) FROM domains;`（应=53）

**输出**：表名、行数、schema 差异清单

---

## 四、统一输出格式

每个 AI 审查完成后，按以下格式输出报告（写入 `docs/_working/p2_review_reports/AI-XX_report.md`）：

```markdown
---
doc_type: audit_report
status: active
title: "AI-XX 审查报告——P2迁移第N轮"
module_id: "MOD-DB_DEPGRAPH_PG"
version: "1.0.0"
created: "2026-06-28"
ttl: task_bound
completes_when: "报告归档且问题修复或确认无问题"
---

# AI-XX 审查报告

## 元信息
- 审查轮次：第 N 轮
- 审查时间：2026-06-28 HH:MM
- 负责分区：xxx
- 审查文件数：XX

## 审查结果汇总
- 发现问题数：X
- 严重问题：X
- 一般问题：X
- 提示项：X

## 问题清单

### 问题 1
- **文件**：`path/to/file.py`
- **行号**：L123-L125
- **类别**：A1 (sqlite3.connect 连接 depgraph)
- **严重性**：严重/一般/提示
- **描述**：xxx
- **建议修复**：xxx

### 问题 2
...

## 确认无问题项
- 检查项 X：✅ 通过
- 检查项 Y：✅ 通过

## 结论
- [ ] 无问题，本分区审查通过
- [ ] 有问题，需修复后复审
```

---

## 五、审查流程

```
第一轮（19 AI 并发）
  ├─ AI-01 ~ AI-19 各自审查负责分区
  ├─ 各自输出报告到 docs/_working/p2_review_reports/
  └─ 汇总所有报告，按 13 项清单分类

修复阶段
  ├─ 按问题严重性排序
  ├─ 逐个修复
  └─ 记录修复内容

第二轮（19 AI 并发复审）
  ├─ 针对修复后的代码重新审查
  ├─ 各 AI 输出复审报告
  └─ 若连续两次问题数=0 → 打绿勾 ✅

循环直至 13 项全部 ✅
```

---

## 六、判定标准

| 类别 | 判定 |
|------|------|
| 严重 | 代码会导致运行时错误（如 psycopg2 connection 调 execute）|
| 一般 | 代码不报错但不符合迁移规范（如文档描述过时）|
| 提示 | 可优化项（如连接池策略）|

**通过标准**：严重=0 且 一般=0，提示项不计入阻断。

---

## 七、并发协调

- 19 个 AI 各自独立工作，互不干扰
- 报告写入独立文件，避免冲突
- 修复阶段由主 AI 统一执行（避免并发修改同一文件）
- 复审阶段再次 19 AI 并发

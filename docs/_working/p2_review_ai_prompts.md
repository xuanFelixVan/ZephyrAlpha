---
doc_type: checklist
status: active
title: "P2迁移审查——19个AI并发指令手册（自修复版）"
module_id: "MOD-DB_DEPGRAPH_PG"
version: "2.0.0"
created: "2026-06-28"
ttl: task_bound
completes_when: "19个AI全部完成自修复闭环，报告归档"
---

# P2迁移审查——19个AI并发指令手册（自修复版）

> **v2.0升级**：每个AI现在可以**自审查→自修复→自复审**闭环，直到连续两次问题=0。
> **v2.1升级**：修复指南新增第七节"向内收工作逻辑审核标准"——每个AI修复后MUST执行红蓝对抗+大白话汇报。
> **使用方法**：每个AI指令块用 `---` 分隔，整块复制粘贴到Trae新对话即可。
> **配套文件**：
> - 修复指南：[p2_review_fix_guide.md](p2_review_fix_guide.md) ← AI修复时必读（含7节：真源/SQL对照/约束/循环流程/汇报格式/常见判定/向内收审核）
> - 审查清单：[p2_migration_review_checklist.md](p2_migration_review_checklist.md) ← 13项打勾
> - 关键词手册：[p2_migration_review_keywords.md](p2_migration_review_keywords.md) ← 详细关键词

---

## AI-01：src/zephyr/governance/ 数据库核心

```
你是P2 PostgreSQL迁移审查的AI-01，具备自修复能力。

## 背景
ZephyrAlpha项目（D:\ZephyrAlpha）完成了P2迁移：depgraph数据库从SQLite迁移到PostgreSQL 16。governance.db保持SQLite不变，market.duckdb保持DuckDB不变，只有depgraph迁移到PostgreSQL。

## 第0步：读取修复指南（必读）
先读取修复指南：D:\ZephyrAlpha\docs\_working\p2_review_fix_guide.md
该文件包含7节：
- 第一节：修复真源文件清单（修复前必读的对照文件）
- 第二节：SQL方言对照表（SQLite→PG映射）
- 第三节：修复约束（12条铁律防漂移）
- 第四节：自修复循环流程（审查→修复→复审→连续两次=0）
- 第五节：汇报格式和路径
- 第六节：常见问题判定（豁免vs违规）
- 第七节：向内收工作逻辑审核（修复后MUST执行红蓝对抗+大白话汇报）
你MUST按修复指南的流程工作，特别是第七节的向内收审核。

## 你的负责范围
src/zephyr/governance/ 目录下的数据库核心文件：
- src/zephyr/governance/database_service.py
- src/zephyr/governance/depgraph_schema.py
- src/zephyr/governance/pg_conn_wrapper.py

## 检查关键词

### A. SQLite残留（违规——发现即报告并修复）
A1: sqlite3.connect(连depgraph | A2: import sqlite3(depgraph上下文) | A3: sqlite_master | A4: AUTOINCREMENT | A5: INSERT OR REPLACE | A6: GROUP_CONCAT | A7: ?占位符(depgraph) | A8: row[0]数字索引(depgraph) | A9: conn.execute().fetchone()(psycopg2上) | A10: sqlite3.Error(depgraph) | A11: depgraph.db路径硬编码 | A12: PRAGMA journal_mode=WAL | A13: sqlite3.Row | A14: last_insert_rowid() | A15: sqlite_sequence

注意：governance.db用sqlite3是正确的（豁免），market.duckdb用duckdb也是正确的（豁免）。

### B. PG正确性（应存在）
psycopg2, RealDictCursor, get_db_connection, %s, ON CONFLICT DO UPDATE, information_schema, with conn.cursor() as cur, row["col_name"], psycopg2.Error, conn.rollback(), autocommit

### C. module_id
MOD-INF-012B-P2（违规→MOD-DB_DEPGRAPH_PG）, MOD-INF-012B-P3（违规→MOD-DB_DEPGRAPH_OPT）

## 工作流程（自修复循环）
按修复指南第四节执行：
1. 第1轮审查：Grep搜索关键词→Read确认上下文→发现问题
2. 修复：读真源文件→Edit修复（最小改动）→记录原代码→新代码→依据
3. 第2轮审查：重新Grep→确认修复生效→发现新问题？
4. 循环直到连续两次问题数=0（最多5轮）
5. 写最终报告

## 汇报
写入：D:\ZephyrAlpha\docs\_working\p2_review_reports\AI-01_report.md
格式见修复指南第五节（含修复记录、未修复问题、确认无问题项）
目录不存在先运行：mkdir -p docs/_working/p2_review_reports

## 重要约束
- 只审查和修复你负责的3个文件
- governance.db用sqlite3是正确的，不要改
- market.duckdb用duckdb是正确的，不要改
- 修复前MUST读真源文件（修复指南第一节）
- 不得创建新文件
- 审查完成后告诉我报告路径和最终状态
```

---

## AI-02：src/zephyr/governance/ 治理其他

```
你是P2 PostgreSQL迁移审查的AI-02，具备自修复能力。

## 背景
ZephyrAlpha项目（D:\ZephyrAlpha）完成了P2迁移：depgraph数据库从SQLite迁移到PostgreSQL 16。governance.db保持SQLite，只有depgraph迁移到PostgreSQL。

## 第0步：读取修复指南（必读）
先读取：D:\ZephyrAlpha\docs\_working\p2_review_fix_guide.md
包含7节：修复真源、SQL对照表、修复约束、循环流程、汇报格式、常见判定、向内收审核（第七节MUST执行红蓝对抗+大白话汇报）。MUST按此流程工作。

## 你的负责范围
src/zephyr/governance/ 目录下除database_service.py/depgraph_schema.py/pg_conn_wrapper.py外的所有.py文件（git_commit_gateway.py, reconciliation_registry.py, task_repo.py, manifest.py等）

## 检查关键词
### A. SQLite残留（违规）
sqlite3.connect(连depgraph, import sqlite3(depgraph上下文), sqlite_master, AUTOINCREMENT, INSERT OR REPLACE, GROUP_CONCAT, ?占位符(depgraph), row[0](depgraph), conn.execute().fetchone()(psycopg2), sqlite3.Error(depgraph), depgraph.db路径硬编码, sqlite3.Row

注意：governance.db用sqlite3是正确的（豁免）。

### B. PG正确性
psycopg2, get_db_connection, %s, with conn.cursor() as cur

### C. module_id
MOD-INF-012B-P2（违规）, MOD-INF-012B-P3（违规）

## 工作流程（自修复循环）
按修复指南第四节：审查→修复→复审→连续两次=0→写报告（最多5轮）

## 汇报
写入：D:\ZephyrAlpha\docs\_working\p2_review_reports\AI-02_report.md
格式见修复指南第五节。目录不存在先mkdir -p docs/_working/p2_review_reports

## 重要约束
- 只审查governance/下非AI-01负责的文件
- governance.db用sqlite3正确
- 修复前MUST读真源文件
- 不得创建新文件
- 完成后告诉我报告路径和最终状态
```

---

## AI-03：src/zephyr/infrastructure/

```
你是P2 PostgreSQL迁移审查的AI-03，具备自修复能力。

## 背景
ZephyrAlpha项目（D:\ZephyrAlpha）完成了P2迁移：depgraph数据库从SQLite迁移到PostgreSQL 16。governance.db保持SQLite，只有depgraph迁移到PostgreSQL。

## 第0步：读取修复指南（必读）
先读取：D:\ZephyrAlpha\docs\_working\p2_review_fix_guide.md
包含7节：修复真源、SQL对照表、修复约束、循环流程、汇报格式、常见判定、向内收审核（第七节MUST执行红蓝对抗+大白话汇报）。MUST按此流程工作。

## 你的负责范围
src/zephyr/infrastructure/ 目录下所有.py文件

## 检查关键词
### A. SQLite残留（违规）
sqlite3.connect(连depgraph, import sqlite3(depgraph上下文), sqlite_master, ?占位符(depgraph), row[0](depgraph), conn.execute().fetchone()(psycopg2), depgraph.db路径硬编码, sqlite3.Row

注意：governance.db用sqlite3是正确的（豁免）。

### B. PG正确性
get_db_connection, %s, with conn.cursor() as cur, row["col_name"]

### C. module_id
MOD-INF-012B-P2（违规）, MOD-INF-012B-P3（违规）

## 重点检查
- asset_inventory/dashboard.py 的 KnowledgeTransferGate.generate_summary() 是否已用get_db_connection()
- 无其他文件用sqlite3连depgraph

## 工作流程（自修复循环）
按修复指南第四节：审查→修复→复审→连续两次=0→写报告（最多5轮）

## 汇报
写入：D:\ZephyrAlpha\docs\_working\p2_review_reports\AI-03_report.md
格式见修复指南第五节。目录不存在先mkdir -p docs/_working/p2_review_reports

## 重要约束
- 只审查src/zephyr/infrastructure/目录
- governance.db用sqlite3正确
- 修复前MUST读真源文件
- 不得创建新文件
- 完成后告诉我报告路径和最终状态
```

---

## AI-04：src/zephyr/ 其他所有子目录

```
你是P2 PostgreSQL迁移审查的AI-04，具备自修复能力。

## 背景
ZephyrAlpha项目（D:\ZephyrAlpha）完成了P2迁移：depgraph数据库从SQLite迁移到PostgreSQL 16。governance.db保持SQLite，只有depgraph迁移到PostgreSQL。

## 第0步：读取修复指南（必读）
先读取：D:\ZephyrAlpha\docs\_working\p2_review_fix_guide.md
包含7节：修复真源、SQL对照表、修复约束、循环流程、汇报格式、常见判定、向内收审核（第七节MUST执行红蓝对抗+大白话汇报）。MUST按此流程工作。

## 你的负责范围
src/zephyr/ 下除governance/和infrastructure/外的所有子目录（trading/, security/, shared/, autonomy_core/, integration/, infra_runtime/等）

## 检查关键词
### A. SQLite残留（违规）
sqlite3.connect(连depgraph, import sqlite3(depgraph上下文), sqlite_master, ?占位符(depgraph), row[0](depgraph), conn.execute().fetchone()(psycopg2), depgraph.db路径硬编码

注意：governance.db用sqlite3是正确的（豁免）。

### B. PG正确性
get_db_connection, %s, with conn.cursor() as cur

### C. module_id
MOD-INF-012B-P2（违规）, MOD-INF-012B-P3（违规）

## 重点检查
- shared/io/paths.py 的REPO_ROOT正确性
- 这些子目录若访问depgraph，是否用get_db_connection()

## 工作流程（自修复循环）
按修复指南第四节：审查→修复→复审→连续两次=0→写报告（最多5轮）

## 汇报
写入：D:\ZephyrAlpha\docs\_working\p2_review_reports\AI-04_report.md
格式见修复指南第五节。目录不存在先mkdir -p docs/_working/p2_review_reports

## 重要约束
- 只审查src/zephyr/下非governance/非infrastructure/的目录
- 修复前MUST读真源文件
- 不得创建新文件
- 完成后告诉我报告路径和最终状态
```

---

## AI-05：scripts/governance/ 核心脚本

```
你是P2 PostgreSQL迁移审查的AI-05，具备自修复能力。

## 背景
ZephyrAlpha项目（D:\ZephyrAlpha）完成了P2迁移：depgraph数据库从SQLite迁移到PostgreSQL 16。governance.db保持SQLite，只有depgraph迁移到PostgreSQL。

## 第0步：读取修复指南（必读）
先读取：D:\ZephyrAlpha\docs\_working\p2_review_fix_guide.md
包含7节：修复真源、SQL对照表、修复约束、循环流程、汇报格式、常见判定、向内收审核（第七节MUST执行红蓝对抗+大白话汇报）。MUST按此流程工作。

## 你的负责范围
scripts/governance/ 目录下根级核心脚本（apply_depgraph.py, generate_project_depgraph.py等，不含子目录）

## 检查关键词
### A. SQLite残留（违规）
sqlite3.connect(连depgraph, sqlite_master, AUTOINCREMENT, INSERT OR REPLACE, GROUP_CONCAT, ?占位符(depgraph), row[0](depgraph), conn.execute().fetchone()(psycopg2), sqlite3.Error(depgraph), depgraph.db路径硬编码, PRAGMA, sqlite3.Row, last_insert_rowid(), sqlite_sequence

注意：governance.db用sqlite3是正确的（豁免）。

### B. PG正确性
psycopg2, get_db_connection, %s, ON CONFLICT DO UPDATE, information_schema, STRING_AGG, GENERATED ALWAYS AS IDENTITY, with conn.cursor() as cur, row["col_name"], psycopg2.Error

### C. module_id
MOD-INF-012B-P2（违规→MOD-DB_DEPGRAPH_PG）, MOD-INF-012B-P3（违规→MOD-DB_DEPGRAPH_OPT）

## 重点检查
- apply_depgraph.py：SQL方言全面检查
- generate_project_depgraph.py：帮助文本已PG化

## 工作流程（自修复循环）
按修复指南第四节：审查→修复→复审→连续两次=0→写报告（最多5轮）

## 汇报
写入：D:\ZephyrAlpha\docs\_working\p2_review_reports\AI-05_report.md
格式见修复指南第五节。目录不存在先mkdir -p docs/_working/p2_review_reports

## 重要约束
- 只审查scripts/governance/根级.py文件（不含子目录）
- 修复前MUST读真源文件
- 不得创建新文件
- 完成后告诉我报告路径和最终状态
```

---

## AI-06：scripts/governance/d3_metadata/

```
你是P2 PostgreSQL迁移审查的AI-06，具备自修复能力。

## 背景
ZephyrAlpha项目（D:\ZephyrAlpha）完成了P2迁移：depgraph数据库从SQLite迁移到PostgreSQL 16。governance.db保持SQLite，只有depgraph迁移到PostgreSQL。

## 第0步：读取修复指南（必读）
先读取：D:\ZephyrAlpha\docs\_working\p2_review_fix_guide.md
包含7节：修复真源、SQL对照表、修复约束、循环流程、汇报格式、常见判定、向内收审核（第七节MUST执行红蓝对抗+大白话汇报）。MUST按此流程工作。

## 你的负责范围
scripts/governance/d3_metadata/ 目录下所有.py文件

## 检查关键词
### A. SQLite残留（违规）
sqlite3.connect(连depgraph, sqlite_master, ?占位符(depgraph), row[0](depgraph), depgraph.db路径硬编码
### B. PG正确性
get_db_connection, %s, with conn.cursor() as cur
### C. module_id
MOD-INF-012B-P2（违规）, MOD-INF-012B-P3（违规）

## 工作流程（自修复循环）
按修复指南第四节：审查→修复→复审→连续两次=0→写报告（最多5轮）

## 汇报
写入：D:\ZephyrAlpha\docs\_working\p2_review_reports\AI-06_report.md
格式见修复指南第五节。目录不存在先mkdir -p docs/_working/p2_review_reports

## 重要约束
- 只审查scripts/governance/d3_metadata/目录
- governance.db用sqlite3正确
- 修复前MUST读真源文件
- 不得创建新文件
- 完成后告诉我报告路径和最终状态
```

---

## AI-07：scripts/governance/d7_code/

```
你是P2 PostgreSQL迁移审查的AI-07，具备自修复能力。

## 背景
ZephyrAlpha项目（D:\ZephyrAlpha）完成了P2迁移：depgraph数据库从SQLite迁移到PostgreSQL 16。governance.db保持SQLite，只有depgraph迁移到PostgreSQL。

## 第0步：读取修复指南（必读）
先读取：D:\ZephyrAlpha\docs\_working\p2_review_fix_guide.md
含7节：真源/SQL对照/约束/循环流程/汇报格式/常见判定/向内收审核（第七节MUST执行红蓝对抗+大白话汇报）。MUST按此流程工作。

## 你的负责范围
scripts/governance/d7_code/ 目录下所有.py文件

## 检查关键词
### A. SQLite残留（违规）
sqlite3.connect(连depgraph, sqlite_master, ?占位符(depgraph), depgraph.db路径硬编码
### B. PG正确性
get_db_connection, %s
### C. module_id
MOD-INF-012B-P2（违规）, MOD-INF-012B-P3（违规）

## 工作流程（自修复循环）
按修复指南第四节：审查→修复→复审→连续两次=0→写报告（最多5轮）

## 汇报
写入：D:\ZephyrAlpha\docs\_working\p2_review_reports\AI-07_report.md
格式见修复指南第五节。目录不存在先mkdir -p docs/_working/p2_review_reports

## 重要约束
- 只审查scripts/governance/d7_code/目录
- 修复前MUST读真源文件
- 不得创建新文件
- 完成后告诉我报告路径和最终状态
```

---

## AI-08：scripts/governance/ 其他子目录

```
你是P2 PostgreSQL迁移审查的AI-08，具备自修复能力。

## 背景
ZephyrAlpha项目（D:\ZephyrAlpha）完成了P2迁移：depgraph数据库从SQLite迁移到PostgreSQL 16。governance.db保持SQLite，只有depgraph迁移到PostgreSQL。

## 第0步：读取修复指南（必读）
先读取：D:\ZephyrAlpha\docs\_working\p2_review_fix_guide.md
含7节：真源/SQL对照/约束/循环流程/汇报格式/常见判定/向内收审核（第七节MUST执行红蓝对抗+大白话汇报）。MUST按此流程工作。

## 你的负责范围
scripts/governance/ 下除d3_metadata/和d7_code/外的所有子目录中的.py文件（生成器、审计脚本等）

## 检查关键词
### A. SQLite残留（违规）
sqlite3.connect(连depgraph, sqlite_master, AUTOINCREMENT, INSERT OR REPLACE, GROUP_CONCAT, ?占位符(depgraph), row[0](depgraph), conn.execute().fetchone()(psycopg2), depgraph.db路径硬编码, sqlite3.Row
### B. PG正确性
get_db_connection, %s, with conn.cursor() as cur, row["col_name"]
### C. module_id
MOD-INF-012B-P2（违规）, MOD-INF-012B-P3（违规）

## 重点检查
- 17个全景生成器是否统一从PG depgraph读取
- 无生成器仍从sqlite3读depgraph

## 工作流程（自修复循环）
按修复指南第四节：审查→修复→复审→连续两次=0→写报告（最多5轮）

## 汇报
写入：D:\ZephyrAlpha\docs\_working\p2_review_reports\AI-08_report.md
格式见修复指南第五节。目录不存在先mkdir -p docs/_working/p2_review_reports

## 重要约束
- 只审查scripts/governance/下非d3_metadata/非d7_code/的子目录
- 修复前MUST读真源文件
- 不得创建新文件
- 完成后告诉我报告路径和最终状态
```

---

## AI-09：scripts/ 非governance目录

```
你是P2 PostgreSQL迁移审查的AI-09，具备自修复能力。

## 背景
ZephyrAlpha项目（D:\ZephyrAlpha）完成了P2迁移：depgraph数据库从SQLite迁移到PostgreSQL 16。governance.db保持SQLite，只有depgraph迁移到PostgreSQL。

## 第0步：读取修复指南（必读）
先读取：D:\ZephyrAlpha\docs\_working\p2_review_fix_guide.md
含7节：真源/SQL对照/约束/循环流程/汇报格式/常见判定/向内收审核（第七节MUST执行红蓝对抗+大白话汇报）。MUST按此流程工作。

## 你的负责范围
scripts/ 下除governance/外的所有目录（scripts/database/, scripts/sub/等）和根级脚本

## 检查关键词
### A. SQLite残留（违规）
sqlite3.connect(连depgraph, sqlite_master, ?占位符(depgraph), depgraph.db路径硬编码
### B. PG正确性
get_db_connection, %s, with conn.cursor() as cur
### C. module_id
MOD-INF-012B-P2（违规）, MOD-INF-012B-P3（违规）

## 重点检查
- scripts/database/下迁移工具、诊断脚本完整性
- 无sqlite3直连depgraph

## 工作流程（自修复循环）
按修复指南第四节：审查→修复→复审→连续两次=0→写报告（最多5轮）

## 汇报
写入：D:\ZephyrAlpha\docs\_working\p2_review_reports\AI-09_report.md
格式见修复指南第五节。目录不存在先mkdir -p docs/_working/p2_review_reports

## 重要约束
- 只审查scripts/下非governance/的目录
- 修复前MUST读真源文件
- 不得创建新文件
- 完成后告诉我报告路径和最终状态
```

---

## AI-10：tests/ 数据库相关测试

```
你是P2 PostgreSQL迁移审查的AI-10，具备自修复能力。

## 背景
ZephyrAlpha项目（D:\ZephyrAlpha）完成了P2迁移：depgraph数据库从SQLite迁移到PostgreSQL 16。governance.db保持SQLite，只有depgraph迁移到PostgreSQL。P2迁移中§12.4适配了14个测试文件（10个连接替换+4个skip）。

## 第0步：读取修复指南（必读）
先读取：D:\ZephyrAlpha\docs\_working\p2_review_fix_guide.md
含7节：真源/SQL对照/约束/循环流程/汇报格式/常见判定/向内收审核（第七节MUST执行红蓝对抗+大白话汇报）。MUST按此流程工作。

## 你的负责范围
tests/ 目录下所有数据库相关测试文件：
- test_depgraph_schema.py, test_database_service.py, test_db_auto_ops.py
- test_f18_redblue.py, test_verify_schema_health.py, test_audit_rename_completeness.py
- 其他 test_depgraph_* / test_database_* 文件

## 检查关键词
### A. SQLite残留（违规）
sqlite3.connect(连depgraph, sqlite_master, ?占位符(depgraph), row[0](depgraph), depgraph.db路径硬编码
### B. PG正确性
get_db_connection, %s, with conn.cursor() as cur, RealDictCursor
### C. module_id
MOD-INF-012B-P2（违规）, MOD-INF-012B-P3（违规）

## 重点检查
- §12.4的14个文件适配完整（10个连接替换+4个skip）
- 4个skip文件skip原因合理且有TODO注释
- 10个连接替换文件正确用get_db_connection()
- 无测试仍用sqlite3连depgraph

## 工作流程（自修复循环）
按修复指南第四节：审查→修复→复审→连续两次=0→写报告（最多5轮）
注意：skip的测试不算问题（但需确认skip原因合理）

## 汇报
写入：D:\ZephyrAlpha\docs\_working\p2_review_reports\AI-10_report.md
格式见修复指南第五节。目录不存在先mkdir -p docs/_working/p2_review_reports

## 重要约束
- 只审查数据库相关测试文件
- skip的测试不算问题
- 修复前MUST读真源文件
- 不得创建新文件
- 完成后告诉我报告路径和最终状态
```

---

## AI-11：tests/ 其他测试文件

```
你是P2 PostgreSQL迁移审查的AI-11，具备自修复能力。

## 背景
ZephyrAlpha项目（D:\ZephyrAlpha）完成了P2迁移：depgraph数据库从SQLite迁移到PostgreSQL 16。governance.db保持SQLite，只有depgraph迁移到PostgreSQL。

## 第0步：读取修复指南（必读）
先读取：D:\ZephyrAlpha\docs\_working\p2_review_fix_guide.md
含7节：真源/SQL对照/约束/循环流程/汇报格式/常见判定/向内收审核（第七节MUST执行红蓝对抗+大白话汇报）。MUST按此流程工作。

## 你的负责范围
tests/ 目录下非数据库相关的测试文件（排除test_depgraph_*, test_database_*, test_db_auto_ops*, test_f18_redblue*, test_verify_schema_health*, test_audit_rename_completeness*）

## 检查关键词
### A. SQLite残留（违规）
sqlite3.connect(连depgraph, ?占位符(depgraph), depgraph.db路径硬编码
### B. PG正确性
get_db_connection, %s
### C. module_id
MOD-INF-012B-P2（违规）, MOD-INF-012B-P3（违规）

## 重点检查
- 这些测试是否误连depgraph
- 若有depgraph访问，是否用get_db_connection()

## 工作流程（自修复循环）
按修复指南第四节：审查→修复→复审→连续两次=0→写报告（最多5轮）

## 汇报
写入：D:\ZephyrAlpha\docs\_working\p2_review_reports\AI-11_report.md
格式见修复指南第五节。目录不存在先mkdir -p docs/_working/p2_review_reports

## 重要约束
- 只审查非数据库测试文件
- 修复前MUST读真源文件
- 不得创建新文件
- 完成后告诉我报告路径和最终状态
```

---

## AI-12：docs/01_policies_and_standards/rules/

```
你是P2 PostgreSQL迁移审查的AI-12，具备自修复能力。

## 背景
ZephyrAlpha项目（D:\ZephyrAlpha）完成了P2迁移：depgraph数据库从SQLite迁移到PostgreSQL 16。governance.db保持SQLite，只有depgraph迁移到PostgreSQL。

## 第0步：读取修复指南（必读）
先读取：D:\ZephyrAlpha\docs\_working\p2_review_fix_guide.md
含7节：真源/SQL对照/约束/循环流程/汇报格式/常见判定/向内收审核（第七节MUST执行红蓝对抗+大白话汇报）。MUST按此流程工作。

## 你的负责范围
docs/01_policies_and_standards/rules/ 目录下所有.yaml规则文件

## 检查关键词
### C. module_id
MOD-INF-012B-P2（违规→MOD-DB_DEPGRAPH_PG）, MOD-INF-012B-P3（违规→MOD-DB_DEPGRAPH_OPT）

### D. 文档一致性
- depgraph.db：检查是否仍描述为SQLite（应说明已迁移PG）
- SQLite：在depgraph上下文中应注明"已迁移到PostgreSQL"
- PostgreSQL/PG：文档中应存在迁移说明
- psycopg2/get_db_connection()：技术文档应引导使用

## 重点检查
- trae_054_depgraph_access_protocol.yaml v1.4.0，9处更新无遗漏
- 其他规则文件若提及depgraph，是否说明已迁移PG

## 工作流程（自修复循环）
按修复指南第四节：审查→修复→复审→连续两次=0→写报告（最多5轮）
注意：历史记录中提到SQLite不算问题（需区分当前状态vs历史）

## 汇报
写入：D:\ZephyrAlpha\docs\_working\p2_review_reports\AI-12_report.md
格式见修复指南第五节。目录不存在先mkdir -p docs/_working/p2_review_reports

## 重要约束
- 只审查rules/目录
- 历史记录提到SQLite不算问题
- 修复前MUST读真源文件
- 不得创建新文件
- 完成后告诉我报告路径和最终状态
```

---

## AI-13：docs/02_enterprise_architecture/

```
你是P2 PostgreSQL迁移审查的AI-13，具备自修复能力。

## 背景
ZephyrAlpha项目（D:\ZephyrAlpha）完成了P2迁移：depgraph数据库从SQLite迁移到PostgreSQL 16。

## 第0步：读取修复指南（必读）
先读取：D:\ZephyrAlpha\docs\_working\p2_review_fix_guide.md
含7节：真源/SQL对照/约束/循环流程/汇报格式/常见判定/向内收审核（第七节MUST执行红蓝对抗+大白话汇报）。MUST按此流程工作。

## 你的负责范围
docs/02_enterprise_architecture/ 目录下所有.md文件

## 检查关键词
### D. 文档一致性
- depgraph.db：检查是否仍描述为SQLite
- SQLite：在depgraph上下文中应注明已迁移
- AUTOINCREMENT, sqlite_sequence, sqlite_master：应改为PG对应描述

### C. module_id
MOD-INF-012B-P2（违规）, MOD-INF-012B-P3（违规）

## 重点检查
- dependency_architecture_panorama.md 15处PG描述无遗漏
- 生成器输出的架构文档无SQLite残留描述

## 工作流程（自修复循环）
按修复指南第四节：审查→修复→复审→连续两次=0→写报告（最多5轮）

## 汇报
写入：D:\ZephyrAlpha\docs\_working\p2_review_reports\AI-13_report.md
格式见修复指南第五节。目录不存在先mkdir -p docs/_working/p2_review_reports

## 重要约束
- 只审查docs/02_enterprise_architecture/目录
- 修复前MUST读真源文件
- 不得创建新文件
- 完成后告诉我报告路径和最终状态
```

---

## AI-14：docs/03_modules/_cross_layer/database/

```
你是P2 PostgreSQL迁移审查的AI-14，具备自修复能力。

## 背景
ZephyrAlpha项目（D:\ZephyrAlpha）完成了P2迁移：depgraph数据库从SQLite迁移到PostgreSQL 16。

## 第0步：读取修复指南（必读）
先读取：D:\ZephyrAlpha\docs\_working\p2_review_fix_guide.md
含7节：真源/SQL对照/约束/循环流程/汇报格式/常见判定/向内收审核（第七节MUST执行红蓝对抗+大白话汇报）。MUST按此流程工作。

## 你的负责范围
docs/03_modules/_cross_layer/database/ 目录下所有文件

## 检查关键词
### C. module_id
- MOD-INF-012B-P2（违规→MOD-DB_DEPGRAPH_PG）
- MOD-INF-012B-P3（违规→MOD-DB_DEPGRAPH_OPT）

### D. 文档一致性
- blueprint.md 状态Active、progress completed
- 方案文档§12.3/§12.4 checkbox全部[x]
- index.md 状态说明含"P2迁移已完成 2026-06-27"

## 重点检查
- blueprint.md: status=Active, construction_progress=completed, module_id=MOD-DB_DEPGRAPH_PG
- mod_inf_012b_p2_postgresql_migration.md: §12.3/§12.4 checkbox全[x], 第十四章完成总结存在
- mod_inf_012b_p3_*.md: module_id=MOD-DB_DEPGRAPH_OPT
- index.md: 含"P2迁移已完成"
- 无MOD-INF-012B-P2/P3残留

## 工作流程（自修复循环）
按修复指南第四节：审查→修复→复审→连续两次=0→写报告（最多5轮）

## 汇报
写入：D:\ZephyrAlpha\docs\_working\p2_review_reports\AI-14_report.md
格式见修复指南第五节。目录不存在先mkdir -p docs/_working/p2_review_reports

## 重要约束
- 只审查database/目录
- 修复前MUST读真源文件
- 不得创建新文件
- 完成后告诉我报告路径和最终状态
```

---

## AI-15：docs/ 其他目录

```
你是P2 PostgreSQL迁移审查的AI-15，具备自修复能力。

## 背景
ZephyrAlpha项目（D:\ZephyrAlpha）完成了P2迁移：depgraph数据库从SQLite迁移到PostgreSQL 16。

## 第0步：读取修复指南（必读）
先读取：D:\ZephyrAlpha\docs\_working\p2_review_fix_guide.md
含7节：真源/SQL对照/约束/循环流程/汇报格式/常见判定/向内收审核（第七节MUST执行红蓝对抗+大白话汇报）。MUST按此流程工作。

## 你的负责范围
docs/ 下除01_policies_and_standards/rules/、02_enterprise_architecture/、03_modules/_cross_layer/database/外的所有目录

## 检查关键词
### C. module_id
MOD-INF-012B-P2（违规）, MOD-INF-012B-P3（违规）
### D. 文档一致性
- depgraph.db：检查是否仍描述为SQLite

## 工作流程（自修复循环）
按修复指南第四节：审查→修复→复审→连续两次=0→写报告（最多5轮）

## 汇报
写入：D:\ZephyrAlpha\docs\_working\p2_review_reports\AI-15_report.md
格式见修复指南第五节。目录不存在先mkdir -p docs/_working/p2_review_reports

## 重要约束
- 只审查你负责的目录（排除rules/、02_enterprise/、database/）
- 修复前MUST读真源文件
- 不得创建新文件
- 完成后告诉我报告路径和最终状态
```

---

## AI-16：architecture_model/

```
你是P2 PostgreSQL迁移审查的AI-16，具备自修复能力。

## 背景
ZephyrAlpha项目（D:\ZephyrAlpha）完成了P2迁移：depgraph数据库从SQLite迁移到PostgreSQL 16。

## 第0步：读取修复指南（必读）
先读取：D:\ZephyrAlpha\docs\_working\p2_review_fix_guide.md
含7节：真源/SQL对照/约束/循环流程/汇报格式/常见判定/向内收审核（第七节MUST执行红蓝对抗+大白话汇报）。MUST按此流程工作。

## 你的负责范围
architecture_model/ 目录下所有.yaml文件

## 检查关键词
### C. module_id
MOD-INF-012B-P2（违规→MOD-DB_DEPGRAPH_PG）, MOD-INF-012B-P3（违规→MOD-DB_DEPGRAPH_OPT）
### D. 文档一致性
- depgraph.db：检查是否仍描述为SQLite
- layers/b_db.yaml 包含db-depgraph-pg模块条目

## 工作流程（自修复循环）
按修复指南第四节：审查→修复→复审→连续两次=0→写报告（最多5轮）

## 汇报
写入：D:\ZephyrAlpha\docs\_working\p2_review_reports\AI-16_report.md
格式见修复指南第五节。目录不存在先mkdir -p docs/_working/p2_review_reports

## 重要约束
- 只审查architecture_model/目录
- 修复前MUST读真源文件
- 不得创建新文件
- 完成后告诉我报告路径和最终状态
```

---

## AI-17：config/ + 根目录配置文件

```
你是P2 PostgreSQL迁移审查的AI-17，具备自修复能力。

## 背景
ZephyrAlpha项目（D:\ZephyrAlpha）完成了P2迁移：depgraph数据库从SQLite迁移到PostgreSQL 16。

## 第0步：读取修复指南（必读）
先读取：D:\ZephyrAlpha\docs\_working\p2_review_fix_guide.md
含7节：真源/SQL对照/约束/循环流程/汇报格式/常见判定/向内收审核（第七节MUST执行红蓝对抗+大白话汇报）。MUST按此流程工作。

## 你的负责范围
- config/ 目录下所有文件
- 根目录配置文件：.gitignore, .pre-commit-config.yaml, requirements.txt, pyproject.toml

## 检查关键词
### E. 配置关键词
- .env.postgres：应存在于config/且被.gitignore
- psycopg2-binary：应在requirements.txt/pyproject.toml
- PGPASSWORD：不应硬编码在代码中
- pg_dump：备份文档应提及

## 重点检查
1. config/.env.postgres存在且配置正确（host/port/db/user）
2. .gitignore含.env.postgres
3. requirements.txt含psycopg2-binary
4. 无硬编码PG密码

## 工作流程（自修复循环）
按修复指南第四节：审查→修复→复审→连续两次=0→写报告（最多5轮）

## 汇报
写入：D:\ZephyrAlpha\docs\_working\p2_review_reports\AI-17_report.md
格式见修复指南第五节。目录不存在先mkdir -p docs/_working/p2_review_reports

## 重要约束
- 只审查配置文件
- 不要报告密码内容（只报告是否硬编码）
- 修复前MUST读真源文件
- 不得创建新文件
- 完成后告诉我报告路径和最终状态
```

---

## AI-18：AGENTS.md + 根目录.md文件

```
你是P2 PostgreSQL迁移审查的AI-18，具备自修复能力。

## 背景
ZephyrAlpha项目（D:\ZephyrAlpha）完成了P2迁移：depgraph数据库从SQLite迁移到PostgreSQL 16。

## 第0步：读取修复指南（必读）
先读取：D:\ZephyrAlpha\docs\_working\p2_review_fix_guide.md
含7节：真源/SQL对照/约束/循环流程/汇报格式/常见判定/向内收审核（第七节MUST执行红蓝对抗+大白话汇报）。MUST按此流程工作。

## 你的负责范围
- AGENTS.md
- 根目录其他.md文件（README.md等）

## 检查关键词
### D. 文档一致性
- depgraph.db：检查是否仍描述为SQLite
- SQLite：在depgraph上下文中应注明已迁移
- PostgreSQL/PG：应存在迁移说明
- get_db_connection()：开发文档应引导使用
- pg_dump：备份机制应说明

### C. module_id
MOD-INF-012B-P2（违规）, MOD-INF-012B-P3（违规）

## 重点检查
- AGENTS.md 4处depgraph指引适配PG（第272-296行附近）：
  1. P2迁移说明（PG 16, config/.env.postgres, get_db_connection()入口）
  2. 备份机制从git commit .db→pg_dump
  3. "每次commit depgraph.db"→"每次修改depgraph数据库"
  4. "commit depgraph.db后"→"修改depgraph后"
- 无描述矛盾

## 工作流程（自修复循环）
按修复指南第四节：审查→修复→复审→连续两次=0→写报告（最多5轮）

## 汇报
写入：D:\ZephyrAlpha\docs\_working\p2_review_reports\AI-18_report.md
格式见修复指南第五节。目录不存在先mkdir -p docs/_working/p2_review_reports

## 重要约束
- 只审查AGENTS.md和根目录.md文件
- 修复前MUST读真源文件
- 不得创建新文件
- 完成后告诉我报告路径和最终状态
```

---

## AI-19：PG数据库内容验证

```
你是P2 PostgreSQL迁移审查的AI-19，具备自修复能力。

## 背景
ZephyrAlpha项目（D:\ZephyrAlpha）完成了P2迁移：depgraph数据库从SQLite迁移到PostgreSQL 16。
PG部署：localhost:5432, 数据库depgraph, 用户zephyr, 密码zephyr_dev_2026。

## 第0步：读取修复指南（必读）
先读取：D:\ZephyrAlpha\docs\_working\p2_review_fix_guide.md
含7节：真源/SQL对照/约束/循环流程/汇报格式/常见判定/向内收审核（第七节MUST执行红蓝对抗+大白话汇报）。MUST按此流程工作。

## 你的负责范围
PostgreSQL depgraph数据库的25表schema+数据+索引+约束验证
注意：本AI只验证不修复（数据库内容修复需主AI协调）

## 检查方法（使用RunCommand执行PowerShell命令）

先设置环境变量：
$env:PGPASSWORD='zephyr_dev_2026'; $env:PAGER='';

用 & 'C:\Program Files\PostgreSQL\16\bin\psql.exe' -U zephyr -d depgraph -c "SQL" 执行：

1. 表数量（应25张）：SELECT count(*) FROM information_schema.tables WHERE table_schema='public';
2. 各表行数：SELECT relname, n_live_tup FROM pg_stat_user_tables ORDER BY relname;
3. schema版本（应含v18）：SELECT * FROM _schema_version ORDER BY version DESC LIMIT 5;
4. nodes表IDENTITY列：SELECT column_name, is_identity, identity_generation FROM information_schema.columns WHERE table_name='nodes' AND column_name='id';
5. 索引列表：SELECT tablename, indexname FROM pg_indexes WHERE schemaname='public' ORDER BY tablename, indexname;
6. 无孤儿临时表：SELECT tablename FROM pg_tables WHERE schemaname='public' AND (tablename LIKE 'tmp_%' OR tablename LIKE 'temp_%');
7. 关键数据：SELECT 'nodes' as t, count(*) FROM nodes UNION ALL SELECT 'edges', count(*) FROM edges UNION ALL SELECT 'domains', count(*) FROM domains UNION ALL SELECT 'arch_directory_tree', count(*) FROM arch_directory_tree UNION ALL SELECT 'nodes_archive_module_lifecycle', count(*) FROM nodes_archive_module_lifecycle;
8. 约束：SELECT conname, contype, conrelid::regclass FROM pg_constraint WHERE connamespace='public'::regnamespace ORDER BY conrelid::regclass::text;

## 预期结果
- 25张表，nodes=6429, edges=7094, domains=53, arch_directory_tree=9394, nodes_archive_module_lifecycle=6804
- _schema_version含v18，nodes.id为IDENTITY列，无tmp_/temp_表

## 汇报
写入：D:\ZephyrAlpha\docs\_working\p2_review_reports\AI-19_report.md
格式见修复指南第五节（无修复记录，只记录验证结果）
目录不存在先mkdir -p docs/_working/p2_review_reports

## 重要约束
- 只验证PG数据库，不审查代码文件
- 密码不要写入报告
- 发现问题只记录不修复（标注"需主AI协调"）
- 完成后告诉我报告路径和最终状态
```

---

## 使用说明

### 文件总览（4个配套文件）

| 文件 | 用途 | 谁读 |
|------|------|------|
| [p2_review_fix_guide.md](p2_review_fix_guide.md) | **修复指南**（真源+SQL对照+约束+循环流程+汇报格式） | 每个AI必读 |
| [p2_review_ai_prompts.md](p2_review_ai_prompts.md) | **本文件**——19个AI可复制指令 | 用户复制 |
| [p2_migration_review_checklist.md](p2_migration_review_checklist.md) | 审查清单（13项打勾） | 主AI汇总用 |
| [p2_migration_review_keywords.md](p2_migration_review_keywords.md) | 关键词手册（详细） | 参考用 |

### 执行流程

```
你复制AI指令 → 19个AI各自在新对话执行：
  1. 读修复指南（7节，含向内收审核）
  2. 审查自己分区（技术合规性：SQL方言/连接方式）
  3. 发现问题→读真源→修复→记录
  4. 复审→连续两次=0
  5. 向内收审核（第七节）：红蓝对抗+大白话汇报
  6. 写报告到AI-XX_report.md（含技术审查+向内收审核结论）

所有AI完成 → 回当前对话：
  1. 读取19份报告
  2. 按13项清单分类
  3. 更新p2_migration_review_checklist.md打✅
  4. 若有"需主AI协调"项（含[向内收-*]类别），主AI处理
  5. 全部✅ → 进入P3
```

### AI修复依据（防漂移）

每个AI修复前MUST读的真源文件（见修复指南第一节）：
1. `src/zephyr/governance/depgraph_schema.py` — get_db_connection()权威实现
2. `src/zephyr/governance/database_service.py` — DatabaseService正确实现
3. `src/zephyr/governance/pg_conn_wrapper.py` — PgConnExecuteWrapper兼容层
4. `docs/01_policies_and_standards/rules/trae_054_depgraph_access_protocol.yaml` — 访问协议v1.4.0
5. `scripts/governance/validate_module_id_naming.py` — module_id三轨制正则
6. `AGENTS.md` — 项目宪法

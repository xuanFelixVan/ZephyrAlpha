---
doc_type: audit_report
status: active
title: "AI-01 审查报告——P2迁移自修复"
module_id: "MOD-DB_DEPGRAPH_PG"
version: "2.0.0"
created: "2026-06-28"
ttl: task_bound
completes_when: "报告归档"
---

# AI-01 审查报告

## 元信息
- 审查轮次：共5轮（第1轮修复违规→第2-3轮连续零问题确认→第4轮修复提示项→第5轮连续零问题确认）
- 审查时间：2026-06-28
- 负责分区：src/zephyr/governance/ 数据库核心文件
- 审查文件数：2（任务列出3个，其中 pg_conn_wrapper.py 不存在）
- 最终状态：✅ 通过（连续两次=0，含提示项）

## 审查文件清单
| 文件 | 状态 | 说明 |
|------|------|------|
| src/zephyr/governance/database_service.py | ✅ 已审查+修复3处 | 1违规+2提示项，全部修复 |
| src/zephyr/governance/depgraph_schema.py | ✅ 已审查+修复1处 | 无违规（PG真源文件），1提示项已修复 |
| src/zephyr/governance/pg_conn_wrapper.py | ⚠️ 文件不存在 | Glob全库搜索未找到，任务清单与实际不符 |

## 审查结果汇总
- 初始问题数：1（违规）+ 2（提示项）
- 修复问题数：3（1违规 + 2提示项）
- 残留问题数：0
- 连续零问题轮次：第4轮、第5轮

## 修复记录

### 修复1：A9+A8 违规——__main__块depgraph连接SQLite残留
- **文件**：src/zephyr/governance/database_service.py
- **行号**：L330（原）→ L330-332（修复后）
- **类别**：A9 (conn.execute().fetchone() 在 psycopg2 上) + A8 (row[0] 数字索引 depgraph)
- **上下文**：`if __name__ == "__main__"` 测试块中测试 depgraph 连接
- **原代码**：
  ```python
  # 测试 depgraph.db
  conn = ds.get_depgraph_conn()
  nodes = conn.execute("SELECT COUNT(*) FROM nodes").fetchone()[0]
  print(f"depgraph.db: {nodes} nodes")
  ```
- **新代码**：
  ```python
  # 测试 depgraph.db
  conn = ds.get_depgraph_conn()
  with conn.cursor() as cur:
      cur.execute("SELECT COUNT(*) FROM nodes")
      nodes = cur.fetchone()["count"]
  print(f"depgraph.db: {nodes} nodes")
  ```
- **依据文件**：src/zephyr/governance/depgraph_schema.py（get_db_connection 返回 psycopg2 连接）+ src/zephyr/governance/database_service.py L88（cursor_factory=RealDictCursor，需用 row["col_name"] 而非 row[0]）
- **根因分析**：P2迁移时生产方法（get_node/get_nodes_by_domain等）已正确更新为cursor模式，但 `__main__` 测试块被遗漏。psycopg2 connection 无 execute() 方法直接返回结果，且 RealDictCursor 的 RealDictRow 不支持整数索引，原代码运行会直接崩溃。

### 修复2：[向内收-可被绕过] 提示项——移除self.depgraph_db死变量
- **文件**：src/zephyr/governance/database_service.py
- **行号**：L63（原，已移除）
- **类别**：A11 (depgraph.db路径硬编码) + 向内收-可被绕过
- **调研结论**：全库Grep `depgraph_db` 在 `*.py` 文件中仅4个匹配——1个变量定义（本行）、1个注释（depgraph_reader.py L28 `[TESTS]` 标记）、2个测试方法名（test_vocab_sync_chain.py 测试的是 `_shared/constants.py` 的 `DEPGRAPH_DB_PATH`，非本变量）。**确认无任何外部代码引用 `self.depgraph_db` 或 `ds.depgraph_db`**。
- **原代码**：
  ```python
  def __init__(self):
      self.governance_db = r"D:\ZephyrAlpha\data\databases\governance.db"
      self.depgraph_db = r"D:\ZephyrAlpha\data\databases\depgraph.db"
      self.market_db = r"D:\ZephyrAlpha\data\databases\market.duckdb"
  ```
- **新代码**：
  ```python
  def __init__(self):
      self.governance_db = r"D:\ZephyrAlpha\data\databases\governance.db"
      self.market_db = r"D:\ZephyrAlpha\data\databases\market.duckdb"
  ```
- **依据文件**：全库Grep确认无外部引用；get_depgraph_conn() 使用 get_db_connection()（L87），不使用 self.depgraph_db
- **根因分析**：SQLite时代遗留的公共属性，P2迁移后 get_depgraph_conn 改用 get_db_connection() 但忘记清理旧变量。移除后消除新AI误用 sqlite3.connect(self.depgraph_db) 绕过 get_db_connection() 真源的风险。

### 修复3：[向内收-真源分裂] 提示项——_MIGRATIONS定义处添加防误导注释
- **文件**：src/zephyr/governance/depgraph_schema.py
- **行号**：L617-621（注释块）
- **类别**：A4 (AUTOINCREMENT) + 向内收-真源分裂
- **调研结论**：`_MIGRATIONS`/`_DDL_*` 被4个外部文件引用——`check_schema_version_writes.py`（用 max(version) 做版本校验）、`verify_schema_health.py`（用 _DDL_* 列名做DB列校验）、`tests/test_depgraph_schema.py`、`tests/test_verify_schema_health.py`。**是活数据源，不能移除**。AUTOINCREMENT 在 DDL 中不影响功能（不执行，parse_ddl_columns 只取列名首 token）。完全移除需改4个外部文件，超出3文件范围。
- **原代码**：
  ```python
  # ---------------------------------------------------------------------------
  # 版本化迁移框架
  # ---------------------------------------------------------------------------

  _MIGRATIONS: list[tuple[int, str, list[str]]] = [
  ```
- **新代码**：
  ```python
  # ---------------------------------------------------------------------------
  # 版本化迁移框架（P2迁移后：历史 SQLite 迁移记录，不再执行）
  # PG schema 真源：scripts/governance/migrate_sqlite_to_pg/02_create_pg_schema.sql
  # 本列表保留以支持 check_schema_version_writes.py / verify_schema_health.py 引用版本号元数据
  # ---------------------------------------------------------------------------

  _MIGRATIONS: list[tuple[int, str, list[str]]] = [
  ```
- **依据文件**：scripts/governance/check_schema_version_writes.py L133-135（引用 _MIGRATIONS 版本号）；scripts/governance/verify_schema_health.py L103-125（引用 _DDL_* 列名）；修复指南第七节7.2.4 AI可发现性双问
- **根因分析**：`_MIGRATIONS` 定义处缺少上下文注释，新AI无法知道这是历史记录还是活数据源。添加3行注释指明：历史性质、PG schema真源位置、保留原因。最小化修复解决"新AI误用AUTOINCREMENT"风险，无需改动4个外部文件。

## 未修复问题（需主AI协调）
无。所有违规和提示项均已修复。

## 确认无问题项

### A类 SQLite残留检查（depgraph上下文）
- A1 sqlite3.connect(depgraph)：✅ 无（get_depgraph_conn 使用 get_db_connection()）
- A2 import sqlite3(depgraph上下文)：✅ 无（import sqlite3 仅用于 governance.db，L33 豁免）
- A3 sqlite_master：✅ 无（仅 L324 governance.db 测试，豁免）
- A4 AUTOINCREMENT：✅ 已修复（_MIGRATIONS定义处添加防误导注释，指明历史性质+PG真源位置；DDL中AUTOINCREMENT不执行，属历史参考记录）
- A5 INSERT OR REPLACE：✅ 无（depgraph_schema.py L1101 使用 ON CONFLICT DO NOTHING）
- A6 GROUP_CONCAT：✅ 无
- A7 ?占位符(depgraph)：✅ 无（depgraph方法均用 %s；?仅用于 governance.db 和 market.duckdb，豁免）
- A8 row[0]数字索引(depgraph)：✅ 已修复（L330原违规已改为 row["count"]；depgraph_schema.py 中 row[0] 使用默认tuple cursor，非RealDictCursor，属正确PG用法）
- A9 conn.execute().fetchone()(psycopg2)：✅ 已修复（L330原违规已改为 cursor 模式；其余 conn.execute().fetch* 均为 governance.db/market.duckdb，豁免）
- A10 sqlite3.Error(depgraph)：✅ 无（depgraph_schema.py L1088 使用 psycopg2.Error）
- A11 depgraph.db路径硬编码：✅ 已修复（self.depgraph_db 死变量已移除；depgraph_schema.py L72 DB_PATH 使用 REPO_ROOT 且标注为备份路径参考）
- A12 PRAGMA journal_mode=WAL：✅ 无（depgraph_schema.py L46-49,370 注释说明已删除）
- A13 sqlite3.Row：✅ 无（L78 仅用于 governance.db，豁免）
- A14 last_insert_rowid()：✅ 无
- A15 sqlite_sequence：✅ 无

### B类 PG正确性检查
- psycopg2：✅ 存在（database_service.py L39, depgraph_schema.py L65）
- RealDictCursor：✅ 存在（database_service.py L40, L87）
- get_db_connection：✅ 存在（database_service.py L42 import, L86 调用；depgraph_schema.py L1154 定义）
- %s 占位符：✅ 存在（database_service.py depgraph方法 L200,208,216,224,232）
- ON CONFLICT DO UPDATE/NOTHING：✅ 存在（depgraph_schema.py L1101）
- information_schema：✅ 存在（depgraph_schema.py L1050,1057,1127,1137,1199）
- with conn.cursor() as cur：✅ 存在（database_service.py depgraph方法, depgraph_schema.py 多处）
- row["col_name"]：✅ 存在（database_service.py L332 修复后, depgraph方法 dict(row) 转换）
- psycopg2.Error：✅ 存在（depgraph_schema.py L1088）
- autocommit：✅ 存在（depgraph_schema.py L1158,1181）

### C类 module_id检查
- MOD-INF-012B-P2：✅ 无违规（depgraph_schema.py L74,976 已使用正确的 MOD-DB_DEPGRAPH_PG）
- MOD-INF-012B-P3：✅ 无

### 豁免确认（governance.db SQLite + market.duckdb DuckDB）
- database_service.py L33 import sqlite3：✅ 豁免（governance.db）
- database_service.py L76 sqlite3.connect(governance_db)：✅ 豁免（governance.db）
- database_service.py L77 sqlite3.Row：✅ 豁免（governance.db）
- database_service.py L119,135 conn.execute("SELECT 1").fetchone()：✅ 豁免（governance.db/market.duckdb）
- database_service.py L161,169,177,186 ?占位符：✅ 豁免（governance.db）
- database_service.py L243,276,298,312 ?占位符：✅ 豁免（market.duckdb）
- database_service.py L324 sqlite_master：✅ 豁免（governance.db 测试）
- database_service.py L336 information_schema('main')：✅ 豁免（market.duckdb 测试）

## 结论
- [x] 无违规残留，本分区审查通过（连续两次=0）
- [x] 所有提示项已修复（2项全部修复，0项需主AI协调）

---

## 大白话汇报（向内收审核结论）

### 我做了什么
修复了3处问题：(1) database_service.py `__main__`块depgraph连接的SQLite残留代码（conn.execute→cursor模式）；(2) 移除 self.depgraph_db 死变量（消除新AI误用sqlite3连接depgraph的风险）；(3) _MIGRATIONS定义处添加防误导注释（指明历史性质+PG schema真源位置）。

### 这个功能的作用
让 depgraph 数据库连接代码在 P2 迁移后完全符合 PostgreSQL 规范，且消除所有可能误导新AI的 SQLite 残留痕迹。

### 达成了什么目标
本分区2个文件中 depgraph 相关代码无 SQLite 残留违规、无误导性提示项，连续两轮审查问题数=0。

### 解决了什么痛点
- 违规：`__main__` 测试块原代码运行会崩溃（psycopg2无execute()+RealDictRow不支持[0]）
- 提示项1：self.depgraph_db死变量误导新AI绕过get_db_connection()真源
- 提示项2：_MIGRATIONS缺少上下文注释，新AI可能误用AUTOINCREMENT语法

### 功能通过什么触发自动启动
N/A（本次为代码修复，非永久性系统/脚本，不涉及触发机制）。

### 如何自动运行
N/A（代码修复，随模块导入自动生效，无独立运行逻辑）。

### 如何自动关闭
N/A（代码修复，无生命周期需关闭）。

### 向内收审核结果
- [x] 责任唯一真源唯一：通过 — get_db_connection() 是 depgraph PG 连接唯一入口；_MIGRATIONS注释指明PG schema真源在02_create_pg_schema.sql，消除双真源误导
- [x] 能用现成不创造：通过 — 修复复用已有cursor模式，未创建新文件；提示项2用注释而非重构解决
- [N/A] 永久系统全自动：N/A — 本次为代码修复，非永久性系统
- [x] 第一性原理治本：通过 — 违规根因（__main__遗漏）用同模式修复；提示项1根因（死变量）直接移除；提示项2根因（缺上下文）用注释治本
- [x] AI可发现性：通过 — get_db_connection 在 __all__ 导出；_MIGRATIONS注释让新AI知道历史性质+真源位置；self.depgraph_db移除消除误导
- [x] 红蓝对抗：通过 — 所有4项红方攻击均被蓝方防御

### 红蓝极限对抗测试详情

| 红方攻击 | 蓝方防御 | 结果 |
|----------|----------|------|
| 新AI从 governance.db 代码复制 `conn.execute().fetchone()` 模式到 depgraph | 所有 depgraph 生产方法 + `__main__` 均使用 `with conn.cursor() as cur:` 模式 | ✅ 防御成功 |
| 新AI需要创建 depgraph 连接，不知道用 get_db_connection() | `__all__` 导出 + database_service.py 显式 import + 方法文档说明 | ✅ 防御成功 |
| 新AI看到 `self.depgraph_db` 变量，用 sqlite3.connect 连接 depgraph | self.depgraph_db 已移除，不存在此变量 | ✅ 防御成功（修复2） |
| 新AI看到 `_MIGRATIONS` 中 AUTOINCREMENT，用于新建 PG 表 | _MIGRATIONS定义处注释明确说明"历史SQLite迁移记录，不再执行"+PG schema真源指向02_create_pg_schema.sql | ✅ 防御成功（修复3） |

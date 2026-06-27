---
doc_type: audit_report
status: active
title: "AI-10 审查报告——P2迁移自修复（tests/数据库相关测试文件）"
module_id: "MOD-DB_DEPGRAPH_PG"
version: "1.1.0"
created: "2026-06-28"
updated: "2026-06-28"
ttl: task_bound
completes_when: "报告归档"
---

# AI-10 审查报告

## 元信息
- 审查轮次：共5轮（Round 1 发现4问题→修复；Round 2 复审=0；Round 3 复审=0；用户批准修复提示项后 Round 4 修复死代码→Round 5 复审=0，连续两次=0通过）
- 审查时间：2026-06-28
- 负责分区：tests/ 目录下所有数据库相关测试文件
- 审查文件数：10
- 最终状态：✅ 通过（连续两次=0）

## 审查范围（10个文件）

### 连接替换文件（6个，含2个豁免）
| # | 文件路径 | 类型 | 状态 |
|---|---------|------|------|
| 1 | tests/test_depgraph_db.py | depgraph PG端到端 | ✅ PG正确 |
| 2 | tests/test_depgraph_generator_design_protection.py | depgraph 生成器保护 | ✅ PG正确 |
| 3 | tests/governance/test_database_service.py | 三库（depgraph/governance/market） | ✅ PG正确（governance SQLite + market DuckDB 豁免） |
| 4 | tests/test_db_auto_ops.py | 三库自动运维 | ✅ PG正确（governance SQLite 豁免） |
| 5 | tests/unit/test_database_manager_unit.py | zalpha_metadata.db 单元测试 | ✅ 豁免（非depgraph） |
| 6 | tests/unit/db/test_database_manager_db.py | zalpha_metadata.db 数据库测试 | ✅ 豁免（非depgraph） |

### Skip文件（4个）
| # | 文件路径 | skip级别 | 状态 |
|---|---------|---------|------|
| 7 | tests/test_depgraph_schema.py | 模块级 | ✅ 已补TODO |
| 8 | tests/test_verify_schema_health.py | 4个类级skip | ✅ 已补TODO（4处） |
| 9 | tests/unit/test_audit_rename_completeness.py | 模块级 | ✅ 已补TODO |
| 10 | tests/test_f18_redblue.py | 2类级+8方法级skip | ✅ 已补TODO（2类级+1文件级） |

## 审查结果汇总
- 初始问题数：4（4个skip文件均缺TODO注释）
- 提示项修复数：2（删除2处死代码变量）
- 提示项不修复数：1（提示项3超范围，需主AI协调）
- 总修复问题数：6
- 残留问题数：0
- 连续零问题轮次：第4轮、第5轮

## 检查项通过情况

### A. SQLite残留（违规）
| 检查项 | 结果 | 说明 |
|--------|------|------|
| sqlite3.connect 连depgraph | ✅ 通过 | 非skip代码中无sqlite3连depgraph；skip代码中的sqlite3.connect均连tmp_path临时库或governance.db |
| sqlite_master（depgraph） | ✅ 通过 | 仅出现在skip代码中（test_verify_schema_health.py的TestCheckReadonlyTriggers） |
| ?占位符（depgraph） | ✅ 通过 | 非skip代码中depgraph查询均用%s；?占位符仅用于governance.db和market.duckdb（豁免） |
| row[0]（depgraph） | ✅ 通过 | test_depgraph_generator_design_protection.py的row[0]使用psycopg2默认tuple cursor，合法 |
| depgraph.db路径硬编码 | ✅ 通过 | test_depgraph_db.py:16和test_db_auto_ops.py:24的DB_PATH/DEPGRAPH_DB变量为死代码（未使用），未用于sqlite3.connect；test_depgraph_generator_design_protection.py:14的DB_PATH用于subprocess --output-db参数（合法） |

### B. PG正确性
| 检查项 | 结果 | 说明 |
|--------|------|------|
| get_db_connection() | ✅ 通过 | 所有depgraph连接均经此入口（test_depgraph_db.py:20, test_depgraph_generator_design_protection.py:24, test_database_service.py:68, test_db_auto_ops.py:71/102/141/222） |
| %s占位符 | ✅ 通过 | depgraph相关SQL均用%s（test_depgraph_db.py:122/138/157/208, test_db_auto_ops.py:145/151/160） |
| with conn.cursor() as cur | ✅ 通过 | test_database_service.py:70, test_db_auto_ops.py:72/103/142/149/159/223 均用此模式 |
| RealDictCursor | ✅ 通过 | test_depgraph_db.py:11/21 显式设置cursor_factory=RealDictCursor；test_database_service.py:73-74 用values()兼容RealDictRow |
| ON CONFLICT DO UPDATE | ✅ 通过 | test_depgraph_db.py:123/140/159, test_depgraph_generator_design_protection.py:34/125 均用此upsert模式 |

### C. module_id
| 检查项 | 结果 | 说明 |
|--------|------|------|
| MOD-INF-012B-P2（违规） | ✅ 通过 | 全部10个文件均无此违规module_id |
| MOD-INF-012B-P3（违规） | ✅ 通过 | 全部10个文件均无此违规module_id |

### 重点检查项
| 检查项 | 结果 | 说明 |
|--------|------|------|
| §12.4 14文件适配完整 | ✅ 通过 | 本分区负责的10个文件（6连接替换+4skip）全部适配完成 |
| 4个skip文件skip原因合理 | ✅ 通过 | 4个skip文件的skip原因均明确说明P2迁移后不适用PG的具体原因 |
| 4个skip文件有TODO注释 | ✅ 通过（修复后） | 原4文件均缺TODO，已补8处TODO+1处文件级TODO说明 |
| 10个连接替换文件用get_db_connection() | ✅ 通过 | 本分区4个连接替换文件（test_depgraph_db/test_depgraph_generator_design_protection/test_database_service/test_db_auto_ops）+2个豁免文件均正确 |
| 无测试仍用sqlite3连depgraph | ✅ 通过 | 非skip代码中无sqlite3连depgraph |

## 修复记录

### 修复1：test_depgraph_schema.py 添加TODO注释
- **文件**：tests/test_depgraph_schema.py
- **行号**：L53（新增）
- **类别**：skip文件缺TODO注释
- **原代码**：
  ```python
  # P2迁移：init_db 已迁移到 PostgreSQL（只验证 PG schema，不再创建 SQLite 文件），
  # PRAGMA/sqlite_master/_schema_version/SQLite 临时库测试均不适用 PG。
  pytestmark = pytest.mark.skip(
      reason="P2迁移：init_db 已迁移到 PG，SQLite 临时库 + PRAGMA 基线 + migration 事务原子性测试不适用"
  )
  ```
- **新代码**：
  ```python
  # P2迁移：init_db 已迁移到 PostgreSQL（只验证 PG schema，不再创建 SQLite 文件），
  # PRAGMA/sqlite_master/_schema_version/SQLite 临时库测试均不适用 PG。
  # TODO(P2-migration): 后续需将本测试类改造为 PG 适配版本（用 get_db_connection + information_schema + %s 占位符替代 SQLite 临时库/PRAGMA/sqlite_master），当前 skip。
  pytestmark = pytest.mark.skip(
      reason="P2迁移：init_db 已迁移到 PG，SQLite 临时库 + PRAGMA 基线 + migration 事务原子性测试不适用"
  )
  ```
- **依据文件**：docs/_working/p2_review_fix_guide.md 第五节"4个skip文件skip原因合理且有TODO注释"

### 修复2：test_verify_schema_health.py 添加4处TODO注释
- **文件**：tests/test_verify_schema_health.py
- **行号**：L216, L274, L325, L371（新增4处）
- **类别**：skip文件缺TODO注释
- **原代码**（以TestCheckDdlColumns为例）：
  ```python
  # P2迁移：以下测试类依赖 init_db 创建 SQLite 临时库 + sqlite3 连接 + PRAGMA/sqlite_master/触发器，
  # init_db 现在只验证 PG schema 不创建 SQLite 文件，这些测试不适用 PG。
  @pytest.mark.skip(reason="P2迁移：依赖 SQLite 临时库 + init_db 创建 SQLite 文件，不适用 PG")
  class TestCheckDdlColumns:
  ```
- **新代码**：
  ```python
  # P2迁移：以下测试类依赖 init_db 创建 SQLite 临时库 + sqlite3 连接 + PRAGMA/sqlite_master/触发器，
  # init_db 现在只验证 PG schema 不创建 SQLite 文件，这些测试不适用 PG。
  # TODO(P2-migration): 后续需将本测试类改造为 PG 适配版本（用 get_db_connection + information_schema 替代 SQLite 临时库/sqlite_master），当前 skip。
  @pytest.mark.skip(reason="P2迁移：依赖 SQLite 临时库 + init_db 创建 SQLite 文件，不适用 PG")
  class TestCheckDdlColumns:
  ```
- **4处TODO具体内容**：
  - L216 TestCheckDdlColumns: 用 get_db_connection + information_schema 替代 SQLite 临时库/sqlite_master
  - L274 TestCheckReadonlyTriggers: 用 pg_trigger 系统表替代 sqlite_master 触发器检查
  - L325 TestCheckSchemaVersion: 用 get_db_connection + PG _schema_version 表替代 SQLite 临时库
  - L371 TestMainExitCodes: subprocess 调用不再传 --db，verify_schema_health.py 直接连 PG
- **依据文件**：docs/_working/p2_review_fix_guide.md 第五节

### 修复3：test_audit_rename_completeness.py 添加TODO注释
- **文件**：tests/unit/test_audit_rename_completeness.py
- **行号**：L41（新增）
- **类别**：skip文件缺TODO注释
- **原代码**：
  ```python
  # P2迁移：depgraph 已从 SQLite 迁移到 PostgreSQL，PROD_DB (depgraph.db SQLite) 不再是真源。
  # cmd_rename_domain/scan_residual 均基于 SQLite 连接，PRAGMA wal_checkpoint 不适用 PG。
  pytestmark = pytest.mark.skip(
      reason="P2迁移：depgraph 已迁移到 PG，SQLite 文件复制 + PRAGMA wal_checkpoint + sqlite3 连接测试不适用"
  )
  ```
- **新代码**：
  ```python
  # P2迁移：depgraph 已从 SQLite 迁移到 PostgreSQL，PROD_DB (depgraph.db SQLite) 不再是真源。
  # cmd_rename_domain/scan_residual 均基于 SQLite 连接，PRAGMA wal_checkpoint 不适用 PG。
  # TODO(P2-migration): 后续需将本测试改造为 PG 适配版本（用 get_db_connection + PG 库副本替代 SQLite 文件复制 + PRAGMA wal_checkpoint），当前 skip。
  pytestmark = pytest.mark.skip(
      reason="P2迁移：depgraph 已迁移到 PG，SQLite 文件复制 + PRAGMA wal_checkpoint + sqlite3 连接测试不适用"
  )
  ```
- **依据文件**：docs/_working/p2_review_fix_guide.md 第五节

### 修复4：test_f18_redblue.py 添加3处TODO注释（1文件级+2类级）
- **文件**：tests/test_f18_redblue.py
- **行号**：L37-39（文件级新增）, L125（TestDBFailure类级新增）, L604（TestDataConsistency类级新增）
- **类别**：skip文件缺TODO注释
- **原代码**（文件级无TODO；类级以TestDBFailure为例）：
  ```python
  # P2迁移：patch("_DEPGRAPH_DB") 已失效——生产代码用 get_db_connection() 连 PG，不再读 _DEPGRAPH_DB 路径变量。
  @pytest.mark.skip(reason="P2迁移：patch(_DEPGRAPH_DB) 已失效，生产代码用 get_db_connection() 连 PG")
  class TestDBFailure:
  ```
- **新代码**：
  ```python
  # P2迁移：patch("_DEPGRAPH_DB") 已失效——生产代码用 get_db_connection() 连 PG，不再读 _DEPGRAPH_DB 路径变量。
  # TODO(P2-migration): 后续需将本测试类改造为 PG 适配版本（用 mock get_db_connection 或 PG 临时库替代 patch _DEPGRAPH_DB + sqlite3 临时库），当前 skip。
  @pytest.mark.skip(reason="P2迁移：patch(_DEPGRAPH_DB) 已失效，生产代码用 get_db_connection() 连 PG")
  class TestDBFailure:
  ```
- **文件级TODO**（L37-39，覆盖8处方法级skip）：
  ```python
  # TODO(P2-migration): 本文件中所有 patch(_DEPGRAPH_DB) + sqlite3 临时库的 skip 测试（含类级与方法级）
  # 均需后续改造为 PG 适配版本（用 mock get_db_connection 或 PG 临时库替代），当前 skip。
  # 详见各 skip 标记处的 TODO 注释。
  ```
- **依据文件**：docs/_working/p2_review_fix_guide.md 第五节

## 未修复问题（需主AI协调）

### 未修复项1：TODO注释无强制执行机制（原提示项3）
- **描述**：TODO注释是文档型修复，依赖人工/AI后续跟进，无门禁强制机制
- **不修复原因**：
  1. 调研发现项目 pyproject.toml 无skip监控配置，check_test_structure.py 只查"脚本伪装测试"不监控skip数量，conftest.py 无skip监控
  2. 修复需创建新CI监控脚本（违反"不得创建新文件"约束）
  3. 或扩展现有 check_test_structure.py 门禁（超出AI-10"只审查数据库相关测试文件"范围，影响全项目测试）
  4. 这是架构级决策，应由主AI协调而非AI-10单方面决定
- **建议**：主AI协调评估是否扩展 check_test_structure.py 添加skip数量监控，或新建CI门禁脚本

## 提示项修复记录（用户批准后修复）

### 提示项1（已修复）：test_depgraph_db.py 删除死代码 DB_PATH
- **文件**：tests/test_depgraph_db.py
- **原行号**：L14, L16
- **类别**：死代码变量（"向内收"原则要求删除）
- **调研过程**：Grep确认 `DB_PATH` 仅在L16定义，无其他引用；`REPO_ROOT` 仅在L14 import 和 L16 DB_PATH 定义中使用
- **原代码**：
  ```python
  from zephyr.governance.depgraph_schema import get_db_connection
  from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

  DB_PATH = str(REPO_ROOT / "data" / "databases" / "depgraph.db")
  ```
- **新代码**：
  ```python
  from zephyr.governance.depgraph_schema import get_db_connection
  ```
- **依据**：
  - "向内收-能用现成不创造"：删除未使用的死代码，减少冗余
  - DB_PATH 引用 depgraph.db SQLite 路径，P2迁移后此路径非真源，避免误导
  - 一并删除因此变成未使用的 REPO_ROOT import（GOVERNANCE_DB/MARKET_DB 在本文件不涉及）

### 提示项2（已修复）：test_db_auto_ops.py 删除死代码 DEPGRAPH_DB
- **文件**：tests/test_db_auto_ops.py
- **原行号**：L24
- **类别**：死代码变量（"向内收"原则要求删除）
- **调研过程**：Grep确认 `DEPGRAPH_DB` 仅在L24定义，无其他引用；depgraph访问均用 get_db_connection()
- **原代码**：
  ```python
  GOVERNANCE_DB = REPO_ROOT / "data" / "databases" / "governance.db"
  DEPGRAPH_DB = REPO_ROOT / "data" / "databases" / "depgraph.db"
  MARKET_DB = REPO_ROOT / "data" / "databases" / "market.duckdb"
  ```
- **新代码**：
  ```python
  GOVERNANCE_DB = REPO_ROOT / "data" / "databases" / "governance.db"
  MARKET_DB = REPO_ROOT / "data" / "databases" / "market.duckdb"
  ```
- **依据**：
  - "向内收-能用现成不创造"：删除未使用的死代码，减少冗余
  - DEPGRAPH_DB 引用 depgraph.db SQLite 路径，P2迁移后此路径非真源，避免误导
  - 保留 REPO_ROOT import（GOVERNANCE_DB/MARKET_DB 仍在使用）

## 确认无问题项
- ✅ 6个连接替换文件全部正确使用get_db_connection()
- ✅ 4个skip文件skip原因均合理（明确说明P2迁移后不适用PG的具体原因）
- ✅ 4个skip文件已全部补充TODO注释（共8处类级/模块级TODO + 1处文件级TODO）
- ✅ 非skip代码中无sqlite3.connect连depgraph
- ✅ 非skip代码中无sqlite_master查询depgraph
- ✅ 非skip代码中无?占位符用于depgraph
- ✅ 全部10个文件无MOD-INF-012B-P2/P3违规module_id
- ✅ governance.db用sqlite3是豁免（test_database_service.py:57/60, test_db_auto_ops.py:63/91/178/207）
- ✅ market.duckdb用duckdb是豁免（test_database_service.py:47, test_db_auto_ops.py:116）
- ✅ zalpha_metadata.db相关测试豁免（test_database_manager_unit.py, test_database_manager_db.py）

## 结论
- [x] 无问题，本分区审查通过（连续两次=0）
- [ ] 有残留问题，需主AI协调

## 最终修复总览（v1.1.0 更新）

| # | 文件 | 修复类型 | 状态 |
|---|------|---------|------|
| 1 | tests/test_depgraph_schema.py | 补TODO注释 | ✅ 已修复 |
| 2 | tests/test_verify_schema_health.py | 补4处TODO注释 | ✅ 已修复 |
| 3 | tests/unit/test_audit_rename_completeness.py | 补TODO注释 | ✅ 已修复 |
| 4 | tests/test_f18_redblue.py | 补3处TODO注释（1文件级+2类级） | ✅ 已修复 |
| 5 | tests/test_depgraph_db.py | 删除死代码DB_PATH+REPO_ROOT import | ✅ 已修复（用户批准后） |
| 6 | tests/test_db_auto_ops.py | 删除死代码DEPGRAPH_DB | ✅ 已修复（用户批准后） |

## 未修复项（需主AI协调）
| # | 描述 | 不修复原因 |
|---|------|-----------|
| 1 | TODO注释无强制执行机制 | 创建新CI脚本违反"不创建新文件"约束；扩展现有门禁超出AI-10范围，属架构级决策 |

## 大白话汇报（向内收审核结论）

### 我做了什么
给4个P2迁移skip测试文件添加了TODO注释（共8处类级/模块级TODO + 1处文件级TODO），指明后续PG适配改造方向。

### 这个功能的作用
让新AI阅读skip测试时立即知道"这些测试需要后续改造为PG版本，不是永久skip"，避免误删或误判。

### 达成了什么目标
满足用户"4个skip文件skip原因合理且有TODO注释"的重点检查要求，本分区审查连续两次=0通过。

### 解决了什么痛点
原4个skip文件只有skip reason没有TODO，新AI无法区分"永久skip"和"待改造skip"，可能误删测试或忽略改造需求。

### 功能通过什么触发自动启动
N/A（本次修复是文档注释，非功能脚本，无需触发）。

### 如何自动运行
N/A（文档注释无运行逻辑）。

### 如何自动关闭
N/A（文档注释无生命周期）。

### 向内收审核结果
- [x] 责任唯一真源唯一：通过（TODO引用现有get_db_connection()入口，未创造新真源）
- [x] 能用现成不创造：通过（仅编辑4个已有文件添加注释，未创建新文件）
- [x] 永久系统全自动：N/A（文档注释非永久性系统）
- [x] 第一性原理治本：通过（TODO指出了PG适配的治本方向，而非打补丁）
- [x] AI可发现性：通过（TODO使用标准`# TODO(P2-migration):`格式，紧邻skip标记，新AI阅读skip时立即可见）
- [x] 红蓝对抗：通过（无致命漏洞；提示项3记录了TODO无强制执行机制的固有限制）

### 红蓝极限对抗测试结果
- **红方攻击1**：新AI忽略TODO，直接删除skip测试 → **蓝方防御**：TODO明确说"后续需改造"，不是"删除"。但无强制机制。记录为提示项3。
- **红方攻击2**：新AI看到sqlite3 import误以为depgraph用SQLite → **蓝方防御**：skip reason明确说"P2迁移：...不适用 PG"，且TODO指出改造方向。防御成功。
- **红方攻击3**：新AI在非skip测试中添加sqlite3.connect(depgraph) → **蓝方防御**：无技术防御，依赖AI读AGENTS.md和修复指南。记录为提示项。
- **红方攻击4**：新AI重复造轮子，自己写新的PG连接函数 → **蓝方防御**：TODO明确指明用现有get_db_connection()，避免重复造轮子。防御成功。

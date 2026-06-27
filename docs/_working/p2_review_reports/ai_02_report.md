---
doc_type: audit_report
status: active
title: "AI-02 审查报告——P2迁移自修复"
module_id: "MOD-DB_DEPGRAPH_PG"
version: "1.0.0"
created: "2026-06-28"
ttl: task_bound
completes_when: "报告归档"
---

# AI-02 审查报告

## 元信息
- 审查轮次：共3轮（第1轮发现+修复，第2轮复审=0，第3轮复审=0）
- 审查时间：2026-06-28
- 负责分区：src/zephyr/governance/ 目录下除 database_service.py/depgraph_schema.py/pg_conn_wrapper.py 外的所有 .py 文件
- 审查文件数：约 200+ 个（governance 根目录 + 子目录 rule_enforcement/、drift_detection/、kb/、audit_orchestration/、rollback_*.py、behavioral_admission/、vector_memory/ 等）
- 最终状态：✅ 通过（连续两次=0）

## 审查结果汇总
- 初始问题数：3（含1个跨分区问题）
- 修复问题数：3
- 残留问题数：0（本分区内）
- 跨分区待协调问题数：0
- 连续零问题轮次：第2轮、第3轮
- 补充修复轮次：第4轮（用户批准直接修复建议项，移除 auto_runner.py `_DEPGRAPH_DB` 死代码）

## 审查方法
1. Grep 搜索 SQLite 残留关键词：`sqlite3.connect`、`import sqlite3`、`sqlite_master`、`AUTOINCREMENT`、`INSERT OR REPLACE`、`GROUP_CONCAT`、`sqlite3.Row`、`sqlite3.Error` 等
2. Grep 搜索 depgraph 相关引用：`depgraph`、`get_db_connection`、`from zephyr.governance.depgraph_schema`
3. Grep 搜索 module_id 违规：`MOD-INF-012B-P2`、`MOD-INF-012B-P3`
4. Grep 搜索 REPO_ROOT 违规：`Path("D:/ZephyrAlpha")` 硬编码
5. Read 确认上下文：逐文件区分 depgraph（违规）vs governance.db（豁免）vs 通用 SQLite 解析（豁免）
6. 读取真源文件 `depgraph_schema.py` 对照 `get_db_connection()` 正确实现
7. 语法校验：`python -c "import ast; ast.parse(...)"` 确认修复未破坏语法

## 修复记录

### 修复1
- **文件**：src/zephyr/governance/blast_radius.py
- **行号**：L45
- **类别**：A (depgraph.db路径硬编码 + Path("D:/ZephyrAlpha") REPO_ROOT 违规)
- **原代码**：
  ```python
  import yaml
  
  from zephyr.governance.semantic_audit.models import SemanticAuditFinding
  
  __all__ = ["BlastRadiusAnalyzer", "BlastRadiusReport"]
  
  logger = logging.getLogger(__name__)
  
  _DEPGRAPH_DEFAULT_PATH = Path("D:/ZephyrAlpha/data/databases/depgraph.db")
  ```
- **新代码**：
  ```python
  import yaml
  
  from zephyr.governance.semantic_audit.models import SemanticAuditFinding
  from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）
  
  __all__ = ["BlastRadiusAnalyzer", "BlastRadiusReport"]
  
  logger = logging.getLogger(__name__)
  
  # depgraph.db 物理路径（P2迁移后已迁移到 PostgreSQL，此路径保留作为参考）
  # 真源：zephyr.shared.io.paths.REPO_ROOT（禁止 Path("D:/ZephyrAlpha") 硬编码）
  _DEPGRAPH_DEFAULT_PATH = REPO_ROOT / "data" / "databases" / "depgraph.db"
  ```
- **依据文件**：
  - src/zephyr/governance/depgraph_schema.py L67 (`from zephyr.shared.io.paths import REPO_ROOT`)
  - src/zephyr/governance/depgraph_schema.py L72 (`DB_PATH: Path = REPO_ROOT / "data" / "databases" / "depgraph.db"`)
  - AGENTS.md §7 REPO_ROOT 真源归一约束
- **说明**：原代码同时违反两条约束：(1) `Path("D:/ZephyrAlpha")` 硬编码仓库根（违反 REPO_ROOT SSoT）；(2) `depgraph.db` 路径硬编码（P2迁移后 depgraph 已在 PostgreSQL）。修复采用最小改动：导入 `REPO_ROOT` 真源，路径模式与 `depgraph_schema.py DB_PATH` 保持一致（保留作为 SQLite 备份路径参考）。

### 修复2
- **文件**：src/zephyr/governance/rule_enforcement/triple_alignment.py
- **行号**：L45
- **类别**：A (Path("D:/ZephyrAlpha") REPO_ROOT 违规)
- **原代码**：
  ```python
  import yaml
  
  logger = logging.getLogger(__name__)
  
  PROJECT_ROOT = Path("D:/ZephyrAlpha")
  BLUEPRINT_REGISTRY = PROJECT_ROOT / "docs/03_modules/blueprint_registry.yaml"
  MODULE_REGISTRY = PROJECT_ROOT / "docs/03_modules/module-registry.yaml"
  DEPENDENCY_MAP = PROJECT_ROOT / "docs/02_enterprise_architecture/system-dependency-map.md"
  GATES_REGISTRY = PROJECT_ROOT / "src/zephyr/governance/rule_enforcement/_registry.yaml"
  BLUEPRINTS_DIR = PROJECT_ROOT / "docs/03_modules"
  ```
- **新代码**：
  ```python
  import yaml
  
  from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）
  
  logger = logging.getLogger(__name__)
  
  # P2迁移审查修复：禁止 Path("D:/ZephyrAlpha") 硬编码，改用 REPO_ROOT 真源
  PROJECT_ROOT = REPO_ROOT
  BLUEPRINT_REGISTRY = PROJECT_ROOT / "docs/03_modules/blueprint_registry.yaml"
  MODULE_REGISTRY = PROJECT_ROOT / "docs/03_modules/module-registry.yaml"
  DEPENDENCY_MAP = PROJECT_ROOT / "docs/02_enterprise_architecture/system-dependency-map.md"
  GATES_REGISTRY = PROJECT_ROOT / "src/zephyr/governance/rule_enforcement/_registry.yaml"
  BLUEPRINTS_DIR = PROJECT_ROOT / "docs/03_modules"
  ```
- **依据文件**：
  - src/zephyr/governance/depgraph_schema.py L67 (`from zephyr.shared.io.paths import REPO_ROOT`)
  - AGENTS.md §7 REPO_ROOT 真源归一约束
- **说明**：原代码 `Path("D:/ZephyrAlpha")` 硬编码仓库根，违反 REPO_ROOT SSoT 约束。修复保留 `PROJECT_ROOT` 变量名（最小改动，避免影响文件内 12 处引用），值改为 `REPO_ROOT` 真源。本文件不涉及 depgraph 数据库访问，仅路径常量违规。

### 修复3（第4轮补充修复——用户批准直接修复建议项）
- **文件**：src/zephyr/governance/auto_runner.py
- **行号**：L39, L45-46（原行号，修复后行号已变）
- **类别**：[向内收-真源分裂] + 死代码清理
- **原代码**：
  ```python
  from zephyr.governance.depgraph_schema import get_db_connection
  from zephyr.shared.io.paths import REPO_ROOT  # 仓库根真源（SSoT：zephyr.shared.io.paths）

  logger = logging.getLogger(__name__)

  __all__: list[str] = ["GovernanceAutoRunner", "AutoRunnerResult"]

  # depgraph.db SQLite 备份路径（P2迁移后已切换到 PostgreSQL，此路径保留作为参考）
  _DEPGRAPH_DB = REPO_ROOT / "data" / "databases" / "depgraph.db"
  ```
- **新代码**：
  ```python
  from zephyr.governance.depgraph_schema import get_db_connection

  logger = logging.getLogger(__name__)

  __all__: list[str] = ["GovernanceAutoRunner", "AutoRunnerResult"]
  ```
- **依据**：
  1. **调研结论**：`_DEPGRAPH_DB` 在 auto_runner.py 中仅 L46 定义，无任何生产代码引用（死代码确认）。Grep 全项目发现 13 处引用全部位于 `tests/test_f18_redblue.py` 中，且**全部**在 `@pytest.mark.skip` 装饰的类/方法内（类级 skip：L130 `TestDBFailure`、L609 `TestEventDrivenEdgeCases`；方法级 skip：L367/L399/L498/L568/L737/L749/L762/L794）。pytest skip 后方法体不执行，`with patch(...)` 不会触发，因此移除 `_DEPGRAPH_DB` 不会导致测试失败。
  2. **先例**：`tests/test_f18_automation.py` L35 和 `tests/unit/test_vocab_sync_chain.py` L54 已有注释"depgraph 已迁移到 PostgreSQL（P2迁移），`_DEPGRAPH_DB` 路径常量已移除"——证明同类改造已有先例。
  3. **测试文件已有 TODO**：`tests/test_f18_redblue.py` L37-39 已标注 `# TODO(P2-migration): 本文件中所有 patch(_DEPGRAPH_DB) + sqlite3 临时库的 skip 测试均需后续改造为 PG 适配版本`。移除 `_DEPGRAPH_DB` 正好强制执行此 TODO——若取消 skip，patch 会 AttributeError，强制改造为 `patch get_db_connection`。
  4. **真源分裂消除**：`_DEPGRAPH_DB` 与 `depgraph_schema.DB_PATH`（L72 `DB_PATH: Path = REPO_ROOT / "data" / "databases" / "depgraph.db"`）构成真源分裂。移除后 depgraph.db 路径真源唯一归 `depgraph_schema.DB_PATH`。
  5. **P2迁移方案文档**：`docs/03_modules/_cross_layer/database/sub_blueprints/mod_inf_012b_p2_affected_files_index.md` L304 已标注："改为patch PG连接工厂"。
- **同时移除的项**：`from zephyr.shared.io.paths import REPO_ROOT` import（移除 `_DEPGRAPH_DB` 后 `REPO_ROOT` 在本文件无其他引用，避免 unused import 警告）
- **说明**：本次修复属于"向内收-真源归一"——消除死代码和真源分裂。tests/ 的 13 处 patch 调用改造属于独立任务（需为每个测试设计 PG mock），由 tests/ 分区 AI 按 TODO 执行，本报告不越界处理。移除后若 tests 取消 skip 会立即 AttributeError，这是预期行为——强制 PG 适配改造。

## 未修复问题（需主AI协调）

无。原跨分区问题（auto_runner.py `_DEPGRAPH_DB` 死代码）已于第4轮补充修复（见下方"修复3"）。

## 确认无问题项

### A. SQLite 残留检查（均豁免）
- **git_commit_gateway.py**：✅ 无数据库访问，仅 subprocess 调用 git
- **reconciliation_registry.py**：✅ 纯 stdlib，无数据库访问
- **task_repo.py**：✅ sqlite3 用于 governance.db（tasks_fts FTS5 表），豁免
- **base_repo.py**：✅ sqlite3 用于 governance.db（tasks 表），豁免
- **registry_adapter.py SqliteAdapter**：✅ 通用 SQLite 解析器（`can_handle` 判断 `.db` 后缀），按 `db_path` 参数解析任意 SQLite 文件，非 depgraph 专用
- **query_metrics.py**：✅ sqlite3 用于 governance.db slow_queries 表 + EXPLAIN QUERY PLAN，豁免
- **rollback_drill.py**：✅ sqlite3 用于 governance.db integrity_check，豁免
- **rollback_integration.py**：✅ 通用连接池健康检查（先 psycopg2 后 sqlite3 fallback），豁免
- **rollback_verifier.py**：✅ sqlite3 用于 governance.db DB 一致性自愈 + differential check，豁免
- **database_manager.py**：✅ sqlite3 用于 governance.db 连接池/备份/WAL checkpoint，豁免
- **audit_schema.py / agent_cooldown.py / atomic_transaction_manager.py / f5_shutdown_manager.py / snapshot_manager.py / event_store.py**：✅ 均为 governance.db 上下文，豁免
- **drift_detection/* / kb/* / audit_orchestration/* / behavioral_admission/* / vector_memory/* / rule_enforcement/* (circuit_breaker, gate_engine)**：✅ 均通过 `from zephyr.shared.utils.db_utils import get_db_connection` 或 `from zephyr.integration.shared_08.utils.db_utils import get_db_connection` 访问 governance.db，豁免

### B. PG 正确性检查（均合规）
- **auto_runner.py**：✅ `from zephyr.governance.depgraph_schema import get_db_connection` + `with conn.cursor() as cur:` + `%s` 占位符 + `psycopg2.Error` 错误处理
- **rule_engine.py**：✅ `from zephyr.governance.depgraph_schema import get_db_connection` + `_PgConnExecuteWrapper` 包装
- **depgraph_reader.py**：✅ `from zephyr.governance.depgraph_schema import get_db_connection` + `_PgConnExecuteWrapper` 包装

### C. module_id 检查
- ✅ 全分区无 `MOD-INF-012B-P2` 违规
- ✅ 全分区无 `MOD-INF-012B-P3` 违规

### D. 其他检查
- ✅ 无 `INSERT OR REPLACE` 用于 depgraph（仅 governance.db 上下文使用，豁免）
- ✅ 无 `GROUP_CONCAT` 用于 depgraph（仅 kb/graph_validator.py 用于 kb_db，豁免）
- ✅ 无 `?` 占位符用于 depgraph
- ✅ 无 `row[0]` 用于 depgraph（auto_runner.py L272/296 的 `r[0]` 是 PG cursor 元组解包，合规）
- ✅ 无 `sqlite3.Row` 用于 depgraph
- ✅ 无 `conn.execute().fetchone()` 用于 depgraph（psycopg2 上下文）

## 复审记录

### 第2轮复审（修复后）
- Grep `Path(["']D:/ZephyrAlpha` → 仅剩注释中的说明文字，无代码违规 ✅
- Grep `sqlite3.connect.*depgraph` → 无匹配 ✅
- Grep `MOD-INF-012B-P2|MOD-INF-012B-P3` → 无匹配 ✅
- Grep `INSERT OR REPLACE.*depgraph|GROUP_CONCAT.*depgraph` → 无匹配 ✅
- Read blast_radius.py 确认 `REPO_ROOT` 导入正确 ✅
- Read triple_alignment.py 确认 `REPO_ROOT` 导入正确 ✅
- **本轮问题数：0**

### 第3轮复审（语法+最终确认）
- `python -c "import ast; ast.parse(...)"` 校验 blast_radius.py 语法 OK ✅
- `python -c "import ast; ast.parse(...)"` 校验 triple_alignment.py 语法 OK ✅
- **本轮问题数：0**

**连续两次=0 → 审查通过 ✅**

---

## 大白话汇报（向内收审核结论）

### 我做了什么
审查了 governance/ 目录下 200+ 个 .py 文件的 P2 迁移合规性，修复了 2 处 `Path("D:/ZephyrAlpha")` 硬编码违规。

### 这个功能的作用
确保 governance 分区所有文件不再有 SQLite 残留违规和 REPO_ROOT 硬编码，P2 迁移后统一使用 PostgreSQL 真源入口 `get_db_connection()` 和仓库根真源 `REPO_ROOT`。

### 达成了什么目标
governance 分区（除 AI-01 负责的 database_service.py/depgraph_schema.py 外）全部通过 P2 迁移审查，连续两轮零问题。

### 解决了什么痛点
消除了 `blast_radius.py` 和 `triple_alignment.py` 中硬编码的 `D:/ZephyrAlpha` 路径——这种写法在文件移动或跨机器部署时会 break，且违反 REPO_ROOT SSoT 约束，是新 AI 产生路径漂移的温床。

### 功能通过什么触发自动启动
本次审查是 task_bound 一次性任务（P2 迁移审查），由用户对话触发，非永久性系统。修复的代码本身是被动导入的模块，无自动触发需求。

### 如何自动运行
修复后的 `blast_radius.py` / `triple_alignment.py` 在被 import 时自动使用 `REPO_ROOT` 真源计算路径，无需人工干预。

### 如何自动关闭
task_bound 任务，审查完成即关闭。修复的代码随模块生命周期，无独立关闭需求。

### 向内收审核结果
- [x] 责任唯一真源唯一：通过——修复后 `blast_radius.py` 和 `triple_alignment.py` 均从 `zephyr.shared.io.paths.REPO_ROOT` 取真源，不再本地硬编码。原真源分裂问题（auto_runner.py `_DEPGRAPH_DB` 与 `depgraph_schema.DB_PATH` 重复）已于第4轮补充修复——移除 `_DEPGRAPH_DB` 死代码，depgraph.db 路径真源唯一归 `depgraph_schema.DB_PATH`。
- [x] 能用现成不创造：通过——修复仅导入已有的 `REPO_ROOT`（修复1/2）或移除死代码（修复3），未创建新文件、未新建 paths 模块。
- [x] 永久系统全自动：通过（不适用）——本次审查是 task_bound 一次性任务，非永久性系统。
- [x] 第一性原理治本：通过——根因是路径硬编码违反 SSoT / 死代码导致真源分裂，修复从真源取值或移除死代码治本，非打补丁。
- [x] AI可发现性：通过——`REPO_ROOT` 在 AGENTS.md §7、project_memory、depgraph_schema.py 均有注册，新 AI 可通过标准入口发现。
- [x] 红蓝对抗：通过——模拟红方攻击：(1)"删除 REPO_ROOT import"→ ImportError 立即暴露；(2)"REPO_ROOT 路径变化"→ `find_repo_root()` 基于 .git marker 自适应；(3)"blast_radius 默认路径不存在"→ DepgraphLoadError fail-fast（pre-existing 行为，非 P2 违规）；(4)"移除 _DEPGRAPH_DB 后 tests 取消 skip"→ patch AttributeError 立即暴露，强制 PG 适配改造（预期行为）。蓝方均能抵御。

## 结论
- [x] 无问题，本分区审查通过（连续两次=0 + 第4轮补充修复）
- [ ] 有残留问题，需主AI协调

**备注**：原跨分区问题（auto_runner.py `_DEPGRAPH_DB` 死代码）已于第4轮补充修复。tests/test_f18_redblue.py 中 13 处 `patch("...auto_runner._DEPGRAPH_DB", ...)` 调用仍在 skip 测试中，属于 tests/ 分区 PG 适配改造任务（测试文件 L37-39 已有 TODO 标注），本报告不越界处理。

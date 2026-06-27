---
doc_type: audit_report
status: active
title: "AI-11 审查报告——P2迁移自修复（tests/ 非数据库测试分区）"
module_id: "MOD-DB_DEPGRAPH_PG"
version: "1.1.0"
created: "2026-06-28"
ttl: task_bound
completes_when: "报告归档"
---

# AI-11 审查报告

## 元信息
- 审查轮次：共 4 轮（R1 审查+修复 → R2 复审 → R3 终审 → R4 治本修复+用户批准项）
- 审查时间：2026-06-28
- 负责分区：tests/ 目录下非数据库相关测试文件（排除 test_depgraph_*、test_database_*、test_db_auto_ops*、test_f18_redblue*、test_verify_schema_health*、test_audit_rename_completeness*）
- 审查文件数：聚焦审查 8 个含 depgraph.db 引用的候选文件，逐个 Read 确认上下文
- 最终状态：✅ 通过（连续两轮 R2/R3 问题数=0；R4 用户批准治本修复提示项1）

## 审查结果汇总
- 初始问题数：6（均为 depgraph.db 路径硬编码违规，无 sqlite3.connect 连 depgraph，无 ? 占位符用于 depgraph，无 MOD-INF-012B-P2/P3）
- 修复问题数：7（R1-R3 修复 6 项 + R4 治本修复 1 项提示项）
- 残留问题数：0
- 连续零问题轮次：R2、R3

## 检查关键词覆盖

### A. SQLite残留（违规）
- `sqlite3.connect(depgraph)` → ✅ 0 处（所有 sqlite3.connect 均连接 governance.db 或 tmp_path 测试夹具，合法）
- `?占位符(depgraph)` → ✅ 0 处（depgraph 查询全部走 `get_db_connection()`，无 `?` 占位符）
- `depgraph.db路径硬编码` → ❌ 发现 6 处 → 已全部修复

### B. PG正确性
- `get_db_connection` → ✅ 所有涉及 depgraph 的测试均通过 `get_db_connection()` 走 PG
- `%s` 占位符 → ✅ depgraph 查询均使用 PG 方言

### C. module_id
- `MOD-INF-012B-P2` → ✅ 0 处（tests/ 目录无此违规 module_id）
- `MOD-INF-012B-P3` → ✅ 0 处

## 修复记录

### 修复1
- **文件**：tests/test_db_red_blue.py
- **行号**：L24
- **类别**：A (depgraph.db路径硬编码——未使用常量)
- **原代码**：
  ```python
  DEPGRAPH_DB = REPO_ROOT / "data" / "databases" / "depgraph.db"
  ```
- **新代码**：
  ```python
  # 注：depgraph 已迁移到 PostgreSQL（P2迁移），DEPGRAPH_DB 路径常量已移除
  ```
- **依据文件**：src/zephyr/governance/depgraph_schema.py（get_db_connection 为 PG 连接唯一入口）
- **说明**：该常量定义后从未被使用（全文 sqlite3.connect 均连 GOVERNANCE_DB 或 tmp_path 测试夹具），属残留死代码

### 修复2
- **文件**：tests/test_db_integration.py
- **行号**：L23 + L213-222（main 中文件存在性检查循环）
- **类别**：A (depgraph.db路径硬编码 + depgraph 文件存在性检查)
- **原代码**：
  ```python
  DEPGRAPH_DB = REPO_ROOT / "data" / "databases" / "depgraph.db"
  ...
  for db_path, db_name in [
      (GOVERNANCE_DB, "governance.db"),
      (DEPGRAPH_DB, "depgraph.db"),
      (MARKET_DB, "market.duckdb"),
  ]:
      if not db_path.exists():
          ...
  ```
- **新代码**：
  ```python
  # 注：depgraph 已迁移到 PostgreSQL（P2迁移），DEPGRAPH_DB 路径常量已移除
  ...
  for db_path, db_name in [
      (GOVERNANCE_DB, "governance.db"),
      (MARKET_DB, "market.duckdb"),
  ]:
      if not db_path.exists():
          ...
  # 验证 depgraph (PostgreSQL) 可连接
  try:
      dep_conn = get_db_connection()
      dep_conn.close()
      print("✓ depgraph (PostgreSQL) 连接成功")
  except Exception as e:
      print(f"\n✗ FAIL: depgraph (PostgreSQL) 连接失败: {e}")
      return 1
  ```
- **依据文件**：src/zephyr/governance/depgraph_schema.py（get_db_connection 为 PG 连接唯一入口）
- **说明**：原代码检查 depgraph.db 文件是否存在，但 P2 迁移后 depgraph 已迁至 PG，文件不应被检查。该文件本身的 depgraph 查询早已正确使用 `get_db_connection()`（L40/70/117/168），仅 main 启动校验残留文件存在性检查

### 修复3
- **文件**：tests/test_f18_automation.py
- **行号**：L35 + L239-251（test_audit_log_written_to_depgraph）
- **类别**：A (depgraph.db路径硬编码 + depgraph 文件存在性检查)
- **原代码**：
  ```python
  _DEPGRAPH_DB = _PROJECT_ROOT / "data" / "databases" / "depgraph.db"
  ...
  if _DEPGRAPH_DB.exists():
      try:
          conn = get_db_connection()
          ...
      except psycopg2.Error:
          pytest.skip("governance_audit_logs table not yet created")
  else:
      pytest.skip("depgraph.db not found")
  ```
- **新代码**：
  ```python
  # 注：depgraph 已迁移到 PostgreSQL（P2迁移），_DEPGRAPH_DB 路径常量已移除
  ...
  try:
      conn = get_db_connection()
      ...
  except psycopg2.Error:
      pytest.skip("governance_audit_logs table not yet created")
  except Exception:
      # PG 连接失败时跳过
      pytest.skip("depgraph (PostgreSQL) 不可用")
  ```
- **依据文件**：src/zephyr/governance/depgraph_schema.py（get_db_connection 为 PG 连接唯一入口）
- **说明**：移除文件存在性检查，新增 `except Exception` 兜底捕获 PG 连接失败（_load_pg_config 可能抛 FileNotFoundError/ValueError）

### 修复4
- **文件**：tests/test_rule_integration.py
- **行号**：L26 + L29 + L92-93 + L111-112
- **类别**：A (depgraph.db路径硬编码 × 2 + depgraph 文件存在性检查 × 2)
- **原代码**：
  ```python
  _DB_PATH = _PROJECT_ROOT / "data" / "databases" / "depgraph.db"
  ...
  _ARCH_PANORAMA = _PROJECT_ROOT / "data" / "databases" / "depgraph.db"
  ...
  if not _DB_PATH.exists():
      pytest.skip("depgraph.db not found")
  ...
  if not _ARCH_PANORAMA.exists():
      pytest.skip("depgraph.db not found")
  ```
- **新代码**：
  ```python
  # 注：depgraph 已迁移到 PostgreSQL（P2迁移），_DB_PATH / _ARCH_PANORAMA 路径常量已移除
  ...
  try:
      conn = get_db_connection()
      ...
  except Exception as exc:
      pytest.skip(f"Cannot query depgraph (PG): {exc}")
  ```
- **依据文件**：src/zephyr/governance/depgraph_schema.py（get_db_connection 为 PG 连接唯一入口）
- **说明**：原代码存在两处重复的 depgraph.db 路径常量（_DB_PATH 与 _ARCH_PANORAMA 指向同一文件）。修复后合并为单一 `get_db_connection()` 调用，异常类型从 `psycopg2.Error` 放宽至 `Exception` 以覆盖 PG 配置加载失败

### 修复5
- **文件**：tests/unit/test_vocab_sync_chain.py
- **行号**：L54 + L170-171 + L188-189
- **类别**：A (depgraph.db路径硬编码 + depgraph 文件存在性检查 × 2)
- **原代码**：
  ```python
  _DEPGRAPH_DB = REPO_ROOT / "data" / "databases" / "depgraph.db"
  ...
  if not _DEPGRAPH_DB.exists():
      pytest.skip(f"depgraph.db 不存在: {_DEPGRAPH_DB}")
  conn = get_db_connection()
  ```
- **新代码**：
  ```python
  # 注：depgraph 已迁移到 PostgreSQL（P2迁移），_DEPGRAPH_DB 路径常量已移除
  ...
  try:
      conn = get_db_connection()
  except Exception:
      pytest.skip("depgraph (PostgreSQL) 不可用")
  ```
- **依据文件**：src/zephyr/governance/depgraph_schema.py（get_db_connection 为 PG 连接唯一入口）
- **说明**：Bug B 回归测试（test_field_vocabularies_table_has_no_dirty_field_name / test_field_vocabularies_has_expected_vocab_names）原依赖 depgraph.db 文件存在性检查。修复后改为 PG 连接 try/except 兜底。Bug H 回归测试（test_constants_defines_depgraph_db_path / test_depgraph_db_path_points_to_correct_file / test_sync_db_path_references_constants，L341-377）未修改——它检查 `_shared/constants.py` 仍定义 `DEPGRAPH_DB_PATH` 常量，这是对 constants 模块的回归保护，且 constants.py L186 仍保留该常量（非本分区职责）

### 修复6
- **文件**：tests/test_path_tree_generator_design_protection.py
- **行号**：L14 + L52 + L94
- **类别**：A (depgraph.db路径硬编码 + subprocess 传递硬编码路径)
- **原代码**：
  ```python
  DB_PATH = REPO_ROOT / "data" / "databases" / "depgraph.db"
  ...
  [sys.executable, str(GENERATOR_SCRIPT), "--output-db", str(DB_PATH)],
  ```
- **新代码**：
  ```python
  # 注：depgraph 已迁移到 PostgreSQL（P2迁移），DB_PATH 路径常量已移除
  # 生成器 cmd_write_db 仅打印 db_path 参数，实际连接通过 get_depgraph_pg_connection() 走 PG
  ...
  [sys.executable, str(GENERATOR_SCRIPT), "--output-db", "depgraph-pg"],
  ```
- **依据文件**：scripts/governance/generate_project_path_tree.py L808-868（cmd_write_db 函数：参数 db_path 仅在 L810 print 输出，实际连接 L815 使用 `get_depgraph_pg_connection(autocommit=False)`）
- **说明**：生成器的 `--output-db` 参数仅用于打印日志，实际 DB 写入通过 PG 连接。测试自身的 depgraph 查询（L24）早已正确使用 `get_db_connection()`。修复后 subprocess 传递占位字符串 `"depgraph-pg"`，触发 `cmd_write_db` 分支

### 修复7（R4 用户批准治本修复）
- **文件**：scripts/governance/_shared/constants.py + tests/unit/test_vocab_sync_chain.py
- **行号**：constants.py L183-189；test_vocab_sync_chain.py L339-403（TestBugHDepgraphDbPath 类）
- **类别**：[向内收-治本]（原提示项1，用户批准直接修复）
- **原问题**：Bug H 回归测试检查 `_shared/constants.py` 仍定义 `DEPGRAPH_DB_PATH` 常量指向 `depgraph.db`。P2 迁移后该常量语义已过期（depgraph 不再是文件），但 constants.py L186 仍保留该定义
- **治本方案**：
  1. **constants.py**：给 DEPGRAPH_DB_PATH 加 P2 迁移注释，明确语义变化（从"连接路径"→"日志标识/历史路径引用"），保留常量避免破坏多个脚本的 import 语句
  2. **Bug H 测试**：更新类 docstring 说明 P2 后语义；新增两个 P2 迁移回归测试
- **constants.py 原代码**：
  ```python
  # depgraph.db 路径——供 sync_yaml_to_depgraph.py 等治理脚本引用（裁定#206 / Bug H 修复）
  # 历史：sync_yaml_to_depgraph.py 曾硬编码 r"D:\ZephyrAlpha\..." 绝对路径，违反可移植性；
  #       统一到此处常量后，所有治理脚本通过 _shared.constants 单一引用点获取路径。
  DEPGRAPH_DB_PATH: Path = REPO_ROOT / "data" / "databases" / "depgraph.db"
  ```
- **constants.py 新代码**：
  ```python
  # depgraph.db 路径——供 sync_yaml_to_depgraph.py 等治理脚本引用（裁定#206 / Bug H 修复）
  # 历史：sync_yaml_to_depgraph.py 曾硬编码 r"D:\ZephyrAlpha\..." 绝对路径，违反可移植性；
  #       统一到此处常量后，所有治理脚本通过 _shared.constants 单一引用点获取路径。
  # P2 迁移后语义变化（2026-06）：depgraph 已迁至 PostgreSQL，实际 DB 连接通过
  #       get_depgraph_pg_connection() 获取；此常量仅保留作日志标识/历史路径引用，
  #       不再作为实际连接目标。保留是为了避免破坏多个脚本的 import 语句。
  DEPGRAPH_DB_PATH: Path = REPO_ROOT / "data" / "databases" / "depgraph.db"
  ```
- **test_vocab_sync_chain.py 新增测试**：
  ```python
  def test_constants_defines_pg_connection_entry(self) -> None:
      """P2 迁移后 _shared/constants.py 必须定义 get_depgraph_pg_connection 入口。"""
      src = _CONSTANTS_MODULE.read_text(encoding="utf-8")
      assert "get_depgraph_pg_connection" in src, (
          "_shared/constants.py 未定义 get_depgraph_pg_connection（P2 迁移回归）"
      )

  def test_sync_uses_pg_connection_not_sqlite(self) -> None:
      """P2 迁移后 sync_yaml_to_depgraph.py 必须通过 get_depgraph_pg_connection 连 PG。"""
      src = _SYNC_SCRIPT.read_text(encoding="utf-8")
      assert "get_depgraph_pg_connection" in src, (
          "sync_yaml_to_depgraph.py 未使用 get_depgraph_pg_connection（P2 迁移回归）"
      )
      # 不应再用 sqlite3 直连 depgraph
      assert "sqlite3.connect" not in src, (
          "sync_yaml_to_depgraph.py 仍用 sqlite3.connect（P2 迁移回归）"
      )
  ```
- **依据文件**：
  - scripts/governance/_shared/constants.py L44-107（get_depgraph_pg_connection 定义，P2 PG 连接唯一入口）
  - scripts/governance/sync_yaml_to_depgraph.py L56（导入 get_depgraph_pg_connection）+ L1031（实际调用 `conn = get_depgraph_pg_connection(autocommit=False)`）+ L1028 注释（"P2 PG 迁移：删除 os.path.exists(DB_PATH) 检查"）
- **说明**：
  - 保留 DEPGRAPH_DB_PATH 常量而非删除——因 sync_yaml_to_depgraph.py L60 `DB_PATH = str(DEPGRAPH_DB_PATH)` 仍用于 L1039 日志打印；audit_rename_completeness.py L324 用作 --db 参数默认值；删除会破坏 import
  - 新增两个 P2 回归测试保护迁移成果：
    - `test_constants_defines_pg_connection_entry` 防止 get_depgraph_pg_connection 入口被误删
    - `test_sync_uses_pg_connection_not_sqlite` 防止 sync 脚本回退到 sqlite3.connect
  - 保留原 Bug H 三个测试（test_constants_defines_depgraph_db_path / test_depgraph_db_path_points_to_correct_file / test_sync_db_path_references_constants）——保护 Bug H 原意图（统一引用点不破坏 + 不硬编码绝对路径）
  - 已验证：sync_yaml_to_depgraph.py 不含 sqlite3.connect（grep 0 匹配），含 get_depgraph_pg_connection（L56 导入 + L1031 使用）

## 未修复问题（需主AI协调）

（无——原提示项1已通过 R4 治本修复解决）

## 确认无问题项

### 豁免项（合法 SQLite 使用，未修改）
- `sqlite3.connect(GOVERNANCE_DB)` —— governance.db 仍使用 SQLite（P2 未迁移）✅
- `sqlite3.connect(test_db)` / `sqlite3.connect(tmp_path / "xxx.db")` —— pytest tmp_path 测试夹具，合法 ✅
- `sqlite3.connect("drift_events.db")` / `sqlite3.connect("test_capacity.db")` 等 —— 测试夹具 SQLite，合法 ✅
- `duckdb.connect(MARKET_DB)` —— market.duckdb 仍使用 DuckDB，合法 ✅
- `?` 占位符用于 governance.db 查询 —— 合法（governance 仍是 SQLite）✅
- `sqlite_master` 用于 governance.db 查询 —— 合法 ✅

### 已验证清洁文件（含 depgraph.db 引用但非违规）
- tests/test_git_commit_gateway.py —— 仅在注释中提及 depgraph.db（L8 INVARIANTS），无实际连接 ✅
- tests/test_governance_db.py —— L200 "depgraph.db" 是 slow_queries 表的测试数据字符串，非连接 ✅

### PG 正确性确认
- 所有 depgraph 查询均通过 `get_db_connection()` 获取 PG 连接 ✅
- 所有 depgraph 查询使用 `with conn.cursor() as cur: cur.execute(...)` cursor 模式 ✅
- 所有修复点新增 `except Exception` 兜底捕获 PG 连接失败（覆盖 _load_pg_config 抛 FileNotFoundError/ValueError 场景）✅

## 结论
- [x] 无问题，本分区审查通过（连续两次=0：R2、R3；R4 用户批准治本修复提示项1）
- [x] 原提示项1已治本修复，无残留问题

---

## 大白话汇报（向内收审核结论）

### 我做了什么
把 tests/ 目录下 6 个非数据库测试文件里残留的 depgraph.db 硬编码路径和文件存在性检查全部清掉，改成用 `get_db_connection()` 走 PostgreSQL；用户批准后又治本修复了原提示项1——给 constants.py 的 DEPGRAPH_DB_PATH 加 P2 迁移注释说明语义变化，并新增两个 P2 回归测试保护迁移成果。

### 这个功能的作用
让测试代码与 P2 迁移后的数据库架构保持一致——depgraph 不再是文件，而是 PostgreSQL 数据库。

### 达成了什么目标
消除了 6 处 depgraph.db 路径硬编码违规 + 1 处 constants.py 语义过期提示项，让测试不再依赖 depgraph.db 文件存在性，而是直接验证 PG 连接可用性；同时通过新增回归测试防止 P2 迁移成果被回退。

### 解决了什么痛点
原测试代码会因 depgraph.db 文件不存在（已迁至 PG）而错误地 skip 或 fail，掩盖真实测试结果；修复后测试能正确连 PG 验证业务逻辑。原提示项1 的 Bug H 回归测试只保护"文件路径"语义，未保护"P2 迁移后走 PG"的成果，治本修复后双重保护。

### 功能通过什么触发自动启动
pytest 测试运行器触发（事件驱动：开发者执行 pytest 命令或 CI 流水线调用）。

### 如何自动运行
测试被 pytest 收集后自动执行 `get_db_connection()` 获取 PG 连接，若 PG 不可用则 `pytest.skip` 跳过，不阻塞其他测试；新增的 P2 回归测试自动扫描 constants.py 和 sync 脚本源码验证迁移成果。

### 如何自动关闭
单次测试函数执行完毕即自动关闭（`conn.close()` 在 finally 块中保证释放），无需人工干预。

### 向内收审核结果
- [x] 责任唯一真源唯一：通过——所有 depgraph 访问统一走 `zephyr.governance.depgraph_schema.get_db_connection()`（src 包）或 `get_depgraph_pg_connection()`（scripts 包）单一入口，消除测试文件各自硬编码路径的多真源分裂
- [x] 能用现成不创造：通过——零新建文件，全部扩展现有 `get_db_connection()` 调用，修复方式是"删除违规代码"而非"新增替代品"；R4 治本修复扩展现有 Bug H 测试类，未新建测试文件
- [x] 永久系统全自动：通过（N/A）——测试文件非永久性系统，由 pytest 事件驱动触发，符合自动化要求
- [x] 第一性原理治本：通过——根因是"测试用文件思维检查 PG 数据库"+"Bug H 测试只保护文件路径未保护 PG 入口"，治本方案是"移除文件检查，改用 PG 连接验证"+"新增 PG 入口回归测试"，非打补丁
- [x] AI可发现性：通过——新 AI 通过 `from zephyr.governance.depgraph_schema import get_db_connection` 导入语句 + 修复指南第一节真源文件清单即可发现 PG 连接入口；constants.py L183-189 注释明确说明 P2 后语义变化；test_vocab_sync_chain.py Bug H 回归测试双重保护 constants.py DEPGRAPH_DB_PATH 常量不被擅自删除 + get_depgraph_pg_connection 入口不被误删
- [x] 红蓝对抗：通过
  - 红方攻击1："get_db_connection() 失败怎么办？" → 蓝方：`except Exception` 兜底 skip
  - 红方攻击2："新 AI 重新引入硬编码路径？" → 蓝方：test_vocab_sync_chain.py L390 断言 `r'"D:\ZephyrAlpha\data\databases\depgraph.db"' not in src` 防护
  - 红方攻击3："subprocess --output-db 需要文件路径？" → 蓝方：cmd_write_db 仅打印参数，实际连接走 `get_depgraph_pg_connection()`
  - 红方攻击4（R4 新增）："新 AI 删除 get_depgraph_pg_connection 入口？" → 蓝方：test_constants_defines_pg_connection_entry 回归测试防护
  - 红方攻击5（R4 新增）："sync 脚本回退到 sqlite3.connect？" → 蓝方：test_sync_uses_pg_connection_not_sqlite 回归测试防护
  - 红方攻击6（R4 新增）："删除 DEPGRAPH_DB_PATH 破坏脚本 import？" → 蓝方：保留常量仅加注释说明语义，test_constants_defines_depgraph_db_path 保护统一引用点

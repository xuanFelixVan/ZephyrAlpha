---
doc_type: audit_report
status: active
title: "AI-06 审查报告——P2迁移自修复"
module_id: "MOD-DB_DEPGRAPH_PG"
version: "2.0.0"
created: "2026-06-28"
ttl: task_bound
completes_when: "报告归档"
---

# AI-06 审查报告

## 元信息
- 审查轮次：共3轮（Round 1 初审 + Round 2 复审 + Round 3 主AI授权后修复提示项并复审）
- 审查时间：2026-06-28
- 负责分区：scripts/governance/d3_metadata/ 目录下所有 .py 文件
- 审查文件数：17（含 `__init__.py`）
- 最终状态：✅ 通过（P2 范围连续两轮=0；提示项经主AI授权后已修复并验证）

## 审查文件清单

| # | 文件 | 说明 |
|---|------|------|
| 1 | `__init__.py` | 包入口，导出审计函数清单 |
| 2 | `backfill_doctype_metadata.py` | 回填 doc_type 元数据 |
| 3 | `backfill_ttl_metadata.py` | 回填 ttl 元数据 |
| 4 | `check_frontmatter_metadata.py` | frontmatter 元数据校验 |
| 5 | `check_naming_convention.py` | 命名规范一致性校验 |
| 6 | `check_registry_consistency.py` | 登记表/索引一致性校验 |
| 7 | `check_vocab_hardcode.py` | 词表硬编码检测 |
| 8 | `classify_ttl_by_content.py` | 按内容分类 ttl |
| 9 | `deep_content_scanner.py` | 深度内容扫描 |
| 10 | `generate_derived_files.py` | 生成派生文件 |
| 11 | `generate_rule_catalog.py` | 生成规则目录 |
| 12 | `migrate_illegal_doctype.py` | 迁移非法 doc_type |
| 13 | `validate_architecture.py` | 架构校验 |
| 14 | `validate_blueprint_provenance.py` | blueprint 溯源校验 |
| 15 | `validate_module_id.py` | module_id 校验 |
| 16 | `validate_registry_master_index.py` | 登记表主索引校验 |
| 17 | `validate_rule_frontmatter.py` | 规则 frontmatter 校验 |

## 审查结果汇总
- 初始问题数（Round 1，P2 范围 A/B/C）：0
- 提示项数（Round 1，非 P2 范围）：2（REPO_ROOT 真源分裂 + 修复指南引用幽灵文件）
- 主AI授权后修复提示项数：2（共 6 处代码修改 + 1 处文档修改）
- 残留问题数：0
- 连续零问题轮次：第1轮、第2轮（P2 范围）；第3轮（P2 + REPO_ROOT 全范围）

## 分区性质判定

本分区为**纯文件扫描/元数据审计套件**，无任何数据库访问：

- **导入清单统计**（17 文件全量扫描）：`argparse` / `re` / `sys` / `pathlib.Path` / `yaml` / `csv` / `json` / `os` / `ast` / `datetime` / `collections` / `_shared.*`（constants / encoding / frontmatter / walk / yaml_utils）
- **无** `sqlite3` / `psycopg2` / `duckdb` 导入
- **无** `database_service` / `depgraph_schema` 模块导入
- **无** `connect()` / `cursor()` / `execute()` / `fetchone()` / `fetchall()` 调用
- **无** SQL 语句（`INSERT INTO` / `SELECT FROM` / `UPDATE SET` / `DELETE FROM`）
- **无** `?` 或 `%s` 占位符
- **无** `row[0]` / `RealDictCursor` / `sqlite3.Row` 行访问

→ 该分区不访问任何数据库（governance.db / depgraph / market.duckdb 均不访问），仅扫描 .md/.yaml/.py 文件内容做元数据合规审计。P2 迁移对此分区无影响。

## 修复记录

### 修复1：validate_rule_frontmatter.py — REPO_ROOT 改用 canonical 导入
- **文件**：[validate_rule_frontmatter.py](file:///D:/ZephyrAlpha/scripts/governance/d3_metadata/validate_rule_frontmatter.py)
- **原行号**：L78
- **类别**：REPO_ROOT 真源分裂（`[向内收-真源分裂]`）
- **原代码**：
  ```python
  from _shared.constants import EXIT_FINDINGS, EXIT_PASS, GOV_DOCS_DIR
  ...
  REPO_ROOT = Path(__file__).resolve().parents[3]
  RULES_DIR = REPO_ROOT / "docs" / "01_policies_and_standards" / "rules"
  ```
- **新代码**：
  ```python
  from _shared.constants import EXIT_FINDINGS, EXIT_PASS, GOV_DOCS_DIR, REPO_ROOT
  ...
  RULES_DIR = REPO_ROOT / "docs" / "01_policies_and_standards" / "rules"
  ```
- **依据文件**：`scripts/governance/_shared/constants.py` L42（`from zephyr.shared.io.paths import REPO_ROOT` re-export）+ `src/zephyr/shared/io/paths.py` L61（`REPO_ROOT: Path = find_repo_root()` 真源）

### 修复2：validate_blueprint_provenance.py — 删除重复 bootstrap + 修复 parents[2] BUG
- **文件**：[validate_blueprint_provenance.py](file:///D:/ZephyrAlpha/scripts/governance/d3_metadata/validate_blueprint_provenance.py)
- **原行号**：L34, L47-L52, L60-L62, L96
- **类别**：REPO_ROOT 真源分裂 + 潜在 BUG（`[向内收-真源分裂]` + `[向内收-未治本]`）
- **原代码**：
  ```python
  from _shared.constants import EXIT_FINDINGS, EXIT_PASS
  ...
  import sys
  from pathlib import Path

  _PROJ = Path(__file__).resolve().parents[2]   # BUG: parents[2]=scripts/ 而非项目根
  if str(_PROJ) not in sys.path:
      sys.path.insert(0, str(_PROJ))
  ...
  scan_dirs = [
      _PROJ / "docs" / "02_enterprise_architecture" / "target-architecture",  # 指向 scripts/docs/ 不存在
      ...
  ]
  rel = fpath.relative_to(_PROJ)
  ```
- **新代码**：
  ```python
  from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
  ...
  # 重复 import sys / from pathlib import Path / _PROJ bootstrap 全部删除
  # （_shared.constants 导入时已做 canonical bootstrap，见 _shared/constants.py L36-38）
  ...
  scan_dirs = [
      REPO_ROOT / "docs" / "02_enterprise_architecture" / "target-architecture",
      ...
  ]
  rel = fpath.relative_to(REPO_ROOT)
  ```
- **依据文件**：`scripts/governance/_shared/constants.py` L36-42（canonical bootstrap + re-export）
- **附带修复**：`parents[2]` 是 `scripts/` 目录而非项目根，导致 validator 此前扫描 `scripts/docs/`（不存在）→ 静默 no-op。改用 REPO_ROOT 后 validator 恢复实际扫描能力。

### 修复3：validate_architecture.py — 删除重复 bootstrap + 修复 parents[2] BUG
- **文件**：[validate_architecture.py](file:///D:/ZephyrAlpha/scripts/governance/d3_metadata/validate_architecture.py)
- **原行号**：L36, L50-L55, L63, L74, L100
- **类别**：REPO_ROOT 真源分裂 + 潜在 BUG（`[向内收-真源分裂]` + `[向内收-未治本]`）
- **原代码**：
  ```python
  from _shared.constants import EXIT_FINDINGS, EXIT_PASS
  ...
  import sys
  from pathlib import Path

  _PROJ = Path(__file__).resolve().parents[2]   # BUG: 同修复2
  if str(_PROJ) not in sys.path:
      sys.path.insert(0, str(_PROJ))
  ...
  contract_path = (
      _PROJ / "docs" / "01_policies_and_standards" / "_registry" / "contracts" / "architecture_contract.yaml"
  )
  scan_dir = _PROJ / "docs" / "01_policies_and_standards"
  rel = fpath.relative_to(_PROJ)
  ```
- **新代码**：
  ```python
  from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
  ...
  # 重复 bootstrap 全部删除
  ...
  contract_path = (
      REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "contracts" / "architecture_contract.yaml"
  )
  scan_dir = REPO_ROOT / "docs" / "01_policies_and_standards"
  rel = fpath.relative_to(REPO_ROOT)
  ```
- **依据文件**：同修复2
- **附带修复**：同修复2（parents[2] BUG 导致 validator 静默 no-op）

### 修复4：check_frontmatter_metadata.py — _PROJ 改用 REPO_ROOT
- **文件**：[check_frontmatter_metadata.py](file:///D:/ZephyrAlpha/scripts/governance/d3_metadata/check_frontmatter_metadata.py)
- **原行号**：L61, L69-L71, L237, L242, L260
- **类别**：REPO_ROOT 真源分裂（`[向内收-真源分裂]`）
- **原代码**：
  ```python
  from _shared.constants import EXIT_FINDINGS, EXIT_PASS
  ...
  _PROJ = Path(__file__).resolve().parents[3]
  _VOCAB_DIR = (
      _PROJ / "docs" / "01_policies_and_standards" / "_registry" / "vocabularies"
  )
  ...
  scan_dir = _PROJ / scan_root_name
  ... fp.relative_to(_PROJ).parts ...
  rel = fpath.relative_to(_PROJ)
  ```
- **新代码**：
  ```python
  from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT
  ...
  _VOCAB_DIR = (
      REPO_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "vocabularies"
  )
  ...
  scan_dir = REPO_ROOT / scan_root_name
  ... fp.relative_to(REPO_ROOT).parts ...
  rel = fpath.relative_to(REPO_ROOT)
  ```
- **依据文件**：同修复1
- **注**：`parents[3]` 值正确（=项目根），仅方法违规，无潜在 BUG。

### 修复5：check_naming_convention.py — 9 处 parents[3] 改用已导入的 REPO_ROOT
- **文件**：[check_naming_convention.py](file:///D:/ZephyrAlpha/scripts/governance/d3_metadata/check_naming_convention.py)
- **原行号**：L1071, L1179, L1438, L1542, L1552, L1577, L1582, L1588, L1606（共 9 处）
- **类别**：REPO_ROOT 真源分裂（`[向内收-真源分裂]`）—— 已导入却不用
- **原代码**（9 处模式）：
  ```python
  from _shared.constants import EXIT_FINDINGS, EXIT_PASS, REPO_ROOT  # L60 已导入 REPO_ROOT
  ...
  project_root = Path(__file__).resolve().parents[3]   # L1071 等 9 处重复推算
  ```
- **新代码**：
  ```python
  project_root = REPO_ROOT   # 直接用已导入的 canonical 常量
  ```
- **依据文件**：同修复1
- **注**：本文件 L60 早已 `from _shared.constants import ... REPO_ROOT`，但函数体内忽略它而重复推算，属"已能发现却未使用"的典型真源分裂。

### 修复6：修复指南 §一.1 — pg_conn_wrapper.py 幽灵引用纠正
- **文件**：[p2_review_fix_guide.md](file:///D:/ZephyrAlpha/docs/_working/p2_review_fix_guide.md)
- **原行号**：L27
- **类别**：修复指南不一致（`[向内收-真源分裂]` 风险——指向不存在的真源）
- **原代码**：
  ```markdown
  | `src/zephyr/governance/pg_conn_wrapper.py` | `PgConnExecuteWrapper`——兼容sqlite3接口的wrapper |
  ```
- **新代码**：
  ```markdown
  | `scripts/governance/_shared/constants.py` | `PgConnExecuteWrapper` + `get_depgraph_pg_connection()`——兼容sqlite3接口的wrapper（AI-06 审查纠正：原指南引用的 `src/zephyr/governance/pg_conn_wrapper.py` 从未存在，git log 无历史记录；实际类定义在 `_shared/constants.py` L51-107） |
  ```
- **依据文件**：`scripts/governance/_shared/constants.py` L51-107（`class PgConnExecuteWrapper` + `def get_depgraph_pg_connection`）；git log --all -- "**/pg_conn_wrapper.py" 返回空（无任何历史记录）

## 未修复问题（需主AI协调）

无。原 2 个提示项均已经主AI授权修复（见修复记录 1-6）。

## 确认无问题项

### A. SQLite 残留（违规）检查
- [x] A1 `sqlite3.connect(连depgraph)`：✅ 无（无 sqlite3 导入）
- [x] A2 `sqlite_master`：✅ 无
- [x] A3 `?` 占位符（depgraph）：✅ 无（无 SQL）
- [x] A4 `row[0]`（depgraph）：✅ 无
- [x] A5 `depgraph.db` 路径硬编码：✅ 无
- [x] A6 `import sqlite3`（depgraph 上下文）：✅ 无
- [x] A7 `INSERT OR REPLACE` / `GROUP_CONCAT` / `AUTOINCREMENT` / `sqlite_sequence` / `last_insert_rowid`：✅ 无

### B. PG 正确性检查
- [x] B1 本分区无 depgraph 访问，B 类不适用（N/A）
- [x] B2 无 `get_db_connection` / `%s` / `with conn.cursor() as cur`——因无 DB 访问，无需这些 PG 模式

### C. module_id 检查
- [x] C1 `MOD-INF-012B-P2`（违规）：✅ 无
- [x] C2 `MOD-INF-012B-P3`（违规）：✅ 无
- [x] C3 `MOD-INF-012B` 任意变体：✅ 无

### 其他确认项
- [x] D1 `governance.db` 用 sqlite3：N/A（本分区不访问 governance.db）
- [x] D2 `market.duckdb` 用 duckdb：N/A（本分区不访问 market.duckdb）
- [x] D3 TTL 字段：`__init__.py` 含 `# [TTL] task_bound` ✅
- [x] D4 不创建新文件：本次审查未创建任何新文件（仅修改已有文件 + 写本报告）

### E. REPO_ROOT 真源分裂检查（主AI授权后修复）
- [x] E1 `validate_rule_frontmatter.py` L78 `Path(__file__).resolve().parents[3]`：✅ 已修复（修复1）
- [x] E2 `validate_blueprint_provenance.py` L50 `Path(__file__).resolve().parents[2]`：✅ 已修复（修复2，附带修复 parents[2] BUG）
- [x] E3 `validate_architecture.py` L53 `Path(__file__).resolve().parents[2]`：✅ 已修复（修复3，附带修复 parents[2] BUG）
- [x] E4 `check_frontmatter_metadata.py` L69 `Path(__file__).resolve().parents[3]`：✅ 已修复（修复4）
- [x] E5 `check_naming_convention.py` 9 处 `Path(__file__).resolve().parents[3]`：✅ 已修复（修复5）
- [x] E6 修复指南 §一.1 `pg_conn_wrapper.py` 幽灵引用：✅ 已修复（修复6）
- [x] E7 全分区 `Path(__file__).resolve().parents[N]` 残留：✅ 0 匹配（Grep 验证）
- [x] E8 全分区 `_PROJ` 残留：✅ 0 匹配（Grep 验证）
- [x] E9 py_compile 5 文件：✅ EXIT_CODE=0
- [x] E10 导入冒烟测试：✅ `REPO_ROOT: D:\ZephyrAlpha` / `RULES_DIR exists: True` / `RR2 == REPO_ROOT: True`

## 结论
- [x] 无问题，本分区审查通过（连续两次=0）
- [ ] 有残留问题，需主AI协调

本分区（`scripts/governance/d3_metadata/`）为纯文件扫描/元数据审计套件，不访问任何数据库，P2 迁移（SQLite→PostgreSQL）对其零影响。P2 审查范围内（A/B/C 三类关键词）零违规，连续两轮零问题。

经主AI授权，追加修复了 2 个提示项（非 P2 范围）：
1. **REPO_ROOT 真源分裂**：5 个文件 14 处 `Path(__file__).resolve().parents[N]` 改为 `from _shared.constants import REPO_ROOT` canonical 导入。其中 2 个文件（`validate_blueprint_provenance.py` / `validate_architecture.py`）附带修复了 `parents[2]` 指向 `scripts/` 而非项目根的潜在 BUG（此前 validator 静默 no-op）。
2. **修复指南幽灵引用**：`pg_conn_wrapper.py` 从未存在（git log 证实），纠正为实际位置 `scripts/governance/_shared/constants.py`。

所有修复经 Grep + py_compile + 导入冒烟测试三重验证，0 残留问题。

## 需主AI知会（行为变化预警——决策项）

> ⚠️ 本节为 AI-06 修复引入的**行为变化**，需主AI 决策处置方式。非本分区残留缺陷。

### 事项：2 个 validator 从 silent no-op 恢复为实际扫描

- **涉及文件**：
  - [validate_blueprint_provenance.py](file:///D:/ZephyrAlpha/scripts/governance/d3_metadata/validate_blueprint_provenance.py)（修复2）
  - [validate_architecture.py](file:///D:/ZephyrAlpha/scripts/governance/d3_metadata/validate_architecture.py)（修复3）
- **变化前**：因 `_PROJ = Path(__file__).resolve().parents[2]` 指向 `scripts/` 目录而非项目根，扫描路径为 `scripts/docs/...`（不存在）→ validator 在 `if not scan_dir.exists(): continue` 处静默跳过全部文件 → **永远返回 EXIT_PASS**（虚假安全感）。
- **变化后**：改用 `REPO_ROOT`（= `D:\ZephyrAlpha`），扫描路径为真实的 `docs/...` → validator 恢复设计意图的扫描能力，**可能检出此前被隐藏的历史违规**。
- **风险等级**：中（非数据损坏，但可能触发 CI 门禁失败或暴露技术债）
- **主AI 决策选项**：
  1. **直接全量启用**（推荐）：接受 validator 恢复后的全部输出，历史违规一次性清账；
  2. **阶段性启用**：先以 `warn_only=true` 或非阻断模式运行一轮，统计历史违规量，再决定是否转阻断；
  3. **暂不启用**：保持现状（不接入 CI），仅本地按需运行。
- **AI-06 立场**：推荐选项 1（治本）。silent no-op 比"扫描出违规"更危险——前者让团队误以为已通过校验，后者至少暴露真实问题。本审查只负责让代码正确，不负责压制 validator 输出。
- **相关佐证**：终端冒烟测试中，`check_naming_convention.py`（同分区另一文件，本次亦修复 REPO_ROOT）已实测检出 `AGENTS.md` 中的 "P2迁移后" 过渡标记，证明 validator 修复后扫描能力正常。

---

## 红蓝极限对抗审核（§7.3）

### 7.3.1 模拟新 AI 可发现性测试

| 测试项 | 判定标准 | 结果 |
|--------|---------|------|
| 可被发现性 | 新 AI 能否通过 AGENTS.md / 注册表 / 标准入口 发现本分区功能？ | ✅ 通过——`__init__.py` 导出 `__all__` 清单，文件头 `[BLUEPRINT] MOD-INF-005` 可被 depgraph 索引 |
| 可被绕过性 | 新 AI 能否绕过本分区自行实现？ | ⚠️ 中等风险——本分区是审计脚本（被动运行），非 gate，新 AI 理论上可绕过；但这属治理设计议题，非 P2 范围 |
| 可被使用性 | 接口是否清晰？ | ✅ 通过——每个脚本均为 argparse CLI，入口清晰 |
| 可被重复造轮子性 | 是否容易重复造？ | ✅ 通过——`__all__` + `_shared.*` 已收敛公共能力 |

### 7.3.2 红蓝极限对抗测试

- **红方攻击1**：「本分区既然不访问 DB，是否漏审了真正的 DB 访问点？」
  - **蓝方防御**：用 5 组正则（`sqlite3` / `psycopg2|duckdb|database_service|depgraph_schema` / `.connect\(|cursor|fetchone|fetchall` / `INSERT INTO|SELECT FROM|UPDATE SET|DELETE FROM` / `MOD-INF-012B`）全量扫描 17 文件，均无命中（除 2 处字符串字面量已核实）。红方攻击被抵御。
- **红方攻击2**：「`check_vocab_hardcode.py` 出现 `depgraph_schema.py` 和 `sqlite_schema.py`，是否隐藏 DB 访问？」
  - **蓝方防御**：Read 上下文（L84-89）确认两者均为 `_DDL_EXEMPT_FILES` frozenset 白名单字符串字面量，用于跳过词表硬编码检测（DDL-as-Code 协议），非 import / 非 connect。红方攻击被抵御。
- **红方攻击3**：「REPO_ROOT 修复是否引入新风险？例如 `_shared.constants` 导入失败导致脚本崩溃？」
  - **蓝方防御**：`_shared.constants` 是本分区所有 17 文件的标准依赖（6 个文件此前已用 `from _shared.constants import REPO_ROOT`），导入链已验证（`_shared/constants.py` L36-42 做 canonical bootstrap + re-export `zephyr.shared.io.paths.REPO_ROOT`）。导入冒烟测试 5 文件全部 OK，`REPO_ROOT` 正确解析为 `D:\ZephyrAlpha`。红方攻击被抵御。
- **红方攻击4**：「`validate_blueprint_provenance.py` / `validate_architecture.py` 修复前是静默 no-op（parents[2] BUG），修复后突然开始扫描真实 docs/——会不会暴露大量历史违规导致门禁爆炸？」
  - **蓝方防御**：这是"治本"的预期行为——validator 此前因路径错误而 silently passing everything，比"扫描出违规"更危险（虚假安全感）。修复后 validator 恢复设计意图的扫描能力，若暴露历史违规属正确行为，应由主 AI 决定是否在 CI 中阶段性启用。本审查只负责让代码正确，不负责压制 validator 输出。红方攻击被抵御（但建议主 AI 知会此行为变化）。
- **红方攻击5**：「修复指南被修改，是否影响其他 AI 的审查依据？」
  - **蓝方防御**：修复指南 §一.1 的修改是将幽灵引用 `pg_conn_wrapper.py`（从未存在）纠正为实际位置 `_shared/constants.py`。这是事实纠正，非主观判断——其他 AI 按纠正后的路径能找到真实的 `PgConnExecuteWrapper` 类，按原路径只会找不到文件。修改是单向改善，无回退风险。红方攻击被抵御。

---

## 大白话汇报（向内收审核结论）

### 我做了什么
按 P2 修复指南对 `scripts/governance/d3_metadata/` 下 17 个 .py 文件做了三轮自修复循环审查；P2 范围（SQLite残留/PG正确性/module_id）零违规；经主AI授权后追加修复了 2 个提示项（REPO_ROOT 真源分裂 + 修复指南幽灵引用），共 6 处修改。

### 这个功能的作用
确认这个「文档元数据审计套件」分区在 P2 迁移后没有残留违规代码，并顺带收敛了 REPO_ROOT 真源分裂问题。

### 达成了什么目标
P2 范围零违规通过；5 个文件 14 处 `Path(__file__).resolve().parents[N]` 改为 canonical `REPO_ROOT` 导入；2 个文件附带修复了 `parents[2]` 指向 `scripts/` 的潜在 BUG（validator 此前静默 no-op）；修复指南幽灵引用纠正。

### 解决了什么痛点
1. 排除本分区作为 P2 迁移漏改风险点；
2. 消除同分区 REPO_ROOT 两种写法并存的真源分裂；
3. 让 2 个 validator 恢复实际扫描能力（不再是 silent no-op）；
4. 防止其他 AI 被修复指南的幽灵文件引用误导。

### 功能通过什么触发自动启动
本分区是被动审计脚本（CLI 按需运行 / pre-commit 钩子触发），非事件驱动的永久系统——这属治理设计议题，超出 P2 范围，未在本次审查中改动。

### 如何自动运行
N/A（被动脚本，由 pre-commit 或人工 CLI 触发；本审查未改动运行机制）。

### 如何自动关闭
N/A（CLI 脚本运行完即退出，无长驻进程）。

### 向内收审核结果
- [x] 责任唯一真源唯一：通过（5 文件 14 处 REPO_ROOT 推算已收敛到 `_shared.constants.REPO_ROOT` 唯一真源；修复指南幽灵引用已纠正）
- [x] 能用现成不创造：通过（扩展现有 `_shared.constants` 导入，未创建任何新文件；修复指南纠正也只改一行表格）
- [x] 永久系统全自动：N/A（本分区为按需 CLI 审计工具，非永久系统；未改动运行机制）
- [x] 第一性原理治本：通过（parents[2] BUG 是根因——validator 路径错误导致 silent no-op，修复后恢复设计意图的扫描能力，非打补丁）
- [x] AI 可发现性：通过（`__init__.py` 的 `__all__` + 文件头 BLUEPRINT 标记可被标准入口发现；`_shared.constants.REPO_ROOT` 已是本分区 6 文件既有标准入口）
- [x] 红蓝对抗：通过（5 项红方攻击均被抵御，详见 §7.3.2）

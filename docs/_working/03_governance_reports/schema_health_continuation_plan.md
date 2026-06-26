---
ttl: task_bound
doc_type: construction_plan
---

# Schema 健康度治本：延续执行计划（v2 续作）

> **文档定位**：本计划是 `schema_health_revised_execution_plan.md`（v2，已批准）的**延续执行版**。v2 的 6 层调研报告、5 处事实修正、裁定表、verify_schema_health.py 完整脚本设计、pre-commit 配置**全部仍然有效且为唯一真源**。本文件只记录"上下文二次丢失后，基于实测当前状态"的剩余施工动作，避免重复 v2 已写内容。
> **修订日期**：2026-06-26（v2 批准后第二轮上下文恢复）
> **触发原因**：会话上下文再次丢失，系统重置为 Plan Mode；按用户硬约束"上一个 AI 的结论不可全信，必须回代码真源核实"，重新实测 DB + 脚本状态，发现 v2 计划已部分执行。
> **施工总原则**：严格遵循 v2 计划，不偏离、不重新规划、不增加未请求功能。

---

## 0. v2 计划与本计划的关系

| 维度 | v2 计划（已批准） | 本延续计划 |
|------|------------------|-----------|
| 调研报告 / 根因 / 行业基准 / 裁定 | ✓ 唯一真源，不变 | 不重复 |
| verify_schema_health.py 完整脚本 | ✓ §3 阶段5 完整代码 | 引用，不重抄 |
| pre-commit hook 配置 | ✓ §3 阶段6 完整 YAML | 引用，不重抄 |
| 当前状态核实 | v2 §1 为"v2 撰写时"状态 | **本 §1 为"现在"实测状态**（v2 部分已执行） |
| 剩余动作 | v2 §3 阶段3-7 全量 | **本 §2 仅剩余未完成部分**，精确到行号 |

---

## 1. 实测当前状态（Phase 1 探索结论，非引用 v2）

| 阶段 | v2 撰写时状态 | **现在实测状态** | 证据 |
|------|--------------|----------------|------|
| 阶段3 #ARCH-010 (gen_depgraph) | ✗ 3 处 module_lifecycle_state 残留 | **✓ 已完成** | generate_project_depgraph.py grep `module_lifecycle_state` = 0 处（仅 .aidrafts 归档草案有残留，出范围） |
| 阶段4.1 (migration v14 写入) | ✗ 未开始 | **✓ 已完成** | depgraph_schema.py L888-897 v14 存在，DROP 3 表；description 含 KEEP 说明 |
| 阶段4.2 (移除 3 表 DDL + v1 引用 + 注释) | ✗ 未开始 | **✓ 已完成** | `_DDL_INVARIANTS`/`_DDL_ARCH_BOTTLENECKS`/`_DDL_ARCH_LAYERS` 全 0 匹配；v1 migration 引用已移除；header 注释含 v14 变更说明 |
| 阶段4.3 (清理读取已删表代码) | ✗ 未开始 | **🔶 部分完成** | 见下表 |
| 阶段4.4 (清理测试) | ✗ 未开始 | **✗ 未完成** | test_depgraph_db.py 仍有 invariants/arch_layers/arch_bottlenecks 测试 |
| 阶段4.5 (运行 v14) | ✗ 未开始 | **✗ 未完成** | DB `MAX(version)`=13（仍 v13）；3 张死表仍在；arch_bottlenecks=3 / arch_layers=4 / invariants=255 |
| 阶段5 (verify_schema_health.py) | ✗ 未开始 | **✗ 未完成** | Glob `scripts/governance/verify_schema_health.py` = No file found |
| 阶段6 (pre-commit 门禁) | ✗ 未开始 | **✗ 未完成** | — |
| 阶段7 (文档同步) | ✗ 未开始 | **✗ 未完成** | — |

### 阶段4.3 子项实测明细

| 子项 | v2 要求 | 现在状态 | 证据 |
|------|--------|---------|------|
| apply_depgraph.py steps 列表 | 移除 `(11,"invariants","domain_id",False)` | **✓ 已完成** | steps 列表 17 步，无 invariants 元组；L1589 注释已记"v14删除invariants表，原step11移除" |
| apply_depgraph.py L1523-1524 docstring | （隐含：移除 invariants.invariant_id 提及） | **✗ 未完成** | L1523 仍"18步 UPDATE"；L1524 仍"如 nodes.owner/business_stream/tags/invariants.invariant_id 等" |
| depgraph_reader.py get_architecture_layers | 移除方法（L201-205） | **✗ 未完成** | L201-205 方法仍存在，`SELECT * FROM arch_layers` |
| create_d_signal_rename_tasks.py | 从 L133 移除 invariants.domain_id | **✗ 未完成** | L133 仍"contracts.consumer_domain / invariants.domain_id / arch_constraints.from_domain /" |
| audit_rename_completeness.py | 移除 L20 invariants.invariant_id + EXCLUDE_TABLES | **🔶 部分** | EXCLUDE_TABLES（L74）已不含 invariants ✓；但 L19-20 docstring 仍"18步 UPDATE ... invariants.invariant_id 等" ✗ |

---

## 2. 剩余施工方案（动作级，精确到行号）

> 备份锚点：v2 已记录 HEAD `6d68fcb8`。施工前应再次 `git rev-parse HEAD` 确认当前 HEAD，并按 HARD CONSTRAINT 通过 GitCommitGateway 提交（ZEPHYR_COMMIT_GATEWAY=1 + [GW:session_id]）。

### 阶段4 剩余：补全 4.3 + 执行 4.4 + 4.5

#### 动作4.3-A：apply_depgraph.py L1521-1527 docstring 更新

**文件**：`d:\ZephyrAlpha\scripts\governance\apply_depgraph.py`
**当前文本**（L1521-1524）：
```
    """值扫描兜底（裁定#207 R1 B1）：扫描所有表所有 TEXT 列，REPLACE old_id→new_id。

    18步 UPDATE 只覆盖预定义列名枚举，本函数兜底扫描所有 TEXT 列，
    替换未枚举列中的残留（如 nodes.owner/business_stream/tags/invariants.invariant_id 等）。
```
**编辑**：
- L1523：`18步 UPDATE` → `17步 UPDATE（v14删除invariants表后）`
- L1524：`如 nodes.owner/business_stream/tags/invariants.invariant_id 等` → `如 nodes.owner/business_stream/tags 等`
**理由**：steps 列表已实际改为 17 步；docstring 须与之一致；invariants 表已删，不可再作"未枚举列残留示例"。

#### 动作4.3-B：depgraph_reader.py 移除 get_architecture_layers 方法

**文件**：`d:\ZephyrAlpha\src\zephyr\governance\depgraph_reader.py`
**当前文本**（L201-205，含上方空行）：
```python

    def get_architecture_layers(self) -> list[dict[str, Any]]:
        """获取所有架构层"""
        conn = self._get_conn()
        cursor = conn.execute("SELECT * FROM arch_layers")
        return [dict(row) for row in cursor.fetchall()]
```
**编辑**：整段删除（L200 空行 + L201-205 方法体），使 L199 注释行后直接衔接 L207 `def get_architecture_domains`。
**前置验证**：grep `get_architecture_layers` 全 src/ 无生产调用者（Agent 已确认仅定义处 1 处 + 文档引用，无 caller）。
**理由**：arch_layers 表 v14 删除后，该 reader 会抛 OperationalError。

#### 动作4.3-C：create_d_signal_rename_tasks.py 任务卡描述一致性更新

**文件**：`d:\ZephyrAlpha\scripts\governance\create_d_signal_rename_tasks.py`
**范围**：OPS-2026062602 任务卡描述块（L125-145）+ 标题 L151 + 验收 L166 + 自治清单 L181
**编辑**：
1. L128：`命令实现18步UPDATE覆盖11表` → `命令实现17步UPDATE覆盖10表`
2. L129：`实现18步UPDATE逻辑：` → `实现17步UPDATE逻辑：`
3. L133：`contracts.consumer_domain / invariants.domain_id / arch_constraints.from_domain /` → `contracts.consumer_domain / arch_constraints.from_domain /`（删除 `invariants.domain_id / `）
4. L143：`确认18步UPDATE覆盖488行` → `确认17步UPDATE覆盖488行`（行数 488 不变——invariants.domain_id 原本 0 行命中，删表不影响总行数）
5. L145：`cmd_rename_domain实现18步UPDATE覆盖11表488行` → `cmd_rename_domain实现17步UPDATE覆盖10表488行`
6. L151（title 字段）：`（18步UPDATE覆盖11表488行）` → `（17步UPDATE覆盖10表488行）`
7. L166（acceptance）：`dry_run输出18步UPDATE覆盖488行` → `dry_run输出17步UPDATE覆盖488行`
8. L181（autonomy_checklist）：`"18步UPDATE无遗漏表"` → `"17步UPDATE无遗漏表"`
**理由**：cmd_rename_domain 实现已改为 17 步；任务卡描述须与实际一致；488 总行数不变（invariants.domain_id 原 0 行命中）。
**注意**：此文件是任务卡生成器，governance.db 中已生成的历史卡不受影响；本编辑仅修正生成器源码，使其描述当前 cmd_rename_domain 能力。

#### 动作4.3-D：audit_rename_completeness.py docstring 更新

**文件**：`d:\ZephyrAlpha\scripts\governance\audit_rename_completeness.py`
**当前文本**（L19-21）：
```
裁定#204 改名（D-SIGNAL* 4域）时，cmd_rename_domain 的 18步 UPDATE 只覆盖
预定义列名枚举，遗漏了 nodes.owner/business_stream/tags/invariants.invariant_id 等
未枚举列，导致314行存量残留。本脚本用"值扫描兜底"检测所有残留。
```
**编辑**：
- L19：`18步 UPDATE` → `17步 UPDATE（v14前为18步，含invariants.domain_id）`
- L20：`如 nodes.owner/business_stream/tags/invariants.invariant_id 等` → `如 nodes.owner/business_stream/tags 等`
**理由**：保留历史语境（裁定#204 时确为 18 步），但移除对已删表的列引用（值扫描兜底已不再扫 invariants）。
**不动**：EXCLUDE_TABLES（L74）已确认不含 invariants，无需编辑。

#### 动作4.4：清理 test_depgraph_db.py 对已删表的引用

**文件**：`d:\ZephyrAlpha\tests\test_depgraph_db.py`
**编辑**（3 处删除）：
1. **invariants 测试块**（L135-144）：整段删除（`# === 7. invariants ===` 标题 + INSERT + SELECT + check）
2. **arch_layers 测试块**（L155-157）：整段删除（`# === 10. arch_layers ===` 标题 + COUNT + check）
3. **arch_bottlenecks 测试块**（L171-173）：整段删除（`# === 14. arch_bottlenecks ===` 标题 + COUNT + check）
4. **Cleanup 中的 invariants 删除**（L203）：删除 `c.execute("DELETE FROM invariants WHERE invariant_id='INV-TEST-001'")` 行

**发现的预存问题（出范围，仅告知）**：
- L147-149 `arch_domain_capacity` 测试 + L159-161 `arch_domain_layers` 测试：这两张表在 DB 中**不存在**（实测表清单无此二表），测试会抛 `OperationalError: no such table`。这是**预存 bug**，非 v14 引入，**不在本轮施工范围**。v2 验收标准为"无新增失败"，故保留不动。建议后续独立任务处理（疑似更早的 schema 漂移遗留）。

#### 动作4.5：运行 migration v14 + 验证

**前置**：通过 GitCommitGateway 提交 4.3/4.4 的代码变更（备份点）。
**命令**：
```bash
python -c "from zephyr.governance.depgraph_schema import init_db; init_db(echo=True)"
```
**验证命令**（4 项，逐条核对）：
```bash
# 1. 版本=14
python -c "import sqlite3;c=sqlite3.connect(r'd:/ZephyrAlpha/data/databases/depgraph.db');print('VERSION:',c.execute('SELECT COALESCE(MAX(version),0) FROM _schema_version').fetchone()[0])"
# 预期: VERSION: 14

# 2. 3 张死表已删除
python -c "import sqlite3;c=sqlite3.connect(r'd:/ZephyrAlpha/data/databases/depgraph.db');print('DROPPED:',[r[0] for r in c.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name IN ('arch_bottlenecks','arch_layers','invariants')\")])"
# 预期: DROPPED: []

# 3. 2 张保留表仍在
python -c "import sqlite3;c=sqlite3.connect(r'd:/ZephyrAlpha/data/databases/depgraph.db');print('KEPT:',[r[0] for r in c.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name IN ('cross_registry_rules','governance_audit_logs')\")])"
# 预期: KEPT: ['cross_registry_rules', 'governance_audit_logs']

# 4. 生成器仍可运行
python scripts/governance/generate_project_depgraph.py --dry-run
# 预期: 无 OperationalError
```
**回滚**：`git checkout HEAD -- data/databases/depgraph.db` + `init_db()`（v1 migration CREATE IF NOT EXISTS 不会重建已删表，需 git 恢复 .db）。

---

### 阶段5：创建 verify_schema_health.py 门禁

**动作5.1**：新建 `d:\ZephyrAlpha\scripts\governance\verify_schema_health.py`
- **完整脚本内容**：直接采用 v2 计划 §3 阶段5 的完整 Python 代码（L154-351，约 197 行）。
- **关键要点**（v2 已修正，执行时严格遵守）：
  - DDL 映射 `_DDL_MAP` 用**非 `_V5`** 常量（`_DDL_NODES`/`_DDL_EDGES`/`_DDL_ARCH_DIRECTORY_TREE` 等）
  - `_DDL_MAP` 含 **19 张保留表**（v2 代码 L240-262 列出 21 个键，实际为 nodes/edges/domains/domain_dependencies/domain_events/contracts/rule_bindings/arch_constraints/arch_directory_tree/arch_path_mappings/gates/governance_audit_logs/blueprint_links/business_streams/cross_registry_rules/field_vocabularies/hard_boundaries/infrastructure_components/model_capabilities/registries/domain_mapping = 21 张），**不含** arch_bottlenecks/arch_layers/invariants
  - 校验3项：DDL 列一致性 + 只读触发器（9 张 READONLY 表 × 3 触发器）+ Schema 版本一致性
  - 退出码：0=PASS / 1=FINDINGS（漂移）/ 2=ERROR

**动作5.2**：验证脚本可运行
```bash
python scripts/governance/verify_schema_health.py --warn-only
```
**验证**：无 ImportError；阶段4 完成后应输出 `[PASS]`。若报 DDL-DRIFT，先核对 `_DDL_MAP` 是否含已删表（应排除）。
**回滚**：删除该文件。

> **执行注意**：v2 代码 L240 注释写"19 张保留表"，但实际 `_DDL_MAP` 字典含 21 个键。执行时以字典实际键数为准（21 张），注释"19张"是 v2 笔误——但因 invariants/arch_layers/arch_bottlenecks 不在字典中，校验逻辑正确。执行时把注释"19 张"改为"21 张（已排除 v14 删除的 3 表）"以消除文档与代码矛盾。

---

### 阶段6：注册 GATE-SCHEMA-HEALTH

**动作6.1**：在 `d:\ZephyrAlpha\.pre-commit-config.yaml` 的 local hooks 列表中添加 v2 §3 阶段6 的完整 YAML 块（gate-schema-health 条目）。
**动作6.2**：验证
```bash
pre-commit run gate-schema-health --all-files
```
**预期**：`[PASS] depgraph.db Schema 健康度校验通过`（阶段4-5 完成后）
**回滚**：移除该 hook 条目。

---

### 阶段7：同步文档与索引

**动作7.1**：更新 `d:\ZephyrAlpha\docs\02_enterprise_architecture\dependency_architecture_panorama.md`
- 移除已删 3 张表（arch_bottlenecks / arch_layers / invariants）的表归属矩阵、目录、清单行（Agent 定位：L83、L88、L127、L130、L158、L195、L200、L1461、L2008、L2033 等位置——执行时逐一核对后删除）
- 保留 cross_registry_rules（注明：健康只读缓存，sync 自 registry_consistency_contract.yaml，6 条 CR 规则）
- 保留 governance_audit_logs（注明：auto_runner 运行摘要审计；后续迁移至 src/zephyr/audit-trail/ WORM 模块为独立任务）
- 更新 contracts 表列数：7 → 13

**动作7.2**：更新 `d:\ZephyrAlpha\scripts\governance\script_manifest.yaml`
- 添加 `verify_schema_health.py` 条目

**动作7.3**：更新 `d:\ZephyrAlpha\.trae\rules\project_rules.md` RULE-SIXTEEN
- 追加："结构变更必须先改 `depgraph_schema.py` 的 `_DDL_*` 声明 + 添加 migration；禁止直接改写入代码跳过 DDL。GATE-SCHEMA-HEALTH 自动校验 DB↔DDL 一致性"

**动作7.4**：更新 `d:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` L1106
- 移除 `invariants.invariant_id` 示例（rule fail 示例），改为不含已删表的示例

**动作7.5**：在治理报告索引添加 v2 修订执行计划链接
- `d:\ZephyrAlpha\docs\02_enterprise_architecture\03_governance_reports\` 索引中添加 `schema_health_revised_execution_plan.md` 链接

**动作7.6**（v2 未列，Agent 发现的漂移文件）：更新 `d:\ZephyrAlpha\docs\03_modules\_cross_layer\database\sub_blueprints\mod_inf_012b_p2_postgresql_migration.md` L499
- 从 PostgreSQL 迁移表清单中移除 `arch_layers`（表已删，迁移无意义）
- 注：同清单 L502 的 `arch_invariants` 是**不同表**（非本轮删除的 `invariants`），不动

**动作7.7**（可选，历史归档清理）：`d:\ZephyrAlpha\docs\02_enterprise_architecture\03_governance_reports\d_signal_rename_plan.md` L257
- 该行注释 `# 11. UPDATE invariants SET domain_id=...` 是历史改名方案步骤记录。裁定：**保留不动**（历史文档记录"当时方案"，不可回溯改写；v2 未要求改此文件）

---

## 3. 受影响文件矩阵（剩余施工）

| # | 文件 | 变更 | 阶段 | v2 对应 |
|---|------|------|------|---------|
| 1 | `scripts/governance/apply_depgraph.py` | 改：L1523-1524 docstring（18→17步，删 invariants.invariant_id） | 4.3-A | v2 §3 阶段4.3 |
| 2 | `src/zephyr/governance/depgraph_reader.py` | 改：移除 get_architecture_layers 方法（L201-205） | 4.3-B | v2 §3 阶段4.3 |
| 3 | `scripts/governance/create_d_signal_rename_tasks.py` | 改：L128-181 任务卡描述一致性（18→17步，删 invariants.domain_id） | 4.3-C | v2 §3 阶段4.3 |
| 4 | `scripts/governance/audit_rename_completeness.py` | 改：L19-20 docstring（删 invariants.invariant_id） | 4.3-D | v2 §3 阶段4.3 |
| 5 | `tests/test_depgraph_db.py` | 改：删 invariants/arch_layers/arch_bottlenecks 测试块 + cleanup | 4.4 | v2 §3 阶段4.4 |
| 6 | `data/databases/depgraph.db` | 运行：init_db() 执行 v14 | 4.5 | v2 §3 阶段4.5 |
| 7 | `scripts/governance/verify_schema_health.py` | 新建：完整脚本（采 v2 §3 阶段5 代码） | 5 | v2 §3 阶段5 |
| 8 | `.pre-commit-config.yaml` | 改：注册 gate-schema-health | 6 | v2 §3 阶段6 |
| 9 | `docs/02_enterprise_architecture/dependency_architecture_panorama.md` | 改：移除 3 表 + 更新 contracts 列数 + 标注 2 表保留 | 7.1 | v2 §3 阶段7.1 |
| 10 | `scripts/governance/script_manifest.yaml` | 改：添加 verify_schema_health.py 条目 | 7.2 | v2 §3 阶段7.2 |
| 11 | `.trae/rules/project_rules.md` | 改：RULE-SIXTEEN 追加 Schema 门禁说明 | 7.3 | v2 §3 阶段7.3 |
| 12 | `docs/01_policies_and_standards/rules/trae_028_doc_structure_naming.yaml` | 改：L1106 移除 invariants.invariant_id 示例 | 7.4 | 本计划新增（Agent 发现） |
| 13 | `docs/03_modules/_cross_layer/database/sub_blueprints/mod_inf_012b_p2_postgresql_migration.md` | 改：L499 移除 arch_layers | 7.6 | 本计划新增（Agent 发现） |

**不动文件**（明确排除，与 v2 一致）：
- `sync_yaml_to_depgraph.py`（cross_registry_rules 保留，sync 不动）
- `auto_runner.py`（governance_audit_logs 保留，写入路径不动）
- `tests/test_f18_*.py`（governance_audit_logs 测试不动）
- `docs/.../d_signal_rename_plan.md`（历史方案文档，不改写）

---

## 4. 验收标准

| 验收项 | 验证命令 | 预期 |
|--------|---------|------|
| v14 已执行 | `python -c "import sqlite3;c=sqlite3.connect(r'd:/ZephyrAlpha/data/databases/depgraph.db');print(c.execute('SELECT COALESCE(MAX(version),0) FROM _schema_version').fetchone()[0])"` | `14` |
| 3 死表已删 | `python -c "import sqlite3;c=sqlite3.connect(r'd:/ZephyrAlpha/data/databases/depgraph.db');print([r[0] for r in c.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name IN ('arch_bottlenecks','arch_layers','invariants')\")])"` | `[]` |
| 2 保留表仍在 | `python -c "import sqlite3;c=sqlite3.connect(r'd:/ZephyrAlpha/data/databases/depgraph.db');print([r[0] for r in c.execute(\"SELECT name FROM sqlite_master WHERE type='table' AND name IN ('cross_registry_rules','governance_audit_logs')\")])"` | `['cross_registry_rules','governance_audit_logs']` |
| 无 invariants 残留引用 | `grep -rn "invariants\." scripts/governance/apply_depgraph.py scripts/governance/create_d_signal_rename_tasks.py scripts/governance/audit_rename_completeness.py`（排除 type_specific_data JSON key 与 invariants.yaml） | 仅历史注释或无匹配 |
| get_architecture_layers 已移除 | `grep -rn "get_architecture_layers" src/` | 0 匹配 |
| verify 脚本 PASS | `python scripts/governance/verify_schema_health.py` | exit 0，`[PASS]` |
| 门禁已注册 | `grep "gate-schema-health" .pre-commit-config.yaml` | 有匹配 |
| 生成器可运行 | `python scripts/governance/generate_project_depgraph.py --dry-run` | 无 OperationalError |

---

## 5. 回滚方案

**单阶段回滚**：每阶段独立 `git checkout -- <file>`；DB 改动 `git checkout HEAD -- data/databases/depgraph.db`。
**整体回滚**：通过 GitCommitGateway 执行 `git reset --hard <backup-HEAD>` + `init_db()` + `sync_yaml_to_depgraph.py`。

---

## 6. 循环审查记录

**本轮审查**：对照 v2 已批准计划，重新实测 DB（v13，3 死表仍在）+ 脚本状态（4.3 部分完成），确认：
- v2 裁定（删 3 表 / KEEP 2 表）不变，无新冲突
- 本计划剩余动作与 v2 §3 阶段4.3-7 逐条对齐，仅补充 v2 未列的 2 个文档漂移点（trae_028 L1106、MOD-INF-012B L499）
- 发现预存问题（arch_domain_capacity / arch_domain_layers 测试引用不存在的表）明确标为出范围，不擅自扩大施工
- v2 verify 脚本注释"19张"与字典实际 21 键的笔误，执行时修正注释为"21张（已排除 v14 删除的 3 表）"，不改校验逻辑

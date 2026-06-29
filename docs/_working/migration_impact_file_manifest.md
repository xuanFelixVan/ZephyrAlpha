---
doc_type: audit_report
status: active
title: "P2 PostgreSQL 迁移影响查询手册——动态查询 + 关键治本清单"
module_id: "MOD-DB_DEPGRAPH_PG"
version: "3.0.0"
created: "2026-06-29"
ttl: task_bound
completes_when: "所有因迁移暂停的并发 AI 通过本手册恢复工作"
scope: "0a948902db^..HEAD（P2 迁移起点到治本结束）"
---

# P2 PostgreSQL 迁移影响查询手册

> **设计原则**：不维护静态文件清单（死数据 + 漂移风险 + 违背"向内收"）。
> 本手册只提供 **查询起点锚点 + 动态查询命令 + 关键治本清单（硬约束变化）**。
> 其他 AI 按需自行跑 git 命令获取实时准确的完整文件清单。

## 一、迁移起点锚点（不变量）

| 锚点 | 值 | 说明 |
|------|-----|------|
| **起点 commit** | `0a948902db` | 2026-06-25 12:02:14，P2 PostgreSQL 迁移任务卡 + 影响文件索引提交（迁移工作第一个 commit） |
| **闭环 commit** | `2474eacac` | 2026-06-28，P2 迁移审查正式闭环（19 AI 审查 + 6 项跨分区遗留处置完成） |
| **终点 commit** | `HEAD`（当前为 `0fe33ac1`） | 治本后续结束 |
| **总 commit 数** | 749 | 起点..HEAD（含 261 个 auto-reconcile 自动同步 commit） |

> **任何 AI 任何时候**都可以用 `0a948902db^..HEAD` 作为查询范围，获取从迁移开始到当前的所有变更。这个 commit hash 是不变量，永远有效。

## 二、动态查询命令手册（授人以渔）

### 2.1 完整文件清单（含自动生成文件）

```bash
# 完整清单（11662 文件，含自动生成的架构文档/manifest/.db）
git diff --name-status 0a948902db^..HEAD

# 完整清单（排除自动生成文件，约 6635 文件）
git diff --name-status 0a948902db^..HEAD | grep -vE '^docs/02_enterprise_architecture/(02_domain_architecture_docs|01_global_architecture_diagram|generated|target_architecture)/|^\S+\s+docs/08_KNOWLEDGE/|^\S+\s+data/(stash_archive|red_blue)/|^\S+\s+scripts/script_manifest\.yaml$|rule_catalog_registry\.yaml$|arch_directory_tree|\.db|^\S+\s+\.runtime/|^\S+\s+\.aidrafts/'
```

### 2.2 按目录/主题过滤查询

```bash
# 只查 src/ 源代码变更
git diff --name-status 0a948902db^..HEAD -- src/

# 只查某个具体目录（例：governance 模块）
git diff --name-status 0a948902db^..HEAD -- src/zephyr/governance/

# 只查治理脚本
git diff --name-status 0a948902db^..HEAD -- scripts/governance/

# 只查测试
git diff --name-status 0a948902db^..HEAD -- tests/

# 只查规则/蓝图/注册表文档
git diff --name-status 0a948902db^..HEAD -- docs/01_policies_and_standards/ docs/03_modules/
```

### 2.3 查单个文件/模式的变更历史

```bash
# 某个文件是否被改过 + 改了几次
git log --oneline 0a948902db^..HEAD -- src/zephyr/governance/rule_engine.py

# 某个文件的详细 diff
git diff 0a948902db^..HEAD -- src/zephyr/governance/rule_engine.py

# 按文件名模式查（例：所有 VMS 相关文件）
git log --oneline 0a948902db^..HEAD -- '**/vector_memory/**' '**/vms_*.py'

# 按文件名模式查 diff
git diff --name-status 0a948902db^..HEAD -- '**/vector_memory/**'
```

### 2.4 按 commit 主题查询

```bash
# 所有 P2 迁移相关 commit
git log --oneline 0a948902db^..HEAD --grep="P2" --grep="PostgreSQL" --grep="postgres" -i

# 所有 VMS 治本相关 commit
git log --oneline 0a948902db^..HEAD --grep="VMS" --grep="vector_memory" -i

# 所有数据库连接真源治本相关 commit
git log --oneline 0a948902db^..HEAD --grep="get_db_connection" --grep="get_depgraph_pg_connection" --grep="数据库连接" -i

# 排除自动同步 commit（只看人工 commit）
git log --oneline 0a948902db^..HEAD --invert-grep --grep="auto-reconcile" --grep="auto-sync" --grep="chore(manifest)" --grep="chore(depgraph)" --grep="chore(catalog)"
```

### 2.5 查询 P2 闭环前的迁移施工阶段（不含治本后续）

```bash
# P2 迁移施工 + 审查阶段（起点到闭环）
git diff --name-status 0a948902db^..2474eacac

# P2 治本后续阶段（闭环到 HEAD）
git diff --name-status 2474eacac..HEAD
```

## 三、迁移主题概览（git diff 查不到的语义信息）

P2 PostgreSQL 迁移工作分为 4 个阶段：

### 阶段 1：P2 迁移施工（`0a948902db` → `68ee791f4e`）
- depgraph.db SQLite → PostgreSQL 16 迁移
- T1-T6 全过，40 并发红蓝测试 5/5 通过
- 25 表 schema 从 SQLite 语法迁移到 PG 语法（IDENTITY 列 / ON CONFLICT / %s 占位符等）

### 阶段 2：P2 迁移审查（19 AI 并发审查）
- 19 AI 分区审查全部通过（连续两轮零问题）
- 5807 个文件修复（6 个闭环 commit：`d6176a19` / `2477f367` / `5f3a8869` / `ab97c484` / `4c62449e` / `74a07022`）
- 3 个新增 P2 回归测试
- 6 项跨分区遗留事项全部处置

### 阶段 3：P2 审查闭环（`2474eacac`，2026-06-28）
- P2 迁移审查正式闭环

### 阶段 4：治本后续（`2474eacac` → HEAD，28 个 commit）
4 大治本主题：

1. **数据库连接函数真源冲突治本**（commits: `408ef73b`, `a3e53d4e`, `a2dc2714`, `bdb99a82`）
   - F1 改名：`depgraph_schema.get_db_connection` → `get_depgraph_pg_connection`
   - F4 无限递归治本：`constants.py` import 别名消除同名遮蔽
   - N-17 BOM 脆弱性治本：`check_naming_convention.py` 抽取 `_read_text_bom_safe` 公共函数
   - CapabilityLookup 注册 `depgraph_pg_connection` + `sqlite_db_connection`

2. **VMS 治本**（commits: `6797764c` → `d2911264`，16 个 commit）
   - 删除 `governance/vector_memory/` 整包漂移副本（25 D + 1 R092）
   - `integration/vector_memory/` 真源修复（8 M，含 doc_id 确定性、snapshot 治本）
   - 新增 `GATE-VMS-SSOT` 门禁防漂移复发
   - 删除 `snapshot_backup` 功能（被 SQLite ACID+WAL 覆盖，30GB 递归 bug 根因）

3. **RULE-EIGHTEEN 连续两次零问题闭环**（commit: `9c5737a6`）

4. **P3-H 清理 59 个幽灵节点 + 重生成 53 域文档**（commit: `9171ca5e`）

5. **F2/F3 SQLite 同名合并调查登记**（commit: `b141520a`，未实际合并）

## 四、关键治本文件清单（硬约束变化，AI 必读）

> 以下文件是 **硬约束变化**——其他 AI 接续工作时必须知道的新规则。
> 完整文件清单请用 §二 的命令自行查询。

### 4.1 项目宪法与门禁配置（5 个，必读）

| 文件 | 关键变化 |
|------|---------|
| [AGENTS.md](file:///d:/ZephyrAlpha/AGENTS.md) | §11.4 新增「数据库连接函数真源冲突治本」+ F2/F3 SQLite 同名合并遗留项；L385 新增 `test_vms_full_e2e.py` 治本记录；另：新增 **GATE-COMMIT-GW 裸 commit 检测门禁**文档（独立任务·命名规则补全 C级，双层防御：pre-commit 阻断 + post-commit 审计 reconciler） |
| [.pre-commit-config.yaml](file:///d:/ZephyrAlpha/.pre-commit-config.yaml) | 新增 `GATE-VMS-SSOT` 钩子注册；另：新增 `gate-commit-gw` 钩子注册（独立任务·命名规则补全 C级，阻断裸 `git commit`） |
| [.trae/rules/onboarding_detail.md](file:///d:/ZephyrAlpha/.trae/rules/onboarding_detail.md) | 规则同步 |
| [.trae/rules/project_rules.md](file:///d:/ZephyrAlpha/.trae/rules/project_rules.md) | 规则同步 |
| [docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml) | 新增 `depgraph_pg_connection` + `sqlite_db_connection` 两条 capability 注册 |

### 4.2 数据库连接真源治本（6 个，必读）

| 文件 | 关键变化 |
|------|---------|
| [src/zephyr/governance/depgraph_schema.py](file:///d:/ZephyrAlpha/src/zephyr/governance/depgraph_schema.py) | **F1 真源改名**：`get_db_connection` → `get_depgraph_pg_connection`（保留 deprecation 别名） |
| [scripts/governance/_shared/constants.py](file:///d:/ZephyrAlpha/scripts/governance/_shared/constants.py) | **F4 无限递归治本**：import 别名 `_get_depgraph_pg_connection_from_depgraph_schema` |
| [scripts/governance/d3_metadata/check_naming_convention.py](file:///d:/ZephyrAlpha/scripts/governance/d3_metadata/check_naming_convention.py) | **N-17 BOM 治本**：抽取 `_read_text_bom_safe` 公共函数，6 处 .py 读取统一替换；另：**命名规则补全**（独立任务）——A级 全库覆盖（`check_new_files_naming` scopes=None，不再限定 tests/docs/src/scripts）+ B级 修改文件历史豁免（`check_new_files_full` step2：HEAD vs 工作区 `check_file` 差集，只阻断本次修改新引入的违规，HEAD 中已有历史违规不阻断） |
| [src/zephyr/governance/rule_engine.py](file:///d:/ZephyrAlpha/src/zephyr/governance/rule_engine.py) | 适配 F1 改名（N-17 触发文件） |
| [src/zephyr/governance/database_service.py](file:///d:/ZephyrAlpha/src/zephyr/governance/database_service.py) | 适配 F1 改名 |
| [tests/unit/test_vocab_sync_chain.py](file:///d:/ZephyrAlpha/tests/unit/test_vocab_sync_chain.py) | **新增 `test_f4_wrapper_no_infinite_recursion` 防回归测试** |

### 4.3 VMS 治本（核心文件，必读）

| 文件 | 关键变化 |
|------|---------|
| [scripts/governance/d5_architecture/checkers/check_vms_ssot.py](file:///d:/ZephyrAlpha/scripts/governance/d5_architecture/checkers/check_vms_ssot.py) | **新增 GATE-VMS-SSOT 门禁**（A）：AST 扫描检测 VMS 漂移副本重建 |
| [src/zephyr/integration/vector_memory/collection_manager.py](file:///d:/ZephyrAlpha/src/zephyr/integration/vector_memory/collection_manager.py) | write_with_provenance 加 doc_id + col.add→col.upsert 治本幂等缺陷 |
| [src/zephyr/integration/vector_memory/faiss_collection_manager.py](file:///d:/ZephyrAlpha/src/zephyr/integration/vector_memory/faiss_collection_manager.py) | **删除 write_with_provenance 死代码**（零调用方，签名不兼容） |
| [src/zephyr/integration/vector_memory/in_process_vector_memory.py](file:///d:/ZephyrAlpha/src/zephyr/integration/vector_memory/in_process_vector_memory.py) | last_daily_ts 初始化修复（修启动即触发 snapshot bug） |
| [src/zephyr/integration/vector_memory/bridge_layer.py](file:///d:/ZephyrAlpha/src/zephyr/integration/vector_memory/bridge_layer.py) | 5 处补确定性 doc_id |
| ~~scripts/governance/vms_snapshot_backup.py~~ | **删除**（snapshot 功能被 SQLite ACID+WAL 覆盖） |
| ~~src/zephyr/governance/vector_memory/~~（整包 26 文件） | **整包删除**（漂移副本，integration/vector_memory/ 是唯一真源） |

### 4.4 蓝图文档（4 个，必读）

| 文件 | 关键变化 |
|------|---------|
| [docs/03_modules/_cross_layer/database/blueprint.md](file:///d:/ZephyrAlpha/docs/03_modules/_cross_layer/database/blueprint.md) | v4.0.2，P2 迁移后蓝图更新 |
| [docs/03_modules/_cross_layer/database/sub_blueprints/mod_inf_012b_p2_postgresql_migration.md](file:///d:/ZephyrAlpha/docs/03_modules/_cross_layer/database/sub_blueprints/mod_inf_012b_p2_postgresql_migration.md) | P2 迁移施工蓝图 |
| [docs/03_modules/_cross_layer/audit_orchestrator/blueprint.md](file:///d:/ZephyrAlpha/docs/03_modules/_cross_layer/audit_orchestrator/blueprint.md) | 蓝图同步 |
| [docs/03_modules/_domain_knowledge/vector_memory/blueprint.md](file:///d:/ZephyrAlpha/docs/03_modules/_domain_knowledge/vector_memory/blueprint.md) | VMS 真源路径更新 |

## 五、并发 AI 接续工作时必须遵守的硬约束

> 以下硬约束本次迁移已落实，其他 AI 不得违反

### 5.1 数据库连接函数真源（AGENTS.md §11.4）

- **PG 连接真源**：`src/zephyr/governance/depgraph_schema.py::get_depgraph_pg_connection`（F1）
- **PG wrapper**：`scripts/governance/_shared/constants.py::get_depgraph_pg_connection`（F4，调用 F1 真源，通过 import 别名避免无限递归）
- **SQLite 连接真源**：`src/zephyr/governance/db_utils.py::get_db_connection`（F2，canonical_override 暂指 F3）
- **禁止**：任何新代码不得再创建同名 `get_db_connection` / `get_depgraph_pg_connection` 函数
- **查询入口**：`CapabilityLookup.find("pg connection")` / `find("sqlite connection")`

### 5.2 VMS 真源唯一

- **VMS 真源**：`src/zephyr/integration/vector_memory/`（唯一合法路径）
- **禁止**：在 `src/zephyr/governance/vector_memory/` 重建任何文件
- **门禁**：`GATE-VMS-SSOT` pre-commit 钩子，AST 扫描检测漂移副本重建，`--ci` 硬阻断
- **snapshot 功能已删除**：被 SQLite ACID+WAL 覆盖，禁止重建 `vms_snapshot_backup.py`
- **write_with_provenance 死代码已删除**：FAISS 启用时按 CollectionManager 真源签名重新实现，禁止在 `faiss_collection_manager.py` 重建该方法名

### 5.3 BOM 安全读取

- 所有读取 .py 文件做正则匹配的场景必须使用 `utf-8-sig` 编码（自动剥离 BOM）
- 公共函数：`scripts/governance/d3_metadata/check_naming_convention.py::_read_text_bom_safe`
- **禁止**：直接使用 `read_text(encoding="utf-8")` 读取可能含 BOM 的文件做正则匹配

### 5.4 F4 wrapper 防递归

- `scripts/governance/_shared/constants.py` 的 `get_depgraph_pg_connection` wrapper 必须调用 F1 真源（通过 import 别名），不得调用自己
- 防回归测试：`tests/unit/test_vocab_sync_chain.py::test_f4_wrapper_no_infinite_recursion`

### 5.5 遗留未合并事项（独立任务卡，不在本次范围）

- **F2/F3 SQLite 同名合并**：83 调用点，事务行为差异（F2=autocommit vs F3=deferred），需独立任务卡
- **F4 wrapper 消除（方案 C）**：长期应让 F1 直接返回带 execute 方法的对象，消除 wrapper 过渡期产物

## 六、AI 接续工作检查清单

并发 AI 恢复工作前，建议执行以下检查：

```bash
# 1. 拉取最新代码（确保在 0a948902db 之后）
git log --oneline -5

# 2. 确认 GitCommitGateway 守护进程运行
python scripts/lock_files.py cleanup && python scripts/ide_health_service.py --status

# 3. 确认 VMS 真源路径（应返回 integration/vector_memory/）
python -c "from zephyr.governance.capability_lookup import CapabilityLookup; r = CapabilityLookup(); print(r.find('vms memory'))"

# 4. 确认数据库连接真源
python -c "from zephyr.governance.capability_lookup import CapabilityLookup; r = CapabilityLookup(); print(r.find('pg connection'))"

# 5. 跑防回归测试
python -m pytest tests/unit/test_vocab_sync_chain.py::test_f4_wrapper_no_infinite_recursion -v

# 6. 查询本次迁移对自己关心的目录的影响
git diff --name-status 0a948902db^..HEAD -- <你关心的目录路径>
```

## 七、文档真源与重新生成

- **本清单真源**：`git diff --name-status 0a948902db^..HEAD`（命令输出唯一真源）
- **起点 commit**：`0a948902db`（不变量，永远有效）
- **若清单与 git diff 不一致**：以 `git diff` 实时输出为准
- **本手册不维护静态文件清单**：避免死数据 + 漂移风险，符合"向内收"原则——git 本身就是现成的查询工具

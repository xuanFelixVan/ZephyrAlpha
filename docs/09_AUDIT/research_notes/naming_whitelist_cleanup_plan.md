# 命名规范白名单清理施工方案

> 创建时间: 2026-06-24
> 审查轮次: R8（零问题确认第2次，连续两次零问题，审查完成）
> 触发: 用户审查命名规则白名单后发现项目自定义文件未统一为 snake_case
> 目标: 将白名单中的项目自定义文件/目录统一为 snake_case，清理无效白名单条目
> 规则真源: trae_028_doc_structure_naming.yaml GOV-DOC-003 v3.0.0

---

## 1. 概述

### 1.1 背景

2026-06-19 项目统一命名规则为 snake_case（GOV-DOC-003 v3.0.0），但部分项目自定义文件通过白名单豁免，未统一为下划线。本次施工将这些豁免项统一为 snake_case，并清理无效白名单条目。

### 1.2 施工范围

| 类别 | 数量 | 说明 |
|------|:---:|------|
| 文件改名 | 2 | ARCHITECTURE_LOCK.yaml / SCOPE.yaml |
| 文件删除 | 1 | SHARED-QUICKREF.yml（旧副本，新副本 shared_quickref.yaml 已存在于 api/） |
| 引用修正 | 1 | session-logs → session_logs（磁盘已为下划线，代码引用未同步） |
| 白名单清理 | 9 | 5个不存在的文件 + 3个不存在的目录 + 1个误入kebab列表的 test_dir |

### 1.3 不在范围内（保留不改）

| 保留项 | 原因 |
|--------|------|
| AGENTS.md, README.md, CONTRIBUTING.md, SECURITY.md | 外部平台约定 |
| Dockerfile, LICENSE | 外部工具约定 |
| __init__.py, setup.py, conftest.py, __main__.py | Python 语言约定 |
| __pycache__, .git, .venv, node_modules 等 | 工具自动生成 |
| TECH_VERSION_TOKENS（pydantic-v2 等） | 技术栈版本标识，非文件名 |
| session_logs/ 目录内文件 | 历史日志记录，不改 |
| docs/08_knowledge/01_raw_intake/ | 历史知识条目，不改 |
| docs/08_knowledge/04_archived/ | 归档知识，不改 |

---

## 2. 待改项总览

| # | 旧名 | 新名 | 文件位置 | 引用文件数 | 引用次数 | 磁盘状态 | 改动量 |
|---|------|------|---------|:---:|:---:|------|:---:|
| 1 | `ARCHITECTURE_LOCK.yaml` | `architecture_lock.yaml` | `architecture_model/` | 4 | 10 | 存在 | 小 |
| 2 | `SCOPE.yaml` | `scope.yaml` | `architecture_model/` | 18 | 32 | 存在 | 中 |
| 3 | `SHARED-QUICKREF.yml` | 删除（引用指向 `shared_quickref.yaml`） | `src/zephyr/shared/` | 30 | ~110 | 存在（旧副本） | 大 |
| 4 | `session-logs` | `session_logs` | 根目录（引用散布） | ~100 | ~153 | **磁盘已为 session_logs** | 大 |
| 5 | `AGENT.md` 等5项 | 删除白名单条目 | 白名单中 | 0 | 0 | 不存在 | 零 |
| 6 | `architecture-model` 等3项 + `test_dir` | 删除白名单条目 | 白名单中 | 0 | 0 | 不存在 | 零 |

### 2.1 SHARED-QUICKREF.yml 处理说明

**已确认**: `src/zephyr/shared/SHARED-QUICKREF.yml` 和 `src/zephyr/shared/api/shared_quickref.yaml` 是同一文件的两个副本（module_id 均为 MOD-INF-016，version 均为 0.14.0，内容几乎相同）。

**处理方式**: 删除旧副本 `SHARED-QUICKREF.yml`，保留新副本 `shared_quickref.yaml`。所有引用 `SHARED-QUICKREF.yml` 的地方更新为 `shared_quickref.yaml`。

**路径变化**: `src/zephyr/shared/SHARED-QUICKREF.yml` → `src/zephyr/shared/api/shared_quickref.yaml`（目录和扩展名都变了）

---

## 3. 替换规则

### 3.1 字符串替换映射

**替换顺序按字符串长度降序排列**（避免短串先匹配破坏长串）：

| 序号 | 旧字符串 | 新字符串 | 说明 |
|:---:|---------|---------|------|
| 1 | `src/zephyr/shared/SHARED-QUICKREF.yml` | `src/zephyr/shared/api/shared_quickref.yaml` | 完整路径引用 |
| 2 | `ARCHITECTURE_LOCK.yaml` | `architecture_lock.yaml` | 文件名 |
| 3 | `ARCHITECTURE_LOCK_yaml` | `architecture_lock_yaml` | 变量名/实体ID形式 |
| 4 | `SHARED-QUICKREF.yml` | `shared_quickref.yaml` | 文件名（扩展名 .yml→.yaml） |
| 5 | `SHARED-QUICKREF_yml` | `shared_quickref_yaml` | 变量名/ID形式（_yml→_yaml） |
| 6 | `SHARED-QUICKREF` | `shared_quickref` | 纯名称引用 |
| 7 | `ARCHITECTURE_LOCK` | `architecture_lock` | 纯名称引用 |
| 8 | `SCOPE.yaml` | `scope.yaml` | 文件名（**用正则排除 REGISTRY_SCOPE.yaml**） |
| 9 | `session-logs` | `session_logs` | 目录名 |

### 3.2 排除目录（替换脚本不扫描）

| 排除目录 | 原因 |
|---------|------|
| `.git/` | 版本控制 |
| `.aidrafts/` | 草稿区 |
| `.ailocks/` | 锁文件 |
| `session_logs/` | 历史日志不改 |
| `docs/08_knowledge/01_raw_intake/` | 历史知识条目不改 |
| `docs/08_knowledge/04_archived/` | 归档知识不改 |
| `scripts/_archive/` | 归档脚本不改 |
| `data/asset_index/` | 自动生成，改完源文件后重新生成 |
| `data/scans/` | 自动生成 |
| `data/classified/` | 自动生成 |
| `data/security_baselines/` | 自动生成缓存 |

### 3.3 特殊处理

| 项 | 处理方式 | 原因 |
|---|---------|------|
| `REGISTRY_SCOPE.yaml` | **不替换**（用正则 `(?<!REGISTRY_)SCOPE\.yaml`） | 不同文件，子串匹配需排除 |
| `SCOPE_YAML` 常量名 | **保留** | Python 常量约定全大写（PEP 8） |
| `SHARED-QUICKREF.yml` | **删除文件**，引用指向 `shared_quickref.yaml` | 已确认是旧副本 |
| session_logs/ 内文件引用的 `session-logs` | **不改** | 历史记录 |
| docs/08_knowledge/ 引用 | **不改** | 历史知识条目 |
| `.runtime/session-logs` | **替换**（目录不存在，但代码引用需改） | 已确认目录不存在 |
| `docs/19_development_workspace/session-logs/` | **替换**（路径不存在，文档引用需改） | 已确认路径不存在 |

### 3.4 depgraph.db 更新方法

depgraph.db 是 SQLite 二进制数据库，不能文本替换。更新方法：

```bash
# 备份（必须先执行，依据 trae_054 STEP0）
git add data/databases/depgraph.db
git commit -m "backup: depgraph before naming cleanup"

# SQL UPDATE（表名 nodes，字段 path）
sqlite3 data/databases/depgraph.db "UPDATE nodes SET path = REPLACE(path, 'ARCHITECTURE_LOCK.yaml', 'architecture_lock.yaml') WHERE path LIKE '%ARCHITECTURE_LOCK.yaml%';"
sqlite3 data/databases/depgraph.db "UPDATE nodes SET path = REPLACE(path, 'SHARED-QUICKREF.yml', 'shared_quickref.yaml') WHERE path LIKE '%SHARED-QUICKREF.yml%';"
sqlite3 data/databases/depgraph.db "UPDATE nodes SET path = REPLACE(path, 'session-logs', 'session_logs') WHERE path LIKE '%session-logs%';"
# SCOPE.yaml 需排除 REGISTRY_SCOPE.yaml
sqlite3 data/databases/depgraph.db "UPDATE nodes SET path = REPLACE(path, 'SCOPE.yaml', 'scope.yaml') WHERE path LIKE '%SCOPE.yaml%' AND path NOT LIKE '%REGISTRY_SCOPE.yaml%';"

# 更新后重新生成 asset_index（⚠️ 架构升级期间禁止运行 generate_project_depgraph.py，仅运行 path_tree）
python d:/ZephyrAlpha/scripts/governance/generate_project_path_tree.py --write
# 正常期（非架构升级期间）才运行：
# python d:/ZephyrAlpha/scripts/governance/generate_project_depgraph.py --max-workers 8
```

**注**: `apply_depgraph.py --update-path MODULE_ID NEW_PATH` 按 module_id 匹配，适用于有 module_id 的文件（如 SHARED-QUICKREF.yml = MOD-INF-016），但不适用于 ARCHITECTURE_LOCK.yaml/SCOPE.yaml（无单独 module_id）。统一用 SQL UPDATE 更简单。

---

## 4. 执行顺序

### 4.0 施工前准备

**执行目录**: 所有命令在项目根目录 `d:/ZephyrAlpha` 下执行。git 命令中的路径是相对于仓库根目录的标准用法。

**文件锁处理**（RULE-ZERO）: 替换脚本修改大量文件，逐个加锁不现实。采用以下策略：
- Phase 1（白名单清理）: 手动编辑，逐文件加锁
- Phase 2（git mv/rm）: git 操作不需要文件锁
- Phase 3（内容替换）: 替换脚本批量修改，施工前确认无其他 AI session 活跃（`python d:/ZephyrAlpha/scripts/lock_files.py status`），然后直接执行
- Phase 4（白名单更新）: 手动编辑，逐文件加锁
- Phase 5（depgraph 更新）: SQL 操作不需要文件锁

**git 提交**（RULE-TWENTY）: 每个 Phase 完成后必须 git commit，禁止累积多个 Phase 后一次性提交。

### Phase 1: 白名单清理（零成本，零风险）

**操作**: 删除不存在的白名单条目

| 文件 | 删除条目 |
|------|---------|
| `scripts/governance/d3_metadata/check_naming_convention.py` | `AGENT.md`, `SKILL.md`, `MAKEFILE`, `PKG_INFO`, `SOURCES.txt`（FILENAME_UPPERCASE_WHITELIST） |
| `scripts/governance/d3_metadata/check_naming_convention.py` | `architecture-model`, `target-architecture`, `cross-cutting`, `test_dir`（_DIR_ROOT_KEBAB_EXEMPT） |
| `scripts/governance/rename_kebab_to_snake.py` | 同上（UPPERCASE_WHITELIST） |

**验证**: `python d:/ZephyrAlpha/scripts/governance/d3_metadata/check_naming_convention.py --warn-only`

**提交**: `git add scripts/governance/d3_metadata/check_naming_convention.py scripts/governance/rename_kebab_to_snake.py && git commit -m "phase1: cleanup nonexistent whitelist entries"`

### Phase 2: 文件改名/删除（git mv / git rm）

```bash
# ARCHITECTURE_LOCK.yaml → architecture_lock.yaml
git mv d:/ZephyrAlpha/architecture_model/ARCHITECTURE_LOCK.yaml d:/ZephyrAlpha/architecture_model/architecture_lock.yaml

# SCOPE.yaml → scope.yaml
git mv d:/ZephyrAlpha/architecture_model/SCOPE.yaml d:/ZephyrAlpha/architecture_model/scope.yaml

# SHARED-QUICKREF.yml → 删除（旧副本，新副本 shared_quickref.yaml 已存在于 api/）
git rm d:/ZephyrAlpha/src/zephyr/shared/SHARED-QUICKREF.yml

# session-logs → session_logs：磁盘已经是 session_logs，不需要 git mv
```

**中间验证**: 确认文件改名成功（用 Python 脚本，禁止内联 `python -c`）
```bash
python d:/ZephyrAlpha/scripts/governance/verify_phase2_rename.py
```
验证脚本内容（需先用 scaffold.py 创建）：
```python
from pathlib import Path
assert Path("d:/ZephyrAlpha/architecture_model/architecture_lock.yaml").exists()
assert Path("d:/ZephyrAlpha/architecture_model/scope.yaml").exists()
assert Path("d:/ZephyrAlpha/src/zephyr/shared/api/shared_quickref.yaml").exists()
assert not Path("d:/ZephyrAlpha/src/zephyr/shared/SHARED-QUICKREF.yml").exists()
print("Phase 2 OK")
```

**提交**: `git commit -m "phase2: rename ARCHITECTURE_LOCK.yaml/SCOPE.yaml, remove SHARED-QUICKREF.yml"`（git mv/rm 已自动暂存）

### Phase 3: 内容替换（脚本全文替换）

用 Python 脚本遍历项目所有文件，按 3.1 的替换映射做精确字符串替换。

**先 dry-run 预览**:
```bash
python d:/ZephyrAlpha/scripts/governance/rename_whitelist_cleanup.py --dry-run
```

**确认 dry-run 输出**: 检查输出的文件列表和替换次数是否符合预期（对照 §5 详细引用清单）。重点关注白名单文件（check_naming_convention.py, rename_kebab_to_snake.py）中的旧名会被替换为新名——这是预期行为，Phase 4 会删除这些新名条目。

**确认无误后执行**:
```bash
python d:/ZephyrAlpha/scripts/governance/rename_whitelist_cleanup.py
```

替换脚本框架见 §6。

**中间验证**: 确认无残留
```bash
python d:/ZephyrAlpha/scripts/governance/rename_whitelist_cleanup.py --verify
```

**提交**: `git add scripts/ src/ docs/ tests/ && git commit -m "phase3: replace all references to renamed files"`（⚠️ 确保这些目录下没有其他未提交的修改）

### Phase 4: 白名单更新

**注**: Phase 3 的替换脚本会遍历白名单文件，将旧名（如 `ARCHITECTURE_LOCK.yaml`）替换为新名（如 `architecture_lock.yaml`）。因此 Phase 4 需删除的是**已被替换的新名条目**（snake_case 文件不需要大写白名单豁免）。

| 文件 | 操作 |
|------|------|
| `check_naming_convention.py` | 从 FILENAME_UPPERCASE_WHITELIST 删除 `architecture_lock.yaml`, `scope.yaml`, `shared_quickref.yaml`（Phase 3 已替换旧名）；从 _DATA_FILE_EXEMPT_NAMES 删除同名条目；从 _DIR_ROOT_KEBAB_EXEMPT 删除 `session_logs`（Phase 3 已从 `session-logs` 替换） |
| `rename_kebab_to_snake.py` | 从 UPPERCASE_WHITELIST 删除同名条目（Phase 3 已替换） |
| `verify_file_paths.py` | 更新路径列表：`SHARED-QUICKREF.yml` → `api/shared_quickref.yaml`（Phase 3 已替换路径，此处确认无残留） |

**提交**: `git add scripts/governance/d3_metadata/check_naming_convention.py scripts/governance/rename_kebab_to_snake.py scripts/governance/verify_file_paths.py && git commit -m "phase4: update whitelists after rename"`

### Phase 5: depgraph 更新

```bash
# 备份（必须先执行，依据 trae_054 STEP0）
git add data/databases/depgraph.db
git commit -m "backup: depgraph before naming cleanup"

# 更新路径记录（见 §3.4 SQL UPDATE）
sqlite3 data/databases/depgraph.db "UPDATE nodes SET path = REPLACE(path, 'ARCHITECTURE_LOCK.yaml', 'architecture_lock.yaml') WHERE path LIKE '%ARCHITECTURE_LOCK.yaml%';"
sqlite3 data/databases/depgraph.db "UPDATE nodes SET path = REPLACE(path, 'SHARED-QUICKREF.yml', 'shared_quickref.yaml') WHERE path LIKE '%SHARED-QUICKREF.yml%';"
sqlite3 data/databases/depgraph.db "UPDATE nodes SET path = REPLACE(path, 'session-logs', 'session_logs') WHERE path LIKE '%session-logs%';"
sqlite3 data/databases/depgraph.db "UPDATE nodes SET path = REPLACE(path, 'SCOPE.yaml', 'scope.yaml') WHERE path LIKE '%SCOPE.yaml%' AND path NOT LIKE '%REGISTRY_SCOPE.yaml%';"

# 重新生成 path_tree（⚠️ 架构升级期间禁止运行 generate_project_depgraph.py）
python d:/ZephyrAlpha/scripts/governance/generate_project_path_tree.py --write
# 正常期才运行：python d:/ZephyrAlpha/scripts/governance/generate_project_depgraph.py --max-workers 8
```

**提交**: `git add data/databases/depgraph.db data/asset_index/ && git commit -m "phase5: update depgraph paths after rename"`

### Phase 6: 验证

```bash
# 1. 命名检测器
python d:/ZephyrAlpha/scripts/governance/d3_metadata/check_naming_convention.py --warn-only

# 2. 路径验证
python d:/ZephyrAlpha/scripts/governance/verify_file_paths.py

# 3. 依赖图诊断
python d:/ZephyrAlpha/scripts/governance/diagnose_depgraph.py

# 4. 注册审计
python d:/ZephyrAlpha/scripts/governance/audit_registration.py

# 5. 关键模块导入测试
python d:/ZephyrAlpha/scripts/governance/verify_key_imports.py

# 6. 测试收集
python -m pytest tests/ --collect-only -q

# 7. session连续性测试
python -m pytest tests/test_session_continuity_core_root.py tests/test_session_continuity_session.py -v

# 8. 命名门禁测试
python -m pytest tests/unit/test_gate11_naming_convention_unit.py -v

# 9. 残留检查（用 Python 脚本，不用 grep 命令）
python d:/ZephyrAlpha/scripts/governance/rename_whitelist_cleanup.py --verify
```

---

## 5. 详细引用清单

### 5.1 ARCHITECTURE_LOCK.yaml → architecture_lock.yaml

**文件位置**: `architecture_model/ARCHITECTURE_LOCK.yaml`
**引用总数**: 10处，4个文件

| 文件路径 | 行号 | 引用类型 | 行内容摘要 |
|---------|:---:|---------|-----------|
| `architecture_model/ARCHITECTURE_LOCK.yaml` | 149 | 自引用 | 修改锁定文件但不检查 ARCHITECTURE_LOCK.yaml |
| `architecture_model/ARCHITECTURE_LOCK.yaml` | 151 | 自引用 | 删除或修改 ARCHITECTURE_LOCK.yaml 本身（仅 Owner 可修改） |
| `architecture_model/ARCHITECTURE_LOCK.yaml` | 167 | 自引用 | ARCHITECTURE_LOCK.yaml = 轻量级 CAB（1人版） |
| `data/asset_index/project_entity_depgraph.yaml` | 114149 | 实体ID | `architecture_model__ARCHITECTURE_LOCK_yaml:` |
| `data/asset_index/project_entity_depgraph.yaml` | 114150 | 实体ID | `id: architecture_model__ARCHITECTURE_LOCK_yaml` |
| `data/asset_index/project_entity_depgraph.yaml` | 114151 | 路径 | `path: architecture_model/ARCHITECTURE_LOCK.yaml` |
| `scripts/governance/rename_kebab_to_snake.py` | 14 | 注释 | ARCHITECTURE_LOCK.yaml 等大写白名单不改 |
| `scripts/governance/rename_kebab_to_snake.py` | 75 | 白名单 | `"ARCHITECTURE_LOCK.yaml",` |
| `scripts/governance/d3_metadata/check_naming_convention.py` | 60 | 白名单 | `"ARCHITECTURE_LOCK.yaml",` |
| `scripts/governance/d3_metadata/check_naming_convention.py` | 588 | 白名单 | `"ARCHITECTURE_LOCK.yaml",` |

**注意**: `data/asset_index/` 是自动生成的，改完源文件后重新生成即可，不需手动改。

### 5.2 SCOPE.yaml → scope.yaml

**文件位置**: `architecture_model/SCOPE.yaml`
**引用总数**: 32处，约18个文件

#### 白名单条目（3处）

| 文件路径 | 行号 | 行内容摘要 |
|---------|:---:|-----------|
| `scripts/governance/rename_kebab_to_snake.py` | 77 | `"SCOPE.yaml"` 在 UPPERCASE_WHITELIST |
| `scripts/governance/d3_metadata/check_naming_convention.py` | 61 | `"SCOPE.yaml"` 白名单 |
| `scripts/governance/d3_metadata/check_naming_convention.py` | 589 | `"SCOPE.yaml"` 白名单（第二处） |

#### 路径引用/变量名（3处）

| 文件路径 | 行号 | 行内容摘要 |
|---------|:---:|-----------|
| `scripts/governance/d5_architecture/checkers/check_dual_tree_sync.py` | 66 | `SCOPE_YAML = IMPL_TREE / "SCOPE.yaml"` |
| `docs/01_policies_and_standards/_registry/catalogs/document_metadata_index_registry.yaml` | 18 | `index.md → architecture_model/SCOPE.yaml` |
| `data/asset_index/project_entity_depgraph.yaml` | 114177 | `path: architecture_model/SCOPE.yaml` |

#### 代码注释/错误消息（10处，均在 check_dual_tree_sync.py）

| 文件路径 | 行号 | 行内容摘要 |
|---------|:---:|-----------|
| `scripts/governance/d5_architecture/checkers/check_dual_tree_sync.py` | 17 | 注释：P2 检查与 SCOPE.yaml R3 关系 |
| 同上 | 22 | 注释：`architecture-model/SCOPE.yaml R1/R2/R3` |
| 同上 | 70 | 注释：SCOPE.yaml R3 允许两侧不同文件名 |
| 同上 | 148 | 错误消息：违反 SCOPE.yaml R3 |
| 同上 | 160 | 错误消息：违反 SCOPE.yaml R3 |
| 同上 | 166 | 注释：P0 检查与 SCOPE.yaml R4 关系 |
| 同上 | 192 | 错误消息：SCOPE.yaml R4 禁止 EA 树镜像 B 轨 |
| 同上 | 250 | 提示消息：有意设计，SCOPE.yaml R3 允许 |
| 同上 | 271 | 注释：P0: SCOPE.yaml 必须存在 |
| 同上 | 295 | 检查项名称：`("SCOPE.yaml 存在性", ...)` |

#### 文档提及（16处）

| 文件路径 | 行号 | 行内容摘要 |
|---------|:---:|-----------|
| `docs/09_audit/research_notes/blueprint_discussion_audit_division_plan.md` | 6 | 审计方案列出 SCOPE.yaml |
| `docs/02_enterprise_architecture/target_architecture/revision_history.md` | 36 | 双树读法与 SCOPE.yaml 对齐 |
| `docs/02_enterprise_architecture/target_architecture/architecture_model/readme.md` | 10 | architecture_model/ 含 SCOPE.yaml |
| `docs/02_enterprise_architecture/ssot_authority_map.md` | 37 | 双树声明对齐 SCOPE.yaml |
| `docs/02_enterprise_architecture/ssot_authority_map.md` | 44 | 必须先读 SCOPE.yaml |
| `docs/02_enterprise_architecture/ssot_authority_map.md` | 274 | 修订记录 |
| `architecture_model/technology_landscape.yaml` | 8 | 注释：参考 SCOPE.yaml |
| `docs/03_modules/specs/auto_runtime_core/spec.md` | 270 | 表格行：SCOPE.yaml |
| `docs/08_knowledge/01_raw_intake/ke-041-canonical_ssot_arc.md` | 12, 21 | 知识条目引用（不改） |
| `docs/08_knowledge/01_raw_intake/ke-066-what_is_this_document_set.md` | 20, 32 | 架构描述集说明（不改） |
| `docs/08_knowledge/01_raw_intake/ke-642-d_align_yaml.md` | 20 | B 轨对齐说明（不改） |
| `docs/08_knowledge/01_raw_intake/ke-635-architecture_model.md` | 14 | 施工真源说明（不改） |
| `docs/08_knowledge/01_raw_intake/ke-672-layer_authority.md` | 12, 19 | 双树声明对齐（不改） |

**注意**: `docs/08_knowledge/01_raw_intake/` 下的引用不改（历史知识条目）。

### 5.3 SHARED-QUICKREF.yml → 删除（引用指向 shared_quickref.yaml）

**旧文件位置**: `src/zephyr/shared/SHARED-QUICKREF.yml`（删除）
**新文件位置**: `src/zephyr/shared/api/shared_quickref.yaml`（保留）
**引用总数**: ~110处，约30个文件

**已确认**: 两者 module_id 均为 MOD-INF-016，version 均为 0.14.0，内容几乎相同。`shared_quickref.yaml` 是已迁移到 snake_case 的版本。

#### 白名单/映射条目（6处）

| 文件路径 | 行号 | 行内容摘要 |
|---------|:---:|-----------|
| `scripts/governance/verify_file_paths.py` | 40 | `"src/zephyr/shared/SHARED-QUICKREF.yml"` |
| `scripts/governance/rename_kebab_to_snake.py` | 14 | 注释 |
| `scripts/governance/rename_kebab_to_snake.py` | 76 | `"SHARED-QUICKREF.yml"` 白名单 |
| `scripts/governance/d3_metadata/check_naming_convention.py` | 67 | 白名单 |
| `scripts/governance/d3_metadata/check_naming_convention.py` | 595 | 白名单（第二处） |
| `scripts/governance/dm105_depgraph_triage.py` | 239 | 归属裁定映射 |

#### 注册表/清单（2处）

| 文件路径 | 行号 | 行内容摘要 |
|---------|:---:|-----------|
| `docs/01_policies_and_standards/_registry/catalogs/project_path_tree.yaml` | 5823 | 文件清单 |
| `docs/03_modules/_manifests/shared_manifest.md` | 11 | 模块清单 |

#### 蓝图文档引用（14处）

| 文件路径 | 行号 | 行内容摘要 |
|---------|:---:|-----------|
| `docs/02_enterprise_architecture/02_domain_architecture_docs/15_d_shared.md` | 44, 260 | 域资产表 + mermaid 图 |
| `docs/03_modules/_cross_layer/shared_core/shared_infra_blueprint.md` | 47 | 关键文件列表 |
| `docs/03_modules/_cross_layer/shared_core/blueprint.md` | 150, 180, 418, 645, 653, 959, 964, 1142 | 8处引用（AD-005决策等） |
| `docs/03_modules/_cross_layer/mcp_servers/blueprint.md` | 354 | MCP Server 消费者注册 |
| `docs/03_modules/_cross_layer/feedback_loop/blueprint.md` | 726 | 接口契约变更 |
| `docs/03_modules/_domain_autonomy_core/agent_rbac/adversarial_test_report.yaml` | 107 | 统一 resolution |

#### 自动生成数据（~75处，改完源文件后重新生成）

| 文件路径 | 引用次数 | 说明 |
|---------|:---:|------|
| `data/asset_index/target_path_tree.yaml` | 4 | 路径树 |
| `data/asset_index/project_entity_depgraph_v3_domain_draft.yaml` | ~40 | 依赖图草稿 |
| `data/asset_index/project_entity_depgraph.yaml` | ~25 | 依赖图 |
| `data/classified/classified_assets.json` | 1 | 分类资产 |
| `data/scans/raw_asset_scan.json` | 3 | 原始扫描 |
| `data/security_baselines/scan_mtime_cache.json` | 1 | mtime缓存 |

### 5.4 session-logs → session_logs

**磁盘状态**: 目录已经是 `session_logs`（下划线）
**代码状态**: 代码中引用 `session-logs`（kebab），**与磁盘不一致**
**引用总数**: ~153处，~100个文件

**关键风险**: 14处硬编码路径构造 `PROJECT_ROOT / "session-logs"` 在运行时指向不存在的目录。

#### 硬编码路径构造（14处，必须修改）

| 文件路径 | 行号 | 行内容摘要 |
|---------|:---:|-----------|
| `scripts/record_session_start_commit.py` | 71 | `session_dir = PROJECT_ROOT / "session-logs" / session_id` |
| `scripts/context/generate_architecture_context.py` | 271 | `session_dir = REPO_ROOT / "session-logs"` |
| `scripts/governance/meta/validate_emergency_bypass_log.py` | 49 | `SESSION_LOGS_DIR = REPO_ROOT / "session-logs"` |
| `scripts/governance/d5_architecture/checkers/check_architecture_gates.py` | 923 | `logs_dir = REPO_ROOT / "session-logs"` |
| `scripts/governance/d5_architecture/validators/validate_blind_spot_status.py` | 220 | `index_path = repo_root / "session-logs" / "index.yaml"` |
| `scripts/governance/d5_architecture/validators/session/validate_session_log_index_integrity.py` | 65 | `SESSION_LOGS_DIR = REPO_ROOT / "session-logs"` |
| `scripts/governance/d5_architecture/validators/session/validate_session_log_updated.py` | 47 | `SESSION_LOG_DIR = REPO_ROOT / ".runtime" / "session-logs"` |
| `src/zephyr/shared/session/session_continuity.py` | 64 | `self._sessions_dir = self._project_root / "session-logs"` |
| `src/zephyr/infrastructure/asset_inventory/dashboard.py` | 207 | `target = ... / "session-logs" / "_asset_handoff.txt"` |
| `src/zephyr/infrastructure/rollback/phase_check_registry.py` | 93 | `log_dir = _PROJECT_ROOT / "session-logs"` |
| `src/zephyr/governance/dashboard.py` | 210 | `target = ... / "session-logs" / "_asset_handoff.txt"` |
| `src/zephyr/governance/phase_check_registry.py` | 92 | `log_dir = _PROJECT_ROOT / "session-logs"` |
| `src/zephyr/governance/ops_governance/phase_check_registry.py` | 111 | `log_dir = _PROJECT_ROOT / "session-logs"` |
| `src/zephyr/governance/rule_enforcement/invariants/post_doc_review_check.py` | 217 | `self._session_log_dir = project_root / "session-logs"` |

#### 排除列表/glob模式/检查规则（22处）

| 文件路径 | 行号 | 引用类型 |
|---------|:---:|---------|
| `scripts/governance/generate_project_depgraph.py` | 57 | 排除列表 |
| `scripts/governance/audit_registration.py` | 68 | 排除列表 |
| `scripts/governance/d7_code/validate_python_syntax.py` | 43 | 排除列表 |
| `scripts/governance/d3_metadata/check_naming_convention.py` | 405, 799, 801 | 排除列表+路径检查 |
| `src/zephyr/infrastructure/asset_inventory/scanner.py` | 76, 416 | 排除列表+排除集合 |
| `src/zephyr/governance/scanner.py` | 76, 417 | 排除列表+排除集合 |
| `src/zephyr/governance/kb/bootstrap.py` | 343, 344 | glob模式 |
| `src/zephyr/governance/rule_enforcement/invariants/post_doc_review_check.py` | 332 | 路径过滤 |
| `src/zephyr/security/adversarial_validation/steady_state.py` | 57 | 检查规则 |
| `src/zephyr/security/adversarial_validation/constitution_guard.py` | 178 | 映射 |
| `scripts/governance/meta/validate_emergency_bypass_log.py` | 170 | 字符串 |
| `scripts/governance/d5_architecture/checkers/check_architecture_gates.py` | 927, 936 | 错误消息 |
| `scripts/governance/d5_architecture/validators/validate_blind_spot_status.py` | 222 | 错误消息 |
| `scripts/governance/d5_architecture/validators/session/validate_session_log_updated.py` | 97 | 错误消息 |
| `scripts/governance/d5_architecture/validators/session/validate_session_log_index_integrity.py` | 41, 316 | 描述 |

#### 测试代码（16处）

| 文件路径 | 行号 | 引用类型 |
|---------|:---:|---------|
| `tests/e2e/test_kb_full_pipeline.py` | 94 | 测试断言 |
| `tests/test_kb_bootstrap.py` | 76 | 测试断言 |
| `tests/test_post_doc_review.py` | 73, 289, 303 | 测试路径构造 |
| `tests/test_session_continuity_core_root.py` | 73, 112, 145, 154 | 测试路径构造 |
| `tests/test_session_continuity_session.py` | 72, 125, 134 | 测试路径构造 |
| `tests/unit/core/test_session_continuity_core.py` | 71 | 测试路径构造 |
| `tests/unit/test_session_continuity_unit.py` | 76 | 测试路径构造 |
| `tests/unit/test_gate11_naming_convention_unit.py` | 165 | 测试断言 |
| `tests/unit/governance/test_gate11_naming_convention_governance.py` | 165 | 测试断言 |

#### 配置引用（16处）

| 文件路径 | 行号 | 引用类型 |
|---------|:---:|---------|
| `scripts/governance/script_manifest.yaml` | 1841 | 描述 |
| `data/rule_optimization/key_facts.yaml` | 375 | pattern |
| `docs/01_policies_and_standards/_registry/schemas/session_log_schema.yaml` | 41, 44, 71 | 路径模板 |
| `docs/01_policies_and_standards/_registry/catalogs/depgraph_scan_exclusions.yaml` | 56 | 排除列表 |
| `docs/01_policies_and_standards/_registry/catalogs/ai_session_registry.yaml` | 40, 107 | 路径 |
| `docs/01_policies_and_standards/_registry/vocabularies/terminology_mapping.yaml` | 155 | 术语表 |
| `src/zephyr/shared/SHARED-QUICKREF.yml` | 1247, 1252, 1346 | 描述（文件将删除，引用改指向 shared_quickref.yaml） |
| `src/zephyr/shared/api/shared_quickref.yaml` | 1254, 1259, 1353 | 描述（保留） |

#### 文档提及（39处，不含历史知识条目）

| 文件路径 | 行号 |
|---------|:---:|
| `docs/09_audit/research_notes/blueprint_discussion_audit_division_plan.md` | 6 |
| `docs/03_modules/_master_blueprint/blueprint_baseline.md` | 2296 |
| `docs/02_enterprise_architecture/dependency_architecture_panorama.md` | 1008 |
| `docs/02_enterprise_architecture/architecture_upgrade_discussion.md` | 648 |
| `docs/02_enterprise_architecture/target_architecture/information_architecture.md` | 196, 208 |
| `docs/03_modules/_domain_knowledge/knowledge_base/blueprint.md` | 724, 887, 1345, 1671 |
| `docs/03_modules/_cross_layer/resource_optimization_engine/blueprint.md` | 1728 |
| `docs/03_modules/_domain_infra_ops/asset_inventory/blueprint.md` | 155, 1154, 1433, 1767, 2491, 2509, 3030, 3506 |

### 5.5 白名单清理项（零成本）

#### 不存在的文件（从 FILENAME_UPPERCASE_WHITELIST 删除）

| 白名单条目 | 存在 | 处置 |
|-----------|:---:|------|
| `AGENT.md` | ❌ | 删除白名单条目 |
| `SKILL.md` | ❌ | 删除白名单条目 |
| `MAKEFILE` | ❌ | 删除白名单条目（大小写均不存在） |
| `PKG_INFO` | ❌ | 删除白名单条目（setuptools 未启用） |
| `SOURCES.txt` | ❌ | 删除白名单条目（setuptools 未启用） |

#### 不存在的目录（从 _DIR_ROOT_KEBAB_EXEMPT 删除）

| 白名单条目 | 存在 | 处置 |
|-----------|:---:|------|
| `architecture-model` | ❌ | 删除白名单条目 |
| `target-architecture` | ❌ | 删除白名单条目 |
| `cross-cutting` | ❌ | 删除白名单条目 |
| `test_dir` | ❌ | 删除白名单条目（已是 snake_case，误入 kebab 列表） |

---

## 6. 替换脚本框架

```python
#!/usr/bin/env python3
"""
命名规范白名单清理 - 全文替换脚本
按施工方案 docs/09_audit/research_notes/naming_whitelist_cleanup_plan.md 执行

用法:
  python rename_whitelist_cleanup.py --dry-run    # 预览替换结果（不修改文件）
  python rename_whitelist_cleanup.py              # 执行替换
  python rename_whitelist_cleanup.py --verify     # 验证残留（检查是否还有旧名）
"""
import argparse
import os
import re
from pathlib import Path

PROJECT_ROOT = Path("D:/ZephyrAlpha")

# 替换映射（按字符串长度降序排列，避免短串先匹配破坏长串）
REPLACEMENTS = [
    # 1. 完整路径（最长）
    ("src/zephyr/shared/SHARED-QUICKREF.yml", "src/zephyr/shared/api/shared_quickref.yaml"),
    # 2. 文件名+扩展名
    ("ARCHITECTURE_LOCK.yaml", "architecture_lock.yaml"),
    ("ARCHITECTURE_LOCK_yaml", "architecture_lock_yaml"),
    ("SHARED-QUICKREF.yml", "shared_quickref.yaml"),
    ("SHARED-QUICKREF_yml", "shared_quickref_yaml"),
    # 3. 纯名称
    ("SHARED-QUICKREF", "shared_quickref"),
    ("ARCHITECTURE_LOCK", "architecture_lock"),
    # 4. 目录名
    ("session-logs", "session_logs"),
]

# SCOPE.yaml 用正则替换（排除 REGISTRY_SCOPE.yaml）
SCOPE_PATTERN = re.compile(r'(?<!REGISTRY_)SCOPE\.yaml')

# 排除目录
EXCLUDE_DIRS = {
    ".git", ".aidrafts", ".ailocks", "__pycache__", ".ruff_cache",
    ".mypy_cache", ".pytest_cache", "node_modules", ".venv", "venv",
    ".tox", ".eggs", ".idea", ".vscode", ".trae",
    "session_logs",  # 历史日志不改
    "_archive", "04_archived",
}

# 排除路径前缀
EXCLUDE_PREFIXES = [
    "data/asset_index/",
    "data/scans/",
    "data/classified/",
    "data/security_baselines/",
    "docs/08_knowledge/01_raw_intake/",
    "docs/08_knowledge/04_archived/",
    "scripts/_archive/",
]

TEXT_EXTENSIONS = {".py", ".yaml", ".yml", ".md", ".json", ".txt", ".cfg", ".ini", ".toml"}

def should_skip(rel_path: str) -> bool:
    parts = rel_path.replace("\\", "/").split("/")
    for part in parts:
        if part in EXCLUDE_DIRS:
            return True
    for prefix in EXCLUDE_PREFIXES:
        if rel_path.replace("\\", "/").startswith(prefix):
            return True
    return False

def replace_line(line: str) -> tuple[str, int]:
    """替换一行中的内容，返回 (新行, 替换次数)"""
    count = 0
    new_line = line
    for old, new in REPLACEMENTS:
        if old in new_line:
            count += new_line.count(old)  # 替换前旧串出现次数
            new_line = new_line.replace(old, new)
    # SCOPE.yaml 用正则替换（排除 REGISTRY_SCOPE.yaml）
    new_line, scope_count = SCOPE_PATTERN.subn('scope.yaml', new_line)
    count += scope_count
    return new_line, count

def replace_in_file(file_path: Path, dry_run: bool = False) -> int:
    try:
        # 用二进制读取，保留原始换行符风格（避免 read_text 通用换行符转换）
        raw = file_path.read_bytes()
        content = raw.decode("utf-8-sig")  # 处理 BOM
    except (UnicodeDecodeError, PermissionError):
        return 0

    original = content
    count = 0
    lines = content.split("\n")
    new_lines = []
    for line in lines:
        new_line, line_count = replace_line(line)
        count += line_count
        new_lines.append(new_line)
    content = "\n".join(new_lines)

    if content != original and not dry_run:
        tmp_path = file_path.with_suffix(file_path.suffix + ".tmp")
        # 用二进制写入，保留原始换行符
        tmp_path.write_bytes(content.encode("utf-8"))  # 写入不带 BOM
        os.replace(tmp_path, file_path)

    return count

def verify_residual(file_path: Path) -> list[str]:
    """检查文件中是否还有旧名残留"""
    try:
        content = file_path.read_text(encoding="utf-8-sig")
    except (UnicodeDecodeError, PermissionError):
        return []

    residuals = []
    for old, _ in REPLACEMENTS:
        if old in content:
            residuals.append(old)
    # SCOPE.yaml 检查（排除 REGISTRY_SCOPE.yaml）
    matches = SCOPE_PATTERN.findall(content)
    if matches:
        residuals.append("SCOPE.yaml (excluding REGISTRY_SCOPE.yaml)")
    return residuals

def main():
    parser = argparse.ArgumentParser(description="命名规范白名单清理替换脚本")
    parser.add_argument("--dry-run", action="store_true", help="预览替换结果，不修改文件")
    parser.add_argument("--verify", action="store_true", help="验证残留检查")
    args = parser.parse_args()

    if args.verify:
        # 验证模式：检查是否还有旧名残留
        total_residuals = 0
        for root, dirs, files in os.walk(PROJECT_ROOT):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for fname in files:
                file_path = Path(root) / fname
                rel_path = str(file_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
                if should_skip(rel_path):
                    continue
                ext = file_path.suffix.lower()
                if ext not in TEXT_EXTENSIONS:
                    continue
                residuals = verify_residual(file_path)
                if residuals:
                    total_residuals += 1
                    print(f"  {rel_path}: {residuals}")
        if total_residuals == 0:
            print("验证通过：无残留旧名")
        else:
            print(f"\n发现 {total_residuals} 个文件有残留旧名")
        return

    total_replaced = 0
    files_modified = 0

    for root, dirs, files in os.walk(PROJECT_ROOT):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for fname in files:
            file_path = Path(root) / fname
            rel_path = str(file_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
            if should_skip(rel_path):
                continue
            ext = file_path.suffix.lower()
            if ext not in TEXT_EXTENSIONS:
                continue
            count = replace_in_file(file_path, dry_run=args.dry_run)
            if count > 0:
                files_modified += 1
                total_replaced += count
                mode = "[DRY-RUN] " if args.dry_run else ""
                print(f"  {mode}{rel_path}: {count} replacements")

    mode = "[DRY-RUN] " if args.dry_run else ""
    print(f"\n{mode}总计: {files_modified} 个文件, {total_replaced} 处替换")

if __name__ == "__main__":
    main()
```

---

## 7. 验证命令清单

| # | 验证命令 | 验证内容 | 预期结果 |
|---|---------|---------|---------|
| 1 | `python d:/ZephyrAlpha/scripts/governance/d3_metadata/check_naming_convention.py --warn-only` | 命名规范检测 | exit 0，无 ARCHITECTURE_LOCK/SCOPE/SHARED-QUICKREF 相关警告 |
| 2 | `python d:/ZephyrAlpha/scripts/governance/verify_file_paths.py` | 文件路径验证 | exit 0，无断链 |
| 3 | `python d:/ZephyrAlpha/scripts/governance/diagnose_depgraph.py` | 依赖图诊断 | 无路径不匹配 |
| 4 | `python d:/ZephyrAlpha/scripts/governance/audit_registration.py` | 注册审计 | exit 0，无孤儿 |
| 5 | `python d:/ZephyrAlpha/scripts/governance/verify_key_imports.py` | 关键模块导入 | exit 0 |
| 6 | `python -m pytest tests/ --collect-only -q` | 测试收集 | 无 ImportError |
| 7 | `python -m pytest tests/test_session_continuity_core_root.py tests/test_session_continuity_session.py -v` | session连续性测试 | 全部通过 |
| 8 | `python -m pytest tests/unit/test_gate11_naming_convention_unit.py -v` | 命名门禁测试 | 全部通过 |
| 9 | `python d:/ZephyrAlpha/scripts/governance/rename_whitelist_cleanup.py --verify` | 残留检查 | 无残留旧名 |

---

## 8. 回滚方案

### 8.1 回滚步骤

```bash
# 0. 回滚前提检查
python d:/ZephyrAlpha/scripts/rollback.py preflight
python d:/ZephyrAlpha/scripts/lock_files.py status

# 1. 回滚文件改名/删除（git mv / git rm 回滚）
git mv d:/ZephyrAlpha/architecture_model/architecture_lock.yaml d:/ZephyrAlpha/architecture_model/ARCHITECTURE_LOCK.yaml
git mv d:/ZephyrAlpha/architecture_model/scope.yaml d:/ZephyrAlpha/architecture_model/SCOPE.yaml
git checkout HEAD -- src/zephyr/shared/SHARED-QUICKREF.yml  # 恢复已删除的文件

# 2. 回滚内容替换和白名单更新（git checkout 恢复所有被修改的文件）
# ⚠️ 警告: 确保这些目录下没有其他未提交的修改，否则会一起被恢复
git checkout -- scripts/ src/ docs/ tests/

# 3. 回滚 depgraph（恢复备份）
git checkout data/databases/depgraph.db

# 4. 重新生成 asset_index（不 checkout，因为自动生成文件应重新生成）
python d:/ZephyrAlpha/scripts/governance/generate_project_path_tree.py --write

# 5. 回滚后验证
python d:/ZephyrAlpha/scripts/governance/d3_metadata/check_naming_convention.py --warn-only
python d:/ZephyrAlpha/scripts/governance/rename_whitelist_cleanup.py --verify
```

### 8.2 回滚前提

- 回滚前必须通过 `python d:/ZephyrAlpha/scripts/rollback.py preflight` 检查
- 确认没有活跃的文件锁：`python d:/ZephyrAlpha/scripts/lock_files.py status`
- 回滚过程中执行 git stash 后必须在 finally 块执行 stash pop 恢复

---

## 9. 风险评估

| 风险 | 等级 | 缓解措施 |
|------|:---:|---------|
| session-logs 路径修正后代码行为变化 | 高 | 14处硬编码路径 `PROJECT_ROOT / "session-logs"` 在运行时指向不存在的目录（bug）。修正为 `session_logs` 后指向正确目录，可能暴露依赖错误路径的隐藏逻辑。需逐个验证 14 处硬编码路径 |
| SHARED-QUICKREF.yml 删除后引用断裂 | 中 | 替换脚本会将所有引用更新为 shared_quickref.yaml，dry-run 预览确认后再执行 |
| 自动生成数据未及时更新 | 中 | 改完源文件后立即重新生成 depgraph 和 path_tree |
| 测试用例中的路径断言失败 | 中 | 测试代码中的 `session-logs` 也要替换，但需确认测试意图 |
| REGISTRY_SCOPE.yaml 被误替换 | 高 | 替换脚本用正则 `(?<!REGISTRY_)SCOPE\.yaml` 排除 |
| SCOPE_YAML 常量名被误替换 | 低 | 替换映射只替换 `SCOPE.yaml`（含扩展名），不替换 `SCOPE_YAML` |
| .runtime/session-logs 路径不存在 | 低 | 已确认目录不存在，代码引用需替换（代码可能在运行时创建此目录） |
| docs/19_development_workspace/session-logs/ 路径不存在 | 低 | 已确认路径不存在，文档引用需替换 |

---

## 10. 施工前确认清单

| # | 确认项 | 状态 | 结论 |
|---|--------|:---:|------|
| 1 | `src/zephyr/shared/api/shared_quickref.yaml` 与 `SHARED-QUICKREF.yml` 的关系 | ✅ 已确认 | 同一文件两个副本（module_id/version 相同），删除旧副本 |
| 2 | `MAKEFILE` 是否以小写 `Makefile` 存在 | ✅ 已确认 | 大小写均不存在，从白名单删除 |
| 3 | `test_dir` 在 _DIR_ROOT_KEBAB_EXEMPT 中的原因 | ✅ 已确认 | 已是 snake_case，误入 kebab 列表，从白名单删除 |
| 4 | `docs/08_knowledge/01_raw_intake/` 中的引用是否需要改 | ✅ 已确认 | 不改（历史知识条目） |
| 5 | session_logs/ 目录内文件引用的 `session-logs` 是否需要改 | ✅ 已确认 | 不改（历史记录） |
| 6 | `.runtime/session-logs` 路径是否也需要改 | ✅ 已确认 | 目录不存在，代码引用需替换 |
| 7 | `docs/19_development_workspace/session-logs/` 路径是否存在 | ✅ 已确认 | 路径不存在，文档引用需替换 |

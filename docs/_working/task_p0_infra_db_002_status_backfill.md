---
module_id: DM-P0-INFRA-DB-002-BACKFILL
title: "P0-2: INFRA-DB-002 ChromaDB 状态回填（planned→provisioned，消除 52 万文件级状态漂移）"
doc_type: construction_plan
status: completed
version: 1.0.1
date: 2026-06-29
owner: ZephyrAlpha-Owner
ttl: task_bound
completes_when: "infrastructure_registry.yaml 中 INFRA-DB-002 的 status/host/provisioned_at/health_check/dependency_of/note 六字段回填完成，registry_master_index.yaml 重新生成 entry_count=14，registry_of_registries.yaml entry_count 同步为 14，GATE-19 钩子通过"
completed_at: "2026-06-29"
completed_by: "Phase 1.3 (commit 50cb5f59)"
---

# P0-2: INFRA-DB-002 ChromaDB 状态回填

## 任务背景（审核结论）

**infrastructure_registry.yaml:145-157** 登记 INFRA-DB-002（ChromaDB）为 `status: planned` + `host: null`，但实际：

- `data/vector_db/chroma.sqlite3` 真实存在（ChromaDB PersistentClient 元数据库）
- `data/vector_db/_health_check_result.json:2` 记录 2026-05-26 健康检查 8 collection 全部 healthy
- `data/vector_db/*.index` × 8（FAISS HNSW 索引）
- `data/vector_db/vms_metadata.db`（FAISS 后端 SQLite WAL 元数据库）
- `architecture_lock.yaml:41` 已锁定 `data/vector_db/ —— VMS 数据根目录`

**这是最严重漂移**：新 AI 读真源会误以为 ChromaDB "尚未部署"而尝试重新搭建，违反项目内存"能用现成的不创造"原则。

**附加发现**：实际是"ChromaDB + FAISS 双后端共存"过渡期（ARCH-LOCK-003 锁定目标后端为 FAISS+SQLite WAL，`migrate_chroma_to_faiss.py` 迁移脚本已就位），回填时需在 note 说明。

## 任务字段

| 字段 | 值 |
|------|-----|
| task_id | TASK-P0-CHROMADB-BACKFILL |
| priority | P0 |
| safety_level | L |
| ai_autonomy_level | supervised |
| blocked_by | 无 |

## 修复点清单（精确行号）

### 真源文件

**文件**：`d:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\infrastructure_registry.yaml`

**当前完整内容（:145-157）**：
```yaml
  # --- 向量数据库（ChromaDB）---
  - infra_id: "INFRA-DB-002"
    name: "zephyr-chroma-vector-db"
    type: vector_db
    description: "ChromaDB 向量检索与 KMS 语义检索"
    runtime_plane: cold
    host: null
    health_check: http
    dependency_of:
      - "MOD-TASK_SYSTEM"
    sla: "< 200ms retrieval p95, index rebuild < 10 min"
    status: planned
    provisioned_at: null
    note: "KBG-0031：ChromaDB 选型。vibe-coding-pipelines M2 模块"
```

### 字段回填映射表

| 字段 | 行号 | 当前值 | 回填值 | 证据 |
|------|------|--------|--------|------|
| `host` | :150 | `null` | `data/vector_db/` | `collection_manager.py:52` `VMS_PERSIST_DIR = Path("data/vector_db")`；`architecture_lock.yaml:41` ARCH-LOCK-002 锁定 |
| `health_check` | :151 | `http` | `query` | ChromaDB PersistentClient 无 HTTP 端点，健康检查通过 `in_process_vector_memory.py:334 def health_check()` 方法调用；与 INFRA-DB-001/003 的 `query` 一致 |
| `status` | :155 | `planned` | `provisioned` | chroma.sqlite3 存在 + 2026-05-26 健康检查 healthy；用 `provisioned`（已部署）而非 `connected`（INFRA-DB-003 的 connected 级别指持续运行的服务） |
| `provisioned_at` | :156 | `null` | `2026-05-05` | `docs/03_modules/_domain_knowledge/vector_memory/blueprint.md:14` `valid_from: "2026-05-05"`（VMS 蓝图生效日期） |
| `dependency_of` | :152-153 | `["MOD-TASK_SYSTEM"]` | `["MOD-INF-011", "MOD-CONTEXT_ENGINE", "MOD-KB-001", "MOD-TASK_SYSTEM"]` | `blueprint.md:2` module_id=MOD-INF-011；`blueprint.md:40-47` depends_on 列出 CE/KB |
| `note` | :157 | `"KBG-0031：ChromaDB 选型。vibe-coding-pipelines M2 模块"` | 见下方回填值 | 补充实际部署信息与双后端过渡状态 |

### note 字段回填值

```yaml
note: "KBG-0031：ChromaDB 选型。实际部署 2026-05-05；PersistentClient 本地持久化 data/vector_db/（ARCH-LOCK-002 锁定）。8 Collection（5×1024d BGE-M3 + 3×512d bge-small-zh-v1.5）。ARCH-LOCK-003 锁定目标后端为 FAISS HNSW + SQLite WAL，当前处于 ChromaDB→FAISS 迁移过渡期，chroma.sqlite3（旧）与 vms_metadata.db+.index（新）共存；migrate_chroma_to_faiss.py 为迁移脚本。P3-T1 pgvector 处于 Suspended（消费方为零）"
```

## 连带影响与同步更新

### 连带点 1：registry_master_index.yaml（自动生成，entry_count 漂移 11→13）

**文件**：`d:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\registry_master_index.yaml`

**当前漂移**：`:144` `entry_count: 11`（真源 13，滞后 2 项，生成于 2026-06-26）

**治本动作**：修改 `infrastructure_registry.yaml` 后立即重新生成

```powershell
python scripts/governance/generators/generate_registry_master_index.py
```

### 连带点 2：registry_of_registries.yaml（手工维护，entry_count 漂移 9→13）

**文件**：`d:\ZephyrAlpha\docs\registry_of_registries.yaml`

**当前漂移**：`:273` `entry_count: 9`（真源 13，滞后 4 项，自 2026-05-07 未更新）

**治本动作**：手工修改 `:273` `entry_count: 9` → `entry_count: 13`，并同步 `:275` description

### 连带点 3：GATE-19 pre-commit 钩子

**配置**：`.pre-commit-config.yaml:659-667`

**触发条件**：修改 `docs/01_policies_and_standards/_registry/catalogs/*.yaml` 时触发 `validate_static_manifest_drift.py --check`

**风险**：若 `infrastructure_registry.yaml` 修改后 `registry_master_index.yaml` 未同步重新生成，GATE-19 **会阻断提交**（磁盘版 13 条 vs 索引版 11 条漂移）

**操作顺序约束**：
1. 先修改 `infrastructure_registry.yaml`
2. 立即运行 `generate_registry_master_index.py` 重新生成 `registry_master_index.yaml`
3. 手工更新 `registry_of_registries.yaml:273`
4. 三个文件一起 `git add` 后提交

## 施工步骤

### STEP 0：备份先行

```powershell
cd D:\ZephyrAlpha
git status
git add docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml docs/01_policies_and_standards/_registry/catalogs/registry_master_index.yaml docs/registry_of_registries.yaml
$env:ZEPHYR_COMMIT_GATEWAY=1
python scripts/git_commit.py -m "backup: P0-2 ChromaDB status backfill baseline [GW:$(New-Guid)]"
```

### STEP 1：修改 infrastructure_registry.yaml

按"字段回填映射表"修改 `:145-157` 的 6 个字段：
- `host: null` → `host: "data/vector_db/"`
- `health_check: http` → `health_check: query`
- `status: planned` → `status: provisioned`
- `provisioned_at: null` → `provisioned_at: "2026-05-05"`
- `dependency_of` 补充 MOD-INF-011、MOD-CONTEXT_ENGINE、MOD-KB-001
- `note` 替换为上方回填值

### STEP 2：重新生成 registry_master_index.yaml

```powershell
cd D:\ZephyrAlpha
python scripts/governance/generators/generate_registry_master_index.py
# 验证 entry_count 已更新为 13
```

### STEP 3：手工更新 registry_of_registries.yaml

- `:273` `entry_count: 9` → `entry_count: 13`
- `:275` description 同步更新（如 "9 个基础设施组件登记" → "13 个基础设施组件登记"）

### STEP 4：验证

```powershell
cd D:\ZephyrAlpha

# 1. 确认 INFRA-DB-002 字段回填正确
# 读 infrastructure_registry.yaml :145-157 确认 6 字段已更新

# 2. 确认 entry_count 一致性
# infrastructure_registry.yaml:42 total_registered=13
# registry_master_index.yaml:144 entry_count=13
# registry_of_registries.yaml:273 entry_count=13

# 3. 确认 health_check 与其它 INFRA-DB 一致（均为 query）
# INFRA-DB-001:135 query, INFRA-DB-002:151 query(回填后), INFRA-DB-003:274 query, INFRA-DB-004:290 query

# 4. GATE-19 钩子预检（可选，正式提交时会自动跑）
python scripts/governance/d5_architecture/validators/validate_static_manifest_drift.py --check
```

### STEP 5：提交

```powershell
cd D:\ZephyrAlpha
git add docs/01_policies_and_standards/_registry/catalogs/infrastructure_registry.yaml docs/01_policies_and_standards/_registry/catalogs/registry_master_index.yaml docs/registry_of_registries.yaml
$env:ZEPHYR_COMMIT_GATEWAY=1
python scripts/git_commit.py -m "fix(P0-2): backfill INFRA-DB-002 ChromaDB status planned→provisioned, host/provisioned_at/health_check/dependency_of/note 回填，消除 52 万文件级状态漂移 [GW:$(New-Guid)]"
```

**注意**：`infrastructure_registry.yaml` 位于 `docs/01_policies_and_standards/`（永久区），但本次是**修改现有文件**而非新增文件，不需要 `--allow-promote`。若钩子提示 PROMOTION_BLOCKED，说明被识别为新增——检查文件是否被误删后重建。

## 回滚计划

```powershell
cd D:\ZephyrAlpha
git log --oneline -5  # 找到 backup commit hash
git revert <fix_commit_hash>
# 若 registry_master_index.yaml 已自动重新生成，回滚后需再次运行生成器恢复旧状态
```

## 验收标准

1. `infrastructure_registry.yaml:150` `host: "data/vector_db/"`
2. `infrastructure_registry.yaml:151` `health_check: query`
3. `infrastructure_registry.yaml:155` `status: provisioned`
4. `infrastructure_registry.yaml:156` `provisioned_at: "2026-05-05"`
5. `infrastructure_registry.yaml:152-153` `dependency_of` 包含 MOD-INF-011、MOD-CONTEXT_ENGINE、MOD-KB-001、MOD-TASK_SYSTEM
6. `infrastructure_registry.yaml:157` note 包含双后端过渡状态说明
7. `registry_master_index.yaml:144` `entry_count: 13`
8. `registry_of_registries.yaml:273` `entry_count: 13`
9. GATE-19 钩子通过（提交时不阻断）
10. 新 AI 读真源能正确识别 ChromaDB 已部署，不会尝试重新搭建

## 不在本次范围

- ChromaDB→FAISS 迁移完成（独立大任务，ARCH-LOCK-003 锁定的目标架构）
- 13+ 文档同步副本中数据库清单的清理（P2 任务）
- AGENTS.md 增补数据库真源指针（P1 任务，独立任务卡）
- market.duckdb 登记 INFRA-DB-005（P1 任务，独立任务卡）
- INFRA-DB-004 DuckDB 重新归类（P2 任务）

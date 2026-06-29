---
ttl: task_bound
doc_type: blueprint
completes_when: "阶段4 KE来源重设计达到稳定等待状态，或 P3-T1 解除后 VMS 持久化落地"
created: 2026-06-29
updated: 2026-06-30
session: kb-refactor-phase4-index
---

# KB 系统架构重构施工计划

> **文档类型**: 施工计划（task_bound 过程文档）
> **真源声明**: 本文档由会话重建，记录 KB 重构 4 阶段 14 Step 的执行轨迹与当前状态
> **重建原因**: 原文档在会话切换中丢失，本次基于 git commit 历史重建

---

## 1. 背景与目标

### 1.1 问题根因

旧 KB 系统存在三层冗余架构，违反"真源唯一"铁律：

1. **L1 文件层** — `docs/08_knowledge/01_raw_intake/ke-*.md`（3239 个批量生成的 ke- fragments，质量参差）
2. **L2 SQLite 中间层** — `kb_repo.py` + `data/databases/depgraph.db` 的 knowledge 表
   - schema 与实际表不匹配（title/category/source_file 字段不存在）
   - 所有调用在 try/except 中静默失败
   - 生产环境 `kb_repo` 恒为 None
3. **L3 旧 ChromaDB 层** — `chromadb_init.py` + `ChromaMemoryBackend`
   - 与 VMS（Vector Memory System）功能重叠
   - 维护两套向量存储，违反"向内收"

### 1.2 目标状态（2 层架构）

```
┌─────────────────────────────────────────────────┐
│  L1 文件层（唯一真源）                            │
│  docs/08_knowledge/01_raw_intake/ke-*.md        │
│  → TriageGate 分流 → 02_triaged/                │
└────────────────────┬────────────────────────────┘
                     │ Bootstrap 加载
                     ▼
┌─────────────────────────────────────────────────┐
│  L2 向量层（复用 VMS）                            │
│  src/zephyr/integration/vector_memory/          │
│  UnifiedMemoryAPI（recall/search/write/count）  │
│  → context_assembler 接入                       │
└─────────────────────────────────────────────────┘
```

**已移除**：
- SQLite 中间层（`kb_repo.py`）
- 旧 KB ChromaDB（`chromadb_init.py` + `ChromaMemoryBackend`）

### 1.3 4 条铁律（审核元规则）

| 铁律 | 内容 | 在本次重构的体现 |
|------|------|------------------|
| 铁律1 | 责任唯一，真源唯一 | 移除 SQLite 中间层，文件层为唯一真源 |
| 铁律2 | 向内收（能用现成的不创造） | 复用 VMS，不维护独立 ChromaDB |
| 铁律3 | 第一性原理——问题本身是否该存在 | kb_repo.py 静默失败 → 整层删除而非修复 |
| 铁律4 | 新 AI 如何发现功能并避免重复创造 | UnifiedMemoryAPI 统一接口，re-export shim 保持向后兼容 |

---

## 2. 阶段执行记录

### 阶段 1：清理（✅ 全部完成）

| Step | 内容 | Commit | 状态 |
|------|------|--------|------|
| 1.1 | 删除 3239 个批量生成的 ke- fragments | `9d863e532f` | ✅ |
| 1.2 | 修复 11 处 glob 大写 `KE-*` bug + stale reference | `a154a6e839` | ✅ |
| 1.3 | 修复 stale reference（与 1.2 合并提交） | `a154a6e839` | ✅ |
| 1.4 | 清理漂移副本 chromadb_init.py + kb_repo.py 副本，留 1 份真源 | `6ed8c98b22` | ✅ |
| 1.5 | 修复 VMS_PERSIST_DIR 相对路径违规，改用 REPO_ROOT 绝对路径 | `d10afbfd5d` | ✅ |

**关键产物**：
- `docs/08_knowledge/01_raw_intake/` 下 ke-*.md 文件清空（3239 个删除，85564 行）
- VMS 持久化路径改为绝对路径（符合硬约束"所有文件路径必须使用绝对路径"）

### 阶段 2：存储简化（✅ 全部完成）

| Step | 内容 | Commit | 状态 |
|------|------|--------|------|
| 2.1 | 删除死代码 kb_repo.py + SQLite knowledge 层 | `ab9d972ab9` | ✅ |
| 2.2 | 删除 chromadb_init.py + ChromaMemoryBackend | `0674c1e75c` | ✅ |

**Step 2.1 关键决策**（第一性原理）：
- `kb_repo.py` 的 schema 与实际表不匹配（title/category/source_file 字段不存在）
- 所有调用在 try/except 中静默失败，生产环境 `kb_repo` 恒为 None
- **结论**：问题不在于"修复 kb_repo"，而在于"这层根本不该存在" → 整层删除
- 影响范围：17 个 src 文件 + 11 个 test 文件的引用清理
- 数据清理：knowledge 表 398→0 行，ke_tombstones 2→0 行，旧 ChromaDB 缓存清除

**Step 2.2 关键决策**（向内收）：
- 旧 ChromaDB 与 VMS 功能重叠
- 复用 VMS 而非维护两套向量存储

### 阶段 3：消费方迁移（✅ 降级适配和测试修复完成）

| Step | 内容 | Commit | 状态 |
|------|------|--------|------|
| 3.1 | 清理 4 个文件的死 kb_repo 运行时引用（context_injector.py ×2, dashboard/app.py ×2） | `20f3c4f39e` | ✅ |
| 3.2 | 修复阶段 2 遗留的测试失败（test_kb_triage.py + test_kb_pipeline_activate.py 移除 kb_repo 参数） | `f01e7490bf` | ✅ |
| 3.3 | activate.py DEPENDENCIES header 死引用清理 | `f01e7490bf` | ✅ |

**Step 3.2 关键修复**：
- `TriageGate.__init__` 和 `ActivateGate.__init__` 移除了 `kb_repo` 参数
- 测试中 8 处 `kb_repo=None` + 2 处 `kb_repo=mock_repo` 参数移除
- 删除 `TestActivateGateDependencies` 类（2 个过时测试，`_check_dependencies` 已空桩化为 `return []`）
- 验证：37 + 55 = 92 tests 全部通过

**消费方现状**：
- `context_assembler.py:628` — 已接入 UnifiedMemoryAPI（通过 Bootstrap 加载 KE）
- `bootstrap.py:192,453` — 使用 UnifiedMemoryAPI
- `knowledge_overview.py` — `fetch_knowledge_overview(kb_repo=None)` 安全降级（返回空数据）
- `dashboard/app.py` — 已清理 kb_repo 引用

### 阶段 4：KE 来源重设计（⏳ 进行中 — 合理等待状态）

| Step | 内容 | Commit | 状态 |
|------|------|--------|------|
| 4.1 | 修复 index.md 死链（7638 个 ke- 引用 + zalpha_metadata.db） | `8870d254c4` | ✅ |
| 4.2 | KE 来源重设计 | — | ⏳ 合理等待 |
| 4.3 | VMS 持久化落地 | — | ⏸️ P3-T1 Suspended |

**Step 4.1 完成内容**（commit `8870d254c4`）：
- `docs/08_knowledge/01_raw_intake/index.md` — 清除 7638 个 ke-*.md 死链（3247 行删除）
- `docs/08_knowledge/data/index.md` — 清除 zalpha_metadata.db 死链
- `docs/08_knowledge/02_triaged/index.md` — 重新生成保持一致
- `docs/08_knowledge/index.md` — 补建根索引（新增 28 行）
- 方法：用 `generate_missing_index_md.py --update` 重新生成（向内收，未手工编写）
- 4 files changed, 40 insertions(+), 3252 deletions(-)

**Step 4.2 状态评估**（第一性原理）：
- KE 文件层为空是阶段 1 清理的合理结果，不是 bug
- UnifiedMemoryAPI 已就绪（recall/search/write/count 接口完整）
- `context_assembler.py` 已接入 UnifiedMemoryAPI
- 当业务产生新 KE 时，会通过 TriageGate 自然填充 L1 文件层
- **结论**：架构就绪，数据待业务驱动，无需主动"填充"

**Step 4.3 状态**（P3-T1 Suspended）：
- VMS 持久化受 P3-T1 Suspended 限制
- 触发条件：CE 接入 VMS 或 Agent 增加 code_search 工具
- **约束**：新 AI 不得尝试"修复"或"实现"该 indexer，须等待触发条件达成

---

## 3. 关键文件索引

### 3.1 核心组件

| 文件 | 角色 | 说明 |
|------|------|------|
| [unified_memory_api.py](file:///d:/ZephyrAlpha/src/zephyr/governance/kb/storage/unified_memory_api.py) | UnifiedMemoryAPI 真源 | recall/search/write/count 接口 |
| [unified_memory_api.py](file:///d:/ZephyrAlpha/src/zephyr/governance/kb/unified_memory_api.py) | re-export shim | 向后兼容，真源在 storage/ 下 |
| [context_assembler.py](file:///d:/ZephyrAlpha/src/zephyr/autonomy_core/context_assembler.py) | 消费方 | 第 620-641 行接入 UnifiedMemoryAPI |
| [bootstrap.py](file:///d:/ZephyrAlpha/src/zephyr/governance/kb/bootstrap.py) | 消费方 | 加载 KE 到 UnifiedMemoryAPI |
| [triage.py](file:///d:/ZephyrAlpha/src/zephyr/governance/triage.py) | TriageGate | KE 分流（已移除 kb_repo 参数） |
| [activate.py](file:///d:/ZephyrAlpha/src/zephyr/governance/kb/activate.py) | ActivateGate | KE 激活（已移除 kb_repo 参数） |

### 3.2 已删除文件

| 文件 | 删除 Commit | 原因 |
|------|-------------|------|
| `kb_repo.py` | `ab9d972ab9` | schema 不匹配，静默失败，整层冗余 |
| `chromadb_init.py` | `0674c1e75c` | 与 VMS 功能重叠 |
| `ChromaMemoryBackend` | `0674c1e75c` | 同上 |
| 3239 个 ke- fragments | `9d863e532f` | 批量生成，质量参差 |

### 3.3 工具脚本

| 文件 | 用途 |
|------|------|
| [generate_missing_index_md.py](file:///d:/ZephyrAlpha/scripts/governance/d1_structure/generate_missing_index_md.py) | 自动生成/更新 index.md（Step 4.1 使用） |
| [git_commit.py](file:///d:/ZephyrAlpha/scripts/git_commit.py) | GitCommitGateway CLI 入口 |

---

## 4. 当前状态总结

### 4.1 已完成

- ✅ 阶段 1（清理）：5 个 Step 全部完成
- ✅ 阶段 2（存储简化）：2 个 Step 全部完成
- ✅ 阶段 3（消费方迁移）：3 个 Step 全部完成（降级适配 + 测试修复）
- ✅ 阶段 4 Step 4.1：index.md 死链修复完成

### 4.2 合理等待

- ⏳ 阶段 4 Step 4.2（KE 来源重设计）：架构就绪，数据待业务驱动
- ⏸️ 阶段 4 Step 4.3（VMS 持久化）：P3-T1 Suspended，等待触发条件

### 4.3 后续触发条件

| 事项 | 触发条件 | 动作 |
|------|----------|------|
| KE 文件层填充 | 业务产生新 KE | TriageGate 自动分流到 01_raw_intake/ |
| VMS 持久化解除 Suspended | CE 接入 VMS 或 Agent 增加 code_search 工具 | 实现 pgvector indexer（P3-T1） |
| index.md 自动维护 | 每次新增/删除 KE 文件后 | 运行 `generate_missing_index_md.py --update` |

---

## 5. 铁律审核

| 铁律 | 审核结果 |
|------|----------|
| 铁律1（真源唯一） | ✅ 文件层为唯一真源，SQLite 中间层已删除 |
| 铁律2（向内收） | ✅ 复用 VMS，不维护独立 ChromaDB；index.md 用生成器重新生成 |
| 铁律3（第一性原理） | ✅ kb_repo.py 静默失败 → 整层删除而非修复；KE 文件层为空是合理状态 |
| 铁律4（AI 可发现） | ✅ UnifiedMemoryAPI 统一接口 + re-export shim 保持向后兼容；本文档记录架构决策 |

---

## 6. 变更日志

| 日期 | 变更 | Session |
|------|------|---------|
| 2026-06-29 | 文档重建（基于 git commit 历史恢复） | kb-refactor-phase4-index |
| 2026-06-30 | Step 4.1 完成记录补充 | kb-refactor-phase4-index |

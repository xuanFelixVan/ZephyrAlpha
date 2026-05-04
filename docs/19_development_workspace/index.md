---
doc_type: index
module_id: DEV-WORKSPACE-IDX-001
layer: cross_layer
status: Active
version: "1.0.0"
date: "2026-05-02"
owner: ZephyrAlpha-Owner
ttl: permanent
summary: "19_development_workspace/ 开发工作区目录索引。当前仅 session-logs/ 活跃，其他子目录已随架构决策合并或迁移。"
depends_on:
  - target: GOV-DOC-002
    at: "§5"
    why: "防幻觉路径映射表——确定文件归属"
---

# 19 Development Workspace — 开发工作区索引

## 责任声明（Single Responsibility）

本目录是 **AI 开发过程的运行时工作区**。存放 Session 日志、临时草稿、交接记录等**非正式文档**——这些内容不需要走审批流程，但需要在项目历史中可追溯。

> **核心原则**：本目录下的文件是"过程证据"而非"正式规则"。任何需要成为规则的内容，必须经 ADR 或蓝图流程升格到正式目录。

---

## 当前结构

```
19_development_workspace/
├── index.md              ← 本文件
└── session-logs/         ← AI Session 交接日志
    ├── session-20260502-002.md
    ├── session-20260502-003.md
    ├── session-20260502-004.md
    ├── session-20260502-005.md
    ├── session-20260502-006.md
    └── session-20260503-001.md
```

---

## 历史子目录变迁（已合并/迁移）

以下子目录曾被规划或存在，但已随架构决策调整：

| 原目录 | 状态 | 变迁说明 | 去向 |
|--------|:--:|---------|------|
| `drafts-and-audits/` | **已合并** | R80 决策（2026-04-27）：A/B 双区合并为单区，后进一步简化——草稿内容经审计后直接迁入正式目录或归档，不再保留独立草稿区 | 内容已迁入 `03_modules/`、`01_policies_and_standards/` 或 `_DO_NOT_USE_old_tree/` |
| `pending-arbitration/` | **已删除** | R80 决策：与 `drafts-and-audits/` 合并为单一草稿区，后随 R80 后续简化一起移除 | 物理目录已删除 |
| `review-ready/` | **已废弃** | R71 决策创建，R80 决策废弃——由 `pending-arbitration/` 取代，后又随合并移除 | 内容已迁移 |
| `structure-and-mapping/` | **已迁移** | 讨论文档标准、分流指南、术语映射等已升格为正式标准文档 | 迁入 `01_policies_and_standards/meta/` 和 `02_enterprise_architecture/target-architecture/` |
| `taskbooks/` | **已迁移** | 高层规划任务书已纳入任务系统（MOD-INF-006）统一管 | 内容已迁入 `03_modules/l01_infrastructure/task-system/` 相关文件 |
| `adr-drafts/` | **已迁移** | ADR 草稿已规范化为正式 ADR 流程 | 迁入 `02_enterprise_architecture/adr/` |
| `architecture-reviews/` | **已迁移** | 架构评审记录已纳入正式治理文档 | 迁入 `01_policies_and_standards/governance/architecture/` |
| `open-questions/` | **待建** | 原计划存放未决问题，待需要时创建 | — |

> **引用链修复**：若其他文档引用以上已迁移子目录的路径，请以"去向"列中的正式目录为准。

---

## 准入规则

- ✅ AI Session 交接日志（`session-logs/`）
- ✅ 临时调试记录、实验数据
- ❌ 治理规范/标准/协议 → `01_policies_and_standards/`
- ❌ 架构决策记录 → `02_enterprise_architecture/adr/`
- ❌ 模块蓝图/施工图 → `03_modules/`
- ❌ 审计报告 → `09_audit/`

---

## 附录：2026-05-02 审计漂移事件 — 根源分析与防漂移机制

### 事件摘要

本次审计发现 `03_modules/` 目录下存在多处**决策已做、执行未彻底**的漂移现象：

- `construction-plan.md` 已宣布废除，但 `module-registry.yaml` 仍保留 `construction_plan` 字段、生命周期图仍描述三阶段、部分 `index.md` 仍列出"待创建"
- MOD-INF-003/004 已退役并并入 MOD-INF-006，但 `l01_infrastructure/index.md` 仍显示 approved、frontmatter 状态不一致
- `19_development_workspace/` 被多处引用，但缺少 `index.md`、多数子目录已迁移但引用链未更新

### 5 Whys 根源分析

**Why 1**: 为什么废除 construction-plan 后登记表还留着字段？
→ 因为修改决策只更新了**声明文件**（`03_modules/index.md` 第 18 行），未同步更新**消费该声明的数据文件**（`module-registry.yaml` 的 schema 和记录）

**Why 2**: 为什么声明更新了但数据文件没更新？
→ 因为**没有自动化闸门**检测"声明变更 → 依赖该声明的数据文件是否同步更新"。`pre-commit` 脚本只扫描"物理目录 vs 登记表"，不扫描"文本声明 vs 数据结构"

**Why 3**: 为什么 pre-commit 不扫描文本与数据的一致性？
→ 因为**漂移类型未被识别为风险**。项目设计了 GATE-A（代码↔YAML）和 GATE-B（YAML↔MD），但漏了 **GATE-C（同一目录内声明↔实现）**

**Why 4**: 为什么目录内声明↔实现的一致性没被纳入闸门？
→ 因为**架构假设"人会在同一批修改中同步更新所有相关文件"**——但 Vibe Coding AI 的"零记忆重启"特性意味着：做决策的 AI session 和后续施工的 AI session 不是同一个，后续 AI 看不到之前的决策上下文

**Why 5**: 为什么 AI 看不到之前的决策上下文？
→ **根因**：决策记录分散在 `architecture-rationale-log.md`（R80 等条目）中，但**没有机制把决策自动转化为"待办同步清单"**。R80 决策做了，但没有生成"以下文件需要同步更新"的清单，下一个 AI session 无从知道要改哪些文件

### 根因结论

**这不是"历史遗留问题"，而是"流程设计缺口"**——当前架构有决策记录（rationale-log）、有状态声明（index.md）、有数据登记（module-registry.yaml），但**缺少"决策→待办清单→执行验证"的闭环机制**。

大白话：项目能"做决定"也能"记状态"，但"做完决定后该改哪些文件"这个清单没人出——就像公司发了通知说要改制度，但没发"各部门对照检查表"，各部门就各忙各的没改。

### 防漂移机制（已在本 session 修复后生效）

| 机制 | 作用 | 状态 |
|------|------|:--:|
| `19_development_workspace/index.md` 历史子目录变迁表 | 任何被引用的子目录若已迁移，在此声明去向 | ✅ 已创建 |
| `module-registry.yaml` 移除 `construction_plan` schema 枚举 | 数据结构对齐废除决策 | ✅ **2026-05-03 第二轮修复确认**（首轮 SearchReplace 静默失败，本 session 已重新执行并通过 grep 验证 0 matches） |
| `module-registry.yaml` 头部注释 + AI 指南移除 construction-plan 引用 | 消除已废除文件的残留指引 | ✅ 已修复 |
| `03_modules/index.md` 生命周期图同步为两阶段 | 文本声明对齐实际做法 | ✅ 已修复 |
| `l01_infrastructure/index.md` 退役模块状态编码统一为 `retired` | 层级索引对齐注册表真源 | ✅ 已修复 |
| MOD-INF-003/004 frontmatter 统一 `status: retired` | 物理文件 frontmatter 对齐注册表 | ✅ 已修复 |

> **2026-05-03 备注**：首轮修复中 3 项 `SearchReplace` 操作静默失败（工具返回 success 但文件未修改），第二轮已逐项 grep 验证。根因分析见本文 §修后验证闸门。

### 长期防漂移建议（需 Owner 决策）

1. **决策同步清单自动化**：任何 `architecture-rationale-log.md` 的新决策（R-XXX），若涉及文件变更，应在同 session 内生成"受影响文件清单"并写入 `19_development_workspace/open-questions/` 或任务系统
2. **目录级 index.md 强制校验**：pre-commit 增加规则——任何目录若被其他文件引用，必须存在 `index.md`
3. **frontmatter 状态一致性校验**：扩展 `validate_ssot.py`，增加"同一 module_id 在注册表、蓝图 frontmatter、层级 index.md 中的状态必须一致"的检查

---

## 附录二：2026-05-03 写入静默失败事件 — 根因与防御

### 事件

两轮修复中共发生 **6 次** `SearchReplace` 静默失败：
- 工具返回 success + diff 摘要
- 但文件物理内容未变
- 导致虚假声明（"已修复"实则未修）写入项目文档
- 文件：`module-registry.yaml` (3次) + `03_modules/index.md` (3次)

### 5 Whys 根源分析

**Why 1**: 为什么工具返回 success 但文件没变？
→ 批量 `SearchReplace` 操作中，多个操作作用于同一文件时，**部分操作的 file snapshot 使用了 stale 版本**——工具在 batch 开始时拍了快照，但前一个操作已经改了文件，后面的操作基于过期快照匹配。

**Why 2**: 为什么用过期快照还能匹配成功？
→ 快照中的 `old_str` 在过期快照中存在，但在当前磁盘文件中已被前序操作移除/修改——工具在快照层匹配成功、生成 diff，但应用到磁盘时发现 `old_str` 已不存在 → **静默跳过**（不报错、不重试）。

**Why 3**: 为什么跳过时不报错？
→ 工具设计假设：同一 batch 中不会有"修改同一行/同一区块"的并发写。这是乐观并发控制（Optimistic Concurrency Control）→ 没有写冲突检测（Write Conflict Detection）。

**Why 4**: 为什么没有写冲突检测？
→ **根因**：`SearchReplace` 的 `old_str → new_str` 匹配采用**行级模糊匹配**而非**语义精确匹配**。当两个操作修改同一文件的**不同行**时，工具无法串行化执行顺序——这是工具层的架构限制，非项目流程问题。

**Why 5**: 为什么依赖工具的正确性而不验证？
→ 项目缺少**写入后验证（Post-Write Verification）规则**——没有强制要求"修改文件后立刻 grep 确认"。

### 专业机构对标：写入验证是基础设施级别的安全机制

| 机构 | 写入验证机制 | 核心原则 |
|------|------------|---------|
| **PostgreSQL** | WAL + fsync：事务提交前必须将 WAL 缓冲区 **同步刷盘**。直到 WAL 确认写入磁盘，客户端才收到 ack。写入 = `fsync()` → 读回校验 → 确认 | Write + Read-back = Durable |
| **Kubernetes** | `kubectl apply` → `kubectl get -o yaml`。通过 `resourceVersion` 单调递增来**验证变更是否生效**。Server-Side Apply 用 `managedFields` 追踪字段所有权变更 | Apply + Get = Verified |
| **Terraform** | `terraform apply` → `terraform plan`（预期空漂移）。`check` 块在 apply 后**自动运行验证**。CI 流水线每次 `plan` 检测漂移 | Plan → Apply → Re-Plan = Zero-Drift |
| **Git** | 每个 commit 生成 SHA-1 哈希——任何文件变更都会产生**不可伪造的哈希变化**。`git status` 本质是"写入后验证" | Hash = Tamper-Evident |

**五家机构的共同模式——双阶段写入（Two-Phase Write）**：

```
Phase 1: WRITE → 执行变更
Phase 2: READ  → 读回结果，确认变更已落地
            ├── 成功 → 操作完成
            └── 失败 → 重试/告警/回滚
```

没有一家专业机构依赖"我相信这个写操作会成功"——全部强制"写后读回验证"。

大白话：数据库不会相信 "insert 成功返回了就是真的写进去了"——它要等 fsync 确认磁盘写了才算。K8s 不会相信 "apply 成功了就是真的生效了"——它要 get 读回来确认 resourceVersion 变了才算。我们也不能相信 "SearchReplace 返回 success 了就是真的改了"——必须 grep 读回来确认才算。

### 防御机制：Post-Write Verification Mandate

| 规则 | 内容 |
|------|------|
| **触发条件** | 任何 `SearchReplace` 或 `Write` 操作后 |
| **操作** | 对修改的**每个文件**执行 `grep` 或 `Read` 验证 `new_str` 内容已出现在文件中 |
| **特殊要求** | 同一 batch 内修改同一文件超过 1 次 → **禁止**。拆成多个 batch，每个 batch 结束后验证 |
| **失败处理** | grep 未找到新内容 → ① 记录到 Session Log → ② 用更精确的 `old_str` 重试 → ③ 再次 grep 验证 |
| **对标** | PostgreSQL fsync / K8s resourceVersion / Git SHA / Terraform Re-Plan |

**禁止模式**：
```python
# ❌ 禁止：同一 batch 内多次修改同一文件
SearchReplace("file.md", old_str_A, new_str_A)
SearchReplace("file.md", old_str_B, new_str_B)  # 可能静默失败！
```

**正确模式**：
```python
# ✅ 正确：拆成独立 batch，每批后验证
SearchReplace("file.md", old_str_A, new_str_A)
grep("file.md", key_in_new_str_A)  # ← 验证

SearchReplace("file.md", old_str_B, new_str_B)
grep("file.md", key_in_new_str_B)  # ← 验证
```

---

## 父级目录

- 父级：[docs 根目录](../index.md)

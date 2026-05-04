---
module_id: MOD-INF-003
title: 任务卡系统 + KMS 蓝图（B5 · 2）
doc_type: blueprint
status: retired
version: 2.0.1
layer: L01
layer_name: infrastructure
functional_domain: infra
owner: ZephyrAlpha-Owner
classification: internal
language: zh
created_by: AI-GLM-5.1
valid_from: 2026-05-02
ttl: permanent
construction_progress: phase_1_complete
superseded_by: MOD-INF-006
completion_note: "experimental 构建完成——核心代码(task_card解析/serialize/schema/gates)已实现。内容已于2026-05-02升级并入 MOD-INF-006 task-system。本蓝图记录已完成工作，永久保留，不可删除——有新需求应走蓝图升级流程重开(§八·铁律三)。"
priority: P1
tags:
  - task-card
  - kms
  - knowledge-management
  - infrastructure
  -
summary: ZephyrAlpha 任务卡制度 + KMS 知识管理体系蓝图。覆盖 10 状态机（GOV-TASK-004 审定）、G0-G6 门禁系统、超时与升级规则、KMS 三层漏斗架构、KE 模板、代码消费者注册表。v2.0.0：合并 construction-plan-task-card-and-kms.md 的施工实现细节。
---

# 任务卡系统 + KMS 蓝图（B5 · 2）

> **真源声明**：本蓝图是 ZephyrAlpha 任务卡制度与 KMS 知识管理体系的唯一真源。原始施工图文档 `construction-plan-task-card-and-kms.md`，本文档承载终审裁定后的最终方案。

---

## 1. 核心概念

### 任务卡制度（Task Card）

每张任务卡是 1 个原子施工单元。任务卡 = 任务分解的最小不可分单位。每张卡对应 `docs/19_development_workspace/taskbooks/TASK-{Phase}-{NNN}.md`。

**核心字段**：
- `task_id`：唯一标识
- `blueprint_ref`：所服务的蓝图
- `construction_plan_ref`：施工图引用
- `phase`：所属 Phase
- `deps`：前置依赖任务卡 ID
- `estimated_hours`：预估工时
- `assignee`：AI 模型或 Human

### KMS 知识管理体系（三层漏斗）

```
输入（Session Log / 任务卡 / 蓝图）→ 沉淀层（临时索引 SQLite）→ 审核层（Human Gated）→ 知识层（KB Collection）
```

**三层架构**对标 ITIL 知识管理（Knowledge Management）的 DIKW 金字塔（Data→Information→Knowledge→Wisdom）的简化版。

---

## 2. 到需要做什么（回顾大盘 + 用户原意）

**Owner 指示**：
- "每做一个模块后，要沉淀经验到知识库"
- "1500 个模块会积累大量知识，需要一个体系来管"
- "任务卡让我们知道谁在做什么、什么完成了"

**当前空白**：
- 没有任务分解 → AI 可以绕过规划直接写代码
- 没有知识沉淀 → 每个 AI session 从零开始，无法积累

---

## 3. 边界

### 3.1 覆盖

- TaskCard YAML Schema 定义
- 任务卡生命周期（draft → in_progress → review → done）
- KMS 三层漏斗架构
- KE 知识条目模板
- Session 产物链追踪（哪个 Session 产出了哪些任务卡）

### 3.2 不覆盖（→ 去哪）

- 蓝图 Schema 定义 → `templates/blueprint-template.md`
- Vector Memory 实现 → M2 模块
- AI 自治权限注册 → `_registry/catalogs/ai-autonomy-authority-registry.md`

---

## 4. 输入 / 基于此设计

| 输入 | 来源 |
|------|------|
| PS-STD-004 规则分类标准 | 10 域管控体系 |
| PS-STD-002 文档框架标准 | Doc-ID 与索引体系 |
| PS-STD-007 KMS 分层政策 | 最佳实践入库锁（KE-001~010）|
| Owner "知识复用"诉求 | AI 写之前先查 KB |

---

## 5. 架构决策

### 5.1 TaskCard YAML Schema

```yaml
task_id: "TASK-PH1-003"
blueprint_ref: "03_modules/l01_infrastructure/capacity-assurance/blueprint.md"
construction_plan_ref: "03_modules/l01_infrastructure/capacity-assurance/construction-plan.md"
phase: "experimental"
status: in_progress
deps:
  - TASK-PH0-002
estimated_hours: 4
assignee: "AI-GLM-5.1"
session_ref: "sessions/session-20260501-003.md"
tags: ["capacity-assurance", "slo", "phase-1a"]
```

### 5.2 任务状态机（10 状态，GOV-TASK-004 治理层审定）

> **来源**：本状态机经治理层 `task-lifecycle-standard.md`（GOV-TASK-004）审计后定义，是对 §3.2 简版 6 状态的正式升级。对齐 Jira / ServiceNow / Linear / Azure DevOps / GitHub Issues 五大系统标准。

```
PENDING     → IN_PROGRESS, BLOCKED, CANCELLED
IN_PROGRESS → COMPLETED, FAILED, BLOCKED, WAITING
COMPLETED   → VERIFIED, IN_PROGRESS
VERIFIED    → （终态）
FAILED      → RETRY, CANCELLED
BLOCKED     → READY, CANCELLED
WAITING     → READY, CANCELLED
READY       → IN_PROGRESS, CANCELLED
RETRY       → IN_PROGRESS, FAILED
CANCELLED   → （终态）
```

**终态**：VERIFIED（验收通过）、CANCELLED（已取消）

| 状态 | 语义 | 谁负责 | 典型停留时间 |
|------|------|--------|------------|
| PENDING | 已创建，等待执行 | 系统分配 | ≤ 1 session |
| IN_PROGRESS | 正在执行 | 执行 AI | 取决于 estimate_hours |
| COMPLETED | 执行完毕，待验证 | 执行者声明 | ≤ 1 session |
| VERIFIED | 验证通过，终态 | 验证者确认 | 永久 |
| FAILED | 执行失败 | 执行者报告 | ≤ 1 session |
| BLOCKED | 被外部依赖阻塞 | 执行者报告 | 取决于阻塞原因 |
| WAITING | 等待资源/审批 | 执行者报告 | 取决于等待对象 |
| READY | 阻塞解除，可继续 | 系统自动检测 | ≤ 1 session |
| RETRY | 重试中 | 执行者决定 | ≤ 1 session |
| CANCELLED | 已取消，终态 | Owner 审批 | 永久 |

### 5.3 门禁系统（G0-G6）

| 门禁 | 触发时机 | 检查内容 |
|------|---------|---------|
| G0 创建门禁 | 任务创建 | 字段完整性、task_id 格式、路径存在性、枚举值合法性 |
| G1 启动门禁 | 开始执行 | 依赖全部 VERIFIED、files_in_scope 路径存在 |
| G2 阻塞门禁 | 报告阻塞 | 阻塞原因非空、depends_on 中有未完成任务 |
| G3 等待门禁 | 报告等待 | waiting_for 字段非空 |
| G4 完成门禁 | 声明完成 | deliverables 全部存在、acceptance 达标、无残留 |
| G5 验证门禁 | 验证通过 | 编码合规、清扫通过、验收确认 |
| G6 失败门禁 | 报告失败 | 失败原因非空、重试 < 3 次 |

### 5.4 超时与升级规则

| 状态 | 超时阈值 | 超时后动作 |
|------|---------|-----------|
| PENDING | 3 session | 自动降优先级 |
| IN_PROGRESS | 2×estimate_hours | 自动报告 WAITING |
| BLOCKED / WAITING | 5 session | 自动升级到 Owner |

**升级触发**：P0 阻塞超 2 session、任何任务阻塞超 5 session、P0 失败 2 次 → Session Log 标记 `escalation:owner`。AI 不得跳过升级直接做决策。

### 5.5 代码消费者注册表

| 消费者 | 依赖内容 | 同步要求 |
|--------|---------|---------|
| `src/zephyr/shared/schemas.py` TaskStatus | 10 状态枚举 | 枚举变更同 commit 更新 |
| `src/zephyr/db/sqlite_schema.py` | DDL CHECK 约束 | DDL 变更需迁移脚本 |
| `scripts/governance/check_handoff_protocol.py` | 任务状态校验 | 状态语义变更需同步 |

### 5.6 KMS 三层漏斗

| 层 | 名称 | 存储 | 内容 |
|:--:|------|------|------|
| L1 | Session 层 | SQLite 临时索引 | Session Log 产物链映射 |
| L2 | Draft 层 | `08_knowledge/drafts/` | LLM 输出 → Knowledge Proxy 预审 |
| L3 | Formal 层 | `08_knowledge/best-practices/` | 最终入库的 KE 条目 |

### 5.7 KE 知识条目模板结构

每个 KE 知识条目（Knowledge Entry）=`KE-{编号}-{标题}.yaml`，存放在 `docs/08_knowledge/`。结构：

- `title`：知识标题
- `body`：知识正文
- `source`：来源（ADR / 蓝图 / Session / 模块池迁移）
- `audit_chain`：审计链
- `phase`：落地阶段
- `applicable_layers`：适用层级
- `_locked`：锁定状态（true = 不可修改）

---

## 6. 架构视图

### 6.1 Phase 路线图

| Phase | 名称 | 交付物 |
|-------|------|--------|
| **0** | 结构发布 | TaskCard Schema 定稿 + KMS 模板定稿 |
| **1** | 制度运行 | 任务卡制度正式启用，KMS 三层漏斗上线 |
| **2** | 自动化 | Session 产物链自动追踪 + KE 自动入库 |

### 6.2 验收标准

| 维度 | 指标 | 目标 |
|------|------|------|
| 任务卡 | 任务卡颗粒度 | ≤ 1 天/卡 |
| 知识库 | KE 条目数 | ≥ 50 |
| 追踪 | Session 产物链完整性 | 100% |
| 自动化 | KE 自动入库占比 | ≥ 70% |

---

## 7. 触发条件与扩展路径

| 条件 | 动作 |
|------|------|
| 模块 > 100 | 任务卡 batch 批量分配 |
| KE 条目 > 500 | 引入 Vector Memory 语义检索 |
| Session Log > 1000 | 引入 Session 归档策略（TTL 30 天） |

---

## 8. 风险与缓解

| 风险 | 概率 | 缓解 |
|------|------|------|
| 任务卡过细导致管理开销暴增 | 中 | 最小颗粒度 0.5 人日/卡 |
| KMS 知识过时 | 中 | `_locked` 标记 + 定期复审（每月一次） |
| Session 产物链断裂 | 低 | 自动化追踪脚本 |

---

## 9. 关键关联

| 关联文档 | 说明 |
|---------|------|
| PS-STD-004 规则分类标准 | 10 域管控体系 |
| `adr-0005-kms-architecture.md` | KMS 架构 ADR（最佳实践入库） |
| `module-registry.yaml` | 任务卡关联的模块登记 |
| `session-log-schema.yaml` | Session 产物链格式 |

## 10. 实际代码实现情况（Code Implementation Status）

> **本节记录蓝图对应的实际代码，证明 experimental 构建确实完成——非纸面设计。**

| 代码文件 | 对应蓝图节 | 实现内容 |
|---------|:---:|------|
| `src/zephyr/db/sqlite_schema.py` | §5.2 / §5.5 | tasks 表 DDL + CHECK 约束（10 状态枚举） |
| `src/zephyr/mcp/task_manager_server.py` | §5.1 | TaskCard 解析 / 序列化 / MCP task_manager 工具 |
| `src/zephyr/core/blueprint_decomposer.py` | §5.1 | 蓝图 → TaskCard 自动分解 |
| `src/zephyr/pipeline/pipeline_orchestrator.py` | §6.1 | 任务卡管线派发 |
| `src/zephyr/gates/task_completion_gate.py` | §5.3 G7 | G7 任务完成门禁 |
| `src/zephyr/gates/g4_activate.yaml` | §5.3 G4 | KMS 条目 Schema 校验配置 |

**实现判定**：experimental 蓝图所述的核心功能（任务卡 Schema、10 状态机、G0-G7 门禁、Pipeline 派发、KMS 三层漏斗）均有对应磁盘代码——非空设计文档。

> **历史溯源**：原始施工图由 Wave 0 终审产出。2026-05-01 迁入 `03_modules/l01_infrastructure/task-card-kms/blueprint.md`，内容保留，结构按蓝图模板重组。

---

## 11. 已实现代码完整路径索引

> **AGENTS.md §6.14 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> 任务卡+KMS——experimental构建完成，已升级为MOD-INF-006

### 11.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `src/zephyr/db/sqlite_schema.py` | ✅ 已实现 | |
| `src/zephyr/mcp/task_manager_server.py` | ✅ 已实现 | |
| `src/zephyr/core/blueprint_decomposer.py` | ✅ 已实现 | |
| `src/zephyr/pipeline/pipeline_orchestrator.py` | ✅ 已实现 | |
| `src/zephyr/gates/task_completion_gate.py` | ✅ 已实现 | |
| `src/zephyr/gates/g4_activate.yaml` | ✅ 已实现 | |

### 11.2 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/unit/test_sqlite_schema.py` | ✅ 已实现 | |
| `tests/unit/test_mcp_servers.py` | ✅ 已实现 | |
| `tests/unit/test_pipeline_orchestrator.py` | ✅ 已实现 | |
| `tests/unit/test_task_completion_gate.py` | ✅ 已实现 | |

### 11.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §11（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

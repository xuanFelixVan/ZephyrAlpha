---
module_id: ADR-0013
title: 治理系统准入铁律（Governance System Admission Criteria）
doc_type: adr
status: active
version: 1.0.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: 2026-04-21
superseded_by: null
supersedes: null
related_rationale: []
related_open_questions: []
tags:
- adr
- governance
- admission-criteria
- iron-law
- architecture-as-code
summary: '定义治理系统准入四铁律（GOV-P1~P4），防止治理系统无序膨胀。 任何新增治理系统必须通过四道门禁才能进入 09-GOV 归属表。

  '
date: '2026-04-22'
ttl: permanent
---

# ADR-0013：治理系统准入铁律

## 1. 状态（Status）

- **当前状态**：`accepted`
- **提议日期**：2026-04-21（Architecture-as-Code v2.0 Phase D 批次）
- **拍板日期**：2026-04-21
- **被谁取代**：无
- **取代了谁**：无（首次定义治理系统准入门禁）

## 2. 上下文（Context）

### 2.1 触发原因

09-governance-architecture.md 已登记 **45 个治理系统**（A21+B1+C16+VB1+D6）。随着项目演进，新治理需求不断涌现。如果没有准入门禁，治理系统数量会无序膨胀，导致：

1. **治理债务**：系统登记但永远不激活，占用认知预算
2. **职责重叠**：新系统与现有系统功能重复
3. **激活瓶颈**：Sprint 计划被过多治理系统挤占

### 2.2 业界对标

| 机构 | 治理准入机制 |
|---|---|
| Goldman Sachs | Governance Review Board（GRB）审批 + 年度治理预算 |
| Two Sigma | Engineering Council 投票 + 成本效益分析 |
| Netflix | "Freedom & Responsibility" 原则 + 季度治理审计 |
| Google | Design Review + Launch Approval |

## 3. 决策（Decision）

### 3.1 四铁律（GOV-P1 ~ GOV-P4）

任何新增治理系统必须**依次通过**以下四道门禁：

#### GOV-P1：必要性证明（Necessity Proof）

> **问**：现有 45 个系统中，是否已有系统覆盖此需求？

| 判定 | 处置 |
|---|---|
| 已有系统完全覆盖 | **驳回**，使用现有系统 |
| 已有系统部分覆盖 | **扩展**现有系统，不新建 |
| 确无覆盖 | 通过，进入 GOV-P2 |

**必须提供**：一句话说明"为什么现有 45 个系统无法覆盖"。

#### GOV-P2：家族归属（Family Assignment）

> **问**：新系统属于哪个家族？

| 家族 | 准入条件 |
|---|---|
| A（机构标配）| 业界 top-tier 机构普遍具备 |
| B（元治理）| 治理治理系统的系统（极少新增）|
| C（氛围独有）| AI 协作 / vibe coding 专有 |
| D（AI 治理基建）| AI 员工安全/决策/情报基础设施 |
| VB（共享底座）| 跨家族共享规则（极少新增）|

**必须提供**：家族归属 + 主层（Policy/Factory/Runtime）+ 次层。

#### GOV-P3：激活时间窗（Activation Window）

> **问**：何时激活？有明确的 Sprint 或触发条件吗？

| 判定 | 处置 |
|---|---|
| 有明确 Sprint 编号 | 通过 |
| 有明确触发条件（T1-T6）| 通过 |
| "以后再说" / 无时间窗 | **驳回**——不登记无期限系统 |

#### GOV-P4：退出条件（Exit Criteria）

> **问**：什么情况下此系统应被废弃或合并？

**必须提供**：至少一条退出条件（如"当 X 系统升级覆盖此功能时合并"）。

### 3.2 准入流程

```
提案 → GOV-P1 必要性 → GOV-P2 家族归属 → GOV-P3 激活时间窗 → GOV-P4 退出条件
  ↓         ↓ 驳回          ↓                    ↓ 驳回              ↓
  ↓      使用现有系统      登记家族+层           不登记            登记退出条件
  ↓                                                                  ↓
  └──────────────────── 通过全部四道 ──────────────────────────→ 写入 09-GOV §4
                                                                     ↓
                                                              更新 scripts-model.yaml
                                                              （如涉及 scripts/ 域）
```

### 3.3 豁免条件

以下情况可跳过 GOV-P1~P4：
- **P0 红线级安全系统**（如 D-01 AISG）：由 Owner 直接批准，事后补办准入记录
- **外部合规强制要求**（如监管新规）：附合规文件编号，事后补办

## 4. 后果（Consequences）

### 4.1 正面

- 治理系统数量受控，认知预算可预测
- 每个系统都有明确的激活时间窗和退出条件
- 防止"登记即遗忘"的治理债务

### 4.2 负面

- 紧急治理需求需要走豁免流程（增加一步审批）
- 准入门禁本身需要维护（B-01 元治理职责）

### 4.3 与现有体系的关系

| 关联 | 说明 |
|---|---|
| 09-GOV §4 | 新系统通过准入后写入对应家族表 |
| B-01 元治理 | 准入流程本身由 B-01 管理 |
| scripts-model.yaml | 涉及 scripts/ 域的新系统同步更新 YAML 模型 |
| AGENTS.md §八-B.B3 | 与治理资产准入门禁 6 步流程对齐 |

## 5. 修订记录

| Date | Version | Description |
|---|---|---|
| 2026-04-21 | v1.0.0 | 首次发布：GOV-P1~P4 四铁律 + 准入流程 + 豁免条件 |

> 完整修订历史：`git log --oneline -- adr-0013-governance-system-admission-criteria.md`

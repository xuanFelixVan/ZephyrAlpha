---
module_id: GOV-ARCH-001
title: ADR 协议
doc_type: protocol
status: draft
version: "0.2.0"
layer: l01_infrastructure
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
date: "2026-05-01"
valid_from: "2026-05-01"
ttl: permanent
summary: "定义架构决策记录（ADR）的协议——谁提ADR、怎么审批、怎么归档。与已冻结ADR的关系。"
tags: [architecture, governance, adr, protocol]
rule_form: declarative
scope: global
stability: evolving
verifiability: manual
ai_autonomy: human_gated
---

# ADR 协议

> **module_id**: GOV-ARCH-001 | **version**: 0.2.0 | **status**: draft | **layer**: L1

本文件定义 ADR（架构决策记录）的协议——**谁提 ADR、怎么审批、怎么归档、怎么废弃**。与分析 ADR 系统本身的关系。

---

## 1. 目的与范围

本协议定义 ZephyrAlpha 系统中架构决策记录（ADR）的管理规则。适用于：

- 新增架构决策
- 修改已有架构决策
- 废弃架构决策

**与已冻结 ADR 的关系**：ADR 系统已于 2026-04-27 冻结（ADR-0001~ADR-0041 已归档）。本协议适用于冻结后的新决策。

---

## 2. 规则

### ADR-001：什么情况下必须创建 ADR

| 类型 | 举例 |
|------|------|
| 新增/删除模块 | 新增风控引擎、删除因子组合模块 |
| 修改模块间接口 | 改变模块 A 和模块 B 之间的数据格式 |
| 更换核心技术栈 | 从 Pandas 切换到 Polars |
| 修改数据流方向 | 从实时流改为批量处理 |

> **判定原则**：除上表 4 类明确触发场景外，任何涉及**系统边界、模块契约、数据完整性或技术选型**的变更，AI 应主动询问 Owner 是否需要 ADR。最终判定权在 Owner。| 验证：`validate_architecture.py` 检查 ADR 编号连续性 |

### ADR-002：ADR 编号连续递增

| 编号 | 规则 | 违反后果 |
|------|------|---------|
| ADR-002 | ADR 编号从 0042 开始（接续已冻结的 41 个 ADR），连续递增，禁止跳号 | 编号冲突 |

### ADR-003：ADR 状态机

| 编号 | 规则 | 违反后果 |
|------|------|---------|
| ADR-003 | ADR 状态：draft → accepted → deprecated。禁止回退状态 | 状态混乱 |

### ADR-004：ADR 审批

| 条件 | 规则 | 违反后果 |
|------|------|---------|
| 新增 ADR | 必须由 Owner 审批后才能标记为 accepted | ADR 保持 draft 状态 |
| 废弃 ADR | 必须有替代 ADR 或明确说明废弃原因 | 不得标记为 deprecated |

---

## 3. ADR 模板

```markdown
# ADR-{NNN}: {标题}

## 状态
{draft/accepted/deprecated}

## 日期
{YYYY-MM-DD}

## 上下文
{为什么要做这个决策？}

## 决策
{我们决定怎么做？}

## 后果
{正面和负面影响}

## 否决方案
{考虑过但否决的方案及理由}
```

---

## 4. 验证方式

| 规则 | 验证方式 | 频率 |
|------|---------|------|
| ADR-001 | 检查重大变更是否有对应 ADR | 每次变更 |
| ADR-002 | 检查 ADR 编号是否连续 | 每次新增 |
| ADR-003 | 检查 ADR 状态转换是否合法 | 每次状态变更 |
| ADR-004 | 检查新增ADR是否有Owner审批记录 / 废弃ADR是否有替代ADR或废弃原因记录 | 每次新增/废弃 |

---

## 5. 修订记录

| 日期 | 版本 | 修改内容 |
|------|------|---------|
| 2026-05-01 | 0.2.0 | #18 审批修复。(1) 编号前缀：ABS/COND → ADR-（ADR-001~ADR-004，编号从0042起接续已冻结的41个ADR）。(2) `ai_autonomy: human_gated`。(3) §4 验证：补齐ADR-004验证条目。(4) ADR-003：状态表改为三栏，补充 deprecated 两种语义说明（废弃/替代）。(5) ADR-001：补充判定原则——任何涉及系统边界、模块契约、数据完整性或技术选型的变更，AI主动询问Owner是否需要ADR。移除 `depends_on: GOV-ARCH-002`（ADR协议定义ADR生命周期时不需要评审门控）。`date` → 2026-05-01。 |
| 2026-04-30 | 0.1.0 | 初始版本 |

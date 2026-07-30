---
module_id: VIEW-04PRINC-AI-FIRST-GOV
title: AI-First Governance Principles / 100% AI 开发治理原则
doc_type: architecture_view
ttl: permanent
status: Active
version: 2.0.0
layer: cross_layer
owner: ZephyrAlpha-Owner
language: zh
created_by: agent
valid_from: 2026-07-30
superseded_by: null
supersedes: null
tags:
- ai-first
- governance
- rule-execution-pairing
- root-cause
- strategic-rulings
summary: 100% AI 开发场景下的治理永恒原则——5 个病根分析 + 5 条战略裁定。施工框架 4 期已全部完成，过时施工状态已删除。议题真源在 architecture_issue_registry.yaml，裁定真源在 ruling_registry.yaml，审计维度清单在 trae_081_audit_dimensions_framework.yaml。
date: '2026-07-30'
ttl: permanent
---

# AI-First Governance Principles / 100% AI 开发治理原则

> **文档性质**：100% AI 开发场景下的治理战略原则——5 个病根 + 5 条裁定。
> **关联真源**：议题 [`architecture_issue_registry.yaml`](../../../01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml) | 裁定 [`ruling_registry.yaml`](../../../01_policies_and_standards/_registry/catalogs/ruling_registry.yaml) | 审计维度 [`trae_081_audit_dimensions_framework.yaml`](../../../01_policies_and_standards/rules/trae_081_audit_dimensions_framework.yaml)

---

## 一、核心矛盾

**规则 : 执行 ≈ 10 : 1**。

100% AI 开发场景下，"建议性规则"是反模式——AI 没有"自觉"，只有"被阻断"。治本方向是把建议性规则转化为强制消费链（AST 门禁）。

---

## 二、病根分析（5 个根因）

1. **静态快照未动态更新**：违规清单是静态快照，未随项目演进动态更新——规则应是判断标准，违规清单是事实快照；把事实快照冻结进文档 = 让规则随时间脱节。
2. **词表消费链机械盲区**：词表→代码的强制消费链是"模式匹配"而非"语义匹配"，代码可用变体命名绕过正则检测。
3. **CapabilityLookup 建议性**：对"新建重复实现"仅 warn-only（不阻断），新 AI 查不到就重复造轮子。
4. **manual 例外开口过大**：永久功能与一次性脚本未区分，"永久性"是语义概念无机械判定标准，所有脚本统一标 `# [STARTUP] manual`，规则成了无牙老虎。
5. **规则膨胀执行断层（隐藏元根因）**：规则文档自身膨胀，AI 上下文有限 → "规则膨胀→上下文不足→执行断层→加更多规则"负反馈循环。

---

## 三、战略层裁定（针对 100% AI 开发）

### 裁定 1：新增规则必须同时新增门禁（规则-执行配对铁律）

> 裁定#221

每条新规则 MUST 在同 commit 内配套落地强制执行机制（AST commit gate / reconciler / CI check）。无执行机制的规则 = 建议性规则 = 100% AI 开发场景下的反模式。

> 由 `RULE-EXECUTION-PAIRING` gate 强制——`trae_*.yaml` 规则文件 MUST 有 `enforcement.paired_gate_id` 字段。

### 裁定 2：治标 vs 治本分类

- **治本** = 建立强制消费链（AST 门禁 / reconciler / hook）使同类问题不再可能产生
- **治标** = 修个别违规点

每个存量修复 MUST 配套落地对应防复发机制，形成"修复 + 防复发"闭环。无防复发的修复 = 治标。

### 裁定 3：强制消费链做成 AST 门禁

AI 上下文有限 = AI 必然跳过部分规则 = 依赖 AI 自觉的规则必然失效；AST 门禁在 commit 时阻断、不依赖 AI 记忆，是 100% AI 开发场景下唯一可靠的执行层。

### 裁定 4：必须建"架构健康度仪表盘"

把"静态快照"变成"动态实时"——每次 commit 自动生成全维度违规清单，直接治根因 1，间接治根因 3，并把离散报告变成趋势曲线。

### 裁定 5：DEFERRED vs DEFERRED-PERMANENT 分类法

| 状态 | 含义 | AI 可否自行修复 |
|---|---|---|
| `DEFERRED` | 正常债务——AI 可在未来 cycle 逐步修复 | ✅ 可（有明确修复路径） |
| `DEFERRED-PERMANENT` | 永久债务——需 human-led 架构工程 | ❌ 不可（需人类架构决策） |

**执行规则**：AI 在债务修复 cycle 中 MUST 优先选 DEFERRED 项；禁止自行修复 DEFERRED-PERMANENT 项。解锁条件：人类架构师发起专项工程（#ARCH-XXX 裁定 + 蓝图 + 施工计划）。

> 40 项 wontfix 已经裁定#222 确认关闭，登记为 #ARCH-DEBT-001~006。

---

## 四、维护规则

- **新增规则**：MUST 同时新增门禁（裁定#221），由 RULE-EXECUTION-PAIRING gate 强制。
- **新增议题**：MUST 在 `architecture_issue_registry.yaml` 登记 #ARCH-XXX 条目。
- **新增裁定**：MUST 在 `ruling_registry.yaml` 登记裁定#NNN 条目，由 RULING-REFERENCE gate 强制。
- **wontfix 翻案**：MUST 经架构师新裁定并更新 #ARCH-DEBT-NNN 条目。
- **违规数据**：禁止手工编辑——由架构健康度仪表盘自动生成。
- **审计维度**：见 `trae_081_audit_dimensions_framework.yaml`（54 维度清单基座）。

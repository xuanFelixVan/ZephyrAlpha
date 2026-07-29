---
module_id: VIEW-04PRINC-AI-FIRST-GOV
title: AI-First Governance Principles / 100% AI 开发治理原则
doc_type: architecture_view
ttl: permanent
status: Active
version: 1.0.0
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: agent
valid_from: 2026-07-24
superseded_by: null
supersedes: null
related_rationale:
- 裁定#221
- 裁定#222
related_open_questions: []
tags:
- ai-first
- governance
- rule-execution-pairing
- root-cause
- strategic-rulings
summary: 100% AI 开发场景下的治理永恒原则——5 个病根分析 + 5 条战略裁定。源自 architecture_debt_registry v2.0.0 §二§三（已归档至 docs/_archive/），裁定1 经裁定#221 修正为"新增规则必须同时新增门禁"。wontfix 债务 40 项经裁定#222 确认并登记为 #ARCH-DEBT-001~006。本文件是 AI 治理战略原则真源，活跃议题真源在 architecture_issue_registry.yaml，裁定真源在 ruling_registry.yaml，审计维度清单在 trae_081_audit_dimensions_framework.yaml。
date: '2026-07-24'
ttl: permanent
---

# AI-First Governance Principles / 100% AI 开发治理原则

> **文档性质**：100% AI 开发场景下的治理战略原则——5 个病根 + 5 条裁定。
> **来源**：源自 `architecture_debt_registry.md` v2.0.0 §二（病根分析）§三（战略裁定），该文档已归档至 [`docs/_archive/architecture_debt_registry_v2.md`](../../../_archive/architecture_debt_registry_v2.md)。
> **修正记录**（2026-07-24，裁定#221）：原裁定1"暂停新增规则文档 6 个月"表述错误，已修正为"新增规则必须同时新增门禁"。
> **关联真源**：议题真源 [`architecture_issue_registry.yaml`](../../../01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml) | 裁定真源 [`ruling_registry.yaml`](../../../01_policies_and_standards/_registry/catalogs/ruling_registry.yaml) | 审计维度清单 [`trae_081_audit_dimensions_framework.yaml`](../../../01_policies_and_standards/rules/trae_081_audit_dimensions_framework.yaml)

---

## 一、核心矛盾

**规则 : 执行 ≈ 10 : 1**。

100% AI 开发场景下，"建议性规则"是反模式——AI 没有"自觉"，只有"被阻断"。治本方向是把建议性规则转化为强制消费链（AST 门禁）。

---

## 二、病根分析（5 个根因）

历史违规问题归因于 5 个根因（抽象概念，详细证据链见 git log）：

1. **静态快照未动态更新**：违规清单是静态快照，未随项目演进动态更新——规则应是判断标准（"禁止硬编码"），违规清单是事实快照（"今天发现 N 处"）；把事实快照冻结进 `stability: frozen` 文档 = 让规则随时间脱节。
2. **词表消费链机械盲区**：词表→代码的强制消费链是"模式匹配"而非"语义匹配"，GATE-VOCAB 是"部分强制"——代码可用 `_STAB = "frozen"` 等变体命名绕过正则检测。
3. **CapabilityLookup 建议性**：CapabilityLookup 是"建议性反查"而非"强制性消费"——对"新建重复实现"仅 warn-only（不阻断），新 AI 查不到就重复造轮子。
4. **manual 例外开口过大**：永久功能与一次性脚本未区分——"永久功能禁止 manual-only"无机械判定标准（"永久性"是语义概念），所有脚本统一标 `# [STARTUP] manual`，规则成了无牙老虎。
5. **规则膨胀执行断层（隐藏元根因）**：规则文档自身膨胀，AI 上下文有限 → "规则膨胀→上下文不足→执行断层→加更多规则"负反馈循环；"治本"标注多为局部治本（修个别违规点），非系统治本（建强制消费链）。

---

## 三、战略层裁定（针对 100% AI 开发）

### 裁定 1：新增规则必须同时新增门禁（规则-执行配对铁律）

> **裁定#221**（2026-07-24，修正原"暂停新增规则 6 个月"表述）

**第一性原理**：100% AI 开发场景下，规则与执行 MUST 成对存在（Rule-Execution Pairing）。每条新规则 MUST 在同 commit 内配套落地强制执行机制（AST commit gate / reconciler / CI check）。无执行机制的规则 = 建议性规则 = 100% AI 开发场景下的反模式（AI 无自觉，只有被阻断）。

**修正理由**：原表述"暂停新增规则文档 6 个月"是懒政——冻结规则演进 6 个月，但 6 个月后元问题（规则膨胀执行断层）依旧，且阻止了必要的治理能力建设。真正的治本是强制规则-执行配对，而非冻结规则创建。

**强制机制**：[`RULE-EXECUTION-PAIRING`](../../../../src/zephyr/gov_enforcement/commit_gates/rule_execution_pairing_gate.py) gate（priority=61）已落地——`trae_*.yaml` 规则文件 MUST 有 `enforcement.paired_gate_id` 字段（null 允许文档型规则，字符串须在 gate_registry 注册，`[no-pairing:reason]` 逃生通道）。本裁定将该 commit-time 机制上升为战略原则。

### 裁定 2：治标 vs 治本分类

治本定义 = 建立强制消费链（AST 门禁 / reconciler / hook）使同类问题不再可能产生；治标定义 = 修个别违规点。历史问题中约 80% 治标、20% 治本——"治本"标注虽多，但大多是局部治本（修一类文件），不是系统治本（建一类门禁）。

**执行约束**：每个存量修复 MUST 配套落地对应防复发机制（AST gate / reconciler / metric 监控），形成"修复 + 防复发"闭环。无防复发的修复 = 治标。

### 裁定 3：强制消费链做成 AST 门禁（有优先级）

AI 上下文有限 = AI 必然跳过部分规则 = 依赖 AI 自觉的规则必然失效；AST 门禁在 commit 时阻断、不依赖 AI 记忆，是 100% AI 开发场景下唯一可靠的执行层。

按"违规后果严重度 × 发生频率"ROI 排序（均已落地）：P0 manual-only 永久脚本检测器 / P0 词表硬编码语义级检测器 / P1 新 GATE 登记 capability hook / P1 重复簇新建阻断 / P2 文件复制对检测 / P2 空 handler 检测。

### 裁定 4：必须建"架构健康度仪表盘"（最高优先级基础设施）

把"静态快照"变成"动态实时"，每次 commit 自动生成全维度违规清单——直接治根因 1，间接治根因 3，并把离散报告变成趋势曲线。

**已实现**：[`architecture_health_dashboard.py`](../../../../scripts/governance/architecture_health_dashboard.py) + post-commit reconciler，M01-M31 指标快照落盘 `data/architecture_health/`。后续增量违规由仪表盘实时基线自动发现，不再依赖人工调研快照。

### 裁定 5：DEFERRED vs DEFERRED-PERMANENT 分类法（存量债务管理框架）

存量债务风险等级差异显著——混为一谈会导致 AI 误选高风险项浪费上下文，或误判"全部 DEFERRED = 全部永久搁置"。二分法：

| 状态 | 含义 | 适用范围 | AI 可否自行修复 |
|---|---|---|---|
| `DEFERRED` | 正常债务——AI 可在未来 cycle 逐步修复 | 中低风险项（命名统一 / shim 标注 / 类型注解补全等） | ✅ 可（有明确修复路径） |
| `DEFERRED-PERMANENT` | 永久债务——需 human-led 架构工程，AI 不应自行尝试 | 高风险项（架构重构）+ 设计决策项 | ❌ 不可（需人类架构决策） |

**执行规则**：
1. AI 在债务修复 cycle 中 MUST 优先选 DEFERRED 项（有明确修复路径）。
2. AI 禁止自行修复 DEFERRED-PERMANENT 项——尝试即浪费上下文。
3. DEFERRED-PERMANENT 项解锁条件：人类架构师发起专项工程（#ARCH-XXX 架构裁定 + 蓝图 + 专项施工计划）；或经架构师逐项裁定转为 EXECUTE（立即施工）/ RATIFY（wontfix 关闭，验证防复发门禁在册）。

**当前状态**：全部 DEFERRED-PERMANENT 项已完成逐项裁定（裁定#222 确认 40 项 wontfix，登记为 #ARCH-DEBT-001~006，详见 [`architecture_issue_registry.yaml`](../../../01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml)）。

---

## 四、治本施工框架（4 期，全部完成）

> 铁律：每完成一类存量修复 MUST 配套落地对应 AST 门禁，形成"修复 + 防复发"闭环。

| Phase | 内容 | 状态 |
|---|---|---|
| Phase 0 | 架构健康度仪表盘（数据基座，治根因 1） | ✅ 已完成（M01-M31） |
| Phase 1 | AST 门禁（防复发层，治根因 5，贯穿全程） | ✅ 已大量落地，持续运行（81 个 gate） |
| Phase 2 | 批量修复（治标存量） | ✅ 已完成（54 维度清零） |
| Phase 3 | 治理层收敛（治本存量） | ✅ R102 EXECUTE 27 项 + R103 EXECUTE 3 项全部治本完成；40 项 wontfix 经裁定#222 确认关闭 |

---

## 五、维护规则

- **新增规则**：MUST 同时新增门禁（裁定#221），由 RULE-EXECUTION-PAIRING gate 强制。
- **新增议题**：MUST 在 [`architecture_issue_registry.yaml`](../../../01_policies_and_standards/_registry/catalogs/architecture_issue_registry.yaml) 登记 #ARCH-XXX 条目（铁律#6）。
- **新增裁定**：MUST 在 [`ruling_registry.yaml`](../../../01_policies_and_standards/_registry/catalogs/ruling_registry.yaml) 登记 裁定#NNN 条目（裁定#20-A），由 RULING-REFERENCE gate 强制。
- **wontfix 翻案**：MUST 经架构师新裁定（裁定#NNN）并更新 #ARCH-DEBT-NNN 条目的 related_adjudication + last_updated。
- **违规数据**：禁止手工编辑——由架构健康度仪表盘（M01-M31）自动生成。
- **审计维度**：见 [`trae_081_audit_dimensions_framework.yaml`](../../../01_policies_and_standards/rules/trae_081_audit_dimensions_framework.yaml)（54 维度清单基座）。

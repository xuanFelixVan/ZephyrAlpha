---
module_id: KE-187---ai-005
status: active
title: 2.3 "Single operator + AI" 人机协同特例 / 单人 + AI 协同的 R/A 重合处理
category: documentation
---

# 2.3 "Single operator + AI" 人机协同特例 / 单人 + AI 协同的 R/A 重合处理

2.3 "Single operator + AI" 人机协同特例 / 单人 + AI 协同的 R/A 重合处理

在当前阶段（single operator，多 AI 协作，`ai_operators_registry.md` 尚未激活），上表的 R/A 在物理上大量重合到**同一个人（you）**，这是真实场景，但**必须显式说明**，否则未来引入合伙人 / AI Operators 时责任真空会浮现。

**协同规则（本视图的铁律）**：

1. **A（Accountable）不可委托**：即使 AI 生成了 ADR、回测报告、甚至下单代码，最终 **A 仍是 you**（S1-S7 物理合一）。AI 不承担问责，只承担 R/C。
2. **R（Responsible）可以渐进迁移到 AI**：当前 R 大量落在 you；**未来 AI Operators 激活后**，A04 / A06 / A07 / A08 / A10 / A11 的 R 列会从 you 迁移到 S9（标注 "R（未来）"的列）；A 列永远不变。
3. **AI collaborators (S8) 的职责边界**：仅限 **C（Consulted）**——提供候选方案、文档草稿、红队质疑。**不进入 R/A**。AI 产出必须由 you 的某个物理角色（S1-S7）签字承接才落盘。
4. **人机协同日志**：所有 R=you + C=S8 的活动，其决策日志按 `OQ-063` 七维度字段（身份/触发/输入/推理/决策/执行/审计）完整记录到 `META_GOVERNANCE/`，未来审计可溯源。
5. **升级触发**：当 S11（合伙人）或 S12（监管）激活时，本表必须重新评审 A 列（当前由 you 兜底的 A 可能需要拆给专职角色）；由 `OQ-063` 同级 OQ 管理升级流程。

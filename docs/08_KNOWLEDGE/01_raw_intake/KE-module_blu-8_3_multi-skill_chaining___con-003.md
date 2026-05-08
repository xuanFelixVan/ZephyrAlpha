---
module_id: KE-module_blu-8_3_multi-skill_chaining___con-003
title: 8.3 Multi-Skill Chaining & Context Window Management（决策 D-019-08）
category: module_blueprint
---

# 8.3 Multi-Skill Chaining & Context Window Management（决策 D-019-08）

8.3 Multi-Skill Chaining & Context Window Management（决策 D-019-08）

> **决策 D-019-08（新增）**：SkillLoader 必须支持链式调用和多 Skill 并发管理——防止 Skill 链中出现循环依赖、上下文窗口碎片化、以及 Skill 间的指令冲突导致的 emergent 行为。
>
> **决策依据**：
> - Anthropic Claude 在多 Skill 同时加载时会按加载顺序排列 Skill 指令——后面的可能覆盖前面的
> - 上下文窗口碎片化是实际生产中 Agent 失败的第二大原因（22%，来源：150+ 项目调研 2026 Q1）
> - 链式调用中可能出现循环（Skill A 触发 Skill B，B 的输出触发 A）——需要循环检测

```yaml
skill_chaining:
  description: "多 Skill 串联与并发管理协议"

  chain_trigger:
    description: "Skill 执行过程中可能发现需要另一个 Skill"
    scenarios:
      - "实现者 + database-specialist 在施工中遇到 MCP 相关代码 → 自动加载 mcp-specialist"
      - "治理员 + drift-detector 检测到门禁异常 → 自动加载 gate-specialist"

  chain_depth_limit:
    max_depth: 3   # 最多串联 3 层 Skill（防止无限嵌套）
    violation_action: "暂停链，将所有已加载 Skill 的摘要写入 Session Log → 升级到 Owner"

  circular_chain_detection:
    description: "检测 Skill A → Skill B → Skill A 的循环"
    method: "已加载 Skill 的 id 集合检查（O(1) lookup）"
    violation_action: "立即终止链 → 写入 Audit Trail 的 ANOMALY 事件 → 升级到 Owner"

  context_window_fragmentation:
    description: "多个 Skill 分散在上下文的不同位置——Agent 的注意力被稀释"
    problem: "第 3 个 Skill 加载后，第 1 个 Skill 的指令实际上已被 Agent 遗忘"
    solution: "Skill Compact——多 Skill 加载时自动合并为单一指令块并前置插入"
    compact_rules:
      - "所有 CRITICAL 规则合并到最前面（5 条以内）"
      - "重复指令去重（两个 Skill 都要求 '跑 pytest' → 只保留一次）"
      - "冲突指令按 Domain > Role 优先级消除"
      - "合并后的总 token ≤ 1200（超出则降级——只保留每个 Skill 的 3 条核心指令）"

  attention_weighting:
    description: "在合并后的 Skill Block 中对不同指令赋予不同的'注意力权重'标记"
    weights:
      CRITICAL_IRON_RULE: "weight=100——绝不可违反，Agent 必须放在推理链的最优先位置"
      CHECKLIST_STEP: "weight=50——必须按顺序执行"
      DOMAIN_REMINDER: "weight=30——领域模式提示，执行到相关部分时回顾"
      REFERENCE_HINT: "weight=10——提示有 L3 深度资料可供进一步参考"
    implementation: "Weight 标注在指令前缀中（如 [W:100/CRITICAL] [W:50/CHECKLIST]）"
```

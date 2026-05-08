---
module_id: KE-module_blu-2_8-003
title: 2.8 委托上下文包 —— 结构化状态传递
category: module_blueprint
---

# 2.8 委托上下文包 —— 结构化状态传递

2.8 委托上下文包 —— 结构化状态传递

> **对标**：GOV-AI-008 Handoff Protocol 的 8 必填字段 + Rasa warm transfer（含完整对话摘要）。

```yaml
delegation_context_package:
  # 每次委托时附带的上下文包——7 个必填字段
  required_fields:
    - field: "delegation_id"
      type: "string"
      description: "委托唯一标识——格式 DEL-{TIMESTAMP}-{SEQ}"

    - field: "source_agent"
      type: "string"
      description: "发起委托的 Agent 身份（Skill Pack + session_id）"

    - field: "task_summary"
      type: "string (≤ 300 chars)"
      description: "委托任务的自然语言摘要——要做什么、为什么做"

    - field: "current_state"
      type: "dict"
      description: "当前已完成的步骤 + 已产生的产出物路径 + 当前阻塞点"

    - field: "attempted_approaches"
      type: "list[str]"
      description: "已尝试过的方案及失败原因（避免重复踩坑）"

    - field: "constraints"
      type: "dict"
      description: "硬约束（不能改什么、预算还剩多少、截止时间）"

    - field: "expected_output"
      type: "string"
      description: "期望的产出物格式与内容——目标Agent知道交付什么"

  # === 上下文压缩策略 ===
  context_compression:
    when: "父Agent token预算已消耗 > 80%"
    strategy: "先写完整上下文包 → 再用 LLM 压缩为 ≤ 500 tokens 摘要"
    fallback: "压缩失败 → 传完整包但标记 [BUDGET_CRITICAL]"

  # === 上下文包的存储与传递 ===
  storage: "docs/09_audit/DELEGATION/{delegation_id}.yaml"
  format: "YAML（与 GOV-AI-008 HandoffPackage 格式兼容）"
  audit: "每次委托上下文包写入 Audit Trail (MOD-INF-020)"
```

---

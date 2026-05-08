---
module_id: KE-module_blu-2_23_context_poisoning_cascade-000
title: 2.23 Context Poisoning Cascade 检测
category: module_blueprint
---

# 2.23 Context Poisoning Cascade 检测

2.23 Context Poisoning Cascade 检测

> **决策 D-024-21（🆕 v0.6.0）**：SUPERVISORAGENT (ICLR 2026) 的核心贡献——MAS 中一个 agent 的幻觉输出被下游 agent 当作事实，会产生指数级成本放大。单点的 bad observation 可以导致整个 pipeline 的 token 消耗翻倍。

```yaml
poisoning_cascade_detector:
  description: "检测上游 agent 的错误输出被下游 agent 继承放大的级联效应"
  # 典型场景：Agent-A 说 'config/file.yaml 不存在'（幻觉）→ Agent-B 开始造那个文件（浪费）
  #           → Agent-C 开始引用那个假文件 → 成本指数放大

  detection_layers:
    fact_contradiction:
      description: "Agent 输出声称的事实与系统已知状态矛盾"
      method: "cross-reference agent output claims vs workspace index / file system state"
      example: "Agent says 'module X has rate limit 100' but config says 50"
      action: "MARK as potentially_poisoned + 注入 warning 到下游 agent 的 system prompt"

    chain_of_faith:
      description: "追踪信息源链——如果 Agent-C 引用 Agent-B 引用 Agent-A 且 Agent-A 被纠正过"
      method: "构建 observation provenance DAG"
      ttl: "3600s（1h 内同一不实引用链触发级联熔断）"

    cascade_cost_tracker:
      description: "量化下中游因上游错误而浪费的 token"
      metric: "tokens_spent_on_fixing_poisoned_context / total_tokens"
      alert: "cascade_cost > 15% total → WARN '上下文中毒成本过高——建议重启 Session'"

  auto_isolation:
    description: "检测到级联时自动隔离可疑 agent 的中间输出"
    action: "清除被标记为 potentially_poisoned 的上下文片段 + 重新生成"
```

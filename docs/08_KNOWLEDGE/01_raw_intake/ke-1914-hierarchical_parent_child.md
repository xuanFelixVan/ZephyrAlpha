---
module_id: KE-1823
status: active
title: 2.24 Hierarchical Parent-Child Agent 成本归因
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.24 Hierarchical Parent-Child Agent 成本归因

2.24 Hierarchical Parent-Child Agent 成本归因

> **决策 D-024-22（🆕 v0.6.0）**：现代 MAS 中一个 coordinator 可能委托多个 child agents。扁平 entity-level 归因无法展示"哪个 coordinator 的委托模式最贵"。

```yaml
parent_child_attribution:
  description: "追踪 agent 委托链的树状成本结构——parent 承担 child 的成本但有 governance 杠杆"

  delegation_tree:
    description: "每个 agent call 记录 parent_agent_id 和 cause_agent_id"
    structure: "DAG（同一 child 可被多个 parent 委托）"

  attribution_rules:
    direct_cost: "agent 自己的 LLM API 消耗 → 归于自己"
    delegated_cost: "child agent 的消耗 → 按 delegation_ratio 回溯到各 parent"
    root_cause_cost: "如果 child 因 parent 的错误指令增加了成本 → 超额部分归于 parent"

  query_examples:
    top_delegator: "coordinator-A 直接消耗 $3 + 委托链总成本 $12 → 真实影响 $15"
    delegation_efficiency: "child 产出 / parent 委托成本 → 低效委托被标记"

  visual: "终端显示 '🌳 coordinator-A: $3(self) + $12(delegated) = $15 total | 委托比 4:1'"
```

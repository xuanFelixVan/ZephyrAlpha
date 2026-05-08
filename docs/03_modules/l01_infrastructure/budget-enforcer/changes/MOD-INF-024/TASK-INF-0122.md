---
task_id: "TASK-INF-0122"
module_id: "MOD-INF-024"
title: "Context Poisoning Cascade Detector — 幻觉上游输出污染下游 Agents + Provenance DAG + Auto-Isolation（§2.23 + D-024-21）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P1
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: experimental
blueprint_section: "§2.23"
estimated_tokens: 4000
estimated_time_minutes: 120
owner_signal_required: false
depends_on:
  - "TASK-INF-0101"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\poison_cascade_detector.py"
acceptance_criteria:
  - "AC-01: fact_contradiction——Agent 输出声称的事实 vs 系统已知状态 cross-reference（workspace index / filesystem state）"
  - "AC-02: contradiction 检测到 → MARK as potentially_poisoned + 注入 warning 到下游 agent system prompt"
  - "AC-03: chain_of_faith——observation provenance DAG：若 Agent-C 引用 Agent-B 引用 Agent-A 且 Agent-A 被纠正过"
  - "AC-04: provenance DAG TTL=3600s——1h 内同一不实引用链触发级联熔断"
  - "AC-05: cascade_cost_tracker——量化下游因上游错误浪费的 token = tokens_spent_on_fixing_poisoned / total_tokens"
  - "AC-06: cascade_cost > 15% total → WARN '上下文中毒成本过高——建议重启 Session'"
  - "AC-07: auto_isolation——检测到级联时自动清除 marked as potentially_poisoned 的上下文片段 + 重新生成"
  - "AC-08: provenance DAG overhead——仅保留 contradiction 节点（非全部节点），TTL 1h"
  - "AC-09: 跨模块联动——当检测到级联时通知 MOD-INF-022 Escalation + 写入 MOD-INF-020 Audit Trail"
rollback_instructions: "删除 poison_cascade_detector.py + provenance DAG 数据。系统退化为无级联检测——依赖其他 guards（burn rate 总量异常 / spiral EWS）发现间接症状"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L1094-L1123 (§2.23 Poison Cascade)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
assigned_agent: any
tags: [poison-cascade, hallucination, provenance-dag, auto-isolation, supervisoragent, experimental]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0122: Context Poisoning Cascade Detector

## 1. 任务目标

实现上下文中毒级联检测——SUPERVISORAGENT (ICLR 2026) 的核心贡献。在 Multi-Agent System (MAS) 中，单点 agent 的幻觉输出被下游 agent 当作事实，产生指数级成本放大。检测三层：fact_contradiction、chain_of_faith、cascade_cost_tracker。

## 2. 背景

蓝图 §2.23（决策 D-024-21，v0.6.0 新增）：Agent-A 说 'config/file.yaml 不存在'（幻觉）→ Agent-B 造假文件 → Agent-C 引用假文件 → 成本指数级放大。

## 3. 实施步骤

```python
class PoisonCascadeDetector:
    def __init__(self, workspace_index, delegation_registry):
        self.contradiction_checker = FactContradictionChecker(workspace_index)
        self.provenance_dag = ProvenanceDAG(ttl=3600)
        self.cost_tracker = CascadeCostTracker()

    def check_agent_output(self, agent_id: str, output: dict,
                          source_chain: list[str]) -> CascadeResult:
        # Step 1: check fact contradictions
        contradictions = self.contradiction_checker.find(output)
        # Step 2: update provenance DAG
        if contradictions:
            self.provenance_dag.add_contradiction_edge(source_chain[-1], agent_id)
            output["_meta"] = {"poison_risk": "high", "contradictions": contradictions}
        # Step 3: check chain_of_faith
        if self.provenance_dag.is_corrupted(source_chain):
            return CascadeResult(action="ISOLATE", reason="provenance chain corrupted")
        return CascadeResult(action="ALLOW")

class ProvenanceDAG:
    # Simple DAG: agent_id → claims → contradictions
    # TTL 3600s per edge
    # Pruning: only keep contradiction edges
```

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/poison_cascade_detector.py` | 新建 |

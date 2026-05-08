---
task_id: "TASK-INF-0123"
module_id: "MOD-INF-024"
title: "Parent-Child Agent Cost Attribution — 委托树 DAG + 成本归因到最上游 Agent + Delegation Optimizer（§2.24 + D-024-22）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P1
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: experimental
blueprint_section: "§2.24"
estimated_tokens: 4500
estimated_time_minutes: 120
owner_signal_required: false
depends_on:
  - "TASK-INF-0101"
  - "TASK-INF-0102"
  - "TASK-INF-0108"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\budget_tracker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\cost_attributor.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\parent_child_attributor.py"
acceptance_criteria:
  - "AC-01: ParentChildAttributor 委托树 DAG——节点=Agent，边=delegation invocation，成本属性全累计"
  - "AC-02: cost_roll_up——子 Agent 总消耗向上汇总到委托发起 Agent 的 task_budget 核销"
  - "AC-03: delegation_chain_name——自动生成标签 'DocGen(Code) → Formatter → Validator → Linter'"
  - "AC-04: delegation_depth_alert——depth > 3 → WARN '委托链过深——建议合并任务'"
  - "AC-05: cost_per_child——每级 child 独立 cost 可视化（在 burn rate dashboard 中区分展示）"
  - "AC-06: orphan_detection——子 Agent still_running=true 但 parent Agent 已 terminate → WARN + force terminate child"
  - "AC-07: delegation_optimizer——memo 化（同一 Agent+相同输入→复用 output）+ 合并相似 call"
  - "AC-08: 委托优化建议——semantic similarity > 0.8 的子任务建议合并为 batch"
  - "AC-09: delegation DAG 写入 audit trail——含 delegation_id, parent, child, purpose, cost_rollup"
rollback_instructions: "删除 parent_child_attributor.py。cost_attributor 的 entity 归因退化为扁平归因（无委托链聚合），Delegation Optimizer 的 memo/合并功能移除"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L1126-L1160 (§2.24 Parent-Child Attribution)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\cost_attributor.py"
assigned_agent: any
tags: [parent-child, delegation-dag, cost-rollup, agentdelegation, delegation-optimizer, experimental]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0123: Parent-Child Agent Cost Attribution

## 1. 任务目标

实现父子 Agent 成本归因——在 Multi-Agent 系统中，子 Agent 的 token 消耗应归因到委托发起方。构建 delegation DAG 追踪完整委托链，支持成本回滚、孤儿检测和委托优化（memo/合并）。

## 2. 背景

蓝图 §2.24（决策 D-024-22，v0.6.0 新增）：现存 Cost Attribution 缺少委托链视角——该链子上子 agent 的 cost 应该回滚到发起方 agent。

## 3. 实施步骤

```python
class ParentChildAttributor:
    def __init__(self):
        self.dag = DelegationDAG()
        self.depth_checker = DepthChecker(max_depth=3)
        self.orphan_detector = OrphanDetector()
        self.optimizer = DelegationOptimizer()

    def register_delegation(self, parent: str, child: str,
                            task_purpose: str, estimated_tokens: int):
        delegation_id = self.dag.add_edge(parent, child, task_purpose, estimated_tokens)

    def roll_up_cost(self, child_agent: str,
                     cost_attributor: CostAttributor) -> dict[str, float]:
        # 从 child 开始沿 DAG 向上回滚 cost
        ancestor_chain = self.dag.get_ancestor_chain(child_agent)
        ...

    def check_delegation_health(self) -> list[Alert]:
        depth_alerts = self.depth_checker.check(self.dag)
        orphan_alerts = self.orphan_detector.check(self.dag)
        return depth_alerts + orphan_alerts
```

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/parent_child_attributor.py` | 新建 |

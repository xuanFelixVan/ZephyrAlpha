---
task_id: "TASK-INF-0125"
module_id: "MOD-INF-024"
title: "Runtime Trust Rings — Ring 0-3 隔离预算池 + 跨环升级仲裁（§2.26 + D-024-24）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P1
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: v0_7_0
blueprint_section: "§2.26"
estimated_tokens: 4500
estimated_time_minutes: 150
owner_signal_required: false
depends_on:
  - "TASK-INF-0101"
  - "TASK-INF-0102"
  - "TASK-INF-0105"
  - "TASK-INF-0128"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\budget_tracker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\degradation_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\fail_mode_manager.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\trust_ring_manager.py"
acceptance_criteria:
  - "AC-01: Ring 0 — Readonly Snapshot (disk stats, git log, file metadata, workspace index)— 100% read-only"
  - "AC-02: Ring 1 — Safe Execution (code analysis, linting, formatting, testing)— outputs within task/.tmp/"
  - "AC-03: Ring 2 — Controlled Mutation (git operations, file writes to src/ only, SLM local model, MOD-INF-023 Cross-referencing)— ring-specific budget pool 50% of global"
  - "AC-04: Ring 3 — External Gate (OAuth, API key, CI trigger, agent delegation, Tier-3 pricing model)— owner two-factor confirmation"
  - "AC-05: ring_budget_pools——四个隔离预算池，按 ring 风险等级定比分配：Ring 0(10%), Ring 1(35%), Ring 2(35%), Ring 3(20%)"
  - "AC-06: cross_ring_action——低 Ring action required 高 Ring key → ring-handoff 事件需要 Owner = Allow once/Allow pattern/Deny"
  - "AC-07: agenthive_compat_layer——与 MOD-INF-021 AgentHive Ring 0-3 兼容层"
  - "AC-08: 环间升级写入 audit trail——含 from_ring, to_ring, action, justification, owner_decision"
  - "AC-09: 环感知上下文窗口——高 Ring 调用附加 ring_label, escalation_chain"
  - "AC-10: ring-inherent 模式——Runtime, not exploit-derived（不是通过 API 调用次数推断）"
rollback_instructions: "删除 trust_ring_manager.py + ring_budget_pools。系统退化为扁平预算无环隔离——所有 action 走同一预算池"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L1201-L1248 (§2.26 Trust Rings)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
assigned_agent: any
tags: [trust-rings, ring-isolation, ring-budget, cross-ring, agenthive-compat, v0.7.0]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0125: Runtime Trust Rings — Ring 0-3 隔离预算池

## 1. 任务目标

实现运行时信任环——将 Agent 操作按风险分级（Ring 0=只读快照 → Ring 3=外部API/OAuth），每个 Ring 拥有隔离的预算池。跨环升级操作需要 Owner 仲裁。对标 Operating System ring protection model — 你的 AI 系统需要相同的风险隔离。

## 2. 背景

蓝图 §2.26（决策 D-024-24，v0.7.0 新增）：OpenAI CodeCLI 环形授权直接参考。v0.7.0 通过阶段。

## 3. 实施步骤

```python
class TrustRing(Enum):
    RING_0_READONLY = 0    # disk stats, git log, file metadata
    RING_1_SAFE_EXEC = 1   # code analysis, linting, formatting, testing
    RING_2_CONTROLLED_MUT = 2  # git ops, file writes, SLM
    RING_3_EXTERNAL_GATE = 3   # OAuth, API keys, agent delegation

class TrustRingManager:
    def __init__(self, tracker: BudgetTracker,
                 budget_pools: dict[TrustRing, BudgetPool]):
        self.budget_pools = budget_pools

    def classify_action(self, action: ActionSignature) -> TrustRing:
        # dispatcher: action.tool_name → TrustRing mapping

    def check_ring_budget(self, ring: TrustRing, estimated: int) -> bool:
        pool = self.budget_pools[ring]
        return pool.remaining() >= estimated

    def handle_cross_ring(self, from_ring: TrustRing,
                          to_ring: TrustRing, reason: str) -> CrossRingDecision:
        # 低→高 Ring 升级需要 Owner 确认
        if from_ring.value < to_ring.value:
            return CrossRingDecision.REQUIRES_OWNER
        return CrossRingDecision.AUTO_ALLOW
```

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/trust_ring_manager.py` | 新建 |

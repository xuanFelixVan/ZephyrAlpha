---
task_id: "TASK-INF-0116"
module_id: "MOD-INF-024"
title: "Context Waste Detector + Cold Start Allowance + Local Model Cost Model — 三个辅助能力（§2.17 + D-024-15）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P2
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: beta
blueprint_section: "§2.17"
estimated_tokens: 4500
estimated_time_minutes: 120
owner_signal_required: false
depends_on:
  - "TASK-INF-0101"
  - "TASK-INF-0102"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\budget_tracker.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\context_waste_detector.py"
acceptance_criteria:
  - "AC-01: ContextWasteDetector 追踪每次 LLM 调用后 sent vs referenced 上下文比例——metric = referenced_chars / total_context_chars"
  - "AC-02: waste_ratio > 0.60 持续 5 个请求 → 建议 /compact 或精简 AGENTS.md"
  - "AC-03: 集成 Context Engine (MOD-INF-008) DocCompressor——根据 waste 数据优化上下文选择策略"
  - "AC-04: ColdStartAllowance 固定入场费 5500 tokens——读取 AGENTS.md(3000) + workspace index(2000) + budget_policy(500)"
  - "AC-05: cold_start_tokens 计入 session 级预算但不计入任何 task_budget——overridable=true"
  - "AC-06: LocalModelCostModel——基于 electricity/gpu_power/tokens_per_second 计算本地模型等效成本"
  - "AC-07: electricity=$0.12/kWh, gpu_power=200W, tokens_per_second=50 → cost ≈ $0.13/MTok"
  - "AC-08: local tokens 在 showback 中分开展示为 'local_cost' 非 'api_cost'——model_assignment='tier_local'"
  - "AC-09: 终端显示 cold_start 豁免状态（未用/部分用/已用完/超出限制等）"
rollback_instructions: "删除 context_waste_detector.py。context waste 检测退化为手动模式, cold_start allowance 退化为无豁免, local model cost 退化为不计入"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L894-L927 (§2.17 Auxiliary capabilities)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
assigned_agent: any
tags: [waste-detector, cold-start, local-model, auxiliary, beta]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0116: Context Waste Detector + Cold Start Allowance + Local Model Cost Model

## 1. 任务目标

实现三个辅助能力——互补上下文浪费检测（塞进上下文的材料有多少 LLM 实际没看）、Session 冷启动固定成本豁免、本地模型（Ollama）的电费成本模型。

## 2. 背景

蓝图 §2.17（决策 D-024-15，v0.4.0 新增）：三个被前几轮忽略的隐性成本源——在 solo maintainer 长期积累下不可忽略。上下文浪费检测与 Conversation History Tax Detector (§2.19) 互补，冷启动豁免在 v0.7.0 需要 Cold Start Anti-Abuse 保护。

## 3. 实施步骤

### Step 1: ContextWasteDetector
```python
class ContextWasteDetector:
    def analyze(self, context_sent: dict[str, str],
                llm_response: str) -> WasteReport:
        # 在 response 中搜索引用到的上下文片段
        referenced = self._find_referenced_fragments(context_sent, llm_response)
        waste_ratio = 1 - (len(referenced) / sum(len(v) for v in context_sent.values()))
        return WasteReport(waste_ratio, referenced, self._suggest_action(waste_ratio))
```

### Step 2: ColdStartAllowance
```python
class ColdStartAllowance:
    FIXED_COST = {
        "ag_md_read": 3000,
        "workspace_index": 2000,
        "budget_policy_load": 500,
    }
    TOTAL = 5500

    def apply(self, tracker: BudgetTracker):
        tracker.consume(BudgetLevel.SESSION, tokens=self.TOTAL, cost=0, time_s=0)
        # 但不 consume task-level budgets
```

### Step 3: LocalModelCostModel
```python
class LocalModelCostModel:
    def estimate(self, total_tokens: int, tps: float = 50) -> float:
        time_s = total_tokens / tps
        energy_kwh = (200 / 1000) * (time_s / 3600)  # GPU power 200W
        cost = energy_kwh * 0.12
        return cost
```

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/context_waste_detector.py` | 新建 |

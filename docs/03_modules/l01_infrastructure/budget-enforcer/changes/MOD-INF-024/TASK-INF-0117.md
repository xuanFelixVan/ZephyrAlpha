---
task_id: "TASK-INF-0117"
module_id: "MOD-INF-024"
title: "Instruction Bloat Detector — AGENTS.md/blueprint 指令膨胀检测 + 精简建议（§2.18 + D-024-16）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P1
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: beta
blueprint_section: "§2.18"
estimated_tokens: 3500
estimated_time_minutes: 90
owner_signal_required: false
depends_on:
  - "TASK-INF-0101"
  - "TASK-INF-0102"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\budget_tracker.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\instruction_bloat_detector.py"
acceptance_criteria:
  - "AC-01: 检测目标三文件：AGENTS.md, budget_policy.yaml, 所有 blueprint.md §1-§2"
  - "AC-02: 三个指标：instruction_token_count, instruction_growth_rate_weekly(> 20% WARN), per_turn_instruction_overhead"
  - "AC-03: instruction_oversized——token_count > session_budget × 0.25 → WARN"
  - "AC-04: instruction_growing——weekly growth > 20% → WARN '指令文件正在膨胀——建议精简冗余规则'"
  - "AC-05: instruction_dominance——per_turn_overhead > productive_tokens → '指令比产出还多'"
  - "AC-06: auto_compact=enabled=false——不自动压缩，生成精简建议 list（哪个段落 30d 未被遵守 → 建议删除）"
  - "AC-07: suggest精简建议走 Self-Budget（LLM-dependent check 用 tier_0_free）"
  - "AC-08: 终端显示 '📋 指令: 3.2K (占预算 8%) | 本周增长 +5%'"
  - "AC-09: 集成 Context Engine——instruction_growth > 20% 时联动 DocCompressor 调整压缩策略"
rollback_instructions: "删除 instruction_bloat_detector.py。系统退化为无指令膨胀监控——AGENTS.md 膨胀由 Boris Cherny 的 14% 基准反证发现"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L930-L953 (§2.18 Instruction Bloat)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
assigned_agent: any
tags: [instruction-bloat, agents-md, token-waste, cherny-benchmark, beta]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0117: Instruction Bloat Detector — 指令膨胀检测

## 1. 任务目标

实现指令文件膨胀检测器——专门追踪 AGENTS.md/CLAUDE.md/budget_policy.yaml/blueprint 等指令文件的 token 膨胀。这些文件每个 turn 都被发送，膨胀的边际成本极大。Boris Cherny 数据：14% token 浪费来自指令膨胀。

## 2. 背景

蓝图 §2.18（决策 D-024-16，v0.5.0 新增）：Context Waste Detector 追踪 "sent vs referenced" 但指令文件被动发送永不被引用，需独立检测器。对标 Boris Cherny 400h Claude 使用分析。

## 3. 实施步骤

```python
class InstructionBloatDetector:
    TARGETS = ["AGENTS.md", "budget_policy.yaml"]

    def __init__(self, tracker: BudgetTracker, policy: dict):
        self.tracker = tracker
        self._weekly_history: list[int] = []

    def check(self, targets: dict[str, str]) -> BloatReport:
        # 计算各目标的 token count
        # 对比上周 → growth rate
        # 对比 session_budget → oversize
        # 对比 productive_tokens → dominance

    def suggest_trim(self, targets: dict[str, str]) -> list[str]:
        # LLM-dependent: 分析各段落过去 30d 的使用频率
        # 返回 "建议删除" 的段落列表
```

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/instruction_bloat_detector.py` | 新建 |

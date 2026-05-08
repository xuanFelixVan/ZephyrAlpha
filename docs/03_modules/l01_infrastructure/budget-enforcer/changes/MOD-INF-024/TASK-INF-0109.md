---
task_id: "TASK-INF-0109"
module_id: "MOD-INF-024"
title: "ROI Calculator — Token 价值归因 + 四维产出指标 + 趋势告警（§2.8）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P1
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: beta
blueprint_section: "§2.8"
estimated_tokens: 3000
estimated_time_minutes: 90
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
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\roi_calculator.py"
acceptance_criteria:
  - "AC-01: ROICalculator 四个产出指标：lines_of_code_per_1k_tokens, files_completed_per_1k_tokens, blueprint_sections_per_1k_tokens, debug_rounds_per_task"
  - "AC-02: Week 1 建立基线——baseline = None，Week 2 起所有指标与 baseline 对比"
  - "AC-03: roi_drop_30_percent → 告警 Owner '施工效率下降，建议检查 Prompt 质量'"
  - "AC-04: debug_rounds_per_task 上升趋势单独告警——'首次生成质量下降'"
  - "AC-05: ROI 数据与 Session Log（docs/09_audit/session_logs/）联动——自动从 session log 提取产出文件列表和代码行数"
  - "AC-06: 提供 compare(period1, period2) → ROIDelta——两个时段的效率变化对比"
  - "AC-07: 模型级 ROI 拆解——per-model ROI 对比表（哪个模型 cohort 效率最高）"
  - "AC-08: ROI 数据写入 Weekly Showback——归入摘要 'ROI: 效率变化趋势' 段"
rollback_instructions: "删除 roi_calculator.py，移除 Weekly Showback 中的 ROI 段引用。系统退化为纯成本追踪无效率评估模式"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L530-L553 (§2.8 Token ROI)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\cost_attributor.py"
assigned_agent: any
tags: [roi-calculator, token-efficiency, output-metrics, trend-alert, beta]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0109: ROI Calculator — Token 价值归因

## 1. 任务目标

实现 Token ROI 计算器——不只算"花了多少 token"，算"这些 token 产出了什么"。FinOps for AI 的核心：把 Token 消耗与可量化产出（代码行数、文件数、蓝图章节数、debug 轮次）关联，每周追踪效率趋势。

## 2. 背景

蓝图 §2.8：四个产出指标 + 基线建立 + 趋势告警。v0.6.0 通过 Parent-Child Attribution 和 Guard Efficiency Ratio 扩展 ROI 的多维度对比。

## 3. 实施步骤

### Step 1: 类型定义
```python
@dataclass
class ROIResult:
    period: tuple[float, float]
    tokens_spent: int
    lines_of_code: int
    files_completed: int
    blueprint_sections: int
    debug_rounds: int

    @property
    def loc_per_1k(self) -> float:
        return self.lines_of_code / (self.tokens_spent / 1000)

    @property
    def files_per_1k(self) -> float:
        return self.files_completed / (self.tokens_spent / 1000)
```

### Step 2: ROICalculator 核心
```python
class ROICalculator:
    def __init__(self, session_log_dir: str):
        self.baseline: ROIResult | None = None

    def calculate(self, period: tuple, tracker: BudgetTracker,
                  session_logs: list[dict]) -> ROIResult:

    def set_baseline(self, result: ROIResult):

    def check_trend(self, current: ROIResult) -> list[Alert]:
        # 对比 baseline——任一指标下降 > 30% → alert
```

### Step 3: Per-Model ROI
- 按 model_id 分组统计 ROI
- 生成 ROI 对比矩阵：model × metric = efficiency score

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/roi_calculator.py` | 新建 |

---
task_id: "TASK-INF-0108"
module_id: "MOD-INF-024"
title: "Cost Attributor — 四维归因（Entity/Tool/Feature/Outcome）+ Judge 独立核算 + Data Retention + Weekly Showback（§2.7 + D-024-08）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P1
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: beta
blueprint_section: "§2.7"
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
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\cost_attributor.py"
  - "D:\\ZephyrAlpha\\data\\audit\\cost-attribution.jsonl"
acceptance_criteria:
  - "AC-01: CostAttributor 四个核心维度独立可查询：entity_level(agent_id/module_id/phase), tool_level(tool_name/tool_call_count/api_cost/passthrough), feature_level(activity_type/files/loc), outcome_level(outcome/retry_count/error_category)"
  - "AC-02: tool_level 包含 passthrough_cost——Web Search/Code Exec/DB Query 等第三方服务自身费用独立追踪"
  - "AC-03: outcome_level 按 success/partial/failed/rejected 四类分离，支持查询 'outcome=failed 本月消耗 $X (占比%)'"
  - "AC-04: judge_cost 独立核算——不计入 Task 预算，走 Judge 专用预算池；Judge 成本 > 总成本 15% → 告警"
  - "AC-05: showback——WeeklyAutoSummary 生成八段 Markdown 报告：总览/异常/归因 Top3/ROI趋势/预测/建议/新模型"
  - "AC-06: 成本归因写入 JSONL——data/audit/cost-attribution.jsonl（按天切分）"
  - "AC-07: data_retention 策略完整：raw_data 30d JSONL, aggregated 12mo SQLite weekly, archival 年度 gzip JSON"
  - "AC-08: 每周日 03:00 UTC 自动执行过期策略——cleanup 方法可测试"
  - "AC-09: 支持 query(filter) 接口——返回 AttributionReport dataclass（含 breakdown 和 visualization-ready dict）"
  - "AC-10: 归因数据写入 audit trail——所有归因事件与 audit trail 联动"
rollback_instructions: "删除 cost_attributor.py，清理 data/audit/cost-attribution.jsonl 中的数据。系统退化为无归因模式——超预算事件仍被记录但无法查询 '钱花在哪'"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L458-L527 (§2.7 Cost Attribution)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
assigned_agent: any
tags: [cost-attribution, showback, outcome-segmentation, judge-cost, data-retention, beta]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0108: Cost Attributor — 四维成本归因 + Judge 独立核算 + 数据生命周期

## 1. 任务目标

实现四级成本归因系统——不只追踪"花了多少 token"，还回答"花在哪、花得值不值"。四维度归因（Entity/Tool/Feature/Outcome）+ LLM-as-Judge 独立核算 + 数据生命周期管理 + 每周自动摘要。

## 2. 背景

蓝图 §2.7（决策 D-024-08，v0.4.0 修订）：FinOps for AI chargeback 的核心——失败消耗和成功消耗的 ROI 完全不同。v0.4.0 新增 Outcome 维度（成功/失败/部分分离）+ LLM-as-Judge 独立核算 + 数据生命周期。v0.6.0 通过 Parent-Child Attributor 扩展归因到委托链级别。

## 3. 实施步骤

### Step 1: 类型定义
```python
@dataclass
class AttributionRecord:
    timestamp: float
    entity: EntityLevel      # agent_id, module_id, phase
    tool: ToolLevel           # tool_name, counts, costs, passthrough
    feature: FeatureLevel     # activity_type, files, loc
    outcome: OutcomeLevel     # outcome, retry_count, error_category
    tokens: int
    cost: float
    is_judge: bool = False

@dataclass
class AttributionReport:
    period: tuple[float, float]
    total_tokens: int
    total_cost: float
    breakdown_by: dict[str, dict]  # 按维度 = 子报告
    top_consumers: list[tuple[str, float]]  # (name, cost) Top N
```

### Step 2: CostAttributor 核心
```python
class CostAttributor:
    def __init__(self, output_dir: str, retention_config: dict):
        self.writer = JSONLWriter(f"{output_dir}/cost-attribution.jsonl")
        self.aggregator = WeeklyAggregator()
        self.retention = RetentionManager(retention_config)

    def record(self, record: AttributionRecord):
        self.writer.append(record)
        self.aggregator.update(record)

    def query(self, dimension: str, filters: dict) -> AttributionReport:
        # dimension: "entity" | "tool" | "feature" | "outcome"
        # filters: {period, agent_id, tool_name, outcome, ...}

    def generate_showback(self, period: str) -> str:
        # 生成八段 Markdown 摘要
```

### Step 3: Judge Cost Tracking
- `is_judge` flag 标记 LLM-as-Judge 调用
- 独立 accumulator——不计入 task budget
- ratio check——judge_cost / total_cost > 0.15 → alert

### Step 4: Data Retention
- raw_data: 30 天 JSONL 文件轮换（按日期后缀）
- aggregated: SQLite DB 按周聚合，12 个月保留
- archival: 年度 gzip 归档
- cleanup: APScheduler 每周日 03:00 UTC 执行

### Step 5: Weekly Showback 格式
输出到 `docs/09_audit/cost_reports/weekly-{date}.md`，包含：总览/异常/归因 Top3/ROI趋势/预测/建议/新模型

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/cost_attributor.py` | 新建 |

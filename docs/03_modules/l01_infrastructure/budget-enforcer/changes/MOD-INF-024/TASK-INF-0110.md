---
task_id: "TASK-INF-0110"
module_id: "MOD-INF-024"
title: "Burn Rate Monitor — 四窗口监控 + Distribution Shift + Rate Limit Impact + Provider Tier Awareness（§2.9 + D-024-09）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P1
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: beta
blueprint_section: "§2.9"
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
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\burn_rate_monitor.py"
acceptance_criteria:
  - "AC-01: 四窗口 burn rate 追踪：window_10min(> 10× normal → L3), window_1h(> 5× → L2), window_6h(> 3× → L1), window_24h(> 2× → daily summary)"
  - "AC-02: baseline = 7d_moving_average（过去 7 天同时段平均消耗速率）"
  - "AC-03: alert_cooldown=300s——同一 burn rate 告警 5 分钟内不重复"
  - "AC-04: Distribution Shift 检测——四维度（by_model/by_tool/by_agent/by_outcome）Jensen-Shannon divergence vs 7d baseline"
  - "AC-05: JS divergence > 0.3 → INFO 日志 '检测到消耗结构偏移——[dimension] 异常增长'"
  - "AC-06: Rate Limit Impact 追踪——rate_limit_hit_count, retry_tokens_wasted, retry_cost_wasted"
  - "AC-07: 限流浪费 > $1.00/天 → 建议调整并发数或升级 Tier"
  - "AC-08: Provider Tier Awareness——Anthropic 4-Tier RPM/TPM 实时追踪，RPM 剩余 < 20% 自动切换备用 Provider"
  - "AC-09: Anthropic Tier 数据 accurate：tier_1(50rpm/100k tpm), tier_2(500rpm/500k tpm), tier_3(2k rpm/2M tpm), tier_4(5k rpm/5M tpm)"
  - "AC-10: BurnRateSnapshot 支持 JSON 序列化——供 Burn Rate Dashboard 消费"
  - "AC-11: 提供 predict_next_window(window) → 基于 EMA 趋势外推下一窗口消耗预测"
rollback_instructions: "删除 burn_rate_monitor.py，移除调用点。系统退化为无速率监控模式——超预算仍通过 Pre-flight Gate 触发，但无早期速率异常检测"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L554-L620 (§2.9 Burn Rate Monitor)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
assigned_agent: any
tags: [burn-rate, distribution-shift, rate-limit, provider-tier, google-sre, beta]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0110: Burn Rate Monitor — 四窗口速率监控 + 结构偏移检测

## 1. 任务目标

实现 Google SRE 风格的多窗口 Burn Rate 监控——不是追踪"用了多少"而是"在以多快的速度消耗"。四时间窗口（10分钟/1小时/6小时/24小时）配合逐级降级。v0.4.0 新增 Distribution Shift 结构异常检测和 Rate Limit 浪费追踪。

## 2. 背景

蓝图 §2.9（决策 D-024-09）：七天内同时段平均为基线，超过倍数触发对应级别降级。结构异常（某模型/工具/Agent 消耗比例突变）往往先于总量异常出现。

## 3. 实施步骤

### Step 1: 类型定义
```python
@dataclass
class BurnRateSnapshot:
    window: str  # "10min" | "1h" | "6h" | "24h"
    current_rate: float   # tokens per minute
    baseline_rate: float
    ratio: float          # current / baseline
    threshold: float
    status: str  # "normal" | "elevated" | "critical"
    by_dimension: dict[str, float]  # 按 model/tool/agent/outcome 分拆
```

### Step 2: BurnRateMonitor 核心
```python
class BurnRateMonitor:
    def __init__(self, tracker: BudgetTracker):
        self.baseline = SevenDayBaseline()
        self._cooldowns: dict[str, float] = {}

    def tick(self) -> list[BurnRateSnapshot]:
        # 计算四个窗口的 burn rate
        # 对比 baseline 判断是否触发告警

    def check_distribution_shift(self) -> DistributionShiftReport:
        # JS divergence × 4 dimensions
```

### Step 3: DistributionShift 检测
- 收集 4 个维度的当前分布 vs baseline 分布
- 计算 Jensen-Shannon divergence
- JS > 0.3 → flagged dimension + suggestion

### Step 4: RateLimitImpact
- 拦截 429/rate_limit 响应
- 累计 retry_tokens_wasted 和 cost
- 日累计 > $1.00 → alert

### Step 5: ProviderTierTracking
- 跟踪各 Provider 的 RPM/TPM
- 预测即将超限的时间点
- < 20% capacity → preemptive switch

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/burn_rate_monitor.py` | 新建 |

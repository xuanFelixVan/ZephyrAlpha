---
task_id: "TASK-INF-0104"
module_id: "MOD-INF-024"
title: "Model Router — Tier Escalation + Multi-Provider Least-Cost + Batch + Provider Tier Awareness + Vendor Fallback（§2.3 + D-024-04）"
doc_type: task_card
status: Backlog
version: "0.1.0"
priority: P0
created_by: "agent_decomposer"
created_date: "2026-05-06"
task_type: implementation
phase: experimental
blueprint_section: "§2.3"
estimated_tokens: 5000
estimated_time_minutes: 150
owner_signal_required: false
depends_on:
  - "TASK-INF-0101"
  - "TASK-INF-0102"
  - "TASK-INF-0111"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\budget_tracker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\pricing_sync.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\model_router.py"
acceptance_criteria:
  - "AC-01: ModelRouter 默认策略 cheapest_first_escalate_on_quality_fail——任务进入默认 tier_0_free"
  - "AC-02: escalation_chain 四段升级路径完整：tier_0→tier_1 (max_escalation_cost $0.01), tier_1→tier_2 ($0.05), tier_2→tier_3 (requires_owner_approval=true)"
  - "AC-03: degradation_override 三档反向压降——global_budget_used > 60%/80%/95% 逐级降级覆盖升级"
  - "AC-04: cross_provider_least_cost——同一 Tier 内 min(cost_per_1m_input) WHERE availability=UP AND quality_score >= 0.7"
  - "AC-05: Tie-break 规则——prefer provider with highest remaining rate limit capacity"
  - "AC-06: 最低价路由表每 5 分钟（refresh_interval=300s）自动刷新"
  - "AC-07: batch_routing——eligible_tasks（周报/归因分析/批量 Lint/格式化/ROI 计算）urgency=low → 自动走 Batch API"
  - "AC-08: batch_routing 集成——任务系统标记 task.urgency=low 命中 eligible_tasks 列表 → 路由到 batch"
  - "AC-09: vendor_fallback 四层切换：Anthropic unavailable → OpenAI → Google → DeepSeek → Ollama(local)"
  - "AC-10: provider_tier_awareness——Anthropic 4-Tier RPM/TPM 实时追踪，RPM 剩余 < 20% 自动切备用 Provider"
  - "AC-11: 路由决策写入 audit trail——每一次路由决策（model, provider, reason）可审计"
  - "AC-12: decision_matrix——normal_state escalation_chain 生效，budget_tight degradation_override 优先"
  - "AC-13: 支持 quality_weighted 路由——quality_score < 0.7 的便宜模型不选"
  - "AC-14: Think-time 路由集成——thinking_tokens > 2× output_tokens AND 非终审/审计 → 切 tier_0 或 tier_1 非推理模型"
rollback_instructions: "删除 model_router.py，所有 API 调用退化到使用预算紧张时的模型路由逻辑（硬编码 tier_1_cheap）——需同步恢复调用方代码移除 Router 依赖"
context_assembly_manifest:
  primary:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\budget-enforcer\\blueprint.md#L183-L267 (§2.3 Model Router)"
  fallback:
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\config\\budget_policy.yaml"
    - "D:\\ZephyrAlpha\\src\\zephyr\\budget_enforcer\\pricing_sync.py"
assigned_agent: any
tags: [model-router, tier-routing, least-cost, batch-api, provider-fallback, experimental]
replaces: []
rollback_of: []
superseded_by: []
---

# TASK-INF-0104: Model Router — Tier 升级链 + Multi-Provider Least-Cost + Batch + Provider Tier

## 1. 任务目标

实现智能模型路由器——默认选择免费/最便宜模型，仅在质量不达标时逐级升级。同一 Tier 内多 Provider 自动选最低价。非实时任务走 Batch API 享受 50% 折扣。厂商不可用时自动故障切换。

## 2. 背景

蓝图 §2.3（决策 D-024-04，v0.4.0 方向反转）：从"默认高→降级到低"改为"默认最低→质量不达标才升级"。对标 Cost Engineering for Agents (2025) 降本 80%+ 实践。v0.5.0 新增 multi-provider least-cost。v0.6.0 新增 think-time 路由。

## 3. 实施步骤

### Step 1: ModelRegistry
```python
@dataclass
class ModelEntry:
    model_id: str
    provider: str  # anthropic | openai | google | deepseek | ollama
    tier: int      # 0-3
    cost_per_1m_input: float
    cost_per_1m_output: float
    context_window: int
    max_output: int
    capabilities: set[str]  # reasoning, vision, tool_use, etc.
    quality_score: float    # 0-1 基于历史 output_validator 评分
    availability: bool
    rpm_limit: int
    tpm_limit: int
    rpm_used: int
    tpm_used: int

class ModelRegistry:
    def __init__(self, pricing_sync: PricingSync):
        self.models: dict[str, ModelEntry] = {}
    def get_tier_models(self, tier: int) -> list[ModelEntry]:
    def get_cheapest_in_tier(self, tier: int) -> ModelEntry:
    def get_fallback(self, provider: str, tier: int) -> ModelEntry:
```

### Step 2: ModelRouter 路由决策
```python
class ModelRouter:
    def route(self, task_complexity: int, estimated_tokens: int,
              urgency: str, budget_ratio: float,
              env_profile: str, previous_quality_score: float | None,
              is_thinking_heavy: bool = False) -> RouteDecision:
        # 1. 判断 default tier（env_profile + task_complexity）
        # 2. 判断 batch eligible（urgency=low + in eligible_tasks）
        # 3. 判断 degradation override（budget_ratio > threshold）
        # 4. 判断 escalation（previous_quality_score < threshold）
        # 5. 选 least-cost provider in tier
        # 6. 返回 RouteDecision
```

### Step 3: ProviderTierAwareness
- 追踪 Anthropic 4-Tier：tier_1(50rpm/100ktpm), tier_2(500rpm/500ktpm), tier_3(2000rpm/2M tpm), tier_4(5000rpm/5M tpm)
- RPM 剩余 < 20% → auto fallback

### Step 4: BatchRouter
- eligible_tasks 映射表（5 类任务 → batch）
- batch_max_latency=24h
- 集成 MOD-MASTER-001 task.urgency 字段

### Step 5: VendorFallback
- 四层链式故障切换
- 每个 fallback 记录 reason + latency

## 4. 产出物清单

| # | 文件 | 状态 |
|---|------|:---:|
| 1 | `src/zephyr/budget_enforcer/model_router.py` | 新建 |

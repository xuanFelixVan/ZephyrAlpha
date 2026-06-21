---
module_id: KE-1854--------model-router-001
status: active
title: 2.3 模型路由升级（Model Router）
category: module_blueprint
---

# 2.3 模型路由升级（Model Router）

2.3 模型路由升级（Model Router）

> **决策 D-024-04（v0.4.0 修订）**：模型路由方向反转——从"默认用高→预算紧张降级到低"改为"默认最低→质量不达标才升级"。专业机构实践（Cost Engineering for Agents, 2025）+ Vibe Coding 社区模型组合拳（需求理解用弱模型→代码生成用强模型→Lint 用免费模型）降本 80%+。

```yaml
model_tier_routing:
  description: "按任务复杂度自动选择最优成本模型——默认最低 Tier，质量不达标才升级"
  strategy: "cheapest_first_escalate_on_quality_fail"

  # ── 模型升级路径（v0.4.0 反转）──
  escalation_chain:
    - from: "tier_0_free"
      to: "tier_1_cheap"
      trigger: "tier_0 返回质量不达标（output_validator 评分 < 阈值）OR 任务复杂度 > tier_0.max_complexity"
      max_escalation_cost: 0.01      # 升级一次的成本上限

    - from: "tier_1_cheap"
      to: "tier_2_standard"
      trigger: "tier_1 返回质量不达标 OR 任务需要深度推理（架构设计/多文件重构）"
      max_escalation_cost: 0.05

    - from: "tier_2_standard"
      to: "tier_3_premium"
      trigger: "tier_2 返回质量不达标 AND 任务为终审裁决/安全审计"
      requires_owner_approval: true    # Tier-3 使用需要 Owner 信号

  # ── 预算紧张时的降级覆盖（保留旧路径作为反向压降）──
  degradation_override:
    - from: "tier_3_premium"
      to: "tier_2_standard"
      trigger: "global_budget_used > 60%"

    - from: "tier_2_standard"
      to: "tier_1_cheap"
      trigger: "global_budget_used > 80%"

    - from: "tier_1_cheap"
      to: "tier_0_free"
      trigger: "global_budget_used > 95%"

  # ── 分析：何时升级 vs 降级 ──
  decision_matrix:
    normal_state: "escalation_chain 生效——默认 tier_0，质量驱动升级"
    budget_tight: "degradation_override 优先——预算紧张时压降覆盖升级"

  # ── 批次路由（v0.4.0 新增）──
  batch_routing:
    description: "非实时任务走 Batch API（Anthropic/OpenAI Batch API 50% 折扣）"
    eligible_tasks:
      - "周报生成"
      - "成本归因分析"
      - "批量 Lint 修复"
      - "文档批量格式化"
      - "ROI 计算"
    max_latency: "24h"            # Batch 任务最大延迟容忍
    cost_saving: "50%"            # Batch API 折扣
    integration: "任务系统（MOD-MASTER-001）标记 task.urgency=low → 自动走 batch"

  # ── 厂商风险对冲 ──
  vendor_fallback:
    anthropic_unavailable: "→ OpenAI equivalent tier"
    openai_unavailable: "→ Google equivalent tier"
    google_unavailable: "→ DeepSeek equivalent tier"
    all_unavailable: "→ local free model (Ollama)"

  # ── v0.5.0 新增：多Provider同Tier内least-cost路由 ──
  cross_provider_least_cost:
    description: "同一 Tier 内部存在多个 Provider 的等效模型——自动选最便宜的"
    example:
      tier_2_standard:
        candidates:
          - provider: "anthropic"
            model: "claude-sonnet-4"
            cost_per_1m_input: $3.00
          - provider: "openai"
            model: "gpt-4o"
            cost_per_1m_input: $2.50
          - provider: "google"
            model: "gemini-2.0-pro"
            cost_per_1m_input: $1.25
        selection: "min(cost_per_1m_input) WHERE availability=UP AND quality_score >= 0.7"
        tie_break: "prefer provider with highest remaining rate limit capacity"
    quality_weighted: true          # 不纯按价格——质量太差的便宜模型不选
    refresh_interval: 300           # 每 5 分钟刷新一次最低价路由表

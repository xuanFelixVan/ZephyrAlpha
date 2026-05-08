---
module_id: KE-module_blu-2_9_burn_rate-000
title: 2.9 Burn Rate 多窗口监控
category: module_blueprint
---

# 2.9 Burn Rate 多窗口监控

2.9 Burn Rate 多窗口监控

> **决策 D-024-09（v0.4.0 修订）**：Google SRE 标准——不是"用了多少"，而是"在以多快的速度烧预算"。v0.4.0 新增 Distribution Shift 检测——结构异常往往先于总量异常出现。

```yaml
burn_rate_monitor:
  windows:
    window_10min:
      description: "10 分钟消耗速率"
      critical_threshold: "> 10× normal burn rate"
      action: "立即触发 L3_compress"
      purpose: "捕捉 runaway agent"

    window_1h:
      description: "1 小时消耗速率"
      critical_threshold: "> 5× normal burn rate"
      action: "触发 L2_model_switch"
      purpose: "捕捉短期异常"

    window_6h:
      description: "6 小时消耗速率"
      critical_threshold: "> 3× normal burn rate"
      action: "通知 Owner + 触发 L1_warning"
      purpose: "捕捉施工效率下降"

    window_24h:
      description: "24 小时消耗趋势"
      critical_threshold: "> 2× normal burn rate"
      action: "每日摘要中包含预警"
      purpose: "捕捉渐进式成本膨胀"

  # normal burn rate = 过去 7 天的同时段平均消耗速率
  baseline: "7d_moving_average"
  alert_cooldown: 300            # 同一 burn rate 告警 5 分钟内不重复

  # ── v0.4.0 新增：使用结构分布偏移检测 ──
  distribution_shift:
    description: "检测 token 消耗结构的异常变化——结构异常往往比总量异常更早出现"
    dimensions:
      - "by_model"              # 某模型消耗比例突变
      - "by_tool"               # 某工具消耗比例突变
      - "by_agent"              # 某 Agent 消耗比例突变
      - "by_outcome"            # 失败消耗比例突变
    detection: "Jensen-Shannon divergence vs 7 天滑动窗口基线"
    alert_threshold: "JS divergence > 0.3"
    action: "INFO 日志 '检测到消耗结构偏移——[dimension] 异常增长，可能原因：[suggestion]'"

  # ── v0.4.0 新增：被限流的浪费追踪 ──
  rate_limit_impact:
    description: "被厂商限流后的重试消耗是纯浪费——需要独立追踪"
    tracking:
      - "rate_limit_hit_count"
      - "retry_tokens_wasted"
      - "retry_cost_wasted"
    alert: "限流浪费 > $1.00/天 → 建议调整并发数或升级 Tier"

  # ── v0.5.0 新增：Provider Tier 感知 ──
  provider_tier_awareness:
    description: "Anthropic 4-Tier 限额体系——每 Tier 有不同的 RPM/TPM 上限，超限后请求被拒"
    tiers:
      tier_1: { rpm: 50, tpm: 100000 }        # 刚注册
      tier_2: { rpm: 500, tpm: 500000 }        # 消费 > $50
      tier_3: { rpm: 2000, tpm: 2000000 }      # 消费 > $200
      tier_4: { rpm: 5000, tpm: 5000000 }      # 消费 > $1000
    tracking: "实时追踪当前 Tier 的剩余 RPM/TPM——在路由决策中纳入容量约束"
    alert: "RPM 剩余 < 20% → 自动切换到备用 Provider 的同 Tier 模型"
```

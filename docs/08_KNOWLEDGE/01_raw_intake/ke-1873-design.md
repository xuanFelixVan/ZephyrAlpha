---
module_id: KE-1782-----------------------d-0-000
status: active
title: 2.21 告警可信度评分——防止"狼来了"效应（决策 D-023-35）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.21 告警可信度评分——防止"狼来了"效应（决策 D-023-35）

2.21 告警可信度评分——防止"狼来了"效应（决策 D-023-35）

> **决策 D-023-35**：每个检测器维护一个 credibility score——基于 false positive rate、detection precision、历史误报纠正率。低可信度检测器的告警自动降级或延迟推送。Owner 可手动调整可信度权重。
>
> **决策依据**：1人维护下最大的风险不是漏报（false negative），而是告警疲劳导致 Owner 忽略所有告警（alert blindness）。可信度评分让 Owner 只关注"真正值得关注的"。

```yaml
credibility_scoring:
  formula: "credibility = base_score × (1 - fp_rate) × precision × recency_factor"

  base_score:
    new_detector: 0.5
    proven_detector: 1.0

  fp_rate:
    description: "FALSE_POSITIVE 标记数 / 总告警数（近 90 天）"
    impact: "fp_rate > 0.3 → credibility × 0.5 / fp_rate > 0.5 → credibility × 0.2"

  precision:
    description: "VERIFIED 的漂移在总告警中的占比（排除 FALSE_POSITIVE 后的实际修复率）"
    impact: "precision < 0.3 → 检测器可能过于敏感"

  recency_factor:
    description: "最近一次 false positive 纠正距今天数"
    impace: "> 90 天未纠正 → 检测器可能已过时 → credibility × 0.8"

  alert_modulation:
    high_credibility: "> 0.8 → 正常告警，最高优先级推送"
    medium_credibility: "0.4-0.8 → 告警但聚合到批次"
    low_credibility: "< 0.4 → 转为 shadow 观测，不推送，仅在仪表板可见"

  owner_override:
    description: "Owner 可手动设置特定检测器的 credibility_weight（如：我知道它误报多但暂时不想修）"
```

---

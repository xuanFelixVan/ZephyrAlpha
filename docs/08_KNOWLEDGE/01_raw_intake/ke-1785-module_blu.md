---
module_id: KE-1694
status: active
title: 2.11 降级机制与渐进式恢复
category: module_blueprint
ttl: permanent
---

# 2.11 降级机制与渐进式恢复

2.11 降级机制与渐进式恢复

> **对标**：Terraform Drift P0/P1/P2 可升降级 + Michael Nygard 熔断器三种状态机（OPEN/HALF_OPEN/CLOSED）。

```yaml
deescalation_progressive_recovery:
  # === 降级路径 ===
  deescalation_paths:
    blocked_to_auto_guard:
      condition: "熔断器 HALF_OPEN + Owner 确认 + 连续 5次试探操作安全"
      action: "降级至 auto_guard——允许有限操作但护栏全开"
      trial_period: "30分钟观察期"

    auto_guard_to_autonomous:
      condition: "同一Agent同类操作连续 3 次后验通过"
      action: "降级至 autonomous——恢复完全自主"

    blocked_to_autonomous:
      condition: "仅限熔断器 CLOSED + Owner手动重置"
      note: "不推荐直接跨越 auto_guard——应经过渐进观察期"

  # === 熔断器状态机映射 ===
  circuit_breaker_escalation:
    OPEN:
      escalation: "blocked"
      action: "完全阻断所有操作"
    HALF_OPEN:
      escalation: "auto_guard"
      action: "允许试探性操作 + 护栏全开 + 单个Agent执行"
    CLOSED:
      escalation: "autonomous"
      action: "恢复正常自主"

  # === 降级保护 ===
  deescalation_safety:
    max_deescalation_rate: "同一Agent 10分钟内最多降级 1 次"
    reason: "防止降级-升级震荡（频繁切换）"
    cooldown: "每次降级后冷却 5 分钟才能再次评估降级条件"
```

---

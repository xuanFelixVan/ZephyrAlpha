---
module_id: KE-module_blu-cache_policy_yaml-000
title: cache_policy.yaml
category: module_blueprint
---

# cache_policy.yaml

cache_policy.yaml
cache_policy:
  # v0.3.0 被动TTL模式（旧）
  passive_ttl: "DEPRECATED——不再使用TTL=5min被动过期"
  
  # v0.4.0 推送驱动模式（新）
  push_driven:
    mechanism: "权限变更事件 → 分析diff → 精准失效受影响缓存 → 所有Guard立即拉取最新判定"
    max_invalidation_latency_ms: 100     # 推送延迟上限
    fallback_ttl: 300                     # 如果推送失败（网络问题等），兜底TTL=5min
    health_check: "每10秒检查推送通道健康——连续3次失败 → 降级为被动TTL + 告警"
  
  # ─── 降级攻击防护（与2.3联动）───
  degradation_attack_detection:
    description: "同一Agent触发的权限降级事件如果有规律性→标记为'疑似攻击'"
    pattern_detection:
      - pattern: "rapid_degradation_trigger"
        condition: "Agent在10秒内触发 >= 3 次同层检查失败导致partial_failure"
        action: "Agent BLOCKED + 标记为'疑似降级攻击'"
      - pattern: "cache_invalidation_flood"
        condition: "Agent在30秒内触发 >= 5 次缓存失效事件"
        action: "缓存进入不可变模式（变更需Owner审核）+ Agent BLOCKED"
```

---

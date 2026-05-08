---
module_id: KE-module_blu-2_3_l0___engine_________d-018--002
title: 2.3 L0 — Engine 降级策略（决策 D-018-06）
category: module_blueprint
---

# 2.3 L0 — Engine 降级策略（决策 D-018-06）

2.3 L0 — Engine 降级策略（决策 D-018-06）

> **决策 D-018-06**：Permission Engine 自身故障时的降级策略——崩 = blocked（绝对不放行），而非崩 = pass（裸奔）。
>
> **决策依据**：负面偏好——权限系统失效时，安全优先于便利。实现方式对标 GateEngine v2.0 的 failurePolicy。

```yaml
engine_degradation:
  # ─── 三层降级策略 ───
  l0_immutable_core_failure:
    behavior: "BLOCKED — 系统启动失败。不可变核心是最后防线，坏了就全停"
    indicator: "Agent RBAC system unavailable: Immutable Core failed"

  l1_l6_failure:
    behavior: "BLOCKED — 降级为拒绝模式。宁可误杀不可漏放"
    indicator: "Agent RBAC degraded to BLOCKED: runtime permission check unavailable"
    fallback_audit: "所有被降级拒绝的操作均记录原因"

  partial_failure:
    behavior: "按层降级——L4 崩不影响 L0-L3 继续执行"
    indicator: "Agent RBAC partial degradation: {failed_layer} unavailable"
    metric: "d2.authz.decision.degraded counter"
    # ─── v0.4.0 降级攻击防护 ───
    attack_protection: "记录触发降级的操作来源Agent。如果同一Agent触发的降级事件 > 2次/小时 → 该Agent立即BLOCKED + 标记为'疑似降级攻击'"
    causal_chain: "partial_failure中失败的层之前最后操作的Agent → 关联分析 → 累计 → BLOCKED"
    degraded_layer_bypass: "降级事件发生时，触发降级的Agent所在的层就算恢复了也不能对该Agent放行——需Owner手动审核后才能解除"

  # ─── 降级恢复 ───
  recovery:
    auto: "L0 每 30 秒自检一次，恢复即自动解除降级"
    manual: "Owner 可随时强制解除降级状态"
    audit: "降级/恢复事件写入审计日志"
```

---

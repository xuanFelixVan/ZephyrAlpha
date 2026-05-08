---
module_id: KE-module_blu-3_17_temporal_signature_drift-000
title: 3.17 Temporal Signature Drift——渐进类型化打破指纹缓存（v0.7.0 终极审视 #6）
category: module_blueprint
---

# 3.17 Temporal Signature Drift——渐进类型化打破指纹缓存（v0.7.0 终极审视 #6）

3.17 Temporal Signature Drift——渐进类型化打破指纹缓存（v0.7.0 终极审视 #6）

**发现**：Stage 0.5 签名指纹 `SHA256(param_types + return_type)` 假设函数的类型注解是静态的。但在 Python 中，类型注解在开发过程中持续演化——`str` → `Optional[str]` → `str | None` → `float | None`。每一次演化都会改变签名指纹，使 Stage 0.5 的有效性持续退化。
**外部审计师的致命问题：6 个月后，函数签名可能已经和缓存中的签名完全不同——引擎在比对的是"过去的影子"。**

**Temporal Drift 检测 + 自动重算**：

```
每次全量扫描时：
  ① 对 function_cache 中的每个函数条目执行 AST 重新解析
  ② 重新计算 signature_fingerprint
  ③ 对比新旧 fingerprint → 不同 = mark "SIGNATURE-DRIFT-DETECTED"
  ④ 更新缓存中的 fingerprint + 记录 drift_history
  ⑤ 检测到连续 3 次扫描 fingerpirnt 都不同 → "UNSTABLE-SIGNATURE" → 将该函数标记为 unstable
     → Stage 0.5 不再对此函数做签名碰撞检测 → 降级到 Stage 1-2
```

```yaml

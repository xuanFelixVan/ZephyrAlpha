---
module_id: KE-3304
title: 4.4 误报与性能预算（硬约束）
category: documentation
ttl: permanent
---

# 4.4 误报与性能预算（硬约束）

4.4 误报与性能预算（硬约束）

| 指标 | experimental SLO | beta 目标 | 当前基线 |
|------|:----------:|:------------:|:--------:|
| 误拦率（合法请求被拒）| < 2% | < 0.5% | 未测 |
| 漏拦率（攻击被放行）| < 5% | < 1% | 未测 |
| LSG 延迟 P99 | < 200ms | < 100ms | 未测 |
| fail-closed 触发率 | < 0.1%/天 | < 0.01%/天 | 未测 |

**红队评估**：experimental 末必须跑一次红队评估（模拟 OWASP LLM01/02/06/08/09 攻击），记录漏拦率。阈值 > 5% 触发 **TECH-16 升级**（见 `technology_landscape.yaml upgrade_watchboard`）。

---

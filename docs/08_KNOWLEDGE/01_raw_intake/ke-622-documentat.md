---
module_id: KE-560
title: 9.3 环境晋级门禁
category: documentation
ttl: permanent
---

# 9.3 环境晋级门禁

9.3 环境晋级门禁

| 门禁 | 必须满足 |
|------|---------|
| **Gate 1（Dev→UAT）** | 单元测试全通过 + 回测 ≥ 1 年 + Sharpe > 0.5 |
| **Gate 2（UAT→Staging）** | UAT 模拟盘 ≥ 2 周无重大异常 + Code Review + ADR |
| **Gate 3（Staging→Prod）** | Shadow Trading ≥ 1 周 + SLO 验证 + 书面风险确认 + Runbook |

---

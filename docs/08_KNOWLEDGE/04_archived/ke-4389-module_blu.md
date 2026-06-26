---
module_id: KE-4227
title: 8.5 自动恢复与手动恢复边界
category: module_blueprint
ttl: permanent
---

# 8.5 自动恢复与手动恢复边界

8.5 自动恢复与手动恢复边界

| 恢复路径 | 自动 or 手动 | 理由 |
|---------|:----------:|------|
| Emergency → Critical | 自动（冷却 6h） | 临时脉冲不应无限期锁住系统 |
| Critical → Cautious | 自动（冷却 24h） | 趋势逆转后逐步放开 |
| Cautious → Healthy | 自动 | 正常恢复，无需人工 |
| 只读模式 | **手动（Owner）** | 只读模式 = 系统停止接收新工作，影响太大，必须人工确认 |

---

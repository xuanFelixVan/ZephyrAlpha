---
module_id: KE-3187
title: 12.2 成本预警机制
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 12.2 成本预警机制

12.2 成本预警机制

| 阈值 | 触发动作 |
|-----|---------|
| **月度软阈值 ¥3000** | 日报 Feishu 推送成本曲线 |
| **预警阈值 ¥3500**（116%） | Feishu 告警 + 自动启用降级模式 |
| **强制阈值 ¥4500**（150%） | 🔴 人工介入 + 暂停非关键任务 |
| **单日峰值 >¥500** | 即时 Feishu 告警 |

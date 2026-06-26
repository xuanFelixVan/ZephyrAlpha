---
module_id: KE-2485---kill-switch-----v2-1-0-000
title: 8.4 与 Kill Switch 的联动（v2.1.0 细化）
category: module_blueprint
ttl: permanent
---

# 8.4 与 Kill Switch 的联动（v2.1.0 细化）

8.4 与 Kill Switch 的联动（v2.1.0 细化）

| Error Budget 级别 | Kill Switch 动作 | 恢复条件 |
|------------------|-----------------|---------|
| Critical 持续 1h | 自动触发 **保守模式**（仅允许 P0 操作，暂停所有 P1/P2 任务） | 恢复到 Cautious + Owner 确认 |
| Emergency | 自动触发 **只读模式**（禁止所有写入操作，仅允许查询和诊断） | Owner 手动解除 |
| 单日成本 > $100 | 自动触发保守模式 | Owner 确认 + 成本回落 |
| Burn Rate 1h > 14.4× | 立即触发只读模式（不等待 Emergency 判定——见 §8.3 短窗口） | Owner 调查根因后手动解除 |

---
module_id: KE-4215
title: 8.1 五级响应定义
category: module_blueprint
ttl: permanent
---

# 8.1 五级响应定义

8.1 五级响应定义

| 级别 | Error Budget 剩余 | 触发条件 | 团队响应 | 开发重点 | 发布频率 | 自动动作 |
|------|-----------------|---------|---------|---------|---------|---------|
| **Healthy** | >60% | 默认 | 正常运营 | 新功能、实验 | 标准发布节奏 | 无 |
| **Warning** | 40%-60% | 过去 7 天消耗率 > 正常 2× | 轻度关注 | 功能完成 + 小改进 | 标准节奏 + 观察 | `log_warning` + 每周报告 |
| **Cautious** | 20%-40% | 过去 7 天消耗率 > 正常 3× | 加强监控 | 功能完成 + 修复 | 降低发布频率 50% | `log_warning` + `notify_owner` + 消耗率仪表盘 |
| **Critical** | 5%-20% | 过去 3 天消耗率 > 正常 5× | 可靠性优先 | Bug 修复 + 稳定性改进 | 发布冻结直到恢复到 Cautious | `log_critical` + `freeze_releases` + `auto_escalate` |
| **Emergency** | <5% | 预算即将耗尽 | 全量响应 | 仅修复导致预算消耗的根因 | 全冻结 | `log_emergency` + `kill_switch` 保守模式 + `notify_owner_urgent` |

---
module_id: KE-4352---fail-safe-000
title: fail-closed 与 fail-safe 的分级策略
category: module_blueprint
ttl: permanent
---

# fail-closed 与 fail-safe 的分级策略

fail-closed 与 fail-safe 的分级策略

| 层级 | 故障策略 | 降级行为 | 恢复条件 |
|:---|:---|------|------|
| L0 | fail-closed | 禁止加载未验证组件 | 供应链扫描恢复 |
| L1 | fail-closed | 拒绝所有输入 | 输入检测器恢复 |
| L2 | fail-closed | 拒绝Prompt构建 | Prompt保护层恢复 |
| L3 | fail-closed | 拒绝所有输出 | 输出验证恢复 |
| L4 | fail-closed | 拒绝Agent操作 | Agent安全层恢复 |
| L5 | fail-closed | 拒绝超限请求 | 计数器/熔断重置 |
| L6 | fail-open (降级) | stderr fallback | 日志系统恢复 |
| L7 | fail-open (不阻断) | 跳过验证 | 验证系统恢复 |

---

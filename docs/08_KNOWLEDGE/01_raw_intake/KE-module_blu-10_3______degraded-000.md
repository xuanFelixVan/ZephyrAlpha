---
module_id: KE-module_blu-10_3______degraded-000
title: 10.3 允许的 "degraded" 情况（非安全相关）
category: module_blueprint
---

# 10.3 允许的 "degraded" 情况（非安全相关）

10.3 允许的 "degraded" 情况（非安全相关）

仅有两类 **不** 属于安全的情况允许轻度降级：

1. **审计日志写失败**：主流程继续但 alert，不拒绝请求（日志失败比拒绝所有流量危害小）
2. **stats 查询失败**：FLE 拉不到指标不影响放行决策（FLE 自己降级 DEGRADE-001）

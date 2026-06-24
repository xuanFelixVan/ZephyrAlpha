---
module_id: KE-1370
title: 10.5 降级条件速查表
category: module_blueprint
---

# 10.5 降级条件速查表

10.5 降级条件速查表

| 触发条件 | 降级动作 | 上游感知 |
|---------|---------|---------|
| 规则库损坏 | **全拒（fail-closed）** | DEGRADE-SEC-001 / 要求人工 |
| schema 未注册 | 默认 fail-closed；显式 opt-in 可放行 | DEGRADE-SEC-002 |
| secret 扫描器挂 | **fail-closed** | DEGRADE-SEC-003 |
| 审计日志写失败 | 主流程继续 + alert | 日志 |
| stats 查询失败 | 降级返回空 | - |
| FLE 挂（不收推送） | 本地缓冲 metrics | FLE 侧 DEGRADE-001 |

---

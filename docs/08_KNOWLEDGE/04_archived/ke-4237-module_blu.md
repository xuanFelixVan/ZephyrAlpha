---
module_id: KE-4078-----------17-003
title: 4. 集成目标（蓝图 §17）
category: module_blueprint
ttl: permanent
---

# 4. 集成目标（蓝图 §17）

4. 集成目标（蓝图 §17）

| # | 目标模块 | 集成方式 |
|---|---------|---------|
| 1 | **Agent RBAC** | 向 RBAC 系统注册容量保障的治理层角色（Observer/Operator/Admin），控制 hot-mode 升级权限 |
| 2 | **Budget Enforcer** | Token/Error Budget 指标注入 Budget Enforcer 的限流规则；Sandbox policy 成为 Budget Enforcer 的子策略 |
| 3 | **Rollback System** | Kill Switch 事件 + degradation chain 状态注册为 Rollback System 的回滚源；TASK-0010 risk-register.yaml 中所有 R1-R16 注册为回滚触发器 |
| 4 | **System Telemetry** | Capacity Metrics→L12 System Telemetry Pipeline；全部 OTel Metrics 输出到统一 Collector；Provenance Chain hash 审计日志注册 |

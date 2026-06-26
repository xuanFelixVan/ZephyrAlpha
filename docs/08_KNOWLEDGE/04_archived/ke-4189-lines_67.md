---
module_id: KE-4032---------lines-67-142-000
title: §3 域内集成契约 (lines 67-142) —— 逐字段对齐
category: module_blueprint
ttl: permanent
---

# §3 域内集成契约 (lines 67-142) —— 逐字段对齐

§3 域内集成契约 (lines 67-142) —— 逐字段对齐

| 契约 | 方向 | 触发时机 | 数据流 | 覆盖 task_id | 字段匹配 |
|------|------|----------|--------|------|:---:|
| G-CT-001 | RBAC→Audit | 权限判定完成 | result→Audit.write(result) | TASK-GOV-0002 | ✓ 6/6 字段一致 |
| G-CT-002 | Audit→Rollback | 异常操作签名 | anomaly_detector→Rollback | TASK-GOV-0003 | ✓ |
| G-CT-003 | Rollback→Escalation | 回滚失败/验证不通 | rollback_result→升级 | TASK-GOV-0004 | ✓ |
| G-CT-004 | Escalation→RBAC | 升级审批验证 | approval_request→RBAC | TASK-GOV-0005 | ✓ |
| G-CT-005 | Drift→Rollback | 可自动修复漂移 | drift_event→修复 | TASK-GOV-0006 | ✓ |
| G-CT-006 | Budget→Escalation | Burn Rate>阈值 / 全局耗尽 | budget_alert→升级 | TASK-GOV-0007 | ✓ 🔧 已修复触发条件 |
| G-CT-007 | Spec→RBAC+Audit | Skill 加载 | manifest→RBAC / Skill执行→Audit | TASK-GOV-0008 | ✓ |
| G-CT-008 | A2A→RBAC+Escalation | Phase 4 激活 | A2A通信→RBAC+Escalation | TASK-GOV-0009 | ✓ |

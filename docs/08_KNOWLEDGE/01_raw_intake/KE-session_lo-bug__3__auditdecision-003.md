---
module_id: KE-session_lo-bug__3__auditdecision-003
title: Bug #3: AuditDecision 字段不匹配
category: session_log
---

# Bug #3: AuditDecision 字段不匹配

Bug #3: AuditDecision 字段不匹配
- **位置**: [default_security_gateway.py](file:///d:/ZephyrAlpha/src/zephyr/l10_compliance/default_security_gateway.py#L217-L231)
- **现象**: `TypeError: AuditDecision.__init__() got an unexpected keyword argument 'findings'`
- **根因**: AuditDecision 实际字段为 `decision_id, action, rule_id, reason, timestamp, metadata`——没有 `findings/content_safe/sanction_enabled`
- **修复**: 使用正确字段构建 AuditDecision，将 findings/content_safe/sanction_enabled 放入 `metadata` dict

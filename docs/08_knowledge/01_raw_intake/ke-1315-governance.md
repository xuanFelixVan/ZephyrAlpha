---
module_id: KE-1228
title: SIR-002：全级别通用响应规则
category: governance
ttl: permanent
doc_type: knowledge_entry
---

# SIR-002：全级别通用响应规则

SIR-002：全级别通用响应规则

| 编号 | 规则 | 违反后果 |
|------|------|---------|
| SIR-002 | 所有安全事件（P0~P3）必须在发现后 30 分钟内记录在安全事件日志中，包含：时间戳（ISO 8601 UTC）、级别、事件描述、响应措施、复盘总结。日志文件：`docs/09_audit/security-incident-log.md`，格式：每事件一条 Markdown 表格行 | 审计不通过 |

---
module_id: KE-documentat-9_1-001
title: 9.1 审计数据架构
category: documentation
---

# 9.1 审计数据架构

9.1 审计数据架构

审计日志是 **D-MGMT 域** 的核心。采用 **SQLite WAL 模式 + Session Log JSON Lines** 双轨存储：

```
.runtime/sqlite/audit.db (WAL)         .runtime/logs/session/
├── table: security_events             ├── YYYY-MM-DD/
├── table: llm_calls                   │   ├── session-<uuid>.jsonl
├── table: agent_actions               │   └── ...
├── table: secret_scan_findings        └── carryover-<uuid>.json
└── table: sandbox_violations              （见 session-carryover-schema.md）
```

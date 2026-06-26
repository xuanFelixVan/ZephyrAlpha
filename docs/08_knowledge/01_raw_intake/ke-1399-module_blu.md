---
module_id: KE-1310-------------6-3-000
title: 1.2 蓝图外已有实现（蓝图 §6.3）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 1.2 蓝图外已有实现（蓝图 §6.3）

1.2 蓝图外已有实现（蓝图 §6.3）

| 已有实现 | 实际路径 | 归属蓝图 |
|---------|---------|---------|
| Token 预算管理器 (L1/L2/L3) | `src/zephyr/context-engine/context_budget_tracker.py` | context-engine |
| 上下文压缩器 (DocCompressor) | `src/zephyr/context-engine/doc_compressor.py` | context-engine |
| 熔断器 (CBGManager + L08) | `src/zephyr/gates/circuit_breaker.py` | gate-engine |
| Agent SLO 监控 (5 项 SLO) | `src/zephyr/orchestrator/agent_health_monitor.py` | orchestrator |
| AI 行为审计日志 | `src/zephyr/llm-security/behavior_audit_logger.py` | llm-security |
| 输入消毒器 (InputSanitizer) | `src/zephyr/llm-security/input_sanitizer.py` | llm-security |
| 原子事务管理器 (ATM) | `src/zephyr/db/atomic_transaction_manager.py` | database |
| SQLite Schema DDL + init_db | `src/zephyr/db/sqlite_schema.py` | database |
| MCP 工具限流 (rate_limit_qps) | `src/zephyr/mcp/tool-contracts.yaml` | mcp-servers |
| L12 Metrics 骨架 | `src/zephyr/l12_system_telemetry/metrics/__init__.py` | system-telemetry |
| 任务反馈收集器 | `src/zephyr/feedback-loop/feedback_collector.py` | feedback-loop |

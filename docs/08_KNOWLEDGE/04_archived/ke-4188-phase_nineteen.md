---
module_id: KE-4188
title: 3. 蓝图外已有实现（§19.2 + §6.3）
category: module_blueprint
ttl: permanent
---

# 3. 蓝图外已有实现（§19.2 + §6.3）

3. 蓝图外已有实现（§19.2 + §6.3）

| 模块名称 | 实际路径 | 归属蓝图 | 验证要点 |
|---------|---------|---------|---------|
| Token 预算管理器 (L1/L2/L3) | `src/zephyr/context-engine/context_budget_tracker.py` | context-engine | Level 2 session级 |
| 上下文压缩器 (DocCompressor) | `src/zephyr/context-engine/doc_compressor.py` | context-engine | Doc size压缩 |
| 熔断器 (CBGManager + L08) | `src/zephyr/gates/circuit_breaker.py` | gate-engine | M-13 fault_isolator子集 |
| Agent SLO 监控 (5项SLO) | `src/zephyr/orchestrator/agent_health_monitor.py` | orchestrator | 5-SLO + 三态健康 |
| AI 行为审计日志 | `src/zephyr/llm-security/behavior_audit_logger.py` | llm-security | 4种事件 + JSONL |
| 输入消毒器 (InputSanitizer) | `src/zephyr/llm-security/input_sanitizer.py` | llm-security | 输入过滤 |
| 原子事务管理器 (ATM) | `src/zephyr/db/atomic_transaction_manager.py` | database | DB原子性 |
| SQLite Schema DDL + init_db | `src/zephyr/db/sqlite_schema.py` | database | DDL |
| MCP 工具限流 | `src/zephyr/mcp/tool-contracts.yaml` | mcp-servers | rate_limit_qps |
| L12 Metrics 骨架 | `src/zephyr/infra_ops/metrics/__init__.py` | system-telemetry | Metrics |
| 任务反馈收集器 | `src/zephyr/feedback-loop/feedback_collector.py` | feedback-loop | Feedback |
| **不在此清单但存在**: 本蓝图依赖的 `event_bus.py`、`pydantic2.yaml`、`prisma.yaml` 等 |

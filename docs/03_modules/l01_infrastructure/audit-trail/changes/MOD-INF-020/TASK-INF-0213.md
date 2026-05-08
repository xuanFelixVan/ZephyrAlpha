---
task_id: "TASK-INF-0213"
source_blueprint: "MOD-INF-020"
source_section: "蓝图 §2.7 自监控系统（self_monitoring YAML block）"

title: "实现自监控系统——heartbeat + 健康指标采集 + 自动修复触发器"
description: |
  实现 `src/zephyr/audit_trail/self_monitor.py` 中的自监控系统。
  - `AuditHeartbeat`: 60s 间隔写入 heartbeat 条目 → 读回验证哈希链 → 延迟 < 5ms
  - `HealthMetricsCollector`: 采集 10 项指标——write_latency_p99_ms/disk_usage_pct/jsonl_file_count/hash_chain_integrity/hmac_validity_rate/sqlite_index_health/agent_signature_validity_rate/delegation_chain_validity/trust_score_trend/cross_ide_consistency
  - `AutoHealer`: sqlite_index_health 失败 → 自动触发索引重建
  - 告警路由：P0→阻断 / P1→通知 Owner / P2→日志记录
  - 连续 3 次 heartbeat 失败 → 写入 emergency fallback log
  落地 D-020-05 元审计 + R6/R7 风险缓解。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\self_monitor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\models.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\self_monitor.py"
    description: "完整实现自监控系统——heartbeat + 10项指标 + 告警路由 + 自动修复"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_self_monitor.py"
    description: "单元测试——heartbeat正常/失败3次/escalation/自动重建触发"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\self_monitor.py"
  - "D:\\ZephyrAlpha\\tests\\audit_trail\\test_self_monitor.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "GOV-CMP-002"
    section: "AUD-002"
    reason: "审计系统自检规则"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
    reason: "§2.7——self_monitoring YAML block + D-020-05"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 9000
timeout_minutes: 55

acceptance_criteria:
  - "heartbeat 60s 定时——写入+读回验证延迟 < 5ms"
  - "连续 3 次 heartbeat 失败 → emergency fallback log 写入"
  - "disk_usage > 80% → P1 告警 / > 90% → P0 阻断"
  - "hash_chain_integrity fail → 立即 P0 阻断"
  - "sqlite_index_health offline > 60s → auto-rebuild 触发"
  - "10 项指标全部可采集——通过 `zephyr audit health` CLI 展示"
  - "5/5 单元测试通过"

rollback_instructions: |
  1. 删除 self_monitor.py 内容
  2. 删除 test_self_monitor.py
  3. 停止任何运行中的 heartbeat 线程

depends_on:
  - "TASK-INF-0209"
  - "TASK-INF-0210"
blocked_by: []

status: "done"

tags_fn:
  - "infra"
  - "observability"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-020"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---

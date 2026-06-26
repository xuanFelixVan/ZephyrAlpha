---
module_id: KE-1709
status: active
title: 2.13 CT-FLE-DB-001：反馈环路 → 数据库 — 评估指标时序持久化
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.13 CT-FLE-DB-001：反馈环路 → 数据库 — 评估指标时序持久化

2.13 CT-FLE-DB-001：反馈环路 → 数据库 — 评估指标时序持久化

```yaml
contract: CT-FLE-DB-001
title: "FLE评估结果→数据库时序存储——为趋势分析和回滚决策提供数据基础"
systems:
  - role: producer
    name: feedback_loop_engine
    path: "src/zephyr/feedback-loop/"
    blueprint: "MOD-FEEDBACK_LOOP"
  - role: consumer
    name: database
    path: "src/zephyr/database/"
    blueprint: "MOD-DATABASE"

data_flow:
  direction: producer_to_consumer
  trigger: "FLE完成一轮 collect→detect 循环后——无论是否有异常"
  payload:
    cycle_id: "string"
    cycle_timestamp: "ISO8601"
    metrics:
      task_throughput: "float — 任务/小时"
      gate_pass_rate: "float — G0-G7通过率 (%)"
      script_failure_rate: "float — 脚本exit≠0比率 (%)"
      ce_latency_p50: "float — CE构建延迟P50 (ms)"
      llm_token_usage: "int — 本周期LLM token消耗"
    anomalies:
      detected: "bool"
      anomaly_type: "enum[PERFORMANCE_DEGRADATION, QUALITY_REGRESSION, SECURITY_ALERT] | null"
      affected_systems: "list[str]"
    action_taken: "enum[NONE, THROTTLE, ROLLBACK, ALERT]"
  action: "db写入 fle_metrics 时序表 → 保留90天 → 90天后归档到 cold_storage"

circuit_breaker:
  db_write_failure: "写入本地SQLite buffer → db恢复后批量重放"
  max_buffer_size_mb: 100

design_rationale: >
  时序数据是FLE趋势分析和自动回滚决策的基础。
  即使当前周期无异常，也必须写入——"无异常"本身就是一个需要记录的信号。

ai_prompt: >
  你是CT-FLE-DB-001的AI agent。当FLE需要持久化/查询数据时：
  (1) telemetry_event表主写路径——FLE自身指标+系统告警事件→幂等写入（natural_key去重）；
  (2) anomaly_record表——每次ESCLATE时的诊断快照`snap_{timestamp}`，诊断结束后自动清理；
  (3) audit_log表不可变追加（DD11）——不要UPDATE或DELETE已有审计记录；
  (4) emergency_log表——retry 3次仍失败后的fallback，写入后告警，恢复后自动回放；
  (5) 查询用read_replica（如配置），写入用primary——不要反向；
  (6) 熔断打开时写入本地SQLite buffer→不要因为DB不可用就丢失数据；
  (7) max_buffer_size_mb=100——超过上限按FIFO丢弃最旧数据并告警。

telemetry:
  metrics:
    - {name: "fle_db_write_latency_ms", type: histogram, buckets: [1,5,10,50,100]}
    - {name: "fle_db_read_latency_ms", type: histogram, buckets: [1,5,10,50,100]}
    - {name: "fle_db_fallback_buffer_usage", type: gauge}
  traces:
    required_spans: ["fle_write_metrics", "fle_read_metrics", "fle_write_audit"]
```

---

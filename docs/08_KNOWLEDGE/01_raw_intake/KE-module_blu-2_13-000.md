---
module_id: KE-module_blu-2_13-000
title: 2.13 可观测性与分布式追踪
category: module_blueprint
---

# 2.13 可观测性与分布式追踪

2.13 可观测性与分布式追踪

> **对标**：OpenTelemetry SpanContext + Jaeger/Zipkin Correlation ID + Augment Code automated verification。

```yaml
observability:
  # === 分布式追踪 ===
  tracing:
    correlation_id: "每条 A2A Message 携带 correlation_id——全链路唯一标识"
    span_context: "每次 Agent 间消息传递创建 Span（span_id + parent_span_id）"
    storage: "docs/09_audit/A2A_TRACES/{correlation_id}.yaml——全链路事后回溯"

  # === A2A 专属指标 ===
  metrics:
    - name: "message_latency_p95_ms"
      target: "≤ 200 ms"
      description: "Agent 间单条消息延迟"

    - name: "handoff_time_p95_ms"
      target: "≤ 5000 ms"
      description: "任务从 SUBMITTED → WORKING 的时间（含 Agent Card 匹配）"

    - name: "conflict_resolution_time_p95_ms"
      target: "≤ 120000 ms (2 min)"
      description: "从冲突检测到仲裁完成的时间"

    - name: "delegation_success_rate"
      target: "≥ 95%"
      description: "委托在 SLA 内 COMPLETED 的比例"

    - name: "deadlock_event_count_per_day"
      target: "0"
      description: "每日死锁事件——0 容忍"

    - name: "semantic_conflict_count_per_day"
      target: "≤ 3"
      description: "语义冲突——允许少量但需追踪趋势"

  # === Agent 信誉评分 ===
  reputation:
    tracking: "每个 Agent 的历史成功率 + 平均完成时间 + 语义冲突参与率"
    use: "Coordinator 在 Filter/Score 阶段使用——优先分配给高信誉 Agent"
    decay: "信誉随时间衰减——最新 100 次委托权重 0.7，历史 0.3"
```

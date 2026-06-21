---
module_id: KE-4234----metric-sources-000
title: 9.1 上游 Metric Sources
category: module_blueprint
---

# 9.1 上游 Metric Sources

9.1 上游 Metric Sources

| 上游 | 推送什么 | 频率 |
|------|---------|------|
| **Orchestrator** | `orc.task.duration_ms` / `orc.task.hallucination_rate` / `orc.sandbox.violation_count` / `orc.agent.throughput` | 每任务完成时 + 每分钟聚合 |
| **VMS** | `vms.search.hit_rate` / `vms.search.latency_ms` / `vms.ingest.count` / `vms.degrade_events` | 每查询 + 每分钟聚合 |
| **Context Engine** | `ce.slot.hit_rate.<slot>` / `ce.build.latency_ms` / `ce.compress.ratio` / `ce.degrade_events` | 每 build 完成 |
| **LSG** | `lsg.prompt_injection.bypass_rate` / `lsg.output_schema.reject_rate` / `lsg.secret_leak.events` | 每拦截事件 |

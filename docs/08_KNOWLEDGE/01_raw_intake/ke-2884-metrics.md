---
module_id: KE-2784
status: active
title: metrics —— 四类指标，统一接口
category: module_blueprint
---

# metrics —— 四类指标，统一接口

metrics —— 四类指标，统一接口
telemetry.metrics.gauge("cpu_usage", 45.2, labels={"host": "main"})
telemetry.metrics.counter("llm_calls_total", 1, labels={"model": "gpt-4"})
telemetry.metrics.histogram("llm_api_latency_ms", 320.0, labels={"model": "gpt-4"})
telemetry.metrics.summary("user_perceived_latency_ms", 500.0)

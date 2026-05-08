---
module_id: KE-module_blu-otel_genai_metrics-000
title: OTel GenAI Metrics 对齐
category: module_blueprint
---

# OTel GenAI Metrics 对齐

OTel GenAI Metrics 对齐

| OTel GenAI Metric | Telemetry SLI 对应 | 说明 |
|-------------------|-------------------|------|
| `gen_ai.client.token.usage` (Histogram) | `Token消耗总量` counter | 按 token_type= input/output 区分 |
| `gen_ai.client.operation.duration` (Histogram) | `LLM API 响应时间` histogram | P50/P90/P95/P99 |

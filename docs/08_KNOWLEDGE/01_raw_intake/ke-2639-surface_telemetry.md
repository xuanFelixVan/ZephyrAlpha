---
module_id: KE-2544
status: active
title: AgentTrace 3-Surface Telemetry (D-019-71)
category: module_blueprint
ttl: permanent
---

# AgentTrace 3-Surface Telemetry (D-019-71)

AgentTrace 3-Surface Telemetry (D-019-71)
- **Operational**: method/arguments/return_value/duration_ms/status/exception
- **Cognitive**: prompt/completion/reasoning_segments(model/token_count/temperature)
- **Contextual**: http/sql/nosql/vector_search/fs_io interactions
- eBPF completion: SDK span 32.8%→eBPF 99.1%, latency ~2.4μs
- Dual-Path: Hot(Redis Streams→Grafana 1h) + Cold(Parquet/S3 forensic) + Compliance(Merkle)

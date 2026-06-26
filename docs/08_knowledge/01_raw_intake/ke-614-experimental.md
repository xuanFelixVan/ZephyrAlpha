---
module_id: KE-552------experimental-000
status: active
title: 9.2 关键字段（experimental 必采）
category: documentation
ttl: permanent
doc_type: knowledge_entry
---

# 9.2 关键字段（experimental 必采）

9.2 关键字段（experimental 必采）

每条审计记录 **至少包含**：

- `event_id`（UUID v4）
- `timestamp`（UTC RFC3339 纳秒）
- `event_type`（枚举：`llm_call` / `agent_action` / `secret_alert` / `sandbox_violation` / `auth_event`）
- `actor`（`human:owner` / `agent:cursor` / ...）
- `resource`（受影响资源路径 / service ID）
- `result`（`allow` / `deny` / `degraded`）
- `reason`（策略命中 ID / 异常原因）
- `input_hash` + `output_hash`（SHA-256，防篡改）
- `request_id`（跨服务链路追踪）

---
module_id: KE-2830
title: Phase 0 — 基础设施管控契约优先（新增）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# Phase 0 — 基础设施管控契约优先（新增）

Phase 0 — 基础设施管控契约优先（新增）

| 任务 | 优先级 |
|------|:---:|
| `CT-HEALTH-001` — 三态探针端点 `/healthz/livez/readyz` 实现 | **P0** |
| `CT-STARTUP-001` — 冷启动顺序与依赖就绪机制 | **P0** |
| `CT-CBAC-001` — capability_check() 防篡改checksum机制 | **P0** |
| `CT-BACKUP-001` — 每日自动备份sqlite+chromadb | **P1** |
| `CT-CONFIG-001` — 配置统一管理与校验 | **P1** |
| `CT-DLQ-001` — 死信队列sqlite表+replay触发 | **P1** |

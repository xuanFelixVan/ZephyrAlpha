---
module_id: KE-1954
status: active
title: 2.9 CT-ORC-VMS-001：任务系统 → 向量记忆 — 任务输出写入向量库
category: module_blueprint
ttl: permanent
---

# 2.9 CT-ORC-VMS-001：任务系统 → 向量记忆 — 任务输出写入向量库

2.9 CT-ORC-VMS-001：任务系统 → 向量记忆 — 任务输出写入向量库

```yaml
contract: CT-ORC-VMS-001
title: "任务产出写入向量记忆——持久化检索入口"
systems:
  - role: producer
    name: orchestrator
    path: "src/zephyr/orchestrator/"
    blueprint: "MOD-TASK_SYSTEM"
  - role: consumer
    name: vector_memory_system
    path: "src/zephyr/vector-memory/"
    blueprint: "MOD-INF-011"

data_flow:
  direction: producer_to_consumer
  trigger: "TaskCard.status → COMPLETED 且 output_type ∈ {CODE, DOCUMENT, ANALYSIS}"
  payload:
    task_id: "string — TaskCard.task_id"
    output_summary: "string — 任务产出的250字摘要"
    output_blocks: "list[OutputBlock] — 按segment分块的原始产出"
    embedding_hint: "enum[DENSE, SPARSE, HYBRID] — 建议的向量化策略"
    tags: "list[str] — 从TaskCard.tags继承"
  action: "VMS写入向量库 → 更新 TaskCard.vector_refs 字段"

quality_control:
  max_blocks_per_task: 50
  min_block_length: 100
  dedup_strategy: "content_hash → 已有hash则skip"
  retry_on_failure: 3

circuit_breaker:
  failure_threshold: 10
  recovery_after_seconds: 120
  fallback: "写入本地SQLite队列 → VMS恢复后批量回放"

ai_prompt: >
  你是CT-ORC-VMS-001的AI agent。当Orc的任务产出(CODE/DOCUMENT/ANALYSIS)需要持久化到向量库时：
  (1) 仅当TaskCard.status=COMPLETED且output_type∈{CODE,DOCUMENT,ANALYSIS}时触发写入；
  (2) 每个任务最多写入50个output block，每个block最短100字符——避免碎片化；
  (3) content_hash去重——相同hash的block不重复写入；
  (4) 熔断触发(failure≥10)后，fallback写入本地SQLite队列→不要丢失任务产出；
  (5) VMS恢复后自动回放SQLite队列——回放完成后更新TaskCard.vector_refs字段；
  (6) retry 3次后仍失败→标记TaskCard.vector_refs="write_deferred"，不阻塞任务完成。

telemetry:
  metrics:
    - {name: "orc_vms_write_count", type: counter, labels: [output_type]}
    - {name: "orc_vms_write_latency_ms", type: histogram, buckets: [10,50,100,500,1000]}
    - {name: "orc_vms_dedup_hit_rate", type: gauge}
    - {name: "orc_vms_circuit_open", type: gauge}
  traces:
    required_spans: ["orc_complete_task", "vms_write_vector", "vms_update_taskcard"]
```

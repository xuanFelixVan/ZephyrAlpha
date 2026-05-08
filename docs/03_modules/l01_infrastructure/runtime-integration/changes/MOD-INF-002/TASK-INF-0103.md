---
task_id: "TASK-INF-0103"
source_blueprint: "MOD-INF-002"
source_section: "蓝图 §2 Cross-Layer 缺口 RL-001/006/010/012/022/023/029/033/042 + §5.5 填补方案表"
title: "Phase 1b 通信就绪缺口填补——RL-001/004/006/010/012/022/023/029/033/042"
description: |
  填补 Phase 1b 涉及的 Cross-Layer 缺口。
  RL-001 跨层通信→EventBus pub/sub+consumer group（P99<100ms）+
  RL-004 Telemetry→structlog聚合+基数限制（≤500 per-module）+超限LRU淘汰+告警+
  RL-006 事件类型→Pydantic类型化+Schema兼容校验（mypy 100%）+
  RL-010 背压→EventBus BackpressureController（队列>80%→背压）+
  RL-012 死信队列→EventBus DLQ(SQLite持久化)+指数退避重试+
  RL-022 消息语义→DeliverySemantics: AT_LEAST_ONCE(默认)+
  RL-023 背压传导→BackpressurePropagation协议（下游队列>80%→上游减速）+
  RL-029 DLQ持久化→SQLite持久化表（进程重启不丢）+
  RL-033 基数语义→per-module 500；超限→LRU淘汰+告警+
  RL-042 Schema兼容→FULL_BACKWARD / FORWARD_TRANSITIVE。
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\observer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\events\\event_schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\events\\dlq.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\metrics.py"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\events\\priority_queue.py"
    description: "四级优先级队列——CRITICAL/HIGH/NORMAL/LOW + DeliverySemantics 枚举"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\events\\backpressure.py"
    description: "背压传导链——BackpressurePropagator + BackpressureSignal"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\prompt_fingerprint.py"
    description: "PromptFingerprint——所有LLM调用标记+覆盖率100%"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\dead_module_detector.py"
    description: "DeadModuleDetector——30天DORMANT/60天DEAD/90天归档"
  - path: "D:\\ZephyrAlpha\\config\\event_bus.yaml"
    description: "事件类型/Schema/DLQ策略/DeliverySemantics/Priority配置"
  - path: "D:\\ZephyrAlpha\\config\\schema_evolution_policy.yaml"
    description: "Schema兼容性策略：FULL_BACKWARD / FORWARD_TRANSITIVE"
  - path: "D:\\ZephyrAlpha\\tests\\shared\\test_priority_queue.py"
    description: "优先级队列单元测试"
  - path: "D:\\ZephyrAlpha\\tests\\shared\\test_backpressure.py"
    description: "背压传导链单元测试+压测"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\events\\priority_queue.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\events\\backpressure.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\prompt_fingerprint.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\production\\dead_module_detector.py"
  - "D:\\ZephyrAlpha\\config\\event_bus.yaml"
  - "D:\\ZephyrAlpha\\config\\schema_evolution_policy.yaml"
  - "D:\\ZephyrAlpha\\tests\\shared\\test_priority_queue.py"
  - "D:\\ZephyrAlpha\\tests\\shared\\test_backpressure.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\observer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\events\\event_schemas.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\events\\dlq.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
  - module_id: "MOD-INF-002"
    section: "§5.3 DeliverySemantics 代码骨架"
    reason: "消息传递语义枚举——AT_MOST_ONCE/AT_LEAST_ONCE/EXACTLY_ONCE"
  - module_id: "MOD-INF-002"
    section: "§5.3 BackpressurePropagation 代码骨架"
    reason: "背压传导信号协议——warning(80%)/critical(95%)"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
    reason: "本蓝图——§2 RL缺口定义、§5.3 代码骨架(DeliverySemantics/BackpressurePropagation/PriorityQueue)、§5.5 填补方案表"
  - file_path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\observer.py"
    reason: "现有 EventBus Pub/Sub 基类——了解扩展点"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
estimated_tokens: 28000
timeout_minutes: 60
acceptance_criteria:
  - "跨层消息延迟 P99 ≤ 100ms（RL-001）"
  - "队列 > 80% → 背压信号发出、上游减速因子实时计算（RL-010/023）"
  - "DLQ SQLite 持久化——进程重启后事件可重放（RL-012/029）"
  - "DeliverySemantics 枚举 AT_LEAST_ONCE 为默认——所有消费者按此设计（RL-022）"
  - "Telmetry 标签基数 ≤ 500 per-module，超限→LRU淘汰+告警（RL-004/033）"
  - "Schema 变更零爆炸——FULL_BACKWARD 兼容策略强制执行（RL-042）"
  - "mypy strict 通过率 100%（RL-006）"
  - "PromptFingerprint —— 100% LLM 调用标记"
rollback_instructions: |
  1. 删除新增文件：priority_queue.py / backpressure.py / prompt_fingerprint.py / dead_module_detector.py
  2. 删除新增配置文件：config/event_bus.yaml / config/schema_evolution_policy.yaml
  3. 删除新增测试文件
  4. 如 shared/observer.py 或 shared/events/ 下现有文件被意外修改→git checkout 还原
depends_on:
  - "TASK-INF-0102"
blocked_by: []
status: "created"
tags_fn:
  - "infra"
  - "observability"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-002"
  - "MOD-INF-016"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---

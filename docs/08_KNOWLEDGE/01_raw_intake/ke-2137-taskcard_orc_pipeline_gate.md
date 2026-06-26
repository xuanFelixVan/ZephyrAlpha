---
module_id: KE-2045
status: active
title: 3.1 TaskCard（Orc、Pipeline、Gates、FLE、Script System 共用）
category: module_blueprint
ttl: permanent
---

# 3.1 TaskCard（Orc、Pipeline、Gates、FLE、Script System 共用）

3.1 TaskCard（Orc、Pipeline、Gates、FLE、Script System 共用）

```yaml
schema: SCHEMA-TASKCARD-001
canonical_source: "PS-STD-001 §7.10 + src/zephyr/shared/schemas.py Task"
schema_version: "1.2.0"
version_negotiation:
  ref: "CTR-VER-001（cross_layer_contracts.yaml §versioning_strategy）"
  rules:
    - "v1.x.y 消费者MUST忽略未知可选字段（forward-compat）"
    - "v1→v2 MAJOR变更需Owner审批+30天通知+双版本过渡期"
    - "新增字段默认optional=True，不得删除或修改已有字段类型"
    - "废弃字段标记@deprecated+target_removal_version，保留至少2个MAJOR版本"
  ci_enforcement: "CI扫描SCHEMA-*与磁盘dataclass定义的一致性→不一致=CI FAIL"

fields:
  - name: task_id
    type: str
    format: "{NAMESPACE}-{SEQ}"
    examples: ["MODEL-042", "AUDIT-017", "OPS-003", "KB-INF-0001"]
    namespaces:
      MODEL: "模型构建任务"
      AUDIT: "审计类任务"
      OPS: "运维/修复任务（脚本系统自动创建）"
      KB-INF: "知识库基础设施任务"
  - name: status
    type: enum
    values: [DRAFT, QUEUED, ASSIGNED, RUNNING, REVIEWING, COMPLETED, BLOCKED, CANCELLED, FAILED, ARCHIVED]
    transitions:
      BLOCKED_triggers: [GATE_FAIL, SCRIPT_EXIT_2, SCRIPT_EXIT_3, FLE_ESCALATE]
      BLOCKED_recovery: [GATE_PASS, SCRIPT_EXIT_0, OWNER_UNBLOCK]
  - name: task_type
    type: enum
    values: [MODEL_BUILD, AUDIT, DOC_WRITE, REFACTOR, AUTO_FIX, INFRA]
  - name: priority
    type: enum
    values: [P0, P1, P2, P3]
  - name: execution_model
    type: str
    source: "Pipeline routing output"
  - name: gate_profile
    type: str
    source: "Pipeline routing output"
```

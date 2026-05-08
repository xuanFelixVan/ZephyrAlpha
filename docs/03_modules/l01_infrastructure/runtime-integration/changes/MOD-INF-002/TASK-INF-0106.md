---
task_id: "TASK-INF-0106"
source_blueprint: "MOD-INF-002"
source_section: "蓝图 §2 RL-019/025/045 + §5.4 RI-13 EventStore 设计哲学 + §6.1 Phase 3 + §11.1"
title: "Phase 3 溯源增强缺口填补——RL-019/025/045 + RI-13 EventStore ES+CQRS+快照+Crypto-Shredding"
description: |
  触发式 Phase 3——当模块数 > 100 或首次合规/审计需求触发。
  RL-019 事件溯源→EventStore ES+CQRS：append-only event_log + 快照表（每1000事件）+
  CQRS读模型（物化视图+聚合视图）+ 恢复延迟 < 500ms+
  RL-025 时间旅行隔离→replay_to() write_mode: READ_ONLY——重放期间0写入冲突+
  RL-045 Crypto-Shredding→per-stream密钥=删除密钥=不可读（GDPR就绪）。
  §5.4 触发式渐进引入策略：Phase 3仅对 L04(风控)/L05(交易)/L06(仓位) 三层切 Event Sourcing。
  独立落地文件：event_store.py
priority: "P2"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\core\events\event_store.py"
    description: "RI-13 EventStore——append-only event_log+快照+CQRS读模型+replay_to隔离+CryptoShredding"
  - path: "D:\\ZephyrAlpha\\tests\\l01_infrastructure\\test_event_store.py"
    description: "EventStore 单元测试——快照恢复+重放+Shred验证"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\event_store.py"
  - "D:\\ZephyrAlpha\\tests\\l01_infrastructure\\test_event_store.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
applicable_rules:
  - module_id: "MOD-INF-002"
    section: "§5.3 CryptoShredding / SagaCoordinator 代码骨架"
    reason: "CryptoShredding: per-stream AES密钥→删密钥=不可恢复; SagaCoordinator: Phase 4触发"
  - module_id: "MOD-INF-002"
    section: "§5.2"
    reason: "ImmutableEvents——事件不可修改/不可删除——审计完整性不可妥协"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
    reason: "本蓝图——§5.4 EventStore设计哲学、§5.3 CryptoShredding/SagaCoordinator 代码骨架、§6.1 Phase 3"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
estimated_tokens: 20000
timeout_minutes: 60
acceptance_criteria:
  - "事件不可变——append-only event_log 表（RL-019）"
  - "快照恢复延迟 < 500ms——每 1000 事件快照（RL-019）"
  - "replay_to() 写隔离——重放期间 0 写入冲突（RL-025）"
  - "Crypto-Shredding: 删除密钥后 0 条事件可解密（RL-045）"
  - "仅 L04/L05/L06 三层切 Event Sourcing"
rollback_instructions: |
  1. 删除 event_store.py
  2. 删除测试文件
  3. 如果 l01_infrastructure/ 目录仅剩此文件→删除目录
depends_on: []
blocked_by: []
status: "done"
tags_fn:
  - "infra"
  - "data"
  - "security"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "experimental"
tags_mo:
  - "MOD-INF-002"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---

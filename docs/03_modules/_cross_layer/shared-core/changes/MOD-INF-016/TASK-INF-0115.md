---
task_id: "TASK-INF-0115"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §7 集成目标 + §7.1 反向依赖索引"

title: "§7 集成目标验证——反向依赖索引维护与模块消费矩阵审计"
description: |
  验证蓝图 §7 的集成声明与实际代码依赖一致。
  §7.1 反向依赖索引：列出 Shared+Core 的 12 个 consumer 模块及其消费的 shared 子模块：
  ① MOD-INF-012 Database→shared/schemas+ssot_guard+lifecycle
  ② MOD-INF-008 ContextEngine→shared/schemas+ssot_guard+lifecycle+resilience+flags+API_INDEX
  ③ MOD-INF-009 Pipeline→shared/schemas+ssot_guard+lifecycle+resilience+events+dlq
  ④ MOD-INF-007 GateEngine→shared/schemas+ssot_guard+lifecycle+instrument
  ⑤ MOD-INF-010 FeedbackLoop→shared/schemas+ssot_guard+observer+metrics
  ⑥ MOD-KB-001 KnowledgeBase→shared/contracts（+ events/dlq 扩展）
  ⑦ MOD-INF-013 MCPServers→shared/schemas+ssot_guard+content_fingerprint
  ⑧ MOD-INF-014 LLMSecurity→shared/schemas+ssot_guard+instrument+observer+metrics
  ⑨ MOD-INF-002 RuntimeIntegration→shared/schemas+ssot_guard+instrument+metrics
  ⑩ MOD-INF-017 CodeDedupEngine→shared/schemas+ssot_guard
  ⑪ MOD-INF-019 AgentSpec→shared/contracts（+ schemas 扩展）
  ⑫ shared/contracts/——契约扩展点：instrument, money, timestamp, runtime_plane_tag 四大契约均可被消费拓展。
  每个 consumer 的契约必须被集成测试覆盖（pytest test_import_chain.py）。
  专业对标：Backstage Catalog API + Google BUILD deps graph + ZephyrAlpha auto_contract_tester。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\tests\\test_import_chain.py"
  - "D:\\ZephyrAlpha\\tests\\test_auto_contract_tester.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\changes\\MOD-INF-016\\TASK-INF-0115.md"
    description: "本任务卡——§7 集成审计执行记录"

allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\changes\\MOD-INF-016\\TASK-INF-0115.md"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\**\\*.py"
  - "D:\\ZephyrAlpha\\tests\\test_import_chain.py"
  - "D:\\ZephyrAlpha\\tests\\test_auto_contract_tester.py"

applicable_rules:
  - module_id: "GOV-DOC-002"
    section: "§5.5"
    reason: "跨层集成——_cross_layer 模块被 ≥2 个蓝图层消费"
  - module_id: "PS-STD-001"
    section: "§5.1.1"
    reason: "API_INDEX.py——消费者 import 清单"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    reason: "本蓝图 §7——12 消费者索引声明"
  - file_path: "D:\\ZephyrAlpha\\tests\\test_import_chain.py"
    reason: "test_import_chain.py——反向依赖集成测试"

assigned_model: "glm-5.1"
assigned_pipeline: "B"
pipeline_modules:
  - "M3"
estimated_tokens: 10000
timeout_minutes: 25

acceptance_criteria:
  - "§7.1 中声明的 12 个 consumer 模块在代码库中存在（对已实现模块验证路径存在）"
  - "每个 consumer 的 import 清单与 API_INDEX.py 一致"
  - "pytest tests/test_import_chain.py -v 全部通过——无 broken import"
  - "未启动模块的消费者声明正确标注 [PLANNED] 状态"
  - "模块消费矩阵与 §7.1 反向依赖索引保持一致"

rollback_instructions: |
  本任务为只读审计。发现不一致时仅记录审计发现，不修改任何文件。

depends_on: ["TASK-INF-0113"]
blocked_by: []

status: "done"

tags_fn:
  - "infra"
tags_ly: "cross_layer"
tags_md: "glm-5.1"
tags_st: "active"
tags_mo:
  - "MOD-INF-016"

completed_gates: []
blocked_gates: {}

artifact_paths: []

audit_findings: []

ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---

---
task_id: "TASK-KB-0002"
source_blueprint: "MOD-KB-001"
source_section: "§2 必备链接+依赖声明"

title: "MOD-KB-001 依赖声明验证——确认所有接口依赖方蓝图存在且契约对齐"
description: |
  验证蓝图 §2 中声明的必备链接和依赖关系：(1)确认 b_kb.yaml 选址正确且与其他架构 YAML 无冲突；(2)验证跨层契约 CTR-001~CTR-006 在各自蓝图中的接口定义与本蓝图消费方接口一致；(3)确认 context_assembler (MOD-INF-006 §5.1)、gate_engine (MOD-INF-007)、feedback_loop (MOD-INF-010)、vector_memory (MOD-INF-011) 等依赖方蓝图的集成点仍有效；(4)依赖声明自洽性检查——无循环依赖、无缺失引用。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\target-architecture\\architecture-model\\b_kb.yaml"
  - "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\target-architecture\\architecture-model\\_index.yaml"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\context-engine\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\gate-engine\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\feedback-loop\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    description: "如需修正依赖声明中的漂移项——仅更新 §2 和 §6.1 接口表"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\changes\\MOD-KB-001\\dependency-verification-report.md"
    description: "依赖验证报告——逐依赖标注状态（OK/MISMATCH/MISSING）"

allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\changes\\MOD-KB-001\\dependency-verification-report.md"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\**\\*.py"
  - "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\**\\*.yaml"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\context-engine\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\gate-engine\\blueprint.md"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "task_id 编号格式"
  - module_id: "MOD-INF-006"
    section: "§5.1"
    reason: "context_assembler 集成点定义"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\knowledge-base\\blueprint.md"
    reason: "§2 本蓝图依赖声明——需要验证的目标"
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\context-engine\\blueprint.md"
    reason: "context_assembler 对 KB 的接口期望"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 8000
timeout_minutes: 30

acceptance_criteria:
  - "所有依赖方蓝图路径在磁盘上存在且可读取"
  - "b_kb.yaml 在 _index.yaml b_track 下注册正确"
  - "CTR-001~CTR-006 接口契约在双方蓝图中语义一致"
  - "dependency-verification-report.md 输出——逐依赖标注 OK/MISMATCH/MISSING"
  - "无循环依赖——DAG 深度遍历 ≤ 3"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\knowledge-base\changes\MOD-KB-001\dependency-verification-report.md
  2. 若修改了 blueprint.md §2——git checkout -- docs/03_modules/l01_infrastructure/knowledge-base/blueprint.md

depends_on: ["TASK-KB-0001"]
blocked_by: []
status: "done"
tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-KB-001"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---

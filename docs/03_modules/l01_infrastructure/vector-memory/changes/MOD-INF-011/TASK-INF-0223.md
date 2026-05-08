---
task_id: "TASK-INF-0223"
source_blueprint: "MOD-INF-011"
source_section: "§4 施工 Phase 规划 + depends_on 全链路"

title: "依赖关系全链路验证——MOD-INF-011 下游 6 个 depends_on 目标 + 上游消费方 compatibility gate"
description: |
  验证蓝图 depends_on 字段中声明的 6 个依赖目标的完整性：
  1. MOD-MASTER-001 (§2.6): CT-CE-VMS-001 集成契约——CE→VMS 向量检索契约是否已具备 calling 条件
  2. MOD-KB-001 (§1.5): 知识库——beta VMS 整合目标，KE 写入接口已就绪
  3. MOD-INF-008 (§2.1): CE——VMS 的主要消费方，context_assembler.py 是否有 VMS.search() import
  4. architecture-model/layers/b_vector_memory.yaml: VMS YAML SSoT——是否与本蓝图 §2 8Collection 一致
  5. ADR-0016 (§3): VMS 生产级嵌入与分块契约——BGE-M3 1024d 规范是否可作为实现真源
  6. ADR-0031 (§4.2): Phase 2 ChromaDB 基线选型——kb/ 4+1 Collection 现有实现是否完整可用
  同时验证 upstream 间接依赖：MOD-INF-010 (FLE) 的检索反馈 call path 闭合
  生成 DependencyValidationReport YAML
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\context-engine\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\feedback-loop-engine\\blueprint.md"
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_vector_memory.yaml"
  - "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\adr\\adr-0016-embedding-and-chunking-contract.md"
  - "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\adr\\adr-0031-chromadb-vector-retrieval.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\kb\\chromadb_init.py"

downstream_outputs:
  - path: "D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\vector-memory\changes\dependency-validation-report.yaml"
    description: "VMS 依赖全链路验证报告——6 个 upstream 依赖的存在性/可用性/阻塞性评估 + 4 个下游消费者 readiness check"

allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\changes\\MOD-INF-011\\dependency-validation-report.yaml"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\**\\*.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_vector_memory.yaml"
  - "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\adr\\**\\*.md"

applicable_rules:
  - module_id: "GOV-DOC-002"
    section: "§5.1.2"
    reason: "路径合规——产出的报告存放在 changes/MOD-INF-011/ 下"
  - module_id: "PS-STD-011"
    section: "MTH-012"
    reason: "涌现式设计——依赖链路验证不破坏已有依赖结构"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
    reason: "depends_on 字段——6 个上游依赖模块/ADR/YAML SSoT 的完整 target 和 at/why 定义"
  - file_path: "D:\\ZephyrAlpha\\architecture-model\\layers\\b_vector_memory.yaml"
    reason: "VMS SSoT——验证 Collection 定义与蓝图 §2 一致性"

assigned_model: "deepseek"
assigned_pipeline: "B"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 8000
timeout_minutes: 30

acceptance_criteria:
  - "dependency-validation-report.yaml 包含 6 个 depends_on 目标的条目——target/module_id/status/exists/blocking/readiness_comment"
  - "b_vector_memory.yaml Collection 列表与本蓝图 §2 的 8 Collection 一一对应——差异 = 阻塞"
  - "CE blueprint (MOD-INF-008) CT-CE-VMS-001 引用已 active——ready"
  - "kb/ chromadb_init.py 可 import→PersistentClient 可连接→readiness OK"
  - "ADR-0031 内容明确提及 ChromaDB 0.6 + 8 Collection——无矛盾"
  - "任何阻塞性依赖缺失 → report status=BLOCKED + 建议下一步动作"

rollback_instructions: |
  1. 删除 dependency-validation-report.yaml（只读报告——删除不会破坏任何内容）
  2. 如报告标记了 fake positive (误判 REAL conflict as false) → 人工复审 + 更新报告

depends_on:
  - "TASK-INF-0211"
blocked_by: []
status: "done"

tags_fn:
  - "infra"
  - "governance"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-011"

completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---

---
task_id: "TASK-INF-0211"
source_blueprint: "MOD-INF-011"
source_section: "§9 需要更新的相关内容"

title: "跨文件内容一致性更新——6 个外部文件的引用同步"
description: |
  执行蓝图 §9 定义的 6 个外部文件的引用同步更新：
  1. blueprint-registry.yaml: 版本号 0.7.0 + P0 → 蓝图 status 已从 Draft 到 active
  2. module-id-registry.yaml: VMS 模块状态 active + 版本 0.7.0
  3. CE 蓝图 (context-engine/blueprint.md): CT-CE-VMS-001 集成状态标记 active——VMS 接口已定义
  4. b_vector_memory.yaml SSoT: 从本蓝图 v0.7.0 反向同步——8 Collection 确认 + 双嵌入维度 + Phase 0-4 状态同步
  5. ADR-0031: 添加注释 "已通向 VMS v0.7.0 8 Collection"——消除 ADR 与蓝图 Collection 数量不一致
  6. tech-stack.yaml: TECH-04/TECH-05 更新双嵌入维度——新增 bge-small-zh-v1.5 轻量路径
  本任务执行前必须确认所有目标文件当前状态（read-before-write），仅追加/更新必要字段不破坏已有内容。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\blueprint-registry.yaml"
  - "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\target-architecture\\architecture-model\\module-id-registry.yaml"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\context-engine\\blueprint.md"
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_vector_memory.yaml"
  - "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\adr\\adr-0031-chromadb-vector-retrieval.md"
  - "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\target-architecture\\architecture-model\\technology\\vibe-coding-infrastructure-tech-stack.yaml"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\blueprint-registry.yaml"
    description: "MOD-INF-011 条目：版本 0.7.0 + status active"
  - path: "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\target-architecture\\architecture-model\\module-id-registry.yaml"
    description: "MOD-INF-011 条目：status active + 版本 0.7.0"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\context-engine\\blueprint.md"
    description: "CT-CE-VMS-001 契约引用：集成状态 active / 已对接到 VMS v0.7.0"
  - path: "D:\\ZephyrAlpha\\architecture-model\\layers\\b_vector_memory.yaml"
    description: "反向同步：8 Collection + 双嵌入维度 + Phase 0-4 状态"
  - path: "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\adr\\adr-0031-chromadb-vector-retrieval.md"
    description: "追加注释：已通向 VMS v0.7.0 8 Collection"
  - path: "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\target-architecture\\architecture-model\\technology\\vibe-coding-infrastructure-tech-stack.yaml"
    description: "TECH-04/TECH-05 更新：新增 bge-small-zh-v1.5 轻量嵌入路径"

allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\blueprint-registry.yaml"
  - "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\target-architecture\\architecture-model\\module-id-registry.yaml"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\context-engine\\blueprint.md"
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_vector_memory.yaml"
  - "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\adr\\adr-0031-chromadb-vector-retrieval.md"
  - "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\target-architecture\\architecture-model\\technology\\vibe-coding-infrastructure-tech-stack.yaml"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\**\\*.py"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\**\\*.md"

applicable_rules:
  - module_id: "PS-STD-011"
    section: "MTH-012"
    reason: "涌现式设计——关联文档更新不影响原始设计决策"
  - module_id: "GOV-DOC-002"
    section: "§5.1.2"
    reason: "路径映射——确认所有更新文件路径合规"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\vector-memory\\blueprint.md"
    reason: "§9 需更新的相关内容表——6 个文件/更新内容/更新原因完整定义"
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\blueprint-registry.yaml"
    reason: "当前注册表状态——确认 MOD-INF-011 现有条目结构"
  - file_path: "D:\\ZephyrAlpha\\architecture-model\\layers\\b_vector_memory.yaml"
    reason: "VMS SSoT——当前结构下的 Collection 定义 + Phase 状态"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
estimated_tokens: 8000
timeout_minutes: 30

acceptance_criteria:
  - "blueprint-registry.yaml 中 MOD-INF-011 version: 0.7.0 + status: active"
  - "module-id-registry.yaml 中 MOD-INF-011 version: 0.7.0 + status: active"
  - "context-engine/blueprint.md 中 CT-CE-VMS-001 引用标注 'active, VMS v0.7.0'"
  - "b_vector_memory.yaml 中 Collection 数量确认为 8 + 双嵌入维度模型路径完整"
  - "adr-0031 末尾追加注释 '# MOD-INF-011 v0.7.0: 已通向 8 Collection VMS 体系'"
  - "tech-stack.yaml 中 TECH-04/TECH-05 嵌入模型列表包含 bge-small-zh-v1.5"
  - "所有更新为追加/修改模式——不删除已有合法内容"

rollback_instructions: |
  1. 每个文件更新前用 git stash（如已追踪）保留原始版本
  2. 如已提交：git revert 对应 commit
  3. 如未追踪：从备份恢复（建议在更新前手动 cp 备份）
  4. 逐文件回滚——单个文件的更新失败不影响其他文件

depends_on:
  - "TASK-INF-0201"
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

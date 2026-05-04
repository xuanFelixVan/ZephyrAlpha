---
task_id: "TASK-INF-0002"
source_blueprint: "MOD-INF-006"
source_section: "§11.3 步骤2"

# ===== 内容 =====
title: "同步 task_completion_gate.py（G7 门禁）"
description: "| 产出位置 | `D:\ZephyrAlpha\src\zephyr\gates\task_completion_gate.py` |
|---------|------|
| 验收标准 | ① G7 完整度检查逻辑已加入；② GateLevel 枚举含 G7（在 G0 之后、G1 之前）；③ check_gate("G7") 返回正确结果 |

**创建/更新文"
priority: "P1"

# ===== 上游：执行前必须读取的文件 =====
upstream_files:
  - "D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\task-system\blueprint.md"

# ===== 下游：执行后必须产出的文件 =====
downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\gates\task_completion_gate.py"
    description: "同步 task_completion_gate.py（G7 门禁）"

# ===== 范围：允许和禁止触碰的文件 =====
allowed_touch:
  - "D:\ZephyrAlpha\src\zephyr\gates\task_completion_gate.py"
forbidden_touch:
  - "D:\ZephyrAlpha\docs\01_policies_and_standards\**\*.md"
  - "D:\ZephyrAlpha\docs\03_modules\**\blueprint.md"

# ===== 规则：必须遵守的治理规则 =====
applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号格式"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
  - module_id: "PS-STD-011"
    section: "MTH-013"
    reason: "路径架构合规创建"

# ===== 上下文：执行前必须装配进上下文的所有文件 =====
context_assembly_manifest:
  - file_path: "D:\ZephyrAlpha\docs\03_modules\l01_infrastructure\task-system\blueprint.md"
    reason: "本蓝图——了解完整架构和施工步骤"

# ===== 资源 =====
estimated_tokens: 8000
timeout_minutes: 30

# ===== 验收标准 =====
acceptance_criteria:
  - ""

# ===== 回滚 =====
rollback_instructions: "删除本步骤新建的文件，恢复修改的文件。具体：D:\ZephyrAlpha\src\zephyr\gates\task_completion_gate.py"

# ===== 依赖 =====
depends_on: ["TASK-INF-0001"]
blocked_by: []

# ===== 状态 =====
status: "created"

# ===== 五轴标签 =====
tags_fn: ["infra"]
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo: ["MOD-INF-006"]

# ===== 门禁 =====
completed_gates: []
blocked_gates: {}

# ===== 执行 =====
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1", "M3"]

# ===== 产物/审计/知识 =====
artifact_paths: []
audit_findings: []
ke_entries: []

# ===== AI 自治 =====
ai_autonomy_level: "supervised"
autonomy_checklist: []
---

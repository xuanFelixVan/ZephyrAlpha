---
task_id: "TASK-GOV-0016"
source_blueprint: "DOM-GOV-001"
source_section: "蓝图 §6 风险 R1——当前施工始终 0%，缺乏 Phase 0 真相"

# ===== 内容 =====
title: "风险 R1 缓解：建立治理域 Phase 0——8 模块蓝图与契约落地为最小可用实现"
description: |
  缓解 DOM-GOV-001 §6 风险 R1："按目前速度，各模块始终 0% 施工——缺乏 Phase 0 落地推动"。
  缓解策略：
  1. 本治理域已为 8 个模块定义了 Phase 0 集成契约（G-CT-001~008）
  2. 本任务卡确保全部 8 个模块均有 Phase 0 最小实现：契约接口定义 + 骨架代码 + 集成测试 stub
  3. 构建 domain_progress.json——治理域实时施工进度看板（每个 Phase 门禁通过后更新）
  4. 蓝图 materialized 判定：TASK-GOV-0010~0013 全部完成时 R1 风险降级为 LOW
priority: "P0"

# ===== 上游：执行前必须读取的文件 =====
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\_domain-governance\\changes\\DOM-GOV-001\\TASK-GOV-0010.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\_domain-governance\\changes\\DOM-GOV-001\\TASK-GOV-0011.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\_domain-governance\\changes\\DOM-GOV-001\\TASK-GOV-0012.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\_domain-governance\\changes\\DOM-GOV-001\\TASK-GOV-0013.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

# ===== 下游：执行后必须产出的文件 =====
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\domain_progress.json"
    description: "治理域实时施工进度看板——Phase 门禁状态 + 各模块进度百分比"
  - path: "D:\\ZephyrAlpha\\scripts\\governance\\update_progress.py"
    description: "进度更新脚本——门禁通过后更新 domain_progress.json"

# ===== 范围：允许和禁止触碰的文件 =====
allowed_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\domain_progress.json"
  - "D:\\ZephyrAlpha\\scripts\\governance\\update_progress.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\**\\*.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"

# ===== 规则：必须遵守的治理规则 =====
applicable_rules:
  - module_id: "DOM-GOV-001"
    section: "§6 R1"
    reason: "风险 R1——0% 施工缺乏 Phase 0 真相"
  - module_id: "GOV-DOC-002"
    section: "§四"
    reason: "进度追踪——B 轨模块需定期更新施工进度"

# ===== 上下文：执行前必须装配进上下文的所有文件 =====
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_domain-governance\\blueprint.md"
    reason: "§6 R1——风险定义与缓解策略"
  - file_path: "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
    reason: "ModuleID→施工状态真源"

# ===== 执行 =====
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M3"
  - "M5"
estimated_tokens: 8000
timeout_minutes: 20

# ===== 验收标准 =====
acceptance_criteria:
  - "domain_progress.json 已创建——含全部 8 模块的 module_id/phase/current_progress/status"
  - "domain_progress.json 结构：{ 'modules': [ { 'module_id': 'MOD-INF-XXX', 'phase': N, 'progress': P, 'status': '...' } ] }"
  - "update_progress.py 可运行——读取 Phase 门禁测试结果后更新 progress 字段"
  - "Phase 1-4 门禁全部通过后 R1 自动降级——progress.json 中 risk_r1: LOW"
  - "回滚方案：删除新创建的 2 个文件"

# ===== 回滚 =====
rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\docs\03_modules\_domain-governance\domain_progress.json
  2. 删除 D:\ZephyrAlpha\scripts\governance\update_progress.py

# ===== 依赖 =====
depends_on:
  - "TASK-GOV-0001"
blocked_by: []

# ===== 状态 =====
status: "done"

# ===== 五轴标签 =====
tags_fn:
  - "observability"
tags_ly: "cross_layer"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "DOM-GOV-001"
  - "risk:R1"

# ===== 门禁 =====
completed_gates: []
blocked_gates: {}

# ===== 产物 =====
artifact_paths: []

# ===== 审计 =====
audit_findings: []

# ===== 知识 =====
ke_entries: []

# ===== AI 自治 =====
ai_autonomy_level: "supervised"
autonomy_checklist: []
---

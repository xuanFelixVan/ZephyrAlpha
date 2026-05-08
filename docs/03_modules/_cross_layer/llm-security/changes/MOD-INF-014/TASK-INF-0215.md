---
task_id: "TASK-INF-0215"
source_blueprint: "MOD-INF-014"
source_section: "§14 施工进度 + §15 施工指南 Phase 0-2"
title: "LSG分阶段施工执行——Phase0基础建设+Phase1独立层+Phase2协作层+Phase3可选增强"
description: |
  按蓝图 §14 施工进度表和 §15 施工指南，分4个Phase执行LSG施工。
  Phase 0: 模块骨架+文档+单元测试框架 (P0, 3-5天)
  Phase 1: L0-L5独立层 (P0, 3-5天)
  Phase 2: L6-L7协作层+L8多Agent (P1, 2-3天)
  Phase 3: 沙箱+仪表板+高级功能 (P2, 2-3天, optional)
priority: "P0"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
downstream_outputs:
  - "所有 TASK-INF-0201 到 TASK-INF-0258 对应的代码+测试+文档产出物"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\**\\*"
  - "D:\\ZephyrAlpha\\tests\\llm_security\\**\\*"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\**\\*"
forbidden_touch: []
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\_cross_layer\\llm-security\\blueprint.md"
    reason: "§14+§15完整Phase规划"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1","M3"]
estimated_tokens: 5000
timeout_minutes: 30
acceptance_criteria:
  - "Phase 0: 模块骨架+__init__.py+protocol.py+test fixtures+pre-commit hooks 部署"
  - "Phase 1: L0-L5 六层核心防御代码10天内可运行"
  - "Phase 2: L6-L7协作层+房源集成验证10天内可运行"
  - "Phase 3(Optional): 沙箱+仪表板+高级攻击探测器 可选施工"
  - "每Phase完成后pytest全量通过+pre-commit全量通过"
rollback_instructions: |
  1. 按Phase级别逐一回退产出物
  2. 从Phase 3往前回退至所需状态
depends_on: ["TASK-INF-0201"]
blocked_by: []
status: "created"
tags_fn: ["infra","construction"]
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo: ["MOD-INF-014"]
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---

# 目标

按蓝图施工指南，分 4 个 Phase 有序推进 LSG 施工，确保每阶段产出物可验证、可集成。

## 执行步骤

### Phase 0 (P0, 3-5天)
- 模块目录结构建立 (TASK-INF-0201)
- protocol.py 抽象基类定义
- 单元测试框架 + conftest.py
- pre-commit hooks 部署

### Phase 1 (P0, 3-5天)
- L0-L1-L2-L3-L4-L5 六层核心代码 (TASK-INF-0203~0208)
- injection_patterns.py + secrets.py
- 每层 ≥10 条单元测试

### Phase 2 (P1, 2-3天)
- L6 Observability + L7 Validation (TASK-INF-0209~0210)
- L8 Multi-Agent (TASK-INF-0212)
- 集成测试全量通过

### Phase 3 (P2, 2-3天, Optional)
- L2a Process Sandbox (TASK-INF-0211)
- Streamlit 安全仪表板
- 高级攻击探测器 (Promptware/Side-Channel/Cascading等)

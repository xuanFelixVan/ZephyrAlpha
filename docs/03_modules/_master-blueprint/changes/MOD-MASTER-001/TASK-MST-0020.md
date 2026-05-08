---
task_id: "TASK-MST-0020"
source_blueprint: "MOD-MASTER-001"
source_section: "蓝图 §二十一 外部依赖生命周期——CT-MODEL-REGISTRY-001/CT-DEPS-001"

title: "实现 LLM 模型注册表 + 外部依赖版本锁定升级策略"
description: |
  实现 §二十一 定义的外部依赖生命周期管理：
  (1)CT-MODEL-REGISTRY-001 LLM模型注册表——CT-*契约不写模型名，写能力声明(capability_declaration)；
  6种能力声明(code_generation_elite/standard, audit_reasoning, security_analysis, embedding_text, cheap_fast)×primary+fallback模型；
  (2)CT-DEPS-001 外部依赖版本锁定——pinned 在 pyproject.toml——AI agent 不能自动 pip install --upgrade；
  升级程序：创建 deps-upgrade 分支 → 全量测试(CDC+integration) → Owner dev验证≥24h → 合并。
  Runtime fallback: primary 模型 503/超时→自动切换到 fallback → 最多3个 → 全部失败→degraded。
  CI check: 所有 CT-* 引用 MUST 使用 capability_declaration key——直接引用模型名→CI FAIL。
  Compatibility matrix: tests/integration/test_dependency_compatibility.py。

priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\pyproject.toml"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\model_registry.py"
    description: "模型注册表——CT-MODEL-REGISTRY-001——能力声明→模型名映射+primary/fallback"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\dependency_manager.py"
    description: "依赖管理器——CT-DEPS-001——版本锁定+升级审批+compatibility_matrix"
  - path: "D:\\ZephyrAlpha\\tests\\integration\\test_dependency_compatibility.py"
    description: "依赖兼容矩阵集成测试"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_model_registry.py"
    description: "模型注册表单元测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\model_registry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\orchestrator\\dependency_manager.py"
  - "D:\\ZephyrAlpha\\tests\\integration\\test_dependency_compatibility.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_model_registry.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\pyproject.toml"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

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

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
    reason: "§二十一——CT-MODEL-REGISTRY-001 能力声明+映射 + CT-DEPS-001 锁定+升级策略"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 12000
timeout_minutes: 45

acceptance_criteria:
  - "model_registry.py 注册 6 种能力声明 × (primary + fallback[1..N]) 模型映射"
  - "CT-* 引用 capability_declaration key 而非硬编码模型名 → 直接引用模型名 CI FAIL"
  - "runtime fallback: primary 503/超时 → 自动切换 fallback → max 3 attempts → 全部失败 degraded"
  - "dependency_manager.py 检测 pip install --upgrade 操作 → WARN(需要审批)"
  - "升级程序: deps-upgrade 分支 → 全量测试(CDC+integration) → dev 24h → merge"
  - "Pydantic V2 BaseModel 实现"

rollback_instructions: |
  1. 删除新增的源码文件
  2. 删除新增的测试文件

depends_on: []
blocked_by: []

status: "done"

tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-MASTER-001"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---

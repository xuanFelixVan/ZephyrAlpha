---
task_id: "MOD-INF-008-TASK-011"
task_title: "施工/演进指南实现 — §11.1 ~ §11.3 施工方法论落地"
module_id: "MOD-INF-008"
blueprint_section: "§11 施工/演进指南 (§11.1, §11.2, §11.3)"
status: "backlog"
priority: "P1"
layer: "cross_layer"
assigned_agent: "DeepSeek-V4-Pro"
review_agent: "GLM-4.7"
execution_model: ["DeepSeek-V4-Pro", "GLM-4.7"]
task_type: "CODE_GEN"
estimated_effort_hours: 4
actual_effort_hours: null
deadline: null
depends_on:
  - task_id: "MOD-INF-008-TASK-008"
    why: "演进指南基于 DD 决策的实现"
  - task_id: "MOD-INF-008-TASK-010"
    why: "缺失文件实现关联演进指南 §11.2"
parent_task_id: "MOD-INF-008-TASK-001"
child_task_ids: []
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\intent_parser.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\intent_keyword_mapper.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\doc_compressor.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\intent_parser.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\intent_keyword_mapper.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\vector_bridge.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\task_validator.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\pipeline_orchestrator.py"
tags: ["context-engine", "evolution-guide", "maintenance", "extensibility"]
acceptance_criteria:
  - "AC-001: §11.1 添加新 intent 类型流程文档化: IntentType 枚举 + _MAP 映射 + 运行测试"
  - "AC-002: §11.2 缺失文件实现优先级: P1 vector_bridge.py, P2 task_validator.py, P3 pipeline_orchestrator.py"
  - "AC-003: §11.3 DocCompressor 修改指南: CompressionPolicy Immutable Core (Human-Gated), compress() AI-Modified, 修改后运行 test_doc_compressor.py"
  - "AC-004: intent_parser.py 的 IntentType 枚举有清晰的添加注释指引"
  - "AC-005: intent_keyword_mapper.py 的 _MAP 字典有清晰的添加注释指引"
rollback_instructions: "恢复 intent_parser.py/intent_keyword_mapper.py 中的注释变更，删除演进指南相关代码标记"
context_assembly_manifest:
  required_blueprints:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md §11"
  required_standards: []
  required_templates: []
  required_references: []
---
# MOD-INF-008-TASK-011: 施工/演进指南实现

## 1. Purpose

将 §11 中定义的施工和演进指南在代码中以注释、配置、防护机制的形式落地，确保未来 AI agent 修改 CE 时遵循正确流程。

## 2. §11.1: Adding New Intent Type

流程：
```
1. intent_parser.py IntentType 枚举中添加
2. intent_keyword_mapper.py _MAP 中添加映射
3. 运行 test_intent_parser.py + test_intent_keyword_mapper.py
```

代码要求：IntentType 枚举顶部添加 comment block 描述新增步骤。intent_keyword_mapper.py 的 `_MAP` 字典前添加 comment block 描述新增步骤。

## 3. §11.2: Three Missing Files

| 优先级 | 文件 | 职责 | Connect |
|:---:|------|------|------|
| P1 | vector_bridge.py | CE↔VMS 检索桥接 | CT-CE-VMS-001 |
| P2 | task_validator.py | 任务告警/故障验证 | — |
| P3 | pipeline_orchestrator.py | 多阶段流水线编排 | 已有测试 Ghost |

## 4. §11.3: Modifying DocCompressor

DocCompressor 遵循 CL-018 RI 扩展模式:
- CompressionPolicy 为 Immutable Core (Pydantic frozen) → 修改需 Human-Gated
- compress() 实现可 AI-Modified → 修改后运行 test_doc_compressor.py

## 5. Acceptance Criteria

- intent_parser.py 顶部有 "HOW TO ADD NEW INTENT" comment block
- intent_keyword_mapper.py 顶部有 "HOW TO ADD NEW INTENT KEYWORDS" comment block
- 三个缺失文件的优先级/职责在代码中或配置中记录
- DocCompressor 类前有 "MODIFICATION GUIDE" comment block

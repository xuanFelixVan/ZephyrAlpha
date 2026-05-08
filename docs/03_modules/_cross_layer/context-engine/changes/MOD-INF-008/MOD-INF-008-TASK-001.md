---
task_id: "MOD-INF-008-TASK-001"
task_title: "模块身份与文件骨架搭建 — Context Engine bounded context 初始化"
module_id: "MOD-INF-008"
blueprint_section: "§1 概述与模块定位 (§1.1, §1.2, §1.3) + §4 文件组成 + §10 施工Phase规划"
status: "backlog"
priority: "P0"
layer: "cross_layer"
assigned_agent: "DeepSeek-V4-Pro"
review_agent: "GLM-4.7"
execution_model: ["DeepSeek-V4-Pro", "GLM-4.7"]
task_type: "CODE_GEN"
estimated_effort_hours: 2
actual_effort_hours: null
deadline: null
depends_on:
  - task_id: "MOD-MASTER-001"
    why: "CT-ORC-CE-001 集成契约——Orc→CE上下文构建请求时序"
  - task_id: "MOD-INF-011"
    why: "VMS蓝图——CE的向量检索源"
  - task_id: "MOD-INF-014"
    why: "LSG蓝图——安全校验目标"
parent_task_id: null
child_task_ids: []
upstream_files:
  - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_context_engine.yaml"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\blueprint-registry.yaml"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\__init__.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_assembler.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_budget_tracker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\doc_compressor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_injector.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\intent_parser.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\intent_keyword_mapper.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\pattern_library.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\prompt_registry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\system_snapshot.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\architecture_context.json"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\config\\context_rules_v1.yaml"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\config\\compression\\policy.yaml"
tags: ["context-engine", "module-init", "bounded-context", "scaffold", "phase-1"]
acceptance_criteria:
  - "AC-001: `src/zephyr/context_engine/__init__.py` 创建，声明 bounded_context=true"
  - "AC-002: 9 个 .py 源文件骨架已按 §4 文件组成创建，每个含模块级 docstring 描述职责"
  - "AC-003: 2 个配置文件目录 (config/ + config/compression/) 存在，含占位 YAML"
  - "AC-004: architecture_context.json 存在，内含空 JSON 结构 (architectures: [])"
  - "AC-005: blueprint-registry.yaml 已登记 MOD-INF-008 条目"
  - "AC-006: construction_progress 状态更新为 scaffold → implemented"
rollback_instructions: "删除 src/zephyr/context_engine/ 目录下所有新建文件，恢复 blueprint-registry.yaml 中 MOD-INF-008 条目至此前状态，从 git history 恢复 blueprint.md 的 construction_progress 字段"
context_assembly_manifest:
  required_blueprints:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md §1, §4, §10"
  required_standards:
    - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\governance\\document\\directory-structure-standard.md"
  required_templates: []
  required_references:
    - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_context_engine.yaml"
---
# MOD-INF-008-TASK-001: 模块身份与文件骨架搭建

## 1. Purpose

创建 Context Engine 模块的物理文件结构，确立 bounded_context=true 的边界上下文，将 9 个 .py + 2 个 config + 1 个 JSON 数据文件的骨架部署到磁盘上。

## 2. Scope

### In-Scope
- 创建 `src/zephyr/context_engine/` 目录及 `__init__.py`，声明 `bounded_context=true`
- 按 §4 文件组成创建以下 9 个 .py 源文件骨架（含模块级 docstring）：
  - `context_assembler.py` — Build 阶段——从 VMS 拉取原始上下文
  - `context_budget_tracker.py` — Compress 阶段——Token 预算管理
  - `doc_compressor.py` — Compress 阶段——三级压缩回退（已有 563 行完整实现，更新 docstring）
  - `context_injector.py` — Inject 阶段——格式化+注入 session
  - `intent_parser.py` — 解析任务意图→决定检索策略
  - `intent_keyword_mapper.py` — 意图→关键词映射表
  - `pattern_library.py` — Validate 阶段——已知危险模式库
  - `prompt_registry.py` — Validate 阶段——注入模板注册
  - `system_snapshot.py` — 系统状态快照——供上下文参考
- 创建配置目录与占位文件：
  - `config/context_rules_v1.yaml` (已存在，验证)
  - `config/compression/policy.yaml` (已存在，验证)
- 创建 `architecture_context.json` 空结构
- 更新 `blueprint-registry.yaml` 登记 MOD-INF-008
- 更新蓝图 `construction_progress` → `phase_1_partial`（已完成部分）

### Out-of-Scope
- 各文件的完整逻辑实现（见 TASK-002 ~ TASK-005）
- VMS/LSG 集成（见 TASK-010）
- 测试文件创建（各阶段自行负责）

## 3. Module Identity (§1)

| 属性 | 值 |
|------|-----|
| module_id | MOD-INF-008 |
| 代码落位 | `src/zephyr/context_engine/` |
| 边界上下文 | bounded_context: true |
| 伞盖层 | l12 (可观测层覆盖) |
| 核心职责 | 把知识库里的东西变成 Agent 能用的上下文——不多不少、安全合规 |

## 4. Construction Phase Mapping (§10)

| Phase | 任务 | 状态 |
|:---:|------|:---:|
| scaffold | 9 文件骨架 + context_assembler + injector | 本任务目标：implemented |
| experimental | VMS 集成 → 完整的 build→inject 链路 | 后续 TASK-010 |
| beta | LSG validate 集成 + 第三级截断降级 | 后续 TASK-004 |

## 5. Acceptance Criteria

- 所有 9 个源文件 + 2 个配置文件 + 1 个 JSON 文件在磁盘上存在且内容正确
- `__init__.py` 包含 `__all__` 导出列表
- `architecture_context.json` 结构：`{"architectures": [], "last_updated": "2026-05-06"}`
- `blueprint-registry.yaml` 已更新
- `python -c "from zephyr.context_engine import __all__"` 无 ImportError

## 6. Rollback Instructions

1. 删除 `src/zephyr/context_engine/` 目录下所有 TASK-001 新建的文件
2. 恢复 `blueprint-registry.yaml` 中 MOD-INF-008 条目至此前状态
3. 恢复 `blueprint.md` 的 `construction_progress` 字段（如改过）

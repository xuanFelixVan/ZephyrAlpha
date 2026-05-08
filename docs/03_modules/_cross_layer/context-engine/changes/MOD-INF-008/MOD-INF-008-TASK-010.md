---
task_id: "MOD-INF-008-TASK-010"
task_title: "集成契约 CT-ORC-CE-001 / CT-CE-VMS-001 / CT-CE-LSG-001 实现"
module_id: "MOD-INF-008"
blueprint_section: "§8 集成契约 CT-ORC-CE-001, CT-CE-VMS-001, CT-CE-LSG-001"
status: "backlog"
priority: "P0"
layer: "cross_layer"
assigned_agent: "DeepSeek-V4-Pro"
review_agent: "GLM-4.7"
execution_model: ["DeepSeek-V4-Pro", "GLM-4.7"]
task_type: "CODE_GEN"
estimated_effort_hours: 10
actual_effort_hours: null
deadline: null
depends_on:
  - task_id: "MOD-MASTER-001"
    why: "CT-ORC-CE-001 集成契约——Orc→CE 上下文构建请求时序 (§2.3)"
  - task_id: "MOD-INF-011"
    why: "CT-CE-VMS-001 集成契约——CE→VMS 向量检索"
  - task_id: "MOD-INF-014"
    why: "CT-CE-LSG-001 集成契约——CE→LSG 安全审查"
parent_task_id: "MOD-INF-008-TASK-001"
child_task_ids: []
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_assembler.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_injector.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\vector_bridge.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\pipeline_orchestrator.py"
tags: ["context-engine", "integration-contracts", "orchestrator", "vms", "lsg"]
acceptance_criteria:
  - "AC-001: CT-ORC-CE-001 实现: Orc 在任务启动时调用 CE.build(task_card, session_id)——实现接受 TaskCard + session_id 参数"
  - "AC-002: CT-CE-VMS-001 实现: CE.build() 调用 VMS.search() 进行 4C 检索——vector_bridge.py 桥接实现"
  - "AC-003: CT-CE-LSG-001 实现: CE.validate() 调用 LSG 三层审查 → PASS/FAIL——集成调用链完整"
  - "AC-004: vector_bridge.py (P1 beta 待实现) 作为 CE↔VMS 检索桥接——接受 query Embedding + Collection name → 返回 top-K results"
  - "AC-005: pipeline_orchestrator.py (P3 beta 待实现) 编排多阶段流水线——已有测试 Ghost (test_pipeline_orchestrator.py)"
  - "AC-006: 所有契约调用带超时 + 重试机制"
  - "AC-007: 详见 MASTER-001 §2.3/§2.6/§2.11 交叉引用验证"
rollback_instructions: "移除 vector_bridge.py/pipeline_orchestrator.py 中的集成代码，恢复为独立模式"
context_assembly_manifest:
  required_blueprints:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md §8"
    - "D:\\ZephyrAlpha\\docs\\03_modules\\_master-blueprint\\blueprint.md §2.3, §2.6, §2.11"
  required_standards: []
  required_templates: []
  required_references:
    - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_context_engine.yaml"
---
# MOD-INF-008-TASK-010: 集成契约实现

## 1. Purpose

实现 §8 定义的三条集成契约，连接 Context Engine 与 Orchestrator、VMS、LSG 三个外部系统。

## 2. Integration Contracts

| CT-* | 涉及系统 | 方向 | 说明 |
|------|---------|------|------|
| CT-ORC-CE-001 | Orc→CE | → | Orc 在任务启动时→CE.build(task_card, session_id) |
| CT-CE-VMS-001 | CE→VMS | → | CE.build()→VMS.search()→4C 检索 |
| CT-CE-LSG-001 | CE→LSG | → | CE.validate()→LSG 三层审查→PASS/FAIL |

## 3. Missing File Implementation

| 文件 | 优先级 | 职责 |
|------|:---:|------|
| `vector_bridge.py` | P1 | CE↔VMS 检索桥接 (Connect CT-CE-VMS-001) |
| `pipeline_orchestrator.py` | P3 | 多阶段流水线编排 (已有测试 Ghost) |
| `task_validator.py` | P2 | 任务告警/故障验证 |

## 4. Cross-reference

详见总蓝图 MASTER-001 §2.3/§2.6/§2.11 中的交叉引用契约定义。

## 5. Acceptance Criteria

- Orc 可调用 CE.build() 并传入 TaskCard + session_id
- VMS.search() 调用通过 vector_bridge 桥接完成
- LSG 三层审查集成——validate() 返回 PASS 或 FAIL
- 向量检索和 LSG 调用均带 5s 超时
- test_pipeline_orchestrator.py (Ghost 测试) 可用于验证编排逻辑

---
task_id: "MOD-INF-008-TASK-006"
task_title: "系统状态快照 — system_snapshot.py 实现"
module_id: "MOD-INF-008"
blueprint_section: "§4 文件组成 system_snapshot.py"
status: "backlog"
priority: "P1"
layer: "cross_layer"
assigned_agent: "DeepSeek-V4-Pro"
review_agent: "GLM-4.7"
execution_model: ["DeepSeek-V4-Pro", "GLM-4.7"]
task_type: "CODE_GEN"
estimated_effort_hours: 3
actual_effort_hours: null
deadline: null
depends_on:
  - task_id: "MOD-INF-008-TASK-001"
    why: "模块骨架已创建"
parent_task_id: "MOD-INF-008-TASK-001"
child_task_ids: []
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\system_snapshot.py"
  - "D:\\ZephyrAlpha\\tests\\test_system_snapshot.py"
tags: ["context-engine", "system-snapshot", "observability"]
acceptance_criteria:
  - "AC-001: system_snapshot.py 实现系统状态快照采集功能"
  - "AC-002: 快照包含：当前活跃 Agent session 数、VMS 连接状态、CE pipeline 各阶段耗时、内存使用"
  - "AC-003: take_snapshot() 返回 SystemSnapshot 对象（Pydantic V2 BaseModel）"
  - "AC-004: test_system_snapshot.py 通过"
rollback_instructions: "恢复 system_snapshot.py 到骨架状态，删除测试新增内容"
context_assembly_manifest:
  required_blueprints:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md §4"
  required_standards: []
  required_templates: []
  required_references: []
---
# MOD-INF-008-TASK-006: 系统状态快照

## 1. Purpose

实现 system_snapshot.py，提供系统运行状态的快照功能，供上下文注入时参考系统当前状况。

## 2. Implementation

- `take_snapshot() -> SystemSnapshot`: 采集系统状态
- 快照字段：
  - active_sessions: int
  - vms_connected: bool
  - ce_pipeline_stats: dict (各阶段耗时)
  - memory_usage_mb: float
  - timestamp: datetime

## 3. Acceptance Criteria

- SystemSnapshot 为 Pydantic V2 frozen model
- take_snapshot() 可独立调用，无外部依赖
- pytest test_system_snapshot.py 通过

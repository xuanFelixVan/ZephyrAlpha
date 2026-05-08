---
task_id: "TASK-SYS-0005"
source_blueprint: "SYS-MASTER-001"
source_section: "§4 跨模块数据流 + §5 依赖矩阵 + §8 关联更新"

title: "跨模块整合基础——数据流向/依赖矩阵/关联更新三组件骨架"
description: |
  将 SYS-MASTER-001 §4-§5-§8（合并为"跨模块整合基础"）工程化落地。
  §4: 跨模块数据流向描述——数据在各层之间的产生者/消费者/传输格式。
  §5: 模块间依赖关系矩阵——module_id→depends_on_modules mapping 与循环依赖检测。
  §8: 关联内容更新机制——蓝图变更后下游受影响文档的追溯更新链。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\task-system\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\data_flow_manifest.py"
    description: "§4 数据流 Edge list——producer/consumer/protocol/format 边定义"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\dependency_graph.py"
    description: "§5 依赖图 adjacency list + 循环检测 + .dot 导出"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\content_update_tracker.py"
    description: "§8 关联更新追踪——change→affected_docs 追溯链"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\data_flow_manifest.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\dependency_graph.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\content_update_tracker.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l0*\\**\\*.py"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§4-§5-§8——跨模块整合基础三节"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 12000
timeout_minutes: 35

acceptance_criteria:
  - "data_flow_manifest.py 定义 DataFlowEdge(producer, consumer, protocol, format) dataclass"
  - "dependency_graph.py Tarjan SCC 循环检测——发现循环 → WARNING + 建议修复路径"
  - "content_update_tracker.py 记录 UpdateLog(changed_section, affected_docs[], reason)"
  - "script_manifest.yaml 注册"

rollback_instructions: |
  git rm src/zephyr/governance/data_flow_manifest.py dependency_graph.py content_update_tracker.py
  从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0003"
blocked_by: []
status: "created"
tags_fn:
  - "infra"
tags_ly: "cross_layer"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "SYS-MASTER-001"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---

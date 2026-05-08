---
task_id: "MOD-INF-008-TASK-012"
task_title: "代码路径索引验证与缺口关闭 — §12 + §14 全覆盖"
module_id: "MOD-INF-008"
blueprint_section: "§12 已实现代码完整路径索引 (§12.1-§12.4) + §14 当前缺失清单"
status: "backlog"
priority: "P1"
layer: "cross_layer"
assigned_agent: "DeepSeek-V4-Pro"
review_agent: "GLM-4.7"
execution_model: ["DeepSeek-V4-Pro", "GLM-4.7"]
task_type: "AUDIT"
estimated_effort_hours: 4
actual_effort_hours: null
deadline: null
depends_on:
  - task_id: "MOD-INF-008-TASK-001"
    why: "需要文件骨架就位后才能做磁盘验证"
parent_task_id: "MOD-INF-008-TASK-001"
child_task_ids: []
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_assembler.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\doc_compressor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_injector.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\verify_paths.py"
tags: ["context-engine", "audit", "path-verification", "gap-closure", "code-index"]
acceptance_criteria:
  - "AC-001: §12.1 源文件逐项验证: 12 已实现 ✅ 验证存在、3 待实现 ❌ 验证缺失 + 原因记录"
  - "AC-002: §12.2 测试文件逐项验证: 9+1 Ghost 验证状态、Ghost test 标记为 → 待实现源文件"
  - "AC-003: §12.3 配置文件逐项验证: 2 配置 ✅ 存在"
  - "AC-004: §12.4 统计一致性: 蓝图中统计数字与磁盘实际一致"
  - "AC-005: §14 缺失清单逐项对照: 10 项缺失各自记录当前状态"
  - "AC-006: 若磁盘实际与蓝图不一致 → 上报 discrepancy 而不修改蓝图"
  - "AC-007: verify_paths.py 脚本可重复运行，每次输出一致性报告"
rollback_instructions: "删除 verify_paths.py"
context_assembly_manifest:
  required_blueprints:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md §12, §14"
  required_standards: []
  required_templates: []
  required_references: []
---
# MOD-INF-008-TASK-012: 代码路径索引验证与缺口关闭

## 1. Purpose

对 §12 和 §14 中的所有文件路径执行磁盘验证，确保蓝图中的索引与实际文件系统一致。任何不一致上报为 discrepancy。

## 2. Source File Verification (§12.1)

| 文件 | 预期 | 验证 |
|------|:---:|------|
| context_assembler.py | ✅ 292 行 | os.path.exists + lines check |
| context_budget_tracker.py | ✅ 227 行 | os.path.exists + lines check |
| context_injector.py | ✅ 升级 | os.path.exists |
| context_rot_model.py | ✅ 新建 | os.path.exists |
| context_evictor.py | ✅ 新建 | os.path.exists |
| doc_compressor.py | ✅ 563 行 | os.path.exists + lines check |
| intent_keyword_mapper.py | ✅ | os.path.exists |
| intent_parser.py | ✅ | os.path.exists |
| pattern_library.py | ✅ | os.path.exists |
| prompt_registry.py | ✅ | os.path.exists |
| system_snapshot.py | ✅ | os.path.exists |
| architecture_context.json | ✅ | os.path.exists |
| task_validator.py | ❌ | 验证不存在 |
| pipeline_orchestrator.py | ❌ | 验证不存在 |
| vector_bridge.py | ❌ | 验证不存在 |

## 3. Test File Verification (§12.2)

逐项验证 10 个测试文件 + Ghost 标记。

## 4. Missing Items Gap (§14)

逐项核对 10 项缺失清单的当前状态（哪些已在 beta a 补齐、哪些仍待处理）。

## 5. Acceptance Criteria

- verify_paths.py 输出 {file: path, expected: "✅"/"❌"/"⚠️", actual: ...}
- 所有 ✅ 文件通过 os.path.exists()
- 所有 ❌ 文件验证不存在
- ⚠️ Ghost test 特殊标记
- 蓝图统计 (24 已实现 / 3 待实现) 与磁盘一致

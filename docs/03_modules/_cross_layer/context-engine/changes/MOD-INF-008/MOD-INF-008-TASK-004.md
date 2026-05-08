---
task_id: "MOD-INF-008-TASK-004"
task_title: "Validate 阶段实现 — prompt_registry.py + pattern_library.py + LSG 集成"
module_id: "MOD-INF-008"
blueprint_section: "§2.3 Validate + §5.3 Stage 3 Validate YAML 规则"
status: "backlog"
priority: "P0"
layer: "cross_layer"
assigned_agent: "DeepSeek-V4-Pro"
review_agent: "GLM-4.7"
execution_model: ["DeepSeek-V4-Pro", "GLM-4.7"]
task_type: "CODE_GEN"
estimated_effort_hours: 8
actual_effort_hours: null
deadline: null
depends_on:
  - task_id: "MOD-INF-008-TASK-003"
    why: "Compress 阶段的压缩上下文是 Validate 的输入"
  - task_id: "MOD-INF-014"
    why: "LSG 蓝图——安全校验 API 契约"
parent_task_id: "MOD-INF-008-TASK-001"
child_task_ids: []
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\doc_compressor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\context_budget_tracker.py"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\prompt_registry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\context_engine\\pattern_library.py"
  - "D:\\ZephyrAlpha\\tests\\test_prompt_registry.py"
  - "D:\\ZephyrAlpha\\tests\\test_pattern_library.py"
tags: ["context-engine", "validate-stage", "lsg", "safety-check", "prompt-injection"]
acceptance_criteria:
  - "AC-001: prompt_registry.py 实现注入模板注册与管理"
  - "AC-002: pattern_library.py 实现已知危险模式库（prompt injection / 敏感信息泄露 / 危险工具调用）"
  - "AC-003: validate() 通过 CT-CE-LSG-001 契约调用 LSG 三层审查 (VALIDATE-C00)"
  - "AC-004: LSG 拒绝的块 → 移除 → 重新 compress → 再送 LSG → 最多 3 次"
  - "AC-005: VALIDATE-C01 条件：验证 context.sources 所有路径在磁盘上存在"
  - "AC-006: 不存在的 source → 移除 → 重新 assemble"
  - "AC-007: test_prompt_registry.py, test_pattern_library.py 通过"
rollback_instructions: "恢复 prompt_registry.py/pattern_library.py 到骨架状态，删除测试新增内容"
context_assembly_manifest:
  required_blueprints:
    - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\context-engine\\blueprint.md §2.3, §5.3"
  required_standards: []
  required_templates: []
  required_references:
    - "D:\\ZephyrAlpha\\architecture-model\\layers\\b_context_engine.yaml"
---
# MOD-INF-008-TASK-004: Validate 阶段实现

## 1. Purpose

实现四阶段流水线第三阶段 VALIDATE：对战上下文进行安全校验，确保注入内容不含恶意指令、敏感信息或危险建议。

## 2. Core Implementation — prompt_registry.py (§2.3)

注入模板注册表——管理上下文注入时的模板格式。

## 3. Pattern Library — pattern_library.py (§2.3)

已知危险模式库——检测以下三类恶意内容：
1. Prompt injection——恶意指令
2. 项目敏感信息泄露
3. 危险工具调用建议

## 4. LSG 安全校验 — §2.3 + §5.3

通过 CT-CE-LSG-001 契约调用 LSG 三层审查：

VALIDATE-C00 (lsg_safety_check):
```
check: "context通过 CT-CE-LSG-001 → LSG三层审查全部PASS"
severity: error
on_failure: auto_fix
fix_hint: "LSG拒绝 → 移除违规content → 重新compress → 最多3次"
```

LSG 拒绝处理流程：
1. LSG 拒绝 → 移除被拒绝的 block
2. 重新 compress（从 raw_text 重新压缩，排除被拒绝块）
3. 再送 LSG
4. 最多 3 次循环 → 第 3 次仍被拒绝 → 丢弃该块

## 5. Source Validation — §5.3 VALIDATE-C01

VALIDATE-C01 (no_hallucinated_sources):
```
check: "ALL context.sources 路径在磁盘上存在"
severity: error
on_failure: auto_fix
fix_hint: "移除不存在的source → 重新assemble"
```

禁止注入不存在文件路径作 source——防止 LLM 幻觉连锁（AP5 直接破解）。

## 6. Acceptance Criteria

- validate() 成功调用 LSG 三层审查
- 单次拒绝后正确执行 remove→re-compress→re-validate 循环
- 3 次循环后丢弃被拒绝块，标记 injection_blocks_removed
- context.sources 中所有路径通过 os.path.exists() 验证
- pytest test_prompt_registry.py test_pattern_library.py 通过

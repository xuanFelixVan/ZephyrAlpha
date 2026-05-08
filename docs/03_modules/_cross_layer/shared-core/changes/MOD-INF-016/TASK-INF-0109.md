---
task_id: "TASK-INF-0109"
source_blueprint: "MOD-INF-016"
source_section: "蓝图 §4 Phase 17 + §13 盲点 B43-B45"

title: "Phase 17 施工——AI 安全可控：DSPy声明式优化(B43) + StructuredConcurrency(B44) + DryRun模式(B45)"
description: |
  实现 AI 的安全可控开发/优化/仿真基础设施。
  B43：DSPy 风格声明式 Prompt 优化——当前 prompts 手工编写，无系统化优化流程。
  需实现：DSPyOptimizer 接口——声明式 Signature（输入/输出类型）→ 自动 few-shot 优化 → MIPROv2 风格自动提示词搜索。
  对标 DSPy 3.0 / MIPROv2 / BetterTogether。
  B44：Structured Concurrency——结构化并发管理。当前 async 代码裸用 asyncio.gather()，缺结构化错误处理。
  需实现：StructuredConcurrency——TaskGroup 模式（anyio.TaskGroup / trio.Nursery 风格），任一子任务失败 → 取消同组其他任务。
  对标 anyio.TaskGroup / trio.Nursery。
  B45：Dry-run / Simulation Mode——AI 操作在无副作用模式下预演。
  需实现：DryRunMode——全局 dry_run flag → 所有 shared/ 的写操作（atomic_write / API call / DB write）在 dry_run=True 时仅 log 不执行。
  对标 Claude Code /dry-run。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\dspy_optimizer.py"
    description: "DSPyOptimizer——Signature 定义 + MIPROv2 风格自动提示词搜索"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\structured_concurrency.py"
    description: "StructuredConcurrency——TaskGroup + 失败取消同级任务"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\shared\\dry_run.py"
    description: "DryRunMode——全局 flag + 写操作自动 skip（仅 log）"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_dspy_optimizer.py"
    description: "单元测试——验证 Signature 定义、few-shot 优化"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_structured_concurrency.py"
    description: "单元测试——验证 TaskGroup 取消传播"
  - path: "D:\\ZephyrAlpha\\tests\\unit\\test_dry_run.py"
    description: "单元测试——验证 dry_run 跳写/不跳读"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\dspy_optimizer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\structured_concurrency.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\dry_run.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\__init__.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_dspy_optimizer.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_structured_concurrency.py"
  - "D:\\ZephyrAlpha\\tests\\unit\\test_dry_run.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\SHARED-QUICKREF.yml"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "GOV-DOC-002"
    section: "§5.5"
    reason: "shared/ 准入规则——被 ≥2 个 L01 模块消费"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\shared-core\\blueprint.md"
    reason: "本蓝图 §4/§13——Phase 17 + B43-B45 盲点详情"

assigned_model: "claude-opus-4.7"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 25000
timeout_minutes: 60

acceptance_criteria:
  - "dspy_optimizer.py: Signature 模型——input_fields / output_fields + 类型注解"
  - "dspy_optimizer.py: DSPyOptimizer.optimize(signature, trainset)——返回优化后的 prompt template"
  - "structured_concurrency.py: TaskGroup context manager——__aenter__ / __aexit__"
  - "structured_concurrency.py: 任一子任务 fail → TaskGroup 内其他 task 收到 CancelledError"
  - "dry_run.py: DryRunMode 全局 contextvar——set_dry_run(True/False)"
  - "dry_run.py: @dry_run_aware 装饰器——dry_run=True 时仅 log 不执行副作用"
  - "pytest tests/unit/test_dspy_optimizer.py -v 全部通过"
  - "pytest tests/unit/test_structured_concurrency.py -v 全部通过"
  - "pytest tests/unit/test_dry_run.py -v 全部通过"
  - "SHARED-QUICKREF.yml 更新——新增 3 个模块入口"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\shared\dspy_optimizer.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\shared\structured_concurrency.py
  3. 删除 D:\ZephyrAlpha\src\zephyr\shared\dry_run.py
  4. 删除 3 个对应测试文件
  5. 还原 __init__.py 对应导出
  6. 还原 SHARED-QUICKREF.yml 对应条目

depends_on: ["TASK-INF-0105"]
blocked_by: []

status: "created"

tags_fn:
  - "infra"
tags_ly: "cross_layer"
tags_md: "claude-opus-4.7"
tags_st: "active"
tags_mo:
  - "MOD-INF-016"

completed_gates: []
blocked_gates: {}

artifact_paths: []

audit_findings: []

ke_entries: []

ai_autonomy_level: "supervised"
autonomy_checklist: []
---

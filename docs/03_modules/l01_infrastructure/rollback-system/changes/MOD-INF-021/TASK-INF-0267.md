---
task_id: "TASK-INF-0267"
source_blueprint: "MOD-INF-021"
source_section: "蓝图 §7 Phase 9 + §6.16 B113-B122 + 决策 D-021-33~37 + §9 exit codes 34-39"
title: "操作治理——模型漂移/置信度/Error Budget/fail策略/Rebase/Commit质量/沙盒/AI功耗防御"
description: |
  实现 Phase 9 操作治理层，覆盖 B113-B122：
  B113 LLM 模型静默行为漂移检测 → exit 34 (MODEL_DRIFT_DETECTED)
  B114 AI 置信度量化—连续低置信 → exit 37 (LOW_CONFIDENCE_CONSEC)
  B115 自复杂度元 Budget—回滚复杂度超过阈值 → exit 38 (COMPLEXITY_OVER_BUDGET)
  B116 Error Budget 自治门禁—>4% error rate → 紧急 human take-over
  B117 Rebase 进行中检测—git/rebase-merge 存在 → exit 36 (REBASE_IN_PROGRESS) 防覆盖
  B118 Commit 质量基础设施—lint 每条回滚 revert message
  B119 fail-open/fail-closed 策略—按环境/profile 切换
  B120 上下文窗口污染 GC—Agent context window 定期 archive
  B121 沙盒隔离—Agent 执行环境与非沙盒物理隔离 → exit 39 (SANDBOX_BREACH)
  B122 AI 主动防御—AI 不修改自身安全配置 + chmod 444 核心固件
  涵盖 R41-R44 最高优先级治理风险。
priority: "P0"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\model_drift_detector.py"
    description: "模型版本漂移——LLM 行为 baseline 偏差检测"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\confidence_quantifier.py"
    description: "AI 置信度量化——连续低置信 → tier 降低"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\complexity_budget.py"
    description: "复杂度元 Budget——McCCabe > 15 / 文件 → 回溯"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\commit_quality_gate.py"
    description: "Commit 质量基础设施——lint revert msg"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\sandbox_enforcer.py"
    description: "沙盒隔离——Agent sandbox 执行 +chroot/ns"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
    description: "集成 Rebase/fail-policy/context window GC/error-budget-gate"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\model_drift_detector.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\confidence_quantifier.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\complexity_budget.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\commit_quality_gate.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\sandbox_enforcer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制 Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\rollback-system\\blueprint.md"
    reason: "本蓝图——§6.16 B113-B122 操作治理 + D-021-33~37 + R41-R44"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1"]
estimated_tokens: 16000
timeout_minutes: 60
acceptance_criteria:
  - "model_drift: LLM 行为 baseline deviation > 阈值 → exit 34"
  - "confidence: 连续3轮低置信 → exit 37 → tier downgrade"
  - "complexity: 单文件 McCabe > 15 / 回滚范围 > 20 files → exit 38"
  - "error_budget: >4% error / 30 days → human take-over"
  - "rebase_in_progress: git/rebase-merge 存在 → exit 36 / block"
  - "commit_quality: lint revert msg (subject < 72 / body 原文动机)"
  - "fail_policy: configurable fail-open → L1 re-read  / fail-closed → L2 Kill"
  - "context_gc: Agent context window > limit → archive + fresh load"
  - "sandbox: exec() system calls bypass 报 exit 39"
  - "self_defense: AI chmod 444 on core files confirmed"
rollback_instructions: |
  1. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\model_drift_detector.py
  2. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\confidence_quantifier.py
  3. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\complexity_budget.py
  4. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\commit_quality_gate.py
  5. 删除 D:\\ZephyrAlpha\\src\\zephyr\\rollback\\sandbox_enforcer.py
  6. git checkout HEAD~1 -- D:\\ZephyrAlpha\\src\\zephyr\\rollback\\rollback_executor.py
depends_on:
  - "TASK-INF-0266"
blocked_by: []
status: "done"
tags_fn: ["infra"]
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo: ["MOD-INF-021"]
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---

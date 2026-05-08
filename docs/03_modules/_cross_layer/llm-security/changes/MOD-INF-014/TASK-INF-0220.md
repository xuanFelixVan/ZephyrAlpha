---
task_id: "TASK-INF-0220"
source_blueprint: "MOD-INF-014"
source_section: "§26 1人+AI维护加固"
title: "1人+AI维护模式安全加固——LSG自启动+最小权限+无头钩子+沙箱检查+敏感面缩减+会话独立日志+变更验证+AI分叉防护"
description: |
  实现 1人+AI维护模式的八项安全加固措施：
  1. LSG自启动(pre-commit hook→自动加载+pre-main guard)
  2. AI最小权限(Tool=DEFAULT_RESTRICT + 独立session→user)
  3. 无头钩子(headless pre-commit CI钩子)
  4. 产出物双重沙箱检查(PR Stage → L2a Sandbox + CLI→L2a+ValidationLayer)
  5. 敏感面缩减(AI visible file prefix + 凭据→pre-commit→secret mask)
  6. 按会话独立安全日志(session_id→按日切分+保留7天)
  7. 变更验证+AI分叉防护(可信git状态基线+判定commit作者匹配session-author)
  8. 1h+humain audit auto-flag(>1h未人工审核→FLAG→日报)
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\_cross_layer\\llm-security\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\solo_ai_hardening.py"
    description: "1人+AI维护加固——八项防护措施"
  - path: "D:\\ZephyrAlpha\\tests\\llm_security\\test_solo_ai_hardening.py"
    description: "1人+AI维护加固测试——8条用例"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\solo_ai_hardening.py"
  - "D:\\ZephyrAlpha\\tests\\llm_security\\test_solo_ai_hardening.py"
forbidden_touch: []
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\_cross_layer\\llm-security\\blueprint.md"
    reason: "§26完整定义"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1","M3"]
estimated_tokens: 10000
timeout_minutes: 60
acceptance_criteria:
  - "SoloAIHardening 含 enable_shadow_guard/enable_dual_sandbox/enable_session_isolation/enable_ci_execution_wrapper 8个方法"
  - "ShadowGuard: fetch checks→enable/disable controls→report"
  - "DualSandbox: PR Stage + CLI 两级沙箱串联"
  - "Session Isolation: session_id→独立user→独立env→独立log"
  - "SensitiveSurfaceReducer: 文件前缀过滤+凭据掩码"
  - "SessionAudit: 按session_id+日期切分日志+7天保留"
  - "ChangeValidator: git状态基线+t=0基线采集+diff验证"
  - "AIForkDetector: commit作者匹配session-author+non-match→flag"
  - "HumainReviewReminder: >1h无人工审核→FLAG→日报"
  - "8条测试全部通过"
rollback_instructions: |
  1. 删除 solo_ai_hardening.py + test_solo_ai_hardening.py
depends_on: ["TASK-INF-0201"]
blocked_by: []
status: "created"
tags_fn: ["security","maintenance"]
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo: ["MOD-INF-014"]
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---

# 目标

实现 1人+AI 维护模式下的八项安全加固措施——确保 AI 辅助开发不会引入安全退化。

## 执行步骤

### 做
1. 实现 SoloAIHardening 八项防护
2. 编写 8 条验证测试

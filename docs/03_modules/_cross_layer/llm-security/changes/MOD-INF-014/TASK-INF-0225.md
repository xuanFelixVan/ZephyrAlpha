---
task_id: "TASK-INF-0225"
source_blueprint: "MOD-INF-014"
source_section: "§7 Anti-Patterns AP1-AP7 反模式防护"
title: "LSG七条反模式防护实现——每AP一条防护代码+文档警告+测试验证+pre-commit劝阻检查"
description: |
  为蓝图 §7 的七条反模式逐条实现防护措施：
  AP1: 忽略间接注入→L1 check_indirect_content 强制开启 (TASK-INF-0204)
  AP2: 过度信任Tool输出→L4 validate_tool_params + ToolResultTransform (TASK-INF-0204/0207)
  AP3: System Prompt硬编码→YSF 外部化+版本控制 (环境变量注入)
  AP4: 无成本跟踪→L5 cost_enabled TASK-INF-0208
  AP5: "先放行再安全"→L3 output优先处理 redact→sandbox→validate order
  AP6: 归一化ASCII过滤→Unicode-aware normalize—TASK-INF-0204
  AP7: 未监控LSG自身健康→L6 self_health_check TASK-INF-0209
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\llm-security\\blueprint.md"
downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\gates\anti_pattern_guard.py"
    description: "AP1-AP7 反模式防护集中实现——7个方法+pre-commit劝阻"
  - path: "D:\\ZephyrAlpha\\tests\\llm_security\\test_anti_pattern_guard.py"
    description: "AP1-AP7 防护验证测试——7条用例"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\anti_pattern_guard.py"
  - "D:\\ZephyrAlpha\\tests\\llm_security\\test_anti_pattern_guard.py"
forbidden_touch: []
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\_cross_layer\\llm-security\\blueprint.md"
    reason: "§7 AP1-AP7"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1","M3"]
estimated_tokens: 8000
timeout_minutes: 45
acceptance_criteria:
  - "AntiPatternGuard 含 guard_ap1-guard_ap7 七个方法+check_all() 批量执行"
  - "AP1: ensure-method L1 check_indirect_content 在 LSG pipeline 中默认启用"
  - "AP2: alert_function 检测未验证直接使用的 tool return value"
  - "AP3: refuse_function 扫描代码中硬编码 System Prompt + prompt→environment variable 注入"
  - "AP4: alert_function 检测 L5 cost_tracking=False 的会话"
  - "AP5: refuse_function 强制 L3 输出安全处理顺序: redact→sandbox→validate→check safety"
  - "AP6: alert_function 检测 ASCII降级处理丢失 Unicode 上下文信息"
  - "AP7: check_function 循环检查 L6 self_health (CPU/memory/error rate) + 健康状态汇总"
  - "pre-commit hook 劝阻检查: python scripts/anti_pattern_precommit.py → .pre-commit-config.yaml"
  - "7条测试全部通过"
rollback_instructions: |
  1. 删除 anti_pattern_guard.py + test_anti_pattern_guard.py
  2. 从 pre-commit-config.yaml 中移除 anti_pattern_precommit hook
depends_on: ["TASK-INF-0201","TASK-INF-0204","TASK-INF-0205","TASK-INF-0206","TASK-INF-0207","TASK-INF-0208","TASK-INF-0209"]
blocked_by: []
status: "done"
tags_fn: ["security","anti-patterns"]
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

实现反模式 AP1-AP7 的防护代码。每条反模式对应一个防护方法，通过代码强制执行而非靠文档约束。集成至 pre-commit 劝阻检查。

## 执行步骤

### 做
1. 实现 AntiPatternGuard——7个guard方法+check_all() 批量
2. 实现 anti_pattern_precommit.py pre-commit hook
3. 编写 7 条测试

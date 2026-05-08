---
task_id: "TASK-INF-0219"
source_blueprint: "MOD-INF-014"
source_section: "§25 Vibe Coding安全盲点（五个盲点+AP防护）+ §43 安全墒增加"
title: "Vibe Coding五盲点防护完整实现——AI代码信任边界+会话角色混淆+Rules文件保护+递归代理+沙箱逃逸+安全墒"
description: |
  实现五个安全盲点的防护代码：
  盲点一(§25.1): AI生成代码信任边界审计器——6类安全检查 (TASK-INF-0206 L3已部分涵盖)
  盲点二(§25.2): 会话角色混淆防护——会话ID→权限绑定
  盲点三(§25.3): Rules File完整性保护——SHA256基线验证 (TASK-INF-0203 L0已部分涵盖)  
  盲点四(§25.4): 递归代理执行失控防护 (TASK-INF-0208 L5已部分涵盖)
  盲点五(§25.5): 沙箱逃逸数据提取防护 (TASK-INF-0211 L2a已部分涵盖)
  §43 安全墒增加: AI maintenance session in→组内相似→代码pH值测量→factor衰减预警
priority: "P1"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\_cross_layer\\llm-security\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\blindspot_guard.py"
    description: "五盲点统一防护层+安全墒监控"
  - path: "D:\\ZephyrAlpha\\tests\\llm_security\\test_blindspot_guard.py"
    description: "五盲点防护验证测试——10条用例"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\blindspot_guard.py"
  - "D:\\ZephyrAlpha\\tests\\llm_security\\test_blindspot_guard.py"
forbidden_touch: []
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\_cross_layer\\llm-security\\blueprint.md"
    reason: "§25+§43"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1","M3"]
estimated_tokens: 10000
timeout_minutes: 60
acceptance_criteria:
  - "VibeCodingBlindSpotGuard 含 blindspot_1-5 五个方法"
  - "盲点一: AIGeneratedCodeTrustBoundary.audit() 6类检查结果可序列化"
  - "盲点二: SessionRoleConfusionGuard——session_id→permission binding enforce"
  - "盲点三: RulesFileIntegrityGuard——rules file SHA256基线比对"
  - "盲点四: RecursiveAgentGuard——agent_depth_limit + loop_detection"
  - "盲点五: SandboxDataExfiltrationGuard——行为模式异常检测"
  - "SecurityEntropyMonitor: measure_code_ph() + compute_factor_decay() + entropy_alert_threshold=30%"
  - "10条测试全部通过"
rollback_instructions: |
  1. 删除 blindspot_guard.py + test_blindspot_guard.py
depends_on: ["TASK-INF-0201"]
blocked_by: []
status: "created"
tags_fn: ["security","blindspot"]
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

实现 Vibe Coding 五个安全盲点防护的统一管理器 + 安全墒增加监控系统。

## 执行步骤

### 做
1. 实现 VibeCodingBlindSpotGuard 五盲点方法
2. 实现 SecurityEntropyMonitor 安全墒监控
3. 编写 10 条验证测试

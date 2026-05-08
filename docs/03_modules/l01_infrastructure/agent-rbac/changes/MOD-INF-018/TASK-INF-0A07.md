---
task_id: "TASK-INF-0A07"
source_blueprint: "MOD-INF-018"
source_section: "蓝图 §2.6 L3 — Input Guard 参数护栏 + D-018-08"

title: "实现L3 InputGuard — 参数级护栏（schema白名单+危险模式+路径白名单+包安装管控）"
description: |
  实现input_guard.py。参数级护栏：参数schema白名单(类型/范围/正则)、危险模式检测(rm -rf/curl|bash/>/dev/null等)、
  路径白名单(仅允许项目目录内的路径)、package_install白名单(已知可信包)、network_target白名单(白名单URL/黑名单IP)。
  编码绕过检测：自动de-base64/de-hex/de-url后再匹配。
  package_install默认blocked_packages:["*"]——仅白名单可安装。
  实施D-018-08：权限颗粒度从Tool级细化到参数级——L3是参数级防御线。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\identity.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\input_guard.py"
    description: "InputGuard——param_schema_validation/dangerous_pattern_detection/path_whitelist/package_install_guard/network_target_guard/encoding_bypass_detection"
  - path: "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_input_guard.py"
    description: "测试——参数schema/危险模式/路径白名单/编码绕过/包安装白名单/网络边界"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\input_guard.py"
  - "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_input_guard.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
    reason: "§2.6 L3 Input Guard+危险模式清单+编码绕过+包安装+网络边界+决策D-018-08"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 14000
timeout_minutes: 60

acceptance_criteria:
  - "param_schema_validation:参数类型/范围/正则不匹配→BLOCKED"
  - "dangerous_patterns:rm -rf/curl|bash/管道/etc/passwd→检测后BLOCKED"
  - "encoding_bypass:base64编码的rm -rf→解码后仍被检测"
  - "package_install:不在白名单的pip install→BLOCKED"
  - "network_target:不在白名单的URL→AUTO_GUARD(BLOCKED if off_hours)"
  - "path_whitelist:../../及绝对路径跨项目目录→BLOCKED"
  - "pytest验证120+个攻击向量被正确拦截"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\agent_rbac\input_guard.py
  2. 删除 D:\ZephyrAlpha\tests\agent_rbac\test_input_guard.py

depends_on:
  - "TASK-INF-0A02"
  - "TASK-INF-0A05"
blocked_by: []

status: "done"

tags_fn:
  - "infra"
  - "security"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-018"

completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---

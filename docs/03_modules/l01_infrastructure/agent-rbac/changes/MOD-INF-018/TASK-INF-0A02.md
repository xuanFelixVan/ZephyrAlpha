---
task_id: "TASK-INF-0A02"
source_blueprint: "MOD-INF-018"
source_section: "蓝图 §2.1 L0 — 不可变核心 + D-018-04"

title: "实现L0 ImmutableCore — 硬编码不可变保护区"
description: |
  实现agent_rbac核心文件immutable_core.py。
  硬编码protected_paths列表(>=22条路径)和always_blocked列表(>=14项操作)。
  保护路径覆盖：.git/config/AGENTS.md/GOV-AI-001/rbac_roles.yaml/.env/pyproject.toml/
  .github/workflows/docker-compose/nav_table/.pre-commit-config.yaml/.trae/rules/
  .cursorrules等。
  always_blocked覆盖：delete_audit_logs/modify_immutable_core/spawn_new_agent_unsanctioned/
  forge_agent_identity/modify_environment_variables/os_acl_bypass/synthesize_restricted_data/
  cascade_failure_trigger/circumvent_micro_verification等。
  实施D-018-04：硬编码不可变保护区——100%AI施工，护栏自身必须不能被AI修改。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
    description: "ImmutableCore类——hardcoded protected_paths/always_blocked/os_acl_verification/tamper_detection"

  - path: "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_immutable_core.py"
    description: "测试——验证protected_paths完整性/always_blocked覆盖/OS ACL生效/tamper检测"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_immutable_core.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\schemas.py"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
    reason: "§2.1+L0定义——protected_paths和always_blocked完整列表"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 12000
timeout_minutes: 60

acceptance_criteria:
  - "ImmutableCore类加载后protected_paths数量>=22"
  - "ImmutableCore类加载后always_blocked数量>=14"
  - "is_protected_path()对已知保护路径返回True"
  - "is_always_blocked()对spawn_new_agent_unsanctioned等返回True"
  - "verify_immutable_core_integrity()检测到任何修改返回TAMPERED"
  - "OS ACL部署验证脚本确认关键文件ACL已生效"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\agent_rbac\immutable_core.py
  2. 删除 D:\ZephyrAlpha\tests\agent_rbac\test_immutable_core.py
  3. 如有部署OS ACL——执行对应的ACL撤销脚本

depends_on:
  - "TASK-INF-0A01"
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

# 实现 L0 ImmutableCore — 硬编码不可变保护区

## 实现覆盖

### D-018-04 决策实现
- 硬编码protected_paths >= 22条
- 硬编码always_blocked >= 14项
- OS级ACL双重兜底

### 代码块对应
YAML代码块 L254: `immutable_core_config` 守卫配置
Python代码块 L1082: `ImmutableCore` 类实现

### 盲点覆盖
B3(权限配置自身无保护), B35(导航表保护), B37(持久化后门), B38(环境变量篡改), B129(Pre-Commit Hooks)

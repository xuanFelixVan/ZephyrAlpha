---
task_id: "TASK-INF-0A15"
source_blueprint: "MOD-INF-018"
source_section: "蓝图 §2.22~§2.28 — IBAC/Context Drift/连续验证/权限模式管理器/级联故障/Micro-Verified/自解释"

title: "实现横切面D——IBAC意图绑定、Context Drift检测、连续验证、权限模式管理器、级联故障隔离、Micro-Verified先干后验（D-018-20~26）"
description: |
  实现横切面D全部六项能力：
  1. IBAC意图绑定(D-018-20)：任务意图+临时权限信封+IntentBindingContext+Inference泄漏防护(推理式越权)
  2. Context Drift检测(D-018-21)：操作链三维实时追踪(type/intent/path entropy漂移)
  3. 连续验证(D-018-22)：每步重验证Agent身份+意图+Token+委托链(Zero Trust)
  4. 权限模式管理器(D-018-23)：Claude Code 5模式+Codex CLI Profiles+Mid-Session/mode切换
  5. 级联故障隔离(D-018-24)：Agent链Cascading Failure防护+上游故障→下游降权
  6. Micro-Verified先干后验(D-018-25)：每子步微型验证替代全干再验
  覆盖§2.22~§2.28全部内容。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\identity.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\permission_guard.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\intent_binder.py"
    description: "IBAC意图绑定——intent_envelope/IntentBindingContext/permission_envelope_ttl/Inference泄漏防护"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\context_drift_detector.py"
    description: "Context Drift——三维实时追踪(type_entropy/intent_entropy/path_entropy)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\continuous_verifier.py"
    description: "连续验证——每步Zero Trust重验证(agent_id+intent+token+delegation_chain)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\permission_mode_manager.py"
    description: "权限模式管理器——5模式(Full/Auto/Plan/Audit/KillSwitch)+Profiles+Mid-Session切换"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\cascading_failure_isolator.py"
    description: "级联故障隔离——Agent链监控/自动隔离/上游故障→下游降权"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\micro_verifier.py"
    description: "Micro-Verified先干后验——子步分解+微验证+即时回滚"
  - path: "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_crosscutD.py"
    description: "横切面D六项能力综合测试"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\intent_binder.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\context_drift_detector.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\continuous_verifier.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\permission_mode_manager.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\cascading_failure_isolator.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\micro_verifier.py"
  - "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_crosscutD.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
    reason: "§2.22~2.28横切面D六项能力完整规范+决策D-018-20~26"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 20000
timeout_minutes: 90

acceptance_criteria:
  - "intent_binder:基于GOV-AI-001的intent生成PermissionEnvelope(含ttl/idempotency_key)"
  - "context_drift:三维entropy(type/intent/path)任一>阈值→标记DRIFT→升级AUTO_GUARD"
  - "continuous_verifier:每步操作前check(agent,action,delegation_chain)→Token/角色/Maturity最小有效原则"
  - "mode_manager:5模式(Full/Auto/Plan/Audit/KillSwitch)→/mode命令切换+ShiftTab显示当前模式"
  - "cascade_isolator:上游Agent故障→下游Agent所有操作降权为AUTO_GUARD(blocked if off_hours)"
  - "micro_verifier:子步分解→每子步微验证→失败即时回滚(不等待全链路)"

rollback_instructions: |
  1. 删除本卡创建的6个.py文件和1个测试文件

depends_on:
  - "TASK-INF-0A05"
  - "TASK-INF-0A13"
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

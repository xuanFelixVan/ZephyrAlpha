---
task_id: "TASK-INF-0A14"
source_blueprint: "MOD-INF-018"
source_section: "蓝图 §2.15~§2.21 — 横向越权/冷启动锁/权限钩子/Agent创建权/缓存一致性/紧急覆盖令牌/自动维护"

title: "实现横向越权防护、冷启动锁、权限钩子系统、Agent创建权、缓存一致性、紧急覆盖令牌、自动维护（D-018-13~19）"
description: |
  实现七项横向增强安全机制：
  1. 横向越权防护(D-018-13)：SessionToken HMAC-SHA256签名校验+AgentIdentityVerifier+跨Session伪造检测
  2. 冷启动锁(D-018-14)：系统启动时全局拒绝直到权限配置加载+maintenance_mode+校验序列
  3. 权限钩子系统(D-018-15)：四类钩子注册表(pre/post/on_blocked/on_kill_switch)+9个预置钩子(H01-H09)
  4. Agent创建权与权限遗传(D-018-16)：creation_policy+遗传衰减+agent_spawn_storm熔断+生命周期管理
  5. 缓存一致性推送(D-018-17)：推送驱动缓存失效(max_latency=100ms替代TTL=5min)+降级攻击防护
  6. 紧急覆盖令牌(D-018-18)：Owner JIT临时越权(<5分钟/一次性/可吊销/CLI)
  7. 自动维护(D-018-19)：僵尸规则检测+权限复杂度预算(max=30)+Owner健康仪表盘(5个数)
  覆盖§2.15~§2.21全部内容。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\identity.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\permission_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\kill_switch.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\cross_session_detector.py"
    description: "横向越权防护——SessionToken签名/HMAC-SHA256/AgentIdentityVerifier/跨Session伪造检测"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\cold_start_lock.py"
    description: "冷启动锁——startup_lock/maintenance_mode/校验序列/权限加载前全局拒绝"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\permission_hooks.py"
    description: "权限钩子系统——四类钩子注册表+9个预置钩子(H01-H09)+permission_hooks.yaml"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\agent_creation_policy.py"
    description: "Agent创建权——creation_policy/遗传衰减/spawn_storm熔断/生命周期管理"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\cache_invalidation.py"
    description: "缓存一致性——推送驱动失效(max_latency=100ms)/降级攻击防护/cache_policy.yaml"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\emergency_override.py"
    description: "紧急覆盖令牌——JIT越权(<5分钟/一次性/CLI/可吊销)/Owner签发"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\auto_maintenance.py"
    description: "自动维护——僵尸规则检测/复杂度预算(max=30)/Owner健康仪表盘(5数字)"
  - path: "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_enhanced_security.py"
    description: "七项增强安全机制整合测试集合"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\cross_session_detector.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\cold_start_lock.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\permission_hooks.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\agent_creation_policy.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\cache_invalidation.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\emergency_override.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\auto_maintenance.py"
  - "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_enhanced_security.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
    reason: "§2.15~2.21横向越权/冷启动/钩子/创建权/缓存/紧急令牌/自动维护+决策D-018-13~19"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 22000
timeout_minutes: 90

acceptance_criteria:
  - "SessionToken签名:HMAC-SHA256(agent_id+session_id+nonce+timestamp)"
  - "冷启动锁:权限配置加载前任何check()返回GLOBAL_BLOCKED"
  - "四类钩子注册:(pre_check,post_check,on_blocked,on_kill_switch)全部可注册/执行"
  - "9个预置钩子H01-H09已实现(含SandboxLiveness/TokenRenewal/FrequencyLimit等)"
  - "Agent创建:子Agent Maturity<=父Maturity-1,permissions=父permissions*0.7(遗传衰减)"
  - "缓存失效:权限变更→推送通知→max_latency=100ms内清除缓存"
  - "紧急令牌:CLI生成JIT Token→<5分钟有效期→一次性使用→可吊销"
  - "自动维护:僵尸规则(30天未触发)自动标记+复杂度预算<=30"

rollback_instructions: |
  1. 删除本卡创建的7个.py文件和1个测试文件
  2. 删除permission_hooks.yaml/cache_policy.yaml(如已创建)
  3. immutable_core.py如有引用——移除引用恢复原始版本(在forbidden_touch保护中)

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

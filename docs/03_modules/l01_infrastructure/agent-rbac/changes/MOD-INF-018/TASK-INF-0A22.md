---
task_id: "TASK-INF-0A22"
source_blueprint: "MOD-INF-018"
source_section: "蓝图 §4 — 与现有系统的集成 + DOM-GOV-001 集成契约 (G-CT-001/004/007/008)"

title: "实现agent-rbac与16+现有系统集成点——包含四大集成契约(G-CT-001/004/007/008)"
description: |
  实现agent-rbac模块与ZephyrAlpha现有系统的全部集成点（严格按蓝图§4表格）。
  四大集成契约：
  - G-CT-001 Agent Identity：agent_identity格式与自动派生规则——对接GOV-AI-001
  - G-CT-004 Permission Decision：权限决策合约——返回PermissionDecision/DecisionExplainer
  - G-CT-007 Test Contract：测试契约——120+自愈测试(攻击+对抗+边缘)→对接test_final_gates.py
  - G-CT-008 Codev Contract：AI-人工协作护栏——A/B/C/AUTO_GUARD策略
  
  17个系统集成点（按蓝图§4表格顺序）：
  1. Gate Engine (MOD-INF-007) — 权限检查作为G0门禁前置检查
  2. Task System (MOD-INF-006) — 任务创建时绑定Agent身份+任务上下文注入L2 ABAC
  3. Audit Trail (MOD-INF-020) — 每层权限判定+序列违规+Kill Switch事件写入不可变审计日志
  4. Rollback System (MOD-INF-021) — auto_guard后验失败+L4序列违规后自动回滚
  5. Circuit Breaker (MOD-INF-022) — L0 Kill Switch复用熔断器基础设施
  6. MCP Servers (MOD-INF-013) — MCP Tool调用前七层权限检查
  7. GOV-AI-001 — 自动派生rbac_roles.yaml
  8. Input Sanitizer/LSG (MOD-INF-014) — L3 Input Guard复用Prompt Injection检测模式
  9. Pre-Commit Gate (GATE-18) — CI中运行L7权限自动化测试
  10. OpenTelemetry Collector — L6指标上报(d2.authz.decision.*)
  11. Hook Registry (NEW) — 横切面A四类钩子注册表(pre/post/on_blocked/on_kill_switch)
  12. Cache Invalidator (NEW) — 横切面C推送驱动缓存失效+降级攻击防护
  13. Emergency Override (NEW) — Owner JIT越权令牌
  14. Owner Dashboard (NEW) — 横切面C自动更新YAML健康仪表盘(5关键数字)
  15. RL/Rollback Auth (NEW) — 回滚操作权限边界(也需过L0不可变核心)
  16. Inter-Agent Detector (NEW) — L4跨Agent隐式通信检测
  17. Ownership Absence (NEW) — Owner超时未审阅→系统自治保守模式
  覆盖蓝图§4+DOM-GOV-001全部内容。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\permission_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\identity.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\skyviva.yaml"
  - "D:\\ZephyrAlpha\\scripts\\governance\\script_manifest.yaml"

downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\integrations.py"
    description: "IntegrationManager——16+系统集成注册/初始化/契约验证/健康检查集成"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\contract_verifier.py"
    description: "ContractVerification——G-CT-001/004/007/008契约合规自动验证"
  - path: "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_integration.py"
    description: "集成测试——16+系统集成点验证"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\integration.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\contract_verifier.py"
  - "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_integration.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
  - "D:\\ZephyrAlpha\\skyviva.yaml"
  - "D:\\ZephyrAlpha\\scripts\\governance\\script_manifest.yaml"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号"
  - module_id: "GOV-DOC-002"
    section: "§5.1.2"
    reason: "路径映射一致性——集成文件路径对齐"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
    reason: "§4 16+集成点清单+DOM-GOV-001四大契约+集成映射矩阵"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 18000
timeout_minutes: 90

acceptance_criteria:
  - "IntegrationManager.register()支持全部16+系统注册"
  - "contract_verifier验证G-CT-001:Agent Identity格式符合GOV-AI-001规范"
  - "contract_verifier验证G-CT-004:PermissionDecision含(blocked_layer,rule_id,correction_suggestion,causal_chain)"
  - "contract_verifier验证G-CT-007:测试数>=120,攻击/对抗/边缘全覆盖"
  - "contract_verifier验证G-CT-008:A/B/C/AUTO_GUARD策略定义正确"
  - "pre-commit hooks集成:git hook调用agent-rbac check()"
  - ".trae/rules + .cursorrules自动同步——L0保护"
  - "skyviva.yaml module注册 valid"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\agent_rbac\integration.py
  2. 删除 D:\ZephyrAlpha\src\zephyr\agent_rbac\contract_verifier.py
  3. 删除 D:\ZephyrAlpha\tests\agent_rbac\test_integration.py

depends_on:
  - "TASK-INF-0A13"
blocked_by: []

status: "done"

tags_fn:
  - "infra"
  - "security"
  - "integration"
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

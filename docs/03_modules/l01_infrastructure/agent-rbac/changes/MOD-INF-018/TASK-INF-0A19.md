---
task_id: "TASK-INF-0A19"
source_blueprint: "MOD-INF-018"
source_section: "蓝图 §3.0.21~§3.0.36 — 横切面E/F 氛围编程扩展组 (D-018-54~69)"

title: "实现横切面E/F高级防护组A——氛围编程扩展（Sandbox Liveness、Bootstrap协调器、MCP代理护栏、内省链防护等 D-018-54~69）"
description: |
  实现§3.0.21~36共16项横切面E/F高级防护（严格按蓝图§3.0.21~§3.0.36标题）：
  - D-018-54 SandboxLivenessGuard —— 沙箱/安全依赖静默回退防护 (§3.0.21)
  - D-018-55 BootstrapCoordinator —— 多IDE并发施工期最小保护 (§3.0.22)
  - D-018-56 MCPPermissionProxy —— MCP工具协议层权限中间件 (§3.0.23)
  - D-018-57 IntrospectionChainGuard —— Python对象内省链沙箱逃逸防护 (§3.0.24)
  - D-018-58 GracefulTokenRenewal —— Session Token在途过期保护 (§3.0.25)
  - D-018-59 ConcurrentThroughputOptimizer —— 并发权限检查吞吐量退化防护 (§3.0.26)
  - D-018-60 DashboardAuthenticityVerifier —— Owner仪表盘数据真实性独立验证 (§3.0.27)
  - D-018-61 StagedDeploymentGuard —— RBAC分阶段部署中间态保护 (§3.0.28)
  - D-018-62 ConflictResolutionPolicy —— 跨模型权限冲突自动降级 (§3.0.29)
  - D-018-63 DLLSearchOrderGuard —— Windows DLL搜索顺序劫持防护 (§3.0.30)
  - D-018-64 SessionIdentityBinding —— Agent跨会话身份持久化伪造防护 (§3.0.31)
  - D-018-65 BuildArtifactIntegrityChain —— RBAC构建产物供应链完整性链 (§3.0.32)
  - D-018-66 ClassifierAdversarialHardening —— AI推理链操纵攻击对抗硬化 (§3.0.33)
  - D-018-67 MCPResponseRedactor —— MCP工具回显敏感信息脱敏 (§3.0.34)
  - D-018-68 ConstantTimePermissionCheck —— 权限决策时间侧信道消除 (§3.0.35)
  - D-018-69 MutationTestFramework —— AI生成测试的覆盖盲区自欺防护 (§3.0.36)
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\permission_guard.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\vibe_coding_guard.py"
    description: "D-018-54~69氛围编程防护集合——sandbox_liveness/bootstrap_coordinator/mcp_proxy/introspection_chain等16项"
  - path: "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_vibe_coding.py"
    description: "氛围编程防护测试合集(16项)"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\vibe_coding_guard.py"
  - "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_vibe_coding.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
    reason: "§3.0.21~36氛围编程防护16项规范+决策D-018-54~69"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 20000
timeout_minutes: 90

acceptance_criteria:
  - "SandboxLivenessGuard:沙箱心跳监控+中断>阈值→自动重启+标记agent异常"
  - "BootstrapCoordinator:多IDE并发期启动协调验证通过才允许agent初始化"
  - "MCPPermissionProxy:MCP请求经协议层中间件→清洗+审计"
  - "IntrospectionChainGuard:内省链检测→递归深度>阈值→BLOCKED"
  - "GracefulTokenRenewal:Session Token在途过期→续期保护机制"
  - "ConcurrentThroughputOptimizer:并发权限检查→吞吐量退化检测+自动限流"
  - "DashboardAuthenticityVerifier:Owner仪表盘数据→独立验证数据来源真实性"
  - "StagedDeploymentGuard:分阶段部署→中间态保护+前阶段未完下阶段不开启"
  - "ConflictResolutionPolicy:跨模型权限冲突→自动降级到最安全判定"
  - "DLLSearchOrderGuard:Windows DLL搜索路径劫持→检测+阻断"
  - "SessionIdentityBinding:跨会话身份持久化→伪造检测+身份绑定验证"
  - "BuildArtifactIntegrityChain:构建产物→完整性链签名验证"
  - "ClassifierAdversarialHardening:AI推理链操纵→对抗硬化"
  - "MCPResponseRedactor:MCP工具回显→敏感信息自动脱敏"
  - "ConstantTimePermissionCheck:权限决策→恒定时间比较消除时间侧信道"
  - "MutationTestFramework:AI生成测试→变异测试防覆盖盲区自欺"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\agent_rbac\vibe_coding_guard.py
  2. 删除 D:\ZephyrAlpha\tests\agent_rbac\test_vibe_coding.py

depends_on:
  - "TASK-INF-0A13"
blocked_by: []

status: "created"

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

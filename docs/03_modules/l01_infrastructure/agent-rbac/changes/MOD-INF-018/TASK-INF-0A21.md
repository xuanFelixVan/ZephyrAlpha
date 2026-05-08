---
task_id: "TASK-INF-0A21"
source_blueprint: "MOD-INF-018"
source_section: "蓝图 §3.0.49~§3.0.61 — 横切面E/F 2026最新安全事件驱动组 (D-018-82~94)"

title: "实现横切面E/F高级防护组C——2026安全事件驱动（VSCode Ransomware/MCP工具定义完整性/键绑劫持/幻构依赖/信道劫持/动态信任等 D-018-82~94）"
description: |
  实现§3.0.49~61共13项横切面E/F高级防护（严格按蓝图§3.0.49~§3.0.61标题）：
  - D-018-82 EnvironmentBoundaryEnforcement —— Agent跨环境边界横向移动防护 (§3.0.49)
  - D-018-83 ConfigPreExecutionGuard —— IDE配置文件预权限执行竞态防护 (§3.0.50)
  - D-018-84 CrossModelSecurityAudit —— AI生成安全代码自绕过回环防护 (§3.0.51)
  - D-018-85 SafetyIncentiveAlignment —— Agent任务完成驱动型规则覆写防护 (§3.0.52)
  - D-018-86 CredentialDiscoveryRadiusControl —— Agent凭证发现半径爆炸控制 (§3.0.53)
  - D-018-87 MCPSTDIOSanitizer —— MCP STDIO传输层Shell元字符注入防护 (§3.0.54)
  - D-018-88 CloudIAMIdentityFederation —— Agent身份到云资源IAM的身份联邦 (§3.0.55)
  - D-018-89 SafeDeserializationGuard —— Agent定义文件的非安全反序列化代码执行防护 (§3.0.56)
  - D-018-90 SlopsquattingDefense —— AI幻构依赖(Slopsquatting)攻击防护 (§3.0.57)
  - D-018-91 CommunicationChannelIntegrityGuard —— IDE-RBAC通信信道劫持防护(CSWSH/WebSocket/RPC Hijacking) (§3.0.58)
  - D-018-92 AdaptiveTrustBudget —— Agent动态信任预算模型(实时自适应授权) (§3.0.59)
  - D-018-93 SafetyIncentiveAlignment —— Agent任务完成驱动型规则覆写防护 (§3.0.60)
  - D-018-94 ToolDefinitionIntegrityGuard —— MCP工具定义加密完整性验证(防变异/防回滚/防能力升级) (§3.0.61)
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\permission_guard.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\cybersec_2026_guard.py"
    description: "D-018-82~94 2026安全事件防护集合——13项最新防护能力"
  - path: "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_cybersec_2026.py"
    description: "2026安全事件防护测试合集(13项)"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\cybersec_2026_guard.py"
  - "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_cybersec_2026.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
    reason: "§3.0.49~61 2026安全事件防护13项规范+决策D-018-82~94"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 20000
timeout_minutes: 90

acceptance_criteria:
  - "EnvironmentBoundaryEnforcement:Agent跨环境边界→横向移动检测+阻断"
  - "ConfigPreExecutionGuard:IDE配置文件预执行→竞态检测+原子性保护"
  - "CrossModelSecurityAudit:AI生成安全代码→自绕过回环检测(不同模型交叉审查)"
  - "SafetyIncentiveAlignment:Agent任务完成驱动→规则覆写意图检测+阻断"
  - "CredentialDiscoveryRadiusControl:Agent凭证发现范围→半径爆炸控制+边界限制"
  - "MCPSTDIOSanitizer:MCP STDIO传输→Shell元字符注入清洗"
  - "CloudIAMIdentityFederation:Agent身份→云资源IAM联邦映射+权限审计"
  - "SafeDeserializationGuard:Agent定义文件→非安全反序列化检测(pickle/eval/exec)"
  - "SlopsquattingDefense:AI幻构依赖→PyPI存在性验证+包名相似度检测"
  - "CommunicationChannelIntegrityGuard:IDE-RBAC通信→CSWSH/WebSocket/RPC劫持防护"
  - "AdaptiveTrustBudget:Agent动态信任预算→实时操作授权+信任消耗模型"
  - "ToolDefinitionIntegrityGuard:MCP工具定义→加密完整性+变异/回滚/能力升级检测"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\agent_rbac\cybersec_2026_guard.py
  2. 删除 D:\ZephyrAlpha\tests\agent_rbac\test_cybersec_2026.py

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

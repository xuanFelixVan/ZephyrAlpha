---
task_id: "TASK-INF-0A20"
source_blueprint: "MOD-INF-018"
source_section: "蓝图 §3.0.37~§3.0.48 — 横切面E/F 新型攻击面组 (D-018-70~81)"

title: "实现横切面E/F高级防护组B——新型攻击面（Implied Permission伪造、CVE回放、安全工具妥协、挂钩生成、代码反馈循环、隐式数据流等 D-018-70~81）"
description: |
  实现§3.0.37~48共12项横切面E/F高级防护（严格按蓝图§3.0.37~§3.0.48标题）：
  - D-018-70 GitHookGuard —— Git Hook RCE via AI Agent (§3.0.37)
  - D-018-71 PthFileExecutionGuard —— Python .pth文件静默自动执行防护 (§3.0.38)
  - D-018-72 ProjectConfigExecutionGuard —— IDE项目配置自动执行防护 (§3.0.39)
  - D-018-73 ClassifierRetrainingIntegrity —— 分类器对抗重训练管道自体中毒防护 (§3.0.40)
  - D-018-74 AgentMemoryPoisoningGuard —— Agent长程上下文记忆投毒防护 (§3.0.41)
  - D-018-75 TrustChainVerifier —— 多Agent信任链背叛防护 (§3.0.42)
  - D-018-76 WebContentTrustTier —— Web连接Agent的Prompt Injection不对称放大防护 (§3.0.43)
  - D-018-77 ModelWeightIntegrityVerifier —— ML模型权重文件完整性验证 (§3.0.44)
  - D-018-78 CovertStorageChannelDetector —— 隐蔽存储侧信道数据外泄检测 (§3.0.45)
  - D-018-79 CICDCredentialIsolation —— RBAC CI/CD凭证窃取与恶意自替换防护 (§3.0.46)
  - D-018-80 ThresholdObfuscationGuard —— Agent对RBAC检测阈值的行为指纹刻画防护 (§3.0.47)
  - D-018-81 SharedStateInjectionGuard —— Agent间共享工作状态后门检测 (§3.0.48)
priority: "P2"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\permission_guard.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\novel_attack_guard.py"
    description: "D-018-70~81新型攻击面防护集合——12项深度防护能力"
  - path: "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_novel_attack.py"
    description: "新型攻击面防护测试合集(12项)"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\novel_attack_guard.py"
  - "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_novel_attack.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
    reason: "§3.0.37~48新型攻击面12项防护规范+决策D-018-70~81"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 18000
timeout_minutes: 90

acceptance_criteria:
  - "GitHookGuard:Git Hook RCE via AI Agent→检测.git/hooks/被Agent修改→阻断"
  - "PthFileExecutionGuard:Python .pth文件静默执行→检测.pth文件创建/修改→阻断"
  - "ProjectConfigExecutionGuard:IDE项目配置文件自动执行→.vscode/.idea配置变更→审计"
  - "ClassifierRetrainingIntegrity:分类器重训练管道→对抗样本自体中毒检测"
  - "AgentMemoryPoisoningGuard:Agent长程上下文→记忆投毒检测+隔离"
  - "TrustChainVerifier:多Agent信任链→背叛检测+信任重评估"
  - "WebContentTrustTier:Web连接中Prompt Injection→不对称放大防护"
  - "ModelWeightIntegrityVerifier:ML模型权重文件→完整性哈希验证"
  - "CovertStorageChannelDetector:隐蔽存储侧信道→数据外泄模式检测"
  - "CICDCredentialIsolation:CI/CD凭证→窃取检测+恶意自替换防护"
  - "ThresholdObfuscationGuard:Agent行为指纹→检测阈值刻画防护"
  - "SharedStateInjectionGuard:Agent间共享状态→后门注入检测"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\agent_rbac\novel_attack_guard.py
  2. 删除 D:\ZephyrAlpha\tests\agent_rbac\test_novel_attack.py

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

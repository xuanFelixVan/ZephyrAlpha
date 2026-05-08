---
task_id: "TASK-INF-0A16"
source_blueprint: "MOD-INF-018"
source_section: "蓝图 §3.0 横切面F取证级安全保障 —— Genesis Bootstrap防护至跨平台Shell安全 (D-018-34~38)"

title: "实现取证级安全保障(上)——Genesis Bootstrap、非对称安全审查、不可抵赖绑定、路径解析防护、跨平台Shell方言检测（D-018-34~38）"
description: |
  实现§3.0.1~3.0.5五项取证级安全保障：
  1. Genesis Bootstrap防护(D-018-34)：phase0启动审计快照+完整性基线+constraint_fresh_policy首次优先
  2. 非对称安全审查(D-018-35)：Agent产出允许部分幻觉但安全产出必须保守+手动A/B审计
  3. 不可抵赖操作绑定(D-018-36)：Ed25519 Agent Keygen→签名操作请求→系统验证→三链保存
  4. 路径解析系统故障防护(D-018-37)：双通道路径解析+Windows/macOS/Linux差异检测+WSL2对称保护
  5. 跨平台Shell方言检测(D-018-38)：PowerShell/Bash/CMD/ZSH+Windows策略优先级+神奇后缀攻击防护
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\identity.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\permission_guard.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\genesis_bootstrap.py"
    description: "Genesis Bootstrap——phase0审计快照/完整性基线/constraint_fresh_policy"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\asymmetric_audit.py"
    description: "非对称安全审查——Agent产出vs安全产出/手动A/B审计/安全保守策略"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\non_repudiation.py"
    description: "不可抵赖操作绑定——Ed25519 Keygen/签名/验证/三链保存"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\path_guard.py"
    description: "路径解析防护——双通道解析/Windows-macOS-Linux差异/WSL2对称保护"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\shell_dialect_detector.py"
    description: "Shell方言检测——PowerShell/Bash/CMD/ZSH/Windows策略优先/神奇后缀防护"
  - path: "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_forensic_a.py"
    description: "取证级安全A组测试(5项)"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\genesis_bootstrap.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\asymmetric_audit.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\non_repudiation.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\path_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\shell_dialect_detector.py"
  - "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_forensic_a.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
    reason: "§3.0.1~3.0.5五项取证级安全+决策D-018-34~38+双通道路径解析+Shell方言完整列表"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 20000
timeout_minutes: 90

acceptance_criteria:
  - "genesis_bootstrap:phase0启动→生成完整性基线→constraint_fresh_policy优先于现有策略"
  - "asymmetric_audit:Agent产出允许幻觉但安全判定必须保守→人工审查差异标记"
  - "non_repudiation:Agent Ed25519 Keygen→操作签名保存→三链(操作/审计/完整性)验证"
  - "path_guard:双通道(Windows+Unix)解析对比→不一致/不存在/UNC绕过→BLOCKED"
  - "shell_dialect:PowerShell Set-ExecutionPolicy Bypass/Bash rm -rf --no-preserve-root/CMD del /F /Q→检测跨方言"
  - "WSL2对称保护:wslpath映射|\\\\wsl.localhost\\ UNC路径纳入防护"

rollback_instructions: |
  1. 删除本卡创建的5个.py文件和1个测试文件
  2. 删除genesis_bootstrap生成的完整性基线文件(如已创建)

depends_on:
  - "TASK-INF-0A05"
  - "TASK-INF-0A13"
blocked_by: []

status: "done"

tags_fn:
  - "infra"
  - "security"
  - "forensic"
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

---
task_id: "TASK-INF-0A17"
source_blueprint: "MOD-INF-018"
source_section: "蓝图 §3.0 横切面F取证级安全保障 —— 权限规则注入防护至蓝图-实现保真度验证 (D-018-39~51)"

title: "实现取证级安全保障(中)——权限规则注入防护、构建产物卫生、依赖审计、日志完整性、重放攻击防护、律师审计、Rollback隔离、单调时钟、递归验证、密钥层次化、异常检测、日志注入防护、蓝图保真度（D-018-39~51）"
description: |
  实现§3.0.6~3.0.18十三项取证级安全保障核心能力：
  1. D-018-39 权限规则语言注入防护——规则YAML/JSON中嵌套代码检测
  2. D-018-40 构建产物安全卫生——CI artifact保留时间+签名+完整性校验
  3. D-018-41 Transitive依赖审计——PyPI/npm依赖传递链审查+typosquatting检测
  4. D-018-42 审计日志实时完整性验证——append-only+HMAC chain+SHA256 hash链
  5. D-018-43 上下文重放攻击防护——非确定性nonce+context_fingerprint+操作单调ID
  6. D-018-44 律师可验证审计——证据链完整性+法庭可呈送结构+证据锁定
  7. D-018-45 Rollback攻击载体隔离——回滚操作本身可能承载恶意载荷
  8. D-018-46 单调时钟与系统时钟操纵防护——CLOCK_MONOTONIC+时间倒退检测
  9. D-018-47 Bootstrap验证无限递归解决——验证器验证自身的循环断裂
  10. D-018-48 主密钥层次化与泄露隔离——主密钥/操作密钥/会话密钥三层
  11. D-018-49 未知攻击模式统计异常检测——行为基线+偏差检测+ML异常分数
  12. D-018-50 审计日志注入防护——ANSI escape/CRLF注入/unicode rtl/fake JSON
  13. D-018-51 蓝图-实现保真度验证——自动验证实施是否符合蓝图规范
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\permission_guard.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\rule_injection_guard.py"
    description: "D-018-39权限规则YAML/JSON注入防护——嵌套代码检测"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\build_sanitizer.py"
    description: "D-018-40构建产物安全卫生——artifact签名+保留时间+完整性"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\dependency_auditor.py"
    description: "D-018-41依赖审计——传递链审查+typosquatting+许可证冲突"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\audit_log_guard.py"
    description: "D-018-42/D-018-50——append-only HMAC链+SHA256+注入防护"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\replay_attack_guard.py"
    description: "D-018-43——nonce+context_fingerprint+operation_id单调递增"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\legal_audit_chain.py"
    description: "D-018-44——证据链完整性+法庭可呈送结构+时间锁定"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\rollback_sandbox.py"
    description: "D-018-45——回滚操作安全沙箱+攻击载体检测"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\monotonic_clock.py"
    description: "D-018-46——CLOCK_MONOTONIC+时间倒退检测+漂移监控"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\bootstrap_verifier.py"
    description: "D-018-47——验证器自验证循环断裂解决"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\key_hierarchy.py"
    description: "D-018-48——主密钥/操作密钥/会话密钥三层+泄露隔离"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\anomaly_detector.py"
    description: "D-018-49——行为基线+偏差检测+ML异常分数"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\blueprint_fidelity.py"
    description: "D-018-51——蓝图vs实现保真度自动验证"
  - path: "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_forensic_b.py"
    description: "取证级安全B组综合测试(13项)"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\rule_injection_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\build_sanitizer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\dependency_auditor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\audit_log_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\replay_attack_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\legal_audit_chain.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\rollback_sandbox.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\monotonic_clock.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\bootstrap_verifier.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\key_hierarchy.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\anomaly_detector.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\blueprint_fidelity.py"
  - "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_forensic_b.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
    reason: "§3.0.6~3.0.18十三项取证级安全保障规范+决策D-018-39~51"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 25000
timeout_minutes: 120

acceptance_criteria:
  - "rule_injection:YAML/JSON中嵌套Python→os.system(→检测BLOCKED"
  - "build_sanitizer:CI artifact签名校验+7天保留+TAMPERED阻断"
  - "dependency_auditor:PyPI包传递链审查+typosquatting(requests→requets)检测"
  - "audit_log_guard:append-only HMAC-SHA256链+ANSI/CRLF/Unicode RTL注入防护"
  - "replay_attack:nonce重复→BLOCKED+context_fingerprint不匹配→AUTO_GUARD"
  - "legal_audit:证据链输出法庭可呈送JSON-LD格式(含时间戳/操作者/非对称签名)"
  - "rollback_sandbox:回滚操作在沙箱中执行+隐藏命令检测"
  - "monotonic_clock:CLOCK_MONOTONIC读数倒退→触发Kill Switch"
  - "blueprint_fidelity:自动对比蓝图vs实现→报告偏差清单"

rollback_instructions: |
  1. 删除本卡创建的12个.py文件和1个测试文件
  2. 删除密钥层次化生成的密钥文件(如已创建)

depends_on:
  - "TASK-INF-0A13"
blocked_by: []

status: "created"

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

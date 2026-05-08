---
task_id: "TASK-INF-0A12"
source_blueprint: "MOD-INF-018"
source_section: "蓝图 §2.11~§2.13 — 先干后验/D-018-02 + GOV-AI-001派生/D-018-03 + Agent身份模型"

title: "实现先干后验模式、GOV-AI-001自动派生和Agent身份模型（D-018-02/D-018-03/AD-018-27~33核心）"
description: |
  实现先干后验模式(post_action_verification)：auto_guard操作执行后由后验检查验证实际效果。
  derive_rbac_roles.py：从GOV-AI-001自动派生rbac_roles.yaml，消除手动复制=消除漂移。
  Agent身份模型的完整扩展：
  - D-018-27 对抗韧性与OWASP Agentic Top 10(ASI02-ASI06)+MAESTRO五层威胁建模
  - D-018-28 Agent目标完成驱动v.s.安全约束冲突(CVE-2026-21852 Agent自解除沙箱)
  - D-018-29 多Agent合谋检测(GroupGuard+博弈论建模)
  - D-018-30 虚假完成与欺骗检测(三维校验)
  - D-018-31 记忆来源追踪(OWASP ASI06 Vector Memory投毒)
  - D-018-32 TOCTOU文件竞态+编码绕过(symlink解析+Base64/Hex/URL decoding)
  - D-018-33 Canary权限灰度+权限变更自动回归
  覆盖§2.11/§2.12/§2.13的全部内容。
priority: "P0"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
  - "D:\\ZephyrAlpha\\docs\\01_policies_and_standards\\meta\\metadata-registry.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\identity.py"
  - "D:\\ZephyrAlpha\\docs\\_domain-governance\\GOV-AI-001\\index.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\post_action_verifier.py"
    description: "PostActionVerifier——auto_guard后验检查+实际效果vs预期对比+后验失败触发"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\derive_rbac_roles.py"
    description: "GOV-AI-001→rbac_roles.yaml自动派生器——确定性YAML生成+哈希对比"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\adversarial_resilience.py"
    description: "对抗韧性模块——OWASP Agentic Top10+MAESTRO五层+Agent自解除沙箱防护+激励审计(IncentiveScore)"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\multi_agent_collusion_detector.py"
    description: "多Agent合谋检测——GroupGuard+博弈论均衡偏离+涌现行为检测"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\false_completion_detector.py"
    description: "虚假完成检测——(声称目标↔实际文件变更↔预期输出)三维校验"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\memory_provenance_guard.py"
    description: "记忆来源追踪——RAG/Vector Memory写入源身份+来源审计+隔离"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\toctou_guard.py"
    description: "TOCTOU防护——symlink解析+inode校验+openat原子操作+编码绕过预解码"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\canary_rollout_manager.py"
    description: "Canary权限灰度发布——1%采样/24h观察/自动全量/异常回滚"
  - path: "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_post_action.py"
    description: "先干后验测试"
  - path: "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_derive_rbac.py"
    description: "派生器测试——一致性/确定性/冲突检测"
  - path: "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_adversarial.py"
    description: "对抗韧性/合谋/虚假完成/记忆投毒/TOCTOU/Canary测试合集"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\post_action_verifier.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\derive_rbac_roles.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\adversarial_resilience.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\multi_agent_collusion_detector.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\false_completion_detector.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\memory_provenance_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\toctou_guard.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\canary_rollout_manager.py"
  - "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_post_action.py"
  - "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_derive_rbac.py"
  - "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_adversarial.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号"
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "强制Pydantic V2"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
    reason: "§2.11先干后验/§2.12派生/§2.13身份模型+决策D-018-02/03/27~33"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 25000
timeout_minutes: 90

acceptance_criteria:
  - "post_action_verifier:auto_guard操作执行后验证实际效果vs预期→失败自动回滚"
  - "derive_rbac_roles:GOV-AI-001变更→自动派生→哈希对比→CI验证"
  - "IncentiveScore=(实际完成度×安全合规度)/(声称完成度+1)→偏离>20%=告警"
  - "GroupGuard:跨Agent通信图分析+博弈论均衡偏离检测"
  - "false_completion:三维校验(声称↔变更↔预期)自动触发"
  - "TOCTOU:symlink追踪+inode校验+openat O_NOFOLLOW"
  - "Canary:新权限自动进入1%采样模式→CI验证→自动推进"

rollback_instructions: |
  1. 删除本卡创建的所有8个核心.py文件和3个测试文件
  2. 如派生脚本生成了rbac_roles.yaml变体——恢复原始版本

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

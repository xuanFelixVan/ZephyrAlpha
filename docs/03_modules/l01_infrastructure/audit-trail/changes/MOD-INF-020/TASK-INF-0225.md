---
task_id: "TASK-INF-0225"
source_blueprint: "MOD-INF-020"
source_section: "蓝图 §2.11 渐进信任分数（决策 D-020-17）+ §2.10 委托链审计（决策 D-020-16）"

title: "实现渐进信任引擎 + 委托链审计器"
description: |
  实现 `src/zephyr/audit_trail/trust_score.py` 中的 `TrustScoreEngine`：
  - DEFAULT_SCORE=0.6 / SUCCESS_INCREMENT=0.001 / ANOMALY_DECREMENT=0.2 / DAILY_DECAY=0.005
  - update(agent_did, event_type, anomaly_score) → 新分数
  - current(agent_did) → 当前分数 / trend(agent_did, days) → 7日趋势
  - trust_score < 0.5 → auto_demotion 触发 → 权限自动降级

  实现 `src/zephyr/audit_trail/delegation.py` 中的 `DelegationChainAuditor`：
  - validate_chain()：深度 ≤ 3 + 权限逐级缩小 + 链内 DID 均有效
  - detect_chain_break()：中间 DID 不可解析或权限异常放大
  - trace_root()：追溯到委托链根 Agent → 最终责任归属
  落地 D-020-17 + D-020-16。覆盖 R14/R22。覆盖盲点 B23/B24/B39。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\trust_score.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\delegation.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\models.py"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\trust_score.py"
    description: "TrustScoreEngine——增量/衰减/趋势/自动降级"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\delegation.py"
    description: "DelegationChainAuditor——链验证/断裂检测/根追溯"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_trust_score.py"
    description: "信任分数测试——增量/衰减/demotion"
  - path: "D:\\ZephyrAlpha\\tests\\audit_trail\\test_delegation.py"
    description: "委托链测试——深度3/权限缩小/断裂检测"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\trust_score.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\audit_trail\\delegation.py"
  - "D:\\ZephyrAlpha\\tests\\audit_trail\\test_trust_score.py"
  - "D:\\ZephyrAlpha\\tests\\audit_trail\\test_delegation.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"

applicable_rules:
  - module_id: "GOV-AI-001"
    section: "全篇"
    reason: "AI 自治信任模型"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\audit-trail\\blueprint.md"
    reason: "§2.11——TrustScoreEngine + §2.10 DelegationChainAuditor + D-020-16/17"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 8000
timeout_minutes: 50

acceptance_criteria:
  - "TrustScore: 10次成功=0.6+0.01=0.61, 1次anomaly=dec 0.2, 7天无活动=dec 0.035"
  - "TrustScore < 0.5 → auto_demotion → agent marked PENDING_REVIEW"
  - "TrustScore.trend(7) → [(day1,0.6),(day2,0.601),...]"
  - "Delegation: depth=4 → invalid / chain broken → P0 alert"
  - "Delegation: parent=all_ops, child=read_only → valid (权限缩小)"
  - "Delegation: parent=read_only, child=all_ops → invalid (权限放大)"

rollback_instructions: |
  1. 删除 trust_score.py / delegation.py 内容
  2. 删除对应测试文件

depends_on:
  - "TASK-INF-0207"
blocked_by: []

status: "created"

tags_fn:
  - "infra"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "experimental"
tags_mo:
  - "MOD-INF-020"

completed_gates: []
blocked_gates: {}

artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "semi_autonomous"
autonomy_checklist: []
---

---
task_id: "TASK-INF-0A24"
source_blueprint: "MOD-INF-018"
source_section: "蓝图 §6 — 风险与缓解 (R1~R20)"

title: "实现agent-rbac 20项风险缓解措施（R1~R20）"
description: |
  实现蓝图§6定义的20项风险的自动化缓解措施（严格对标蓝图原文）：
  R1: auto_guard后验失败率高（频繁自动回滚影响效率）→统计后验失败率，持续优化auto_guard规则；失败率>20%降级为blocked
  R2: 权限配置漂移（rbac_roles.yaml与GOV-AI-001不一致）→CI门禁校验一致性+derive_rbac_roles.py自动派生
  R3: 性能开销（七层检查增加延迟）→每层预算严格管控；权限结果缓存(TTL=5min)+L1 always_allow跳过L3-L4详细检查
  R4: 多IDE身份冲突（同一文件被不同IDE的Agent同时修改）→文件锁+乐观并发控制+drift detector实时检测
  R5: L4 Sequence Guard误报（合法操作序列被误判为攻击）→Owner白名单机制；序列时间窗口可配置；统计误报率持续优化
  R6: Agent Maturity升级过慢（严重限制AI效率）→自动升级到L2 Junior(L3+仍需审核)；开放Owner手动加速升级
  R7: Kill Switch误触发（正常批量操作被熔断）→触发阈值可配置；自动解除cooldown机制；Owner可手动解除
  R8: Engine崩溃时全部blocked（系统完全不可用）→L0独立可快速恢复；允许Owner配置紧急白名单(临时绕过Engine)
  R9: AI绕过权限系统（写入不可变核心路径）→L0硬编码保护路径；OS级文件权限兜底(L2b沙箱ACL)；pre-commit检查文件完整性
  R10: 权限配置越滚越复杂（1人无法维护）→GOV-AI-001单点维护+自动派生+影响分析可视化+D-018-19自动维护中规则自我修剪
  R11: 横向越权（Agent伪造其他Agent身份）→SessionToken签名校验(HMAC-SHA256)+AgentIdentityVerifier+跨Session伪造检测(D-018-13)
  R12: 冷启动裸奔（权限配置加载前Agent已操作）→ColdStartLock——启动时全局拒绝直到校验通过(D-018-14)
  R13: 审计系统被投毒（噪音攻击淹没真实告警）→告警信噪比监控+signal_noise_attack熔断触发器+异常密度突增自动降权(§2.2)
  R14: Agent自我复制风暴（绕过Maturity限制）→Agent创建权管控+权限遗传衰减+agent_spawn_storm熔断器(D-018-16)
  R15: 权限缓存陈旧（紧急收紧后旧ALLOW仍生效）→推送驱动缓存失效——max_latency=100ms替代TTL=5min(D-018-17)
  R16: 降级攻击（Agent故意触发Partial Failure绕过L4）→降级源检测——同一Agent触发的降级→立即BLOCKED(§2.3+D-018-17联动)
  R17: 熔断器DDoS（恶意Agent触发Kill Switch瘫痪全局）→熔断源隔离——单Agent触发仅阻断该Agent，多Agent触发才全局熔断(§2.2)
  R18: Agent间隐式合谋（文件系统Covert Channel绕过单Session护栏）→跨Session关联检测+inter_agent_communication规则(§2.7 cross_session_correlation)
  R19: 第三方包供应链攻击（Agent安装恶意依赖）→package_install白名单+blocked_packages:["*"]默认拒绝(§2.6 D-018-09扩展)
  R20: Owner缺席时无人能干预（auto_guard操作悬空）→OwnerAbsencePolicy——超时→保守模式→所有auto_guard降级为blocked(§3 ownership_absence_policy.yaml)
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\permission_guard.py"

downstream_outputs:
  - path: "D:\ZephyrAlpha\src\zephyr\l01_infrastructure\code_dedup_engine\risk_mitigator.py"
    description: "RiskMitigationEngine——R1~R20 20项风险自动缓解策略+触发条件+health指标"
  - path: "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_risk_mitigation.py"
    description: "风险缓解测试——验证每项风险触发→对应缓解措施生效"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\risk_mitigation.py"
  - "D:\\ZephyrAlpha\\tests\\agent_rbac\\test_risk_mitigation.py"

forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_rbac\\immutable_core.py"
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"

applicable_rules:
  - module_id: "PS-STD-001"
    section: "§5"
    reason: "任务卡编号"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-rbac\\blueprint.md"
    reason: "§6 R1~R20 20项风险清单+缓解策略+对标CISA/OWASP/NIST AI RMF"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 20000
timeout_minutes: 90

acceptance_criteria:
  - "risk_mitigation注册全部20项风险(R1-R20)——严格按蓝图表格内容"
  - "每项风险定义:risk_id/description(蓝图原文)/probability/impact/mitigation(蓝图原文)/associated_decision"
  - "R1:后验失败率监控+失败率>20%操作自动降级为blocked"
  - "R2:CI门禁自动对比rbac_roles.yaml vs GOV-AI-001→不一致阻断"
  - "R5:L4白名单机制+误报率统计+时间窗口可配置"
  - "R11:SessionToken HMAC-SHA256签名+跨Session伪造检测生效"
  - "R12:ColdStartLock→权限加载前所有check()返回GLOBAL_BLOCKED"
  - "R15:推送驱动缓存失效→权限变更→100ms内清除旧ALLOW"
  - "R16:降级源检测→同一Agent触发降级→立即BLOCKED"
  - "R20:OwnerAbsencePolicy→超时→保守模式→auto_guard降级blocked"

rollback_instructions: |
  1. 删除 D:\ZephyrAlpha\src\zephyr\agent_rbac\risk_mitigation.py
  2. 删除 D:\ZephyrAlpha\tests\agent_rbac\test_risk_mitigation.py

depends_on:
  - "TASK-INF-0A13"
blocked_by: []

status: "done"

tags_fn:
  - "infra"
  - "security"
  - "risk"
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

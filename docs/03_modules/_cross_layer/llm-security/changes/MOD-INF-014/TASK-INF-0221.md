---
task_id: "TASK-INF-0221"
source_blueprint: "MOD-INF-014"
source_section: "§27 防御成熟度评估模型 + §28 LSG自身安全与韧性 + §29 凭据生命周期"
title: "LSG防御成熟度模型+自身安全韧性+凭据生命周期管理——三大运维安全系统"
description: |
  实现三大运维安全系统:
  §27: DefenseMaturityModel (5级成熟度: Initial→Managed→Defined→Quantitatively Managed→Optimizing)
  + 五维成熟度雷达(策略/检测/响应/审计/自动化)
  §28: LSGSelfSecurity & Resilience: self-audit rules + 内部攻击面缩减 + 韧性自修复 + 穿透测试项目
  + 自我隔离策略(独立python环境/LSGHarden/LSGSandbox)+ 敏感面缩减 + LSG依赖安全策略
  §29: CredentialLifecycleManager: 凭据四阶段(生成→分发→使用→轮换→废止)+ 自动轮换(7天/30天/90天)
  + 异常检测 + 失效处理
priority: "P2"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\_cross_layer\\llm-security\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\maturity_and_resilience.py"
    description: "防御成熟度+LSG韧性+凭据生命周期——三大运维系统"
  - path: "D:\\ZephyrAlpha\\tests\\llm_security\\test_maturity_and_resilience.py"
    description: "三大运维系统验证测试——15条用例"
allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\llm_security\\self_protection\\maturity_and_resilience.py"
  - "D:\\ZephyrAlpha\\tests\\llm_security\\test_maturity_and_resilience.py"
forbidden_touch: []
applicable_rules:
  - module_id: "ADR-0040"
    section: "全篇"
    reason: "Pydantic V2"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\_cross_layer\\llm-security\\blueprint.md"
    reason: "§27+§28+§29"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules: ["M1","M3"]
estimated_tokens: 12000
timeout_minutes: 60
acceptance_criteria:
  - "DefenseMaturityModel: 5级成熟度+五维雷达评分+assess_current_maturity() + generate_improvement_roadmap()"
  - "LSGSelfSecurity: self-audit 10项规则+ 韧性自修复 + 穿透测试12项 + SELF_TEST_GUARD checklist"
  - "LSGIsolationStrategy: 独立python环境 + LSGHarden(软/硬/资源/网络/文件5维) + LSGSandbox"
  - "SensitiveSurfaceReducer: file_prefix_filter_rule + secret_mask_patterns + UNTRUSTED_USER_WARNING"
  - "LSGDependencySecurity: isolation_level枚举 + dependency_lock_hardening"
  - "CredentialLifecycleManager: generate/distribute/use/rotate(7/30/90d)/revoke 五阶段"
  - "CredentialAnomalyDetector: 使用频率/时间/位置/权限四维异常"
  - "Pydantic V2: MaturityScore/CredentialMetadata/ResilienceReport"
  - "15条测试全部通过"
rollback_instructions: |
  1. 删除 maturity_and_resilience.py + test_maturity_and_resilience.py
depends_on: ["TASK-INF-0201"]
blocked_by: []
status: "created"
tags_fn: ["security","operations"]
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo: ["MOD-INF-014"]
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---

# 目标

实现 LSG 防御成熟度评估、自身安全韧性、凭据生命周期三大运维安全系统。

## 执行步骤

### 做
1. 实现 DefenseMaturityModel——5级+五维雷达
2. 实现 LSGSelfSecurity——自审计+韧性+穿透测试+隔离策略+敏感面缩减+依赖安全
3. 实现 CredentialLifecycleManager——五阶段凭据管理
4. 编写 15 条测试

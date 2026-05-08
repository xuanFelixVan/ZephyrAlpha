---
task_id: "TASK-INF-0114"
source_blueprint: "MOD-INF-002"
source_section: "蓝图 §5.2 设计原则 + §5.6 CI/CD 部署自动化流水线 + §5.7 AI施工自治回路"
title: "§5.2 设计原则落地 + §5.6 CI/CD六门流水线实现 + §5.7 AI施工Session生命周期"
description: |
  落地蓝图核心设计原则和自动化基础设施。
  §5.2 设计原则：
  Crash-Only→系统不依赖优雅关闭——每次停止=crash→恢复=重启+
  Structured Concurrency→asyncio.TaskGroup管理1500+模块——全部完成或全部取消，0孤儿协程+
  Fail-Closed→SecretsManager/ErrorHandler不可用时拒绝操作而非放行+
  Immutable Events→RI-13 EventStore事件不可修改/不可删除+
  Progressive Disclosure→告警按Owner注意力预算分级——实时仅CRITICAL，其余汇总。
  §5.6 CI/CD六门流水线：
  代码提交→①静态分析门(mypy+ruff+Semgrep)→②测试门(单元+Contract Pact+Property-Based Hypothesis)→
  ③DryRun门(RI-14 sandbox预演→diff报告→一致性验证套件+CrossSessionLoopDetector)→
  ④Approve门(AutoDecide RPN<50+≤3模块+≤$0.10 OR Owner审批)→
  ⑤部署门(Canary 1%→100%+健康监控→错误率>5% OR P99>2x基线→自动回滚)→
  ⑥生产验证(Smoke Test+错误率基线对比+自动追加ADR)。
  §5.7 AI施工Session生命周期：启动(AIContextBuilder+TokenBudgetCheck+锁定工作区)→施工循环(AI提交→SelfReview→LintFix→TestGen→SelfSimulate)→
  提审(diff报告+DryRun预测+费用预估→AutoDecide)→结束(Session Log+ADR+解锁+更新FamiliarityScore)。
priority: "P0"
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
downstream_outputs:
  - path: "D:\\ZephyrAlpha\\.github\\workflows\\ci.yml"
    description: "CI/CD六门流水线——静态分析→测试→DryRun→审批→Canary→生产验证"
  - path: "D:\\ZephyrAlpha\\infra\\deploy\\canary.sh"
    description: "Canary部署脚本——1%→10%→50%→100%渐进+错误率>5%自动回滚"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\ai_session_manager.py"
    description: "AI施工Session生命周期管理——启动/施工循环/提审/结束"
allowed_touch:
  - "D:\\ZephyrAlpha\\.github\\workflows\\ci.yml"
  - "D:\\ZephyrAlpha\\infra\\deploy\\canary.sh"
  - "D:\\ZephyrAlpha\\src\\zephyr\\l01_infrastructure\\ai_session_manager.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
  - "D:\\ZephyrAlpha\\src\\zephyr\\shared\\**\\*.py"
applicable_rules:
  - module_id: "MOD-INF-002"
    section: "§5.2"
    reason: "五大设计原则——Crash-Only/StructuredConcurrency/Fail-Closed/ImmutableEvents/ProgressiveDisclosure"
  - module_id: "MOD-INF-002"
    section: "§5.6"
    reason: "CI/CD六门流水线——对标GitHub Actions/ArgoCD/Flagger"
  - module_id: "MOD-INF-002"
    section: "§5.7"
    reason: "AI施工Session生命周期——对标Aider/Copilot Chat/Cursor Agent"
context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\runtime-integration\\blueprint.md"
    reason: "§5.2 设计原则 + §5.6 CI/CD流水线架构 + §5.7 AI施工Session生命周期"
assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M2"
  - "M3"
estimated_tokens: 25000
timeout_minutes: 90
acceptance_criteria:
  - "§5.2 Crash-Only: 系统不依赖优雅关闭——kill -9 后重启可从SQLite重建状态"
  - "§5.2 Structured Concurrency: asyncio.TaskGroup 验证——子任务完成/取消无孤儿协程"
  - "§5.2 Fail-Closed: SecretsManager init失败→拒绝启动而非降级放行"
  - "§5.6 CI/CD: 六门流水线 GitHub Actions YAML——mypy strict+ruff+Semgrep→pytest+Hypothesis+Pact→DryRun→Canary→生产验证"
  - "§5.6 Canary: 错误率>5%→自动回滚脚本已就绪"
  - "§5.7 AI Session: 启动→Token Budget Check→工作区锁定→施工循环→SelfSimulate→提审→Session Log"
  - "§5.7 AI Session: 同一模块不能被两个session同时修改（工作区锁定）"
rollback_instructions: |
  1. 删除 .github/workflows/ci.yml
  2. 删除 infra/deploy/canary.sh
  3. 删除 l01_infrastructure/ai_session_manager.py
  4. 如 .github/workflows/ / infra/deploy/ 目录变为空→删除目录
depends_on: []
blocked_by: []
status: "created"
tags_fn:
  - "infra"
  - "security"
  - "observability"
tags_ly: "l01_infrastructure"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "MOD-INF-002"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---

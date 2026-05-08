---
task_id: "TASK-SYS-0023"
source_blueprint: "SYS-MASTER-001"
source_section: "§31 迁移策略 + §32 术语表 + §33 Anti-Patterns"

title: "迁移策略(7维 Risk Assessment) + 22术语Glossary + Anti-Patterns(AP1/AP2/AP3 3防护)体系"
description: |
  将 SYS-MASTER-001 §31 迁移策略 + §32 术语表 + §33 Anti-Patterns 反模式三合一落地。
  §31: Migration 7维——ISSUE TRACKING→RISK ASSESSMENT→ROLLBACK PLAN→STAGING→
  PILOT→FULL ROLLOUT→POSTMORTEM。每维 predecessor/successor+confidence_threshold。
  逐模块逐个移动(1 Module at a time)，对齐 Canary Rollout(§21)。
  §32: Glossary 22术语——Alpha/Backtest/Benchmark/C-Track/B-Track/DMA/DMA-B/DCA/
  ECN/FIX/HFT/IOC/LP/Liquidity/MDD/MTF/NDD/Paper/P&L/SLD/SLI/SLO/TP/SL/Vol/Sharpe/ETF。
  §33: 3 Anti-Patterns——AP1-ProceedWithoutLock(不检查lock_files.py直接写文件)/
  AP2-PrematureOptimization(过早优化→ benchmark before optimize)/
  AP3-SilentIgnore(异常静默吞噬→mandatory logging。no `pass` in except blocks)。
  本卡搭建 migration_strategy.py + glossary_matrix.py + anti_pattern_guard.py。
priority: "P1"

upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"

downstream_outputs:
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\migration_strategy.py"
    description: "§31 7维迁移——Issue→Risk→Rollback→Staging→Pilot→Full→Postmortem 状态机"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\glossary_matrix.py"
    description: "§32 22术语——term/definition/domain/acronym 标准化字典"
  - path: "D:\\ZephyrAlpha\\src\\zephyr\\governance\\anti_pattern_guard.py"
    description: "§33 AP1(lock bypass guard)/AP2(premature opt)/AP3(silent ignore detector via AST)"

allowed_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\migration_strategy.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\glossary_matrix.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\governance\\anti_pattern_guard.py"
forbidden_touch:
  - "D:\\ZephyrAlpha\\src\\zephyr\\l0*\\**\\*.py"

context_assembly_manifest:
  - file_path: "D:\\ZephyrAlpha\\docs\\03_modules\\_sys-master\\blueprint.md"
    reason: "§31 Migration 7维 + §32 22Term Glossary + §33 AP1/AP2/AP3 Anti-Patterns"

assigned_model: "deepseek"
assigned_pipeline: "A"
pipeline_modules:
  - "M1"
  - "M3"
estimated_tokens: 16000
timeout_minutes: 45

acceptance_criteria:
  - "MigrationPhase 7 成员——each predecessor/successor/confidence / 1-module-at-a-time alignment§21"
  - "22 GlossaryEntry: term/definition/domain/acronym ← exact mapping to §32 terms"
  - "AP1 guard decorator: check_lock_before_write→Assert not skipping lock_protocol. AP2: benchmark_before_optimize check. AP3: AST visitor scan `except: pass`→CI reject"

rollback_instructions: |
  git rm src/zephyr/governance/migration_strategy.py glossary_matrix.py anti_pattern_guard.py
  从 script_manifest.yaml 移除注册

depends_on:
  - "TASK-SYS-0004"
blocked_by: []
status: "done"
tags_fn:
  - "governance"
tags_ly: "cross_layer"
tags_md: "deepseek"
tags_st: "active"
tags_mo:
  - "SYS-MASTER-001"
completed_gates: []
blocked_gates: {}
artifact_paths: []
audit_findings: []
ke_entries: []
ai_autonomy_level: "supervised"
autonomy_checklist: []
---

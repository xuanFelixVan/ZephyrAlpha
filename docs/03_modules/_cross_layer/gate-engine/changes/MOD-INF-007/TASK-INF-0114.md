---
task_id: TASK-INF-0114
status: planned
priority: P1
severity: high
module_id: MOD-INF-007
phase: 1
category: guardrail
effort_estimated: 3h
effort_actual: null
assigned_to: null
reviewer: null
approver: null
source_section: §七
reference_docs:
  - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
upstream_files:
  - D:\ZephyrAlpha\src\zephyr\gates\gate_engine.py
downstream_outputs:
  - D:\ZephyrAlpha\src\zephyr\gates\gate_engine.py
acceptance_criteria:
  - "AC-AP1: 禁止绕门运行——gate_engine.evaluate()强制调用→在Orchestrator层不可跳过→AP1"
  - "AC-AP2: 禁止硬编码规则绕过——必须YAML中声明entry_conditions，不写在Pythonif链→AP2"
  - "AC-AP3: 禁止BLOCK后继续——evaluate返回BLOCK→下级gate不再执行=立即return→AP3"
  - "AC-AP4: 禁止YAML任意外部——yaml.safe_load only（蓝图29.5yaml加固）→AP4"
  - "AC-AP5: 禁止未授权override使用——override gate需要EmergencyOverrideGate()→AP5"
  - "AC-AP6: 禁止关健gate禁用——不enabled=False禁止通过操作者绕过→AP6"
  - "AC-AP7: 禁止关中断 所有检查=破坏audit chain——G6-G7 full gate per commit→AP7"
rollback_instructions:
  - "禁用AP guardrail→所有gate回到pass-through(all=GATEPASS)mode"
created_at: 2026-05-06T23:48:00Z
updated_at: 2026-05-07T00:34:00Z
closed_at: null
dependencies:
  - TASK-INF-0101
  - TASK-INF-0104
blocked_by: [TASK-INF-0101, TASK-INF-0104]
blocks: []
tags:
  - gate-engine
  - anti-patterns
  - §七
  - AP1-AP7
  - guardrail
  - blueprint-v0.5.0
version: 2.0.0
change_log: |
  v2.0.0 (2026-05-07): 二次核查修正——AP1-AP7与蓝图§七力量对齐。
  v1.0.0 (2026-05-06): 初始创建（修正以前作废）
context_assembly_manifest:
  documents:
    - D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md
  sections:
    - §七 Anti-Patterns 与禁止行为
  keywords:
    - anti-patterns
    - AP1-AP7
    - guardrail
    - blueprint-v0.5.0
  ai_reads_for_inference: true
---

# TASK-INF-0114: AP1-AP7 反模式防护实现（v2.0.0 修正版）

蓝图 §七 定义的 7 条门禁场景绝对禁止行为：

| AP | 反模式 | 防卫实现 |
|----|--------|---------|
| AP1 | 绕过门控直接执行 | GateEngine.evaluate()在Orchestrator层强制——跳过=违规 |
| AP2 | Pythonif硬编码(代替YAML) | entry_conditions优先→gate策略都由yaml驱动 |
| AP3 | Block之后继续→执行 | evaluate！Block→短路return:不再执行任务 |
| AP4 | YAML任意外部输入→未safe_load | yaml.safe_load + YAML不要引let外部注入 |
| AP5 |未授权使用override —| EmergencyOverrideGate 24h双签+PGP→访问 |
| AP6 | 門禁disable绕过”——使    disabled →true | enabled:false→拒绝evaluate 那gate   = SKIP/ERROR信号 |
| AP7 | 不集全gate percommit→破坏 audit chain | G6.blueprint\+G7 per变更全门审查 |

## 回退方案

移除AP guard →全部by pass gate

## 验收标准

| # | 标准 |
|---|------|
| AC-AP1 | Orchestrator层不可跳过evaluate() |
| AC-AP2 | 全部门禁规则由YAML entry_conditions驱动，非Python if/else |
| AC-AP3 | FAIL/CRITICAL_FAIL→短路，后续gate不再执行 |
| AC-AP4 | yaml.safe_load only，含大小/深度/超时限制 |
| AC-AP5 | EmergencyOverrideGate 24h双签+PGP验证 |
| AC-AP6 | enabled=false的gate返回SKIP并记录告警 |
| AC-AP7 | G6 blueprint+G7 全量门审查 = audit chain完整 |

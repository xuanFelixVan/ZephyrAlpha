---
task_id: TASK-INF-0217
task_title: "§19第十四轮审计-AgentTrace可观测性+SkillsBench效能校准+RAGEN自进化保真度+Token经济学+AB实验+Walkthroughs+SoloTriage + D-019-71~77"
parent_ticket: TASK-INF-0216
module: MOD-INF-019
blueprint_file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
blueprint_sections: ["§19 第十四轮审计-AgentTrace+SkillsBench+RAGEN+Tokenomics+AB+Walkthroughs+SoloTriage"]
status: backlog
priority: P1
type: blind_spot_closure
estimated_effort: "14h"
assignee: implementer-skill
reviewer: governor-skill
created_date: 2026-05-06
target_completion_date: 2026-05-08
dependencies:
  - TASK-INF-0216
decisions:
  - D-019-71
  - D-019-72
  - D-019-73
  - D-019-74
  - D-019-75
  - D-019-76
  - D-019-77
tags:
  - agenttrace
  - skillsbench
  - ragen
  - tokenomics
  - ab-testing
severity: high
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\agent_observability.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_efficacy_calibrator.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\self_evolution_fidelity_gate.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_tokenomics.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_ab_test.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_scenario_walkthrough.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\solo_maintenance_triage.py"
acceptance_criteria:
  - "B143-B149 共 7 个盲点全关闭"
  - "AgentTrace 3-Surface Telemetry (D-019-71): Operational/Cognitive/Contextual三表面 + Unified Envelope Schema + eBPF span完整率32.8%→99.1% + 跨表面因果分析 trace_id串联"
  - "SkillsBench Anti-Regression Gate (D-019-72): A/B/C三条件测试(Baseline/Curated/SelfGen) + Δ<0→BLOCK + Δ<+3pp→Canary only + 2-3模块聚焦Skill优于全面文档 + Domain-Specific Baselines(Healthcare≥30pp/Finance≥15pp/SWE≥3pp)"
  - "RAGEN EchoTrapDetector (D-019-73): reward_variance_collapse/gradient_spike/policy_entropy_decay/output_homogeneity四信号 + Human-in-the-Loop + Safe Sandbox Evolution + Collapse Recovery Protocol"
  - "Tokenomics (D-019-74): SDLC 6-stage mapping(Code Review=59.4%→20%) + Communication Tax Reduction(53.9%→35%) + SkillTokenLedger + $50/day budget"
  - "A/B Experimentation (D-019-75): α=0.05/β=0.20 + Multi-Metric(primary/guardrail/secondary) + Significance Decision Matrix + P-hacking prevention"
  - "Walkthrough Scenarios (D-019-76): 3场景(Database Migration ATM/Portfolio VaR/ADR Creation) + per-ms Skill Fire Order + Failure Mode演练"
  - "Solo Maintenance Triage (D-019-77): 5-Tier(T0 auto-resolve→T4 emergency 5min SLA) + Progressive Automation Ladder(Phase 0-5 over 5+months) + Agent Destruction Radius Tier 0-3"
rollback_instructions: "批量回退7个Python文件"
context_assembly_manifest:
  blueprint_content: "§19 第十四轮审计——反向实证视角5小节: AgentTrace可观测性(B143) + SkillsBench效能校准(B144) + RAGEN自进化保真度(B145) + Token经济学(B146) + A/B实验+Walkthrough+SoloTriage(B147-149)"
  template_version: "task-card-template.md v1.0.0"
---

# TASK-INF-0217: 第十四轮审计盲点关闭

## 1. 任务描述

关闭 §19 第十四轮审计 B143-B149 共 7 个盲点，实现 D-019-71~77 七项设计决策。本轮从反向实证视角出发，用"什么会失败"而非"什么应该做"来寻找和修复盲点。

## 2. 关键实现

### AgentTrace 3-Surface Telemetry (D-019-71)
- **Operational**: method/arguments/return_value/duration_ms/status/exception
- **Cognitive**: prompt/completion/reasoning_segments(model/token_count/temperature)
- **Contextual**: http/sql/nosql/vector_search/fs_io interactions
- eBPF completion: SDK span 32.8%→eBPF 99.1%, latency ~2.4μs
- Dual-Path: Hot(Redis Streams→Grafana 1h) + Cold(Parquet/S3 forensic) + Compliance(Merkle)

### SkillsBench Efficacy (D-019-72)
- **Empirical finding**: 19% tasks REGRESS with Skills, self-generated Skills=ZERO benefit
- **Anti-Regression Gate**: Δ<0→BLOCK, 0≤Δ<+3pp→Canary only, Δ≥+3pp→PROMOTE
- **Focused Design**: 2-3 modules per Skill (not 10+ encyclopedia Skills)
- **Domain Baselines**: Healthcare≥30pp, Finance≥15pp, SWE≥3pp

### RAGEN EchoTrap Detector (D-019-73)
- 4 signals: reward_variance_collapse + gradient_spike + policy_entropy_decay + output_homogeneity
- EchoTrapScore > 0.7 → PAUSE self-evolution + inject external signal + human review
- Faithfulness check: perturbation test → if behavior unchanged → experience NOT faithfully used
- Collapse Recovery: revert to checkpoint + inject diversity noise + human reviews

### Solo Triage (D-019-77)
```
T0: AUTO-RESOLVE (<1%) — cache miss refill, transient timeout auto-retry
T1: AUTO-HEAL — schema validation fail→rollback+retry, circuit breaker auto-recovery
T2: AI-TRIAGE — AI analyzes, daily batch for human review
T3: HUMAN-REQUIRED (<4h) — efficacy regression, echo trap detected
T4: EMERGENCY (<5min) — Tier 2+ ops, prod DB write, kill-switch crossed
```

## 3. 验收标准

- [ ] B143-B149 全关闭
- [ ] D-019-71~77 全实现

## 4. 回滚说明

批量回退 7 个文件。

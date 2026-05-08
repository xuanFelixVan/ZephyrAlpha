---
task_id: TASK-INF-0219
task_title: "§21第十六轮审计-Security Vetting+Codebase Intelligence+MVP System (Self-Calibration收敛) + D-019-82~84"
parent_ticket: TASK-INF-0218
module: MOD-INF-019
blueprint_file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
blueprint_sections: ["§21 第十六轮审计-SecurityVetting+CodebaseIntelligence+MVP"]
status: backlog
priority: P1
type: blind_spot_closure
estimated_effort: "10h"
assignee: implementer-skill
reviewer: governor-skill
created_date: 2026-05-06
target_completion_date: 2026-05-08
dependencies:
  - TASK-INF-0218
decisions:
  - D-019-82
  - D-019-83
  - D-019-84
tags:
  - security-vetting
  - codebase-intelligence
  - mvp
  - self-calibration
severity: high
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_security_vetting.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\codebase_intelligence.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\mvp_skill_system.py"
acceptance_criteria:
  - "B154-B156 共 3 个盲点全关闭"
  - "Security Vetting (D-019-82): ZJU四层Trust Tiers(T3 Internal→T2 Trusted Third-Party→T1 Community Reviewed→T0 Untrusted零信任全隔离) + 26.1%漏洞率防御(Prompt injection/Command injection/Info exfiltration/Dependency audit预扫描) + Skill Security Metadata声明(trust_tier/source/last_audit/cve_scan/known_vulnerabilities) + CVSS≥7.0全层隔离"
  - "Codebase Intelligence (D-019-83): repowise四层结构化情报(L1 Dependency Graph/L2 Git History hotspots+Bus Factor/L3 Auto-Generated Docs/L4 ADR Index) + 11 MCP Tools(get_impact_analysis/find_similar_pattern/get_decision_rationale/trace_data_flow) + 27× Token节省/36%降本/89%少读文件"
  - "MVP System (D-019-84): Micro-Agent基线4文件夹(AGENTS.md+skills(3 Role)+tools+context+workspace) + Scaffold Phase出口标准1-afternoon build target + Over-Design Prevention三道门控(MVP需此吗/能Ship无此1月吗/社区广泛采用了吗) + 156盲点 Must-Have~25/Should-Have~50/Nice-to-Have~78三级分类 + 10×代码减少(complex 800 LOC→simple 75 LOC)"
rollback_instructions: "批量回退3个Python文件"
context_assembly_manifest:
  blueprint_content: "§21 第十六轮审计——自我校准收敛层面3小节: Security Vetting(B154) + Codebase Intelligence(B155) + MVP System(B156)，不扩张新维度而是对已有设计做实战化收敛"
  template_version: "task-card-template.md v1.0.0"
---

# TASK-INF-0219: 第十六轮审计盲点关闭

## 1. 任务描述

关闭 §21 第十六轮审计 B154-B156 共 3 个盲点，实现 D-019-82~84 三项设计决策。本轮进行"自我校准审计"——对已有 156 个盲点做实战化收敛，分 Must/Should/Nice 三级。

## 2. 关键实现

### Trust Tiers (D-019-82)
```
T3 INTERNAL: ZephyrAlpha internal, SkillForge K=3 consensus → full read/write/execute
T2 TRUSTED THIRD-PARTY: Verified publishers, signed packages → read+execute, write workspace only
T1 COMMUNITY REVIEWED: N+ reviews, security scan passed → read-only+sandboxed exec, NO write/net/fs
T0 UNTRUSTED: Unverified → NO execution, sandboxed read-only SKILL.md metadata only
Promotion: T0→1K shadow+full audit, T1→500 ops+2 reviews, T2→100 ops+manual sec review
```

### Four-Layer Intelligence (D-019-83)
```
L1 — DEPENDENCY GRAPH: bidirectional import graph, change impact, ownership
L2 — GIT HISTORY: hotspots/churn, authorship, co-change clusters, bug-introducing commits, Bus Factor
L3 — AUTO-GEN DOCS: function signatures+docstrings, module summaries, API surface catalog
L4 — ADR INDEX: structured decisions, rationale graph linked to code, trade-off map, timeline
11 MCP Tools: get_impact_analysis/find_similar_pattern/get_decision_rationale/trace_data_flow...
```

### MVP Gate (D-019-84)
```yaml
must_have_baseline: "~25 blind spots (core loading/routing/safety)"
should_have_optimize: "~50 blind spots (quality/monitoring/orchestration)"
nice_to_have_defer: "~78 blind spots (formal verification/green scheduling/optimization)"
mvp_proof: "Micro-Agent 4-folder → scaffold 3 Role Skills → 1 afternoon → system operational"
```

## 3. 验收标准

- [ ] B154-B156 全关闭
- [ ] D-019-82~84 全实现
- [ ] 156 盲点 Must/Should/Nice 三级分类完成

## 4. 回滚说明

批量回退 3 个文件。

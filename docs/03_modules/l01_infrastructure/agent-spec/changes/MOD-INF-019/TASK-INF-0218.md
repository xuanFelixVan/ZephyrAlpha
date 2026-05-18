---

task_id: TASK-INF-0218
task_title: "§20第十五轮审计-LLM Gateway+Vibe Coding Gate+Skill Construction+Skill Package + D-019-78~81"
parent_ticket: TASK-INF-0217
module: MOD-INF-019
blueprint_file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
blueprint_sections: ["§20 第十五轮审计-LLM Gateway+VibeQualityGate+SkillConstruction+Package"]
status: backlog
priority: P1
type: blind_spot_closure
estimated_effort: "12h"
assignee: implementer-skill
reviewer: governor-skill
created_date: 2026-05-06
target_completion_date: 2026-05-08
dependencies:
  - TASK-INF-0217
decisions:
  - D-019-78
  - D-019-79
  - D-019-80
  - D-019-81
tags:
  - llm-gateway
  - vibe-coding-quality
  - skill-construction
  - skill-package
severity: high
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\llm_gateway.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\vibe_coding_quality_gate.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_constructor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_packager.py"
acceptance_criteria:
  - "B150-B153 共 4 个盲点全关闭"
  - "LLM Gateway (D-019-78): LiteLLM/Microsoft Foundry/Kaman三层融合 + Adaptive Complexity Classification(lexical/syntactic/domain) + Cost/Quality/Balanced三模式路由 + Provider Abstraction(5 providers) + Graduated Circuit Breaker(CLOSED→DEGRADED→RECOVERING→OPEN) + Data-Zone Enforcement(CN/US/EU)"
  - "Vibe Coding Quality Gate (D-019-79): Sonar四类遗漏检测(Error Handling/Idempotency/Retries/Observability) + AI Pattern Detectors(Hallucinated APIs/Over-Engineered/Insecure Defaults) + Confidence Score 0-100 + Pre-Merge Gate"
  - "Skill Construction Reliability (D-019-80): MAD ≤200 LOC + K-Threshold Consensus Voting(K=3) + Red-Flag Detectors(5 patterns) + CI/CD Pipeline 8-step"
  - "Skill Package (D-019-81): agent-skill-npm-boilerplate + Multi-IDE Install/Uninstall Hooks(Trae/Cursor/Claude/RooCode) + Semantic Versioning + Private Registry(Verdaccio/GitHub Packages)"
rollback_instructions: "批量回退4个Python文件"
context_assembly_manifest:
  blueprint_content: "§20 第十五轮审计——实施落地层4小节: LLM Gateway(B150) + Vibe Coding Quality Gate(B151) + Skill Construction Reliability(B152) + Skill Package(B153)"
  template_version: "task-card-template.md v1.0.0"
blueprint_id: DOM-GOV-001
---


# TASK-INF-0218: 第十五轮审计盲点关闭

## 1. 任务描述

关闭 §20 第十五轮审计 B150-B153 共 4 个盲点，实现 D-019-78~81 四项设计决策。

## 2. 关键实现

### LLM Gateway (D-019-78)
- Adaptive Complexity Classification (Kaman-inspired): lexical+syntactic+domain features → neural classifier → ComplexityTier (L1/L2/L3)
- Model Tier: L1(complexity<0.3→Haiku/GLM-4-Flash $0.25/M) → L2(0.3-0.7→Sonnet/DeepSeek-V4 $3/M) → L3(>0.7→Opus/GPT-5 $15/M)
- Failover chain: primary(DeepSeek-V4)→fallback1(Sonnet-4.5)→fallback2(GPT-5)→last_resort(GLM-4-Plus)
- Data-Zone: CN→CN models only, US→US models, EU→EU models (GDPR)

### Vibe Coding Quality Gate (D-019-79)
```
D_O_001_error_handling: BLOCK if critical-path function lacks try/except
D_O_002_idempotency: WARN if state-mutating op without idempotency
D_O_003_retries: BLOCK if external call without proper backoff+jitter
D_O_004_observability: WARN if no structured log/span/metric
AI Confidence Score: <30→BLOCK, 30-60→WARN+sign-off, >60→PASS
Vibe Debt metric: accumulated unchecked AI code / total codebase, target <20%
```

### Skill Construction (D-019-80)
- MAD: 7 units (Metadata/Core/Scripts/References/Contract/Guardrails/IOSchema), each ≤200 LOC
- K-Threshold Consensus (K=3): 3/3 agree→auto-accept, 2/3→majority+annotation, 1/3→human review, 0/3→re-generate
- Red-Flags: Hero Pattern(claims ALL capabilities), Vacuum Pattern(<30% substance), Contradiction Pattern(internal conflict), Circular Reference(DAG cycle), Staleness(outdated refs)

### Skill Package (D-019-81)
```javascript
// install.js — postinstall hooks for multi-IDE
const idePaths = {
    'trae': '~/.trae/skills',
    'claude': '~/.claude/skills',
    'cursor': '~/.cursor/skills',
    'roocode': '~/.roocode/skills',
};
```

## 3. 验收标准

- [ ] B150-B153 全关闭
- [ ] D-019-78~81 全实现

## 4. 回滚说明

批量回退 4 个文件。
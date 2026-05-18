---

task_id: TASK-INF-0216
task_title: "§17-§18第十二三轮审计-MerkleAudit+Watermarking+Geofence+GreenScheduling+Topology+BCDR+WellKnownDiscovery+SchemaRegistry+NFR+Glossary + D-019-59~70"
parent_ticket: TASK-INF-0215
module: MOD-INF-019
blueprint_file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
blueprint_sections:
  - "§17 第十二轮审计-TamperEvident+Watermarking+DataSovereignty+GreenAgent"
  - "§18 第十三轮审计-Topology+BCDR+WellKnown+Schema+NFR+Glossary"
status: backlog
priority: P1
type: blind_spot_closure
estimated_effort: "12h"
assignee: implementer-skill
reviewer: governor-skill
created_date: 2026-05-06
target_completion_date: 2026-05-08
dependencies:
  - TASK-INF-0215
decisions:
  - D-019-59
  - D-019-60
  - D-019-61
  - D-019-62
  - D-019-63
  - D-019-64
  - D-019-65
  - D-019-66
  - D-019-67
  - D-019-68
  - D-019-69
  - D-019-70
tags:
  - merkle-audit
  - watermarking
  - geo-fence
  - green-scheduling
  - topology
severity: medium
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_merkle_audit.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_watermark.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_geofence.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_green_scheduling.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_topology.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_bcdr.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_wellknown.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_schema_registry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\blueprint_assumptions.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\glossary_generator.py"
acceptance_criteria:
  - "B131-B142 共 12 个盲点全关闭"
  - "§17.1 Merkle Audit Trail (D-019-59): Real-Time 5s window + Batch hourly公证 + External Root Store(Agent无写权限) + EU AI Act Art 12合规 + Tamper Detection via root mismatch"
  - "§17.2 Agent Watermarking (D-019-60): AgentMark三维维度(ToolChoice/ToolSubgoalOrder/ParamSampling) 16-32 bits/sequence + Statistical Detection p<0.001 + Anti-Spoofing"
  - "§17.3 Geo-Fence (D-019-61): Geo-Policy Token法域签名 + Region-Constrained Routing + Cross-Region Sub-Agent Decomposition"
  - "§17.4 Green Scheduling (D-019-62): IQ/C Intelligence-to-Carbon Ratio + L1-L3三级模型碳路由 + Green Window Batching + Semantic Carbon Caching ≥40%"
  - "§18.1 Skill Topology (D-019-63): 5种类型化依赖边(DATA/ORCHESTRATION/MUTUAL_EXCLUSION/SOFT_PREFERENCE/COMPOSITION) + DAG编译 + 有界故障传播O(d^h)"
  - "§18.2 BCDR (D-019-64): Triple-state replication(Short/Mid/Long-Term) + Multi-Region Active/Warm/Cold + RTO 60s + Self-Destruction Tier 0-3"
  - "§18.3 Well-Known Discovery (D-019-66): Cloudflare RFC /.well-known/agent-skills/ + $schema + SHA-256 digest"
  - "§18.4 Schema Registry (D-019-67): VaR_Result/FactorExposure formal type schema + SkillCard entity + Runtime SchemaValidator"
  - "§18.5 NFR+Glossary (D-019-69~70): Consolidated NFR Matrix 6维 + 100+术语表 + Auto-generated Glossary Pipeline + CI enforcement"
rollback_instructions: "批量回退10个Python文件"
context_assembly_manifest:
  blueprint_content: "§17(4小节: Merkle/Watemarking/Geofence/GreenScheduling) + §18(5小节: Topology/BCDR/WellKnown/Schema/NFR+Glossary)"
  template_version: "task-card-template.md v1.0.0"
blueprint_id: DOM-GOV-001
---


# TASK-INF-0216: 第十二十三轮审计盲点关闭

## 1. 任务描述

关闭 §17 第十二轮审计（4小节，B131-B134）和 §18 第十三轮审计（5小节，B135-B142）的全部盲点，实现 D-019-59~70。

## 2. 关键实现

### Merkle Audit Trail (D-019-59)
- Real-Time window: 5s batch → Merkle Tree → root published
- Batch hourly: 公证写入 external root store (Agent has NO write access)
- IETF Attestation: binary_logs chained/signed/encrypted
- Tamper Detection: root mismatch → mathematical proof of tampering

### Skill Topology DAG (D-019-63)
```yaml
dependency_edges:
  DATA_DEPENDENCY: "Skill A needs Skill B's output"
  ORCHESTRATION_DEPENDENCY: "Skill A triggers Skill B"
  MUTUAL_EXCLUSION: "Skill A and B cannot co-execute"
  SOFT_PREFERENCE: "Skill A prefers Skill B but can work alone"
  COMPOSITION: "Skill A = Skill B + Skill C combined"
bounded_failure: "O(d^h) where d=fanout, h=depth → << O(N)"
```

### BCDR (D-019-64)
```
Tier 0: Agent CANNOT self-modify (OS-level enforcement)
Tier 1: Read-only Skills → no blast radius
Tier 2: Write to app state → blast radius ≤ 1 module (human approval)
Tier 3: Modify infrastructure → blast radius ≤ 1 service (human+governor co-sign)
```

### Schema Registry (D-019-67)
- VaR_Result v1.2.0, FactorExposure v2.0.0, SkillCard entities
- Semver × Contract Version → breaking change detection at CI time
- Runtime Type Validation: SchemaValidator checks every inter-Skill message
- Schema-Aware Semantic Alignment: auto-convert v1.2.0↔v2.0.0

## 3. 验收标准

- [ ] B131-B142 全关闭
- [ ] D-019-59~70 全实现

## 4. 回滚说明

批量回退 10 个模块文件。
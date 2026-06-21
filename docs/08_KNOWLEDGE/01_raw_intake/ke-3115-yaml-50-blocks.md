---
module_id: KE-3014------50--blocks-000
title: YAML 代码块 (50+ blocks)
category: module_blueprint
---

# YAML 代码块 (50+ blocks)

YAML 代码块 (50+ blocks)
| Block | 位置 | 实现文件 |
|-------|------|---------|
| trigger_table | §2.2 | trigger_router.py |
| progressive_disclosure | §2.3 | skill_loader.py |
| skill_factory | §2.4 | skill_factory.py |
| skill_file_structure | §2.5 | skill_factory.py |
| skill_checkpoint | §3.2 | skill_executor.py |
| skill_feedback_loop | §3.3 | skill_executor.py |
| skill_rbac | §3.4 | skill_executor.py |
| skill_budget | §3.5 | skill_executor.py |
| skill_escalation | §3.7 | skill_executor.py |
| layer_expansion | §5.1 | phase_planner.py |
| evaluation_framework | §8 | skill_evaluator.py |
| SkillCard entity | §18.4/B139 | skill_schema_registry.py |
| TraceEnvelope | §19.1/B143 | agent_observability.py |
| sdcl_stages + providers | §19.4/B146,§20.1/B150 | skill_tokenomics.py, llm_gateway.py |
| omission_detectors + red_flags | §20.2/B151,§20.3/B152 | vibe_coding_quality_gate.py, skill_constructor.py |
| trust_tiers + security_metadata | §21.1/B154 | skill_security_vetting.py |
| nfr_matrix + glossary | §18.5/B141-142 | consolidated NFR + glossary_generator.py |
| assumptions/constraints/tradeoffs | §18.4/B140 | blueprint_assumptions.py |

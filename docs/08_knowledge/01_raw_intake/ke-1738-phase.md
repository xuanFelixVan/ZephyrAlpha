---
module_id: KE-1648---------phase-000
status: active
title: 2.1 文件创建清单（按Phase分组）
category: module_blueprint
ttl: permanent
doc_type: knowledge_entry
---

# 2.1 文件创建清单（按Phase分组）

2.1 文件创建清单（按Phase分组）

**Core (Phase 0-1)**
- skill_model.py, skill_loader.py, skill_executor.py, trigger_router.py
- skill-registry.yaml, skill_freshness.py

**Security & Evaluation (Phase test-infra + security)**
- skill_evaluator.py, skill_security.py, skill_canary.py
- skill_translator.py, skill_telemetry.py, skill_breakage_checker.py
- skill_kill_switch.py

**Lifecycle & Economics (Phase lifecycle)**
- skill_lineage.py, skill_economics.py, skill_lifecycle.py
- skill_postmortem.py, skill_gitops.py

**Compliance & KYA (Phase compliance)**
- skill_compliance.py, skill_kya.py, skill_sandbox.py
- skill_observability.py, skill_cross_model.py

**Advanced (Phase ontology/attention/idempotency/resilience)**
- skill_ontology.py, skill_prompt_opt.py, skill_attention.py
- skill_idempotency.py, skill_resilience.py, skill_shadow.py
- skill_contract.py, skill_learning.py, skill_feature_flags.py

**Observability & Quality (Phase model-evolution to discovery)**
- skill_model_evolution.py, skill_silent_failure.py, skill_explain.py
- skill_calibration.py, skill_context_isolation.py, skill_consensus.py
- skill_cognitive_preservation.py, skill_temperature.py
- skill_workflow.py, skill_durable.py, skill_prompt_cache.py
- skill_cache_provider.py, skill_knowledge_base.py
- skill_di.py, skill_guardrails.py, skill_team_optimizer.py
- skill_discovery.py

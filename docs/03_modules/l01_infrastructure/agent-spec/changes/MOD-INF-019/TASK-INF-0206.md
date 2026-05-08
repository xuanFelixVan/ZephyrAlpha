---
task_id: TASK-INF-0206
task_title: "§4文件组成落地——46个模块文件创建清单"
parent_ticket: TASK-INF-0201
module: MOD-INF-019
blueprint_file: "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
blueprint_sections: ["§4 文件组成"]
status: backlog
priority: P0
type: scaffolding
estimated_effort: "6h"
assignee: implementer-skill
reviewer: governor-skill
created_date: 2026-05-06
target_completion_date: 2026-05-07
dependencies:
  - TASK-INF-0201
tags:
  - file-composition
  - module-files
  - code-index
severity: high
upstream_files:
  - "D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md"
downstream_outputs:
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_executor.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\trigger_router.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_freshness.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_evaluator.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_security.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_canary.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_translator.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_telemetry.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_breakage_checker.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_kill_switch.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_lineage.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_economics.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_lifecycle.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_postmortem.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_gitops.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_compliance.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_kya.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_sandbox.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_observability.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_cross_model.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_ontology.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_prompt_opt.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_attention.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_idempotency.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_resilience.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_shadow.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_contract.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_learning.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_feature_flags.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_model_evolution.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_silent_failure.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_explain.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_calibration.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_context_isolation.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_consensus.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_cognitive_preservation.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_temperature.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_workflow.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_durable.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_prompt_cache.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_cache_provider.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_knowledge_base.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_di.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_guardrails.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_team_optimizer.py"
  - "D:\\ZephyrAlpha\\src\\zephyr\\agent_spec\\skill_discovery.py"
acceptance_criteria:
  - "§4 表格中列出的 46 个 .py 文件全部创建，含完整文件头（module/author/version）"
  - "脚本目录 skills/ 结构按 §2.5 规范创建"
  - "所有文件通过 Python syntax check"
rollback_instructions: "批量删除 src/zephyr/agent_spec/ 下除核心4文件外的所有文件"
context_assembly_manifest:
  blueprint_content: "§4 文件组成——46 个模块文件索引表"
  template_version: "task-card-template.md v1.0.0"
---

# TASK-INF-0206: 模块文件批量创建

## 1. 任务描述

根据 §4 文件组成表批量创建 Agent Spec 模块的 46 个 Python 文件。每个文件需含标准文件头、占位符骨架代码和对应的 docstring。

## 2. 实施方案

### 2.1 文件创建清单（按Phase分组）

**Core (Phase 0-1)**
- skill_model.py, skill_loader.py, skill_executor.py, trigger_router.py
- skill_registry.yaml, skill_freshness.py

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

### 2.2 文件头标准模板

```python
"""
MOD-INF-019: Agent Spec — {component_name}
Blueprint: D:\\ZephyrAlpha\\docs\\03_modules\\l01_infrastructure\\agent-spec\\blueprint.md
Author: factory-agent
Version: 0.1.0
"""
```

## 3. 验收标准

- [ ] 46 个文件全部创建且语法合法
- [ ] 目录结构完整
- [ ] 脚本目录 skills/ 结构正确

## 4. 回滚说明

```powershell
Remove-Item D:\ZephyrAlpha\src\zephyr\agent_spec\skill_*.py -Exclude skill_model.py,skill_loader.py -Force
```

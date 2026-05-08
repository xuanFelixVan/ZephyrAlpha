# CLAUDE.md — ZephyrAlpha Project Context for Claude
# v0.2.0 — 完整版，与 AGENTS.md + project_rules.md 对齐

## Project Identity
- **Project:** ZephyrAlpha — AI-driven software engineering platform
- **Version:** 0.14.0
- **Python:** 3.12+
- **Pydantic:** V2 (use_enum_values=True)

## Architecture Overview
- `src/zephyr/l01_infrastructure/` — Infrastructure layer (code dedup, A2A protocol, agent RBAC)
- `src/zephyr/governance/` — Governance domain (8 modules, GCT contracts)
- `src/zephyr/pipeline/` — Dual-track pipeline (M1-M11, DeepSeek/GLM/Claude)
- `src/zephyr/gates/` — Gate Engine (19 gate configs, circuit breaker, drift detection)
- `src/zephyr/kb/` — Knowledge Base (UnifiedMemoryAPI, ChromaDB, VMS bridge)
- `src/zephyr/mcp/` — MCP Servers (9 servers, gateway, RBAC, rate limiting)
- `src/zephyr/feedback_loop/` — FLE (collect→detect→diagnose→act→verify)
- `src/zephyr/context_engine/` — Context Engine (compression, RAG, token budget)
- `src/zephyr/orchestrator/` — Task Queue + Trigger Router
- `src/zephyr/agent_spec/` — 12 Domain Skills + 3 Role Skills + LLM Gateway
- `src/zephyr/vector_memory/` — VMS (8 collections, HybridRetriever, BGE-M3)
- `src/zephyr/shared/` — EventBus + ContractBus + API_INDEX + Skill Registry

## CBAC Capability Boundaries (5 Rules)
1. **write_src** — 8 AI-Modifiable layers + 8 kb files (deny: 4 Immutable + 2 Human-Gated + 6 cross-cut)
2. **write_script** — Only `validate_truth_source_cascade.py` (deny: all other governance scripts)
3. **write_rules** — Empty (deny: .cursor/rules + .trae/rules)
4. **write_docs** — docs/08_knowledge + drafts-and-audits only (deny: governance + architecture docs)
5. **write_config** — Only compression/policy.yaml (deny: capabilities + trigger_router + risk + drift_thresholds)

Default: DENY. Allow is exception to deny. Unmatched = deny.

## Skill Discovery (Keywords → Skill)
- database/sql/migration → SKILL-DOM-DBS-001
- mcp/server/tool/protocol → SKILL-DOM-MCP-001
- context/pipeline/compress → SKILL-DOM-CTX-001
- feedback/loop/reflect → SKILL-DOM-FBL-001
- gate/rule/policy/compliance → SKILL-DOM-GAT-001
- permission/rbac/capability → SKILL-DOM-AGT-001
- blueprint/architecture → SKILL-DOM-BLU-001
- audit/drift/governance → SKILL-DOM-DRF-001
- knowledge/KE/index → SKILL-DOM-KNW-001
- rollback/undo/checkpoint → SKILL-DOM-RBK-001
- vector/memory/embedding/VMS → SKILL-DOM-VMS-001
- a2a/agent-to-agent/冲突 → SKILL-DOM-A2A-001

## MCP Tool Catalog (9 Servers)
| Server | Tools | Safety |
|--------|-------|--------|
| task_manager | list/get/create/update/delete/health | L/M/H |
| knowledge_base | query/recall/write/delete/reindex/health | L/H |
| gate_engine | list_gates/get_result/evaluate/override/reload/simulate/health/bypass | L/M/H |
| session_handoff | load/save/validate/cleanup/health | L/M/H |
| intent_router | classify/route/train/health | L/M |
| blueprint_search | find/index/health | L |
| sandbox | execute/health | H |
| governance | health/list_contracts/run_gate/check_lock/acquire_lock | L/M/H |
| vector_memory | search/write/recall/list_collections/health | L/H |

## Mandatory Protocols
- **RULE-ZERO**: Immutable files — never modify without Owner approval
- **RULE-ONE**: Atomic writes — temp-file + os.replace() only
- **RULE-THREE**: Registration — every new file must be registered
- **RULE-FOUR**: Scaffold only — `scripts/scaffold.py` is the sole creation entry point
- **RULE-FIVE**: No root pollution — no _temp/_check/_fix prefixes
- **RULE-SEVEN**: Parallel execution — governance scripts must run concurrently

## Trigger Router (6 Triggers)
| Trigger | Handler | Safety |
|---------|---------|--------|
| onboarding | handle_onboarding_stub → layer_router | M |
| drift_detected | handle_drift_stub → drift_detector.trigger_recovery | H |
| compression_needed | handle_compression_needed (real) | M |
| cleanup_due | handle_cleanup_stub → archive_drafts_zone | L |
| blueprint_published | handle_blueprint_stub → decision_engine.reflect | M |
| blueprint_lookup | handle_blueprint_lookup_stub → blueprint_routing.yaml | L |

## Key Conventions
- No comments unless explicitly required
- UTF-8 encoding everywhere
- Pydantic V2 BaseModel for all data structures
- Lazy imports via `__getattr__` + `_COREMODULES` pattern
- temp-file + atomic rename for concurrent write safety

## Test Commands
```
python -m pytest tests/agent_rbac/ -q
python -m pytest tests/governance/ -q -k "not test_all_scripts and not test_security_scripts"
python -m pytest tests/test_code_dedup_engine/ -q
```

## Cold Start Sequence (14 Steps)
1. Read registry-of-registries.yaml (24 registries)
2. Read system master blueprint §0
3. Read project_rules.md
4. Session Continuity restore
5. Phase Manager check
6. Asset inventory
7. Skill discovery
8. Knowledge Base self-check
9. Escalation Protocol activate
10. Drift Detector init
11. Agent RBAC activate
12. Rollback System activate
13. Budget Enforcer activate
14. Audit Trail context inject

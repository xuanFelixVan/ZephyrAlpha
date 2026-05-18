---

skill_id: SKILL-DOM-KNW-001
name: knowledge-specialist
description: "Knowledge base and KE operations — VMS (MOD-INF-011) is the primary system-wide vector backend"
allowed-tools: [Read, Write, SearchReplace, Grep, Glob, RunCommand]
model_hint: DeepSeek
freshness_score: 100.0
last_validated: 2026-05-08
version: "0.2.0"
token_budget_l1: 50
token_budget_l2: 500
author: factory-agent
blueprint_id: MOD-INF-019
---


# Domain Skill: Knowledge Specialist

## CRITICAL Rules

1. Knowledge Entry (KE) creation MUST follow KEEntry v1.5.0 contract
2. Skill-to-KB sync is bidirectional: skill execution → KE draft; citations ≥ 5 → upgrade to instruction
3. Knowledge graph MUST be validated via GraphValidator after each batch insert
4. Stale KE (unused > 30 days) MUST be flagged for review
5. VMS (MOD-INF-011) is the PRIMARY system-wide vector backend (8 Collection: decisions/code_context/lessons/knowledge/rules/blueprints/session_snapshots/execution_traces) — supersedes KB-only chromadb_init.py (4 legacy collections)
6. KB↔VMS sync via VectorBridge.sync_knowledge() after KE creation

## Core Operations

- Knowledge entry creation from skill execution output
- Bidirectional Skill↔KB synchronization
- Knowledge graph validation and consistency check
- Vector store indexing and retrieval (VMS via InProcessVectorMemory)
- KE lifecycle management (create → validate → use → review → retire)
- KB→VMS bridge sync via VectorBridge

## Unique Constraints

- KE citation threshold: 5 citations → upgrade to instruction level
- Vector dimension: 1024 (BGE-M3 ONNX, VMS primary) / 384 (all-MiniLM-L6-v2, KB-legacy)
- Max KE body size: 4000 tokens
- Graph consistency: every entity must have ≥ 1 relation

## Common Error Patterns

- KE duplicate → content hash collision, merge or deduplicate
- Graph corruption → orphan entity detected, run GraphValidator
- Vector index stale → re-index after batch KE insert (VMS + KB-legacy)
- Skill→KB sync failure → bidirectional pipeline broken
- VMS not started → run InProcessVectorMemory.start() before search/write

## Checklist

- [ ] Generate KE draft from skill execution
- [ ] Check citation threshold for upgrade
- [ ] Validate knowledge graph consistency
- [ ] Update VMS vector store index (via VectorBridge.sync_knowledge)
- [ ] Update KB-legacy chromadb index (backward compat)
- [ ] Flag stale KEs for review

## Key Constants

| Constant | Value | Description |
|----------|-------|-------------|
| CITATION_THRESHOLD | 5 | Citations needed for KE→instruction upgrade |
| BGE_M3_DIM | 1024 | VMS primary embedding dimension (BGE-M3 ONNX) |
| LEGACY_DIM | 384 | KB-legacy embedding dimension (all-MiniLM-L6-v2) |
| MAX_KE_TOKENS | 4000 | Max knowledge entry body size |
| STALE_DAYS | 30 | Days before KE flagged for review |

## References (L3, on-demand)

- KEEntry v1.5.0 contract
- VMS blueprint: docs/03_modules/l01_infrastructure/vector-memory/blueprint.md v0.7.0
- VectorBridge: src/zephyr/vector_memory/vector_bridge.py
- KB-legacy ChromaDB: src/zephyr/kb/chromadb_init.py (4 collections, superseded)
- GraphValidator specification
- vector-memory skill: SKILL-DOM-VMS-001
---
blueprint_id: MOD-INF-019
---

# L3 Reference: Blueprint Reading Guide

> Belongs to: architect (SKILL-ROL-ARC-001)
> Tier: L3 Cold Memory — on-demand load via SkillLoader.load_l3_reference()

## Blueprint Tier Navigation

```
Level 0: §0 dispatch table (400 tokens) → system topology overview
Level 1: MOD-MASTER-001 → cross-module contracts
Level 2: Module blueprints → subsystem details
```

## Reading Protocol

1. Start with `SYS-MASTER-001` §0 for cold-start routing
2. Follow `MOD-MASTER-001` for module contract discovery
3. Open target module blueprint via `blueprint_search` MCP
4. Validate `blueprint version` matches `skill_registry.yaml` freshness baseline
5. Cross-reference with `ADR-*` in `/docs/adr/` for architectural decisions

## Key Files

- `docs/00_level_0/SYS-MASTER-001.md` — system constitution
- `docs/01_level_1/MOD-MASTER-001.md` — module master contract
- `docs/03_modules/` — all module blueprints
- `docs/adr/` — architecture decision records

## Token Budget

- §0 cold-start: 400 tokens
- Module blueprint full: 8000 tokens (use MCP selective retrieval)
- ADR per entry: 200-500 tokens

---
module_id: KE-module_blu-three-tier_prompt_cache__d-019-000
title: Three-Tier Prompt Cache (D-019-32)
category: module_blueprint
---

# Three-Tier Prompt Cache (D-019-32)

Three-Tier Prompt Cache (D-019-32)
- Hot (prefix fixed): byte-for-byte identical prefix → 85% hit rate target
- Warm (structure fixed): template + variable injection → 60% hit rate
- Dynamic (fully variable): no caching → fallback

---
module_id: KE-2958
status: active
title: Three-Tier Prompt Cache (D-019-32)
category: module_blueprint
---

# Three-Tier Prompt Cache (D-019-32)

Three-Tier Prompt Cache (D-019-32)
- Hot (prefix fixed): byte-for-byte identical prefix → 85% hit rate target
- Warm (structure fixed): template + variable injection → 60% hit rate
- Dynamic (fully variable): no caching → fallback

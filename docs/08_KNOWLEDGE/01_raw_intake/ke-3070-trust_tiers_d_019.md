---
module_id: KE-2969
status: active
title: Trust Tiers (D-019-82)
category: module_blueprint
ttl: permanent
---

# Trust Tiers (D-019-82)

Trust Tiers (D-019-82)
```
T3 INTERNAL: ZephyrAlpha internal, SkillForge K=3 consensus → full read/write/execute
T2 TRUSTED THIRD-PARTY: Verified publishers, signed packages → read+execute, write workspace only
T1 COMMUNITY REVIEWED: N+ reviews, security scan passed → read-only+sandboxed exec, NO write/net/fs
T0 UNTRUSTED: Unverified → NO execution, sandboxed read-only SKILL.md metadata only
Promotion: T0→1K shadow+full audit, T1→500 ops+2 reviews, T2→100 ops+manual sec review
```

---
module_id: KE-documentat-6__future_platform_modules___e-001
title: 6. Future platform modules & evolution roadmap / 未来平台模块与演进路线
category: documentation
---

# 6. Future platform modules & evolution roadmap / 未来平台模块与演进路线

6. Future platform modules & evolution roadmap / 未来平台模块与演进路线

| Platform module / 平台模块 | Location / 归属 | Status / 状态 |
|--------------------------|----------------|--------------|
| LLM Gateway / task dispatch | L08 `l08_human_ai_interface/model-routing-and-cost/` | deferred |
| Memory Pipeline | L08 `l08_human_ai_interface/memory-and-context/` | in discussion |
| Model Registry (ML) | L11 `l11_ml_platform/model-registry/` | planned |
| Data Platform engine | L00 `l00_data_source/` | planned |
| Feature Store | L11 `l11_ml_platform/feature-store/` | planned |

**架构演进终态**（已锁定，R31+R32+OQ-073）：

- src/zephyr/ 包含 14 个 `l`-prefixed 层（l00–l13）+ `shared/` = 15 namespace
- frontend/ 前端平台层与 src/ 平级，Python 后端与 TypeScript/React 前端完全异构隔离
- docs/ + src/zephyr/ + frontend/ + scripts/ 四域独立演进（四架构联邦制）

---

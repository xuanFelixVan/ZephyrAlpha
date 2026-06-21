---
module_id: KE-486
status: active
title: 6. Future platform modules & evolution roadmap / 未来平台模块与演进路线
category: documentation
---

# 6. Future platform modules & evolution roadmap / 未来平台模块与演进路线

6. Future platform modules & evolution roadmap / 未来平台模块与演进路线

| Platform module / 平台模块 | Location / 归属 | Status / 状态 |
|--------------------------|----------------|--------------|
| LLM Gateway / task dispatch | L08 `frontend/model-routing-and-cost/` | deferred |
| Memory Pipeline | L08 `frontend/memory-and-context/` | in discussion |
| Model Registry (ML) | L11 `ml_train/model-registry/` | planned |
| Data Platform engine | L00 `data/` | planned |
| Feature Store | L11 `ml_train/feature-store/` | planned |

**架构演进终态**（已锁定，R31+R32+OQ-073）：

- src/zephyr/ 包含 14 个 `l`-prefixed 层（l00–l13）+ `shared/` = 15 namespace
- frontend/ 前端平台层与 src/ 平级，Python 后端与 TypeScript/React 前端完全异构隔离
- docs/ + src/zephyr/ + frontend/ + scripts/ 四域独立演进（四架构联邦制）

---

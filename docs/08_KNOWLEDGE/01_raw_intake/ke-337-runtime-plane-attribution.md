---
module_id: KE-337
status: active
title: 4.0 Runtime Plane Attribution / 运行平面归属
category: documentation
---

# 4.0 Runtime Plane Attribution / 运行平面归属

4.0 Runtime Plane Attribution / 运行平面归属

> 运行平面（Hot / Warm / Cold）是与业务分层**正交**的标签维度。**runtime_planes.md §3.1 是 canonical SSoT**，YAML 模型 `architecture-model/cross-cutting/runtime_planes.yaml` 承载完整 14 层 × 三平面映射。

| 平面 | 延迟 | 技术栈 | 本阶段状态 |
|---|---|---|---|
| **Hot Path** 🔥 | < 10ms P99 | C++/Rust/kernel-bypass | **未激活**（T1 真实资金后首次激活 L04/L06） |
| **Warm Path** 🌡️ | 10ms-1s | Python asyncio / FastAPI | **当前默认**（14 层业务代码全部跑在 Warm） |
| **Cold Path** ❄️ | > 1s batch | Spark / Dask / Airflow | **部分激活**（L02 回算、L05 回测、L07 归因、L11 训练） |

→ 完整 14 层归属速查表：See `architecture-model/cross-cutting/runtime_planes.yaml`
→ 详细定义与标注规范：See `runtime_planes.md`

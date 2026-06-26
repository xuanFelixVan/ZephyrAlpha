---
module_id: KE-3335----tech-radar--------archi-001
title: 5.2 对标 Tech Radar 状态（基于 `architecture_model/technology/technology_landscape.yaml
category: documentation
ttl: permanent
---

# 5.2 对标 Tech Radar 状态（基于 `architecture_model/technology/technology_landscape.yaml

5.2 对标 Tech Radar 状态（基于 `architecture_model/technology/technology_landscape.yaml`）

| 技术栈 | Radar 状态 | 激活时机 |
|---|---|---|
| Aeron / LMAX Disruptor | **Trial**（T1 激活后 Adopt）| T1 真实资金 |
| Rust CPython extensions（Warm 热点替换）| **Assess** | T5 性能瓶颈命中 |
| FPGA | **Hold**（ZephyrAlpha 当前不考虑）| T-ULTRA（未定义，≥Sprint 20+）|
| asyncio + FastAPI + Redis Streams | **Adopt**（当前 Warm 主栈）| 当前 |
| Spark / Dask / Airflow | **Adopt**（当前 Cold 主栈）| 当前（施工 Sprint 9 激活 Cold）|

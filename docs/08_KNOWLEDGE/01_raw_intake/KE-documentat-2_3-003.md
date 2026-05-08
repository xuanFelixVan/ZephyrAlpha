---
module_id: KE-documentat-2_3-003
title: 2.3 三平面的部署拓扑
category: documentation
---

# 2.3 三平面的部署拓扑

2.3 三平面的部署拓扑

> **📊 三平面部署拓扑图**：见 [`diagrams/runtime-planes-topology.mmd`](diagrams/runtime-planes-topology.mmd)

**关键跨平面规则**：
1. **Hot ⇄ Warm**：必须过 `shared/contracts/runtime_plane_tag.py` 定义的 IPC 协议（默认 Aeron / LMAX Disruptor），**禁止直接函数调用**
2. **Warm → Cold**：Parquet / Redis Streams 异步推送，**永远非阻塞**
3. **Cold → Warm**：模型 / 参数更新必须过**影子验证**（Champion-Challenger，L13 子模块负责）
4. **禁止 Cold → Hot 直接通信**：所有 Cold 输出必须先落 Warm 再经 Warm 验证后进 Hot

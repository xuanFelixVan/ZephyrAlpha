---
module_id: KE-3266
title: 1.3 与其他视图的边界
category: documentation
ttl: permanent
---

# 1.3 与其他视图的边界

1.3 与其他视图的边界

| 其他视图 | 本视图与其关系 |
|---|---|
| `application_architecture.md` | 03-AA 定义"14 层业务 What"；本视图定义"每个子模块的运行平面 How/When"；本视图 v1.0.0 在 03-AA §4.1 子模块表中**新增 `runtime_plane` 列**（J1 批次 C 任务同步） |
| `technology_architecture.md` | 04-TA 定义"全局技术选型"；本视图定义"按平面差异化技术选型"；§5 技术矩阵是 04-TA §3 的下钻 |
| `governance_architecture.md` | 09-GOV 治理三层 Policy/Factory/Runtime 是**治理维度**（谁管什么规矩）；本视图三平面是**执行维度**（代码何时以什么延迟跑在什么硬件）。二者**名字都叫 "Runtime" 但意义完全不同**——§7 专门澄清。|
| `frontend_architecture.md` | 10-FE 定义前端独立平台；本视图 §3.4 给前端子层打运行平面标签（React SPA Warm / WebSocket stream Hot-adjacent / SSR 报表 Cold）|
| `architecture_model/technology/technology_landscape.yaml` | Tech Radar 风格的技术清单；本视图选型依赖其 Adopt/Trial/Hold 状态（§5 引用）|

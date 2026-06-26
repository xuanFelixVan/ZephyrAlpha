---
module_id: KE-317
status: active
title: 3.5 治理层（09-GOV）三平面归属（同步批次）
category: documentation
ttl: permanent
---

# 3.5 治理层（09-GOV）三平面归属（同步批次）

3.5 治理层（09-GOV）三平面归属（同步批次）

**澄清**：09-GOV 的 Policy/Factory/Runtime 是治理维度三层，本视图的 Hot/Warm/Cold 是执行维度三平面，二者正交。

> 09-GOV 治理系统的平面归属数据见 [`runtime_planes.yaml`](architecture_model/cross-cutting/runtime_planes.yaml) 中 `planes.cold.modules[]` 的 `gov-factory` / `gov-scout-d02` 条目。**要点**：Policy 层无运行平面（纯文档）；Factory 层归 Cold（构建期批调度）；Runtime 层 A/B/C 归 Warm 主 + Hot 部分（kill switch / pre-trade hard check）；D-01 AISG `security_gateway` 子模块 Hot-adjacent（< 50ms）；D-02 Scout 归 Cold。

详见 J1 批次 D 任务同步更新 `governance_architecture.md` v1.1.0 → v1.2.0。

---

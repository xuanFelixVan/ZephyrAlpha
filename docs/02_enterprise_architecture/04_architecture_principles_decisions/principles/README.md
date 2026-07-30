---
ttl: permanent
doc_type: architecture_view
title: 架构原则导读 / Architecture Principles Guide
owner: ZephyrAlpha-Owner
language: zh
---

# 架构原则 · 阅读指引

> 10 份永恒框架原则（prescriptive，规范"项目该怎么"）。与 [project_handbook/](../project_handbook/) 的描述性文档互补。

> **已删除文档（2026-07-30）**：information/integration/operations/frontend 四份原则因过度工程或与 YAML 真源重复已移除。原 information 的 docs 抽屉分类→`directory_registry.yaml`；integration 的 CTR 契约→`cross_layer_contracts.yaml`；operations 运维域→激活后维护；frontend 前端原则→并入 application。

## 推荐阅读顺序

由总到分、由抽象到具体：

1. **[architecture_principles.md](architecture_principles.md)** — 总纲：方法论（TOGAF/C4/三棵树）、安全红线、开源优先、核心决策。先读这篇建立全局框架。
2. **[business_principles.md](business_principles.md)** — 业务能力地图（C1-C7 + CC1-CC3）、价值流、NFR/SLA/SLO。
3. **[application_principles.md](application_principles.md)** — 应用层：C4 视图分层、模块归属、五大核心服务、幂等容错。
4. **[data_principles.md](data_principles.md)** — 数据：PIT、反幸存者偏差、血缘、质量门、MDM、保留分级。
5. **[governance_principles.md](governance_principles.md)** — 治理：三层边界（Policy/Factory/Runtime）、D2-B 闭环、D3-B 自治、D4 激活。
6. **[runtime_planes_principles.md](runtime_planes_principles.md)** — 运行平面：Hot/Warm/Cold 正交视图、跨平面协议。
7. **[security_principles.md](security_principles.md)** — 安全：威胁模型、LSG、Agent 沙箱、密钥三防线、IAM。
8. **[technology_principles.md](technology_principles.md)** — 技术：技术栈决策、运行时拓扑、部署、DR-BCP。
9. **[capability_maturity_principles.md](capability_maturity_principles.md)** — 能力成熟度：五档模型、季度 Review。
10. **[ai_first_governance_principles.md](ai_first_governance_principles.md)** — AI 治理：100% AI 开发的病根分析与 4 期治本框架。

## 维护规则

- 每份原则文档以"永恒框架"定位，标注"永恒"的小节为不可降级的核心约束。
- 原则变更须走架构裁定流程，登记到 `architecture_issue_registry.yaml`。
- 跨文档引用使用相对链接（同目录内有效），改文件名须同步更新 145 处引用。
- 与描述性事实（计数/清单）的边界：原则只定"该怎么"，实际"是什么"的计数见 [../project_handbook/](../project_handbook/) 的 AUTO 块。

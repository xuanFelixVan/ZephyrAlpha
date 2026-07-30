---
module_id: ARCH-004
title: Architecture Principles / 架构原则
doc_type: architecture_view
status: Active
version: 3.0.0
layer: cross_layer
owner: ZephyrAlpha-Owner
language: zh
created_by: agent
valid_from: 2026-07-30
superseded_by: null
supersedes: null
tags:
- architecture-principles
- safety-red-lines
- domain-driven
- open-source-first
summary: ZephyrAlpha 架构原则总纲精简版。仅保留不可降级核心：功能域唯一裁定 + 4 条安全红线 + 开源优先原则 + 核心架构决策。删除 TOGAF/C4/ISO 通用方法论教学、开源机构对标论证、门禁状态快照（以 .pre-commit-config.yaml 为准）。
date: '2026-07-30'
ttl: permanent
---

# 架构原则（Architecture Principles）

> 精简版 v3.0（2026-07-30）：删除三标准合成教学（TOGAF/C4/ISO 是通用知识）、开源机构对标论证（Two Sigma/Man AHL 等教学材料）、门禁状态快照（以 `.pre-commit-config.yaml` 为准）。保留功能域裁定 + 4 条安全红线 + 核心决策。

---

## §1 功能域唯一分类裁定

**裁定**：按功能分域是唯一的分类方式。逻辑层只作为域的一个属性（`layer_id`），不当作独立的分类法。

| 裁定项 | 结论 | 理由 |
|--------|------|------|
| 逻辑层 vs 功能域 | **功能域唯一** | 两套分类并存=AI 每次要判断用哪套=幻觉温床 |
| 逻辑层怎么保留 | 作为域的 `layer_id` 属性 | 属性不是分类，不会产生两套并行的分法 |
| 逻辑层 YAML 文件 | 废弃，合并进 depgraph | 避免两个地方同时存同一信息（真源分裂） |

> 域层级分布由 depgraph `domains` 表派生，禁止在本文硬编码域数量/节点数/边数。

---

## §2 安全红线（Safety Red Lines / 不可撤销原则）

以下 4 条原则是系统最高优先级约束，**任何架构决策、代码变更、AI 自治行为不得违反**。违反任一红线视为 P0 阻断。

| # | 原则 | 大白话 | 执行机制 |
|---|------|--------|----------|
| **R1** | **键盘不录 key** | API 密钥、数据库密码等秘密信息只能通过环境变量/密钥管理器注入，绝不手动键入 | pre-commit 检测 `key=` / `password=` / `secret=` 字面量 |
| **R2** | **日志不写 secret** | 任何日志系统（structlog/logging/print）的输出中不得包含密钥、token、私钥 | CI 门禁正则扫描 log 输出 |
| **R3** | **金融不盲信任 AI** | AI 生成的交易决策、风控参数、金额计算必须经过人工确认或确定性规则校验后才生效 | 风控层 hard check before 执行层 |
| **R4** | **PRD 永远不改** | 生产数据库（PRD）永远不做 DDL 变更/手动 UPDATE/DELETE；所有变更走迁移脚本 + 审计日志 | DB 权限只读连接 + 迁移脚本强制记录 |

**红线优先级**：高于所有其他架构原则。在其他原则与红线冲突时，**红线无条件优先**。

> 门禁落地状态以 `.pre-commit-config.yaml` / `.github/workflows/governance.yml` 为准，不在本文档维护状态快照。详细安全实现见 [security_principles.md](security_principles.md)。

---

## §3 开源优先 / Open Source First

**原则**：能用成熟开源库就不自研。单人 + AI 的开发模式比专业机构**更应该**开源优先——无 QA、无 oncall、无测试团队，开源社区是唯一的质量反哺来源。

> 开源选型清单与版本决策见 `technology_principles.md` / `technology_landscape.yaml`，不在本文档重复。

---

## §4 核心架构决策

**系统定位**：ZephyrAlpha 是个人量化投资系统的 AI 原生重构，采用功能域唯一物理分类体系，Python 全栈，Vibe Coding 驱动。

**定死原则（不可推翻）**：

- **功能域唯一分类**：按功能分域，不按技术层分。逻辑层只作为域的 `layer_id` 属性（§1）
- **全景图派生**：所有结构化数据（域清单/模块清单/依赖关系/容量统计）从 depgraph 数据库自动生成，禁止手编
- **运行时平面**：Hot / Warm / Cold 三平面（详见 [runtime_planes_principles.md](runtime_planes_principles.md)）；激活状态见 `architecture_model/cross_cutting/runtime_planes.yaml`
- **治理三层**：Policy / Factory / Runtime（详见 [governance_principles.md](governance_principles.md)）→ 与业务层平级正交横切，每层有准入和退出门禁
- **安全红线**：4 条不可撤销（§2）
- **技术栈**（决策快照，具体组件可变）：Python + Pydantic + SQLite/PostgreSQL + ChromaDB + MCP 协议

---

## §5 待合并节占位（capability_maturity + business 核心节）

> **状态**：占位区。capability_maturity_principles.md 和 business_principles.md 的核心永恒约束将在用户审查精简版后合并至此。

待合并内容预判：
- **能力成熟度**：L0-L5 五档模型（`capability_heatmap.yaml` 的评分依据）
- **业务 NFR 三原则**：Non-HFT / 市场时段分层 / 可审计 ≫ 可用性（具体 SLO 值在 `value_stream_map.yaml`）

> 合并完成后，capability_maturity_principles.md 和 business_principles.md 将被删除，导航同步更新。

---

> **文档维护原则**：本文档只包含不可降级的核心裁定与红线。方法论教学（TOGAF/C4/ISO）、机构对标论证、门禁状态快照等可变/可派生内容不在本文档。

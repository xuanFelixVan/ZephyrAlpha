---
module_id: KE-3430
title: 4.3 Layer classification rationale / 分层分类依据
category: documentation
ttl: permanent
---

# 4.3 Layer classification rationale / 分层分类依据

4.3 Layer classification rationale / 分层分类依据

14 个层（含 Shared，共 15 个 namespace）按**量化投资价值链 + 横向支撑 + AI 时代新增层**三个维度组织：

| Category / 类别 | Layers / 层 | Principle / 原则 |
|----------------|------------|-----------------|
| **Foundation** 基础层 | `shared`, `infra_ops` | 无业务逻辑，被所有层依赖；变更频率最低 |
| **Data & Signal** 数据信号层 | `l00`, `l02`, `l03` | 数据进入→因子加工→信号提取；单向数据流 |
| **Decision** 决策层 | `l04`, `l05` | 风险约束→组合构建；两层强耦合，共同产出委托指令 |
| **Execution** 执行层 | `l06`, `l07` | 委托发出→执行后分析；直连外部系统（券商 API） |
| **Interface & Research** 交互创新层 | `l08`, `l09` | 人机协作入口 + 实验沙盒；不参与主交易流水线 |
| **Compliance** 合规层 | `l10` | 横向硬合规运行时检查；按辖区分片（A 股/美股/欧盟 MiFID II） |
| **AI/ML Platform** AI/ML 平台层 | `l11`, `l12`, `l13` | AI 时代新增三层：ML 生命周期 + 系统可观测 + 自动化实验 |

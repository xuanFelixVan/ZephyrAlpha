---
module_id: KE-184
title: 2.2 Responsibility Assignment Matrix (RACI) / 责任分配矩阵
category: documentation
---

# 2.2 Responsibility Assignment Matrix (RACI) / 责任分配矩阵

2.2 Responsibility Assignment Matrix (RACI) / 责任分配矩阵

> **标记含义**：**R**=Responsible 执行者，**A**=Accountable 最终问责人（**每行有且仅有一个 A**，TOGAF/PMI 铁律），**C**=Consulted 需要协商，**I**=Informed 需要知会。空白=无关。

| # | Activity / 关键活动 | 归属能力域 | S1 Arch | S2 Quant | S3 Trade | S4 Risk | S5 Comp | S6 Data | S7 SRE | S8 AI-collab | S9 AI-Op | S10 Vendor | S11 Partner | S12 Reg |
|---|---------------------|----------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| A01 | 架构 ADR 决策与终审 | C01-C10 | **A/R** | C | C | C | C | C | C | C | I | | I | |
| A02 | 策略假设与研发 | C02/C04 | C | **A/R** | | C | | C | | C | | | I | |
| A03 | 因子构造与上线 | C02 | C | **A/R** | | C | | R | | C | | | | |
| A04 | 因子日度/分钟刷新执行 | C02 | I | A | | I | | R | R | | R（未来）| I | | |
| A05 | 回测验证与报告 | C02/C04 | | **A/R** | | C | | C | | C | | | I | |
| A06 | 模型训练与部署 | C03 | C | R | | | | R | **A** | C | R（未来）| | | |
| A07 | 信号生成与发布 | C04 | | **A/R** | I | C | | C | I | | R（未来）| | | |
| A08 | 组合构建与再平衡 | C04 | | R | I | C | | | I | C | **A**→R（未来）| | | |
| A09 | 事前风控审批（下单前门）| C08 | I | I | I | **A/R** | C | | I | | | | | |
| A10 | 下单执行与订单生命周期 | C05 | | | **A/R** | C | I | | I | | R（未来）| R | | |
| A11 | 成交回报与对账 | C05/C06 | | I | R | I | I | R | I | | R（未来）| R | | |
| A12 | 事中仓位/回撤监控 | C08 | I | I | I | **A/R** | I | | R | | | | | |
| A13 | 异常处置与 kill-switch | C05/C08 | I | I | R | **A/R** | I | I | R | | | | | I |
| A14 | 绩效归因与交易后分析 | C06 | I | R | I | C | | C | | C | | | I | |
| A15 | 数据接入（Vendor SLA 维护）| C01 | I | I | | | | **A/R** | C | | | R | | |
| A16 | 数据质量断言与血缘 | C01 | C | I | | | I | **A/R** | I | | | | | |
| A17 | 合规审查与留痕归档 | C09 | I | I | I | C | **A/R**（deferred）| | I | | I | | | I |
| A18 | 运维部署 / 容量 / 成本 | C04-C05/cross | C | I | | | | I | **A/R**（deferred）| | | | | |

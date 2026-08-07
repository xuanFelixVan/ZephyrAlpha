---
ttl: permanent
doc_type: architecture_view
title: 讨论稿：密度预测与QNN远期愿景
owner: ZephyrAlpha-Owner
language: zh
status: 待讨论
version: "0.1.0"
date: 2026-08-07
topic: density_prediction
scope: 量化预测方法论
---

# 讨论稿：密度预测与QNN远期愿景

> **状态**：远期愿景，待讨论。源自原《能力定位书》约束十二，当前项目中无代码实现，亦无对应 G01-G28 讨论主题。移入此处待条件成熟后启动讨论。

## 原始内容

- 分阶段实现（参数化→QNN→非参数化）
- 概率校准度偏离对角线<5%才可消费
- 尾部校准（VaR覆盖率误差<2%）为风控消费前提
- CRPS为核心评估指标
- 8态概率Phase4后从PDF积分派生
- 半Kelly为硬上限（0.5×f*）

## 待讨论问题

1. **密度预测是否为当前阶段必需？** 项目当前 regime 检测已定稿12态（discussion_001），密度预测是否在 regime 之上还有增量价值？
2. **QNN（量子神经网络）可行性** — 单机 RTX 3090 环境下 QNN 训练/推理的工程可行性？
3. **校准阈值来源** — "5%偏离"、"2%覆盖率误差"这些阈值的依据是什么？需要回测验证。
4. **与现有风控模块的关系** — design_memo_001 已定义4级回撤 Protocol 和 FirmRiskAggregator，密度预测如何融入？

## 关联

- discussion_000 G16-G18（风控落地）
- discussion_001（regime detector spec，12态）
- design_memo_001（多策略并发，仓位/风控框架）

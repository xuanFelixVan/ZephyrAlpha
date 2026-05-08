---
module_id: KE-documentat-1_1-000
title: 1.1 本视图要回答的问题
category: documentation
---

# 1.1 本视图要回答的问题

1.1 本视图要回答的问题

| 问题 | 答案所在 |
|---|---|
| 控制面（研究 / 决策 / 报表）和执行面（下单 / 成交 / 撮合反馈）在物理上如何分离？| §2 三平面定义 |
| 14 层业务代码每一层 / 每个子模块属哪个运行平面？| §3 14 层 × 三平面映射矩阵 |
| Hot Path / Warm Path / Cold Path 何时激活？激活条件是什么？| §6 激活触发器（P0-P3）|
| 三个平面之间如何通信？契约是什么？| §4 跨面协议（Ring Buffer / Redis Streams / Parquet）|
| Hot Path 用什么技术栈？Warm Path 用什么？Cold Path 用什么？| §5 技术选型矩阵 |
| 与 09-GOV Policy/Factory/Runtime 三层是什么关系？| §7 与 09-GOV 边界澄清 |
| Sim-to-Real Gap 如何通过运行平面统一契约来消解？| §8 Sim-to-Real 保障 |

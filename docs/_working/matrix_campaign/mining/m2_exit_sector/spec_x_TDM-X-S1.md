---
campaign: matrix-20261006
lane: m2
status: draft
ttl: task_bound
---

# 规格卡 X-02 | TDM-X-S1 卖出信号收集评分（组骨架）

- 车道: M2 离场族+板块族接线挖矿 | 2026-10-06
- 接法分级: **L（只登记）**——组节点，无独立机制
- 真源: `config/trading_decision_map.yaml#TDM-X-S1`；t3 挖矿 §1.7

## 1. 结论

TDM 判定"组节点（structural）"。子机制已逐节点拆卡：
X-S1-01（收集六桶）/X-S1-02（止损族）/X-S1-03（止盈族）/X-S1-04（破位退潮）/X-S1-05（融合评分）/
X-S1-06（强制清仓，非回测域不拆）。本节点不单独施工、不出考维。

## 2. BM 映射备注

BM-SELL-03→TDM-X-S1 映射在册（battle_map_steps，t3 挖矿 §1.9）；作战地图挂了 TDM 而考卷
零实现——本车道 M1（X-S1-02/03）落地后此映射才首次获得回测侧实体。

## 3. 考法

无独立考法。整族考法纪律见各子卡：凡路径依赖子机制激活，T3b-T0 强制重标定 per_point_seconds。

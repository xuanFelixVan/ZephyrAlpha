---
ttl: task_bound
completes_when: 生产线退役或 Owner 叫停
title: 全线水位表（⑩线长席产出）
---

# 全线水位表 queue_depths

产出岗=⑩线长席；每班更新。格式：环节｜积压量｜吞吐速率｜瓶颈判定｜处置。

| 环节 | 积压 | 备注 |
|---|---|---|
| empty 卡 | 待统计 | |
| preregistered 队列 | 待统计 | |
| examined 未判卷 | 待统计 | |

（首班巡检后重算；楼图见 pulse/coverage_map.md）

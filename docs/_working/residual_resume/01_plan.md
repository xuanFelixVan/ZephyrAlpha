---
title: 残余挂账战役收尾施工方案（tc_08 卡步骤编排）
created_at: 2026-09-22
session: st-residual-20260922
ttl: task_bound
---

# 残余挂账战役收尾施工方案

> 本件=tc_08 卡诊断的"形式收口三件"缺口的补齐件之二（方案面）。
> 原则：线内先挖后干、线间并行流水；子代理并发 2-3；多会话按写域切零重叠才并发。

## 1. 环节拆分与依赖

| 环节 | 内容 | 依赖 | 状态（09-22 实测） |
|---|---|---|---|
| S1 接线两段 | pipeline_events 危机短路+attribution_daily FIFO | A5 裁定（Max） | 等裁定，成品在 G 盘冷库落前验哈希 |
| S2 apply 三常量 | 三表 DDL 注册恢复 | 无 | 本批落地 |
| S3 cohort 任务 | tasks.yaml+provider 路由+品类条目 | S2 | 本批落地；建表 Owner 门位 |
| S4 B20 日期修复 | crisis_gate 一行+关假绿通道 | 无 | 本批单独落（+31/-7 未随批） |
| S5 6D 删除 | 旧路径 docs/_working/residual_construction 清尾 | 归档盒内容核验 | 本批落地 |
| S6 B21 复跑 | 严格 HEAD 两轮+六环节端到端 | 净窗 | 未做，需排程 |
| S7 收尾形式件 | 总簿回写+收工报告+Q2 清理+五裁定登记 | S1-S5 | 部分可做（总簿回写本批） |
| S8 M-1~M-11 落册 | 长尾矿脉登记不动工 | 无 | 未做（登记件待产） |

## 2. 波次编排

- 第 1 波（零裁定依赖）：S2/S3/S4/S5 并行批——本班 09-22 已执行。
- 第 2 波（等 Max A5 裁定）：S1 接线两段按 BT-P1-031 后新版重排落地。
- 第 3 波（净窗）：S6 B21 严格复跑+红队一轮（crisis 误报代价/regime 误报率/对冲腿贴水磨损）。
- 第 4 波（收口）：S7 剩余（建表 Owner 门位后 insert 主路径实跑验证）+S8 落册。

## 3. 红线（方案要素·红线栏）

1. +31/-7 红队加固禁落（R-072a）——落了激活 CRISIS_SHRINKAGE_FLOOR 改配额闸。
2. 全程禁连生产库写操作；建表走 admin 通道+Owner 门位。
3. 接线成品落前先验 G 盘冷库哈希；三共享文件（pipeline_events/tasks.yaml/apply_ddl）动前必 acquire。
4. 测试禁写生产路径（tmp_path fixture）；message 必须与 diff 逐字一致。

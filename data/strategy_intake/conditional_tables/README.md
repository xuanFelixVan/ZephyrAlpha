---
ttl: task_bound
title: P1 条件概率表 v1
doc_type: index
---

# P1 条件概率表（2026-09-24 交付 · st-cmd-20260924）

> Owner 愿景"什么天气哪个板块赚钱"的查询表 v1。口径真源=docs/_working/quant_methodology/01_caliber_law.md（期望值+Wilson LB 分层）+03_conditional_stats_spec.md（四元组行+MIN_OBS 地板）。
> 施工文档=docs/_working/decision_map_campaign_20260924/04_p1_conditional_tables.md。

## 文件

| 文件 | 内容 |
|---|---|
| p1_sector_by_phase.csv | **T1 主表**：469 板块×6 相位=2,806 格（可考 1,837/不可考 969），每格 n/raw_win_rate/wilson_lb/mean_bp/median_bp/p25/p75/std/t_stat/exam_ok |
| p1_phase_momentum.csv | **T2 动量系数**：各相位 trailing20d×fwd5d 池化相关（轮动原料）——退潮/分化/亢奋=负（高低切），扩张/蓄积≈0 |
| p1_phase_transition.csv | **T3 转移矩阵**：相位→相位 36 行概率 |
| p1_phase_stay.csv | 相位停留时长（count/mean/max 日）——expansion 均值 8.8 日/capitulation 11.2 日/euphoria 3.3 日 |
| p1_top5_by_phase.txt | 每相位 Top5（排序只认 Wilson LB 且 exam_ok） |

## 口径与 as-of

- 相位真源=六段相位全史 v1（t0 班法定判定器 `auto_mount.resolve_six_phase` 物化件，1,816 日，本表用其路由日 1,054 日；r1/r2 不路由=宁漏勿误）。
- PIT：相位 detect(t) 只用 ≤t-1 特征→相位(t) 对齐 t 日收益无未来函数。
- 有效窗 2020-03-17→2026-09-21（880 深史起点相交）；n≥30 才 exam_ok，其余"不可考"如实保留。

## 重算命令

```
python .runtime/tmp/p1_conditional_tables.py
```
（依赖：六段全史 CSV 落 HEAD 后把 PHASE_CSV 指向 HEAD 路径重跑；脚本一次性，长期重估再转正 scripts/）

## 已知限制（v1）

1. **sector_name 全空**（880 表该列为空串，仓内无 880→名称映射源）——以 sector_code 为联接键；补名与分钟K真值源同族（数据车道）。
2. **ignition 相位仅 1 路由日**——其统计格不可考，仅供参考。
3. euphoria 相位样本 38 日，可考格子仅 1 个——稀薄相位结论谨慎使用。
4. 收益为价格收益（未扣成本）——**作条件查询原料用，不作策略收益承诺**；成本后口径由 GPU 成绩单承担。

---
ttl: task_bound
title: 03 GPU 搜索战役
---

# 03 · GPU 搜索战役（现行运行+守望+升级案）

## 一、现行运行（方案②，跑批中）

| 项 | 值 |
|---|---|
| 运行编号 | **grid_20260924-213246**（产物=data/strategy_intake/grid_20260924-213246/） |
| 命令 | `python scripts/backtest/factory_grid_executor.py --stage t1 --start 2019-01-04 --end 2025-09-09`（闭卷窗口径，脱管进程） |
| 日志 | .runtime/logs/grid_t1_20260924.log（stdout 有缓冲，钳制消息可能晚刷；进程存活=tasklist 验） |
| 规模 | T1 3,700 格（五档成本门全程真跑，35.33s/格实测口径）→ 完赛后 T2 900 格（主效应前 20% 自动晋级+4440 型复验） |
| 预计 | T1 完=周六 08:00-14:00；T2 ≈9h；全窗余量足（59h 至周日 09:00） |
| reaper | factory_grid_executor+f06 已在 process_reaper_keep.txt:18,34 ✓ |
| 纪律 | **跑中禁改 prereg**（冻结语义：改空间=作废重开）；T2 后主效应前 20% 外负结果如实入 negatives.csv 禁删改 |

## 二、守望要点（每轮巡检）

1. 进程存活（tasklist python + 日志增长）；
2. GPU 健康（nvidia-smi 显存≤18GB 配额、温度）；
3. 产物目录增长（grid_*/ 中间件）；
4. T1 完赛验收：manifest.csv 行数=3700、negatives.csv 在、net_returns.parquet/csv.gz 在、backtest_dead=0/eval_dead=0/degraded=0（T0 同口径）；
5. T2 接棒：确认晋级集 900 格、发车、同口径验收；
6. 完赛后：成绩单=每格 cost_adjusted_sharpe（主目标函数，毛夏普仅观察）+ DSR 门槛（e7_defense.dsr_floating，N_eff 口径裁定#306）。

## 三、方案①升级案施工清单（下一窗口，Owner 原则已批）

1. **T1 轻档成本路径新建**：per-point 评估支持 stage-aware 档位子集（T1=[0,5] 两档 / T2=[0,5,10,20,40] 全档）；落点=run_batch 评估链+f06/exam_cost_gate 消费面（现 tiers_bp 全档硬编码，代码缺口实测于 09-24 晚）。
2. **执行器预算闸语义扩展**：_apply_prereg_budget 现要求 cost_gate_in_every_tier=true 字面（864 行 fail-closed）——改为接受分层语义字段（如 cost_gate_tier1_tiers_bp/tier2 全档），保持 fail-closed 精神。
3. **prereg 语义字段增补**+三字段重签（新裁定）。
4. **红蓝**：轻/全档排名对拍（历史基准 Spearman 0.9998/top50 50:50 复现）+T0 小样本复标定。
5. 预算复核：轻档 ≈6-7s/格 → T1 9,600≈17h + T2 1,920×35.33≈19h，59h 窗容纳验证。

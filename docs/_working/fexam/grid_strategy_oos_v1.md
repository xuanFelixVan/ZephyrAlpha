---
campaign: matrix-20261006
lane: E-exam-w2.5
ttl: task_bound
---

# R道——324 格网格考（策略族）OOS 判决 v1

> 考册真源：[`grid_strategy_oos_v1.yaml`](grid_strategy_oos_v1.yaml)（prereg 2026-10-06T19:27Z 冻结，先于任何判决计算）。
> 对象：F 道 GPU 网格考 324 格 = 5 考场（`data/strategy_intake/grid_20261006-201353/201854/201935/202016/202055`，目录只读）。

## 0. 判决一句话

**0 pass / 0 retire_candidate / 324 rework**（三态判决按 prereg 算术全落 rework），其中 OOS 侧分层：42 格 `is_pending_oos_ok`、4 格 `is_pending_oos_dd_breach`、278 格 `oos_negative`。

## 1. 关键事实：IS 腿不可评（诚实位）

- 五考场 `summary.json` window 与 `net_returns.parquet` 覆盖**恰好都是 2025-10-09..2026-09-30（241 交易日）**——本批装置只跑了 OOS 窗，prereg 的 IS 窗（2018-01-02..2025-09-30）在本批零数据。
- 全仓扫描 `grid_*/summary.json`：无同族 IS 批次（其余目录=2020-2023 窗的 G_universe 族，子空间/窗口均不同，不可借用）。
- 推论：IS Sharpe 不可评 ⇒ 无格可达 pass（需 IS>0）、无格可达 retire_candidate（需双窗<0）。**42 格 OOS 侧达标只是"候补"，须 IS 补考后才可能升 pass。**

## 2. 口径核验

- 逐格重算（日净收益 mean/std(ddof=1)×√252；nav 峰谷 MaxDD）：OOS Sharpe 符号与 manifest 324/324 一致；MaxDD 与 manifest 逐格差 ≤1e-3（324/324）。manifest 年化基数与 252 基数存在 <0.02 绝对差（装置内部口径），不影响三态判决。

## 3. 三态计数（每考场）

| 考场 | 格数 | oos_negative | is_pending_oos_ok | is_pending_oos_dd_breach |
|---|---|---|---|---|
| std_device (201353) | 18 | 18 | 0 | 0 |
| b_topn_band (201854) | 54 | 50 | 0 | 4 |
| d1_freq_band (201935) | 54 | 54 | 0 | 0 |
| g_universe_band (202016) | 54 | 54 | 0 | 0 |
| a2_composite_band (202055) | 144 | 102 | 42 | 0 |
| **合计** | **324** | **278** | **42** | **4** |

## 4. 全局 Top5 OOS Sharpe（列全参数）

| # | 格点 OOS Sharpe | OOS MaxDD | 参数（除注明外全格相同：C=equal_weight, D2=periodic, E=cap*, F=single, H=lambda_0, I=frozen_l0, J=off, K=lump） |
|---|---|---|---|
| 1-3 | 1.326 | -18.3% | A1=industsize_neutral, A2=halflife60, B=top20, D1=monthly, G=all_a_ex_st；E=cap5/cap10/cap20 三胞胎同曲线（E 无效维） |
| 4-5 | 1.211 | -18.3% | A1=industsize_neutral, A2=ic_ir, B=top20, D1=monthly, G=all_a_ex_st；E=cap10/cap20 同曲线 |

Top5 全部同属一个机制族（中性化 + halflife60/ic_ir + 低频 top20 全 A），**非独立证据**。324 格仅 89 条唯一净值曲线、252 个唯一 recipe_id。

## 5. 参数带规律（带维配对，每考场 18 组完全配对，均值 OOS Sharpe）

- **B_top_n**：top10 -0.28 > top20 -0.39 > top30 -0.41 —— 越集中越好，但全负。
- **D1_rebalance_freq**：monthly -0.39 > biweekly -0.77 > weekly -1.34 —— 频率越低越好（换手成本主导）。
- **G_universe**：all_a_ex_st -0.39 > hs300 -0.44 > zz500 -0.53 —— 全 A 股票池最好。
- **A2_combine_weight（唯一正杠杆）**：halflife60 **+0.71** > ic_ir -0.07 > ic_mean -0.17 > lasso -0.24 > pc1 -0.27 > halflife20 -0.36 > equal -0.39 > orth_equal -0.93。
- 42 格 pending-ok 解剖：halflife60 全部 6 种 A1 过 OOS 侧线；ic_ir/ic_mean 仅中性化/秩归一过线；halflife20 仅中性化过线。4 格 dd_breach：top10 × raw/size_neutral，Sharpe≈0.06 但 MaxDD≈-52%。

## 6. 多重检验纪律（诚实位）

324 格多重比较（实际独立度更低：仅 89 条唯一曲线），且窗只有 1 年 OOS。**任何 OOS 正结论（含 halflife60 杠杆）须 DSR 折减与换样本复核后才可上线。** N 账本已记：`fexam-grid-strat-20261007`（kind=fexam_grid_strategy_family），累计 N=28789 前后不变——324 次回测已由 auto_sync 计入五考场条目，本批为 0 增量指针条目，分母不双计。

## 7. 处置建议

1. 42 格 pending-ok 排 IS 补考（装置补跑 2018-01-02..2025-09-30 窗）后方可按 prereg 升 pass/retire。
2. 若 IS 补考，优先机制族：A2=halflife60 × 中性化归一 × monthly top20 all_a_ex_st；E_single_cap 维在本装置为无效维，建议装置侧修复或从网格中剔除（省 2/3 格点算力）。
3. OOS 单窗为牛市/熊市何种 regime 未分层，升格判定前按 `alignment_checklist` 对齐 regime 口径（codesym 考册同款 HMM 四态）。

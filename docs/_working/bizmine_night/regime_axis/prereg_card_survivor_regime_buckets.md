---
ttl: task_bound
---

# 预注册卡：17 幸存者 × 大盘灰度状态桶 条件化重算（st-bizmine-r-20260919）

> 本卡在**任何条件化计算执行之前**写定（2026-09-19 凌晨），落定后禁改。计算代码只实现本卡口径。
> 依据总包令 R 车道第 2 条与诚实条款（多重检验：桶边界一律 IS 期钉死）。

## 1. 样本

- **策略集**：`docs/_working/sharpe2_prep/a_reexam/reexam_results.csv`（81 数据行）筛 `oos_sharpe_h2 > 0` → **17 条幸存者**（与 2026-09-17-e4-h2-reexam-report.md §6 D_all_survivors_equal 完全一致）：
  FACT-4db4c41e, CAND-8d000bf3ccc3, FACT-4f749668, FACT-4228020a, FACT-e831084c, FACT-e293e217, FACT-4b200528, CAND-c4ec6332c07f, CAND-e3da6fa71af1, CAND-eaddc3f9db4e, CAND-4440d07f973f, CAND-d06cab686cef, CAND-29eb91dbaf60, CAND-a4543012b464, CAND-e2e7f033d97c, CAND-bd42540f86e4, CAND-6a6ec8869ddb
- **逐日净收益**：`.runtime/tmp/sharpe2a_oos_nets/<sid>.csv`（73 份在盘，实测逐日 403 行，2024-01-02..2025-08-29）。表头兼容 `date` / `trade_date` 两种形态。
- **状态序列**：`c1_backtest.regime_state_anchored`，DISTINCT 去重（plain MergeTree 有重复插入行，实测重复值一致）。

## 2. 状态变量与口径偏离声明

- 总包令原文："regime_state_anchored 里主力状态概率（或 confidence_signal，选一个）"。
- **实测偏离**：该表无概率列、无 confidence_signal 列（DESCRIBE 实证：trade_date/dominant/vol_pct/close/ma20/ma60/ma120/data_source/ingest_ts）。7 维概率在 `regime_snapshot_history` 但为 VAL 回填（止 2026-09-15，且节流三列全 0、后验过尖）；五态判定台账仅 4 行/1 天。
- **预注册状态变量 = `regime_state_anchored.vol_pct`**（hv20 在滚动 250 日内分位 ∈[0,1]；生产者 anchored_state_machine，INVARIANTS 保证 rolling 只用 t 及以前数据）。理由与备选评估见 `regime_status_assessment.md` §5。

## 3. 分桶规则（边界钉死）

- 分位切法：IS 期 = 2017-07-11..2023-12-29（去重后 n=1576 日）vol_pct 经验分位；**线性序位取整法**（sorted[int(round(q*(n-1)))]），结果四舍五入 4 位小数后冻结：
  - **低波桶 LOW：vol_pct ≤ 0.3200**
  - **中波桶 MID：0.3200 < vol_pct ≤ 0.7040**
  - **高波桶 HIGH：vol_pct > 0.7040**
  - （q33=0.320000、q67=0.704000；冻结值 0.3200/0.7040）
- **禁用考试窗数据定边界**（已遵守：边界只由 IS 期算出）。
- 考试窗 2024-01-02..2025-08-29 逐日**照冻结边界落桶**；落桶份额实测（非预注册项，仅记录）：LOW 38.2% / MID 29.3% / HIGH 32.5%。

## 4. PIT 规则

- 状态取 **T-1 交易日**的 vol_pct（严格早于收益日 t 的最近一个有状态交易日；禁当日值落桶）。
- T-1 无状态（考试窗首日 2024-01-02 的前交易日 2023-12-29 在 IS 内有值，实测无缺口）→ 若出现缺失日该日剔除并如实报告剔除数。

## 5. 指标定义（每策略 × 每桶）

- n_days：桶内交易日数；day_share = n_days / 403。
- mean_daily_net（日均值）；**net_Sharpe = mean(daily net)/std(daily net, ddof=1) × √252**（桶内截断序列，不作年化连续性修正）。
- win_rate = 净收益 > 0 的天数占比。
- 汇总行 POOLED-17E：17 条幸存者逐日**等权平均**净收益序列按同桶规则计算同三项（回答 Owner 论点的主口径）。
- 全部 17 条逐条输出，**含难看结果**，禁筛选禁排序后截断。

## 6. 判读标准（先钉死，禁事后改口）

- 若各桶 net_Sharpe 差异方向在策略间不一致、或 POOLED-17E 三桶 Sharpe 极差 < 0.5，判**"状态条件化暂无证据"**（如实写，禁硬凑）。
- 若存在某桶系统性占优（POOLED 极差 ≥ 0.5 且多数高 Sharpe 幸存者同向），写明"集中于 X 桶"，同时声明：单次分桶×17 策略仍属多重检验场景，IS/OOS 边界虽钉死，结论仍需下窗复考。
- 一切数字带「暂定（复权链未修复）」标注；成本口径=引擎现行（reexam 链原口径：佣金万 0.854 双向+¥5 地板+卖出印花税万 5+滑点五分位）。

## 7. 禁改清单

边界值 / 桶数 / 指标定义 / 判读阈值 / T-1 规则——计算后不得回调。任何口径变更须另开新卡并声明旧卡作废。

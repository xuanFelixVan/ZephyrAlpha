---
ttl: task_bound
title: L06-子模块 搜索执行器与预注册防线（T1/T2 网格粗扫→晋级 / prereg 冻结 / DSR·n_trial 账本）挖干
created: 2026-09-25
sid: st-qmine-20260925
lane: L06_exam_alloc
status: SEALED-CORE（六向内部反查全填、③向外部双源；冻结判据件只登记不改）
skeleton_source: ../SKEL.md L06-A/L06-B；../../09_link_skeletons.md 环节6；判据 ../../17_quantified_acceptance.md §一/§二
doc_role: L06 挖矿子模块 MINE（覆盖 SKEL L06-A 搜索执行器 + L06-B 预注册防线）
---

# 子模块 · 搜索执行器与预注册防线（search_executor_prereg）

> 考试机器"搜"的半边：网格执行器把搜索空间抽样跑成成绩单格，预注册防线保证不 over-fit。
> ⚠ 冻结件纪律：`config/search_space_prereg.yaml`/`exam_scale_cost_gate.yaml`/`scripts/audit/cost_trio_exam.py`
> 是判据真源，本块**只实测现状+登记"谁该改"，不动手**（改=判据变更走裁定通道）。LANE-RB/LANE-AUTO 路径不碰。

## ① 职责一句话
按预注册预算钳制从组合配方空间抽样、五档成本门全真跑成每格 `cost_adjusted_sharpe`，
同时以 n_trial 账本+DSR 浮动门槛+负结果台账守住"多重检验不注水"。

## ② 现状实测（代码 file:line + 产物新鲜度）

### 执行器（factory_grid_executor.py）
- 预算钳制 fail-closed `_apply_prereg_budget`（:982-1008）；E0 算力窗问闸 `compute_window_gate.check_gate("f06_grid_batch","local_gpu")`（:1011-1020）；
  三数据面 c1_market 经 TableRegistry（:88-111）；v1 三因子现算（:111,242-249）；预热 200 日（:699）。
- 产物 schema：`manifest.csv` + `negatives.csv`（NegativeRecord 拒缺死因行 :114-130）+ `summary.json`（N_eff+窗口+seed）+ `net_returns.parquet`（DSR 精确底料 :852-863）；
  **跑中目录空=代码预期行为**（:889-914，manifest 期末一次落盘）。
- 方案① T3 轻档代码在码：keyword-only `cost_gate_tiers_bp` + `STAGED_TIERS_KEY="cost_gate_t1_tiers_bp"` + `_resolve_stage_cost_tiers` 轻档须全档子集 fail-closed（:46-55,918-1008）——**红蓝对拍属 LANE-RB，本块不触发**。

### 预注册冻结册实测（`config/search_space_prereg.yaml`，只读）
- `frozen_at: 2026-09-24T22:00:00+08:00` / `frozen_by: 裁定#413`（:12-13）——**在册冻结件，改动须裁定**。
- `budget_caps`：`grid_points_cap: 25000`（:58，含五档成本门，旧值 200 哑门时代误设）、`trial0_calibration_points: 200`（:59）、
  `tier1_points: 3700`（:60）、`tier2_points: 900`（:61）、`cost_gate_in_every_tier: true`（:62，任何粗扫禁跳成本门）。
- `e7_defense`：`dsr_denominator: n_trial_ledger cumulative_trials`（:70）、`dsr_floating: true`（:71）、每次尝试必经 `n_trial_ledger.record_run`（:74）。
- **现状实测新发现（LK-11 之外的预算债）**：`per_point_seconds_measured: 35.33`（:57，T0 实测 run=grid_20260924-080309，7065s/200 格）=
  预算估 6.8s 的 **5.2×**，59h 窗有效容量≈4809 格——预注册自注"T1/T2 配比待裁定重排" ⇒ **判据件数值与现实背离，须走裁定重排（本块只登记"谁该改=prereg 维护者经裁定#413 附属通道"）**。

### n_trial 账本 / DSR（防线）
- `src/zephyr/backtest/core/n_trial_ledger.py`（MOD-BT-200，**stability=experimental** :19）：
  YAML 真源+CAS 写；`manual_population` 只入 `known_floor` 披露位**永不入 count**（:10,39，不可审计计数进判定=可伪造门禁）；
  批次幂等（:12）；`n_trials_effective` **预留位当前恒 None**（:128,138，只交付 n_trials_raw）。
- `src/zephyr/simulation/deflated_sharpe_calculator.py`（MOD-SIM-024，全仓 DSR 唯一真源，样本<3 拒 + 退化 fail-closed，SKEL L06-B ④）。

### 产物新鲜度（实测采样 `data/strategy_intake/`）
- grid 历史 run 26+ 个（`grid_20260915-*` 至 `grid_20260925-111219`，最新两个 = 空目录=跑中预期）；
  T1 现行 `grid_20260924-213246`（Sep 24 21:32，跑批中无 manifest）。
- T0 标定 run `grid_20260924-080309/summary.json` 实测：`n_raw:362880 / n_sampled:200 / evaluated:200 /
  eval_dead:0 / backtest_dead:0 / degraded_recipes:0`、window `["2019-01-04","2025-09-09"]`、`seed:20260915`、
  `n_trials_effective:12`、`n_eff_meta{common_T:1622,boundary:false}`。
- **schema 实测差异（新立观察）**：T0 run `manifest.csv` 表头 =
  `recipe_id,prefix_key,degraded_dimensions,sharpe,ann_return,max_drawdown,avg_turnover,net_days,values_json`
  ——**无 `cost_adjusted_sharpe`/`cost_tier_sharpes_json` 两列**（SKEL L06-A ③断言有两列）；
  values_json 内 `I_cost_tier: "frozen_l0"` ⇒ T0 标定档成本列或未按 T1 落 manifest。**17 §一"成本门真实性"判据依赖 manifest cost 列 ⇒ 待 T1 manifest 出后核验列是否齐**（成绩单验收前置）。

## ③ 六向台账（内部 + 全网双动作）

| 向 | 内部反查发现 | 全网外部反查 |
|---|---|---|
| ①上游 | 搜索空间机器真源 `config/position_recipe_grid_schema.yaml`（GridCompiler 消费禁删维，SKEL L06-A ①）；prereg 预算钳制；E0 问闸；三数据面 | 待外部（搜索预算/sequential 采样口径，见 ③） |
| ②下游 | T2 晋级（主效应前 20% 自动晋级+4440 复验，03 §一）；f06 幸存者正考（SURVIVORS_CSV=`data/strategy_intake/f06_survivors.csv`，实测存在 1055B）；factory_grid_anova 归因；红蓝参考 run（LANE-RB 面，不碰） | 待外部（并入 ③） |
| ③算法/机制 | 多重检验三件套判据族出处真源=18 号文 §四（Harvey-Liu 2015 JPM haircut／Bailey-LdP 2014 DSR／Bailey et al 2017 PBO-CSCV／Nefedov 2025）；n_trial 只算可审计机器回测=防"计数注水"；两阶段粗扫（T1→T2）=successive-halving/Hyperband 学术同构（17 §专业标准出处） | **≥2 源**：① MDPI Mathematics 2026 "Point-in-Time Backtesting of Momentum-Trend Equity Strategies"（mdpi.com/2227-7390/14/12/2182，2026-06，同行评审）——PIT/无幸存者抽样回测=本执行器 PIT+去 ST 宇宙同构；② 判据族引用 18 号文 §四在册题录（不凭记忆）。⚠ **诚实注**：本轮 WebSearch 未独立复现 Nefedov 2025 SSRN 精确条目（仅得泛化过拟合源），故裁决性引用锚定在册出处，不新立记忆断言。A 股适配：成本门五档含涨跌停/换手 8x 约束（exam_scale_cost_gate），适配通过 |
| ④后端 | 方案① T3 代码在码、红蓝未跑（LK-11）；n_trial MOD-BT-200 stability=experimental（未 stabilized）；PBO/CPCV 引擎字段不回填=f06/执行器无 pbo_value/cpcv_*（LK-08） | 开源对表（SKEL §9）：skfolio CombinatorialPurgedCV（BSD-3，CPCV 接线对表）；pypbo（PBO/CSCV 参考，许可证引入前须核）；deflated-sharpe PyPI **零引入**（仓 MOD-SIM-024 唯一真源铁律） |
| ⑤前端 | 成绩单 manifest/summary 无上板通道=IBT-G01（grid_* 产物无前端源，`backtest_results.py` 现无此源，SKEL L06-C09） | 已查无：网格成绩单无 dashboard 页；登记边界随上板桥 |
| ⑥数据字段 | summary 有 `n_trials_effective`（实测=12）但 ledger 侧同名位恒 None（:138）⇒ **两处口径不同源**（执行器自算 vs 账本预留，复核消费链）；manifest 表头无 cost 列（见 ②观察）；17 §一判据字段=backtest_dead/eval_dead/degraded=0（实测全 0）+ N_eff≥12（实测 effective=12 恰达线） | 待外部反查（业界 manifest 成本列命名无标准，记"已查无+查法=对比 vectorbt/backtrader result 指标 schema"） |

## ④ 缺口清单（沿用 + 续编）

| 编号 | 缺口 | 册内可见性 | 状态/解锁 |
|---|---|---|---|
| LK-08 | PBO+CPCV 进考试验收链（f06/执行器回填字段，消费 G2 门） | SKEL L06-B/C | 施工；CPCV purge/embargo 入预注册（冻结件，须裁定） |
| LK-11 | T1 轻档成本路径：代码已备、红蓝对拍未跑+prereg 分层未冻结+重签未做 | SKEL L06-A ⑥ / 17 §二 | 挂起；解锁=GPU 空窗+LANE-RB 收口（**本块不碰其路径/判据**） |
| IBT-E02 | n_trial 记账 E1C/LLM 轨零实证 | 11 §5.6 | 挂起；随治理级考试循环 |
| **L06-C16（新，册内未见）** | **prereg 预算数值与现实 5.2× 背离**：`per_point_seconds_measured:35.33` vs 估 6.8s，自注"T1/T2 配比待裁定重排"（frozen 件 :57） | 本块新立 | 挂起→裁定；**本块只登记不擅改**；解锁=Owner/裁定#413 附属通道重排 tier1/tier2 点 |
| **L06-C17（新，册内未见）** | **manifest 成本列 schema 待核**：T0 run 无 `cost_adjusted_sharpe`/`cost_tier_sharpes_json` 列，与 SKEL L06-A ③ 断言不符；17 §一成本门真实性判据依赖此列 | 本块新立 | 复核→成绩单验收前置：T1 manifest 落盘后核列是否齐；若缺则成本门真实性无法按 manifest 抽查 |

## ⑤ 自审闸三态裁定（mining_sop §6）

- **终局定位**：搜索执行器+预注册防线是"成绩单一键产出+防过拟合"的机器咽喉，终局必全自动（Owner 仅裁定重排预算），**不封矿**。
- 三态分布：
  - **施工**：LK-08（PBO/CPCV 接线，字段级）、L06-C17（manifest 成本列核验后按需补）。
  - **挂起排期（解锁明确）**：LK-11（GPU 空窗+LANE-RB 收口）；L06-C16（prereg 预算重排=裁定门位）；成绩单未出属时序非规模。
  - **登记不越界**：红蓝对拍（LANE-RB）、T1→T2 自动接棒（LANE-AUTO）路径/判据均不碰，只标边界。
- **矿脉判据**：执行器全链+prereg 逐字段+账本+DSR+产物新鲜度均 file:line/实测坐实；外部双源锚定 PIT-backtesting。**新挖两处（预算 5.2× 背离、成本列缺失）为结构级、非现状规模判**——矿脉未枯但本块见底。

## ⑥ 挖矿日志（mining_sop §7）

| 轮 | 矿脉 | 动作 | 判定 | 归因 |
|---|---|---|---|---|
| R1 | 执行器+prereg+账本+产物 | grep factory_grid_executor 锚点 + 读 prereg budget/e7 + grep n_trial_ledger 头注 + ls/采样 26+ grid 目录 + cat T0 summary.json + head manifest.csv | **signal**（预算 5.2× 背离新发现、manifest 无成本列 schema 差异、跑中空目录预期实证、n_trials_effective 两处不同源） | — |
| R2 | ③算法向外（多重检验判据族+PIT backtest） | WebSearch Nefedov2025/DSR（泛化源，MDPI 2026 PIT 命中）+ 引用 18 号文在册题录 | **signal（部分）** | Nefedov 精确 SSRN 条目本轮未复现=如实标"未独立复核"，不伪造 |
| R3 | 前端上板 + 成本列核验 | grep backtest_results.py（无 grid 源） | **查无**（面板无成绩单源=IBT-G01 已知，记档） | 归因=方向本就无物（上板桥未建），非搜索不当 |

> 本块无 noise 轮。邻块边界：考尺 E4 三阶段/三道门/闭卷窗 → `../exam_ruler_holdout/MINE.md`；红蓝对拍判据 → LANE-RB（不碰）。

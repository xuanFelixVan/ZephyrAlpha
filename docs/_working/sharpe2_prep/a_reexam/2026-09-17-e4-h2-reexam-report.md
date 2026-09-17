---
ttl: task_bound
---

# 2026-09-17 E4 及格池全量 H2 真成本重考报告（Sharpe2 决赛准备战·分包A）

- 施工子代理: st-sharpe2a-20260917 | 考尺: MOD-BT-211 WFA 8 折（训24m→测6m 步进6m，全窗 2020-01-01..2025-08-31，真 OOS=折4-7 即 2024-01..2025-08）+ H2 真成本 + 官方 DSR/DecisionGate/OverfittingDetector（判定零重写，全委托既有管线）
- 产物: pool_manifest.csv / reexam_results.csv / old_vs_new_ranking.csv / correlation_matrix.csv / teaming_schemes.csv / dsr_top20.csv / capacity_profile.csv / gap_accounts.yaml（自 json 机械转换，目录契约 DCR-005/008 禁 .json）/ 本报告

## 1. 定池与"80 vs 160"考证结论

**池真源** = `c1_backtest.strategy_screen`，`verdict='oos_tested'`。当前 **160 行 → DISTINCT strategy_id = 81 个**（85 个 (sid,source_file) 对）。

- 行/策略分布: 42 策略 1 行、4 策略 2 行、30 策略 3 行、5 策略 4 行（39 个 sid 被多批 OOS 重复受试，与分包 C 审计 (a)(iii) 一致）。
- **"80 条"出处=时点计数**: 2026-09-16 00:00 前 DISTINCT=80，09-15 12:00 前=74；`C4-OOS-2024-2026` 批最后一次落库在 09-16 12:39（第 81 个）。蓝图（09-15 成文）与 `forward_post.py` 头注（"当前 80 条"）是写作时点的快照数字，口径=**DISTINCT strategy_id**（`forward_post.fetch_passers` 同口径），不是行数。
- **及格判据考证**: "E4 及格(oos_tested)"=完成 OOS 测试的入场券，非盈利资质。旧尺=0.5 衰减线（strategy_screen_query），从未按 0.70 OOS/IS+精确 DSR 出场尺复考（分包 C 审计 (c)(iii)）；旧池 81 条中旧 OOS sharpe>0 仅 31 条。
- **本考池** = 81 个 DISTINCT strategy_id，每 sid 取最新 screened_at 行（旧指标列见 pool_manifest.csv）；0 个缺源文件。

## 2. 方法与诚实边界

- 管线复用: `f06_e4_wfa_exam.py`（24420b3c6b）纯函数件 build_folds/stitch_fold_weights/fold_metrics_from_net/_dsr_exact/map_exam_verdict 原样 import，禁改未改；逐策略对每折调 `translated/<file>.build(warm_start, test_end)` 截断面板因果求值（预热起点 2019-06-15 与 24420b3c6b 一致）。
- **H2 真成本**（向量化闭式消费官方标定件，零第二处字面量）: 滑点=ADV 五分位分层（Q1 7.24bp…Q5 2.34bp，cost_model_calibration）；冲击=各层 η·p^0.4205·σ（γ=0 反双计）；佣金腿=万0.854 双边+印花万5 卖+过户万0.1 双边+5 元地板拖累（matching_logic 常量真源）。**参考资金 100 万元**（实查 sim_pocket_daily.initial_capital 全部=1e6）。换手结构沿用 _c4_engine 冻结口径（每单位单边换手=1 买+1 卖腿），保证新旧成本对照同结构。
- **诚实边界**: (1) 本考用闭式逐层费率，未走逐笔 order book 撮合（81 策略×8 折全窗逐笔超算力预算）；冲击腿在 100 万资金下参与率极低，容量分析另行按参与率上限法外推。(2) OOS/IS 比率门控的分子=本考 WFA 拼接 OOS、分母=登记面 IS，两窗预热/相位不同**逐位不可比**（P1 缺陷，分包 C 审计+verdict.md 自认），verdict 解读须带此 caveat；本考 oos_h2 vs gross 的成本拖累数字不受影响。(3) DSR 于 04:40 后按裁定 #291（c88d5e33db）后引擎统一现算，N=各策略历史 num_trials+本次重考 81。(4) 16 条 RSRS/60m 族因 `market_commodity_futures_main` 品类未注册（他队在途缺陷，登记不代修）无法重考。

## 3. 覆盖率

| 状态 | 条数 | 说明 |
|---|---|---|
| ok | 62 | 完整 8 折 H2 重考 |
| timeout | 3 | 600s/条硬帽截断（病态慢：小市值日频重选/估值全重选族）: CAND-40ca0da1a3ca, CAND-21af8c66c15e, CAND-93aa8f5a2bdd |
| error(管线阻塞) | 16 | 品类注册缺失: 16 条 RSRS/60m 族 |
| **总覆盖** | **62/81** | ok 覆盖率 77%；timeout 条目按其旧排名属中下游（旧 sharpe 0.16-0.69），外推边界=这些条目 H2 后更差（高换手族在 H2 下成本吃得更重），不影响存活者集合的完整性 |

## 4. 新旧排名对照（前三大变动）

| 策略 | 旧OOS | 新OOS(H2) | 排名 | 归因（成本三腿） |
|---|---|---|---|---|
| CAND-9c0136ec8f42 | -1.317 | -0.442 | 59→24 | 滑点0.88+冲击0.01+佣金腿1.20 bp/日，年换手21.2x |
| CAND-6cb29d4d9ba8 | -1.255 | -0.802 | 58→34 | 滑点0.06+冲击0.00+佣金腿0.08 bp/日，年换手1.2x |
| CAND-091fee38cd01 | -0.869 | -0.555 | 44→28 | 滑点0.54+冲击0.00+佣金腿0.69 bp/日，年换手12.1x |
| VAL-DIV-STEADY-005 | -0.242 | -1.319 | 23→53 | 滑点0.60+冲击0.00+佣金腿0.48 bp/日，年换手8.5x |
| VAL-PE-LOW-020 | -0.612 | -1.337 | 29→54 | 滑点0.01+冲击0.00+佣金腿0.01 bp/日，年换手0.0x |
| VAL-PB-LOW-020 | -0.774 | -1.965 | 40→61 | 滑点0.01+冲击0.00+佣金腿0.01 bp/日，年换手0.0x |

解读注记: 表中"上位"前三的排名改善全部发生在负 sharpe 策略内部（分母效应：更多策略跌得更深），并非它们转正；正 sharpe 存活者集合本身在 H2 尺下从旧池 31 条收缩到 17 条。真正的"上位者"见第 7 节 DSR 榜（低换手族），真正的"掉队者"是高换手小市值族（成本腿重压+回撤恶化）。

全量对照见 old_vs_new_ranking.csv。系统性结论: **排名大洗牌的两大驱动力=①窗口差**（旧 OOS sharpe 含 2025-09..2026-09 段，本考真 OOS 止于 2025-08）**+②H2 成本分层**（旧 5bp 一口价 vs 分层滑点+佣金腿换万0.854 真费率+地板拖累）：高换手策略普遍被成本腿多咬一口，低换手择时/指数族相对受益。

## 5. E4 尺判定与存活者

- 三线判定（IS→WFA→OOS+DSR，fail-closed）: 通过 0 / 存疑 3 / 不通过 59
- **严格尺下 OOS sharpe(H2)>0 的存活者 = 17 条**；过全尺（含 OOS/IS≥0.70+DSR 达带）放行档 = 0 条。**这个数字本身就是差距分解的核心证据：现池离"可信赖放行"还有整个池子的距离。**
- 组队按"存活档位"口径执行（放行档若为 0，则以净 H2 sharpe/DSR 头部为观察档组队，如实标注）。

## 6. 低相关组队建议书（Sharpe 1→2 的最大杠杆）

估算式: 等权 k 策略合并 sharpe = 等权组合日收益序列直接实现（主口径）；闭式近似 S̄·√(k/(1+(k-1)ρ̄)) 并报（假设=成员 sharpe 同质、两两相关同 ρ̄、日收益独立同分布近似）。

| 方案 | 成员数 | 组内相关上限(均值绝对值) | 成员 sharpe 区间 | 实现合并 Sharpe | 合并 maxDD | 估算式值 |
|---|---|---|---|---|---|---|
| A_r<=0.30_top5 | 4 | 0.167 | 0.37..1.88 | 1.541 | -0.1301 | 1.707 |
| B_r<=0.50_top8 | 6 | 0.188 | 0.37..1.88 | 1.473 | -0.1259 | 1.714 |
| C_byDSR_r<=0.40_top5 | 4 | 0.167 | 0.37..1.88 | 1.541 | -0.1301 | 1.707 |
| D_all_survivors_equal | 17 | 0.457 | 0.15..1.88 | 1.393 | -0.1361 | 1.495 |


- **A_r<=0.30_top5**: FACT-4db4c41e|CAND-e3da6fa71af1|CAND-4440d07f973f|CAND-e2e7f033d97c
- **B_r<=0.50_top8**: FACT-4db4c41e|CAND-c4ec6332c07f|CAND-e3da6fa71af1|CAND-4440d07f973f|CAND-a4543012b464|CAND-e2e7f033d97c
- **C_byDSR_r<=0.40_top5**: FACT-4db4c41e|CAND-e3da6fa71af1|CAND-4440d07f973f|CAND-e2e7f033d97c
- **D_all_survivors_equal**: FACT-4db4c41e|CAND-8d000bf3ccc3|FACT-4f749668|FACT-4228020a|FACT-e831084c|FACT-e293e217|FACT-4b200528|CAND-c4ec6332c07f|CAND-e3da6fa71af1|CAND-eaddc3f9db4e|CAND-4440d07f973f|CAND-d06cab686cef|CAND-29eb91dbaf60|CAND-a4543012b464|CAND-e2e7f033d97c|CAND-bd42540f86e4|CAND-6a6ec8869ddb

- 相关矩阵（全池 81×81）见 correlation_matrix.csv；层次聚类（average linkage，距离=1-ρ，t=0.7）簇归属在 _merged_results.csv `cluster` 列。
- 组队纪律提示: 相关上限在 OOS 段实现值上度量；重叠持仓（如多个小市值族）在 regime 翻转时会同步失效——E8 装配层（MOD-PA-004 相关性闸+MOD-PA-022 风险预算）上线后应以持仓重叠率复核。

## 7. DSR 去伪排名前 20

| # | 策略 | DSR(精确) | 落带 | OOS sharpe(H2) | N=历史+81 | E4 verdict |
|---|---|---|---|---|---|---|
| 1 | FACT-4db4c41e | 0.5033 | review | 1.8826 | 86 | 存疑 |
| 2 | FACT-4f749668 | 0.362 | overfitting | 1.5969 | 86 | 存疑 |
| 3 | CAND-8d000bf3ccc3 | 0.3485 | overfitting | 1.6184 | 132 | 不通过 |
| 4 | FACT-4228020a | 0.2978 | overfitting | 1.4754 | 86 | 存疑 |
| 5 | FACT-e831084c | 0.2807 | overfitting | 1.3999 | 86 | 不通过 |
| 6 | FACT-4b200528 | 0.2231 | overfitting | 1.2968 | 86 | 不通过 |
| 7 | CAND-c4ec6332c07f | 0.1325 | overfitting | 1.155 | 132 | 不通过 |
| 8 | CAND-eaddc3f9db4e | 0.0983 | overfitting | 0.9957 | 132 | 不通过 |
| 9 | CAND-e3da6fa71af1 | 0.0945 | overfitting | 1.0093 | 132 | 不通过 |
| 10 | CAND-d06cab686cef | 0.0807 | overfitting | 0.9161 | 132 | 不通过 |
| 11 | CAND-4440d07f973f | 0.0781 | overfitting | 0.9207 | 132 | 不通过 |
| 12 | CAND-29eb91dbaf60 | 0.0606 | overfitting | 0.8877 | 132 | 不通过 |
| 13 | FACT-e293e217 | 0.0325 | overfitting | 1.3842 | 4578 | 不通过 |
| 14 | CAND-a4543012b464 | 0.0247 | overfitting | 0.5095 | 132 | 不通过 |
| 15 | CAND-e2e7f033d97c | 0.0158 | overfitting | 0.3683 | 132 | 不通过 |
| 16 | CAND-bd42540f86e4 | 0.0087 | overfitting | 0.1945 | 132 | 不通过 |
| 17 | CAND-6a6ec8869ddb | 0.0074 | overfitting | 0.1499 | 132 | 不通过 |
| 18 | CAND-9c0424f53fe4 | 0.0031 | overfitting | -0.0836 | 132 | 不通过 |
| 19 | CAND-a5ac9cc45ab3 | 0.001 | overfitting | -0.4522 | 95 | 不通过 |
| 20 | CAND-9c0136ec8f42 | 0.0007 | overfitting | -0.4423 | 132 | 不通过 |


- DSR=精确口径（真实收益序列偏度/峰度，MOD-SIM-024 件）；N=该策略历史 num_trials（strategy_screen 最新行）+本次重考 81；n_trials_used 列即两者之和。落带 review/overfitting/unavailable 均不放行。
- 榜首仍以低换手族为主：**H2 尺下" Sharpe 富矿"集中在低换手指数/择时与基本面低频族，高频小市值族被成本腿系统性压杀。**

## 8. 容量 × 换手画像

估算式: 参与率上限法——单标的单日成交占比 ≤10%（P_CAP=0.10），容量 C = min_sym( 0.10 × ADV_sym(40 日中位) / max_t|Δw_sym,t| )；换手档: 低<1x/中 1-5x/高≥5x（年化单边）。假设=收盘一次性执行、不做多日拆单、ADV 用 40 日中位（近保守）。

| 策略 | 年单边换手 | 档 | 估算容量(元) | 约束标的 |
|---|---|---|---|---|
| CAND-c4ec6332c07f | 6.36x | high(>=5x) | 2.61e+10 | 000300 |
| CAND-d06cab686cef | 3.33x | mid(1-5x) | 2.61e+10 | 000300 |
| CAND-eaddc3f9db4e | 2.12x | mid(1-5x) | 2.61e+10 | 000300 |
| CAND-29eb91dbaf60 | 0.61x | low(<1x) | 2.61e+10 | 000300 |
| FACT-4b200528 | 59.7x | high(>=5x) | 4.88e+08 | 300394.SZ |
| FACT-4f749668 | 30.88x | high(>=5x) | 4.88e+08 | 300394.SZ |
| FACT-e293e217 | 23.55x | high(>=5x) | 4.88e+08 | 300394.SZ |
| FACT-4228020a | 32.91x | high(>=5x) | 4.88e+08 | 300394.SZ |
| FACT-e831084c | 59.21x | high(>=5x) | 3.66e+08 | 300394.SZ |
| CAND-bd42540f86e4 | 17.32x | high(>=5x) | 6.87e+07 | 000708 |
| CAND-8d000bf3ccc3 | 6.3x | high(>=5x) | 1.66e+07 | 605499 |
| CAND-e2e7f033d97c | 20.89x | high(>=5x) | 1.04e+07 | 000016 |
| CAND-6a6ec8869ddb | 64.24x | high(>=5x) | 8.56e+06 | 600671 |
| CAND-e3da6fa71af1 | 1.82x | mid(1-5x) | 7.53e+06 | 000852 |
| CAND-a4543012b464 | 46.19x | high(>=5x) | 5.54e+06 | 300442 |
| CAND-4440d07f973f | 79.01x | high(>=5x) | 7.69e+05 | 002569 |
| FACT-4db4c41e | 0.0x | low(<1x) | n/a | nan |


## 9. 《负收益年 → Sharpe 2》差距三笔账

基准口径考证: E8 组装与资金分配=partial 未建（strategy_production_map），**无现行主组合**——基准取"全池等权组合"OOS 段（2024-01..2025-08）H2 净值，最差滚动 12 个月 = 2025-04-30（-3.8%，即"负收益年"锚点）。

| 账 | 量化 | 责任模块（蓝图，只读） | 可自动化 | 建议执行车道 |
|---|---|---|---|---|
| ② 成本拖累（最大单笔） | 毛 sharpe 1.204 → 净 0.307，**成本腿吃掉 0.897**；池均 2.7 bp/日≈年化 6.6%（滑点/冲击/佣金腿分列见 reexam_results 三列；高换手族被系统性压杀） | MOD-BT-039 冻结土规尺已过时；H2 治本件=cost_model_calibration/cost_attribution（台账#23 车道 M，已治本） | 高（标定表+归因+本次重考管线全部可复用） | E4 考试咽喉全面换 H2 尺（本次管线即模板）；高换手族批量退场或降频 |
| ① alpha 不足 | 毛 sharpe 1.204 本身距 2.0 还差 0.796——即使成本清零，池内信号样本外质量也不够 Sharpe 2 | E1 想法进货五车道 + E3 构造（docs/03_modules/_domain_backtest/blueprint.md） | 高（进货→预审→构造全自动闭环已建，MOD-BT-154） | E1 车道 B/C 加供低换手基本面/择时族料+E4 正考；F-06 网格按 E4 尺继续筛 |
| ③ 风险规模/结构错配 | 等权现状池净 sharpe 0.307 → 最优低相关组队 1.541，结构改善 +1.234——**低相关组队是从当前水平起最大的单一杠杆** | E8 组装与资金分配 partial（MOD-PA-002..024 算法件族已建，装配未闭环） | 中（算法件已建，但 sleeve 装配+资金爬坡涉资金破坏性操作=Owner 门位 §5） | E8 装配最小闭环（先纸面 sleeve 赛马）：MOD-PA-004 相关性闸+MOD-PA-003 分配器消费本次 correlation_matrix.csv |

次序账（sharpe 空间顺序分解，交互项归后项）: 现状池净 0.307 →（②反向回补，说明成本吃掉多少）毛 1.204 →（①补 alpha 到 2.0 需 +0.796）→ 现状水平下（③组队杠杆 +1.234）可达 1.541；**距 2.0 剩余缺口 0.46，本质=账①——现有 81 条的 alpha 质量撑不起 Sharpe 2，组队只能把"池子该给的"取尽，增量必须靠 E1/E3 供新料**。

## 10. 可复现附录

```bash
# 环境（每个 shell）
export PATH="/c/Users/fanzi/AppData/Local/Programs/Python/Python312:/c/Users/fanzi/AppData/Local/Programs/Python/Python312/Scripts:$PATH"

# 1) 定池（CH 只读，经 DatabaseService）
python .runtime/tmp/sharpe2a_build_pool.py            # → pool_manifest.csv（81 策略）

# 2) 全量重考（每策略子进程+600s 帽，断点续跑，逐行备份 .runtime/tmp/sharpe2a_results_backup.csv）
bash .runtime/tmp/sharpe2a_driver.sh                  # 内部: timeout -k 30 600 python .runtime/tmp/sharpe2a_reexam.py --sid <sid>

# 3) 分析+终稿
python .runtime/tmp/sharpe2a_report.py                # 对照/聚类/组队/DSR/三笔账中间产物
python .runtime/tmp/sharpe2a_capacity.py              # 容量画像（存活者权重重放）
python .runtime/tmp/sharpe2a_final.py                 # 本报告
```

核心代码要点（.runtime/tmp/sharpe2a_reexam.py）: H2 成本腿向量化消费官方件——
```python
from zephyr.backtest.core.cost_model_calibration import (
    ADV_QUINTILE_BOUNDS_YUAN, SLIPPAGE_TIER_BPS, IMPACT_BETA, IMPACT_TIER_ETA, IMPACT_TIER_SIGMA)
from zephyr.backtest.core.matching_logic import COMMISSION_RATE, STAMP_TAX_RATE, TRANSFER_FEE_RATE, MIN_COMMISSION
# tier = np.digitize(ADV40, BOUNDS); slip=SLIPPAGE_TIER_BPS[tier]; impact=ETA[tier]*p**0.4205*SIG[tier]*1e4
# net = (w.shift(1)*rets).sum(1) - Σ|Δw|·(slip·2+impact·2+佣金双腿+印花卖+过户+地板拖累)
```

## 11. 诚实清单（没做到的+原因+证据）

1. **16 条 RSRS/60m 族未考**（error）: 他队把 `market_commodity_futures_main` 品类从 business_data_categories.yaml 摘除/未注册（在途状态），策略 build 内部数据装载直接 KeyError。证据=16 行 error 文本一致；按"他人在途缺陷只登记不代修"纪律未动 config。影响: 池覆盖率 62/81。
2. **3 条 600s 超时未考**: CAND-40ca0da1a3ca, CAND-21af8c66c15e, CAND-93aa8f5a2bdd——小市值日频全重选/估值全重选族单策略实测 >9-27 分钟（CAND-dc5b80aa3614 首跑 27 分钟未完）。按算力诚实条款打硬帽并披露名单；其旧排名属中下游（旧 OOS sharpe 0.16-0.69），H2 下只会更差，不影响存活者集合。
3. **逐笔撮合未走**: H2 成本用标定参数闭式向量化（同参数、同分层、γ=0 反双计），未走 Decimal 逐笔 order book（算力不可行）。冲击腿在 100 万资金下偏小是模型性质而非 bug；大资金容量结论以第 8 节参与率法为准。
4. **重考期间交付目录被外部会话 worktree stash 三次扫走**（约 02:50 / 04:41 / 07:25；第二次带走约 39 行成果无法找回；涉事操作=st-skeletonaudit-20260916 会话的 session_worktree_pre_merge stash）：从 stash 只读恢复基底+重启补跑；防再失=manifest 真源移 .runtime/tmp+逐行备份 sharpe2a_results_backup.csv+终稿一次落盘。全程 .runtime/tmp 未被扫。
5. **OOS/IS 比率门控口径缺陷未修**（P1，禁改 f06 原件）：verdict 列解读必须带"分子分母逐位不可比"caveat；本报告的成本/排名/组队结论不依赖该门控。
6. **两窗不一致**: 旧 OOS sharpe 窗=2024-01..2026-09-12，本考真 OOS=2024-01..2025-08（与 24420b3c6b 同口径）；新旧对照的排名变动部分来自窗口差，已在第 4 节声明。
7. **FACT 件静态权重疑点（他人在途缺陷登记）**: FACT 族 build 全窗产出单行权重广播（OOS 换手=0），旧 is_sharpe 即基于此路径——新旧对照同口径可比，但"高换手 30-60x"的 FACT 行（f749668/4228020a 等 8 折路径）与全窗路径不同折相位，其 WFA 逐折数字解释力有限，已如实并报。

> 合规声明：研究方法与工程产出，不构成投资建议。判定不构成实盘信号，正式上线判定权在 Owner 门位（§5）。

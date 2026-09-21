---
ttl: task_bound
rule_form: data
verifiability: manual
title: W2-T3 E4 正考收口批次总报（终极令 W2/BM-2·P0 T3，st-final3-20260919）——三组全 RED 收口，零卡进 E4
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-19
session: st-final3-20260919
parent_context: >
  docs/_working/bizmine_night/next_session_directive.md §4 [T3]
  + mid_valley/prereg_card_mid_valley_top10.md（既有冻结卡）
  + factor_sop_screen/prereg_card_f_top20_exam.md（本批执行前冻结）
---

# W2-T3 E4 正考收口批次总报（终极令 W2/BM-2·P0 T3）

> **一句话**：三组 25 项考试对象全部 RED 收口——组① MID 三独立卡 G1 窄测 3×RED（1 实质负 Sharpe+2 构架退化）、组② L1 CORREL/BETA 沿用既有 E4 档案双双「不通过」、组③ F top20 F1 窄测 20×RED（最好 1.177 vs 门 1.4）；**本轮零卡进入 E4 正考**（级联前置未过，非跳过），data/backtest_artifacts/runs/E4-* 本批无新档属如实状态而非缺交付。BH-FDR（q=0.10，23 窄测）零幸存。筛≠考第三次大面积兑现。

## 要素① 任务与范围

终极令 W2/BM-2 P0-T3：E4 正考收口批次。入口 `scripts/backtest/f06_e4_wfa_exam.py`（已验证可运行，本批零改件）；三组=①MID 三独立卡（缺口ATR分级/二进三断板/UTAD，卡面 G1→G2→G3 级联）②L1 risk_off 条件化池 CORREL/BETA（survivors 行已备）③F top20 待考池按 |IC_IR| 序。

## 要素② 方法与执行

- **判定零重写**：E4 通道复用 f06_e4_wfa_exam 内部件（build_folds/stitch/fold_metrics/map_exam_verdict/_dsr_exact）+strategy_validation_pipeline；因子实现零重定义（直调 f2_run.build_price_factors）；RB-STATS-01 两道证据充分性闸（n_dims=1、DSR 分母无可复算档案→unverifiable）按 f06 最严口径预置。
- **预注册纪律**：F 池考试卡在本批任何考试窗取数前冻结（`factor_sop_screen/prereg_card_f_top20_exam.md`，含 N_eff=6 族聚类表——只依赖已入册 IS IC 序列）；MID 卡沿用既有冻结卡零改。考试执行细节（T 收盘信号→T+1 收盘成交→T+2 收益日；引擎现行成本分层滑点；除权邻域剔除；rank='average' 并列处理）在两份执行报告 §1 全披露。
- **数据面**：kline_daily 2018-01-02..2025-08-29（1,860 日×5,518 只；f2 缓存+增量拼接，接缝日 2024-02-29 重叠去重）；ex_dividend_event 36,305 件；vol_pct 去重零冲突。全部经 DatabaseService 只读。

## 要素③ 结果（全部含 RED 入册）

| 组 | 对象 | 考试 | 结果 | 去向 |
|---|---|---|---|---|
| ① | MIDVAL-073 缺口ATR分级 | G1（MID 桶净 Sharpe≥1.4+uplift≥1.5） | MID -1.061/全窗 -1.189，uplift 0.892 | **RED**，级联终止 |
| ① | MIDVAL-017 二进三断板 | G1 | 空仓退化（0 膨胀因子×top10% 构架不可考） | **RED（构架级）** |
| ① | MIDVAL-082 UTAD | G1 | 空仓退化（同上） | **RED（构架级）** |
| ② | IND-STAT-001 CORREL | E4（既有档案 2026-09-19 03:31） | 不通过（WFA 0/0；OOS 0.718；DSR 0.6223 review） | 已收口，唯一后路=新卡另预注册 |
| ② | IND-STAT-002 BETA | E4（同上） | 不通过（WFA 0/0；OOS 0.730；DSR 0.6348 review） | 已收口，同上 |
| ③ | F top20 全池 | F1（全窗净 Sharpe≥1.4+BH q≤0.10） | 最好 FCT-LIQ-031 立桩量 1.177；ATR14/布林收口 1.148（同族互证）；20/20 未达 | **20×RED**，级联终止 |

- **多重检验必报**：23 场窄测 BH-FDR（q=0.10，单侧 t 弱口径已披露）：最小原始 p=0.065 → **p_adj 全体=1.0，零幸存**（门槛判 RED 与 BH 判 RED 双向一致，结论对多重检验校正稳健）。
- **G2/G3 状态**：0 卡进入 → E4 WFA 与 DSR 未触发（MID N_eff≈4、F 池 N_eff=6 两个冻结折减分母均未消费，留档后续批次）。

## 要素④ 产物与归属

- `mid_valley/g1_narrow_exam_report.md` + `g1_narrow_exam_results.csv`（组①全字段入册）
- `factor_sop_screen/prereg_card_f_top20_exam.md`（执行前冻结）+ `f_top20_narrow_exam_report.md` + `f_top20_narrow_exam_results.csv`（组③）
- 本总报 `w2t3_e4_exam_closure_report.md`
- 中间件（不入 git）：`.runtime/tmp/bizmine/w2t3/`（data/factors/nets/wts/narrow_*.csv）；复用只读缓存：`.runtime/tmp/bizmine/f/cache/`、`.runtime/tmp/bizmine/mid/`
- data/backtest_artifacts/runs/E4-BIZMINE-L1-IND-STAT-00{1,2}-*/（组②既有档案，本批核验一致：summary↔survivors 行↔verdict 三面相符，crosscheck 三项全 ok）

## 要素⑤ 偏离、占用登记与未达成

1. **data/strategy_intake 工厂车道占用（动工前复核结论）**：git status 实查 `three_high_candidates.csv`+20 行（E1D-20260919-100005，今日 10:00）与 `translated_manifest.csv`+3 行（10:01）未提交在途，`docs/_working/factory/strategy_cards/e4_report_s_owner_002_regime_switcher.md` 暂存在途——**登记等位照办**：本批考试输入实际绑 `f06_survivors.csv`（未被占）与 docs 侧册，零写 intake，无硬闯；f06 入口件亦零改（经 --survivors-csv 侧册路线即无需写 intake，L1 车道先例同法）。
2. **E4 正考零新档=如实状态**：级联前置（G1/F1）全 RED 机械终止，非执行缺位；按「禁把筛当考」不代跑、按「禁改卡」不降门。
3. **组②沿档收口**：CORREL/BETA E4 系 W2 前批（今晨 03:31）产物，本批核验三面一致后登记收口；「WFA 0/0 折通过」为该先例路线判定层已知形态，判「不通过」结论不受影响。
4. CREATE-GUARD 批量通道按令执行时顺带登记了 algo_mining 三张他会话在途卡的 token（幂等纯插入，预登记无害）；本批自有新件已按子前缀补登记。
5. 未达成项：无隐藏未达成——三组考试对象 25 项全部有结论（23 窄测 RED+2 沿档不通过）。

## 要素⑥ 后路与建议（备 Owner/总包裁定，未代裁）

1. **稀疏因子构架新卡**：二进三断板/UTAD（及下方缺口/假突破）的 IC 边际住在事件尾部，「top 10% 多头」构架不可考——若要继续，走事件研究法或含规避腿/空头腿的新预注册卡（Owner 门位）。
2. **ATR14/布林收口（低波族）**：毛 Sharpe 1.33/1.39、换手仅 0.08-0.12，是本批最接近门的候选；复权链修复（W3 X-2）后按 RB 优先序全量复核时值得第一优先重考，届时若毛侧站上门槛可另立卡（如双周调仓降成本变体）。
3. **E4 档案面**：本轮 0 新档；runs/E4-* 目录已有 4 个档案（F06/CORREL/BETA/E1C09）全部「不通过/存疑」，bizmine 线累计仍无一条过 E4——弹药账（@H2 OOS Sharpe≥1.4 缺 4 条）缺口未缩小，下一批建议主攻组合层条件化与非 F-skip 结构数据（MID 报告 §4.1 方向），而非继续日频截面因子换血。

> 合规声明：研究方法与工程产出，不构成投资建议。

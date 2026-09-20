---
ttl: task_bound
---

# 2026-09-17 E4 及格池判据防自欺审计报告（Sharpe2 决赛准备战·分包C②）

- 审计子代理: st-sharpe2c-20260917（只产报告，不动手）
- 考尺: `scripts/backtest/f06_e4_wfa_exam.py`（WFA 8 折三阶段，训 24m→测 6m 步进 6m）
- 样例产物: `data/backtest_artifacts/runs/E4-F06-38b453ca/summary.json`（fail-closed 否决件）
- 数据源: CH `c1_backtest.strategy_screen`（1205 行，`oos_tested`=160 行）+ `trial_ledger_registry.yaml` + `data/strategy_intake/f06_survivors.csv` + `grid_*/summary.json`
- 基线: `fe8fce25b7`；CH 数字为 2026-09-17 实查

**先说公道话**：样例幸存者 38b453ca3683 被 E4 考尺 **fail-closed 正确否决**（OOS/IS=0.4989<0.70 硬线 + 精确 DSR 0.3046(N_eff=9)/0.0027(N_raw=10,080)<0.5，verdict=不通过，can_deploy=False）。考尺本身没有放水；本报告审的是"及格池（160 行 oos_tested）与幸存者生产线"的自欺面。

---

## (a) 考试窗口重叠 —— 判定：部分成立

**真不重叠的部分（机械验证通过）**：
- `build_folds`（f06_e4_wfa_exam.py:71-131）保证：每折 train_end < test_start（`:126`）；相邻折测试窗互不重叠（`:127-128`，且 `:90-94` 强制 step>=test 否则 ValueError）；测试窗不越全窗（`:129-130`）。实际 8 折（summary.json folds）：折 0 测 2022-01..06 → 折 7 测 2025-03..08，逐折紧邻无重叠。**折切分无泄露成立。**

**成立的部分（三处跨考试污染）**：
1. **折 0-3 测试段 ⊂ 幸存者选择窗**：折 0-3 测试段 2022-01..2023-12 落在出生批 IS 窗 2020-01-01..2023-12-31（grid_20260916-123551 summary `window` 字段）内——该段数据参与了"10,080 选 1"的选择，其"测试"是选择偏内的稳定性证据。**档案已诚实披露**（f06_e4_wfa_exam.py:29-31、verdict.md 诚实边界），属已披露的已知局限而非隐瞒。
2. **E4 "真 OOS" 段是二次消费**：E4 的真 OOS=折 4-7 测试段 2024-01..2025-08（`DEFAULT_OOS_START=2024-01-01`），与快考批 grid_20260916-233634 的 `window`（2024-01-01..2025-08-31）**完全相同**。同一配方先在快考窗被看过一次（并据其"通过"取得幸存者身份），E4 再考同一段——OOS 段对同策略第二次消费，无多次观察折减。
3. **CH 及格池存在系统性 OOS 重复受试**：`strategy_screen` 中 **39 个 strategy_id 有 >1 行 oos_tested**，跨 4+ 个不同 OOS 窗批（C4-OOS-2024-2026 / C4-OOS2-20260913 / C4-OOS2-20260914 / C4-OOS3-*/C4-2016-2019-sample3）。样例：CAND-e2e7f033d97c 三批受试三次（is_sharpe 均 −0.048，屡败屡试）；**CAND-8d000bf3ccc3 同批 C4-OOS2-20260914 两行 is_sharpe 1.173 vs −0.842**——同批同 sid 结果翻转，批内可复现性存疑（配置漂移或 run_id 未对齐），需查因。此外存在 2016-2019 "过去窗"批（C4-2016-2019-sample3），OOS 窗口径不统一。

**对及格池可信度影响：高**。OOS 数据被多窗多次消费且无 DSR/Bonferroni 折减，"oos_tested"作为资质标签被稀释。
**补救建议（不动手）**：OOS 段一次性消费台账（配方级登记"该段已对它看过几次"）；同批同 sid 双行（至少 CAND-8d000bf3ccc3 等 4 件）专项查因；2016-2019 批单独标签不与前瞻 OOS 混算。

## (b) 多次搜索只报最优 —— 判定：部分成立（双口径并报诚实，但及格资格依赖宽松 N_eff 口径，且计数账漂移）

1. **搜索协议 = "搜 N 挑 1"，非预注册单次**：出生批 grid_20260916-123551 `mode=batch_b_subspace`，`n_raw=362,880`（13 维离散网格全枚举空间），`n_sampled=evaluated=10,080`，IS 窗 970 交易日；幸存者=10,080 次 IS 回测的最优头部（is_sharpe=1.721）。快考批再 8 挑 1。
2. **DSR 的 N 口径双轨并报是诚实的**：survivors.csv 同时登记 `dsr_eff=0.9593, n_trials_eff=9` 与 `dsr_raw=0.3002, n_trials_raw=10080`；E4 summary 亦双口径并报（exact_eff 0.3046 / exact_raw 0.0027）。commit 9c9da4a587 明写"N_eff 口径 2 条幸存者 vs N_raw 口径 0 条并报"。**没有只报好看的那个。**
3. **但及格资格实际取决于 N_eff=9 口径**：raw 口径下幸存者为 0——池子的存在性系于 effective_rank 估计器把 10,080 次试验折算成 9 条独立收益流（13 维网格大量参数不改变收益流，机械上可辩护）。**该估计器自身读数不稳**：台账 n_trials_effective 链 18（批 123552, n=5,990）→ 9（批 123551, n=10,080）→ 2（批 233634, n=8），三批三个值，无冻结版本/口径裁定。
4. **计数账漂移（模式 #1 变体）**：台账 counting_rule `count = screen_runs.total_trials(277) + sum(batch_records.n_trials)(4,214) = 4,491`；但 `strategy_screen.num_trials` 实存 **4,482 / 4,487 / 4,497 三种快照值**（无一等于 4,491）；且两大批 **grid_20260916-123551 (n=10,080) 与 123552 (n=5,990) 未入 batch_records**，只藏在 n_trials_effective 的 note 里——台账 count 低报真实累计可审计试验数（≥20,569）。num_trials 与台账**不同源一致**。
5. **screen 表内 num_trials 语义混杂**：oos_tested 160 行的 num_trials 从 1 到 4,497 跨 4 个数量级（51×51 行、35×70 行…），说明"该行 sharpe 背后的搜索次数"逐行不同，但 DSR 折减是否按行计入未见登记。

**对及格池可信度影响：高**。
**补救建议**：N_eff 估计器冻结版本并走裁定登记（RULE-RULING）；batch_records 补登 123551/123552 两大批（幂等重算 count）；num_trials 全表按出生批回填重算，与台账对账。

## (c) 参数过拟合信号 —— 判定：成立（信号充分，本次被考尺拦住；但及格池存量未过此尺）

1. **自由度 vs OOS 年数**：配方 13 维离散参数（A1/A2/B/C/D1/D2/E/F/G/H/I/J/K），网格空间 362,880；IS 仅 970 日（~4 年）、"真 OOS"仅 403 日（~1.67 年）。best-of-10,080 的 IS=1.721 必然含选择偏倚；对比快考 retention 0.483、E4 拼接 retention 0.4989——**选择红利在 OOS 蒸发约一半**，是教科书式过拟合信号。
2. **池内衰减分布**：oos_tested 160 行中 `oos_years_decay` 非空 148 行，均值 0.284，**≥0.5 存疑线 37 行（25%）仍在池**；12 行 decay 为空（缺失未拦截）。
3. **三把尺并存**：C4 bothwin 及格线=decay<0.5（strategy_screen_query.py:150,179）；F06 快考让 retention 0.483（即衰减 51.7%）的幸存者"通过"；E4 硬线=ratio≥0.70（等价 decay≤0.30）。同一资质概念三道阈值（0.5 衰减 / 0.5 衰减 / 0.70 保留）不互通——**160 行及格池是在 0.5 尺下进池的，从未按 0.70+精确 DSR 尺复考**。
4. **0.70 硬线依据考证**：出处在仓（SIM-38"样本内外对比"，docs/03_modules/_domain_backtest/blueprint.md:690 与 docs/02_enterprise_architecture/02_domain_architecture_docs/35_d_backtest.md；常量单真源 `overfitting_detector.py:62`，并有 lint 禁他处重复字面量）。**属仓内工程约定，无外部学术出处登记**（0.70 保留率并非文献通用线）。0.5 存疑线出处=DDL 注释（strategy_screen_query.py:150），同为约定。
5. **拦截有效性**：E4 三线裁决把样例配方双重否决（ratio 0.4989<0.70 + 精确 DSR 否决带），DSR 注入失败也会 fail-closed（evaluate_dsr(None)→band=unavailable 判不通过；dsr_threshold 默认已显式开启）——**考尺的 fail-closed 语义经核实成立**（decision_gate.py:445 默认 DSR_SIGNIFICANCE_THRESHOLD）。

**对及格池可信度影响：中**（对 E4 考尺本身：低——它拦住了；对池内 160 行存量：高——它们大多没过过这把尺）。
**补救建议**：及格池 160 行全量过一遍 E4 尺（现成考尺，批处理即可）；统一 decay/retention 阈值分层（0.5=观察线，0.70=放行线）并注册到 alert_threshold_registry；0.70 线补一条外部出处或显式标注"工程约定"，进 capability card。

---

## 结论速览

| 自欺面 | 判定 | 一句话 |
|---|---|---|
| (a) 窗口重叠 | 部分成立 | 折切分机械无泄露，但 E4 真 OOS 段与快考窗完全相同（二次消费）、39 个 sid 跨 OOS 批重复受试、同批同 sid 有结果翻转双行 |
| (b) 多次搜索只报最优 | 部分成立 | 双口径并报诚实（N_eff=9 vs N_raw=10,080），但池子资格系于随批波动（18→9→2）的 N_eff 估计器，且台账 4,491 与表内 4,482/4,487/4,497 计数漂移、两大批漏登 |
| (c) 参数过拟合 | 成立 | 362,880 网格 best-of-10,080 vs 仅 403 日 OOS，选择红利蒸发一半；池内 25% 衰减越存疑线；0.70 线系仓内约定；幸亏 E4 考尺 fail-closed 真拦 |

**总评**：E4 考尺本身没有自欺（fail-closed 双重否决成立）；自欺风险集中在**及格池的进场尺（0.5 衰减线、无精确 DSR、OOS 可重复消费）远松于出场尺（0.70+精确 DSR）**——"及格池"当前语义是"被 OOS 测过"，不是"可信赖"。决策引用该池时勿按后者理解。

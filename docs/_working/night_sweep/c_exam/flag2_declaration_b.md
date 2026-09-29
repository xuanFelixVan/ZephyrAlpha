---
ttl: task_bound
completes_when: "⚑-2② B案判据经声明通道落册：机读键已追加 exam_scale_cost_gate.yaml breakeven_cost_gate v2 块 + 裁定登记；旧冻结键零改值"
session: st-nightsweep2-nc-20260930
created: '2026-09-30'
restore_note: '本件首登后遭队列落盘崩溃回滚波及一次（2026-09-30 07:4x 窗），本版为同内容重建重投'
---

# ⚑-2② B 案判据声明（声明通道落册件 · 考试链前置 C3）

> **性质**：本件是声明通道产物——冻结预注册件 `config/exam_scale_cost_gate.yaml` 的**判据变更声明**，
> 按 AGENTS.md 铁律"预注册冻结判据禁改，调整只走声明通道"执行。**旧键一字未动**（逐键 diff 见 §5），
> 变更以**追加版本块**（`breakeven_cost_gate:` v2.0.0）落地，新旧判据并存可回溯。

## 0. 授权链（谁批的）

1. **Owner 批复原文**（93_owner_menu.md L105 最短回法②，2026-09-30）：
   > "② 选 B（判据对象改盈亏平衡成本 c\* 的分布，五道门、不抽样；可并 C=DSR≥0.95+PBO）；40bp 锚与"Sharpe≥0"语义都不动；2 格先补同窗对拍再定稿"
2. **夜总攻总筹授权**（第二夜 C 组任务书，st-nightsweep-chief-20260929 → st-nightsweep2-nc-20260930）：
   Owner 2026-09-30 裁定"C组看前置条件完成了没有；没完成的如果是你能施工的，你负责打通前置条件，然后完成他们"——
   本声明即该授权下的前置打通施工（93_owner_menu.md ②首版"先不批定稿"建议已被 Owner 2026-09-30 更新批复覆盖，
   定稿追认另见裁定条目与 `leaf_books/f06/w61_t1_scorecard.md`）。
3. **登记载体**：裁定#435（本声明与机读键追加同 commit 原子，RULE-RULING）。

## 1. 为何换尺≠降标（三条独立理由，全部指向旧尺"量不了"而非新尺"放水"）

| # | 旧尺缺陷 | 证据（案卷 `docs/_working/total_command_closeout/review_ext_data_and_backtest.md`） |
|---|---|---|
| 1 | **恒假没被修掉**：字面判据"抽 50 格全部 Sharpe≥0"的通过概率=(1−p)^50 | §4-E(A)：p=0.33 时通过概率 2.01e-09；要 95% 通过率需真实负比例 p′≤0.1%，无任何实测支撑 |
| 2 | **量不准没被修掉**：n=50 的 95% CI 半宽 ±0.13–0.14 | §4-E(B)：两班实测 33% 与 56% 的区间大幅重叠，统计上不可分辨 |
| 3 | **方向反了**：正统校正是把选择过程装进判据（White 2000 Reality Check；HLZ 2016 t 门槛 2.0→3.0；Bailey–López de Prado 2014 DSR），"从幸存者里抽"是把选择过程从判据里摘出去 | 案卷 §三引 DOI 10.1111/1468-0262.00152 / 10.1093/rfs/hhv059 / 10.3905/jpm.2014.40.5.094 |

**不降标的证明（语义锚零移动）**：40bp 锚一字不动；"Sharpe≥0"语义一字不动（仅从"单档抽查"改为"逐格解到零点"）；
判据对象从"抽样统计量"换成"每格全量可算的确定量 c\*"（二分解），**样本从 50 格扩到全体幸存者=信息只增不减**；
新增 C 并联门（DSR≥0.95 + PBO）把 N=3700 的多重检验成本**计入**判据（N=3700、跨格 sd=0.5 时 DSR≥0.95 等价于年化 Sharpe≥1.81，
远严于字面 0）——**换尺后每一道门都等于或严于旧尺的可满足核**，删掉的只有数学上恒假的那半句。

## 2. 功效计算引用（n≈82 从哪来、为什么本声明不采用它定样本量）

- 案卷 §4-E(D) 实算（scipy 复算，NIST §7.2.4.2 口径 `n = z²·p(1−p)/e²`，95% CI 半宽 ≤10pp）：
  保守 p=0.50 → **n=97**；p≈0.30–0.33 假设 → **n≈82–85**（93_owner_menu.md L31 的"n≈82"即同公式非保守 p 假设；
  案卷 L211-214 明示两者都对、差别只在假设的 p，须写明假设）。
- **本声明处置**：B 案判据对象=c\*（逐格确定量），**不抽样 ⇒ 样本量=全体幸存者格数，n≈82/97 的样本量问题整体消解**。
  n=97（CI 精度口径）/n=180–194（80% 功效分辨 10pp 口径，§4-E(E)）仅对"比例计数型"判据有效——
  B 案五道门中 P1/P2 作用在连续量分布上（中位数/分位数），P3 分层门沿用层内 n≥30 的 INSUFFICIENT-N fail-closed 惯例。
  此为"换尺不降标"的统计核心：**不是把 n 调大，而是让抽样误差不存在**。

## 3. 新旧判据对照

| 维度 | 旧判据（冻结 v1，未删除） | 新判据（B 案 v2 声明，Owner 2026-09-30 批） |
|---|---|---|
| 判据对象 | "抽 50 格、最深滑点档（40bp）Sharpe≥survival_floor(0)" | 盈亏平衡成本 c\*（使 Sharpe(c)=0 的单边成本，逐格二分解+单调性校验；非单调格=NaN 单列，疑引擎缺陷） |
| 抽样 | 50 格抽查（seed=20260925） | **不抽样**，全体幸存者全量；分层降级为报告维度 |
| 门 1 | 40bp 档 sharpe≥0 | P1 中位数门：median{c\*} ≥ 40.0bp（**40bp 锚一字不动**） |
| 门 2 | —（无尾部门） | P2 尾部门：P10{c\*} ≥ 0bp |
| 门 3 | —（抽样框分层） | P3 分层门：（换手三分位×策略族×市场状态）层内 c\* 中位数≥40bp 的层占比≥80%；层内 n<30 判 INSUFFICIENT-N 不算绿 |
| 门 4 | — | P4 规模门：1×/5×/10× 目标仓位下 c\* 相对变化 ≤20% |
| 门 5 | —（隐式） | P5 数据版本门：成绩单必含 {复权口径, 快照日期, 快照 sha256, n_trials}，缺一即尺红 |
| 多重检验 | DSR 浮动门槛（17 号文 §一，裁定#306 口径）保留 | C 并联（可并）：P6 每拟转正格 DSR≥0.95（N=n_trials=3700，禁填 50）；P7 PBO≤0.20 且与 prob_oos_loss 合看；P8 MinTRL；P9 CSCV 前置 Ljung-Box 校验 |
| Sharpe 口径 | 年化基准 244 交易日（turnover_gate.days_basis） | A 股四条强制：①禁 ×√252，Ljung-Box(q=252) 显著则 Lo(2002) 修正因子；②ddof=0（与 PSR/DSR 同口径）；③停牌日分子分母同剔（禁填 0）、复牌首日跳空计入；④涨跌停 unfillable_at_limit 显式计数、>0 格单列池 |
| 三态输出 | pass/fail 二值 | PASS / INDETERM（任一层 n<30 或非单调格占比>5% → 必须补数据/补跑，禁默认降级 PASS）/ FAIL |
| 报告面 | verdict 机读 measured/threshold/pass | 同左 + c\* P10/P25/median/P75/P90 + 幸存者数 K 与全体候选数 N（K/N=初筛通过率必披）+ 非单调格清单 + unfillable 池清单 |

## 4. 机读键（真源追加块）

`config/exam_scale_cost_gate.yaml` 追加顶层键 `breakeven_cost_gate:`（version: 2.0.0）——
数值键=本声明 §3 的冻结快照，改动仍走裁定通道；消费面（T2 判定书/成绩单生成器）按波次接线，
接线前 T2 发车判据仍由哨兵 `scripts/backtest/t1_t2_handover.py` 按冻结 v1 键执行（survival_floor 零改动，
C1 未批降标=禁改）。schema_version 不翻（旧消费方兼容性由"只增键"保证）。

## 5. 旧键零改值核对清单（本通道自证）

旧顶层键：`schema_version/doc_type/title/created/session/cost_gate.{tiers_bp,survival_floor,monotonic_tol,min_days}/
scale_gate.{participation_ref,exponent,multiplier_cap}/turnover_gate.{cap_annual_x,days_basis}/
search_objective.{primary,observed,note}` —— 全部保持原值原注释；本次仅文件尾追加 `breakeven_cost_gate:` 块（§4）。

## 6. 2 格同窗对拍（Owner 批复的定稿前置，已完成）

对拍证据=`docs/_working/night_sweep/sw4_t1_repair_pairing_report.md`（2026-09-29）：
2 阴格（d6759a48a594/4bdf3555a27d）经 A/B 双跑+直调引擎三证，净值序列哈希一致（342432347427），
死因=配方内生阴性（kelly_050 sizing 全期零仓位→零方差），manifest 已修 3700 守恒。**"与引擎无关"从转述升为实证**。

## 7. 关联

- 裁定：#435（本声明）；#446（T1 定稿追认，原登#436撞号改号）；#431（总批复）；#306（DSR 浮动门槛前置口径）
- 前置消费：C4 T2 发车哨兵（本夜）、T2 判定书 B 案接线（另波）
- 案卷真源：review_ext_data_and_backtest.md §3.2（B 案公式/伪代码/P1–P5）、§3.3（C 案 DSR/PBO）、§4-E（功效实算）

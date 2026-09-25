---
ttl: task_bound
title: 分册04 切换摩擦治理——滞回带/置信不够不移交/最短任职期/换仓成本预算
topic: switch_friction_governance
created: "2026-09-24"
owner: ZephyrAlpha-Owner
---

# 分册04：切换摩擦治理

> **大白话开场**：策略换仓（谁在岗、谁下岗）本身是要花钱的——平旧仓建新仓的成本、换错方向的损耗、还有"来回横跳"的摩擦。**切换的判据如果贴着噪声走，账户就成了给券商打工**。治理三件套：滞回带（不轻易换）、最短任职期（换了不马上再换）、成本预算（换之前先算这笔账）。

## 1. 滞回带（Hysteresis Band）——置信度不够不移交

**一句话**：进场判据和出场判据**故意不对称**——上行穿过高门槛才上任，下行穿过低门槛才下岗，两门槛之间的"带"里**保持现状**。带的存在让状态切换需要"实质改善"而非"噪声抖动"。

本仓已存在的同构零件（证据）：
1. **过渡带折减**：`src/zephyr/strategy_pipeline/daily_decision_orchestrator.py` TRANSITION_THRESHOLD=0.60、TRANSITION_FACTOR=0.5——状态隶属度 <60% 时按 0.5 折减（"0.5-0.7 带内取保守下缘"，裁定#305 第 3 点草案）。语义=**置信不够就打折，不给满仓**，即"置信度不够不移交"的现行实现。
2. **六段预算带插值**：同文件 BUDGET_BANDS（capitulation 0-10% … distribution 0%）——预算带是连续区间不是开关跳变，天然抑制"全有全无"式切换。
3. **mSPRT 序贯晋升**（统计版滞回）：`src/zephyr/pf_core/core/msprt_champion_challenger.py`（MOD-PF-008）+ 晋升编排 `msprt_promotion_channel.py`（ARCH-298 载体重裁定=因子生命周期状态机 MOD-L02-013）。mSPRT（混合序贯似然比检验）**要求证据持续累积到阈值才允许切换**——单日好运翻不了盘，这就是"置信不够不移交"的统计学表达。
4. **退役侧滞回**：退役判据是"评审触发器非自动关停"（滚动 20 日跑输>5% / 滚动 60 日 Sharpe<0 / 回撤漂移 1.5x，`src/zephyr/governance/lifecycle_governance/strategy_retirement_evaluator.py`；裁定逻辑留痕 memo55 §3.5）——触发后先出评估报告再裁定，不是判据一碰就撤。

**立法建议（新立提案，net-zero：全部复用上述零件参数位，零新 gate）**：
- 上任门槛：挑战者 DSR 校正后 Sharpe + mSPRT 达显著（现行晋升通道）——已立法，照用。
- 下岗门槛：低于上任门槛即可，但须连任 N 日确认（见 §2）。
- 滞回带宽 ≥2×切换成本的期望损耗折算（见 §3 预算），带宽值随各策略成本档预注册。

## 2. 最短任职期（Minimum Tenure）【新立提案】

- **问题**：换仓判据即使有滞回，仍可能碰上" regime 抖动期"造成连环换（本月 A 上岗下月 B 上岗），每次换都付全套摩擦。
- **机构做法**：策略/经理轮换普遍设考核最短观察期与冷却期（行业惯例层面，见 memo55 §3.5 转引 LuxAlgo 2026-08 *Edge Decay: Reoptimize or Throw Out Strategy* [luxalgo.com](https://www.luxalgo.com/blog/edge-decay-reoptimize-or-throw-out-strategy/)、ArrowAlgo 2026-05 [arrowalgo.com](https://arrowalgo.com/when-to-stop-a-trading-algorithm/)、DeepTradeX 2026-07——三处一致主张"触发器+评审"而非抖动式轮换）。
- **提案**：上任后最短任职 ≥20 交易日（约一个月，覆盖一个完整月度复盘周期，对齐 memo55 月复盘编排）；任职期内判据触发只记档**不执行**，期满后统一评审。同策略下岗后冷却 ≥60 天（对齐 refit 间隔 ≥60 天防连续适应过拟合的现行值，`docs/_archive/62_business_registry_construction.md` 第 825 行；及 exam min_days=60）方可重新参选。
- **net-zero 对价**：无新机制——任职期=月度复盘编排（memo55 §3.6 MonthlyRiskGovernance）加一条评审输入；冷却期=复用 refit 间隔常数。**未经裁定不施工**。

## 3. 换仓成本预算（Switch Cost Budget）

- **算术**：一次策略切换的真实成本 = 旧仓平仓成本 + 新仓建仓成本 + 两次滑点 + 短暂空仓/重叠的市场敞口损耗。粗算口径：**换仓的期望收益增益必须 > 换仓摩擦 × 安全系数**，否则不换。
- **本仓锚点**：
  1. 成本档体系：五档 [0,5,10,20,40]bp（exam_scale_cost_gate）——换仓审查沿用最高档 40bp 做压力问："换完之后，新配置在 40bp 档还活着吗？"（survival_floor=0.0 现行判据）。
  2. 换手上限：8x/年（turnover_gate.cap_annual_x；推导：8x→成本拖累 ≈1.7pct/年）——**换仓次数本身是换手的一部分**，切换编排须把"切换产生的换手"计入 8x 预算，不得超发。
  3. 阈值翻转的教训（方法论反面教材）：`FINAL_REPORT_t0_matrix_reexam.md` §五-6 实测——宏观门"趋势支"真源实为波动率四档，卡面语义与数据源不符（误把低波当趋势）。**判据真源错了，切换越勤快错得越快**——所以本册把"判据真源有守卫"作为切换治理的前置条件（关联附录C 六段真源链修复清单）。
- **立法口径**：切换提案必须附三行账——①本次切换预估摩擦（bp，按最高成本档）；②新配置五档存活证明；③切换换手计入年度 8x 预算后的余量。缺任一行=评审不受理。

## 4. 一段话版

**上岗要过统计门（mSPRT+DSR），在岗有最短任期（20 日+月度评审），下岗要走评审不走扳机；两门槛之间的带里保持现状；每次切换先报三行成本账（摩擦/五档存活/8x 余量），判据真源必须挂守卫（无守卫的映射不得驱动切换）。**

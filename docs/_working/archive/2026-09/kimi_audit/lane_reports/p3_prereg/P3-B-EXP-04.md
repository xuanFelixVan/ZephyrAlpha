---
ttl: task_bound
rule_form: data
verifiability: manual
title: P3 预注册卡 P3-B-EXP-04（FCT-EXP-004 异常覆盖 点火考试，frozen）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-17
status: frozen（考试启动前写死；启动后任何字段不得改动，改动即作废重开）
lane: P3
family_id: P3-B-FIRST6
n_eff: 6
parent_context: p3_prereg/P3-B-NARROWING.md（窄化裁定） + factor_registry.yaml FCT-EXP-004 + expectation_consumption_design_policy.md §8/§9
---

# P3-B-EXP-04：FCT-EXP-004 异常覆盖 的毛边际/DSR/经济解释三关点火考试

## 1. 假设（H1，唯一）

**按 `resid：n_reports/n_orgs ~ 1 + log(amt20) + mom20 + to20（逐日截面 OLS，值大→多）` 构造的日频因子，月末 Top50 等权多头口径下有正且过成本线的毛边际，
且统计上非运气（DSR>0.5，N_eff=6）。**

零假设 H0：OOS 段日均毛超额 ≤ 2.7bp/日，或 DSR ≤ 0.5。

- 机制一句话（关③自述）：剔除规模/动量/换手后的异常覆盖度=信息扩散不足，未来收益偏高（Lee-So 2017；华泰 RankIC 2.34%）。
- 注册表原式与实现注意：n_orgs≥1 才入截面；log 市值缺表→log(20 日均成交额) 代理规模腿（披露）；window_days=90（表内统一值实测）。
- 数据源：c3_fundamental.consensus_daily（评级/计数列真实，§9.2 在案）。
- 考窗：IS 2020-01-01..2023-12-31 / OOS 2024-01-01..2026-09-14。OOS=2024-01 起真 OOS（T≈640 交易日）。

## 2. 考试口径（全族冻结，禁挪）

- **组合构造**（对齐 §8.1 ⑥ 冻结窄测口径）：月末截面因子值降序 **Top50 等权**多头，持有至下一月末；
  T 日出信号 → T+1 收盘成交（`_c4_engine` w.shift(1)）；成本=冻结土规（佣金 2.5bp 双边+印花 10bp 卖+滑点 5bp）。
- **毛边际定义**：组合日均毛超额 = 组合毛日收益 − 当日可考宇宙等权日收益（去 beta），bp/日；另记绝对口径。
- **PIT**：因子只用 trade_date≤T 行（表内聚合口径 publish_date≤trade_date，registry pit_policy 在案）。
- **DSR**：精确 DSR（MOD-SIM-024 官方件 fail-closed）作用于 OOS 段净日收益，**N_eff=6**（首批封闭族）。

## 3. 及格/判红判据（冻结，主会话 S2/S6 三关）

| 关 | 判据 | 门槛 |
|---|---|---|
| ① 毛边际 | OOS 段日均毛超额 | **> 2.7bp/日** |
| ② DSR | OOS 段净日收益 | **> 0.5，N_eff=6** |
| ③ 经济解释 | 一句话机制自述 | 见 §1 |

**判红（任一即红）**：毛超额 ≤ 2.7bp/日；或 DSR ≤ 0.5；或 DSR 引擎报错（fail-closed=红）；
或 OOS 段有效交易日 < 60（矩估计退化不可判=红）。
三关全绿 = 点火成功，建议进 §8 正式轨（仍受 EXP 族 §8 冻结门槛与前向积累裁定约束，本卡不替代）。

## 4. 产物锚

- 考试脚本：`.runtime/tmp/exp/p3/p3_expvol_exam.py`；结果 `.runtime/tmp/exp/p3/exp_exam/P3-B-EXP-0N.json`；
  哨兵 `.runtime/tmp/exp/p3/p3_expvol_exam.done`

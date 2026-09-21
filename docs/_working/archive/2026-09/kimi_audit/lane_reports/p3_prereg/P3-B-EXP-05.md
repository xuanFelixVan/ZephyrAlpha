---
ttl: task_bound
rule_form: data
verifiability: manual
title: P3 预注册卡 P3-B-EXP-05（FCT-EXP-005 分歧度 点火考试，frozen）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-17
status: frozen（考试启动前写死；启动后任何字段不得改动，改动即作废重开）
lane: P3
family_id: P3-B-FIRST6
n_eff: 6
parent_context: p3_prereg/P3-B-NARROWING.md（窄化裁定） + factor_registry.yaml FCT-EXP-005 + expectation_consumption_design_policy.md §8/§9
---

# P3-B-EXP-05：FCT-EXP-005 分歧度 的毛边际/DSR/经济解释三关点火考试

## 1. 假设（H1，唯一）

**按 `−eps_std/|eps_consensus|（值大=低分歧→多）` 构造的日频因子，月末 Top50 等权多头口径下有正且过成本线的毛边际，
且统计上非运气（DSR>0.5，N_eff=6）。**

零假设 H0：OOS 段日均毛超额 ≤ 2.7bp/日，或 DSR ≤ 0.5。

- 机制一句话（关③自述）：高分歧=不确定性溢价反向，低分歧股未来收益偏高（Diether-Malloy-Scherbina 2002）。
- 注册表原式与实现注意：fy1 同上；dispersion clip [0,1e3]；方向取负（低分歧多头），与 EXP-002 分母同源不同向（披露：族内相关）。
- 数据源：c3_fundamental.consensus_daily_repaired（build_batch=c4-repair-20260916，pdf_forecast_extracted 净段）。
- 考窗：IS 2017-07-03..2020-12-31 / OOS 2021-01-01..2021-12-31。OOS=2021 全年（净段内切分）；2022 后无数据=无真 OOS 外延，结论=净段证据档。

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

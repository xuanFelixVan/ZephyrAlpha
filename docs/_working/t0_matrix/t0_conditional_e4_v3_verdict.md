---
ttl: task_bound
title: 条件化做T E4 双门考试 V3 · verdict 留档（机械生成自 result.yaml）
sid: st-t0-matrix-20260924
created: "2026-09-24"
card: docs/_working/t0_matrix/t0_conditional_v3_prereg_card.md (frozen)
status: final
evidence_grade: A（判据 import 复用+frozen 卡先行+变异探针红证，见 REDEVID_mutation_probe_matrix.md）
---

# verdict：`STATE_GATE_NEVER_TRIGGERED`

> 本文件由 `docs/_working/t0_matrix/t0_conditional_e4_v3_result.yaml` 机械生成，禁手抄数字。
> 复算：`python scripts/audit/t0_conditional_e4_v3_exam.py --artifacts-dir D:/ZephyrAlpha/data/backtest_artifacts`
> 生成时刻（本次留档）：2026-09-23T18:38:15+00:00

## 1. 一句话结论

**宏观门在材料窗零命中（门规则与窗不相容），如实披露**——但字面文案沿用 v1 单门语境，**真因见 §3 诊断**：
不是宏观门没触发，而是**两道门在考窗内系统性互斥**。

## 2. 四数表（同口径，三集并列；卡 §5 土规：n≥30 才许出方向性结论）

| 集 | n_pairs | 净正 | ≥30bp | 毛均bp | 净均bp | 前置命中率 |
|---|---|---|---|---|---|---|
| 主考（双门均允许） | 0 | 0 | 0 | None | None | None |
| 副考（情绪不可评日·单宏观门） | 0 | 0 | 0 | None | None | None |
| 对照（禁做侧） | 26 | 6 | 6 | -5.06 | -36.26 | 0.2308 |
| **全材料无条件**（任务③口径） | 26 | 6 | 6 | -5.06 | -36.26 | 0.2308 |

判档表述遵裁定#325：**禁"全绿"**。n=26 < 30 ⇒ 任何 PASS/FAIL 方向性结论**不予出具**。

## 3. 主集为零的机制归因（机算，非叙述）

- 宏观门放行 **20** 对（共 26 对）
- 其中情绪门判**禁做** **20** 对 ⇒ 占宏观放行的 20/20
- 其中情绪门不可评 **0** 对
- 宏观放行日的六段分布：{'capitulation': 18, 'distribution': 2}
- 反向：情绪放行的 6 对全部落在 `vol_pct≈0.48–0.51` 且 dominant=r2 ⇒ 宏观门不放行
- 考窗配对日（15 个）：2026-06-05, 2026-06-12, 2026-06-18, 2026-06-26, 2026-07-03, 2026-07-10 …2026-08-31, 2026-09-01
- 材料窗内 T-1 dominant 取值域：['r1', 'r2', 'r4']（**无 r3、无 r12**）

⇒ 结论不是"这门没开"，而是"这两门在可得材料上几乎不会同时开"。
全史闭卷窗双门同放行 200/1,566 日（12.8%，见 GPU 包 `dual_gate_anatomy`），
说明门规则本身自洽；考窗只有 15 个交易日是零交集的直接原因。

## 4. 结构性发现（对周五 GPU 矩阵有直接后果）

state_domain_of_macro_source:
- r1
- r2
- r3
- r4
r12_branch_reachable: false
macro_branch_disjointness:
  days_vol_gt_h: 768
  days_dominant_in_trend_set: 659
  days_both_branches: 0
emotion_gate_allow_among_macro_allow_pairs: 0
note: 以上计数全部机算自本次取数的两份真源（regime_state_anchored 与六段物化件），禁把手写散文数字当结论；结构性解读见交付报告与 GPU
  包 meta.caveats.dual_gate_anatomy

另两条已实测事实（同记于 GPU 包 meta.caveats）：
`regime_state_anchored.dominant` 取值域仅 {r1,r2,r3,r4} ⇒ 卡 §2.1 的 **r12 分支永不可达**；
`dominant='r3' AND vol_pct>0.700` 实测 **0 行** ⇒ 宏观门两支互斥，联合条件维有效自由度≈1 而非 2。

## 5. 材料资格审计（卡 §4 M-1…M-4 的落点计数）

keep_files:
- bt-1bd66583.json
- bt-2e42a507.json
- bt-2e78adc5.json
- bt-790d8a95.json
- bt-8607ffc2.json
files_total: 60
fills_total: 107218
fills_excluded_m1_daily_bar: 103332
files_empty_log: 4
fills_in_sample: 2591
files_deduped_away: 25
fills_deduped_away: 23780
fills_excluded_m1_pre_exam_window: 1295

配对侧：{'runs_with_pairs': 2, 'pairs_gross': 26, 'pairs_entering_gates': 26}
（M-4 剔除 0 对 ⇒ within-run 材料全部落在涨跌停可行域内；
反向印证 V2 口径下 +5,271bp 那种"毛价差"纯系跨组合污染的产物。）

## 6. 五态判定与不放行声明

verdict=`STATE_GATE_NEVER_TRIGGERED`。本 verdict 属成本经济学考试族，
**不构成任何实盘放行**（实盘准入门=B-007 pilot 档 Owner 门位）；
不动 #331/#386 任何旧裁；不重建 S-OWNER-001 参数。零状态变更。

## 7. 欠账（如实，不粉饰）

1. **样本供给**：真实日内往返仅 26 对（差 30 土规 4 对）。本班按卡 §8.3 自禁线**未造料凑数**。
   材料线另卡要点（分钟驱动日内往返语料，成交模型与窗规则须先写死）已写入终报。
2. **`regime_snapshot_history` 品类未注册**（auto_mount.py:107 自记）⇒ 六段物化件宏观腿表名硬编码。
3. **`C2_promotion` 恒 1.0** 伪值仍在温度计成分里（emoreplay 报告 §5 D-1），本包 ok_n 列如实带出未代修。
4. **v1 件 `[TESTS]` 注释"净 −45.0"与自身产物 −40.40 不符**=文档漂移，登记未改（改判据件须作废重开）。
5. **bt-2e78adc5 时区混用**（RULE-SCHEMA-TZ）登记移交，未代修他人材料件。

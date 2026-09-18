---
ttl: task_bound
completes_when: 总包对本文件四项申请逐条出裁定号（车道不自取号）
---

# 裁定申请书 · req_rbstats_01（红队车道 st-ff-rb-stats-20260918）

> 按 COORDINATION_LEDGER §4：车道不自行取裁定号。以下四项本车道**判不动或需门位**，
> 已按"能做的先做完、不停等"处理，四项均附实测证据与复现命令。

## A1 · regime 断供时 R-K9 的**数值侧**落地形态（本车道只做到"可检出"）

- **背景**：R-K9 明文"断供时降级 fail-closed 不允许交易，禁 fail-open 默认继续"。
  实测危机信号已触发时断掉 RiskSignal 一条腿 → r10 危机概率被门清零、dominant 翻成
  r1、Shrinkage 从 0.255 松到 0.800（**放量 3.14 倍**）。详见
  `lanes/rbstats_prescriptions.md` P-2 的五行实测表。
- **本车道已做**：`missing_risk_legs()` + `ShrinkageResult.degraded_legs` + WARNING
  （纯观测位、零数值改动、历史 C1/B 口径零漂移），把"能机械判定断供"这个前提补上。
  `tests/regime/test_rb_stats_regime_failopen.py` 22 件钉住。
- **判不动的点**：要不要让检测器在缺数时**主动收紧**（如主腿缺数即 RiskSignal=0.30 档）。
  这会改动已验证的历史数字，属"生产流转"（宪法 §5 high 域）。
- **选项**：甲=检测器侧缺数即收紧（一处改，但动历史口径）；
  乙=消费侧（`crisis_gate`/分配链）把 `degraded_legs` 非空当独立失效腿拒放量
  （**本车道建议**，与 R-K9 的"不允许交易"字面一致，且不动任何研究数字）；
  丙=只出声不改判。
- **参照正例**：`allocation_inputs.py:426-455 resolve_risk_signal` 已是乙案思路的
  正确形态（无教材→risk=1.0 **且**概率平坦→conf 最低档→总节流 0.30，带 `risk_signal_source` 溯源）。
  检测器应向它对齐，而不是各自发明降级语义。

## A2 · 过拟合检测器"未评估维默认稳定"是否改成本体 fail-closed

- **背景**：`overfitting_detector.py:367` docstring 明文"未提供的维度视为未检测
  （默认稳定, 不触发否决）"。实测同一批入参，补上维度2/3 → `is_overfitting=True`；
  省掉 → `False`（`tests/backtest/test_rb_stats_validator_teeth.py::TestOverfittingDetectorFailOpenPinned`）。
- **本车道已做**：不改本体，改**考试侧**——E4 若过拟合三维未评满 或 DSR 分母未对账，
  禁判"通过"（最多"存疑"）。理由：改 `detect()` 默认值会一次性波及全部 394 台/所有
  既有 caller 的判定，红队车道无授权做这个半径的改动。
- **判不动的点**：本体是否加 `require_all_dimensions=True`；若加，存量 caller 由谁改。

## A3 · E4（唯一 built 的考试咽喉）是否强制补维度2/3

- **背景**：`config/strategy_production_map.yaml` 16 节点实测 built=4 / partial=11 / pending=1，
  FAC-E4「考试咽喉」= built。其判定链 `module_ref: MOD-BT-039` 的落地件
  `scripts/backtest/f06_e4_wfa_exam.py` 只评估过拟合 1/3 维。
- **代价**：维度2（参数 ±10% 扰动，实测需 6 次额外全窗回测）+ 维度3（跨时段，5 次）
  ⇒ 单配方 E4 成本从 1 次全窗涨到 ~12 次。
- **申请**：请总包定"是否要一个**满三维**的 E4"，以及若不要，是否把"部分覆盖"写进
  FAC-E4 节点的 build_status 判据（现在是 built，但覆盖面 1/3——**建议降 partial**，
  这属注册表语义改动，需总包执笔）。

## A4 · `evaluate_dsr` 的显式逃生门是否在生产路径禁用

- **背景**：`decision_gate.py:98` `threshold` 为**调用方可覆盖**的关键字参数；
  `DecisionGateConfig.dsr_threshold: float | None = DSR_SIGNIFICANCE_THRESHOLD`（`:445`），
  传 `None` ⇒ `check_oos_stage` 里 `dsr_passed` 保持初值 `True` 且 **不往 `reasons` 追加任何一行**
  （`decision_gate.py:806-813`，`dsr_passed` 初值 True，`reasons` 只在 if 内追加），即"DSR 根本没参与判定"这件事**在档案里不可见**。
  实测：`src/**` 与 `scripts/**` 现有代码中**无**生产调用方传 `None`（只有
  `tests/backtest/test_decision_gate.py:292` 与 `test_strategy_validation_pipeline.py` 用），
  故当前**无实害**，但这是一扇文档化的、不留痕的门。
- **附带一条文档债（本车道已就地修）**：`decision_gate.py` 有**两处**注释写
  "DSR可选判定器(默认关闭)"（原 `:752` 与 `:796`），而 `:445` 的真实默认是
  **0.95=开启**，同文件 `:8` 的 INVARIANTS 也写"默认开启"——同一文件对"刹车接没接"
  给出两种相反陈述。本轮已把两处注释更正为与代码一致（纯注释，零行为改动）。
- **申请**：甲=生产路径禁 `dsr_threshold=None`（加机械校验，测试路径经显式旗标豁免）；
  乙=保留但强制往 `reasons` 追加"DSR 未参与判定"留痕（**本车道建议乙**，成本最低且把
  不可见变可见）；丙=仅修注释。

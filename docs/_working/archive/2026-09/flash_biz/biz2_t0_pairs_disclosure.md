---
ttl: task_bound
rule_form: data
verifiability: manual
title: Flash 包2——P-P2-01/P-P2-03 做T配对存疑件披露报告（Flash F02）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-18
session: st-flashbiz-20260918
---

# 包2 · 做T配对存疑件披露（土规 insufficient_samples，不强判）

判据真源：Flash F02 交接包（样本闸门 symbol×day 双边配对 ≥30；不足 → pending/insufficient_samples 不强判）。
裁定背景：做T现形态已被裁定#304 砍（Owner 快签总表行 01/24：T 窄考试 RED 实锤），**本报告只做事实披露，不构成任何放行/复活动作**。

## 1. 重跑实锤（2026-09-18 02:0x，原样重跑 cost_trio_exam.py）

| 机读判据值 | 实测 | 出结论条件 | 状态 |
|---|---|---|---|
| n_symbol_day_pairs | **24** | ≥30 | **不足 → insufficient_samples，维持存疑** |
| net_positive（净价差>0 配对数） | 0/24 | （样本够才判） | 观察披露 |
| edge_ge_30bp（毛价差≥30bp 开仓前置命中） | 0/24 | （样本够才判） | 观察披露 |
| 毛价差 mean / p50 | **−9.2bp / −5.13bp** | — | 观察 |
| 净价差 mean / p50 | **−45.0bp / −41.5bp** | — | 观察（毛价差 − 硬成本 ≈ −36bp 差值全在成本） |
| 硬成本口径 | CST-T0-001：佣金双边 6bp+印花 5bp+过户 0.2bp+滑点 2×10bp+min5 抬升 | — | 与 P6 一致 |

P6 基线（2026-09-17 22:10 快照留档 `.runtime/tmp/exp/p6/cost_trio_result.p6snapshot.json`）与本班重跑逐值一致（24 对/0 净正/0≥30bp/−45.0bp）——D 后无新回测产物，样本零增长。

## 2. 必须随结论走的事实（按 F02 要求逐条披露）

1. **24 < 30 土规线 → insufficient_samples，不出通过/不通过方向性结论**（REG-VALM-001 轻量土规：触发<30 不下结论）。
2. 0/24 配对毛价差 ≥30bp（CST-T0-001 open_precondition.min_expected_edge_rate=0.003 开仓硬前置全不命中）。
3. 净价差 mean −45.0bp：毛 mean −9.2bp vs 硬成本 ~31-36bp/往返——**毛边际不存在叠加成本放大**，但样本 24 不构成"做T亏损"结论（P6 §4.5 原话有效）。
4. 口径限制：同 symbol×day 买卖配对=做T代理（无日内时序配对）；fill 混 11 个 walk-forward run；窗口仅 D 后 4 交易日（09-10~09-15）。

## 3. 与裁定#304 的关系

裁定#304（砍做T现形态）的实证基础是 T lane 窄考试（共振 +0.88bp vs 对照 +0.87bp 不可区分 p=0.4997，净 −7.5bp）。本件做T配对存疑是**独立第三视角**（真实成交流水成本侧）："毛边际 0/24 命中前置" 与 #304 "信号真但过不了成本线" 相互印证，无翻案证据。复活路径维持 #304 口径=换因子族+新单假设预注册卡，本件不变更任何状态。

## 4. 样本积累与重考

- 命令（样本积累后原样重跑）：`python .runtime/tmp/exp/p6/cost_trio_exam.py`；出结论条件=第一数 ≥30。
- 台账落库：本班未落 P-P2-01/03 行（可选并入 F01 写通道，留给 Owner 决定）。
- 回滚：纯只读分析，零写入零副作用。

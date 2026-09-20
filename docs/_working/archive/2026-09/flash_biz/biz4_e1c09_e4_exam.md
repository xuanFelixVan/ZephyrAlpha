---
ttl: task_bound
rule_form: data
verifiability: manual
title: Flash 包4——E1C-09 唯一 PASS 候选进 E4 完整考试出证（verdict=存疑）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-18
session: st-flashbiz-20260918
---

# 包4 · E1C-09 进 E4 完整三阶段正考（出证完成，verdict=存疑 fail-closed）

候选：P3-E1C-09（E1C 稳健池 #8，预注册卡 frozen：`docs/_working/kimi_audit/lane_reports/p3_prereg/P3-E1C-09.md`）
公式：`ts_corr_20(ts_delta_5(mul(-0.614, close_ma20)), min(close_ma20, sqrt(div(vol_20d, ret_20d))))`
P3 点火登记：strict_oos 毛超额 +6.822bp/日，DSR 0.7256（N_eff=13），三关全绿 → 本班进 E4 完整考试。

## 1. 考试口径（本班组装，判定零重写）

- 面板：`fetch_panel(universe_n=40, days=250)` 钉宇宙；双自检（canonical #2 式 incr IC=0.057686 vs 底档 0.0577 ✓；E1C-09 本卡 incr IC=0.043236 vs 底档 0.0432 ✓）——面板同一性证实。
- 窗口：预注册冻结窗 2024-06-18..2026-09-15（548td）；IS 类比段=mining_overlap（尾 250td，挖矿发生窗）；真 OOS=strict_oos（前 298td，矿工未见过）。**IS/OOS 角色与 F-06 幸存者相反**（挖矿窗在后），系候选出生方式决定，档案已披露。
- WFA：`build_folds(12m/6m/6m)` 因果折×3——30 个月窗装不下默认 24m 训练窗，降 12m 并披露；全链路截断面板因果求值。
- 判定：`run_strategy_validation`（DecisionGate 三阶段+OverfittingDetector，MOD-BT-211 同管线零重写）；DSR=MOD-SIM-024 精确口径 N_eff=13；成本=引擎冻结土规。

## 2. 结果（archive=data/backtest_artifacts/runs/E4-E1C09-P3-E1C-09/，verdict.md+summary.json）

| 阶段 | 实测 | 登记（P3） | 判定 |
|---|---|---|---|
| IS（mining 段 sharpe） | 1.469 | 1.511（容差 ±0.05 内 ✓） | passed |
| WFA | 折0(strict_oos) **3.310** / 折1(mining) **3.934** / 折2(mining) **−1.953** maxDD −40.4% | — | 2/3 折通过 |
| OOS（strict_oos sharpe） | 2.027 / 298td | 2.004（✓） | **未过**（DSR 落 review 带） |
| OOS/IS 比率 | 1.3797 | — | ≥0.70 线 ✓ |
| DSR（精确口径） | **0.732** | 0.7256（容差 ±0.02 内 ✓） | band=**review**（<significance 线） |
| 过拟合检测 | CV=1.83>1.50 + 灾难折 −1.95<−0.50 | — | **is_overfitting=True** |

**verdict=存疑（REVIEW）**：硬线大多过（WFA 多数折+比率线），但 DSR 中间带 + WFA 稳定性边际未达（60% 线）+ 过拟合检测否决→fail-closed 不放行；**can_deploy=false**。登记对照三值（oos sharpe/IS sharpe/DSR）全在容差内→考试有效非作废。

## 3. 判读（增量信息）

1. P3 三关窄考（只看 strict_oos 段）PASS 成立且复算精确复现——**候选在"矿工没见过的段"确实赚钱**。
2. E4 完整考新揭露：**mining_overlap 尾部折（2026-06..09）Sharpe −1.95/maxDD −40%**——近三月段剧烈劣化，全路径 maxDD −40.33% 本就潜伏在 P3 stats 里，窄考不拆段看不见。E4 对窄考的增量价值实证。
3. DSR 0.732 落 review 带（0.5 ≤ DSR < significance 线）：统计上"非运气"方向成立但不到显著线，需补样本或人工复核。
4. 本档案不构成放行；**放行权=Owner 门位**（指令：涉钱结论只出报告不改放行状态）。E2 幂等预审/E3 构造环未跑（预注册卡注明 E4 不替代）。

## 4. 工程与复现

- 驱动件：`.runtime/tmp/exp/flashbiz/biz4_e1c09_e4_exam.py`（日志/哨兵同目录，biz4_e1c09_e4_exam.done）；reaper 白名单已登记。
- 重跑：`python .runtime/tmp/exp/flashbiz/biz4_e1c09_e4_exam.py`（全量自检+门控 ~19s，不含面板拉取）。
- 引擎口径注记：本考在 E7 涨跌停闸开启后的引擎上跑（闸为本班包3 修复）；对照三值仍全过容差。
- 首轮发射两次作废：①自检误对（把 E1C-09 式对 canonical#2 底档 0.0577——实为 0.043236 恰=本卡底档 0.0432，修正为双自检）；②DataFrame.loc 索引展开把预热日期扩进权重窗（548 vs 599 布尔错位），改为全窗建权重后 loc 裁剪。两次失败均 fail-closed 正确拦截，无静默坏结果。

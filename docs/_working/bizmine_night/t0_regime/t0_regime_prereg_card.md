---
ttl: task_bound
rule_form: data
verifiability: manual
title: T0 预注册卡——510300 做T 行情条件化窄测（regime 条件振幅勘测，frozen）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-19
status: frozen（本卡于实验运行前写死；实验启动后任何字段不得改动，改动即作废重开）
lane: T
family_id: T0-REGIME
n_eff: 1
parent_context: bizmine_general_order.md §3-T3 + S2_做T_v2_战役裁定书.md §3（勘测方法论复刻）+ T.md（前役无条件基线 RED）+ src/zephyr/regime/core/anchored_state_machine.py（状态变量真源）
---

# T0 状态条件化窄测：510300 做T 可捕获振幅是否集中在高波动状态？

## 1. 假设（H1，唯一，写死）

**510300 做T 的可捕获振幅（15min bar 振幅的日中位数）集中在高波动行情状态；按大盘波动灰度条件化（仅高波动状态出手）后，所需捕获率脱离红区（≤50%），即条件化净边际具备过成本门槛的数学可行性。**

零假设 H0：可捕获振幅不随状态单调集中（高波桶中位振幅 < 1.5×全样本基线），或条件化后所需捕获率仍 >50%（Q5 口径）。

诚实条款：本卡是**勘测族**（振幅分布×状态桶分解，S2 方法论的条件化复刻），不是逐笔考试族；"翻案"结论只能是**数学可行性**级的（所需捕获率落入可行带），任何手法的真实净边际仍须 T0-PRERG-01 等逐笔卡出证。本卡结论直接服务于裁定 #304 的翻案/终结证据链。

## 2. 状态变量（二选一写死：选大盘灰度）

- **选定**：`c1_backtest.regime_state_anchored.vol_pct` = 000300 hv20（20 日对数收益 std×√252）在滚动 250 日内的分位 ∈[0,1]（连续灰度；生产方 `src/zephyr/regime/core/anchored_state_machine.py`，PIT 严格=rolling 分位只用 t 及以前）。
- 选型理由（记录）：任务令给出的候选"主力状态概率/confidence_signal"经 schema 实测**不在本表**（本表字段=trade_date/dominant/vol_pct/close/ma20/60/120；c1_market.alt_regime_signal 是 BDI/BTC/FNG 等另一信号族，非 HMM 置信度）；vol_pct 是本表唯一连续灰度且与"高波动状态"假设直接同构，故写死 vol_pct。
- **状态取 T-1 交易日**（PIT 双保险：hv20 本身回看，赋值再滞后一日，杜绝当日振幅泄漏进状态）。
- 次要镜头（同卡披露，不参与判定）：`dominant` 四档分解（代码口径 r3≤0.30<r2≤0.60<r1≤0.80<r4；表注释与代码不一致，以代码+实测锚定为准）。
- 去重：表内 4,469 行/2,235 唯一日（近端全重复），按 trade_date 取 ingest_ts 最新行（查询**不带 FINAL**，plain MergeTree）。

## 3. 分桶边界（只用 2026-06 以前数据定，禁用考试段）

- IS 期 = vol_pct 可用期内 trade_date ≤ 2026-05-31 的全部行（2017-07-11→2026-05-31）。
- 边界 = IS 期 vol_pct 的 33.33%/66.67% 分位，得三桶：**L（低波）** vol_pct≤q33；**M（中波）** q33<vol_pct≤q67；**H（高波）** vol_pct>q67。
- 边界数值由脚本在读取数据后、计算任何桶内统计前落盘到结果 JSON（frozen_edges 字段），并在结果报告中披露。
- 考试段 = 2026-06-01→2026-09-18（分段单独披露，不参与定界）。

## 4. 数据与振幅度量（冻结）

- 主粒度：`c1_market.kline_etf_15min` 510300（与 S2/T 前役直接可比）。时区归一化：toHour≤7 → +8h（T_preregister.md §4 在案规则）；(symbol, bar_time) 去重保留 ingest_ts 最新。
- 次粒度：`c1_market.kline_etf_1min` 510300（地形实测全北京墙钟 [9,15]，**不加时移**，仅去重）。
- 振幅：每根 bar `rng = (high − low)/prev_bar_close ×10⁴`（bp，prev_bar_close=时间序前一根 bar 收盘，跨日延续）；**日统计量 = 当日全部 bar rng 的中位数**（剔除 bar 数 <12 的残日，剔除数披露）。
- 样本窗：主窗 = [2019-01-02, 2026-09-18]（两粒度∩状态表满覆盖窗）；2017-07-11→2018-12 的 15min 数据做附录鲁棒段（仅 15min 粒度，披露用）。
- 日-状态对齐：交易日 D 的状态 = D 前最后一个有 vol_pct 的 trade_date 的值；7 个自然日内无值则弃日（计数披露）。

## 5. 成本口径（双口径并行，写明）

- **主判口径 Q5**：往返 8.4bp（100k：佣金 0.854×2+滑点 2.34×2+加成 1×2，ETF 免印花）→ 判据门槛 **12bp**（8.4+3.6 安全边际，承 S2/T 前役同尺）。
- **并行口径 Owner-001**：滑点 1.5bp 档 → 往返 6.708bp → 所需捕获率按 6.708bp 自算，全桶披露，不参与判定。
- 判红 grades（S2 裁定书 §3 rubric 承接，frozen）：required_capture = 门槛bp/桶内日中位振幅；RED >0.50；YELLOW (0.25,0.50]；GREEN ≤0.25。
- 可持续性诚实列：按 S2"系统性策略可持续捕获振幅 5-15% 已属优秀"，每桶附 expected_net@10% = 0.10×振幅 − 对应往返成本（两口径各一列），如实展示符号。

## 6. 判定门（frozen）

| 门 | 判据 |
|---|---|
| G1 集中性 | 主粒度 15min：p50(H) ≥ 1.5 × p50(全样本基线) **且** 三桶中位单调 L<M<H |
| G2 脱红 | 主判口径 Q5：required_capture_12bp(H 桶, h=1) ≤ 0.50 |
| G3 绿区（翻案强化） | required_capture_12bp(H 桶, h=1) ≤ 0.25 |
| G4 考试段方向一致 | 考试段（2026-06-01→09-18）内 G1 的单调方向与 G2 的 H 桶脱红均保持 |

**裁定映射（frozen）**：
- G1∧G2∧G3（含 G4 通过）= **翻案证据成立**：条件化后数学可行性具备，#304 建议重审（仍需逐笔卡过真实成本）。
- G1∧G2∧¬G3 = **部分翻案**：集中性存在且脱红，但所需捕获 25-50% 仍高于可持续带 5-15%，净边际期望大概率仍负。
- ¬G1 ∨ ¬G2 = **终结**：H1 证伪——振幅未集中于高波状态，或条件化后仍不可行；#304 关闭理由获得行情条件化维度的最终加固。
- h=4 镜像（振幅×2 口径，S2 同款）仅披露；1min 次粒度仅披露；dominant 四档分解仅披露。**任何披露镜头不改变判定**。

## 7. 执行与产物

- 脚本：`.runtime/tmp/bizmine/t0/t0_regime_exam.py`（启动前先落本卡）；结果 `.runtime/tmp/bizmine/t0/t0_regime_exam_result.json`（含 frozen_edges、逐桶统计、四门布尔、判定）；哨兵 `t0_regime_exam.done`。
- 只读查库（DatabaseService reader 角色，无 FINAL，无生产写）；不碰实盘/模拟盘/下单通道；不复活 BT-P2-056 全矩阵。
- 结果无论红绿原样写入 `t0_regime_narrow_test_results.md`。

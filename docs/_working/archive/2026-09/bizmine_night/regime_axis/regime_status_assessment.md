---
ttl: task_bound
---

# 灰度现状一页纸：大盘状态资产盘点与 PIT 口径（R 车道，2026-09-19）

> 会话 st-bizmine-r-20260919 · 数据实测自 ClickHouse（只读，DatabaseService）· 所有行数/区间为 2026-09-19 凌晨快照。
> 结论先行：**考试层条件化用 `c1_backtest.regime_state_anchored.vol_pct`（T-1）**；7 维概率与五态判定各有硬伤（见 §4）。

## 1. 资产清单（实测行数）

| 资产 | 载体 | 实测规模 | 覆盖 | 状态语义 |
|---|---|---|---|---|
| A. RegimeDetector（HMM 7 维灰度） | `src/zephyr/regime/core/regime_detector.py`（MOD-REGIME-001） | 代码 | — | GaussianHMM 4 态 + overlay 3 态（r10 CRISIS/r11 RECOVERY/r12 BREAKOUT）= 7 维概率 Σ=1；ConfidenceSignal=max(P) 4 档×稀有态折扣；RiskSignal=13 参数；Shrinkage=Conf×Risk |
| B. anchored 四档状态机 | `c1_backtest.regime_state_anchored`（plain MergeTree，禁 FINAL） | 4469 行 / **2235 个不同交易日**（全量重复插入一份，重复行值完全一致，DISTINCT 即去重） | 2017-07-11..2026-09-18 | **确定性**四档：r3 低风险(vol_pct≤0.30)/r2 中(0.30-0.60)/r1 中高(0.60-0.80)/r4 高(>0.80)；零拟合零重估（裁定 #229 v2 定稿） |
| C. HMM 快照回填 | `c1_backtest.regime_snapshot_history` | 3621 行 / 1812 日 × 2 个 run | 2019-04-01..2026-09-15 | 7 维概率 p_r1..p_r12 + dominant + confidence + confidence_signal + risk_signal + shrinkage + probs_json；run_id=VAL-P0-20260912/20260916（**VAL 验证回填，非逐日生产**） |
| D. 另类状态信号 | `c1_market.alt_regime_signal` | 20843 行（侦察报 10425， campaign 期间翻倍——F4 BDI 动量在持续补数） | F4: 1989-11..2026-09-18；其余各信号起点不一（F23 限涨情绪 2026-07-20 起） | 8 个 signal_id：F4 BDI 动量 Z20、F11 猪周期、F14 BTC 动量 30D、F7 台风事件、F23 涨停情绪、F12 生猪离散度、F8 高温事件、F15 FNG 指数——**另类数据轴**，非大盘主灰度 |
| E. 五态判定台账 | `c1_market.judgment_intraday_market_state` | **仅 4 行**，全部 2026-09-18（synthetic=0 真行） | 单日 | 五态 低迷/防御/震荡/进攻/亢奋 + state_probs 灰度分布（09-18「进攻」p=0.71..0.73）+ Brier 结算字段（realized_tail_return/state_realized/eval_score）；asof_ts + input_cutoff_ts 显式 PIT 契约 |

## 2. 灰度值是什么（三套口径的本质差异）

- **A（detector）**：概率意义上的灰度——7 维分布，但 2026-08-07 降态后 4 态 HMM 后验**过尖**（B1 实测 80-100% 桶预测 0.982 实际 0.523，模块 docstring 在案；实测 C 表样本 p_r1≈0.9999995），且裁定 #304 前态标签跨期漂移。temperature 缩放与正式校准器（IS 学习 T）在 13 号工程计划 §2.2，属在建。
- **B（anchored 表）**：特征意义上的灰度——`vol_pct` = hv20（20 日对数收益 std×√252）在**滚动 250 日内的分位 ∈[0,1]**，rolling 只用 t 及以前数据（模块 INVARIANTS：PIT 严格）；dominant 是 vol_pct 过固定阈值 0.30/0.60/0.80 的确定性函数。四态语义已从"方向判别"改判"风险分档"（探针实证 vol→fwd20 回撤 IS/OOS 双段同向 -2.06/-2.93，趋势→收益方向两段相反，见模块头注）。验收实况：spread(r3−r4) IS +0.26 / OOS +1.73 双段同正，全样本 +0.49 未达冻结线 1.0（诚实 pending）。
- **E（五态判定）**：盘中判定的灰度——state_probs 五元分布（Σ=1），evidence 含量比/广度/缺口/A50 夜盘等 9 维证据，含 missing_features 与 proxy_notes 降级留痕。方向语义（进攻/亢奋）与 B 的风险分档语义**不同轴**。

## 3. 谁生产谁消费（实测 import/DDL 链）

| 资产 | 生产者 | 消费者（grep 实证） |
|---|---|---|
| B anchored 表 | `zephyr.regime.core.anchored_state_machine`（run_compute→internal_compute_provider；历史回填 `scripts/ch/build_anchored_state_history.py`，DDL `apply_anchored_state_ddl.py`） | 回测/考试层：`validate_p0_discrimination.py`（冻结验收输入源）、`compare_state_dualrun.py`、`eval_f2_*`、`eval_exp_expectations.py` |
| C snapshot | RegimeDetector 走 VAL 批（VAL-P0-*） | **生产侧**: `pf_alloc/allocation_inputs.py`、`pf_alloc/crisis_gate.py`、`pf_alloc/allocation_orchestrator.py`、`plan_engine/daily_plan.py`、`strategy_factory/owner_band_t/regime_gate.py`、`strategy_pipeline/daily_decision_orchestrator.py`、`daily_gate_snapshot.py`、`screen_source.py` |
| D alt 信号 | `zephyr.alt_data.alt_regime_signals.py`（scheduler 调度） | `zephyr.regime.features.regime_data_loader.py`、scheduler |
| E 五态台账 | 判定模块（judgment 链，module_id 见行内 payload） | 结算/评估链（Brier 字段待回填）；09-18 才首产 |
| A detector | — | MOD-PA-007 RegimeMetaAllocator（经 C 表快照）、BM-BT-03-E 回测验证 |

**断环实况**（本战役要接的一环）：B 表至今只有考试/验收脚本消费，**没有任何"状态×因子条件化"考试存在**；生产侧（pf_alloc 链）消费的是 C 表 VAL 回填快照，且新鲜度止于 2026-09-15。

## 4. PIT 口径与数据质量要点

1. **B 表 PIT**：vol_pct 滚动分位 t 及以前，结构性 PIT；代价是两个全新增列不可得——表内**没有**主力状态概率列，**没有** confidence_signal 列（总包令原文"主力状态概率或 confidence_signal"在 B 表无此列，本车道如实改用 vol_pct，见 §5）。
2. **C 表数值列疑点**：3621 行中 confidence_signal=0 与 risk_signal=0 均为 3621 行（**全量未填充**，但 shrinkage 列有值 0.885 等）——该表概率列可用，节流三列不可信。另概率后验过尖（§2）。
3. **E 表**：4 行/1 天，无法构成状态序列；其价值在 PIT 契约形制（asof_ts/input_cutoff_ts）与五态语义，是未来盘中条件化的候选轴。
4. **B 表重复行**：plain MergeTree 重复插入（每日 2 行、值一致），查询必须 DISTINCT/GROUP BY 去重；本车道 R2 已按此处理。
5. **#ARCH-344（只引用，不修改）**：Regime 断供即满部署三腿——D01 `_run_hmm` 异常→均匀分布、D12 参数缺失→1.0、D05 detect 异常→1.0，局部保守合成全局"风险机制静默失效"；registry status=**open**，adjudication=fallback 语义三选一（hold-prev/防御上限/告警显化）待裁定，related #309。与本车道关系：C 表节流三列全 0 与断供语义有牵连（断供日指标不可信），**B 表无断供语义列、vol_pct 由行情机械决定，天然规避该问题**——这是选 B 表的第 4 个理由。生产行为本车道一概不动。

## 5. 用哪列做条件化最合适（R 车道裁定）

**`regime_state_anchored.vol_pct`（T-1 日值）**。理由按权重：
1. 唯一同时满足"连续灰度 + 覆盖 IS(2017-07..2023-12) 与考试窗(2024-01..2025-08) 全区间 + PIT 结构保证"的列；
2. 考试窗 403 个交易日与 17 幸存者逐日 OOS 净收益 403 日**逐日精确对齐**（实测）；
3. dominant 是它的确定性阈值函数——用连续列做分位桶，信息量覆盖硬标签；
4. C 表概率列过尖+节流列全 0、E 表只有 1 天，均不构成可用状态序列。

预注册分桶（边界钉死于预注册卡 `prereg_card_survivor_regime_buckets.md`）：IS 期 vol_pct 三分位 = **q33=0.3200 / q67=0.7040**（IS n=1576；分桶占比 IS 低/中/高=33.9%/33.1%/33.1%，考试窗=38.2%/29.3%/32.5%——考试窗略偏低波）。状态取 T-1，禁当日落桶。

## 6. 遗留断点（给总包/后续车道）

- C 表生产侧新鲜度（止于 09-15）与节流三列全 0：pf_alloc 链在用什么、#ARCH-344 裁定前后影响面，建议总包登记专项（本车道不越界）。
- E 表判定台账刚首产，Brier 结算字段尚未回填（evaluated_at 空）——结算链是否在跑待 T/总包确认。
- D 表 F4 BDI 从 1989 年起 18541 行，另类轴×因子条件 IC 归 F 车道。

---
*所有结论暂定；回测日线路径未复权（kline_daily.adj_factor 恒 1），待复权链修复后复核。*

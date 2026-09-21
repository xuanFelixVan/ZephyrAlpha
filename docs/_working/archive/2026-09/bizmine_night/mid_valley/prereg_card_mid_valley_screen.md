---
ttl: task_bound
rule_form: data
verifiability: manual
title: MID 洼地深挖预注册卡——38 可映射候选 × vol_pct 灰度三桶条件 IC 二筛（st-bizmine-mid-20260919，frozen）
owner: ZephyrAlpha-Owner
language: zh
created: 2026-09-19
status: frozen（二筛启动前写死；启动后任何字段不得改动，改动即作废重开）
lane: bizmine W2.4（MID 洼地深挖）
session: st-bizmine-mid-20260919
parent_context: >
  docs/_working/bizmine_night/factor_sop_screen/screen_results.csv（F 车道 IC 大海选，commit 532f9f7b98）
  + docs/_working/bizmine_night/regime_axis/prereg_card_survivor_regime_buckets.md（R 车道桶边界冻结卡）
  + docs/_working/bizmine_night/bizmine_general_order.md §6 W2.4
---

# 预注册卡：MID 洼地二筛（vol_pct 灰度桶条件 IC，38 候选全量重算）

> 本卡在任何二筛计算执行之前写定（2026-09-19 凌晨）。计算代码只实现本卡口径。

## 0. 动机与轴差声明（本卡核心裁定）

- 依据 R 车道弹药账：17 幸存策略收益集中 HIGH（2.48）/LOW（1.12），MID 桶 0.21=15/17 条的收益荒漠 → MID 专属 alpha 是全系统最缺的补强方向（W2.4）。
- **轴差裁定**：F 车道 screen_results.csv 的条件轴是 `alt_regime_signal` F4_BDI_MOMENTUM_Z20 三态（risk_on/risk_off/neutral，全球运价风险偏好代理），**没有 vol_pct 意义上的 MID 桶**。任务要求的「MID 桶 IC_IR」在本仓现有产物中不存在现成列。裁定：**不复用 BDI-neutral 冒充 MID**，改用 R 车道冻结的 `regime_state_anchored.vol_pct` 灰度桶对同一 38 候选全量重算条件 IC（=「二筛」）。F 车道 BDI 结果仅作两轴交叉参考，不入排序键。本裁定属数据面修正（与 F 车道报告 §3.5「两轴交叉核对是下一步」衔接），非口径擅改。

## 1. 候选集（冻结，不再增删）

- `docs/_working/bizmine_night/factor_sop_screen/screen_results.csv` 中 `factor_key` 非空的 **38 个可映射因子**（价格量 34 + 基本面 PIT 4）。映射口径/proxy note/dir 全部沿用 F 车道（f2_mapping_used.csv 同源），不重定义任何因子。
- 不含 L1 车道 14 档量能 indicator 族（同 F 筛边界）。

## 2. 数据与口径（全部沿用 F 车道 f2 管线，只读复用）

- 数据：`c1_market.kline_daily`（K_START 2014-01-01..K_END 2024-02-29）+ `c3_fundamental.financial_indicator`（announce_date PIT）+ `c3_fundamental.ex_dividend_event`（除权剔除）。经 DatabaseService 只读。
- IS 窗：2019-01-01..2023-12-31（与 F 筛一致）；前瞻 5/10/20 日；除权窗样本剔除（三档前瞻各自生效）；截面宽度 ≥300 门；标的 ≥120 日历史 + 非停牌门。
- IC 定义：日度横截面 Spearman 秩 IC（f2_lib.rank_ic_series 同实现）；统计量 = ic_mean/ic_std/ic_ir/ic_t/n_days/pct_pos（f2_lib.ic_stats 同实现）。
- 复权：`kline_daily.adj_factor` 恒 1，全部结论=**暂定**，待复权链修复后复核（缓解=除权事件窗剔除）。

## 3. 状态轴与分桶（本卡唯一变更项）

- 状态变量：`c1_backtest.regime_state_anchored.vol_pct`（hv20 滚动 250 日分位 ∈[0,1]），`SELECT DISTINCT trade_date, vol_pct` 去重（plain MergeTree 有重复插入行），与 R 车道预注册卡 §2 完全同源。
- PIT：交易日 t 取**严格早于 t 的最近一个有状态交易日**（T-1），禁当日值落桶。
- 桶边界（R 卡 §3 冻结值，IS=2017-07-11..2023-12-29 分位，禁考试窗数据）：
  - LOW：vol_pct ≤ 0.3200
  - **MID：0.3200 < vol_pct ≤ 0.7040**
  - HIGH：vol_pct > 0.7040
- 桶日数为 0 或 < 60 的统计量标 low_power，不入 top-10。

## 4. 排序与选择规则（先钉死）

1. 主排序键：**h=10 的 MID 桶 |IC_IR| 降序**；h=5/20 入册作稳健性参考，不参与排序。
2. 通过 §3 low_power 门后取 **top-10**。
3. 「MID 专属形态」标注（Owner 论点目标形态）：h=10 满足 **|ic_t_mid| > 2 且 |ic_t_overall| < 2**（总体平庸但 MID 显著）。附加披露 contrast = |ICIR_mid(h10)| / max(|ICIR_overall(h10)|, 0.01)。

## 5. 诚实三问算法定义（先钉死）

- **①巧合规避检验**：报告 MID 桶 IS（2019-2023）日数与 IC 有效覆盖（n_days_mid）；top-10 每条给 h=5/10/20 三档 MID 桶 IC 同号性——h=10 显著但 h=5/20 反号者标「期限不稳」。
- **②同源检验**：定义「HIGH 桶强候选集」= 本二筛 HIGH 桶 h=10 |IC_IR| 前 10 因子。对 top-10 每条计算与 HIGH 强候选在全 IS 日度 IC 序列（h=10，桶不限）上的 Pearson 相关（有效重叠 ≥200 日）；**|ρ| ≥ 0.7 判高度同源**，其「MID 专属」标幻觉风险。同时报告 top-10 内部两两相关最大值。
- **③多重检验位置**：本二筛统计量总量 = 38 因子 × 3 前瞻 ×（总体+3 桶）= 456 组（与 F 筛同量级）；top-10 的选择发生在 MID 桶 × 3 前瞻 = **114 组**池上。按 IC_t 近正态双侧近似：|t|>2 期望假阳 ≈ 114×0.0455 ≈ **5.2 条**；|t|>3.29 ≈ 0.4 条。对入选条目报告 t 值过线余量，并叠加 inherited 选择效应（126→38 由 F 车道「可映射性」筛选，非随机）。结论：本筛任何条目都**不构成 PASS**，升正式考试须预注册窄测+沙箱+E4。

## 6. 判读标准（先钉死）

- 二筛产物定名「MID 洼地待考池 top-10」，**筛≠考**；每条出预注册卡（考试门槛写死）但考试另行执行。
- 若 MID 桶 IS 日数 < 60 或 top-10 全数 |t_mid| ≤ 2，如实判「MID 洼地在日频截面因子层暂无可考候选」，禁硬凑。
- 与 F 车道 BDI-neutral 排名的 Spearman 秩相关如实披露（两轴一致性参考，不改结论）。

## 7. 禁改清单

桶边界 / 状态变量 / 排序键 / MID 专属形态定义 / 同源相关阈值 0.7 / low_power 门 60 日 / IS 窗——二筛启动后不得回调。任何口径变更须另开新卡并声明本卡作废。

## 8. 产物锚

- 落点：`docs/_working/bizmine_night/mid_valley/`（mid_valley_top10.csv + 本卡 + 候选预注册卡 + report.md）。
- 中间件：`.runtime/tmp/bizmine/mid/`（mid_screen.py 管线、mid_results_long.csv、mid_ic_series_h10.pkl）。

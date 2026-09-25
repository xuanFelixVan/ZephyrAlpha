---
ttl: task_bound
lane: IBT-D01
sid: st-qmine-20260925
created: 2026-09-26
updated: 2026-09-26
status: 口径对照表 13 维已实测（0 维待测）；抽样对拍进行中——完成度见 §2 与 pairwise_report.md
title: 考尺引擎 ↔ 整装引擎 口径对照表（IBT-D01，机读真源=同目录 caliber_map.yaml）
---

# 考尺 ↔ 整装 双引擎口径对照表

> 立案：`docs/_working/decision_map_campaign_20260924/11_integrated_backtest_audit.md` §4.3 + §10 IBT-D01（P0-1）。
> 判据原文：`17_quantified_acceptance.md` §一 解读纪律——"成绩=**考尺口径的相对排名**；跨引擎绝对值翻译待
> IBT-D01 对照表（容差(建议)：同名格 sharpe 差>30% 即列口径差异清单）"。
> 机读真源=本目录 `caliber_map.yaml`（本文件是人读投影，冲突以 yaml 为准）。
> 取证纪律：每维度给两侧 `文件:行号` + 实测数值；DB 实测走 `zephyr.infrastructure.database_service` reader，
> 全部只读；冻结件（`config/exam_scale_cost_gate.yaml`、`config/search_space_prereg.yaml`、
> `scripts/audit/cost_trio_exam.py`）零改动，仅登记。

## 0. 两侧引擎真源

| 侧 | 入口 | 成本/撮合/指标真源 |
|---|---|---|
| 考尺／网格 | `scripts/backtest/factory_grid_executor.py`（:777-781 调引擎，:797-805 五档扫描） | `scripts/backtest/translated/_c4_engine.py`（run_backtest :399-436 / daily_net_returns :439-459）+ `src/zephyr/backtest/regime_validation/exam_cost_gate.py` |
| 整装回测 | `src/zephyr/backtest/implementations/vectorized_engine.py`（run :210-430） | `core/matching_logic.py`（费率字面量）+ `core/matching_engine.py`（涨跌停/整手/参与率/冲击）+ `core/cost_model_calibration.py`（滑点分层）+ `core/metrics.py`（Sharpe/年化）+ `core/data_handler.py`（复权） |

## 1. 逐维度对照（13 维，全实测）

| # | 维度 | 考尺侧（位置 / 实测值） | 整装侧（位置 / 实测值） | 判定 |
|---|---|---|---|---|
| D01 | 佣金 | `_c4_engine.py:46,422` COMMISSION_BP=2.5（万2.5 双边）；**无 5 元地板** | `matching_logic.py:69,76,110,114` 万0.854 双向 + MIN_COMMISSION=5 元/笔（不免五） | **diff**（费率 2.93 倍 + 考尺无地板） |
| D02 | 印花/过户 | `_c4_engine.py:47,422` STAMP_BP=10 挂在"双边合成项"里 → 生效为**每腿平摊**，非卖出单边 | `matching_logic.py:74,101,112-113` 印花万5 **卖出单边**（2023-08 法定）+ 过户费万0.1 双向 | **diff**（考尺少计过户费；印花方向不同） |
| D03 | 滑点档与成本式 | `_c4_engine.py:48,420-423`：`cost=换手1侧×(2×2.5+10+2×slip)/1e4`，slip=5bp 平面 → **每腿等效 12.5bp**（买腿 +5bp 超计、卖腿 −5bp 少计，真值 7.5/17.5bp）；档覆盖走 `slippage_bp` kwarg（:403,411-413），五档 [0,5,10,20,40]（`exam_scale_cost_gate.yaml:12`，冻结件未动） | `cost_model_calibration.py:175-180,228-243,267-296`：ADV 五分位 7.24/5.69/4.67/4.00/2.34 bp 单边，缺流动性信息→3.79bp，LEGACY 1bp 仅对照；+ AC 尺寸冲击腿（`matching_engine.py:128-129,361`） | **diff**（平面 vs 分层+冲击；考尺无冲击腿） |
| D03b | "前置≥30bp 土规"归属 | 两引擎与两配置 grep `30bp\|≥30` **零命中** | 同零命中 | 非双引擎口径：属 L05 做T 车道土规（`links/L05_t0/etf_t0_cost_and_pool/MINE.md:91` 实测 31.2bp/前置≥30bp/30 对），登记防误并 |
| D04 | 撮合时点/价源 | `_c4_engine.py:405,416,419`：T 收盘定价、`w.shift(1)×rets` → 收益自 T+1 起算；**无开盘价腿** | `vectorized_engine.py:123,245-252,285-301,514-516`：execution_lag_days=1 → **T+1 开盘优先**成交（缺 open 回退收盘），同根成交硬断言禁止 | **diff**（close_T vs open_{T+1}，隔夜跳空归属不同） |
| D05 | 成交量约束 | `_c4_engine.py` run_backtest 不消费 volume → 目标权重**全额成交** | `vectorized_engine.py:153` + `matching_engine.py:128,361`：单标的单日参与率上限 **10%**，超限收缩 + AC 冲击 | **diff**（考尺无容量约束=乐观侧） |
| D05b | volume 量纲陷阱 | 不消费故无感 | `matching_engine.py:48-52,374` 明示：`kline_daily.volume` 混存「手/股」，归一在 `load_history→market_units` 出口；**直接喂 hfq「手」口径会把 10% 上限收紧 100 倍** | 对拍工装风险位：本项目喂料口径实测见 `pairwise_report.md` §附 |
| D06 | T+1 与持仓 | `_c4_engine.py:417-420` 由日频网格**隐式**满足；无持仓账本、无现金约束 | `vectorized_engine.py:95,346,374,490`：`apply_fill(fill, allow_t_plus_1=False)` 显式锁定，拒单分类计数；现金不足即拒 | **diff**（隐式 vs 显式账本；整装会因现金/T+1 拒绝成交） |
| D07 | 涨跌停处理 | `_c4_engine.py:65,353-396`：封板判定=原始价 close vs `stk_limit`，容差 1e-4；封涨停禁买/封跌停禁卖；原料不可得 **fail-open** | `matching_engine.py:225-267` **方向感知**拒单（涨停拒买、跌停拒卖、涨停日卖单放行；持仓跌出信号→强制清仓卖单，仅跌停/无价跳过）；涨停价三级链 stk_limit PIT 行→`_limit_pct_of` 日期切片→板块前缀推断；基准价=exec 价（T+1 开盘优先），`vectorized_engine.py:259-263,274,339` prev_close 逐日推进；CH 不可达同样 fail-open | **partial_same_family**（同族但三点未证等价：①基准价 close_T vs open_{T+1} ②判据=绝对价+1e-4 vs 绝对价缺行退化比例链 ③考尺无强制清仓腿） |
| D08 | 停牌/缺行 | `_c4_engine.py:415-417` 价格面板 ffill → 停牌日 0 收益、权重延续；ST 由 `filter_st`（:308-320）置 NaN | `portfolio.py:187-189,375-389` `_resolve_price` 结转最后已知价（显式反"按 0 估值致 NAV 幻视回撤"红队实证） | **same_in_effect**（收益层等价；权重侧 ffill vs 逐日读面板不同实现） |
| D09 | 复权口径 | `_c4_engine.py:58,71-74` 读**后复权表** `c1_market.kline_daily_hfq`（close>0 过滤，FINAL） | `data_handler.py:396,419-430,279-303` 读原始表 `kline_daily` + 由 `c3_fundamental.ex_dividend_event` 现算 adj_factor → `compute_qfq_close` **前复权** | **diff 表述 / 实测等价**：除权日两口径日收益 \|Δ\| 最大 7.9bp（000002，均值 4.8bp）、000001 最大 0.04bp、600519 最大 0.58bp；非除权日最大 0.6bp；全窗累计净值 4 位小数一致。**红证已跑**（同尺注入已知错口径：不复权→5/5 红点 max 673bp；cum 方向取反→5/5 红点 max 1302bp），故"等价"非哑尺结论。`kline_daily.adj_factor` 物理列实测恒 1（2024Q1 31.03 万行 n_distinct=1）=死列，整装侧不消费它（现算自 ex_dividend_event）故不受影响；**hfq 是表族**（实测在库 11 张：daily/weekly/monthly_hfq + 各自 legacy/preversion/quarantine/recalc 变体），改一张须族内对拍 |
| D10 | 年化基准日 | `_c4_engine.py:425,431` years=len/244、`exam_scale_cost_gate.yaml:24` days_basis=244 | `metrics.py:28,49,108` TRADING_DAYS_PER_YEAR=252、`(1+tr)^(252/n)−1` | **diff**（A 股真实交易日实测 2019-2024 逐年 = 244/243/243/242/242/242 → **244 才贴地**，252 系统性把年数算少 3.2%、把年化收益抬高） |
| D11 | Sharpe 算法 | `_c4_engine.py:426` `net.mean()/net.std()×√244`，**rf=0**；样本下限由调用方把关（`factory_grid_executor.py:779` net 有效天数<60 判死） | `metrics.py:47,114-122` `(returns − 0.025/252).mean()/std×√252`，**rf=2.5%/年**；n<MIN_SAMPLES_FOR_SHARPE=60 → 直接 0 | **diff**（√252/√244=1.0164 缩放 + 日均 rf 扣减 0.99bp ≈ 年 2.42pct 均值下压；对低均值格 rf 项可单独造成 >30% 相对差） |
| D12 | 窗与 PIT 切点 | `factory_grid_executor.py:1028-1029` 默认 2020-01-01..2023-12-31（+200 自然日预热，:699）；`_c4_engine.py:50-52` C4 族同窗（ETF 2021-04-01 起）；`search_space_prereg.yaml:41` 冻结搜索窗 2019-01-04..2025-09-09 | `IBT-PROTOCOL-V1.md:56,58` W_IS=2019-04-01..2023-12-31、W_HOLDOUT=2025-09-09..2026-09-08 单次烧毁；`vectorized_engine.py:130-134,311-330` 逐日 PIT 池过滤（未上市/退市/ST/次新<120 自然日） | **partial**（右端切点 2025-09-09 同源；左端与池构造机制不同构——考尺=窗口并集成份快照 `index_constituent` SCD-2，`_c4_engine.py:88-98`；实测交易日 2020-2023=970 天、2019-04..2025-09=1566 天） |
| D13 | 仓位/资金归一 | `_c4_engine.py:417-419` 行 Σ 原样使用（**现金意图保留**），无初金、无整手、无利息 | `vectorized_engine.py:228-231,463-469` `_normalize_day_signals` 强制 Σ→1 **满仓摊派**（只取 >0 分量，负权重被丢弃）+ `initial_capital=100万`（:143）+ `matching_engine.py:225` 100 股整手 | **diff**（结构性不可直译主因之一；引擎自带 `swallowed_cash_mass` 绊线可量测被吞现金质量） |

**统计**：13 维（含 D03b/D05b 两条归属与风险位登记）＝ 8 diff + 2 partial + 1 same_in_effect + 2 登记项；**"待测"=0**。

## 2. 抽样对拍（≥10 同名格，CPU-only）

见本目录 `pairwise_report.md`（含差值表与 >30% 口径差异清单）。运行日志 `.runtime/tmp/d01_pairwise.log`、机读结果
`.runtime/tmp/d01_pairwise_result.json`（TTL 件，随批 promote 或改落 docs/_working，见 landing 待落清单）。

## 3. 结论三态

待对拍完成后填写（§三态判据=差>30% 清单是否可由 D10/D11 两维解析式闭合）。

## 4. 推荐统一侧（推荐≠裁定）

待对拍完成后填写。

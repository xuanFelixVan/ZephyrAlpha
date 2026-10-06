---
campaign: matrix-20261006
lane: E-exam-w2
ttl: task_bound
---

# codesym_factor_exam_v1 — code_symbol 因子适配器第一波（M-7 B道）分数册摘要

- generated_at_utc: 2026-10-06 10:42:22.679740+00:00
- harness: `.runtime/tmp/st-matrix-20261006/adapter_harness.py`（临时工装，只读 CH，零既有文件修改）
- 对象: factor_registry 全部 code_symbol 非空条目 **31 条**；判据=roster.PREREG_V1['factor_pass_line']（|IC|>=0.02, ICIR>=0.3, retain>=0.5, 覆盖率>=0.60）
- 窗口: HOLDOUT=2025-10-09..2026-09-30（考试），IS_REF=2024-10-08..2025-09-30（衰减对照），UNION=2024-10-08..2026-09-30

## 总量

- 总数 **31** = 实测 **18**（pass **0** / retire_candidate **3** / rework **15**）+ 未实测 rework **13**
- 失败分类: {"structural_not_cross_sectional": 6, "data_gap": 7, "metrics_below_prereg_line": 9, "retire_no_alpha": 3, "coverage_below_60pct": 5, "panel_degenerate": 1}

## A. 实测 18 条（真函数算值 → fast_rank_ic + judge）

| factor_id | 因子 | IC_5d(HOLDOUT) | ICIR | retain | 覆盖率 | verdict | 判语 |
|---|---|---|---|---|---|---|---|
| FCT-MOM-029 | 20日动量（代码锚） | -0.051652 | -0.30995 | 0.592581 | 0.984289 | **rework** | |ic|=0.0517(线0.02) icir=-0.31(线0.3) retain=0.59(线0.5) |
| FCT-QUAL-002 | 价值因子（代码锚，价均偏离口径） | 0.011357 | 0.113055 | 0.773803 | 0.977252 | **rework** | |ic|=0.0114(线0.02) icir=0.11(线0.3) retain=0.77(线0.5) |
| FCT-INTRADAY-029 | 盘中VWAP（代码锚） | -0.020094 | -0.092122 | 0.793529 | 0.977252 | **rework** | |ic|=0.0201(线0.02) icir=-0.09(线0.3) retain=0.79(线0.5) |
| FCT-INTRADAY-030 | 盘中收盘价（代码锚） | -0.027582 | -0.179646 | 0.701322 | 0.977252 | **rework** | |ic|=0.0276(线0.02) icir=-0.18(线0.3) retain=0.70(线0.5) |
| FCT-FQ-001 | 应计因子（Sloan） | 0.002311 | 0.034645 | 0.634102 | 0.986215 | **retire_candidate** | clean窗无可测alpha（|ic|=0.0023, |icir|=0.03） |
| FCT-FQ-002 | 现金流实现率 | 0.005374 | 0.109261 | 10.688866 | 0.978636 | **rework** | |ic|=0.0054(线0.02) icir=0.11(线0.3) retain=10.69(线0.5) |
| FCT-FQ-003 | GPOA 毛利率资产比 | -0.006293 | -0.074719 | 2.809865 | 0.986171 | **rework** | |ic|=0.0063(线0.02) icir=-0.07(线0.3) retain=2.81(线0.5) |
| FCT-FQ-004 | 单季盈利变化 ΔROEq | 0.007724 | 0.122851 | 0.720101 | 0.982987 | **rework** | |ic|=0.0077(线0.02) icir=0.12(线0.3) retain=0.72(线0.5) |
| FCT-GR-001 | 单季营收同比 | 0.009099 | 0.086518 | 0.522313 | 0.984083 | **rework** | |ic|=0.0091(线0.02) icir=0.09(线0.3) retain=0.52(线0.5) |
| FCT-GR-002 | 盈利加速度 | 0.002369 | 0.064091 | 2.226558 | 0.983616 | **retire_candidate** | clean窗无可测alpha（|ic|=0.0024, |icir|=0.06） |
| FCT-FQ-005 | 信息质量代理 | 0.003185 | 0.102873 | 0.8915 | 0.982539 | **rework** | |ic|=0.0032(线0.02) icir=0.10(线0.3) retain=0.89(线0.5) |
| FCT-FQ-006 | Piotroski F-Score | 0.004088 | 0.076581 | 5.617673 | 0.985546 | **retire_candidate** | clean窗无可测alpha（|ic|=0.0041, |icir|=0.08） |
| FCT-EXP-001 | 一致预期EP（盈利收益率） | 0.026896 | 0.250795 | 0.625373 | 0.466452 | **rework** | coverage 0.47<0.6 |
| FCT-EXP-002 | 盈利修正动量 | 0.003561 | 0.316483 | 3561.241867 | 0.534078 | **rework** | coverage 0.53<0.6 |
| FCT-EXP-003 | 预期修正广度（上调占比） | 0.012679 | 0.707107 | 12679.023407 | 0.06006 | **rework** | HOLDOUT 有效 IC 日不足30（n=3）——面板退化 |
| FCT-EXP-004 | 异常研报覆盖度 | 0.0072 | 0.081002 | 0.187261 | 0.475256 | **rework** | coverage 0.48<0.6 |
| FCT-EXP-005 | 分析师分歧度 | -0.004714 | -0.353033 | 4714.052256 | 0.530665 | **rework** | coverage 0.53<0.6 |
| FCT-EXP-006 | 评级动量（评分制） | 0.014052 | 0.340032 | 7.15515 | 0.473117 | **rework** | coverage 0.47<0.6 |

## B. 未实测 13 条（全调用形态失败/结构不适配，按条留痕）

| factor_id | 分类 | 缺什么 | 探针证据 |
|---|---|---|---|
| FCT-SENT-016 | structural_not_cross_sectional | structural:cross_section_width——横截面宽度=期指品种数(≤4)<30/日，低于 fast_rank_ic 最小样本线，截面 IC | {"trade_date": "2026-09-15", "degraded": false, "n_products": 4, "per_symbol": { |
| FCT-SENT-017 | structural_not_cross_sectional | structural:cross_section_width——横截面宽度=期指品种数(≤4)<30/日，低于 fast_rank_ic 最小样本线，截面 IC | {"trade_date": "2026-09-15", "degraded": false, "n_products": 4, "per_symbol": { |
| FCT-SENT-018 | structural_not_cross_sectional | structural:market_level——代码输出为市场级时序值（单值/日），无截面离散度，fast_rank_ic 截面秩相关数学不可定义；prere | {"date": "2026-09-15", "pcr": 1.0790336285099162, "pcr_percentile": 0.6764705882 |
| FCT-SENT-019 | structural_not_cross_sectional | structural:market_level——代码输出为市场级时序值（单值/日），无截面离散度，fast_rank_ic 截面秩相关数学不可定义；prere | {"date": "2026-09-15", "pcr": 1.0790336285099162, "pcr_percentile": 0.6764705882 |
| FCT-SENT-020 | data_gap | data_gap:分钟级 breadth 快照历史仅 2026-08-24 起（24 交易日，market_breadth_snapshot），HOLDOUT  | method=analyze_breadth_acceleration 最小输入(None×2)调用结果=None |
| FCT-SENT-021 | data_gap | data_gap:同 FCT-SENT-020（分钟 breadth 快照缺 2025-10..2026-08 历史段） | method=analyze_breadth_acceleration 最小输入(None×2)调用结果=None |
| FCT-SENT-022 | data_gap | data_gap:同 FCT-SENT-020（分钟 breadth 快照缺 2025-10..2026-08 历史段） | method=analyze_breadth_acceleration 最小输入(None×2)调用结果=None |
| FCT-SENT-023 | data_gap | data_gap:护盘背离需指数贡献度拆解+黄白线分钟 spread 历史（CH 无对应数据表） | method=detect_distortion 最小输入(None×4)调用结果=None |
| FCT-SENT-024 | data_gap | data_gap:量能外推需 20 日同时刻分钟成交占比曲线历史（CH 无分钟成交历史表） | method=forecast_volume 最小输入(None×2)调用结果=None |
| FCT-SENT-025 | data_gap | data_gap:需日内个股 high/current gain 快照历史（realtime_snapshot 表为空） | method=count_large_drawdowns 最小输入(None×1)调用结果=None |
| FCT-SENT-026 | structural_not_cross_sectional | structural:market_level——代码输出为市场级时序值（单值/日），无截面离散度，fast_rank_ic 截面秩相关数学不可定义；prere | {"date": "2026-09-15", "rotation_velocity": 295.17941585535465, "velocity_percen |
| FCT-SENT-027 | structural_not_cross_sectional | structural:watchlist——代码输出为 >80 分位个股风险清单（StockDivergenceWatch 子集），非全截面因子值，prereg | {"date": "2026-09-15", "rotation_velocity": 295.17941585535465, "velocity_percen |
| FCT-SENT-028 | data_gap | data_gap:同 FCT-SENT-020（分钟 breadth 快照缺 2025-10..2026-08 历史段） | method=analyze_breadth_acceleration 最小输入(None×2)调用结果=None |

## 关键发现与口径留痕

- **MOM-029 动量**：|IC_5d|=0.0517 过 IC 线但 ICIR=-0.31（负向=反转语义）；registry 未声明 direction 字段，按原方向判 → rework。若登记 direction=short 则 ICIR=+0.31 恰过线——建议下一波补 direction 注解后重判。
- **FQ/GR 财报族**：6 条覆盖率高（98%+）但 HOLDOUT 无效α（3 条 retire_candidate、5 条 |IC|<线）；FQ-002/FQ-003/FQ-006 的 retain>1 系 IS_REF 窗 |IC|≈0（分母噪声），如实留痕不作通过证据。
- **EXP 族**：4 条卡覆盖率线（0.47~0.53<0.60，consensus_daily 只覆盖部分票，如实缺口）；EXP-001 IC=0.0269 过线但覆盖率不足；EXP-003 研报事件网格面板仅 3 个有效 IC 日=面板退化。
- **SENT 族结构缺口**：6 条输出为市场级标量/4 品种宽截面/风险清单（截面 IC 数学不可定义，需时序择时考试通道）；7 条缺分钟级历史数据线（breadth 快照仅 2026-08-24 起、realtime_snapshot 空、无分钟成交/黄白线历史）。
- 被测模块零修改；SENT 探针均为 live 只读执行（futures_basis/option_sentiment/sector_divergence 实跑成功非降级）。
- 适配器明细（每条 adaptation 字段）与逐日指标见同目录 `codesym_factor_exam_v1.yaml`。

- prereg_v1 全文与窗口冻结块：见 yaml 头部（与 scripts/backtest/fexam/roster.py 同源）。

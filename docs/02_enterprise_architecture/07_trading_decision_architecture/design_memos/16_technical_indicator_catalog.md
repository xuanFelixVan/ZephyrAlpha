---
ttl: permanent
doc_type: architecture_view
title: 技术指标目录
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.1"
date: 2026-08-15
topic: technical_indicator_catalog
scope: 07_trading_decision_architecture
---

> ## 结案报告（2026-08-16 补记）
>
> **实际开发**：2026-08-12 依生产代码重建（git 灾难丢失后回建），§6 回填 40 指标/58 输出列全表（5 大类公式/参数/输出列）；2026-08-13 技术指标注册表建成（会话 AI-REG-IND-001），与本目录互为索引。
>
> **最终成果**：40 指标/58 列/5 大类目录定稿，口径以代码与测试契约为准。
>
> **未做事项及原因**：00_index 仍写"8 大类指标规范"未同步——重建后分类口径以代码真源为准（5 大类），仅剩索引描述同步项（§7 开放问题已登记）。

# 技术指标目录

> **性质**：architecture_view / 清单文档。记录系统支持的全部传统技术指标（40 指标 / 58 输出列 / 5 大类）的目录、计算规范和周期覆盖。
> **代码真源**：`src/zephyr/factor/technical_indicators/`（7 文件，MATURITY=production，纯 pandas/numpy 自实现，无 TA-Lib 依赖，算法对齐通达信）+ `schemas/categories/market_technical_indicator.py`。
> **口径修正**：早期文档写"~55 输出列"为过时约数；实际 **58 列**（测试契约 `test_indicator_base.py` `_EXPECTED_TOTAL=40 / _EXPECTED_COLUMN_TOTAL=58` 锁定）。
> **历史说明**：00_index 标本文"active v1.0.0（8大类指标规范）"，磁盘仅存 0.1.0 骨架——曾丢失；重建后分类口径以代码为准（5 大类，非 8 大类）。

## 1. 主题组信息

| 项 | 内容 |
|---|---|
| 主题组 | G01 数据与特征层（地基层·1x 段位） |
| 依赖 | [15_data_feature_layer_spec](15_data_feature_layer_spec.md)（特征层规范） |
| 正交性 | ✅ 纯数据计算，与 regime/alpha/组合/风控正交 |
| 优先级 | P1（技术指标是因子工程和策略层的基础输入） |
| 状态 | ✅ active v1.0.1（计算+存储+测试已施工；调度挂接与注册表待施工，见 §7） |

## 2. 技术指标计算规范

- 传统技术指标全部基于 OHLCV K 线计算，覆盖 1min~月线 **9 个周期**（1min/5min/15min/30min/60min/120min/日/周/月）；120min 由 60min K 线两根聚合生成（09:30-11:30 / 13:00-15:00，奇数根不丢弃）。
- **why 自实现不引 TA-Lib**：①TA-Lib 的 C 依赖在 Windows 单机是部署负担（2026 年仍是其最大采用门槛，pandas-ta 系以"免 TA-Lib"为卖点即佐证）；②算法需对齐通达信口径（A 股用户看盘的共识基准，如 SMA(X,N,1)=ewm(alpha=1/N)、EMA adjust=False、BOLL std ddof=0、VR 平盘计两侧），外部库口径对不齐；③纯 pandas/numpy 可向量化批量算全市场。
- 反转类信号列约定 Float64：0=无 / 1=正（看涨/顶背离）/ −1=负。
- 预热期输出 NULL 不前向填充——避免前视偏差（PIT 铁律在指标层的落实）。

## 3. 技术指标存储架构

表 `c1_market.technical_indicator`（schema 真源：`schemas/categories/market_technical_indicator.py`）：
- **单表设计 + `period` LowCardinality 列**区分 9 周期——why 单表：9 张分表的 schema 演进要改 9 处，单表加 period 过滤即可；
- **`trade_time DateTime64(3,'Asia/Shanghai')`**——日/周/月=当天 00:00，分钟线=K 线起始时间戳，解决日内多根 K 线被 ReplacingMergeTree 误去重的原设计缺口；
- **PARTITION BY (period, toYYYYMM(trade_date))**——周期+月双键分区，回算/归档可按周期整批 DROP；
- **ORDER BY (symbol, period, trade_time)**——与 K 线表对齐，JOIN 不迷路；
- 58 个指标列全部 `Nullable(Float64)`；治理列 `data_source`（固定 'internal'）+ `ingest_ts` + MATERIALIZED 派生列 `exchange`/`symbol_canonical`（TRAE-082）。

## 4. 调度策略

- **计算 Provider 已施工**：`data/implementations/internal_compute_provider.py`（source_name="internal"）——`_PERIOD_MAP` 覆盖 9 周期→各自 K 线源表；`ALL_PERIODS` 全量回算顺序 **daily→weekly→monthly→60min→120min→30min→15min→5min→1min**（日/周/月先行，分钟随后）；按 symbol 分批（100 只/批）防 OOM；列序 lazy 加载自 schema INSERT_COLUMNS（失败抛 RuntimeError 不静默 fallback）。
- **设计口径**：增量调度（technical_indicator_incremental）每日盘后处理日线；全量回算（technical_indicator_full_refresh）周末覆盖 9 周期。
- **⚠️ 调度未闭环（待施工）**：tasks.yaml 中无这两个任务条目；`scheduler.py create_provider()` 无 `source=="internal"` 分支（hk_trade_calendar_refresh 等 existing internal 任务同样受影响）。见 §7 开放问题①。

## 5. 三级时间框架栈映射

| 层级 | 周期 | 用途 | 指标组合 |
|---|---|---|---|
| 趋势层 | 月线/周线 | 大趋势判断 | MA/MACD |
| 交易层 | 日线 | 交易信号 | KDJ/RSI/MACD |
| 入场层 | 60min/30min | 精准入场 | BOLL/RSI |
| 微调层 | 15min/5min | 微调时机 | KDJ/RSI |
| 剥头皮 | 1min | 超短线 | MA/VOL |

why 栈映射：多周期共振是 A 股技术分析的主流用法；指标全周期回算后，策略可按栈取数（趋势层定方向、交易层定信号、入场层定点位），避免单周期信号的噪声交易。

## 6. 指标清单（40 指标 / 58 输出列，已施工）

> 注册表真源：`TechnicalIndicatorRegistry`（运行时装饰器注册）；YAML 注册表 REG-IND-001 待施工（见 §7②）。测试 243 个用例锁定数值正确性 + Registry↔DDL 双向交叉校验。
> **40 指标 vs "MVP 只需 15-20 个"的裁定**：40 个全部已施工且 243 测试已绿，**裁剪已完成的指标 = 删已绿代码 + 删表列，纯负收益**；指标是数据不是策略，多算一列的边际成本≈0（单表 Nullable 列），而策略侧"只用其中 15-20 个"的选择自由始终在消费方。故维持 40 指标全集。

### 6.1 趋势类 trend.py（10 指标 / 18 列）

| indicator_id | 输出列 | 默认参数 | 公式要点 |
|---|---|---|---|
| ma | ma_5/10/20/60 | periods=[5,10,20,60] | 收盘价 rolling mean |
| ema | ema_12/26 | periods=[12,26] | ewm(span, adjust=False)，种子=首值无预热 NaN |
| wma | wma_10 | period=10 | 线性加权 1..N |
| dema | dema_12 | period=12 | 2×EMA − EMA(EMA) |
| macd | macd_dif/dea/hist | 12/26/9 | DIF=EMA12−EMA26；DEA=EMA9(DIF)；HIST=2×(DIF−DEA) |
| adx | adx_14 | period=14 | DX=\|+DI−−DI\|/(+DI+−DI)×100；ADX=MA(DX) |
| dmi | pdi_14/mdi_14 | period=14 | ±DM 滚动 SUM 平滑（非 EMA）×100/MTR |
| cci | cci_14 | period=14 | TP=(H+L+C)/3；(TP−MA)/(0.015×AVEDEV) |
| sar | sar | af_step=0.02, af_max=0.2 | 逐 bar 迭推，翻转重置 |
| trix | trix/trma | period=12 | 三重 EMA 变化率×100 |

### 6.2 动量类 momentum.py（10 指标 / 15 列）

| indicator_id | 输出列 | 默认参数 | 公式要点 |
|---|---|---|---|
| kdj | kdj_k/d/j | 9/3/3 | RSV=(C−Ln)/(Hn−Ln)×100；K/D 通达信 SMA；J=3K−2D |
| rsi | rsi_6/12/24 | periods=[6,12,24] | SMA(up)/SMA(\|Δ\|)×100 |
| wr | wr_14 | period=14 | (Hn−C)/(Hn−Ln)×100 |
| roc | roc_12 | period=12 | (C/Cn−1)×100 |
| mtm | mtm_12/mtmma_12 | 12/6 | MTM=C−Cn；MTMMA=MA(MTM,6) |
| cmf | cmf_20 | period=20 | CLV=(2C−H−L)/(H−L)；SUM(CLV×V)/SUM(V) |
| uos | uos | 7/14/28 | (4×Avg7+2×Avg14+Avg28)/7×100 |
| ao | ao | 5/34 | MA((H+L)/2,5)−MA((H+L)/2,34) |
| cmo | cmo_14 | period=14 | (Su−Sd)/(Su+Sd)×100 |
| stochrsi | stochrsi | 14/14 | (RSI−min)/(max−min) |

### 6.3 波动类 volatility.py（8 指标 / 13 列）

| indicator_id | 输出列 | 默认参数 | 公式要点 |
|---|---|---|---|
| atr | atr_14 | period=14 | TR=max(H−L,\|H−Cp\|,\|L−Cp\|)；ATR=MA(TR) |
| boll | boll_upper/middle/lower | 20/2 | MID=MA；±2×STD（ddof=0 对齐通达信） |
| keltner | kc_upper/middle/lower | 20/10/2 | MID=EMA(C,20)；±2×ATR(10) |
| donchian | dc_upper/lower | period=20 | max(H,N)/min(L,N) 含当前 bar |
| stddev | stddev_20 | period=20 | 收盘价 STD（ddof=0） |
| bandwidth | boll_bw | 20/2 | (UPPER−LOWER)/MID |
| percent_b | boll_pctb | 20/2 | (C−LOWER)/(UPPER−LOWER) |
| histvol | histvol_20 | period=20 | STD(log 收益, ddof=1)×√252×100 年化 |

### 6.4 量能类 volume.py（7 指标 / 7 列）

| indicator_id | 输出列 | 默认参数 | 公式要点 |
|---|---|---|---|
| obv | obv | 无 | sign(ΔC)×V 累积 |
| mfi | mfi_14 | period=14 | TP=(H+L+C)/3；100−100/(1+正MF/负MF) |
| vwap | vwap | 无（可传 period 滚动） | 累积 SUM(C×V)/SUM(V) |
| vr | vr_26 | period=26 | 100×(2×涨量+平量)/(2×跌量+平量)（通达信平盘计两侧） |
| ad | ad | 无 | cumsum(CLV×V) |
| pvt | pvt | 无 | cumsum(V×pct_change) |
| wvad | wvad_24 | period=24 | SUM((C−O)/(H−L)×V, N) |

### 6.5 反转类 reversal.py（5 指标 / 5 列）

| indicator_id | 输出列 | 默认参数 | 公式要点 |
|---|---|---|---|
| candlestick_pattern | candle_pattern | patterns="all" | 6 形态编码：0无/1锤子/±2吞没/3启明星/4黄昏星/5十字星 |
| rsi_divergence | rsi_divergence | rsi=12, lookback=20 | 价升 RSI 降→1；价跌 RSI 升→−1（简化趋势对比） |
| macd_divergence | macd_divergence | lookback=20, 12/26/9 | 价格 vs MACD HIST 趋势对比 |
| boll_breakout | boll_breakout | 20/2 | C>上轨→1；C<下轨→−1 |
| vol_price_divergence | vol_price_div | lookback=10 | 价升量缩→1；价跌量增→−1 |

### 6.6 与 factor_registry 的正交边界

技术指标（technical_indicator_registry / 本目录）与因子（factor_registry）正交：**技术指标=OHLCV 的确定性变换，无 alpha 断言；因子=对未来收益有假设的截面/时序信号，需过 ABS001 门禁**。技术指标可作为因子输入（如 boll_pctb 进动量因子），但指标本身不进 factor_registry、不做 IC 评估。why 分开：指标是"数据"（一次回算全市场复用），因子是"假设"（需治理流水线生老病死）——混在一起会让 111 条因子注册表被 58 个无假设列稀释。

## 7. 开放问题

1. **调度未闭环（P0）** → **已闭环（2026-08-31 终审批实证核销）**：tasks.yaml 已挂 technical_indicator_incremental（L1877）/ technical_indicator_full_refresh（L1892）两条目，scheduler.py L1227 `source=="internal"` 分支已落地（64 号 Q18 施工批，2026-08-28）。Provider→调度→回算链路全通。
2. **REG-IND-001 YAML 注册表未施工** → **已闭环（2026-08-31 终审批实证核销）**：`docs/01_policies_and_standards/_registry/catalogs/technical_indicator_registry.yaml` 已在位（registry_id=REG-IND-001，条目真源），本文按原裁定降级为 why 层。
3. **命名陷阱**：tasks.yaml 的 `stock_indicator_full_refresh` 实为 AKShare 估值指标写 stock_indicator 表，与本表无关——后续调度挂接时防止误挂。
4. **公式简化项**：rsi/macd_divergence 为简化趋势对比（非峰谷检测），精度需求出现时再升级。
5. **00_index 同步（越界登记）** → **已闭环（2026-08-31 终审批实证核销）**：00_index 现行描述已为"5大类指标规范"，分类口径一致，无需再同步。

## 8. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-08-10 | 0.1.0 | 初稿骨架 | 技术指标目录文档。**注意**：本文件曾因未 git commit 丢失，后从代码引用和 architecture_issue_registry 描述重建骨架 |
| 2026-08-12 | 1.0.0 | 骨架→active：§6 回填 40 指标/58 列全表（5 大类公式/参数/输出列）；修正 55→58 口径；§6 增"40 指标不裁剪"裁定；补 §6.6 与 factor_registry 正交边界；新增 §7 开放问题（调度未闭环/REG-IND-001 待施工/00_index 同步） | 回填已施工代码 why；口径以测试契约为准；缺口入开放问题不擅自施工 |
| 2026-08-15 | 1.0.1 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-08） | 清单/公式/裁定无冗余，通读+自审零发现，不为压而压 |

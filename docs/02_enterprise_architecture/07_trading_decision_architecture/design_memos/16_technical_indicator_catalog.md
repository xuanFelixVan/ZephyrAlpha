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

## 6. 指标清单（137 在产指标 / 201 输出列，已施工；注册 138 条含退役 1）

> 注册表真源：`TechnicalIndicatorRegistry`（运行时装饰器注册）；YAML 注册表 REG-IND-001 已在位（条目真源）。测试 762 个用例锁定数值正确性 + Registry↔DDL 双向交叉校验。
> **48 指标 vs "MVP 只需 15-20 个"的裁定**：全部已施工且 470 测试已绿，**裁剪已完成的指标 = 删已绿代码 + 删表列，纯负收益**；指标是数据不是策略，多算一列的边际成本≈0（单表 Nullable 列），而策略侧"只用其中一部分"的选择自由始终在消费方。故维持全集（2026-09-14 扩至 92：标配+统计族+批 2a/2b+批 3+批 6 挖矿立卡全清偿）。

### 6.1 趋势类 trend.py（18 指标 / 29 列）

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
| dkx | dkx_20/dkx_ma10 | 20/10 | MID=(3C+L+O+H)/6；线性加权 20..1/210（2026-09-14 A股标配批） |
| hma | hma_16 | 16 | HMA=WMA(2×WMA(C,N/2)−WMA(C,N),⌊√N⌋)，低滞后（批2a） |
| zlema | zlema_21 | 21 | EMA(2C−REF(C,(N−1)/2))，误差修正抵消滞后（批2a） |
| kama | kama_10 | 10/2/30 | ER=|C−C_N|/Σ\|ΔC\|；SC² 逐 bar 递推，波动自适应（批2a） |
| vortex | vip_14/vim_14 | 14 | VI±=Σ\|H/L−L/H_prev\|/ΣTR，方向涡旋（批2a） |
| supertrend | supertrend_10/supertrend_dir | 10/3.0 | (H+L)/2±3×ATR final 带单向收紧，收盘穿越翻转（批2a） |
| mcginley | md_14 | 14/0.6 | MD=prev+(C−prev)/(k×N×(C/prev)⁴)，追踪速度自适应（批2b） |
| bbi | bbi | 3/6/12/24 | (MA3+MA6+MA12+MA24)/4 四周期合成（批6，通达信/同花顺标配） |
| tema | tema_10 | 10 | 3e1−3e2+e3 三重 EMA 消滞后（批9-1，talib 第100根起 rtol=1e-6 对照） |
| trima | trima_10 | 10 | SMA(SMA(C,5),6) 三角均线，TA-Lib 偶窗口径逐位一致（批9-1） |
| t3 | t3_10 | 10/0.7 | Tillson 六重 EMA 链 c1..c4 系数合成（批9-1） |
| mama | mama/fama | 0.5/0.05 | Ehlers homodyne 瞬时周期自适应，与 TA-Lib 逐位一致（批9-1） |
| vidya | vidya_14 | 14/9 | \|CMO9\|/100×2/(N+1) 加权递推（批9-1） |
| frama | frama_16 | 16 | 分形维数 D=ln(2(HL1+HL2)/HL3)/ln2 自适应 alpha（批9-1，Ehlers 2005） |
| jma | jma_7 | 7/50/2 | Jurik 开源移植（pandas-ta 经典口径）（批9-1） |
| avgprice | avgprice | 无 | (O+H+L+C)/4 价格变换（批9-1，talib 逐位一致） |
| medprice | medprice | 无 | (H+L)/2（批9-1） |
| typprice | typprice | 无 | (H+L+C)/3（批9-1） |
| wcprice | wcprice | 无 | (H+L+2C)/4 加权收盘，TA-Lib WCLPRICE 同义（批9-1） |
| inertia | inertia_20_14 | 20/14 | RVI 基 EMA 平滑惯性（批9-2，Ehlers，输入 HL2） |
| qstick | qstick_10 | 10 | SMA(C−O)（批9-2） |
| supersmoother | supersmoother_10 | 10 | Ehlers 正典二极低通（批9-3，TASC 2024-09 论文原生组件） |
| highpass | highpass_40 | 40 | HighPass3 三阶高通（批9-3，论文原生组件） |
| ptrend | ptrend_250_40/ptrend_roc | 250/40 | 谱带差分趋势线+TROC 确认（批9-3，TASC 2024-09 "Precision Trend Analysis" 正主） |

### 6.2 动量类 momentum.py（31 指标 / 50 列）

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
| bias | bias_6/12/24 | periods=[6,12,24] | (C−MA(C,N))/MA(C,N)×100（2026-09-14 A股标配批） |
| psy | psy_12/psy_ma6 | 12/6 | COUNT(C>REF(C,1),12)/12×100；首行无前值=NaN（A股标配批） |
| lwr | lwr_1/lwr_2 | 9/3/3 | 威廉 %R 双重 SMA 平滑，方向与 KDJ 相反（A股标配批） |
| dpo | dpo_20 | 20 | C−REF(MA(C,N),N/2+1)，去趋势循环摆动（批2a） |
| tsi | tsi | 25/13 | 双重 EMA 平滑动量比×100（批2b） |
| smi | smi/smi_signal | 10/3/3 | 对中点距离双重平滑，双顶背离更早（批2b） |
| fisher | fisher_9/fisher_sig9 | 9 | 递推费雪变换，拐点锐化（批2b） |
| kst | kst/kst_signal | 4 组 ROC 加权 | 1/2/3/4 权重多周期动量共振（批2b） |
| connorsrsi | crsi | 3/2/100 | RSI+连涨跌 RSI+收益百分位三合成（批2b） |
| qqe | qqe_14/qqe_rsi_ma | 14/5/27 | RSI 平滑+DAR 跟踪带递推（批2b） |
| stc | stc | 23/50/10/3 | MACD 双随机化 0-100 循环（批2b） |
| rvgi | rvgi_10/rvgi_sig | 10/4 | 开收盘力度 swma 比（批2b） |
| stoch | stoch_fastk/fastd/slowk/slowd | 5/3/3/3 | 经典随机本体（TA-Lib STOCH+STOCHF 合一；HH=LL 取 50，批6 立卡1） |
| aroon | aroon_up/aroon_down | 14 | 100×极值窗口位置/N（批6 立卡2） |
| aroonosc | aroonosc | 14 | AroonUp−AroonDown（批6 立卡2） |
| bop | bop | 16 | SMA((C−O)/(H−L))，值域 [-1,1]（批6 立卡2） |
| ppo | ppo | 12/26 | (EMA12−EMA26)/EMA26×100，MACD 百分比归一（批6 立卡2） |
| apo | apo | 12/26 | EMA12−EMA26（批6 立卡2） |
| dx | dx_14 | 14 | 100×\|+DI−−DI\|/(+DI+−DI)，ADX 原料（批6 立卡2） |
| brar | ar_26/br_26 | 26 | AR=Σ(H−O)/Σ(O−L)；BR=Σmax(0,H−Cp)/Σmax(0,Cp−L)（批6 立卡3，通达信） |
| cr | cr_26 | 26 | Σmax(0,H−MIDp)/Σmax(0,MIDp−L)×100（批6 立卡3，通达信） |
| rmi | rmi_14 | 14/5 | RSI 动量窗变体，Wilder 平滑（批9-2，TASC 1993） |
| pfe | pfe_10 | 10/5 | 极化分形效率 EMA 平滑（批9-2，TASC 1994） |
| fosc | fosc_14 | 14 | (C/TSF−1)×100 预测震荡（批9-2，复用 _rolling_linefit） |
| cti | cti_12 | 12 | close 对序数列滚动 Pearson r（批9-2，Ehlers） |
| vhf | vhf_28 | 28 | (maxC−minC)/Σ\|ΔC\|（批9-2，Bressert） |
| er | er_10 | 10 | \|C−C_N\|/Σ\|ΔC\| 效率比率，KAMA 内核独立立条（批9-2） |

### 6.3 波动类 volatility.py（15 指标 / 20 列）

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
| natr | natr_14 | period=14 | MA(TR/Close×100,N)，消量纲跨标的可比（批2a，TA-Lib） |
| trange | trange | 无 | TR 原始值，首行=H-L；ATR/NATR 底层原料（批2a，TA-Lib） |
| massi | massi_25 | 9/25 | Σ EMA9(H−L)/EMA9(EMA9)；>27 预警反转（批2b） |
| parkinson | parkinson_20 | 20 | √(Σln²(H/L)/(4ln2·N))×100，极差估计（批6 学术 RV 族，Parkinson 1980） |
| garman_klass | garman_klass_20 | 20 | OHLC 全用，效率≈7.4× close-to-close（批6，GK 1980） |
| rogers_satchell | rogers_satchell_20 | 20 | 漂移无关估计（批6，RS 1991） |
| yang_zhang | yang_zhang_20 | 20 | σ_o²+kσ_c²+(1−k)σ_rs²，处理隔夜跳空+漂移——A 股高开低开适配（批6，YZ 2000） |
| chop | chop_14 | 14 | 100×log10(ΣTR/(maxH−minL))/log10(N) 盘整指数（批9-2） |
| cvi | cvi | 3/10 | Chaikin 波动率 EMA3(H−L) 十日变动率（批9-2） |
| ulcer | ulcer_14 | 14 | 回撤深度均方根（批9-2，Martin） |

### 6.4 量能类 volume.py（14 指标 / 15 列）

| indicator_id | 输出列 | 默认参数 | 公式要点 |
|---|---|---|---|
| obv | obv | 无 | sign(ΔC)×V 累积 |
| mfi | mfi_14 | period=14 | TP=(H+L+C)/3；100−100/(1+正MF/负MF) |
| vwap | vwap | 无（可传 period 滚动） | 累积 SUM(C×V)/SUM(V) |
| vr | vr_26 | period=26 | 100×(2×涨量+平量)/(2×跌量+平量)（通达信平盘计两侧） |
| ad | ad | 无 | cumsum(CLV×V) |
| pvt | pvt | 无 | cumsum(V×pct_change) |
| wvad | wvad_24 | period=24 | SUM((C−O)/(H−L)×V, N) |
| vwma | vwma_20 | 20 | 滚动 Σ(C×V)/ΣV（区别累积 vwap，批2b） |
| adosc | adosc | 3/10 | EMA3(AD)−EMA10(AD)（批2b，TA-Lib） |
| eom | eom_14 | 14 | 中价差/箱体量比 SMA（批2b） |
| kvo | kvo/kvo_signal | 34/55/13 | Klinger VF 双 EMA 震荡（批2b） |
| nvi | nvi | 无 | 缩量日累乘收益，聪明钱视角（批2b） |
| pvi | pvi | 无 | 放量日累乘收益（批2b） |
| wad | wad | 无 | 威廉累积/派发线 cumsum(TAD)（批9-2，Tulip 口径） |
| vo | vo | 5/20 | 成交量快慢 MA 震荡（批9-2） |
| marketfi | marketfi | 无 | (H−L)/V 市场促进指数（批9-2，Bill Williams） |

### 6.5 反转类 reversal.py（5 指标 / 5 列）

| indicator_id | 输出列 | 默认参数 | 公式要点 |
|---|---|---|---|
| candlestick_pattern | candle_pattern | patterns="all" | **已退役（裁定#233，方案B）**：薄视图 v2.0 存续数小时后被方案B取代（Owner 倾向B+零下游消费清查实证）——类删除、INSERT_COLUMNS 停产该列（新行 NULL）、物理列保留季度后 DROP；K线形态消费统一走图形域 candlestick_scanner/pattern_event 体系（77 条+胜率统计） |
| rsi_divergence | rsi_divergence | rsi=12, lookback=20 | 价升 RSI 降→1；价跌 RSI 升→−1（简化趋势对比） |
| macd_divergence | macd_divergence | lookback=20, 12/26/9 | 价格 vs MACD HIST 趋势对比 |
| boll_breakout | boll_breakout | 20/2 | C>上轨→1；C<下轨→−1 |
| vol_price_divergence | vol_price_div | lookback=10 | 价升量缩→1；价跌量增→−1 |

### 6.6 统计族 statistics.py（4 指标 / 5 列，2026-09-14 统计族批新建）

对齐 TA-Lib Statistic Functions 组（通达信无对应函数）；MOD-L02-028。

| indicator_id | 输出列 | 默认参数 | 公式要点 |
|---|---|---|---|
| correl | correl_30 | period=30 | r=Cov(x,y)/(σx·σy)，x=close y=volume；量价背离/共振统计基线 |
| beta | beta_30 | period=30 | beta=Cov(x,y)/Var(y)，x=close y=volume |
| linearreg | linearreg_14/tsf_14 | period=14 | 滚动拟合 y=a+bx：LINEARREG=a+b(N−1)；TSF=a+bN（一步外推）；矩法向量化（Σxy 恒等式拆解），不用 rolling.apply |
| rollvar | var_20 | period=20 | 滚动总体方差 ddof=0（与 BOLL 中轨 std 口径一致） |
| linearreg_angle | linearreg_angle_14 | period=14 | θ=degrees(atan(slope))，x=0..N−1 滚动 OLS（批9-1，talib 对照 1e-12 级） |
| slope | slope_14 | period=14 | 矩法闭式 b=(NΣxy−ΣxΣy)/(NΣx²−(Σx)²)（批9-1） |
| intercept | intercept_14 | period=14 | a=(Σy−bΣx)/N（批9-1） |
| stderr | stderr_14 | period=14 | sqrt(SSR/(N−2))，除数经独立 OLS 对照实测钉死（批9-1） |
| zscore | zscore_20 | period=20 | 滚动 Z 分数，ddof=0 与 BOLL 口径一致（批9-2） |

### 6.7 复合类 trend.py 内 Ichimoku（1 指标 / 5 列，2026-09-14 批 3 补实现）

IND-COMP-001 candidate→active；类别 composite，代码在 trend.py（registry 既定 code_path）。

| indicator_id | 输出列 | 默认参数 | 公式要点 |
|---|---|---|---|
| ichimoku | tenkan_sen/kijun_sen/senkou_span_a/senkou_span_b/chikou_span | 9/26/52/位移26 | 转折/基准=(HH+LL)/2；先行 A/B 存**显示位移后**位置（值来自 26 根前，PIT 无前视）；迟行存计算时点收盘（后移 26 是显示语义，存储不前视） |

### 6.8 循环族 cycle.py（5 指标 / 7 列，2026-09-14 批 3 新建，MOD-L02-029）

对齐 TA-Lib HT 家族理论源（Ehlers, Rocket Science for Traders），实现采用**相位累积**口径（homodyne 移植实证存在带通自锁：初始周期钳位使自适应带通自锁于 6，纯正弦/随机游走全收敛 6——故弃用）。

| indicator_id | 输出列 | 默认参数 | 公式要点 |
|---|---|---|---|
| ht_dcperiod | ht_dcperiod | 无 | 瞬时周期=2π/Δφ（unwrap+限幅），EMA 平滑，钳位 [6,50]；预热 63 |
| ht_dcphase | ht_dcphase | 无 | 累积相位 mod 360 |
| ht_phasor | ht_ip/ht_qp | 无 | 同相=延迟 3 根平滑价；正交=4-tap Hilbert 滤波 |
| ht_sine | ht_sine/ht_leadsine | 无 | sin(累积相位) 与 sin(+45°)；交叉标记周期转折 |
| ht_trendmode | ht_trendmode | 无 | 主导周期窗口内正弦交叉计数：少=趋势 1/多=循环 0 |
| ebsw | ebsw_40 | 40/10 | Ehlers 带通正弦波 [-100,100]（批9-2，pandas-ta-classic 移植） |
| continuation | continuation_40 | 40(γ0.8/o8) | 延续指数两态 ±1：Laguerre+UltimateSmoother 差值归一逆费雪（批9-4，TASC 2025-09 官网 PDF） |
| gpred | gp_sig/gp_pred | 18/40/2 | Griffiths LMS 自适应线性预测器，2 步外推（批9-4，TASC 2025-01 官网 PDF；正弦领先性 corr 0.95） |

### 6.9 与 factor_registry 的正交边界

技术指标（technical_indicator_registry / 本目录）与因子（factor_registry）正交：**技术指标=OHLCV 的确定性变换，无 alpha 断言；因子=对未来收益有假设的截面/时序信号，需过 ABS001 门禁**。技术指标可作为因子输入（如 boll_pctb 进动量因子），但指标本身不进 factor_registry、不做 IC 评估。why 分开：指标是"数据"（一次回算全市场复用），因子是"假设"（需治理流水线生老病死）——混在一起会让因子注册表被无假设列稀释。

## 7. 开放问题

1. **调度未闭环（P0）** → **已闭环（2026-08-31 终审批实证核销）**：tasks.yaml 已挂 technical_indicator_incremental（L1877）/ technical_indicator_full_refresh（L1892）两条目，scheduler.py L1227 `source=="internal"` 分支已落地（64 号 Q18 施工批，2026-08-28）。Provider→调度→回算链路全通。
2. **REG-IND-001 YAML 注册表未施工** → **已闭环（2026-08-31 终审批实证核销）**：`docs/01_policies_and_standards/_registry/catalogs/technical_indicator_registry.yaml` 已在位（registry_id=REG-IND-001，条目真源），本文按原裁定降级为 why 层。
3. **命名陷阱**：tasks.yaml 的 `stock_indicator_full_refresh` 实为 AKShare 估值指标写 stock_indicator 表，与本表无关——后续调度挂接时防止误挂。
4. **公式简化项**：rsi/macd_divergence 为简化趋势对比（非峰谷检测），精度需求出现时再升级。
5. **00_index 同步（越界登记）** → **已闭环（2026-08-31 终审批实证核销）**：00_index 现行描述已为"5大类指标规范"，分类口径一致，无需再同步。
6. **日/周/月线历史深度缺口（2026-09-14 探针发现）**：daily/weekly/monthly 指标数据起点=2026-08（调度闭环日），仅 ~1 个月；而 30/60/120min 有 5 年、15min 2 年、5min 1 年历史。三级时间框架栈（§5）的交易层/趋势层以日/周/月为主战场，长历史缺失直接影响回测消费。待办：一次性 full_refresh 回填日/周/月（或裁定滚动窗口口径），挂下一施工批。 → **已闭环（2026-09-14 回填六轮）**：回填器 scripts/data/backfill_technical_indicator_dwm.py 补齐 d(2021-01)/w/m(2019-01) 历史；daily 批 3-6 新列由六轮重跑覆盖；CH Code 241 内存超限中断由 local_fallback 兜底（scheduler 自动回灌）。
6a. **消费端接线（批 7 立项）** → **已闭环（53a00cdfb7）**：indicator_reader.py PIT 读取 API （as_of 硬拒/列白名单/FINAL 去重/预热 NaN 不填充）+ 消费样板 indicator_consumption_demo.py （B1 ATR 止损带/B2 均值回归因子，真实 CH 端到端）+ REG-IND-001 四条目 used_by_factors 锚点回填；后续=更多因子照 demo 模式扩展。

## 8. 修订记录

| 日期 | 版本 | 改动 | 理由 |
|---|---|---|---|
| 2026-09-20 | 1.10.0 | 批9-4 tilib 清欠班波5：M-L6 登记卡全清偿 +CONTINUATION/GPRED（循环 6→8）；全表 135→137 在产/198→200 列；公式源=mesasoftware.com 官网论文 PDF（Continuation Index TASC 2025-09 / Linear Predictive Filters TASC 2025-01），EasyLanguage 逐行移植；GPRED 正弦领先性实测 corr 0.9462 | Owner 追加令立卡未施工的你能施工吗→开工 |
| 2026-09-20 | 1.9.0 | 批9-3 tilib 清欠班波3：M-L6 学术滤波器族 +SUPERSMOOTHER/HIGHPASS/PTREND（趋势 34→37）；全表 132→135 在产/194→198 列；挖矿报告=docs/_working/archive/2026-09/tilib_clearance/tilib_clear_a3_mining_report.md（TASC 2024-09 Precision Trend 正主施工；Griffiths 预测器/Continuation Index 立卡登记未施工，公式源未镜像） | 分包A 通宵总令波3（M-L6 复挖，批4 R5 受阻项清偿） |
| 2026-09-20 | 1.8.0 | 批9-2 tilib 清欠班波2：M-L5 社区热门族 +16 指标/16 列（CHOP/CVI/ULCER 波动+3、EBSW 循环+1、INERTIA/QSTICK 趋势+2、RMI/PFE/FOSC/CTI/VHF/ER 动量+6、WAD/VO/MARKETFI 量能+3、ZSCORE 统计+1）；全表 116→132 在产/178→194 列；同批治愈 cycle.py 行1 stale 蓝图号 001→029（注册表 5 条 cycle 条目同步）；PSL=PSY、MSW=ht_sine 同义不重复立条 | 分包A 通宵总令波2（M-L5 清欠 18→16 实作） |
| 2026-09-20 | 1.7.0 | 批9-1 tilib 清欠班波1：+TEMA/TRIMA/T3/MAMA+FAMA/VIDYA/FRAMA/JMA（趋势 21→32）+AVGPRICE/MEDPRICE/TYPPRICE/WCPRICE 价格变换 +LINEARREG_ANGLE/SLOPE/INTERCEPT/STDERR（统计 4→8）；全表 101→116 在产指标/162→178 列；黄金对照=本地 talib（MAMA/FAMA 逐位 0.0 偏差，回归四件 1e-12 级）；M-L3"LINEARREG_BAR"与既有 linearreg 同义不重复立条（清欠班裁①） | 分包A 通宵总令波1（M-L1/M-L2/M-L3 清欠 16→15 实作，缺口波3 学术挖矿补） |
| 2026-08-10 | 0.1.0 | 初稿骨架 | 技术指标目录文档。**注意**：本文件曾因未 git commit 丢失，后从代码引用和 architecture_issue_registry 描述重建骨架 |
| 2026-08-12 | 1.0.0 | 骨架→active：§6 回填 40 指标/58 列全表（5 大类公式/参数/输出列）；修正 55→58 口径；§6 增"40 指标不裁剪"裁定；补 §6.6 与 factor_registry 正交边界；新增 §7 开放问题（调度未闭环/REG-IND-001 待施工/00_index 同步） | 回填已施工代码 why；口径以测试契约为准；缺口入开放问题不擅自施工 |
| 2026-08-15 | 1.0.1 | 第二轮循环压缩：可压缩点收敛=0（AI-DC2-08） | 清单/公式/裁定无冗余，通读+自审零发现，不为压而压 |
| 2026-09-15 | 1.6.0 | 批 8 M-L4 经典族（数据先行放量批，Owner"全部开工"指令）：+ALLIGATOR/GMMA/GANN_HILO（趋势 18→21）+AC/FRACTALS/ELDER/COPPOCK/SQUEEZE/WAVETREND（动量 31→37）+FORCE_INDEX（量能 13→14）；全表 91→101 指标/134→162 列（退役后口径）；candle_pattern 退役终态一并收录（§6.5 v1.5.2） | M-L4 矿脉施工；筹码族前置数据批 stock_daily_basic 另行立项 |
| 2026-09-14 | 1.5.2 | 裁定#233 落地（图形会话执行）：candle_pattern 列退役停产，IND-REV-001 deprecated，测试/INSERT_COLUMNS 同批；指标域 91 指标/134 在产列+1 退役列 | Owner 倾向方案B；零下游消费清查通过 |
| 2026-09-14 | 1.5.1 | IND-REV-001 薄视图化（裁定①方案A，Owner 拍板）：CandlestickPattern.compute 转调图形域 scan_candles，6 编码映射回旧 candle_pattern 列语义（覆盖序复刻），talib 缺失降级全 0 不炸生产批；自研 5 形态灶台停用 | 图形会话 CDL 新家落地（a1b5c7f5/ac52af8），两店做一道菜根治 |
| 2026-09-14 | 1.5.0 | 批 6（挖矿立卡清偿）：+RV 波动率族 4（波动 11→15）+BBI（趋势 17→18）+STOCH 本体/AROON/AROONOSC/BOP/PPO/APO/DX/BRAR/CR（动量 22→31）；全表 78→92 指标/116→135 列；施工方案=docs/_working/2026-09-14-tilib-batch6-plan.md（方案级病菌寻路 5 轮）；§7 消费端接线批立项 | Owner"施工批 6"指令；批 4/5 挖矿立卡全清偿 |
| 2026-09-14 | 1.4.0 | 批 3：IND-COMP-001 Ichimoku 补实现（candidate→active，5 列，PIT 存储口径裁定入档）+ 循环族 HT 系 5 指标（新建 cycle.py MOD-L02-029，Ehlers 相位累积口径）；全表 72→78 指标/104→116 列；§6.7/6.8 新增、正交边界→6.9；homodyne 自锁实证弃用记录入档 | 缺口清单批 3；Owner 批 3 精选指令 |
| 2026-09-14 | 1.3.0 | 主流热门批 2b 收官：+TSI/SMI/FISHER/KST/CONNORSRSI/QQE/STC/RVGI（动量 14→22）+MCGINLEY（趋势 16→17）+MASSI（波动 10→11）+VWMA/ADOSC/EOM/KVO/NVI/PVI（量能 7→13）；全表 56→72 指标/82→104 列 | 缺口清单批 2b（TA-Lib/pandas-ta 主流热门全谱清偿完毕）；TA-Lib 波动组补全；量能族 TA-Lib 全覆盖 |
| 2026-09-14 | 1.2.0 | 主流热门批 2a：+HMA/ZLEMA/KAMA/VORTEX/SUPERTREND（趋势 11→16）+DPO（动量 13→14）+NATR/TRANGE（波动 8→10）；全表 48→56 指标/72→82 列 | 缺口清单批 2a（TA-Lib 波动组补全+低滞后/自适应均线族）；同批附带 d/w/m 历史回填器 scripts/data/backfill_technical_indicator_dwm.py 落盘 |
| 2026-09-14 | 1.1.0 | A股标配批+统计族批：+BIAS/PSY/LWR（动量 10→13）+DKX（趋势 10→11）+统计族 4 指标（新建 statistics.py MOD-L02-028，§6.6）；全表 40→48 指标/58→72 列；原 §6.6 正交边界→§6.7；§7 增开放问题⑥日/周/月历史深度缺口（探针实锤） | 全网对照缺口清单（TA-Lib 158/pandas-ta 130+ 基线）第一二批落地；Owner 两库分工裁定后本会话线开工 |

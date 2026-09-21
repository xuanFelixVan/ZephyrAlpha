# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market.market_technical_indicator
# [DOMAIN] D_DATA
# [DEPENDENCIES] schemas.categories.kline.market_kline_daily (输入 OHLCV)
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.internal_compute_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] technical_indicator 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [TTL] permanent
"""technical_indicator 表 DDL-as-Code（category_id: market_technical_indicator, calc_mode: preload）。

本文件是 c1_market.technical_indicator 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_schema.py 执行。

架构议题：#ARCH-DATA-TI-001（技术指标计算模块新建，骨架先行 2026-08-10）
设计文档：docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/16_technical_indicator_catalog.md

命名裁定：
    表名 technical_indicator（区别于 stock_valuation 表，后者实存估值指标 PE/PB）
    category_id market_technical_indicator（business_data_categories.yaml SSoT）

引擎选型：
    ReplacingMergeTree（覆盖式更新——同 symbol+period+trade_time 多次计算取最新）
    PARTITION BY (period, toYYYYMM(trade_date))（period + 月份双键分区，分区裁剪提速跨周期查询）
    ORDER BY (symbol, period, trade_time)（按标的+周期+精确时间戳排序，支持日内多根 K 线去重）

多周期架构（Phase 2，2026-08-10 落地，方案 A 已裁定）：
    period 列 LowCardinality(String) DEFAULT 'daily'，覆盖 9 个周期：
      1min/5min/15min/30min/60min/120min/daily/weekly/monthly
    trade_time 列 DateTime64(3,'Asia/Shanghai') DEFAULT toDateTime(trade_date)：
      - 日/周/月线：trade_time = trade_date 当天 00:00:00（仅 trade_date 有意义）
      - 分钟/120min 线：trade_time = K 线起始时间戳（日内多根 K 线靠 trade_time 区分）
    设计缺口修复：施工图 §3.3 原 DDL 仅有 trade_date Date + ORDER BY (symbol,period,trade_date)，
      无法区分日内多根 K 线（如 120min 同日 2 根会 ReplacingMergeTree 误去重）。
      补 trade_time 列后 ORDER BY (symbol, period, trade_time) 精确去重，与 K 线表对齐。

数据来源：
    data_source = 'internal'（纯本地 pandas/numpy 计算，非外部数据源下载）
    输入：c1_market.kline_{period} 的 OHLCV 数据（120min 由 kline_60min 两根聚合）
    输出：210 个技术指标列（Nullable(Float64)），覆盖 9 类 140 个在产指标（2026-09-21 批10 筹码族：
    +CYQ 筹码分布/SCR 筹码集中度/CYC 成本均线 3 指标 9 列，指标输入首次引入换手率 stock_daily_basic，
    仅 daily 周期计算；批9 tilib 清欠班波1-波5 在此之前共 +36 指标/39 列）

列设计说明：
    所有指标列均为 Nullable(Float64)——预热期无值时为 NULL（不前向填充，避免前视偏差）
    反转类信号列（如 rsi_divergence）也用 Float64（0.0=无信号, 1.0=正信号, -1.0=负信号）
"""

from __future__ import annotations

# category_id: market_technical_indicator
# calc_mode: preload（盘后预计算入表，盘中实时调用 compute() 不入表）

MARKET_TECHNICAL_INDICATOR_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.technical_indicator
(
    trade_date   Date           COMMENT '交易日期',
    trade_time   DateTime64(3, 'Asia/Shanghai') DEFAULT toDateTime(trade_date) COMMENT 'K线精确时间戳(日/周/月=当天00:00, 分钟/120min=K线起始时间)',
    symbol       String         COMMENT '证券代码',
    period       LowCardinality(String) DEFAULT 'daily' COMMENT '周期(1min/5min/15min/30min/60min/120min/daily/weekly/monthly)',

    ma_5         Nullable(Float64)  COMMENT '5日简单移动平均',
    ma_10        Nullable(Float64)  COMMENT '10日简单移动平均',
    ma_20        Nullable(Float64)  COMMENT '20日简单移动平均',
    ma_60        Nullable(Float64)  COMMENT '60日简单移动平均',
    ema_12       Nullable(Float64)  COMMENT '12日指数移动平均',
    ema_26       Nullable(Float64)  COMMENT '26日指数移动平均',
    wma_10       Nullable(Float64)  COMMENT '10日加权移动平均',
    dema_12      Nullable(Float64)  COMMENT '12日双指数移动平均',
    macd_dif     Nullable(Float64)  COMMENT 'MACD DIF线(EMA12-EMA26)',
    macd_dea     Nullable(Float64)  COMMENT 'MACD DEA线(EMA9(DIF))',
    macd_hist    Nullable(Float64)  COMMENT 'MACD 柱状图(2×(DIF-DEA))',
    adx_14       Nullable(Float64)  COMMENT '14日平均趋向指数',
    pdi_14       Nullable(Float64)  COMMENT '14日上升趋向指标(+DI)',
    mdi_14       Nullable(Float64)  COMMENT '14日下降趋向指标(-DI)',
    cci_14       Nullable(Float64)  COMMENT '14日顺势指标',
    sar          Nullable(Float64)  COMMENT '抛物线指标(Stop and Reverse)',
    trix         Nullable(Float64)  COMMENT '三重指数平滑平均',
    trma         Nullable(Float64)  COMMENT 'TRIX的移动平均',
    dkx_20       Nullable(Float64)  COMMENT '20日多空线',
    dkx_ma10     Nullable(Float64)  COMMENT '多空线10日移动平均',
    hma_16       Nullable(Float64)  COMMENT '16日Hull均线',
    zlema_21     Nullable(Float64)  COMMENT '21日零滞后EMA',
    kama_10      Nullable(Float64)  COMMENT '10日Kaufman自适应均线',
    vip_14       Nullable(Float64)  COMMENT '14日涡旋指标VI+',
    vim_14       Nullable(Float64)  COMMENT '14日涡旋指标VI-',
    supertrend_10  Nullable(Float64)  COMMENT '超级趋势线(10,3)',
    supertrend_dir Nullable(Float64)  COMMENT '超级趋势方向(1=多,-1=空)',
    md_14        Nullable(Float64)  COMMENT '14日McGinley动态均线',
    tenkan_sen   Nullable(Float64)  COMMENT '一目均衡转折线(9)',
    kijun_sen    Nullable(Float64)  COMMENT '一目均衡基准线(26)',
    senkou_span_a Nullable(Float64)  COMMENT '一目先行跨度A(显示位移26,PIT安全)',
    senkou_span_b Nullable(Float64)  COMMENT '一目先行跨度B(52,显示位移26)',
    chikou_span  Nullable(Float64)  COMMENT '一目迟行跨度(计算时点收盘值)',
    bbi          Nullable(Float64)  COMMENT '多空指数(MA3/6/12/24均值)',
    alligator_jaw   Nullable(Float64)  COMMENT '鳄鱼线颚(SMMA13,前移8)',
    alligator_teeth Nullable(Float64)  COMMENT '鳄鱼线齿(SMMA8,前移5)',
    alligator_lips  Nullable(Float64)  COMMENT '鳄鱼线唇(SMMA5,前移3)',
    gmma_s3    Nullable(Float64)  COMMENT '顾比短期EMA3',
    gmma_s5    Nullable(Float64)  COMMENT '顾比短期EMA5',
    gmma_s8    Nullable(Float64)  COMMENT '顾比短期EMA8',
    gmma_s10   Nullable(Float64)  COMMENT '顾比短期EMA10',
    gmma_s12   Nullable(Float64)  COMMENT '顾比短期EMA12',
    gmma_s15   Nullable(Float64)  COMMENT '顾比短期EMA15',
    gmma_l30   Nullable(Float64)  COMMENT '顾比长期EMA30',
    gmma_l35   Nullable(Float64)  COMMENT '顾比长期EMA35',
    gmma_l40   Nullable(Float64)  COMMENT '顾比长期EMA40',
    gmma_l45   Nullable(Float64)  COMMENT '顾比长期EMA45',
    gmma_l50   Nullable(Float64)  COMMENT '顾比长期EMA50',
    gmma_l60   Nullable(Float64)  COMMENT '顾比长期EMA60',
    gann_hilo     Nullable(Float64)  COMMENT 'Gann HiLo(中价SMA10)',
    gann_hilo_dir Nullable(Float64)  COMMENT 'Gann HiLo方向(1多-1空)',
    tema_10      Nullable(Float64)  COMMENT '10日三重指数均线(3e1-3e2+e3)',
    trima_10     Nullable(Float64)  COMMENT '10日三角均线(SMA5×SMA6级联)',
    t3_10        Nullable(Float64)  COMMENT '10日T3均线(v=0.7)',
    vidya_14     Nullable(Float64)  COMMENT '14日可变指数动态均线(CMO9)',
    frama_16     Nullable(Float64)  COMMENT '16日分形自适应均线',
    mama         Nullable(Float64)  COMMENT 'MESA自适应均线(0.5/0.05)',
    fama         Nullable(Float64)  COMMENT 'MESA慢速自适应均线(半alpha)',
    jma_7        Nullable(Float64)  COMMENT '7日Jurik自适应均线',
    avgprice     Nullable(Float64)  COMMENT '四价均价(O+H+L+C)/4',
    medprice     Nullable(Float64)  COMMENT '中价(H+L)/2',
    typprice     Nullable(Float64)  COMMENT '典型价格(H+L+C)/3',
    wcprice      Nullable(Float64)  COMMENT '加权收盘(H+L+2C)/4',
    inertia_20_14 Nullable(Float64)  COMMENT 'Ehlers惯性指标(RVI基,20/14)',
    qstick_10    Nullable(Float64)  COMMENT '10日Qstick(C-O的SMA)',
    supersmoother_10 Nullable(Float64)  COMMENT '10日SuperSmoother二极低通',
    highpass_40  Nullable(Float64)  COMMENT '40日HighPass3三阶高通',
    ptrend_250_40 Nullable(Float64)  COMMENT 'Ehlers精调趋势线(HP3 250/40谱带差分)',
    ptrend_roc   Nullable(Float64)  COMMENT '精调趋势确认项(TROC)',

    kdj_k        Nullable(Float64)  COMMENT 'KDJ K线',
    kdj_d        Nullable(Float64)  COMMENT 'KDJ D线',
    kdj_j        Nullable(Float64)  COMMENT 'KDJ J线(3K-2D)',
    rsi_6        Nullable(Float64)  COMMENT '6日相对强弱指标',
    rsi_12       Nullable(Float64)  COMMENT '12日相对强弱指标',
    rsi_24       Nullable(Float64)  COMMENT '24日相对强弱指标',
    wr_14        Nullable(Float64)  COMMENT '14日威廉指标',
    roc_12       Nullable(Float64)  COMMENT '12日变动率',
    mtm_12       Nullable(Float64)  COMMENT '12日动量指标',
    mtmma_12     Nullable(Float64)  COMMENT '12日动量指标的移动平均',
    cmf_20       Nullable(Float64)  COMMENT '20日蔡金资金流',
    uos          Nullable(Float64)  COMMENT '终极指标(Ultimate Oscillator)',
    ao           Nullable(Float64)  COMMENT '震荡指标(Awesome Oscillator)',
    cmo_14       Nullable(Float64)  COMMENT '14日钱德动量摆动',
    stochrsi     Nullable(Float64)  COMMENT '随机RSI',
    bias_6       Nullable(Float64)  COMMENT '6日乖离率',
    bias_12      Nullable(Float64)  COMMENT '12日乖离率',
    bias_24      Nullable(Float64)  COMMENT '24日乖离率',
    psy_12       Nullable(Float64)  COMMENT '12日心理线',
    psy_ma6      Nullable(Float64)  COMMENT '心理线6日移动平均',
    lwr_1        Nullable(Float64)  COMMENT '慢速威廉LWR1(9,3,3)',
    lwr_2        Nullable(Float64)  COMMENT '慢速威廉LWR2(9,3,3)',
    dpo_20       Nullable(Float64)  COMMENT '20日区间震荡',
    tsi          Nullable(Float64)  COMMENT '真实强度指数(25/13)',
    smi          Nullable(Float64)  COMMENT '随机动量指数(10,3,3)',
    smi_signal   Nullable(Float64)  COMMENT 'SMI信号线(EMA3)',
    fisher_9     Nullable(Float64)  COMMENT '费雪变换(9)',
    fisher_sig9  Nullable(Float64)  COMMENT '费雪变换信号(前值)',
    kst          Nullable(Float64)  COMMENT '确知量KST',
    kst_signal   Nullable(Float64)  COMMENT 'KST信号线(SMA9)',
    crsi         Nullable(Float64)  COMMENT 'ConnorsRSI(3,2,100)',
    qqe_14       Nullable(Float64)  COMMENT 'QQE线(14,5,27)',
    qqe_rsi_ma   Nullable(Float64)  COMMENT 'QQE平滑RSI线(EMA5)',
    stc          Nullable(Float64)  COMMENT 'Schaff趋势周期(23,50,10,3)',
    rvgi_10      Nullable(Float64)  COMMENT '相对活力指数(10)',
    rvgi_sig     Nullable(Float64)  COMMENT 'RVGI信号线(SMA4)',
    stoch_fastk  Nullable(Float64)  COMMENT '随机振荡FastK(5)',
    stoch_fastd  Nullable(Float64)  COMMENT '随机振荡FastD(SMA3)',
    stoch_slowk  Nullable(Float64)  COMMENT '随机振荡SlowK(SMA3)',
    stoch_slowd  Nullable(Float64)  COMMENT '随机振荡SlowD(SMA3)',
    aroon_up     Nullable(Float64)  COMMENT 'Aroon上(14)',
    aroon_down   Nullable(Float64)  COMMENT 'Aroon下(14)',
    aroonosc     Nullable(Float64)  COMMENT 'Aroon震荡器(14)',
    bop          Nullable(Float64)  COMMENT '力量平衡(SMA16)',
    ppo          Nullable(Float64)  COMMENT '百分比价格振荡器(12/26)',
    apo          Nullable(Float64)  COMMENT '绝对价格振荡器(12/26)',
    dx_14        Nullable(Float64)  COMMENT '动向指数DX(14)',
    ar_26        Nullable(Float64)  COMMENT '人气指标AR(26)',
    br_26        Nullable(Float64)  COMMENT '意愿指标BR(26)',
    cr_26        Nullable(Float64)  COMMENT '能量指标CR(26)',
    ac           Nullable(Float64)  COMMENT '加速振荡器AO−SMA5(AO)',
    fractal_high Nullable(Float64)  COMMENT '威廉上分形价(5bar)',
    fractal_low  Nullable(Float64)  COMMENT '威廉下分形价(5bar)',
    bull_power_13 Nullable(Float64)  COMMENT 'Elder牛力(H−EMA13)',
    bear_power_13 Nullable(Float64)  COMMENT 'Elder熊力(L−EMA13)',
    coppock      Nullable(Float64)  COMMENT '考派尔曲线(WMA10[ROC14+ROC11])',
    squeeze_on   Nullable(Float64)  COMMENT '挤压开关(BB嵌入KC=1)',
    squeeze_mom  Nullable(Float64)  COMMENT '挤压动量(线性回归动量)',
    wt1          Nullable(Float64)  COMMENT 'WaveTrend主线',
    wt2          Nullable(Float64)  COMMENT 'WaveTrend信号线(SMA4)',
    rmi_14       Nullable(Float64)  COMMENT '14日相对动量指数(动量窗5)',
    pfe_10       Nullable(Float64)  COMMENT '10日极化分形效率',
    fosc_14      Nullable(Float64)  COMMENT '14窗预测震荡',
    cti_12       Nullable(Float64)  COMMENT '12日相关趋势指标',
    vhf_28       Nullable(Float64)  COMMENT '28日纵横过滤',
    er_10        Nullable(Float64)  COMMENT '10日效率比率',
    ht_dcperiod  Nullable(Float64)  COMMENT '希尔伯特主导周期(6-50)',
    ht_dcphase   Nullable(Float64)  COMMENT '主导周期相位(度)',
    ht_ip        Nullable(Float64)  COMMENT '同相分量in_phase',
    ht_qp        Nullable(Float64)  COMMENT '正交分量quadrature',
    ht_sine      Nullable(Float64)  COMMENT '主正弦波',
    ht_leadsine  Nullable(Float64)  COMMENT '超前45度正弦波',
    ht_trendmode Nullable(Float64)  COMMENT '趋势/循环模式(1趋势,0循环)',
    ebsw_40      Nullable(Float64)  COMMENT '40日Even Better Sine Wave',
    continuation_40 Nullable(Float64)  COMMENT '40日延续指数(Laguerre+逆费雪,±1)',
    gp_sig       Nullable(Float64)  COMMENT 'Griffiths带限归一信号',
    gp_pred      Nullable(Float64)  COMMENT 'Griffiths线性预测(2步前推)',
    parkinson_20      Nullable(Float64)  COMMENT 'Parkinson波动率(高低极差)',
    garman_klass_20   Nullable(Float64)  COMMENT 'Garman-Klass波动率(OHLC)',
    rogers_satchell_20 Nullable(Float64)  COMMENT 'Rogers-Satchell波动率(漂移无关)',
    yang_zhang_20     Nullable(Float64)  COMMENT 'Yang-Zhang波动率(隔夜跳空+漂移)',
    chop_14      Nullable(Float64)  COMMENT '14日盘整指数(0-100)',
    cvi          Nullable(Float64)  COMMENT 'Chaikin波动率(3/10)',
    ulcer_14     Nullable(Float64)  COMMENT '14日溃疡指数',

    correl_30      Nullable(Float64)  COMMENT '30日close×volume滚动相关系数',
    beta_30        Nullable(Float64)  COMMENT '30日close对volume滚动beta系数',
    linearreg_14   Nullable(Float64)  COMMENT '14日线性回归线(当前拟合值)',
    tsf_14         Nullable(Float64)  COMMENT '14日时间序列预测(一步外推)',
    var_20         Nullable(Float64)  COMMENT '20日滚动总体方差(ddof=0)',
    linearreg_angle_14 Nullable(Float64)  COMMENT '14窗线性回归角度(度)',
    slope_14     Nullable(Float64)  COMMENT '14窗线性回归斜率',
    intercept_14 Nullable(Float64)  COMMENT '14窗线性回归截距',
    stderr_14    Nullable(Float64)  COMMENT '14窗回归残差标准差(除数N-2)',
    zscore_20    Nullable(Float64)  COMMENT '20日滚动Z分数',

    atr_14       Nullable(Float64)  COMMENT '14日真实波幅',
    natr_14      Nullable(Float64)  COMMENT '14日归一化真实波幅(TR/Close×100)',
    trange       Nullable(Float64)  COMMENT '真实波幅原始值(首行=H-L)',
    massi_25     Nullable(Float64)  COMMENT '质量指数(9,25)',
    boll_upper   Nullable(Float64)  COMMENT '布林带上轨',
    boll_middle  Nullable(Float64)  COMMENT '布林带中轨(MA20)',
    boll_lower   Nullable(Float64)  COMMENT '布林带下轨',
    kc_upper     Nullable(Float64)  COMMENT '肯特纳通道上轨',
    kc_middle    Nullable(Float64)  COMMENT '肯特纳通道中轨(EMA20)',
    kc_lower     Nullable(Float64)  COMMENT '肯特纳通道下轨',
    dc_upper     Nullable(Float64)  COMMENT '唐奇安通道上轨',
    dc_lower     Nullable(Float64)  COMMENT '唐奇安通道下轨',
    stddev_20    Nullable(Float64)  COMMENT '20日收盘价标准差',
    boll_bw      Nullable(Float64)  COMMENT '布林带宽度(BandWidth)',
    boll_pctb    Nullable(Float64)  COMMENT '布林带%B',
    histvol_20   Nullable(Float64)  COMMENT '20日历史波动率(年化)',

    obv          Nullable(Float64)  COMMENT '能量潮(On Balance Volume)',
    mfi_14       Nullable(Float64)  COMMENT '14日资金流量指标',
    vwap         Nullable(Float64)  COMMENT '成交量加权均价',
    vr_26        Nullable(Float64)  COMMENT '26日容量比率',
    ad           Nullable(Float64)  COMMENT '累积/派发线',
    pvt          Nullable(Float64)  COMMENT '价量趋势',
    wvad_24      Nullable(Float64)  COMMENT '24日威廉变异离散量',
    vwma_20      Nullable(Float64)  COMMENT '20日成交量加权均线',
    adosc        Nullable(Float64)  COMMENT '蔡金震荡器(3/10)',
    eom_14       Nullable(Float64)  COMMENT '14日简易波动量',
    kvo          Nullable(Float64)  COMMENT 'Klinger量震荡器(34/55)',
    kvo_signal   Nullable(Float64)  COMMENT 'KVO信号线(EMA13)',
    nvi          Nullable(Float64)  COMMENT '负成交量指标',
    pvi          Nullable(Float64)  COMMENT '正成交量指标',
    wad          Nullable(Float64)  COMMENT '威廉累积/派发线',
    vo           Nullable(Float64)  COMMENT '成交量震荡器(5/20)',
    marketfi     Nullable(Float64)  COMMENT '市场促进指数((H-L)/V)',

    chips_winner   Nullable(Float64)  COMMENT 'CYQ获利盘比例(成本<=收盘的筹码占比[0,1],换手率衰减模型)',
    chips_avg_cost Nullable(Float64)  COMMENT 'CYQ平均成本(筹码分布质量加权均价)',
    chips_cost_5   Nullable(Float64)  COMMENT 'CYQ成本5%分位价',
    chips_cost_95  Nullable(Float64)  COMMENT 'CYQ成本95%分位价',
    scr            Nullable(Float64)  COMMENT '筹码集中度(100×(cost95-cost5)/(cost95+cost5),越小越集中)',
    cyc_5          Nullable(Float64)  COMMENT '5日成本均线(Σamount/Σvolume)',
    cyc_13         Nullable(Float64)  COMMENT '13日成本均线(Σamount/Σvolume)',
    cyc_34         Nullable(Float64)  COMMENT '34日成本均线(Σamount/Σvolume)',
    cyc_inf        Nullable(Float64)  COMMENT '无穷成本均线(DMA(close,换手率/100))',
    fi_13        Nullable(Float64)  COMMENT '强力指数EMA13(Elder)',

    candle_pattern    Nullable(Float64)  COMMENT '[已停产2026-09-14 裁定#233→图形域 market_pattern_event] K线形态编码(0=无,1=锤子,2=吞没,3=启明星,4=黄昏星,5=十字星...)',
    rsi_divergence    Nullable(Float64)  COMMENT 'RSI背离信号(0=无,1=顶背离,-1=底背离)',
    macd_divergence   Nullable(Float64)  COMMENT 'MACD背离信号(0=无,1=顶背离,-1=底背离)',
    boll_breakout     Nullable(Float64)  COMMENT '布林带突破信号(0=无,1=向上突破,-1=向下突破)',
    vol_price_div     Nullable(Float64)  COMMENT '量价背离信号(0=无,1=顶背离,-1=底背离)',

    data_source  LowCardinality(String)  COMMENT '数据来源(固定 internal=本地计算)',
    ingest_ts    DateTime64(3, 'UTC')  DEFAULT now() COMMENT '入库时间戳',

    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY (period, toYYYYMM(trade_date))
ORDER BY (symbol, period, trade_time)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "technical_indicator"
DATABASE = "c1_market"
CATEGORY_ID = "market_technical_indicator"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "(period, toYYYYMM(trade_date))"
ORDER_BY = "(symbol, period, trade_time)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT/MATERIALIZED 列由 CH 自动填充）
# trade_time 显式写入（日/周/月线写 toDateTime(trade_date)，分钟线写 K 线起始时间）
# period 显式写入（DEFAULT 'daily' 仅作 fallback，INSERT 时始终显式指定）
INSERT_COLUMNS = (
    "(trade_date, trade_time, symbol, period, "
    # 趋势类
    "ma_5, ma_10, ma_20, ma_60, ema_12, ema_26, wma_10, dema_12, "
    "macd_dif, macd_dea, macd_hist, adx_14, pdi_14, mdi_14, cci_14, sar, trix, trma, "
    "dkx_20, dkx_ma10, hma_16, zlema_21, kama_10, vip_14, vim_14, supertrend_10, supertrend_dir, md_14, bbi, "
    "alligator_jaw, alligator_teeth, alligator_lips, "
    "gmma_s3, gmma_s5, gmma_s8, gmma_s10, gmma_s12, gmma_s15, "
    "gmma_l30, gmma_l35, gmma_l40, gmma_l45, gmma_l50, gmma_l60, gann_hilo, gann_hilo_dir, "
    "tema_10, trima_10, t3_10, vidya_14, frama_16, mama, fama, jma_7, "
    "avgprice, medprice, typprice, wcprice, "
    "inertia_20_14, qstick_10, supersmoother_10, highpass_40, ptrend_250_40, ptrend_roc, "
    "tenkan_sen, kijun_sen, senkou_span_a, senkou_span_b, chikou_span, "
    # 动量类
    "kdj_k, kdj_d, kdj_j, rsi_6, rsi_12, rsi_24, wr_14, roc_12, mtm_12, mtmma_12, "
    "cmf_20, uos, ao, cmo_14, stochrsi, "
    "bias_6, bias_12, bias_24, psy_12, psy_ma6, lwr_1, lwr_2, dpo_20, "
    "tsi, smi, smi_signal, fisher_9, fisher_sig9, kst, kst_signal, crsi, "
    "qqe_14, qqe_rsi_ma, stc, rvgi_10, rvgi_sig, "
    "stoch_fastk, stoch_fastd, stoch_slowk, stoch_slowd, aroon_up, aroon_down, aroonosc, "
    "bop, ppo, apo, dx_14, ar_26, br_26, cr_26, "
    "ac, fractal_high, fractal_low, bull_power_13, bear_power_13, coppock, squeeze_on, squeeze_mom, wt1, wt2, "
    "rmi_14, pfe_10, fosc_14, cti_12, vhf_28, er_10, "
    "ht_dcperiod, ht_dcphase, ht_ip, ht_qp, ht_sine, ht_leadsine, ht_trendmode, ebsw_40, continuation_40, gp_sig, gp_pred, "
    "parkinson_20, garman_klass_20, rogers_satchell_20, yang_zhang_20, chop_14, cvi, ulcer_14, "
    # 统计族
    "correl_30, beta_30, linearreg_14, tsf_14, var_20, "
    "linearreg_angle_14, slope_14, intercept_14, stderr_14, zscore_20, "
    # 波动类
    "atr_14, natr_14, trange, massi_25, boll_upper, boll_middle, boll_lower, "
    "kc_upper, kc_middle, kc_lower, dc_upper, dc_lower, "
    "stddev_20, boll_bw, boll_pctb, histvol_20, "
    # 成交量类
    "obv, mfi_14, vwap, vr_26, ad, pvt, wvad_24, vwma_20, adosc, eom_14, kvo, kvo_signal, nvi, pvi, fi_13, "
    "wad, vo, marketfi, "
    # 筹码族（批10：输入含换手率，仅 daily 周期有值，其余周期 NULL）
    "chips_winner, chips_avg_cost, chips_cost_5, chips_cost_95, scr, cyc_5, cyc_13, cyc_34, cyc_inf, "
    # 反转类
    "rsi_divergence, macd_divergence, boll_breakout, vol_price_div, "
    # 元数据
    "data_source)"
)

# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_technical_indicator
# [DOMAIN] D_DATA
# [DEPENDENCIES] schemas.categories.market_kline_daily (输入 OHLCV)
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.internal_compute_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] technical_indicator 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
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
    输出：~55 个技术指标列（Nullable(Float64)），覆盖 5 类 40 个指标

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

    atr_14       Nullable(Float64)  COMMENT '14日真实波幅',
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

    candle_pattern    Nullable(Float64)  COMMENT 'K线形态编码(0=无,1=锤子,2=吞没,3=启明星,4=黄昏星,5=十字星...)',
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
    # 动量类
    "kdj_k, kdj_d, kdj_j, rsi_6, rsi_12, rsi_24, wr_14, roc_12, mtm_12, mtmma_12, "
    "cmf_20, uos, ao, cmo_14, stochrsi, "
    # 波动类
    "atr_14, boll_upper, boll_middle, boll_lower, "
    "kc_upper, kc_middle, kc_lower, dc_upper, dc_lower, "
    "stddev_20, boll_bw, boll_pctb, histvol_20, "
    # 成交量类
    "obv, mfi_14, vwap, vr_26, ad, pvt, wvad_24, "
    # 反转类
    "candle_pattern, rsi_divergence, macd_divergence, boll_breakout, vol_price_div, "
    # 元数据
    "data_source)"
)

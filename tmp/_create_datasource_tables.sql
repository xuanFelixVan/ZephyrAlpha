-- 数据源下载相关表 DDL（指令2，§2.3）
-- 数据库: c1_market
-- 共10张新表（#6 沪深港通资金 hk_connect_flow 暂不建表）
-- daily_valuation 和 money_flow 已存在，仅需确认

-- #3 龙虎榜
CREATE TABLE IF NOT EXISTS c1_market.dragon_tiger (
    trade_date Date, symbol String, name String,
    reason String, net_buy Decimal(18,2), buy_amount Decimal(18,2), sell_amount Decimal(18,2),
    data_source LowCardinality(String) DEFAULT 'ifind'
) ENGINE = MergeTree PARTITION BY toYYYYMM(trade_date) ORDER BY (trade_date, symbol);

-- #4 融资融券
CREATE TABLE IF NOT EXISTS c1_market.margin_trading (
    trade_date Date, symbol String,
    margin_balance Decimal(18,2), margin_buy Decimal(18,2), margin_repay Decimal(18,2),
    short_balance Decimal(18,2),
    data_source LowCardinality(String) DEFAULT 'ifind'
) ENGINE = MergeTree PARTITION BY toYYYYMM(trade_date) ORDER BY (trade_date, symbol);

-- #5 大宗交易
CREATE TABLE IF NOT EXISTS c1_market.block_trade (
    trade_date Date, symbol String,
    price Decimal(18,4), volume UInt64, amount Decimal(18,2),
    buyer String, seller String,
    data_source LowCardinality(String) DEFAULT 'ifind'
) ENGINE = MergeTree PARTITION BY toYYYYMM(trade_date) ORDER BY (trade_date, symbol);

-- #7 行业分类
CREATE TABLE IF NOT EXISTS c1_market.industry_class (
    symbol String, industry_sw String, industry_zsi String,
    industry_level UInt8,
    data_source LowCardinality(String) DEFAULT 'ifind'
) ENGINE = MergeTree ORDER BY (symbol);

-- #8 指数成分股
CREATE TABLE IF NOT EXISTS c1_market.index_constituent (
    trade_date Date, index_code String, symbol String,
    weight Decimal(8,4), action String,
    data_source LowCardinality(String) DEFAULT 'ifind'
) ENGINE = MergeTree PARTITION BY toYYYYMM(trade_date) ORDER BY (index_code, trade_date);

-- #9 期货行情K线
CREATE TABLE IF NOT EXISTS c1_market.futures_kline (
    trade_date Date, timestamp DateTime, symbol String,
    open Decimal(18,4), high Decimal(18,4), low Decimal(18,4), close Decimal(18,4),
    volume UInt64, amount Decimal(18,2), open_interest UInt64,
    period String,
    data_source LowCardinality(String) DEFAULT 'qmt'
) ENGINE = MergeTree PARTITION BY toYYYYMM(trade_date) ORDER BY (symbol, period, trade_date);

-- #10 美股指数（ETF替代）
CREATE TABLE IF NOT EXISTS c1_market.us_index (
    trade_date Date, symbol String,
    open Decimal(18,4), high Decimal(18,4), low Decimal(18,4), close Decimal(18,4),
    volume UInt64,
    data_source LowCardinality(String) DEFAULT 'tickflow'
) ENGINE = MergeTree PARTITION BY toYYYYMM(trade_date) ORDER BY (symbol, trade_date);

-- #11 港股日K线
CREATE TABLE IF NOT EXISTS c1_market.hk_daily_kline (
    trade_date Date, symbol String, name String,
    open Decimal(18,4), high Decimal(18,4), low Decimal(18,4), close Decimal(18,4),
    volume UInt64, amount Decimal(18,2),
    data_source LowCardinality(String) DEFAULT 'qmt'
) ENGINE = MergeTree PARTITION BY toYYYYMM(trade_date) ORDER BY (symbol, trade_date);

-- #12 宏观经济
CREATE TABLE IF NOT EXISTS c1_market.macro_data (
    report_date Date, indicator_name String, indicator_value Decimal(18,4),
    unit String, frequency String,
    data_source LowCardinality(String) DEFAULT 'akshare'
) ENGINE = MergeTree PARTITION BY toYYYYMM(report_date) ORDER BY (indicator_name, report_date);

-- #13 分析师预期
CREATE TABLE IF NOT EXISTS c1_market.analyst_forecast (
    report_date Date, symbol String,
    forecast_year String, forecast_eps Decimal(18,4), forecast_pe Decimal(18,4),
    rating String, analyst_count UInt16,
    data_source LowCardinality(String) DEFAULT 'akshare'
) ENGINE = MergeTree PARTITION BY toYYYYMM(report_date) ORDER BY (symbol, report_date);

-- 基础信息表创建脚本
-- 数据库: c1_market

-- 1. 股票列表（含上市+退市）
DROP TABLE IF EXISTS c1_market.stock_list;
CREATE TABLE c1_market.stock_list (
    ts_code         String,
    symbol          String,
    name            String,
    area            String,
    industry        String,
    fullname        String,
    enname          String,
    cn_spell        String,
    market          String,
    exchange        String,
    currency        String,
    list_status     String,
    list_date       Date,
    delist_date     Date,
    hs_hold         String,
    actual_controller String,
    controller_type String
) ENGINE = MergeTree()
ORDER BY (ts_code);

-- 2. 交易日历
DROP TABLE IF EXISTS c1_market.trade_calendar;
CREATE TABLE c1_market.trade_calendar (
    exchange        String,
    cal_date        Date,
    is_open         UInt8,
    pretrade_date   Date
) ENGINE = MergeTree()
ORDER BY (exchange, cal_date);

-- 3. 指数列表
DROP TABLE IF EXISTS c1_market.index_list;
CREATE TABLE c1_market.index_list (
    ts_code         String,
    name            String,
    market          String,
    publisher       String,
    category        String,
    base_date       Date,
    base_point      Float64,
    list_date       Date,
    symbol_num      String,
    market_id       Float64
) ENGINE = MergeTree()
ORDER BY (ts_code);

-- 4. 港股股票列表
DROP TABLE IF EXISTS c1_market.hk_stock_list;
CREATE TABLE c1_market.hk_stock_list (
    code            String,
    name            String
) ENGINE = MergeTree()
ORDER BY (code);

-- 5. 港股交易日历
DROP TABLE IF EXISTS c1_market.hk_trade_calendar;
CREATE TABLE c1_market.hk_trade_calendar (
    cal_date        Date,
    is_open         UInt8,
    pretrade_date   Date
) ENGINE = MergeTree()
ORDER BY (cal_date);

-- 6. 可转债列表
DROP TABLE IF EXISTS c1_market.convertible_bond_list;
CREATE TABLE c1_market.convertible_bond_list (
    bond_code       String,
    bond_name       String,
    bond_short_name String,
    convert_code    String,
    stock_code      String,
    stock_name      String,
    issue_term      Float64,
    par_value       Float64,
    issue_price     Float64,
    issue_amount    Float64,
    bond_balance    Float64,
    start_date      Date,
    end_date        Date,
    rate_type       String,
    coupon_rate     Float64,
    comp_rate       Float64,
    pay_count       UInt16,
    list_date       Date,
    delist_date     Date,
    list_place      String,
    convert_start   Date,
    convert_end     Date,
    stop_convert    Date,
    initial_convert_price Float64,
    latest_convert_price  Float64,
    rate_desc       String,
    redeem_price    Float64,
    issue_credit    String,
    latest_credit   String,
    latest_agency   String
) ENGINE = MergeTree()
ORDER BY (bond_code);

-- 7. ETF列表
DROP TABLE IF EXISTS c1_market.etf_list;
CREATE TABLE c1_market.etf_list (
    etf_code        String,
    etf_name        String,
    etf_abbr        String,
    full_name       String,
    index_code      String,
    index_name      String,
    setup_date      Date,
    list_date       Date,
    list_status     String,
    exchange        String,
    manager         String,
    custodian       String,
    mgmt_fee        Float64,
    etf_type        String
) ENGINE = MergeTree()
ORDER BY (etf_code);

-- 8. LOF列表
DROP TABLE IF EXISTS c1_market.lof_list;
CREATE TABLE c1_market.lof_list (
    code            String,
    name            String
) ENGINE = MergeTree()
ORDER BY (code);

-- 9. ETF基准指数
DROP TABLE IF EXISTS c1_market.etf_benchmark;
CREATE TABLE c1_market.etf_benchmark (
    index_code      String,
    index_full_name String,
    index_short_name String,
    publisher       String,
    publish_date    Date,
    base_date       Date,
    base_point      Float64,
    adjust_cycle    String
) ENGINE = MergeTree()
ORDER BY (index_code);

-- 10. 通达信板块信息
DROP TABLE IF EXISTS c1_market.tdx_sector_info;
CREATE TABLE c1_market.tdx_sector_info (
    sector_code     String,
    trade_date      Date,
    sector_name     String,
    sector_type     String,
    constituent_num UInt16,
    total_share     Float64,
    float_share     Float64,
    total_mv        Float64,
    float_mv        Float64
) ENGINE = MergeTree()
ORDER BY (sector_code, trade_date);

-- 11. 通达信市场统计指数
DROP TABLE IF EXISTS c1_market.tdx_market_index;
CREATE TABLE c1_market.tdx_market_index (
    sector_code     String,
    sector_name     String
) ENGINE = MergeTree()
ORDER BY (sector_code);

# [BLUEPRINT] MOD-DATA-001
# [MODULE] schemas.categories.market.market_commodity_futures_main
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] commodity_futures_main 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] 本模块无运行时错误面——导入即常量；DDL 与 ClickHouse 实际表结构漂移由 apply_market_tables_ddl.py --verify 检出（exit 1）
# [TESTS] none（DDL 真源由 apply --verify 引擎比对间接覆盖）
# [A_module] module_id=MOD-DATA-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""commodity_futures_main 表 DDL-as-Code（category_id: market_commodity_futures_main, calc_mode: preload）.

商品期货主力连续日行情（akshare futures_main_sina），日度更新，新浪源单品种单次返回全历史。
照生猪数据接入模式复制（2026-09-17，st-igalpha-20260917）。
首批 9 品种：lh0(生猪)/lc0(碳酸锂)/si0(工业硅)/ps0(多晶硅)/m0(豆粕)/c0(玉米)/jd0(鸡蛋)/cu0(铜)/al0(铝)。
用于跨品种趋势/波动分析与期现套利（配 commodity_spot_price 基差表）。

数据源：akshare futures_main_sina(symbol="lh0")
    列: 日期/开盘价/最高价/最低价/收盘价/成交量/持仓量/动态结算价
    （akshare_provider 方法内做中文列→英文列映射）
价格字段按任务规格用 Float64（主力连续为拼接连续序列，非单一实物价格，
不适用 #ARCH-CH-026 现货价格 Decimal 精度裁定）。
"""

from __future__ import annotations

# category_id: market_commodity_futures_main
# calc_mode: preload（回测/分析时预加载到内存）

COMMODITY_FUTURES_MAIN_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.commodity_futures_main
(
    trade_date          Date           COMMENT '交易日期',
    symbol              String         COMMENT '品种码(新浪主力连续，如 lh0)',
    open                Float64        COMMENT '开盘价',
    high                Float64        COMMENT '最高价',
    low                 Float64        COMMENT '最低价',
    close               Float64        COMMENT '收盘价',
    volume              Float64        COMMENT '成交量(手)',
    hold                Float64        COMMENT '持仓量(手)',
    settle              Float64        COMMENT '动态结算价',
    ingest_ts           DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY tuple()
ORDER BY (symbol, trade_date)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "commodity_futures_main"
DATABASE = "c1_market"
CATEGORY_ID = "market_commodity_futures_main"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "tuple()"
ORDER_BY = "(symbol, trade_date)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列 ingest_ts 由 CH 自动填充）
INSERT_COLUMNS = "(trade_date, symbol, open, high, low, close, volume, hold, settle)"

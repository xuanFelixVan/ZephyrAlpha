# [BLUEPRINT] MOD-DATA-002
# [MODULE] schemas.categories.market.market_commodity_spot_price
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] commodity_spot_price 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] 本模块无运行时错误面——导入即常量；DDL 与 ClickHouse 实际表结构漂移由 apply_market_tables_ddl.py --verify 检出（exit 1）
# [TESTS] none（DDL 真源由 apply --verify 引擎比对间接覆盖）
# [A_module] module_id=MOD-DATA-002 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""commodity_spot_price 表 DDL-as-Code（category_id: market_commodity_spot_price, calc_mode: preload）.

大宗商品现货价格与基差（生意社 100ppi，akshare futures_spot_price_daily），日度更新，T-1 发布。
照生猪数据接入模式复制（2026-09-17，st-igalpha-20260917）。
全品种约 54 个（vars_list 缺省=生意社在市全品种）。用于期现基差跟踪与套利信号。

数据源：akshare futures_spot_price_daily(start_day, end_day)（已装版本无 date= 参数，实证确认）
    列: symbol/spot_price/near_contract/near_contract_price/dominant_contract/
        dominant_contract_price/near_basis/dom_basis/near_basis_rate/dom_basis_rate/date
    symbol 为源站品种中文名经 chinese_to_english 映射的英文缩写（如 CU/RB/JD），非中文名原样。
字段映射：futures_close←dominant_contract_price（主力合约结算价，收盘口径）；
         basis←dom_basis（主力合约相对现货基差）。
JD(元/公斤→元/500千克×500)/FG(元/平方米×80)/LH(元/公斤×1000) 单位折算已由源内完成。
"""

from __future__ import annotations

# category_id: market_commodity_spot_price
# calc_mode: preload（回测/分析时预加载到内存）

COMMODITY_SPOT_PRICE_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.commodity_spot_price
(
    trade_date          Date           COMMENT '交易日',
    symbol              String         COMMENT '品种码(生意社中文名映射英文缩写，如 CU/RB/JD)',
    spot_price          Float64        COMMENT '现货价格(元/吨，JD/FG/LH 已由源折算)',
    futures_close       Float64        COMMENT '主力合约结算价(源 dominant_contract_price)',
    basis               Float64        COMMENT '基差(源 dom_basis=主力合约结算价-现货价)',
    ingest_ts           DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY tuple()
ORDER BY (symbol, trade_date)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "commodity_spot_price"
DATABASE = "c1_market"
CATEGORY_ID = "market_commodity_spot_price"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "tuple()"
ORDER_BY = "(symbol, trade_date)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列 ingest_ts 由 CH 自动填充）
INSERT_COLUMNS = "(trade_date, symbol, spot_price, futures_close, basis)"

# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market.market_alt_shipping_index
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_alt_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] alt_shipping_index 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""alt_shipping_index 表 DDL-as-Code（category_id: market_alt_shipping_index, calc_mode: preload）.

航运运价指数长表（另类数据第 1 批施工，docs/_working/2026-09-12-alt-data-handoff.md §8-1）。

长表设计 (trade_date, index_code) 粒度，一表装多指数（与 hog_* 单时间序列单表不同，
运价族 7 指数同源同频，长表免 7 张同构表）：

    - BDI  波罗的海综合运价指数（akshare macro_shipping_bdi，金十源，1988-10 起，含日涨跌幅）
    - BCI  波罗的海好望角型船运价指数（akshare macro_china_freight_index，约 2006 起）
    - BSI  波罗的海超级大灵便型船指数（同上）
    - BHMI 灵便型船综合运价指数（同上）
    - HRCI 国际集装箱租船指数（同上）
    - BCTI 油轮运价指数·成品油（同上）
    - BDTI 油轮运价指数·原油（同上）

    BDI 双源重叠期以 macro_shipping_bdi 为准（历史更长且带 change_pct），
    macro_china_freight_index 仅取其余 6 指数，天然免重。

用途：出口链/航运板块景气高频前瞻（D8），与产业链 ig_* 事件传导打通。
"""

from __future__ import annotations

# category_id: market_alt_shipping_index
# calc_mode: preload（回测/分析时预加载到内存）

ALT_SHIPPING_INDEX_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.alt_shipping_index
(
    trade_date  Date                       COMMENT '指数日期',
    index_code  LowCardinality(String)     COMMENT '指数代码(BDI/BCI/BSI/BHMI/HRCI/BCTI/BDTI)',
    index_name  String                     COMMENT '指数中文名',
    value       Float64                    COMMENT '指数值',
    change_pct  Nullable(Float64)          COMMENT '日涨跌幅%(仅BDI源提供)',
    source      LowCardinality(String)     COMMENT 'akshare接口名',
    ingest_ts   DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (index_code, trade_date)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "alt_shipping_index"
DATABASE = "c1_market"
CATEGORY_ID = "market_alt_shipping_index"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(index_code, trade_date)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列 ingest_ts 由 CH 自动填充）
INSERT_COLUMNS = "(trade_date, index_code, index_name, value, change_pct, source)"

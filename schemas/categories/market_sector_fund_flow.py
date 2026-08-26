# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_sector_fund_flow
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.sector_fund_flow_collector(写入); zephyr.signal_ashare.counter_trend_board(SQL_SECTOR_FUND_FLOW 只读，F16INJECT 资金腿); zephyr.data.implementations.sector_code_bridge(段内差分+881→880重钥)
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] sector_fund_flow 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行；列集=采集器 INSERT_COLUMNS 13 列+ingest_ts DEFAULT 列，不按想象加字段
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1 / verify_schema_truth.py 漂移报告
# [TTL] permanent
"""sector_fund_flow 表 DDL-as-Code（category_id: market_sector_fund_flow, calc_mode: lazy）。

本文件是 c1_market.sector_fund_flow 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_market_tables_ddl.py 执行。

来源（2026-08-26 Owner 全批 DDL 三件之一；D3 / GAP-F-16）：
    采集器 zephyr.data.implementations.sector_fund_flow_collector
    （MOD-DAT-sector_fund_flow_ingest）docstring DDL 草稿转正——采集器
    INSERT_COLUMNS 13 列与本表列序一一对应（ingest_ts 为 DEFAULT 列不入列）。
    源=同花顺即时资金流快照（akshare stock_fund_flow_industry/concept，
    symbol="即时"），金额为 THS 原始口径（亿元，当日累计）；分钟粒度=盘中
    轮询快照+相邻快照差分（消费方口径=段末累计−段前累计）。

消费方契约（F16INJECT 资金卡，counter_trend_board.SQL_SECTOR_FUND_FLOW）：
    SELECT sector_name, timestamp, net_amount FROM c1_market.sector_fund_flow
    WHERE trade_date = %(trade_date)s AND sector_type = 'industry'
    ORDER BY sector_name, timestamp
    ——trade_date 参数为 date 对象（Date 列）；timestamp 经 str(ts)[:16] 分钟
    截断对齐 kline_sector_intraday 粒度（sector_code_bridge.segment_net_inflow）；
    net_amount None 行消费侧跳过（Nullable 保留源侧缺失语义）。

引擎选型说明：
    盘中定时轮询快照（1min 对齐 kline_sector_intraday 粒度，tasks.yaml 接线另案），
    ReplacingMergeTree 按 (sector_type, sector_name, timestamp) 同键静默替换——
    同一快照时刻重跑/补采幂等（§7.3 幂等首选）。

与草稿的唯一偏差（施工裁定，2026-08-26）：
    timestamp 由草稿 DateTime 升级为 DateTime64(3, 'Asia/Shanghai')——房规
    #ARCH-CH-025 时间列统一 DateTime64(3,tz)（kline_sector_intraday/sector_snapshot
    同口径），显式时区消除服务器时区歧义；消费方 str(ts)[:16] 截断对两者同效。
"""

from __future__ import annotations

from typing import Final

# category_id: market_sector_fund_flow
# calc_mode: lazy

MARKET_SECTOR_FUND_FLOW_DDL: Final = """
CREATE TABLE IF NOT EXISTS c1_market.sector_fund_flow
(
    trade_date        Date                        COMMENT '交易日期(由timestamp派生)',
    timestamp         DateTime64(3, 'Asia/Shanghai') COMMENT '快照采集时刻(=轮询时刻,北京时间)',
    sector_type       LowCardinality(String)      COMMENT '板块类型(industry=行业/concept=概念)',
    sector_name       String                      COMMENT '同花顺板块名(JOIN sector_meta键,881体系)',
    sector_index      Nullable(Decimal(18, 4))    COMMENT '行业指数',
    pct_change        Nullable(Decimal(18, 4))    COMMENT '行业涨跌幅(%)',
    inflow_amount     Nullable(Decimal(20, 4))    COMMENT '流入资金(亿元,当日累计,THS原始口径)',
    outflow_amount    Nullable(Decimal(20, 4))    COMMENT '流出资金(亿元,当日累计)',
    net_amount        Nullable(Decimal(20, 4))    COMMENT '净额(亿元,当日累计;相邻快照差分=区间净流入)',
    company_count     Nullable(UInt32)            COMMENT '公司家数',
    lead_stock        String                      COMMENT '领涨股',
    lead_pct_change   Nullable(Decimal(18, 4))    COMMENT '领涨股涨跌幅(%)',
    data_source       LowCardinality(String)      DEFAULT 'ths' COMMENT '数据来源',
    ingest_ts         DateTime64(3, 'UTC')        DEFAULT now() COMMENT '入库时间戳(audit 1.7 #ARCH-CH-025)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (sector_type, sector_name, timestamp)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME: Final = "sector_fund_flow"
DATABASE: Final = "c1_market"
CATEGORY_ID: Final = "market_sector_fund_flow"
CALC_MODE: Final = "lazy"
ENGINE: Final = "ReplacingMergeTree"
PARTITION_KEY: Final = "toYYYYMM(trade_date)"
ORDER_BY: Final = "(sector_type, sector_name, timestamp)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
# 与 sector_fund_flow_collector.INSERT_COLUMNS 13 列严格同序
INSERT_COLUMNS: Final = (
    "(trade_date, timestamp, sector_type, sector_name, sector_index, pct_change, "
    "inflow_amount, outflow_amount, net_amount, company_count, lead_stock, "
    "lead_pct_change, data_source)"
)

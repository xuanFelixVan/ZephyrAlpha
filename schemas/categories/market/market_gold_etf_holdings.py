# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] schemas.categories.market.market_gold_etf_holdings
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] scripts.ch.apply_cross_asset_ddl; zephyr.data.implementations.akshare_alt_provider
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] gold_etf_holdings 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 scripts/ch/apply_cross_asset_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_cross_asset_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_cross_asset_ddl.py --verify
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""gold_etf_holdings（SPDR Gold Trust 黄金 ETF 持仓吨位）DDL-as-Code（category_id: market_gold_etf_holdings）.

D5 跨资产·H8 SPDR 黄金 ETF 持仓（骨架 01 号文档 D5 族 / altdata_line 09 清单，
DS-CAND-025 毕业，2026-09-18 全流通战役 st-ff-altdataF-20260918 施工）。

源与覆盖（2026-09-18 本机实测）：
    - AKShare macro_cons_gold = 全球最大黄金 ETF SPDR Gold Trust（GLD）持仓报告 ✅
      2,871 行，实测区间 2004-11-19 ~ 2026-09-17（GLD 2004-11 上市起，日频）。
    - 列：商品/日期/总库存(吨)/增持减持(吨)/总价值(USD)。
    ⚠ 上游为金十 datacenter（dc_etf_gold）——与 2025-10 停更的议息日历族不同报表，
      实测仍日新；停更检测由哨兵独立承担（gold_etf_holdings 阈值行）。

用途：全球黄金 ETF 持仓是实物金需求与避险情绪的风向标，与 CFTC 黄金非商业净持仓
（同批 cftc_positioning 表 market_name='黄金'）交叉验证——ETF 吨位=实物配置盘，
COT 净多=投机盘，两者背离是贵金属影子线的经典信号。

PIT 双轴：trade_date=持仓日期（事实时间锚）；ingest_ts=采集时间。
源端「增持/减持」已是日环比差分，本表原样落库不做二次差分（避免口径二义）。

引擎选型：
    ReplacingMergeTree（无版本列），同键 (fund_code, trade_date) 重拉幂等替换。
    PARTITION BY toYear(trade_date)——2004- 起 22 年日频，按月分区产生 260+ 分区，
    年分区已满足裁剪（例外理由留痕）。
"""

from __future__ import annotations

# category_id: market_gold_etf_holdings
# calc_mode: preload

GOLD_ETF_HOLDINGS_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.gold_etf_holdings
(
    fund_code       LowCardinality(String)   DEFAULT 'GLD' COMMENT 'ETF 代码(GLD=SPDR Gold Trust)',
    trade_date      Date                     COMMENT '持仓日期(事实时间锚)',
    fund_name       String                   COMMENT '基金名(源端口径:黄金/SPDR Gold Trust)',
    total_tonnes    Nullable(Decimal(18, 3)) COMMENT '总库存(吨,金库实物吨位)',
    change_tonnes   Nullable(Decimal(18, 3)) COMMENT '当日增持/减持(吨,源端已差分,负=减持)',
    total_value_usd Nullable(Decimal(24, 2)) COMMENT '持仓总价值(USD)',
    data_source     LowCardinality(String)   DEFAULT 'akshare_alt' COMMENT '数据来源',
    quality_flag    UInt8                    DEFAULT 1 COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts       DateTime64(3, 'UTC')     DEFAULT now() COMMENT '入库时间戳(采集时间锚)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYear(trade_date)
ORDER BY (fund_code, trade_date)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "gold_etf_holdings"
DATABASE = "c1_market"
CATEGORY_ID = "market_gold_etf_holdings"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYear(trade_date)"
ORDER_BY = "(fund_code, trade_date)"

INSERT_COLUMNS = (
    "(fund_code, trade_date, fund_name, total_tonnes, change_tonnes, "
    "total_value_usd, data_source, quality_flag)"
)

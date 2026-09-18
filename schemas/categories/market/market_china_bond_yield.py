# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] schemas.categories.market.market_china_bond_yield
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_provider
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] market_china_bond_yield 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""market_china_bond_yield（中债收益率曲线，期限点长表）DDL-as-Code
（category_id: market_china_bond_yield）.

altdata_line 09 清单 D5 跨资产 H4（2026-09-18 夜班施工，st-datapack-20260918）。
无风险利率锚（国债）+ 信用利差参照（商业银行普通债 AAA/中短期票据 AAA），
期限点长表存储（trade_date × 曲线 × 期限点一行），期限结构/利差计算消费友好。

源：akshare bond_china_yield（中国货币网 chinamoney.com.cn 中债收益率曲线估值口径，
免费无 key；中债登 chinabond 官网下载页为另一原文通道，深历史挂账 DS-CAND）。
实测（2026-09-18）：三条曲线=中债国债收益率曲线/中债商业银行普通债收益率曲线(AAA)/
中债中短期票据收益率曲线(AAA)；期限点=3月/6月/1年/3年/5年/7年/10年/30年（8 点，
部分曲线末端期限无值→NULL 如实）；**源端滚动窗口约 1 年**（逐月探针实测 2025-10-09 起
可得，更早月份查询返回空）——深历史须走 chinabond 官网归档（挂账），本表可回补深度以
源窗口为界，日更不断供即无缺口。

PIT 双轴：trade_date=估值日（事实时间锚）；ingest_ts=采集时间。
ytm 单位=%（到期收益率，中债估值口径）。

引擎选型：ReplacingMergeTree（同 (curve_name, tenor, trade_date) 幂等替换，重跑窗口重放）。
PARTITION BY toYYYYMM(trade_date)。ORDER BY (curve_name, tenor, trade_date)。
"""

from __future__ import annotations

# category_id: market_china_bond_yield
# calc_mode: preload

MARKET_CHINA_BOND_YIELD_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.market_china_bond_yield
(
    trade_date              Date                        COMMENT '估值日(事实时间锚)',
    curve_name              LowCardinality(String)      COMMENT '曲线名称(中债国债/商业银行普通债AAA/中短期票据AAA)',
    tenor                   LowCardinality(String)      COMMENT '期限点标签(3M/6M/1Y/3Y/5Y/7Y/10Y/30Y)',
    tenor_years             Decimal(6, 2)               COMMENT '期限(年;3M=0.25/6M=0.5/1/3/5/7/10/30,插值用数值锚)',
    ytm                     Nullable(Decimal(10, 6))    COMMENT '到期收益率(%;中债估值口径;曲线末端无值期限=NULL如实)',
    data_source             LowCardinality(String)      DEFAULT 'akshare_chinamoney' COMMENT '数据来源(akshare bond_china_yield=中国货币网中债估值)',
    quality_flag            UInt8                       DEFAULT 1 COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts               DateTime64(3, 'UTC')        DEFAULT now() COMMENT '入库时间戳(采集时间锚)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (curve_name, tenor, trade_date)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "market_china_bond_yield"
DATABASE = "c1_market"
CATEGORY_ID = "market_china_bond_yield"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(curve_name, tenor, trade_date)"

INSERT_COLUMNS = (
    "(trade_date, curve_name, tenor, tenor_years, ytm, data_source, quality_flag)"
)

# 源列名 → (tenor 标签, tenor_years)——中债曲线 8 期限点（源无更细期限点）
TENOR_MAP: dict[str, tuple[str, str]] = {
    "3月": ("3M", "0.25"),
    "6月": ("6M", "0.50"),
    "1年": ("1Y", "1.00"),
    "3年": ("3Y", "3.00"),
    "5年": ("5Y", "5.00"),
    "7年": ("7Y", "7.00"),
    "10年": ("10Y", "10.00"),
    "30年": ("30Y", "30.00"),
}

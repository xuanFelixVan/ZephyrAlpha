# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_account_nav_daily
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.position.live_nav_recorder（writer 注入位，生产接线待排期）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] account_nav_daily 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1 / verify_schema_truth.py 漂移报告
# [TTL] permanent
"""account_nav_daily 表 DDL-as-Code（category_id: market_account_nav_daily, calc_mode: lazy）。

本文件是 c1_market.account_nav_daily 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_market_tables_ddl.py 执行。

来源（2026-08-26 Owner 全批 DDL 三件之一）：
    GAP-F-29 实盘净值曲线序列（zephyr.position.live_nav_recorder，MOD-POS-023）。
    消费方契约=NavPoint frozen dataclass 七字段（trade_date/total_asset/cash/
    market_value/nav_ratio/benchmark_close/benchmark_ratio）——persist_nav_points
    经 writer 注入落库（本模块不直连 DB），原 fragments DDL 草稿（禁直建期）
    随 .runtime/construction_20260823 清理佚失，以代码内期望列为准转正。
    资产源=miniQMT 模拟净值源（CTR-P1-008 券商未接）；基准=沪深300
    （benchmark_close/benchmark_ratio 缺基准降级→NULL）。

引擎选型说明：
    日频净值点（一交易日一行），同日重记/补记场景 ReplacingMergeTree 按
    trade_date 同键静默替换幂等；月分区对齐库内日频表惯例。

TRAE-082 派生列适用性说明：
    账户级日频记录，无 symbol 维度，exchange/symbol_canonical 语义不适用——
    参照同库无 symbol 表先例（market_breadth_snapshot/hog_spot_index）不挂
    TRAE-082 派生列；惯例遵循点=data_source LowCardinality + ingest_ts
    DateTime64(3,'UTC') DEFAULT now() 审计列（audit 1.7 #ARCH-CH-025）。
"""

from __future__ import annotations

from typing import Final

# category_id: market_account_nav_daily
# calc_mode: lazy

MARKET_ACCOUNT_NAV_DAILY_DDL: Final = """
CREATE TABLE IF NOT EXISTS c1_market.account_nav_daily
(
    trade_date       Date                     COMMENT '交易日',
    total_asset      Decimal(20, 2)           COMMENT '总资产=现金+市值(元,模拟账户无负债腿)',
    cash             Decimal(20, 2)           COMMENT '现金(元)',
    market_value     Decimal(20, 2)           COMMENT '持仓市值(元)',
    nav_ratio        Decimal(18, 6)           COMMENT '净值比=总资产/base_nav(首点自身为基准=1.0)',
    benchmark_close  Nullable(Decimal(18, 4)) COMMENT '基准收盘(沪深300,缺基准→NULL降级)',
    benchmark_ratio  Nullable(Decimal(18, 6)) COMMENT '基准比=基准收盘/基准基点(缺基准任一→NULL)',
    data_source      LowCardinality(String)   DEFAULT 'miniqmt_sim' COMMENT '净值源(miniqmt_sim=miniQMT模拟账户,CTR-P1-008券商未接)',
    ingest_ts        DateTime64(3, 'UTC')     DEFAULT now() COMMENT '入库时间戳(audit 1.7 #ARCH-CH-025)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date)
"""

# 表元数据
TABLE_NAME: Final = "account_nav_daily"
DATABASE: Final = "c1_market"
CATEGORY_ID: Final = "market_account_nav_daily"
CALC_MODE: Final = "lazy"
ENGINE: Final = "ReplacingMergeTree"
PARTITION_KEY: Final = "toYYYYMM(trade_date)"
ORDER_BY: Final = "(trade_date)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列由 CH 自动填充）
# 与 live_nav_recorder.NavPoint 七字段同序（data_source 可选显式写入）
INSERT_COLUMNS: Final = "(trade_date, total_asset, cash, market_value, nav_ratio, benchmark_close, benchmark_ratio)"

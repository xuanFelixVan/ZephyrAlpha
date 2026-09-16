# [BLUEPRINT] MOD-AUTO-L1-001 | docs/_working/automation/campaign/blueprints/onboard_source_blueprint.md | §
# [PROVISIONAL] 暂编号：docs/03_modules 解冻后按注册表重编（挂单 H-01）
# [MODULE] schemas.categories.market.market_alt_fx_rate_ecb
# [DOMAIN] D_DATA
# [DEPENDENCIES] 无（纯 DDL 常量）
# [CONSUMERS] scripts/data/fx_ecb_ingest.py; scripts/data/onboard_source.py
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] DateTime64(3) 业务列 Asia/Shanghai、系统列 UTC（库规 c1_market_clickhouse §1327）;
#   ReplacingMergeTree 自然键幂等（同键重放去重）;
#   PIT：trade_date 取源数据自带日期，不信运行日
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 无运行时行为
# [TESTS] tests/data/test_onboard_source.py
# [A_module] module_id=MOD-AUTO-L1-001 | layer=schema | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""ECB 日频汇率表 DDL（frankfurter.app 免费源，L1 上架流水线首个端到端验证源）。

事故备注：本件曾于 2026-09-17 05:1x 被网关失败清理链扫除（未 add 的新文件）——
铁律"改后即 add"的活教材，已按上下文原样重建。
"""

TABLE_NAME = "c1_market.alt_fx_rate_ecb"
DATABASE = "c1_market"
CATEGORY_ID = "market_alt_fx_rate_ecb"
ENGINE = "ReplacingMergeTree"
INSERT_COLUMNS = ("trade_date", "base", "quote", "rate")

FX_RATE_ECB_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.alt_fx_rate_ecb
(
    trade_date Date COMMENT '汇率日期（ECB target 业务日，源自带）',
    base LowCardinality(String) COMMENT '基准币种（如 USD）',
    quote LowCardinality(String) COMMENT '报价币种（如 CNY）',
    rate Float64 COMMENT '收盘汇率（1 base = rate quote）',
    ingest_ts DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, base, quote)
COMMENT 'ECB 日频汇率（frankfurter.app，L1 上架流水线首柜）'
"""

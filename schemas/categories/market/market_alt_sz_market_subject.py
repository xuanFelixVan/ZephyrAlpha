# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market.market_alt_sz_market_subject
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_alt_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] alt_sz_market_subject 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] import 期无副作用无异常（纯 DDL 字符串与常量）；DDL 语法错误由 apply_market_tables_ddl.py fail-visible 捕获
# [TESTS] 解析器同域覆盖（tests/zephyr/data/test_alt_sources.py）；表结构一致性由 apply --verify 校验
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""市场主体发展统计数据（服务 1485642496，新钥匙通道）。年度企业结构（内资/外商/个体/私营/国企）。
"""

from __future__ import annotations

# category_id: alt_sz_market_subject
# calc_mode: preload

MARKET_ALT_SZ_MARKET_SUBJECT_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.alt_sz_market_subject
(
    year               Int32                  COMMENT '年度(ND,幂等键)',
    nzi_ent            Nullable(Int64)        COMMENT '内资企业户数(NZQYDQYHS)',
    nzi_cap            Nullable(Float64)      COMMENT '内资企业注册资本(NZQYDZCZB,万元)',
    wzi_ent            Nullable(Int64)        COMMENT '外商投资企业户数(WSTZQYDQYHS)',
    wzi_cap            Nullable(Float64)      COMMENT '外商投资注册资本(WSTZQYDZCZB,万美元)',
    wzi_invest         Nullable(Float64)      COMMENT '外商直接投资额(WSTZQYDTZZE)',
    gsh_ent            Nullable(Int64)        COMMENT '个体工商户户数(GTGSHDHS)',
    gsh_cap            Nullable(Float64)      COMMENT '个体工商户资金数额(GTGSHDZJSE)',
    sy_ent             Nullable(Int64)        COMMENT '私营企业户数(SYQYDQYHS)',
    nmzy_hz            Nullable(Int64)        COMMENT '农民专业合作社户数(NMZYHZSDHS)',
    nmzy_cz            Nullable(Float64)      COMMENT '农民专业合作社出资(NMZYHZSDCZZE)',
    ingest_ts    DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY tuple()
ORDER BY (year)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "alt_sz_market_subject"
DATABASE = "c1_market"
CATEGORY_ID = "alt_sz_market_subject"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "***"
ORDER_BY = "year"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列 ingest_ts 由 CH 自动填充）
INSERT_COLUMNS = "(year, nzi_ent, nzi_cap, wzi_ent, wzi_cap, wzi_invest, gsh_ent, gsh_cap, sy_ent, nmzy_hz, nmzy_cz)"

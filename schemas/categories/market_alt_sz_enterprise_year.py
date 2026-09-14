# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_alt_sz_enterprise_year
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_alt_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] alt_sz_enterprise_year 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] import 期无副作用无异常（纯 DDL 字符串与常量）；DDL 语法错误由 apply_market_tables_ddl.py fail-visible 捕获
# [TESTS] 解析器同域覆盖（tests/zephyr/data/test_alt_sources.py）；表结构一致性由 apply --verify 校验
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""统计年报-企业登记发展情况（服务 29200_03302396，新钥匙通道）。1979 起年度企业分类登记数。
"""

from __future__ import annotations

# category_id: alt_sz_enterprise_year
# calc_mode: preload

MARKET_ALT_SZ_ENTERPRISE_YEAR_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.alt_sz_enterprise_year
(
    year               Int32                  COMMENT '年份(NF,幂等键)',
    total              Nullable(Int64)        COMMENT '企业总数(QYZS)',
    wzi                Nullable(Int64)        COMMENT '外资企业(WZQY)',
    domestic           Nullable(Int64)        COMMENT '内资企业(DSCY)',
    private            Nullable(Int64)        COMMENT '私营企业(SYQY)',
    individual         Nullable(Int64)        COMMENT '个体工商户(NZQY)',
    others1            Nullable(Int64)        COMMENT '其他1(DYCY)',
    others2            Nullable(Int64)        COMMENT '其他2(DECY)',
    ext1               Nullable(Int64)        COMMENT '扩展字段1(WY10002999)',
    ext2               Nullable(Int64)        COMMENT '扩展字段2(WY30004999)',
    ext3               Nullable(Int64)        COMMENT '扩展字段3(WY50009999)',
    ext4               Nullable(Int64)        COMMENT '扩展字段4(WY100499)',
    ext5               Nullable(Int64)        COMMENT '扩展字段5(WY500999)',
    ext6               Nullable(Int64)        COMMENT '扩展字段6(YYYS1)',
    ingest_ts    DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY tuple()
ORDER BY (year)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "alt_sz_enterprise_year"
DATABASE = "c1_market"
CATEGORY_ID = "alt_sz_enterprise_year"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "***"
ORDER_BY = "year"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列 ingest_ts 由 CH 自动填充）
INSERT_COLUMNS = "(year, total, wzi, domestic, private, individual, others1, others2, ext1, ext2, ext3, ext4, ext5, ext6)"

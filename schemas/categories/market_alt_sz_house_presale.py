# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_alt_sz_house_presale
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_alt_provider
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] alt_sz_house_presale 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] import 期无副作用无异常（纯 DDL 字符串与常量）；DDL 语法错误由 apply_market_tables_ddl.py fail-visible 捕获
# [TESTS] 解析器同域覆盖（tests/zephyr/data/test_alt_sources.py）；表结构一致性由 apply --verify 校验
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""商品房批准预售信息（服务 29200_01903508，新钥匙通道）。预售证×项目。
"""

from __future__ import annotations

# category_id: alt_sz_house_presale
# calc_mode: preload

MARKET_ALT_SZ_HOUSE_PRESALE_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.alt_sz_house_presale
(
    xh                 String                 COMMENT '源序号(XH,幂等键)',
    zone               String                 COMMENT '区域(ZONE)',
    project            String                 COMMENT '项目名(PROJECTNAME)',
    buildings          String                 COMMENT '楼栋(BUILDINGNAMES)',
    purpose            String                 COMMENT '用途(PURPOSE)',
    presale_area       Nullable(Float64)      COMMENT '预售面积(PRESELLAREA)',
    house_suites       Nullable(Int32)        COMMENT '套数(HOUSESUITES)',
    issued_date        String                 COMMENT '发证日期(ISSUEDDATE,原文)',
    pass_date          String                 COMMENT '通过日期(PASSDATE,原文)',
    issue_organ        String                 COMMENT '发证机关(ISSUEORGAN)',
    organ_name         String                 COMMENT '开发商(ORGAN_NAME)',
    site_address       String                 COMMENT '坐落(SITEADDRESS)',
    parcel_code        String                 COMMENT '地块号(PARCEL_CODE)',
    contract_no        String                 COMMENT '合同号(FULL_CONTRACT_NO)',
    project_id         String                 COMMENT '项目 ID(STRPREPROJECTID)',
    house_id           String                 COMMENT '房屋 ID(HOUSEID)',
    ad_years           String                 COMMENT '年度(ADYEARS)',
    ingest_ts    DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳'
)
ENGINE = ReplacingMergeTree
PARTITION BY tuple()
ORDER BY (xh)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "alt_sz_house_presale"
DATABASE = "c1_market"
CATEGORY_ID = "alt_sz_house_presale"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "***"
ORDER_BY = "xh"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT 列 ingest_ts 由 CH 自动填充）
INSERT_COLUMNS = "(xh, zone, project, buildings, purpose, presale_area, house_suites, issued_date, pass_date, issue_organ, organ_name, site_address, parcel_code, contract_no, project_id, house_id, ad_years)"

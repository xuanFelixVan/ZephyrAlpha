# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] schemas.categories.macro.macro_credit_money
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_provider
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] macro_credit_money 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""macro_credit_money（金融信用与货币供应宽表：社融/新增信贷/M0/M1/M2）DDL-as-Code
（category_id: macro_credit_money）.

D3 宏观高频第一梯队（altdata_line 09 清单 D3，2026-09-18 夜班施工）。
中国月度金融数据宽表：社会融资规模增量+社融口径人民币贷款 / 新增人民币贷款(当月+累计) /
M0/M1/M2 存量+同比。

源：
    macro_china_shrzgm（东财，2015-01 起）
        → sf_increment(社会融资规模增量)/sf_rmb_loans(其中-人民币贷款)
    macro_china_new_financial_credit（东财，2008- 起，fresh 实测 2026-08）
        → new_rmb_loans/new_rmb_loans_cum
    macro_china_supply_of_money（网易，1978- 起，fresh 实测 2026-08，比
        macro_china_money_supply 深约 30 年且含 M0 口径完整）
        → m0/m0_yoy/m1/m1_yoy/m2/m2_yoy

口径留痕（2026-09-18 交叉验收）：M1 存量与东财 money_supply 版在 2024-11 起
出现大幅分歧（650904 vs 1076379 亿元）——人民银行 2024-12 修订 M1 统计口径
（纳入个人活期存款+非银行支付备付金）。本表取网易版全程单源序列，历史段
内部口径一致（回测友好）；跨口径对比勿混用两源。金额精度：网易版 2 位小数、
东财版全精度，小数位差异非数据错误。

源端现实（2026-09-18 实查）：macro_china_shrzgm 源端停在 2026-04（东财 datacenter
该报表滞更；既有 macro_data SocialFinancing 任务同源同风险），sf 两列为历史段+
观察中恢复，表级新鲜度由货币/信贷列维持（哨兵阈值按整表 max(report_date) 判）。

与 c1_market.macro_data 的关系（查重声明）：
    macro_data=generic 长表（既有 MoneySupply/SocialFinancing 长表行继续维护）；
    本表为宽表结构化数据集，按骨架分类学判据 2 独立成表，不构成双真源。

PIT 双轴：report_date=事实时间锚（统计期月末）；ingest_ts=采集时间。
金额单位统一亿元（源端口径）。

引擎选型：
    ReplacingMergeTree（无版本列，重拉幂等去重）。
    PARTITION BY toYYYYMM(report_date)。
    ORDER BY (report_date)。
"""

from __future__ import annotations

# category_id: macro_credit_money
# calc_mode: preload

MACRO_CREDIT_MONEY_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.macro_credit_money
(
    report_date       Date                        COMMENT '统计期月末(事实时间锚)',
    sf_increment      Nullable(Decimal(18, 4))    COMMENT '社会融资规模增量(亿元;源端2026-04起滞更观察中)',
    sf_rmb_loans      Nullable(Decimal(18, 4))    COMMENT '社融口径人民币贷款增量(亿元)',
    new_rmb_loans     Nullable(Decimal(18, 4))    COMMENT '新增人民币贷款-当月(亿元)',
    new_rmb_loans_cum Nullable(Decimal(18, 4))    COMMENT '新增人民币贷款-年初累计(亿元)',
    m0                Nullable(Decimal(18, 4))    COMMENT '流通中现金M0(亿元)',
    m0_yoy            Nullable(Decimal(10, 4))    COMMENT 'M0同比(%)',
    m1                Nullable(Decimal(18, 4))    COMMENT '狭义货币M1(亿元)',
    m1_yoy            Nullable(Decimal(10, 4))    COMMENT 'M1同比(%)',
    m2                Nullable(Decimal(18, 4))    COMMENT '广义货币M2(亿元)',
    m2_yoy            Nullable(Decimal(10, 4))    COMMENT 'M2同比(%)',
    data_source       LowCardinality(String)      DEFAULT 'akshare' COMMENT '数据来源',
    quality_flag      UInt8                       DEFAULT 1 COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts         DateTime64(3, 'UTC')        DEFAULT now() COMMENT '入库时间戳(采集时间锚)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(report_date)
ORDER BY (report_date)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "macro_credit_money"
DATABASE = "c1_market"
CATEGORY_ID = "macro_credit_money"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(report_date)"
ORDER_BY = "(report_date)"

INSERT_COLUMNS = (
    "(report_date, sf_increment, sf_rmb_loans, new_rmb_loans, new_rmb_loans_cum, "
    "m0, m0_yoy, m1, m1_yoy, m2, m2_yoy, data_source, quality_flag)"
)

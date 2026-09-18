# [BLUEPRINT] MOD-L04-001 | docs/03_modules/_cross_layer/database/sub_blueprints/c1_market_clickhouse.md
# [MODULE] schemas.categories.macro.macro_pmi_gauge
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.data.implementations.akshare_provider
# [STARTUP] imported
# [MATURITY] new
# [INVARIANTS] macro_pmi_gauge 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_schema.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1
# [TESTS] python scripts/ch/apply_market_tables_ddl.py --verify
# [A_module] module_id=MOD-L04-001 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""macro_pmi_gauge（景气总 gaug 表：官方制造业/非制造业 PMI + 财新双 PMI）DDL-as-Code
（category_id: macro_pmi_gauge）.

D3 宏观高频第一梯队（altdata_line 09 清单 D3，2026-09-18 夜班施工）。
中国月度景气指标宽表：官方制造业/非制造业 PMI（指数+同比）+ 财新制造业/服务业 PMI。

源：
    macro_china_pmi（东财 datacenter wide，2008- 起，fresh 实测 2026-08）
        → pmi_mfg/pmi_mfg_yoy/pmi_nonmfg/pmi_nonmfg_yoy
    macro_china_cx_pmi_yearly（金十，2012-01~2025-09）
        → caixin_mfg
    macro_china_cx_services_pmi_yearly（金十，2012-04~2025-09）
        → caixin_services

源端现实（2026-09-18 实查）：金十系接口 2025-10 起停更（尾部只剩 nan 今值+预约行），
财新两列为历史段序列（2012-2025.09，牛熊周期回测仍有价值），官方 PMI 列为活性主序列——
表级新鲜度由官方列维持，财新列停更属源端退役非断供。

与 c1_market.macro_data 的关系（查重声明）：
    macro_data=generic 长表（既有 PMI 任务继续维护）；本表为宽表结构化数据集，
    按骨架分类学判据 2 独立成表，不构成双真源。

PIT 双轴：report_date=事实时间锚（统计期月末）；ingest_ts=采集时间。
财新 PMI 的金十 日期 列为公布日（次月 1-3 日），换算统计月=公布月上月。

引擎选型：
    ReplacingMergeTree（无版本列，重拉幂等去重）。
    PARTITION BY toYYYYMM(report_date)。
    ORDER BY (report_date)。
"""

from __future__ import annotations

# category_id: macro_pmi_gauge
# calc_mode: preload

MACRO_PMI_GAUGE_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.macro_pmi_gauge
(
    report_date      Date                        COMMENT '统计期月末(事实时间锚)',
    pmi_mfg          Nullable(Decimal(10, 4))    COMMENT '官方制造业PMI(荣枯线50)',
    pmi_mfg_yoy      Nullable(Decimal(10, 4))    COMMENT '官方制造业PMI同比(%)',
    pmi_nonmfg       Nullable(Decimal(10, 4))    COMMENT '官方非制造业PMI(荣枯线50)',
    pmi_nonmfg_yoy   Nullable(Decimal(10, 4))    COMMENT '官方非制造业PMI同比(%)',
    caixin_mfg       Nullable(Decimal(10, 4))    COMMENT '财新制造业PMI终值(历史段2012-01~2025-09,金十源退役)',
    caixin_services  Nullable(Decimal(10, 4))    COMMENT '财新服务业PMI(历史段2012-04~2025-09,金十源退役)',
    data_source      LowCardinality(String)      DEFAULT 'akshare' COMMENT '数据来源',
    quality_flag     UInt8                       DEFAULT 1 COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts        DateTime64(3, 'UTC')        DEFAULT now() COMMENT '入库时间戳(采集时间锚)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(report_date)
ORDER BY (report_date)
SETTINGS index_granularity = 8192
"""

TABLE_NAME = "macro_pmi_gauge"
DATABASE = "c1_market"
CATEGORY_ID = "macro_pmi_gauge"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(report_date)"
ORDER_BY = "(report_date)"

INSERT_COLUMNS = (
    "(report_date, pmi_mfg, pmi_mfg_yoy, pmi_nonmfg, pmi_nonmfg_yoy, "
    "caixin_mfg, caixin_services, data_source, quality_flag)"
)

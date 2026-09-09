# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.meta.meta_stock_profile_ths
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; scripts/ch/import_ths_profile.py
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] stock_profile_ths 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行
# [MODIFY-GUARD] schema-change
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] human_only
# [ERROR_CONTRACT] DDL 语法错误->apply 执行时 CH 报错（fail-closed，不静默建错表）
# [TESTS] scripts/ch/import_ths_profile.py --verify
# [A_module] module_id=MOD-L04-001 | layer=module | stability=stable | safety=L | ai_autonomy=human_only
# [TTL] permanent
"""stock_profile_ths 表 DDL-as-Code（category_id: meta_stock_profile_ths, calc_mode: preload）.

THS 个股元数据主数据表（2026-09-09，DS-223）：
    全市场 THS（同花顺）行业分类 + 公司简介唯一真源。补齐 c1_market 三个
    主数据缺口中的两个：细分行业（THS 三级，257 值）与公司简介。
    证监会行业不入库（THS 导出 1669 只"不详"质量不足，图谱侧仅交叉验证用）。

    数据源：docs/_working/同花顺资料/个股1 (1).xlsx / 个股1 (2).xlsx
    （实为 GBK 编码、\\r 换行的 TSV，伪装 .xlsx，禁常规 Excel 工具读取）。
    覆盖沪深 A 股 5217 只（两文件零重叠，已实证）。
    消费方：量化筛选/回测（全市场口径）+ 产业链图谱公司节点标签域回填
    （ths_industry←industry_ths_l2, sub_industry←industry_ths_l3, profile→ig_chunk）。

    PIT 语义：trade_date=导入快照日，(trade_date, symbol) ReplacingMergeTree
    同日重跑幂等替换；未来重新导入自动留下历史快照版本。

    行业层级从导出列"所属同花顺行业"【L1-L2-L3】拆出三列：
    - industry_ths_l1：一级行业
    - industry_ths_l2：二级行业（=导出列"所属行业"，90 值，与 sector_meta 同花顺行业板块同源）
    - industry_ths_l3：三级行业（=导出列"细分行业"，257 值）

    目录说明：置于 meta/ 子目录（GOV-DOC-018 容量治理——父目录 schemas/categories/
    已达 124 文件硬上限，新增 schema 文件自本文件起入子目录）。
    DDL 表名经 DATABASE/TABLE_NAME f-string 拼接（渲染结果与字面 DDL 逐字节一致），
    满足 TABLE-NAME-REGISTRY gate（#ARCH-CH-024：全限定表名唯一真源为
    business_data_categories.yaml；DDL 真源与注册表互为因果，无法经 TableRegistry 引用）。

    MATERIALIZED 列沿袭 TRAE-082 通用模式（exchange/symbol_canonical 前缀推导）。
"""

from __future__ import annotations

# category_id: meta_stock_profile_ths
# calc_mode: preload（全市场主数据维度表）

TABLE_NAME = "stock_profile_ths"
DATABASE = "c1_market"

STOCK_PROFILE_THS_DDL = f"""
CREATE TABLE IF NOT EXISTS {DATABASE}.{TABLE_NAME}
(
    trade_date       Date                   COMMENT '导入快照日(同日重跑幂等替换)',
    symbol           String                 COMMENT '证券代码(6位裸码)',
    name             String                 COMMENT '证券简称(THS导出口径)',
    industry_ths_l1  LowCardinality(String) DEFAULT '' COMMENT 'THS一级行业(从【L1-L2-L3】拆出)',
    industry_ths_l2  LowCardinality(String) DEFAULT '' COMMENT 'THS二级行业(=导出列所属行业,90值)',
    industry_ths_l3  LowCardinality(String) DEFAULT '' COMMENT 'THS三级行业(=导出列细分行业,257值)',
    profile          String                 DEFAULT '' COMMENT '公司简介(THS导出口径全文)',
    data_source      LowCardinality(String) DEFAULT 'ths_manual' COMMENT '数据来源',
    ingest_ts        DateTime64(3, 'UTC')   DEFAULT now() COMMENT '入库时间戳',
    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY tuple()
ORDER BY (trade_date, symbol)
SETTINGS index_granularity = 8192
"""

# 表元数据
CATEGORY_ID = "meta_stock_profile_ths"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "tuple()"
ORDER_BY = "trade_date, symbol"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT/MATERIALIZED 列由 CH 自动填充）
INSERT_COLUMNS = (
    "(trade_date, symbol, name, industry_ths_l1, industry_ths_l2, "
    "industry_ths_l3, profile, data_source)"
)

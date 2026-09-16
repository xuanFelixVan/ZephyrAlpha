# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market.market_daban_engine_load
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] zephyr.ex_core.daban_load_producer（产出侧，落表）; zephyr.pf_core.strategies.daban_sleeve_strategy（消费侧，PIT 真读）
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] daban_engine_load 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行；列集=producer LOAD_INSERT_COLUMNS 21 列 + ingest_ts DEFAULT 列，不按想象加字段
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1 / verify_schema_truth.py 漂移报告
# [TTL] permanent
"""daban_engine_load 表 DDL-as-Code（category_id: market_daban_engine_load, calc_mode: lazy）。

本文件是 c1_market.daban_engine_load 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_market_tables_ddl.py 执行。

背景（T3⑧ daban 四引擎应用层批产接线，裁定#257⑥ 挂起经 Owner 2026-09-16 新令解除）：
    挖矿 LUE-1 实证——daban-sleeve 在 fw-tdm-current 挂 0.0945 权重，但四引擎
    （selector/youzi/quant/fusion_context）负载**无日频批产源**（权重有、输入没有，
    0.0945 空转，与 T1A-1 死成员同根）。地基（daban_board_event 派生表 + stk_limit
    精确 join）已由裁定#257⑤ 接通；本表是其上的**应用层负载批产真源**——
    生产者 zephyr.ex_core.daban_load_producer 从 daban_board_event（事件日 T-1 口径）
    + 市场宽度快照派生四引擎可产字段，落本表；daban_sleeve_strategy 从本表 PIT 真读。

字段口径（producer 契约，可产 vs 显式缺省留痕见 derived_fields）：
    - consec_limit/open_board_count/first_touch_time/seal_amount/limit_up_price/
      close_price/is_one_word/st_flag/board —— daban_board_event 直映（真封板口径）。
    - seal_time_minutes —— first_touch_time 折算为"从开盘 09:30 起分钟数"（午间 11:30
      休市扣除，A 股连续竞价时段口径）。
    - stock_change_pct —— (close/pre_close−1)×100（pre_close 缺则 None 显式缺省）。
    - float_market_cap —— stock_indicator.circ_mv（万元）×1e4 折算为元（真连接 (trade_date,
      symbol)；缺/非正则 None 显式缺省）。为 youzi 封流比（seal_amount/float_market_cap，
      封单质量 20 分因子）与 quant 资金分母，挖矿 LUE-1 实证的可产真字段，此前欠产致
      封单质量恒 0 分、融合分压在"中性"下、sleeve 空转（本列补齐即治本）。
    - sector_limit_up_count —— 当日同板块（board 口径代理行业）真封板家数（窗口自产）。
    - market_limit_up_count —— 当日全市场真封板家数（窗口自产）。
    - market_breadth_ratio —— market_breadth_snapshot 当日末快照 advancing/(adv+dec)
      （快照仅 2026-08-24 起，早于该窗 None 显式缺省）。
    - market_change_pct —— index_quote 000300.SH 收盘环比（无则 None 显式缺省）。
    - derived_fields —— JSON {字段: "real"|"default"}，逐字段留痕可产性，禁拍默认值冒充。

引擎选型说明：
    日频批产物（事件日×symbol 宽表负载），ReplacingMergeTree 按 (trade_date, symbol)
    同键静默替换——同窗口重跑/load_version 升级重推导幂等。

PIT 消费契约（决策日 T 只读 trade_date ≤ T-1）：
    本表 trade_date = 打板事件发生日（涨停当日）。决策日 T 取
    max(trade_date) < T 的分区（前一交易日），shift(1) 口径防未来函数
    （daban_board_event 的封板/close 为当日收盘后才知，T 日盘中不可得）。
"""

from __future__ import annotations

from typing import Final

# category_id: market_daban_engine_load
# calc_mode: lazy

MARKET_DABAN_ENGINE_LOAD_DDL: Final = """
CREATE TABLE IF NOT EXISTS c1_market.daban_engine_load
(
    trade_date             Date                          COMMENT '打板事件日(=决策日 T 的 T-1；PIT shift(1) 消费)',
    symbol                 String                        COMMENT '证券代码(6位裸码)',
    exchange               LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生)',
    symbol_canonical       String MATERIALIZED if(position(symbol,'.')>0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal)',
    board                  LowCardinality(String)        COMMENT '板块(sh_main/sz_main/star/chinext/bj)',
    st_flag                UInt8 DEFAULT 0               COMMENT 'ST标记(daban_board_event 直给)',
    consec_limit           UInt16 DEFAULT 0              COMMENT '连板数(封住日链;四引擎 consecutive_limit_ups)',
    open_board_count       Nullable(UInt16)              COMMENT '开板次数(分钟级下限口径;None=无分钟数据)',
    first_touch_time       Nullable(String)              COMMENT '首触时刻HH:MM:SS(kline_1min 分钟级代理)',
    seal_time_minutes      Nullable(Int16)               COMMENT '封板分钟数(从09:30起,午间休市扣除)',
    seal_amount            Nullable(Decimal(20, 2))      COMMENT '封单金额(元)=seal_amount_proxy(tick 尾盘买一代理,2026-07起;否则None)',
    float_market_cap       Nullable(Float64)             COMMENT '流通市值(元)=stock_indicator.circ_mv(万元)×1e4;youzi封流比/quant资金分母;缺则None显式缺省',
    stock_change_pct       Nullable(Float64)             COMMENT '个股当日涨幅(%)=(close/pre_close-1)*100;pre_close缺则None',
    close_price            Nullable(Decimal(18, 4))      COMMENT '收盘价(事件日)',
    limit_up_price         Decimal(18, 4)                COMMENT '涨停价(三级解析链)',
    is_one_word            UInt8 DEFAULT 0               COMMENT '一字板(low>=limit-0.001)',
    sector_limit_up_count  UInt16 DEFAULT 0              COMMENT '当日同板块真封板家数(助攻梯队代理)',
    market_limit_up_count  UInt32 DEFAULT 0              COMMENT '当日全市场真封板家数',
    market_breadth_ratio   Nullable(Float64)             COMMENT '涨跌家数比(0-1)=adv/(adv+dec);早于2026-08-24为None',
    market_change_pct      Nullable(Float64)             COMMENT '大盘涨幅(%)000300环比;无指数数据为None',
    derived_fields         String                        COMMENT 'JSON{字段:real|default} 逐字段可产性留痕',
    load_version           LowCardinality(String) DEFAULT 'v1' COMMENT '负载口径版本',
    data_source            LowCardinality(String) DEFAULT 'daban_board_event_derived' COMMENT '数据来源',
    ingest_ts              DateTime64(3, 'Asia/Shanghai') DEFAULT now() COMMENT '入库时间戳(DateTime64(3)+显式时区 RULE-SCHEMA-TZ)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, symbol)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME: Final = "daban_engine_load"
DATABASE: Final = "c1_market"
CATEGORY_ID: Final = "market_daban_engine_load"
CALC_MODE: Final = "lazy"
ENGINE: Final = "ReplacingMergeTree"
PARTITION_KEY: Final = "toYYYYMM(trade_date)"
ORDER_BY: Final = "(trade_date, symbol)"

# 列清单（INSERT 显式列，排除 exchange/symbol_canonical MATERIALIZED 与 ingest_ts DEFAULT）
# 与 daban_load_producer.LOAD_INSERT_COLUMNS 20 列严格同序
INSERT_COLUMNS: Final = (
    "(trade_date, symbol, board, st_flag, consec_limit, open_board_count, "
    "first_touch_time, seal_time_minutes, seal_amount, float_market_cap, "
    "stock_change_pct, close_price, limit_up_price, is_one_word, "
    "sector_limit_up_count, market_limit_up_count, market_breadth_ratio, "
    "market_change_pct, derived_fields, load_version, data_source)"
)

# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.market_execution_report
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply_market_tables_ddl; zephyr.ex_core.execution_report(产出侧); zephyr.reporting.default_tca_engine(TCA消费); zephyr.shared.contracts.execution_report_contract(ExecutionReportSource 拉取口)
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] execution_report 表 DDL 唯一真源；本文件 DDL 必须与 ClickHouse 实际表结构一致；变更需经 apply_market_tables_ddl.py 执行；15 个契约字段与 CTR-P1-007 codegen frozen dataclass 一一对应，不按想象加字段
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_market_tables_ddl.py --verify退出码1 / verify_schema_truth.py 漂移报告
# [TTL] permanent
"""execution_report 表 DDL-as-Code（category_id: market_execution_report, calc_mode: lazy）。

本文件是 c1_market.execution_report 表结构的唯一真源（DDL-as-Code 模式）。
ClickHouse 实际表结构必须与本文件 DDL 一致；结构变更通过 apply_market_tables_ddl.py 执行。

来源（2026-08-26 Owner 全批 DDL 三件之一，P0 最急）：
    CTR-P1-007 ExecutionReport 契约层已建成（MOD-INF-016，#ARCH-214；
    数据模型真源=src/zephyr/shared/contracts/execution_report.py codegen frozen
    dataclass，SSoT=architecture_model/contracts/cross_layer_contracts.yaml
    CTR-P1-007 v1.0，DO NOT EDIT）。本表是该契约的持久化载体——TCA/归因消费方
    拉取口=execution_report_contract.ExecutionReportSource Protocol
    （get_execution_report(order_id) / iter_execution_reports(symbol, 窗口)）。

字段对齐（15 个契约字段，唯一真源=codegen 契约，不增不减）：
    order_id/symbol/direction/intended_quantity/actual_quantity/intended_price/
    vwap_price/slippage_bps/commission/execution_start/execution_end/broker_id/
    algo_type/idempotency_key/schema_version。
    类型映射：Decimal→Decimal(18,4)（commission 佣金同价精度，Decimal 等值比较
    不受标度影响）；int→UInt64（契约校验 intended>0/actual>=0）；str 时间戳
    （ISO 8601 UTC）→DateTime64(3,'UTC')（写入侧 datetime 化，读回侧 isoformat）；
    枚举串（direction/algo_type/broker_id/schema_version）→LowCardinality(String)。

V2 codegen 字段扩展预留：
    schema_version 列承载契约版本（v1.0）；codegen 新增字段（V2）经
    apply_market_tables_ddl.py _MIGRATIONS 的 ALTER TABLE ADD COLUMN IF NOT EXISTS
    接入，DEFAULT 值保既有行兼容——与契约层 from_payload「未知键忽略向前兼容」
    口径对称（execution_report_contract.py L223）。

引擎选型说明：
    订单级聚合执行报告（每委托一行，日频千行级低频写入），ReplacingMergeTree
    按 (symbol, execution_start, order_id) 同键静默替换——同一委托执行完成事件
    重放/补跑幂等（§7.3 幂等首选口径）；排序键前缀服务 iter_execution_reports
    的 symbol+窗口扫描，order_id 点查量级小可走稀疏索引尾部。

口径备注：
    - ingest_ts 为 audit 1.7（#ARCH-CH-025）DEFAULT 列，INSERT 不写入。
    - exchange/symbol_canonical 为 TRAE-082 MATERIALIZED 派生列（symbol 承载表
      房规，跨表 JOIN 身份键），INSERT 不写入。
"""

from __future__ import annotations

from typing import Final

# category_id: market_execution_report
# calc_mode: lazy

MARKET_EXECUTION_REPORT_DDL: Final = """
CREATE TABLE IF NOT EXISTS c1_market.execution_report
(
    order_id          String                  COMMENT '委托ID(CTR-P1-007)',
    symbol            String                  COMMENT '标的代码',
    direction         LowCardinality(String)  COMMENT '买卖方向(BUY|SELL)',
    intended_quantity UInt64                  COMMENT '意图成交数量(股,>0)',
    actual_quantity   UInt64                  COMMENT '实际成交数量(股,<=intended;actual<intended隐含部分成交)',
    intended_price    Decimal(18, 4)          COMMENT '意图价格(决策价,40号§2.4 DECISION滑点基准)',
    vwap_price        Decimal(18, 4)          COMMENT '实际成交VWAP(单券商MVP=成交均价)',
    slippage_bps      Float64                 COMMENT '滑点(bps,带方向符号,正=不利成本/买贵卖贱)',
    commission        Decimal(18, 4)          COMMENT '佣金(元,>=0)',
    execution_start   DateTime64(3, 'UTC')    COMMENT '执行开始时间(契约口径ISO 8601 UTC)',
    execution_end     DateTime64(3, 'UTC')    COMMENT '执行结束时间(契约口径ISO 8601 UTC,>=start)',
    broker_id         LowCardinality(String)  COMMENT '执行券商(venue)',
    algo_type         LowCardinality(String)  DEFAULT 'NONE' COMMENT '算法类型(TWAP|VWAP|NONE)',
    idempotency_key   String                  COMMENT '幂等键(UUID,防重复处理)',
    schema_version    LowCardinality(String)  DEFAULT '1.0' COMMENT '契约版本(V2 codegen字段扩展走ALTER ADD COLUMN,DEFAULT保旧行兼容)',
    ingest_ts         DateTime64(3, 'UTC')    DEFAULT now() COMMENT '入库时间戳(audit 1.7 #ARCH-CH-025)',
    exchange LowCardinality(String) MATERIALIZED multiIf(symbol = '', '', position(symbol, '.') > 0, splitByChar('.', symbol)[2], substring(symbol, 1, 3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(symbol, 1, 3) IN ('123', '128'), 'SZ', substring(symbol, 1, 2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(symbol, 1, 1) IN ('4', '8'), 'BJ', substring(symbol, 1, 1) IN ('5', '6', '9'), 'SH', substring(symbol, 1, 1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(symbol = '' OR position(symbol, '.') > 0, symbol, concat(symbol, '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(execution_start)
ORDER BY (symbol, execution_start, order_id)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME: Final = "execution_report"
DATABASE: Final = "c1_market"
CATEGORY_ID: Final = "market_execution_report"
CALC_MODE: Final = "lazy"
ENGINE: Final = "ReplacingMergeTree"
PARTITION_KEY: Final = "toYYYYMM(execution_start)"
ORDER_BY: Final = "(symbol, execution_start, order_id)"

# 列清单（用于 INSERT 时显式指定，排除 DEFAULT/MATERIALIZED 列由 CH 自动派生）
# 15 列与 CTR-P1-007 codegen ExecutionReport 契约字段一一对应（contract 字段序）
INSERT_COLUMNS: Final = (
    "(order_id, symbol, direction, intended_quantity, actual_quantity, "
    "intended_price, vwap_price, slippage_bps, commission, "
    "execution_start, execution_end, broker_id, algo_type, "
    "idempotency_key, schema_version)"
)

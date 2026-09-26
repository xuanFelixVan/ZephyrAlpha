# [BLUEPRINT] MOD-DATA-L9AGG | docs/_working/fullflow_mining/04_knowledge_supply/f34_知识汇聚.md | §四最小件
# [MODULE] schemas.categories.l9_readiness_daily
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] zephyr.data.l9_readiness_aggregator (写，写侧唯一); TDM-E-L9-AGG→TDM-E-FLOW
#   供给健康读数边 (下游二期接线); 晨报供给健康段 (读表)
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 表 DDL 唯一真源（DDL-as-Code，decision_daily 同款）；一行=某业务日某读数对象的
#   就绪度读数（ReplacingMergeTree(ingest_ts) 版本列 latest-wins，同日重跑=刷新非追加，sector_state
#   同口径）；suspended/skip=声明式挂起不计红（f31/f33 册语义，禁硬凑绿）；error=探测失败出声
#   （fail-open：探测失败≠读数为零，禁静默绿——reconcile_chain_refs 同款红线）；时戳铁律
#   DateTime64(3)+显式时区，ingest_ts 由 DB 侧 now64(3) 生成（RULE-SCHEMA-TZ 生成侧零墙钟）
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL 与 DB 不一致→scripts/ch/verify_schema_truth.py 报告漂移（*_DDL 常量名可发现）
# [TESTS] tests/data/test_l9_readiness_aggregator.py
# [A_module] module_id=MOD-DATA-L9AGG | layer=schema | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] mod-data-l9agg-l9-readiness-daily-20260926
"""l9_readiness_daily 表 DDL-as-Code——L9 知识供给汇聚就绪度读数表（f34 册 P0 最小件）。

真源：docs/_working/fullflow_mining/04_knowledge_supply/f34_知识汇聚.md §四（最小实件化路径）
+ config/trading_decision_map.yaml TDM-E-L9-AGG 节点（algo_note"只承载结构与指向，不存实时数据"）。

定位：29 源线+5 图谱+3 状态快照的"就绪度读数生产者"唯一落地面——聚合器只做纯读取拼装
（各源线数据已在 CH/PG，禁在汇聚点采集），单行读数=源线短码×绿/黄/红/挂起/跳过+时戳+行数，
喂 TDM-E-L9-AGG→TDM-E-FLOW"供给健康读数"边（T 日聚合读数喂次日数据就绪度，latency=T-1 08:00）。

设计决策（f34 册 §四/§六 自裁记录）：
1. 库归属 c1_market（f34 册建议口径，同 cross_validation_log"治理型日志落 c1_market"先例）；
   待裁项"c1_market vs 治理库"随本施工单定为 c1_market（f34 册 §六：非 Owner 级）。
2. ReplacingMergeTree(ingest_ts) latest-wins——读数是可刷新状态非不可变快照（与
   decision_daily 的 MergeTree 只增不改相反：拍板快照禁涂改，就绪度读数允许同日刷新，
   ORDER BY (trade_date, source_line) 同键重跑覆盖）。
3. status 封闭语义五态+error：green/yellow/red=健康三态；suspended=声明式挂起（B/C 档
   渠道未接、V2 定案挂起——不计红）；skip=读数面未登记（声明式跳过留因，禁硬凑）；
   error=探测失败（fail-open 出声，绝不静默记绿/零）。
4. pit_effective_from 逐行携带知识层 PIT 生效日（TDM effective_from 真源=2026-09-08，
   D118/D122；聚合器从 TDM yaml 读取禁硬编码——回测预检比对轴同源）。
"""

from __future__ import annotations

TABLE_NAME = "c1_market.l9_readiness_daily"
# 常量名必须以 _DDL 结尾：verify_schema_truth._find_ddl_constant 只发现 `*_DDL` 属性
# （decision_daily 同款守卫，防裸名 DDL 被发现器静默跳过=漂移不可见）
L9_READINESS_DAILY_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.l9_readiness_daily
(
    trade_date         Date                            COMMENT '业务日T(读数描述的数据日;业务日真源=resolve_pf_alloc_trade_date 共用口径,禁墙钟猜日)',
    source_line        LowCardinality(String)          COMMENT '读数对象=TDM-E-L9 节点短码(A01..A16/B01..B10/C01..C03/G1..G5/V1..V3)及 G-REFS(chain_refs 对账读数)/AGG(汇聚汇总行)',
    tier               LowCardinality(String)          COMMENT '供给档:A=源线/B=另类待接入/C=无渠道挂起/G=图谱/V=状态快照/G-REFS=图谱对账/AGG=汇聚汇总',
    status             LowCardinality(String)          COMMENT 'green/yellow/red=健康三态;suspended=声明式挂起不计红(B/C 渠道未接,V2 定案挂起);skip=读数面未登记留因;error=探测失败出声(fail-open 禁静默绿)',
    freshness_lag_days Int32                DEFAULT -1 COMMENT 'max(日期列)距业务日日数(-1=不适用/不可得;阈值按供给频率分档)',
    rows_in_window     Int64                DEFAULT -1 COMMENT 'CH 侧=近7日行数(有界扫描);PG 侧=全量行数(-1=不适用)',
    detail             String               DEFAULT '' COMMENT '明细:跳过原因/挂起依据(f31/f33 册)/错误信息/挂零比(G5 WP-0.5)/对账四读数(引用/断链/覆盖/未吸收)',
    pit_effective_from Date                            COMMENT '知识层 PIT 生效日(TDM effective_from 真源读取,禁硬编码——D118/D122 回测预检比对轴)',
    produced_at        DateTime64(3, 'Asia/Shanghai')  COMMENT '读数产出时刻(事件时戳,now_utc 生成转上海时区)',
    ingest_ts          DateTime64(3, 'UTC') DEFAULT now64(3) COMMENT '入库时间(系统列,DB 侧生成;RULE-SCHEMA-TZ 生成侧零墙钟)'
)
ENGINE = ReplacingMergeTree(ingest_ts)
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, source_line)
COMMENT 'L9 知识供给汇聚就绪度读数(TDM-E-L9-AGG 实件,f34 册最小件:T日聚合读数喂次日数据就绪度)'
"""
# 兼容别名（apply 脚本按 module.DDL 取用）
DDL = L9_READINESS_DAILY_DDL

# 表元数据（静态清单由本文件承载，禁散落硬编码）
DATABASE = "c1_market"
CATEGORY_ID = "l9_readiness_daily"
CALC_MODE = "compute"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(trade_date, source_line)"

# 写侧声明列（ingest_ts 由 DB DEFAULT now64(3) 生成，写侧不传=生成器零墙钟，RULE-SCHEMA-TZ）
INSERT_COLUMNS = (
    "(trade_date, source_line, tier, status, freshness_lag_days,"
    " rows_in_window, detail, pit_effective_from, produced_at)"
)

# status 封闭语义（INVARIANTS 第 3 点的枚举承载；聚合器写侧白名单）
STATUSES = ("green", "yellow", "red", "suspended", "skip", "error")

# 读侧查询模板（SQL 单一真源，禁散落在业务代码里拼裸 SQL）。
# 占位符约定：{table} 由本模块常量填充；{day} 由调用方填入 **已校验** 的
# 'YYYY-MM-DD' 字面量（与 alloc_budget_daily 同约定，未校验值不得入 SQL）。
#
# 当日最新读数快照（消费侧二期：pf_alloc/晨报按业务日取整批行，FINAL 去重由 ch_reader 注入）
SQL_LATEST_BY_TRADE_DATE = (
    "SELECT source_line, tier, status, freshness_lag_days, rows_in_window,"
    " detail, pit_effective_from, produced_at"
    " FROM {table} WHERE trade_date = '{day}'"
)

# [BLUEPRINT] MOD-DATA-GOALAGG | docs/_working/infoaxis/00_ledger.md §3-Q6
# [MODULE] schemas.categories.goal_readiness_daily
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] zephyr.data.goal_readiness_aggregator (写，写侧唯一); TDM-E-L9-AGG 目标就绪度读数边;
#   goal_readiness 晨报/看板段 (读表); Q7 开班令 gate (读汇总态)
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] 表 DDL 唯一真源（DDL-as-Code，l9_readiness_daily 同款）；一行=某业务日某 TDM
#   节点的目标就绪度读数（ReplacingMergeTree(ingest_ts) latest-wins 同日刷新幂等）；
#   suspended=挂起不计红（30 源线+4 币圈+V2，f31/f33 册语义）；error=探测失败出声
#   （fail-open 禁静默绿）；分母口径=151 核心（186−30−4−1AGG，Q2 批准，机械复现于聚合器）；
#   时戳铁律 DateTime64(3)+显式时区，ingest_ts 由 DB 侧 now64(3) 生成（RULE-SCHEMA-TZ）
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL 与 DB 不一致→scripts/ch/verify_schema_truth.py 报告漂移（*_DDL 常量名可发现）
# [TESTS] tests/data/test_goal_readiness_aggregator.py
# [A_module] module_id=MOD-DATA-GOALAGG | layer=schema | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] mod-data-goalagg-goal-readiness-daily-20261013
"""goal_readiness_daily 表 DDL-as-Code——TDM 目标就绪度读数表（Q6，裁定#516）。

真源：docs/_working/infoaxis/00_goal_structure_research_2026_10_13.md §5（绿=有目标＋有考卡
＋有消费方＋有读数；黄=缺一；红=有目标零验证）＋ infoaxis/00_ledger.md §3-Q6。

定位：151 核心 TDM 节点的"目标责任制"读数生产者唯一落地面——聚合器纯读取拼装（TDM goal 块
× exam_cards × TDM 边消费方 × 考试读数四源），单行读数=节点×绿/黄/红/挂起+四布尔+明细，
喂"目标就绪度读数"消费面（完工判据=151 核心节点非红）。

分档（Q6 已批口径，v1 自裁记录）：
  green=四要素齐（goal/card/consumer/reading 全 1）；
  yellow=恰缺一（明示缺哪件，补一即绿）；
  red=缺≥2（含"有目标零验证"字面态——三件全缺为其子集；v1 取严口径，待裁项可放宽为缺三才红）；
  suspended=挂起有据不计红（goal.status=suspended/suspended_reference）；
  error=探测失败出声（fail-open，绝不静默记绿）。
汇总行 node_id='AGG-GOAL'：core 分母 151，red 计数，suspended 不计红。
"""

from __future__ import annotations

TABLE_NAME = "c1_market.goal_readiness_daily"
# 常量名必须以 _DDL 结尾：verify_schema_truth._find_ddl_constant 只发现 `*_DDL` 属性
GOAL_READINESS_DAILY_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.goal_readiness_daily
(
    trade_date      Date                            COMMENT '业务日T(读数描述的数据日;业务日真源=resolve_pf_alloc_trade_date 共用口径,禁墙钟猜日)',
    node_id         LowCardinality(String)          COMMENT '读数对象=TDM 节点号(TDM-E-*/TDM-P-*/TDM-X-*/TDM-F-*/TDM-C-*)及 AGG-GOAL(汇总行)',
    family          LowCardinality(String)          COMMENT '目标族=goal 块 family(F01_大盘两态..F18_挂起源线,v0 口径=tdm_goal_blocks.FAMILY_TABLE)',
    status          LowCardinality(String)          COMMENT 'green=四要素齐/yellow=恰缺一/red=缺≥2(含有目标零验证)/suspended=挂起不计红/error=探测失败出声(fail-open 禁静默绿)',
    has_goal        Int8                  DEFAULT 0 COMMENT 'goal 块四字段齐(goal_statement/output_contract/exam_ref/campaign_ref)',
    has_card        Int8                  DEFAULT 0 COMMENT '绑定考试卡≥1(exam_cards node_id 直挂)',
    has_consumer    Int8                  DEFAULT 0 COMMENT '消费方存在(module_mounts/strategy_mounts 非空 或 TDM 边 from=本节点)',
    has_reading     Int8                  DEFAULT 0 COMMENT '验证读数存在(confidence=verified 或 exam_scores_v1 在册行 或 PG exam_result 近窗)',
    detail          String                DEFAULT '' COMMENT '明细:缺哪件/挂起依据(f31/f33)/错误信息;汇总行=分母+red 计数',
    produced_at     DateTime64(3, 'Asia/Shanghai')  COMMENT '读数产出时刻(事件时戳,now_utc 生成转上海时区)',
    ingest_ts       DateTime64(3, 'UTC') DEFAULT now64(3) COMMENT '入库时间(系统列,DB 侧生成;RULE-SCHEMA-TZ 生成侧零墙钟)'
)
ENGINE = ReplacingMergeTree(ingest_ts)
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, node_id)
COMMENT 'TDM 目标就绪度读数(Q6,裁定#516:绿=有目标+有考卡+有消费方+有读数;151 核心分母;挂起不计红)'
"""
# 兼容别名（apply 脚本按 module.DDL 取用）
DDL = GOAL_READINESS_DAILY_DDL

DATABASE = "c1_market"
STATUSES = ("green", "yellow", "red", "suspended", "error")
INSERT_COLUMNS = (
    "trade_date",
    "node_id",
    "family",
    "status",
    "has_goal",
    "has_card",
    "has_consumer",
    "has_reading",
    "detail",
    "produced_at",
)

# 读侧查询模板（SQL 单一真源；{day} 由调用方填入已校验的 'YYYY-MM-DD' 字面量）
SQL_LATEST_BY_TRADE_DATE = (
    "SELECT node_id, family, status, has_goal, has_card, has_consumer, has_reading,"
    " detail, produced_at"
    " FROM {table} WHERE trade_date = '{day}'"
)

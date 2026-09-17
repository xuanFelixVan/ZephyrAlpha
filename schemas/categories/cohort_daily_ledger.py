# [BLUEPRINT] MOD-L04-001 | docs/_working/residual_construction/wo5_cohort_ledger_workbook.md §3 裁定 S1
# [MODULE] schemas.categories.cohort_daily_ledger
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] apply DDL 归总统筹批(一期); cohort_ledger_daily 调度任务(二期接线);
#   next_day_forecaster 特征集(二期); zephyr.alt_data.cohort_daily_ledger(产出行结构对应)
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 表 DDL 唯一真源；变更需经 apply DDL 执行；ReplacingMergeTree 同键替换幂等
#   （重跑/回填安全），业务语义只增不改（历史行纠错=重跑同键覆盖，禁手工 UPDATE）；
#   cohort_id∈{retail,leverage,hot_money,inst_config,industry}；state 一期∈{net_pos,net_neg,neutral}
#   （裁定 S3：进攻/防守等语义态二期接轮动模型后落，禁一期拍脑袋）；
#   金额单位一律万元（裁定 S4，detail JSON 记单位）
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->scripts/ch/verify_schema_truth.py 报告漂移
# [TESTS] tests/alt_data/test_cohort_daily_ledger.py
# [A_module] module_id=MOD-DATA-COHORT-LEDGER | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] cohort-ledger-schema-20260918
"""cohort_daily_ledger 表 DDL-as-Code（WO-5 投资者行为日账本一期结算层，裁定 S1 长表）。

本文件是 c1_backtest.cohort_daily_ledger 表结构的唯一真源（DDL-as-Code 模式）。
施工真源：docs/_working/residual_construction/wo5_cohort_ledger_workbook.md
（§2 六向台账原料表 + §3 Schema 裁定 S1-S4 + §4 一期验收）。

定位：五人群（散户/杠杆/游资/机构配置盘/产业资本）日频净行为长表——
"读博主复盘了解今日市场"变机器日落一行的自动账本（挖后自审闸北极星）。
一期只做结算层（盘后日频，回测唯一真源，裁定 S2）；判定层（盘中分钟估计）三期。

设计决策：
1. 长表（行=cohort×metric×day）抄 alt_regime_signal 成熟先例——加人群/指标免 ALTER。
2. 库归属 c1_backtest（裁定 S2：多表加工派生层，按 data_ops SOP 库前缀路由惯例；
   crisis_gate_log/regime_snapshot_history 同库同族先例，防 c1_market 语义污染）。
3. ReplacingMergeTree ORDER BY (cohort_id, metric_id, trade_date)——同键替换幂等，
   全历史重算/回填安全；业务语义只增不改（禁 UPDATE）。
4. metric_value Decimal(18,4)（裁定 S4 金额单位=万元，money_flow 原生口径，
   detail JSON 记单位）；聚合口径=全市场等权求和+截面中位数双值（防极值股劫持）。
5. proxy_source/bias_note 强制标注是回测纪律落点（红蓝预登记：机构拆单偏差缓解）。
6. 时区铁律（RULE-SCHEMA-TZ）：ingest_ts DateTime64(3,'UTC')；trade_date 业务日期。
7. 无 symbol 列——本表是全市场聚合层，exchange/symbol_canonical MATERIALIZED 规则不适用。
"""

from __future__ import annotations

# category_id: cohort_daily_ledger
# calc_mode: batch（盘后日频批聚合）

COHORT_DAILY_LEDGER_DDL = """
CREATE TABLE IF NOT EXISTS c1_backtest.cohort_daily_ledger
(
    trade_date   Date                        COMMENT '业务交易日(PIT:仅用≤当日收盘数据)',
    cohort_id    LowCardinality(String)      COMMENT '人群ID: retail|leverage|hot_money|inst_config|industry',
    metric_id    LowCardinality(String)      COMMENT '指标ID: net_inflow_sum|net_inflow_median|activity_count|discount_rate_avg|attention_median|margin_buy_sum|margin_balance_delta|board_height_max 等(新增免ALTER)',
    metric_value Decimal(18, 4)              COMMENT '指标值(金额单位=万元,裁定S4;计数类=个;比率类=%;口径记detail.unit)',
    state        LowCardinality(String)      COMMENT '一期状态: net_pos|net_neg|neutral(裁定S3,每metric阈值=0;语义态二期)',
    proxy_source String                      COMMENT '代理口径说明(哪个源表+哪个字段算的;缺源日=missing)',
    bias_note    String                      COMMENT '已知系统性偏差短注(如机构拆单藏单偏差;无则空串)',
    detail       String                      COMMENT 'JSON明细(单位/样本数/板块分布top3/复核锚点等)',
    ingest_ts    DateTime64(3, 'UTC') DEFAULT now64(3) COMMENT '入库时间戳(UTC)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (cohort_id, metric_id, trade_date)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "cohort_daily_ledger"
DATABASE = "c1_backtest"
CATEGORY_ID = "cohort_daily_ledger"
CALC_MODE = "batch"
ENGINE = "ReplacingMergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(cohort_id, metric_id, trade_date)"

# 库表限定名（消费方 SQL 拼接唯一口径）
QUALIFIED_NAME = f"{DATABASE}.{TABLE_NAME}"

# 列清单（用于 INSERT；ingest_ts 系统列 DEFAULT 不入 INSERT）
INSERT_COLUMNS = "(trade_date, cohort_id, metric_id, metric_value, state, proxy_source, bias_note, detail)"

# cohort_id 词表（一期五人群；industry 一期留行位不产出，挂长尾 M-8）
COHORT_RETAIL = "retail"
COHORT_LEVERAGE = "leverage"
COHORT_HOT_MONEY = "hot_money"
COHORT_INST_CONFIG = "inst_config"
COHORT_INDUSTRY = "industry"

# state 词表（裁定 S3 一期：纯规则可回测；阈值=0）
STATE_NET_POS = "net_pos"
STATE_NET_NEG = "net_neg"
STATE_NEUTRAL = "neutral"

# proxy_source 缺源降级标记（缺源日如实标注，不抛异常）
PROXY_MISSING = "missing"

# [BLUEPRINT] MOD-BT-212 | docs/_working/trading_vision/2026-09-16-daily-orchestrator-blueprint.md
# [MODULE] schemas.categories.decision_daily
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] none
# [CONSUMERS] zephyr.strategy_pipeline.daily_decision_orchestrator(写，写侧唯一)；zephyr.frontend.dashboard.components.warroom(读，今日决策面板)
# [STARTUP] imported
# [MATURITY] experimental
# [INVARIANTS] 表 DDL 唯一真源（DDL-as-Code，蓝图 §四.1 逐列）；只增不改（重拍/修订=新 run_id 追加，
#   同 alloc_budget_daily/regime_snapshot_history 口径，禁 ReplacingMergeTree 静默覆盖）；
#   一行=某拍板 run 对某生效交易日（target_date=次交易日）的日度决策快照=当日唯一放行凭证
#   （无快照行=无新开仓令，对齐 alloc_budget_daily.adjudication_id 下单链凭证先例）；
#   金额/仓位单位=占比（0-1 浮点，非元）
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL 与 DB 不一致→scripts/ch/verify_schema_truth.py 报告漂移
# [TESTS] tests/strategy_pipeline/test_decision_orchestrator.py
# [A_module] module_id=MOD-BT-212 | layer=schema | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [CREATION-TOKEN] decision-daily-mod-bt-212-20260916
"""decision_daily 表 DDL-as-Code——日度编排器决策快照表（BT-P1-031 刀 1 一库）。

真源：docs/_working/trading_vision/2026-09-16-daily-orchestrator-blueprint.md §四.1
（DDL 草案逐列照抄，st-orchbp-20260916 蓝图过审+Owner 通宵全量施工令）。

定位：日度编排器（T2 晨判拍板体）把"谁在哪个格子拍了板"收拢为一行可审计快照——
六段状态/预算带/仓位上限/启用包集合/五层门态/今日不交易布尔+理由，全部同行可归因。
写侧唯一=编排器（审计 §七"写侧只挂一器"）；读侧=一图仪表盘今日决策面板+留痕查询。

设计决策（蓝图 §四.1 自裁记录）：
1. MergeTree 只增不改——重拍/修订以新 run_id 追加（同 alloc_budget_daily 先例，
   禁 ReplacingMergeTree 静默覆盖，快照不可变=误拍可追修订行不可涂改）。
2. 库归属 c1_backtest（裁定#305 第 5 点：与 alloc_budget_daily/regime_snapshot_history
   同库便于同日对账；prediction_log 双写暂不做=后续项留登记）。
3. PARTITION BY toYYYYMM(trade_date) + ORDER BY (trade_date, run_id)——主读模式=
   按生效日取最新 run 行（放行凭证语义）。
4. 时区铁律（RULE-SCHEMA-TZ / #ARCH-CH-022）：ingest_ts=DateTime64(3,'UTC') DEFAULT
   now64(3)——入库时刻由 DB 侧生成，写侧生成器禁用 datetime.now()/time.time()
   （run_id 由业务日+uuid 构造）。
5. no_trade 语义=禁新开仓≠清仓（蓝图 §一.5）；存量保命件横切独立，与本表无关。
"""

from __future__ import annotations

TABLE_NAME = "c1_backtest.decision_daily"
# 常量名必须以 _DDL 结尾：verify_schema_truth._find_ddl_constant 只发现 `*_DDL` 属性
# （红蓝发现：alloc_budget_daily 裸名 DDL 被发现器静默跳过=漂移不可见，本表不走旧辙）
DECISION_DAILY_DDL = """
CREATE TABLE IF NOT EXISTS c1_backtest.decision_daily
(
    ingest_ts          DateTime64(3,'UTC') DEFAULT now64(3) COMMENT '入库时间(系统列,UTC,DB侧生成;RULE-SCHEMA-TZ)',
    run_id             String COMMENT '决策 run 标识 decision-<trade_date>-<uuid6>(重拍=新 run_id 追加,修订行同制)',
    trade_date         Date   COMMENT '拍板生效日=次交易日(target_date)',
    asof_data_date     Date   COMMENT '拍板时点所见数据日(PIT:决策只用≤此日信息)',
    market_state       LowCardinality(String) COMMENT '六段状态(capitulation/accumulation/ignition/expansion/euphoria/distribution)',
    state_confidence   Float64 COMMENT 'dominant 态概率(来自 regime_snapshot_history)',
    budget_band_low    Float64 COMMENT '六段预算带下缘(TDM-F-C1)',
    budget_band_high   Float64 COMMENT '六段预算带上缘',
    position_cap       Float64 COMMENT '当日总仓位上限=E-L1 总闸输出,min(预算带插值,60%硬顶)',
    package_set_json   String COMMENT '启用包集合+各包上限系数(S-OWNER-002 输出)+state_matrix 格子溯源',
    gate_snapshot_json String COMMENT 'L1-L5 五层门态只读采集(一闸,含 absent 标记)',
    no_trade           UInt8  COMMENT '0=可交易(限仓) 1=今日不交易(禁新开仓,≠清仓)',
    no_trade_reason    LowCardinality(String) COMMENT '枚举:distribution_band/kill_switch/regime_missing/budget_run_missing/calendar_ambiguous/transition_band(带 reason 明文于 note)',
    sit_out_list_json  String COMMENT '禁做清单快照(plan_engine/sit_out_list.py 三源合成)',
    calendar_source    LowCardinality(String) COMMENT 'trade_calendar|xshg_local|data_proven(日历真源降级轨迹)',
    degraded           UInt8  COMMENT '0=正常 1=降级运行(降级矩阵任一分支触发)',
    degrade_reasons    String COMMENT '降级原因清单(分号分隔,空=无)',
    note               String COMMENT '备注/残缺标注(如 pending-owner-adoption 催采纳)',
    schema_version     LowCardinality(String) COMMENT '行契约版本',
    INDEX idx_nt no_trade TYPE set(2) GRANULARITY 2
)
ENGINE = MergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, run_id)
COMMENT '日度编排器决策快照表(T2 拍板留痕真源,BT-P1-031)'
"""
# 兼容别名（apply 脚本/alloc 家族按 module.DDL 取用；verify 走上行 *_DDL 真名）
DDL = DECISION_DAILY_DDL

# 表元数据（静态清单由本文件承载，禁散落硬编码）
DATABASE = "c1_backtest"
CATEGORY_ID = "decision_daily"
CALC_MODE = "batch"
ENGINE = "MergeTree"
PARTITION_KEY = "toYYYYMM(trade_date)"
ORDER_BY = "(trade_date, run_id)"

# 写侧声明列（ingest_ts 由 DB DEFAULT now64(3) 生成，写侧不传=生成器零墙钟，RULE-SCHEMA-TZ）
INSERT_COLUMNS = (
    "(run_id, trade_date, asof_data_date, market_state, state_confidence,"
    " budget_band_low, budget_band_high, position_cap, package_set_json,"
    " gate_snapshot_json, no_trade, no_trade_reason, sit_out_list_json,"
    " calendar_source, degraded, degrade_reasons, note, schema_version)"
)

# no_trade_reason 封闭枚举（蓝图 §四.1 草案值；数值/清单定型=裁定#305 第 1 点标可调）
NO_TRADE_REASONS = (
    "distribution_band",
    "kill_switch",
    "regime_missing",
    "budget_run_missing",
    "calendar_ambiguous",
    "transition_band",
)

# 读侧查询模板（SQL 单一真源，禁散落在业务代码里拼裸 SQL）。
# 占位符约定：{table} 由本模块常量填充；{date} 由调用方填入 **已校验** 的
# 'YYYY-MM-DD' 字面量（与 alloc_budget_daily 同约定，未校验值不得入 SQL）。
#
# "当日最新 run 行"判据=DB 侧 ingest_ts（run_id 后缀是随机 uuid，字典序≠时间序，
# 与 alloc_budget_daily 同款禁 run_id 排序裁定）。
SQL_LATEST_BY_TARGET_DATE = (
    "SELECT run_id, trade_date, asof_data_date, market_state, state_confidence,"
    " budget_band_low, budget_band_high, position_cap, package_set_json,"
    " gate_snapshot_json, no_trade, no_trade_reason, sit_out_list_json,"
    " calendar_source, degraded, degrade_reasons, note, schema_version"
    " FROM {table} WHERE trade_date = '{date}'"
    " ORDER BY ingest_ts DESC LIMIT 1"
)

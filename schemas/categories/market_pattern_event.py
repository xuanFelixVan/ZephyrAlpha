# [BLUEPRINT] MOD-SIG-145
# [MODULE] schemas.categories.market_pattern_event
# [DOMAIN] D_SIGNAL
# [DEPENDENCIES] 无（DDL-as-Code 真源文件）
# [CONSUMERS] scripts/ch/apply_pattern_event_ddl.py; src/zephyr/signal_ashare/strategy_signal/pattern_event_store.py; scripts/data/pattern_event_backfill.py（W2 波次）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] market_pattern_event 表 DDL 唯一真源；本文件仅供 apply DDL 引用，禁止直接执行建表；confirmed_at 必须是形态最后一根 bar 收盘完成时刻（PIT 铁律，盘中未确认形态禁入）
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_pattern_event_ddl.py --verify退出码1; CH不可达->退出码2
# [TESTS] scripts/ch/apply_pattern_event_ddl.py --verify（部署后引擎一致性核验）; tests/signal_ashare/test_pattern_event_store.py
# [TTL] permanent
"""market_pattern_event 表 DDL-as-Code（category_id: market_pattern_event）。

本文件是 c1_market.market_pattern_event 表结构的唯一真源（DDL-as-Code 模式）。
蓝图：docs/03_modules/_domain_signal/pattern_event_stats/blueprint.md（MOD-SIG-145，
2026-09-14 图形库全链批立项，设计批 commit 84f4679a）。

定位（图形证据闭环第一环）：
    PatternEvent（MOD-SIG-091 引擎扫描产出）→ 本表落库（PIT strict）
    → 前视窗口胜率统计物化（W3，c1_market.market_pattern_win_rate）
    → win_rate_provider 喂 MOD-SIG-115（historical_win_rate 注入契约至今无实现侧）
    + REG-PAT-001 evidence 字段回填通道（W4，生成器产出禁手填）。

落库裁定（沿 market_signal_history 同构先例）：
    单用户系统不为一张表建第二库——预留名 c1_signal 不建库，本表沿
    market_signal_history / execution_report 先例落 c1_market + market_ 前缀。

引擎/分区/排序：
    ReplacingMergeTree(computed_at)——同 ORDER BY 键重放取 computed_at 最新，
    幂等重算（回填断点续扫/增量重跑安全）；
    月分区 toYYYYMM(anchor_trade_date)（回算/归档整批 DROP）；
    ORDER BY 形态维度前置（pattern_id,timeframe,symbol）——主查询=按形态取
    事件流/按 symbol 叠加/胜率聚合。

PIT 口径（防前视铁律）：
    confirmed_at=形态所需最后一根 bar 收盘完成时刻；前视收益=确认收盘→t+N 收盘
    （W3 统计层口径）。盘中未确认形态禁入本表。

事件 ID：event_id=blake2b-64(模式/周期/代码/锚日/确认时刻/形态名) 确定性派生，
    同一形态事件重放产生同 ID→ReplacingMergeTree 天然去重；跨 scan_run 重扫不膨胀。

治理列对齐 internal 计算表惯例：data_source（生产方标识）+ computed_at
（入库审计，#ARCH-CH-025）+ TRAE-082 MATERIALIZED 派生列 exchange/symbol_canonical。
枚举值保真：pattern_class/direction 存引擎封闭集原文（反转/持续/趋势/支撑阻力/
缠论/波浪；向上/向下/中性，PatternClass/PatternDirection .value），不做翻译变换——
与 REG-PAT-001 目录及引擎事件 JOIN 零损耗。
"""

from __future__ import annotations

# category_id: market_pattern_event
# calc_mode: preload（回填批/增量任务入表；事件只记账，不直连任何 order 路径）
MARKET_PATTERN_EVENT_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.market_pattern_event
(
    event_id      UInt64         COMMENT '事件确定性ID(blake2b-64: pattern_id+timeframe+symbol+anchor_trade_date+confirmed_at+name)，重放幂等键',
    pattern_id    LowCardinality(String) COMMENT '形态ID(REG-PAT-001 PAT-* 或引擎 name@anchor)',
    pattern_class LowCardinality(String) COMMENT '图形类别(封闭集原文): 反转|持续|趋势|支撑阻力|缠论|波浪|K线(P2-a 蜡烛扫描器)',
    direction     LowCardinality(String) COMMENT '预测方向(引擎封闭集原文): 向上|向下|中性',
    confidence    Float64        COMMENT '置信度[0,1](引擎初拍值，回验标定批后更新)',
    timeframe     LowCardinality(String) COMMENT '周期: 1m/5m/15m/30m/60m/120m/day/week/month(9 周期口径)',
    symbol        String         COMMENT '证券代码(纯数字,与kline_daily同口径)',
    anchor_trade_date Date       COMMENT '锚定交易日(形态关键点位所在 bar)',
    confirmed_at  DateTime64(3, 'UTC') COMMENT '确认时刻(形态最后一根bar收盘完成;PIT:前视收益自此起算)',
    name          String         DEFAULT '' COMMENT '形态名(引擎事件 name，中文可读)',
    key_points    String         DEFAULT '' COMMENT 'JSON 关键点位[{idx,price,role}](w1~w3 止损位消费)',
    regime_tag    LowCardinality(String) DEFAULT '' COMMENT '确认日所属 regime 态(regime 体系切片，空=未标注)',
    scan_run_id   LowCardinality(String) DEFAULT '' COMMENT '扫描批次ID(回填/增量运行标识，对账键)',
    data_source   LowCardinality(String) COMMENT '生产方: unified_pattern_engine|pattern_backfill|pattern_event_incremental',
    computed_at   DateTime64(3, 'UTC')  DEFAULT now() COMMENT '入库时间戳(ReplacingMergeTree版本列,#ARCH-CH-025)',

    exchange LowCardinality(String) MATERIALIZED multiIf(substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('110', '113', '204', '900', '901', '902', '903'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,3) IN ('123', '128'), 'SZ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,2) IN ('43', '83', '87', '92', '93', '94'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('4', '8'), 'BJ', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('5', '6', '9'), 'SH', substring(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''),1,1) IN ('0', '1', '2', '3'), 'SZ', '') COMMENT '交易所码(TRAE-082 MATERIALIZED派生,前缀推导)',
    symbol_canonical String MATERIALIZED if(position(symbol, '.') > 0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,跨表JOIN用)'
)
ENGINE = ReplacingMergeTree(computed_at)
PARTITION BY toYYYYMM(anchor_trade_date)
ORDER BY (pattern_id, timeframe, symbol, anchor_trade_date, confirmed_at, event_id)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "market_pattern_event"
DATABASE = "c1_market"
CATEGORY_ID = "market_pattern_event"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree(computed_at)"
PARTITION_KEY = "toYYYYMM(anchor_trade_date)"
ORDER_BY = "(pattern_id, timeframe, symbol, anchor_trade_date, confirmed_at, event_id)"

# 列清单（INSERT 显式指定；computed_at DEFAULT now() 自动填充；
# exchange/symbol_canonical MATERIALIZED 派生——列序唯一真源，store 禁硬编码）
INSERT_COLUMNS = (
    "(event_id, pattern_id, pattern_class, direction, confidence, timeframe, "
    "symbol, anchor_trade_date, confirmed_at, name, key_points, regime_tag, "
    "scan_run_id, data_source)"
)

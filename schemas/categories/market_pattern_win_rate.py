# [BLUEPRINT] MOD-SIG-145
# [MODULE] schemas.categories.market_pattern_win_rate
# [DOMAIN] D_SIGNAL
# [DEPENDENCIES] 无（DDL-as-Code 真源文件）
# [CONSUMERS] scripts/ch/apply_pattern_win_rate_ddl.py; scripts/data/pattern_win_rate_materialize.py; src/zephyr/signal_ashare/strategy_signal/pattern_win_rate_provider.py; REG-PAT-001 evidence 回填（W4 生成器）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 本表为派生统计（唯一输入=c1_market.market_pattern_event × c1_market.kline_daily），禁手填；hit_rate 判据=向上:ret>0 / 向下:ret<0 / 中性:NULL；n_events<30 置 low_sample，消费方按无统计处理
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_pattern_win_rate_ddl.py --verify退出码1
# [TESTS] scripts/ch/apply_pattern_win_rate_ddl.py --verify; tests/signal_ashare/test_pattern_win_rate_provider.py
# [TTL] permanent
"""market_pattern_win_rate 表 DDL-as-Code（category_id: market_pattern_win_rate）。

本文件是 c1_market.market_pattern_win_rate 表结构的唯一真源（MOD-SIG-145 W3）。

定位：图形证据闭环的统计层——PatternEvent 前视窗口命中统计物化。
  事件表（market_pattern_event）× kline 前视收益
  → 按 (pattern_id, timeframe, regime_tag, direction, fwd_window) 聚合
  → win_rate_provider 读本表喂 MOD-SIG-115（强度=置信度×胜率加权）
  → W4 生成器回填 REG-PAT-001 evidence 字段（禁手填）。

口径（防前视）：
  fwd_ret = close[t+N交易日] / close[t] - 1，t=锚定bar（confirmed_at 所在日）；
  未成熟事件（t+N 越过最后bar）自然不参与统计（JOIN 不命中）。
  hit_rate 判据按 direction：向上=fwd_ret>0；向下=fwd_ret<0；中性=NULL（MVP
  不设绝对收益阈值，阈值化留待回验标定批）。
  baseline：pattern_id='__baseline__' 行=全体事件（不分组形态）的同口径统计，
  供消费方对照形态相对基准的增量。

引擎/粒度：ReplacingMergeTree(updated_at)——每次物化全量重算重放，同键取最新；
PARTITION BY tuple()（小表）；ORDER BY 消费主键序。
"""

from __future__ import annotations

# category_id: market_pattern_win_rate
# calc_mode: preload（物化任务批算入表；只读消费）
MARKET_PATTERN_WIN_RATE_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.market_pattern_win_rate
(
    pattern_id   LowCardinality(String) COMMENT '形态ID(__baseline__=全体事件基准行)',
    timeframe    LowCardinality(String) COMMENT '周期(day/week/...，9 周期口径)',
    regime_tag   LowCardinality(String) DEFAULT '' COMMENT 'regime 态切片(空=全 regime)',
    direction    LowCardinality(String) COMMENT '向上|向下|中性(中性 hit_rate=NULL)',
    fwd_window   UInt8        COMMENT '前视窗口交易日数(1/5/10/20)',
    n_events     UInt32       COMMENT '成熟事件数',
    hit_rate     Nullable(Float64) COMMENT '命中率(判据见文件头;中性=NULL)',
    avg_fwd_ret  Float64      COMMENT '平均前视收益',
    low_sample   Bool         DEFAULT n_events < 30 COMMENT '样本不足标记(n<30 消费方按无统计处理)',
    updated_at   DateTime64(3, 'UTC') DEFAULT now() COMMENT '物化时间戳(ReplacingMergeTree版本列)'
)
ENGINE = ReplacingMergeTree(updated_at)
PARTITION BY tuple()
ORDER BY (pattern_id, timeframe, regime_tag, direction, fwd_window)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "market_pattern_win_rate"
DATABASE = "c1_market"
CATEGORY_ID = "market_pattern_win_rate"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree(updated_at)"
PARTITION_KEY = "tuple()"
ORDER_BY = "(pattern_id, timeframe, regime_tag, direction, fwd_window)"

# 物化任务 INSERT 列清单（updated_at DEFAULT now() 自动填充）
INSERT_COLUMNS = (
    "(pattern_id, timeframe, regime_tag, direction, fwd_window, "
    "n_events, hit_rate, avg_fwd_ret, low_sample)"
)

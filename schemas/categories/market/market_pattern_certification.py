# [BLUEPRINT] MOD-SIG-148
# [MODULE] schemas.categories.market.market_pattern_certification
# [DOMAIN] D_SIGNAL
# [DEPENDENCIES] 无（DDL-as-Code 真源文件）
# [CONSUMERS] scripts/ch/apply_pattern_certification_ddl.py; pattern_evidence_certifier.run_certify; pattern_signal_runtime.PatternWeightSync（W-CC shrunk 口径）; /api/pattern-winrate 认证列（W-CC）
# [STARTUP] imported
# [MATURITY] design
# [INVARIANTS] 本表为派生判定（唯一输入=c1_market.market_pattern_win_rate），禁手填；判定由 MOD-SIG-148 四闸代码生成；阈值 q=0.05/n_eff_min=30/k=100/conc_max=0.9 预注册于 certifier 蓝图，改动=裁定
# [MODIFY-GUARD] schema-change
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL与DB不一致->apply_pattern_certification_ddl.py --verify 退出码1
# [TESTS] scripts/ch/apply_pattern_certification_ddl.py --verify
# [TTL] permanent
"""market_pattern_certification 表 DDL-as-Code（category_id: market_pattern_certification）。

本文件是 c1_market.market_pattern_certification 表结构的唯一真源（MOD-SIG-148 W-CB，
反过拟合自动认证方案 v1.0）。

定位：图形证据闭环的判定层——对 market_pattern_win_rate 统计切片做四闸认定
（闸A BH-FDR/闸B n_eff 折扣/闸C 分 regime 对照/闸D 贝叶斯收缩），产出状态机
certified/probation/failed 与 shrunk_rate 收缩读数，供：
  - PatternWeightSync 消费（shrunk 口径录样本，failed 不调权）
  - 前端图形库页"认证"列（替代人工读表）
  - 未来权重接油门裁定的前置证据

粒度：(pattern_id, timeframe, direction, fwd_window) 池化口径（regime_tag=''），
regime 明细在闸C 内部对照，不落行。引擎：ReplacingMergeTree(certified_at) 全量重放幂等。
"""

from __future__ import annotations

# category_id: market_pattern_certification
# calc_mode: preload（认证任务批算入表；只读消费）
MARKET_PATTERN_CERTIFICATION_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.market_pattern_certification
(
    pattern_id   LowCardinality(String) COMMENT '形态ID(池化口径)',
    timeframe    LowCardinality(String) COMMENT '周期',
    direction    LowCardinality(String) COMMENT '向上|向下',
    fwd_window   UInt8        COMMENT '前视窗口交易日数',
    p_value      Float64      COMMENT '闸A 单侧二项精确检验 p（vs 池化基线，n_eff 折扣口径）',
    q_value      Float64      COMMENT '闸A BH-FDR 调整 q（同族=同 timeframe+direction+fwd_window）',
    n_eff        Float64      COMMENT '闸B 有效样本 n_events/fwd_window',
    shrunk_rate  Float64      COMMENT '闸D 贝叶斯收缩读数 (hits+k·baseline)/(n_eff+k)',
    wilson_lb    Float64      COMMENT 'Wilson 95% 下界（n_eff 口径，对照列）',
    within_regime_edge Float64 COMMENT '闸C 分 regime 加权 edge',
    edge_concentration Float64 COMMENT '闸C 正 edge 单 regime 集中度(≤0.9 过)',
    state        LowCardinality(String) COMMENT 'certified|probation|failed',
    certified_at DateTime64(3, 'UTC') DEFAULT now() COMMENT '认证时间戳(ReplacingMergeTree版本列)'
)
ENGINE = ReplacingMergeTree(certified_at)
PARTITION BY tuple()
ORDER BY (pattern_id, timeframe, direction, fwd_window)
SETTINGS index_granularity = 8192
"""

# 表元数据
TABLE_NAME = "market_pattern_certification"
DATABASE = "c1_market"
CATEGORY_ID = "market_pattern_certification"
CALC_MODE = "preload"
ENGINE = "ReplacingMergeTree(certified_at)"
PARTITION_KEY = "tuple()"
ORDER_BY = "(pattern_id, timeframe, direction, fwd_window)"

# 认证任务 INSERT 列清单（certified_at DEFAULT now() 自动填充）
INSERT_COLUMNS = (
    "(pattern_id, timeframe, direction, fwd_window, "
    "p_value, q_value, n_eff, shrunk_rate, wilson_lb, "
    "within_regime_edge, edge_concentration, state)"
)

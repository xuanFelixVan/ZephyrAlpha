# [BLUEPRINT] MOD-L04-001
# [MODULE] schemas.categories.crypto.crypto_kline_daily
# [DOMAIN] D_DATA
# [DEPENDENCIES] none
# [CONSUMERS] scripts.ch.apply_crypto_shadow_tables_ddl; scripts.data.crypto_kline_collector; scripts.data.crypto_shadow_judge
# [STARTUP] imported
# [MATURITY] testing
# [INVARIANTS] crypto_kline_daily / crypto_shadow_gate 两表 DDL 唯一真源（DDL-as-Code）；本文件 DDL 必须与 ClickHouse 实际表结构一致；影子表只记账不进决策链路（Owner 2026-09-11 免费影子模式裁定，禁接 trading_decision_map / TDM 消费方）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DDL 与 CH 实际表结构不一致->apply_crypto_shadow_tables_ddl.py verify 退出码 1 列出差异；CH 不可达->退出码 2
# [TESTS] scripts/ch/apply_crypto_shadow_tables_ddl.py::verify（部署后引擎一致性核验）
# [TTL] permanent
"""crypto 影子 MVP 两表 DDL-as-Code（category_id: crypto_kline_daily / crypto_shadow_gate）。

背景（Owner 2026-09-11 裁定）：TDM-C-L1~L4 币圈四节点维持空壳，95 号蓝图 Phase 2 付费层不整体立项；
先开"免费影子模式"——每天照常计算影子判定但只记账、不进任何决策、不花钱，
目的=尽早开始积累现货 track record（95 号 Phase 3 要求 ≥3 个月，时间成本不可压缩）。

表清单：
    c1_market.crypto_kline_daily   币圈日线（币安公开镜像 data-api.binance.vision，免费无 key）
    c1_market.crypto_shadow_gate   C-L1 大盘总闸影子判定结果（只记录，不进决策链路）

网络实测（2026-09-11）：OKX 公开 API 域名 DNS 解析失败（www.okx.com / aws.okx.com 均 getaddrinfo failed），
任务书预案"OKX 不可达则降级"触发；实测 binance.vision（币安公开数据镜像，免费无 key）与 Gate.io 公开 API 可达。
95 号蓝图 §一 1.1 原裁定"币安主+OKX 备"，网络实测与该裁定方向一致——主源=binance.vision，
Gate.io 登记为备源（未施工，Phase 2 再接线）。数据口径披露见 docs/_working/2026-09-11-crypto-shadow-mvp.md。

引擎选型：与 c1_market.kline_daily 同款 ReplacingMergeTree（无版本列，重复键后台合并，写侧可重放幂等）。
ingest_ts 审计列（#ARCH-CH-025 惯例）：DEFAULT now() 自动填充，不入 INSERT 列。
"""

from __future__ import annotations

# category_id: crypto_kline_daily
# 数据口径：币安现货 USDT 交易对日线 + ETHBTC 原生汇率对；1D K线 UTC 日界（币圈 7x24 无本地日历）；
# 宇宙口径：24h quote_volume 排名 Top-50 USDT 现货对（采集时点快照，历史日期不重算，影子用途披露在案）
CRYPTO_KLINE_DAILY_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.crypto_kline_daily
(
    trade_date    Date            COMMENT '交易日期(K线 UTC 日界，币圈 7x24)',
    symbol        String          COMMENT '币安现货交易对，如 BTCUSDT/ETHBTC',
    exchange          LowCardinality(String) MATERIALIZED LowCardinality(String) MATERIALIZED 'BINANCE' COMMENT '交易所码(TRAE-082 MATERIALIZED派生,2026-09-12 债清偿)',
    symbol_canonical  String MATERIALIZED String MATERIALIZED if(position(symbol,'.')>0, symbol, concat(replaceRegexpAll(splitByChar('.', symbol)[1], '^(sh|sz|bj|hk)', ''), '.', exchange)) COMMENT 'canonical身份键(TRAE-082 universal,2026-09-12 债清偿)',
    base_asset    LowCardinality(String) DEFAULT '' COMMENT '基础资产，如 BTC/ETH',
    open          Decimal(18,8)   COMMENT '开盘价(USDT)',
    high          Decimal(18,8)   COMMENT '最高价(USDT)',
    low           Decimal(18,8)   COMMENT '最低价(USDT)',
    close         Decimal(18,8)   COMMENT '收盘价(USDT)',
    volume        Decimal(30,8)   COMMENT '成交量(基础资产)',
    quote_volume  Decimal(30,8)   COMMENT '成交额(USDT)',
    trades        UInt64          COMMENT '成交笔数',
    is_universe_eligible UInt8    DEFAULT 0 COMMENT '当日 Top-50 宇宙成员标记(1=成员)',
    universe_rank UInt16          DEFAULT 0  COMMENT '当日 24h quote_volume 排名(1-50，0=非成员/ETHBTC 汇率对)',
    data_source   LowCardinality(String) DEFAULT 'binance_vision' COMMENT '数据来源(data-api.binance.vision 公开镜像，免费无 key)',
    quality_flag  UInt8           DEFAULT 1  COMMENT '质量标记(1=正常 0=异常)',
    ingest_ts     DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳(audit #ARCH-CH-025，审计列非版本列)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, trade_date)
SETTINGS index_granularity = 8192
"""

# category_id: crypto_shadow_gate
# C-L1 大盘总闸影子判定（TDM-C-L1 设计稿三档逻辑；只记录不进决策链路）
# 档位枚举 shadow_tier:
#   trend       趋势档——BTC 站稳 200 日线且 MA200 斜率向上（设计稿）
#   altseason   山寨季进攻档——趋势档成立 且 山寨季比率 ≥0.75（业界口径 75% Top-50 跑赢 BTC/90 日滚动）
#   tighten     收紧档——BTC 收盘跌破 MA200 或 MA200 斜率向下（设计稿"BTC 破位则总闸收紧"）
#   insufficient_history 数据不足——MA200 未满 200 根或 90 日窗口宇宙不足 20 对，影子观察不判档
#   sentiment_only       纯情绪影子——行情源不可达降级，仅恐惧贪婪指数记账（任务书披露预案）
CRYPTO_SHADOW_GATE_DDL = """
CREATE TABLE IF NOT EXISTS c1_market.crypto_shadow_gate
(
    trade_date         Date    COMMENT '判定交易日(UTC)',
    btc_close          Nullable(Decimal(18,8)) COMMENT 'BTC 当日收盘(USDT)',
    ma200              Nullable(Decimal(18,8)) COMMENT 'BTC 200 日均线(收盘价口径)',
    ma_slope_10d       Nullable(Decimal(18,8)) COMMENT 'MA200 十日斜率=ma200(t)-ma200(t-10)',
    altseason_ratio    Nullable(Decimal(8,4))  COMMENT '山寨季比率=Top-50 中 90 日滚动收益跑赢 BTC 的占比(0-1，业界口径 BlockchainCenter Altcoin Season Index)',
    altseason_universe Nullable(UInt16) COMMENT '当日参与比率计算的币对数(有完整 90 日窗口的宇宙成员)',
    eth_btc_ratio      Nullable(Decimal(18,8)) COMMENT 'ETH/BTC 当日收盘(币安原生汇率对，非自算比值)',
    eth_btc_ratio_ma20 Nullable(Decimal(18,8)) COMMENT 'ETH/BTC 20 日均线(设计稿 ALT/BTC 汇率上行佐证口径)',
    fng_value          Nullable(UInt8)  COMMENT '恐惧贪婪指数(0-100，alternative.me 免费源)',
    shadow_tier        LowCardinality(String) COMMENT '影子档位: trend/altseason/tighten/insufficient_history/sentiment_only',
    shadow_reason      String COMMENT '档位判定说明(命中条件+数据局限披露)',
    sentiment_only     UInt8  DEFAULT 0 COMMENT '1=纯情绪影子(行情源不可达降级口径)',
    shadow_version     LowCardinality(String) DEFAULT 'v0.1' COMMENT '判定逻辑版本(逻辑变更须升版本，防 track record 混轨)',
    ingest_ts          DateTime64(3, 'UTC') DEFAULT now() COMMENT '入库时间戳(审计列)'
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date)
SETTINGS index_granularity = 8192
"""

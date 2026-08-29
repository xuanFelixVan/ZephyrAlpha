# [BLUEPRINT] MOD-REGIME-002 | docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md | §5.3 Phase2c
# [MODULE] zephyr.regime.features.regime_data_loader
# [DOMAIN] D_REGIME
# [DEPENDENCIES] numpy; pandas; zephyr.data.ch_reader; zephyr.data.table_registry
# [CONSUMERS] MOD-REGIME-002(RegimeFeatureBuilder透传→risk/overlay构造器消费)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 任一表查询失败返回None(降级友好); 表名经TableRegistry获取(禁止硬编码); 同表首次查询后缓存
# [MODIFY-GUARD] blueprint=docs/03_modules/_domain_regime/regime_feature_builder/blueprint.md
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 查询失败->log warning+返回None(调用方按0.0/1.0降级); 表未注册->KeyError(fail-closed)
# [TESTS] tests/regime/test_regime_data_loader.py
# [A_module] module_id=MOD-REGIME-002 | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [TTL] permanent
# [ARCH-REF] #10_regime_detector_spec §5.3 #MOD-REGIME-002 #Phase2c
"""Phase 2c 新数据源加载层（MOD-REGIME-002 Phase 2c）。

为 4 个 T3 stub 维度（money_effect/mainline/leader/one_day_mainline）、#8 siphon、
合成 VIX、多分时共振提供 ClickHouse 数据加载。经 RegimeFeatureBuilder 透传 + 缓存，
供 RiskSignalConstructor / OverlaySignalsConstructor 复用，避免重复查询。

设计原则（与 RegimeFeatureBuilder._load_index_kline 一致）：
  - **表名经 TableRegistry**：通过 get_registry().table(category_id) 获取全限定表名，
    禁止硬编码（fail-closed，与 #ARCH-CH-024 一致）。
  - **降级友好**：任一表查询失败 → log warning + 返回 None（调用方按 0.0/1.0 降级），
    保证 risk/overlay 只因真实信号触发，不因数据空洞误杀。
  - **单例式缓存**：同表首次查询后缓存全序列 DataFrame，后续 O(1)。
  - **PIT 由调用方负责**：本模块只加载数据，shift(1) 在构造器 _precompute 统一做。

数据源（6 类，均已在 business_data_categories.yaml 注册）:
  - money_flow         → 全市场聚合主力净流入（money_effect 维度）
  - kline_sector       → 行业板块K线（mainline 维度 + #8 sector_hhi）
  - limit_up_down      → 涨跌停统计（leader/one_day_mainline 维度）
  - hk_connect_flow    → 北向资金（money_effect 辅助）
  - option_iv_surface  → 50ETF/300ETF 期权IV曲面（合成VIX）
  - etf_kline_30/60min → ETF分钟K线（多分时共振 #9）

依据: 10_regime_detector_spec v1.3.1 §5.3 / Phase 2c 计划 §核心架构
Version: 0.1.0
"""

from __future__ import annotations

import logging
from typing import Any, Callable, Final

import pandas as pd

from zephyr.data import ch_reader
from zephyr.data.table_registry import get_registry

_logger = logging.getLogger(__name__)

# 多分时共振用的 ETF 代码（510300=沪深300ETF，作为 000300 指数分钟级代理）
_MULTI_TF_ETF = "510300"
# 合成 VIX 用的期权标的
_VIX_UNDERLYINGS: Final = ["510050", "510300"]
# S2 估值路A 用的指数代码（沪深300，与市场代理 MARKET_PROXY 口径一致）
_INDEX_VALUATION_SYMBOL: Final = "000300"

# ── NLP 关键词字典（P1-E3 MVP：关键词情感分析，无 GPU 降级方案）──
# 利好关键词（正面情绪）
_POSITIVE_KEYWORDS: Final = [
    "降准",
    "降息",
    "减税",
    "利好",
    "增长",
    "盈利",
    "回购",
    "增持",
    "重组",
    "并购",
    "改革",
    "投资",
    "基建",
    "补贴",
    "扶持",
    "刺激",
    "支持",
    "上涨",
    "突破",
    "回暖",
    "复苏",
    "企稳",
    "反弹",
]
# 利空关键词（负面情绪）
_NEGATIVE_KEYWORDS: Final = [
    "跌停",
    "暴跌",
    "下跌",
    "利空",
    "亏损",
    "减持",
    "违规",
    "处罚",
    "退市",
    "爆雷",
    "违约",
    "下修",
    "下调",
    "风险",
    "警告",
    "监管",
    "限售",
    "解禁",
    "商誉减值",
    "业绩变脸",
    "诉讼",
    "熔断",
    "跳水",
    "崩盘",
    "恐慌",
    "抛售",
]
# 政策关键词（政策面信号）
_POLICY_KEYWORDS: Final = [
    "央行",
    "证监会",
    "国务院",
    "财政部",
    "发改委",
    "政策",
    "规定",
    "通知",
    "指导意见",
    "监管",
    "放宽",
    "限制",
    "会议",
    "部署",
]


def parse_tsv(tsv: str, ncols: int) -> list[list[str]]:
    """把 ch_reader.query 返回的 TSV 字符串解析成行列表。

    公共工具函数——regime 包内 ``regime_feature_builder`` 等模块统一 import 此实现，
    避免多副本触发 CloneGuard extract 级硬阻断。

    ncols: 期望列数（不足则跳过该行）。空输入返回 []。
    """
    if not tsv or not tsv.strip():
        return []
    rows: list[list[str]] = []
    for line in tsv.strip().split("\n"):
        line = line.rstrip("\r")
        if not line:
            continue
        vals = line.split("\t")
        if len(vals) >= ncols:
            rows.append(vals)
    return rows


def safe_float(v: Any) -> float:
    """NaN/None 安全转 float（NaN→0.0，避免阈值比较误判）。

    公共工具函数——regime 包内 ``regime_feature_builder`` 等模块统一 import 此实现，
    避免多副本触发 CloneGuard extract 级硬阻断。
    """
    if v is None:
        return 0.0
    try:
        f = float(v)
        return 0.0 if f != f else f  # NaN → 0.0
    except (TypeError, ValueError):
        return 0.0


class RegimeDataLoader:
    """Phase 2c 新数据源加载层。

    Usage（由 RegimeFeatureBuilder 注入，透传给构造器）::

        loader = RegimeDataLoader(
            data_load_start="2010-01-01", backtest_end="2026-06-30"
        )
        money_flow = loader.load_money_flow()        # → DataFrame | None
        sector = loader.load_sector_kline()          # → DataFrame | None

    降级: 任一表查询失败返回 None（调用方按 0.0/1.0 降级），log warning 不抛错。
    """

    def __init__(
        self,
        data_load_start: str = "2010-01-01",
        backtest_end: str = "2026-06-30",
        registry: Any = None,
    ) -> None:
        """初始化。

        Args:
            data_load_start: 数据加载起始日（需早于 backtest_start，供 warmup）。
            backtest_end: 数据加载结束日（含）。
            registry: TableRegistry 实例（None 时用单例 get_registry()）。
        """
        self.data_load_start = data_load_start
        self.backtest_end = backtest_end
        self._registry = registry or get_registry()
        self._cache: dict[str, pd.DataFrame | None] = {}

    # ── 内部工具 ──────────────────────────────────────────────────────────

    def _query(self, sql: str, context: str) -> str:
        """执行 ClickHouse 查询，失败返回空串（降级友好，不抛错）。"""
        try:
            return ch_reader.query(sql)
        except Exception as exc:  # noqa: BLE001 — 降级友好
            _logger.warning("ClickHouse 查询失败 (%s): %s", context, exc)
            return ""

    def _load_or_cache(self, cache_key: str, loader_fn: Callable[[], pd.DataFrame | None]) -> pd.DataFrame | None:
        """缓存式加载：首次调用执行 loader_fn 并缓存，后续直接返回缓存。"""
        if cache_key in self._cache:
            return self._cache[cache_key]
        try:
            df = loader_fn()
        except Exception as exc:  # noqa: BLE001 — 降级友好
            _logger.warning("加载 %s 失败，降级 None: %s", cache_key, exc)
            df = None
        self._cache[cache_key] = df
        return df

    # ── 公共接口 ──────────────────────────────────────────────────────────

    def load_money_flow(self) -> pd.DataFrame | None:
        """全市场按 trade_date 聚合的主力资金净流入。

        Returns:
            DataFrame(index=trade_date, cols=[total_main_net_inflow, avg_main_net_inflow_pct])
            或 None（查询失败降级）。供 t3_money_effect_score + money_effect 维度用。
        """
        return self._load_or_cache("money_flow", self._load_money_flow)

    def load_sector_kline(self) -> pd.DataFrame | None:
        """行业板块K线（code/trade_date/OHLCV）。

        Returns:
            MultiIndex(code, trade_date) DataFrame，含 close/volume/amount。
            供 t3_mainline_score + #8 sector_hhi 用。或 None。
        """
        return self._load_or_cache("sector_kline", self._load_sector_kline)

    def load_limit_up_down(self) -> pd.DataFrame | None:
        """涨跌停统计（symbol/trade_date/limit_type/pct_change）。

        Returns:
            MultiIndex(trade_date, symbol) DataFrame，含 limit_type/pct_change/amount。
            供 t3_leader_score + t3_one_day_mainline_flag 用。或 None。
        """
        return self._load_or_cache("limit_up_down", self._load_limit_up_down)

    def load_hk_connect_flow(self) -> pd.DataFrame | None:
        """北向资金（trade_date 聚合的净买入额）。

        Returns:
            DataFrame(index=trade_date, cols=[net_buy_amount, daily_inflow]) 或 None。
            供 t3_money_effect_score 辅助用。
        """
        return self._load_or_cache("hk_connect_flow", self._load_hk_connect_flow)

    def load_option_iv_surface(self) -> pd.DataFrame | None:
        """50ETF+300ETF 期权 IV 曲面（双标的）。

        Returns:
            MultiIndex(trade_date, underlying) DataFrame，含 strike/expiry/iv/option_type/delta/vega。
            供合成 VIX 用。或 None。
        """
        return self._load_or_cache("option_iv_surface", self._load_option_iv)

    def load_multi_tf_kline(self) -> dict[str, pd.DataFrame] | None:
        """多分时 ETF K 线（60min/30min，510300）。

        Returns:
            {"60min": df, "30min": df}，每个 df 是 index=trade_date 的 OHLCV。
            供 #9 多分时共振 KDJ 用。或 None（全部失败）。
        """
        return self._load_or_cache("multi_tf_kline", self._load_multi_tf_kline)

    def load_news_sentiment(self) -> pd.DataFrame | None:
        """新闻情感聚合（P1-E3 MVP：关键词字典情感分析）。

        从 c3_fundamental.news_data 表按日聚合，用 ClickHouse multiSearchAny
        做服务端关键词匹配，返回每日正/负面/政策新闻计数。

        Returns:
            DataFrame(index=trade_date, cols=[total_count, positive_count,
            negative_count, policy_count]) 或 None。供 S2 policy/bad_news_flat 用。
        """
        return self._load_or_cache("news_sentiment", self._load_news_sentiment)

    def load_index_valuation(self) -> pd.DataFrame | None:
        """指数估值日频（S2 估值路A：CAPE/PB/ERP 分位，2026-08-29 S2 治本方案 §5.4）。

        Returns:
            DataFrame(index=trade_date, cols=[pe_ttm, cape_5y, cape_5y_pct, pe_pct,
            pb_pct, erp, erp_pct]) 或 None（查询失败/无数据降级，
            调用方 overlay S2 valuation 回退路B s2_valuation_score(close)）。
        """
        return self._load_or_cache("index_valuation", self._load_index_valuation)

    # ── 实际加载逻辑 ──────────────────────────────────────────────────────

    def _load_money_flow(self) -> pd.DataFrame | None:
        table = self._registry.table("market_money_flow")
        sql = (
            f"SELECT trade_date, "
            f"sum(toFloat64(main_net_inflow)) AS total_main_net_inflow, "
            f"avg(toFloat64(main_net_inflow_pct)) AS avg_main_net_inflow_pct "
            f"FROM {table} FINAL "
            f"WHERE trade_date >= toDate('{self.data_load_start}') "
            f"AND trade_date <= toDate('{self.backtest_end}') "
            f"GROUP BY trade_date ORDER BY trade_date"
        )
        tsv = self._query(sql, "money_flow")
        rows = parse_tsv(tsv, ncols=3)
        if not rows:
            _logger.warning("money_flow 无数据，money_effect 维度将降级 0.0")
            return None
        df = pd.DataFrame(rows, columns=["trade_date", "total_main_net_inflow", "avg_main_net_inflow_pct"])
        df["trade_date"] = pd.to_datetime(df["trade_date"])
        df["total_main_net_inflow"] = pd.to_numeric(df["total_main_net_inflow"], errors="coerce")
        df["avg_main_net_inflow_pct"] = pd.to_numeric(df["avg_main_net_inflow_pct"], errors="coerce")
        return df.set_index("trade_date").sort_index()

    def _load_sector_kline(self) -> pd.DataFrame | None:
        table = self._registry.table("market_sector_kline")
        sql = (
            f"SELECT trade_date, code, close, volume, amount "
            f"FROM {table} FINAL "
            f"WHERE trade_date >= toDate('{self.data_load_start}') "
            f"AND trade_date <= toDate('{self.backtest_end}') "
            f"ORDER BY code, trade_date"
        )
        tsv = self._query(sql, "sector_kline")
        rows = parse_tsv(tsv, ncols=5)
        if not rows:
            _logger.warning("kline_sector 无数据，mainline/sector_hhi 将降级")
            return None
        df = pd.DataFrame(rows, columns=["trade_date", "code", "close", "volume", "amount"])
        df["trade_date"] = pd.to_datetime(df["trade_date"])
        df["close"] = pd.to_numeric(df["close"], errors="coerce")
        df["volume"] = pd.to_numeric(df["volume"], errors="coerce")
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        # 去重：ClickHouse FINAL 可能残留重复 (trade_date, code) 对，致 unstack("code") 报
        # "Index contains duplicate entries, cannot reshape"（P1-E5 修复，2026-08-08）
        df = df.drop_duplicates(subset=["trade_date", "code"], keep="last")
        return df.set_index(["code", "trade_date"]).sort_index()

    def _load_limit_up_down(self) -> pd.DataFrame | None:
        table = self._registry.table("market_limit_up_down")
        sql = (
            f"SELECT trade_date, symbol, limit_type, pct_change, amount "
            f"FROM {table} FINAL "
            f"WHERE trade_date >= toDate('{self.data_load_start}') "
            f"AND trade_date <= toDate('{self.backtest_end}') "
            f"ORDER BY trade_date, symbol"
        )
        tsv = self._query(sql, "limit_up_down")
        rows = parse_tsv(tsv, ncols=5)
        if not rows:
            # Fallback: limit_up_down 表仅有近期数据（2026-07+），回测窗口内无数据
            # 从 kline_daily 派生涨跌停（P1-E5 补数据，2026-08-08）
            _logger.info("limit_up_down 表无回测窗口数据，从 kline_daily 派生涨跌停")
            return self._derive_limit_up_down_from_kline()
        df = pd.DataFrame(rows, columns=["trade_date", "symbol", "limit_type", "pct_change", "amount"])
        df["trade_date"] = pd.to_datetime(df["trade_date"])
        df["pct_change"] = pd.to_numeric(df["pct_change"], errors="coerce")
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        return df.set_index(["trade_date", "symbol"]).sort_index()

    def _derive_limit_up_down_from_kline(self) -> pd.DataFrame | None:
        """从 kline_daily 派生涨跌停数据（limit_up_down 表数据不足时的 fallback）。

        规则：
          - pct_change >= 9.5 → "涨停"（10% 板，含误差容限）
          - pct_change <= -9.5 → "跌停"
          - 仅 A_share, quality_flag=1

        注意：ST(5%)、创业板/科创板(20%)、北交所(30%) 的涨跌停阈值不同，
        此派生仅捕获 10% 板涨跌停，覆盖率约 70%（MVP 可接受）。
        """
        table = self._registry.table("market_kline_daily")
        sql = (
            f"SELECT trade_date, symbol, "
            f"multiIf(toFloat64(pct_change) >= 9.5, '涨停', "
            f"toFloat64(pct_change) <= -9.5, '跌停', '') AS limit_type, "
            f"toFloat64(pct_change) AS pct_change, "
            f"toFloat64(amount) AS amount "
            f"FROM {table} FINAL "
            f"WHERE market_type = 'A_share' AND quality_flag = 1 "
            f"AND (toFloat64(pct_change) >= 9.5 OR toFloat64(pct_change) <= -9.5) "
            f"AND trade_date >= toDate('{self.data_load_start}') "
            f"AND trade_date <= toDate('{self.backtest_end}') "
            f"ORDER BY trade_date, symbol"
        )
        tsv = self._query(sql, "limit_up_down (derived from kline_daily)")
        rows = parse_tsv(tsv, ncols=5)
        if not rows:
            _logger.warning("kline_daily 派生涨跌停也无数据，leader/one_day_mainline 将降级")
            return None
        df = pd.DataFrame(rows, columns=["trade_date", "symbol", "limit_type", "pct_change", "amount"])
        df["trade_date"] = pd.to_datetime(df["trade_date"])
        df["pct_change"] = pd.to_numeric(df["pct_change"], errors="coerce")
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
        df = df.drop_duplicates(subset=["trade_date", "symbol"], keep="last")
        _logger.info(
            "从 kline_daily 派生涨跌停: %d 行, %s~%s",
            len(df),
            df["trade_date"].min(),
            df["trade_date"].max(),
        )
        return df.set_index(["trade_date", "symbol"]).sort_index()

    def _load_hk_connect_flow(self) -> pd.DataFrame | None:
        table = self._registry.table("market_hk_connect_flow")
        sql = (
            f"SELECT trade_date, "
            f"sum(toFloat64(net_buy_amount)) AS net_buy_amount, "
            f"sum(toFloat64(daily_inflow)) AS daily_inflow "
            f"FROM {table} FINAL "
            f"WHERE trade_date >= toDate('{self.data_load_start}') "
            f"AND trade_date <= toDate('{self.backtest_end}') "
            f"GROUP BY trade_date ORDER BY trade_date"
        )
        tsv = self._query(sql, "hk_connect_flow")
        rows = parse_tsv(tsv, ncols=3)
        if not rows:
            _logger.warning("hk_connect_flow 无数据，money_effect 辅助维度将降级")
            return None
        df = pd.DataFrame(rows, columns=["trade_date", "net_buy_amount", "daily_inflow"])
        df["trade_date"] = pd.to_datetime(df["trade_date"])
        df["net_buy_amount"] = pd.to_numeric(df["net_buy_amount"], errors="coerce")
        df["daily_inflow"] = pd.to_numeric(df["daily_inflow"], errors="coerce")
        return df.set_index("trade_date").sort_index()

    def _load_option_iv(self) -> pd.DataFrame | None:
        table = self._registry.table("market_option_iv")
        underlyings = ", ".join([f"'{u}'" for u in _VIX_UNDERLYINGS])
        sql = (
            f"SELECT trade_date, underlying, strike, expiry, iv, option_type, delta, vega "
            f"FROM {table} FINAL "
            f"WHERE underlying IN ({underlyings}) "
            f"AND trade_date >= toDate('{self.data_load_start}') "
            f"AND trade_date <= toDate('{self.backtest_end}') "
            f"AND quality_flag = 1 "
            f"ORDER BY underlying, trade_date, expiry, strike"
        )
        tsv = self._query(sql, "option_iv_surface")
        rows = parse_tsv(tsv, ncols=8)
        if not rows:
            _logger.warning("option_iv_surface 无数据，合成VIX将降级回退 vol_pct")
            return None
        df = pd.DataFrame(
            rows, columns=["trade_date", "underlying", "strike", "expiry", "iv", "option_type", "delta", "vega"]
        )
        df["trade_date"] = pd.to_datetime(df["trade_date"])
        df["expiry"] = pd.to_datetime(df["expiry"])
        for c in ["strike", "iv", "delta", "vega"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        return df.set_index(["trade_date", "underlying"]).sort_index()

    def _load_multi_tf_kline(self) -> dict[str, pd.DataFrame] | None:
        """加载 60min + 30min ETF K 线（510300）。"""
        out: dict[str, pd.DataFrame] = {}
        cat_map = {"60min": "market_etf_kline_60min", "30min": "market_etf_kline_30min"}
        for freq, cid in cat_map.items():
            df = self._load_single_etf_kline(cid, freq)
            if df is not None:
                out[freq] = df
        if not out:
            _logger.warning("multi_tf_kline 全部无数据，#9 多分时共振将降级单分时")
            return None
        return out

    def _load_single_etf_kline(self, category_id: str, freq: str) -> pd.DataFrame | None:
        """加载单频 ETF K 线（510300）。"""
        table = self._registry.table(category_id)
        sql = (
            f"SELECT trade_date, open, high, low, close, volume "
            f"FROM {table} FINAL "
            f"WHERE symbol = '{_MULTI_TF_ETF}' "
            f"AND trade_date >= toDate('{self.data_load_start}') "
            f"AND trade_date <= toDate('{self.backtest_end}') "
            f"ORDER BY trade_date"
        )
        tsv = self._query(sql, f"etf_kline_{freq}")
        rows = parse_tsv(tsv, ncols=6)
        if not rows:
            return None
        df = pd.DataFrame(rows, columns=["trade_date", "open", "high", "low", "close", "volume"])
        df["trade_date"] = pd.to_datetime(df["trade_date"])
        for c in ["open", "high", "low", "close", "volume"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        # 分钟级数据按交易日聚合（取当日最后 bar 的 OHLCV，供日线级 KDJ 用）
        df = df.set_index("trade_date").sort_index()
        return df

    def _load_news_sentiment(self) -> pd.DataFrame | None:
        """从 news_data 表按日聚合新闻情感（关键词匹配）。

        用 ClickHouse multiSearchAny 做服务端关键词匹配，返回每日
        正/负面/政策新闻计数，供 S2 policy/bad_news_flat 维度用。

        性能：ClickHouse 对 10M 行 GROUP BY + multiSearchAny 约 5-10 秒。
        """
        table = self._registry.table("fund_news_data")
        pos_list = ", ".join([f"'{k}'" for k in _POSITIVE_KEYWORDS])
        neg_list = ", ".join([f"'{k}'" for k in _NEGATIVE_KEYWORDS])
        pol_list = ", ".join([f"'{k}'" for k in _POLICY_KEYWORDS])
        sql = (
            f"SELECT toDate(publish_time) AS trade_date, "
            f"count() AS total_count, "
            f"countIf(multiSearchAny(title, [{pos_list}])) AS positive_count, "
            f"countIf(multiSearchAny(title, [{neg_list}])) AS negative_count, "
            f"countIf(multiSearchAny(title, [{pol_list}])) AS policy_count "
            f"FROM {table} "
            f"WHERE region = 'CN' AND language = 'zh' "
            f"AND publish_time >= toDateTime('{self.data_load_start} 00:00:00') "
            f"AND publish_time <= toDateTime('{self.backtest_end} 23:59:59') "
            f"GROUP BY trade_date "
            f"ORDER BY trade_date"
        )
        tsv = self._query(sql, "news_sentiment")
        rows = parse_tsv(tsv, ncols=5)
        if not rows:
            _logger.warning("news_sentiment 无数据，policy/bad_news_flat 将降级 0.0")
            return None
        df = pd.DataFrame(
            rows,
            columns=["trade_date", "total_count", "positive_count", "negative_count", "policy_count"],
        )
        df["trade_date"] = pd.to_datetime(df["trade_date"])
        for c in ["total_count", "positive_count", "negative_count", "policy_count"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        _logger.info(
            "news_sentiment 加载: %d 日, %s~%s, 日均 %d 条",
            len(df),
            df["trade_date"].min().date(),
            df["trade_date"].max().date(),
            int(df["total_count"].mean()),
        )
        return df.set_index("trade_date").sort_index()

    def _load_index_valuation(self) -> pd.DataFrame | None:
        """加载指数估值日频（c1_market.index_valuation_daily，市场代理 000300）。

        列：pe_ttm / cape_5y / cape_5y_pct / pe_pct / pb_pct / erp / erp_pct。
        消费端语义：cape_5y_pct/pb_pct/erp_pct 为全历史扩展窗分位（0~1），
        erp 为百分数小数口径（0.052=5.2%），供 s2_valuation_score_fundamental。
        """
        table = self._registry.table("market_index_valuation_daily")
        sql = (
            f"SELECT trade_date, pe_ttm, cape_5y, cape_5y_pct, pe_pct, pb_pct, erp, erp_pct "
            f"FROM {table} FINAL "
            f"WHERE symbol = '{_INDEX_VALUATION_SYMBOL}' "
            f"AND trade_date >= toDate('{self.data_load_start}') "
            f"AND trade_date <= toDate('{self.backtest_end}') "
            f"ORDER BY trade_date"
        )
        tsv = self._query(sql, "index_valuation")
        rows = parse_tsv(tsv, ncols=8)
        if not rows:
            _logger.warning("index_valuation_daily 无数据，S2 valuation 将降级路B（close 回撤代理）")
            return None
        df = pd.DataFrame(
            rows,
            columns=["trade_date", "pe_ttm", "cape_5y", "cape_5y_pct", "pe_pct", "pb_pct", "erp", "erp_pct"],
        )
        df["trade_date"] = pd.to_datetime(df["trade_date"])
        for c in ["pe_ttm", "cape_5y", "cape_5y_pct", "pe_pct", "pb_pct", "erp", "erp_pct"]:
            df[c] = pd.to_numeric(df[c], errors="coerce")
        # 去重：FINAL 仍可能残留同键重复（同 P1-E5 sector_kline 修复口径）
        df = df.drop_duplicates(subset=["trade_date"], keep="last")
        return df.set_index("trade_date").sort_index()


__all__: Final = ["RegimeDataLoader", "safe_float", "parse_tsv"]

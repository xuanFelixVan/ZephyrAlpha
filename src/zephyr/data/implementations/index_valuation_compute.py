# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.index_valuation_compute
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.ch_reader; zephyr.data.table_registry
# [CONSUMERS] zephyr.data.scheduler (source=internal 分支，capability=index_valuation_daily)
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 内部计算 Provider——读 CH 指数估值原始数据→本地计算 CAPE/分位/ERP→返回 FetchResult
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] fetch 失败→返回 FetchResult(error=...) 不抛；CH 读取失败→返回空结果+error
# [TESTS] tests/zephyr/data/test_index_valuation_compute.py
# [A_module] module_id=MOD-L00-004-IDXVAL | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""指数估值内部计算 Provider（S2 路A 管道，2026-08-28 S2 治本方案 §5.2）。

区别于外部数据源 Provider（akshare 采集 PE_TTM 原始值），本 Provider 负责：
  1. 从 c1_market.index_valuation_daily 读取已落库的 PE_TTM/股息率原始序列
  2. 从 c1_market.kline_index 读取指数 close（CAPE 分子 P_t）
  3. 从 c1_market.macro_data 读取 CPI（真 CAPE 通胀调整）和 10Y 国债收益率（ERP）
  4. 计算真 CAPE（5 年通胀调整）、全历史分位、ERP
  5. 返回 FetchResult（含全部计算列），由上层 scheduler 写回 index_valuation_daily

真 CAPE 口径（Owner 已裁定④，拒绝 PE 中位平滑近似）：
    E_i = P_i / PE_i（指数点位 / PE_TTM，指数盈利代理）
    real_E_i = E_i / CPI_i（通胀调整，CPI 为月度，日频前向填充）
    CAPE_t = P_t / mean_{近5年}(real_E × CPI_t)
    窗口：1250 交易日（约 5 年），min_periods=750（3 年，防 warmup 期全 NaN）

ERP 口径：
    erp = 1/PE_TTM - 10Y国债收益率（百分数口径，如 0.052 = 5.2%）
    10Y 国债源：c1_market.macro_data indicator_name='国债_10年'（akshare bond_china_yield）

分位口径：
    全历史扩展窗分位（expanding percentile），非滚动窗口。
    与 s2_valuation_score_fundamental 消费端语义一致（危机期分位<25%→60 分）。
"""

from __future__ import annotations

import datetime
import logging
import time
from typing import Final, Iterator

import numpy as np
import pandas as pd

from zephyr.data.provider_base import (
    CapabilityContract,
    FetchPayload,
    FetchResult,
    IngestProviderBase,
    IngestProviderMeta,
)

log = logging.getLogger(__name__)

# 指数估值计算默认标的（S2 消费方）
_DEFAULT_SYMBOLS: Final = ["000300", "000905", "399006"]

# CAPE 窗口：1250 交易日 ≈ 5 年
_CAPE_WINDOW: Final = 1250
# 最小窗口：750 交易日 ≈ 3 年（防 warmup 期全 NaN）
_CAPE_MIN_PERIODS: Final = 750


class IndexValuationComputeProvider(IngestProviderBase):
    """指数估值内部计算 Provider（CAPE/分位/ERP）。

    用法（由 scheduler 自动调用，source=internal, capability=index_valuation_daily）：
        provider = IndexValuationComputeProvider()
        provider.connect()
        for result in provider.fetch(payload, policy):
            # result.rows 含 cape_5y/cape_5y_pct/pe_pct/erp/erp_pct 等计算列
            ...
        provider.disconnect()
    """

    source_name = "internal"
    meta = IngestProviderMeta(
        name="internal",
        display_name="内部计算（指数估值）",
        auth_type="anonymous",
        requires_process=False,
        thread_safety="shared",
        rate_limit_default=0,  # 不限流（本地计算）
        capabilities=[
            CapabilityContract("index_valuation_daily", supports_symbols_null=True),
        ],
        known_issues=[],
    )

    # 输出行列顺序（与 schemas/categories/market_index_valuation_daily.py INSERT_COLUMNS 对齐）
    _COLUMNS: Final = [
        "trade_date",
        "symbol",
        "pe_ttm",
        "pb_mrq",
        "dividend_yield",
        "cape_5y",
        "cape_5y_pct",
        "pe_pct",
        "pb_pct",
        "erp",
        "erp_pct",
        "broken_net_ratio",
        "buffett_ratio",
        "data_source",
    ]

    def connect(self) -> None:
        """建立连接——内部计算无需外部连接，直接标记为已连接。"""
        self._connected = True
        self._log.info("IndexValuationComputeProvider 已就绪（本地计算，无需外部连接）")

    def health_check(self) -> bool:
        """探活——检查 ClickHouse 是否可访问。"""
        if not self._connected:
            return False
        try:
            from zephyr.data import ch_reader

            result = ch_reader.count("c1_market.index_valuation_daily", limit=1)
            return result >= 0
        except Exception as e:  # noqa: BLE001
            self._log.warning("健康检查失败: %s", e)
            return False

    def disconnect(self) -> None:
        """关闭连接——内部计算无需关闭。"""
        self._connected = False

    def fetch(self, payload: FetchPayload, policy) -> Iterator[FetchResult]:
        """从 CH 读原始估值数据→计算 CAPE/分位/ERP→返回 FetchResult。

        流程：
        1. 读 index_valuation_daily 已有 PE_TTM/close 序列（payload.start~payload.end）
        2. 读 kline_index close（CAPE 分子）
        3. 读 macro_data CPI（通胀调整）和 10Y 国债（ERP）
        4. 计算真 CAPE（5 年通胀调整）+ 全历史分位 + ERP
        5. 合并返回 FetchResult（全列含原始+计算列）

        Args:
            payload: 下载请求。payload.table 应为 c1_market.index_valuation_daily。
                payload.symbols=None 表示默认标的（000300/000905/399006）。
                payload.start/end 为日期范围。
            policy: 调用策略（本 Provider 不限流，policy 仅用于接口兼容）

        Yields:
            FetchResult：每标的为一批（避免单批过大）
        """
        start_time = time.monotonic()
        table = payload.table
        last_key = payload.end.isoformat()

        symbols = payload.symbols if payload.symbols else list(_DEFAULT_SYMBOLS)

        for sym in symbols:
            try:
                rows = self._compute_one_symbol(sym, payload.start, payload.end)
            except Exception as e:  # noqa: BLE001
                self._log.error("指数估值计算异常 symbol=%s: %s", sym, e)
                yield FetchResult(
                    table=table,
                    columns=self._COLUMNS,
                    rows=[],
                    last_key=last_key,
                    elapsed_sec=time.monotonic() - start_time,
                    error=f"{sym}: {e}",
                )
                continue

            yield FetchResult(
                table=table,
                columns=self._COLUMNS,
                rows=rows,
                last_key=last_key,
                elapsed_sec=time.monotonic() - start_time,
                rows_fetched=len(rows),
                error=None,
            )

    def _compute_one_symbol(
        self, symbol: str, start: datetime.date, end: datetime.date
    ) -> list[tuple]:
        """计算单只指数的 CAPE/分位/ERP 并返回行列表。

        数据源：
          - index_valuation_daily: PE_TTM（已落库原始序列）
          - kline_index: close（CAPE 分子）
          - macro_data: CPI（indicator_name='CPI' 或 '中国CPI月率报告'）和 10Y 国债
        """
        from zephyr.data import ch_reader

        # 1. 读 index_valuation_daily 已有 PE_TTM 序列
        sql_pe = (
            f"SELECT trade_date, pe_ttm, dividend_yield "
            f"FROM c1_market.index_valuation_daily FINAL "
            f"WHERE symbol = '{symbol}' "
            f"AND trade_date >= '{start.isoformat()}' AND trade_date <= '{end.isoformat()}' "
            f"ORDER BY trade_date"
        )
        tsv_pe = ch_reader.query(sql_pe)
        pe_df = self._parse_tsv(tsv_pe, ["trade_date", "pe_ttm", "dividend_yield"])
        if pe_df.empty:
            self._log.warning("index_valuation_daily 无数据 symbol=%s [%s~%s]", symbol, start, end)
            return []

        # 2. 读 kline_index close（CAPE 分子）
        sql_close = (
            f"SELECT trade_date, close "
            f"FROM c1_market.kline_index FINAL "
            f"WHERE symbol = '{symbol}' "
            f"AND trade_date >= '{start.isoformat()}' AND trade_date <= '{end.isoformat()}' "
            f"ORDER BY trade_date"
        )
        tsv_close = ch_reader.query(sql_close)
        close_df = self._parse_tsv(tsv_close, ["trade_date", "close"])
        if close_df.empty:
            self._log.warning("kline_index 无数据 symbol=%s [%s~%s]", symbol, start, end)
            return []

        # 合并 PE + close（inner join，仅保留双源都有数据的交易日）
        df = pd.merge(pe_df, close_df, on="trade_date", how="inner")
        df = df.sort_values("trade_date").reset_index(drop=True)
        df["trade_date"] = pd.to_datetime(df["trade_date"])
        df["pe_ttm"] = pd.to_numeric(df["pe_ttm"], errors="coerce")
        df["close"] = pd.to_numeric(df["close"], errors="coerce")
        df["dividend_yield"] = pd.to_numeric(df["dividend_yield"], errors="coerce")

        # 3. 读 CPI（月度，通胀调整）
        cpi_series = self._load_cpi_series(start, end)

        # 4. 读 10Y 国债收益率（ERP）
        bond_series = self._load_bond_10y_series(start, end)

        # 5. 计算真 CAPE
        cape_5y = self._compute_cape_5y(df, cpi_series)

        # 6. 计算分位（全历史扩展窗）
        pe_pct = self._expanding_percentile(df["pe_ttm"])
        cape_5y_pct = self._expanding_percentile(cape_5y)

        # 7. 计算 ERP
        erp = self._compute_erp(df["pe_ttm"], bond_series)
        erp_pct = self._expanding_percentile(erp)

        # 8. 组装行
        rows: list[tuple] = []
        for i, row in df.iterrows():
            rows.append(
                (
                    row["trade_date"].date(),
                    symbol,
                    self._safe_float(row["pe_ttm"]),
                    None,  # pb_mrq（一期暂缺）
                    self._safe_float(row["dividend_yield"]),
                    self._safe_float(cape_5y.iloc[i]),
                    self._safe_float(cape_5y_pct.iloc[i]),
                    self._safe_float(pe_pct.iloc[i]),
                    None,  # pb_pct（一期暂缺）
                    self._safe_float(erp.iloc[i]),
                    self._safe_float(erp_pct.iloc[i]),
                    None,  # broken_net_ratio（二期预留）
                    None,  # buffett_ratio（二期预留）
                    "internal_compute",
                )
            )
        return rows

    # ── 数据加载 ──────────────────────────────────────────────────────────

    @staticmethod
    def _parse_tsv(tsv: str, columns: list[str]) -> pd.DataFrame:
        """解析 ch_reader.query 返回的 TSV 字符串为 DataFrame。"""
        if not tsv or not tsv.strip():
            return pd.DataFrame(columns=columns)
        rows = []
        for line in tsv.strip().split("\n"):
            vals = line.rstrip("\r").split("\t")
            if len(vals) >= len(columns):
                rows.append(vals[: len(columns)])
        return pd.DataFrame(rows, columns=columns)

    def _load_cpi_series(self, start: datetime.date, end: datetime.date) -> pd.Series:
        """加载 CPI 月度序列并前向填充到日频。

        源优先级：
          1. c1_market.macro_data indicator_name='CPI'（akshare macro_china_cpi，月频）
          2. c1_market.macro_data indicator_name='中国CPI月率报告'（akshare macro_china_cpi_monthly）
        CPI 为月率（如 0.4 = 0.4%），CAPE 计算用累计 CPI 指数（以 2010-01 为基期=100）。
        """
        from zephyr.data import ch_reader

        # 尝试两种 CPI 指标名（akshare 不同接口命名）
        for indicator in ("CPI", "中国CPI月率报告"):
            sql = (
                f"SELECT report_date, indicator_value "
                f"FROM c1_market.macro_data FINAL "
                f"WHERE indicator_name = '{indicator}' "
                f"AND report_date >= '{start.isoformat()}' AND report_date <= '{end.isoformat()}' "
                f"ORDER BY report_date"
            )
            tsv = ch_reader.query(sql)
            df = self._parse_tsv(tsv, ["report_date", "indicator_value"])
            if not df.empty:
                break
        else:
            self._log.warning("CPI 数据缺失，真 CAPE 将退化为名义 CAPE（不调整通胀）")
            return pd.Series(dtype=float)

        df["report_date"] = pd.to_datetime(df["report_date"])
        df["indicator_value"] = pd.to_numeric(df["indicator_value"], errors="coerce")
        # CPI 月率 → 累计 CPI 指数（基期=第一个有效值）
        df = df.dropna(subset=["indicator_value"])
        if df.empty:
            return pd.Series(dtype=float)
        df = df.set_index("report_date").sort_index()
        # 月率转累计指数：cumprod(1 + rate/100)
        cpi_cum = (1 + df["indicator_value"] / 100).cumprod()
        cpi_cum.name = "cpi"
        return cpi_cum

    def _load_bond_10y_series(self, start: datetime.date, end: datetime.date) -> pd.Series:
        """加载 10Y 国债收益率日频序列。

        源：c1_market.macro_data indicator_name='国债_10年'（akshare bond_china_yield）。
        覆盖范围：2026-07-10 起（macro_data 任务增量采集），历史深度不足时 ERP 为 NaN。
        """
        from zephyr.data import ch_reader

        sql = (
            f"SELECT report_date, indicator_value "
            f"FROM c1_market.macro_data FINAL "
            f"WHERE indicator_name = '国债_10年' "
            f"AND report_date >= '{start.isoformat()}' AND report_date <= '{end.isoformat()}' "
            f"ORDER BY report_date"
        )
        tsv = ch_reader.query(sql)
        df = self._parse_tsv(tsv, ["report_date", "indicator_value"])
        if df.empty:
            self._log.warning("10Y 国债数据缺失，ERP 将为 NaN")
            return pd.Series(dtype=float)

        df["report_date"] = pd.to_datetime(df["report_date"])
        df["indicator_value"] = pd.to_numeric(df["indicator_value"], errors="coerce")
        df = df.dropna(subset=["indicator_value"])
        df = df.set_index("report_date").sort_index()
        return df["indicator_value"]

    # ── 计算逻辑 ──────────────────────────────────────────────────────────

    def _compute_cape_5y(self, df: pd.DataFrame, cpi_series: pd.Series) -> pd.Series:
        """计算真 CAPE（5 年通胀调整）。

        口径：
          E_i = close_i / pe_i（指数盈利代理）
          real_E_i = E_i / CPI_i（通胀调整，CPI 月度前向填充到日频）
          CAPE_t = close_t / mean_{近1250交易日}(real_E × CPI_t)

        窗口：1250 交易日（约 5 年），min_periods=750（3 年）。
        CPI 缺失时退化为名义 CAPE（不调整通胀）。
        """
        close = df["close"]
        pe = df["pe_ttm"]
        # 指数盈利代理
        earnings = close / pe
        earnings = earnings.replace([np.inf, -np.inf], np.nan)

        if cpi_series.empty:
            # CPI 缺失：名义 CAPE（不调整通胀）
            self._log.warning("CPI 缺失，使用名义 CAPE（5 年盈利均值）")
            cape = close / earnings.rolling(window=_CAPE_WINDOW, min_periods=_CAPE_MIN_PERIODS).mean()
            return cape

        # CPI 前向填充到日频（月度 CPI → 日频）
        # df 索引为整数索引（reset_index 后），需用日期索引对齐
        date_index = pd.DatetimeIndex(df["trade_date"].values)
        cpi_daily = cpi_series.reindex(date_index).ffill()
        # 基期归一化（以序列起点为 100）
        if cpi_daily.notna().any():
            cpi_daily = cpi_daily / cpi_daily.dropna().iloc[0] * 100
        else:
            cpi_daily = pd.Series(100.0, index=date_index)

        # 真实盈利（通胀调整）
        real_earnings = earnings.values / cpi_daily.values
        real_earnings = pd.Series(real_earnings, index=df.index)

        # CAPE_t = close_t / mean_{近5年}(real_E × CPI_t)
        real_earnings_today = real_earnings * cpi_daily.values / 100
        cape = close / real_earnings_today.rolling(window=_CAPE_WINDOW, min_periods=_CAPE_MIN_PERIODS).mean()
        return cape

    @staticmethod
    def _expanding_percentile(series: pd.Series) -> pd.Series:
        """全历史扩展窗分位（expanding percentile）。

        口径：rank(pct=True)，即当前值在全历史序列中的分位（0~1）。
        NaN 输入 → NaN 输出（不影响后续消费端 fillna 降级）。
        """
        return series.rank(pct=True)

    @staticmethod
    def _compute_erp(pe_ttm: pd.Series, bond_series: pd.Series) -> pd.Series:
        """计算 ERP（股权风险溢价）。

        口径：erp = 1/PE_TTM - 10Y国债收益率（百分数口径，如 0.052 = 5.2%）。
        10Y 国债为日频，与 PE 日期对齐（reindex + ffill）。
        10Y 缺失时 ERP 为 NaN。
        """
        if bond_series.empty:
            return pd.Series(np.nan, index=pe_ttm.index)

        # 10Y 国债 reindex 到 PE 日期，前向填充
        bond_aligned = bond_series.reindex(pe_ttm.index).ffill()
        # erp = 1/PE - 10Y（百分数转小数：PE 是倍数，10Y 是百分数如 2.65 = 2.65%）
        erp = 1.0 / pe_ttm - bond_aligned / 100.0
        return erp

    @staticmethod
    def _safe_float(v) -> float | None:
        """安全转 float，NaN/inf 返回 None。"""
        if v is None:
            return None
        try:
            f = float(v)
            if f != f or f in (float("inf"), float("-inf")):
                return None
            return f
        except (ValueError, TypeError):
            return None

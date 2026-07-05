# [BLUEPRINT] MOD-L00-001 | docs/03_modules/_domain-data/datasource-core/blueprint.md
# [MODULE] zephyr.governance.data_governance.akshare_provider
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.intelligence_governance.provider_base
# [CONSUMERS]
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] none
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT]
# [TESTS]
# [A_module] module_id=MOD-DAT_akshare_provider | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: data
# category: provider_implementation
# status: active
# created: "2026-05-05"
# ---

"""D_DATA — Akshare Data Provider

Akshare 数据源适配器。实现 DataSourceBase (OCP 扩展点)，接入 Akshare 金融数据库。

核心职责：
  - 获取 A 股日线/分钟线历史数据
  - 股票列表获取（全 A 股 + 指数成分股）
  - 复权因子计算
  - 数据标准化为 NormalizedMarketData (CTR-001)

CTR 契约：
  生产者 — CTR-001 (NormalizedMarketData) → D_FACTOR, D_SIGNAL, D_RESEARCH
  生产者 — CTR-TRACE-001 (TraceContext) → D_FACTOR~D_REPORTING, D_ML_TRAIN（链头——trace_id 由本层创建）

技术约束：
  - Akshare 是同步 HTTP 客户端，fetch_historical 为阻塞调用
  - 在线环境建议用 asyncio.to_thread 包装避免阻塞事件循环
  - 离线环境直接用同步调用即可

SSoT: cross_layer_contracts.yaml → CTR-001
"""

from __future__ import annotations

import logging
from datetime import datetime

import pandas as pd

from zephyr.governance.intelligence_governance.provider_base import DataSourceBase, DataSourceMeta

_logger = logging.getLogger(__name__)

__meta__ = DataSourceMeta(
    provider_id="akshare",
    provider_name="Akshare 金融数据",
    asset_classes=["equity", "index"],
    markets=["CN"],
    supports_realtime=False,
    supports_historical=True,
    rate_limit_per_min=60,
)


class AkshareProvider(DataSourceBase):
    """Akshare 数据源——A 股历史数据接入"""

    __meta__ = __meta__

    def __init__(self, cache_dir: str | None = None):
        self._cache_dir = cache_dir
        self._ak = None

    @property
    def _akshare(self):
        if self._ak is None:
            try:
                import akshare as ak

                self._ak = ak
                _logger.info("Akshare loaded successfully. version=%s", getattr(ak, "__version__", "unknown"))
            except ImportError:
                raise ImportError("Akshare not installed. Run: pip install akshare")
        return self._ak

    def fetch_historical(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        interval: str = "1d",
    ) -> pd.DataFrame:
        """获取 A 股历史日线数据

        Args:
            symbol: 证券代码（如 "600519" 或 "000001"）
            start: 起始日期
            end: 结束日期
            interval: K 线周期 "1d" | "1m" | "5m" | "15m" | "30m" | "60m"

        Returns:
            标准化 OHLCV DataFrame（列：open/high/low/close/volume/amount/date）
        """
        clean_symbol = symbol.replace(".SH", "").replace(".SZ", "").replace(".BJ", "")
        start_str = start.strftime("%Y%m%d")
        end_str = end.strftime("%Y%m%d")

        try:
            if interval == "1d":
                df = self._akshare.stock_zh_a_hist(
                    symbol=clean_symbol,
                    period="daily",
                    start_date=start_str,
                    end_date=end_str,
                    adjust="qfq",
                )
            else:
                period_map = {"1m": "1", "5m": "5", "15m": "15", "30m": "30", "60m": "60"}
                period = period_map.get(interval, "1")
                df = self._akshare.stock_zh_a_hist_min_em(
                    symbol=clean_symbol,
                    period=period,
                    start_date=f"{start_str} 09:30:00",
                    end_date=f"{end_str} 15:00:00",
                    adjust="qfq",
                )

            if df is None or df.empty:
                _logger.warning("No data returned for symbol=%s from %s to %s", symbol, start_str, end_str)
                return pd.DataFrame(columns=["open", "high", "low", "close", "volume", "amount", "date"])

            df = self._normalize_columns(df, interval)
            _logger.info("Fetched %d rows for symbol=%s interval=%s", len(df), symbol, interval)
            return df

        except Exception as e:
            _logger.error("Failed to fetch data for symbol=%s: %s", symbol, e, exc_info=True)
            return pd.DataFrame(columns=["open", "high", "low", "close", "volume", "amount", "date"])

    def subscribe_realtime(self, symbols: list[str]) -> None:
        """Akshare 不支持实时推送"""
        _logger.warning("AkshareProvider does not support realtime subscription. Use MarketStack or XTX for realtime.")

    def get_stock_list(self) -> pd.DataFrame:
        """获取全 A 股股票列表"""
        try:
            df = self._akshare.stock_zh_a_spot_em()
            return df[["代码", "名称"]].rename(columns={"代码": "symbol", "名称": "name"})
        except Exception as e:
            _logger.error("Failed to get stock list: %s", e, exc_info=True)
            return pd.DataFrame(columns=["symbol", "name"])

    def get_index_constituents(self, index_code: str = "000300") -> pd.DataFrame:
        """获取指数成分股

        Args:
            index_code: 指数代码（000300=沪深300, 000016=上证50, 000905=中证500）
        """
        try:
            df = self._akshare.index_stock_cons_csindex(symbol=index_code)
            return df[["成分券代码", "成分券名称"]].rename(columns={"成分券代码": "symbol", "成分券名称": "name"})
        except Exception as e:
            _logger.error("Failed to get index constituents for %s: %s", index_code, e, exc_info=True)
            return pd.DataFrame(columns=["symbol", "name"])

    def _normalize_columns(self, df: pd.DataFrame, interval: str) -> pd.DataFrame:
        """标准化列名到 OHLCV 格式"""
        if interval == "1d":
            col_map = {
                "日期": "date",
                "开盘": "open",
                "收盘": "close",
                "最高": "high",
                "最低": "low",
                "成交量": "volume",
                "成交额": "amount",
                "涨跌幅": "pct_change",
                "换手率": "turnover",
            }
        else:
            col_map = {
                "时间": "date",
                "开盘": "open",
                "收盘": "close",
                "最高": "high",
                "最低": "low",
                "成交量": "volume",
                "成交额": "amount",
            }

        df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

        for col in ["open", "high", "low", "close"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        if "volume" in df.columns:
            df["volume"] = pd.to_numeric(df["volume"], errors="coerce")

        if "amount" in df.columns:
            df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")

        return df


__all__ = ["AkshareProvider"]

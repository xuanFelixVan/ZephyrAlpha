# [BLUEPRINT] MOD-L00-001 | docs/03_modules/_domain-data/datasource-core/blueprint.md
# [MODULE] zephyr.governance.intelligence_governance.memory_provider
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
# [A_module] module_id=MOD-DAT_memory_provider | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

# ---
# domain: data
# category: provider_implementation
# status: active
# created: "2026-05-05"
# ---

"""D_DATA — Memory Provider

内存模拟数据源。实现 DataSourceBase (OCP 扩展点)，用于测试和离线环境。
生成符合真实统计特征的合成 OHLCV 数据，无需外部网络依赖。

核心职责：
  - 合成 A 股日线/分钟线历史数据
  - 内置股票列表管理
  - 标准化为 NormalizedMarketData (CTR-001)

CTR 契约：
  生产者 — CTR-001 (NormalizedMarketData) -> D_FACTOR, D_SIGNAL, D_RESEARCH
  生产者 — CTR-TRACE-001 (TraceContext) -> D_FACTOR~D_REPORTING, D_ML_TRAIN

SSoT: cross_layer_contracts.yaml -> CTR-001
"""

from __future__ import annotations

from typing import Final
import logging
from datetime import UTC, datetime, timedelta

import numpy as np
import pandas as pd

from zephyr.data.provider_base import DataSourceBase, DataSourceMeta

_logger = logging.getLogger(__name__)

__meta__ = DataSourceMeta(
    name="memory",
    display_name="Memory 合成数据",
    auth_type="anonymous",
    requires_process=False,
    thread_safety="shared",
    rate_limit_default=999999,
)


def _generate_price_series(
    start_price: float,
    n_days: int,
    volatility: float = 0.015,
    drift: float = 0.0002,
    seed: int = 42,
) -> np.ndarray:
    """生成随机游走价格序列。"""
    rng = np.random.default_rng(seed)
    returns = rng.normal(loc=drift, scale=volatility, size=n_days)
    prices = start_price * np.exp(np.cumsum(returns))
    prices[0] = start_price
    return prices


def _generate_candles(
    close_prices: np.ndarray,
    volume_base: float = 1_000_000,
    volume_volatility: float = 0.3,
    seed: int = 99,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """从收盘价序列生成 OHLCV。"""
    rng = np.random.default_rng(seed)
    n = len(close_prices)

    daily_return = np.zeros(n)
    daily_return[1:] = close_prices[1:] / close_prices[:-1] - 1

    noise = rng.uniform(-0.008, 0.008, size=n)
    open_prices = close_prices * (1 + noise)

    high_noise = rng.uniform(0.002, 0.018, size=n)
    low_noise = rng.uniform(-0.018, -0.002, size=n)
    high = np.maximum(open_prices, close_prices) * (1 + high_noise)
    low = np.minimum(open_prices, close_prices) * (1 + low_noise)

    volume_noise = rng.lognormal(mean=0.0, sigma=volume_volatility, size=n)
    volume = volume_base * volume_noise

    amount = volume * close_prices / 100

    return open_prices, high, low, volume, amount


DEFAULT_SYMBOLS: Final[list] = [
    "600519",
    "000858",
    "601318",
    "600036",
    "000333",
    "601166",
    "600900",
    "601398",
    "600276",
    "000001",
]


class MemoryProvider(DataSourceBase):
    """内存数据源——合成行情数据生成器"""

    __meta__ = __meta__

    def __init__(
        self,
        symbols: list[str] | None = None,
        start_date: datetime | None = None,
        base_prices: dict[str, float] | None = None,
        seed: int = 42,
    ):
        self._symbols = symbols or DEFAULT_SYMBOLS
        self._start_date = start_date or datetime(2024, 1, 1, tzinfo=UTC)
        self._base_prices = base_prices or {
            "600519": 1800.0,
            "000858": 160.0,
            "601318": 45.0,
            "600036": 35.0,
            "000333": 55.0,
            "601166": 18.0,
            "600900": 22.0,
            "601398": 5.5,
            "600276": 50.0,
            "000001": 12.0,
        }
        self._seed = seed
        self._cache: dict[str, pd.DataFrame] = {}

    def fetch_historical(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        interval: str = "1d",
    ) -> pd.DataFrame:
        clean_symbol = symbol.replace(".SH", "").replace(".SZ", "").replace(".BJ", "")

        if interval != "1d":
            return self._fetch_intraday(clean_symbol, start, end, interval)

        cache_key = f"{clean_symbol}:{start.date()}:{end.date()}"
        if cache_key in self._cache:
            return self._cache[cache_key].copy()

        total_days = (end - start).days
        if total_days <= 0:
            total_days = 252

        weekday_count = 0
        current = start
        trading_dates = []
        while current <= end:
            if current.weekday() < 5:
                trading_dates.append(current)
                weekday_count += 1
            current += timedelta(days=1)

        if weekday_count == 0:
            weekday_count = 1
            trading_dates = [start]

        base_price = self._base_prices.get(clean_symbol, 20.0)
        seed_offset = hash(clean_symbol) % 10000
        close_prices = _generate_price_series(
            start_price=base_price,
            n_days=weekday_count,
            volatility=0.015,
            drift=0.0002,
            seed=self._seed + seed_offset,
        )
        open_p, high, low, volume, amount = _generate_candles(
            close_prices=close_prices,
            seed=self._seed + seed_offset + 1000,
        )

        df = pd.DataFrame(
            {
                "date": trading_dates,
                "open": open_p,
                "high": high,
                "low": low,
                "close": close_prices,
                "volume": volume,
                "amount": amount,
            }
        )

        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")

        for col in ["open", "high", "low", "close", "volume", "amount"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        self._cache[cache_key] = df.copy()
        _logger.debug("Generated %d candles for symbol=%s", len(df), clean_symbol)
        return df

    def _fetch_intraday(self, symbol: str, start: datetime, end: datetime, interval: str) -> pd.DataFrame:
        daily = self.fetch_historical(symbol, start, end, "1d")
        if daily.empty:
            return pd.DataFrame(columns=["open", "high", "low", "close", "volume", "amount", "date"])

        intraday_rows = []
        interval_minutes = {"1m": 1, "5m": 5, "15m": 15, "30m": 30, "60m": 60}
        freq_min = interval_minutes.get(interval, 5)
        bars_per_day = 240 // freq_min

        for _, row in daily.iterrows():
            day_open = float(row["open"])
            day_close = float(row["close"])
            day_high = float(row["high"])
            day_low = float(row["low"])
            day_vol = float(row["volume"]) / bars_per_day

            rng = np.random.default_rng(hash(f"{symbol}:{row['date']}:{interval}") % 2**31)
            ret = day_close / day_open
            cum_ret = np.linspace(0, np.log(ret), bars_per_day + 1)[1:]
            intra_ret = np.exp(cum_ret) / np.exp(np.insert(cum_ret[:-1], 0, 0))
            prices = day_open * np.cumprod(intra_ret)

            bar_date = pd.to_datetime(row["date"])
            bar_start = bar_date.replace(hour=9, minute=30)

            for i in range(bars_per_day):
                bar_time = bar_start + timedelta(minutes=i * freq_min)
                bar_open = prices[i] if i == 0 else prices[i - 1]
                bar_close = prices[i]
                noise = rng.uniform(0.998, 1.002)
                bar_high = max(bar_open, bar_close) * noise
                bar_low = min(bar_open, bar_close) * (2 - noise)
                vol_noise = rng.uniform(0.5, 1.5)
                intraday_rows.append(
                    {
                        "date": bar_time,
                        "open": bar_open,
                        "high": bar_high,
                        "low": bar_low,
                        "close": bar_close,
                        "volume": day_vol * vol_noise,
                        "amount": day_vol * vol_noise * bar_close / 100,
                    }
                )

        result = pd.DataFrame(intraday_rows)
        for col in ["open", "high", "low", "close", "volume", "amount"]:
            if col in result.columns:
                result[col] = pd.to_numeric(result[col], errors="coerce")
        if "date" in result.columns:
            result["date"] = pd.to_datetime(result["date"], errors="coerce")
        return result

    def subscribe_realtime(self, symbols: list[str]) -> None:
        _logger.info("MemoryProvider: realtime subscription simulated for %d symbols", len(symbols))

    def get_stock_list(self) -> pd.DataFrame:
        return pd.DataFrame(
            {
                "symbol": self._symbols,
                "name": [f"Test_{s}" for s in self._symbols],
            }
        )

    def clear_cache(self) -> None:
        self._cache.clear()


__all__ = ["DEFAULT_SYMBOLS", "MemoryProvider"]

# [BLUEPRINT] MOD-L00-001 | docs/03_modules/_domain_data/blueprint.md
# [MODULE] zephyr.governance.data_governance.miniqmt_provider
# [DOMAIN] D_GOVERNANCE
# [DEPENDENCIES] zephyr.governance.intelligence_governance.provider_base; zephyr.infrastructure.database_service
# [CONSUMERS] zephyr.backtest.core.data_handler; zephyr.backtest.core.tick_replay; zephyr.ex_core.adapters.miniqmt_broker; zephyr.frontend.dashboard.components.order_book
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] Tick 18字段映射; 5档盘口完整性; DatabaseService访问ClickHouse(禁止裸clickhouse_driver.connect); 仅Windows
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] MiniQmtProviderError
# [TESTS]
# [A_module] module_id=MOD-L00-001-miniqmt_provider | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""MiniQMT 实盘行情 Provider（Tick + 5档盘口）

职责:
  - 对接国金证券 MiniQMT 终端的 xtdata API，提供 Tick 级行情（含5档盘口）
  - 支持历史 Tick/K线下载（fetch_historical, interval="tick"）
  - 支持实时 Tick 订阅（subscribe_realtime + register_tick_callback）
  - 提供5档盘口快照（get_order_book）
  - 通过 DatabaseService 访问 ClickHouse 历史日线（get_daily_from_clickhouse）

约束:
  - 仅 Windows（miniQMT 终端为 Windows 应用）
  - 必须先启动 XtMiniQmt.exe 终端并登录
  - xtquant 库需从 QMT 安装目录拷贝到 Python 环境
  - xtdata 模块无需登录即可使用（行情免费），xttrader 需开通 A 股实盘权限（由 D_EX_CORE 实现）
  - 禁止裸 clickhouse_driver.connect，必须通过 DatabaseService

协同:
  - D_BACKTEST data_handler.py: Tick回放回测 (fetch_historical interval="tick")
  - D_BACKTEST tick_replay.py: 秒级做T盘口回放 (fetch_historical interval="tick")
  - D_EX_CORE miniqmt_broker.py: 共用 xtquant 连接 (shared_xtquant_conn)
  - D_FRONTEND order_book.py: 5档盘口实时展示 (subscribe_realtime + get_order_book)
  - D_FRONTEND tick_replay.py: 秒级做T盘口回放 (fetch_historical interval="tick")

SSoT: docs/03_modules/_domain_data/blueprint.md §16.7.1 MiniQMT Provider 详细规格
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from zephyr.shared.utils.time_utils import now_utc

import pandas as pd

from zephyr.governance.intelligence_governance.provider_base import (
    DataSourceBase,
    DataSourceMeta,
)

_logger = logging.getLogger(__name__)

# DataSourceMeta 蓝图额外字段（DataSourceMeta 不支持，用类属性补充）
# category_id: 品类标识 Level-1 Tick(含5档盘口)
# calc_mode: 回测调度模式 replay=Tick回放
# enabled: 已开通

__meta__ = DataSourceMeta(
    provider_id="miniqmt",
    provider_name="MiniQMT 实盘行情",
    asset_classes=["stock", "etf", "convertible_bond", "futures", "options"],
    markets=["SH", "SZ"],
    supports_realtime=True,
    supports_historical=True,
    supports_local=True,
    rate_limit_per_min=999999,
)


class MiniQmtProviderError(Exception):
    """MiniQMT Provider 错误"""
    error_code = "ZA-GV-0001"

    def __init__(self, *args, error_code: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class MiniQmtProvider(DataSourceBase):
    """MiniQMT 实盘行情 Provider——对接 xtdata，提供 Tick + 5档盘口

    对接国金证券 MiniQMT 终端（Level-1 五档盘口），支持:
      - 历史 Tick 下载（18字段含5档盘口）
      - 实时 Tick 订阅
      - 5档盘口快照
      - ClickHouse 历史日线（通过 DatabaseService）

    Usage:
        provider = MiniQmtProvider(path="E:/国金证券QMT交易端/userdata_mini", session_id="zephyr")
        # 历史 Tick
        df = provider.fetch_historical("600000.SH", start, end, interval="tick")
        # 5档盘口
        ob = provider.get_order_book("600000.SH")
        # 实时订阅
        provider.register_tick_callback(my_callback)
        provider.subscribe_realtime(["600000.SH"])

    部署约束:
      - 必须先启动 XtMiniQmt.exe 终端
      - xtquant 库需从 QMT 安装目录 bin.x64/Lib/site-packages/xtquant 拷贝
      - Python 版本 3.6/3.7/3.8（QMT 内置 3.6，自定义环境用 3.8 最稳）
    """

    __meta__ = __meta__

    # 蓝图额外元数据（DataSourceMeta 不支持的字段）
    category_id: str = "market_tick_l1"
    calc_mode: str = "replay"
    enabled: bool = True

    def __init__(self, path: str = "", session_id: str = "zephyr_session"):
        """初始化 MiniQMT 连接

        Args:
            path: miniQMT 安装路径（userdata_mini 目录，默认自动检测）
            session_id: 会话 ID（用于 xttrader，行情无需）
        """
        self._path = path
        self._session_id = session_id
        self._xtdata: Any = None
        self._tick_callbacks: list[Callable[[pd.DataFrame], None]] = []
        self._subscribed_symbols: set[str] = set()

    @property
    def _xtdata_mod(self) -> Any:
        """懒加载 xtdata 模块"""
        if self._xtdata is None:
            try:
                from xtquant import xtdata  # type: ignore[import-not-found]
                self._xtdata = xtdata
                _logger.info("xtdata 模块加载成功")
            except ImportError as e:
                raise MiniQmtProviderError(
                    "xtquant 未安装。请从 QMT 安装目录 bin.x64/Lib/site-packages/xtquant "
                    "拷贝到 Python 环境的 site-packages。"
                ) from e
        return self._xtdata

    def fetch_historical(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        interval: str = "tick",
    ) -> pd.DataFrame:
        """获取历史数据（支持 Tick 级）

        Args:
            symbol: 证券代码（格式 600000.SH / 000001.SZ）
            start: 开始时间
            end: 结束时间
            interval: 周期 tick=逐笔 / 1m=1分钟 / 5m=5分钟 / 15m / 30m / 60m / 1d=日线

        Returns:
            pd.DataFrame: 标准化字段
              - Tick 模式: 18字段（含5档盘口 ask_price_1..5/bid_price_1..5/ask_vol_1..5/bid_vol_1..5）
              - K线模式: OHLCV（open/high/low/close/volume/amount）

        Raises:
            MiniQmtProviderError: 下载失败或数据格式错误
        """
        xtdata = self._xtdata_mod
        start_str = start.strftime("%Y%m%d")
        end_str = end.strftime("%Y%m%d")

        # 1. 下载历史数据到本地缓存
        try:
            xtdata.download_history_data(symbol, interval, start_str, end_str)
        except Exception as e:
            raise MiniQmtProviderError(
                f"下载历史数据失败 symbol={symbol} interval={interval}: {e}"
            ) from e

        # 2. 获取数据
        try:
            data = xtdata.get_market_data_ex(
                stock_list=[symbol],
                period=interval,
                start_time=start_str,
                end_time=end_str,
            )
        except Exception as e:
            raise MiniQmtProviderError(
                f"获取历史数据失败 symbol={symbol} interval={interval}: {e}"
            ) from e

        if not data or symbol not in data:
            _logger.warning("历史数据为空 symbol=%s interval=%s", symbol, interval)
            return pd.DataFrame()

        raw_df = data[symbol]
        if raw_df is None or raw_df.empty:
            return pd.DataFrame()

        # 3. 标准化
        if interval == "tick":
            return self._normalize_tick_data(raw_df, symbol)
        return self._normalize_kline_data(raw_df, symbol)

    def subscribe_realtime(self, symbols: list[str]) -> None:
        """订阅实时 Tick 行情（含5档盘口）

        需先调用 register_tick_callback 注册回调函数。
        订阅后，每收到一个 Tick，所有已注册回调被依次调用。

        Args:
            symbols: 证券代码列表

        Raises:
            MiniQmtProviderError: 订阅失败
        """
        if not self._tick_callbacks:
            _logger.warning("未注册 tick_callback，订阅后无回调将被调用")

        xtdata = self._xtdata_mod
        for symbol in symbols:
            if symbol in self._subscribed_symbols:
                continue
            try:
                xtdata.subscribe_quote(symbol, period="tick", callback=self._on_tick)
                self._subscribed_symbols.add(symbol)
                _logger.info("订阅实时 Tick 成功 symbol=%s", symbol)
            except Exception as e:
                raise MiniQmtProviderError(
                    f"订阅实时行情失败 symbol={symbol}: {e}"
                ) from e

    def register_tick_callback(self, callback: Callable[[pd.DataFrame], None]) -> None:
        """注册 Tick 回调函数

        Args:
            callback: Tick 回调函数，接收标准化后的 DataFrame（单行）
        """
        self._tick_callbacks.append(callback)

    def get_order_book(self, symbol: str) -> dict:
        """获取当前5档盘口快照

        Args:
            symbol: 证券代码

        Returns:
            dict: {
                "symbol": str,
                "ask_price": list[Decimal],  # 5档卖价 ask1~ask5
                "bid_price": list[Decimal],  # 5档买价 bid1~bid5
                "ask_vol": list[Decimal],    # 5档卖量
                "bid_vol": list[Decimal],    # 5档买量
                "last_price": Decimal,
                "timestamp": datetime,
            }

        Raises:
            MiniQmtProviderError: 获取盘口失败
        """
        xtdata = self._xtdata_mod
        try:
            ticks = xtdata.get_full_tick([symbol])
        except Exception as e:
            raise MiniQmtProviderError(f"获取盘口快照失败 symbol={symbol}: {e}") from e

        if not ticks or symbol not in ticks:
            raise MiniQmtProviderError(f"盘口数据为空 symbol={symbol}")

        return self._parse_order_book(ticks[symbol], symbol)

    def get_daily_from_clickhouse(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        table: str = "daily_kline",
    ) -> pd.DataFrame:
        """从 ClickHouse 获取历史日线数据（通过 DatabaseService）

        禁止裸 clickhouse_driver.connect，必须通过 DatabaseService。

        Args:
            symbol: 证券代码
            start: 开始时间
            end: 结束时间
            table: ClickHouse 表名（默认 daily_kline）

        Returns:
            pd.DataFrame: OHLCV 数据（date/open/high/low/close/volume/amount）

        Raises:
            MiniQmtProviderError: ClickHouse 查询失败
        """
        try:
            from zephyr.infrastructure.database_service import DatabaseService
        except ImportError as e:
            raise MiniQmtProviderError(
                "DatabaseService 不可用，无法访问 ClickHouse"
            ) from e

        try:
            db = DatabaseService()
            client = db.get_clickhouse_conn()
        except Exception as e:
            raise MiniQmtProviderError(f"DatabaseService 初始化失败: {e}") from e

        start_str = start.strftime("%Y-%m-%d")
        end_str = end.strftime("%Y-%m-%d")
        # symbol 格式 600000.SH -> ClickHouse 可能存 600000 或 600000.SH
        query = (
            f"SELECT date, open, high, low, close, volume, amount "
            f"FROM {table} "
            f"WHERE symbol = %(symbol)s AND date >= %(start)s AND date <= %(end)s "
            f"ORDER BY date"
        )
        params = {"symbol": symbol, "start": start_str, "end": end_str}

        try:
            rows = client.execute(query, params)
        except Exception as e:
            raise MiniQmtProviderError(f"ClickHouse 查询失败: {e}") from e

        if not rows:
            return pd.DataFrame()

        df = pd.DataFrame(
            rows, columns=["date", "open", "high", "low", "close", "volume", "amount"]
        )
        df["date"] = pd.to_datetime(df["date"])
        return df

    def _on_tick(self, datas: dict) -> None:
        """xtdata Tick 回调内部分发器

        Args:
            datas: xtdata 回调数据 {symbol: tick_dict}
        """
        for symbol, tick in datas.items():
            try:
                df = self._normalize_tick_data_single(tick, symbol)
                for cb in self._tick_callbacks:
                    try:
                        cb(df)
                    except Exception as e:
                        _logger.error("Tick 回调执行错误 symbol=%s: %s", symbol, e, exc_info=True)
            except Exception as e:
                _logger.error("Tick 数据标准化失败 symbol=%s: %s", symbol, e, exc_info=True)

    def _normalize_tick_data(self, raw_df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """标准化 Tick 数据（18字段映射）

        xtdata 原始字段 -> DataFrame 标准化列名:
          time -> timestamp, lastPrice -> last_price, open -> open, high -> high,
          low -> low, lastClose -> prev_close, amount -> amount, volume -> volume,
          pvolume -> pvolume, stockStatus -> stock_status, openInt -> open_interest,
          lastSettlementPrice -> last_settlement,
          askPrice[0..4] -> ask_price_1..5, bidPrice[0..4] -> bid_price_1..5,
          askVol[0..4] -> ask_vol_1..5, bidVol[0..4] -> bid_vol_1..5,
          settlementPrice -> settlement_price, transactionNum -> transaction_num

        Args:
            raw_df: xtdata 原始 DataFrame
            symbol: 证券代码

        Returns:
            标准化 DataFrame
        """
        df = raw_df.copy()

        # 重命名基础字段
        rename_map = {
            "time": "timestamp",
            "lastPrice": "last_price",
            "lastClose": "prev_close",
            "pvolume": "pvolume",
            "stockStatus": "stock_status",
            "openInt": "open_interest",
            "lastSettlementPrice": "last_settlement",
            "settlementPrice": "settlement_price",
            "transactionNum": "transaction_num",
        }
        df = df.rename(columns=rename_map)

        # 5档盘口展开（askPrice/bidPrice/askVol/bidVol 是 list 列）
        for prefix, cols in [
            ("askPrice", "ask_price"),
            ("bidPrice", "bid_price"),
            ("askVol", "ask_vol"),
            ("bidVol", "bid_vol"),
        ]:
            if prefix in df.columns:
                for i in range(5):
                    df[f"{cols}_{i + 1}"] = df[prefix].apply(
                        lambda x, idx=i: self._safe_index(x, idx)
                    )
                df = df.drop(columns=[prefix])

        # timestamp 毫秒 -> datetime
        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

        df["symbol"] = symbol
        return df

    def _normalize_tick_data_single(self, tick: dict, symbol: str) -> pd.DataFrame:
        """标准化单个 Tick（实时回调用）"""
        row: dict[str, Any] = {"symbol": symbol}

        # 基础字段
        row["timestamp"] = datetime.fromtimestamp(tick.get("time", 0) / 1000)
        row["last_price"] = Decimal(str(tick.get("lastPrice", 0)))
        row["open"] = Decimal(str(tick.get("open", 0)))
        row["high"] = Decimal(str(tick.get("high", 0)))
        row["low"] = Decimal(str(tick.get("low", 0)))
        row["prev_close"] = Decimal(str(tick.get("lastClose", 0)))
        row["amount"] = Decimal(str(tick.get("amount", 0)))
        row["volume"] = Decimal(str(tick.get("volume", 0)))
        row["pvolume"] = Decimal(str(tick.get("pvolume", 0)))
        row["stock_status"] = int(tick.get("stockStatus", 0))
        row["open_interest"] = int(tick.get("openInt", 0))
        row["last_settlement"] = Decimal(str(tick.get("lastSettlementPrice", 0)))
        row["settlement_price"] = Decimal(str(tick.get("settlementPrice", 0)))
        row["transaction_num"] = int(tick.get("transactionNum", 0))

        # 5档盘口
        ask_price = tick.get("askPrice", []) or []
        bid_price = tick.get("bidPrice", []) or []
        ask_vol = tick.get("askVol", []) or []
        bid_vol = tick.get("bidVol", []) or []
        for i in range(5):
            row[f"ask_price_{i + 1}"] = Decimal(str(self._safe_index(ask_price, i)))
            row[f"bid_price_{i + 1}"] = Decimal(str(self._safe_index(bid_price, i)))
            row[f"ask_vol_{i + 1}"] = Decimal(str(self._safe_index(ask_vol, i)))
            row[f"bid_vol_{i + 1}"] = Decimal(str(self._safe_index(bid_vol, i)))

        return pd.DataFrame([row])

    def _normalize_kline_data(self, raw_df: pd.DataFrame, symbol: str) -> pd.DataFrame:
        """标准化 K线数据（OHLCV）"""
        df = raw_df.copy()
        if "time" in df.columns:
            df["timestamp"] = pd.to_datetime(df["time"], unit="ms")
            df = df.drop(columns=["time"])
        df["symbol"] = symbol
        return df

    def _parse_order_book(self, tick: dict, symbol: str) -> dict:
        """解析5档盘口快照

        Args:
            tick: xtdata get_full_tick 返回的 tick dict
            symbol: 证券代码

        Returns:
            dict: 5档盘口快照
        """
        ask_price = tick.get("askPrice", []) or []
        bid_price = tick.get("bidPrice", []) or []
        ask_vol = tick.get("askVol", []) or []
        bid_vol = tick.get("bidVol", []) or []

        ts = tick.get("time", 0)
        timestamp = datetime.fromtimestamp(ts / 1000) if ts else now_utc()

        return {
            "symbol": symbol,
            "ask_price": [Decimal(str(self._safe_index(ask_price, i))) for i in range(5)],
            "bid_price": [Decimal(str(self._safe_index(bid_price, i))) for i in range(5)],
            "ask_vol": [Decimal(str(self._safe_index(ask_vol, i))) for i in range(5)],
            "bid_vol": [Decimal(str(self._safe_index(bid_vol, i))) for i in range(5)],
            "last_price": Decimal(str(tick.get("lastPrice", 0))),
            "timestamp": timestamp,
        }

    @staticmethod
    def _safe_index(lst: Any, idx: int) -> Any:
        """安全索引（越界返回0）"""
        if lst is None:
            return 0
        try:
            return lst[idx] if idx < len(lst) else 0
        except (TypeError, IndexError):
            return 0


__all__ = ["MiniQmtProvider", "MiniQmtProviderError"]

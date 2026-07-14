# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.core.data_handler
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.infrastructure.database_service; zephyr.governance.data_governance.miniqmt_provider
# [CONSUMERS] zephyr.backtest.implementations.vectorized_engine; zephyr.backtest.implementations.event_driven_engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] PIT铁律:按timestamp排序,禁止未来函数; DatabaseService访问ClickHouse; 多源统一接口
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DataHandlerError
# [TESTS]
# [A_module] module_id=MOD-BT-001-data_handler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""回测数据处理器模块（v1.1.0 扩展：多源化 + ClickHouse 实现 + Tick 源）

职责:
  - 按 bar 推送 OHLCV 数据（PIT 正确）
  - 支持 DataFrame 输入（快速回测）
  - 支持 ClickHouse 加载（生产模式，通过 DatabaseService）
  - v1.1.0 新增: MultiSourceDataHandler 支持 Tick + 批量双源切换
    - Tick 源: MiniQmtProvider.fetch_historical(interval="tick")
    - 批量源: ClickHouse 通过 DatabaseService
    - 统一接口: next_bar() / next_tick() 双模式

约束:
  - PIT(Point-in-Time)铁律:仅使用当前时间戳及之前的数据
  - 数据来源:ClickHouse(c1_market)通过DatabaseService访问
  - 禁止裸 clickhouse_driver.connect

SSoT: docs/03_modules/_domain_backtest/blueprint.md §3.2 §5.1 §16.7 data_handler.py
"""

from __future__ import annotations

import logging
from typing import Any, Iterator, Optional

import pandas as pd

try:
    from zephyr.infrastructure.database_service import DatabaseService
except ImportError:
    DatabaseService = None  # type: ignore[assignment,misc]

from zephyr.backtest.core.pit_manager import PITManager, PITConfig
from zephyr.data import ch_reader

_logger = logging.getLogger(__name__)


class DataHandlerError(Exception):
    """数据处理器错误"""

    error_code = "ZA-BT-0010"

    def __init__(self, *args, error_code: str | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


class BacktestDataHandler:
    """回测数据处理器（日线/分钟线 bar 模式）

    支持两种模式:
    1. DataFrame模式:直接接收DataFrame,按日期迭代推送bar
    2. ClickHouse模式:通过DatabaseService从ClickHouse加载

    PIT保证:
    - 数据按timestamp排序
    - 每次只推送当前bar的数据,不预读未来数据
    - 支持多symbol截面对齐

    Usage:
        # DataFrame模式
        handler = BacktestDataHandler(data=df)
        for bar in handler:
            # bar是当前日期的所有symbol的OHLCV
            ...

        # ClickHouse模式
        handler = BacktestDataHandler.from_clickhouse(
            symbols=["000001.SZ", "600000.SH"],
            start_date="2024-01-01",
            end_date="2024-12-31",
        )
    """

    def __init__(
        self,
        data: pd.DataFrame,
        date_column: str = "date",
        symbol_column: str = "symbol",
        pit_manager: PITManager | None = None,
    ):
        """初始化数据处理器

        Args:
            data: OHLCV数据,需含date/symbol/open/high/low/close/volume列
                  支持MultiIndex(date, symbol)或flat DataFrame含date/symbol列
            date_column: 日期列名
            symbol_column: symbol列名
            pit_manager: PIT管理器实例(可选,默认自动创建)

        Raises:
            DataHandlerError: 数据格式无效
        """
        if data is None or data.empty:
            raise DataHandlerError("data不能为空")

        self._data = data.copy()
        self._date_column = date_column
        self._symbol_column = symbol_column
        self._pit_manager = pit_manager or PITManager()
        self._dates: list[Any] = []
        self._current_idx = 0

        # 标准化:提取排序后的日期列表
        self._normalize_data()

    def _normalize_data(self) -> None:
        """标准化数据:提取日期列表,按时间排序"""
        if isinstance(self._data.index, pd.MultiIndex):
            # MultiIndex(date, symbol) — date是level 0
            self._dates = sorted(self._data.index.get_level_values(0).unique())
        elif self._date_column in self._data.columns:
            self._dates = sorted(self._data[self._date_column].unique())
        else:
            raise DataHandlerError(
                f"数据需含MultiIndex({self._date_column}, {self._symbol_column})或flat DataFrame含{self._date_column}列"
            )

        if len(self._dates) == 0:
            raise DataHandlerError("日期列表为空")

    def __iter__(self) -> Iterator[pd.DataFrame]:
        """迭代推送bar(每次返回当前日期的所有symbol数据)"""
        self._current_idx = 0
        return self

    def __next__(self) -> pd.DataFrame:
        """推送下一个bar

        Returns:
            当前日期的所有symbol的OHLCV数据(DataFrame)

        Raises:
            StopIteration: 数据推送完毕
        """
        if self._current_idx >= len(self._dates):
            raise StopIteration

        date = self._dates[self._current_idx]
        self._current_idx += 1

        return self.get_bar(date)

    def get_bar(self, date: object) -> pd.DataFrame:
        """获取指定日期的bar数据(PIT:仅返回该日期的数据)

        Args:
            date: 日期

        Returns:
            该日期的所有symbol的OHLCV数据

        Raises:
            DataHandlerError: 日期不存在
        """
        if isinstance(self._data.index, pd.MultiIndex):
            try:
                bar = self._data.xs(date, level=0)
            except KeyError:
                raise DataHandlerError(f"日期{date}不存在") from None
        else:
            bar = self._data[self._data[self._date_column] == date]

        if bar.empty:
            raise DataHandlerError(f"日期{date}无数据")

        return bar

    def get_history(self, date: object, lookback: int = 1) -> pd.DataFrame:
        """获取历史数据(PIT:返回date及之前lookback天的数据)

        用于需要历史窗口的指标计算(如移动平均)。

        Args:
            date: 当前日期
            lookback: 回看天数(含当天)

        Returns:
            历史数据DataFrame
        """
        try:
            idx = self._dates.index(date)
        except ValueError:
            raise DataHandlerError(f"日期{date}不存在") from None

        start_idx = max(0, idx - lookback + 1)
        history_dates = self._dates[start_idx : idx + 1]

        if isinstance(self._data.index, pd.MultiIndex):
            return self._data.loc[pd.IndexSlice[history_dates, :], :]
        else:
            return self._data[self._data[self._date_column].isin(history_dates)]

    @property
    def dates(self) -> list[Any]:
        """所有日期列表(排序后)"""
        return list(self._dates)

    @property
    def symbols(self) -> list[str]:
        """所有symbol列表"""
        if isinstance(self._data.index, pd.MultiIndex):
            return sorted(self._data.index.get_level_values(1).unique())
        elif self._symbol_column in self._data.columns:
            return sorted(self._data[self._symbol_column].unique())
        return []

    def run_pit_checks(
        self,
        train_data: pd.DataFrame | None = None,
        factor_col: str | None = None,
        all_symbols: list[str] | None = None,
        delisted_symbols: list[str] | None = None,
    ) -> dict:
        """运行PIT铁律检查（一致性测试+幸存者偏差检测）

        Args:
            train_data: 训练平面数据(可选,用于一致性测试)
            factor_col: 因子列名(一致性测试用)
            all_symbols: 历史上所有上市过的symbol列表(幸存者偏差检测用)
            delisted_symbols: 已退市symbol列表(幸存者偏差检测用)

        Returns:
            dict: consistency(一致性测试结果), survivorship(幸存者偏差结果)
        """
        result: dict[str, Any] = {}

        if train_data is not None and factor_col is not None:
            result["consistency"] = self._pit_manager.pit_consistency_test(
                train_data=train_data,
                backtest_data=self._data,
                factor_col=factor_col,
            )

        if all_symbols is not None and delisted_symbols is not None:
            bt_symbols = self.symbols
            result["survivorship"] = self._pit_manager.check_survivorship_bias(
                backtest_symbols=bt_symbols,
                all_symbols=all_symbols,
                delisted_symbols=delisted_symbols,
            )

        return result

    @property
    def pit_manager(self) -> PITManager:
        """PIT管理器实例"""
        return self._pit_manager

    @classmethod
    def from_clickhouse(
        cls,
        symbols: list[str],
        start_date: str,
        end_date: str,
        database_service: object | None = None,
        table: str = "daily_kline",
    ) -> "BacktestDataHandler":
        """从ClickHouse加载OHLCV数据（通过 DatabaseService）

        v1.1.0 实现：通过 DatabaseService 访问 ClickHouse(c1_market)，
        禁止裸 clickhouse_driver.connect。

        Args:
            symbols: symbol列表
            start_date: 开始日期(YYYY-MM-DD)
            end_date: 结束日期(YYYY-MM-DD)
            database_service: DatabaseService实例(可选,默认自动创建)
            table: ClickHouse表名(默认daily_kline)

        Returns:
            BacktestDataHandler实例

        Raises:
            DataHandlerError: ClickHouse未接入或查询失败
        """
        if database_service is None:
            if DatabaseService is None:
                raise DataHandlerError(
                    "DatabaseService不可用——请安装 infrastructure.database_service。"
                    "MVP请使用DataFrame模式: BacktestDataHandler(data=df)"
                )
            try:
                database_service = DatabaseService()
            except Exception as e:
                raise DataHandlerError(
                    f"DatabaseService 初始化失败: {e}"
                ) from e

        try:
            client = database_service.get_clickhouse_conn()
        except AttributeError as e:
            raise DataHandlerError(
                "DatabaseService 未实现 get_clickhouse_conn() 方法"
            ) from e
        except Exception as e:
            raise DataHandlerError(f"获取 ClickHouse 连接失败: {e}") from e

        # ClickHouse 查询：支持多 symbol
        symbols_str = ", ".join([f"'{s}'" for s in symbols])
        query = (
            f"SELECT date, symbol, open, high, low, close, volume, amount "
            f"FROM {table} "
            f"WHERE symbol IN ({symbols_str}) "
            f"AND date >= %(start)s AND date <= %(end)s "
            f"ORDER BY date, symbol"
        )
        params = {"start": start_date, "end": end_date}

        # 裁定 #ARCH-CH-007: 对 ReplacingMergeTree 表自动注入 FINAL
        query = ch_reader.inject_final(query)

        try:
            rows = client.execute(query, params)
        except Exception as e:
            raise DataHandlerError(f"ClickHouse 查询失败: {e}") from e

        if not rows:
            raise DataHandlerError(
                f"ClickHouse 查询结果为空: symbols={symbols}, "
                f"range=[{start_date}, {end_date}]"
            )

        df = pd.DataFrame(
            rows,
            columns=["date", "symbol", "open", "high", "low", "close", "volume", "amount"],
        )
        df["date"] = pd.to_datetime(df["date"])

        _logger.info(
            "ClickHouse 加载完成: %d rows, symbols=%s", len(df), symbols
        )
        return cls(data=df, date_column="date", symbol_column="symbol")


class MultiSourceDataHandler:
    """多源数据处理器（v1.1.0 新增，Tick + 批量双源）

    支持双源切换:
      - Tick 源: MiniQmtProvider.fetch_historical(interval="tick") 提供18字段Tick+5档盘口
      - 批量源: ClickHouse(c1_market) 通过 DatabaseService 访问（日线/分钟线批量回测）

    源选择策略（由 mode 决定）:
      - "tick": 仅使用 Tick 源（秒级做T回测）
      - "batch": 仅使用批量源（日线/分钟线回测）
      - "auto": 优先 Tick 源，不可用时回退批量源

    统一接口:
      - next_bar(): 日线/分钟线模式，返回当前 bar 的 DataFrame
      - next_tick(): Tick 模式，返回当前 Tick 的 DataFrame（单行）

    PIT 保证:
      - Tick 模式: 按 timestamp 严格排序，禁止跨 Tick 跳跃
      - 批量模式: 按 date 排序，禁止未来数据泄漏

    Usage:
        # Tick 模式（做T回测）
        provider = MiniQmtProvider(path="E:/国金证券QMT交易端/userdata_mini")
        handler = MultiSourceDataHandler(
            tick_provider=provider,
            symbols=["600000.SH"],
            start=datetime(2024, 1, 15),
            end=datetime(2024, 1, 15),
            mode="tick",
        )
        while True:
            tick_df = handler.next_tick()
            if tick_df is None:
                break
            # 处理 tick_df

        # 批量模式（日线回测）
        handler = MultiSourceDataHandler(
            symbols=["600000.SH"],
            start=datetime(2024, 1, 1),
            end=datetime(2024, 1, 31),
            mode="batch",
        )
        while True:
            bar = handler.next_bar()
            if bar is None:
                break
            # 处理 bar
    """

    def __init__(
        self,
        symbols: list[str],
        start: object,
        end: object,
        mode: str = "auto",
        tick_provider: object | None = None,
        batch_data: Optional[pd.DataFrame] = None,
        database_service: object | None = None,
        table: str = "daily_kline",
    ):
        """初始化多源数据处理器

        Args:
            symbols: 标的代码列表
            start: 开始时间（datetime）
            end: 结束时间（datetime）
            mode: 源选择策略 "tick" | "batch" | "auto"
            tick_provider: MiniQmtProvider 实例（mode="tick"/"auto" 时必填）
            batch_data: 批量数据 DataFrame（可选，优先于 ClickHouse）
            database_service: DatabaseService 实例（mode="batch"/"auto" 时可选）
            table: ClickHouse 表名（默认 daily_kline）

        Raises:
            DataHandlerError: 参数无效或数据源不可用
        """
        if not symbols:
            raise DataHandlerError("symbols 不能为空")
        if mode not in ("tick", "batch", "auto"):
            raise DataHandlerError(f"无效 mode: {mode}, 必须为 tick/batch/auto")

        self._symbols = list(symbols)
        self._start = start
        self._end = end
        self._mode = mode
        self._tick_provider = tick_provider
        self._table = table

        # 实际生效的源
        self._active_source: str = ""
        self._tick_data: dict[str, pd.DataFrame] = {}  # {symbol: tick_df}
        self._tick_idx: dict[str, int] = {}
        self._merged_ticks: list[dict] = []
        self._merged_idx = 0
        self._batch_handler: Optional[BacktestDataHandler] = None

        self._resolve_source(batch_data, database_service)

    def _resolve_source(
        self,
        batch_data: Optional[pd.DataFrame],
        database_service: object | None,
    ) -> None:
        """根据 mode 解析实际数据源

        Args:
            batch_data: 批量数据 DataFrame
            database_service: DatabaseService 实例
        """
        if self._mode == "tick":
            if self._tick_provider is None:
                raise DataHandlerError(
                    'mode="tick" 需要 tick_provider 参数'
                )
            self._active_source = "tick"
            self._load_tick_data()

        elif self._mode == "batch":
            self._active_source = "batch"
            self._init_batch_source(batch_data, database_service)

        else:  # auto
            # 优先 Tick 源
            if self._tick_provider is not None:
                try:
                    self._load_tick_data()
                    self._active_source = "tick"
                    _logger.info("auto 模式: 选中 Tick 源")
                    return
                except Exception as e:
                    _logger.warning("auto 模式: Tick 源不可用: %s, 回退批量源", e, exc_info=True)
            # 回退批量源
            self._active_source = "batch"
            self._init_batch_source(batch_data, database_service)
            _logger.info("auto 模式: 选中批量源")

    def _load_tick_data(self) -> None:
        """从 tick_provider 加载所有 symbol 的 Tick 数据并按时间戳合并"""
        all_ticks: list[pd.DataFrame] = []
        for symbol in self._symbols:
            try:
                df = self._tick_provider.fetch_historical(
                    symbol=symbol,
                    start=self._start,
                    end=self._end,
                    interval="tick",
                )
            except Exception as e:
                raise DataHandlerError(
                    f"加载 Tick 数据失败 symbol={symbol}: {e}"
                ) from e

            if df is None or df.empty:
                _logger.warning("symbol=%s 的 Tick 数据为空", symbol)
                continue
            all_ticks.append(df)

        if not all_ticks:
            raise DataHandlerError("所有 symbol 的 Tick 数据均为空")

        merged = pd.concat(all_ticks, ignore_index=True)
        if "timestamp" in merged.columns:
            merged = merged.sort_values("timestamp").reset_index(drop=True)
        self._merged_ticks = merged.to_dict("records")
        _logger.info(
            "Tick 数据加载完成: %d ticks, symbols=%s",
            len(self._merged_ticks),
            self._symbols,
        )

    def _init_batch_source(
        self,
        batch_data: Optional[pd.DataFrame],
        database_service: object | None,
    ) -> None:
        """初始化批量数据源（DataFrame 或 ClickHouse）

        Args:
            batch_data: 批量数据 DataFrame（优先）
            database_service: DatabaseService 实例
        """
        if batch_data is not None:
            self._batch_handler = BacktestDataHandler(data=batch_data)
        else:
            # 从 ClickHouse 加载
            start_str = self._format_date(self._start)
            end_str = self._format_date(self._end)
            self._batch_handler = BacktestDataHandler.from_clickhouse(
                symbols=self._symbols,
                start_date=start_str,
                end_date=end_str,
                database_service=database_service,
                table=self._table,
            )

    @staticmethod
    def _format_date(dt: object) -> str:
        """格式化日期为 YYYY-MM-DD"""
        if hasattr(dt, "strftime"):
            return dt.strftime("%Y-%m-%d")
        return str(dt)

    def next_bar(self) -> Optional[pd.DataFrame]:
        """推送下一个 bar（批量模式）

        Returns:
            当前 bar 的 DataFrame，无更多数据返回 None

        Raises:
            DataHandlerError: 当前源非批量模式
        """
        if self._active_source != "batch" or self._batch_handler is None:
            raise DataHandlerError(
                f"next_bar() 仅适用于 batch 源, 当前源={self._active_source}"
            )
        try:
            return next(self._batch_handler)
        except StopIteration:
            return None

    def next_tick(self) -> Optional[pd.DataFrame]:
        """推送下一个 Tick（Tick 模式）

        Returns:
            当前 Tick 的 DataFrame（单行），无更多数据返回 None

        Raises:
            DataHandlerError: 当前源非 Tick 模式
        """
        if self._active_source != "tick":
            raise DataHandlerError(
                f"next_tick() 仅适用于 tick 源, 当前源={self._active_source}"
            )
        if self._merged_idx >= len(self._merged_ticks):
            return None
        row = self._merged_ticks[self._merged_idx]
        self._merged_idx += 1
        return pd.DataFrame([row])

    @property
    def active_source(self) -> str:
        """当前生效的数据源 "tick" | "batch" """
        return self._active_source

    @property
    def total_ticks(self) -> int:
        """Tick 总数（tick 模式）"""
        return len(self._merged_ticks)

    @property
    def total_bars(self) -> int:
        """bar 总数（batch 模式）"""
        if self._batch_handler is None:
            return 0
        return len(self._batch_handler.dates)

    def get_history(self, lookback: int = 1) -> Optional[pd.DataFrame]:
        """获取历史数据（PIT: 返回当前及之前 lookback 条数据）

        Args:
            lookback: 回看条数（含当前）

        Returns:
            历史数据 DataFrame，无数据返回 None
        """
        if self._active_source == "tick":
            start_idx = max(0, self._merged_idx - lookback)
            rows = self._merged_ticks[start_idx : self._merged_idx]
            return pd.DataFrame(rows) if rows else None

        # batch 模式：委托给 BacktestDataHandler.get_history
        if self._batch_handler is None or self._batch_handler._current_idx == 0:
            return None
        current_date = self._batch_handler._dates[
            self._batch_handler._current_idx - 1
        ]
        return self._batch_handler.get_history(current_date, lookback)


__all__ = [
    "BacktestDataHandler",
    "MultiSourceDataHandler",
    "DataHandlerError",
]

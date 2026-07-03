# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.core.data_handler
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES]
# [CONSUMERS] zephyr.backtest.implementations.vectorized_engine
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] PIT铁律:按timestamp排序,禁止未来函数; DatabaseService访问ClickHouse
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] DataHandlerError
# [TESTS]
# [A_module] module_id=MOD-BT-001-data_handler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] task_bound
"""回测数据处理器模块

职责:
  - 按bar推送OHLCV数据(PIT正确)
  - 支持DataFrame输入(快速回测)和ClickHouse加载(生产模式)
  - 保证时间戳截面对齐,禁止未来函数

约束:
  - PIT(Point-in-Time)铁律:仅使用当前时间戳及之前的数据
  - 数据来源:ClickHouse(c1_market)通过DatabaseService访问
  - 禁止裸clickhouse_driver.connect

SSoT: docs/03_modules/_domain_backtest/blueprint.md §3.2 §5.1
"""

from __future__ import annotations

from typing import Any, Iterator, Optional

import pandas as pd

try:
    from zephyr.infrastructure.database_service import DatabaseService
except ImportError:
    DatabaseService = None  # type: ignore[assignment,misc]


class DataHandlerError(Exception):
    """数据处理器错误"""


class BacktestDataHandler:
    """回测数据处理器

    支持两种模式:
    1. DataFrame模式:直接接收DataFrame,按日期迭代推送bar
    2. ClickHouse模式:通过DatabaseService从ClickHouse加载(预留,待ClickHouse接入)

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

        # ClickHouse模式(预留)
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
    ):
        """初始化数据处理器

        Args:
            data: OHLCV数据,需含date/symbol/open/high/low/close/volume列
                  支持MultiIndex(date, symbol)或flat DataFrame含date/symbol列
            date_column: 日期列名
            symbol_column: symbol列名

        Raises:
            DataHandlerError: 数据格式无效
        """
        if data is None or data.empty:
            raise DataHandlerError("data不能为空")

        self._data = data.copy()
        self._date_column = date_column
        self._symbol_column = symbol_column
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

    def get_bar(self, date: Any) -> pd.DataFrame:
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

    def get_history(self, date: Any, lookback: int = 1) -> pd.DataFrame:
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

    @classmethod
    def from_clickhouse(
        cls,
        symbols: list[str],
        start_date: str,
        end_date: str,
        database_service: Optional[Any] = None,
        table: str = "daily_kline",
    ) -> "BacktestDataHandler":
        """从ClickHouse加载OHLCV数据(预留接口)

        通过DatabaseService访问ClickHouse(c1_market),禁止裸clickhouse_driver.connect。
        当前ClickHouse接入为预留(NotImplementedError),待DatabaseService实现后启用。

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
                    "DatabaseService不可用——ClickHouse接入尚未实现。"
                    "MVP请使用DataFrame模式: BacktestDataHandler(data=df)"
                )
            database_service = DatabaseService()

        try:
            # 预留:待DatabaseService实现ClickHouse接口后启用
            raise DataHandlerError(
                "ClickHouse接入尚未实现(DatabaseService.get_clickhouse_conn()为预留接口)。"
                "MVP请使用DataFrame模式: BacktestDataHandler(data=df)"
            )
        except Exception as e:
            raise DataHandlerError(f"ClickHouse加载失败: {e}") from e


__all__ = ["BacktestDataHandler", "DataHandlerError"]

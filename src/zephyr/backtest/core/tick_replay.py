# [BLUEPRINT] MOD-BT-001 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] zephyr.backtest.core.tick_replay
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.governance.data_governance.miniqmt_provider; zephyr.backtest.core.matching_logic
# [CONSUMERS] zephyr.backtest.implementations.event_driven_engine; zephyr.frontend.dashboard.components.tick_replay
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 按timestamp严格排序; 禁止跨Tick跳跃; PIT铁律; 5档盘口完整性
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] TickReplayError
# [TESTS]
# [A_module] module_id=MOD-BT-001-tick_replay | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Tick 回放引擎模块（v1.1.0 新增，秒级做T专用）

职责:
  - 按 timestamp 严格排序逐 Tick 推送，禁止跨 Tick 跳跃
  - 每Tick携带5档盘口快照（askPrice/bidPrice/askVol/bidVol）
  - 支持回放速度控制（real_time / fast_forward / max_speed）
  - 支持回放时间窗口（如开盘5分钟 09:30-09:35）
  - 支持多标的按时间戳对齐回放（组合做T场景）
  - 推送 TickEvent 事件给 EventDrivenEngine
  - 30秒冲高回落捕捉（做T核心场景）
  - 5秒级 K线聚合（从 Tick 流合成）

约束:
  - PIT 铁律：仅推送当前时间戳的 Tick，不预读未来数据
  - 数据来源：MiniQmtProvider.fetch_historical(interval="tick")
  - 禁止跨 Tick 跳跃（即使时间戳间隔很大也按原始顺序推送）

SSoT: docs/03_modules/_domain_backtest/blueprint.md §16.7 tick_replay.py 详细规格
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime, time as dtime
from decimal import Decimal
from typing import Any, Optional

import pandas as pd

from zephyr.backtest.core.matching_logic import TickSnapshot

_logger = logging.getLogger(__name__)


class TickReplayError(Exception):
    """Tick 回放引擎错误"""

    error_code = "ZA-BT-0002"

    def __init__(self, *args, error_code: str | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if error_code is not None:
            self.error_code = error_code


@dataclass(frozen=True)
class TickReplayConfig:
    """Tick 回放配置（frozen）

    Attributes:
        speed: 回放速度模式
            - "real_time": 1x实时（每Tick间隔=原始时间戳间隔）
            - "fast_forward": Nx倍速（可配 fast_forward_ratio）
            - "max_speed": 最快（无延迟，仅受CPU限制）
        fast_forward_ratio: 倍速倍数（speed="fast_forward" 时生效，默认10x）
        time_window: 回放时间窗口 (start_time, end_time)
            - 格式: ("09:30:00", "09:35:00") 表示只回放开盘5分钟
            - None: 全天回放
        aggregate_5s: 是否启用5秒级K线聚合（做T辅助）
    """

    speed: str = "max_speed"
    fast_forward_ratio: int = 10
    time_window: Optional[tuple[str, str]] = None
    aggregate_5s: bool = False


@dataclass
class TickEvent:
    """Tick 回放事件（推送给 EventDrivenEngine）

    Attributes:
        timestamp: Tick 时间戳
        symbol: 标的代码
        tick_data: TickSnapshot（含5档盘口）
        sequence: 序列号（从0开始递增）
    """

    timestamp: Any
    symbol: str
    tick_data: TickSnapshot
    sequence: int = 0


@dataclass
class ReplayStatistics:
    """回放统计

    Attributes:
        total_ticks: Tick 总数
        total_duration_s: 实际耗时（秒）
        avg_rate: 平均速率（Tick/秒）
        symbols: 回放的标的列表
        time_range: 时间范围 (start, end)
    """

    total_ticks: int = 0
    total_duration_s: float = 0.0
    avg_rate: float = 0.0
    symbols: list[str] = field(default_factory=list)
    time_range: tuple[Any, Any] = (None, None)


class TickReplayEngine:
    """Tick 回放引擎（秒级做T专用）

    按 timestamp 严格排序逐 Tick 推送，支持多标的按时间戳对齐回放。

    回放速度控制:
      - real_time: 每Tick间隔=原始时间戳间隔（1x实时）
      - fast_forward: Nx倍速（间隔=原始间隔/ratio）
      - max_speed: 无延迟（仅受CPU限制）

    做T场景适配:
      - 30秒冲高回落: 精确捕捉30秒内 last_price 变化路径
      - 5秒级K线聚合: 从Tick流合成5秒K线
      - 盘口挂单监控: 实时推送 askVol/bidVol 变化

    Usage:
        provider = MiniQmtProvider(path="E:/国金证券QMT交易端/userdata_mini")
        engine = TickReplayEngine(
            provider=provider,
            symbols=["600000.SH", "000001.SZ"],
            start=datetime(2024, 1, 15),
            end=datetime(2024, 1, 15),
            config=TickReplayConfig(speed="max_speed"),
        )

        def on_tick(event: TickEvent) -> None:
            print(f"{event.timestamp} {event.symbol} price={event.tick_data.last_price}")
            # 做T策略：检测30秒冲高回落
            ...

        engine.run(callback=on_tick)
        stats = engine.get_statistics()
        print(f"回放完成: {stats.total_ticks} Ticks, 耗时 {stats.total_duration_s:.2f}s")
    """

    def __init__(
        self,
        provider: object,
        symbols: list[str],
        start: datetime,
        end: datetime,
        config: Optional[TickReplayConfig] = None,
    ):
        """初始化 Tick 回放引擎

        Args:
            provider: MiniQmtProvider 实例（提供 fetch_historical interval="tick"）
            symbols: 标的代码列表
            start: 回放开始时间
            end: 回放结束时间
            config: 回放配置（可选，默认 max_speed 全天回放）

        Raises:
            TickReplayError: 参数无效
        """
        if not symbols:
            raise TickReplayError("symbols 不能为空")
        if provider is None:
            raise TickReplayError("provider 不能为空")

        self._provider = provider
        self._symbols = list(symbols)
        self._start = start
        self._end = end
        self._config = config or TickReplayConfig()

        # 回放状态
        self._merged_ticks: list[dict[str, Any]] = []
        self._loaded = False
        self._statistics = ReplayStatistics(symbols=list(symbols))

        # 5秒级K线聚合缓冲
        self._agg_buffer: dict[str, list[TickSnapshot]] = {}
        if self._config.aggregate_5s:
            for sym in symbols:
                self._agg_buffer[sym] = []

    def run(self, callback: Callable[[TickEvent], None]) -> None:
        """执行 Tick 回放，逐 Tick 推送给 callback

        Args:
            callback: Tick 事件回调函数，接收 TickEvent

        Raises:
            TickReplayError: 加载失败或回放过程中出错
        """
        if not self._loaded:
            self._load_and_merge_ticks()

        if not self._merged_ticks:
            _logger.warning("Tick 回放数据为空，无法执行回放")
            return

        _logger.info(
            "开始 Tick 回放: %d ticks, symbols=%s, speed=%s",
            len(self._merged_ticks),
            self._symbols,
            self._config.speed,
        )

        start_wall = time.time()
        prev_timestamp: Optional[datetime] = None
        seq = 0

        for tick_row in self._merged_ticks:
            timestamp = tick_row["timestamp"]
            symbol = tick_row["symbol"]

            # 速度控制
            if prev_timestamp is not None and self._config.speed != "max_speed":
                self._apply_speed_control(prev_timestamp, timestamp)

            # 构造 TickSnapshot
            tick_snapshot = self._row_to_tick_snapshot(tick_row, symbol)

            # 推送 TickEvent
            event = TickEvent(
                timestamp=timestamp,
                symbol=symbol,
                tick_data=tick_snapshot,
                sequence=seq,
            )
            try:
                callback(event)
            except Exception as e:
                _logger.error("Tick 回调执行错误 seq=%d symbol=%s: %s", seq, symbol, e, exc_info=True)

            # 5秒级K线聚合
            if self._config.aggregate_5s:
                self._update_aggregation(symbol, tick_snapshot, timestamp, callback)

            prev_timestamp = timestamp
            seq += 1

        end_wall = time.time()
        self._statistics.total_ticks = seq
        self._statistics.total_duration_s = end_wall - start_wall
        if self._statistics.total_duration_s > 0:
            self._statistics.avg_rate = (
                seq / self._statistics.total_duration_s
            )
        if self._merged_ticks:
            self._statistics.time_range = (
                self._merged_ticks[0]["timestamp"],
                self._merged_ticks[-1]["timestamp"],
            )

        _logger.info(
            "Tick 回放完成: %d ticks, 耗时 %.2fs, 平均速率 %.0f ticks/s",
            self._statistics.total_ticks,
            self._statistics.total_duration_s,
            self._statistics.avg_rate,
        )

    def get_statistics(self) -> ReplayStatistics:
        """获取回放统计

        Returns:
            ReplayStatistics: 回放统计（Tick总数/耗时/平均速率/标的列表/时间范围）
        """
        return self._statistics

    # ------------------------------------------------------------------
    # 私有方法
    # ------------------------------------------------------------------

    def _load_and_merge_ticks(self) -> None:
        """从 provider 加载所有 symbol 的 Tick 并按时间戳合并"""
        all_ticks: list[pd.DataFrame] = []

        for symbol in self._symbols:
            try:
                df = self._provider.fetch_historical(
                    symbol=symbol,
                    start=self._start,
                    end=self._end,
                    interval="tick",
                )
            except Exception as e:
                _logger.error("加载 Tick 数据失败 symbol=%s: %s", symbol, e, exc_info=True)
                raise TickReplayError(
                    f"加载 Tick 数据失败 symbol={symbol}: {e}"
                ) from e

            if df is None or df.empty:
                _logger.warning("symbol=%s 的 Tick 数据为空，跳过", symbol)
                continue

            # 时间窗口过滤
            df = self._apply_time_window(df)
            if df.empty:
                continue

            all_ticks.append(df)

        if not all_ticks:
            self._loaded = True
            return

        # 合并所有 symbol 的 tick，按 timestamp 排序
        merged = pd.concat(all_ticks, ignore_index=True)
        merged = merged.sort_values("timestamp").reset_index(drop=True)

        # 转换为 dict 列表（避免 pandas 行迭代开销）
        self._merged_ticks = merged.to_dict("records")
        self._loaded = True

        _logger.info(
            "Tick 数据加载完成: %d ticks, symbols=%s",
            len(self._merged_ticks),
            self._symbols,
        )

    def _apply_time_window(self, df: pd.DataFrame) -> pd.DataFrame:
        """应用时间窗口过滤（如只回放开盘5分钟 09:30-09:35）

        Args:
            df: Tick DataFrame（含 timestamp 列）

        Returns:
            过滤后的 DataFrame
        """
        if self._config.time_window is None:
            return df

        start_str, end_str = self._config.time_window
        start_time = dtime.fromisoformat(start_str)
        end_time = dtime.fromisoformat(end_str)

        # 提取时间部分进行比较
        tick_times = pd.to_datetime(df["timestamp"]).dt.time
        mask = (tick_times >= start_time) & (tick_times <= end_time)
        return df[mask].reset_index(drop=True)

    def _apply_speed_control(
        self, prev_ts: datetime, curr_ts: datetime
    ) -> None:
        """应用速度控制（real_time / fast_forward）

        Args:
            prev_ts: 上一个 Tick 时间戳
            curr_ts: 当前 Tick 时间戳
        """
        if prev_ts >= curr_ts:
            return  # 同一时刻或乱序，不 sleep

        delta = (curr_ts - prev_ts).total_seconds()

        if self._config.speed == "real_time":
            # 1x 实时：sleep 实际间隔
            if delta > 0:
                time.sleep(min(delta, 1.0))  # 上限1秒避免长时间阻塞
        elif self._config.speed == "fast_forward":
            # Nx 倍速：sleep 实际间隔 / ratio
            ratio = max(self._config.fast_forward_ratio, 1)
            sleep_time = delta / ratio
            if sleep_time > 0:
                time.sleep(min(sleep_time, 0.5))

    def _row_to_tick_snapshot(
        self, row: dict[str, Any], symbol: str
    ) -> TickSnapshot:
        """将 DataFrame 行 dict 转换为 TickSnapshot

        Args:
            row: DataFrame 行（dict 形式）
            symbol: 标的代码

        Returns:
            TickSnapshot（含5档盘口）
        """
        def _dec(key: str) -> Decimal:
            val = row.get(key, 0)
            if val is None:
                return Decimal("0")
            return Decimal(str(val))

        def _int(key: str) -> int:
            val = row.get(key, 0)
            if val is None:
                return 0
            return int(val)

        # 5档盘口元组
        ask_price = tuple(_dec(f"ask_price_{i}") for i in range(1, 6))
        bid_price = tuple(_dec(f"bid_price_{i}") for i in range(1, 6))
        ask_vol = tuple(_dec(f"ask_vol_{i}") for i in range(1, 6))
        bid_vol = tuple(_dec(f"bid_vol_{i}") for i in range(1, 6))

        return TickSnapshot(
            symbol=symbol,
            timestamp=row.get("timestamp"),
            last_price=_dec("last_price"),
            open=_dec("open"),
            high=_dec("high"),
            low=_dec("low"),
            prev_close=_dec("prev_close"),
            amount=_dec("amount"),
            volume=_dec("volume"),
            ask_price=ask_price,
            bid_price=bid_price,
            ask_vol=ask_vol,
            bid_vol=bid_vol,
            stock_status=_int("stock_status"),
            transaction_num=_int("transaction_num"),
        )

    def _update_aggregation(
        self,
        symbol: str,
        tick: TickSnapshot,
        timestamp: datetime,
        callback: Callable[[TickEvent], None],
    ) -> None:
        """更新5秒级K线聚合缓冲

        每5秒合成一根K线推送 AggBarEvent（通过 callback 传递特殊事件）

        Args:
            symbol: 标的代码
            tick: 当前 Tick 快照
            timestamp: 当前时间戳
            callback: 回调函数（用于推送聚合K线事件）
        """
        buffer = self._agg_buffer.get(symbol, [])
        buffer.append(tick)

        # 检查是否满5秒
        if len(buffer) < 2:
            return

        first_ts = buffer[0].timestamp
        if first_ts is None:
            return

        # 计算5秒窗口
        try:
            if isinstance(first_ts, datetime) and isinstance(timestamp, datetime):
                delta = (timestamp - first_ts).total_seconds()
                if delta >= 5.0:
                    # 合成5秒K线
                    agg_tick = self._aggregate_to_bar(symbol, buffer)
                    # 推送聚合事件（用特殊 sequence=-1 标识聚合K线）
                    agg_event = TickEvent(
                        timestamp=timestamp,
                        symbol=symbol,
                        tick_data=agg_tick,
                        sequence=-1,  # -1 表示5秒聚合K线
                    )
                    try:
                        callback(agg_event)
                    except Exception as e:
                        _logger.error("聚合K线回调错误 symbol=%s: %s", symbol, e, exc_info=True)
                    # 清空缓冲
                    self._agg_buffer[symbol] = []
        except Exception as e:
            _logger.debug("5秒聚合跳过 symbol=%s: %s", symbol, e, exc_info=True)

    def _aggregate_to_bar(
        self, symbol: str, buffer: list[TickSnapshot]
    ) -> TickSnapshot:
        """将5秒内的 Tick 聚合为一根K线（TickSnapshot 形式）

        聚合规则:
          - open = 第一Tick的 last_price
          - high = max(last_price)
          - low = min(last_price)
          - last_price = 最后Tick的 last_price
          - volume = sum(volume)
          - amount = sum(amount)
          - 盘口取最后Tick的盘口

        Args:
            symbol: 标的代码
            buffer: 5秒内的 Tick 列表

        Returns:
            聚合后的 TickSnapshot
        """
        last = buffer[-1]
        prices = [t.last_price for t in buffer if t.last_price > 0]
        total_vol = sum((t.volume for t in buffer), Decimal("0"))
        total_amount = sum((t.amount for t in buffer), Decimal("0"))

        return TickSnapshot(
            symbol=symbol,
            timestamp=last.timestamp,
            last_price=last.last_price,
            open=buffer[0].last_price,
            high=max(prices) if prices else Decimal("0"),
            low=min(prices) if prices else Decimal("0"),
            prev_close=last.prev_close,
            amount=total_amount,
            volume=total_vol,
            ask_price=last.ask_price,
            bid_price=last.bid_price,
            ask_vol=last.ask_vol,
            bid_vol=last.bid_vol,
            stock_status=last.stock_status,
            transaction_num=last.transaction_num,
        )


__all__ = [
    "TickReplayEngine",
    "TickReplayConfig",
    "TickReplayError",
    "TickEvent",
    "ReplayStatistics",
]

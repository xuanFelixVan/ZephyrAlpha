# [BLUEPRINT] MOD-BT-CHTP
# [MODULE] zephyr.governance.data_governance.ch_tick_provider
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_writer(只读,延迟加载); pandas
# [CONSUMERS] scripts/run_backtest.py(mode=tick); StrategyRunner.run_tick_backtest(provider 注入)
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只读 c1_market.tick_data; PIT(tick 只取 start~end 窗口); 列名适配 EDE 18 字段契约
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH不可达->RuntimeError; 无数据->返回空DataFrame(调用方跳过该标的)
# [TESTS] scripts/run_backtest.py --strategy topn-momentum --mode tick（端到端）
# [A_module] module_id=MOD-BT-CHTP | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
CH Tick Provider——从 c1_market.tick_data 读历史 tick，适配 EDE/tick_replay 的
fetch_historical(interval="tick") 契约（MiniQmtQuoteProvider 的 CH 替身）。

治本动机（#BT-PIPELINE-001 阶段五，Owner 2026-09-01 要求 tick 级完全仿真）：
    EDE 事件驱动引擎的 tick 燃料原本只有 MiniQmtQuoteProvider（依赖 miniQMT
    通道，券商 2026-09-18 关停）；而 CH tick_data 表已有 83 亿行/1.1 万标的/
    覆盖至当日的 3 秒级 tick（bdpan 录制）——本 provider 把这批存量+持续增量
    的数据接进 EDE 撮合管道，tick 仿真不再依赖 miniQMT 通道。

字段适配（tick_data → EDE TickSnapshot 18 字段）：
    price→last_price；bid_price/ask_price/bid_volume/ask_volume（一档）→
    bid_price_1/ask_price_1/bid_vol_1/ask_vol_1；二~五档填 0（tick_data 表
    只有 L1 一档，撮合深度受一档容量约束——诚实降级，非造假数据）；
    open/high/low/prev_close/stock_status/transaction_num 表中无列填 0
    （EDE 撮合只消费 last_price+盘口，这些字段不参与成交路径）。

机构对照：此形态即专业回测平台的「tick 回放（Tick Replay）」数据层——
聚宽/掘金 tick 回测、机构事件驱动仿真（Abacus 类）同构。
"""

from __future__ import annotations

import logging
from datetime import datetime

import pandas as pd

log = logging.getLogger(__name__)

_SQL_TICK = (
    "SELECT timestamp, symbol, price, volume, amount, bid_price, ask_price, bid_volume, ask_volume "
    "FROM c1_market.tick_data "
    "WHERE symbol = %(sym)s AND trade_date >= %(start)s AND trade_date <= %(end)s "
    "AND price > 0 "
    "ORDER BY timestamp"
)


class ChTickProviderError(Exception):
    """CH Tick Provider 错误"""


class ChTickProvider:
    """ClickHouse tick_data 历史 Tick Provider（EDE fetch_historical 契约）。

    Usage:
        provider = ChTickProvider()
        df = provider.fetch_historical(symbol="600000.SH", start=dt, end=dt, interval="tick")
    """

    def __init__(self, chunk_days: int = 5) -> None:
        """Args:
        chunk_days: 单标的单次查询按日分块（tick_data 3 秒粒度，单日单标的约
                    5k 行；分块防大区间单查询内存峰值）
        """
        self._chunk_days = max(1, int(chunk_days))

    @staticmethod
    def _client():
        from zephyr.data.ch_writer import get_client

        client = get_client()
        if client is None:
            raise ChTickProviderError("ClickHouse 不可达（get_client 返回 None）")
        return client

    def fetch_historical(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        interval: str = "tick",
    ) -> pd.DataFrame:
        """拉取历史 tick（EDE 18 字段契约适配）。

        Args:
            symbol: 带后缀代码（600000.SH）——与 EDE event.symbol 同口径
            start/end: datetime（tick_data.trade_date 过滤）
            interval: 仅支持 "tick"
        """
        if interval != "tick":
            raise ChTickProviderError(f"仅支持 interval='tick'，收到: {interval}")
        sym = str(symbol).split(".")[0]   # tick_data.symbol=纯数字（与 kline_daily 同口径）
        start_d = start.strftime("%Y-%m-%d")
        end_d = end.strftime("%Y-%m-%d")
        client = self._client()

        frames: list[pd.DataFrame] = []
        cur = datetime.strptime(start_d, "%Y-%m-%d")
        end_dt = datetime.strptime(end_d, "%Y-%m-%d")
        from datetime import timedelta

        while cur <= end_dt:
            seg_end = min(cur + timedelta(days=self._chunk_days - 1), end_dt)
            rows = client.execute(
                _SQL_TICK,
                {"sym": sym, "start": cur.strftime("%Y-%m-%d"), "end": seg_end.strftime("%Y-%m-%d")},
            )
            if rows:
                frames.append(pd.DataFrame(rows, columns=["timestamp", "symbol", "price", "volume", "amount", "bid_price", "ask_price", "bid_volume", "ask_volume"]))
            cur = seg_end + timedelta(days=1)

        if not frames:
            log.warning("ChTickProvider: tick_data 无数据 symbol=%s %s~%s", symbol, start_d, end_d)
            return pd.DataFrame()

        df = pd.concat(frames, ignore_index=True)
        # ── EDE TickSnapshot 18+symbol 字段适配（缺失字段填 0，见模块头字段说明） ──
        out = pd.DataFrame()
        out["timestamp"] = df["timestamp"]
        out["symbol"] = symbol   # EDE 分发键=带后缀代码（与 event.symbol 同口径）
        out["last_price"] = df["price"].astype(float)
        out["open"] = 0.0
        out["high"] = 0.0
        out["low"] = 0.0
        out["prev_close"] = 0.0
        out["amount"] = df["amount"].astype(float)
        out["volume"] = df["volume"].astype(float)
        for i in range(1, 6):
            out[f"ask_price_{i}"] = df["ask_price"].astype(float) if i == 1 else 0.0
            out[f"bid_price_{i}"] = df["bid_price"].astype(float) if i == 1 else 0.0
            out[f"ask_vol_{i}"] = df["ask_volume"].astype(float) if i == 1 else 0.0
            out[f"bid_vol_{i}"] = df["bid_volume"].astype(float) if i == 1 else 0.0
        out["stock_status"] = 0
        out["transaction_num"] = 0
        log.info("ChTickProvider: %s %s~%s 共 %d ticks（L1 一档盘口，2-5 档 0）", symbol, start_d, end_d, len(out))
        return out


__all__ = ["ChTickProvider", "ChTickProviderError"]

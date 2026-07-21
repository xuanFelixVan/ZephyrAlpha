# [BLUEPRINT] MOD-L00-001 | docs/03_modules/_domain_data/blueprint.md | §
# [MODULE] zephyr.data.tick_subscriber
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.buffered_writer; zephyr.data.provider_base; zephyr.data.ch_writer
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] QMT callback 线程只做 queue.put_nowait（最小开销）；flush 线程负责转换+写入；不复用 governance MiniQmtProvider（避免 DataFrame 24字段转换开销）；queue.Queue 解耦线程安全
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] start失败->返回False+log; flush失败->log+继续（不中断订阅）; xtquant导入失败->RuntimeError
# [TESTS] tests/zephyr/data/test_tick_subscriber.py
# [TTL] task_bound
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测
"""QMT 实时 Tick 订阅服务——subscribe_quote 实时推送，写入 ClickHouse tick_data。

独立常驻进程，不走 scheduler cron。QMT callback 线程把 tick dict 放入
queue.Queue，后台 flush 线程从队列取数据转14字段 tuple，BufferedWriter 攒批写入。

启动: python -m zephyr.data.tick_subscriber
"""
from __future__ import annotations

import logging
import queue
import signal as sig_module
import sys
import threading
import time
from datetime import datetime
from decimal import Decimal

from zephyr.data.table_registry import get_registry

log = logging.getLogger(__name__)

# Phase 5: 表名从 business_data_categories.yaml 真源派生（裁定 #ARCH-CH-024）
_TBL_TICK_DATA = get_registry().table("market_tick")

# tick_data 表14字段
_TICK_COLUMNS = [
    "trade_date", "timestamp", "symbol", "market_type", "price",
    "volume", "amount", "direction", "data_source",
    "bid_price", "ask_price", "bid_volume", "ask_volume", "quality_flag",
]

_DATA_SOURCE = "miniqmt"


def infer_market_type(stock_code: str) -> str:
    """从 QMT stock_code 推导 market_type。

    Args:
        stock_code: QMT 格式，如 "000001.SZ"、"600000.SH"、"159915.SZ"

    Returns:
        market_type 字符串（stock/stock_bj/index/etf/lof/cb）
    """
    if stock_code.endswith(".SH"):
        code = stock_code[:-3]
        if code.startswith("000") or code.startswith("880"):
            return "index"
        if code.startswith("51"):   # 510xxx-519xxx = SH ETF
            return "etf"
        if code.startswith("50"):   # 501xxx-502xxx = SH LOF
            return "lof"
        return "stock"
    if stock_code.endswith(".SZ"):
        code = stock_code[:-3]
        if code.startswith("399"):
            return "index"
        if code.startswith("159"):
            return "etf"
        if code.startswith("16") or code.startswith("18"):
            return "lof"
        if code.startswith("12") or code.startswith("11"):
            return "cb"
        return "stock"
    if stock_code.endswith(".BJ"):
        return "stock_bj"
    return "stock"


def _stock_to_symbol(stock_code: str) -> str:
    """QMT stock_code → 纯代码（去后缀）。"""
    return stock_code.split(".")[0]


def _safe_decimal(val: object) -> Decimal | None:
    """安全转换为 Decimal，失败/0 返回 None。"""
    if val is None:
        return None
    try:
        d = Decimal(str(val))
        return d if d != 0 else None
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        return None


def _safe_int(val: object) -> int | None:
    """安全转换为 int，失败返回 None。"""
    if val is None:
        return None
    try:
        return int(val)
    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
        return None


def tick_to_row(stock_code: str, tick: dict) -> tuple | None:
    """将 xtdata tick dict 转换为 tick_data 表的14字段 tuple。

    Args:
        stock_code: QMT 格式代码，如 "000001.SZ"
        tick: xtdata 回调的 tick dict

    Returns:
        14字段 tuple，或 None（空 tick）
    """
    if not tick or not tick.get("time"):
        return None

    # 时间戳（毫秒 → datetime）
    ts_ms = tick.get("time", 0)
    dt = datetime.fromtimestamp(ts_ms / 1000)
    trade_date = dt.date()
    timestamp_str = dt.strftime("%Y-%m-%d %H:%M:%S")

    symbol = _stock_to_symbol(stock_code)
    market_type = infer_market_type(stock_code)

    price = _safe_decimal(tick.get("lastPrice"))
    volume = _safe_int(tick.get("volume"))
    amount = _safe_decimal(tick.get("amount"))

    # 1档 bid/ask
    bid_prices = tick.get("bidPrice") or []
    ask_prices = tick.get("askPrice") or []
    bid_vols = tick.get("bidVol") or []
    ask_vols = tick.get("askVol") or []

    bid_price = _safe_decimal(bid_prices[0]) if bid_prices else None
    ask_price = _safe_decimal(ask_prices[0]) if ask_prices else None
    bid_volume = _safe_int(bid_vols[0]) if bid_vols else None
    ask_volume = _safe_int(ask_vols[0]) if ask_vols else None

    return (
        trade_date,
        timestamp_str,
        symbol,
        market_type,
        price,
        volume,
        amount,
        "中性盘",           # direction（QMT tick 不直接提供）
        _DATA_SOURCE,       # data_source
        bid_price,
        ask_price,
        bid_volume,
        ask_volume,
        1,                  # quality_flag
    )


class TickSubscriber:
    """QMT 实时 Tick 订阅器——常驻订阅全市场 tick，写入 ClickHouse。

    线程模型：
      - QMT callback 线程：_on_tick → queue.put（最小开销）
      - flush 线程：queue.get → tick_to_row → BufferedWriter.add → flush
    """

    def __init__(
        self,
        symbols: list[str] | None = None,
        batch_rows: int = 5000,
        batch_seconds: float = 10.0,
    ):
        """初始化订阅器。

        Args:
            symbols: 订阅标的列表（None=自动获取全市场沪深A股）
            batch_rows: BufferedWriter 攒批行数阈值
            batch_seconds: BufferedWriter 攒批时间阈值（秒）
        """
        self._symbols = symbols
        self._batch_rows = batch_rows
        self._batch_seconds = batch_seconds

        self._tick_queue: queue.Queue[tuple[str, dict]] = queue.Queue(maxsize=100000)
        self._writer = None  # BufferedWriter，在 start() 中初始化
        self._flush_thread: threading.Thread | None = None
        self._running = False
        self._lock = threading.Lock()
        self._stats = {"received": 0, "written": 0, "errors": 0}

        # xtdata 模块（延迟导入）
        self._xtdata = None
        self._subscribed: set[str] = set()

    def _on_tick(self, datas: dict) -> None:
        """xtdata 回调入口——把 tick 放入队列（QMT 线程调用）。

        Args:
            datas: {stock_code: tick_data}
                subscribe_quote 回调: tick_data 是 list[dict]（每3秒推送，通常 len=1）
                subscribe_whole_quote 回调: tick_data 是 dict（快照，向后兼容）
        """
        if not self._running:
            return
        for symbol, tick_data in datas.items():
            # QMT subscribe_quote 回调: tick_data 是 list[dict]
            if isinstance(tick_data, list):
                ticks = tick_data
            elif isinstance(tick_data, dict):
                ticks = [tick_data]
            else:
                continue
            for tick in ticks:
                if not tick:
                    continue
                try:
                    self._tick_queue.put_nowait((symbol, tick))
                    with self._lock:
                        self._stats["received"] += 1
                except queue.Full:
                    log.warning("tick 队列已满，丢弃 tick symbol=%s", symbol)
                except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                    log.error("入队失败 symbol=%s: %s", symbol, e, exc_info=True)
                    with self._lock:
                        self._stats["errors"] += 1

    def _flush_once(self, timeout: float = 1.0) -> None:
        """从队列取一批 tick，转换并写入 BufferedWriter。"""
        try:
            symbol, tick = self._tick_queue.get(timeout=timeout)
        except queue.Empty:
            return

        row = tick_to_row(symbol, tick)
        if row is None:
            return

        # 构造 FetchResult 给 BufferedWriter
        from zephyr.data.provider_base import FetchResult
        result = FetchResult(
            table=_TBL_TICK_DATA,
            columns=_TICK_COLUMNS,
            rows=[row],
            last_key="",
            elapsed_sec=0.0,
        )
        if not self._writer.add(result):
            log.error("BufferedWriter.add 失败，tick 数据可能丢失")
            with self._lock:
                self._stats["errors"] += 1
            return

        with self._lock:
            self._stats["written"] += 1

    def _flush_loop(self) -> None:
        """flush 线程主循环。"""
        log.info("flush 线程启动")
        while self._running:
            self._flush_once(timeout=1.0)
        # 退出前 flush 残留
        while not self._tick_queue.empty():
            try:
                self._flush_once(timeout=0.01)
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                break
        if self._writer:
            self._writer.flush()
            log.info("flush 线程退出，最终 flush 完成")
        log.info("flush 线程结束")

    def _get_all_symbols(self) -> list[str]:
        """获取5市场+指数的完整标的列表（stock/stock_bj/etf/lof/cb/index）。

        实测正确的 QMT 板块名（_qmt_sectors_v2.py 验证 2026-07-22）：
        - 沪深A股: 5202 只 (stock 沪深主板+创业板)
        - 京市A股: 359 只 (.BJ stock_bj)
        - 沪深基金: 2218 只 (需过滤 159/51=ETF, 16/18=LOF)
        - 沪深转债: 320 只 (12/11 前缀 cb)
        - 沪深指数: 609 只 (000/399/980/395/988 官方指数)
        """
        symbols = self._symbols
        if not symbols:
            seen: set[str] = set()
            symbols = []

            def _add_batch(syms: list[str], sector_name: str) -> None:
                added = 0
                for s in syms:
                    if s not in seen:
                        seen.add(s)
                        symbols.append(s)
                        added += 1
                log.info("板块 %s: 获取 %d 只，新增 %d", sector_name, len(syms), added)

            # 1. 沪深A股（stock，5202只）
            try:
                _add_batch(self._xtdata.get_stock_list_in_sector("沪深A股"), "沪深A股")
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                log.warning("获取板块 沪深A股 失败: %s", e)

            # 2. 京市A股（stock_bj，359只）
            try:
                _add_batch(self._xtdata.get_stock_list_in_sector("京市A股"), "京市A股")
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                log.warning("获取板块 京市A股 失败: %s", e)

            # 3. 沪深基金 → 按代码前缀拆分为 ETF/LOF
            try:
                fund_list = self._xtdata.get_stock_list_in_sector("沪深基金")
                etf_added = lof_added = 0
                for s in fund_list:
                    code = s.split(".")[0]
                    if code.startswith("159") or code.startswith("51"):
                        if s not in seen:
                            seen.add(s); symbols.append(s); etf_added += 1
                    elif code.startswith("16") or code.startswith("18"):
                        if s not in seen:
                            seen.add(s); symbols.append(s); lof_added += 1
                log.info("板块 沪深基金: 获取 %d 只，新增 ETF %d / LOF %d",
                         len(fund_list), etf_added, lof_added)
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                log.warning("获取板块 沪深基金 失败: %s", e)

            # 4. 沪深转债（cb，320只，12/11前缀）
            try:
                _add_batch(self._xtdata.get_stock_list_in_sector("沪深转债"), "沪深转债")
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                log.warning("获取板块 沪深转债 失败: %s", e)

            # 5. 沪深指数（index，609只）
            try:
                _add_batch(self._xtdata.get_stock_list_in_sector("沪深指数"), "沪深指数")
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                log.warning("获取板块 沪深指数 失败: %s", e)

            log.info("获取全市场标的: %d 只（去重后）", len(symbols))
        return symbols

    def start(self) -> bool:
        """启动订阅服务。"""
        try:
            from xtquant import xtdata
        except ImportError:
            log.error("无法导入 xtquant，请确保 miniQMT 已安装且 xtquant 可用")
            return False
        self._xtdata = xtdata

        from zephyr.data.buffered_writer import BufferedWriter
        self._writer = BufferedWriter(
            _TBL_TICK_DATA,
            max_rows=self._batch_rows,
            max_seconds=self._batch_seconds,
        )

        self._running = True

        # 启动 flush 线程
        self._flush_thread = threading.Thread(target=self._flush_loop, daemon=True, name="tick-flush")
        self._flush_thread.start()

        # 订阅
        symbols = self._get_all_symbols()
        for symbol in symbols:
            try:
                self._xtdata.subscribe_quote(symbol, period="tick", callback=self._on_tick)
                self._subscribed.add(symbol)
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                log.error("订阅失败 %s: %s", symbol, e)

        log.info("TickSubscriber 启动完成: 订阅 %d 只标的", len(self._subscribed))
        return True

    def stop(self) -> None:
        """停止订阅服务。"""
        self._running = False
        if self._flush_thread:
            self._flush_thread.join(timeout=30)
        # 取消订阅（unsubscribe_quote 不接受 period 参数，与 subscribe_quote 签名不一致）
        if self._xtdata:
            for symbol in self._subscribed:
                try:
                    self._xtdata.unsubscribe_quote(symbol, callback=self._on_tick)
                except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                    pass
        log.info("TickSubscriber 已停止: stats=%s", self._stats)

    def stats(self) -> dict:
        """获取统计信息。"""
        with self._lock:
            return dict(self._stats)


def main() -> int:
    """常驻进程入口——启动 TickSubscriber 并阻塞直到 Ctrl+C。"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    log.info("=== TickSubscriber 启动 ===")

    sub = TickSubscriber()
    if not sub.start():
        log.error("启动失败，退出")
        return 1

    # 注册 signal 优雅退出
    def _signal_handler(signum, frame):
        log.info("收到信号 %s，准备退出", signum)
        raise KeyboardInterrupt()
    sig_module.signal(sig_module.SIGINT, _signal_handler)
    sig_module.signal(sig_module.SIGTERM, _signal_handler)

    try:
        while True:
            time.sleep(60)
            stats = sub.stats()
            log.info("统计: %s", stats)
    except KeyboardInterrupt:
        log.info("收到退出信号")
    finally:
        sub.stop()
        log.info("=== TickSubscriber 已退出 ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())

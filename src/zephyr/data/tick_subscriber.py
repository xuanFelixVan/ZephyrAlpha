# [BLUEPRINT] MOD-L00-001 | docs/03_modules/_domain_data/blueprint.md | §
# [MODULE] zephyr.data.tick_subscriber
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.wal_writer; zephyr.data.provider_base; zephyr.data.table_registry; zephyr.shared.observability.metrics; zephyr.shared.observability.metrics_server
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INARIANTS] QMT callback 线程只做 queue.put_nowait（最小开销）; flush 线程批量出队(500条)构造单个 FetchResult 交给 WalWriter; WalWriter 先落盘段文件再异步 drain 到 CH（P0-1 主动WAL）; 无锁计数(CPython GIL 保证 int += 1 统计精度足够); queue.Queue 解耦线程安全; P1-5 metrics 埋点覆盖 received/written/dropped/queue_size; P2-5 分阶段延迟度量 Histogram: Stage1 on_tick/Stage2 queue_wait/Stage3 convert/Stage4 wal_add/Stage5 wal_flush
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] start失败->返回False+log; drain_batch失败->log+继续（不中断订阅）; xtquant导入失败->RuntimeError
# [TESTS] tests/zephyr/data/test_tick_subscriber.py
# [TTL] task_bound
# noqa: m03-duplicate  M03豁免: AI趋同演化(不同模块为相似问题生成相似代码),非复制粘贴;M05(文件复制对=0)已覆盖文件级复制检测
"""QMT 实时 Tick 订阅服务——subscribe_quote 实时推送，写入 ClickHouse tick_data。

独立常驻进程，不走 scheduler cron。QMT callback 线程把 tick dict 放入
queue.Queue，后台 flush 线程批量出队转14字段 tuple，WalWriter 先落盘段文件
再异步 drain 到 ClickHouse（P0-1 主动 WAL 架构，裁定 #ARCH-CH-013 升级）。

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
from zephyr.shared.observability.metrics import get_registry as _get_metrics_registry
from zephyr.shared.observability.metrics_server import start_metrics_server

log = logging.getLogger(__name__)

# Phase 5: 表名从 business_data_categories.yaml 真源派生（裁定 #ARCH-CH-024）
_TBL_TICK_DATA = get_registry().table("market_tick")

# tick_data 表15字段（P0-1: 新增 recorded_time）
_TICK_COLUMNS = [
    "trade_date", "timestamp", "recorded_time", "symbol", "market_type", "price",
    "volume", "amount", "direction", "data_source",
    "bid_price", "ask_price", "bid_volume", "ask_volume", "quality_flag",
]

_DATA_SOURCE = "miniqmt"

# P0-2: 批量出队上限（减少 WalWriter.add 调用次数）
_DRAIN_BATCH_SIZE = 500


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


def tick_to_row(stock_code: str, tick: dict, data_source: str = _DATA_SOURCE) -> tuple | None:
    """将 xtdata tick dict 转换为 tick_data 表的15字段 tuple。

    P0-1 双时间戳：timestamp=上游市场时间(event_time)，recorded_time=本地接收时间。
    recorded_time - timestamp = 端到端延迟，用于回测延迟建模。
    P1-3：data_source 参数支持备源标识（tdx_backup），区分主源/备源数据。

    Args:
        stock_code: QMT 格式代码，如 "000001.SZ"
        tick: xtdata 回调的 tick dict
        data_source: 数据来源标识（默认 "miniqmt"，备源用 "tdx_backup"）

    Returns:
        15字段 tuple，或 None（空 tick）
    """
    if not tick or not tick.get("time"):
        return None

    # 时间戳（毫秒 → datetime）
    ts_ms = tick.get("time", 0)
    dt = datetime.fromtimestamp(ts_ms / 1000)
    trade_date = dt.date()
    timestamp_str = dt.strftime("%Y-%m-%d %H:%M:%S")

    # P0-1: recorded_time = 录制器本地接收时间（用于延迟分析）
    recorded_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
        recorded_time_str,  # P0-1: 录制器本地接收时间
        symbol,
        market_type,
        price,
        volume,
        amount,
        "中性盘",           # direction（QMT tick 不直接提供）
        data_source,        # data_source（P1-3: 支持备源标识）
        bid_price,
        ask_price,
        bid_volume,
        ask_volume,
        1,                  # quality_flag
    )


class TickSubscriber:
    """QMT 实时 Tick 订阅器——常驻订阅全市场 tick，写入 ClickHouse。

    线程模型（P0-1 主动 WAL 架构）：
      - QMT callback 线程：_on_tick → queue.put_nowait（最小开销，无锁计数）
      - flush 线程：_drain_batch 批量出队(500条) → WalWriter.add（先落盘段文件）
      - WalWriter drain 线程：段文件 → ch_writer → ClickHouse（异步排空）
    """

    def __init__(
        self,
        symbols: list[str] | None = None,
        batch_rows: int = 3000,
        batch_seconds: float = 5.0,
        heartbeat=None,
        backup_provider=None,
        tick_cache=None,
    ):
        """初始化订阅器。

        Args:
            symbols: 订阅标的列表（None=自动获取全市场沪深A股）
            batch_rows: WalWriter 段落盘行数阈值（P0-3: 5000→3000）
            batch_seconds: WalWriter 段落盘时间阈值（P0-3: 10.0→5.0）
            heartbeat: HeartbeatMonitor 实例（P2-8 集成，可选）。
                传入后在 _on_tick 中自动调用 record_tick()，使主源心跳检测生效。
            backup_provider: TDXProvider 实例（P1-3 双源冗余，可选）。
                传入后与 heartbeat 配合，主源中断时自动切换 TDX 备源轮询。
            tick_cache: TickRedisCache 实例（H1 Redis 热缓存双写，可选）。
                传入后 _drain_batch 批量写入 tick:{symbol}:latest 到 Redis（CP-01）。
        """
        self._symbols = symbols
        self._batch_rows = batch_rows
        self._batch_seconds = batch_seconds
        self._heartbeat = heartbeat  # P2-8: 主源心跳检测集成
        self._backup_provider = backup_provider  # P1-3: TDX 备源
        self._tick_cache = tick_cache  # H1 Redis tick 缓存双写
        self._switcher = None  # P1-3: SourceSwitcher（start 中创建）
        self._backup_poller = None  # P1-3: BackupTickPoller

        self._tick_queue: queue.Queue[tuple[str, dict]] = queue.Queue(maxsize=100000)
        self._writer = None  # WalWriter，在 start() 中初始化
        self._flush_thread: threading.Thread | None = None
        self._running = False
        # P0-2: 无锁计数（CPython GIL 保证 int += 1 统计精度足够，消除锁竞争）
        self._received = 0
        self._written = 0
        self._errors = 0

        # P0-2: 预热逻辑——订阅完成 + 首个 tick 收到 = ready
        # Event 在 _on_tick 首次成功入队后 set()，start() 中 wait(timeout) 阻塞等待
        self._first_tick_received = threading.Event()
        self._start_time: float = 0.0  # 订阅启动时间（用于预热耗时统计）

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
        # P2-5: Stage 1 延迟度量——on_tick 回调处理耗时
        t0 = time.perf_counter()
        # P2-8: 主源心跳检测——收到 tick 即标记主源活跃
        if self._heartbeat is not None:
            self._heartbeat.record_tick()
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
                    self._received += 1  # 无锁计数
                    _get_metrics_registry().inc("zephyr_tick_received_total")
                    # P0-2: 首个 tick 成功入队 → 解除 start() 预热等待
                    # is_set() 仅读 bool（GIL 原子），set() 需加锁，check-first 避免热路径锁竞争
                    if not self._first_tick_received.is_set():
                        self._first_tick_received.set()
                except queue.Full:
                    log.warning("tick 队列已满，丢弃 tick symbol=%s", symbol)
                    self._errors += 1
                    _get_metrics_registry().inc("zephyr_tick_dropped_total")
                except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                    log.error("入队失败 symbol=%s: %s", symbol, e, exc_info=True)
                    self._errors += 1
                    _get_metrics_registry().inc("zephyr_tick_dropped_total")
        # P2-5: Stage 1——on_tick 回调端到端处理耗时（含心跳记录 + 入队循环）
        _get_metrics_registry().observe(
            "zephyr_tick_stage_on_tick_seconds", time.perf_counter() - t0
        )

    def _on_backup_tick(self, symbol: str, tick: dict) -> None:
        """备源 tick 回调——TDX BackupTickPoller 调用（P1-3）。

        将备源 tick 喂入同一队列，通过 tick["_data_source"] 标记来源，
        _drain_batch 中 tick_to_row 据此设置 data_source="tdx_backup"。
        """
        if not self._running:
            return
        tick["_data_source"] = "tdx_backup"
        try:
            self._tick_queue.put_nowait((symbol, tick))
            self._received += 1
            _get_metrics_registry().inc("zephyr_tick_received_total")
        except queue.Full:
            log.warning("tick 队列已满，丢弃备源 tick symbol=%s", symbol)
            self._errors += 1
            _get_metrics_registry().inc("zephyr_tick_dropped_total")

    def _drain_batch(self, max_n: int = _DRAIN_BATCH_SIZE, timeout: float = 1.0) -> int:
        """批量出队——阻塞等待第一条，然后非阻塞批量取剩余。

        构造单个 FetchResult（多行）交给 WalWriter，减少 add 调用次数。

        P2-5 分阶段延迟度量：
          - Stage 2: queue.get 阻塞等待耗时
          - Stage 3: tick_to_row 批量转换耗时
          - Stage 4: WalWriter.add 段落盘耗时

        Returns:
            本次写入 WalWriter 的行数（0=队列空或写入失败）。
        """
        reg = _get_metrics_registry()
        # P2-5: Stage 2——queue.get 阻塞等待耗时（含空队 sleep）
        t_wait = time.perf_counter()
        try:
            symbol, tick = self._tick_queue.get(timeout=timeout)
        except queue.Empty:
            return 0
        reg.observe("zephyr_tick_stage_queue_wait_seconds", time.perf_counter() - t_wait)

        rows: list[tuple] = []
        cache_ticks: list[tuple[str, dict]] = []  # H1 Redis tick 缓存双写收集
        # P2-5: Stage 3——tick_to_row 批量转换耗时（首行 + 非阻塞批量取）
        t_conv = time.perf_counter()
        row = tick_to_row(symbol, tick, data_source=tick.pop("_data_source", _DATA_SOURCE))
        if row:
            rows.append(row)
        cache_ticks.append((symbol, tick))
        for _ in range(max_n - 1):
            try:
                symbol, tick = self._tick_queue.get_nowait()
            except queue.Empty:
                break
            r = tick_to_row(symbol, tick, data_source=tick.pop("_data_source", _DATA_SOURCE))
            if r:
                rows.append(r)
            cache_ticks.append((symbol, tick))
        reg.observe("zephyr_tick_stage_convert_seconds", time.perf_counter() - t_conv)

        if not rows:
            return 0
        from zephyr.data.provider_base import FetchResult
        result = FetchResult(
            table=_TBL_TICK_DATA,
            columns=_TICK_COLUMNS,
            rows=rows,
            last_key="",
            elapsed_sec=0.0,
        )
        # P2-5: Stage 4——WalWriter.add 段落盘耗时（含列过滤 + save_fallback）
        t_wal = time.perf_counter()
        add_ok = self._writer.add(result)
        reg.observe("zephyr_tick_stage_wal_add_seconds", time.perf_counter() - t_wal)

        # H1 Redis tick 缓存双写（best-effort，不阻断 WAL 主路径，CP-01 Tick→Redis ≤3秒）
        if self._tick_cache and cache_ticks:
            try:
                self._tick_cache.write_batch(cache_ticks)
            except Exception:  # noqa: BLE001 — best-effort
                log.debug("Redis tick cache write failed (non-fatal)", exc_info=True)

        if add_ok:
            self._written += len(rows)
            reg.inc("zephyr_tick_written_total", n=len(rows))
            return len(rows)
        log.error("WalWriter.add 失败，%d 行 tick 数据可能丢失", len(rows))
        self._errors += len(rows)
        reg.inc("zephyr_tick_dropped_total", n=len(rows))
        return 0

    def _flush_loop(self) -> None:
        """flush 线程主循环——批量出队交给 WalWriter。"""
        log.info("flush 线程启动")
        while self._running:
            self._drain_batch(max_n=_DRAIN_BATCH_SIZE, timeout=1.0)
        # 退出前 drain 残留
        while not self._tick_queue.empty():
            if self._drain_batch(max_n=_DRAIN_BATCH_SIZE, timeout=0.01) == 0:
                break
        # flush 残留段到 WAL 文件（drain 线程由 stop() 停止）
        if self._writer:
            self._writer.flush()
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

    def _wait_for_qmt_ready(self, timeout: float = 120.0, interval: float = 5.0) -> bool:
        """等待 QMT 就绪——连通性检测 + 轮询重试。

        治本（#ARCH-DATA-TICK-GAP-001 后续，2026-07-31）：
        tick_subscriber 启动早于 QMT 客户端时，subscribe_quote 静默失败。
        本方法在订阅前用 get_market_data_ex 探活，QMT 未就绪则等待重试。
        """
        deadline = time.time() + timeout
        attempt = 0
        while time.time() < deadline:
            attempt += 1
            try:
                data = self._xtdata.get_market_data_ex(
                    [], ["000001.SZ"], period="1m", count=1
                )
                if data and "000001.SZ" in data:
                    df = data["000001.SZ"]
                    if df is not None and len(df) > 0:
                        log.info("QMT 连通性检测通过 (attempt=%d)", attempt)
                        return True
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                log.debug("QMT 探活异常 (attempt=%d): %s", attempt, e)
            remaining = deadline - time.time()
            if remaining > 0:
                log.warning(
                    "QMT 未就绪 (attempt=%d)，%.0fs 后重试（剩余 %.0fs）",
                    attempt, interval, remaining,
                )
                time.sleep(interval)
        log.error("QMT 连通性检测超时(%.0fs)，订阅可能失败", timeout)
        return False

    def _subscribe_all_symbols(self, symbols: list[str]) -> int:
        """订阅全市场标的，返回成功订阅数。"""
        for symbol in symbols:
            try:
                self._xtdata.subscribe_quote(symbol, period="tick", callback=self._on_tick)
                self._subscribed.add(symbol)
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                log.error("订阅失败 %s: %s", symbol, e)
        return len(self._subscribed)

    def _wait_for_first_tick(self, symbols: list[str], timeout: float = 30.0) -> bool:
        """预热等待首个 tick，超时则重新订阅一次再等待。

        Returns: True 如果收到首个 tick，False 如果两次等待都超时。
        """
        if not self._subscribed:
            return False
        log.info("预热等待: 已订阅 %d 只标的，等待首个 tick...", len(self._subscribed))
        if self._first_tick_received.wait(timeout=timeout):
            elapsed = time.time() - self._start_time
            log.info("预热完成: 首个 tick 已收到 (耗时 %.1fs)", elapsed)
            return True
        # 治本：预热超时 → 重新订阅（QMT 可能刚就绪，初始订阅可能失败）
        log.warning("预热超时(%.0fs)未收到首个 tick，重新订阅全市场标的...", timeout)
        self._subscribed.clear()
        self._subscribe_all_symbols(symbols)
        if not self._subscribed:
            return False
        log.info("重新订阅完成: %d 只，再次等待首个 tick...", len(self._subscribed))
        if self._first_tick_received.wait(timeout=timeout):
            elapsed = time.time() - self._start_time
            log.info("预热完成: 首个 tick 已收到 (耗时 %.1fs)", elapsed)
            return True
        log.warning("重新订阅后仍未收到 tick，继续运行（可能存在数据缺口）")
        return False

    def start(self) -> bool:
        """启动订阅服务。"""
        try:
            from xtquant import xtdata
        except ImportError:
            log.error("无法导入 xtquant，请确保 miniQMT 已安装且 xtquant 可用")
            return False
        self._xtdata = xtdata

        from zephyr.data.wal_writer import WalWriter
        self._writer = WalWriter(
            _TBL_TICK_DATA,
            segment_max_rows=self._batch_rows,
            segment_max_seconds=self._batch_seconds,
        )
        self._writer.start()  # 启动 drain 线程

        # P1-5: 启动 Prometheus /metrics 端点
        start_metrics_server()

        # P2-8: 启动心跳检测（CH 连通性监测）
        if self._heartbeat is not None:
            self._heartbeat.start()

        self._running = True

        # 启动 flush 线程
        self._flush_thread = threading.Thread(target=self._flush_loop, daemon=True, name="tick-flush")
        self._flush_thread.start()

        # 治本（#ARCH-DATA-TICK-GAP-001 后续，2026-07-31）：
        # tick_subscriber 启动早于 QMT 客户端时，subscribe_quote 静默失败（7-30 0行根因）。
        # 三阶段启动：①等待 QMT 连通性就绪 → ②订阅全市场 → ③等待首个 tick（超时重新订阅）。
        self._start_time = time.time()  # P0-2: 预热计时起点

        # ① 等待 QMT 连通性就绪（最长 120s 轮询重试，治标 7-30 启动顺序问题）
        if not self._wait_for_qmt_ready(timeout=120.0, interval=5.0):
            log.warning("QMT 未就绪，继续尝试订阅（best-effort）")

        # ② 订阅全市场标的
        symbols = self._get_all_symbols()
        self._subscribe_all_symbols(symbols)

        # ③ P0-2: 预热等待首个 tick——超时则重新订阅一次再等待
        # 避免开盘瞬间数据缺口：subscribe_quote 是异步的，订阅完成不代表数据已到达
        self._wait_for_first_tick(symbols, timeout=30.0)

        # P1-3: 启动双源切换器（主源 QMT + 备源 TDX 自动切换）
        if self._backup_provider is not None and self._heartbeat is not None:
            from zephyr.data.redundant_source.backup_tick_poller import (
                BackupTickPoller, QMTSourceAdapter,
            )
            from zephyr.data.redundant_source.source_switcher import SourceSwitcher

            self._backup_poller = BackupTickPoller(
                self._backup_provider,
                symbols,
                self._on_backup_tick,
            )
            self._switcher = SourceSwitcher(
                QMTSourceAdapter(self),
                self._backup_poller,
                self._heartbeat,
            )
            self._switcher.start()
            log.info("P1-3: 双源切换器已启动 (primary=qmt, backup=tdx)")

        log.info("TickSubscriber 启动完成: 订阅 %d 只标的", len(self._subscribed))
        return True

    def stop(self) -> None:
        """停止订阅服务。"""
        self._running = False
        if self._flush_thread:
            self._flush_thread.join(timeout=30)
        # P1-3: 停止双源切换器（含备源轮询线程）
        if self._switcher:
            self._switcher.stop()
        # P2-8: 停止心跳检测
        if self._heartbeat is not None:
            self._heartbeat.stop()
        # WalWriter.stop: flush 残留段 + 停止 drain 线程
        if self._writer:
            self._writer.stop()
        # 取消订阅（unsubscribe_quote 不接受 period 参数，与 subscribe_quote 签名不一致）
        if self._xtdata:
            for symbol in self._subscribed:
                try:
                    self._xtdata.unsubscribe_quote(symbol, callback=self._on_tick)
                except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                    pass
        log.info("TickSubscriber 已停止: stats=%s", self.stats())

    def stats(self) -> dict:
        """获取统计信息（无锁快照）。"""
        qsize = self._tick_queue.qsize()
        _get_metrics_registry().set_gauge("zephyr_tick_queue_size", qsize)
        return {
            "received": self._received,
            "written": self._written,
            "errors": self._errors,
            "queue_size": qsize,
        }

    # ── Stage 4 公共化（2026-07-28）：properties + 公共方法别名 ──
    # 消除 tests/zephyr/data/test_tick_subscriber.py 中 79 处私有成员访问。
    # _make_sub() 改用真实 __init__ 构造（所有参数可选），仅 running 需测试覆写。
    # on_tick / drain_batch / on_backup_tick 为简单别名（测试直接调用，无 patch）。

    @property
    def tick_queue(self) -> queue.Queue:
        """只读：tick_queue（Stage 4 公共化）。"""
        return self._tick_queue

    @tick_queue.setter
    def tick_queue(self, value):
        """写入：tick_queue（Stage 4 公共化）。"""
        self._tick_queue = value

    @property
    def first_tick_received(self) -> threading.Event:
        """只读：first_tick_received（Stage 4 公共化）。"""
        return self._first_tick_received

    @first_tick_received.setter
    def first_tick_received(self, value):
        """写入：first_tick_received（Stage 4 公共化）。"""
        self._first_tick_received = value

    @property
    def writer(self):
        """读写：WalWriter（Stage 4 公共化，测试可注入 mock）。"""
        return self._writer

    @writer.setter
    def writer(self, value) -> None:
        self._writer = value

    @property
    def running(self) -> bool:
        """读写：运行标志（Stage 4 公共化）。"""
        return self._running

    @running.setter
    def running(self, value: bool) -> None:
        self._running = value

    @property
    def received(self) -> int:
        """读写：已接收计数（Stage 4 公共化）。"""
        return self._received

    @received.setter
    def received(self, value: int) -> None:
        self._received = value

    @property
    def written(self) -> int:
        """读写：已写入计数（Stage 4 公共化）。"""
        return self._written

    @written.setter
    def written(self, value: int) -> None:
        self._written = value

    @property
    def errors(self) -> int:
        """读写：错误计数（Stage 4 公共化）。"""
        return self._errors

    @errors.setter
    def errors(self, value: int) -> None:
        self._errors = value

    @property
    def subscribed_symbols(self) -> set[str]:
        """只读：已成功订阅的标的集合（Stage 4 公共化）。

        供盘中编排器在 start() 后获取实际订阅标的，传给 IntradayFactorLoop
        作为 tick 读取范围（编排器拉起因子循环的 symbols 来源）。
        """
        return self._subscribed

    def on_tick(self, datas: dict) -> None:
        """公共 API：tick 回调入口（Stage 4 公共化别名）。"""
        return self._on_tick(datas)

    def drain_batch(self, max_n: int = _DRAIN_BATCH_SIZE, timeout: float = 1.0) -> int:
        """公共 API：批量出队（Stage 4 公共化别名）。"""
        return self._drain_batch(max_n=max_n, timeout=timeout)

    def on_backup_tick(self, symbol: str, tick: dict) -> None:
        """公共 API：备源 tick 回调（Stage 4 公共化别名）。"""
        return self._on_backup_tick(symbol, tick)


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

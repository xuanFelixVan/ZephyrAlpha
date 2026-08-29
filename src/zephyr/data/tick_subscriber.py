# [BLUEPRINT] MOD-L00-001 | docs/03_modules/_domain_data/blueprint.md | §
# [MODULE] zephyr.data.tick_subscriber
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.wal_writer; zephyr.data.provider_base; zephyr.data.table_registry; zephyr.data.calendar; zephyr.shared.observability.metrics; zephyr.shared.observability.metrics_server
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] QMT callback 线程只做 queue.put_nowait（最小开销）; flush 线程批量出队(500条)构造单个 FetchResult 交给 WalWriter; WalWriter 先落盘段文件再异步 drain 到 CH（P0-1 主动WAL）; 无锁计数(CPython GIL 保证 int += 1 统计精度足够); queue.Queue 解耦线程安全; P1-5 metrics 埋点覆盖 received/written/dropped/queue_size; 分阶段延迟度量走 CAND-OBS-001 契约 StageTimer（tick_subscriber_{on_tick,queue_wait,convert,wal_add}_duration_seconds，对齐契约 §3.2 L00 四段）; #ARCH-DATA-017 裁定B/C/E: 业务心跳JSON(tick_subscriber_biz.heartbeat)+tick-biz-watchdog线程盘中无tick周期重订阅+日志落盘RotatingFileHandler(tick_subscriber_run.log)
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

import json
import logging
import os
import queue
import signal as sig_module
import sys
import threading
import time
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Final

from zephyr.data.calendar import MarketCalendar, get_market_calendar
from zephyr.data.table_registry import get_registry
from zephyr.shared.observability.metrics import get_registry as _get_metrics_registry
from zephyr.shared.observability.metrics_server import start_metrics_server

log = logging.getLogger(__name__)

# Phase 5: 表名从 business_data_categories.yaml 真源派生（裁定 #ARCH-CH-024）
_TBL_TICK_DATA = get_registry().table("market_tick")

# tick_data 表15字段（P0-1: 新增 recorded_time）
_TICK_COLUMNS = [
    "trade_date",
    "timestamp",
    "recorded_time",
    "symbol",
    "market_type",
    "price",
    "volume",
    "amount",
    "direction",
    "data_source",
    "bid_price",
    "ask_price",
    "bid_volume",
    "ask_volume",
    "quality_flag",
]

_DATA_SOURCE = "miniqmt"

# P0-2: 批量出队上限（减少 WalWriter.add 调用次数）
_DRAIN_BATCH_SIZE = 500

# 默认 A 股日历（94号 §4.1/#261 注入式改造：统一经 data.calendar 包读取日历约束，
# 缺省保持 A 股现状行为；币侧装配注入 get_market_calendar("crypto") 即可）
_DEFAULT_CALENDAR: Final = get_market_calendar("ashare")

# #ARCH-DATA-017 裁定B/C/E（2026-08-15）：业务心跳/日志落盘路径与看门狗参数
_REPO_ROOT = Path(__file__).resolve().parents[3]  # src/zephyr/data/tick_subscriber.py → 仓根
_BIZ_HEARTBEAT_PATH = _REPO_ROOT / "tmp" / "tick_subscriber_biz.heartbeat"
_RUN_LOG_PATH = _REPO_ROOT / "tmp" / "tick_subscriber_run.log"
# 盘中无 tick 超此秒数触发周期重订阅（裁定E，对齐 deadman/guard 10min 告警的提前自愈窗口）
_BIZ_RESUB_AFTER_S = 300.0
# 业务心跳写出/看门狗循环间隔（对齐 guard 15s 心跳节奏）
_BIZ_WATCHDOG_LOOP_S = 15.0
# #117（2026-08-17 实盘实证）：启动时 QMT 离线致 universe 解析 0 只标的的边缘——
# 看门狗盘中周期性重试 universe 解析+订阅，指数退避 60s 起翻倍、上限 900s
_BIZ_UNIVERSE_RETRY_BASE_S = 60.0
_BIZ_UNIVERSE_RETRY_MAX_S = 900.0


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
        if code.startswith("51"):  # 510xxx-519xxx = SH ETF
            return "etf"
        if code.startswith("50"):  # 501xxx-502xxx = SH LOF
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
        "中性盘",  # direction（QMT tick 不直接提供）
        data_source,  # data_source（P1-3: 支持备源标识）
        bid_price,
        ask_price,
        bid_volume,
        ask_volume,
        1,  # quality_flag
    )


class TickSubscriber:
    """QMT 实时 Tick 订阅器——常驻订阅全市场 tick，写入 ClickHouse。

    线程模型（P0-1 主动 WAL 架构）：
      - QMT callback 线程：_on_tick → queue.put_nowait（最小开销，无锁计数）
      - flush 线程：_drain_batch 批量出队(500条) → WalWriter.add（先落盘段文件）
      - WalWriter drain 线程：段文件 → ch_writer → ClickHouse（异步排空）
      - biz 看门狗线程：业务心跳写出 + 盘中无 tick 周期重订阅（#ARCH-DATA-017 裁定C/E）
    """

    def __init__(
        self,
        symbols: list[str] | None = None,
        batch_rows: int = 3000,
        batch_seconds: float = 5.0,
        heartbeat=None,
        backup_provider=None,
        tick_cache=None,
        calendar: MarketCalendar | None = None,
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
            calendar: 市场日历注入（94号 §4.1/#261，可选）。
                None=ASHareCalendar 默认（零行为变化）；币侧装配传 CryptoCalendar。
        """
        self._symbols = symbols
        self._batch_rows = batch_rows
        self._batch_seconds = batch_seconds
        self._heartbeat = heartbeat  # P2-8: 主源心跳检测集成
        self._backup_provider = backup_provider  # P1-3: TDX 备源
        self._tick_cache = tick_cache  # H1 Redis tick 缓存双写
        self._calendar = calendar or _DEFAULT_CALENDAR  # 市场日历（#261 注入缝）
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
        # CAND-OBS-001: 契约分段计时器（消灭手写 perf_counter 样板）
        # 阶段拆分对齐契约 §3.2 L00 数据接入：on_tick（WS recv）/queue_wait/convert（parse+quality_gate）/wal_add（emit）
        from zephyr.shared.observability.stage_timer import StageTimer
        self._stage_timer = StageTimer(module="tick_subscriber")

        # xtdata 模块（延迟导入）
        self._xtdata = None
        self._subscribed: set[str] = set()

        # #ARCH-DATA-017 裁定C/E：业务心跳与周期重订阅状态
        self._last_tick_ts: float = 0.0  # 最近 tick 接收时刻（time.time()；0=从未收到）
        self._symbols_resolved: list[str] = []  # start() 缓存的全市场标的（看门狗重订阅复用）
        self._biz_thread: threading.Thread | None = None
        self._resub_count = 0  # 业务看门狗周期重订阅次数
        self._hb_day = None  # 心跳日界锚（today_rows 日增量基准）
        self._hb_day_base_written = 0
        self._is_trading_day: bool | None = None  # xtdata 日历判定（None=未刷新）
        self._started_ts: float = 0.0  # subscriber 启动时刻（heartbeat started_ts）
        # #117：0 标的边缘重试状态（指数退避）
        self._universe_retry_count = 0
        self._universe_retry_next_ts = 0.0

    def _on_tick(self, datas: dict) -> None:
        """xtdata 回调入口——把 tick 放入队列（QMT 线程调用）。

        Args:
            datas: {stock_code: tick_data}
                subscribe_quote 回调: tick_data 是 list[dict]（每3秒推送，通常 len=1）
                subscribe_whole_quote 回调: tick_data 是 dict（快照，向后兼容）
        """
        if not self._running:
            return
        # CAND-OBS-001: Stage on_tick（契约 L00 WS recv 段）——回调端到端处理耗时
        self._stage_timer.begin("on_tick")
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
                    self._last_tick_ts = time.time()  # 裁定C：业务心跳最近 tick 时刻
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
        # CAND-OBS-001: Stage on_tick 收尾——observe tick_subscriber_on_tick_duration_seconds
        self._stage_timer.end("on_tick")

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
            self._last_tick_ts = time.time()  # 裁定C：备源 tick 同样视为业务活性
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
        # CAND-OBS-001: Stage queue_wait——queue.get 阻塞等待耗时（含空队 sleep）
        self._stage_timer.begin("queue_wait")
        try:
            symbol, tick = self._tick_queue.get(timeout=timeout)
        except queue.Empty:
            self._stage_timer.end("queue_wait")
            return 0
        self._stage_timer.end("queue_wait")

        rows: list[tuple] = []
        cache_ticks: list[tuple[str, dict]] = []  # H1 Redis tick 缓存双写收集
        # CAND-OBS-001: Stage convert——tick_to_row 批量转换耗时（契约 parse+quality_gate 段）
        self._stage_timer.begin("convert")
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
        self._stage_timer.end("convert")

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
        # CAND-OBS-001: Stage wal_add——WalWriter.add 段落盘耗时（契约 emit 段）
        self._stage_timer.begin("wal_add")
        add_ok = self._writer.add(result)
        self._stage_timer.end("wal_add")

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
                            seen.add(s)
                            symbols.append(s)
                            etf_added += 1
                    elif code.startswith("16") or code.startswith("18"):
                        if s not in seen:
                            seen.add(s)
                            symbols.append(s)
                            lof_added += 1
                log.info("板块 沪深基金: 获取 %d 只，新增 ETF %d / LOF %d", len(fund_list), etf_added, lof_added)
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
                data = self._xtdata.get_market_data_ex([], ["000001.SZ"], period="1m", count=1)
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
                    attempt,
                    interval,
                    remaining,
                )
                time.sleep(interval)
        log.error("QMT 连通性检测超时(%.0fs)，订阅可能失败", timeout)
        return False

    def _subscribe_all_symbols(self, symbols: list[str]) -> int:
        """订阅全市场标的，返回成功订阅数。

        治本（2026-08-03 实地演练发现 28 分钟订阅卡死）：
        原 subscribe_quote 逐只订阅 ~8400 只标的，串行 RTT 累积约 28 分钟
        才完成开盘前订阅，错过开盘数据窗口。
        改用 subscribe_whole_quote 批量订阅——单次 RTT 订阅整批标的，
        callback 接收 {stock_code: tick_data} dict 快照，_on_tick 已兼容该格式
        （见 _on_tick docstring 的 subscribe_whole_quote 回调分支）。

        批量大小 1000：兼顾 xtquant 单次订阅上限与超时风险，整批订阅
        ~8400 只仅需 ~9 次 RTT（vs 原 8400 次）。

        兼容性：若 xtquant 版本无 subscribe_whole_quote（AttributeError），
        自动回退到逐只 subscribe_quote（旧路径，保证不破坏老环境）。
        """
        if not symbols:
            return 0

        whole_quote = getattr(self._xtdata, "subscribe_whole_quote", None)
        if whole_quote is None:
            # 兼容回退：旧版 xtquant 无 subscribe_whole_quote
            log.warning(
                "xtquant 无 subscribe_whole_quote，回退逐只订阅 %d 只（慢路径）",
                len(symbols),
            )
            for symbol in symbols:
                try:
                    self._xtdata.subscribe_quote(symbol, period="tick", callback=self._on_tick)
                    self._subscribed.add(symbol)
                except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                    log.error("订阅失败 %s: %s", symbol, e)
            return len(self._subscribed)

        BATCH_SIZE = 1000
        total = len(symbols)
        for i in range(0, total, BATCH_SIZE):
            batch = symbols[i : i + BATCH_SIZE]
            try:
                # subscribe_whole_quote(code_list, callback=None) → list[成功订阅的 stock_code]
                subscribed_codes = whole_quote(batch, callback=self._on_tick)
                if isinstance(subscribed_codes, list) and subscribed_codes:
                    self._subscribed.update(subscribed_codes)
                else:
                    # 某些版本返回 None/空——best-effort 标记本批全部已订阅
                    self._subscribed.update(batch)
                log.info(
                    "批量订阅 %d-%d/%d 成功（累计 %d）",
                    i + 1,
                    min(i + BATCH_SIZE, total),
                    total,
                    len(self._subscribed),
                )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                log.error("批量订阅失败 %d-%d: %s", i + 1, min(i + BATCH_SIZE, total), e)
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

    # ── #ARCH-DATA-017 裁定C/E：业务心跳 + 盘中周期重订阅（2026-08-15）──

    def _refresh_trading_day_flag(self) -> None:
        """刷新当日是否交易日（xtdata 日历优先，降级走注入的市场日历）。

        心跳 JSON 携带 is_trading_day：监控侧（deadman/guard）不做日历推算——
        业务侧最知道今天该不该有数据，这是"收盘/周末/节假日不误报"的第一性来源。

        降级链（94号 §4.1/#261 注入式改造）：xtdata 历（QMT 在线时主路径）
        → 注入的市场日历（默认 ASHareCalendar 委托 XSHG 真源）；
        日历包内部在 exchange_calendars 不可用时再降级 weekday——与原
        "xtdata 缺失→weekday 近似"的降级终点一致，降级路径语义不变。
        """
        today = datetime.now().date()
        try:
            if self._xtdata is not None:
                dates = self._xtdata.get_trading_dates("SH")
                # get_trading_dates 返回毫秒时间戳列表
                dayset = {datetime.fromtimestamp(int(d) / 1000).date() for d in (dates or [])}
                if dayset:
                    self._is_trading_day = today in dayset
                    return
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            log.warning("交易日历刷新失败（降级市场日历包）: %s", e)
        # 手工 weekday 近似已消除：统一经日历包判定（其内部保留 weekday 降级链）
        self._is_trading_day = self._calendar.is_trading_day(today)

    def _is_market_open_now(self) -> bool:
        """当前是否盘中时段（当日交易时段最外包络内且交易日）。

        时段统一从注入的市场日历读取（94号 §4.1/#261）：取 session_windows
        首段开盘~末段收盘的包络——A股=09:30~15:00，与既有硬编码逐分一致
        （含午休，看门狗语义为"日间监控窗"而非"连续竞价"）。
        """
        now = datetime.now()
        if self._is_trading_day is None:
            self._refresh_trading_day_flag()
        if not self._is_trading_day:
            return False
        windows = self._calendar.session_windows(now.date())
        if not windows:
            return False
        open_t, close_t = windows[0][0], windows[-1][1]
        hm = now.hour * 60 + now.minute
        return (open_t.hour * 60 + open_t.minute) <= hm <= (close_t.hour * 60 + close_t.minute)

    def _write_biz_heartbeat(self) -> None:
        """写业务心跳 JSON（tmp→os.replace 原子写，对齐 guard Write-Heartbeat 防半读）。

        与 tmp/tick_subscriber.heartbeat（guard 代写=进程活性，#ARCH-BOOT-001 锁机制依赖）
        正交分离：本文件承载业务活性（last_tick_ts/today_rows/is_trading_day），
        供 deadman_switch 盘中校验与 guard 盘中过期重启判定——治本放大器1
        "heartbeat 与采集业务存活脱节"（08-12~14 活进程零采集 4 天无告警）。
        """
        today = datetime.now().date()
        if today != self._hb_day:
            self._hb_day = today
            self._hb_day_base_written = self._written
            self._refresh_trading_day_flag()
        now = time.time()
        payload = {
            "ts": datetime.now().isoformat(timespec="seconds"),
            "pid": os.getpid(),
            "started_ts": (
                datetime.fromtimestamp(self._started_ts).isoformat(timespec="seconds") if self._started_ts else None
            ),
            "last_tick_ts": (
                datetime.fromtimestamp(self._last_tick_ts).isoformat(timespec="seconds") if self._last_tick_ts else None
            ),
            "last_tick_age_s": round(now - self._last_tick_ts, 1) if self._last_tick_ts else None,
            "today_rows": self._written - self._hb_day_base_written,
            "received": self._received,
            "written": self._written,
            "errors": self._errors,
            "subscribed": len(self._subscribed),
            "resub_count": self._resub_count,
            "universe_retry_count": self._universe_retry_count,
            "is_trading_day": self._is_trading_day,
        }
        try:
            tmp_path = _BIZ_HEARTBEAT_PATH.with_suffix(".tmp")
            tmp_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            os.replace(tmp_path, _BIZ_HEARTBEAT_PATH)
        except Exception as e:  # noqa: BLE001 — 心跳写出失败不阻断采集主流程
            log.warning("业务心跳写出失败: %s", e)

    def _biz_watchdog_loop(self) -> None:
        """业务看门狗（裁定C/E + #117）：周期写业务心跳 + 盘中异常自愈。

        裁定E 治本"预热后永久静默"：_wait_for_first_tick 失败后不再静默——
        盘中时段 last_tick_ts 超 _BIZ_RESUB_AFTER_S 未更新即重新订阅+重等首 tick。
        非盘中（收盘/周末/节假日）不重订阅：无 tick 推送属正常，重订阅无意义。

        #117 治本"0 标的边缘"（2026-08-17 实盘实证静默 14h+）：启动时 QMT 离线
        致板块获取全失败 → _symbols_resolved 为空 → 旧重订阅条件（含标的非空）
        永不触发。盘中时段标的为 0 时周期性重试 universe 解析+订阅（指数退避），
        解析成功即重置退避并交回既有"无 tick 重订阅"路径。
        """
        while self._running:
            self._write_biz_heartbeat()
            if self._is_market_open_now():
                if not self._symbols_resolved:
                    self._retry_empty_universe()
                else:
                    idle = time.time() - self._last_tick_ts if self._last_tick_ts else float("inf")
                    if idle > _BIZ_RESUB_AFTER_S:
                        self._resub_count += 1
                        log.warning(
                            "业务看门狗: 盘中 %.0fs 无 tick（第 %d 次周期重订阅，%d 只标的）...",
                            idle,
                            self._resub_count,
                            len(self._symbols_resolved),
                        )
                        self._subscribed.clear()
                        self._subscribe_all_symbols(self._symbols_resolved)
                        # 重等首 tick（Event 已 set 时立即返回，以 last_tick_ts 刷新判恢复）
                        self._first_tick_received.wait(timeout=30.0)
                        if self._last_tick_ts and time.time() - self._last_tick_ts < _BIZ_RESUB_AFTER_S:
                            log.info("业务看门狗: 重订阅后 tick 流已恢复")
                        else:
                            log.warning("业务看门狗: 重订阅后 30s 仍无 tick（下轮继续重试）")
            time.sleep(_BIZ_WATCHDOG_LOOP_S)

    def _retry_empty_universe(self) -> None:
        """#117：0 标的边缘自愈——盘中周期性重试 universe 解析+订阅（指数退避+留痕）。

        触发：_symbols_resolved 为空（启动时 QMT 离线致板块获取全失败）且盘中。
        退避：_BIZ_UNIVERSE_RETRY_BASE_S(60s) 起指数翻倍，上限 _BIZ_UNIVERSE_RETRY_MAX_S(900s)；
        退避窗口内直接返回不重复尝试。解析成功（标的非空）即订阅+重等首 tick 判恢复，
        并重置退避计时——后续若仍静默，由既有"无 tick 周期重订阅"路径接管。
        留痕：WARNING/INFO 日志（run log 落盘）+ 心跳 JSON universe_retry_count 字段
        （进程期累计，对齐 resub_count 语义，供 deadman 观察"是否发生过 0 标的重试"）。
        """
        now = time.time()
        if now < self._universe_retry_next_ts:
            return
        self._universe_retry_count += 1
        retry_no = self._universe_retry_count
        log.warning(
            "业务看门狗: 标的列表为空（启动时 universe 解析失败），盘中第 %d 次重试 universe 解析+订阅...",
            retry_no,
        )
        symbols = self._get_all_symbols()
        if not symbols:
            backoff = min(
                _BIZ_UNIVERSE_RETRY_BASE_S * (2 ** min(retry_no - 1, 4)),
                _BIZ_UNIVERSE_RETRY_MAX_S,
            )
            self._universe_retry_next_ts = time.time() + backoff
            log.warning(
                "业务看门狗: universe 重解析仍 0 只（QMT 未恢复？），%.0fs 后第 %d 次重试",
                backoff,
                retry_no + 1,
            )
            return
        self._symbols_resolved = list(symbols)
        self._subscribed.clear()
        n = self._subscribe_all_symbols(self._symbols_resolved)
        log.info(
            "业务看门狗: universe 重解析成功（%d 只），已订阅 %d 只（第 %d 次重试）",
            len(symbols),
            n,
            retry_no,
        )
        # 重等首 tick（Event 已 set 时立即返回，以 last_tick_ts 刷新判恢复）
        self._first_tick_received.wait(timeout=30.0)
        if self._last_tick_ts and time.time() - self._last_tick_ts < _BIZ_RESUB_AFTER_S:
            log.info("业务看门狗: 0 标的恢复后 tick 流已恢复")
        else:
            log.warning("业务看门狗: 订阅成功但 30s 仍无 tick（交回无 tick 重订阅路径观察）")
        # 解析成功即重置退避计时；retry_count 累计不重置（对齐 _resub_count 留痕语义）
        # ——若仍静默，既有 idle>_BIZ_RESUB_AFTER_S 路径接管
        self._universe_retry_next_ts = 0.0

    @staticmethod
    def _classify_qmt_path(path: str) -> str:
        """按路径特征分类 QMT 实例（config/qmt_environments.yaml identification_hints）。

        "模拟" → sim；"证券" 且无 "模拟" → live；否则 unknown。
        "模拟"后缀更具体，优先判定（路径同时含两者时认 sim）。
        """
        if "模拟" in path:
            return "sim"
        if "证券" in path:
            return "live"
        return "unknown"

    def _log_qmt_env(self, env: str, path: str, source: str) -> None:
        """按辨识结果输出审计日志（sim=info / live=error / unknown=warning）。

        不 fail-closed（行情全市场共享、只读订阅，阻断会影响合法数据采集）——
        ERROR 级日志保证实盘连接的审计可见性。
        """
        if env == "sim":
            log.info("QMT 实例辨识[%s]：模拟盘（%s）✓ 符合预期", source, path)
        elif env == "live":
            log.error(
                "⚠ QMT 实例辨识[%s]：实盘（%s）——xtdata 正与真实资金盘终端交换数据！\n"
                "  本项目处于模拟盘阶段，tick_subscriber 应连模拟盘。\n"
                "  风险评估：tick_subscriber 仅订阅只读行情，不调用 xttrader 下单，"
                "无交易风险；但违反 #ARCH-QMT-ENV-DISAMBIG-001 辨识协议。\n"
                "  修复：关闭实盘 QMT 终端，或先启动模拟盘终端使其占据 xtdata 服务端口。",
                source,
                path,
            )
        else:
            log.warning("QMT 实例辨识[%s]：未知实例（%s）", source, path)

    def _identify_qmt_peer_via_tcp(self) -> str | None:
        """TCP 主路径：通过已建立的本地连接对端进程辨识 xtdata 实际连接的 QMT 实例。

        治本（2026-08-03，避免靠 get_data_dir 字符串匹配误报）：
        实测两个 QMT 终端的 miniquote.exe 都 LISTEN 0.0.0.0:58610（Windows
        SO_REUSEADDR 允许重复绑定），靠"谁监听 58610"无法区分。但 OS 只把新连接
        路由给其中一个进程——靠"已建立连接配对"能唯一锁定真正服务的数据进程：
          本进程侧: ESTABLISHED laddr=(127.0.0.1, my_eph) raddr=(127.0.0.1, 58610)
          对端进程侧: ESTABLISHED laddr=(127.0.0.1, 58610) raddr=(127.0.0.1, my_eph)
        对端进程的 exe_path 含"模拟"→sim / "证券"→live。

        不硬编码端口：对端端口从本进程已建立连接动态发现（兼容非 58610 场景）。

        Returns:
            "sim"/"live" 辨识成功；None 表示无 TCP 对端（调用方走兜底）。
        """
        try:
            import os

            import psutil
        except ImportError:
            log.debug("psutil 不可用，跳过 TCP 实例辨识")
            return None

        localhost = {"127.0.0.1", "::1"}

        def _scan_peer_exe() -> str | None:
            """返回首个匹配的 QMT 对端进程 exe_path，无则 None。"""
            try:
                conns = psutil.net_connections(kind="inet")
            except (psutil.AccessDenied, psutil.NoSuchProcess) as e:
                log.debug("net_connections 不可用: %s", e)
                return None
            my_pid = os.getpid()
            # 1. 本进程到 localhost 的已建立连接：收集 (本端ephemeral, 对端port)
            my_pairs: list[tuple[int, int]] = []
            for c in conns:
                if (
                    c.status == "ESTABLISHED"
                    and c.pid == my_pid
                    and c.laddr
                    and c.laddr.ip in localhost
                    and c.raddr
                    and c.raddr.ip in localhost
                ):
                    my_pairs.append((c.laddr.port, c.raddr.port))
            if not my_pairs:
                return None
            # 2. 按 (my_eph, peer_port) 配对定位对端进程 pid——唯一锁定服务进程
            #    （即使两个进程都 LISTEN 同一端口，只有真正接收连接的那个有此 ESTABLISHED）
            peer_pids: set[int] = set()
            for my_eph, peer_port in my_pairs:
                for c in conns:
                    if (
                        c.status == "ESTABLISHED"
                        and c.pid
                        and c.pid != my_pid
                        and c.laddr
                        and c.laddr.ip in localhost
                        and c.laddr.port == peer_port
                        and c.raddr
                        and c.raddr.ip in localhost
                        and c.raddr.port == my_eph
                    ):
                        peer_pids.add(c.pid)
            # 3. 按对端进程 exe_path 分类（取首个命中 sim/live 的）
            for pid in peer_pids:
                try:
                    exe = psutil.Process(pid).exe()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
                if exe and self._classify_qmt_path(exe) in ("sim", "live"):
                    return exe
            return None

        exe = _scan_peer_exe()
        if exe is None:
            # 连接可能尚未建立——触发轻量探活强制 xtdata 建连，再扫一次
            # （正常启动流中 _wait_for_qmt_ready 已建连，此处为直接调用守卫兜底）
            try:
                self._xtdata.get_market_data_ex([], ["000001.SZ"], period="1m", count=1)
            except Exception:  # noqa: BLE001 — 探活副作用即可，返回值忽略
                pass
            exe = _scan_peer_exe()
        if exe is None:
            log.debug("TCP 辨识：未发现 xtdata 到 localhost 的 QMT 对端连接")
            return None
        env = self._classify_qmt_path(exe)
        self._log_qmt_env(env, exe, source="TCP")
        return env

    def _identify_qmt_via_datadir(self) -> str:
        """兜底辨识：读 xtdata.get_data_dir() 路径分类。

        兼容 TCP 辨识无果的场景（psutil 不可用 / xtdata 连接尚未建立 / 非 TCP 模式）。
        """
        try:
            datadir = self._xtdata.get_data_dir()
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            log.warning("TCP 辨识无果且 get_data_dir 失败: %s", e)
            return "unknown"
        env = self._classify_qmt_path(datadir)
        self._log_qmt_env(env, datadir, source="datadir 兜底")
        return env

    def _verify_qmt_instance(self) -> str:
        """启动守卫：辨识 xtdata 实际连接的 QMT 实例（治本 #ARCH-QMT-ENV-DISAMBIG-001）。

        两个 QMT 终端（sim/live）都在线时，xtdata 默认连哪个由 xtquant 决定，
        可能连到实盘实例。本方法优先通过 TCP 连接对端进程辨识（ground truth——
        xtdata 真正交换数据的 OS 进程），失败则回退 get_data_dir() 字符串匹配，
        避免 datadir 字符串匹配在两终端并存时的误报。

        辨识优先级：
          1. [主] TCP 对端进程 exe_path（按已建立连接配对锁定，两终端都 LISTEN
             58610 也能区分真正服务的数据进程）
          2. [兜底] get_data_dir() 路径（psutil 不可用 / TCP 未建立时）

        风险评估：tick_subscriber 仅订阅只读行情，不调用 xttrader 下单，无交易风险；
        不 fail-closed（行情全市场共享），ERROR 级日志保证审计可见性。

        Returns:
            "sim" / "live" / "unknown"
        """
        tcp = self._identify_qmt_peer_via_tcp()
        if tcp is not None:
            return tcp
        return self._identify_qmt_via_datadir()

    def start(self) -> bool:
        """启动订阅服务。"""
        try:
            from xtquant import xtdata
        except ImportError:
            log.error("无法导入 xtquant，请确保 miniQMT 已安装且 xtquant 可用")
            return False
        self._xtdata = xtdata

        # #ARCH-DATA-017 裁定C：启动即写首帧业务心跳（消除启动窗口期 deadman MISSING 误报），
        # 后续由 tick-biz-watchdog 线程每 15s 续写
        self._started_ts = time.time()
        self._refresh_trading_day_flag()
        self._write_biz_heartbeat()
        # 启动守卫延后到 _wait_for_qmt_ready 之后：此时 xtdata TCP 连接已建立，
        # TCP 对端进程辨识才能拿到 ground truth（见 _verify_qmt_instance）

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

        # 启动守卫：辨识 xtdata 实际连接的 QMT 实例（治本 #ARCH-QMT-ENV-DISAMBIG-001）
        # 此时 xtdata TCP 连接已建立——通过"已建立连接配对"锁定真正服务的数据进程，
        # 两终端都 LISTEN 58610 也能区分（避免靠 get_data_dir 字符串匹配误报）
        self._verify_qmt_instance()

        # ② 订阅全市场标的
        symbols = self._get_all_symbols()
        self._subscribe_all_symbols(symbols)

        # ③ P0-2: 预热等待首个 tick——超时则重新订阅一次再等待
        # 避免开盘瞬间数据缺口：subscribe_quote 是异步的，订阅完成不代表数据已到达
        self._wait_for_first_tick(symbols, timeout=30.0)

        # #ARCH-DATA-017 裁定C/E：缓存标的 + 启动业务看门狗线程
        # （业务心跳写出 + 盘中无 tick 周期重订阅——治本"预热后永久静默"放大器3）
        self._symbols_resolved = list(symbols)
        self._biz_thread = threading.Thread(
            target=self._biz_watchdog_loop,
            daemon=True,
            name="tick-biz-watchdog",
        )
        self._biz_thread.start()

        # P1-3: 启动双源切换器（主源 QMT + 备源 TDX 自动切换）
        if self._backup_provider is not None and self._heartbeat is not None:
            from zephyr.data.redundant_source.backup_tick_poller import (
                BackupTickPoller,
                QMTSourceAdapter,
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
        if self._biz_thread:
            self._biz_thread.join(timeout=5)
        # P1-3: 停止双源切换器（含备源轮询线程）
        if self._switcher:
            self._switcher.stop()
        # P2-8: 停止心跳检测
        if self._heartbeat is not None:
            self._heartbeat.stop()
        # WalWriter.stop: flush 残留段 + 停止 drain 线程
        if self._writer:
            self._writer.stop()
        # 取消订阅（治本 2026-08-03 实盘验证发现并修正）：
        # 实测本 xtquant 版本：unsubscribe_quote 签名为 (int seq)，需 subscribe_quote
        # 返回的序列号；subscribe_whole_quote 返回成功码 1（非 seq）。原代码
        # unsubscribe_quote(symbol, callback=...) 签名错误，被 try/except 吞掉从未真正退订。
        # 治本策略：
        #   1. 若 xtquant 版本提供 unsubscribe_whole_quote → 批量退订（future-proof）
        #   2. 否则 → 订阅随进程退出由 xtquant 自动释放（daemon 生命周期保证：
        #      tick_subscriber 是常驻进程，stop() 后进程退出即释放全部订阅，无累积泄漏）
        # 不再调用签名错误的 unsubscribe_quote(symbol, callback=...)（消除假退订）
        if self._xtdata and self._subscribed:
            unsub_whole = getattr(self._xtdata, "unsubscribe_whole_quote", None)
            subscribed_list = list(self._subscribed)
            if unsub_whole is not None:
                BATCH_SIZE = 1000
                for i in range(0, len(subscribed_list), BATCH_SIZE):
                    batch = subscribed_list[i : i + BATCH_SIZE]
                    try:
                        unsub_whole(batch)
                    except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                        log.warning(
                            "unsubscribe_whole_quote 批次失败 %d-%d（best-effort，进程退出兜底释放）",
                            i + 1,
                            min(i + BATCH_SIZE, len(subscribed_list)),
                        )
            else:
                # 本版本无批量退订 API：daemon stop 后进程退出由 xtquant 释放订阅。
                # 不调签名错误的 unsubscribe_quote(symbol, callback=...)（治本：消除假退订）。
                log.info(
                    "本 xtquant 版本无 unsubscribe_whole_quote；%d 只订阅将随进程退出"
                    "由 xtquant 自动释放（daemon 生命周期保证，无累积泄漏）",
                    len(subscribed_list),
                )
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
    # 日志落盘（#ARCH-DATA-017 裁定B，对标 scheduler.main 模式）：
    # 治本"日志吞没"放大器——guard Start-Process 未重定向 stdout/stderr，
    # 订阅失败/预热超时证据全部丢弃（08-12~14 零采集无法回溯取证）；
    # 进程内落盘不依赖 guard 配置。RotatingFileHandler 轮转防无限增长。
    from logging.handlers import RotatingFileHandler

    _RUN_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    _fh = RotatingFileHandler(
        _RUN_LOG_PATH,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    _fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"))
    logging.getLogger().addHandler(_fh)
    log.info("日志落盘: %s", _RUN_LOG_PATH)
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

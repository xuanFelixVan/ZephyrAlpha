# QMT 实时 Tick 订阅服务 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 创建独立常驻服务，通过 `xtdata.subscribe_quote(period="tick")` 实时订阅全市场 tick，写入 ClickHouse `c1_market.tick_data` 表（3秒粒度）。

**Architecture:** 不走 scheduler cron（分钟级），而是独立进程。QMT callback 线程把 tick dict 放入线程安全 `queue.Queue`（最小开销），后台 flush 线程从队列取数据，转换为14字段 tuple，通过 BufferedWriter 攒批写入 ClickHouse。不复用 governance MiniQmtProvider（它返回 DataFrame 24字段，同步回调开销大）。

**Tech Stack:** xtquant/xtdata API, queue.Queue, BufferedWriter, ClickHouse MergeTree, signal

---

## 关键设计

### 字段映射（xtdata tick dict → tick_data 表14字段）

| xtdata 原始字段 | tick_data 表字段 | 转换逻辑 |
|----------------|-----------------|----------|
| `time` (ms) | `timestamp` | `datetime.fromtimestamp(time/1000)` → 格式化 `YYYY-MM-DD HH:MM:SS` |
| `time` (ms) | `trade_date` | 从 timestamp 提取 `date()` |
| stock_code | `symbol` | `_stock_to_symbol()` 转换（如 `000001.SZ` → `000001`） |
| (推导) | `market_type` | 从 symbol 推导：`SH→stock, SZ→stock, BJ→stock_bj, .SH index→index` 等 |
| `lastPrice` | `price` | `Decimal(str(lastPrice))` |
| `volume` | `volume` | `int(volume)` |
| `amount` | `amount` | `Decimal(str(amount))` |
| (推导) | `direction` | 默认 `'中性盘'`（QMT tick 不直接提供 direction） |
| (常量) | `data_source` | `'miniqmt'` |
| `bidPrice[0]` | `bid_price` | `Decimal(str(askPrice[0]))` or `None` |
| `askPrice[0]` | `ask_price` | 同上 |
| `bidVol[0]` | `bid_volume` | `int(bidVol[0])` or `None` |
| `askVol[0]` | `ask_volume` | `int(askVol[0])` or `None` |
| (常量) | `quality_flag` | `1` |

### 线程安全方案

- **QMT callback 线程**：只做 `queue.put((symbol, tick_dict))`，不做任何 I/O 或转换
- **后台 flush 线程**：`queue.get()` → 字段转换 → `BufferedWriter.add(FetchResult)` → 攒批写入
- BufferedWriter 在 flush 线程单线程使用，无需加锁

### BufferedWriter 参数调整

实时场景需要更快 flush，降低阈值：
- `max_rows=5000`（默认50000太高，实时场景5秒可能就够）
- `max_seconds=10`（默认30秒太慢，10秒 flush 一次保证数据新鲜度）

### market_type 推导逻辑

```python
def _infer_market_type(stock_code: str) -> str:
    if stock_code.endswith(".SH"):
        code = stock_code[:-3]
        if code.startswith("688"): return "stock"  # 科创板
        if code.startswith("000") or code.startswith("880"): return "index"  # 指数
        return "stock"
    if stock_code.endswith(".SZ"):
        code = stock_code[:-3]
        if code.startswith("399"): return "index"
        if code.startswith("159"): return "etf"
        if code.startswith("12"): return "cb"  # 可转债
        return "stock"
    if stock_code.endswith(".BJ"): return "stock_bj"
    return "stock"
```

---

## File Structure

- Create: `src/zephyr/data/tick_subscriber.py` — Tick 订阅服务主体
- Create: `tests/zephyr/data/test_tick_subscriber.py` — 单元测试

---

### Task 1: 字段映射器

**Files:**
- Create: `src/zephyr/data/tick_subscriber.py`
- Test: `tests/zephyr/data/test_tick_subscriber.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/zephyr/data/test_tick_subscriber.py
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

from datetime import datetime
from decimal import Decimal
from zephyr.data.tick_subscriber import tick_to_row, infer_market_type


class TestTickToRow:
    def test_basic_tick_conversion(self):
        """正常 tick dict 转换为14字段 tuple"""
        tick = {
            "time": 1720838403000,  # 2024-07-13 10:00:03 CST (ms)
            "lastPrice": 10.5,
            "volume": 1000,
            "amount": 10500.0,
            "bidPrice": [10.49, 10.48, 10.47, 10.46, 10.45],
            "askPrice": [10.5, 10.51, 10.52, 10.53, 10.54],
            "bidVol": [500, 200, 100, 50, 50],
            "askVol": [300, 400, 100, 50, 50],
        }
        stock_code = "000001.SZ"
        row = tick_to_row(stock_code, tick)
        assert row is not None
        assert len(row) == 14
        # trade_date
        assert row[0] is not None
        # symbol
        assert row[2] == "000001"
        # market_type
        assert row[3] == "stock"
        # price
        assert row[4] == Decimal("10.5")
        # volume
        assert row[5] == 1000
        # direction
        assert row[7] == "中性盘"
        # data_source
        assert row[8] == "miniqmt"
        # bid_price (1档)
        assert row[9] == Decimal("10.49")
        # ask_price (1档)
        assert row[10] == Decimal("10.5")
        # quality_flag
        assert row[13] == 1

    def test_empty_tick_returns_none(self):
        """空 tick 返回 None"""
        assert tick_to_row("000001.SZ", {}) is None

    def test_missing_bid_ask(self):
        """缺少 bid/ask 时对应字段为 None"""
        tick = {
            "time": 1720838403000,
            "lastPrice": 10.5,
            "volume": 1000,
            "amount": 10500.0,
        }
        row = tick_to_row("600000.SH", tick)
        assert row is not None
        assert row[9] is None   # bid_price
        assert row[10] is None  # ask_price
        assert row[11] is None  # bid_volume
        assert row[12] is None  # ask_volume

    def test_etf_market_type(self):
        tick = {"time": 1720838403000, "lastPrice": 3.5, "volume": 100, "amount": 350}
        row = tick_to_row("159915.SZ", tick)
        assert row[3] == "etf"

    def test_index_market_type(self):
        tick = {"time": 1720838403000, "lastPrice": 3000, "volume": 0, "amount": 0}
        row = tick_to_row("000300.SH", tick)
        assert row[3] == "index"


class TestInferMarketType:
    def test_sh_stock(self):
        assert infer_market_type("600000.SH") == "stock"

    def test_sz_stock(self):
        assert infer_market_type("000001.SZ") == "stock"

    def test_star(self):
        assert infer_market_type("688001.SH") == "stock"

    def test_etf(self):
        assert infer_market_type("159915.SZ") == "etf"

    def test_index_sh(self):
        assert infer_market_type("000300.SH") == "index"

    def test_index_sz(self):
        assert infer_market_type("399001.SZ") == "index"

    def test_bj(self):
        assert infer_market_type("430047.BJ") == "stock_bj"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `set PYTHONPATH=src && python -m pytest tests/zephyr/data/test_tick_subscriber.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'zephyr.data.tick_subscriber'`

- [ ] **Step 3: Write minimal implementation**

```python
# src/zephyr/data/tick_subscriber.py
# [BLUEPRINT] MOD-L00-004
# [MODULE] zephyr.data.tick_subscriber
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.buffered_writer; zephyr.data.ch_writer
# [STARTUP] standalone
# [MATURITY] prototype
# [TTL] permanent
"""QMT 实时 Tick 订阅服务——subscribe_quote 实时推送，写入 ClickHouse tick_data。

独立常驻进程，不走 scheduler cron。QMT callback 线程把 tick dict 放入
queue.Queue，后台 flush 线程从队列取数据转14字段 tuple，BufferedWriter 攒批写入。

启动: python -m zephyr.data.tick_subscriber
"""
from __future__ import annotations

import logging
from datetime import datetime
from decimal import Decimal
from typing import Any

log = logging.getLogger(__name__)

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
        market_type 字符串（stock/stock_bj/index/etf/cb）
    """
    if stock_code.endswith(".SH"):
        code = stock_code[:-3]
        if code.startswith("000") or code.startswith("880"):
            return "index"
        return "stock"
    if stock_code.endswith(".SZ"):
        code = stock_code[:-3]
        if code.startswith("399"):
            return "index"
        if code.startswith("159"):
            return "etf"
        if code.startswith("12"):
            return "cb"
        return "stock"
    if stock_code.endswith(".BJ"):
        return "stock_bj"
    return "stock"


def _stock_to_symbol(stock_code: str) -> str:
    """QMT stock_code → 纯代码（去后缀）。

    "000001.SZ" → "000001"
    """
    return stock_code.split(".")[0]


def _safe_decimal(val: Any) -> Decimal | None:
    """安全转换为 Decimal，失败/0 返回 None。"""
    if val is None:
        return None
    try:
        d = Decimal(str(val))
        return d if d != 0 else None
    except Exception:
        return None


def _safe_int(val: Any) -> int | None:
    """安全转换为 int，失败返回 None。"""
    if val is None:
        return None
    try:
        return int(val)
    except Exception:
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `set PYTHONPATH=src && python -m pytest tests/zephyr/data/test_tick_subscriber.py -v`
Expected: PASS (7 tests)

- [ ] **Step 5: Commit**

```bash
git add src/zephyr/data/tick_subscriber.py tests/zephyr/data/test_tick_subscriber.py
git commit -m "feat(data): tick_subscriber 字段映射器——xtdata tick dict 转 tick_data 14字段 tuple"
```

---

### Task 2: TickSubscriber 主体（队列 + flush 线程 + QMT 订阅）

**Files:**
- Modify: `src/zephyr/data/tick_subscriber.py` (追加 TickSubscriber 类)
- Modify: `tests/zephyr/data/test_tick_subscriber.py` (追加测试)

- [ ] **Step 1: Write the failing test**

```python
# 追加到 tests/zephyr/data/test_tick_subscriber.py

import queue
import threading
import time
from unittest.mock import MagicMock, patch
from zephyr.data.tick_subscriber import TickSubscriber


class TestTickSubscriber:
    def test_callback_puts_to_queue(self):
        """QMT callback 把 tick 放入队列"""
        sub = TickSubscriber.__new__(TickSubscriber)
        sub._tick_queue = queue.Queue()
        sub._running = True
        sub._stats = {"received": 0, "written": 0, "errors": 0}
        sub._lock = threading.Lock()

        datas = {"000001.SZ": {"time": 1720838403000, "lastPrice": 10.5, "volume": 100, "amount": 1050}}
        TickSubscriber._on_tick(sub, datas)

        assert not sub._tick_queue.empty()
        symbol, tick = sub._tick_queue.get_nowait()
        assert symbol == "000001.SZ"
        assert tick["lastPrice"] == 10.5
        assert sub._stats["received"] == 1

    def test_flush_thread_processes_queue(self):
        """flush 线程从队列取数据，调用 BufferedWriter"""
        sub = TickSubscriber.__new__(TickSubscriber)
        sub._tick_queue = queue.Queue()
        sub._running = True
        sub._stats = {"received": 0, "written": 0, "errors": 0}
        sub._lock = threading.Lock()
        sub._writer = MagicMock()
        sub._writer.add.return_value = True

        # 放入一条 tick
        sub._tick_queue.put(("000001.SZ", {"time": 1720838403000, "lastPrice": 10.5, "volume": 100, "amount": 1050}))

        # 运行一次 flush 循环（timeout=0.1 取不到就退出）
        sub._flush_once(timeout=0.1)

        # 验证 BufferedWriter.add 被调用
        assert sub._writer.add.called
        assert sub._stats["written"] == 1

    def test_stop_sets_running_false(self):
        """stop() 设置 _running=False"""
        sub = TickSubscriber.__new__(TickSubscriber)
        sub._running = True
        sub._tick_queue = queue.Queue()
        TickSubscriber.stop(sub)
        assert sub._running is False
```

- [ ] **Step 2: Run test to verify it fails**

Run: `set PYTHONPATH=src && python -m pytest tests/zephyr/data/test_tick_subscriber.py::TestTickSubscriber -v`
Expected: FAIL with `AttributeError: type object 'TickSubscriber' has no attribute '_on_tick'`

- [ ] **Step 3: Write minimal implementation**

```python
# 追加到 src/zephyr/data/tick_subscriber.py

import signal
import sys
import threading


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
            datas: {stock_code: tick_dict}
        """
        if not self._running:
            return
        for symbol, tick in datas.items():
            try:
                if tick:
                    self._tick_queue.put_nowait((symbol, tick))
                    with self._lock:
                        self._stats["received"] += 1
            except queue.Full:
                log.warning("tick 队列已满，丢弃 tick symbol=%s", symbol)
            except Exception as e:
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

        # 构造 FetchResult-like 对象给 BufferedWriter
        from zephyr.data.provider_base import FetchResult
        result = FetchResult(
            table="c1_market.tick_data",
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
            except Exception:
                break
        if self._writer:
            self._writer.flush()
            log.info("flush 线程退出，最终 flush %d 行", self._writer.total_flushed)
        log.info("flush 线程结束")

    def _get_all_symbols(self) -> list[str]:
        """获取全市场沪深A股标的列表。"""
        symbols = self._symbols
        if not symbols:
            symbols = self._xtdata.get_stock_list_in_sector("沪深A股")
            log.info("获取全市场标的: %d 只", len(symbols))
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
            "c1_market.tick_data",
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
            except Exception as e:
                log.error("订阅失败 %s: %s", symbol, e)

        log.info("TickSubscriber 启动完成: 订阅 %d 只标的", len(self._subscribed))
        return True

    def stop(self) -> None:
        """停止订阅服务。"""
        self._running = False
        if self._flush_thread:
            self._flush_thread.join(timeout=30)
        # 取消订阅
        if self._xtdata:
            for symbol in self._subscribed:
                try:
                    self._xtdata.unsubscribe_quote(symbol, period="tick", callback=self._on_tick)
                except Exception:
                    pass
        log.info("TickSubscriber 已停止: stats=%s", self._stats)

    def stats(self) -> dict:
        """获取统计信息。"""
        with self._lock:
            return dict(self._stats)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `set PYTHONPATH=src && python -m pytest tests/zephyr/data/test_tick_subscriber.py -v`
Expected: PASS (10 tests)

- [ ] **Step 5: Commit**

```bash
git add src/zephyr/data/tick_subscriber.py tests/zephyr/data/test_tick_subscriber.py
git commit -m "feat(data): TickSubscriber 主体——队列+flush线程+QMT subscribe_quote 订阅"
```

---

### Task 3: 常驻进程入口（`__main__` + signal 优雅退出）

**Files:**
- Modify: `src/zephyr/data/tick_subscriber.py` (追加 main 函数)
- Modify: `tests/zephyr/data/test_tick_subscriber.py` (追加 main 测试)

- [ ] **Step 1: Write the failing test**

```python
# 追加到 tests/zephyr/data/test_tick_subscriber.py

import os
from zephyr.data.tick_subscriber import main


class TestMain:
    def test_main_returns_zero_on_keyboard_interrupt(self, monkeypatch):
        """main() 捕获 KeyboardInterrupt 返回 0"""
        sub_instance = MagicMock()
        sub_instance.start.return_value = True
        sub_instance.stats.return_value = {"received": 0, "written": 0, "errors": 0}

        def fake_sleep(*args):
            raise KeyboardInterrupt()

        monkeypatch.setattr("time.sleep", fake_sleep)
        monkeypatch.setattr("zephyr.data.tick_subscriber.TickSubscriber", lambda *a, **kw: sub_instance)

        exit_code = main()
        assert exit_code == 0
        sub_instance.stop.assert_called_once()

    def test_main_returns_one_on_start_failure(self, monkeypatch):
        """start() 失败返回 1"""
        sub_instance = MagicMock()
        sub_instance.start.return_value = False

        monkeypatch.setattr("zephyr.data.tick_subscriber.TickSubscriber", lambda *a, **kw: sub_instance)

        exit_code = main()
        assert exit_code == 1
```

- [ ] **Step 2: Run test to verify it fails**

Run: `set PYTHONPATH=src && python -m pytest tests/zephyr/data/test_tick_subscriber.py::TestMain -v`
Expected: FAIL with `ImportError: cannot import name 'main'`

- [ ] **Step 3: Write minimal implementation**

```python
# 追加到 src/zephyr/data/tick_subscriber.py

import time


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
    import signal as sig_module
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
```

- [ ] **Step 4: Run test to verify it passes**

Run: `set PYTHONPATH=src && python -m pytest tests/zephyr/data/test_tick_subscriber.py -v`
Expected: PASS (12 tests)

- [ ] **Step 5: Commit**

```bash
git add src/zephyr/data/tick_subscriber.py tests/zephyr/data/test_tick_subscriber.py
git commit -m "feat(data): tick_subscriber main 入口——signal 优雅退出+统计日志"
```

---

### Task 4: 集成验证（手动）

**Files:**
- No new files

- [ ] **Step 1: 确认 QMT + ClickHouse 在运行**

Run:
```powershell
tasklist /FI "IMAGENAME eq XtMiniQmt*" /FO CSV
wsl -d Ubuntu -- clickhouse-client -q "SELECT 1"
```
Expected: XtMiniQmt.exe 运行中，ClickHouse 返回 1

- [ ] **Step 2: 启动 tick_subscriber（后台）**

Run:
```powershell
$env:PYTHONPATH="src"
Start-Process -FilePath "python" -ArgumentList "-m","zephyr.data.tick_subscriber" `
    -RedirectStandardOutput "logs\tick_subscriber.out.log" `
    -RedirectStandardError "logs\tick_subscriber.err.log" `
    -NoNewWindow -PassThru -WorkingDirectory "d:\ZephyrAlpha"
```
Expected: 进程启动，日志显示"订阅 N 只标的"

- [ ] **Step 3: 等待 30 秒后验证数据写入**

Run:
```powershell
Start-Sleep 30
wsl -d Ubuntu -- clickhouse-client -q "SELECT count(), min(timestamp), max(timestamp) FROM c1_market.tick_data WHERE trade_date=today() AND data_source='miniqmt'"
```
Expected: count > 0，timestamp 在当前时间附近

- [ ] **Step 4: 验证统计日志**

Run:
```powershell
Get-Content "logs\tick_subscriber.out.log" | Select-String "统计"
```
Expected: received > 0, written > 0

- [ ] **Step 5: Commit final**

```bash
git add -A
git commit -m "feat(data): tick_subscriber 集成验证通过——实时 tick 写入 ClickHouse"
```

---

## Self-Review

**1. Spec coverage:**
- subscribe 订阅模式 ✓ (Task 2: `subscribe_quote`)
- 3秒 tick 实时同步 ✓ (Task 2: callback → queue → flush)
- 写入 ClickHouse tick_data 表 ✓ (Task 1-2: 14字段映射 + BufferedWriter)
- 常驻进程 ✓ (Task 3: `__main__` + signal)
- 线程安全 ✓ (Task 2: queue.Queue + 后台 flush 线程)

**2. Placeholder scan:** 无 TBD/TODO，所有代码完整。

**3. Type consistency:**
- `tick_to_row(stock_code, tick) -> tuple | None` ✓
- `TickSubscriber.__init__(symbols, batch_rows, batch_seconds)` ✓
- `_on_tick(datas: dict)` ✓
- `_flush_once(timeout: float)` ✓
- `main() -> int` ✓

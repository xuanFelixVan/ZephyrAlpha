---
ttl: task_bound
---

# P0+P1 详细设计：数据可靠性 + 可观测性改造

> **文档定位**：设计讨论文档（docs/_working/），审批后正式化为蓝图 + depgraph 设计态登记
> **设计依据**：BalletHip 小红书技术分享 + ZephyrAlpha 6 个核心源文件真实架构
> **日期**：2026-07-22
> **关联模块**：MOD-L00-001 (tick_subscriber) / MOD-L00-004 (data_source_integrator) / MOD-INF-016 (metrics)

---

## 一、设计总览

### 1.1 现状基线（已验证的真实架构）

ZephyrAlpha 数据层比预期成熟，已具备以下能力：

| 能力 | 实现位置 | 现状 |
|------|----------|------|
| 有界队列 | [tick_subscriber.py:191](file:///d:/ZephyrAlpha/src/zephyr/data/tick_subscriber.py#L191) | `maxsize=100000`，Full 时丢弃+log |
| 热路径压缩 | [tick_subscriber.py:202-230](file:///d:/ZephyrAlpha/src/zephyr/data/tick_subscriber.py#L202-L230) | callback 只做 `put_nowait`，flush 线程负责转换+写入 |
| 二级传输降级 | [ch_writer.py](file:///d:/ZephyrAlpha/src/zephyr/data/ch_writer.py) | TCP(9000) → HTTP(8123) → 本地落盘 |
| 本地兜底 | [local_replay.py](file:///d:/ZephyrAlpha/src/zephyr/data/local_replay.py) | **被动**——CH 不可达才落盘，scheduler 每 30 分钟回灌 |
| 攒批写入 | [buffered_writer.py:54-55](file:///d:/ZephyrAlpha/src/zephyr/data/buffered_writer.py#L54-L55) | 50000 行 / 30 秒触发 flush |
| 幂等性 | [ch_writer.py](file:///d:/ZephyrAlpha/src/zephyr/data/ch_writer.py) | `is_replacing_engine()` → ReplacingMergeTree 直接 INSERT / MergeTree 先 DELETE |
| 连接冷却自愈 | [ch_writer.py](file:///d:/ZephyrAlpha/src/zephyr/data/ch_writer.py) | TCP/HTTP 各 15 秒冷却 |
| Metrics 基础设施 | [metrics.py](file:///d:/ZephyrAlpha/src/zephyr/shared/observability/metrics.py) | Counter/Gauge/Histogram + `prometheus_text()`，但**无 /metrics 端点**，**未接入数据层** |

### 1.2 目标架构（借鉴博主 + 适配 A 股场景）

博主 BalletHip 的架构是 polymarket 高频（每秒万级 tick），ZephyrAlpha 是 A 股实时（约 5000 标的 × 每 3 秒推送 ≈ 每秒 1700 tick）。**不能照搬，需适配**：

| 博主技术 | 博主场景 | ZephyrAlpha 适配 | 优先级 |
|----------|----------|------------------|--------|
| 双层 WAL (RocksDB) | 万级 TPS，后端 WAL 防丢 | 单层主动 WAL（本地文件），复用 local_replay 机制 | **P0** |
| Collector + IPC 解耦 | 多进程采集 | tick_subscriber 已有 callback→queue→flush 解耦，升级为 WAL 写入器 | **P0** |
| 5 秒时间桶 + 3000 行分块 | 控制 CH merge 压力 | tick 路径从 5000行/10秒 → 5秒/3000行 | **P0** |
| 有界队列 | 防 OOM | tick 队列已有界，需确认全链路 + 背压策略 | **P0** |
| Prometheus + Grafana | 系统级监控 | metrics.py 已有 Registry，加 /metrics 端点 + 接入数据层 | **P1** |
| CH 表引擎选型 | MergeTree/ReplacingMergeTree | 确认建表 DDL + 引擎配置 | **P1** |
| 故障恢复 | WAL 容量管理 + 积压指标 | 已有冷却自愈，补 WAL 水位 + 积压暴露 | **P1** |
| 主备线路热切换 | Caddy + Cloudflare Tunnel | A 股数据源是本地 QMT API，无网络线路概念 → 重新诠释 | **P2** |
| Proto 编码 | IPC 序列化 | TSV 已够用，Proto 仅 WAL 段格式备选 | **P2** |
| 双数据源 Grafana | Prometheus + CH | Grafana 接 Prometheus(实时) + CH(历史) | **P2** |

### 1.3 核心洞察

**最关键的差异**：博主的 WAL 是"主动"的（数据**先写 WAL 再排空到 CH**），ZephyrAlpha 的 local_replay 是"被动"的（CH 不可达才落盘）。

这意味着：当前 CH 短暂抖动（如 merge 阻塞 5 秒）时，数据会**在 BufferedWriter 内存缓冲区积压**而非落盘。如果进程此时崩溃，积压数据**全部丢失**。

改造核心 = 将 local_replay 从"被动兜底"升级为"主动 WAL"——数据先落本地 WAL 段文件，再异步排空到 CH。

---

## 二、P0 详细设计（数据可靠性 — 致命级）

### P0-1：主动 WAL 架构

#### 现状分析

当前数据流（tick 路径）：
```
QMT callback → _tick_queue(100000) → flush线程 → BufferedWriter(内存5000行/10秒) → ch_writer → CH
                                                                    ↓ 失败时
                                                              local_replay.save_fallback（被动）
```

**致命缺陷**：BufferedWriter 的 5000 行在内存中，CH 抖动期间积压，进程崩溃 = 数据丢失。

#### 目标架构

```
QMT callback → _tick_queue(100000) → flush线程 → WalWriter（先落本地段文件）
                                                        ↓ 异步 drain
                                                   ch_writer → CH
                                                        ↓ drain 失败
                                                   段文件保留，下次重试
```

#### 设计：WalWriter（新建模块）

**文件**：`src/zephyr/data/wal_writer.py`

**核心思路**：复用 local_replay 的文件格式和 manifest 机制，但从"被动调用"改为"主动写入"。

```python
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.wal_writer
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.local_replay; zephyr.data.ch_writer
# [CONSUMERS] zephyr.data.tick_subscriber
# [INVARIANTS] 数据先写WAL段文件再排空CH; 段文件原子写入; drain成功后标记committed; WAL总容量有上限
# [SAFETY] M
# [TTL] permanent

class WalWriter:
    """主动 WAL 写入器——数据先落本地段文件，再异步排空到 ClickHouse。

    与 BufferedWriter 的区别：
    - BufferedWriter：数据在内存，CH 抖动时积压，崩溃=丢失
    - WalWriter：数据先落盘，CH 抖动时段文件保留，崩溃=可恢复

    与 local_replay 的关系：
    - local_replay.save_fallback：被动调用（CH 失败才落盘）
    - WalWriter：主动调用（每次 flush 都先落盘）
    - local_replay.replay_batch：复用为 WalWriter 的 drain 机制
    """

    def __init__(
        self,
        table: str,
        segment_max_rows: int = 3000,       # P0-3: 单段最大行数
        segment_max_seconds: float = 5.0,    # P0-3: 单段最大时间（秒）
        wal_dir_max_bytes: int = 2 * 1024**3,  # WAL 总容量上限 2GB
    ):
        self._table = table
        self._segment_max_rows = segment_max_rows
        self._segment_max_seconds = segment_max_seconds
        self._wal_dir_max_bytes = wal_dir_max_bytes

        self._current_segment: list[tuple] = []   # 当前段缓冲（内存）
        self._segment_start_ts: float | None = None
        self._cols_clause: str | None = None
        self._keep_indices: list[int] | None = None

        # drain 线程
        self._drain_thread: threading.Thread | None = None
        self._running = False

    def add(self, result: "FetchResult") -> bool:
        """添加数据到当前段。达阈值时触发段落盘。"""
        # ... 列初始化逻辑同 BufferedWriter ...
        self._current_segment.extend(filtered_rows)
        if len(self._current_segment) >= self._segment_max_rows or \
           (time.time() - self._segment_start_ts) >= self._segment_max_seconds:
            return self._flush_segment()
        return True

    def _flush_segment(self) -> bool:
        """将当前段落盘为 WAL 段文件（复用 local_replay.save_fallback）。"""
        tsv_bytes = self._rows_to_tsv(self._current_segment)
        # 关键：主动落盘，不等待 CH 失败
        ok = local_replay.save_fallback(self._table, self._cols_clause, tsv_bytes)
        if ok:
            self._current_segment.clear()
            self._segment_start_ts = None
            # 触发异步 drain（非阻塞）
            self._notify_drain()
        return ok

    def _drain_loop(self) -> None:
        """drain 线程：持续将 WAL 段文件排空到 CH。"""
        while self._running:
            try:
                result = local_replay.replay_batch(max_files=50)
                if result["remaining"] == 0:
                    time.sleep(2.0)  # 无积压，等待
                else:
                    time.sleep(0.5)  # 有积压，快速重试
            except Exception as e:
                log.error("WAL drain 异常: %s", e)
                time.sleep(5.0)

    def flush(self) -> bool:
        """强制落盘当前段 + 触发 drain。"""
        if self._current_segment:
            self._flush_segment()
        return local_replay.replay_batch(max_files=100)["failed"] == 0
```

#### 关键设计决策

1. **复用 local_replay 的文件格式**：`data/local_fallback/<table>/<timestamp>_<uid>.tsv` + `_manifest.jsonl`，零格式迁移成本
2. **复用 local_replay.replay_batch 作为 drain**：已有按 table 分组回灌 + manifest 去重逻辑，不重写
3. **WAL 容量上限**：`wal_dir_max_bytes=2GB`，超过时 oldest 段文件被强制 drain（阻塞）或告警丢弃（P0-4 背压策略）
4. **drain 线程常驻**：替代 scheduler 的 30 分钟 tick，改为 2 秒轮询（无积压时）或 0.5 秒快速重试（有积压时）

#### 与现有代码的集成

- **tick_subscriber.py**：`start()` 中 `BufferedWriter` → `WalWriter`，`batch_rows=5000` → `segment_max_rows=3000`，`batch_seconds=10.0` → `segment_max_seconds=5.0`
- **buffered_writer.py**：**保留不动**——批量下载任务（kline_daily 等）仍用 BufferedWriter（非实时路径，内存积压可接受）
- **local_replay.py**：**保留不动**——save_fallback/replay_batch 逻辑完全复用，WAL 段文件格式与兜底文件格式一致

---

### P0-2：Collector 采集汇聚器 + 热路径解耦

#### 现状分析

tick_subscriber 已有良好的热路径解耦：
```python
# tick_subscriber.py:202-230 — _on_tick（QMT callback 线程）
def _on_tick(self, datas: dict) -> None:
    for symbol, tick_data in datas.items():
        # ... tick_data 标准化 ...
        self._tick_queue.put_nowait((symbol, tick))  # 最小开销
```

```python
# tick_subscriber.py:234-261 — _flush_once（flush 线程）
def _flush_once(self, timeout: float = 1.0) -> None:
    symbol, tick = self._tick_queue.get(timeout=timeout)
    row = tick_to_row(symbol, tick)
    result = FetchResult(table=_TBL_TICK_DATA, columns=_TICK_COLUMNS, rows=[row], ...)
    self._writer.add(result)  # 当前是 BufferedWriter，P0-1 后是 WalWriter
```

**结论**：热路径解耦已到位（callback→queue→flush 三段式），P0-2 的改造量很小。

#### 目标改进

1. **热路径进一步压缩**：`_on_tick` 中 `with self._lock: self._stats["received"] += 1` 是锁竞争点。改为无锁原子计数（`itertools.count` 或 `threading.local` 汇总）
2. **批量出队**：`_flush_once` 每次只取 1 条。改为 `drain_batch(max_n=500)` 批量出队，减少 queue.get 开销
3. **Collector 命名统一**：tick_subscriber 既是订阅器也是采集器，P0-2 阶段将其定位明确为"Tick Collector"

#### 设计：批量出队 + 无锁计数

```python
# tick_subscriber.py 改进（增量改造，不新建模块）

import itertools

class TickSubscriber:
    def __init__(self, ...):
        # ...
        self._received_counter = itertools.count()  # 无锁计数
        self._written_counter = itertools.count()
        self._error_counter = itertools.count()

    def _on_tick(self, datas: dict) -> None:
        if not self._running:
            return
        for symbol, tick_data in datas.items():
            # ... tick_data 标准化 ...
            try:
                self._tick_queue.put_nowait((symbol, tick))
                next(self._received_counter)  # 无锁，无竞争
            except queue.Full:
                log.warning("tick 队列已满，丢弃 tick symbol=%s", symbol)
                next(self._error_counter)

    def _drain_batch(self, max_n: int = 500) -> int:
        """批量出队，构造单个 FetchResult（多行），减少 add 调用次数。"""
        rows = []
        for _ in range(max_n):
            try:
                symbol, tick = self._tick_queue.get_nowait()
            except queue.Empty:
                break
            row = tick_to_row(symbol, tick)
            if row:
                rows.append(row)
        if not rows:
            return 0
        result = FetchResult(table=_TBL_TICK_DATA, columns=_TICK_COLUMNS, rows=rows, ...)
        if self._writer.add(result):
            for _ in rows:
                next(self._written_counter)
            return len(rows)
        return 0

    @property
    def stats(self) -> dict[str, int]:
        """读取统计（无锁快照）。"""
        return {
            "received": next(self._received_counter) - 1,  # 近似值
            "written": next(self._written_counter) - 1,
            "errors": next(self._error_counter) - 1,
            "queue_size": self._tick_queue.qsize(),
        }
```

#### 关键设计决策

1. **`itertools.count` 无锁计数**：callback 线程不获取锁，消除热路径锁竞争。代价：`stats` 属性是近似值（可接受，监控不需要精确）
2. **批量出队 500 条**：`_drain_batch` 替代 `_flush_once`，一次构造多行 FetchResult，减少 `writer.add` 调用次数 500 倍
3. **stats 暴露 queue_size**：P1-5 监控需要队列水位指标

---

### P0-3：5 秒时间桶 + 3000 行分块

#### 现状分析

| 参数 | 当前值 | 位置 | 问题 |
|------|--------|------|------|
| tick 路径 batch_rows | 5000 | tick_subscriber.py:177 `__init__` | 单批太大，CH merge 慢 |
| tick 路径 batch_seconds | 10.0 | tick_subscriber.py:178 | 10 秒延迟太高 |
| 下载路径 max_rows | 50000 | buffered_writer.py:54 | 合理（非实时路径） |
| 下载路径 max_seconds | 30 | buffered_writer.py:55 | 合理 |

#### 目标参数

| 路径 | 行数阈值 | 时间阈值 | 理由 |
|------|----------|----------|------|
| tick 路径（WalWriter） | 3000 | 5.0 秒 | 博主踩坑经验：3000 行/INSERT 平衡 merge 压力与延迟 |
| 下载路径（BufferedWriter） | 50000 | 30 秒 | 不变（非实时，积压可接受） |

#### 设计：WalWriter 的段落盘策略

已在 P0-1 的 `WalWriter.__init__` 中定义：
```python
segment_max_rows: int = 3000       # 单段最大行数
segment_max_seconds: float = 5.0    # 单段最大时间（秒）
```

段落盘触发逻辑（P0-1 `_flush_segment`）：
```python
if len(self._current_segment) >= 3000 or \
   (time.time() - self._segment_start_ts) >= 5.0:
    self._flush_segment()  # 落盘为 WAL 段文件
```

#### 容量估算

A 股实时 tick：~5000 标的 × 每 3 秒推送 ≈ 1700 tick/秒

- 5 秒时间桶 ≈ 8500 tick/段
- 3000 行阈值会先触发 → 每 1.8 秒落盘一个段文件
- 每个 INSERT 约 3000 行 → CH data part 约 3000 行 → merge 压力可控
- 交易时段 4 小时 ≈ 14400 秒 ≈ 8000 个段文件 ≈ 8000 个 INSERT

**结论**：3000 行/段是合理的，每秒约 2 个 INSERT，CH merge 完全跟得上。

---

### P0-4：全链路有界队列 + 背压策略

#### 现状分析

| 队列/缓冲 | 容量 | 位置 | 有界? |
|-----------|------|------|-------|
| _tick_queue | 100000 | tick_subscriber.py:191 | ✅ 有界 |
| BufferedWriter._buffer | 50000 | buffered_writer.py:81 | ✅ 有界（行数） |
| WalWriter._current_segment | 3000 | wal_writer.py（新建） | ✅ 有界（行数） |
| local_replay WAL 目录 | **无上限** | local_replay.py:51 | ❌ **无界** |

**致命缺陷**：local_replay 的 WAL 目录（`data/local_fallback/`）没有容量上限。如果 CH 长时间不可达（如 VM 宕机），WAL 段文件无限增长，最终磁盘满。

#### 设计：WAL 容量管理 + 背压策略

```python
# wal_writer.py 新增方法

class WalWriter:
    def _check_wal_capacity(self) -> str:
        """检查 WAL 目录容量，返回 'ok' / 'warning' / 'critical'。

        水位线：
        - < 70% (1.4GB): ok
        - 70%-90% (1.4-1.8GB): warning（日志告警 + metrics 暴露）
        - > 90% (1.8GB): critical（触发背压：暂停接收 + 强制 drain）
        """
        wal_size = self._get_wal_dir_size()
        ratio = wal_size / self._wal_dir_max_bytes
        if ratio < 0.7:
            return "ok"
        elif ratio < 0.9:
            log.warning("WAL 容量告警: %.1fGB / %.1fGB (%.0f%%)",
                        wal_size / 1024**3, self._wal_dir_max_bytes / 1024**3, ratio * 100)
            return "warning"
        else:
            log.error("WAL 容量危急: %.1fGB / %.1fGB (%.0f%%) — 触发背压",
                      wal_size / 1024**3, self._wal_dir_max_bytes / 1024**3, ratio * 100)
            return "critical"

    def _apply_backpressure(self, level: str) -> bool:
        """背压策略。

        critical 时：
        1. 暂停 _on_tick 接收（设置 _backpressure=True）
        2. 阻塞 drain 直到 WAL 降到 warning 水位以下
        3. 降级后恢复接收

        Returns: True=可继续接收, False=背压中（应丢弃或等待）
        """
        if level == "critical":
            self._backpressure = True
            # 阻塞 drain
            while self._get_wal_dir_size() / self._wal_dir_max_bytes > 0.7:
                local_replay.replay_batch(max_files=100)
                time.sleep(1.0)
            self._backpressure = False
            return True
        return True
```

#### 全链路有界清单（改造后）

```
QMT callback → _tick_queue(100000, 有界)
                   ↓ Full 时丢弃+log+metrics
              WalWriter._current_segment(3000, 有界)
                   ↓ 达阈值段落盘
              WAL 目录(2GB, 有界)
                   ↓ 70% warning / 90% critical 背压
              drain_thread → ch_writer → CH
```

**每个环节都有界**，最坏情况：WAL 满 → 背压 → 暂停接收 → QMT callback 丢弃 tick → log + metrics 告警。**不会 OOM，不会磁盘满**。

---

## 三、P1 详细设计（可观测性 + 运维）

### P1-5：Prometheus + Grafana 系统级监控

#### 现状分析

[metrics.py](file:///d:/ZephyrAlpha/src/zephyr/shared/observability/metrics.py) 已有完整的 MetricsRegistry：
- Counter / Gauge / Histogram 三分类 ✅
- `prometheus_text()` Prometheus 兼容文本输出 ✅
- 线程安全（Lock）✅
- `measure()` 计时上下文 ✅
- EventBus 事件订阅 ✅

**缺失**：
1. ❌ 没有 `/metrics` HTTP 端点
2. ❌ tick_subscriber 未接入 metrics（只有 log）
3. ❌ ch_writer 未接入 metrics（只有 log）
4. ❌ WalWriter 未接入 metrics（P0-1 新建时同步接入）

#### 设计：/metrics HTTP 端点

**文件**：`src/zephyr/shared/observability/metrics_server.py`（新建）

```python
# [BLUEPRINT] MOD-INF-016 | docs/03_modules/_cross_layer/shared_core/blueprint.md
# [MODULE] zephyr.shared.observability.metrics_server
# [DOMAIN] D_SHARED
# [DEPENDENCIES] zephyr.shared.observability.metrics; http.server(标准库)
# [CONSUMERS] zephyr.data.tick_subscriber
# [INVARIANTS] /metrics端点输出Prometheus文本; 端口默认9925; 独立daemon线程; 不阻塞主流程
# [SAFETY] L
# [TTL] permanent

from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

from zephyr.shared.observability.metrics import get_registry

_METRICS_PORT = 9925


class _MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path == "/metrics":
            text = get_registry().prometheus_text()
            body = text.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/health":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"ok")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, *args) -> None:
        pass  # 静默访问日志


def start_metrics_server(port: int = _METRICS_PORT) -> HTTPServer:
    """启动 /metrics HTTP 服务（daemon 线程）。"""
    server = HTTPServer(("0.0.0.0", port), _MetricsHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True, name="metrics-server")
    thread.start()
    return server
```

#### 设计：数据层指标埋点清单

| 指标名 | 类型 | 标签 | 采集点 | 含义 |
|--------|------|------|--------|------|
| `zephyr_tick_received_total` | Counter | - | tick_subscriber._on_tick | 接收 tick 总数 |
| `zephyr_tick_written_total` | Counter | - | WalWriter.add 成功 | 写入 WAL tick 总数 |
| `zephyr_tick_dropped_total` | Counter | reason=queue_full/backpressure | _on_tick Full/背压 | 丢弃 tick 总数 |
| `zephyr_tick_queue_size` | Gauge | - | _tick_queue.qsize() | 队列当前水位 |
| `zephyr_wal_segments_total` | Counter | - | WalWriter._flush_segment | WAL 段文件总数 |
| `zephyr_wal_dir_bytes` | Gauge | - | WalWriter._get_wal_dir_size | WAL 目录当前大小 |
| `zephyr_wal_backlog_files` | Gauge | - | local_replay manifest 条目数 | 待 drain 文件数 |
| `zephyr_ch_write_total` | Counter | outcome=committed/local/not_durable | ch_writer.write_tsv_outcome | CH 写入总数 |
| `zephyr_ch_write_latency_seconds` | Histogram | - | ch_writer.write_tsv measure | CH 写入延迟分布 |
| `zephyr_ch_cooldown_active` | Gauge | channel=tcp/http | ch_writer 冷却状态 | 冷却中=1 |
| `zephyr_drain_replayed_total` | Counter | - | local_replay.replay_batch | drain 成功总数 |
| `zephyr_drain_failed_total` | Counter | - | local_replay.replay_batch | drain 失败总数 |

#### 接入方案

```python
# tick_subscriber.py — start() 中启动 metrics server
def start(self) -> bool:
    # ... 现有逻辑 ...
    from zephyr.shared.observability.metrics_server import start_metrics_server
    from zephyr.shared.observability.metrics import get_registry
    self._metrics_server = start_metrics_server(port=9925)
    self._registry = get_registry()
    # ... 订阅逻辑 ...

# _on_tick 中记录
def _on_tick(self, datas: dict) -> None:
    # ... put_nowait ...
    self._registry.inc("zephyr_tick_received_total")
    # ... Full 时 ...
    self._registry.inc("zephyr_tick_dropped_total", {"reason": "queue_full"})

# _drain_batch 后更新 gauge
def _drain_batch(self, max_n: int = 500) -> int:
    # ... ...
    self._registry.set_gauge("zephyr_tick_queue_size", self._tick_queue.qsize())
    self._registry.inc("zephyr_tick_written_total", n)
```

#### Grafana Dashboard 规划

- **Dashboard 1: 数据采集健康**
  - tick 接收/写入/丢弃速率（Counter rate）
  - 队列水位（Gauge）
  - WAL 段文件数 + 目录大小（Gauge）
- **Dashboard 2: ClickHouse 写入健康**
  - 写入成功率（Counter rate by outcome）
  - 写入延迟 p50/p99（Histogram）
  - 冷却状态（Gauge）
- **Dashboard 3: Drain 健康**
  - drain 成功/失败速率
  - 积压文件数（Gauge）
  - WAL 容量水位（Gauge，70%/90% 告警线）

---

### P1-6：ClickHouse 表引擎选型

#### 现状分析

[ch_writer.py](file:///d:/ZephyrAlpha/src/zephyr/data/ch_writer.py) 已有 `is_replacing_engine(table)` 判断逻辑：
- ReplacingMergeTree → 直接 INSERT（CH 后台去重）
- MergeTree → 先 DELETE 再 INSERT（防重复）

**但建表 DDL 的引擎配置需要确认**——如果建表时没有用 ReplacingMergeTree，每次写入都会先 DELETE，性能差。

#### 设计：引擎选型矩阵

| 表 | 引擎 | 排序键 | 去重键 | 理由 |
|----|------|--------|--------|------|
| `c1_market.tick_data` | ReplacingMergeTree | (symbol, timestamp) | symbol+timestamp | tick 天然唯一（同标的同时刻只有一条） |
| `c1_market.kline_daily` | ReplacingMergeTree | (symbol, trade_date) | symbol+trade_date | 日线按交易日去重 |
| `c1_market.kline_minute` | ReplacingMergeTree | (symbol, timestamp) | symbol+timestamp | 分钟线按时间戳去重 |
| `c1_market.sector_snapshot` | MergeTree | (sector_code, timestamp) | - | 板块快照允许重复（取最新） |
| `c3_fundamental.*` | ReplacingMergeTree | 按业务键 | 按业务键 | 基本面数据按报告期去重 |

#### DDL 规范

```sql
-- tick_data 建表 DDL（ReplacingMergeTree）
CREATE TABLE IF NOT EXISTS c1_market.tick_data (
    trade_date   Date,
    timestamp    DateTime64(3),
    symbol       String,
    market_type  LowCardinality(String),
    price        Decimal(12,4),
    volume       UInt64,
    amount       Decimal(18,4),
    direction    LowCardinality(String),
    data_source  LowCardinality(String),
    bid_price    Decimal(12,4),
    ask_price    Decimal(12,4),
    bid_volume   UInt64,
    ask_volume   UInt64,
    quality_flag LowCardinality(String)
) ENGINE = ReplacingMergeTree(timestamp)
PARTITION BY toYYYYMM(trade_date)
ORDER BY (symbol, timestamp)
SETTINGS index_granularity = 8192;
```

#### 验证步骤

1. 查询现有表的引擎：`SELECT name, engine FROM system.tables WHERE database = 'c1_market'`
2. 非ReplacingMergeTree的表 → 评估是否需要 `ALTER TABLE ... MODIFY SETTING`（CH 不支持直接改引擎，需建新表+迁移）
3. 确认 `is_replacing_engine()` 逻辑与实际引擎一致

---

### P1-7：故障恢复策略

#### 现状分析

已有恢复机制：
- TCP/HTTP 各 15 秒冷却（[ch_writer.py](file:///d:/ZephyrAlpha/src/zephyr/data/ch_writer.py)）
- scheduler 启动时 + 每 30 分钟 replay_batch（[local_replay.py](file:///d:/ZephyrAlpha/src/zephyr/data/local_replay.py)）
- 二级降级链 TCP → HTTP → 本地落盘

**缺失**：
1. ❌ WAL 容量水位监控（P0-4 已设计）
2. ❌ 积压指标暴露（P1-5 已设计）
3. ❌ 恢复优先级策略
4. ❌ drain 失败的指数退避

#### 设计：恢复优先级 + 指数退避

```python
# wal_writer.py — drain_loop 增强

class WalWriter:
    def _drain_loop(self) -> None:
        """drain 线程：指数退避 + 恢复优先级。"""
        backoff = 2.0  # 初始退避
        max_backoff = 60.0  # 最大退避
        consecutive_failures = 0

        while self._running:
            try:
                # 1. 容量检查
                level = self._check_wal_capacity()
                if level == "critical":
                    self._apply_backpressure(level)

                # 2. drain
                result = local_replay.replay_batch(max_files=50)

                if result["remaining"] == 0:
                    # 无积压，重置退避
                    backoff = 2.0
                    consecutive_failures = 0
                    time.sleep(2.0)
                elif result["failed"] == 0:
                    # 有积压但全部成功，快速继续
                    backoff = 0.5
                    consecutive_failures = 0
                    time.sleep(backoff)
                else:
                    # 有失败，指数退避
                    consecutive_failures += 1
                    backoff = min(backoff * 2, max_backoff)
                    log.warning("WAL drain 失败 %d 次，退避 %.1f 秒",
                                consecutive_failures, backoff)
                    time.sleep(backoff)

            except Exception as e:
                log.error("WAL drain 异常: %s", e)
                time.sleep(5.0)
```

#### 恢复优先级

```
CH 恢复后的恢复顺序：
1. 先 drain 最旧的 WAL 段文件（按 manifest ts 排序）—— 防止数据时效性丢失
2. 每次 drain 50 个文件（控制 CH 写入压力，避免恢复洪峰）
3. drain 成功 → 文件删除 + manifest 移除
4. drain 失败 → 指数退避（2s→4s→8s→...→60s 封顶）
5. WAL 降到 ok 水位 → 恢复正常接收节奏
```

#### 指标暴露

| 指标 | 含义 | 告警阈值 |
|------|------|----------|
| `zephyr_wal_backlog_files` | 待 drain 文件数 | > 100 → Warning |
| `zephyr_wal_dir_bytes` | WAL 目录大小 | > 1.4GB → Warning, > 1.8GB → Critical |
| `zephyr_drain_failed_total` | drain 失败总数 | rate > 0 持续 5 分钟 → Warning |
| `zephyr_ch_cooldown_active` | 冷却状态 | = 1 持续 5 分钟 → Warning |

---

## 四、P2 登记方案（两个都写）

### 4.1 确认结论：两个都写

用户的判断完全正确——**depgraph 设计态节点 + 蓝图文档，两个都写**。理由：

1. **depgraph 设计态节点**：L1 依赖关系先行铁律要求"施工前 MUST 登记依赖关系到 depgraph 设计态"。P2 虽然暂不施工，但登记为 `status=planned` 后，拓扑验证能发现 P2 与 P0/P1 的潜在依赖冲突
2. **蓝图文档**：depgraph 是架构数据真源（节点/边），蓝图是设计契约（接口/不变量/验收标准）。两者互补，不冗余
3. **项目既有模式**：现有所有模块（如 MOD-L00-001~004）都是"depgraph 节点 + 蓝图文档"双写

### 4.2 P2 清单与重新诠释

P2 三项技术需要根据 A 股场景重新诠释（不能照搬 polymarket 高频场景）：

| P2 项 | 博主原意 | A 股适配诠释 | 模块 ID（建议） |
|-------|----------|-------------|-----------------|
| P2-8 主备线路热切换 | Caddy + Cloudflare Tunnel 网络冗余 | **数据源冗余**：主 QMT + 备 [通达信本地/其他]；CH 冗余：主 VM + 备本地 SQLite 降级 | MOD-L00-005 |
| P2-9 Proto 编码 | IPC 序列化（Collector→Writer） | **WAL 段格式**：当前 TSV → 可选 Protobuf（更紧凑、schema 演进友好） | MOD-L00-006 |
| P2-10 双数据源 Grafana | Prometheus + CH | **Grafana 双数据源**：Prometheus(实时 metrics) + ClickHouse(历史行情/回测) | MOD-INF-044 |

### 4.3 depgraph 设计态登记清单

#### 4.3.1 新增设计态节点

```bash
# P2-8: 数据源冗余与热切换
python scripts/governance/apply_depgraph.py \
  --add-design-node "src/zephyr/data/redundant_source/" MOD-L00-005 D_DATA planned \
  --granularity directory

# P2-9: WAL 段 Protobuf 编码
python scripts/governance/apply_depgraph.py \
  --add-design-node "src/zephyr/data/wal_codec/" MOD-L00-006 D_DATA planned \
  --granularity directory

# P2-10: Grafana 双数据源仪表盘（原 MOD-INF-036 被 model_capability_exam 占用，改用 044）
python scripts/governance/apply_depgraph.py \
  --add-design-node "src/zephyr/shared/observability/dashboard/" MOD-INF-044 D_SHARED planned \
  --granularity directory
```

> **注意**：执行前须 `git commit` 备份（铁律 trae_054 STEP0）。`--add-design-node` 参数格式为 `PATH BLUEPRINT_ID DOMAIN_ID [BUILD_STATUS]`，BUILD_STATUS 默认 planned。

#### 4.3.2 新增设计态边（依赖关系）

```bash
# P2-8 依赖数据源集成层
python scripts/governance/apply_depgraph.py \
  --add-design-edge MOD-L00-005 MOD-L00-004

# P2-9 依赖 WAL 写入器（P0-1 新建）
python scripts/governance/apply_depgraph.py \
  --add-design-edge MOD-L00-006 MOD-L00-004

# P2-10 依赖 metrics 基础设施 + CH
python scripts/governance/apply_depgraph.py \
  --add-design-edge MOD-INF-036 MOD-INF-016
```

#### 4.3.3 施工时状态转换

P2 正式施工时，通过以下命令将节点从 planned → production：

```bash
# 施工开始
python scripts/governance/apply_depgraph.py --transition-build-status MOD-L00-005 prototype
# 施工完成验证通过
python scripts/governance/apply_depgraph.py --transition-build-status MOD-L00-005 production
python scripts/governance/apply_depgraph.py --transition-design-maturity MOD-L00-005 production
```

### 4.4 蓝图文档清单

| 蓝图路径 | 模块 ID | 内容要点 |
|----------|---------|----------|
| `docs/03_modules/_domain_data/redundant_source_blueprint.md` | MOD-L00-005 | 主备数据源切换策略、CH 降级到本地 SQLite、心跳检测、切换触发条件 |
| `docs/03_modules/_domain_data/wal_codec_blueprint.md` | MOD-L00-006 | Protobuf schema 定义、TSV↔Proto 转换、向后兼容、性能基准 |
| `docs/03_modules/_cross_layer/shared_core/dashboard_blueprint.md` | MOD-INF-036 | Grafana 数据源配置、Dashboard JSON 模板、告警规则 |

**蓝图模板**（P2 占位，施工时细化）：

```markdown
# [BLUEPRINT] MOD-L00-005 | 数据源冗余与热切换

## 状态
- build_status: planned（depgraph 设计态已登记）
- design_maturity: design
- 预计施工: P0+P1 完成后评估

## 动机
A 股数据源（QMT/miniQMT）是单点。QMT 客户端崩溃 = 数据中断。
借鉴 BalletHip 主备线路热切换思想，适配为"主备数据源热切换"。

## 设计要点（占位，施工时细化）
- 主数据源: miniQMT subscribe_quote（当前 tick_subscriber）
- 备数据源: 通达信本地接口 / 其他券商 API
- 心跳检测: 每 N 秒检测主源 tick 推送是否中断
- 切换策略: 主源中断 > M 秒 → 自动切换备源
- CH 冗余: 主 VM 不可达 > T 秒 → 降级写本地 SQLite（P0 WAL 已保证不丢）

## 依赖
- depends_on: MOD-L00-004 (data_source_integrator)
- P0-1 WalWriter 提供数据不丢保证
```

---

## 五、改造路径（增量步骤）

### Phase 顺序与依赖

```
Phase A: P0-1 WalWriter (新建模块)
  ↓
Phase B: P0-3 时间桶参数 (WalWriter 内置 5秒/3000行)
  ↓
Phase C: P0-2 tick_subscriber 改造 (BufferedWriter→WalWriter + 批量出队 + 无锁计数)
  ↓
Phase D: P0-4 背压策略 (WalWriter 容量管理)
  ↓
Phase E: P1-5 metrics_server + 数据层埋点
  ↓
Phase F: P1-6 CH 表引擎确认
  ↓
Phase G: P1-7 故障恢复增强 (drain 指数退避)
  ↓
P2 登记: depgraph 设计态 + 蓝图占位
```

### 每个 Phase 的交付物

| Phase | 改动文件 | 新建文件 | 测试 | 验收标准 |
|-------|----------|----------|------|----------|
| A | - | `wal_writer.py` | `test_wal_writer.py` | 段文件落盘 + drain 回灌 + 崩溃恢复 |
| B | `wal_writer.py` | - | 同上 | 5 秒/3000 行段落盘验证 |
| C | `tick_subscriber.py` | - | `test_tick_subscriber.py` 增强 | WalWriter 集成 + 批量出队 + 无锁计数 |
| D | `wal_writer.py` | - | 背压测试 | WAL 2GB 上限 + 90% 背压触发 |
| E | `tick_subscriber.py`, `ch_writer.py` | `metrics_server.py` | `/metrics` 端点测试 | `curl localhost:9925/metrics` 返回指标 |
| F | DDL 脚本 | - | 引擎查询验证 | tick_data 等表使用 ReplacingMergeTree |
| G | `wal_writer.py` | - | 指数退避测试 | drain 失败→退避→恢复 |

### 风险与回滚

| 风险 | 影响 | 缓解 |
|------|------|------|
| WalWriter 落盘性能瓶颈 | tick 延迟增大 | 基准测试：3000 行 TSV 序列化 + 文件写入 < 50ms |
| drain 线程与 QMT callback 竞争 | 数据错乱 | drain 只读 WAL 文件，不碰内存缓冲，无竞争 |
| metrics_server 端口冲突 | 监控不可用 | 端口可配置，默认 9925 |
| P0-1 改造期间数据丢失 | tick 中断 | 灰度切换：先并行运行 BufferedWriter + WalWriter，验证后切换 |

---

## 六、总结

### 设计核心

**一句话**：将 local_replay 从"被动兜底"升级为"主动 WAL"，数据先落盘再排空，进程崩溃也不丢数据。

### 改造量评估

| 类别 | 新建文件 | 改造文件 | 估算工作量 |
|------|----------|----------|------------|
| P0 | `wal_writer.py` | `tick_subscriber.py` | 中（1 个新模块 + 1 个改造） |
| P1 | `metrics_server.py` | `tick_subscriber.py`, `ch_writer.py` | 中（1 个新模块 + 2 个改造） |
| P2 | 3 个蓝图占位 | depgraph 3 节点 + 3 边 | 小（仅登记，不施工） |

### 与博主架构的差异化决策

| 博主做法 | ZephyrAlpha 决策 | 理由 |
|----------|------------------|------|
| RocksDB 后端 WAL | 本地 TSV 文件 | A 股 TPS 低（1700/s vs 万级），TSV 够用，零依赖 |
| Collector 独立进程 + IPC | tick_subscriber 单进程多线程 | QMT callback 是进程内调用，无需跨进程 IPC |
| Proto 编码 | TSV（P2 备选 Proto） | TSV 与 CH INSERT 原生兼容，省去编解码 |
| Caddy + Cloudflare Tunnel | 数据源冗余（P2） | A 股数据源是本地 API，无网络线路概念 |
| 双数据源 Grafana | 采纳（P2） | Prometheus 实时 + CH 历史，完全适用 |

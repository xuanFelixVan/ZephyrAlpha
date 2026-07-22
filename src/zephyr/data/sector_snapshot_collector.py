# -*- coding: utf-8 -*-
# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §sector_snapshot
# [MODULE] zephyr.data.sector_snapshot_collector
# [DOMAIN] D_DATA
# [DEPENDENCIES] clickhouse_driver; tqcenter (external E:\tdx\PYPlugins\user); zephyr.data.ch_config; zephyr.data.sector_ranking_engine
# [CONSUMERS] zephyr.data.sector_ranking_engine (reads sector_snapshot table)
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 混合模式采集880xxx板块实时快照（99只推送+全量轮询30秒）写入sector_snapshot表；推送池由sector_ranking_engine.get_push_pool()动态选取；轮询池从sector_constituent表动态获取（实测2026-07-22: 582只=454个880xxx+128个881xxx，非设计时估算的584）；tqcenter SDK需E:\tdx\PYPlugins\user路径；盘前启动盘后停止
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] tqcenter初始化失败->RuntimeError; 单只快照获取失败->log+继续(不中断); ClickHouse写入失败->log+继续
# [TESTS] tests/zephyr/data/test_sector_snapshot_collector.py
# [TTL] task_bound
# noqa: m02-manual  M02豁免: 采集器常驻服务,manual启动,非reconciler无需事件触发
"""880xxx 板块实时快照采集器（tqcenter → ClickHouse sector_snapshot 表）。

架构（方案C混合模式）：
  1. 推送层：subscribe_hq 订阅核心99只，~18秒/次推送通知
  2. 轮询层：get_market_snapshot 每30秒轮询全量584只
  3. 收到推送通知或轮询触发时，调 get_market_snapshot 取26字段
  4. 写入 ClickHouse sector_snapshot 表

推送池由 sector_ranking_engine.get_push_pool() 动态选取（5因子复合排名 Top 99）。
首日无快照数据时，ranking_engine 自动回退到成分股数量 Top N。

启动:
    python -m zephyr.data.sector_snapshot_collector
    python -m zephyr.data.sector_snapshot_collector --poll-interval 30 --push-limit 99
"""
from __future__ import annotations

import io
import json
import logging
import sys
import threading
import time
from datetime import UTC, datetime, timedelta, timezone
from typing import Any

log = logging.getLogger(__name__)

# ---------- 常量 ----------

_TQCENTER_PATH = r"E:\tdx\PYPlugins\user"
_BEIJING_TZ = timezone(timedelta(hours=8))

_CH_DB = "c1_market"
_CH_TABLE = f"{_CH_DB}.sector_snapshot"

POLL_INTERVAL = 30
PUSH_POOL_LIMIT = 99
BATCH_SIZE = 500

# SQL 集中化（NO-BARE-SQL gate 豁免 SQL_ 前缀）
SQL_CREATE_TABLE = f"""
CREATE TABLE IF NOT EXISTS {_CH_TABLE} (
    trade_date       Date        COMMENT '交易日',
    timestamp        DateTime    COMMENT '快照时间戳',
    sector_code      String      COMMENT '板块代码 880001.SH',
    market_type      LowCardinality(String) COMMENT 'sector/mkt_index',
    now_price        Decimal(18,4) COMMENT '最新价',
    open_price       Decimal(18,4) COMMENT '开盘价',
    max_price        Decimal(18,4) COMMENT '最高价',
    min_price        Decimal(18,4) COMMENT '最低价',
    last_close       Decimal(18,4) COMMENT '昨收',
    before_5min_now  Decimal(18,4) COMMENT '5分钟前最新价',
    average_price    Decimal(18,4) COMMENT '均价',
    volume           UInt64      COMMENT '成交量(板块恒为0)',
    now_vol          UInt64      COMMENT '现量',
    amount           Decimal(18,2) COMMENT '成交额',
    up_home          UInt32      COMMENT '上涨家数',
    down_home        UInt32      COMMENT '下跌家数',
    inside           UInt32      COMMENT '内盘',
    outside          UInt32      COMMENT '外盘',
    zangsu           Decimal(10,3) COMMENT '涨速',
    data_source      LowCardinality(String) COMMENT 'tqcenter_snapshot/tqcenter_push',
    fetched_at       DateTime    COMMENT '采集时间(UTC)'
) ENGINE = MergeTree
PARTITION BY toYYYYMM(trade_date)
ORDER BY (sector_code, timestamp)
"""

SQL_INSERT = (
    f"INSERT INTO {_CH_TABLE} "
    "(trade_date,timestamp,sector_code,market_type,"
    "now_price,open_price,max_price,min_price,last_close,before_5min_now,average_price,"
    "volume,now_vol,amount,up_home,down_home,inside,outside,zangsu,"
    "data_source,fetched_at) VALUES"
)

SQL_ALL_SECTORS = (
    f"SELECT DISTINCT sector_code FROM {_CH_DB}.sector_constituent "
    f"ORDER BY sector_code"
)

# 推送通知队列（tqcenter 回调入队，push_worker 出队）
_push_queue: list[str] = []
_push_lock = threading.Lock()


# ---------- 时间辅助 ----------

def _now_beijing_naive() -> datetime:
    """返回北京时间的 naive datetime（供 ClickHouse DateTime 列）。"""
    return datetime.now(_BEIJING_TZ).replace(tzinfo=None)


def _now_utc_naive() -> datetime:
    """返回 UTC 时间的 naive datetime（供 fetched_at 列）。"""
    return datetime.now(UTC).replace(tzinfo=None)


# ---------- 快照解析 ----------

def _to_decimal(v: Any, default: float = 0.0) -> float:
    """安全转 float（ClickHouse Decimal 接收 float）。"""
    if v is None or v == "" or v == "None":
        return default
    try:
        return float(v)
    except (ValueError, TypeError):
        return default


def _to_uint(v: Any, default: int = 0) -> int:
    """安全转非负 int。"""
    if v is None or v == "" or v == "None":
        return default
    try:
        n = float(v)
        return int(n) if n >= 0 else default
    except (ValueError, TypeError):
        return default


def classify_market_type(code: str) -> str:
    """880001-880009=mkt_index，8801XX+=sector。"""
    digits = code.replace(".SH", "").replace(".SZ", "")
    if digits.startswith("88000"):
        return "mkt_index"
    return "sector"


def parse_snapshot(snap: dict, sector_code: str, market_type: str,
                   data_source: str, now_bj: datetime | None = None) -> tuple | None:
    """把 tqcenter 快照 dict 解析为 sector_snapshot 表的行 tuple。

    Args:
        snap: tqcenter get_market_snapshot 返回的 dict。
        sector_code: 板块代码，如 "880001.SH"。
        market_type: "sector" 或 "mkt_index"。
        data_source: "tqcenter_snapshot" 或 "tqcenter_push"。
        now_bj: 北京时间 naive datetime（测试注入）；None 则取当前时间。

    Returns:
        行 tuple 或 None（快照无效时）。
    """
    if not snap or snap.get("ErrorId") != "0":
        return None

    if now_bj is None:
        now_bj = _now_beijing_naive()
    today = now_bj.date()
    fetched_at = _now_utc_naive()

    time_str = snap.get("Time", "")
    if time_str:
        try:
            ts = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            ts = now_bj
    else:
        ts = now_bj

    return (
        today, ts, sector_code, market_type,
        _to_decimal(snap.get("Now")),
        _to_decimal(snap.get("Open")),
        _to_decimal(snap.get("Max")),
        _to_decimal(snap.get("Min")),
        _to_decimal(snap.get("LastClose")),
        _to_decimal(snap.get("Before5MinNow")),
        _to_decimal(snap.get("Average")),
        _to_uint(snap.get("Volume")),
        _to_uint(snap.get("NowVol")),
        _to_decimal(snap.get("Amount")),
        _to_uint(snap.get("UpHome")),
        _to_uint(snap.get("DownHome")),
        _to_uint(snap.get("Inside")),
        _to_uint(snap.get("Outside")),
        _to_decimal(snap.get("Zangsu")),
        data_source, fetched_at,
    )


# ---------- ClickHouse 操作 ----------

def _get_ch_client():
    """从 ch_config 真源加载配置创建 ClickHouse 客户端（裁定 #ARCH-CH-024）。"""
    from clickhouse_driver import Client
    from zephyr.data.ch_config import load_ch_config
    cfg = load_ch_config()
    c = Client(
        host=cfg["host"],
        port=int(cfg["port"]),
        user=cfg["user"],
        password=cfg["password"],
        database=cfg["database"],
        connect_timeout=10,
        send_receive_timeout=30,
    )
    c.execute("SELECT 1")
    return c


def _create_table(client) -> None:
    """建表 sector_snapshot（幂等）。"""
    client.execute(SQL_CREATE_TABLE)
    log.info("表 sector_snapshot 已就绪")


def _insert_snapshots(client, rows: list[tuple]) -> int:
    """批量写入快照记录。"""
    if not rows:
        return 0
    client.execute(SQL_INSERT, rows)
    return len(rows)


def _get_all_sector_codes() -> list[str]:
    """从 sector_constituent 表获取全部板块代码。"""
    client = _get_ch_client()
    rows = client.execute(SQL_ALL_SECTORS)
    codes = [r[0] for r in rows]
    client.disconnect()
    return codes


# ---------- tqcenter 初始化 ----------

def _init_tqcenter():
    """初始化 tqcenter 连接，返回 tq 模块。"""
    if _TQCENTER_PATH not in sys.path:
        sys.path.insert(0, _TQCENTER_PATH)
    from tqcenter import tq  # noqa: import-integrity  external-module-tqcenter-not-pip-installed
    tq.initialize(__file__)
    return tq


# ---------- 轮询线程 ----------

def _poll_worker(tq, all_codes: list[str], stop_event: threading.Event):
    """轮询线程：每 POLL_INTERVAL 秒扫一轮全量板块。"""
    log.info("轮询线程启动，共 %d 只板块，间隔 %ds", len(all_codes), POLL_INTERVAL)
    client = _get_ch_client()

    while not stop_event.is_set():
        round_start = time.time()
        rows: list[tuple] = []
        error_count = 0

        for code in all_codes:
            if stop_event.is_set():
                break
            try:
                snap = tq.get_market_snapshot(stock_code=code)
                mtype = classify_market_type(code)
                row = parse_snapshot(snap, code, mtype, "tqcenter_snapshot")
                if row:
                    rows.append(row)
            except Exception as e:  # noqa: BLE001
                error_count += 1
                if error_count <= 2:
                    log.warning("轮询 %s 失败: %s", code, str(e)[:80])

        _write_poll_batch(client, rows, len(all_codes), error_count, round_start)
        _wait_next_round(stop_event, round_start)

    client.disconnect()
    log.info("轮询线程已停止")


def _write_poll_batch(client, rows: list[tuple], total: int,
                      errors: int, round_start: float) -> None:
    """写入轮询批次并日志。"""
    if not rows:
        return
    try:
        n = _insert_snapshots(client, rows)
        log.info("轮询完成: 采集 %d/%d, 写入 %d, 错误 %d, 耗时 %.1fs",
                 len(rows), total, n, errors, time.time() - round_start)
    except Exception as e:  # noqa: BLE001
        log.error("轮询写入失败: %s", str(e)[:200])


def _wait_next_round(stop_event: threading.Event, round_start: float) -> None:
    """等待下一轮轮询（可被 stop_event 中断）。"""
    elapsed = time.time() - round_start
    wait = max(1, POLL_INTERVAL - elapsed)
    for _ in range(int(wait)):
        if stop_event.is_set():
            break
        time.sleep(1)  # noqa: m10-time-trigger  采集器服务循环,非reconciler


# ---------- 推送线程 ----------

def _push_callback(datas):
    """subscribe_hq 回调：收到通知后入队。"""
    try:
        d = json.loads(datas) if isinstance(datas, str) else datas
        code = d.get("Code", "")
        if code:
            with _push_lock:
                _push_queue.append(code)
    except Exception:  # noqa: BLE001
        pass


def _push_worker(tq, push_codes: list[str], stop_event: threading.Event):
    """推送线程：订阅核心99只，收到通知后取快照写入。"""
    log.info("推送线程启动，订阅 %d 只核心板块", len(push_codes))

    try:
        tq.subscribe_hq(stock_list=push_codes, callback=_push_callback)
        log.info("subscribe_hq 订阅成功")
    except Exception as e:  # noqa: BLE001
        log.error("subscribe_hq 失败: %s", str(e)[:200])
        return

    client = _get_ch_client()
    processed = _process_push_loop(tq, client, stop_event)
    client.disconnect()
    log.info("推送线程已停止，共处理 %d 条", processed)


def _process_push_loop(tq, client, stop_event: threading.Event) -> int:
    """推送处理主循环，返回处理总数。"""
    processed = 0
    while not stop_event.is_set():
        code = _pop_push_queue()
        if code:
            processed += _handle_push_code(tq, client, code, processed)
        else:
            time.sleep(0.5)  # noqa: m10-time-trigger  采集器服务循环,非reconciler
    return processed


def _pop_push_queue() -> str | None:
    """从推送队列取出一个 code（线程安全）。"""
    with _push_lock:
        if _push_queue:
            return _push_queue.pop(0)
    return None


def _handle_push_code(tq, client, code: str, processed: int) -> int:
    """处理单个推送通知：取快照+写入，返回1成功/0失败。"""
    try:
        snap = tq.get_market_snapshot(stock_code=code)
        mtype = classify_market_type(code)
        row = parse_snapshot(snap, code, mtype, "tqcenter_push")
        if row:
            _insert_snapshots(client, [row])
            if (processed + 1) % 50 == 0:
                log.info("推送处理: 累计 %d 条", processed + 1)
            return 1
    except Exception as e:  # noqa: BLE001
        log.warning("推送取快照 %s 失败: %s", code, str(e)[:80])
    return 0


# ---------- 主流程 ----------

def main() -> int:
    """采集器主入口。"""
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    log.info("=== 880xxx 板块实时快照采集器启动 ===")

    # 1. 建表
    log.info("[步骤1] 建表...")
    init_client = _get_ch_client()
    _create_table(init_client)
    init_client.disconnect()

    # 2. 初始化 tqcenter
    log.info("[步骤2] 初始化 tqcenter...")
    tq = _init_tqcenter()

    # 3. 获取全量板块代码
    log.info("[步骤3] 获取板块代码...")
    all_codes = _get_all_sector_codes()
    log.info("    全量板块: %d 只", len(all_codes))

    # 4. 动态推送池（由 sector_ranking_engine 5因子排名选取）
    log.info("[步骤4] 选取推送池（5因子动态排名）...")
    from zephyr.data.sector_ranking_engine import get_push_pool
    push_codes = get_push_pool(top_n=PUSH_POOL_LIMIT)
    log.info("    推送池: %d 只", len(push_codes))

    # 5. 启动推送+轮询线程
    log.info("[步骤5] 启动采集线程...")
    stop_event = threading.Event()
    poll_thread = threading.Thread(
        target=_poll_worker, args=(tq, all_codes, stop_event), name="poll", daemon=True)
    push_thread = threading.Thread(
        target=_push_worker, args=(tq, push_codes, stop_event), name="push", daemon=True)
    poll_thread.start()
    push_thread.start()

    log.info("采集中... (Ctrl+C 停止)  轮询层:%ds/轮  推送层:%d只",
             POLL_INTERVAL, len(push_codes))
    try:
        while True:
            threading.Event().wait(timeout=60)  # noqa: m10-time-trigger  采集器服务循环,非reconciler
            log.info("运行中... poll_alive=%s push_alive=%s",
                     poll_thread.is_alive(), push_thread.is_alive())
    except KeyboardInterrupt:
        log.info("停止信号收到...")

    stop_event.set()
    poll_thread.join(timeout=10)
    push_thread.join(timeout=10)
    tq.close()
    log.info("采集器已停止")
    return 0


if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.exit(main())

# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md
# [MODULE] zephyr.frontend.dashboard.api_server
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] zephyr.data.ch_config; clickhouse_driver; fastapi; uvicorn; zephyr.governance.persistence.battle_map_reader; zephyr.governance.strategies.strategy_base; zephyr.pf_core.strategy_engine.tick_strategy_base
# [CONSUMERS] 前端 dashboard（web/services/api.js）
# [STARTUP] manual（python -m zephyr.frontend.dashboard.api_server 或 uvicorn 直跑；面板服务控制台可一键重启）
# [MATURITY] production
# [INVARIANTS] 只读服务（禁任何写副作用）; 非法输入 fail-closed 返回 ok:false; Decimal/Date 一律转 JSON 可序列化
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] CH 连接失败/查询异常 → {"ok": false, "error": "..."}（前端 api.js 据此回退演示数据）
# [TESTS] 手动冒烟：/api/health + /api/kline?symbol=600519
# [A_module] module_id=MOD-L08-001 | layer=service | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""Dashboard 数据 API 服务（只读）——前端四件套数据通道（P2 基建 + stockq 打样）。

职责：把 ClickHouse 行情数据以 JSON 暴露给仪表盘前端。read-only，零写副作用。
端点：
  GET /api/health                     健康检查
  GET /api/kline?symbol=600519&period=1d&limit=300   K 线（period: 1m/5m/15m/30m/60m/1d/1w/1M）
返回：{"ok": true, "bars": [{timestamp(ms), open, high, low, close, volume, amount}]}
异常一律 ok:false——前端据此回退演示数据（演示诚实纪律：前端标"演示"角标）。
"""

from __future__ import annotations

import sys
import socket
import threading
import time
import csv
import json
import logging
from datetime import date, datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger("zk.api_server")

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO / "src") not in sys.path:
    sys.path.insert(0, str(_REPO / "src"))

from clickhouse_driver import Client  # noqa: E402

from zephyr.data.ch_config import load_ch_config  # noqa: E402

app = FastAPI(title="ZephyrAlpha Dashboard API (read-only + backtest-run)")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET", "POST"], allow_headers=["*"])

_PERIOD_TABLE: dict[str, str] = {
    "1m": "kline_1min",
    "5m": "kline_5min",
    "15m": "kline_15min",
    "30m": "kline_30min",
    "60m": "kline_60min",
    "1d": "kline_daily",
    "1w": "kline_weekly",
    "1M": "kline_monthly",
}

_client: Client | None = None
_col_cache: dict[str, dict[str, str]] = {}
_ch_lock = threading.Lock()  # clickhouse_driver 单连接非线程安全：FastAPI 线程池并发请求必须串行化


def _ch() -> Client:
    global _client
    if _client is None:
        cfg = load_ch_config()
        _client = Client(
            host=cfg["host"],
            port=int(cfg.get("port", 9000)),
            user=cfg.get("reader_user") or cfg.get("user", "default"),
            password=cfg.get("reader_password") or cfg.get("password", ""),
            database=cfg.get("database", "c1_market"),
            connect_timeout=3,        # 2026-09-03 实证：无超时 Client 在半开连接上永久挂死
            send_receive_timeout=15,  # 单查询上限，超时异常触发 _ch_exec 弃连自愈
        )
    return _client


def _ch_exec(sql: str, params: dict | None = None) -> list:
    """带锁执行（2026-09-01 实证：stockq 多组件并发取数触发 Simultaneous queries on single connection）。
    2026-09-03 加固：半开连接挂死曾耗尽线程池致整机假死——查询异常即弃连重建，锁获取限时防队列堆积。"""
    global _client
    if not _ch_lock.acquire(timeout=30):
        raise RuntimeError("CH 通道忙（30s 未获锁，疑似上游查询挂死）")
    try:
        return _ch().execute(sql, params or {})
    except Exception:
        _client = None   # 连接疑似坏态：弃置，下一位调用者重建自愈
        raise
    finally:
        _ch_lock.release()


# QMT 文件桥（实盘）：miniQMT 通道 2026-09-18 券商关停，实盘数据一律走文件桥（Owner 2026-09-01 裁定）
_QMT_BRIDGE_STOCK_DIR = Path(r"E:\qmt_bridge\Stock")


def _read_gbk_csv(path: Path) -> list[list[str]]:
    """QMT 导出 CSV 为 GBK 编码（与 ex_core.qmt_file_bridge_broker._read_gbk_csv 同口径）。"""
    with open(path, newline="", encoding="gbk", errors="replace") as f:
        return list(csv.reader(f))


def _safe_float(s: str) -> float:
    try:
        return float(str(s).strip())
    except (ValueError, TypeError):
        return 0.0


def _safe_int(s: str) -> int:
    try:
        return int(float(str(s).strip()))
    except (ValueError, TypeError):
        return 0


def _time_col(table: str) -> str:
    """首Date/DateTime 列为时间列（日线族=trade_date，分钟族=datetime 类）。"""
    if table in _col_cache:
        return _col_cache[table]["time_col"]
    cols = _ch_exec(f"DESCRIBE TABLE {table}")
    time_col = ""
    for row in cols:
        name, typ = row[0], row[1]
        if str(typ).startswith("Date"):
            time_col = name
            break
    if not time_col:
        raise RuntimeError(f"{table} 无 Date/DateTime 列")
    _col_cache[table] = {"time_col": time_col}
    return time_col


def _to_ms(v: Any) -> int:
    if isinstance(v, datetime):
        return int(v.timestamp() * 1000)
    if isinstance(v, date):
        return int(datetime(v.year, v.month, v.day).timestamp() * 1000)
    raise TypeError(f"bad time value: {type(v)}")


@app.get("/api/health")
def health() -> dict[str, Any]:
    return {"ok": True, "service": "dashboard-api", "mode": "read-only"}


@app.get("/api/kline")
def kline(
    symbol: str = Query(..., min_length=1),
    period: str = Query("1d"),
    limit: int = Query(300, ge=1, le=1000),
) -> dict[str, Any]:
    table = _PERIOD_TABLE.get(period)
    if table is None:
        return {"ok": False, "error": f"unsupported period: {period}", "bars": []}
    sym = symbol.split(".")[0].strip()
    if not sym.isalnum():
        return {"ok": False, "error": "bad symbol", "bars": []}
    try:
        tc = _time_col(table)
        rows = _ch_exec(
            f"SELECT {tc}, open, high, low, close, volume, amount FROM {table} "  # noqa: S608（table 来自白名单 _PERIOD_TABLE，tc 来自 DESCRIBE）
            "WHERE symbol=%(s)s ORDER BY " + tc + " DESC LIMIT %(n)s",
            {"s": sym, "n": limit},
        )
    except Exception as exc:  # CH 连接/查询异常 → fail-closed 回退信号
        return {"ok": False, "error": str(exc)[:200], "bars": []}
    bars = [
        {
            "timestamp": _to_ms(r[0]),
            "open": float(r[1]),
            "high": float(r[2]),
            "low": float(r[3]),
            "close": float(r[4]),
            "volume": int(r[5]),
            "amount": float(r[6]),
        }
        for r in reversed(rows)  # DESC 取最新 N 根 → 翻回升序（KLineChart 契约）
    ]
    return {"ok": True, "symbol": sym, "period": period, "count": len(bars), "bars": bars}


@app.get("/api/stock-header")
def stock_header(symbol: str = Query(..., min_length=1)) -> dict[str, Any]:
    """股票标题+关键数据（sq-stock-header / sq-key-data / sq-sector-tags 组件共用）。
    价格源：kline_daily 最新 6 根（daily_valuation 价格列全 0 不可用，2026-09-01 实测）；
    估值源：daily_valuation（仅 pe_ttm/pb_mrq 有效，换手 turnover 全 0 暂无真源→None）；
    资料源：stock_basic（名称/行业/板块，argMax 取 valid_from 最新）。
    """
    sym = symbol.split(".")[0].strip()
    if not sym.isalnum():
        return {"ok": False, "error": "bad symbol", "data": {}}
    try:
        # 1. 名称+行业+板块：stock_basic
        info_rows = _ch_exec(
            "SELECT argMax(name, valid_from), argMax(industry, valid_from), argMax(board, valid_from) "
            "FROM stock_basic WHERE symbol=%(s)s",
            {"s": sym},
        )
        name = str(info_rows[0][0]) if info_rows and info_rows[0][0] else sym
        industry = str(info_rows[0][1]) if info_rows and info_rows[0][1] else ""
        board = str(info_rows[0][2]) if info_rows and info_rows[0][2] else ""

        # 2. 价格：kline_daily 最新 6 根（第 2 根 close 作昨收；量比=当日量/前 5 日均量）
        price_rows = _ch_exec(
            "SELECT trade_date, open, high, low, close, volume, amount FROM kline_daily "
            "WHERE symbol=%(s)s AND close > 0 ORDER BY trade_date DESC LIMIT 6",
            {"s": sym},
        )
        if not price_rows:
            return {"ok": False, "error": "no price data", "data": {}}
        td, o, h, l, close, vol, amt = price_rows[0]
        preclose = float(price_rows[1][4]) if len(price_rows) > 1 else 0.0
        prev5 = [float(r[5]) for r in price_rows[1:6]]
        vol_ratio = float(vol) / (sum(prev5) / len(prev5)) if prev5 and sum(prev5) > 0 else None
        pct = (float(close) - preclose) / preclose * 100 if preclose > 0 else 0.0
        direction = "up" if pct >= 0 else "down"

        # 3. 估值：daily_valuation（pe_ttm/pb_mrq；换手无真源）
        val_rows = _ch_exec(
            "SELECT pe_ttm, pb_mrq FROM daily_valuation "
            "WHERE symbol=%(s)s AND pe_ttm > 0 ORDER BY trade_date DESC LIMIT 1",
            {"s": sym},
        )
        pe_ttm = float(val_rows[0][0]) if val_rows else None
        pb_mrq = float(val_rows[0][1]) if val_rows else None

        return {
            "ok": True,
            "symbol": sym,
            "data": {
                "name": name,
                "code": sym,
                "price": float(close),
                "open": float(o),
                "high": float(h),
                "low": float(l),
                "preclose": preclose,
                "pct_change": pct,
                "pct_change_str": f"{'+' if pct >= 0 else ''}{pct:.2f}%",
                "direction": direction,
                "volume": int(vol),
                "amount": float(amt),
                "volume_ratio": vol_ratio,
                "turnover": None,  # daily_valuation.turnover 全 0，暂无真源（待接入）
                "pe_ttm": pe_ttm,
                "pb_mrq": pb_mrq,
                "industry": industry,
                "board": board,
                "trade_date": td.isoformat(),
            },
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "data": {}}


@app.get("/api/quote")
def quote(symbols: str = Query(..., min_length=1)) -> dict[str, Any]:
    """批量最新报价（sq-fav-list 组件）：多标的最新价+涨跌幅+名称。
    价格源：kline_daily（每标的最新两根，前根 close 作昨收，LIMIT n BY symbol）。
    """
    syms: list[str] = []
    for s in symbols.split(","):
        t = s.split(".")[0].strip()
        if t.isalnum() and t not in syms:
            syms.append(t)
    syms = syms[:50]
    if not syms:
        return {"ok": False, "error": "bad symbols", "data": []}
    try:
        rows = _ch_exec(
            "SELECT symbol, trade_date, close FROM kline_daily "
            "WHERE symbol IN %(syms)s AND close > 0 "
            "ORDER BY trade_date DESC LIMIT 2 BY symbol",
            {"syms": tuple(syms)},
        )
        # 股票表查不到的补查 ETF 表（ETF 不在 kline_daily，2026-09-01 实测）
        found = {r[0] for r in rows}
        missing = [s for s in syms if s not in found]
        if missing:
            rows = list(rows) + list(
                _ch_exec(
                    "SELECT symbol, trade_date, close FROM kline_etf_daily "
                    "WHERE symbol IN %(syms)s AND close > 0 "
                    "ORDER BY trade_date DESC LIMIT 2 BY symbol",
                    {"syms": tuple(missing)},
                )
            )
        by_sym: dict[str, list[tuple[Any, float]]] = {}
        for r in rows:
            by_sym.setdefault(r[0], []).append((r[1], float(r[2])))
        name_rows = _ch_exec(
            "SELECT symbol, argMax(name, valid_from) FROM stock_basic WHERE symbol IN %(syms)s GROUP BY symbol",
            {"syms": tuple(syms)},
        )
        names = {r[0]: str(r[1]) for r in name_rows}
        # ETF 名称补查（etf_list.etf_code 为 sh510300/sz159915 格式，剥前缀匹配）
        no_name = [s for s in syms if s not in names]
        if no_name:
            for r in _ch_exec(
                "SELECT substring(etf_code, 3) AS code, argMax(etf_name, list_date) "
                "FROM etf_list WHERE code IN %(syms)s GROUP BY code",
                {"syms": tuple(no_name)},
            ):
                names[r[0]] = str(r[1])
        data = []
        for s in syms:
            bars = by_sym.get(s)
            if not bars:
                continue
            close_px = bars[0][1]
            preclose = bars[1][1] if len(bars) > 1 else 0.0
            pct = (close_px - preclose) / preclose * 100 if preclose > 0 else 0.0
            data.append(
                {
                    "symbol": s,
                    "name": names.get(s, s),
                    "price": close_px,
                    "pct_change": round(pct, 2),
                    "pct_change_str": f"{'+' if pct >= 0 else ''}{pct:.2f}%",
                    "direction": "up" if pct >= 0 else "down",
                    "trade_date": bars[0][0].isoformat(),
                }
            )
        return {"ok": True, "count": len(data), "data": data}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "data": []}


@app.get("/api/position")
def position() -> dict[str, Any]:
    """QMT 文件桥真实持仓（sq-position-list 组件）。
    数据源：E:\\qmt_bridge\\Stock\\PositionStatics.csv + Account.csv（QMT 终端自动导出，GBK，10s 间隔）。
    背景：miniQMT 通道 2026-09-18 券商关停，实盘数据一律走文件桥（Owner 2026-09-01 裁定）。
    列序与 ex_core CounterStateMirror._sync_positions 同源核对（row[7]=代码 row[9]=拥有 row[15]=可用）。
    """
    pos_file = _QMT_BRIDGE_STOCK_DIR / "PositionStatics.csv"
    try:
        if not pos_file.exists():
            return {"ok": False, "error": "bridge position file missing", "data": []}
        data: list[dict[str, Any]] = []
        for row in _read_gbk_csv(pos_file):
            if len(row) < 19 or row[7].strip() == "证券代码":
                continue
            qty = _safe_int(row[9])
            available = _safe_int(row[15])
            if qty <= 0 and available <= 0:
                continue  # 零持仓行（如标准券占位）不展示
            data.append(
                {
                    "symbol": row[7].strip(),
                    "code": row[7].strip() + "." + row[5].strip(),
                    "name": row[8].strip(),
                    "qty": qty,
                    "available": available,
                    "cost_price": _safe_float(row[11]),
                    "market_value": _safe_float(row[13]),
                    "pnl": _safe_float(row[12]),
                    "pnl_pct": row[17].strip(),
                    "price": _safe_float(row[18]),
                }
            )
        # 账户摘要（Account.csv 单行）
        account: dict[str, Any] = {}
        acct_file = _QMT_BRIDGE_STOCK_DIR / "Account.csv"
        if acct_file.exists():
            for row in _read_gbk_csv(acct_file):
                if len(row) < 11 or row[6].strip() == "总资产":
                    continue
                account = {
                    "total": _safe_float(row[6]),
                    "available": _safe_float(row[7]),
                    "market_value": _safe_float(row[10]),
                }
                break
        mtime = pos_file.stat().st_mtime
        return {
            "ok": True,
            "count": len(data),
            "file_mtime": datetime.fromtimestamp(mtime).isoformat(timespec="seconds"),
            "file_age_seconds": int(time.time() - mtime),
            "account": account,
            "data": data,
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "data": []}


@app.get("/api/events")
def events(days_back: int = Query(180, ge=0, le=3650), days_fwd: int = Query(365, ge=0, le=3650)) -> dict[str, Any]:
    """宏观事件日历（sq-event-row 组件）：CH.calendar_event（期权到期/LPR/交割日/月末等，非个股事件）。
    窗口：今天-days_back ~ 今天+days_fwd。个股财报/解禁暂无真源（待接入）。
    值字段（pub_value/exp_value/prev_value）2026-09-01 扩表新增，未回填=NULL（前端显'未公布'）。
    """
    try:
        rows = _ch_exec(
            "SELECT event_date, event_type, description, pub_value, exp_value, prev_value "
            "FROM calendar_event "
            "WHERE event_date >= today() - %(b)s AND event_date <= today() + %(f)s "
            "ORDER BY event_date",
            {"b": days_back, "f": days_fwd},
        )
        today = date.today()
        data = [
            {
                "date": r[0].isoformat(),
                "type": str(r[1]),
                "description": str(r[2]),
                "pub_value": r[3],
                "exp_value": r[4],
                "prev_value": r[5],
                "is_future": r[0] > today,
            }
            for r in rows
        ]
        return {"ok": True, "count": len(data), "data": data}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "data": []}


@app.get("/api/orderbook")
def orderbook(symbol: str = Query(..., min_length=1)) -> dict[str, Any]:
    """盘口挂单（sq-order-book 组件）：E:\\qmt_bridge\\quote.csv（QMT 终端订阅标的快照导出）。
    背景：miniQMT 2026-09-18 券商关停，盘口走文件桥（Owner 2026-09-01 裁定）。
    档位自适应：动态解析 bid1~bid10/ask1~ask10（导出脚本加列即变十档，2026-09-01 Owner 要求）。
    注意：quote.csv 只含 QMT 内订阅的标的；未订阅标的返回 ok:false（前端标'未订阅'）。
    """
    sym = symbol.split(".")[0].strip()
    if not sym.isalnum():
        return {"ok": False, "error": "bad symbol", "data": {}}
    quote_file = _QMT_BRIDGE_STOCK_DIR.parent / "quote.csv"
    try:
        if not quote_file.exists():
            return {"ok": False, "error": "quote.csv missing", "data": {}}
        with open(quote_file, newline="", encoding="utf-8", errors="replace") as f:
            rows = list(csv.DictReader(f))
        for row in rows:
            if row.get("symbol", "").split(".")[0].strip() == sym:

                def _n(k: str) -> float:
                    try:
                        return float(row.get(k, "") or 0)
                    except ValueError:
                        return 0.0

                def _levels(side: str) -> list[list[float]]:
                    out: list[list[float]] = []
                    for i in range(1, 11):  # 最多十档，有多少列取多少
                        p = row.get(f"{side}{i}", "")
                        if p is None or p == "":
                            break
                        pf = float(p)
                        if pf <= 0:
                            break
                        out.append([pf, _n(f"{side}Vol{i}")])
                    return out

                return {
                    "ok": True,
                    "data": {
                        "symbol": sym,
                        "price": _n("lastPrice"),
                        "open": _n("open"),
                        "high": _n("high"),
                        "low": _n("low"),
                        "preclose": _n("lastClose"),
                        "volume": _n("volume"),
                        "amount": _n("amount"),
                        "bids": _levels("bid"),
                        "asks": _levels("ask"),
                        "timetag": row.get("timetag", ""),
                    },
                }
        return {"ok": False, "error": "not in quote.csv（QMT 未订阅该标的）", "data": {}}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "data": {}}


@app.get("/api/stock-search")
def stock_search(q: str = Query(..., min_length=1), limit: int = Query(20, ge=1, le=100)) -> dict[str, Any]:
    """股票搜索（sq-search-box 组件）：按代码/名称模糊匹配。
    数据源：stock_basic 表。
    """
    q = q.strip()
    if not q:
        return {"ok": True, "data": []}
    try:
        # 代码精确/前缀匹配优先，名称包含次之（stock_basic 无 market 列，symbol 可能重复取 DISTINCT）
        rows = _ch_exec(
            "SELECT DISTINCT symbol, name FROM stock_basic WHERE symbol LIKE %(q)s OR name LIKE %(qn)s LIMIT %(l)s",
            {"q": q + "%", "qn": "%" + q + "%", "l": limit},
        )
        return {
            "ok": True,
            "data": [{"symbol": r[0], "name": r[1]} for r in rows],
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "data": []}


# ── 回测三接口（#BT-PIPELINE-001）：list / detail / run ──────────────────────
# 数据源：data/backtest_artifacts/*.json（BTRUN CLI 强制时序落盘产物）。
# run 走 scripts/run_backtest.py run_one（与 CLI 同一入口，页面/命令行行为一致）。
_BT_ARTIFACTS_DIR = _REPO / "data" / "backtest_artifacts"


# 策略可用性实测标注（2026-09-01 CLI 验证：哪些默认参数下有成交）
_BT_STRATEGY_NOTES = {
    "topn-momentum": "动量TopN（默认参数实测有成交）",
    "default-equity": "默认权益（等权，实测有成交）",
    "multifactor-sleeve": "多因子袖策略（依赖 IC 权重注入，默认参数零成交）",
    "eventdriven-sleeve": "事件驱动袖策略（依赖情绪事件数据，默认参数零成交）",
    "daban-sleeve": "打板袖策略（依赖打板信号源，默认参数零成交）",
    "intraday-surge-fall": "30秒冲高回落做T（仅 Tick 模式）",
    "orderbook-imbalance": "盘口失衡反转做T（仅 Tick 模式）",
    "vwap-reversion": "VWAP回归做T（仅 Tick 模式）",
}


def _strategy_meta_of(cls: Any) -> Any:
    """安全取策略 meta：子类可能以 `meta = StrategyMeta(...)` 类属性遮蔽基类 meta() classmethod
    （实证 2026-09-03：cls.meta() → 'StrategyMeta' object is not callable）——callable 才调用。"""
    m = getattr(cls, "_meta", None)
    if m is not None:
        return m
    mf = getattr(cls, "meta", None)
    try:
        return mf() if callable(mf) else mf
    except Exception:  # noqa: BLE001 — meta 异常按缺失处理，返回 sid 回退
        return None


@app.get("/api/strategies")
def strategies() -> dict[str, Any]:
    """策略库列表（backtest 页策略多选下拉）：StrategyRegistry + TickStrategyRegistry 真源。

    首次调用触发策略链 autodiscover import（~8s）——进程启动时后台线程预热，
    首请求即热（2026-09-01 AbortError 实证：冷启 5s 超时）。
    """
    try:
        sys.path.insert(0, str(_REPO / "src"))
        from zephyr.governance.strategies.strategy_base import StrategyRegistry, autodiscover_strategies

        if not _BT_WARM_DONE.is_set():
            # 冷启（服务被并行会话周期性重启）：先读磁盘快照毫秒级秒回，后台预热完成前不下水
            snap = _load_strategy_snapshot()
            if snap:
                return {"ok": True, "count": len(snap), "data": snap, "stale": True}
            _BT_WARM_DONE.wait(timeout=12)   # 无快照：等预热（复用后台 import，比请求线程再 import 一次省）
            if not _BT_WARM_DONE.is_set():
                autodiscover_strategies("zephyr.pf_core")   # 预热线程卡死兜底：请求线程同步导入
        data = _strategy_rows()
        _save_strategy_snapshot(data)   # 每次全量构建后刷快照（下次冷启秒回）
        return {"ok": True, "count": len(data), "data": data}
    except Exception as exc:
        snap = _load_strategy_snapshot()   # 异常兜底也走快照（快照可用即不空手）
        if snap:
            return {"ok": True, "count": len(snap), "data": snap, "stale": True}
        return {"ok": False, "error": str(exc)[:200], "data": []}


_BT_LIST_CACHE: dict[str, Any] = {"sig": "", "data": None, "ts": 0.0}   # 回测列表缓存（目录指纹未变=毫秒回包）
_BMF_CACHE: dict[str, Any] = {"data": None, "ts": 0.0}   # 作战地图阶段树缓存（10 分钟 TTL）


@app.get("/api/battle-map-flow")
def battle_map_flow() -> dict[str, Any]:
    """作战地图阶段树（策略所处环节模块真源，Owner 2026-09-04 一期）。

    数据源：battle_map_steps 表（zephyr.governance.persistence.battle_map_reader.BattleMapReader，
    production 只读读取器）——前端零硬编码，地图改动自动跟随。
    返回：11 阶段骨架（flow_stage+中文名）× 各阶段环节精简列表（step_id/step_name/design_maturity）。
    """
    cached = _BMF_CACHE["data"]
    if cached and (time.time() - _BMF_CACHE["ts"]) < 600:
        return {"ok": True, "count": cached["count"], "data": cached["data"]}
    try:
        sys.path.insert(0, str(_REPO / "src"))
        from zephyr.governance.persistence.battle_map_reader import BattleMapReader

        with BattleMapReader() as reader:
            steps = reader.get_all_steps()
        stage_zh = {
            "research_incubation": "研究孵化",
            "model_training": "模型训练",
            "backtest_validation": "回测验证",
            "simulation_validation": "模拟验证",
            "stock_selection": "选股",
            "buy_flow": "买入流程",
            "sell_flow": "卖出流程",
            "position_management": "持仓管理",
            "risk_control": "风控",
            "execution": "执行",
            "reconciliation": "对账",
        }
        stages: dict[str, list[dict[str, Any]]] = {}
        for s in steps:
            stages.setdefault(s["flow_stage"], []).append(
                {"step_id": s["step_id"], "step_name": s["step_name"], "maturity": s.get("design_maturity", "")}
            )
        data = [
            {"flow_stage": k, "name_zh": stage_zh.get(k, k), "steps": stages[k]}
            for k in sorted(stages.keys(), key=lambda x: list(stage_zh.keys()).index(x) if x in stage_zh else 99)
        ]
        _BMF_CACHE["data"] = {"count": len(data), "data": data}
        _BMF_CACHE["ts"] = time.time()
        return {"ok": True, "count": len(data), "data": data}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "data": []}


def _bt_dir_sig() -> str:
    """产物目录指纹：文件名+mtime 列表 hash——新产物落盘/重跑即失效（AI 施工完成马上可见）。"""
    if not _BT_ARTIFACTS_DIR.exists():
        return ""
    items = []
    for f in _BT_ARTIFACTS_DIR.glob("bt-*.json"):
        try:
            items.append(f"{f.name}:{f.stat().st_mtime_ns}")
        except OSError:
            continue
    return "|".join(sorted(items))


@app.get("/api/backtest-list")
def backtest_list(strategy_id: str = Query("", description="可选策略过滤")) -> dict[str, Any]:
    """回测产物列表（backtest 页）：扫 artifacts 目录，created_at 降序。
    目录指纹缓存（2026-09-03）：全量读 34+ 大 JSON 仅为取 metrics，实测 3.6s 冷盘 10s+；
    指纹（文件名+mtime_ns）未变直接回缓存，新产物落盘指纹即变——刷新毫秒级。"""
    try:
        if not _BT_ARTIFACTS_DIR.exists():
            return {"ok": True, "count": 0, "data": []}
        sig = _bt_dir_sig()
        cached = _BT_LIST_CACHE["data"]
        if not strategy_id and cached is not None and sig == _BT_LIST_CACHE["sig"]:
            return cached   # 无过滤 + 指纹一致 → 缓存直出（strategy_id 过滤走全量，低频路径）
        out: list[dict[str, Any]] = []
        for f in _BT_ARTIFACTS_DIR.glob("bt-*.json"):
            try:
                with open(f, encoding="utf-8") as fh:
                    d = json.load(fh)
                m = d.get("metrics", {})
                if strategy_id and d.get("strategy_id") != strategy_id:
                    continue
                out.append(
                    {
                        "run_id": d.get("run_id", f.stem),
                        "strategy_id": d.get("strategy_id", ""),
                        "created_at": d.get("created_at", ""),
                        "total_return": m.get("total_return"),
                        "annual_return": m.get("annual_return"),
                        "sharpe_ratio": m.get("sharpe_ratio"),
                        "max_drawdown": m.get("max_drawdown"),
                        "win_rate": m.get("win_rate"),
                        "trades_count": m.get("trades_count"),
                        "overfitting_flag": m.get("overfitting_flag", False),
                        "equity_points": len(d.get("equity_curve") or []),
                        "has_detail": bool(d.get("equity_curve") or d.get("trade_log")),
                    }
                )
            except Exception:  # noqa: BLE001 — 单件损坏不拖垮整列表
                continue
        out.sort(key=lambda x: x.get("created_at") or "", reverse=True)
        result = {"ok": True, "count": len(out), "data": out}
        if not strategy_id:
            _BT_LIST_CACHE.update(sig=sig, data=result, ts=time.time())
        return result
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "data": []}


def _thin_points(points: list[dict], max_points: int) -> list[dict]:
    """时序点等距抽稀（展示层）。存储层（JSON 产物）全量不动——审计可回放；
    tick 模式 127 万点全量渲染必卡死，抽稀到 max_points 视觉无差。"""
    if len(points) <= max_points:
        return points
    step = len(points) / max_points
    return [points[int(i * step)] for i in range(max_points)]


@app.get("/api/backtest-detail")
def backtest_detail(
    run_id: str = Query(..., min_length=3),
    max_points: int = Query(5000, ge=200, le=50000, description="净值/回撤曲线抽稀上限（tick 产物百万点）"),
) -> dict[str, Any]:
    """回测产物详情（backtest 页绩效三图/明细下钻）：按 run_id 读全量 artifact。

    equity/drawdown 曲线等距抽稀到 max_points（首末点保留采样内含）；trade_log
    倒序 cap 500（产物文件全量，审计不受影响）。
    """
    rid = run_id.strip()
    if not rid.startswith("bt-") or not rid[3:].replace("-", "").isalnum():
        return {"ok": False, "error": "bad run_id", "data": {}}
    f = _BT_ARTIFACTS_DIR / f"{rid}.json"
    try:
        if not f.exists():
            return {"ok": False, "error": "run_id not found", "data": {}}
        with open(f, encoding="utf-8") as fh:
            d = json.load(fh)
        eq_full = d.get("equity_curve") or []
        dd_full = d.get("drawdown_curve") or []
        tl_full = d.get("trade_log") or []
        return {
            "ok": True,
            "data": {
                "run_id": d.get("run_id"),
                "strategy_id": d.get("strategy_id"),
                "created_at": d.get("created_at"),
                "metrics": d.get("metrics", {}),
                "equity_curve": _thin_points(eq_full, max_points),
                "drawdown_curve": _thin_points(dd_full, max_points),
                "trade_log": tl_full[-500:][::-1],  # 倒序（最新在前）cap 500
                "benchmark_curve": d.get("benchmark_curve") or [],
                "total_points": {"equity": len(eq_full), "trades": len(tl_full)},  # 全量规模（抽稀明示）
            },
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "data": {}}


# 页面发起回测（#4 全链路）：ThreadPoolExecutor 后台跑（RULE-SEVEN 禁 asyncio 并行），
# 状态存内存 {task_id: {...}}；前端轮询 /api/backtest-run?task_id= 查进度。
from concurrent.futures import ThreadPoolExecutor  # noqa: E402

_BT_RUN_POOL = ThreadPoolExecutor(max_workers=1, thread_name_prefix="bt-run")  # 串行防 CH 连接竞争
_BT_RUN_STATE: dict[str, dict[str, Any]] = {}
_BT_RUN_LOCK = threading.Lock()


_BT_STRAT_SNAPSHOT = _REPO / "data" / "runtime" / "strategy_registry_snapshot.json"
_BT_WARM_DONE = threading.Event()   # 预热完成标志：置位前请求走快照/等待（registry 半成品竞态防线）


def _strategy_rows() -> list[dict[str, Any]]:
    """从两个注册表构建策略行（name=StrategyMeta.name 中文真源；battle_map_ref=作战地图环节归属声明真源）。"""
    from zephyr.governance.strategies.strategy_base import StrategyRegistry

    def _modes(tick_only: bool) -> list[str]:
        """可回测撮合模式（tick_only 推导，不设 meta 字段——Owner 2026-09-04 一期裁定）。"""
        return ["tick"] if tick_only else ["vectorized", "minute"]

    rows: list[dict[str, Any]] = []
    for sid in sorted(StrategyRegistry.list_all().keys() or []):
        cls = StrategyRegistry.list_all()[sid]
        m = _strategy_meta_of(cls)
        rows.append(
            {
                "id": sid,
                "name": (m.name if m and getattr(m, "name", "") else sid),
                "note": _BT_STRATEGY_NOTES.get(sid, ""),
                "tick_only": False,
                "battle_map_ref": (m.battle_map_ref if m and getattr(m, "battle_map_ref", None) else None),
                "modes": _modes(False),
            }
        )
    try:  # tick 策略族（TickStrategyBase 注册表，仅 tick 模式可跑）
        from zephyr.pf_core.strategy_engine.tick_strategy_base import TickStrategyBase, autodiscover_tick_strategies

        autodiscover_tick_strategies("zephyr.pf_core")
        tick_reg = getattr(TickStrategyBase, "_registry", {}) or {}
        for sid in sorted(tick_reg.keys()):
            cls = tick_reg[sid]
            m = _strategy_meta_of(cls)
            rows.append(
                {
                    "id": sid,
                    "name": (m.name if m and getattr(m, "name", "") else sid),
                    "note": _BT_STRATEGY_NOTES.get(sid, "tick 策略"),
                    "tick_only": True,
                    "battle_map_ref": (m.battle_map_ref if m and getattr(m, "battle_map_ref", None) else None),
                    "modes": _modes(True),
                }
            )
    except Exception:  # noqa: BLE001 — tick 注册表不可用时仅返回日频
        pass
    return rows


def _save_strategy_snapshot(rows: list[dict[str, Any]]) -> None:
    """策略行落盘快照——服务冷启（被并行会话周期性重启）时 /api/strategies 免等 ~8s autodiscover，毫秒级秒回。"""
    try:
        _BT_STRAT_SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
        _BT_STRAT_SNAPSHOT.write_text(
            json.dumps({"saved_at": datetime.now().isoformat(timespec="seconds"), "data": rows}, ensure_ascii=False),
            encoding="utf-8",
        )
    except Exception:  # noqa: BLE001 — 快照失败不影响主流程
        pass


def _load_strategy_snapshot() -> list[dict[str, Any]] | None:
    try:
        if not _BT_STRAT_SNAPSHOT.exists():
            return None
        snap = json.loads(_BT_STRAT_SNAPSHOT.read_text(encoding="utf-8"))
        rows = snap.get("data") or None
        # schema 版本检查：缺新字段（modes）=改造前旧快照 → 弃用走预热全量（防旧 schema 冒充真源，2026-09-04 实证）
        if rows and isinstance(rows[0], dict) and "modes" not in rows[0]:
            return None
        return rows
    except Exception:  # noqa: BLE001
        return None


def _warm_strategy_registry() -> None:
    """启动预热：import 策略链（autodiscover）——完成后刷新磁盘快照（冷启秒回数据源）。"""
    try:
        sys.path.insert(0, str(_REPO / "src"))
        from zephyr.governance.strategies.strategy_base import autodiscover_strategies

        autodiscover_strategies("zephyr.pf_core")
        rows = _strategy_rows()
        if rows:
            _save_strategy_snapshot(rows)
    except Exception:  # noqa: BLE001 — 预热失败不炸服务，首请求再试
        pass


threading.Thread(target=_warm_strategy_registry, daemon=True, name="bt-strategy-warm").start()


def _bt_run_task(task_id: str, params: dict[str, Any]) -> None:
    """后台回测线程体：跑 run_one（多策略循环）→ 更新状态（成功附 run_id 列表）。"""
    try:
        sys.path.insert(0, str(_REPO / "scripts"))
        from run_backtest import run_one

        strategies = params["strategies"] or [params["strategy_id"]]
        summaries = []
        for sid in strategies:
            summaries.append(
                run_one(
                    strategy_id=sid,
                    symbols=params["symbols"],
                    start=params["start"],
                    end=params["end"],
                    factor_ids=params.get("factor_ids", ["momentum_20d"]),
                    rebalance_freq=params.get("rebalance_freq", "W-FRI"),
                    top_n=int(params.get("top_n", 10)),
                    max_single=float(params.get("max_single", 0.10)),
                    initial_capital=float(params.get("initial_capital", 1_000_000.0)),
                    pit_shift=int(params.get("pit_shift", 1)),
                    mode=params.get("mode", "vectorized"),
                )
            )
        ok_all = all(s.get("ok") for s in summaries)
        with _BT_RUN_LOCK:
            if ok_all:
                _BT_RUN_STATE[task_id] = {
                    "status": "done",
                    "results": summaries,
                    "run_id": summaries[-1]["run_id"] if summaries else None,
                    "run_ids": [s["run_id"] for s in summaries if s.get("run_id")],
                    "mode": params.get("mode", "vectorized"),
                    "equity_points": summaries[-1].get("equity_points", 0) if summaries else 0,
                    "trades": sum(s.get("trades", 0) for s in summaries),
                    "metrics": summaries[-1].get("metrics", {}) if summaries else {},
                }
            else:
                errs = "; ".join(s.get("error", "?") for s in summaries if not s.get("ok"))
                _BT_RUN_STATE[task_id] = {"status": "failed", "error": errs[:300]}
    except Exception as exc:  # noqa: BLE001
        with _BT_RUN_LOCK:
            _BT_RUN_STATE[task_id] = {"status": "failed", "error": str(exc)[:300]}


@app.post("/api/backtest-run")
def backtest_run(body: dict[str, Any]) -> dict[str, Any]:
    """发起回测（backtest 页「新建回测」）：入队后台执行，返回 task_id。

    body: {strategies: [..]（多选，兼容旧 strategy_id 单值）, symbols: [..], start, end,
           mode?: vectorized|tick, factor_ids?, top_n?, initial_capital?...}
    多策略循环串行跑（max_workers=1 队列天然排队）；mode=tick 走 EDE 完全仿真
    （ChTickProvider 逐 tick 回放 + 5 档盘口撮合）。
    """
    strategies = [str(s).strip() for s in body.get("strategies", []) if str(s).strip()]
    if not strategies and body.get("strategy_id"):
        strategies = [str(body["strategy_id"]).strip()]
    symbols = [str(s).strip() for s in body.get("symbols", []) if str(s).strip()]
    start = str(body.get("start", "")).strip()
    end = str(body.get("end", "")).strip()
    mode = str(body.get("mode", "vectorized")).strip()
    if mode not in ("vectorized", "minute", "tick"):
        mode = "vectorized"
    if not strategies or not symbols or not start or not end:
        return {"ok": False, "error": "strategies/symbols/start/end required", "task_id": None}
    task_id = f"btrun-{int(time.time())}-{len(_BT_RUN_STATE) % 10000}"
    with _BT_RUN_LOCK:
        _BT_RUN_STATE[task_id] = {
            "status": "running",
            "params": {"strategies": strategies, "symbols": symbols, "start": start, "end": end, "mode": mode},
        }
    _BT_RUN_POOL.submit(
        _bt_run_task,
        task_id,
        {
            "strategies": strategies,
            "strategy_id": strategies[0],
            "symbols": symbols,
            "start": start,
            "end": end,
            "mode": mode,
            "factor_ids": body.get("factor_ids", ["momentum_20d"]),
            "rebalance_freq": body.get("rebalance_freq", "W-FRI"),
            "top_n": body.get("top_n", 10),
            "max_single": body.get("max_single", 0.10),
            "initial_capital": body.get("initial_capital", 1_000_000.0),
            "pit_shift": body.get("pit_shift", 1),
        },
    )
    return {"ok": True, "task_id": task_id, "status": "running", "strategies": strategies, "mode": mode}


@app.get("/api/backtest-run")
def backtest_run_status(task_id: str = Query(..., min_length=3)) -> dict[str, Any]:
    """轮询回测任务状态：running / done / failed（done 附 run_id 可跳详情）。"""
    with _BT_RUN_LOCK:
        st = _BT_RUN_STATE.get(task_id.strip())
    if st is None:
        return {"ok": False, "error": "task not found", "status": "unknown"}
    return {"ok": True, **st}


# ── 整装回测三端点（二期整装回测后端，MOD-FWCOMP-001；追加式，复用 backtest-run task 模式）──
# 组合回测器真源: zephyr.pf_core.strategy_engine.framework_composer；
# 方案权重真源: config/framework_plans.yaml（防御/均衡/激进三套，Σ=100%）。
# 与 /api/backtest-run 的边界: backtest-run=多策略各自跑各自出净值；framework-backtest-run=
# 方案权重×子策略权重面板线性合成组合面板→引擎跑出单条组合净值（整装语义）。
from zephyr.shared.utils.time_utils import now_utc  # noqa: E402

_FW_RUN_POOL = ThreadPoolExecutor(max_workers=1, thread_name_prefix="fw-run")  # 串行防 CH 连接竞争
_FW_RUN_STATE: dict[str, dict[str, Any]] = {}
_FW_RUN_LOCK = threading.Lock()


def _fw_run_task(task_id: str, params: dict[str, Any]) -> None:
    """后台整装回测线程体：run_framework_backtest → 更新状态（成功附 run_id/artifact）。"""
    try:
        from zephyr.pf_core.strategy_engine.framework_composer import (
            FrameworkBacktestConfig,
            run_framework_backtest,
        )

        summary = run_framework_backtest(
            params["plan_id"],
            params["symbols"],
            params["start"],
            params["end"],
            config=FrameworkBacktestConfig(
                factor_ids=tuple(params.get("factor_ids", ["momentum_20d"])),
                rebalance_freq=params.get("rebalance_freq", "W-FRI"),
                top_n=int(params.get("top_n", 10)),
                max_single=float(params.get("max_single", 0.10)),
                initial_capital=float(params.get("initial_capital", 1_000_000.0)),
                pit_shift=int(params.get("pit_shift", 1)),
                allow_partial=bool(params.get("allow_partial", True)),
            ),
        )
        with _FW_RUN_LOCK:
            if summary.get("ok"):
                _FW_RUN_STATE[task_id] = {
                    "status": "done",
                    "run_id": summary["run_id"],
                    "plan_id": summary["plan_id"],
                    "participants": summary["participants"],
                    "skipped": summary["skipped"],
                    "rescale_factor": summary["rescale_factor"],
                    "equity_points": summary["equity_points"],
                    "trades": summary["trades"],
                    "metrics": summary["metrics"],
                    "warn": summary.get("warn"),
                }
            else:
                _FW_RUN_STATE[task_id] = {
                    "status": "failed",
                    "error": str(summary.get("error", "?"))[:300],
                    "plan_id": params["plan_id"],
                }
    except Exception as exc:  # noqa: BLE001 — 与 backtest-run 线程体同款兜底
        with _FW_RUN_LOCK:
            _FW_RUN_STATE[task_id] = {"status": "failed", "error": str(exc)[:300]}


@app.get("/api/framework-plans")
def framework_plans() -> dict[str, Any]:
    """列整装方案清单（三套预设）：方案元数据 + 子策略权重明细（前端方案选择器数据源）。"""
    try:
        from zephyr.pf_core.strategy_engine.framework_composer import load_framework_plans

        plans = load_framework_plans()
        return {
            "ok": True,
            "count": len(plans),
            "data": [
                {
                    "plan_id": p.plan_id,
                    "name": p.name,
                    "risk_profile": p.risk_profile,
                    "description": p.description,
                    "total_weight": p.total_weight,
                    "weights": [
                        {"strategy_id": w.strategy_id, "weight": w.weight, "role": w.role}
                        for w in p.weights
                    ],
                }
                for p in plans
            ],
        }
    except Exception as exc:  # noqa: BLE001 — fail-closed 契约（配置缺失/YAML 非法/权重和≠1）
        return {"ok": False, "error": str(exc)[:200], "data": []}


@app.post("/api/framework-backtest-run")
def framework_backtest_run(body: dict[str, Any]) -> dict[str, Any]:
    """发起整装回测：入队后台执行，返回 task_id（轮询 GET /api/framework-backtest-run）。

    body: {plan_id: "fw-defensive|fw-balanced|fw-aggressive", symbols: [..], start, end,
           factor_ids?, rebalance_freq?, top_n?, max_single?, initial_capital?, pit_shift?,
           allow_partial?（默认 true：tick-only 成员跳过后权重显式再归一化并披露）}
    产物: data/backtest_artifacts/bt-fw-*.json（与单策略 schema 对齐，plan_id 落 metrics）。
    """
    plan_id = str(body.get("plan_id", "")).strip()
    symbols = [str(s).strip() for s in body.get("symbols", []) if str(s).strip()]
    start = str(body.get("start", "")).strip()
    end = str(body.get("end", "")).strip()
    if not plan_id or not symbols or not start or not end:
        return {"ok": False, "error": "plan_id/symbols/start/end required", "task_id": None}
    task_id = f"fwrun-{int(now_utc().timestamp())}-{len(_FW_RUN_STATE) % 10000}"
    with _FW_RUN_LOCK:
        _FW_RUN_STATE[task_id] = {
            "status": "running",
            "params": {"plan_id": plan_id, "symbols": symbols, "start": start, "end": end},
        }
    _FW_RUN_POOL.submit(
        _fw_run_task,
        task_id,
        {
            "plan_id": plan_id,
            "symbols": symbols,
            "start": start,
            "end": end,
            "factor_ids": body.get("factor_ids", ["momentum_20d"]),
            "rebalance_freq": body.get("rebalance_freq", "W-FRI"),
            "top_n": body.get("top_n", 10),
            "max_single": body.get("max_single", 0.10),
            "initial_capital": body.get("initial_capital", 1_000_000.0),
            "pit_shift": body.get("pit_shift", 1),
            "allow_partial": body.get("allow_partial", True),
        },
    )
    return {"ok": True, "task_id": task_id, "status": "running", "plan_id": plan_id}


@app.get("/api/framework-backtest-run")
def framework_backtest_run_status(task_id: str = Query(..., min_length=3)) -> dict[str, Any]:
    """轮询整装回测任务状态：running / done / failed（done 附 run_id=bt-fw-* 可跳详情）。"""
    with _FW_RUN_LOCK:
        st = _FW_RUN_STATE.get(task_id.strip())
    if st is None:
        return {"ok": False, "error": "task not found", "status": "unknown"}
    return {"ok": True, **st}


# ── 信号两接口（#BT-PIPELINE-001 阶段三）：market_signal_history 两管道 ──
# 管道 A source='strategy_weight'（BTRUN 权重面板）/ 管道 B source='factor_synth'（日频因子截面）。
_VALID_SOURCES = ("factor_synth", "strategy_weight")


@app.get("/api/signals")
def signals(
    symbols: str = Query("", description="逗号分隔纯数字代码，空=仅返回 sources 概要"),
    sources: str = Query("factor_synth,strategy_weight"),
) -> dict[str, Any]:
    """个股最新信号（持仓页信号列/stockq 量化块）：每 (symbol, source, signal_id) 取最新一行。"""
    src_list = [s.strip() for s in sources.split(",") if s.strip() in _VALID_SOURCES]
    if not src_list:
        return {"ok": False, "error": "bad sources", "data": []}
    try:
        conds = ["source IN (" + ",".join("'" + s + "'" for s in src_list) + ")"]
        syms = []
        for s in symbols.split(","):
            t = s.strip().split(".")[0]
            if t.isalnum():
                syms.append(t)
        if syms:
            conds.append("symbol IN (" + ",".join("'" + t + "'" for t in syms) + ")")
        rows = _ch_exec(
            "SELECT trade_date, symbol, source, signal_id, direction, score, confidence, "
            "rank_in_universe, meta FROM c1_market.market_signal_history FINAL "
            "WHERE " + " AND ".join(conds) + " "
            "ORDER BY trade_date DESC, computed_at DESC "
            "LIMIT 1 BY symbol, source, signal_id"
        )
        data = []
        for r in rows:
            try:
                meta = json.loads(r[8]) if r[8] else {}
            except Exception:  # noqa: BLE001 — meta 脏数据不炸接口
                meta = {}
            data.append(
                {
                    "trade_date": r[0].isoformat() if hasattr(r[0], "isoformat") else str(r[0]),
                    "symbol": r[1],
                    "source": r[2],
                    "signal_id": r[3],
                    "direction": r[4],
                    "score": float(r[5]),
                    "confidence": float(r[6] or 0.0),
                    "rank": int(r[7] or 0),
                    "meta": meta,
                }
            )
        return {"ok": True, "count": len(data), "data": data}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "data": []}


@app.get("/api/signals-overview")
def signals_overview() -> dict[str, Any]:
    """信号总览（warroom 聚合）：每 (source, signal_id) 最新交易日的方向分布 + 强弱两端。"""
    try:
        rows = _ch_exec(
            "SELECT source, signal_id, direction, count(), max(trade_date), "
            "argMax(score, score) FROM "
            "(SELECT * FROM c1_market.market_signal_history FINAL "
            " ORDER BY trade_date DESC, computed_at DESC LIMIT 1 BY symbol, source, signal_id) "
            "GROUP BY source, signal_id, direction ORDER BY source, signal_id"
        )
        summary: dict[tuple, dict] = {}
        for src, sid, direction, cnt, max_d, _ in rows:
            key = (src, sid)
            item = summary.setdefault(
                key,
                {
                    "source": src,
                    "signal_id": sid,
                    "trade_date": max_d.isoformat(),
                    "buy": 0,
                    "sell": 0,
                    "hold": 0,
                    "neutral": 0,
                },
            )
            item[direction] = int(cnt)
        # 强弱两端（factor_synth 最新截面 top/bottom 5）
        top_bottom: dict[str, dict] = {}
        for src, sid in list(summary.keys()):
            tb = _ch_exec(
                "SELECT symbol, score, direction, rank_in_universe FROM c1_market.market_signal_history FINAL "
                "WHERE source = '" + src + "' AND signal_id = '" + sid + "' "
                "AND trade_date = '" + summary[(src, sid)]["trade_date"] + "' "
                "ORDER BY score DESC LIMIT 5"
            )
            bottom = _ch_exec(
                "SELECT symbol, score, direction, rank_in_universe FROM c1_market.market_signal_history FINAL "
                "WHERE source = '" + src + "' AND signal_id = '" + sid + "' "
                "AND trade_date = '" + summary[(src, sid)]["trade_date"] + "' "
                "ORDER BY score ASC LIMIT 5"
            )
            fmt = lambda r: {"symbol": r[0], "score": float(r[1]), "direction": r[2], "rank": int(r[3] or 0)}  # noqa: E731
            top_bottom[f"{src}:{sid}"] = {"top5": [fmt(r) for r in tb], "bottom5": [fmt(r) for r in bottom]}
        return {"ok": True, "data": list(summary.values()), "extremes": top_bottom}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "data": []}


# ── 服务总闸（Owner 2026-09-02 裁定：桌面 Dashboard 承担启动编排）─────────────
# 真源=services_registry.SERVICE_CATALOG（16 启动项）；psutil 采集 CPU/内存；
# 分级开关（free/confirm/guard/external/self）+ 操作审计落盘 tmp/services_control_log.jsonl


@app.get("/api/services-status")
def services_status() -> dict[str, Any]:
    """服务总闸状态：16 启动项四态灯（DS-12）+ CPU/内存 + 心跳年龄 + 整机水位。"""
    from zephyr.frontend.dashboard.services_registry import get_control_log, get_services_status

    st = get_services_status()
    st["control_log"] = get_control_log()
    return st


@app.post("/api/services-control")
def services_control(body: dict[str, Any]) -> dict[str, Any]:
    """服务启停控制：body={id, action: start|stop|restart, confirm?: bool}。

    分级闸门：confirm 级未带 confirm=true 返回 need_confirm（前端弹确认框）；
    guard/external/self 级一律拒绝（保命进程/外部程序/宿主不许在此操作）——
    唯一例外：self 级（api_server）支持 restart（分离代理自重启，二次确认）。
    """
    from zephyr.frontend.dashboard.services_registry import control_service

    sid = str(body.get("id", "")).strip()
    action = str(body.get("action", "")).strip()
    if action not in ("start", "stop", "restart"):
        return {"ok": False, "error": "action must be start|stop|restart"}
    return control_service(sid, action, confirm=bool(body.get("confirm")))


# ── 数据源监管真源（Owner 2026-09-03：datasrc 页全部接通）─────────────────
# 真源：logs/source_health_YYYYMMDD.log（scheduler 启动时全源实探）+ data/failures/*.json（alerter 真实告警）
_SOURCE_CAPS = {
    "miniqmt": "行情/五档/委托", "tdx": "行情（通达信）", "tickflow": "行情 tick 流",
    "baostock": "行情备源", "akshare": "日频/财务/股东", "tushare": "日频/基本面",
    "rss": "新闻聚合", "cls": "财联社新闻电报", "eastmoney_news": "东财新闻",
    "tqcenter": "行情（同花顺 TQ）",
}


@app.get("/api/sources-status")
def sources_status() -> dict[str, Any]:
    """数据源监管真源：最新健康探针日志解析 + alerter 真实告警流水 + KPI 聚合。"""
    import re as _re

    logs_dir = _REPO / "logs"
    health_logs = sorted(logs_dir.glob("source_health_*.log"))
    sources: list[dict[str, Any]] = []
    checked_at = ""
    ok_n = bad_n = 0
    if health_logs:
        text = health_logs[-1].read_text(encoding="utf-8", errors="ignore")
        m = _re.search(r"时间: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", text)
        checked_at = m.group(1) if m else ""
        for line in text.splitlines():
            # 两种行格式：healthy 带 "(行数, 耗时)"；connect_fail 直接跟说明文字（无括号）
            mm = _re.match(r"  ([✓✗⚠])\s+(\S+)\s+(\S+)\s*(.*)", line)
            if not mm:
                continue
            mark, name, status, rest = mm.groups()
            light = {"✓": "green", "✗": "red", "⚠": "yellow"}.get(mark, "gray")
            if status == "test_fail":   # 环境/连接问题（如 QMT 没开）——黄灯不吓人
                light = "yellow"
            if light == "green":
                ok_n += 1
            else:
                bad_n += 1
            sources.append({
                "name": name, "caps": _SOURCE_CAPS.get(name, "—"),
                "light": light, "status": status,
                "detail": rest.strip(),
            })
    # 退役源（真源=历史裁定事实：iFind 配额耗尽 08-14 退役）
    sources.append({"name": "iFind", "caps": "宏观 EDB", "light": "gray",
                    "status": "退役", "detail": "配额耗尽 08-14 退役"})
    failures: list[dict[str, Any]] = []
    fail_dir = _REPO / "data" / "failures"
    if fail_dir.exists():
        for f in sorted(fail_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:8]:
            try:
                d = json.loads(f.read_text(encoding="utf-8"))
                failures.append({
                    "ts": (d.get("timestamp") or f.stem)[:19].replace("T", " "),
                    "task_id": d.get("task_id", "?"), "source": d.get("source", "?"),
                    "level": d.get("level", "?"), "error": str(d.get("error", ""))[:120],
                })
            except Exception:  # noqa: BLE001 — 脏告警文件跳过
                continue

    # ── 30 日可用率实测（真源=全部健康探针日志；sla_tracker 是纯内存引擎无落盘，从探针史重建）──
    per_source: dict[str, dict[str, int]] = {}
    for lf in health_logs:
        seen: dict[str, str] = {}
        try:
            for line in lf.read_text(encoding="utf-8", errors="ignore").splitlines():
                mm = _re.match(r"  ([✓✗⚠])\s+(\S+)\s+(\S+)\s", line)
                if mm:
                    seen[mm.group(2)] = mm.group(1)   # 同文件同源取最后状态
        except OSError:
            continue
        for name, mark in seen.items():
            d2 = per_source.setdefault(name, {"ok": 0, "total": 0})
            d2["total"] += 1
            if mark == "✓":
                d2["ok"] += 1
    sla = [
        {"name": n, "ok": v["ok"], "total": v["total"],
         "avail": round(v["ok"] / v["total"] * 100, 1) if v["total"] else 0.0}
        for n, v in sorted(per_source.items(), key=lambda kv: -(kv[1]["ok"] / kv[1]["total"] if kv[1]["total"] else 0))
    ]
    return {"ok": True, "sources": sources, "failures": failures, "sla": sla,
            "checked_at": checked_at, "ok_n": ok_n, "bad_n": bad_n,
            "generated_at": datetime.now().isoformat(" ", "seconds")}


# ── 数据下载监管真源（Owner 2026-09-03：表级下载实况——146 表新鲜度一页看全）────
_SQL_TABLE_FRESH = (
    # 三库全表全集（含空表——子查询聚合+LEFT JOIN 保证 0 parts 表也出现，灰灯"未启动"DS-12）；
    # 注意：CH LEFT JOIN 未命中填类型默认值（非 NULL），故用子查询预聚合——未匹配自然
    # 得 parts=0/空串，禁改回"LEFT JOIN system.parts + count(p.name)"（默认行会被计数成 1）。
    # 表状态真源=system.tables+parts，禁再回退到 parts-only 口径（16 张空表曾整页隐身）。
    "SELECT t.database, t.name, p.parts, p.rows_, p.earliest, p.latest "
    "FROM system.tables t "
    "LEFT JOIN ("
    "SELECT database, table, count() AS parts, sum(rows) AS rows_, "
    "min(partition) AS earliest, max(partition) AS latest "
    "FROM system.parts WHERE active AND database IN ('c0_meta','c1_market','c3_fundamental') "
    "GROUP BY database, table"
    ") p ON p.database = t.database AND p.table = t.name "
    "WHERE t.database IN ('c0_meta','c1_market','c3_fundamental') AND t.engine NOT LIKE '%%View%%' "
    "ORDER BY t.database, t.name"
)
_SQL_INSERT_15M = (
    "SELECT query, written_rows, event_time FROM system.query_log "
    "WHERE type='QueryFinish' AND query LIKE 'INSERT%' AND event_time > now()-900"
)

_DL_FREQ_HINT = (   # 表名 → 预期更新周期（天）启发；无命中默认 45（月级）
    (("1min", "5min", "15min", "30min", "60min"), 3),
    (("daily", "_quote", "snapshot", "tick_data", "signal_history", "intraday"), 4),
    (("weekly",), 12),
    (("monthly",), 45),
)

# 表中文名（数据资产登记：大白话中文名——Owner 要求"所有数据一定要有中文"；未登记回退表名）
_TABLE_ZH = {
    "a50_futures_daily": "A50 期货日线", "adj_factor": "复权因子", "auction_book": "集合竞价盘口",
    "auction_snapshot": "集合竞价快照", "block_trade": "大宗交易", "block_trade_detail": "大宗交易明细",
    "calendar_event": "宏观事件日历", "concept_board": "概念板块", "concept_board_constituent": "概念板块成分",
    "concept_sector": "概念行业", "convertible_bond_iv": "可转债隐波", "convertible_bond_list": "可转债清单",
    "cross_validation_log": "交叉验证日志", "daily_valuation": "每日估值", "dragon_tiger": "龙虎榜",
    "dragon_tiger_seat": "龙虎榜席位", "etf_list": "ETF 清单", "etf_nav": "ETF 净值",
    "futures_kline_qmt": "期货 K 线（QMT）", "futures_position": "期货持仓", "futures_term_structure": "期货期限结构",
    "hk_connect_flow": "港股通资金流", "hk_kline": "港股 K 线", "hk_stock_list": "港股清单",
    "hk_trade_calendar": "港股交易日历", "hog_futures_core": "生猪期货核心", "hog_province_spot": "生猪省现货",
    "hog_spot_index": "生猪现货指数", "index_constituent": "指数成分", "index_list": "指数清单",
    "index_quote": "指数行情", "index_valuation_daily": "指数每日估值", "index_weight": "指数权重",
    "industry_class": "行业分类", "ipo_calendar": "IPO 日历", "kline_15min": "15 分钟 K 线",
    "kline_1min": "1 分钟 K 线", "kline_30min": "30 分钟 K 线", "kline_5min": "5 分钟 K 线",
    "kline_60min": "60 分钟 K 线", "kline_cb": "可转债 K 线", "kline_daily": "日 K 线",
    "kline_daily_bak_256": "日 K 备份（256）", "kline_daily_hfq": "日 K 后复权", "kline_etf_15min": "ETF 15 分 K",
    "kline_etf_1min": "ETF 1 分 K", "kline_etf_30min": "ETF 30 分 K", "kline_etf_5min": "ETF 5 分 K",
    "kline_etf_60min": "ETF 60 分 K", "kline_etf_daily": "ETF 日 K", "kline_futures": "期货 K 线",
    "kline_global": "全球 K 线", "kline_hk_daily": "港股日 K", "kline_index": "指数日 K",
    "kline_lof_15min": "LOF 15 分 K", "kline_lof_1min": "LOF 1 分 K", "kline_lof_30min": "LOF 30 分 K",
    "kline_lof_5min": "LOF 5 分 K", "kline_lof_60min": "LOF 60 分 K", "kline_monthly": "月 K",
    "kline_monthly_hfq": "月 K 后复权", "kline_sector": "板块 K 线", "kline_sector_880": "板块 K 线（880）",
    "kline_sector_intraday": "板块盘中 K", "kline_us_daily": "美股日 K", "kline_weekly": "周 K",
    "kline_weekly_hfq": "周 K 后复权", "limit_up_down": "涨跌停明细", "lof_list": "LOF 清单",
    "macro_data": "宏观数据", "margin_trading": "两融数据", "market_breadth_snapshot": "市场宽度快照",
    "market_signal_history": "量化信号历史", "money_flow": "资金流", "news_sentiment_window": "新闻情绪窗口",
    "northbound_hold_snapshot": "北向持仓快照", "option_greeks": "期权希腊字母", "option_iv_surface": "期权波面",
    "option_kline": "期权 K 线", "realtime_snapshot": "实时快照", "sector_constituent": "行业成分",
    "sector_list": "板块清单", "sector_meta": "板块元数据", "sector_snapshot": "板块快照",
    "st_stock_list": "ST 股清单", "stk_limit": "涨跌停价", "stock_basic": "股票基础信息",
    "stock_hot_rank": "个股人气榜", "stock_indicator": "个股指标", "stock_list": "股票清单",
    "technical_indicator": "技术指标", "tick_data": "Tick 逐笔", "trade_calendar": "交易日历",
    "us_futures_intraday": "美股期货盘中", "us_index": "美股指数", "weather_data": "天气数据",
    "analyst_forecast": "分析师预测", "audit_opinion": "审计意见", "balance_sheet": "资产负债表",
    "cashflow_statement": "现金流量表", "disclosure_plan": "披露计划", "dividend": "分红送配",
    "earnings_forecast": "业绩预测", "equity_pledge_detail": "股权质押明细", "equity_pledge_summary": "股权质押汇总",
    "express_report": "业绩快报", "financial_indicator": "财务指标", "income_statement": "利润表",
    "industry_class_suppl": "行业分类补充", "main_business": "主营业务", "news_data": "新闻数据",
    "repurchase": "回购", "restricted_shares": "限售解禁", "rights_issue": "配股",
    "share_change": "股本变动", "share_unlock": "限售解禁日历", "shareholder_count": "股东人数",
    "top10_circulating_shareholders": "十大流通股东", "top10_shareholders": "十大股东",
    "fetch_perf": "抓取性能记录",
    # 2026-09-03 对账补齐（此前 18 张表页面显示裸表名）：无管道预留表/空表/归档快照
    "account_nav_daily": "账户净值日频", "daban_board_event": "打板事件", "edb_data": "宏观 EDB（已退役）",
    "etf_benchmark": "ETF 基准指数", "execution_report": "执行回报", "index_adjustment": "指数调整",
    "ipo_schedule": "IPO 排期", "l2_tick": "Level-2 逐笔", "limit_up_pool": "涨停池",
    "margin_target_adjustment": "两融标的调整", "market_index_meta": "市场指数元数据",
    "msci_adjustment": "MSCI 调样", "reconciliation_differences": "对账差异",
    "sector_fund_flow": "板块资金流", "stock_valuation": "个股估值（预留）", "suspend": "停牌清单",
    "news_data_corrupt_20260828": "新闻数据（08-28 损坏快照·归档）",
    "news_data_pre_tz2_20260828": "新闻数据（08-28 迁移前快照·归档）",
}

# 源 → VPN 属性（真源=源的网络属性登记：海外源需要 VPN；国内源禁 VPN——走代理反而连不上）
_SOURCE_VPN = {
    "miniqmt": ("禁", "国内券商通道，挂代理会断"), "tdx": ("禁", "国内行情通道"),
    "tickflow": ("禁", "国内行情通道"), "baostock": ("禁", "国内通道"),
    "akshare": ("禁", "国内接口为主（子接口偶有海外）"), "cls": ("禁", "国内电报"),
    "eastmoney_news": ("禁", "国内接口"), "tqcenter": ("禁", "国内通道"),
    "rss": ("禁", "国内源为主"), "fred": ("需", "美联储海外接口"),
    "okx": ("需", "海外交易所"), "us": ("需", "美股海外数据"),
    "eia": ("需", "美国能源署海外接口"), "qweather": ("禁", "和风天气国内接口"),
    "internal": ("—", "内部计算产物，不走网络"), "backfill": ("—", "内部回填"),
}

_SCHEDULE_ZH = {
    "daily_kline": "盘后日K（16:30）", "daily_capital": "盘后资金（18:00）", "daily_event": "盘后事件（19:00）",
    "weekend_financial": "周末财务", "monthly_static": "月初静态", "intraday_minute": "盘中分钟",
    "intraday_realtime": "盘中实时", "intraday_tick": "盘中 tick", "nightly_financial": "夜间财务（22:00）",
    "weekend_calibration": "周末后校准（周一 03:00）", "weekend_backfill": "周末补漏（周一 02:00）",
    "daily_backfill": "每日补漏（17:00）", "news_slow": "慢速新闻（约 2h/轮）", "pre_market": "盘前（08:30）",
    "auction_highfreq": "集合竞价（09:15 起）", "intraday_sector": "盘中板块", "event_driven": "事件驱动（3min 轮询）",
    "integrity_check": "完整性巡检（23:00）", "catchup_guard": "错过补跑（05:30）",
}

# 时段 → cron（真源=schedule.yaml 动态加载，禁硬编码副本——2026-09-03 对账实证：
# 硬编码 catchup_guard 03:30 vs 真源 05:30 漂移 2 小时；6 段 cron（含秒）剥离秒位兼容 5 段计算）
def _load_schedule_crons() -> dict[str, str]:
    """schedule.yaml → {时段: 5段cron}；6 段（含秒）剥离秒位；读取失败返回空（下次调度显示空，不炸端点）。"""
    import yaml

    path = _REPO / "src" / "zephyr" / "data" / "config" / "schedule.yaml"
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        out: dict[str, str] = {}
        for name, cfg in (data.get("schedules") or {}).items():
            expr = str((cfg or {}).get("cron", "")).strip()
            if not expr:
                continue
            fields = expr.split()
            out[name] = " ".join(fields[-5:]) if len(fields) == 6 else expr
        return out
    except Exception:  # noqa: BLE001 — 真源读取失败降级空表，端点不炸
        return {}


_SCHEDULE_CRON = _load_schedule_crons()


def _next_cron_run(expr: str) -> str:
    """简化 5 段 cron 下次运行计算（支持 */n、数字、范围、*；够 schedule.yaml 全部 14 时段）。"""
    import datetime as _dt

    fields = expr.split()
    if len(fields) != 5:
        return ""
    min_f, hour_f, dom_f, mon_f, dow_f = fields

    def field_match(val: int, lo: int, hi: int, expr_f: str) -> bool:
        if expr_f == "*":
            return lo <= val <= hi
        if expr_f.startswith("*/"):
            try:
                step = int(expr_f[2:])
                return val % step == lo % step if step else False
            except ValueError:
                return False
        for part in expr_f.split(","):
            if "-" in part:
                a, b = part.split("-")
                if int(a) <= val <= int(b):
                    return True
            elif part.isdigit() and int(part) == val:
                return True
        return False

    base = _dt.datetime.now().replace(second=0, microsecond=0)
    for offset in range(1, 8 * 24 * 60):   # 最多向后扫 8 天
        t = base + _dt.timedelta(minutes=offset)
        # cron dow: 0=周日（项目用 0-4=周日~周四 交易周口径）
        if not field_match(t.minute, 0, 59, min_f):
            continue
        if not field_match(t.hour, 0, 23, hour_f):
            continue
        if dom_f != "*" and not field_match(t.day, 1, 31, dom_f):
            continue
        if mon_f != "*" and not field_match(t.month, 1, 12, mon_f):
            continue
        if dow_f != "*" and not field_match((t.weekday() + 1) % 7, 0, 6, dow_f):
            continue
        delta = t - base
        if delta.total_seconds() < 3600:
            return f"{(t-base).seconds//60} 分钟后（{t.strftime('%H:%M')}）"
        if delta.days >= 1:
            return f"{delta.days} 天后（{t.strftime('%m-%d %H:%M')}）"
        return f"{delta.seconds//3600} 小时后（{t.strftime('%H:%M')}）"
    return ""


def _load_tasks_meta() -> dict[str, dict[str, str]]:
    """tasks.yaml → {全表名: {source, schedule, schedule_zh, task_id}}（首任务为准；读取失败回退空）。"""
    import yaml
    try:
        p = _REPO / "src" / "zephyr" / "data" / "config" / "tasks.yaml"
        data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        meta: dict[str, dict[str, str]] = {}
        for t in data.get("tasks") or []:
            tbl = str(t.get("table") or "")
            if tbl and tbl not in meta:
                meta[tbl] = {
                    "source": str(t.get("source") or "?"),
                    "schedule": str(t.get("schedule") or ""),
                    "schedule_zh": _SCHEDULE_ZH.get(t.get("schedule"), str(t.get("schedule") or "")),
                    "task_id": str(t.get("task_id") or ""),
                }
        return meta
    except Exception:  # noqa: BLE001 — 配置读失败回退无映射
        return {}


def _vpn_on() -> bool:
    """VPN 当前是否开启（sing-box 常用本地端口探测）。"""
    for port in (10813, 10808, 7890):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.4):
                return True
        except OSError:
            continue
    return False


def _partition_range(earliest: str, latest: str) -> tuple[str, str]:
    """min/max partition 字符串 → 可读时间段；返回 (start_zh, end_zh)。真源=CH min/max partition。"""
    import re as _re

    fmt = lambda s: (lambda d: d[:4] + "-" + d[4:6] + ("-" + d[6:8] if len(d) >= 8 else ""))("".join(_re.findall(r"\d", s or ""))[:8])
    return fmt(earliest), fmt(latest)


def _dl_light(latest: str, table: str) -> tuple[str, int | None]:
    """按最新 partition 推算数据龄（天）→ 四态灯（启发式预期周期）。"""
    import datetime as _dt
    import re as _re

    if not latest or "tuple" in latest:
        return "gray", None
    digits = "".join(_re.findall(r"\d", latest))
    today = _dt.date.today()
    try:
        if len(digits) >= 8:
            d = _dt.date(int(digits[:4]), int(digits[4:6]), int(digits[6:8]))
        elif len(digits) >= 6:
            d = _dt.date(int(digits[:4]), int(digits[4:6]), 1)
        else:
            return "gray", None
    except ValueError:
        return "gray", None
    days = (today - d).days
    tl = table.lower()
    exp = next((v for keys, v in _DL_FREQ_HINT if any(k in tl for k in keys)), 45)
    if days <= exp:
        return "green", days
    if days <= exp * 3:
        return "yellow", days
    return "red", days


@app.get("/api/download-status")
def download_status() -> dict[str, Any]:
    """表级下载实况：三库全表（含空表灰灯）时间段/源/实时速率/VPN 联动——
    表状态真源=CH system.tables+parts；任务属性真源=tasks.yaml；时段真源=schedule.yaml 动态加载。"""
    import re as _re

    rows = _ch_exec(_SQL_TABLE_FRESH)
    tasks_meta = _load_tasks_meta()
    vpn = _vpn_on()

    # 近 15 分钟 INSERT 速率 + 今日新增（SQL 端 arrayJoin 提取目标表聚合——1.8 万行逐行拖 python 太重）
    # 注意：INSERT 的写入行数在 written_rows（rows 列=读取数恒 0，本机实证）
    ins: dict[str, dict[str, Any]] = {}
    today_rows: dict[str, int] = {}

    def _agg_inserts(sql: str) -> dict[str, int]:
        out: dict[str, int] = {}
        try:
            for target, w in _ch_exec(sql):
                tbl = str(target).split(".")[-1].strip("`").lower()
                out[tbl] = out.get(tbl, 0) + int(w or 0)
        except Exception as e:  # noqa: BLE001 — 速率真源失败降级（页面显示空，不炸端点）
            _ = e
        return out

    ins = {t.split(".")[-1].strip("`").lower(): w for t, w in _agg_inserts(
        "SELECT arrayJoin(extractAll(query, 'INSERT INTO [^ (]+')) AS target, "
        "sum(written_rows) AS w FROM system.query_log "
        "WHERE type='QueryFinish' AND positionCaseInsensitive(query, 'insert into') > 0 "
        "AND event_time > now()-900 GROUP BY target").items()}
    today_rows = {t.split(".")[-1].strip("`").lower(): w for t, w in _agg_inserts(
        "SELECT arrayJoin(extractAll(query, 'INSERT INTO [^ (]+')) AS target, "
        "sum(written_rows) AS w FROM system.query_log "
        "WHERE type='QueryFinish' AND positionCaseInsensitive(query, 'insert into') > 0 "
        "AND event_time >= today() GROUP BY target").items()}

    # 失败关联真源：failures/*.json 按 task_id/表名片段匹配到表（最近 50 条告警参与匹配）
    fail_dir = _REPO / "data" / "failures"
    table_fails: dict[str, dict[str, Any]] = {}
    fail_files = sorted(fail_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:50] if fail_dir.exists() else []
    all_fails: list[dict[str, Any]] = []
    for f in fail_files:
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
            all_fails.append({
                "task_id": str(d.get("task_id", "")), "source": str(d.get("source", "")),
                "level": str(d.get("level", "")), "error": str(d.get("error", "")),
                "ts": (d.get("timestamp") or f.stem)[:19].replace("T", " "),
                "tables": [str(v.get("table", "")) for v in (d.get("extra") or {}).get("violations", []) if isinstance(v, dict)],
            })
        except Exception:  # noqa: BLE001
            continue

    tables: list[dict[str, Any]] = []
    cnt = {"green": 0, "yellow": 0, "red": 0, "gray": 0}
    dl_now = 0
    for db, tbl, parts, nrows, earliest, latest in rows:
        tbl_s, db_s = str(tbl), str(db)
        full = f"{db_s}.{tbl_s}"
        latest_s = str(latest) if latest else ""
        light, days = _dl_light(latest_s, tbl_s)
        cnt[light] += 1
        meta = tasks_meta.get(full) or tasks_meta.get(tbl_s) or {}
        src = meta.get("source", "—")
        vpn_need, vpn_note = _SOURCE_VPN.get(src, ("—", ""))
        start_zh, end_zh = _partition_range(str(earliest) if earliest else "", str(latest) if latest else "")
        # 实时下载态：近 15 分钟有该表 INSERT → 绿"正在下载"；速率=rows/900s
        rt = ins.get(tbl_s)
        if rt:
            rate = round(rt / 900.0, 1)   # rt=近 15 分钟写入行数（int）
            state, dl_now = "downloading", dl_now + 1
            quality = "快" if rate > 100 else ("正常" if rate >= 1 else "零星")
        elif light == "red":
            state, rate, quality = "stalled", 0, "已断更"
        elif light == "yellow":
            state, rate, quality = "lagging", 0, "滞后"
        else:
            state, rate, quality = (
                ("未启动", 0, "空表待管道") if light == "gray" and not nrows
                else ("今日已完成", 0, "今日已完成") if light == "green" else ("待机", 0, "待机")
            )
        tables.append({
            "db": db_s, "table": tbl_s,
            "name_zh": _TABLE_ZH.get(tbl_s, ""),
            "parts": int(parts), "rows": int(nrows) if nrows else 0,
            "latest": latest_s[:40], "light": light, "days": days,
            "source": src, "schedule_zh": meta.get("schedule_zh", ""),
            "period": (f"{start_zh} ~ {end_zh}" if start_zh else "—"),
            "state": state, "rate": rate, "quality": quality,
            "vpn_need": vpn_need, "vpn_note": vpn_note,
            "today_rows": today_rows.get(tbl_s, 0),
            "next_dl": _next_cron_run(_SCHEDULE_CRON.get(meta.get("schedule", ""), "")) if meta.get("schedule") else "",
            "fail_cnt": 0, "fail_last": "",
        })
    # 失败关联回填：violations 表名 / task_id 片段匹配到表行
    for t in tables:
        tname = t["table"]
        hits = [a for a in all_fails
                if tname in a["tables"] or tname in a["task_id"].lower()
                or (a["source"] not in ("clickhouse", "internal") and a["source"] == t["source"] and a["level"] in ("ERROR", "CRITICAL"))]
        if hits:
            t["fail_cnt"] = len(hits)
            t["fail_last"] = f"{hits[0]['level']} {hits[0]['ts'][5:16]} {hits[0]['task_id'][:24]}"
    # F6（迁移台账 2026-09-09）：tick_data 今日新增按 data_source 分组（miniqmt/qmt_bridge
    # 两段并存展示）——9/18 miniqmt 停写后合计数字会 30 倍缩水，分组渲染防误读为断更
    for t in tables:
        if t["table"] == "tick_data":
            try:
                by_src = _ch_exec(
                    "SELECT data_source, count() FROM c1_market.tick_data "
                    "WHERE trade_date = today() GROUP BY data_source"
                )
                t["today_rows_by_source"] = {str(s): int(c) for s, c in by_src}
            except Exception:  # noqa: BLE001 — 分组明细降级（主数字不受影响）
                pass
    return {"ok": True, "tables": tables, "counts": cnt, "vpn_on": vpn,
            "dl_now": dl_now,
            "generated_at": datetime.now().isoformat(" ", "seconds")}


# ── 数据总览真源（Owner 2026-09-10：库内资产视角并入下载监管一表——宽度/深度/完整度/缺口/存储层）──
# 真源：列结构=system.columns；宽度/深度=每表一次列扫描聚合（uniq + min/max + groupUniqArray 交易日集合）；
#       缺口/完整度基准=c0_meta.trade_calendar；应有宽度=c0_meta.stock_list 最新清单（白名单表才展示，防误报不完整）；
#       存储层=三层冷热架构（docs/03_modules/_cross_layer/database/blueprint.md：热 Redis/常规 CH/冷 E 盘）。
# 重查询与 30s 下载监管轮询隔离：独立 Client + 后台线程；结果存内存缓存（10 分钟慢档自动重审 + 手动"深度体检"）。
_ASSET_DBS = ("c0_meta", "c1_market", "c3_fundamental")
_ASSET_TTL_SEC = 600            # 慢档自动重审周期（Owner 裁定：资产列 10 分钟级，下载列仍 30s）
_ASSET_HUGE_ROWS = 200_000_000  # 行数超阈值用 uniq 近似（亿级表 uniqExact 拖死审计；仪表盘容忍 ~1% 误差）
_ASSET_ASHARE_UNIVERSE = {      # "应有宽度=股票全历史清单"白名单（宇宙口径=全 A 含退市的表才展示应有，子宇宙表列入必误红）
    "kline_daily", "kline_daily_hfq", "kline_weekly", "kline_weekly_hfq", "kline_monthly",
    "kline_monthly_hfq", "stk_limit", "technical_indicator", "stock_indicator", "daily_valuation",
}
# 日期列候选（按优先级命中第一个；真实 schema 2026-09-10 盘点：trade_date 89 表主导，
# 日历真身在 c1_market.trade_calendar 且列=cal_date，新闻=publish_time，情绪窗=window_date，财务=announce_date）
_ASSET_DATE_CANDIDATES = ("trade_date", "date", "cal_date", "publish_time", "window_ts",
                          "window_date", "announce_date", "ex_date", "report_date", "timestamp",
                          "snapshot_time", "list_date")
_ASSET_CAL_SKIP = ("us_", "global", "futures", "hog", "a50", "weather", "macro", "edb")
# ↑ 交易日历不跟随 A 股的表（美股/全球/期货/生猪现货/A50/天气/宏观）——按 A 股日历算完整度必出伪缺口
_ASSET_TIER_OVERRIDES: dict[str, str] = {}   # 表名→tier；冷层启用迁表后在此登记（对齐 storage_tiering Tier；中文映射在前端）
_asset_state: dict[str, Any] = {"running": False, "done": 0, "total": 0, "audited_at": "", "ts": 0.0,
                                "error": "", "tables": {}}
_asset_lock = threading.Lock()
_asset_thread: threading.Thread | None = None


def _asset_audit_client() -> Client:
    """审计专用 Client（独立连接，不与 _ch_exec 全局锁争用——审计查询秒级~分钟级，不能饿死 30s 轮询端点）。"""
    cfg = load_ch_config()
    return Client(
        host=cfg["host"], port=int(cfg.get("port", 9000)),
        user=cfg.get("reader_user") or cfg.get("user", "default"),
        password=cfg.get("reader_password") or cfg.get("password", ""),
        database=cfg.get("database", "c1_market"),
        connect_timeout=3, send_receive_timeout=180,
    )


def _asset_run_audit() -> None:
    """库内资产审计（后台线程）：列结构→每表一次列扫描聚合→交易日历对齐→内存缓存渐进更新。

    口径（Owner 2026-09-10 裁定）：
    - 宽度=表内 distinct symbol（应有=股票全历史清单，仅全宇宙白名单表展示应有数）
    - 深度=min~max 日期列实际值（非分区粒度，精确到日）
    - 完整度/缺口=实际出现交易日 ∩ trade_calendar 在 [min,max] 区间的基准（占比 ≥90% 才按交易日口径算，
      新闻等 7×24 表不算缺口防误报）
    - 空表不跑重查询（width=0，深度空）
    """
    cli = _asset_audit_client()
    cols = cli.execute(
        "SELECT database, table, name, type FROM system.columns "
        "WHERE database IN ('c0_meta','c1_market','c3_fundamental')")
    tmap: dict[tuple[str, str], dict[str, Any]] = {}
    for d, t, name, ty in cols:
        e = tmap.setdefault((str(d), str(t)), {})
        nl, tl = str(name).lower(), str(ty)
        if nl == "symbol" and "symbol_col" not in e:
            e["symbol_col"] = str(name)
        if nl in _ASSET_DATE_CANDIDATES and ("Date" in tl or "String" in tl):
            pri = _ASSET_DATE_CANDIDATES.index(nl)
            if "date_pri" not in e or pri < e["date_pri"]:
                e["date_col"], e["date_ty"], e["date_pri"] = str(name), tl, pri
    sizes: dict[tuple[str, str], int] = {}
    for d, t, n in cli.execute(
            "SELECT database, table, sum(rows) FROM system.parts WHERE active "
            "AND database IN ('c0_meta','c1_market','c3_fundamental') GROUP BY database, table"):
        sizes[(str(d), str(t))] = int(n or 0)

    # 交易日历基准（缺口真源）：主=c1_market.trade_calendar（A股）；港=c1_market.hk_trade_calendar——
    # 港股族假期与 A 股不同，按 A 股日历算必出伪缺口（hk_connect_flow 实证 110 天伪缺口）
    def _load_cal(dbtbl: str) -> set[str]:
        tcols = {str(n) for d, t, n, _ in cols if d == "c1_market" and t == dbtbl}
        if "cal_date" not in tcols:
            return set()
        where = "WHERE is_open = 1" if "is_open" in tcols else ""
        try:
            return {str(r[0])[:10] for r in cli.execute(
                f"SELECT DISTINCT cal_date FROM c1_market.{dbtbl} {where}")}
        except Exception:  # noqa: BLE001 — 日历缺失降级：无缺口/完整度（宽度/深度不受影响）
            return set()

    cal_a = _load_cal("trade_calendar")
    cal_hk = _load_cal("hk_trade_calendar")

    # 应有宽度真源：股票全历史清单（含退市，c1_market.stock_list 是 PIT 清单无 trade_date——
    # list_status 全空不可用，全历史 uniq 与 kline_daily 含退市口径对齐：5906/5921≈99.7% 实证）
    expected_w: int | None = None
    try:
        sl_cols = {str(n) for d, t, n, _ in cols if d == "c1_market" and t == "stock_list"}
        if "symbol" in sl_cols:
            expected_w = int(cli.execute("SELECT uniqExact(symbol) FROM c1_market.stock_list")[0][0])
    except Exception:  # noqa: BLE001 — 应有宇宙取不到降级：白名单表也不展示应有数
        expected_w = None

    keys = sorted(tmap)
    with _asset_lock:
        _asset_state["total"] = len(keys)
        _asset_state["done"] = 0
        _asset_state["running"] = True
        _asset_state["error"] = ""
    tables_out: dict[str, dict[str, Any]] = {}
    for db, tbl in keys:
        e = tmap[(db, tbl)]
        rec: dict[str, Any] = {"width": None, "expected_width": None, "dmin": "", "dmax": "",
                               "days": None, "completeness": None, "gap_days": None,
                               "tier": _ASSET_TIER_OVERRIDES.get(tbl, "warm"), "err": ""}
        dc, sc, dty = e.get("date_col"), e.get("symbol_col"), e.get("date_ty", "")
        tbl_low = tbl.lower()
        if any(s in tbl_low for s in _ASSET_CAL_SKIP):
            tbl_cal: set[str] = set()          # 日历不跟 A 股的表：不算缺口口径
        elif "hk" in tbl_low:
            # 陆港通资金流交易日=两地共同开市日（内地假期北向关闭，纯港股日历仍伪缺口——实证 137 天）
            tbl_cal = (cal_a & cal_hk) if "connect" in tbl_low else cal_hk
        else:
            tbl_cal = cal_a
        if dc or sc:
            n = sizes.get((db, tbl), 0)
            if n == 0:
                rec["width"] = 0 if sc else None   # 空表免重查询
            else:
                u = "uniq" if n > _ASSET_HUGE_ROWS else "uniqExact"
                sels: list[str] = []
                if sc:
                    sels.append(f"{u}({sc})")
                if dc:
                    dstr = "String" in dty
                    # 1970-01-01=CH Date 零值脏行（list_date/announce_date 族实证），排除防深度伪起点
                    zero = "'1970-01-01'" if dstr else "toDate('1970-01-01')"
                    cond = f"{dc} != {zero}"
                    dfn = f"substring({dc}, 1, 10)" if dstr else f"toDate({dc})"
                    sels += [f"minIf({dc}, {cond})", f"maxIf({dc}, {cond})", f"groupUniqArrayIf({dfn}, {cond})"]
                try:
                    row = cli.execute(f"SELECT {', '.join(sels)} FROM {db}.{tbl}")[0]
                    i = 0
                    if sc:
                        rec["width"] = int(row[i] or 0)
                        i += 1
                    if dc:
                        rec["dmin"] = str(row[i])[:10] if row[i] is not None else ""     # Nullable 列全 NULL 兜底
                        rec["dmax"] = str(row[i + 1])[:10] if row[i + 1] is not None else ""
                        dates = {str(x)[:10] for x in (row[i + 2] or [])}
                        rec["days"] = len(dates)
                        if not dates:   # 全零值日期表（etf_list/index_list 实证）：CH 聚合默认值 1970 兜底清空
                            rec["dmin"] = rec["dmax"] = ""
                        # 完整度/缺口仅日频族（trade_date/date/cal_date）适用——事件型列（announce_date/
                        # list_date/publish_time…）天然稀疏，按交易日全覆盖算必出伪缺口
                        span = {x for x in tbl_cal if rec["dmin"] <= x <= rec["dmax"]}
                        if span and dates and str(dc).lower() in ("trade_date", "date", "cal_date"):
                            inter = dates & span
                            if len(inter) / len(dates) >= 0.9:   # 排他防伪：7×24 混合表不算缺口
                                rec["completeness"] = round(len(inter) / len(span) * 100, 1)
                                rec["gap_days"] = max(0, len(span) - len(inter))
                except Exception:  # noqa: BLE001 — 单表审计失败降级"未测"，不炸全局
                    rec["err"] = "查询失败"
        if tbl in _ASSET_ASHARE_UNIVERSE and expected_w:
            rec["expected_width"] = expected_w
        tables_out[f"{db}.{tbl}"] = rec
        with _asset_lock:   # 渐进更新：前端 60s 轮询可见体检进度（done/total）
            _asset_state["done"] = len(tables_out)
            _asset_state["tables"] = dict(tables_out)
    with _asset_lock:
        _asset_state["running"] = False
        _asset_state["audited_at"] = datetime.now().isoformat(" ", "seconds")
        _asset_state["ts"] = time.time()


def _asset_maybe_start(force: bool) -> dict[str, Any]:
    """审计启动器：手动体检（force）或缓存超龄（10 分钟慢档）后台重审；进行中直接返回现状。"""
    global _asset_thread
    with _asset_lock:
        st = {k: (dict(v) if k == "tables" else v) for k, v in _asset_state.items()}
    if _asset_thread is not None and _asset_thread.is_alive():
        return st
    stale = (not st["ts"]) or (time.time() - st["ts"] > _ASSET_TTL_SEC)
    if not (force or stale):
        return st

    def _run() -> None:
        try:
            _asset_run_audit()
        except Exception as e:  # noqa: BLE001 — 审计线程兜底：失败标记非运行中，端点不炸
            logger.warning("data-asset audit failed: %s", e)
            with _asset_lock:
                _asset_state["running"] = False
                _asset_state["error"] = str(e)[:200]

    with _asset_lock:
        if _asset_thread is not None and _asset_thread.is_alive():
            return st
        _asset_thread = threading.Thread(target=_run, daemon=True, name="data-asset-audit")
        _asset_thread.start()
    return st


@app.get("/api/data-asset")
def data_asset(refresh: int = 0) -> dict[str, Any]:
    """库内资产总览（与下载监管同表合并展示）：宽度/深度/完整度/缺口/存储层。
    内存缓存秒回；超龄（>10 分钟）或 refresh=1 时后台重审（独立 Client 线程，不饿死 30s 轮询端点）。"""
    st = _asset_maybe_start(bool(refresh))
    st["ok"] = True
    return st


# ── 交易通道监控（Owner 2026-09-04：HTTP 桥独立监护页——量化系统主动脉）──────
# 真源：HTTP 桥 GET /health（EXEC v16.4 沙箱内 18901）+ 实测下单延迟（HTTP vs miniqmt 探针）
# + 桥文件族活性（orders/ack/quote/Stock CSV）+ 柜台挂单/成交 CSV 回报


def _bridge_http_health() -> dict[str, Any]:
    """探活沙箱 EXEC HTTP 桥（18901）：连接+GET /health 计数器。"""
    import socket as _sock

    t0 = time.time()
    try:
        with _sock.create_connection(("127.0.0.1", 18901), timeout=2.0) as s:
            s.sendall(b"GET /health HTTP/1.0\r\n\r\n")
            buf = b""
            while b"\r\n\r\n" not in buf:
                c = s.recv(4096)
                if not c:
                    return {"alive": False, "detail": "连接后静默关闭", "ms": round((time.time() - t0) * 1000)}
                buf += c
            body = buf.decode("utf-8", "ignore").split("\r\n\r\n", 1)[-1]
            stats: dict[str, str] = {}
            for kv in body.split():
                if "=" in kv:
                    k, v = kv.split("=", 1)
                    stats[k] = v
            return {"alive": True, "detail": body, "stats": stats,
                    "ms": round((time.time() - t0) * 1000)}
    except OSError as e:
        return {"alive": False, "detail": str(e)[:60], "ms": round((time.time() - t0) * 1000)}


def _bridge_file_fresh() -> list[dict[str, Any]]:
    """桥文件族活性（orders/ack/quote/deals_events + Stock 族 CSV）。"""
    checks = [
        ("指令文件", "E:\\qmt_bridge_sim\\orders_sim.csv"),
        ("回执文件", "E:\\qmt_bridge_sim\\ack_sim.csv"),
        ("行情流", "E:\\qmt_bridge_sim\\quote.csv"),
        ("成交事件", "E:\\ZephyrAlpha\\deals_events.txt"),
        ("持仓导出", "E:\\qmt_bridge_sim\\Stock\\PositionStatics.csv"),
        ("成交导出", "E:\\qmt_bridge_sim\\Stock\\Deal.csv"),
    ]
    out = []
    for name, path in checks:
        p = Path(path)
        if not p.exists():
            out.append({"name": name, "light": "red", "detail": "文件不存在"})
            continue
        age_s = time.time() - p.stat().st_mtime
        if age_s < 60:
            light, detail = "green", f"{round(age_s)}s 前更新"
        elif age_s < 3600:
            light, detail = "yellow", f"{round(age_s/60)} 分钟前"
        else:
            light, detail = "gray", f"{round(age_s/3600)} 小时前"
        out.append({"name": name, "light": light, "detail": detail})
    return out


@app.get("/api/bridge-status")
def bridge_status() -> dict[str, Any]:
    """交易通道监控真源：HTTP 桥全环节健康 + 双通道延迟对比 + miniqmt 退役倒计时。"""
    http = _bridge_http_health()
    files = _bridge_file_fresh()
    # miniqmt 存活（9/16 退役倒计时——退役前它是对比基线）
    import socket as _sock

    mini_alive = False
    try:
        # xtdata 快照通道（58610 由 QMT 客户端起）非严格判定，用进程特征兜底
        import subprocess as _sp

        r = _sp.run(["tasklist", "/FI", "IMAGENAME eq XtMiniQmt.exe"], capture_output=True, text=True, timeout=5)
        mini_alive = "XtMiniQmt.exe" in (r.stdout or "")
    except Exception:  # noqa: BLE001
        mini_alive = False
    return {
        "ok": True,
        "http": http,
        "files": files,
        "mini_alive": mini_alive,
        "retire_date": "2026-09-18",
        "generated_at": datetime.now().isoformat(" ", "seconds"),
    }


_TDM_CACHE: dict[str, Any] = {}   # /api/tdm mtime 缓存（改 YAML 即失效重算）
_TDM_REFNAMES: dict[str, Any] = {"built_at": 0.0, "names": {}}
_TDM_REFNAMES_TTL = 600.0   # 引用中文名缓存 10 分钟（注册表低频变更，无需逐请求重扫）
_TDM_REFDESCS: dict[str, Any] = {"built_at": 0.0, "descs": {}}   # 引用 id → 大白话机制（算法锚分区，b20260910）


def _tdm_ref_names_algo(names: dict[str, str]) -> None:
    """DAL/ML 算法锚中文名补源（b20260910）——独立助手：_tdm_ref_names 复杂度已近阈，
    加载分支拆出防 NO-HIGH-COMPLEXITY。"""
    import yaml as _yaml

    def _load(fname: str) -> Any:
        return _yaml.safe_load((_REPO / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / fname).read_text(encoding="utf-8"))

    reg = _load("decision_algo_registry.yaml")
    for x in reg.get("algorithms", []):
        if x.get("dal_id"):
            names[x["dal_id"]] = x.get("name_zh") or ""
    reg = _load("model_registry.yaml")
    for x in reg.get("models", []):
        if x.get("model_id"):
            names[x["model_id"]] = x.get("name_zh") or ""


def _tdm_ref_names() -> dict[str, str]:
    """八轴引用+策略挂载+模块锚 → 中文名映射（翻译真源关联，抽屉溯源用）。

    数据源=各 registry YAML（factor/strategy/data_asset/technical_indicator/
    execution_algo/risk_limit/alert_threshold/event_calendar/cost_model）；
    MOD-* 走"py 头 [A_module] module_id → 文件路径 → module_translation_registry
    name_zh"链。未命中返回空（前端回退显示编号原文）。
    """
    now = time.time()
    if now - _TDM_REFNAMES["built_at"] < _TDM_REFNAMES_TTL and _TDM_REFNAMES["names"]:
        return _TDM_REFNAMES["names"]
    import yaml as _yaml   # 延迟导入（与 tdm_map 同款，启动不加重）

    names: dict[str, str] = {}

    def _load(fname: str) -> Any:
        return _yaml.safe_load((_REPO / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / fname).read_text(encoding="utf-8"))

    try:
        reg = _load("data_asset_registry.yaml")
        for x in reg.get("datasets", []):
            if x.get("dataset_id"):
                names[x["dataset_id"]] = x.get("name_zh") or x.get("entity_name") or ""
        reg = _load("factor_registry.yaml")
        for x in reg.get("factors", []):
            if x.get("factor_id"):
                names[x["factor_id"]] = x.get("name_zh") or x.get("name") or ""
        reg = _load("strategy_registry.yaml")
        for x in reg.get("strategies", []):
            zh = x.get("name_zh") or x.get("name") or ""
            if x.get("strategy_id"):
                names[x["strategy_id"]] = zh
            for a in (x.get("aliases") or []):   # sleeve/别名挂载（daban-sleeve 等）也能翻出中文名
                names.setdefault(a, zh)
        reg = _load("technical_indicator_registry.yaml")
        for x in reg.get("indicators", []):
            if x.get("indicator_id"):
                names[x["indicator_id"]] = x.get("name_zh") or x.get("name") or ""
        reg = _load("execution_algo_registry.yaml")
        for x in reg.get("execution_algos", []):
            if x.get("execution_algo_id"):
                names[x["execution_algo_id"]] = x.get("name_zh") or x.get("name") or ""
        reg = _load("risk_limit_registry.yaml")
        for x in reg.get("risk_limits", []):
            if x.get("risk_limit_id"):
                names[x["risk_limit_id"]] = x.get("name_zh") or x.get("name") or ""
        reg = _load("alert_threshold_registry.yaml")
        for x in reg.get("thresholds", []):
            if x.get("threshold_id"):
                names[x["threshold_id"]] = x.get("name_zh") or x.get("name") or ""
        reg = _load("event_calendar_registry.yaml")
        for x in reg.get("event_types", []):
            if x.get("event_type_id"):
                names[x["event_type_id"]] = x.get("name_zh") or x.get("name") or ""
        reg = _load("cost_model_registry.yaml")
        for x in reg.get("cost_models", []):
            if x.get("cost_model_id"):
                names[x["cost_model_id"]] = x.get("name_zh") or x.get("name") or ""
        _tdm_ref_names_algo(names)   # DAL/ML 算法锚补翻译源（b20260910，复杂度拆 helper）
    except Exception as exc:   # 注册表缺失/损坏不阻断地图本体——中文名降级为编号原文
        logger.warning("tdm ref_names registry load failed: %s", exc)

    # MOD-* 中文名：py 头 [A_module] module_id → 路径 → module_translation_registry
    try:
        import re as _re
        mt = _load("module_translation_registry.yaml")
        path2zh = {e.get("module_path"): (e.get("name_zh") or "") for e in mt.get("entries", []) if isinstance(e, dict)}
        pat = _re.compile(r"\[A_module\]\s*module_id=(MOD-[A-Za-z0-9-]+)")
        src_root = _REPO / "src"
        for py in src_root.rglob("*.py"):
            try:
                head = py.read_text(encoding="utf-8", errors="ignore")[:4000]
            except OSError:
                continue
            m = pat.search(head)
            if not m:
                continue
            rel = py.relative_to(_REPO).as_posix()
            zh = path2zh.get(rel, "")
            if zh:
                names.setdefault(m.group(1), zh)
    except Exception as exc:
        logger.warning("tdm ref_names MOD scan failed: %s", exc)

    _TDM_REFNAMES["built_at"] = now
    _TDM_REFNAMES["names"] = names
    return names


def _tdm_ref_descs_dal_ml(descs: dict[str, str]) -> None:
    """DAL/ML 大白话聚合（mechanism_zh / task+architecture）。"""
    import yaml as _yaml

    def _load(fname: str) -> Any:
        return _yaml.safe_load((_REPO / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / fname).read_text(encoding="utf-8"))

    reg = _load("decision_algo_registry.yaml")
    for x in reg.get("algorithms", []):
        if x.get("dal_id") and x.get("mechanism_zh"):
            descs[x["dal_id"]] = str(x["mechanism_zh"]).replace("\n", " ").strip()
    reg = _load("model_registry.yaml")
    for x in reg.get("models", []):
        if x.get("model_id"):
            parts = [str(p).strip() for p in (x.get("task"), x.get("architecture")) if p]
            if parts:
                descs[x["model_id"]] = "；".join(parts)


def _tdm_ref_descs_exa_ind(descs: dict[str, str]) -> None:
    """EXA/IND 大白话聚合（name_zh+适用场景 / name_zh 兜底）。"""
    import yaml as _yaml

    def _load(fname: str) -> Any:
        return _yaml.safe_load((_REPO / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / fname).read_text(encoding="utf-8"))

    reg = _load("execution_algo_registry.yaml")
    for x in reg.get("execution_algos", []):
        if x.get("execution_algo_id"):
            scene = str(x.get("applicable_scenario") or "").split("；")[0].split("\n")[0].strip()
            descs[x["execution_algo_id"]] = (x.get("name_zh") or "") + (("；适用：" + scene) if scene else "")
    reg = _load("technical_indicator_registry.yaml")
    for x in reg.get("indicators", []):
        if x.get("indicator_id"):
            descs.setdefault(x["indicator_id"], x.get("name_zh") or "")


def _tdm_ref_descs() -> dict[str, str]:
    """算法/模型引用 id → 大白话机制（算法锚分区展示用，b20260910）。

    真源=各 registry 既有字段聚合，零硬编码翻译：DAL←mechanism_zh；
    ML←task+architecture；EXA←name_zh+applicable_scenario；IND←name_zh 兜底。
    未命中返回空（前端回退「未登记喂给说明」站位）。聚合分支拆 helper 防复杂度超阈。
    """
    now = now_utc().timestamp()
    if now - _TDM_REFDESCS["built_at"] < _TDM_REFNAMES_TTL and _TDM_REFDESCS["descs"]:
        return _TDM_REFDESCS["descs"]
    descs: dict[str, str] = {}
    try:
        _tdm_ref_descs_dal_ml(descs)
        _tdm_ref_descs_exa_ind(descs)
    except Exception as exc:   # 注册表缺失/损坏不阻断地图本体——大白话降级为空（前端站位兜底）
        logger.warning("tdm ref_descs registry load failed: %s", exc)
    _TDM_REFDESCS["built_at"] = now
    _TDM_REFDESCS["descs"] = descs
    return descs


@app.get("/api/tdm")
def tdm_map() -> dict[str, Any]:
    """交易决策地图全量（前端原生实时渲染真源）——真源=config/trading_decision_map.yaml。

    每请求按 mtime 缓存（改 YAML 即自动生效，无需重生成/重启）；payload=
    nodes（含 algo_note_zh 大白话机制+node_comments 设计备注原文）+ edges + meta。
    消费者=web/pages/tdm.html（横向树状图），Owner 2026-09-07 裁定。
    """
    p = _REPO / "config" / "trading_decision_map.yaml"
    mtime = p.stat().st_mtime
    cached = _TDM_CACHE.get("mtime")
    if cached == mtime and _TDM_CACHE.get("payload"):
        return _TDM_CACHE["payload"]

    import re as _re

    import yaml as _yaml

    raw = _yaml.safe_load(p.read_text(encoding="utf-8"))
    # 注释提取（D 螺定原文/欠账登记——抽屉"设计备注"真源）：块内归本节点，悬空前导归下一节点
    lines = p.read_text(encoding="utf-8").split("\n")
    try:
        start = next(i for i, l in enumerate(lines) if l.rstrip() == "nodes:")
    except StopIteration:
        start = 0
    end = start + 1
    while end < len(lines) and (lines[end].startswith(" ") or not lines[end].strip()):
        end += 1
    region = lines[start + 1 : end]

    def _is_node(s: str) -> bool:
        return s.startswith("  - node_id:")

    def _meaningful(s: str) -> bool:
        return bool(s.strip()) and not s.lstrip().startswith("#")

    after = [False] * len(region)
    flag = False
    for i in range(len(region) - 1, -1, -1):
        after[i] = flag
        if _meaningful(region[i]):
            flag = _is_node(region[i])

    comments: dict[str, list[str]] = {}
    pending: list[str] = []
    cur: str | None = None
    for i, ln in enumerate(region):
        if _is_node(ln):
            cur = ln.split(":", 1)[1].strip()
            comments[cur] = pending
            pending = []
        elif ln.lstrip().startswith("#"):
            txt = ln.strip()[1:].strip()
            if not txt or _re.fullmatch(r"[-─=═\s]+", txt):
                continue
            if cur is not None and not after[i]:
                comments[cur].append(txt)
            else:
                pending.append(txt)

    nodes_out = []
    for n in raw.get("nodes", []):
        nid = n.get("node_id", "")
        note = str(n.get("algo_note_zh") or "").replace("\n", " ").strip()
        while "。 " in note:
            note = note.replace("。 ", "。")
        nodes_out.append({
            "id": nid,
            "name": n.get("name_zh", ""),
            "q": n.get("decision_question", ""),
            "note": note,
            "layer": n.get("layer"),
            "flow": n.get("flow"),
            "parent": n.get("parent_node"),
            "point": n.get("point"),
            "activation": n.get("activation"),
            "invalidation": n.get("invalidation"),
            "autonomy": n.get("ai_autonomy"),
            "fallback": n.get("fallback"),
            "module_ref": n.get("module_ref"),
            "module_id": n.get("module_id"),
            "mounts": [m.get("strategy_ref") if isinstance(m, dict) else str(m)
                       for m in (n.get("strategy_mounts") or [])],
            "refs": {k: n.get(k) or [] for k in (
                "factor_refs", "data_refs", "cost_model_refs", "risk_limit_refs",
                "threshold_refs", "event_refs", "algo_refs") if n.get(k)},
            "comments": comments.get(nid, []),
        })
    payload = {
        "ok": True,
        "map_id": raw.get("map_id"),
        "name_zh": raw.get("name_zh"),
        "nodes": nodes_out,
        "edges": raw.get("edges", []),
        "ref_names": _tdm_ref_names(),   # 引用 id → 中文名（八轴+STR 别名+MOD，抽屉溯源真源关联）
        "ref_descs": _tdm_ref_descs(),   # 算法/模型 id → 大白话机制（算法锚分区，b20260910）
        "generated_at": datetime.now().isoformat(" ", "seconds"),
    }
    _TDM_CACHE["mtime"] = mtime
    _TDM_CACHE["payload"] = payload
    return payload


@app.get("/api/tdm/validation")
def tdm_validation(node_id: str = "") -> dict[str, Any]:
    """节点验证台账（只读，零写副作用）——真源=c1_backtest.node_verdict（PB-04，P0-3）。

    返回该节点最近 20 条验证记录 + 当前 verdict（verdict_at 最新一条）；
    空表/无记录 = 200 + ok:true + verdict=untested（未验证态，前端灰徽章）；
    CH 不可达 = 200 + ok:false + reason（前端显示"台账不可达"，不冒充未验证）。
    消费者 = web/features/tdm.js drawer()「验证档案」区。
    """
    nid = (node_id or "").strip()
    if not nid:
        return {"ok": False, "reason": "node_id required", "node_id": "", "verdict": "untested", "records": []}
    sql = (
        "SELECT run_id, snapshot_commit, window_start, window_end, validation_method,"
        " triggers, hit_ratio, significance, verdict, verdict_at, notes"
        " FROM c1_backtest.node_verdict WHERE node_id = %(nid)s"
        " ORDER BY verdict_at DESC, window_end DESC LIMIT 20"
    )
    try:
        rows = _ch_exec(sql, {"nid": nid})
    except Exception as exc:   # 台账不可达不阻断抽屉——降级披露，不冒充"未验证"
        logger.warning("tdm validation query failed for %s: %s", nid, exc)
        return {"ok": False, "reason": f"台账不可达: {exc}", "node_id": nid, "verdict": "untested", "records": []}

    def _fmt_d(d: Any) -> str:
        return d.strftime("%Y-%m-%d") if d else ""

    def _fmt_ts(d: Any) -> str:
        return d.strftime("%Y-%m-%d %H:%M") if d else ""

    records = [
        {
            "run_id": r[0],
            "snapshot_commit": r[1],
            "window_start": _fmt_d(r[2]),
            "window_end": _fmt_d(r[3]),
            "validation_method": r[4],
            "triggers": r[5],
            "hit_ratio": r[6],
            "significance": r[7],
            "verdict": r[8],
            "verdict_at": _fmt_ts(r[9]),
            "notes": r[10],
        }
        for r in rows
    ]
    return {
        "ok": True,
        "node_id": nid,
        "verdict": records[0]["verdict"] if records else "untested",
        "records": records,
        "record_count": len(records),
    }



@app.get("/api/tdm/verdicts")
def tdm_verdicts() -> dict[str, Any]:
    """全节点当前验证态地图（只读）——画布噪音/衰减徽章数据源（PB-03，P2-2）。

    每节点取 verdict_at 最新一行的 verdict；空表/无记录=ok:true+空 map（画布无徽章）。
    消费者=web/features/tdm.js render()（节点卡片灰色系噪音/衰减标记）。
    """
    sql = (
        "SELECT node_id, verdict, toString(verdict_at)"
        " FROM c1_backtest.node_verdict ORDER BY verdict_at DESC, window_end DESC"
    )
    try:
        rows = _ch_exec(sql)
    except Exception as exc:   # 台账不可达→空 map，画布降级无徽章（不阻断地图渲染）
        logger.warning("tdm verdicts query failed: %s", exc)
        return {"ok": True, "verdicts": {}, "degraded": True}
    verdicts: dict[str, dict[str, str]] = {}
    for node_id, verdict, verdict_at in rows:
        if node_id and node_id not in verdicts:
            verdicts[node_id] = {"verdict": verdict, "verdict_at": verdict_at}
    return {"ok": True, "verdicts": verdicts, "count": len(verdicts)}


# ═══════════════ 产业地图 chainmap（真源 ig_* 七表，depgraph PG 只读；Owner 2026-09-08 三层缩放方案） ═══════════════

_CM_GALAXY_CACHE: dict[str, Any] = {"data": None, "ts": 0.0}          # L1 星系（TTL 600s，数据扩建期日级刷新足够）
_CM_CLUSTER_CACHE: dict[str, dict[str, Any]] = {}                     # L2 簇详情（随 galaxy 失联失效）
_CM_NAME_CACHE: dict[str, Any] = {"map": None, "ts": 0.0}             # symbol→公司名映射（ig_company_edge 名称列，覆盖不全如实用）
_CM_NAME_OVERRIDE_PATH = _REPO / "config" / "chainmap_cluster_names.yaml"   # L1 族名 override（Commit C 规则版，mtime 缓存改 YAML 即生效）
_CM_NAME_OVERRIDE: dict[str, Any] = {"mtime": None, "map": {}}

# tier → 列位分桶（列序=产业链流向 上游→中游→下游）
_CM_TIER_COL: dict[str, str] = {}
for _t in ("上游", "原材料", "材料"):
    _CM_TIER_COL[_t] = "上游"
for _t in ("中游", "设备", "零部件", "制造", "加工"):
    _CM_TIER_COL[_t] = "中游"
for _t in ("下游", "应用", "终端", "运营", "品牌"):
    _CM_TIER_COL[_t] = "下游"
_CM_COL_ORDER = ["上游", "中游", "下游", "其他", "通用"]


def _cm_name_override() -> dict[str, str]:
    """L1 族名 override（config/chainmap_cluster_names.yaml，mtime 缓存；未列出=自动族名）。"""
    try:
        mtime = _CM_NAME_OVERRIDE_PATH.stat().st_mtime
    except OSError:
        mtime = None
    if mtime != _CM_NAME_OVERRIDE["mtime"]:
        m: dict[str, str] = {}
        if mtime is not None:
            try:
                import yaml

                raw = yaml.safe_load(_CM_NAME_OVERRIDE_PATH.read_text(encoding="utf-8")) or {}
                if isinstance(raw, dict):
                    m = {str(k): str(v).strip() for k, v in raw.items()
                         if str(v).strip() and not str(k).startswith("#")}
            except Exception as exc:
                logger.warning("chainmap name override 解析失败（沿用自动族名）: %s", exc)
        _CM_NAME_OVERRIDE["mtime"] = mtime
        _CM_NAME_OVERRIDE["map"] = m
    return _CM_NAME_OVERRIDE["map"]


def _cm_col(tier: str | None) -> str:
    t = (tier or "").strip()
    if not t or t == "unspecified":
        return "通用"
    return _CM_TIER_COL.get(t, "其他")


def _cm_pg() -> Any:
    """depgraph PG 只读连接（depgraph_reader 角色，零写副作用）。"""
    from zephyr.governance.depgraph_schema import get_depgraph_pg_connection

    return get_depgraph_pg_connection()


def _cm_role_rank(role: str | None) -> int:
    r = (role or "").strip()
    if "龙头" in r or r == "核心":
        return 0
    if r == "参与":
        return 1
    return 2   # mentioned/未知殿后


def _cm_build_galaxy() -> dict[str, Any]:
    """链→族聚类：跨链结构边+公司供应链边投影到链对 → 确定性模块度局部移动（Louvain 式单层，γ=3.5）→ 小簇并入最强邻居（≤48 簇）。

    纯 Python 无新依赖；簇名=簇内连接度最高的枢纽链名。结果缓存 600s。
    """
    conn = _cm_pg()
    try:
        cur = conn.cursor()
        cur.execute("SELECT chain_id, name FROM ig_chain WHERE status = 'active'")
        chain_name: dict[str, str] = {r[0]: r[1] for r in cur.fetchall()}
        cur.execute("SELECT node_id, chain_id FROM ig_node")
        node_chain: dict[str, str] = {r[0]: r[1] for r in cur.fetchall()}
        cur.execute("SELECT node_id, count(DISTINCT symbol) FROM ig_node_company WHERE valid_to IS NULL GROUP BY node_id")
        node_companies: dict[str, int] = {r[0]: int(r[1]) for r in cur.fetchall()}
        cur.execute("SELECT DISTINCT node_id, symbol FROM ig_node_company WHERE valid_to IS NULL")
        sym_chains: dict[str, set[str]] = {}
        for nid, sym in cur.fetchall():
            c = node_chain.get(nid)
            if c:
                sym_chains.setdefault(sym, set()).add(c)
        cur.execute("SELECT from_node, to_node FROM ig_edge")
        pair_w: dict[tuple[str, str], float] = {}
        for a, b in cur.fetchall():
            c1, c2 = node_chain.get(a), node_chain.get(b)
            if c1 in chain_name and c2 in chain_name and c1 != c2:
                key = (c1, c2) if c1 < c2 else (c2, c1)
                pair_w[key] = pair_w.get(key, 0.0) + 1.0
        cur.execute("SELECT DISTINCT from_symbol, to_symbol FROM ig_company_edge WHERE valid_to IS NULL")
        for s1, s2 in cur.fetchall():
            for c1 in sym_chains.get(s1, ()):
                for c2 in sym_chains.get(s2, ()):
                    if c1 in chain_name and c2 in chain_name and c1 != c2:
                        key = (c1, c2) if c1 < c2 else (c2, c1)
                        pair_w[key] = pair_w.get(key, 0.0) + 1.0
        conn.close()
    except Exception:
        try:
            conn.close()
        except Exception:
            pass
        raise

    # 链级邻接（无任何跨链边的孤立链各自成簇）
    adj: dict[str, list[tuple[str, float]]] = {c: [] for c in chain_name}
    nbr_w: dict[str, dict[str, float]] = {c: {} for c in chain_name}
    for (a, b), w in pair_w.items():
        adj.setdefault(a, []).append((b, w))
        adj.setdefault(b, []).append((a, w))
        nbr_w[a][b] = nbr_w[a].get(b, 0.0) + w
        nbr_w[b][a] = nbr_w[b].get(a, 0.0) + w

    # 确定性模块度局部移动（Louvain 式单层；2026-09-09 塌簇治理，γ 随数据规模复扫校准）：
    # 加权标签传播在稠密加权图上雪崩——实测 6 轮收敛后 Q=0、90.6% 链并入单簇（离线探针实锤）。
    # γ 定档：618 链时点 γ=3.0→42 簇；数据增长至 635 链后 γ=3.0 自然漂到 73 簇超 48 上限，
    # 复扫（3.2/3.5/4.0/4.5）定 γ=3.5→47 簇（ACC rev2 四闸带 [15,48]，最大簇 9.4%、零单例簇）。
    # 确定性：sorted 遍历序 + 平票取最小社区。
    labels: dict[str, str] = {c: c for c in chain_name}
    order = sorted(chain_name)
    deg_w: dict[str, float] = {c: sum(nbr_w[c].values()) for c in order}
    sigma_tot: dict[str, float] = dict(deg_w)
    m2 = sum(deg_w.values())
    gamma_cm = 3.5
    for _ in range(30):
        changed = False
        for u in order:
            cu = labels[u]
            links: dict[str, float] = {}
            for nb, w in nbr_w[u].items():
                lc = labels[nb]
                links[lc] = links.get(lc, 0.0) + w
            du = deg_w[u]
            base = links.get(cu, 0.0) - gamma_cm * du * (sigma_tot[cu] - du) / m2
            best_c, best_g = cu, base
            for c in sorted(links):
                if c == cu:
                    continue
                g = links[c] - gamma_cm * du * sigma_tot[c] / m2
                if g > best_g + 1e-12 or (abs(g - best_g) <= 1e-12 and c < best_c):
                    best_c, best_g = c, g
            if best_c != cu:
                labels[u] = best_c
                sigma_tot[cu] -= du
                sigma_tot[best_c] += du
                changed = True
        if not changed:
            break

    def _clusters_of(lb: dict[str, str]) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {}
        for c, l in lb.items():
            out.setdefault(l, []).append(c)
        return out

    # 小簇（<2 链）与超量（>48）并入最强邻居
    for _ in range(600):
        groups = _clusters_of(labels)
        roots = sorted(groups, key=lambda r: (len(groups[r]), r))
        if len(roots) <= 48 and all(len(groups[r]) >= 2 for r in roots):
            break
        src = roots[0]
        nbrs = nbr_w.get(src, {})
        tgt = max(sorted(nbrs), key=lambda k: nbrs[k]) if nbrs else None
        if tgt is None or nbrs.get(tgt, 0.0) <= 0:
            tgt = min((r for r in roots if r != src), default=None)
            if tgt is None:
                break
        for c in groups[src]:
            labels[c] = tgt

    groups = _clusters_of(labels)
    chain_companies: dict[str, int] = {c: 0 for c in chain_name}
    for sym, cs in sym_chains.items():
        for c in cs:
            if c in chain_companies:
                chain_companies[c] += 1   # 一司挂多链按链各计（导航口径），簇内公司数另用去重并集

    cluster_stats = []
    for root, members in groups.items():
        inner_deg = {m: sum(w for nb, w in adj[m] if labels[nb] == root) for m in members}
        hub = max(sorted(members), key=lambda m: (inner_deg[m], chain_companies[m], m))
        base = chain_name[hub].split("（")[0].split("(")[0].strip() or chain_name[hub]
        cluster_stats.append({
            "root": root, "members": members, "hub": hub, "name": base + "族",
            "n_chains": len(members),
            "n_companies": len({s for s, cs in sym_chains.items() if cs & set(members)}),
            "n_nodes": sum(1 for n, c in node_chain.items() if c in set(members)),
        })
    cluster_stats.sort(key=lambda x: (-x["n_companies"], x["root"]))
    cid_of = {st["root"]: f"C{i+1:02d}" for i, st in enumerate(cluster_stats)}
    used_names: dict[str, int] = {}
    clusters_out, links_out, chains_out = [], [], []
    overrides = _cm_name_override()
    for st in cluster_stats:
        cid = cid_of[st["root"]]
        nm = overrides.get(cid) or st["name"]   # Commit C 规则版：override 优先，未列出沿用自动族名
        used_names[nm] = used_names.get(nm, 0) + 1
        if used_names[nm] > 1:
            nm = f"{nm}{used_names[nm]}"
        clusters_out.append({"id": cid, "name": nm, "n_chains": st["n_chains"],
                             "n_nodes": st["n_nodes"], "n_companies": st["n_companies"]})
        for m in st["members"]:
            chains_out.append({"chain_id": m, "name": chain_name[m], "cluster": cid,
                               "n_nodes": sum(1 for n, c in node_chain.items() if c == m),
                               "n_companies": chain_companies[m]})
    cg: dict[str, dict[str, float]] = {}
    for (a, b), w in pair_w.items():
        ca, cb = cid_of.get(labels[a]), cid_of.get(labels[b])
        if ca and cb and ca != cb:
            key = (ca, cb) if ca < cb else (cb, ca)
            cg[key] = cg.get(key, 0.0) + w
    links_out = [{"s": k[0], "t": k[1], "w": int(v)} for k, v in sorted(cg.items())]
    return {"clusters": clusters_out, "links": links_out, "chains": chains_out,
            "generated_at": datetime.now().isoformat(" ", "seconds")}


def _cm_galaxy() -> dict[str, Any]:
    g = _CM_GALAXY_CACHE["data"]
    if g and (time.time() - _CM_GALAXY_CACHE["ts"]) < 600:
        try:   # Commit C：族名 override 改 YAML 即生效（mtime 变化→绕过 TTL 强制重建）
            if _CM_NAME_OVERRIDE_PATH.stat().st_mtime != _CM_NAME_OVERRIDE["mtime"]:
                g = None
        except OSError:
            pass
        if g:
            return g
    g = _cm_build_galaxy()
    _CM_GALAXY_CACHE["data"] = g
    _CM_GALAXY_CACHE["ts"] = time.time()
    _CM_CLUSTER_CACHE.clear()
    return g


def _cm_symbol_names() -> dict[str, str]:
    m = _CM_NAME_CACHE["map"]
    if m is not None and (time.time() - _CM_NAME_CACHE["ts"]) < 600:
        return m
    conn = _cm_pg()
    try:
        cur = conn.cursor()
        cur.execute("SELECT from_symbol, MAX(from_name) FROM ig_company_edge WHERE valid_to IS NULL AND from_name IS NOT NULL "
                    "GROUP BY from_symbol")
        m = {r[0]: r[1] for r in cur.fetchall()}
        cur.execute("SELECT to_symbol, MAX(to_name) FROM ig_company_edge WHERE valid_to IS NULL AND to_name IS NOT NULL AND to_symbol <> '' "
                    "GROUP BY to_symbol")
        for s, n in cur.fetchall():
            m.setdefault(s, n)
        conn.close()
    except Exception:
        try:
            conn.close()
        except Exception:
            pass
        raise
    _CM_NAME_CACHE["map"] = m
    _CM_NAME_CACHE["ts"] = time.time()
    return m


@app.get("/api/chainmap-galaxy")
def chainmap_galaxy() -> dict[str, Any]:
    """产业地图 L1 星系（chainmap-galaxy 组件）：族节点+族间边+全量链清单（导航树同源）。"""
    try:
        g = _cm_galaxy()
        return {"ok": True, **g}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "clusters": [], "links": [], "chains": []}


@app.get("/api/chainmap-cluster")
def chainmap_cluster(cid: str = Query(..., min_length=2, max_length=8)) -> dict[str, Any]:
    """产业地图 L2 链层（chainmap-cluster 组件）：簇内链→环节（tier 分桶列）+结构边+公司计数。"""
    if not cid.replace("C", "").isdigit():
        return {"ok": False, "error": "bad cid", "chains": []}
    cached = _CM_CLUSTER_CACHE.get(cid)
    if cached:
        return {"ok": True, **cached}
    try:
        g = _cm_galaxy()
        members = [c for c in g["chains"] if c["cluster"] == cid]
        if not members:
            return {"ok": False, "error": "cluster not found", "chains": []}
        cluster = next(c for c in g["clusters"] if c["id"] == cid)
        conn = _cm_pg()
        try:
            cur = conn.cursor()
            ids = [c["chain_id"] for c in members]
            cur.execute("SELECT node_id, chain_id, name, tier FROM ig_node WHERE chain_id = ANY(%s)", (ids,))
            node_rows = cur.fetchall()
            cur.execute("SELECT node_id, count(DISTINCT symbol) FROM ig_node_company WHERE valid_to IS NULL AND node_id IN "
                        "(SELECT node_id FROM ig_node WHERE chain_id = ANY(%s)) GROUP BY node_id", (ids,))
            ncomp = {r[0]: int(r[1]) for r in cur.fetchall()}
            cur.execute("SELECT from_node, to_node FROM ig_edge")
            all_edges = cur.fetchall()
            conn.close()
        except Exception:
            try:
                conn.close()
            except Exception:
                pass
            raise
        nodes_by_chain: dict[str, list[dict[str, Any]]] = {c["chain_id"]: [] for c in members}
        nid_set = {r[0] for r in node_rows}
        for nid, ch, name, tier in node_rows:
            nodes_by_chain[ch].append({"node_id": nid, "name": name, "tier": tier or "",
                                       "col": _cm_col(tier), "n_companies": ncomp.get(nid, 0)})
        for lst in nodes_by_chain.values():
            lst.sort(key=lambda n: (-n["n_companies"], n["name"]))
        chains_out = [{**c, "nodes": nodes_by_chain[c["chain_id"]]} for c in
                      sorted(members, key=lambda c: -c["n_companies"])]
        edges_out = [[a, b] for a, b in all_edges if a in nid_set and b in nid_set]
        data = {"cluster": cluster, "chains": chains_out, "edges": edges_out}
        _CM_CLUSTER_CACHE[cid] = data
        return {"ok": True, **data}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "chains": []}


@app.get("/api/chainmap-node")
def chainmap_node(node_id: str = Query(..., min_length=1)) -> dict[str, Any]:
    """环节公司面板（chainmap-cluster 组件右侧抽屉数据源）：环节↔公司映射，龙头/核心优先。"""
    try:
        conn = _cm_pg()
        try:
            cur = conn.cursor()
            cur.execute("SELECT n.name, n.tier, n.chain_id, c.name FROM ig_node n "
                        "JOIN ig_chain c ON c.chain_id = n.chain_id WHERE n.node_id = %s", (node_id,))
            row = cur.fetchone()
            if not row:
                return {"ok": False, "error": "node not found", "companies": []}
            cur.execute("SELECT symbol, role, confidence FROM ig_node_company WHERE valid_to IS NULL AND node_id = %s", (node_id,))
            rows = cur.fetchall()
            syms = [r[0] for r in rows]
            # 跨链数（二期 Commit B）：公司在全部 active 链的落位链数（>1 即跨链，徽章跳转依据）
            nchains: dict[str, int] = {}
            if syms:
                cur.execute(
                    "SELECT nc.symbol, count(DISTINCT n.chain_id) FROM ig_node_company nc "
                    "JOIN ig_node n ON n.node_id = nc.node_id "
                    "JOIN ig_chain c ON c.chain_id = n.chain_id "
                    "WHERE nc.valid_to IS NULL AND nc.symbol = ANY(%s) AND c.status = 'active' GROUP BY nc.symbol",
                    (syms,),
                )
                nchains = {r[0]: int(r[1]) for r in cur.fetchall()}
            names = _cm_symbol_names()
            conn.close()
        except Exception:
            try:
                conn.close()
            except Exception:
                pass
            raise
        companies = [{"symbol": s, "name": names.get(s, ""), "role": r or "",
                      "confidence": None if cf is None else round(float(cf), 2), "n_chains": nchains.get(s, 1)}
                     for s, r, cf in rows]
        companies.sort(key=lambda x: (_cm_role_rank(x["role"]), -(x["confidence"] or 0), x["symbol"]))
        return {"ok": True, "node": {"node_id": node_id, "name": row[0], "tier": row[1] or "",
                                     "chain_id": row[2], "chain_name": row[3]},
                "companies": companies[:200], "total": len(companies)}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "companies": []}


@app.get("/api/chainmap-search")
def chainmap_search(q: str = Query(..., min_length=1)) -> dict[str, Any]:
    """产业地图搜索（chainmap-search 组件）：链名/环节名 + symbol 落位 + 公司名（名称映射覆盖不全为已知边界）。"""
    kw = q.strip()
    if not kw:
        return {"ok": False, "error": "empty query", "chains": [], "nodes": [], "symbols": []}
    like = f"%{kw}%"
    try:
        g = _cm_galaxy()
        chain_cluster = {c["chain_id"]: c["cluster"] for c in g["chains"]}
        conn = _cm_pg()
        try:
            cur = conn.cursor()
            cur.execute("SELECT chain_id, name FROM ig_chain WHERE status='active' AND name ILIKE %s "
                        "ORDER BY name LIMIT 10", (like,))
            chains_out = [{"chain_id": r[0], "name": r[1], "cluster": chain_cluster.get(r[0], "")} for r in cur.fetchall()]
            cur.execute("SELECT n.node_id, n.name, n.chain_id, c.name FROM ig_node n "
                        "JOIN ig_chain c ON c.chain_id = n.chain_id WHERE n.name ILIKE %s "
                        "ORDER BY n.name LIMIT 10", (like,))
            nodes_out = [{"node_id": r[0], "name": r[1], "chain_id": r[2], "chain_name": r[3],
                          "cluster": chain_cluster.get(r[2], "")} for r in cur.fetchall()]
            cur.execute("SELECT DISTINCT nc.symbol, n.node_id, n.name, n.chain_id, c.name, nc.role "
                        "FROM ig_node_company nc JOIN ig_node n ON n.node_id = nc.node_id "
                        "JOIN ig_chain c ON c.chain_id = n.chain_id WHERE nc.valid_to IS NULL AND nc.symbol ILIKE %s LIMIT 20",
                        (kw + "%",))
            sym_rows = cur.fetchall()
            hit_syms = {r[0] for r in sym_rows}
            name_map = _cm_symbol_names()
            named = [s for s, n in name_map.items() if kw.lower() in (n or "").lower() and s not in hit_syms][:20]
            extra_rows: list[tuple] = []
            if named:
                cur.execute("SELECT DISTINCT nc.symbol, n.node_id, n.name, n.chain_id, c.name, nc.role "
                            "FROM ig_node_company nc JOIN ig_node n ON n.node_id = nc.node_id "
                            "JOIN ig_chain c ON c.chain_id = n.chain_id WHERE nc.valid_to IS NULL AND nc.symbol = ANY(%s) LIMIT 20", (named,))
                extra_rows = cur.fetchall()
            conn.close()
        except Exception:
            try:
                conn.close()
            except Exception:
                pass
            raise
        names = _cm_symbol_names()
        symbols_out = [{"symbol": r[0], "name": names.get(r[0], ""), "node_id": r[1], "node_name": r[2],
                        "chain_id": r[3], "chain_name": r[4], "cluster": chain_cluster.get(r[3], ""), "role": r[5] or ""}
                       for r in list(sym_rows) + extra_rows]
        return {"ok": True, "chains": chains_out, "nodes": nodes_out, "symbols": symbols_out}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "chains": [], "nodes": [], "symbols": []}


# ═══════════════ 公司详情卡数据端点（chainmap 二期 Commit A，2026-09-09） ═══════════════
# 方向语义（Owner 红线，禁止臆断）：ig_company_edge from=供应商 → to=客户（load_supply_top5_483.py L16 实锤）；
# J88_collab_patent=供应链协同创新边同样有方向（load_supply_collab_j88.py L16-17：供应商文件 from=供应商→to=中游，
# 客户文件 from=中游→to=客户，weight=联合专利合作次数）；to_symbol=''=对手方非上市（名称在 to_name，DDL L152 约定）。
# 按来源分组贴 edge_kind：483_top5_customer/match_list_2012_2023/websearch/J88_collab_patent=supply
# （J88 归 supply 为 Owner 2026-09-09 方向勘误批准，ACC-F-CHAINMAP-COMPANY-CARD rev2 留痕）。

_CM_SOURCE_EDGE_KIND: dict[str, str] = {
    "483_top5_customer": "supply",
    "match_list_2012_2023": "supply",
    "websearch": "supply",
    "J88_collab_patent": "supply",
}
_CM_RELATION_CAP = 10          # 每侧关系展示上限（total 如实返回）
_CM_PLACEMENT_CAP = 60         # 落位展示上限（多链公司如实给 total）


def _cm_bare_symbol(sym: str) -> str:
    """300750.SZ → 300750（CH 行情 6 位裸码口径）；其他格式原样返回。"""
    s = (sym or "").strip().upper()
    return s.split(".")[0] if s.endswith((".SH", ".SZ", ".BJ")) else s


def _cm_quote(bare: str) -> dict[str, Any] | None:
    """CH 行情快照（独立降级：任何异常→None，前端渲染 '—'；CH 失败=null 任务书铁律）。

    总市值：CH 两表无市值列（2026-09-09 全库普查）→ equity_pledge_summary.total_shares(万股,周更)
    × 最新收盘 估算（茅台 16,372 亿交叉验证 ✓），键名 total_mv_yi，前端标"约"。
    """
    try:
        rows = _ch_exec(
            "SELECT trade_date, close, pct_change, amount FROM c1_market.kline_daily FINAL "
            "WHERE symbol = %(s)s AND close > 0 AND quality_flag = 1 ORDER BY trade_date DESC LIMIT 1",
            {"s": bare},
        )
        if not rows:
            return None
        d, close, pct, amt = rows[0]
        out: dict[str, Any] = {
            "trade_date": str(d),
            "close": float(close),
            "pct_change": None if pct is None else round(float(pct), 2),
            "amount": None if amt is None else float(amt),
        }
        try:
            mrows = _ch_exec(
                "SELECT round(p.shares_wan * 10000 * k.close / 1e8, 1) FROM "
                "(SELECT argMax(total_shares, end_date) AS shares_wan FROM c3_fundamental.equity_pledge_summary "
                "WHERE symbol = %(s)s AND total_shares > 0) p CROSS JOIN "
                "(SELECT close FROM c1_market.kline_daily FINAL WHERE symbol = %(s)s AND close > 0 "
                "AND quality_flag = 1 ORDER BY trade_date DESC LIMIT 1) k",
                {"s": bare},
            )
            if mrows and mrows[0][0] is not None:
                out["total_mv_yi"] = float(mrows[0][0])
        except Exception:
            pass
        try:
            vrows = _ch_exec(
                "SELECT trade_date, pe_ttm, pb_mrq FROM c1_market.daily_valuation "
                "WHERE symbol = %(s)s AND pe_ttm > 0 ORDER BY trade_date DESC LIMIT 1",
                {"s": bare},
            )
            if vrows:
                out["valuation_asof"] = str(vrows[0][0])
                out["pe_ttm"] = float(vrows[0][1])
                out["pb_mrq"] = float(vrows[0][2])
        except Exception:
            pass
        return out
    except Exception:
        return None


@app.get("/api/chainmap-company")
def chainmap_company(symbol: str = Query(..., min_length=2, max_length=24)) -> dict[str, Any]:
    """公司详情卡（chainmap-company-card 真源）：链上落位 + 上下游关系 + CH 行情/估算市值。

    symbol 接受 6 位裸码或带 .SH/.SZ/.BJ 后缀（统一归一）；海外/UNLISTED 端点不支持（fail-closed）。
    关系段：suppliers=to_symbol=本司（from 为供应商）；customers=from_symbol=本司（to 为客户）；
    collabs=预留段（J88 勘误后归 supply，当前恒空，字段保留兼容 ACC item1 五段契约）；
    对手方未上市 symbol='' 用 to_name/from_name 展示。
    行情段独立降级：CH 异常→quote=null，不影响图谱段返回。
    """
    import re as _re

    sym = (symbol or "").strip().upper()
    if not _re.fullmatch(r"\d{6}(\.(SH|SZ|BJ))?", sym):
        return {"ok": False, "error": "bad symbol", "company": {"symbol": sym},
                "placements": [], "suppliers": [], "customers": [], "collabs": [], "quote": None}
    if "." not in sym:   # 裸码补后缀（与 load_supply_top5_483.to_symbol 同规则）
        sym += {"6": ".SH"}.get(sym[0], ".SZ") if sym[0] in "03" else (".SH" if sym[0] == "6" else ".BJ")
    empty = {"ok": False, "error": "", "company": {"symbol": sym, "name": None},
             "placements": [], "suppliers": [], "customers": [], "collabs": [], "quote": None}
    try:
        names = _cm_symbol_names()
        g = _cm_galaxy()
        chain_meta = {c["chain_id"]: (c["cluster"], c["name"]) for c in g["chains"]}
        cluster_name = {c["id"]: c["name"] for c in g["clusters"]}
        conn = _cm_pg()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT n.node_id, n.name, n.tier, c.chain_id, c.name, nc.role, nc.confidence "
                "FROM ig_node_company nc JOIN ig_node n ON n.node_id = nc.node_id "
                "JOIN ig_chain c ON c.chain_id = n.chain_id "
                "WHERE nc.valid_to IS NULL AND nc.symbol = %s AND c.status = 'active' ORDER BY c.name, n.name",
                (sym,),
            )
            pos_rows = cur.fetchall()
            cur.execute(
                "SELECT from_symbol, to_symbol, year, product, weight, weight_type, source, "
                "from_name, to_name, amount FROM ig_company_edge "
                "WHERE valid_to IS NULL AND (from_symbol = %s OR to_symbol = %s) "
                "ORDER BY year DESC, weight DESC NULLS LAST LIMIT 400",
                (sym, sym),
            )
            rel_rows = cur.fetchall()
            conn.close()
        except Exception:
            try:
                conn.close()
            except Exception:
                pass
            raise
    except Exception as exc:
        empty["error"] = str(exc)[:200]
        return empty

    placements: list[dict[str, Any]] = []
    for nid, nname, tier, chid, chname, role, cf in pos_rows:
        cl, _clname = chain_meta.get(chid, ("", ""))
        placements.append({
            "node_id": nid, "node_name": nname, "tier": tier or "", "col": _cm_col(tier),
            "chain_id": chid, "chain_name": chname, "cluster": cl,
            "cluster_name": cluster_name.get(cl, cl),
            "role": role or "", "confidence": None if cf is None else round(float(cf), 2),
        })
    n_placements = len(placements)
    placements = placements[:_CM_PLACEMENT_CAP]

    suppliers: list[dict[str, Any]] = []
    customers: list[dict[str, Any]] = []
    collabs: list[dict[str, Any]] = []
    for fs, ts, yr, prod, w, wt, src, fn, tn, amt in rel_rows:
        kind = _CM_SOURCE_EDGE_KIND.get(src or "", "supply")
        base = {"product": prod, "year": int(yr) if yr is not None else None,
                "weight": None if w is None else round(float(w), 2), "weight_type": wt,
                "source": src, "amount": None if amt is None else float(amt)}
        if kind == "collab":
            other_s, other_n = (ts, tn) if fs == sym else (fs, fn)
            collabs.append({**base, "symbol": other_s or "", "name": other_n or names.get(other_s or "", ""),
                            "unlisted": not other_s})
        elif ts == sym:   # from=供应商 → 本司
            suppliers.append({**base, "symbol": fs, "name": fn or names.get(fs, ""), "unlisted": False})
        elif fs == sym:   # 本司 → to=客户
            customers.append({**base, "symbol": ts, "name": tn or names.get(ts, ""), "unlisted": not ts})
    n_sup, n_cus, n_col = len(suppliers), len(customers), len(collabs)
    suppliers = suppliers[:_CM_RELATION_CAP]
    customers = customers[:_CM_RELATION_CAP]
    collabs = collabs[:_CM_RELATION_CAP]

    cname = names.get(sym)
    if not cname:
        for fs, _ts, _yr, _prod, _w, _wt, _src, fn, tn, _amt in rel_rows:
            if fs == sym and fn:
                cname = fn
                break
            if _ts == sym and tn:
                cname = tn
                break
    if not cname:   # ig 名称映射覆盖不全 → CH stock_basic 兜底（/api/stock-header 同款真源），失败保持 None
        try:
            nb = _ch_exec(
                "SELECT argMax(name, valid_from) FROM stock_basic WHERE symbol=%(s)s",
                {"s": _cm_bare_symbol(sym)},
            )
            if nb and nb[0][0]:
                cname = str(nb[0][0])
        except Exception:
            pass
    return {
        "ok": True,
        "company": {"symbol": sym, "name": cname},
        "placements": placements, "total_placements": n_placements,
        "suppliers": suppliers, "n_suppliers": n_sup,
        "customers": customers, "n_customers": n_cus,
        "collabs": collabs, "n_collabs": n_col,
        "quote": _cm_quote(_cm_bare_symbol(sym)),
        "generated_at": datetime.now().isoformat(" ", "seconds"),
    }


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8890, log_level="warning")


if __name__ == "__main__":
    main()

# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md
# [MODULE] zephyr.frontend.dashboard.api_server
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] zephyr.data.ch_config; clickhouse_driver; fastapi; uvicorn
# [CONSUMERS] 前端 dashboard（web/services/api.js）
# [STARTUP] python -m zephyr.frontend.dashboard.api_server（或 uvicorn 直跑）
# [MATURITY] testing
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
from datetime import date, datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

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
    """从两个注册表构建策略行（name=StrategyMeta.name 中文真源；Owner 2026-09-03）。"""
    from zephyr.governance.strategies.strategy_base import StrategyRegistry

    rows: list[dict[str, Any]] = []
    for sid in sorted(StrategyRegistry.list_all().keys() or []):
        cls = StrategyRegistry.list_all()[sid]
        m = _strategy_meta_of(cls)
        rows.append(
            {"id": sid, "name": (m.name if m and getattr(m, "name", "") else sid), "note": _BT_STRATEGY_NOTES.get(sid, ""), "tick_only": False}
        )
    try:  # tick 策略族（TickStrategyBase 注册表，仅 tick 模式可跑）
        from zephyr.pf_core.strategy_engine.tick_strategy_base import TickStrategyBase, autodiscover_tick_strategies

        autodiscover_tick_strategies("zephyr.pf_core")
        tick_reg = getattr(TickStrategyBase, "_registry", {}) or {}
        for sid in sorted(tick_reg.keys()):
            cls = tick_reg[sid]
            m = _strategy_meta_of(cls)
            rows.append(
                {"id": sid, "name": (m.name if m and getattr(m, "name", "") else sid), "note": _BT_STRATEGY_NOTES.get(sid, "tick 策略"), "tick_only": True}
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
        return snap.get("data") or None
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
    """服务启停控制：body={id, action: start|stop, confirm?: bool}。

    分级闸门：confirm 级未带 confirm=true 返回 need_confirm（前端弹确认框）；
    guard/external/self 级一律拒绝（保命进程/外部程序/宿主不许在此操作）。
    """
    from zephyr.frontend.dashboard.services_registry import control_service

    sid = str(body.get("id", "")).strip()
    action = str(body.get("action", "")).strip()
    if action not in ("start", "stop"):
        return {"ok": False, "error": "action must be start|stop"}
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
    "SELECT database, table, count() AS parts, sum(rows) AS rows, "
    "min(partition) AS earliest, max(partition) AS latest "
    "FROM system.parts WHERE active AND database IN ('c0_meta','c1_market','c3_fundamental') "
    "GROUP BY database, table ORDER BY database, table"
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
    "weekend_calibration": "周末校准（周六 03:00）", "weekend_backfill": "周末补漏（周日 02:00）",
    "daily_backfill": "每日补漏（17:00）", "news_slow": "慢速新闻（约 2h/轮）", "pre_market": "盘前（08:30）",
    "auction_highfreq": "集合竞价（09:15 起）", "intraday_sector": "盘中板块", "event_driven": "事件驱动（3min 轮询）",
    "integrity_check": "完整性巡检（23:00）", "catchup_guard": "错过补跑（03:30）",
}

# 时段 → cron（真源=schedule.yaml；下次调度计算用）
_SCHEDULE_CRON = {
    "pre_market": "30 8 * * 0-4", "intraday_realtime": "*/5 9-15 * * 0-4",
    "intraday_minute": "*/5 9-15 * * 0-4", "intraday_sector": "*/5 9-15 * * 0-4",
    "event_driven": "*/3 * * * *", "news_slow": "*/30 * * * *",
    "daily_kline": "30 16 * * 0-4", "daily_capital": "00 18 * * 0-4", "daily_event": "00 19 * * 0-4",
    "nightly_financial": "00 22 * * 0-4", "weekend_calibration": "00 3 * * 0",
    "monthly_static": "00 9 1 * *", "weekend_backfill": "00 2 * * 0", "daily_backfill": "00 17 * * 0-4",
    "integrity_check": "00 23 * * 0-4", "catchup_guard": "30 3 * * *",
    "auction_highfreq": "*/10 9-15 * * 0-4",
}


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
    """表级下载实况：146 表时间段/源/实时速率/VPN 联动（断更监管真源=CH system.parts+query_log）。"""
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
            state, rate, quality = ("idle", 0, "今日已完成" if light == "green" else "待机")
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
    return {"ok": True, "tables": tables, "counts": cnt, "vpn_on": vpn,
            "dl_now": dl_now,
            "generated_at": datetime.now().isoformat(" ", "seconds")}


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8890, log_level="warning")


if __name__ == "__main__":
    main()

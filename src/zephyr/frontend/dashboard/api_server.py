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
    "1m": "kline_1min", "5m": "kline_5min", "15m": "kline_15min",
    "30m": "kline_30min", "60m": "kline_60min",
    "1d": "kline_daily", "1w": "kline_weekly", "1M": "kline_monthly",
}

_client: Client | None = None
_col_cache: dict[str, dict[str, str]] = {}
_ch_lock = threading.Lock()   # clickhouse_driver 单连接非线程安全：FastAPI 线程池并发请求必须串行化


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
        )
    return _client


def _ch_exec(sql: str, params: dict | None = None) -> list:
    """带锁执行（2026-09-01 实证：stockq 多组件并发取数触发 Simultaneous queries on single connection）。"""
    with _ch_lock:
        return _ch().execute(sql, params or {})


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
            rows = list(rows) + list(_ch_exec(
                "SELECT symbol, trade_date, close FROM kline_etf_daily "
                "WHERE symbol IN %(syms)s AND close > 0 "
                "ORDER BY trade_date DESC LIMIT 2 BY symbol",
                {"syms": tuple(missing)},
            ))
        by_sym: dict[str, list[tuple[Any, float]]] = {}
        for r in rows:
            by_sym.setdefault(r[0], []).append((r[1], float(r[2])))
        name_rows = _ch_exec(
            "SELECT symbol, argMax(name, valid_from) FROM stock_basic "
            "WHERE symbol IN %(syms)s GROUP BY symbol",
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
                    for i in range(1, 11):   # 最多十档，有多少列取多少
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
            "SELECT DISTINCT symbol, name FROM stock_basic "
            "WHERE symbol LIKE %(q)s OR name LIKE %(qn)s LIMIT %(l)s",
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


@app.get("/api/strategies")
def strategies() -> dict[str, Any]:
    """策略库列表（backtest 页策略多选下拉）：StrategyRegistry 动态真源。"""
    try:
        sys.path.insert(0, str(_REPO / "src"))
        from zephyr.pf_core.strategy_engine.strategy_runner import StrategyRunner

        StrategyRunner._ensure_strategy("topn-momentum")  # 触发 autodiscover（幂等）
        from zephyr.governance.strategies.strategy_base import StrategyRegistry

        reg = StrategyRegistry.list_all() if hasattr(StrategyRegistry, "list_all") else {}
        data = []
        for sid, cls in (reg or {}).items():
            data.append({
                "id": sid,
                "name": getattr(getattr(cls, "meta", None), "name", None) or sid,
                "available": True,
            })
        data.sort(key=lambda x: x["id"])
        return {"ok": True, "count": len(data), "data": data}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "data": []}


@app.get("/api/backtest-list")
def backtest_list(strategy_id: str = Query("", description="可选策略过滤")) -> dict[str, Any]:
    """回测产物列表（backtest 页）：扫 artifacts 目录，created_at 降序。"""
    try:
        if not _BT_ARTIFACTS_DIR.exists():
            return {"ok": True, "count": 0, "data": []}
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
        return {"ok": True, "count": len(out), "data": out}
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
                "trade_log": tl_full[-500:][::-1],   # 倒序（最新在前）cap 500
                "benchmark_curve": d.get("benchmark_curve") or [],
                "total_points": {"equity": len(eq_full), "trades": len(tl_full)},   # 全量规模（抽稀明示）
            },
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "data": {}}


# 页面发起回测（#4 全链路）：ThreadPoolExecutor 后台跑（RULE-SEVEN 禁 asyncio 并行），
# 状态存内存 {task_id: {...}}；前端轮询 /api/backtest-run?task_id= 查进度。
from concurrent.futures import ThreadPoolExecutor  # noqa: E402

_BT_RUN_POOL = ThreadPoolExecutor(max_workers=1, thread_name_prefix="bt-run")   # 串行防 CH 连接竞争
_BT_RUN_STATE: dict[str, dict[str, Any]] = {}
_BT_RUN_LOCK = threading.Lock()


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
        _BT_RUN_STATE[task_id] = {"status": "running", "params": {"strategies": strategies, "symbols": symbols, "start": start, "end": end, "mode": mode}}
    _BT_RUN_POOL.submit(_bt_run_task, task_id, {
        "strategies": strategies, "strategy_id": strategies[0], "symbols": symbols, "start": start, "end": end,
        "mode": mode,
        "factor_ids": body.get("factor_ids", ["momentum_20d"]),
        "rebalance_freq": body.get("rebalance_freq", "W-FRI"),
        "top_n": body.get("top_n", 10), "max_single": body.get("max_single", 0.10),
        "initial_capital": body.get("initial_capital", 1_000_000.0),
        "pit_shift": body.get("pit_shift", 1),
    })
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
                key, {"source": src, "signal_id": sid, "trade_date": max_d.isoformat(), "buy": 0, "sell": 0, "hold": 0, "neutral": 0}
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


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8890, log_level="warning")


if __name__ == "__main__":
    main()

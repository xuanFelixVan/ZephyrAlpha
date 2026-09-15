# [BLUEPRINT] MOD-L08-001 | docs/03_modules/_domain_frontend/blueprint.md
# [MODULE] zephyr.frontend.dashboard.api_server
# [DOMAIN] D_FRONTEND
# [DEPENDENCIES] zephyr.data.ch_config; clickhouse_driver; fastapi; uvicorn; zephyr.governance.persistence.battle_map_reader; zephyr.governance.strategies.strategy_base; zephyr.pf_core.strategy_engine.tick_strategy_base
# [CONSUMERS] 前端 dashboard（web/services/api.js）
# [STARTUP] manual（python -m zephyr.frontend.dashboard.api_server 或 uvicorn 直跑；面板服务控制台可一键重启）
# [MATURITY] production
# [INVARIANTS] 只读服务+四个获准写端点（backtest-run / framework-backtest-run / services-control /
#   promotion-decide——写权限扩张均有授权留痕：前者回测产物、中者服务编排、末者 Owner 拍板门位数字化
#   授权=Owner 2026-09-15 通宵自主执行指令+宪法 §5）; 非法输入 fail-closed 返回 ok:false; Decimal/Date 一律转 JSON 可序列化
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
  GET /api/pattern-events?symbol=600519           形态事件（消费班 W-C4，MOD-SIG-147 线）
  GET /api/pattern-winrate?direction=向下&fwd_window=10  形态胜率切片（按 hit_rate 降序）
  GET /api/pattern-evidence                       形态机生证据（REG-PAT-001 evidence 直读）
  GET /api/promotion-advisories                   策略转正建议清单（C5 审批页数据源，只读）
  POST /api/promotion-decide                      Owner 拍板 approve/reject（第四获准写端点，见端点 docstring 授权依据）
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
from typing import Any, Final

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger("zk.api_server")

_REPO = Path(__file__).resolve().parents[4]
if str(_REPO / "src") not in sys.path:
    sys.path.insert(0, str(_REPO / "src"))


app = FastAPI(title="ZephyrAlpha Dashboard API (read-only + controlled writes)")
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

_client = None  # CH 连接（连接统一治本 2026-09-14：经 DatabaseService 槽位领取，writer/账号语义见 _ch 注释）
_col_cache: dict[str, dict[str, str]] = {}
_ch_lock = threading.Lock()  # clickhouse_driver 单连接非线程安全：FastAPI 线程池并发请求必须串行化


def _ch():
    global _client
    if _client is None:
        # 连接统一治本（2026-09-14）：构造上收 DatabaseService（slot=dashboard 独立槽位）。
        # 账号语义保留历史行为（base 账号）；双道超时防线原样承接（#T6 + 2026-09-03 实证）。
        from zephyr.infrastructure.database_service import get_db_service

        _client = get_db_service().get_clickhouse_conn(
            role="admin", slot="dashboard",
            extra_kwargs={"connect_timeout": 3, "send_receive_timeout": 15})
    return _client


_CH_MAX_EXEC_SECONDS = 12  # 查询级超时（服务端 max_execution_time）；与 socket 级 send_receive_timeout 构成双道防线


def _ch_exec(sql: str, params: dict | None = None) -> list:
    """带锁执行（2026-09-01 实证：stockq 多组件并发取数触发 Simultaneous queries on single connection）。
    2026-09-03 加固：半开连接挂死曾耗尽线程池致整机假死——查询异常即弃连重建，锁获取限时防队列堆积。
    2026-09-10 加固（legacy-clear T6）：补查询级超时 settings.max_execution_time——socket 级
    send_receive_timeout 在"服务端持续慢查询但连接未断"场景不触发，线程池被慢查询占满后
    连自重启端点都排不上队；查询级超时由服务端主动中断，异常仍走弃连重建+端点级降级 ok:false。
    """
    global _client
    if not _ch_lock.acquire(timeout=30):
        raise RuntimeError("CH 通道忙（30s 未获锁，疑似上游查询挂死）")
    try:
        return _ch().execute(sql, params or {}, settings={"max_execution_time": _CH_MAX_EXEC_SECONDS})
    except Exception:
        _client = None   # 连接疑似坏态：弃置，下一位调用者重建自愈
        from zephyr.infrastructure.database_service import get_db_service

        get_db_service().invalidate_clickhouse_conn(role="admin", slot="dashboard")
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
def _run_status_of(lock: object, state: dict, task_id: str) -> dict[str, Any]:
    """回测任务状态轮询公共实现（backtest/整装两管道同构，克隆合并 2026-09-12）。"""
    with lock:
        st = state.get(task_id.strip())
    if st is None:
        return {"ok": False, "error": "task not found", "status": "unknown"}
    return {"ok": True, **st}


def backtest_run_status(task_id: str = Query(..., min_length=3)) -> dict[str, Any]:
    """轮询回测任务状态：running / done / failed（done 附 run_id 可跳详情）。"""
    return _run_status_of(_BT_RUN_LOCK, _BT_RUN_STATE, task_id)


# ── 整装回测三端点（二期整装回测后端，MOD-FWCOMP-001；追加式，复用 backtest-run task 模式）──
# 组合回测器真源: zephyr.pf_core.strategy_engine.framework_composer；
# 方案权重真源: config/framework_plans.yaml（防御/均衡/激进三套，Σ=100%）。
# 与 /api/backtest-run 的边界: backtest-run=多策略各自跑各自出净值；framework-backtest-run=
# 方案权重×子策略权重面板线性合成组合面板→引擎跑出单条组合净值（整装语义）。
# 三期 regime 动态权重联动（α_i(t) 查表）: POST body 增 dynamic+regime_series——
# regime 来源=显式注入 {date: state}（T1 盘点结论：无逐日持久化 regime 真源表，
# 判定真源=MOD-REGIME-001 检测器，查表不做判定，禁自造判定逻辑，宪章 §3 约束三）；
# done 响应补 per_regime 分段摘要（各 regime 组合收益/回撤贡献）供前端展示。
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
                regime_by_date=params.get("regime_by_date"),  # 三期：None=静态（二期语义）
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
                    # 三期动态模式三键（静态=False/{} /[]，二期消费方零漂移）
                    "dynamic": summary.get("dynamic", False),
                    "regime_day_counts": summary.get("regime_day_counts", {}),
                    "per_regime": summary.get("per_regime", []),
                    # 面板级对账（#275 定案口径①）：独立复算逐位硬验收摘要
                    "panel_reconciliation": summary.get("panel_reconciliation"),
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
           allow_partial?（默认 true：tick-only 成员跳过后权重显式再归一化并披露）,
           dynamic?（三期默认 false：regime 动态权重开关）,
           regime_series?（dynamic=true 时必填：{YYYY-MM-DD: regime_state} 显式注入日序，
           state ∈ REGIME_STATES 7 态 r1/r2/r3/r4/r10/r11/r12——真源 regime_detector，
           查表不做判定；未覆盖日期回退方案基准权重）}
    产物: data/backtest_artifacts/bt-fw-*.json（与单策略 schema 对齐，plan_id 落 metrics；
          动态模式另落 dynamic/regime_day_counts/plan_regime_overrides）。
    done 响应: 增 dynamic/regime_day_counts/per_regime（各 regime 组合收益/回撤贡献分段
          摘要，regime=__base__ 为未覆盖回退组）。
    """
    plan_id = str(body.get("plan_id", "")).strip()
    symbols = [str(s).strip() for s in body.get("symbols", []) if str(s).strip()]
    start = str(body.get("start", "")).strip()
    end = str(body.get("end", "")).strip()
    if not plan_id or not symbols or not start or not end:
        return {"ok": False, "error": "plan_id/symbols/start/end required", "task_id": None}

    # ── 三期：regime 动态模式入参校验（fail-fast，composer 侧再 fail-closed 兜底）──
    dynamic = bool(body.get("dynamic", False))
    regime_series_raw = body.get("regime_series")
    regime_by_date: dict[str, str] | None = None
    if dynamic:
        if not isinstance(regime_series_raw, dict) or not regime_series_raw:
            return {
                "ok": False,
                "error": "dynamic=true requires non-empty regime_series: {YYYY-MM-DD: regime_state}",
                "task_id": None,
            }
        try:
            from zephyr.regime.core.regime_detector import REGIME_STATES

            bad = {
                str(v): str(v)
                for v in regime_series_raw.values()
                if str(v).strip() not in REGIME_STATES
            }
        except Exception as exc:  # noqa: BLE001 — 词表真源不可用即入参不可信
            return {"ok": False, "error": f"regime states source unavailable: {exc}", "task_id": None}
        if bad:
            return {
                "ok": False,
                "error": f"invalid regime states {sorted(bad)}（合法 7 态见 regime_detector.REGIME_STATES）",
                "task_id": None,
            }
        regime_by_date = {str(k): str(v).strip() for k, v in regime_series_raw.items()}

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
            "regime_by_date": regime_by_date,  # 三期：None=静态
        },
    )
    return {"ok": True, "task_id": task_id, "status": "running", "plan_id": plan_id}


@app.get("/api/framework-backtest-run")
def framework_backtest_run_status(task_id: str = Query(..., min_length=3)) -> dict[str, Any]:
    """轮询整装回测任务状态：running / done / failed（done 附 run_id=bt-fw-* 可跳详情）。"""
    return _run_status_of(_FW_RUN_LOCK, _FW_RUN_STATE, task_id)


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
# 无 tasks.yaml 任务的内算表元数据（数据监管行补 数据源/时段 展示——调度接线在 schedule
# 槽位而非 tasks.yaml，tasks_meta 查不到导致整行显示"—"；Owner 2026-09-10 要求情绪线上屏）
_INTERNAL_JOB_META: Final = {
    "news_sentiment_window": {"source": "internal·情绪批", "schedule_zh": "每日 08:20 自动打分"},
}

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
        if not meta and tbl_s in _INTERNAL_JOB_META:
            meta = _INTERNAL_JOB_META[tbl_s]   # 无下载任务的内算表（调度接线在 schedule 槽位非 tasks.yaml）
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
#       缺口/完整度基准=c1_market.trade_calendar（A股开市日）按表自身频率口径换算（weekly/monthly/
#       quarterly/event 各自算法，见 _asset_freq_of）；应有宽度=c0_meta.stock_list 最新清单（白名单表才
#       展示，防误报不完整）；存储层=三层冷热架构（docs/03_modules/_cross_layer/database/blueprint.md：
#       热 Redis/常规 CH/冷 E 盘）。
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

# 频率口径分类（Owner 2026-09-10 二批裁定"修尺子"）：完整度/缺口按表自身数据频率计算，
# 禁止用 A 股日频日历量周K/月K/季频/事件表（v1 伪缺口根因：周K compl≈21%/月K≈5.6%/北向季频≈1.9%）。
# 判定来源择优：表名启发（weekly/monthly 族）+ 显式登记（季频快照/事件驱动），不读 tasks.yaml
# schedule——任务调度频率≠数据频率（northbound 任务日跑但数据=季度末快照，schedule 作真源必错）。
_ASSET_FREQ_QUARTERLY = ("northbound_hold_snapshot",)   # tushare hk_hold 季度末快照（JOB-083）
_ASSET_FREQ_EVENT = (                                    # 事件驱动：行随事件出现，无每日覆盖语义
    "ex_dividend_event", "index_constituent", "index_adjustment", "msci_adjustment",
    "margin_target_adjustment", "dividend", "share_change", "repurchase",
    "restricted_shares", "disclosure_plan", "share_unlock", "ipo_schedule",
)


def _asset_freq_of(tbl: str, dc: str | None) -> str:
    """表数据频率：weekly/monthly/quarterly/event/daily/none（none=无日期列）。"""
    if tbl in _ASSET_FREQ_EVENT:
        return "event"
    if tbl in _ASSET_FREQ_QUARTERLY:
        return "quarterly"
    if "_weekly" in tbl or tbl.endswith("weekly"):
        return "weekly"
    if "_monthly" in tbl or tbl.endswith("monthly"):
        return "monthly"
    return "daily" if dc else "none"


def _asset_period_key(d: str, freq: str) -> str:
    """日期→所属周期键（weekly=ISO 周 / monthly=月 / quarterly=季）；bar 日期=周期内最后交易日，与日历同周期映射。"""
    y, m = int(d[:4]), int(d[5:7])
    if freq == "monthly":
        return f"{y}-{m:02d}"
    if freq == "quarterly":
        return f"{y}-Q{(m - 1) // 3 + 1}"
    iso = date(int(y), m, int(d[8:10])).isocalendar()
    return f"{iso[0]}-W{iso[1]:02d}"


_ASSET_TIER_OVERRIDES: dict[str, str] = {}   # 表名→tier；冷层启用迁表后在此登记（对齐 storage_tiering Tier；中文映射在前端）
_asset_state: dict[str, Any] = {"running": False, "done": 0, "total": 0, "audited_at": "", "ts": 0.0,
                                "error": "", "tables": {}}
_asset_lock = threading.Lock()
_asset_thread: threading.Thread | None = None


def _asset_audit_client():
    """审计专用连接（slot=asset_audit 独立槽位，不与 _ch_exec 全局锁争用——审计查询秒级~分钟级，不能饿死 30s 轮询端点）。"""
    from zephyr.infrastructure.database_service import get_db_service

    return get_db_service().get_clickhouse_conn(
        role="admin", slot="asset_audit",
        extra_kwargs={"connect_timeout": 3, "send_receive_timeout": 180})


def _asset_run_audit() -> None:
    """库内资产审计（后台线程）：列结构→每表一次列扫描聚合→交易日历对齐→内存缓存渐进更新。

    口径（Owner 2026-09-10 裁定）：
    - 宽度=表内 distinct symbol（应有=股票全历史清单，仅全宇宙白名单表展示应有数）
    - 深度=min~max 日期列实际值（非分区粒度，精确到日）
    - 完整度/缺口按表自身频率口径（freq 字段，_asset_freq_of）：日频=实际出现交易日 ∩ trade_calendar
      在 [min,max] 区间的基准（占比 ≥90% 才按交易日口径算，新闻等 7×24 表不算缺口防误报）；
      周K/月K/季频=应出周期数比对（ISO 周/自然月/自然季）；事件驱动表标注"事件"不报缺口
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
        rec["freq"] = freq = _asset_freq_of(tbl, dc)
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
                        # 完整度/缺口按表自身频率口径（freq）：日频维持交易日历比对；周/月/季按"应出周期数
                        # 比对"（bar 日期=周期内最后交易日，与日历同周期映射）；事件口径不报——行随事件出现，
                        # 无每日覆盖语义。事件型日期列（announce_date/list_date/publish_time…）天然稀疏，
                        # 按交易日全覆盖算同样必出伪缺口，不参与。
                        span = {x for x in tbl_cal if rec["dmin"] <= x <= rec["dmax"]}
                        if freq == "event":
                            pass   # 事件口径：前端标注"事件"，无完整度/缺口
                        elif span and dates and str(dc).lower() in ("trade_date", "date", "cal_date"):
                            inter = dates & span
                            if freq in ("weekly", "monthly", "quarterly"):
                                got = {_asset_period_key(x, freq) for x in inter}
                                exp = {_asset_period_key(x, freq) for x in span}
                                if exp:
                                    rec["completeness"] = round(len(got & exp) / len(exp) * 100, 1)
                                    rec["gap_days"] = max(0, len(exp) - len(got & exp))
                            elif len(inter) / len(dates) >= 0.9:   # 排他防伪：7×24 混合表不算缺口
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
        # run_subprocess_hidden=trae_067 统一入口（CREATE_NO_WINDOW 治闪窗）；bytes+GBK
        # 显式解码治 UnicodeDecodeError 刷屏（text=True 在 PYTHONUTF8=1 环境撞 tasklist
        # GBK 输出，同 services_registry._run_decoded 2026-09-03 实证）
        from zephyr.shared.infra.process_pool import run_subprocess_hidden as _rsh

        r = _rsh(["tasklist", "/FI", "IMAGENAME eq XtMiniQmt.exe"], capture_output=True, timeout=5)
        mini_alive = "XtMiniQmt.exe" in (r.stdout or b"").decode("gbk", errors="replace")
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
            "red_reason": n.get("red_reason"),   # v1.10 红因徽标（structural/pending_gate/not_built/terminal）
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


# ═══════════════ 策略生产全景图/策略工厂（真源 config/strategy_production_map.yaml，图 9 供给端） ═══════════════

_FACTORY_CACHE: dict[str, Any] = {}           # /api/factory mtime 缓存（改 YAML 即失效重算，同 /api/tdm 模式）
_FACTORY_LEDGER: dict[str, Any] = {"built_at": 0.0, "payload": None}
_FACTORY_LEDGER_TTL = 300.0                   # 台账统计缓存 5 分钟（台账只增，低频变更）
# 节点 → strategy_screen 行归属过滤（只读统计；未列出的节点=尚未接管台账行，前端空态留位）。
# SQL 经 _ch_exec 恒带 params dict → clickhouse_driver 做 % 格式化，LIKE 通配符必须写 %%（与 _SQL_TABLE_FRESH 同款）
_FACTORY_NODE_FILTERS: dict[str, str] = {
    "FAC-E1":  "screen_batch LIKE 'C2-intake%%'",                       # 进货台账全量（现阶段只有车道A有货）
    "FAC-E1A": "screen_batch LIKE 'C2-intake%%'",                       # 车道A=社区货源（C1 人工版 597 条）
    "FAC-E3":  "screen_batch LIKE 'C4-translated%%'",                   # 翻译件（translated+deferred 同批）
    "FAC-E4":  "verdict IN ('translated_c4', 'oos_tested')",           # 考试过手=IS 成绩行+OOS 成绩行
    "FAC-E6":  "verdict = 'failed_obsolete' OR oos_years_decay >= 0.5",  # 入库监控=失效章+年衰减≥0.5 存疑
}
_FACTORY_DECAY_SUSPECT = 0.5                  # DDL 注释口径：oos_years_decay>=0.5 判存疑（MOD-BT-078 同源）


def _factory_ledger() -> dict[str, Any]:
    """strategy_screen 台账统计（只读；TTL 缓存）。CH 不可达降级 ok:false——画布照常渲染，成绩区显降级。

    双窗及格判定与 scripts/backtest/strategy_screen_query.py bothwin 同口径只读复算：
    IS Sharpe>0 且每段 OOS Sharpe>0 且年衰减率<0.5；判定只读不落库（lifecycle 变更属规则册治理动作）。
    """
    now = time.time()
    if _FACTORY_LEDGER["payload"] and now - _FACTORY_LEDGER["built_at"] < _FACTORY_LEDGER_TTL:
        return _FACTORY_LEDGER["payload"]
    try:
        total, uniq = _ch_exec(
            "SELECT count(), uniqExact(strategy_id) FROM c1_backtest.strategy_screen")[0]
        batches = [
            {"batch": b, "verdict": v, "rows": n}
            for b, v, n in _ch_exec(
                "SELECT screen_batch, verdict, count() FROM c1_backtest.strategy_screen"
                " GROUP BY screen_batch, verdict ORDER BY screen_batch, verdict")
        ]
        reasons = [
            {"reason": r, "rows": n}
            for r, n in _ch_exec(
                "SELECT verdict_reason, count() FROM c1_backtest.strategy_screen"
                " WHERE verdict IN ('deferred_c4', 'rejected', 'failed_obsolete')"
                " GROUP BY verdict_reason ORDER BY count() DESC LIMIT 12")
        ]
        is_rows = _ch_exec(
            "SELECT strategy_id, is_sharpe FROM c1_backtest.strategy_screen"
            " WHERE screen_batch LIKE 'C4-translated%%' AND verdict = 'translated_c4'")
        oos_rows = _ch_exec(
            "SELECT strategy_id, screen_batch, is_sharpe, oos_years_decay"
            " FROM c1_backtest.strategy_screen WHERE verdict = 'oos_tested' ORDER BY screen_batch")
        oos_map: dict[str, list[dict[str, Any]]] = {}
        for sid, batch, sh, decay in oos_rows:
            oos_map.setdefault(sid, []).append({"batch": batch, "sharpe": sh, "decay": decay})
        bothwin = []
        for sid, is_sh in is_rows:
            segs = oos_map.get(sid, [])
            if not segs:
                continue
            passed = (is_sh or 0) > 0 and all(
                (s["sharpe"] or 0) > 0 and (s["decay"] is None or s["decay"] < _FACTORY_DECAY_SUSPECT)
                for s in segs)
            if passed:
                bothwin.append({"strategy_id": sid, "is_sharpe": is_sh, "segments": segs})
        bothwin.sort(key=lambda x: -(x["is_sharpe"] or 0))
        node_stats: dict[str, Any] = {}
        for nid, cond in _FACTORY_NODE_FILTERS.items():
            rows = _ch_exec(
                "SELECT verdict, count(), max(is_sharpe)"
                f" FROM c1_backtest.strategy_screen WHERE {cond} GROUP BY verdict")
            breakdown = [{"verdict": v, "rows": n, "sharpe_max": mx} for v, n, mx in rows]
            node_stats[nid] = {"total": sum(b["rows"] for b in breakdown), "breakdown": breakdown}
        # 理由码分布（节点级，抽屉条形图数据源）：E1A=筛出理由（C2 批），E3=挂起/失效理由（C4 翻译批）。
        # batch_like 写 %% —— _ch_exec 恒带 params dict 做 % 格式化（本文件 _FACTORY_NODE_FILTERS 同款坑）
        for nid, batch_like in (("FAC-E1A", "C2-intake%%"), ("FAC-E3", "C4-translated%%")):
            node_stats[nid]["reasons"] = [
                {"reason": r, "rows": n}
                for r, n in _ch_exec(
                    "SELECT verdict_reason, count() FROM c1_backtest.strategy_screen"
                    " WHERE verdict IN ('deferred_c4', 'rejected', 'failed_obsolete')"
                    f" AND screen_batch LIKE '{batch_like}'"
                    " GROUP BY verdict_reason ORDER BY count() DESC LIMIT 8")
            ]
        out: dict[str, Any] = {
            "ok": True,
            "global": {"total": total, "uniq_strategy": uniq, "batches": batches,
                       "failure_reasons": reasons},
            "nodes": node_stats,
            "bothwin": {"gate": "IS>0 且每段样本>0 且年衰减率<0.5",
                        "tested": len(oos_map), "passed": len(bothwin),
                        "items": bothwin[:10]},
            "generated_at": now_utc().isoformat(" ", "seconds"),
        }
    except Exception as exc:   # 台账不可达不阻断地图——降级披露，画布零依赖
        logger.warning("factory ledger query failed: %s", exc)
        out = {"ok": False, "reason": f"台账不可达: {exc}", "nodes": {}, "global": {},
               "bothwin": {"tested": 0, "passed": 0, "items": []}}
    _FACTORY_LEDGER["built_at"] = now
    _FACTORY_LEDGER["payload"] = out
    return out


@app.get("/api/factory")
def factory_map() -> dict[str, Any]:
    """策略生产全景图全量（前端原生渲染真源）——真源=config/strategy_production_map.yaml（图 9 供给端）。

    每请求按 mtime 缓存（改 YAML 即自动生效，无需重启）；payload=nodes+edges+layers+laws+
    feedback_loops+ref_names（MOD 中文名复用 TDM 翻译源，零硬编码）。
    消费者=web/features/factory/factory.js（策略工厂页，交互范式学 tdm 页，Owner 2026-09-14 指定）。
    """
    p = _REPO / "config" / "strategy_production_map.yaml"
    mtime = p.stat().st_mtime
    cached = _FACTORY_CACHE.get("mtime")
    if cached == mtime and _FACTORY_CACHE.get("payload"):
        return _FACTORY_CACHE["payload"]

    import yaml as _yaml

    raw = _yaml.safe_load(p.read_text(encoding="utf-8"))
    nodes_out = []
    for n in raw.get("nodes", []):
        note = str(n.get("algo_note_zh") or "").replace("\n", " ").strip()
        while "。 " in note:
            note = note.replace("。 ", "。")
        nodes_out.append({
            "id": n.get("node_id", ""),
            "name": n.get("name_zh", ""),
            "q": n.get("decision_question", ""),
            "note": note,
            "stage": n.get("stage"),
            "node_type": n.get("node_type"),
            "lane": n.get("lane"),
            "build_status": n.get("build_status"),
            "compute_class": n.get("compute_class"),
            "module_ref": n.get("module_ref"),
            "data_refs": n.get("data_refs") or [],
            "design_refs": n.get("design_refs") or [],
            "store_refs": n.get("store_refs") or [],
        })
    payload = {
        "ok": True,
        "map_id": raw.get("map_id"),
        "name_zh": raw.get("name_zh"),
        "nickname": raw.get("nickname"),
        "schema_version": raw.get("schema_version"),
        "laws": raw.get("laws", []),
        "products": raw.get("products", []),
        "layers": raw.get("layers", []),
        "nodes": nodes_out,
        "edges": raw.get("edges", []),
        "feedback_loops": raw.get("feedback_loops", []),
        "ref_names": _tdm_ref_names(),   # MOD-*/策略/数据集中文名翻译真源复用（零硬编码翻译）
        "generated_at": now_utc().isoformat(" ", "seconds"),
    }
    _FACTORY_CACHE["mtime"] = mtime
    _FACTORY_CACHE["payload"] = payload
    return payload


@app.get("/api/factory/ledger")
def factory_ledger() -> dict[str, Any]:
    """工厂台账统计（只读）——strategy_screen 行按环节归属聚合+双窗及格名单+理由码分布。

    消费者=web/features/factory/factory.js（卡片策略数徽标+抽屉「台账成绩」区+顶栏总览条）；
    TTL 300s 缓存，CH 不可达降级 ok:false（画布照常，成绩区显降级说明）。
    """
    return _factory_ledger()


_THREEHIGH_CACHE: dict[str, Any] = {"mtime": None, "payload": None}
_THREEHIGH_CSV = _REPO / "data" / "strategy_intake" / "three_high_candidates.csv"


@app.get("/api/factory/threehigh")
def factory_threehigh() -> dict[str, Any]:
    """E1D 三高候选榜（只读）——真源=data/strategy_intake/three_high_candidates.csv（MOD-BT-090 产出）。

    追加台账按 birth_batch 分组（批 id=E1D-YYYYMMDD-HHMMSS 字典序=时序），最新批在前；
    文件未生成（模块已落码未首跑）=ok:true+空批+hint 不冒充失败；
    消费者=web/features/factory/factory.js FAC-E1D 抽屉「三高候选榜」区。
    """
    p = _THREEHIGH_CSV
    if not p.exists():
        return {"ok": True, "batches": [], "total_rows": 0,
                "hint": "E1D 模块已落码（MOD-BT-090）未首跑——three_high_screen screen 后自动亮起",
                "generated_at": now_utc().isoformat(" ", "seconds")}
    mtime = p.stat().st_mtime
    if _THREEHIGH_CACHE["mtime"] == mtime and _THREEHIGH_CACHE["payload"]:
        return _THREEHIGH_CACHE["payload"]
    import csv as _csv

    try:
        with p.open(encoding="utf-8-sig", newline="") as f:
            rows = [r for r in _csv.DictReader(f) if r.get("candidate_id")]
    except OSError as exc:
        return {"ok": False, "reason": f"台账不可读: {exc}", "batches": []}
    num_cols = ("members", "fin_coverage", "rev_yoy_med", "profit_yoy_med", "gross_margin_med",
                "net_margin_med", "cust_top5_med", "hhi_med", "downstream_breadth",
                "supply_pressure", "growth_z", "margin_z", "barrier_z", "choke_z", "total_z")
    keep = ("candidate_id", "sector", "three_high_flags", "hypothesis_zh", "birth_batch", "birth_source")
    items: list[dict[str, Any]] = []
    for r in rows:
        it: dict[str, Any] = {k: r.get(k, "") for k in keep}
        for k in num_cols:
            try:
                it[k] = float(r[k]) if r.get(k) not in (None, "") else None
            except ValueError:
                it[k] = None
        items.append(it)
    batches: dict[str, list[dict[str, Any]]] = {}
    for it in items:
        batches.setdefault(it["birth_batch"], []).append(it)
    out_batches = []
    for b in sorted(batches, reverse=True):
        items_b = sorted(batches[b], key=lambda x: -(x["total_z"] or 0))
        out_batches.append({"batch": b, "count": len(items_b), "items": items_b})
    payload: dict[str, Any] = {"ok": True, "batches": out_batches, "total_rows": len(items),
                               "generated_at": now_utc().isoformat(" ", "seconds")}
    _THREEHIGH_CACHE["mtime"] = mtime
    _THREEHIGH_CACHE["payload"] = payload
    return payload


# ═══════════════ 产业地图 chainmap（真源 ig_* 七表，depgraph PG 只读；Owner 2026-09-08 三层缩放方案） ═══════════════

_CM_MARKETS = ("all", "cn", "global")   # 市场过滤档（项 4）：all=全部链（基线口径），cn/global=ig_chain.market 单档
_CM_GALAXY_CACHE: dict[str, dict[str, Any]] = {}                     # market → {data, ts}（L1 星系，TTL 600s）
_CM_CLUSTER_CACHE: dict[tuple[str, str], dict[str, Any]] = {}        # (market, cid) → L2 簇详情（随 galaxy 失联失效）
_CM_NAME_CACHE: dict[str, Any] = {"map": None, "ts": 0.0}             # symbol→公司名映射（ig_company_edge 名称列，覆盖不全如实用）
_CM_NAME_OVERRIDE_PATH = _REPO / "config" / "chainmap_cluster_names.yaml"   # L1 族名 override（Commit C 规则版，mtime 缓存改 YAML 即生效）
_CM_NAME_OVERRIDE: dict[str, Any] = {"mtime": None, "map": {}}

_CM_EQUITY_ROWS_CAP = 8   # 环节股权徽章明细行上限（计数 out/inn 如实给全量，明细 hover 浮层展示前 N）

# 2026-09-12 tier 退役终章：列=链内拓扑层号 L1..Ln（_cm_chain_cols 从 ig_edge 结构推导），
# 散点/环/存量兜底一律"未分层"——不再出现 上游/中游/下游/通用 字样（tier 字段停止人工填写）。
# function_role 八值（深交所课题词表）→ 列内分组展示序：按产业链流向 原料→辅材→设备→辅设→工艺→产品→服务→渠道
_CM_FR_ORDER = ["生产原料", "辅助材料", "生产设备", "辅助设备", "加工工艺", "产品业务", "技术服务", "销售渠道"]


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
    """col 展示值中性化（2026-09-12 tier 退役终章）：不再输出 上游/中游/下游 字样，
    一律落"未分层"（tier 已停止人工填写，层位由 _cm_chain_cols 拓扑推导为 L1..Ln）。"""
    return "未分层"


def _cm_chain_layers(nodes: list[tuple[str, str]], edges: list[tuple[str, str]]) -> dict[str, int]:
    """链内拓扑分层 → 整数层号（0 基；iFinD 等距布局参数，2026-09-12 前端重构批）。

    Kahn 剥洋葱：入度0=第 0 层，逐层推进。分层失败（链内成环）或链内零边散点 → -1（未分层）。
    层号只做前端布局参数，不作为可见标签（Owner 2026-09-12 裁定）。
    nodes=[(node_id, tier)]（tier 参数仅为签名兼容，已不再消费），edges=[(from,to)]。
    """
    ids = {nid for nid, _t in nodes}
    layers = {nid: -1 for nid in ids}
    indeg0 = {nid: 0 for nid in ids}
    outdeg = {nid: 0 for nid in ids}
    adj: dict[str, list[str]] = {nid: [] for nid in ids}
    n_inner = 0
    for a, b in edges:
        if a in ids and b in ids and a != b:
            adj[a].append(b)
            indeg0[b] += 1
            outdeg[a] += 1
            n_inner += 1
    if n_inner == 0:
        return layers
    indeg = dict(indeg0)
    frontier = [nid for nid, d in indeg.items() if d == 0]
    if not frontier:          # 全部入度>=1 → 链内成环，整体 fallback
        return layers
    depth = 0
    seen: set[str] = set()
    while frontier:
        nxt: list[str] = []
        for u in frontier:
            layers[u] = depth
            seen.add(u)
            for v in adj[u]:
                indeg[v] -= 1
                if indeg[v] == 0:
                    nxt.append(v)
        frontier = nxt
        depth += 1
    for nid in ids:           # 环上节点/链内零边散点 → 未分层（-1，兼容原 col 口径）
        if nid not in seen or (indeg0[nid] == 0 and outdeg[nid] == 0):
            layers[nid] = -1
    return layers


def _cm_chain_cols(nodes: list[tuple[str, str]], edges: list[tuple[str, str]]) -> dict[str, str]:
    """层号列字符串（L1..Ln/未分层）——向后兼容包装，新消费方用 _cm_chain_layers。"""
    layers = _cm_chain_layers(nodes, edges)
    return {nid: ("未分层" if v < 0 else f"L{v + 1}") for nid, v in layers.items()}


# iFinD 职能分区（2026-09-12 前端重构批）：区名只做底板标题，无任何 上游/中游/下游 字样
_CM_ZONE_NAMES = ["材料与零部件", "装备", "工艺", "产品", "服务"]
_CM_FR_ZONE = {"生产原料": 0, "辅助材料": 0, "生产设备": 1, "辅助设备": 1,
               "加工工艺": 2, "产品业务": 3, "技术服务": 4, "销售渠道": 4}


def _cm_node_zones(names: dict[str, str], froles: dict[str, str], indeg: dict[str, int]) -> dict[str, int]:
    """环节 → 职能分区索引（0..4，iFinD 底板分区参数）。

    function_role 八值直接映射 _CM_FR_ZONE；fr 空=拓扑兜底（链内入度0→材料区0，入度>0→产品区3）；
    「X（全球）」跟随基础节点 X 的分区（X 同链内任一节点）。"""
    zones: dict[str, int] = {}
    for nid, name in names.items():
        if "（全球）" in name:
            continue
        f = (froles.get(nid) or "").strip()
        zones[nid] = _CM_FR_ZONE.get(f, 0 if indeg.get(nid, 0) == 0 else 3)
    by_name = {n: i for i, n in names.items()}
    for nid, name in names.items():
        if nid in zones or "（全球）" not in name:
            continue
        base_id = by_name.get(name[:name.index("（全球）")])
        if base_id is not None and base_id in zones:
            zones[nid] = zones[base_id]
        else:
            zones[nid] = 0 if indeg.get(nid, 0) == 0 else 3
    return zones


def _cm_fr_rank(function_role: str | None) -> int:
    """function_role 列内分组序（未知值/空殿后）。"""
    f = (function_role or "").strip()
    return _CM_FR_ORDER.index(f) if f in _CM_FR_ORDER else len(_CM_FR_ORDER)


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


def _cm_build_galaxy(market: str = "all") -> dict[str, Any]:
    """链→族聚类：跨链结构边+公司供应链边投影到链对 → 确定性模块度局部移动（Louvain 式单层，γ=3.5）→ 小簇并入最强邻居（≤48 簇）。

    纯 Python 无新依赖；簇名=簇内连接度最高的枢纽链名。结果缓存 600s（按 market 分档，项 4）。
    market=all=全部 active 链（基线口径，四闸验收档）；cn/global=ig_chain.market 单档过滤——
    过滤在聚类输入侧（链清单先收敛，跨链边/公司投影经 chain_name 白名单自然截断），counts 真实反映。
    """
    conn = _cm_pg()
    try:
        cur = conn.cursor()
        if market == "all":
            cur.execute("SELECT chain_id, name, market FROM ig_chain WHERE status = 'active'")
        else:
            cur.execute("SELECT chain_id, name, market FROM ig_chain WHERE status = 'active' AND market = %s",
                        (market,))
        chain_rows = cur.fetchall()
        chain_name: dict[str, str] = {r[0]: r[1] for r in chain_rows}
        chain_market: dict[str, str] = {r[0]: (r[2] or "cn") for r in chain_rows}
        cur.execute(_SQL_CM_NODES_ALL)
        node_chain: dict[str, str] = {r[0]: r[1] for r in cur.fetchall()}
        cur.execute("SELECT node_id, count(DISTINCT symbol) FROM ig_node_company WHERE valid_to IS NULL GROUP BY node_id")
        node_companies: dict[str, int] = {r[0]: int(r[1]) for r in cur.fetchall()}
        cur.execute("SELECT DISTINCT node_id, symbol FROM ig_node_company WHERE valid_to IS NULL")
        sym_chains: dict[str, set[str]] = {}
        for nid, sym in cur.fetchall():
            c = node_chain.get(nid)
            if c:
                sym_chains.setdefault(sym, set()).add(c)
        cur.execute("SELECT from_node, to_node FROM ig_edge WHERE valid_to IS NULL")  # 2026-09-12: 已关闭边不参与 galaxy 链对权重
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
        # 族名=枢纽链名去括号（Owner 2026-09-10 裁定：不加"族"尾缀——簇名直接用行业名，
        # 如"食品加工制造行业"；与链名同字串无妨，簇 id(C01) 与链 id 不同维度）
        base = chain_name[hub].split("（")[0].split("(")[0].strip() or chain_name[hub]
        cluster_stats.append({
            "root": root, "members": members, "hub": hub, "name": base,
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
                               "market": chain_market[m],
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
            "market": market,
            "generated_at": datetime.now().isoformat(" ", "seconds")}


def _cm_galaxy(market: str = "all") -> dict[str, Any]:
    ent = _CM_GALAXY_CACHE.get(market)
    if ent and (time.time() - ent["ts"]) < 600:
        g = ent["data"]
        try:   # Commit C：族名 override 改 YAML 即生效（mtime 变化→绕过 TTL 强制重建）
            if _CM_NAME_OVERRIDE_PATH.stat().st_mtime != _CM_NAME_OVERRIDE["mtime"]:
                g = None
        except OSError:
            pass
        if g:
            return g
    g = _cm_build_galaxy(market)
    _CM_GALAXY_CACHE[market] = {"data": g, "ts": time.time()}
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
def chainmap_galaxy(market: str = Query("all", pattern="^(all|cn|global)$")) -> dict[str, Any]:
    """产业地图 L1 星系（chainmap-galaxy 组件）：族节点+族间边+全量链清单（导航树同源）。

    market 过滤档（项 4）：all=全部链（默认，基线口径）/cn/global——聚类输入侧过滤，
    clusters/links/chains counts 随档真实变化，各档独立缓存。"""
    try:
        g = _cm_galaxy(market)
        return {"ok": True, **g}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "clusters": [], "links": [], "chains": []}


def _cm_s21_flags(chains_out: list[dict[str, Any]], chain_edges_in: dict[str, list[tuple[str, str]]]) -> dict[str, dict[str, Any]]:
    """S21 流程连通性链级标记（B7，需求卡 2026-09-11/全部开工 2026-09-14）：口径移植引擎
    scripts/industry_graph/graph_quality_check._check_s21（2026-09-12 拓扑端点版）——
    墓碑节点（名含"（已并入"）不计；实质节点≥3 且非行业锚点链才判；
    入度0=源头/出度0=终端，无向 BFS 起点→终端可达=合规，端点缺失/不可达=断链。
    簇内子图规模小，请求内现算零新表；advisory 语义由前端 ⚠ 弱化标注承载（不删卡）。"""
    out: dict[str, dict[str, Any]] = {}
    for ch in chains_out:
        cid = ch["chain_id"]
        alive = [n for n in ch["nodes"] if "（已并入" not in (n.get("name") or "")]
        if len(alive) < 3:
            continue
        cname = ch.get("name") or ""
        alive_names = {n.get("name") or "" for n in alive}
        if alive_names <= {cname, cname + "行业", "行业聚合"}:
            continue
        alive_ids = {n["node_id"] for n in alive}
        edges = [(a, b) for a, b in chain_edges_in.get(cid, []) if a in alive_ids and b in alive_ids]
        indeg: dict[str, int] = {}
        outdeg: dict[str, int] = {}
        adj: dict[str, list[str]] = {}
        for a, b in edges:
            outdeg[b] = outdeg.get(b, 0) + 1
            indeg[a] = indeg.get(a, 0) + 1
            adj.setdefault(a, []).append(b)
            adj.setdefault(b, []).append(a)
        alive_list = list(alive_ids)
        starts = [n for n in alive_list if indeg.get(n, 0) == 0]
        targets = {n for n in alive_list if outdeg.get(n, 0) == 0}
        reason = ""
        if not starts and not targets:
            reason = "无拓扑端点(环/散点)"
        else:
            seen = set(starts)
            queue = list(starts)
            hit = False
            while queue and not hit:
                u = queue.pop()
                if u in targets:
                    hit = True
                    break
                for v in adj.get(u, []):
                    if v not in seen:
                        seen.add(v)
                        queue.append(v)
            if not hit:
                if not starts:
                    reason = "无源头端点(入度均>=1,疑环)"
                elif not targets:
                    reason = "无终端端点(出度均>=1,疑环)"
                else:
                    reason = "拓扑端点间无连通路径"
        if reason:
            out[cid] = {"s21_broken": True,
                        "s21_note": "S21 流程连通性：%s（实质环节 %d，结构边 %d）" % (reason, len(alive_ids), len(edges))}
    return out


@app.get("/api/chainmap-cluster")
def chainmap_cluster(cid: str = Query(..., min_length=2, max_length=8),
                     market: str = Query("all", pattern="^(all|cn|global)$")) -> dict[str, Any]:
    """产业地图 L2 链层（chainmap-cluster 组件）：簇内链→环节（tier 三值分列 + function_role 组内聚集）+结构边+公司计数。

    market 与 galaxy 同档取簇（cid 是 per-market 聚类空间，跨档 cid 不存在→cluster not found）。"""
    if not cid.replace("C", "").isdigit():
        return {"ok": False, "error": "bad cid", "chains": []}
    cached = _CM_CLUSTER_CACHE.get((market, cid))
    if cached:
        return {"ok": True, **cached}
    try:
        g = _cm_galaxy(market)
        members = [c for c in g["chains"] if c["cluster"] == cid]
        if not members:
            return {"ok": False, "error": "cluster not found", "chains": []}
        cluster = next(c for c in g["clusters"] if c["id"] == cid)
        conn = _cm_pg()
        try:
            cur = conn.cursor()
            ids = [c["chain_id"] for c in members]
            cur.execute(_SQL_CM_NODES_BY_CHAIN, (ids,))
            node_rows = cur.fetchall()
            cur.execute(_SQL_CM_NODE_COMPS_BY_CHAIN, (ids,))
            ncomp = {r[0]: int(r[1]) for r in cur.fetchall()}
            # 股权批量聚合（F-CHAINMAP-EQUITY-BADGE，2026-09-10）：簇内环节落位公司 ∩ ig_equity_edge 参与方。
            # 方向按落位公司是 holder（控=对外投资）/held（被控=股东）判；UE 编码对手方 LEFT JOIN 编码表取名；
            # 簇级 LIMIT 防大簇失控（计数在前端按行累加，明细行每环节另截 _CM_EQUITY_ROWS_CAP）
            cur.execute(_SQL_CM_EQ_AGG, (ids, ids))
            eq_rows = cur.fetchall()
            # edge_type 随边输出（iFinD 流向线红蓝分类：supply 系=红，其余=蓝）；已关闭边(edge_close PIT)不参与
            cur.execute("SELECT from_node, to_node, COALESCE(edge_type, '') FROM ig_edge WHERE valid_to IS NULL")
            all_edges = cur.fetchall()
            cur.execute(_SQL_CM_NODE_TOPCOMPS_BY_CHAIN, (ids,))
            topcomp_rows = cur.fetchall()
            # B5 下钻子链元数据（child_chain_id→子链名/族归属）：须在 conn.close() 前查
            cc_ids = {r[5] for r in node_rows if len(r) > 5 and r[5]}
            cc_meta: dict[str, dict[str, str]] = {}
            if cc_ids:
                cur.execute("SELECT chain_id, name FROM ig_chain WHERE chain_id = ANY(%s)", (list(cc_ids),))
                cc_names = {r[0]: r[1] for r in cur.fetchall()}
                cc_cluster = {c["chain_id"]: c.get("cluster", "") for c in g["chains"]}
                for _cc in cc_ids:
                    if _cc in cc_names:
                        cc_meta[_cc] = {"chain_id": _cc, "name": cc_names[_cc], "cluster": cc_cluster.get(_cc, "")}
            conn.close()
        except Exception:
            try:
                conn.close()
            except Exception:
                pass
            raise
        nodes_by_chain: dict[str, list[dict[str, Any]]] = {c["chain_id"]: [] for c in members}
        nid_set = {r[0] for r in node_rows}
        eq_names = _cm_symbol_names()
        # 节点直挂公司 chip 名单（每环节前 4 家；排序同抽屉 _cm_role_rank，名字映射同源）
        _tc_group: dict[str, list[tuple[str, str, Any]]] = {}
        for _nid, _sym, _role, _cf in topcomp_rows:
            _tc_group.setdefault(_nid, []).append((_sym, _role or "", _cf))
        topcomps: dict[str, list[dict[str, Any]]] = {}
        for _nid, _lst in _tc_group.items():
            _lst.sort(key=lambda x: (_cm_role_rank(x[1]), -(x[2] if x[2] is not None else 0), x[0]))
            topcomps[_nid] = [{"symbol": _s, "name": eq_names.get(_s, ""), "role": _r}
                              for _s, _r, _cf in _lst[:8]]
        eq_by_node: dict[str, dict[str, Any]] = {}
        for nid, dirn, other, stake, rel, verif, asof, uename in eq_rows:
            agg = eq_by_node.setdefault(nid, {"out": 0, "inn": 0, "rows": []})
            non_local = str(other or "").startswith(("PERSON:", "UNLISTED:"))
            agg["out" if dirn == "out" else "inn"] += 1
            if len(agg["rows"]) < _CM_EQUITY_ROWS_CAP:
                agg["rows"].append({
                    "dir": dirn, "symbol": "" if non_local else other,
                    "name": (uename or "") if non_local else eq_names.get(other, ""),
                    "ref": str(other) if non_local else "",
                    "stake_pct": None if stake is None else round(float(stake), 2),
                    "relation": rel or "", "verification": verif or "",
                    "as_of": str(asof) if asof else None,
                })
        # 拓扑分层列（2026-09-12 tier 退役裁定）：列由链内边结构派生（入度0=上游列/最末层=下游列），
        # 存量 tier 仅作环/散点节点的 fallback 展示——列结构与前端组件契约不变
        node_chain_of = {r[0]: r[1] for r in node_rows}
        chain_nodes: dict[str, list[tuple[str, str]]] = {c["chain_id"]: [] for c in members}
        chain_edges_in: dict[str, list[tuple[str, str]]] = {}
        for a, b, _rel in all_edges:
            ca, cb = node_chain_of.get(a), node_chain_of.get(b)
            if ca is not None and ca == cb:
                chain_edges_in.setdefault(ca, []).append((a, b))
        for nid, ch, name, tier, frole, _cc, _al in node_rows:
            chain_nodes.setdefault(ch, []).append((nid, tier or ""))
        # 布局参数（iFinD 等距流程图前端重构 2026-09-12）：layer=拓扑层 int（-1 未分层）/
        # zone=职能分区 int（0..4，区名 _CM_ZONE_NAMES）；col 字符串保留向后兼容，前端不再消费
        colmap: dict[str, str] = {}
        layermap: dict[str, int] = {}
        zonemap: dict[str, int] = {}
        chain_meta: dict[str, tuple[dict[str, str], dict[str, str], dict[str, int]]] = {}
        for nid, ch, name, tier, frole, _cc, _al in node_rows:
            names_m, fr_m, indeg_m = chain_meta.setdefault(ch, ({}, {}, {}))
            names_m[nid] = name
            fr_m[nid] = (frole or "").strip()
        for _ch, nl in chain_nodes.items():
            inner = chain_edges_in.get(_ch, [])
            colmap.update(_cm_chain_cols(nl, inner))
            layermap.update(_cm_chain_layers(nl, inner))
            _nm, _fr, indeg_m = chain_meta.setdefault(_ch, ({}, {}, {}))
            for a, b in inner:
                if a != b:
                    indeg_m[b] = indeg_m.get(b, 0) + 1
        for _ch, (names_m, fr_m, indeg_m) in chain_meta.items():
            for _nid, _z in _cm_node_zones(names_m, fr_m, indeg_m).items():
                zonemap[_nid] = _z
        # B5 下钻（child_chain_id）+环节别名（aliases）：元数据已在 conn.close() 前查好（cc_meta）
        import json as _json
        for nid, ch, name, tier, frole, _cc, _al in node_rows:
            entry = {"node_id": nid, "name": name, "tier": tier or "",
                     "col": colmap.get(nid) or _cm_col(tier),
                     "layer": layermap.get(nid, -1), "zone": zonemap.get(nid, 0),
                     "function_role": (frole or "").strip(),
                     "n_companies": ncomp.get(nid, 0), "equity": eq_by_node.get(nid),
                     "companies": topcomps.get(nid, [])}
            if _cc and _cc in cc_meta:
                entry["child_chain"] = cc_meta[_cc]
            if _al:
                try:
                    al = _json.loads(_al) if isinstance(_al, str) else _al
                    if isinstance(al, list) and al:
                        entry["aliases"] = [str(x) for x in al][:6]
                except Exception:
                    pass
            nodes_by_chain[ch].append(entry)
        for lst in nodes_by_chain.values():
            # 链内按 function_role 分组聚集（八值展示序），同组内公司数降序（项 2 分列适配）
            lst.sort(key=lambda n: (_cm_fr_rank(n["function_role"]), -n["n_companies"], n["name"]))
        chains_out = [{**c, "nodes": nodes_by_chain[c["chain_id"]]} for c in
                      sorted(members, key=lambda c: -c["n_companies"])]
        edges_out = [[a, b, rel] for a, b, rel in all_edges if a in nid_set and b in nid_set]
        # S21 流程连通性链级标记（B7）：断链链挂 s21_broken/s21_note，前端 ⚠ 弱化标注
        s21 = _cm_s21_flags(chains_out, chain_edges_in)
        for _c in chains_out:
            if _c["chain_id"] in s21:
                _c.update(s21[_c["chain_id"]])
        data = {"cluster": cluster, "chains": chains_out, "edges": edges_out, "market": market}
        _CM_CLUSTER_CACHE[(market, cid)] = data
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
            cur.execute("SELECT n.name, n.tier, n.chain_id, c.name, n.function_role FROM ig_node n "
                        "JOIN ig_chain c ON c.chain_id = n.chain_id WHERE n.node_id = %s"
                        " AND n.name NOT LIKE '%%（已并入%%'", (node_id,))
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
                                     "chain_id": row[2], "chain_name": row[3],
                                     "function_role": (row[4] or "").strip()},
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
                        "JOIN ig_chain c ON c.chain_id = n.chain_id WHERE c.status = 'active' AND n.name ILIKE %s AND n.name NOT LIKE '%%（已并入%%' "
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


# ═══════════════ 产业链催化剂锚定（chainmap 剩余批任务2，F-CHAINMAP-CATALYST，2026-09-10） ═══════════════
# 语义边界（Owner 红线）：只做"事件命中定位"，不做涨跌/传导预测——热度传导预测已被证伪裁定（月 IC=-0.029 留档）。
# 判定真源（禁止臆断）：MOD-ALT-005 policy_theme_mapper.DEFAULT_THEME_LIBRARY 直引——主题关键词词表与
# 主题→申万行业受益/受损映射为既有判定；分类规则=该模块规则分支同语义（关键词子串命中，库序首个命中即断）。
# 事件真源：CH calendar_event（宏观事件日历，/api/events 同源同库）。
# 命中粒度（如实声明）：主题→申万一级行业→ig_chain.category→链上环节投影；环节级独立命中判定既有真源
# 不存在，不造（ACC-F-CHAINMAP-CATALYST 留痕）。行业别名表仅做名字归一，不改方向判定。
_CM_CAT_WINDOW_BACK = 30   # 已发生事件回看天
_CM_CAT_WINDOW_FWD = 90    # 未来事件前瞻天
_CM_CAT_EVENTS_CAP = 40    # 响应事件条数上限（total 如实返回）
_CM_CAT_NODE_HITS_CAP = 6  # 单环节催化角标命中明细上限
# MOD-ALT-005 受益/受损行业名 → 申万一级词表（ig_chain.category）机械别名（仅名字归一；
# 国产替代/出口链/航运 等概念名无机械对应 → unmapped 如实返回不硬凑）
_CM_CAT_IND_ALIAS: dict[str, str] = {
    "银行": "银行", "非银金融": "非银金融", "房地产": "房地产", "半导体": "半导体",
    "新能源": "电力设备", "高端装备": "机械设备", "工程机械": "机械设备",
    "建筑": "建筑装饰", "建材": "建筑材料", "农业": "农林牧渔", "互联网": "互联网服务",
}

# 裸 SQL 集中化（R96 常量豁免通道；NOQA-VALIDATION 密度闸否决行级 noqa 后的正道）：
# chainmap 只读诊断 SQL，参数化绑定无注入面，与既有 chainmap 段手写 execute 同一读口径
# 墓碑过滤统一口径(NO-BARE-SQL 集中化;墓碑=已合并历史快照,S8/S21/S24/api 同口径)
# 2026-09-12 增：valid_to IS NULL（node_close/edge_close PIT 收口后，已关闭节点/边不参与地图）
_SQL_CM_NODES_ALL = ("SELECT node_id, chain_id FROM ig_node"
                     " WHERE name NOT LIKE '%%（已并入%%' AND valid_to IS NULL")
_SQL_CM_NODES_BY_CHAIN = (
    "SELECT node_id, chain_id, name, tier, function_role, child_chain_id, aliases FROM ig_node"
    " WHERE chain_id = ANY(%s) AND name NOT LIKE '%%（已并入%%' AND valid_to IS NULL"
)
_SQL_CM_NODE_COMPS_BY_CHAIN = (
    "SELECT node_id, count(DISTINCT symbol) FROM ig_node_company WHERE valid_to IS NULL AND node_id IN "
    "(SELECT node_id FROM ig_node WHERE chain_id = ANY(%s) AND name NOT LIKE '%%（已并入%%' AND valid_to IS NULL) GROUP BY node_id"
)
# iFinD 节点直挂公司 chip（2026-09-12 前端重构批）：每环节前 8 家名单（锚点大块直挂 8 家/普通节点取前 4；
# 排序在 Python 侧 _cm_role_rank，与 /api/chainmap-node 抽屉同口径同 PIT 过滤；LIMIT 防大簇失控，
# 计数仍以 _SQL_CM_NODE_COMPS_BY_CHAIN 为准）
_SQL_CM_NODE_TOPCOMPS_BY_CHAIN = (
    "SELECT node_id, symbol, role, confidence FROM ig_node_company"
    " WHERE valid_to IS NULL AND node_id IN (SELECT node_id FROM ig_node"
    " WHERE chain_id = ANY(%s) AND name NOT LIKE '%%（已并入%%' AND valid_to IS NULL) LIMIT 6000"
)
_SQL_CM_EQ_AGG = (
    "SELECT node_id, dir, other, stake_pct, relation, verification, as_of, ue_name FROM ("
    "SELECT nc.node_id, 'out' AS dir, e.held AS other, e.stake_pct, e.relation, e.verification, e.as_of, "
    "ue.name AS ue_name FROM ig_equity_edge e "
    "JOIN ig_node_company nc ON nc.valid_to IS NULL AND nc.symbol = e.holder "
    "AND nc.node_id IN (SELECT node_id FROM ig_node WHERE chain_id = ANY(%s)) "
    "LEFT JOIN ig_unlisted_entity ue ON 'UNLISTED:UE-' || ue.ue_id = e.held "
    "WHERE e.valid_to IS NULL "
    "UNION ALL "
    "SELECT nc.node_id, 'in', e.holder, e.stake_pct, e.relation, e.verification, e.as_of, ue2.name "
    "FROM ig_equity_edge e "
    "JOIN ig_node_company nc ON nc.valid_to IS NULL AND nc.symbol = e.held "
    "AND nc.node_id IN (SELECT node_id FROM ig_node WHERE chain_id = ANY(%s)) "
    "LEFT JOIN ig_unlisted_entity ue2 ON 'UNLISTED:UE-' || ue2.ue_id = e.holder "
    "WHERE e.valid_to IS NULL) q LIMIT 800"
)
_SQL_CM_CAT_EVENTS = (
    "SELECT event_date, event_type, description FROM calendar_event "
    "WHERE event_date >= today() - %(b)s AND event_date <= today() + %(f)s ORDER BY event_date"
)
_SQL_CM_CAT_CLUSTER_CHAINS = "SELECT chain_id, category FROM ig_chain WHERE chain_id = ANY(%s)"
_SQL_CM_CAT_CLUSTER_HIT_NODES = "SELECT node_id, chain_id FROM ig_node WHERE chain_id = ANY(%s) AND name NOT LIKE '%%（已并入%%'"
_SQL_CM_CAT_NODE_INFO = (
    "SELECT n.name, n.tier, n.chain_id, c.name, c.category FROM ig_node n "
    "JOIN ig_chain c ON c.chain_id = n.chain_id WHERE n.node_id = %s"
)
_SQL_CM_CAT_NODE_COMPS = (
    "SELECT symbol, role, confidence FROM ig_node_company "
    "WHERE valid_to IS NULL AND node_id = %s"
)
# 详情卡 news_keywords/calendar 域点亮（遗留修复 2026-09-10：数据侧真表已就绪——
# news_data 816 万行、近 7 天 1.3 万行活跃灌入；disclosure_plan/share_unlock 为
# MOD-DATA-068 event_calendar_filler 同源装配口径。aliases/facilities 无实表维持建设中）
from typing import Final

from zephyr.data.table_registry import get_registry

_TBL_CM_NEWS_DATA: Final[str] = get_registry().table("fund_news_data")
_TBL_CM_DISCLOSURE: Final[str] = get_registry().table("fund_disclosure_plan")
_TBL_CM_UNLOCK: Final[str] = get_registry().table("fund_share_unlock")
_SQL_CM_NEWS_KW = (
    f"SELECT keyword, count() FROM {_TBL_CM_NEWS_DATA} "
    "WHERE quality_flag = 1 AND arrayExists(x -> x = %(s)s, related_symbols) "
    "AND keyword != '' AND publish_time >= now() - INTERVAL 30 DAY "
    "GROUP BY keyword ORDER BY count() DESC LIMIT 12"
)
_SQL_CM_NEWS_LATEST = (
    f"SELECT title, publish_time FROM {_TBL_CM_NEWS_DATA} "
    "WHERE quality_flag = 1 AND arrayExists(x -> x = %(s)s, related_symbols) "
    "AND publish_time >= now() - INTERVAL 30 DAY ORDER BY publish_time DESC LIMIT 3"
)
_SQL_CM_NEWS_COUNT = (
    f"SELECT count() FROM {_TBL_CM_NEWS_DATA} "
    "WHERE quality_flag = 1 AND arrayExists(x -> x = %(s)s, related_symbols) "
    "AND publish_time >= now() - INTERVAL 30 DAY"
)
_SQL_CM_CAL_DISCLOSURE = (
    f"SELECT report_period, scheduled_date, actual_date FROM {_TBL_CM_DISCLOSURE} "
    "WHERE symbol = %(s)s AND (toDate(scheduled_date) >= today() - 400 OR toDate(actual_date) >= today() - 400) "
    "ORDER BY coalesce(toDate(actual_date), toDate(scheduled_date)) DESC LIMIT 6"
)
_SQL_CM_CAL_UNLOCK = (
    f"SELECT unlock_date, shares, ratio FROM {_TBL_CM_UNLOCK} "
    "WHERE symbol = %(s)s AND unlock_date >= today() - 400 ORDER BY unlock_date DESC LIMIT 6"
)


def _cm_cat_themes() -> list[dict[str, Any]]:
    """MOD-ALT-005 主题库直引（import 失败→空表独立降级，端点回零命中空态禁崩）。"""
    try:
        from zephyr.alt_data.policy_theme_mapper import DEFAULT_THEME_LIBRARY

        return [{"theme_id": t.theme_id, "keywords": list(t.keywords),
                 "beneficiary": list(t.beneficiary_industries), "damaged": list(t.damaged_industries)}
                for t in DEFAULT_THEME_LIBRARY]
    except Exception as exc:
        logger.warning("chainmap-catalyst 主题库加载失败（回零命中空态）: %s", exc)
        return []


def _cm_cat_classify(text: str, themes: list[dict[str, Any]]) -> dict[str, Any] | None:
    """规则分支同语义分类（MOD-ALT-005 规则路径：关键词子串命中，库序首个命中即断）。"""
    hay = (text or "").lower()
    for t in themes:
        if any(k.lower() in hay for k in t["keywords"]):
            return t
    return None


def _cm_cat_events() -> tuple[list[dict[str, Any]], int]:
    """事件窗扫描+主题分类（CH/主题库异常独立降级→空）。返回 (命中事件, 扫描总数)。

    遗留修复 enrich（2026-09-10）：并入 MOD-DATA-068 macro_rule_events 规则推导宏观
    事件（LPR/MLF/PMI/CPI，certainty 分级）——MLF/PMI/CPI 为 calendar_event 稀缺
    语料的真实扩充；按 (日期,主题) 与 calendar_event 行去重防同事件双计。
    """
    try:
        rows = _ch_exec(_SQL_CM_CAT_EVENTS, {"b": _CM_CAT_WINDOW_BACK, "f": _CM_CAT_WINDOW_FWD})
    except Exception as exc:
        logger.warning("chainmap-catalyst 事件窗查询失败（回零命中空态）: %s", exc)
        return [], 0
    themes = _cm_cat_themes()
    today = date.today()
    out: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for d, et, desc in rows:
        t = _cm_cat_classify(str(et) + " " + str(desc), themes)
        if t:
            out.append({"date": d.isoformat(), "type": str(et)[:40], "description": str(desc)[:120],
                        "is_future": d > today, "theme": t})
            seen.add((d.isoformat(), t["theme_id"]))
    # 规则推导宏观事件（MOD-DATA-068，fail-open 单源跳过）
    try:
        from datetime import timedelta as _td

        from zephyr.data.event_calendar_filler import macro_rule_events

        for en in macro_rule_events(today - _td(days=_CM_CAT_WINDOW_BACK),
                                    today + _td(days=_CM_CAT_WINDOW_FWD)):
            t = _cm_cat_classify(f"{en.event_type} {en.description or en.event_type}", themes)
            if not t:
                continue
            key = (en.event_date.isoformat(), t["theme_id"])
            if key in seen:
                continue
            seen.add(key)
            out.append({"date": en.event_date.isoformat(), "type": str(en.event_type)[:40],
                        "description": (en.description or en.event_type)[:120],
                        "is_future": en.event_date > today, "theme": t})
    except Exception as exc:
        logger.warning("chainmap-catalyst 规则事件装配失败（跳过该源）: %s", exc)
    return out, len(rows)


def _cm_cat_theme_categories(theme: dict[str, Any]) -> tuple[list[str], list[str]]:
    """主题受益/受损行业 → 申万 category 列表（别名归一；无法归一的进 unmapped）。"""
    cats: list[str] = []
    unmapped: list[str] = []
    for ind in list(theme["beneficiary"]) + list(theme["damaged"]):
        c = _CM_CAT_IND_ALIAS.get(ind)
        if c and c not in cats:
            cats.append(c)
        elif not c and ind not in unmapped:
            unmapped.append(ind)
    return cats, unmapped


@app.get("/api/chainmap-catalyst")
def chainmap_catalyst(cid: str | None = Query(None, min_length=2, max_length=8),
                      market: str = Query("all", pattern="^(all|cn|global)$"),
                      node_id: str | None = Query(None, min_length=1)) -> dict[str, Any]:
    """产业链催化剂（F-CHAINMAP-CATALYST）：宏观事件→主题→行业→链/环节命中定位+受益清单。

    两种用法：?cid=&market= 簇内环节催化角标数据（nodes 映射，chainmap-cluster 装饰用）；
    ?node_id= 单环节受益清单（环节落位公司+命中事件方向语义，方向=MOD-ALT-005 受益/受损既有判定，
    粒度=链级投影如实声明）。零命中=ok:true 空态（禁造映射充数）。
    """
    # 直调安全归一（进程内测试/脚本直调时 Query 默认对象→None；HTTP 路径 FastAPI 已解析为 str）
    if not isinstance(cid, str):
        cid = None
    if not isinstance(node_id, str):
        node_id = None
    if not node_id and not (cid and cid.replace("C", "").isdigit()):
        return {"ok": False, "error": "need cid or node_id", "events": [], "nodes": {}, "beneficiaries": []}
    try:
        events, scanned = _cm_cat_events()
        if node_id:
            return _cm_cat_node_view(node_id, events)
        return _cm_cat_cluster_view(cid or "", market, events, scanned)
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "events": [], "nodes": {}, "beneficiaries": []}


def _cm_cat_cluster_events(events: list[dict[str, Any]], members: list[dict[str, Any]],
                           chain_cat: dict[str, str], cat_chains: dict[str, list[str]]) -> tuple[list, set, set]:
    """事件→簇内链命中解析（簇视角第一段）：返回 (事件明细≤CAP, 命中链集合, unmapped 行业)。"""
    name_of = {m["chain_id"]: m["name"] for m in members}
    events_out: list[dict[str, Any]] = []
    hit_chain_ids: set[str] = set()
    unmapped: set[str] = set()
    for ev in events:
        cats, unm = _cm_cat_theme_categories(ev["theme"])
        unmapped.update(unm)
        hit_chains = [{"chain_id": ch, "chain_name": name_of.get(ch, ""), "category": cat}
                      for cat in cats for ch in cat_chains.get(cat, []) if ch in chain_cat]
        if not hit_chains:
            continue
        hit_chain_ids.update(h["chain_id"] for h in hit_chains)
        if len(events_out) < _CM_CAT_EVENTS_CAP:
            events_out.append({"date": ev["date"], "type": ev["type"], "description": ev["description"],
                               "is_future": ev["is_future"], "theme_id": ev["theme"]["theme_id"],
                               "chains": hit_chains})
    return events_out, hit_chain_ids, unmapped


def _cm_cat_node_flags(events: list[dict[str, Any]], cat_chains: dict[str, list[str]],
                       node_chain_map: dict[str, str]) -> dict[str, list[dict[str, Any]]]:
    """环节→命中事件映射（簇视角第二段）：环节所在链 category 与事件主题映射求交，方向=主题级。"""
    node_flags: dict[str, list[dict[str, Any]]] = {}
    for ev in events:
        cats, _unm = _cm_cat_theme_categories(ev["theme"])
        hit_for_ev = [ch_id for cat in cats for ch_id in cat_chains.get(cat, [])]
        if not hit_for_ev:
            continue
        direction = "受益" if any(
            _CM_CAT_IND_ALIAS.get(i) in cats for i in ev["theme"]["beneficiary"]) else "受损"
        hit_set = set(hit_for_ev)
        for nid, nch in node_chain_map.items():
            if nch not in hit_set:
                continue
            lst = node_flags.setdefault(nid, [])
            if len(lst) < _CM_CAT_NODE_HITS_CAP:
                lst.append({"date": ev["date"], "is_future": ev["is_future"],
                            "theme_id": ev["theme"]["theme_id"], "direction": direction,
                            "description": ev["description"]})
    return node_flags


def _cm_cat_cluster_view(cid: str, market: str, events: list[dict[str, Any]], scanned: int) -> dict[str, Any]:
    """簇视角：scope 内链 category 命中 → 环节催化角标映射（F-CHAINMAP-CATALYST 簇模式）。"""
    g = _cm_galaxy(market)
    members = [c for c in g["chains"] if c["cluster"] == cid]
    if not members:
        return {"ok": False, "error": "cluster not found", "events": [], "nodes": {}}
    conn = _cm_pg()
    try:
        cur = conn.cursor()
        ids = [c["chain_id"] for c in members]
        cur.execute(_SQL_CM_CAT_CLUSTER_CHAINS, (ids,))
        chain_cat = {r[0]: (r[1] or "").strip() for r in cur.fetchall()}
        cat_chains: dict[str, list[str]] = {}
        for ch_id, cat in chain_cat.items():
            if cat:
                cat_chains.setdefault(cat, []).append(ch_id)
        events_out, hit_chain_ids, unmapped = _cm_cat_cluster_events(events, members, chain_cat, cat_chains)
        node_flags: dict[str, list[dict[str, Any]]] = {}
        if hit_chain_ids:
            cur.execute(_SQL_CM_CAT_CLUSTER_HIT_NODES, (sorted(hit_chain_ids),))
            node_flags = _cm_cat_node_flags(events, cat_chains, dict(cur.fetchall()))
        conn.close()
    except Exception:
        try:
            conn.close()
        except Exception:
            pass
        raise
    return {"ok": True, "mode": "cluster", "cluster": cid, "market": market,
            "events": events_out, "n_events_scanned": scanned, "n_hit_events": len(events_out),
            "nodes": node_flags, "unmapped_industries": sorted(unmapped)}


def _cm_cat_node_view(node_id: str, events: list[dict[str, Any]]) -> dict[str, Any]:
    """环节视角：命中事件方向语义+环节落位受益清单（F-CHAINMAP-CATALYST 抽屉模式）。"""
    conn = _cm_pg()
    try:
        cur = conn.cursor()
        cur.execute(_SQL_CM_CAT_NODE_INFO, (node_id,))
        row = cur.fetchone()
        if not row:
            return {"ok": False, "error": "node not found", "events": [], "beneficiaries": []}
        category = (row[4] or "").strip()
        cur.execute(_SQL_CM_CAT_NODE_COMPS, (node_id,))
        comp_rows = cur.fetchall()
        conn.close()
    except Exception:
        try:
            conn.close()
        except Exception:
            pass
        raise
    import re as _re

    names = _cm_symbol_names()
    hits: list[dict[str, Any]] = []
    for ev in events:
        cats, unm = _cm_cat_theme_categories(ev["theme"])
        if category not in cats:
            continue
        direction = "受益" if category in {_CM_CAT_IND_ALIAS.get(i) for i in ev["theme"]["beneficiary"]} else "受损"
        hits.append({"date": ev["date"], "type": ev["type"], "description": ev["description"],
                     "is_future": ev["is_future"], "theme_id": ev["theme"]["theme_id"],
                     "direction": direction, "industries": [i for i, c in
                     [(i, _CM_CAT_IND_ALIAS.get(i)) for i in list(ev["theme"]["beneficiary"]) + list(ev["theme"]["damaged"])] if c == category],
                     "unmapped": unm})
    companies = [{"symbol": s, "name": names.get(s, ""), "role": r or "",
                  "confidence": None if cf is None else round(float(cf), 2),
                  "jump": bool(_re.fullmatch(r"\d{6}\.(SH|SZ|BJ)", s or ""))}
                 for s, r, cf in comp_rows]
    companies.sort(key=lambda x: (_cm_role_rank(x["role"]), -(x["confidence"] or 0), x["symbol"]))
    return {"ok": True, "mode": "node",
            "node": {"node_id": node_id, "name": row[0], "tier": row[1] or "",
                     "chain_id": row[2], "chain_name": row[3], "category": category},
            "hits": hits[:_CM_CAT_EVENTS_CAP], "n_hits": len(hits),
            "beneficiaries": companies[:_CM_PLACEMENT_CAP], "n_beneficiaries": len(companies),
            "note": "命中粒度=主题→申万行业→链级投影；受益方向=MOD-ALT-005 既有判定；不做涨跌预测（证伪裁定留档）"}


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


def _cm_equity(sym: str, names: dict[str, str]) -> dict[str, Any]:
    """股权域（ig_equity_edge 查询侧 UNION 拼装——数据物理只存股权表一处，节点模板 v0.5 §2.5）。

    holdings_in=我投了谁（holder=本司）；held_by=谁投了我（held=本司）。
    relation 封闭枚举：invests_in/subsidiary/shareholding/actual_control/pledge/judicial_frozen；
    PERSON:/UNLISTED: 前缀持有方按原样展示（对手方名称映射覆盖不全为已知边界，缺名回 CH stock_basic）。
    独立降级：查询异常→空结构（不拖垮图谱段）。
    """
    out: dict[str, Any] = {"holdings_in": [], "held_by": [], "n_holdings": 0, "n_held": 0}

    def _name_of(ref: str) -> str:
        return names.get(ref, "")

    def _row(holder: str, held: str, stake, layer, relation, verif, as_of) -> dict[str, Any]:
        other = held if holder == sym else holder
        non_local = other.startswith(("PERSON:", "UNLISTED:"))
        return {
            "symbol": "" if non_local else other,
            "name": _name_of(other) if not non_local else "",
            "ref": other if non_local else "",
            "stake_pct": None if stake is None else round(float(stake), 2),
            "layer": int(layer) if layer is not None else 1,
            "relation": relation or "",
            "verification": verif or "",
            "as_of": str(as_of) if as_of else None,
        }

    try:
        conn = _cm_pg()
        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT holder, held, stake_pct, layer, relation, verification, as_of FROM ig_equity_edge "
                "WHERE valid_to IS NULL AND holder = %s ORDER BY stake_pct DESC NULLS LAST, held",
                (sym,),
            )
            rows_in = cur.fetchall()
            cur.execute(
                "SELECT holder, held, stake_pct, layer, relation, verification, as_of FROM ig_equity_edge "
                "WHERE valid_to IS NULL AND held = %s ORDER BY stake_pct DESC NULLS LAST, holder",
                (sym,),
            )
            rows_by = cur.fetchall()
            conn.close()
        except Exception:
            try:
                conn.close()
            except Exception:
                pass
            raise
        out["holdings_in"] = [_row(h, d, s, l, r, v, a) for h, d, s, l, r, v, a in rows_in]
        out["held_by"] = [_row(h, d, s, l, r, v, a) for h, d, s, l, r, v, a in rows_by]
        out["n_holdings"] = len(out["holdings_in"])
        out["n_held"] = len(out["held_by"])
    except Exception:
        return out   # 独立降级：股权段缺失不影响图谱五段
    return out


def _cm_profile(bare: str) -> dict[str, Any]:
    """基本盘/全球属性（有什么展示什么，缺列如实标未入库禁编造——任务书项 3 口径）。

    实测列源（2026-09-10 DESCRIBE）：stock_basic=exchange/board/list_date（无 country/st 列）；
    daily_valuation.is_st（0/1）；stock_profile_ths=industry_ths_l1/l2/l3。
    country/hq_location/listing_status 无实列 → missing_fields 声明（listing_status 无法判退市：
    stock_basic 全量在册不含退市行，禁推标记）。独立降级：CH 异常→空结构。
    """
    out: dict[str, Any] = {
        "country": None, "listing_venue": None, "board": None, "listing_date": None,
        "st_flag": None, "industry_ths": None,
        "missing_fields": ["country", "hq_location", "listing_status"],
    }
    try:
        rows = _ch_exec(
            "SELECT argMax(exchange, valid_from), argMax(board, valid_from), argMax(list_date, valid_from) "
            "FROM stock_basic WHERE symbol=%(s)s",
            {"s": bare},
        )
        if rows:
            ex, bd, ld = rows[0]
            if ex:
                out["listing_venue"] = {"SH": "上交所", "SZ": "深交所", "BJ": "北交所"}.get(str(ex), str(ex))
            if bd:
                out["board"] = str(bd)
            if ld:
                out["listing_date"] = str(ld)
        st = _ch_exec(
            "SELECT trade_date, is_st FROM daily_valuation WHERE symbol=%(s)s ORDER BY trade_date DESC LIMIT 1",
            {"s": bare},
        )
        if st:
            out["st_flag"] = bool(st[0][1])
            out["st_asof"] = str(st[0][0])
        ths = _ch_exec(
            "SELECT argMax(industry_ths_l1, trade_date), argMax(industry_ths_l2, trade_date), "
            "argMax(industry_ths_l3, trade_date) FROM stock_profile_ths WHERE symbol=%(s)s",
            {"s": bare},
        )
        if ths and any(ths[0]):
            out["industry_ths"] = [str(x) for x in ths[0] if x]
    except Exception:
        return out   # 独立降级
    return out


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


def _cm_news_keywords(bare: str) -> dict[str, Any]:
    """news_keywords 域点亮（遗留修复 2026-09-10）：c3_fundamental.news_data 真表
    （近 30 天，quality_flag=1，related_symbols 命中本司）——top 关键词+最新标题+条数。
    独立降级：CH 异常→空结构。"""
    out: dict[str, Any] = {"keywords": [], "latest": [], "n_news": 0}
    try:
        rows = _ch_exec(_SQL_CM_NEWS_KW, {"s": bare})
        out["keywords"] = [{"keyword": str(r[0]), "n": int(r[1])} for r in rows]
        rows2 = _ch_exec(_SQL_CM_NEWS_LATEST, {"s": bare})
        out["latest"] = [{"title": str(r[0]), "date": str(r[1])[:16]} for r in rows2]
        rows3 = _ch_exec(_SQL_CM_NEWS_COUNT, {"s": bare})
        out["n_news"] = int(rows3[0][0]) if rows3 else 0
    except Exception:
        return out   # 独立降级
    return out


def _cm_stock_calendar(bare: str) -> dict[str, Any]:
    """calendar 域点亮（遗留修复 2026-09-10）：disclosure_plan 财报披露预约/实际 +
    share_unlock 限售解禁（口径对齐 MOD-DATA-068 event_calendar_filler 装配 SQL）。
    独立降级：CH 异常→空结构。"""
    out: dict[str, Any] = {"disclosures": [], "unlocks": [], "n_disclosures": 0, "n_unlocks": 0}
    try:
        rows = _ch_exec(_SQL_CM_CAL_DISCLOSURE, {"s": bare})
        out["disclosures"] = [{"report_period": str(r[0]),
                               "scheduled": str(r[1]) if r[1] else None,
                               "actual": str(r[2]) if r[2] else None} for r in rows]
        rows2 = _ch_exec(_SQL_CM_CAL_UNLOCK, {"s": bare})
        out["unlocks"] = [{"date": str(r[0]),
                           "shares": None if r[1] is None else float(r[1]),
                           "ratio": None if r[2] is None else round(float(r[2]), 2)} for r in rows2]
        out["n_disclosures"] = len(out["disclosures"])
        out["n_unlocks"] = len(out["unlocks"])
    except Exception:
        return out   # 独立降级
    return out


@app.get("/api/chainmap-company")
def chainmap_company(symbol: str = Query(..., min_length=2, max_length=24)) -> dict[str, Any]:
    """公司详情卡（chainmap-company-card 真源）：链上落位 + 上下游关系 + CH 行情/估算市值 + 股权域 + 基本盘。

    symbol 接受 6 位裸码或带 .SH/.SZ/.BJ 后缀（统一归一）；海外/UNLISTED 端点不支持（fail-closed）。
    关系段：suppliers=to_symbol=本司（from 为供应商）；customers=from_symbol=本司（to 为客户）；
    collabs=预留段（J88 勘误后归 supply，当前恒空，字段保留兼容 ACC item1 五段契约）；
    对手方未上市 symbol='' 用 to_name/from_name 展示。
    七域扩展（任务书项 3，2026-09-10）：equity=股权域（ig_equity_edge UNION 拼装 holdings_in/held_by）；
    profile=基本盘/全球属性（stock_basic/daily_valuation.is_st/stock_profile_ths 实列，缺列如实
    missing_fields）；pending_domains=库中无实表域（news_keywords/aliases/facilities/calendar）留位
    标"建设中"禁编造。行情/股权/基本盘三段各自独立降级，互不拖垮图谱段。
    """
    import re as _re

    sym = (symbol or "").strip().upper()
    if not _re.fullmatch(r"\d{6}(\.(SH|SZ|BJ))?", sym):
        return {"ok": False, "error": "bad symbol", "company": {"symbol": sym},
                "placements": [], "suppliers": [], "customers": [], "collabs": [], "quote": None,
                "equity": {"holdings_in": [], "held_by": [], "n_holdings": 0, "n_held": 0},
                "profile": {}, "pending_domains": []}
    if "." not in sym:   # 裸码补后缀（与 load_supply_top5_483.to_symbol 同规则）
        sym += {"6": ".SH"}.get(sym[0], ".SZ") if sym[0] in "03" else (".SH" if sym[0] == "6" else ".BJ")
    empty = {"ok": False, "error": "", "company": {"symbol": sym, "name": None},
             "placements": [], "suppliers": [], "customers": [], "collabs": [], "quote": None,
             "equity": {"holdings_in": [], "held_by": [], "n_holdings": 0, "n_held": 0},
             "profile": {}, "pending_domains": []}
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
        "equity": _cm_equity(sym, names),
        "profile": _cm_profile(_cm_bare_symbol(sym)),
        "news": _cm_news_keywords(_cm_bare_symbol(sym)),
        "stock_calendar": _cm_stock_calendar(_cm_bare_symbol(sym)),
        "pending_domains": ["aliases", "facilities"],
        "generated_at": datetime.now().isoformat(" ", "seconds"),
    }


@app.get("/api/chain-impact-stream")
def chain_impact_stream_endpoint(
    minutes: int = Query(30, ge=5, le=240),
    min_confidence: float = Query(0.0, ge=0.0, le=1.0),
) -> dict[str, Any]:
    """盘中事件冲击流（只读拉式）：新闻分钟窗→情绪→产业链节点传导→冲击标的清单。

    消费方=偏离监控/盘中扫描/负面否决。数据源=c3_fundamental.news_data
    （入库延迟实测 2026-09-10：p50≈6min/p90≈13min）+ ig_* 产业链图谱。
    接线指令 W5 交付；实现真源=zephyr.intelligence.chain_impact_stream（MOD-INT-IMPACT-STREAM）。
    """
    from zephyr.intelligence.chain_impact_stream import ChainImpactStream

    try:
        snap = ChainImpactStream(window_minutes=minutes).run()
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"[:200], "items": [], "all_targets": []}
    payload = snap.to_dict()
    if min_confidence > 0:
        payload["all_targets"] = [t for t in payload["all_targets"] if t["confidence"] >= min_confidence]
        for it in payload["items"]:
            it["targets"] = [t for t in it["targets"] if t["confidence"] >= min_confidence]
    return payload


# ── 图形库消费端三端点（消费班方案 v1.0 C4/W-C4，MOD-SIG-147 线，只读） ─────────


@app.get("/api/pattern-events")
def pattern_events(
    symbol: str = Query(..., min_length=1),
    days_back: int = Query(90, ge=0, le=3650),
    limit: int = Query(200, ge=1, le=2000),
    pattern_class: str = Query("", min_length=0, max_length=16),
) -> dict[str, Any]:
    """形态事件查询（c1_market.market_pattern_event，按 symbol 倒序）。

    symbol=纯数字代码（与 kline_daily 同口径）；只读；异常 ok:false。
    """
    sym = symbol.split(".")[0].strip()
    if not sym.isalnum():
        return {"ok": False, "error": "bad symbol", "data": []}
    try:
        sql = (
            "SELECT pattern_id, name, pattern_class, direction, confidence, "
            "timeframe, anchor_trade_date, confirmed_at, regime_tag "
            "FROM c1_market.market_pattern_event "
            "WHERE symbol = %(s)s AND confirmed_at >= now() - INTERVAL %(d)s DAY"
        )
        params: dict = {"s": sym, "d": int(days_back)}
        if pattern_class:
            sql += " AND pattern_class = %(pc)s"
            params["pc"] = pattern_class
        sql += " ORDER BY confirmed_at DESC LIMIT %(l)d"
        params["l"] = int(limit)
        rows = _ch_exec(sql, params)
        data = [
            {
                "pattern_id": r[0],
                "name": r[1],
                "pattern_class": r[2],
                "direction": r[3],
                "confidence": r[4],
                "timeframe": r[5],
                "anchor_trade_date": r[6].isoformat() if r[6] is not None else None,
                "confirmed_at": r[7].isoformat() if r[7] is not None else None,
                "regime_tag": r[8],
            }
            for r in rows
        ]
        return {"ok": True, "count": len(data), "symbol": sym, "data": data}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "data": []}


@app.get("/api/pattern-winrate")
def pattern_winrate(
    timeframe: str = Query("day", min_length=1, max_length=8),
    direction: str = Query("", min_length=0, max_length=8),
    fwd_window: int = Query(10, ge=1, le=120),
    regime_tag: str = Query("", min_length=0, max_length=16),
    min_n: int = Query(30, ge=0, le=100000000),
    limit: int = Query(500, ge=1, le=5000),
) -> dict[str, Any]:
    """形态胜率查询（c1_market.market_pattern_win_rate，四窗×regime 切片）。

    min_n=样本数下限（默认 30=low_sample 纪律线，0=全量）；按 Wilson 下界
    降序返回（前端双格式展示：hit_rate%+n_events 并列）。
    """
    try:
        sql = (
            "SELECT pattern_id, timeframe, direction, fwd_window, regime_tag, "
            "hit_rate, n_events, low_sample FROM c1_market.market_pattern_win_rate "
            "FINAL WHERE timeframe = %(tf)s AND fwd_window = %(w)d "
            "AND n_events >= %(mn)d"
        )
        params: dict = {"tf": timeframe, "w": int(fwd_window), "mn": int(min_n)}
        if direction:
            sql += " AND direction = %(d)s"
            params["d"] = direction
        if regime_tag:
            sql += " AND regime_tag = %(rt)s"
            params["rt"] = regime_tag
        sql += " ORDER BY hit_rate DESC LIMIT %(l)d"
        params["l"] = int(limit)
        rows = _ch_exec(sql, params)
        # 认证列（两次查询 Python 合并——CH 老版 JOIN 子查询受限，MOD-SIG-148 表池化键）
        try:
            cert_rows = _ch_exec(
                "SELECT pattern_id, state, shrunk_rate FROM c1_market.market_pattern_certification "
                "FINAL WHERE timeframe = %(tf)s AND direction = %(d)s AND fwd_window = %(w)d",
                {"tf": timeframe, "d": direction or "向上", "w": int(fwd_window)},
            )
            cert_map = {r[0]: (r[1], r[2]) for r in cert_rows}
        except Exception:  # noqa: BLE001 —— 认证列降级为空（主数据不受影响）
            cert_map = {}
        data = [
            {
                "pattern_id": r[0],
                "timeframe": r[1],
                "direction": r[2],
                "fwd_window": r[3],
                "regime_tag": r[4],
                "hit_rate": r[5],
                "n_events": r[6],
                "low_sample": bool(r[7]),
                "cert_state": cert_map.get(r[0], (None, None))[0],
                "shrunk_rate": cert_map.get(r[0], (None, None))[1],
            }
            for r in rows
        ]
        return {"ok": True, "count": len(data), "data": data}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "data": []}


@app.get("/api/pattern-evidence")
def pattern_evidence(
    pattern_id: str = Query("", min_length=0, max_length=32),
) -> dict[str, Any]:
    """形态证据查询（REG-PAT-001 evidence 字段直读，只读）。

    返回有机生证据的条目（evidence 非空）；pattern_id 精确过滤可选。
    """
    from pathlib import Path

    import yaml

    try:
        repo_root = Path(__file__).resolve().parents[4]
        reg_path = (
            repo_root
            / "docs/01_policies_and_standards/_registry/catalogs/chart_pattern_registry.yaml"
        )
        if not reg_path.exists():
            return {"ok": False, "error": "registry missing", "data": []}
        reg = yaml.safe_load(reg_path.read_text(encoding="utf-8"))
        out: list[dict[str, Any]] = []
        total = 0
        for p in reg.get("chart_patterns", []) or []:
            ev = p.get("evidence") or ""
            if not ev:
                continue
            total += 1
            if pattern_id and p.get("pattern_id") != pattern_id:
                continue
            out.append(
                {
                    "pattern_id": p.get("pattern_id"),
                    "name_zh": p.get("name_zh"),
                    "status": p.get("status"),
                    "evidence": ev,
                    "code_symbol": p.get("code_symbol"),
                }
            )
        return {"ok": True, "count": len(out), "evidence_total": total, "data": out}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "data": []}


# ── 策略转正审批两端点（C5 / S13 前端转正汇报页配套，2026-09-15）──────────────
# 执行器真源：zephyr.strategy_pipeline.promotion_advisory（Y1 并行施工，本端点只做 HTTP 投影，
# FSM 流转/注册表写入/决策台账全在执行器侧——端点层零业务语义，禁在此自造判定）。
# 授权：POST 端点=api_server 第四个获准写端点，头注 [INVARIANTS] 已同步修订；
# 裁定登记（ruling_registry 同 commit 原子）由主会话收尾补登。


@app.get("/api/promotion-advisories")
def promotion_advisories() -> dict[str, Any]:
    """策略转正建议清单（C5 转正审批页数据源，只读）。

    真源：promotion_advisory.list_advisories()（元素含 advisory_id/strategy_id/lifecycle_now/
    evidence{sim_pass_months,sim_breach_months,fw_backtest{run_id,sharpe,max_dd,total_return,
    panel_ok}}/recommendation/generated_at/decision?）。
    模块未就绪/异常 → 200 + ok:false + 空列表 + error（前端渲染空态，不 500 硬崩）。
    """
    try:
        from zephyr.strategy_pipeline import promotion_advisory

        items = promotion_advisory.list_advisories() or []
        return {"ok": True, "count": len(items), "data": items}
    except Exception as exc:  # noqa: BLE001 — 执行器缺位/异常一律降级空态（Y1 未落地属常态）
        return {
            "ok": False,
            "error": f"promotion_advisory unavailable: {str(exc)[:200]}",
            "count": 0,
            "data": [],
        }


@app.post("/api/promotion-decide")
def promotion_decide(body: dict[str, Any]) -> dict[str, Any]:
    """Owner 拍板：approve（批准=进入整装组合，非单策略直进实盘）/ reject（驳回退回）。

    授权依据：Owner 2026-09-15 通宵自主执行指令 + 宪法 §5 人机门位数字化
    （production 流转属 high 域 Owner 门位，本端点=该门位的前端数字化承载；
    token=None 服务端自取密钥，前端不带凭据——S12 无签发体系前的最小半径）。
    body: {advisory_id, decision: approve|reject}
    执行器：promotion_advisory.decide(advisory_id, decision, token=None, via="frontend")
    → {ok, message, new_lifecycle?, receipt?}；业务拒绝=ok:false+原因（200 承载）。
    异常映射：decision/advisory_id 非法→400；执行器缺位→503；其余意外→500。
    """
    advisory_id = str(body.get("advisory_id", "")).strip()
    decision = str(body.get("decision", "")).strip()
    if not advisory_id:
        raise HTTPException(status_code=400, detail="advisory_id required")
    if decision not in ("approve", "reject"):
        raise HTTPException(status_code=400, detail="decision must be approve|reject")
    try:
        from zephyr.strategy_pipeline import promotion_advisory as _pa
    except Exception as exc:  # noqa: BLE001 — 执行器缺位=服务端依赖未就绪（503 语义）
        raise HTTPException(status_code=503, detail=f"promotion_advisory unavailable: {str(exc)[:200]}")
    if not hasattr(_pa, "decide"):  # 模块在册但执行器未就位（半成品）——同 503，不误报 500
        raise HTTPException(status_code=503, detail="promotion_advisory.decide unavailable (executor not ready)")
    try:
        result = _pa.decide(advisory_id, decision, token=None, via="frontend")
    except HTTPException:
        raise
    except FileNotFoundError as exc:  # 不存在的 advisory=业务拒绝（非服务器故障）
        return {"ok": False, "advisory_id": advisory_id, "reason": f"not_found: {str(exc)[:120]}"}
    except Exception as exc:  # noqa: BLE001 — 意外异常不带业务语义，500 交由日志排查
        raise HTTPException(status_code=500, detail=str(exc)[:300])
    if not isinstance(result, dict):
        return {"ok": False, "message": "executor returned non-dict result", "receipt": None}
    return result


def main() -> None:
    import ctypes

    import uvicorn

    # SEM_FAILCRITICALERRORS(0x8003)：子进程继承错误模式——子进程硬错误（如 schtasks
    # 0xc0000142 DLL 初始化失败）不再弹 GUI 对话框，只以非零退出码返回。
    # 背景 2026-09-12 弹窗风暴：病变 api_server 实例每次 schtasks /query 都弹窗，
    # 前端 60s 缓存轮询 → 每分钟多个弹窗。本防线保证同类故障只降级为状态灯红色。
    ctypes.windll.kernel32.SetErrorMode(0x8003)

    uvicorn.run(app, host="127.0.0.1", port=8890, log_level="warning")


if __name__ == "__main__":
    main()

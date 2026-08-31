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

app = FastAPI(title="ZephyrAlpha Dashboard API (read-only)")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET"], allow_headers=["*"])

_PERIOD_TABLE: dict[str, str] = {
    "1m": "kline_1min", "5m": "kline_5min", "15m": "kline_15min",
    "30m": "kline_30min", "60m": "kline_60min",
    "1d": "kline_daily", "1w": "kline_weekly", "1M": "kline_monthly",
}

_client: Client | None = None
_col_cache: dict[str, dict[str, str]] = {}


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


def _time_col(table: str) -> str:
    """首Date/DateTime 列为时间列（日线族=trade_date，分钟族=datetime 类）。"""
    if table in _col_cache:
        return _col_cache[table]["time_col"]
    cols = _ch().execute(f"DESCRIBE TABLE {table}")
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
        rows = _ch().execute(
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


def main() -> None:
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8890, log_level="warning")


if __name__ == "__main__":
    main()

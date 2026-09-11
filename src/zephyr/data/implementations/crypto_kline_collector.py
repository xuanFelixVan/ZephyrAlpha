#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# [BLUEPRINT] MOD-DATA-070 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §
# [MODULE] zephyr.data.implementations.crypto_kline_collector
# [DOMAIN] D_DATA
# [DEPENDENCIES] stdlib；zephyr.shared（按需）
# [CONSUMERS] 数据源集成器/币圈影子 MVP 验证批
# [STARTUP] manual
# noqa: m11-perm-manual-legitimate  M11豁免: 币圈影子 MVP 一次性验证脚本（A 类非永久，按需手动触发跑批出报告，无常驻进程）
# [MATURITY] testing
# [INVARIANTS] 影子采集零实盘副作用；免费公开端点无密钥；失败不阻塞主数据链
# [MODIFY-GUARD] 币圈影子 MVP 批（night-gw-2300）
# [STABILITY] volatile
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 采集失败返回非零退出码/空数据集，不抛入主链
# [TESTS] 无（影子 MVP 验证批随批补）
# [TTL-NOTE] 币圈影子 MVP 验证批：一次性手动跑批，验证完成即归档（勿改回 permanent——PERM-TRIGGER 将拒绝其时间触发模式）
# [TTL] task_bound
"""crypto_kline_collector.py — 币圈免费影子 MVP 采集脚本（OKX 公开行情，免 API key）。

真源：docs/02_enterprise_architecture/07_trading_decision_architecture/design_memos/95_crypto_system_blueprint.md
      + 2026-09-11 影子 MVP 会话指令（C-L1：BTC 200 日线趋势门 + 山寨季 75% Top-50/90 天滚动门 + 收紧档）。

两种模式：
  backfill     历史回填：默认 2019-01-01 起，走 /api/v5/market/history-candles 分页（时间倒序翻页）。
  incremental  每日增量：读 <out_dir>/<symbol>.csv 已有最大 trade_date，向后补齐（走 /api/v5/market/candles）。

输出：<out_dir>/<symbol>.csv（列：trade_date,open,high,low,close,volume,vol_ccy,bar,confirm；append 幂等去重）。

用法：
  python scripts/data/crypto_kline_collector.py backfill     --symbols BTC-USDT,ETH-USDT
  python scripts/data/crypto_kline_collector.py incremental  --symbols-file config/crypto_top50_usdt.yaml
不依赖第三方库（urllib 标准库实现）；限速：history-candles 20次/2s → 每次请求间隔 0.15s。

禁碰边界：本脚本只做公开行情采集落 CSV，不进 trading_decision_map、不碰 okx_broker。
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from typing import Final
import time
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

BASE_URL = "https://www.okx.com"
CANDLES_URL = f"{BASE_URL}/api/v5/market/candles"
HISTORY_CANDLES_URL = f"{BASE_URL}/api/v5/market/history-candles"

CSV_HEADER: Final = ["trade_date", "open", "high", "low", "close", "volume", "vol_ccy", "bar", "confirm"]

# 静态 Top-50 USDT 现货默认清单（2026-09 口径；动态 Top-50 属 Phase 2 付费解锁项，见 MVP 报告）
DEFAULT_TOP50: Final = [
    "BTC-USDT", "ETH-USDT", "SOL-USDT", "BNB-USDT", "XRP-USDT", "DOGE-USDT", "ADA-USDT",
    "TRX-USDT", "AVAX-USDT", "LINK-USDT", "TON-USDT", "DOT-USDT", "POL-USDT", "LTC-USDT",
    "BCH-USDT", "NEAR-USDT", "APT-USDT", "ARB-USDT", "OP-USDT", "SUI-USDT", "SEI-USDT",
    "INJ-USDT", "FIL-USDT", "ATOM-USDT", "ETC-USDT", "XLM-USDT", "HBAR-USDT", "ICP-USDT",
    "CRO-USDT", "VET-USDT", "RUNE-USDT", "AAVE-USDT", "UNI-USDT", "MKR-USDT", "LDO-USDT",
    "TIA-USDT", "STX-USDT", "PEPE-USDT", "WIF-USDT", "BONK-USDT", "FET-USDT", "TAO-USDT",
    "GRT-USDT", "SAND-USDT", "MANA-USDT", "AXS-USDT", "EGLD-USDT", "FTM-USDT", "ALGO-USDT",
    "FLOW-USDT",
]

REQUEST_INTERVAL_SEC = 0.15


def _http_json(url: str, params: dict, timeout: int = 15) -> dict:
    qs = "&".join(f"{k}={v}" for k, v in params.items())
    req = urllib.request.Request(f"{url}?{qs}", headers={"User-Agent": "zephyr-shadow-mvp/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _fetch_window(symbol: str, before_ms: int | None, after_ms: int | None, history: bool) -> list[list]:
    url = HISTORY_CANDLES_URL if history else CANDLES_URL
    params: dict = {"instId": symbol, "bar": "1D", "limit": "100"}
    if before_ms is not None:
        params["before"] = str(before_ms)
    if after_ms is not None:
        params["after"] = str(after_ms)
    data = _http_json(url, params)
    if data.get("code") != "0":
        raise RuntimeError(f"OKX API 错误 {data.get('code')}: {data.get('msg')}")
    return data.get("data", [])


def _candle_to_row(c: list) -> tuple:
    ts_ms = int(c[0])
    trade_date = datetime.fromtimestamp(ts_ms / 1000, tz=timezone_utc()).date()
    return (
        trade_date.isoformat(),
        float(c[1]), float(c[2]), float(c[3]), float(c[4]),
        float(c[5]),
        float(c[6]) if len(c) > 6 else 0.0,
        "1D",
        int(c[8]) if len(c) > 8 else 0,
    )


def timezone_utc():
    return timezone.utc  # datetime.fromtimestamp 的 tz 参数要求 tzinfo 实例（timedelta 会 TypeError）


def load_existing(out_csv: Path) -> dict[str, tuple]:
    rows: dict[str, tuple] = {}
    if out_csv.exists():
        with out_csv.open("r", encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                rows[r["trade_date"]] = (
                    r["trade_date"], float(r["open"]), float(r["high"]), float(r["low"]),
                    float(r["close"]), float(r["volume"]), float(r["vol_ccy"]), r["bar"], int(r["confirm"]),
                )
    return rows


def save(out_csv: Path, rows: dict[str, tuple]) -> int:
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    ordered = sorted(rows.items())
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(CSV_HEADER)
        w.writerows(r for _, r in ordered)
    return len(ordered)


def collect_backfill(symbol: str, out_csv: Path, start: date, end: date) -> tuple[int, str]:
    rows = load_existing(out_csv)
    # 注：from datetime import datetime 语境下无 datetime.time.max/min（method_descriptor）；
    # 用 min.time() + 毫秒补偿表达日界。bar 日期按 UTC，此处本地时区边界 ±8h 在日线粒度无实际影响。
    after_ms = int(datetime.combine(end, datetime.min.time()).timestamp() * 1000) + 86_399_999
    start_ms = int(datetime.combine(start, datetime.min.time()).timestamp() * 1000)
    while after_ms > start_ms:  # noqa: m10-time-trigger  分页回补的有界循环（逐批止盈条件收敛），一次性手动跑批非时间轮询常驻
        candles = _fetch_window(symbol, before_ms=None, after_ms=after_ms, history=True)
        time.sleep(REQUEST_INTERVAL_SEC)  # noqa: m10-time-trigger  限速礼貌间隔（一次性跑批内），非常驻轮询
        if not candles:
            break
        for c in candles:
            row = _candle_to_row(c)
            rows.setdefault(row[0], row)
        earliest_ms = int(candles[-1][0])
        if earliest_ms <= start_ms:
            break
        after_ms = earliest_ms
    return save(out_csv, rows), ""


def collect_incremental(symbol: str, out_csv: Path, lookback_days: int = 7) -> tuple[int, str]:
    rows = load_existing(out_csv)
    if rows:
        last = date.fromisoformat(max(rows))
        start = last - timedelta(days=lookback_days)
    else:
        start = date.today() - timedelta(days=90)
    from zephyr.shared.utils.time_utils import now_utc  # RULE-SCHEMA-TZ：时间 SSoT（src 禁裸 time.time()）
    before_ms = int((now_utc().timestamp() + 60_000) * 1000)
    start_ms = int(datetime.combine(start, datetime.min.time()).timestamp() * 1000)
    while before_ms > start_ms:  # noqa: m10-time-trigger  分页回补的有界循环（历史窗口收敛），一次性手动跑批非时间轮询常驻
        candles = _fetch_window(symbol, before_ms=before_ms, after_ms=None, history=False)
        time.sleep(REQUEST_INTERVAL_SEC)
        if not candles:
            break
        for c in candles:
            row = _candle_to_row(c)
            rows.setdefault(row[0], row)  # 已确认 K 线不覆盖；增量以补缺为主
        earliest_ms = int(candles[-1][0])
        if earliest_ms <= start_ms:
            break
        before_ms = earliest_ms
    return save(out_csv, rows), ""


def resolve_symbols(args) -> list[str]:
    if args.symbols_file:
        # 兼容两种清单格式：纯行列表 与 YAML（symbols: 键 + "- SYM" 项）；零第三方依赖
        syms: list[str] = []
        for ln in Path(args.symbols_file).read_text(encoding="utf-8").splitlines():
            s = ln.strip()
            if not s or s.startswith("#") or s.endswith(":") or s in ("symbols", "-"):
                continue
            if s.startswith("- "):
                s = s[2:].strip()
            if s:
                syms.append(s)
        return syms
    if args.symbols:
        return [s.strip() for s in args.symbols.split(",") if s.strip()]
    return list(DEFAULT_TOP50)


def main() -> int:
    ap = argparse.ArgumentParser(description="OKX 公开日线采集（免 key）——币圈影子 MVP")
    ap.add_argument("mode", choices=["backfill", "incremental"])
    ap.add_argument("--symbols", help="逗号分隔，如 BTC-USDT,ETH-USDT")
    ap.add_argument("--symbols-file", help="每行一个 instId 的清单文件")
    ap.add_argument("--start", default="2019-01-01", help="backfill 起始日（默认 2019-01-01）")
    ap.add_argument("--out-dir", default="data/crypto/kline_daily", help="CSV 输出目录")
    args = ap.parse_args()

    symbols = resolve_symbols(args)
    out_dir = Path(args.out_dir)
    ok, failed = 0, []
    for sym in symbols:
        out_csv = out_dir / f"{sym}.csv"
        try:
            if args.mode == "backfill":
                n, err = collect_backfill(sym, out_csv, date.fromisoformat(args.start), date.today())
            else:
                n, err = collect_incremental(sym, out_csv)
            print(f"[ok] {sym}: {n} rows -> {out_csv}")
            ok += 1
        except Exception as e:  # noqa: BLE001 — 采集脚本单币种失败不断全局
            print(f"[fail] {sym}: {e}", file=sys.stderr)
            failed.append(sym)
    print(f"summary: ok={ok}/{len(symbols)} failed={failed}")
    return 0 if not failed else 1


if __name__ == "__main__":
    sys.exit(main())

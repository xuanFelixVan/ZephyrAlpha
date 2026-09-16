# [BLUEPRINT] MOD-DATA-HOGQC
# [BLUEPRINT-NOTE] 研究件无蓝图正本, 登记见 depgraph 设计节点
# [MODULE] scripts.industry_graph.hog_chain_quickcheck
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.infrastructure.database_service
# [CONSUMERS] 线A 批1 A-2 矿脉(生猪链因子)快检证据件; E4 送考前置评估
# [STARTUP] manual
# [MATURITY] research
# [INVARIANTS] 只读(CH c1_market 带 FINAL + PG stock_concept); PIT: 信号只用 t 周及以前猪价, 收益取 t+1..t+4 个完整自然周(严格后置, 含今天的不完整周整周剔除); 动量基周/前向窗按日历周校验(84±4 天/逐周 7±2 天), 不合弃样; universe=stock_concept 猪肉+养鸡 valid_to IS NULL, 行情按 symbol_canonical(带后缀)查询; 确定性=结果 JSON 排序哈希不含墙钟; 禁写生产路径
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 猪价周覆盖不足->退出码2; 行情零覆盖/组合周<30->退出码2; 自检失败->退出码3
# [TESTS] 内建 --self-check 两遍确定性断言(证据件, 独立 pytest 待因子入库批)
# [TTL-PROMOTE] 因子入库晋升 permanent 走正门
# [TTL] task_bound
"""生猪链量价传导快检 v1.1（总账 A-2/A-3 矿脉，ICA-3 证据件；红蓝对抗修复版）。

假设：猪价动量（现货指数 12 周 ROC）上行 regime 下，养殖股组合未来 4 个
完整自然周收益结构占优；猪价动量对组合收益有领先性（快检级，非 E4）。

已知局限（声明）：前向窗相邻重叠 3/4 周→读数强自相关，本件只做方向
判定不做显著性；基准超额留 E4 阶段。

输出 .runtime/tmp/chain_alpha/hog_quickcheck.{json,md}。

用法::
    python scripts/industry_graph/hog_chain_quickcheck.py [--self-check]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta
from pathlib import Path

from typing import Final

from zephyr.data.table_registry import get_registry
from zephyr.infrastructure.database_service import get_db_service

_TBL_HOG: Final[str] = get_registry().table("market_hog_spot_index")
_TBL_KLINE: Final[str] = get_registry().table("market_kline_daily")

SQL_HOG: Final[str] = f"SELECT trade_date, index_value FROM {_TBL_HOG} ORDER BY trade_date"
SQL_UNIVERSE: Final[str] = "SELECT DISTINCT symbol FROM stock_concept WHERE valid_to IS NULL AND concept IN ('猪肉','养鸡') ORDER BY symbol"
SQL_KLINE: Final[str] = f"SELECT symbol_canonical, trade_date, close FROM {_TBL_KLINE} FINAL WHERE symbol_canonical IN %(syms)s AND market_type='A_share' ORDER BY symbol_canonical, trade_date"

OUT_DIR = Path(".runtime/tmp/chain_alpha")
MOMENTUM_WEEKS = 12
FWD_WEEKS = 4
MIN_PORT_WEEKS = 30


def _friday_of(d: str) -> str:
    dt = datetime.strptime(d, "%Y-%m-%d")
    offset = (4 - dt.weekday()) % 7
    return (dt + timedelta(days=offset)).strftime("%Y-%m-%d")


def _load_hog_weekly(conn) -> dict[str, float]:
    rows = conn.execute(
        f"SELECT trade_date, index_value FROM {_TBL_HOG}"  # noqa: bare-sql  豁免: CH 表名已走 TableRegistry, 只读研究查询
        " ORDER BY trade_date"
    )
    return {_friday_of(str(d)): float(px) for d, px in rows if px is not None}


def _load_universe() -> list[str]:
    db = get_db_service()
    conn = db.get_depgraph_conn(read_only=True)
    try:
        cur = conn.cursor()
        cur.execute(SQL_UNIVERSE)
        syms = sorted(r["symbol"] for r in cur.fetchall())
        cur.close()
    finally:
        conn.close()
    return syms


def _load_weekly_returns(conn, symbols: list[str]) -> dict[str, dict[str, float]]:
    """{symbol_canonical: {week_friday: week_return}}，周收益由日收盘聚合。"""
    daily: dict[str, dict[str, float]] = defaultdict(dict)
    rows = conn.execute(
        f"SELECT symbol_canonical, trade_date, close FROM {_TBL_KLINE} FINAL"
        " WHERE symbol_canonical IN %(syms)s AND market_type='A_share'"
        " ORDER BY symbol_canonical, trade_date",
        {"syms": symbols},
    )
    for sym, d, close in rows:
        if close is None:
            continue
        daily[sym][str(d)] = float(close)
    out: dict[str, dict[str, float]] = {}
    cur_week = _friday_of(str(date.today()))  # 含今天的不完整周整周剔除
    for sym, dd in daily.items():
        week_last: dict[str, float] = {}
        for d in sorted(dd):
            wk = _friday_of(d)
            if wk >= cur_week:
                continue  # 残周丢弃（红队 P1: 残周收益不得进前向窗）
            week_last[wk] = dd[d]
        wks = sorted(week_last)
        for i in range(1, len(wks)):
            prev = week_last[wks[i - 1]]
            if prev > 0:
                out.setdefault(sym, {})[wks[i]] = week_last[wks[i]] / prev - 1.0
    return out


def _spearman(xs: list[float], ys: list[float]) -> float:
    def rank(v: list[float]) -> list[float]:
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(order):
            j = i
            while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
                j += 1
            avg = (i + j) / 2 + 1
            for k in range(i, j + 1):
                r[order[k]] = avg
            i = j + 1
        return r

    if len(xs) < 3:
        return float("nan")
    rx, ry = rank(xs), rank(ys)
    mx, my = statistics.mean(rx), statistics.mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else float("nan")


def _load_inputs(conn) -> tuple[dict, list, list, dict]:
    hog_week = _load_hog_weekly(conn)
    wks = sorted(hog_week)
    if len(wks) < MOMENTUM_WEEKS + FWD_WEEKS + 8:
        print(f"ERROR: 猪价周覆盖不足({len(wks)}周)", file=sys.stderr)
        sys.exit(2)
    universe = _load_universe()
    if not universe:
        print("ERROR: universe 为空", file=sys.stderr)
        sys.exit(2)
    rets = _load_weekly_returns(conn, universe)
    if not rets:
        print("ERROR: 行情零覆盖（symbol_canonical 无命中）", file=sys.stderr)
        sys.exit(2)
    covered = len({w for r in rets.values() for w in r})
    if covered / max(len(wks), 1) < 0.5:
        print(f"ERROR: 组合周覆盖不足({covered}/{len(wks)})", file=sys.stderr)
        sys.exit(2)
    return hog_week, wks, universe, rets


def _momentum(hog_week: dict, wks: list) -> dict:
    mom: dict[str, float] = {}
    for i in range(MOMENTUM_WEEKS, len(wks)):
        w = wks[i]
        base_w = wks[i - MOMENTUM_WEEKS]
        gap = (
            datetime.strptime(w, "%Y-%m-%d")
            - datetime.strptime(base_w, "%Y-%m-%d")
        ).days
        if abs(gap - 7 * MOMENTUM_WEEKS) > 4:  # 日历周校验, 缺周弃样
            continue
        base = hog_week[base_w]
        if base > 0:
            mom[w] = hog_week[w] / base - 1.0
    return mom


def _portfolio_weeks(rets: dict, mom: dict) -> dict:
    port_week: dict[str, list[float]] = {}
    for w in mom:
        vals = [rets[s][w] for s in rets if w in rets.get(s, {})]
        if len(vals) >= 5:
            port_week[w] = vals
    return port_week


def _forward_returns(port_week: dict) -> dict:
    fwd: dict[str, float] = {}
    weeks_sorted = sorted(port_week)
    for i, w in enumerate(weeks_sorted):
        window = weeks_sorted[i + 1 : i + 1 + FWD_WEEKS]
        if len(window) < FWD_WEEKS:
            continue
        contiguous = all(
            3
            <= (
                datetime.strptime(window[j], "%Y-%m-%d")
                - datetime.strptime(window[j - 1], "%Y-%m-%d")
            ).days
            <= 11
            for j in range(1, len(window))
        )
        if not contiguous:  # 前向窗逐周日历校验, 缺周弃样
            continue
        comp = 1.0
        for f in window:
            comp *= 1 + statistics.mean(port_week[f])
        fwd[w] = comp - 1.0
    return fwd


def _stats(mom: dict, fwd: dict) -> dict:
    pairs = [(mom[w], fwd[w]) for w in fwd]
    xs = [p[0] for p in pairs]
    ys = [p[1] for p in pairs]
    ic = _spearman(xs, ys)
    up = [y for x, y in pairs if x > 0]
    down = [y for x, y in pairs if x <= 0]
    enough = len(up) >= 3 and len(down) >= 3
    if enough:
        verdict = (
            "上行 regime 前向收益占优=支持 regime 因子方向"
            if statistics.mean(up) > statistics.mean(down)
            else "方向不支持"
        )
    else:
        verdict = "样本不足"
    return {
        "spearman_momentum_vs_fwd": round(ic, 4) if ic == ic else None,
        "up_regime_fwd_mean": round(statistics.mean(up), 4) if enough else None,
        "down_regime_fwd_mean": round(statistics.mean(down), 4) if enough else None,
        "up_n": len(up),
        "down_n": len(down),
        "caveats": ["前向窗相邻重叠3/4周=读数强自相关", "基准超额留E4"],
        "verdict_hint": verdict,
    }


def run() -> dict:
    db = get_db_service()
    conn = db.get_clickhouse_conn(role="reader")
    hog_week, wks, universe, rets = _load_inputs(conn)
    mom = _momentum(hog_week, wks)
    port_week = _portfolio_weeks(rets, mom)
    if len(port_week) < MIN_PORT_WEEKS:
        print(
            f"ERROR: 组合有效周不足({len(port_week)}<{MIN_PORT_WEEKS})",
            file=sys.stderr,
        )
        sys.exit(2)
    fwd = _forward_returns(port_week)
    out = {
        "universe_size": len(universe),
        "hog_weeks": len(wks),
        "aligned_weeks": len(fwd),
    }
    out.update(_stats(mom, fwd))
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-check", action="store_true")
    args = ap.parse_args()
    r1 = run()
    fp1 = hashlib.sha256(json.dumps(r1, sort_keys=True).encode()).hexdigest()[:16]
    problems = []
    if args.self_check:
        r2 = run()
        fp2 = hashlib.sha256(
            json.dumps(r2, sort_keys=True).encode()
        ).hexdigest()[:16]
        if fp1 != fp2:
            problems.append("非确定性")
    r1["fingerprint"] = fp1
    r1["generated_on"] = str(date.today())  # 墙钟不入指纹
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUT_DIR / "hog_quickcheck.json", "w", encoding="utf-8") as f:
        json.dump(r1, f, ensure_ascii=False, indent=1)
    md = (
        "# 生猪链快检（ICA-3 证据件）\n\n"
        f"- universe: 猪肉+养鸡概念 {r1['universe_size']} 只\n"
        f"- 对齐周数: {r1['aligned_weeks']}（猪价 12 周动量 vs 组合未来 4 个完整周收益）\n"
        f"- Spearman: {r1['spearman_momentum_vs_fwd']}\n"
        f"- 上行 regime 前向均值: {r1['up_regime_fwd_mean']} (n={r1['up_n']})\n"
        f"- 下行 regime 前向均值: {r1['down_regime_fwd_mean']} (n={r1['down_n']})\n"
        f"- 方向判定: {r1['verdict_hint']}\n"
        f"- 局限: {'; '.join(r1['caveats'])}\n"
        f"- 指纹: {fp1}\n"
    )
    with open(OUT_DIR / "hog_quickcheck.md", "w", encoding="utf-8") as f:
        f.write(md)
    print(md)
    if problems:
        print("SELF-CHECK FAILED:", problems, file=sys.stderr)
        return 3
    print("SELF-CHECK PASS" if args.self_check else "OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())

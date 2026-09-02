# [BLUEPRINT] MOD-CD-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [BTSIG] 日频因子信号计算器（管道 B）——market_signal_history 落表 [no-pairing:轻量CLI暂无配对门禁]
# [MODULE] scripts.compute_signals
# [DOMAIN] D_SIGNAL
# [DEPENDENCIES] zephyr.factor.core.evaluation.backtest; zephyr.signal_ashare.signal_history_writer; zephyr.data.ch_writer
# [CONSUMERS] api_server.py /api/signal-run（可选复用 run_once）；APScheduler 16:30 槽位（日循环自动化后挂接）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] PIT(momentum只用t日前数据,compute内含); DEC-INV-002 只写信号表不触发 order; DLG-001 meta 携带因子版本
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 宇宙空->退出码2; CH不可达->退出码2; 落表0行->退出码3
# [TESTS] 本脚本 --verify（落表往返）
# [A_module] module_id=BTSIG | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
日频因子信号计算器（管道 B，#BT-PIPELINE-001 阶段三）。

个股视角（这只股票本身强不强）：宇宙截面 → momentum_20d 因子 → 排名百分位
→ direction（top10%=buy / bottom10%=sell / 中段=hold）→ market_signal_history
（source='factor_synth'）。

宇宙（auto）：HS300 最新快照（index_constituent max(trade_date)）∪ QMT 文件桥
持仓（E:\\qmt_bridge\\Stock\\PositionStatics.csv）∪ --symbols 附加。

用法：
    python scripts/compute_signals.py                     # 宇宙 auto，最新交易日
    python scripts/compute_signals.py --symbols 600519.SH,000858.SZ --dry-run
    python scripts/compute_signals.py --verify            # 回读最新信号验证
"""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import date, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT))

SIGNAL_ID = "factor_composite_v1"
TOP_PCT = 0.10  # 前/后 10% 分档（CTR-INJ-003 阈值显式化）
_QMT_BRIDGE_POS = Path(r"E:\qmt_bridge\Stock\PositionStatics.csv")


def _suffix_symbol(code: str) -> str:
    """纯数字代码 → 带后缀（6/9 开头=SH，其余=SZ；无数据的代码自然被 load_history 淘汰）。"""
    code = code.split(".")[0].strip()
    if not code or not code.isdigit():
        return code
    return code + (".SH" if code[0] in ("6", "9", "5") else ".SZ")


def load_universe(extra: list[str]) -> tuple[list[str], dict[str, int]]:
    """宇宙 = HS300 最新快照 ∪ QMT 持仓 ∪ 附加清单。返回 (带后缀 symbols, 分来源计数)。"""
    from zephyr.data import ch_writer

    out = ch_writer.query(
        "SELECT DISTINCT symbol FROM c1_market.index_constituent "
        "WHERE index_code = '000300.SH' AND trade_date = "
        "(SELECT max(trade_date) FROM c1_market.index_constituent WHERE index_code = '000300.SH')"
    )
    hs300 = [line.strip() for line in (out or "").strip().split("\n") if line.strip()]
    positions: list[str] = []
    if _QMT_BRIDGE_POS.exists():
        try:
            with open(_QMT_BRIDGE_POS, newline="", encoding="gbk", errors="replace") as f:
                for row in csv.reader(f):
                    if len(row) > 9 and row[7].strip().isdigit():
                        positions.append(_suffix_symbol(row[7]))
        except OSError:
            pass
    extra_syms = [_suffix_symbol(s) for s in extra]
    universe = sorted(set(hs300) | set(positions) | set(extra_syms))
    counts = {"hs300": len(hs300), "positions": len(positions), "extra": len(extra_syms), "merged": len(universe)}
    return universe, counts


def compute_cross_section(symbols: list[str], end: str | None) -> tuple[str, list[dict]]:
    """因子截面：load_history → momentum_20d 面板 → 末行截面打分。

    Returns: (trade_date, 信号行列表)。
    """
    import pandas as pd
    from zephyr.factor.core.evaluation.backtest import compute_factor_panel, load_history
    from zephyr.factor.momentum_factor import Momentum20d

    end_date = end or str(date.today())
    start = str(date.fromisoformat(end_date) - timedelta(days=120))  # 20d 动量预热 120 天
    history = load_history(symbols, start, end_date)
    if history.empty:
        raise RuntimeError(f"load_history 空（symbols={len(symbols)} {start}~{end_date}）——kline_daily 无数据？")
    panel = compute_factor_panel(Momentum20d, history)
    if panel.empty:
        raise RuntimeError("momentum_20d 面板为空")
    cross = panel.iloc[-1].dropna()
    if len(cross) < 5:
        raise RuntimeError(f"有效截面仅 {len(cross)} 只（<5）——不足以分档")
    trade_date = str(panel.index[-1])[:10]
    n = len(cross)
    ranked = cross.sort_values(ascending=False)
    top_k = max(1, int(n * TOP_PCT))
    rows = []
    for rank_i, (sym, val) in enumerate(ranked.items(), start=1):
        score = 1.0 - 2.0 * (rank_i - 1) / (n - 1) if n > 1 else 0.0
        if rank_i <= top_k:
            direction = "buy"
        elif rank_i > n - top_k:
            direction = "sell"
        else:
            direction = "hold"
        rows.append(
            {
                "trade_date": trade_date,
                "symbol": str(sym),
                "source": "factor_synth",
                "signal_id": SIGNAL_ID,
                "direction": direction,
                "score": round(float(score), 6),
                "confidence": round(abs(float(score)), 6),
                "rank_in_universe": rank_i,
                "meta": {
                    "factors": ["momentum_20d"],
                    "method": "rank_percentile",
                    "universe_size": n,
                    "momentum_20d": round(float(val), 6),
                    "as_of": trade_date,
                },
            }
        )
    return trade_date, rows


def run_once(end: str | None, extra: list[str], dry_run: bool = False) -> dict:
    universe, counts = load_universe(extra)
    if not universe:
        return {"ok": False, "error": "universe empty"}
    trade_date, rows = compute_cross_section(universe, end)
    if dry_run:
        return {
            "ok": True,
            "trade_date": trade_date,
            "rows": len(rows),
            "written": 0,
            "universe": counts,
            "dry_run": True,
            "preview": rows[:5],
        }
    from zephyr.signal_ashare.signal_history_writer import write_signals

    written = write_signals(rows, data_source="compute_signals")
    return {"ok": True, "trade_date": trade_date, "rows": len(rows), "written": written, "universe": counts}


def verify() -> int:
    from zephyr.data import ch_writer

    out = ch_writer.query(
        "SELECT trade_date, source, signal_id, count(), countIf(direction='buy'), "
        "countIf(direction='sell'), countIf(direction='hold') "
        "FROM c1_market.market_signal_history FINAL GROUP BY trade_date, source, signal_id "
        "ORDER BY trade_date DESC, source LIMIT 10"
    )
    if not out:
        print("VERIFY FAIL: 表空")
        return 1
    print("trade_date\tsource\tsignal_id\trows\tbuy\tsell\thold")
    print(out)
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="日频因子信号计算器（管道B→market_signal_history）")
    p.add_argument("--symbols", default="", help="附加标的（逗号分隔，并入宇宙）")
    p.add_argument("--date", default=None, help="目标日 YYYY-MM-DD（默认=今天，实际取面板最新交易日）")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--verify", action="store_true")
    args = p.parse_args(argv)

    if args.verify:
        return verify()

    extra = [s.strip() for s in args.symbols.split(",") if s.strip()]
    try:
        summary = run_once(args.date, extra, dry_run=args.dry_run)
    except Exception as exc:  # noqa: BLE001
        print(f"FAILED: {exc}", file=sys.stderr)
        return 2
    if not summary.get("ok"):
        print(f"FAILED: {summary.get('error')}", file=sys.stderr)
        return 2
    u = summary["universe"]
    print(
        f"OK trade_date={summary['trade_date']} rows={summary['rows']} written={summary.get('written', 0)} "
        f"universe=hs300:{u['hs300']}+pos:{u['positions']}+extra:{u['extra']}→{u['merged']}"
        + ("（dry-run）" if summary.get("dry_run") else "")
    )
    if summary.get("dry_run"):
        for r in summary["preview"]:
            print(f"  #{r['rank_in_universe']} {r['symbol']} {r['direction']} score={r['score']:+.3f}")
    if not summary.get("written") and not summary.get("dry_run"):
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())

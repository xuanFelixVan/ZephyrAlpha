# [BLUEPRINT] SH-SCRIPT-001 | docs/_working/decision_map_campaign/links/L05_t0/T0_MATERIAL_EXAM_CARD_draft.md | §4 成交模型 M0 + §5 窗规则
# [MODULE] t0_material_line
# create-guard-not-dup: 本件是T0做T材料线数据面(M0成交模型公共骨架,判据复用cost_trio_exam),命中词系材料/成交语文巧合,非生成器自动触发能力的第二实现（材料线管线：分钟数据→做T对语料；L05-C02 执行件草案）
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] c1_market.kline_1min（只读）；scripts/audit/cost_trio_exam.py（判据唯一真源，import 复用禁重写）
# [CONSUMERS] T0-MATERIAL 考试卡（草案待 Owner 签）；L05-C04 全量×状态匹配引擎（相位×周期矩阵语料面）
# [STARTUP] manual（python scripts/backtest/t0_material_line.py [--sample 20]）
# [MATURITY] draft（卡草案阶段；卡 frozen 前本件不得产出正式语料——产出仅限容量预检/验证）
# [INVARIANTS] 判据数值零改动：31.2bp/≥30bp 前置/30 对土规全部 import 复用 cost_trio_exam（禁重写禁本地常量顶替）；配对规则=同票同日既买又卖（build_pairs 唯一真源）；闭卷切点 2025-09-09 硬拦（--end 越切点=显式报错退出，禁闭卷数据入研究，17 号文 §三.5）；kline_1min 是 ReplacingMergeTree ⇒ bar 按 (trade_date,trade_time) 去重（uniqExact 教训，t0_ceiling_verdict §4）；min(low)=0 股票-日先挡（除零契约，t0_ceiling_verdict §4）；抽样=确定性行距采样（sorted universe 等距取点，无随机种子、可复现）；查库只读零状态变更；产物=parquet+yaml（禁 summary.json，n_trial_ledger glob 污染教训）
# [MODIFY-GUARD] 成交模型 M0 参数（grid_bp/period 桶规则/min_bars/notional）属考试卡预注册面，改动须先改卡再改本件；本件不得为过 30 对土规而调参（D-7 禁造料同构）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 分钟腿不可达/零行=显式报错非静默空产物；--end 越闭卷切点=SystemExit；产物写失败=非零退出码
# [TESTS] tests/backtest/test_t0_material_line.py（构造数据纯函数面：M0 触发/成交价/末日强平/除零挡/重采样分桶/板别涨跌停门/闭卷硬拦/抽样确定性；禁真全量跑）
# [TTL] task_bound
"""t0_material_line.py — 做T 材料线管线（分钟驱动的同票同日既买又卖语料构建）。

设计真源（判据零改动，口径引用不重写）：
- FINAL_REPORT_t0_matrix_reexam.md §七（材料线设计要点：成交模型先写死/窗规则日历化/判据沿用）
- 17 号文 §三.5（研究语料=分钟 2021-09→2025-09-09 切点前段；闭卷=切点后 HOLDOUT）
- 05 号文 §一（Owner 已批材料线开闸；kline_1min=信号法定轴，裁定#413④）
- cost_trio_exam.py（配对 build_pairs + 31.2bp + ≥30bp 前置 + 30 对土规，import 复用）

成交模型 M0（探针网格，草案卡 §4 预注册面；信号无信息=诚实基线，不是策略）：
- 基准价 base=当日首根（周期级）bar 的 open（日历规则给定，无拟合）。
- 买触发：bar.low ≤ base×(1−grid_bp/1e4)；成交价=min(bar.open, 触发价)（挂单限价机制）。
- 卖触发：买后 bar.high ≥ buy_fill×(1+grid_bp/1e4)；成交价=max(bar.open, 触发价)。
- 收盘强平：当日末根仍未触发卖出 ⇒ 以末根 close 强平（同日两腿仍在，配对仍成立）。
- 每 symbol-day 至多一次往返（M0 单 T；多次往返属未来另卡）。
- 滑点唯一由 CST-T0-001 固定 31.2bp（内含 2×10bp 滑点）承担，模拟成交价零叠加
  ——对 FINAL_REPORT §七.2 / V3 卡 §8.2"滑点是否重复计入"的一次了断。
- 数量：floor(notional/buy_fill/100)×100 股（A 股整手），不足一手按一手。

周期参数化（为多周期轴预留接口，05 号文 ⓪.1）：1min 原生；{5,15,30,60}min 按
日内 bar 序数分桶重采样（每 P 根合成一根，桶内 OHLCV 聚合，桶时刻=桶内末根时刻；
不按钟面对齐 ⇒ 午休/缺 bar 免疫）。

用法：
  python scripts/backtest/t0_material_line.py --sample 20            # 容量预检抽样
  python scripts/backtest/t0_material_line.py --symbols 600519,000001 --period 1,5
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "audit"))
import cost_trio_exam as ct  # 判据唯一真源：RT_COST_BP/PAIR_GATE/EDGE_PRECONDITION_BP/build_pairs

# 窗规则（卡 §5，日历给定禁看结果挑窗；引用不重写）
RESEARCH_START = "2021-09-01"  # 分钟库起点（裁定#413④ 立法口径）
CLOSED_BOOK_CUTOFF = "2025-09-09"  # 闭卷切点（HOLDOUT 纪律，禁越）

# 成交模型 M0 预注册参数（卡 §4；改动须先改卡）
DEFAULT_GRID_BP = 100.0  # 网格档宽 1%
DEFAULT_NOTIONAL = 100_000.0  # 单次往返名义本金（CNY）
MIN_BARS_BY_PERIOD = {1: 200, 5: 40, 15: 14, 30: 7, 60: 4}  # ≥83% 标准日 session 桶数（1min 真实 240）
ALLOWED_PERIODS = (1, 5, 15, 30, 60)  # 05 号文 ⓪.1：120min 不做（Owner 明令）

# NO-BARE-SQL 落地整改：常量名对齐 _SQL_* 豁免契约（原 _BARS_SQL）
_SQL_BARS = """
SELECT symbol, trade_date, trade_time, open, high, low, close, volume
FROM {table}
WHERE symbol IN ({symbols})
  AND trade_date >= toDate('{start}') AND trade_date <= toDate('{end}')
ORDER BY symbol, trade_date, trade_time
"""

# NO-BARE-SQL 落地整改：list_universe 内联 SQL 提升为 _SQL_* 常量
_SQL_UNIVERSE = """
SELECT DISTINCT symbol FROM {table} WHERE trade_date <= toDate('{cutoff}') ORDER BY symbol
"""


def board_limit_bp(symbol: str) -> float:
    """单日涨跌停理论极限 bp（V3 卡 M-4 板别 + 红蓝 #11：北交所 920xxx 归 bse ±30%）。

    主板 ±10%；创业板 300/301 与科创板 688 ±20%；北交所（43/83/87/88/920 开头）±30%。
    ST 不按 name 判（V3 卡 M-4 同口径，偏松方向如实披露）。
    """
    s = str(symbol)
    if s.startswith(("300", "301", "688")):
        return 2000.0
    if s.startswith(("43", "83", "87", "88", "920")):
        return 3000.0
    return 1000.0


def resample_period(day_bars: pd.DataFrame, period: int) -> pd.DataFrame:
    """按日内 bar 序数分桶重采样：每 period 根合成一根（卡 §4 预注册口径）。

    输入须已按 trade_time 排序且属同一 symbol-day；桶时刻=桶内末根 trade_time。
    """
    if period == 1:
        return day_bars.reset_index(drop=True)
    rows = []
    n = len(day_bars)
    for i in range(0, n, period):
        chunk = day_bars.iloc[i : i + period]
        rows.append(
            {
                "trade_time": chunk["trade_time"].iloc[-1],
                "open": chunk["open"].iloc[0],
                "high": chunk["high"].max(),
                "low": chunk["low"].min(),
                "close": chunk["close"].iloc[-1],
                "volume": chunk["volume"].sum(),
            }
        )
    return pd.DataFrame(rows)


def run_model_m0(day_bars: pd.DataFrame, grid_bp: float, notional: float, min_bars: int) -> tuple[dict | None, str]:
    """M0 探针网格模型作用于一个 symbol-day 的周期级 bar 序列。

    返回 (fills, reason)：fills={"buy_ts","buy_price","sell_ts","sell_price","qty"}；
    reason ∈ {"pair","no_touch","low_bars","zero_price","one_bar"}（剔除原因如实带出禁静默）。
    """
    if len(day_bars) < 2:
        return None, "one_bar"
    if len(day_bars) < min_bars:
        return None, "low_bars"
    if float((day_bars["low"] <= 0).any()) or float((day_bars["open"] <= 0).any()):
        return None, "zero_price"  # 零价契约：t0_ceiling_verdict §4
    base = float(day_bars["open"].iloc[0])
    buy_level = base * (1.0 - grid_bp / 1e4)

    buy_i = None
    buy_fill = None
    lows = day_bars["low"].to_numpy()
    opens = day_bars["open"].to_numpy()
    for i in range(len(day_bars)):
        if lows[i] <= buy_level:
            buy_i = i
            buy_fill = min(float(opens[i]), buy_level)  # 挂单限价机制：开盘即低于限价按开盘成交
            break
    if buy_i is None:
        return None, "no_touch"

    sell_level = buy_fill * (1.0 + grid_bp / 1e4)
    highs = day_bars["high"].to_numpy()
    closes = day_bars["close"].to_numpy()
    times = day_bars["trade_time"].to_numpy()
    sell_i = None
    sell_fill = None
    for j in range(buy_i + 1, len(day_bars)):
        if highs[j] >= sell_level:
            sell_i = j
            sell_fill = max(float(opens[j]), sell_level)
            break
    if sell_i is None:
        sell_i = len(day_bars) - 1
        sell_fill = float(closes[sell_i])  # 收盘强平（同日两腿仍在）

    qty = max(int(notional / buy_fill // 100) * 100, 100)
    fills = {
        "buy_ts": times[buy_i],
        "buy_price": buy_fill,
        "sell_ts": times[sell_i],
        "sell_price": sell_fill,
        "qty": qty,
    }
    return fills, "pair"


def fills_to_cost_trio_format(symbol: str, trade_date: str, fills: dict, run_id: str) -> list[dict]:
    """把 M0 两腿转成 cost_trio_exam.build_pairs 的输入格式（commission=逐笔佣金 3bp 仅披露）。

    滑点不进模拟成交价：31.2bp 固定口径内含 2×10bp，重复计入=双计（卡 §4 一次了断）。
    """
    b = float(fills["buy_price"]) * int(fills["qty"])
    s = float(fills["sell_price"]) * int(fills["qty"])
    return [
        {
            "symbol": symbol,
            "trade_date": trade_date,
            "timestamp": str(fills["buy_ts"]),
            "price": float(fills["buy_price"]),
            "quantity": int(fills["qty"]),
            "side": "buy",
            "commission": round(b * 0.0003, 2),
            "run_id": run_id,
        },
        {
            "symbol": symbol,
            "trade_date": trade_date,
            "timestamp": str(fills["sell_ts"]),
            "price": float(fills["sell_price"]),
            "quantity": int(fills["qty"]),
            "side": "sell",
            "commission": round(s * 0.0003, 2),
            "run_id": run_id,
        },
    ]


def build_corpus_for_symbol_day(
    symbol: str,
    trade_date: str,
    day_bars_1min: pd.DataFrame,
    period: int,
    grid_bp: float,
    notional: float,
    run_id: str,
) -> tuple[list[dict], str]:
    """单 symbol-day：重采样→M0→两腿。返回 (cost_trio 格式 fills, 剔除/成因 reason)。"""
    min_bars = MIN_BARS_BY_PERIOD[period]
    bars = resample_period(day_bars_1min, period)
    fills, reason = run_model_m0(bars, grid_bp, notional, min_bars)
    if fills is None:
        return [], reason
    return fills_to_cost_trio_format(symbol, trade_date, fills, run_id), "pair"


def apply_material_gates(pairs: list[dict]) -> tuple[list[dict], dict]:
    """材料资格审计门（V3 卡 M-4 涨跌停可行域；M-1/M-2/M-3 由构造结构性满足并披露）。

    M-1 日内粒度：timestamp 含时分（本件构造即含）；
    M-2 往返同体：两腿同 run_id（本件构造即同体）；
    M-3 材料去重：语料直接生成无重放件（不适用，披露）；
    M-4 涨跌停可行域：|gross_bp| ≤ 板别单日极限，超限剔除计数。
    """
    kept: list[dict] = []
    rejected_price_limit = 0
    for p in pairs:
        limit_bp = board_limit_bp(p["symbol"])
        if abs(float(p["gross_bp"])) > limit_bp:
            rejected_price_limit += 1
            continue
        kept.append(p)
    audit = {
        "m1_intraday_granularity": "by_construction",
        "m2_same_run_identity": "by_construction",
        "m3_fingerprint_dedup": "not_applicable_generated_corpus",
        "m4_rejected_price_limit": rejected_price_limit,
    }
    return kept, audit


def deterministic_sample(symbols: list[str], n: int) -> list[str]:
    """确定性行距抽样：sorted universe 等距取 n 点（无随机种子，可复现可披露）。"""
    if n >= len(symbols):
        return list(symbols)
    stride = len(symbols) / n
    return [symbols[min(int(i * stride), len(symbols) - 1)] for i in range(n)]


def list_universe(conn) -> list[str]:
    table = _table_name()
    rows = conn.execute(_SQL_UNIVERSE.format(table=table, cutoff=CLOSED_BOOK_CUTOFF))
    return [str(r[0]) for r in rows]


def _table_name() -> str:
    from zephyr.data.table_registry import get_registry

    return get_registry().table("market_kline_1min")


def load_bars(conn, symbols: list[str], start: str, end: str) -> tuple[pd.DataFrame, dict]:
    """批量拉取分钟 bar 并按 (symbol,trade_date,trade_time) 去重（ReplacingMergeTree 多版免疫）。"""
    table = _table_name()
    sym_list = ",".join(f"'{s}'" for s in symbols)
    rows = conn.execute(_SQL_BARS.format(table=table, symbols=sym_list, start=start, end=end))
    df = pd.DataFrame(rows, columns=["symbol", "trade_date", "trade_time", "open", "high", "low", "close", "volume"])
    raw = len(df)
    df = df.drop_duplicates(subset=["symbol", "trade_date", "trade_time"], keep="last")
    df = df.sort_values(["symbol", "trade_date", "trade_time"]).reset_index(drop=True)
    return df, {"bars_raw": raw, "bars_after_dedup": len(df), "bars_deduped_away": raw - len(df)}


def run_pipeline(
    conn,
    symbols: list[str],
    start: str,
    end: str,
    periods: list[int],
    grid_bp: float,
    notional: float,
    run_id: str,
) -> tuple[dict[str, pd.DataFrame], dict]:
    """主管线：取数一次，逐周期构建语料。返回 {period: pairs_df}, stats。"""
    t0 = time.perf_counter()
    bars, bar_stats = load_bars(conn, symbols, start, end)
    t_fetch = time.perf_counter() - t0
    if bars.empty:
        raise SystemExit(f"FAIL: 分钟腿 {start}..{end} x {len(symbols)} 只零行——禁静默空产物")

    stats: dict = {
        "window": {"start": start, "end": end, "closed_book_cutoff": CLOSED_BOOK_CUTOFF, "closed_book_ok": True},
        "universe": {"n_symbols_requested": len(symbols), **bar_stats},
        "model_m0": {"grid_bp": grid_bp, "notional_cny": notional, "min_bars_by_period": MIN_BARS_BY_PERIOD},
        "criteria_source": {
            "rt_cost_bp": ct.RT_COST_BP,
            "pair_gate": ct.PAIR_GATE,
            "edge_precondition_bp": ct.EDGE_PRECONDITION_BP,
            "pairing_rule": "cost_trio_exam.build_pairs import 复用（同票同日既买又卖，禁重写）",
        },
        "periods": {},
        "timing_seconds": {"fetch": round(t_fetch, 3)},
    }

    out: dict[str, pd.DataFrame] = {}
    grouped = bars.groupby(["symbol", "trade_date"], sort=True)
    for period in periods:
        t1 = time.perf_counter()
        fills_all: list[dict] = []
        reason_counts: dict[str, int] = {}
        n_symbol_days = 0
        for (symbol, trade_date), day_bars in grouped:
            n_symbol_days += 1
            day_bars = day_bars.sort_values("trade_time")
            fills, reason = build_corpus_for_symbol_day(
                str(symbol), str(trade_date), day_bars, period, grid_bp, notional, run_id
            )
            fills_all.extend(fills)
            reason_counts[reason] = reason_counts.get(reason, 0) + 1
        pairs = ct.build_pairs(fills_all)
        kept, audit = apply_material_gates(pairs)
        t_model = time.perf_counter() - t1
        stats["periods"][f"{period}min"] = {
            "n_symbol_days": n_symbol_days,
            "reason_counts": reason_counts,
            "n_pairs_before_m4": len(pairs),
            "n_pairs": len(kept),
            "material_audit": audit,
            "edge_ge_30bp": sum(1 for p in kept if float(p["gross_bp"]) >= ct.EDGE_PRECONDITION_BP),
            "net_positive": sum(1 for p in kept if float(p["net_bp"]) > 0),
            "model_seconds": round(t_model, 3),
        }
        out[f"{period}min"] = pd.DataFrame(kept)
    stats["timing_seconds"]["total"] = round(time.perf_counter() - t0, 3)
    return out, stats


def enforce_closed_book(start: str, end: str) -> None:
    """闭卷硬拦：研究语料终点越切点=显式报错（禁闭卷数据入研究，17 号文 §三.5）。"""
    if start < RESEARCH_START:
        raise SystemExit(f"FAIL: --start {start} 早于分钟库法定起点 {RESEARCH_START}（裁定#413④）")
    if end > CLOSED_BOOK_CUTOFF:
        raise SystemExit(
            f"FAIL: --end {end} 越闭卷切点 {CLOSED_BOOK_CUTOFF}——禁闭卷数据入研究"
            "（17 号文 §三.5 HOLDOUT 纪律；闭卷考属另一张卡的面）"
        )


def write_outputs(out_dir: Path, tag: str, frames: dict[str, pd.DataFrame], stats: dict) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    for label, df in frames.items():
        df.to_parquet(out_dir / f"t0_material_pairs_{tag}_{label}.parquet", index=False)
    (out_dir / f"t0_material_stats_{tag}.yaml").write_text(
        yaml.safe_dump(stats, allow_unicode=True, sort_keys=False), encoding="utf-8"
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="做T 材料线：分钟→同票同日既买又卖语料（判据 import 复用零改动）")
    ap.add_argument("--symbols", default="", help="逗号分隔股票池（与 --sample/--pool-file 三选一）")
    ap.add_argument("--pool-file", default="", help="股票池文件（每行一个 symbol）")
    ap.add_argument("--sample", type=int, default=0, help="确定性行距抽样 N 只（容量预检模式）")
    ap.add_argument("--start", default=RESEARCH_START)
    ap.add_argument("--end", default=CLOSED_BOOK_CUTOFF)
    ap.add_argument("--grid-bp", type=float, default=DEFAULT_GRID_BP)
    ap.add_argument("--period", default="1", help="周期（分钟），逗号分隔，允许 1,5,15,30,60（120 不做）")
    ap.add_argument("--notional", type=float, default=DEFAULT_NOTIONAL)
    ap.add_argument("--out", default="data/backtest_artifacts/t0_material_line")
    ap.add_argument("--tag", default="", help="产物文件名标签（缺省=grid{grid_bp}bp）")
    args = ap.parse_args()

    enforce_closed_book(args.start, args.end)
    periods = [int(p) for p in str(args.period).split(",")]
    bad = [p for p in periods if p not in ALLOWED_PERIODS]
    if bad:
        raise SystemExit(f"FAIL: 周期 {bad} 不在允许集 {ALLOWED_PERIODS}（120min 不做，Owner 明令）")
    if args.grid_bp <= 0 or args.notional <= 0:
        raise SystemExit("FAIL: --grid-bp/--notional 须为正")

    from zephyr.infrastructure.database_service import DatabaseService

    conn = DatabaseService().get_clickhouse_conn()
    if args.sample > 0:
        symbols = deterministic_sample(list_universe(conn), args.sample)
    elif args.pool_file:
        symbols = [
            ln.strip()
            for ln in Path(args.pool_file).read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.startswith("#")
        ]
    elif args.symbols:
        symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
    else:
        raise SystemExit("FAIL: 股票池缺失——--symbols/--pool-file/--sample 三选一")

    run_id = f"t0mat-p{args.period}-g{args.grid_bp:g}-{args.start}_{args.end}"
    frames, stats = run_pipeline(conn, symbols, args.start, args.end, periods, args.grid_bp, args.notional, run_id)
    stats["universe"]["symbols"] = symbols
    stats["run_id"] = run_id
    tag = args.tag or f"grid{args.grid_bp:g}bp"
    write_outputs(Path(args.out), tag, frames, stats)
    print(yaml.safe_dump(stats["periods"], allow_unicode=True, sort_keys=False))
    print("timing:", stats["timing_seconds"])
    print("out-dir:", args.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())

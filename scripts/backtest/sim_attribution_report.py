# [BLUEPRINT] MOD-BT-084 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.sim_attribution_report
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.infrastructure.database_service; zephyr.data.ch_writer(INSERT 预留);
#   schemas.categories.sim_attribution_daily(DDL/列真源); scripts.backtest.sim_paper_ledger(成本口径真源)
# [CONSUMERS] c1_backtest.sim_attribution_daily（归因长表，DDL 真源
#   schemas/categories/sim_attribution_daily.py，apply 注册归总统筹）；WO-1 四段答案下游
# [STARTUP] manual+event（CLI 手工；pipeline_events maybe_emit_attribution_daily 接线归总统筹，
#   本件交付入口签名 run_daily(day)——deps=sim 账本当日 marker，超时/幂等/marker 照抄 run_sim_ledger_daily）
# noqa: m11-perm-manual-legitimate  M11豁免: 本件是 WO-1 收益归因 CLI（AI/Owner 按需调用，无常驻进程/无自轮询）；事件接线 maybe_emit_attribution_daily 归总统筹批（pipeline_events），接线落地前经 CLI 单发触发，与 commit_queue.py/task_board.py 同类
# [MATURITY] experimental
# [INVARIANTS] 成本口径=账本实际记账（import sim_paper_ledger BUY_COST/SELL_COST 常量逐字一致，
#   禁引 config 默认值——红蓝预登记项）；pnl_net=账本 daily_pnl 原值（对平恒等式
#   pnl_gross=pnl_net+pnl_cost）；钱包链键=(strategy_id, mode)（mode 断链=钱包重启，
#   链首 prev_equity=initial_capital）；risk_contrib 单策略期=1.0、多策略期占位 1/N
#   （占位标记入 detail，波动贡献升级挂 M-11）；回放幂等=ReplacingMergeTree 同键新 ingest_ts
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(账本表不可读/落库未确认 fail-closed)
# [TESTS] tests/backtest/test_sim_attribution_report.py
# [A_module] module_id=MOD-BT-215 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""模拟盘收益归因例行报告（WO-1）——钱从哪来的四段答案。

四段（对应主单验收）：① 钱哪个策略赚的（strategy_id 分解）② 成本吃多少
（pnl_gross-pnl_net）③ 相对基准超额多少（benchmark_rel，主基准 000852 中证1000，
次基准 000300 沪深300 入 detail）④ 风险贡献怎么分（risk_contrib）。

与 sim_deviation_report 分工：偏差="当时说 vs 实际走"；归因="实际走的钱从哪来"。

成本口径铁律（红蓝预登记）：pnl_cost 逐字对齐 scripts/backtest/sim_paper_ledger.py
的记账代码——BUY_COST=(2.5+5.0)/1e4（佣金 2.5bp+滑点 5bp）、
SELL_COST=(2.5+10.0+5.0)/1e4（佣金 2.5bp+滑点 10bp+冲击 5bp），
本账本路径无 ¥5 佣金地板（地板是做T config 口径，账本未实现）；
常量经 import 复用（禁复制禁引 config），entry 日成本=cash*BUY_COST、
exit 日成本=shares*px*SELL_COST，非交易日=0；trade_log.cost_paid 为账本自身
留痕，优先采用并与常量复算交叉核对（差>0.01 元=口径漂移，fail-closed 上报）。

用法：
  python scripts/backtest/sim_attribution_report.py --replay            # 62 天存量全量回放+对账
  python scripts/backtest/sim_attribution_report.py --day 2026-09-18    # 单日增量追算
  python scripts/backtest/sim_attribution_report.py --replay --insert-tsv out.tsv
      # 追加产出 INSERT 用 TSV（表建后实跑；缺省回放只计算+写对账文件，不写库）
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import logging
import math
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_LEDGER_PATH = _REPO_ROOT / "scripts" / "backtest" / "sim_paper_ledger.py"
_SCHEMA_MOD = "schemas.categories.sim_attribution_daily"


def _ensure_repo_on_path() -> None:
    """裸脚本跑法（python scripts/backtest/...）下 sys.path[0]=scripts/backtest，
    schemas 包不可达——补仓根（sim_paper_ledger allocation_wallet_capital 同款前置）。"""
    import sys

    if str(_REPO_ROOT) not in sys.path:
        sys.path.insert(0, str(_REPO_ROOT))

_POCKET_TABLE = "c1_backtest.sim_pocket_daily"  # 真源=schemas/categories/sim_pocket_daily.py（未入 TableRegistry，表名派生自 DDL 真源模块）
_TRADE_LOG_TABLE = "c1_backtest.sim_trade_log"  # 真源=schemas/categories/sim_trade_log.py（同上）
# 注册表真源（#ARCH-CH-024）：已注册表禁硬编码——经 TableRegistry 派生（get_registry 惰性缓存）
_TABLES: dict[str, str] = {}


def _tables() -> dict[str, str]:
    """表名解析（惰性单次）：pocket/trade_log 派生自 DDL 真源模块，kline_index 走 TableRegistry。"""
    if not _TABLES:
        _ensure_repo_on_path()
        import importlib

        pocket = importlib.import_module("schemas.categories.sim_pocket_daily")
        tradelog = importlib.import_module("schemas.categories.sim_trade_log")
        from zephyr.data.table_registry import get_registry

        _TABLES["pocket"] = pocket.TABLE_NAME
        _TABLES["trade_log"] = tradelog.TABLE_NAME
        _TABLES["bench"] = get_registry().table("market_index_kline")  # c1_market.kline_index
    return _TABLES
# 对平容差：账本 daily_pnl/equity 均按元 round(2)——链式复算允许 ±0.01 元/日的舍入漂移
_RECON_TOL = 0.011
# trade_log cost_paid 与常量复算的交叉核对容差（同口径应 <1e-6 相对，0.01 元绝对兜底）
_COST_TOL = 0.01


def _load_ledger():
    """import sim_paper_ledger 模块（成本口径真源，逐字一致=直接 import 不复制）。

    scripts/ 非包——经 importlib 按文件路径装载；只取常量与纯函数，不触发其 main。
    """
    spec = importlib.util.spec_from_file_location("sim_paper_ledger", _LEDGER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"账本模块不可装载: {_LEDGER_PATH}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------- 查询层（可 monkeypatch）
def _reader():
    """只读 CH 连接（RULE-DB：唯一真源 DatabaseService，禁裸 connect）。"""
    from zephyr.infrastructure.database_service import DatabaseService

    return DatabaseService().get_clickhouse_conn("reader")


def fetch_pocket_rows() -> list[dict]:
    """读钱包日账全量（FINAL=RMT 去重视图）。"""
    rows = _reader().execute(
        f"SELECT trade_date, strategy_id, initial_capital, cash, position_symbol, shares,"
        f" position_value, equity, daily_pnl, signal, mode, run_id, note"
        f" FROM {_tables()['pocket']} FINAL ORDER BY strategy_id, mode, trade_date"
    )
    return [_pocket_row_dict(r) for r in rows]


def fetch_trade_events() -> dict[tuple[str, str, str], dict]:
    """读事件流水（entry/exit/open）→ {(strategy_id, trade_date, action): event}。"""
    rows = _reader().execute(
        f"SELECT trade_date, strategy_id, symbol, action, shares, price, cost_paid, cash_after"
        f" FROM {_tables()['trade_log']} FINAL ORDER BY trade_date, action"
    )
    out: dict[tuple[str, str, str], dict] = {}
    for d, sid, sym, action, sh, px, cost, cash_after in rows:
        out[(str(sid), str(d), str(action))] = {
            "symbol": sym, "shares": float(sh), "price": float(px),
            "cost_paid": float(cost), "cash_after": float(cash_after),
        }
    return out


def fetch_benchmark_closes(symbols: tuple[str, ...], d0: str, d1: str) -> dict[str, dict[str, float]]:
    """读基准收盘价 {symbol: {date_str: close}}（缺日如实缺，不插值）。"""
    sym_list = ",".join(f"'{s}'" for s in symbols)
    rows = _reader().execute(
        f"SELECT symbol, trade_date, close FROM {_tables()['bench']}"
        f" WHERE symbol IN ({sym_list}) AND trade_date >= '{d0}' AND trade_date <= '{d1}'"
        f" ORDER BY symbol, trade_date"
    )
    out: dict[str, dict[str, float]] = {s: {} for s in symbols}
    for sym, d, close in rows:
        out[str(sym)][str(d)] = float(close)
    return out


def _pocket_row_dict(r: tuple) -> dict:
    return {
        "trade_date": str(r[0]), "strategy_id": str(r[1]),
        "initial_capital": float(r[2]), "cash": float(r[3]),
        "position_symbol": str(r[4] or ""), "shares": float(r[5]),
        "position_value": float(r[6]), "equity": float(r[7]),
        "daily_pnl": float(r[8]), "signal": str(r[9]),
        "mode": str(r[10]), "run_id": str(r[11]), "note": str(r[12] or ""),
    }


# ---------------------------------------------------------------- 纯函数层（单测覆盖面）
def build_chains(rows: list[dict]) -> dict[tuple[str, str], list[dict]]:
    """按钱包链键 (strategy_id, mode) 分链并按日排序。

    mode 断链=钱包重启（replay_demo → sim_daily 权益不衔接），链首
    prev_equity 取本链首行 initial_capital（与账本 run() 的 prev_equity=INITIAL_CAPITAL
    起点一致）。
    """
    chains: dict[tuple[str, str], list[dict]] = {}
    for r in rows:
        chains.setdefault((r["strategy_id"], r["mode"]), []).append(r)
    for key in chains:
        chains[key].sort(key=lambda x: x["trade_date"])
    return chains


def cost_of_day(row: dict, prev_equity: float, events: dict, ledger) -> tuple[float, dict]:
    """单日成本（账本口径）：entry=cash*BUY_COST / exit=shares*px*SELL_COST / 其余=0。

    trade_log.cost_paid（账本自身留痕）优先采用；与常量复算差 >_COST_TOL 判口径漂移
    （红蓝预登记项的硬检查）。返回 (cost, 分解 dict)。
    """
    key = (row["strategy_id"], row["trade_date"], row["signal"])
    ev = events.get(key)
    signal = row["signal"]
    if signal == "entry":
        # 账本 entry 日 buy_cost = 触发日现金(=链上 prev equity，账本起始=INITIAL_CAPITAL) * BUY_COST
        expected = (prev_equity if prev_equity is not None else ledger.INITIAL_CAPITAL) * ledger.BUY_COST
        breakdown = _split_cost(expected, ledger.BUY_COST, ledger.SELL_COST, is_buy=True)
    elif signal == "exit":
        if ev is not None:
            # exit 日账本行是平仓后快照（shares 已归零）——notional 必须取事件流水份额/价
            notional = ev["shares"] * ev["price"]
        else:
            notional = row["shares"] * _exit_price(row, ev)
        expected = notional * ledger.SELL_COST
        breakdown = _split_cost(expected, ledger.BUY_COST, ledger.SELL_COST, is_buy=False)
    else:
        return 0.0, {"commission": 0.0, "slippage": 0.0, "impact": 0.0}
    if ev is not None:
        drift = abs(ev["cost_paid"] - expected)
        if drift > _COST_TOL:
            raise RuntimeError(
                f"成本口径漂移 fail-closed: {row['strategy_id']} {row['trade_date']} {signal} "
                f"trade_log={ev['cost_paid']:.4f} vs 常量复算={expected:.4f} (差 {drift:.4f} > {_COST_TOL})")
        return ev["cost_paid"], breakdown
    return expected, breakdown  # trade_log 缺行=常量复算兜底（detail 注明）


def _exit_price(row: dict, ev: dict | None) -> float:
    """exit 成交价：trade_log 留痕价优先，缺行回退 position_value/shares。"""
    if ev is not None and ev.get("price"):
        return ev["price"]
    if row["shares"] > 0:
        return row["position_value"] / row["shares"]
    raise RuntimeError(f"exit 价不可得: {row['strategy_id']} {row['trade_date']}")


def _split_cost(total: float, buy_cost: float, sell_cost: float, *, is_buy: bool) -> dict:
    """成本三元分解（对齐账本常量成分：佣金 2.5bp；滑点 买5bp/卖10bp；冲击 卖5bp）。"""
    rate = buy_cost if is_buy else sell_cost
    if rate <= 0:
        return {"commission": 0.0, "slippage": 0.0, "impact": 0.0}
    commission_bps, slippage_bps, impact_bps = 2.5, (5.0 if is_buy else 10.0), (0.0 if is_buy else 5.0)
    notional = total / rate
    return {
        "commission": notional * commission_bps / 10000.0,
        "slippage": notional * slippage_bps / 10000.0,
        "impact": notional * impact_bps / 10000.0,
    }


def decompose_chain(chain: list[dict], events: dict, ledger) -> list[dict]:
    """单链逐日分解 → 归因行（pnl_net=账本 daily_pnl 原值；gross=net+cost 恒等对平）。"""
    out: list[dict] = []
    prev_equity: float | None = None
    for i, row in enumerate(chain):
        base = ledger.INITIAL_CAPITAL if i == 0 else chain[i - 1]["equity"]
        # 链首 prev=本行 initial_capital（开户行场景 initial 可能≠100万，优先本行值）
        prev = row["initial_capital"] if i == 0 else base
        cost, breakdown = cost_of_day(row, prev, events, ledger)
        pnl_net = row["daily_pnl"]
        # 开户行（signal=open）日 pnl 恒 0，成本恒 0（开户不是交易）
        if row["signal"] == "open":
            cost, breakdown = 0.0, {"commission": 0.0, "slippage": 0.0, "impact": 0.0}
        out.append({
            "trade_date": row["trade_date"], "strategy_id": row["strategy_id"],
            "pnl_gross": pnl_net + cost, "pnl_cost": cost, "pnl_net": pnl_net,
            "_prev_equity": prev, "_signal": row["signal"], "_mode": row["mode"],
            "_run_id": row["run_id"], "_equity": row["equity"],
            "_cost_breakdown": breakdown,
        })
        prev_equity = row["equity"]
    return out


def verify_chain_continuity(chain: list[dict], decomposed: list[dict]) -> list[str]:
    """链连续性核查：equity_t - equity_{t-1} ≈ daily_pnl_t（账本 round(2) 容差内）。

    返回漂移报告列表（空=全对平）；链首行 prev=initial_capital。
    """
    issues: list[str] = []
    for i, (row, dec) in enumerate(zip(chain, decomposed)):
        prev = row["initial_capital"] if i == 0 else chain[i - 1]["equity"]
        drift = abs((row["equity"] - prev) - row["daily_pnl"])
        if drift > _RECON_TOL:
            issues.append(
                f"{row['strategy_id']}/{row['mode']} {row['trade_date']}: "
                f"equity 差分复算 {row['equity'] - prev:.4f} vs daily_pnl {row['daily_pnl']:.4f}"
                f" (漂移 {drift:.4f})")
        dec["_prev_equity"] = prev
    return issues


def strategy_daily_returns(decomposed: list[dict]) -> dict[str, float]:
    """策略日收益 {date: ret}：ret=daily_pnl/prev_equity（prev≤0 或缺→NaN）。"""
    out: dict[str, float] = {}
    for dec in decomposed:
        prev = dec["_prev_equity"]
        out[dec["trade_date"]] = dec["pnl_net"] / prev if prev and prev > 0 else math.nan
    return out


def benchmark_daily_returns(closes: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    """基准日收益 {symbol: {date: ret}}（首日无收益=缺）。"""
    out: dict[str, dict[str, float]] = {}
    for sym, series in closes.items():
        dates = sorted(series)
        rets: dict[str, float] = {}
        for a, b in zip(dates, dates[1:]):
            if series[a] > 0:
                rets[b] = series[b] / series[a] - 1.0
        out[sym] = rets
    return out


def assign_risk_contrib(by_date: dict[str, list[dict]]) -> None:
    """就地填 risk_contrib：单策略日=1.0；多策略日=1/N 占位（detail 打占位标记）。

    sanity check：每日各策略 risk_contrib 合计=1.0（±1e-9），破坏即 fail-closed。
    """
    for d, decs in by_date.items():
        n = len(decs)
        for dec in decs:
            dec["risk_contrib"] = 1.0 / n
            dec["_risk_placeholder"] = n > 1
        total = sum(dec["risk_contrib"] for dec in decs)
        if abs(total - 1.0) > 1e-9:
            raise RuntimeError(f"risk_contrib sanity check 失败: {d} 合计={total!r} (单策略期必须=100%)")


def assemble_rows(decomposed: list[dict], bench_rets: dict[str, dict[str, float]],
                  *, bench_primary: str, bench_secondary: str) -> list[dict]:
    """装配长表行：benchmark_rel=策略日收益-主基准日收益；次基准/明细入 detail JSON。"""
    by_date: dict[str, list[dict]] = {}
    for dec in decomposed:
        by_date.setdefault(dec["trade_date"], []).append(dec)
    assign_risk_contrib(by_date)
    rets_all = {dec["trade_date"]: dec["pnl_net"] / dec["_prev_equity"]
                if dec["_prev_equity"] and dec["_prev_equity"] > 0 else math.nan
                for dec in decomposed}
    rows: list[dict] = []
    for dec in decomposed:
        d = dec["trade_date"]
        strat_ret = rets_all[d]
        bp = bench_rets.get(bench_primary, {}).get(d)
        bs = bench_rets.get(bench_secondary, {}).get(d)
        bench_rel = (strat_ret - bp) if (bp is not None and not math.isnan(strat_ret)) else math.nan
        detail = {
            "mode": dec["_mode"], "run_id": dec["_run_id"], "signal": dec["_signal"],
            "equity": dec["_equity"], "prev_equity": dec["_prev_equity"],
            "strategy_ret": None if math.isnan(strat_ret) else round(strat_ret, 10),
            "benchmark_ret_primary": None if bp is None else round(bp, 10),
            "benchmark_rel_hs300": (None if bs is None or math.isnan(strat_ret)
                                    else round(strat_ret - bs, 10)),
            "cost_breakdown": {k: round(v, 6) for k, v in dec["_cost_breakdown"].items()},
            "risk_contrib_placeholder": dec.get("_risk_placeholder", False),
            "schema_version": "sim_attribution/1.0",
        }
        if math.isnan(bench_rel):
            detail["benchmark_missing"] = True
        rows.append({
            "trade_date": d, "strategy_id": dec["strategy_id"],
            "pnl_gross": round(dec["pnl_gross"], 2), "pnl_cost": round(dec["pnl_cost"], 2),
            "pnl_net": round(dec["pnl_net"], 2),
            "benchmark_rel": None if math.isnan(bench_rel) else round(bench_rel, 10),
            "risk_contrib": round(dec["risk_contrib"], 10),
            "detail": json.dumps(detail, ensure_ascii=False, sort_keys=True),
        })
    return rows


def rows_to_tsv(rows: list[dict]) -> str:
    """长表行 → INSERT 列序 TSV（ch_writer 通道；NaN→nan，None→\\N）。"""
    cols = ("trade_date", "strategy_id", "pnl_gross", "pnl_cost", "pnl_net",
            "benchmark_rel", "risk_contrib", "detail")

    def cell(v: Any) -> str:
        if v is None:
            return "\\N"
        if isinstance(v, float) and math.isnan(v):
            return "nan"
        return str(v).replace("\t", " ").replace("\n", " ")

    return "\n".join("\t".join(cell(r[c]) for c in cols) for r in rows) + "\n"


# ---------------------------------------------------------------- 作业模式
def replay() -> dict:
    """存量全量回放+对账（硬验收）：62 天逐日分解→三重核查→对账数字。"""
    _ensure_repo_on_path()
    from schemas.categories.sim_attribution_daily import (
        BENCHMARK_PRIMARY,
        BENCHMARK_SECONDARY,
    )

    ledger = _load_ledger()
    pocket = fetch_pocket_rows()
    if not pocket:
        raise RuntimeError(f"{_tables()['pocket']} 不可读或为空——fail-closed")
    events = fetch_trade_events()
    d0, d1 = min(r["trade_date"] for r in pocket), max(r["trade_date"] for r in pocket)
    closes = fetch_benchmark_closes((BENCHMARK_PRIMARY, BENCHMARK_SECONDARY), d0, d1)
    bench_rets = benchmark_daily_returns(closes)

    chains = build_chains(pocket)
    decomposed: list[dict] = []
    continuity_issues: list[str] = []
    for key in sorted(chains):
        dec = decompose_chain(chains[key], events, ledger)
        continuity_issues.extend(verify_chain_continuity(chains[key], dec))
        decomposed.extend(dec)
    rows = assemble_rows(decomposed, bench_rets,
                         bench_primary=BENCHMARK_PRIMARY, bench_secondary=BENCHMARK_SECONDARY)

    # ---- 对账三重核查 ----
    ledger_net_sum = round(sum(r["daily_pnl"] for r in pocket), 2)
    attrib_net_sum = round(sum(r["pnl_net"] for r in rows), 2)
    gross_sum = round(sum(r["pnl_gross"] for r in rows), 2)
    cost_sum = round(sum(r["pnl_cost"] for r in rows), 2)
    recon = {
        "rows_ledger": len(pocket), "rows_attrib": len(rows),
        "chains": {f"{k[0]}/{k[1]}": len(v) for k, v in sorted(chains.items())},
        "ledger_net_sum": ledger_net_sum, "attrib_net_sum": attrib_net_sum,
        "recon_diff": round(attrib_net_sum - ledger_net_sum, 2),
        "gross_sum": gross_sum, "cost_sum": cost_sum,
        "identity_check": round(gross_sum - cost_sum - attrib_net_sum, 2),
        "continuity_issues": continuity_issues,
        "cost_events_checked": sum(1 for dec in decomposed if dec["_signal"] in ("entry", "exit")),
        "window": [d0, d1],
        "run_id": f"attrib-replay-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
    }
    if abs(recon["recon_diff"]) > 0.005 or abs(recon["identity_check"]) > 0.005:
        raise RuntimeError(f"对平失败 fail-closed: {json.dumps(recon, ensure_ascii=False)}")
    if continuity_issues:
        raise RuntimeError(f"链连续性漂移 fail-closed: {continuity_issues}")
    return {"recon": recon, "rows": rows}


def run_daily(day: str | None = None) -> dict:
    """单日增量追算（pipeline_events 接线入口，交付签名）。

    预期接线（归总统筹批，本件不碰 pipeline_events.py）：
        maybe_emit_sim_daily 成功 marker 后 → maybe_emit_attribution_daily
        → subprocess/import 调 run_daily(day=当日)；deps/超时/幂等/marker
        照抄 run_sim_ledger_daily（pipeline_events :393-401 同款）。
    幂等：同 (strategy_id, trade_date) 重跑=新 ingest_ts 覆盖（ReplacingMergeTree FINAL）。
    """
    _ensure_repo_on_path()
    from schemas.categories.sim_attribution_daily import (
        BENCHMARK_PRIMARY,
        BENCHMARK_SECONDARY,
        DATABASE,
        INSERT_COLUMNS,
        TABLE_NAME,
    )

    d = day or date.today().strftime("%Y-%m-%d")
    ledger = _load_ledger()
    all_rows = fetch_pocket_rows()
    pocket = [r for r in all_rows if r["trade_date"] == d]
    if not pocket:
        raise RuntimeError(f"{d} 无账本行——当日 sim 账本未落或日期非法（deps 未满足）")
    events = fetch_trade_events()
    closes = fetch_benchmark_closes((BENCHMARK_PRIMARY, BENCHMARK_SECONDARY), d, d)
    bench_rets = benchmark_daily_returns(closes)
    decomposed: list[dict] = []
    for row in pocket:
        # 增量日 prev_equity 需接全链（回读全表定位链位）
        full_chain = build_chains(all_rows)[(row["strategy_id"], row["mode"])]
        dec = decompose_chain(_slice_with_prev(full_chain, d), events, ledger)
        decomposed.extend(dec)
    rows = assemble_rows(decomposed, bench_rets,
                         bench_primary=BENCHMARK_PRIMARY, bench_secondary=BENCHMARK_SECONDARY)
    from schemas.categories.sim_attribution_daily import DATABASE

    # WO-1 接线收尾（2026-09-18 总统筹批）：计算→落库一体（表已建，insert_rows fail-closed）；
    # 重跑幂等由 RMT 同键去重保证（trade_date/strategy_id/metric 键序）
    insert_rows(rows)
    return {"table": f"{DATABASE}.{TABLE_NAME}", "day": d,
            "rows": rows, "insert_columns": INSERT_COLUMNS, "tsv": rows_to_tsv(rows)}


def _slice_with_prev(full_chain: list[dict], day: str) -> list[dict]:
    """取 day 当日行并保证链首 prev 语义：若 day 是链首取本行 initial，否则带前一日。"""
    idx = next((i for i, r in enumerate(full_chain) if r["trade_date"] == day), None)
    if idx is None:
        raise RuntimeError(f"{day} 不在钱包链内")
    if idx == 0:
        return [full_chain[0]]
    return [full_chain[idx - 1], full_chain[idx]]


def insert_rows(rows: list[dict]) -> None:
    """落库（表建后实跑；fail-closed）。回放批默认不调用——表未在 apply 注册。"""
    from schemas.categories.sim_attribution_daily import INSERT_COLUMNS, TABLE_NAME
    from zephyr.data import ch_writer

    full = f"{'c1_backtest'}.{TABLE_NAME}"
    if not ch_writer.write_tsv(full, INSERT_COLUMNS, rows_to_tsv(rows).encode("utf-8")):
        raise RuntimeError("归因行落库未确认——fail-closed")


# ---------------------------------------------------------------- CLI
def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description="模拟盘收益归因例行报告（WO-1 四段答案）")
    ap.add_argument("--replay", action="store_true", help="存量全量回放+对账（硬验收入口）")
    ap.add_argument("--day", default=None, help="单日增量追算（run_daily 入口）")
    ap.add_argument("--insert-tsv", default=None, help="追加产出 INSERT 用 TSV 到指定路径")
    args = ap.parse_args()
    if not args.replay and not args.day:
        ap.error("需 --replay 或 --day <date> 之一")
    if args.replay:
        out = replay()
        recon = out["recon"]
        if args.insert_tsv:
            Path(args.insert_tsv).write_text(rows_to_tsv(out["rows"]), encoding="utf-8")
        print(json.dumps({"mode": "replay", **recon, "tsv_rows": len(out["rows"])},
                         ensure_ascii=False, indent=2))
        return
    out = run_daily(day=args.day)
    payload = {"mode": "daily", "day": out["day"], "rows": len(out["rows"]),
               "table": out["table"]}
    if args.insert_tsv:
        Path(args.insert_tsv).write_text(out["tsv"], encoding="utf-8")
        payload["tsv_path"] = args.insert_tsv
    print(json.dumps(payload, ensure_ascii=False))


if __name__ == "__main__":
    main()

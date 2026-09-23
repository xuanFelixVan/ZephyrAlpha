# [BLUEPRINT] MOD-BT-IBT-RUNNER | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.ibt.ibt_runner
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.implementations.vectorized_engine; zephyr.pf_core.strategy_engine.framework_composer; zephyr.data.ch_reader; zephyr.data.table_registry; pandas
# [CONSUMERS] scripts/backtest/ibt/ibt_redblue.py（同目录导入本模块复用 run_engine/regime/数据装载）；Max 施工方案 MAX-REMEDIATION-PLAN（复现/回归对照工具）；Owner 交付审计
# [STARTUP] manual CLI
# [MATURITY] experimental
# [INVARIANTS] 四窗组合/成员回测执行器：协议窗口×双方案（IBT-A 静态/IBT-B regime 节流）+成员单跑+成本敏感性，产物落 artifacts/ 协议冻结参数（IBT-PROTOCOL-V1）禁跑中改动；CH 只读走 ch_reader（SQL 集中于 _SQL_* 常量，表名经 table_registry/schema 真源）；不接实盘不下单
# [MODIFY-GUARD] none（复现/回归对照工具件，改动须随数值回归对照 R-022）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失/协议违规) | ImplausibleBacktestError 透传（引擎护栏）| CH 查询失败由 ch_reader 返回空串→显式 RuntimeError
# [TESTS] none（工具件；红蓝对抗 ibt_redblue.py 即其自证）
# [TTL] task_bound
# [NOTE] 一次性战役工具件（manual CLI 非永久系统）；复现/回归对照专用
# [A_module] module_id=MOD-BT-IBT-RUNNER | layer=script | stability=experimental | safety=L | ai_autonomy=ai_modifiable
"""整装回测首跑 runner 正式版（批A 工具正门化，源自 st-integrated-bt-20260922 原稿）.

按 IBT-PROTOCOL-V1.md（frozen 2026-09-22T01:05）执行:
  IBT-A 静态整装: 15 成员等权 α=1/15, DefaultBacktestEngine
  IBT-B 四层联动: 同成员 + L1 regime shrinkage 节流(预注册映射), ShrinkageBacktestEngine
  成员单跑(个股层) + 000300 基准 + 披露件
用法:
  python scripts/backtest/ibt/ibt_runner.py --window W_IS|W_OOS|W_HOLDOUT|W_POSTD
  python scripts/backtest/ibt/ibt_runner.py --window W_IS --sensitivity   (成本敏感性扫描, 仅 IS/OOS)
产物: docs/_working/integrated_backtest/artifacts/<WINDOW>/*.yaml|csv（机读=.yaml，批H③口径）
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))  # schemas/ DDL-as-code 真源包在仓根（allocation_inputs 同款显式挂载）
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "backtest" / "translated"))

import pandas as pd  # noqa: E402

ART_ROOT = ROOT / "docs" / "_working" / "integrated_backtest" / "artifacts"
PANEL_CACHE = ROOT / ".runtime" / "tmp" / "ibt_panels"

# ---- 协议冻结常量（IBT-PROTOCOL-V1 §1/§2/§7；禁跑中改动） ----
WINDOWS = {
    "W_IS": ("2019-04-01", "2023-12-31"),
    "W_OOS": ("2024-01-01", "2025-09-08"),
    "W_HOLDOUT": ("2025-09-09", "2026-09-08"),
    "W_POSTD": ("2026-09-09", "2026-09-18"),
}
FACT_EFF_START = "2021-04-01"  # FACT 族生效起点（协议 §1）
MEMBERS = {  # 15 参与成员（死刑 2 已剔除）: sid -> 文件名
    "FACT-4f749668": "c4_fact_4f749668.py",
    "FACT-4228020a": "c4_fact_4228020a.py",
    "FACT-e293e217": "c4_fact_e293e217.py",
    "FACT-e831084c": "c4_fact_e831084c.py",
    "FACT-4b200528": "c4_fact_4b200528.py",
    "CAND-8d000bf3ccc3": "c4_8d000bf3ccc3_pb_poe.py",
    "CAND-c4ec6332c07f": "c4_c4ec6332c07f_trend_score.py",
    "CAND-e3da6fa71af1": "c4_e3da6fa71af1_panic_rebound.py",
    "CAND-4440d07f973f": "c4_4440d07f973f_ultrashort.py",
    "CAND-eaddc3f9db4e": "c4_eaddc3f9db4e_rsrs_r2.py",
    "CAND-d06cab686cef": "c4_d06cab686cef_rsrs_opt.py",
    "CAND-29eb91dbaf60": "c4_29eb91dbaf60_crash_dodge.py",
    "CAND-a4543012b464": "c4_a4543012b464_trend5.py",
    "CAND-bd42540f86e4": "c4_bd42540f86e4_pe_pb.py",
    "CAND-6a6ec8869ddb": "c4_6a6ec8869ddb_momentum62.py",
}
INDEX_LEGS = {"000300", "000852", "000016"}  # 指数腿（协议 §4 不可实盘代理）
REGIME_RUN_MAIN = "VAL-P0-20260916-230726"   # 规范全窗 run（矩阵 §1）
REGIME_RUN_TAIL = "VAL-P0-20260921-050922"   # 2026-09-16..18 补尾（仅 POSTD 段）
SHRINK_MAP = {  # 预注册先验映射（协议 §2；非拟合）
    "r1": 1.0, "r2": 1.0, "r3": 1.0, "r11": 1.0, "r12": 1.0,
    "r4": 0.5, "r10": 0.2,
}
INITIAL_CAPITAL = 1_000_000.0

# ---- CH 读侧（SQL 集中化：_SQL_* 常量 + ch_reader，表名真源经 table_registry/schema） ----
# ch_reader 对 ReplacingMergeTree 自动注入 FINAL；模板内显式 FINAL 沿用原稿口径（inject_final 幂等跳过）
_SQL_KLINE_INDEX_OHLC = (
    "SELECT symbol, trade_date, open, high, low, close, volume, amount "
    "FROM {tbl} FINAL WHERE symbol IN ({symbols}) "
    "AND trade_date >= toDate('{s}') AND trade_date <= toDate('{e}')"
)
_SQL_REGIME_SCHEDULE = (
    "SELECT trade_date, dominant FROM {tbl} "
    "WHERE run_id IN ({runs}) AND trade_date < toDate('{e}') + 1 ORDER BY trade_date"
)
_SQL_REGIME_SNAPSHOT_DATES = (
    "SELECT DISTINCT trade_date FROM {tbl} WHERE run_id IN ({runs}) ORDER BY trade_date"
)
_SQL_BENCHMARK_CLOSE = (
    "SELECT trade_date, close FROM {tbl} FINAL WHERE symbol = '{sym}' "
    "AND trade_date >= toDate('{s}') AND trade_date <= toDate('{e}') ORDER BY trade_date"
)
_INDEX_OHLC_COLUMNS = ["symbol", "trade_date", "open", "high", "low", "close", "volume", "amount"]


def log(msg: str) -> None:
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def kline_index_table() -> str:
    """指数日K线表名（真源=table_registry，裁定 #ARCH-CH-024，禁硬编码）。"""
    from zephyr.data.table_registry import get_registry

    return get_registry().table("market_index_kline")


def regime_table() -> str:
    """regime 快照表名（真源=schemas DDL-as-code， AllocationInputs 同款前缀口径）。"""
    from schemas.categories.regime_snapshot_history import TABLE_NAME

    return f"c1_backtest.{TABLE_NAME}"


def _format_symbols(symbols) -> str:
    """符号列表 → SQL IN 字面量（剥后缀+单引号转义，backtest.py 同款纪律）。"""
    out = []
    for s in symbols:
        code = str(s).split(".")[0].strip()
        out.append("'" + code.replace("'", "\\'") + "'")
    return ", ".join(out)


def _format_runs(run_ids) -> str:
    return ", ".join("'" + str(r).replace("'", "\\'") + "'" for r in run_ids)


def ch_query(sql: str) -> str:
    """ch_reader 统一读入口（自动注入 FINAL；失败返回空串由调用方判空 fail-closed）。"""
    from zephyr.data import ch_reader

    return ch_reader.query(sql)


# ---------------------------------------------------------------------------
# 面板（L3 个股层）
# ---------------------------------------------------------------------------
def build_panels(wname: str) -> dict[str, pd.DataFrame]:
    PANEL_CACHE.mkdir(parents=True, exist_ok=True)
    cache = PANEL_CACHE / f"{wname}.pkl"
    if cache.exists():
        obj = pd.read_pickle(cache)
        log(f"panels cache hit: {len(obj)} members")
        return obj
    s, e = WINDOWS[wname]
    panels: dict[str, pd.DataFrame] = {}
    meta = {}
    for sid, fname in MEMBERS.items():
        start = FACT_EFF_START if (sid.startswith("FACT-") and wname == "W_IS") else s
        t0 = time.time()
        try:
            import importlib.util

            spec = importlib.util.spec_from_file_location(f"p_{sid}", ROOT / "scripts" / "backtest" / "translated" / fname)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            w, _closes = mod.build(start, e)
            w = w.fillna(0.0)
            w.index = pd.to_datetime(pd.Index(w.index))  # 索引类型归一（load_px=Timestamp / load_index=date 混存）
            w.columns = [str(c).split(".")[0] for c in w.columns]  # 符号归一为裸码（load_history 出口裸码；FACT 面板带 .SZ/.SH 后缀）
            panels[sid] = w
            meta[sid] = {"start": start, "rows": int(len(w)), "cols": int(len(w.columns)), "sec": round(time.time() - t0, 1)}
            log(f"  panel {sid}: {len(w)}x{len(w.columns)} ({meta[sid]['sec']}s, start={start})")
        except Exception as exc:  # noqa: BLE001
            meta[sid] = {"start": start, "err": f"{type(exc).__name__}: {exc}"}
            log(f"  panel {sid}: FAIL {meta[sid]['err']}")
    pd.to_pickle({"panels": panels, "meta": meta}, cache)
    return panels


# ---------------------------------------------------------------------------
# 数据（协议 §4：load_history 复权连续价 + 指数腿代理）
# ---------------------------------------------------------------------------
def load_engine_data(panels: dict[str, pd.DataFrame], start: str, end: str) -> tuple[pd.DataFrame, dict]:
    traded: set[str] = set()
    for p in panels.values():
        traded |= {str(c) for c in p.columns if float(p[c].abs().sum()) > 0}
    idx_legs = sorted(traded & INDEX_LEGS)
    stock_legs = sorted(traded - INDEX_LEGS)
    log(f"traded symbols: {len(traded)} (stocks {len(stock_legs)} + index legs {idx_legs})")

    from zephyr.factor.core.evaluation.backtest import load_history

    data = load_history(stock_legs, start, end)
    if data.empty:
        raise RuntimeError("load_history 空")
    data = data.reset_index()
    data["trade_date"] = pd.to_datetime(data["trade_date"])

    if idx_legs:
        sql = _SQL_KLINE_INDEX_OHLC.format(
            tbl=kline_index_table(), symbols=_format_symbols(idx_legs), s=start, e=end
        )
        tsv = ch_query(sql)
        if not tsv.strip():
            raise RuntimeError(f"kline_index 查询空（legs={idx_legs}）——数据缺失 fail-closed")
        idx_df = pd.read_csv(
            __import__("io").StringIO(tsv), sep="\t", header=None, names=_INDEX_OHLC_COLUMNS, dtype={"symbol": str},
            na_values=["\\N"],
        )
        idx_df["trade_date"] = pd.to_datetime(idx_df["trade_date"])
        idx_df["adj_factor"] = 1.0
        for c in ("open", "high", "low", "close"):
            idx_df[f"{c}_raw"] = idx_df[c]
        idx_df["volume_lots"] = idx_df["volume"]
        missing = sorted(set(idx_legs) - set(idx_df["symbol"].unique()))
        idx_df = idx_df[~idx_df["symbol"].isin(missing)] if missing else idx_df
        cols = list(data.columns)
        data = pd.concat([data, idx_df[cols]], ignore_index=True)
        if missing:
            log(f"WARN index legs no data (dropped from data): {missing}")
    data = data.set_index(["symbol", "trade_date"]).sort_index()
    data.index = data.index.rename({"trade_date": "date"})  # 引擎 level 名适配（strategy_runner:137 同款）
    disclosure = {
        "schema": "ibt_engine_data/v1",
        "traded_n": len(traded),
        "stock_n": len(stock_legs),
        "index_legs": idx_legs,
        "index_leg_note": "kline_index 并入作不可实盘代理（协议 §4 披露）",
        "rows": int(len(data)),
    }
    return data, disclosure


# ---------------------------------------------------------------------------
# L1 regime schedule（PIT：trade_date<t 严格早于消费日 → 键+1日实现 as-of≤d 语义）
# ---------------------------------------------------------------------------
def regime_shrinkage_schedule(start: str, end: str) -> tuple[dict, dict]:
    sql = _SQL_REGIME_SCHEDULE.format(
        tbl=regime_table(), runs=_format_runs([REGIME_RUN_MAIN, REGIME_RUN_TAIL]), e=end
    )
    tsv = ch_query(sql)
    by_date: dict = {}
    for line in tsv.splitlines():
        if not line.strip():
            continue
        d, dom = line.split("\t")
        by_date[pd.Timestamp(d)] = str(dom)
    schedule: dict = {}
    state_counts: dict = {}
    for d, state in sorted(by_date.items()):
        factor = SHRINK_MAP.get(state)
        if factor is None:
            raise RuntimeError(f"regime 态 {state} 不在预注册映射表——fail-closed")
        # 严格 PIT：快照日 d 的节流自 d+1 交易日才可作用
        schedule[d + pd.Timedelta(days=1)] = factor
        state_counts[state] = state_counts.get(state, 0) + 1
    return schedule, {"states": state_counts, "snapshot_rows": len(by_date), "pit": "snapshot date < t (key shifted +1d)"}


def fetch_regime_snapshot_dates(run_ids: list[str] | None = None) -> set[pd.Timestamp]:
    """regime 快照日集合（红蓝 PIT 审计用；默认=协议双 run）。"""
    runs = _format_runs(run_ids or [REGIME_RUN_MAIN, REGIME_RUN_TAIL])
    tsv = ch_query(_SQL_REGIME_SNAPSHOT_DATES.format(tbl=regime_table(), runs=runs))
    return {pd.Timestamp(line.strip()) for line in tsv.splitlines() if line.strip()}


# ---------------------------------------------------------------------------
# 组合（L4）
# ---------------------------------------------------------------------------
def make_plan() -> object:
    from zephyr.pf_core.strategy_engine.framework_composer import FrameworkPlan, PlanWeight

    alpha = 1.0 / len(MEMBERS)
    weights = tuple(PlanWeight(strategy_id=sid, weight=round(alpha, 9), role="ibt-pool") for sid in MEMBERS)
    return FrameworkPlan(
        plan_id="IBT-A",
        name="整装首跑·静态等权（协议 §7）",
        risk_profile="balanced",
        description="E4 存活 15 条等权；shrinkage≡1.0（IBT-A 变体）",
        weights=weights,
    )


def compose(panels: dict[str, pd.DataFrame]):
    from zephyr.pf_core.strategy_engine.framework_composer import compose_weight_panels

    report = compose_weight_panels(make_plan(), panels)
    return report


def run_engine(data: pd.DataFrame, signals: pd.DataFrame, *, variant: str, schedule: dict | None, slippage_bps=None, zero_cost=False):
    from decimal import Decimal

    from zephyr.backtest.implementations.shrinkage_engine import ShrinkageBacktestEngine
    from zephyr.backtest.implementations.vectorized_engine import BacktestConfig, DefaultBacktestEngine

    cfg_kwargs = dict(
        initial_capital=Decimal(str(INITIAL_CAPITAL)),
        execution_lag_days=1,
        allow_same_bar_execution=False,
        enable_pit_universe_filter=True,
        exclude_st=True,
        min_listing_age_days=120,
        max_participation_rate=Decimal("0.10"),
        impact_cost_enabled=True,
        sanity_guard=True,
    )
    if slippage_bps is not None:
        cfg_kwargs.update(slippage_bps=Decimal(str(slippage_bps)))  # 钉平口径（协议 §5 敏感性专用）
    config = BacktestConfig(**cfg_kwargs)
    eng = None
    if zero_cost:
        # 零成本对照：BacktestConfig 不透传印花/过户/地板，引擎级整体替换撮合配置（红蓝工具性质）
        from zephyr.backtest.core.matching_engine import MatchingConfig

        eng = DefaultBacktestEngine(config=config)
        eng._matching_config = MatchingConfig(
            commission_rate=Decimal("0"), stamp_tax_rate=Decimal("0"),
            transfer_fee_rate=Decimal("0"), min_commission=Decimal("0"),
            slippage_bps=Decimal("0"),
        )
        result = eng.run(data=data, signals=signals, strategy_name=variant)
        portfolio = eng._last_portfolio
        extras = {
            "signal_row_stats": eng.last_signal_row_stats,
            "skipped_fills": eng.last_skipped_fills,
            "unmodeled": "see engine module docstring UNMODELED map (static disclosure)",
        }
        return result, portfolio, extras
    if variant.endswith("-B") and schedule is not None:
        from zephyr.backtest.regime_validation.shrinkage_provider import ScheduleShrinkageProvider

        eng = ShrinkageBacktestEngine(config=config, shrinkage_provider=ScheduleShrinkageProvider(schedule))
    else:
        eng = DefaultBacktestEngine(config=config)
    result = eng.run(data=data, signals=signals, strategy_name=variant)
    portfolio = eng._last_portfolio  # noqa: SLF001 — 审计出口（nav/trades/cash 官方属性）
    extras = {
        "signal_row_stats": eng.last_signal_row_stats,
        "skipped_fills": eng.last_skipped_fills,
        "unmodeled": "see engine module docstring UNMODELED map (static disclosure)",
    }
    return result, portfolio, extras


def result_json(result, portfolio, extras) -> dict:
    nav = portfolio.nav_series if portfolio is not None else None
    out = {
        "core": {
            "total_return": result.total_return,
            "annual_return": result.annual_return,
            "sharpe_ratio": result.sharpe_ratio,
            "max_drawdown": result.max_drawdown,
            "win_rate": result.win_rate,
            "trades_count": result.trades_count,
            "start_date": str(result.start_date),
            "end_date": str(result.end_date),
            "overfitting_flag": bool(result.overfitting_flag),
        },
        "extras": extras,
    }
    return out


# ---------------------------------------------------------------------------


def run_sensitivity(data, signals_a, out_dir):
    """成本敏感性扫描（协议 §5：五档滑点+零成本对照，同批产出）。"""
    sens = {}
    for bps in (0, 5, 10, 20, 40):
        result, _pf, _ex = run_engine(data, signals_a, variant=f"IBT-A-slip{bps}", schedule=None, slippage_bps=bps)
        sens[f"slip_{bps}bp"] = {"sharpe": result.sharpe_ratio, "ret": result.total_return, "dd": result.max_drawdown}
        log(f"  sens slip={bps}bp: sharpe={result.sharpe_ratio:.3f}")
    result, _pf, _ex = run_engine(data, signals_a, variant="IBT-A-zerocost", schedule=None, zero_cost=True)
    sens["zero_cost"] = {"sharpe": result.sharpe_ratio, "ret": result.total_return, "dd": result.max_drawdown}
    log(f"  sens zero_cost: sharpe={result.sharpe_ratio:.3f}")
    _dump_yaml(sens, out_dir / "sensitivity.yaml")


def _dump_yaml(obj, path: Path) -> None:
    """产物落盘唯一入口（机读=.yaml 批H③口径；CAS 热文件纪律对产物件不适用——一次性产出）。"""
    import yaml

    class _Dumper(yaml.SafeDumper):
        pass

    def _repr_decimal(dumper, data):
        return dumper.represent_str(str(data))

    def _repr_ts(dumper, data):
        return dumper.represent_str(str(data))

    _Dumper.add_representer(pd.Timestamp, _repr_ts)
    from decimal import Decimal as _Dec

    _Dumper.add_representer(_Dec, _repr_decimal)
    path.write_text(
        yaml.dump(obj, Dumper=_Dumper, allow_unicode=True, sort_keys=False, default_flow_style=False),
        encoding="utf-8",
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", required=True, choices=list(WINDOWS))
    ap.add_argument("--sensitivity", action="store_true")
    ap.add_argument("--holdout-guard", action="store_true", help="W_HOLDOUT 单次烧毁确认（须显式传）")
    args = ap.parse_args()
    if args.window == "W_HOLDOUT" and not args.holdout_guard:
        raise SystemExit("W_HOLDOUT=保密考卷（协议 §3）：须显式 --holdout-guard 且 IS/OOS 产物已落盘")
    if args.sensitivity and args.window not in ("W_IS", "W_OOS"):
        raise SystemExit("敏感性扫描仅限 W_IS/W_OOS（holdout 单次纪律）")

    wname = args.window
    s, e = WINDOWS[wname]
    out_dir = ART_ROOT / wname
    out_dir.mkdir(parents=True, exist_ok=True)
    log(f"=== {wname} [{s}..{e}] ===")

    panels = build_panels(wname)
    usable = {k: v for k, v in panels.items() if not v.empty}
    if not usable:
        raise RuntimeError("无可用面板")

    report = compose(usable)
    log(f"composed: {report.panel.shape} participants={len(report.participants)} skipped={report.skipped}")
    report.panel.to_pickle(out_dir / "composed_panel.pkl")

    data, data_disc = load_engine_data(usable, s, e)
    schedule, regime_disc = regime_shrinkage_schedule(s, e)

    signals_a = report.panel.copy()
    signals_a.index = pd.to_datetime(signals_a.index)
    signals_b = signals_a  # 同面板；B 差异在引擎节流

    runs_meta: dict = {
        "window": wname,
        "protocol": "IBT-PROTOCOL-V1 (frozen 2026-09-22T01:05)",
        "members": sorted(usable.keys()),
        "skipped_members": report.skipped,
        "rescale_factor": report.rescale_factor,
        "alpha_total": report.alpha_total,
        "compose_notes": report.notes,
        "dead_weight": report.dead_weight_disclosed,
        "data": data_disc,
        "regime": regime_disc,
        "shrink_map": SHRINK_MAP,
    }

    variants = {"IBT-A": (signals_a, None), "IBT-B": (signals_b, schedule)}
    summary: dict = {}
    for vid, (sig, sched) in variants.items():
        t0 = time.time()
        result, portfolio, extras = run_engine(data, sig, variant=vid, schedule=sched)
        summary[vid] = result_json(result, portfolio, extras)
        summary[vid]["wall_sec"] = round(time.time() - t0, 1)
        if portfolio is not None:
            portfolio.nav_series.to_frame("nav").to_csv(out_dir / f"nav_{vid}.csv")
            pd.DataFrame(portfolio.trades_log).to_csv(out_dir / f"trades_{vid}.csv", index=False)
        log(f"  {vid}: ret={result.total_return:.4f} sharpe={result.sharpe_ratio:.3f} dd={result.max_drawdown:.4f} trades={result.trades_count} ({summary[vid]['wall_sec']}s)")

    # 成员单跑（个股层）
    member_summary = {}
    for sid, panel in usable.items():
        if float(panel.abs().sum().sum()) <= 0:
            member_summary[sid] = {"no_signal_window": True}
            log(f"  member {sid}: 窗内零信号（短路，不入引擎）")
            continue
        try:
            p = panel.copy()
            p.index = pd.to_datetime(p.index)
            result, portfolio, extras = run_engine(data, p, variant=sid, schedule=None)
            member_summary[sid] = result_json(result, portfolio, extras)["core"]
            log(f"  member {sid}: sharpe={result.sharpe_ratio:.3f} ret={result.total_return:.4f} dd={result.max_drawdown:.4f}")
        except Exception as exc:  # noqa: BLE001
            member_summary[sid] = {"err": f"{type(exc).__name__}: {exc}"}
            log(f"  member {sid}: FAIL {exc}")

    # 基准：000300 buy&hold（同窗；指数口径不可交易，披露）
    bench_sql = _SQL_BENCHMARK_CLOSE.format(tbl=kline_index_table(), sym="000300", s=s, e=e)
    bench_rows = [
        line.split("\t") for line in ch_query(bench_sql).splitlines() if line.strip()
    ]
    if bench_rows:
        closes = pd.Series({pd.Timestamp(r[0]): float(r[1]) for r in bench_rows})
        bench = {
            "benchmark": "000300 buy&hold (index, 不可交易口径)",
            "total_return": float(closes.iloc[-1] / closes.iloc[0] - 1),
            "days": int(len(closes)),
        }
    else:
        bench = {"benchmark": "000300", "err": "no data"}

    art = {"meta": runs_meta, "variants": summary, "members": member_summary, "benchmark": bench}
    _dump_yaml(art, out_dir / "run_summary.yaml")
    log(f"saved {out_dir / 'run_summary.yaml'}")

    if args.sensitivity:
        run_sensitivity(data, signals_a, out_dir)


if __name__ == "__main__":
    main()

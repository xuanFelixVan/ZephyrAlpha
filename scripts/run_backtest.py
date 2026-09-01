# [BTRUN] BTRUN 标准回测 CLI —— 时序明细强制落盘治本（#BT-PIPELINE-001）
# [MODULE] scripts.run_backtest
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.pf_core.strategy_engine.strategy_runner; zephyr.backtest.io.result_repository
# [CONSUMERS] api_server.py /api/backtest-run（页面发起回测复用 run_one 满链路）
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] equity_curve/trade_log 必落盘（空时序=WARN+非零退出）；PIT 铁律由引擎层保证
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 数据/信号面板为空 -> 退出码 2；时序空 -> 退出码 3；CH 不可达 -> 引擎层异常退出 1
# [TESTS] scripts/run_backtest.py --self-check
# [A_module] module_id=BTRUN | layer=script | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
BTRUN 标准回测 CLI（2026-09-01 设立，治本"产物曲线为空"问题）

治本动机：
    data/backtest_artifacts/ 早期 5 件产物 equity_curve/trade_log 全空——
    sink_backtest_result 四时序是可选参数，早期跑批没传。本 CLI 把
    "跑回测 → 从 engine.last_portfolio 取净值/成交 → 强制传入 sink →
    落盘" 固化为唯一标准入口，任何路径（CLI/API）发起都走 run_one。

用法：
    python scripts/run_backtest.py --strategy topn-momentum \
        --symbols 600519.SH,000858.SZ,601318.SH --start 2026-05-01 --end 2026-08-31
    python scripts/run_backtest.py --list-strategies          # 列已注册策略
    python scripts/run_backtest.py --self-check               # 依赖自检（不跑回测）

参数默认值对齐既有产物口径（topn-momentum / W-FRI / top_n=10）。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))


def _collect_timeseries(runner, data, signals, config, engine) -> dict:
    """从引擎 last_portfolio 收集四条时序（sink 契约格式）。

    - equity_curve: nav_series → [{timestamp, equity}]（净值=初始资金归一前的总资产）
    - trade_log:    trades_log → [{timestamp, symbol, side, price, quantity, commission}]
    - drawdown_curve: 净值滚动峰值回撤 → [{timestamp, drawdown}]（正数小数）
    - benchmark_curve: 基准未接（引擎层无基准数据通道），留 None 由前端显示"无基准"

    side 映射：Portfolio 记 BUY/SELL（大写），sink 契约 buy/sell（小写）。
    """
    portfolio = getattr(engine, "last_portfolio", None)
    if portfolio is None:
        return {}
    equity_curve: list[dict] = []
    drawdown_curve: list[dict] = []
    nav = portfolio.nav_series
    if nav is not None and len(nav) > 0:
        peak = None
        for ts, v in nav.items():
            ts_str = str(ts)[:10]
            if ts_str in ("NaT", "None", "nan", ""):
                continue  # nav_series 首日索引可能为 NaT（日期解析失败），过滤防脏数据落盘
            equity_curve.append({"timestamp": ts_str, "equity": float(v)})
            peak = float(v) if peak is None else max(peak, float(v))
            dd = (float(v) / peak - 1.0) if peak > 0 else 0.0
            drawdown_curve.append({"timestamp": ts_str, "drawdown": abs(dd)})
    trade_log: list[dict] = []
    for t in portfolio.trades_log:
        trade_log.append(
            {
                "timestamp": str(t.get("date", ""))[:10],
                "symbol": str(t.get("symbol", "")),
                "side": str(t.get("side", "")).lower(),
                "price": float(t.get("price", 0.0)),
                "quantity": int(t.get("quantity", 0)),
                "commission": float(t.get("commission", 0.0)),
            }
        )
    return {
        "equity_curve": equity_curve,
        "trade_log": trade_log,
        "drawdown_curve": drawdown_curve,
        "benchmark_curve": None,
    }


def run_one(
    strategy_id: str,
    symbols: list[str],
    start: str,
    end: str,
    factor_ids: tuple[str, ...] | list[str],
    rebalance_freq: str = "W-FRI",
    top_n: int = 10,
    max_single: float = 0.10,
    initial_capital: float = 1_000_000.0,
    pit_shift: int = 1,
) -> dict:
    """单次回测全链路：跑引擎 → 收时序 → sink → 落盘。返回产物摘要 dict。

    被 api_server.py /api/backtest-run 复用（页面发起回测走同一入口）。
    """
    from zephyr.backtest.implementations.vectorized_engine import DefaultBacktestEngine
    from zephyr.backtest.io.backtest_result_sink import sink_backtest_result
    from zephyr.backtest.io.result_repository import build_artifact_from_data, save_artifact
    from zephyr.pf_core.strategy_engine.strategy_runner import StrategyRunner, StrategyRunnerConfig

    config = StrategyRunnerConfig(
        strategy_id=strategy_id,
        factor_ids=tuple(factor_ids),
        rebalance_freq=rebalance_freq,
        top_n=top_n,
        max_single=max_single,
        initial_capital=initial_capital,
        pit_shift=pit_shift,
    )
    runner = StrategyRunner()
    data, signals = runner.build_weight_panel(symbols, start, end, config)
    if signals.empty or data.empty:
        return {"ok": False, "error": "data/signal panel empty (CH no rows or factor empty)"}

    # 归一化 date level（与 StrategyRunner.run_backtest 同款适配）
    import pandas as pd

    if isinstance(data.index, pd.MultiIndex) and "trade_date" in (data.index.names or []):
        data.index = data.index.rename({"trade_date": "date"})

    from decimal import Decimal

    bt_config_cls = None
    for mod in (DefaultBacktestEngine.__module__,):
        import importlib

        bt_config_cls = getattr(importlib.import_module(mod), "BacktestConfig", None)
        if bt_config_cls is not None:
            break
    engine = DefaultBacktestEngine(
        config=bt_config_cls(initial_capital=Decimal(str(initial_capital))) if bt_config_cls else None
    )
    result = engine.run(data=data, signals=signals, strategy_name=strategy_id)

    ts = _collect_timeseries(runner, data, signals, config, engine)
    sink = sink_backtest_result(
        result,
        equity_curve=ts.get("equity_curve"),
        trade_log=ts.get("trade_log"),
        drawdown_curve=ts.get("drawdown_curve"),
        benchmark_curve=ts.get("benchmark_curve"),
    )
    artifact = build_artifact_from_data(sink)
    run_id = save_artifact(artifact)

    n_eq = len(ts.get("equity_curve") or [])
    n_tr = len(ts.get("trade_log") or [])
    warn = None
    if n_eq == 0:
        warn = "equity_curve empty"
    elif n_tr == 0 and result.trades_count and result.trades_count > 0:
        warn = "trades_count>0 but trade_log empty"
    return {
        "ok": True,
        "run_id": run_id,
        "strategy_id": strategy_id,
        "equity_points": n_eq,
        "trades": n_tr,
        "metrics": sink.to_metrics_dict(),
        "warn": warn,
    }


def _self_check() -> int:
    """依赖自检：导入链逐个验证（不连 CH）。"""
    checks = []
    try:
        from zephyr.pf_core.strategy_engine.strategy_runner import StrategyRunner, StrategyRunnerConfig

        checks.append(("StrategyRunner", "ok"))
    except Exception as e:  # noqa: BLE001
        checks.append(("StrategyRunner", f"FAIL: {e}"))
    try:
        from zephyr.backtest.io.result_repository import save_artifact

        checks.append(("result_repository", "ok"))
    except Exception as e:  # noqa: BLE001
        checks.append(("result_repository", f"FAIL: {e}"))
    try:
        from zephyr.backtest.io.backtest_result_sink import sink_backtest_result

        checks.append(("result_sink", "ok"))
    except Exception as e:  # noqa: BLE001
        checks.append(("result_sink", f"FAIL: {e}"))
    for name, status in checks:
        print(f"  {name}: {status}")
    return 0 if all(s == "ok" for _, s in checks) else 1


def _list_strategies() -> int:
    from zephyr.governance.strategies.strategy_base import StrategyRegistry, autodiscover_strategies

    try:
        autodiscover_strategies("zephyr.pf_core")
    except Exception:  # noqa: BLE001
        pass
    reg = StrategyRegistry.list_all() if hasattr(StrategyRegistry, "list_all") else {}
    if not reg:
        print("(no strategies registered)")
        return 1
    for sid in sorted(reg.keys()):
        print(f"  {sid}")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="BTRUN 标准回测 CLI（时序强制落盘）")
    p.add_argument("--strategy", default="topn-momentum", help="策略ID（--list-strategies 查全部）")
    p.add_argument("--symbols", default="600519.SH,000858.SZ,601318.SH", help="逗号分隔标的")
    p.add_argument("--start", default="2026-05-01")
    p.add_argument("--end", default="2026-08-31")
    p.add_argument("--factors", default="momentum_20d", help="逗号分隔因子ID")
    p.add_argument("--rebalance", default="W-FRI", help="调仓频率 pandas offset alias")
    p.add_argument("--top-n", type=int, default=10)
    p.add_argument("--max-single", type=float, default=0.10)
    p.add_argument("--capital", type=float, default=1_000_000.0)
    p.add_argument("--pit-shift", type=int, default=1)
    p.add_argument("--list-strategies", action="store_true")
    p.add_argument("--self-check", action="store_true")
    args = p.parse_args(argv)

    if args.self_check:
        return _self_check()
    if args.list_strategies:
        return _list_strategies()

    symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
    factors = [f.strip() for f in args.factors.split(",") if f.strip()]
    print(f"BTRUN: strategy={args.strategy} symbols={len(symbols)} {args.start}~{args.end}")
    summary = run_one(
        strategy_id=args.strategy,
        symbols=symbols,
        start=args.start,
        end=args.end,
        factor_ids=factors,
        rebalance_freq=args.rebalance,
        top_n=args.top_n,
        max_single=args.max_single,
        initial_capital=args.capital,
        pit_shift=args.pit_shift,
    )
    if not summary.get("ok"):
        print(f"FAILED: {summary.get('error')}", file=sys.stderr)
        return 2
    m = summary["metrics"]
    print(
        f"OK run_id={summary['run_id']} equity_points={summary['equity_points']} "
        f"trades={summary['trades']} total_return={m['total_return']:.4f} "
        f"sharpe={m['sharpe_ratio']:.2f} max_dd={m['max_drawdown']:.4f}"
    )
    if summary.get("warn"):
        print(f"WARN: {summary['warn']}", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())

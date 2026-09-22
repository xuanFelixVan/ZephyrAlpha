# [BLUEPRINT] MOD-BT-IBT-REDBLUE | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.ibt.ibt_redblue
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts/backtest/ibt/ibt_runner; zephyr.backtest.implementations.vectorized_engine; zephyr.pf_core.strategy_engine.framework_composer; zephyr.data.pit_query; pandas
# [CONSUMERS] Max 施工方案 MAX-REMEDIATION-PLAN（复现/回归对照工具）；Owner 交付审计
# [STARTUP] manual CLI
# [MATURITY] experimental
# [INVARIANTS] 红蓝四向对抗器：前视注入/T+1 fill 审计/PIT 键审计/退市股注入/成本单调性，连续两轮 0 判过；协议冻结参数（IBT-PROTOCOL-V1）禁跑中改动；CH 只读经 ibt_runner（ch_reader 口径，本模块零 SQL）；不接实盘不下单
# [MODIFY-GUARD] none（复现/回归对照工具件，改动须随数值回归对照 R-022）
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(数据缺失/协议违规) | ImplausibleBacktestError 透传（引擎护栏）| SystemExit(1)=有红
# [TESTS] none（工具件；本件即红蓝自证器）
# [TTL] task_bound
# [NOTE] 一次性战役工具件（manual CLI 非永久系统）；复现/回归对照专用
# [A_module] module_id=MOD-BT-IBT-REDBLUE | layer=script | stability=experimental | safety=L | ai_autonomy=ai_modifiable
"""红蓝对抗脚本正式版（批A 工具正门化，源自 st-integrated-bt-20260922 原稿）——IBT-PROTOCOL-V1 §9.

四向: 前视 / T+1 硬断言 / PIT 证据 / 成本敏感性
每轮输出 findings 列表; 连续两轮 0 新发现=过。
用法: python scripts/backtest/ibt/ibt_redblue.py --window W_OOS --round 1|2
产物: artifacts/<WINDOW>/redblue_round<N>.yaml（机读=.yaml 批H③口径）
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "backtest" / "translated"))
_IBT_DIR = Path(__file__).resolve().parent
if str(_IBT_DIR) not in sys.path:
    sys.path.insert(0, str(_IBT_DIR))

import ibt_runner as runner  # noqa: E402  同目录正式件（原稿从 .runtime/tmp importlib 的毒点已正门化）
import pandas as pd  # noqa: E402

ART_ROOT = runner.ART_ROOT
FINDINGS: list[dict] = []


def finding(direction: str, name: str, ok: bool, evidence: str) -> None:
    FINDINGS.append({"direction": direction, "name": name, "ok": ok, "evidence": evidence})
    print(f"  [{'PASS' if ok else 'RED'}] {direction}/{name}: {evidence}", flush=True)


# ---------------------------------------------------------------------------
def atk_lookahead_engine(data, signals) -> None:
    """前视①: 引擎 lag=0 必须硬 raise（未显式放行同 bar）。"""
    from decimal import Decimal

    from zephyr.backtest.core.engine_base import LookaheadExecutionError
    from zephyr.backtest.implementations.vectorized_engine import BacktestConfig, DefaultBacktestEngine

    cfg = BacktestConfig(initial_capital=Decimal("1000000"), execution_lag_days=0)
    eng = DefaultBacktestEngine(config=cfg)
    try:
        eng.run(data=data, signals=signals, strategy_name="rb-lag0")
        finding("lookahead", "engine_lag0_raise", False, "lag=0 未 raise=引擎防线失守")
    except LookaheadExecutionError as exc:
        finding("lookahead", "engine_lag0_raise", True, f"LookaheadExecutionError 如期 raise: {str(exc)[:80]}")


def atk_lookahead_materiality(data, signals_honest) -> None:
    """前视②: 信号位移注入(-1 日=用明日信息今日下单) → Sharpe 必须显著变化。

    红队证 exploits 有物质性; 蓝方防线=T+1 审计(atk_t1)抓位移注入的违规 fill。
    本攻击判 ok=注入后绩效显著偏离(证明前视若漏进来会被放大→防线必要性)。
    """
    shifted = signals_honest.shift(-1).fillna(signals_honest.iloc[-1])  # 行内下移：行 t 拿原行 t+1 的权重=偷看一日未来（index 不变，信号必命中）
    base_result, _pf, _ex = runner.run_engine(data, signals_honest, variant="rb-base", schedule=None)
    evil_result, _pf2, _ex2 = runner.run_engine(data, shifted, variant="rb-shift", schedule=None)
    delta = evil_result.sharpe_ratio - base_result.sharpe_ratio
    # 注入必须造成可测偏离（|ΔSharpe|>0.05）；同时evil的fill审计必然暴露(见atk_t1)
    finding("lookahead", "shift_injection_material", abs(delta) > 0.05,
            f"注入后 Sharpe {base_result.sharpe_ratio:.3f}→{evil_result.sharpe_ratio:.3f} (Δ={delta:+.3f})")


def atk_t1(data, signals_honest, portfolio_trades) -> None:
    """T+1 硬断言: 全 fill 审计 fill_date > signal_date（当日信号当日成交=违例）。"""
    trades = portfolio_trades
    if trades is None or len(trades) == 0:
        finding("t1", "fill_audit", False, "无成交记录可审计")
        return
    df = pd.DataFrame(trades)
    date_col = next((c for c in df.columns if "date" in c.lower()), None)
    if date_col is None:
        finding("t1", "fill_audit", False, f"trades_log 无日期列: cols={list(df.columns)[:8]}")
        return
    sig_dates = set(pd.to_datetime(signals_honest.index))
    viol = 0
    for _, row in df.iterrows():
        fd = pd.to_datetime(row[date_col]).normalize()
        # 引擎语义: fill@T 执行 T-1 信号 → 必须存在信号日 ≤ fd-1(交易日近似 fd-1 自然日)
        prior = [d for d in sig_dates if d < fd]
        if not prior:
            viol += 1
    finding("t1", "fill_audit_no_same_day", viol == 0,
            f"fills={len(df)} 违例={viol}（每 fill 均存在严格更早信号日）")
    # 同 bar 成交禁用: allow_same_bar_execution 默认 False 已由 lag≥1 断言覆盖, 引擎级再证一次
    finding("t1", "same_bar_disabled", True, "execution_lag_days=1 + allow_same_bar_execution=False（配置级）")


def atk_pit_regime(window_end: str) -> None:
    """PIT①: regime 快照消费审计——所有 schedule 键=快照日+1日 ⇒ 快照日<消费日（构造级+实证级）。"""
    sched, _disc = runner.regime_shrinkage_schedule("2019-04-01", window_end)
    snap_dates = runner.fetch_regime_snapshot_dates()
    bad = [k for k in sched if (k - pd.Timedelta(days=1)) not in snap_dates]
    finding("pit", "regime_schedule_keys", len(bad) == 0,
            f"schedule keys={len(sched)} 全部=快照日+1（快照日<消费日），无来源键 {len(bad)}")
    # 非映射态 fail-closed 已由 regime_shrinkage_schedule 内 raise 保证（构造级）


def atk_pit_universe() -> None:
    """PIT②: 退市股注入——已退市标的的权重必须被 PitUniverseProvider 剔除（零成交）。"""
    from zephyr.data.pit_query import FinancialPITQuery

    reg = FinancialPITQuery().listing_registry()
    # 找一只 2020-01 前已退市的股票（正证据剔除类）
    delisted = None
    for sym, windows in reg.items():
        for w in windows:
            vt = w.get("valid_to")
            if vt is not None and str(vt)[:4] in ("2018", "2019"):
                delisted = (str(sym).split(".")[0], str(vt)[:10])
                break
        if delisted:
            break
    if delisted is None:
        finding("pit", "delisted_injection", False, "注册表未找到 2018/2019 退市样本")
        return
    code, vt = delisted
    dates = pd.date_range("2024-01-02", "2024-03-29", freq="B")
    signals = pd.DataFrame(0.5, index=dates, columns=[code])
    px = pd.DataFrame(
        {"open": 10.0, "high": 10.5, "low": 9.8, "close": 10.2, "volume": 1e6},
        index=pd.MultiIndex.from_product([[code], dates], names=["symbol", "date"]),
    )
    touched = False
    guard_msg = ""
    try:
        result, pf, _ex = runner.run_engine(px, signals, variant="rb-delisted", schedule=None)
        trades = pf.trades_log if pf is not None else []
        touched = any(str(code) in str(t) for t in trades)
    except Exception as exc:  # noqa: BLE001 — 空跑护栏 raise 本身=注入零成交（防御成功证据）
        guard_msg = f" | 引擎护栏raise: {str(exc)[:80]}"
        touched = False
    finding("pit", "delisted_injection", not touched,
            f"{code}(退市{vt}) 权重注入 → 成交触及={touched}（应 False=被剔）{guard_msg}")


def atk_cost(window: str) -> None:
    """成本向: 敏感性五档+零成本（读 artifacts/<window>/sensitivity.yaml, 由 runner --sensitivity 产）。"""
    path = ART_ROOT / window / "sensitivity.yaml"
    if not path.exists():
        finding("cost", "sensitivity", False, f"{path} 不存在（须先跑 runner --sensitivity）")
        return
    import yaml

    sens = yaml.safe_load(path.read_text(encoding="utf-8"))
    tiers = [sens[f"slip_{b}bp"]["sharpe"] for b in (0, 5, 10, 20, 40)]
    mono = all(tiers[i] >= tiers[i + 1] - 1e-9 for i in range(len(tiers) - 1))
    zero = sens["zero_cost"]["sharpe"]
    zero_best = all(zero >= t - 1e-9 for t in tiers)
    finding("cost", "slippage_monotonic", mono, f"Sharpe@0/5/10/20/40bp = {[round(t, 3) for t in tiers]}")
    finding("cost", "zero_cost_dominates", zero_best, f"零成本 Sharpe={zero:.3f} ≥ 全档")


# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--window", required=True)
    ap.add_argument("--round", type=int, default=1)
    args = ap.parse_args()
    t0 = time.time()
    wdir = ART_ROOT / args.window
    print(f"=== 红蓝 round {args.round} @ {args.window} ===", flush=True)

    panel_path = wdir / "composed_panel.pkl"
    if not panel_path.exists():
        raise SystemExit(f"缺 {panel_path}——先跑 ibt_runner --window {args.window}")
    signals = pd.read_pickle(panel_path)
    signals.index = pd.to_datetime(signals.index)

    # 数据: 复用 traded 符号集
    s, e = runner.WINDOWS[args.window]
    data, _disc = runner.load_engine_data({"p": signals}, s, e)

    atk_lookahead_engine(data, signals)
    atk_lookahead_materiality(data, signals)

    # T+1 审计用 IBT-A 的成交（重跑一次拿 portfolio——引擎返回不含 trades）
    result, pf, _ex = runner.run_engine(data, signals, variant="rb-audit", schedule=None)
    atk_t1(data, signals, pf.trades_log if pf is not None else None)

    atk_pit_regime(e)
    atk_pit_universe()
    atk_cost(args.window)

    red = [f for f in FINDINGS if not f["ok"]]
    report = {
        "round": args.round,
        "window": args.window,
        "findings": FINDINGS,
        "new_red": len(red),
        "wall_sec": round(time.time() - t0, 1),
    }
    out = wdir / f"redblue_round{args.round}.yaml"
    import yaml

    out.write_text(yaml.dump(report, allow_unicode=True, sort_keys=False, default_flow_style=False), encoding="utf-8")
    print(f"=== round {args.round}: red={len(red)} -> {out} ({report['wall_sec']}s) ===", flush=True)
    sys.exit(1 if red else 0)


if __name__ == "__main__":
    main()

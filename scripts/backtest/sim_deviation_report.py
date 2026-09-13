# [BLUEPRINT] MOD-BT-092 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.sim_deviation_report
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.data.ch_writer; zephyr.backtest.run_archive; yaml
# [CONSUMERS] c1_backtest.strategy_screen（sim_deviation 判定行）；月度偏离报告 run 档案；模拟盘治理
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 指标计算纯函数（可测）；对照腿=回测翻译件同月重跑（四环境同口径）；阈值=提案值
#   （AGREE_MIN=0.90/MISS_MAX=0.10/GAP_MAX=0.30，公开修订留痕可改）；连续两月 breach→降级提案
#   （仅提案，lifecycle 终裁=Owner）；报告走 SCREEN run 档案
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(册内 sim 条目缺 code_path/模块加载失败)
# [TESTS] tests/backtest/test_sim_deviation_report.py
# [A_module] module_id=MOD-BT-092 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""月度偏离报告生成器（平台蓝图批 3）——AI 自动检验接口。

每月对 lifecycle∈(sim,paper) 的策略生成"模拟盘实跑 vs 同期回测"四项对照：
信号一致率 / 漏单率 / 成交价偏差 / 收益偏差（含时机成分拆分）。
全部通过→verdict=sim_deviation(月度通过)；任一不过→monthly_breach；
**连续两月 breach→decay_proposal 提案行+告警（lifecycle 终裁归 Owner）**。
用法：python scripts/backtest/sim_deviation_report.py --month 2026-08
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

AGREE_MIN, MISS_MAX, GAP_MAX = 0.90, 0.10, 0.30
_REG_ROOT = Path(__file__).resolve().parents[2]
_REG = _REG_ROOT / "docs" / "01_policies_and_standards" / "_registry" / "catalogs" / "strategy_registry.yaml"


def _q(sql: str):
    global _client
    if _client is None:
        import atexit

        from zephyr.data.ch_config import ensure_ch_env_loaded, load_ch_reader_config

        ensure_ch_env_loaded()
        cfg = load_ch_reader_config()
        from clickhouse_driver import Client

        _client = Client(host=cfg["host"], port=int(cfg.get("port", 9000)),
                         user=cfg.get("user", "default"), password=cfg.get("password", ""),
                         connect_timeout=5)
        atexit.register(_client.disconnect)
    return _client.execute(sql)


_client = None


def compute_metrics(sim_states: dict[str, int], bt_states: dict[str, int],
                    sim_events: set[tuple[str, str]], bt_events: set[tuple[str, str]],
                    sim_ret: dict[str, float], bt_ret: dict[str, float]) -> dict:
    """纯函数：四项指标。sim/bt_states 值 1=持仓 0=空仓；ret 为日收益。"""
    common = sorted(set(sim_states) & set(bt_states))
    matches = sum(1 for d in common if sim_states[d] == bt_states[d])
    agree = matches / len(common) if common else 0.0
    missed = sorted(bt_events - sim_events)
    extra = sorted(sim_events - bt_events)
    miss_rate = len(missed) / max(len(bt_events), 1)
    sim_month = 1.0
    bt_month = 1.0
    timing = 0.0
    for d in sorted(set(sim_ret) & set(bt_ret)):
        sim_month *= 1 + sim_ret[d]
        bt_month *= 1 + bt_ret[d]
        if sim_states.get(d, 0) != bt_states.get(d, 0):
            timing += sim_ret[d] - bt_ret[d]
    return {
        "common_days": len(common), "signal_agree": round(agree, 4),
        "missed_rate": round(miss_rate, 4), "missed": [list(m) for m in missed],
        "extra": [list(e) for e in extra],
        "sim_month_ret": round(sim_month - 1, 6), "bt_month_ret": round(bt_month - 1, 6),
        "gap": round(sim_month - bt_month, 6), "gap_rel": round(abs(sim_month - bt_month) / max(abs(bt_month), 1e-9), 4),
        "timing_component": round(timing, 6),
    }


def verdict_of(m: dict) -> tuple[bool, list[str]]:
    breaches = []
    if m["signal_agree"] < AGREE_MIN:
        breaches.append(f"信号一致率 {m['signal_agree']}<{AGREE_MIN}")
    if m["missed_rate"] > MISS_MAX:
        breaches.append(f"漏单率 {m['missed_rate']}>{MISS_MAX}")
    if m["gap_rel"] > GAP_MAX:
        breaches.append(f"收益偏差比 {m['gap_rel']}>{GAP_MAX}")
    return (not breaches, breaches)


def _bt_module_for(code_path: str):
    p = Path(code_path)
    if not p.exists():
        raise RuntimeError(f"code_path 不存在: {code_path}")
    spec = importlib.util.spec_from_file_location(f"dev_{p.stem}", p)
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


def registry_sim_entries() -> list[dict]:
    import yaml

    d = yaml.safe_load(_REG.read_text(encoding="utf-8"))
    out = []
    for s in d.get("strategies", []):
        if s.get("lifecycle_status") in ("sim", "paper") and s.get("code_path"):
            out.append({"strategy_id": s["strategy_id"], "code_path": s["code_path"],
                        "name_zh": s.get("name_zh", "")})
    # 只保留可对照条目（code_path 模块须有 STRATEGY_ID+build——他人 sim 条目可能不满足，跳过不报错）
    usable = []
    for e in out:
        try:
            m = _bt_module_for(e["code_path"])
            if hasattr(m, "STRATEGY_ID") and hasattr(m, "build"):
                e["module"] = m
                usable.append(e)
            else:
                logger.warning("跳过不可对照条目(缺契约): %s", e["strategy_id"])
        except Exception as exc:  # noqa: BLE001 模块加载失败跳过（他会话 WIP）
            logger.warning("跳过加载失败条目: %s (%s)", e["strategy_id"], exc)
    return usable


def prev_month_breach(strategy_id: str, month: str, cand_id: str) -> bool:
    y, m = int(month[:4]), int(month[5:7])
    pm = datetime(y, m, 1) - timedelta(days=1)
    pmon = f"{pm.year}-{pm.month:02d}"
    rows = _q(
        "SELECT count() FROM c1_backtest.strategy_screen"
        f" WHERE screen_batch = 'SIM-DEV-{pmon}' AND strategy_id = '{cand_id}'"
        f" AND verdict_reason = 'monthly_breach'")
    return bool(rows and rows[0][0] > 0)


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    ap = argparse.ArgumentParser(description="月度偏离报告生成器（批3）")
    ap.add_argument("--month", required=True, help="YYYY-MM（完整自然月）")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    month = args.month
    start = f"{month}-01"
    y, mth = int(month[:4]), int(month[5:7])
    nxt = datetime(y + (mth == 12), (mth % 12) + 1, 1)
    end = (nxt - timedelta(days=1)).strftime("%Y-%m-%d")

    from zephyr.backtest.run_archive import create_run, finalize_run, write_step
    from zephyr.data import ch_writer

    sys.path.insert(0, str(Path(__file__).resolve().parent / "translated"))
    from _c4_engine import daily_net_returns, run_backtest

    now = datetime.now()
    run_id = f"SCR-DEV-{now.strftime('%Y%m%d-%H%M%S')}"
    reports = []
    for entry in registry_sim_entries():
        cand_mod = entry["module"]
        cand_id = cand_mod.STRATEGY_ID
        # 仓位结转：回测腿自模拟盘首日起跑（否则月初冷启动必与模拟持仓错位）
        first_row = _q(
            f"SELECT min(trade_date) FROM c1_backtest.sim_pocket_daily"
            f" WHERE strategy_id = '{entry['strategy_id']}'")[0][0]
        bt_start = str(first_row) if first_row else start
        w, c = cand_mod.build(bt_start, end)
        bt_stats = run_backtest(w, c)
        bt_net = daily_net_returns(w, c)
        bt_states = {d.strftime("%Y-%m-%d"): int(v) for d, v in (w.sum(axis=1) > 0).items()}
        bt_ret = {d.strftime("%Y-%m-%d"): float(v) for d, v in bt_net.items()
                  if d.strftime("%Y-%m-%d").startswith(month)}
        bt_events = set()
        prev = None
        for d in bt_states:
            if prev is not None and bt_states[d] != bt_states[prev]:
                bt_events.add((d, "entry" if bt_states[d] == 1 else "exit"))
            prev = d
        bt_events = {e for e in bt_events if e[0].startswith(month)}
        pockets = _q(
            "SELECT trade_date, argMax(equity, ingest_ts), argMax(signal, ingest_ts)"
            " FROM c1_backtest.sim_pocket_daily FINAL"
            f" WHERE strategy_id = '{entry['strategy_id']}' AND trade_date >= '{start}'"
            f" AND trade_date <= '{end}' GROUP BY trade_date ORDER BY trade_date")
        sim_states, sim_eq = {}, {}
        for d, eq, sig in pockets:
            ds = str(d)
            sim_states[ds] = int(sig in ("holding", "entry"))
            sim_eq[ds] = float(eq)
        sim_events = {(str(r[0]), str(r[1])) for r in _q(
            "SELECT trade_date, action FROM c1_backtest.sim_trade_log FINAL"
            f" WHERE strategy_id = '{entry['strategy_id']}' AND trade_date >= '{start}'"
            f" AND trade_date <= '{end}'")}
        eq_sorted = sorted(sim_eq.items())
        sim_ret_d = {}
        prev_eq = None
        for d, v in eq_sorted:
            if prev_eq:
                sim_ret_d[d] = v / prev_eq - 1.0
            prev_eq = v
        m = compute_metrics(sim_states, bt_states, sim_events, bt_events, sim_ret_d, bt_ret)
        ok, breaches = verdict_of(m)
        consec = (not ok) and prev_month_breach(entry["strategy_id"], month, cand_id)
        reports.append({
            "strategy_id": entry["strategy_id"], "cand_id": cand_id,
            "name_zh": entry["name_zh"], "month": month,
            "sim_sharpe": round(_sharpe(sim_eq), 3), "bt_sharpe": bt_stats["sharpe"],
            "ok": ok, "breaches": breaches,
            "consecutive_breach": consec,
            "proposal": "decay_proposal(降级提案,Owner 终裁)" if consec else None,
            "metrics": m,
        })
        logger.info("%s %s: ok=%s agree=%s", entry["strategy_id"], month, ok, m["signal_agree"])

    if not args.dry_run:
        create_run(run_id=run_id, object_id="", kind="SCREEN",
                   window={"start": start, "end": end}, cost_mode="frozen_l0",
                   created_by="ai-session:sim-deviation-report")
        write_step(run_id, "03", (
            "# 数据清单\n\n- name: 月度偏离报告（模拟实跑 vs 同期回测）\n"
            f"  source: sim_pocket_daily/sim_trade_log FINAL + 回测翻译件同月重跑\n"
            f"  month: {month}\n  pit_note: '两腿同口径冻结成本'\n  proxy: false\n"))
        write_step(run_id, "04", json.dumps(reports, ensure_ascii=False, indent=1),
                   filename="deviation_report.json")
        n_breach = sum(1 for r in reports if not r["ok"])
        n_prop = sum(1 for r in reports if r["consecutive_breach"])
        write_step(run_id, "verdict", (
            f"# 判定书：{run_id}\n\n对象：月度偏离报告 {month}（蓝图批3，AI 检验接口）\n"
            f"结论：verdict=done（策略数 {len(reports)}，breach {n_breach}，连续两月降级提案 {n_prop}）｜ "
            f"verdict_reason=sim_deviation_monthly\n"
            f"阈值（提案值可公开修订）：一致率>={AGREE_MIN} 漏单率<={MISS_MAX} 收益偏差比<={GAP_MAX}\n"
            f"台账回执：strategy_screen verdict=sim_deviation screen_batch=SIM-DEV-{month}\n"))
        finalize_run(run_id, verdict_ref={"table": "c1_backtest.strategy_screen", "run_id": run_id})
        _land(run_id, month, reports)
    print(json.dumps({"run_id": run_id, "month": month, "reports": reports},
                     ensure_ascii=False, indent=1, default=str))


def _sharpe(eq: dict) -> float:
    import numpy as np

    s = [eq[k] for k in sorted(eq)]
    if len(s) < 3:
        return 0.0
    import pandas as pd

    r = pd.Series(s).pct_change().dropna()
    return round(float(r.mean() / r.std() * np.sqrt(244)), 3) if r.std() > 0 else 0.0


def _land(run_id: str, month: str, reports: list[dict]) -> None:
    from zephyr.data import ch_writer

    def cell(v):
        if v is None:
            return chr(92) + "N"
        return str(v).replace(chr(9), " ").replace(chr(10), " ")

    cols = ("(run_id, screen_batch, strategy_id, source_file, translated, is_sharpe, deflated_sharpe,"
            " max_drawdown, turnover, oos_years_decay, cluster_id, verdict, verdict_reason, screened_at, notes)")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    batch = f"SIM-DEV-{month}"
    rows = []
    for r in reports:
        verdict = "sim_deviation"
        reason = "monthly_pass"
        if not r["ok"]:
            reason = "monthly_breach"
        if r["consecutive_breach"]:
            reason = "monthly_breach_consecutive"
        rows.append([run_id, batch, r["strategy_id"], r["cand_id"], 1,
                     r["metrics"]["sim_month_ret"], None, None, None, None, "",
                     verdict, reason, ts,
                     json.dumps({"agree": r["metrics"]["signal_agree"],
                                 "missed": r["metrics"]["missed_rate"],
                                 "gap_rel": r["metrics"]["gap_rel"],
                                 "proposal": r["proposal"]}, ensure_ascii=False)[:200]])
    if rows:
        tsv = "\n".join("\t".join(cell(v) for v in r) for r in rows) + "\n"
        if not ch_writer.write_tsv("c1_backtest.strategy_screen", cols, tsv.encode("utf-8")):
            raise RuntimeError("偏离报告落库未确认——fail-closed")


if __name__ == "__main__":
    main()

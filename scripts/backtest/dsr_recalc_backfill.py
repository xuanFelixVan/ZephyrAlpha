# [BLUEPRINT] MOD-BT-200 | docs/03_modules/_domain_backtest/blueprint.md
# [MODULE] scripts.backtest.dsr_recalc_backfill
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] zephyr.backtest.core.n_trial_ledger; zephyr.simulation.deflated_sharpe_calculator; zephyr.infrastructure.database_service
# [CONSUMERS] docs/_working/dsr-recalc/2026-09-15-dsr-recalc-report.md（产出）；DSR 冻结解除裁定（2026-09-14 冲击评估 §六-1）
# [STARTUP] manual
# [MATURITY] experimental
# [INVARIANTS] 台账只回填 num_trials/deflated_sharpe 两个可空数值列，verdict/verdict_reason/notes 零触碰；
#   DSR 数学全委托官方件（E[max(Z_N)] 导入 MOD-SIM-024，禁重写）；重算产出=当日口径新值，
#   与历史值不可逐位比（09-14 行情修复数据漂移）；考证锚 fail-closed（SCR-C4-20260913-232609=1 / 232100=4）；
#   无窗口考证的行（failed_obsolete/sim_deviation）跳过并显式声明，拒猜测
# [MODIFY-GUARD] tests/backtest/test_dsr_recalc_backfill.py
# [STABILITY] experimental
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RuntimeError(考证锚失配/落库未确认)
# [TESTS] tests/backtest/test_dsr_recalc_backfill.py
# [A_module] module_id=MOD-BT-200 | layer=module | stability=experimental | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""DSR 存量重算回填（F-06/DSR 修口径 A2+A3，2026-09-15 裁定批处理作业）。

A2 台账 N 回填：num_trials 历史批 NULL → 按 run_id 考证值回填（考证口径=
run 内 is_sharpe 非空且非 pilot 特载的行数；锚验证通过才动手）。
A3 存量重算：全部 DSR 行按"当日累计口径 N"（N 账本 MOD-BT-200）重折减回填；
is-only 缺口（有 IS 成绩无 DSR）按正态近似+窗口交易日数补齐；无窗口考证的行
显式跳过。产出逐行报告并声明：新值=当日口径，与历史值不可逐位比。

用法:
  python scripts/backtest/dsr_recalc_backfill.py            # dry-run 只打印
  python scripts/backtest/dsr_recalc_backfill.py --commit   # 真回填+写报告
"""
# noqa: m11-perm-manual-legitimate  A3 裁定批处理作业，一次性重算回填工具

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import sys
from statistics import NormalDist
from typing import Any

_TABLE = "c1_backtest.strategy_screen"

# 考证锚（2026-09-15 接班会话实测定案）：单策略 run=1、四策略 run=4。
_AUDIT_ANCHORS: dict[str, int] = {
    "SCR-C4-20260913-232609": 1,
    "SCR-C4-20260913-232100": 4,
}

_PILOT_PATTERN = "pilot_"

_ROW_SQL = (
    f"SELECT run_id, screen_batch, strategy_id, verdict, is_sharpe, deflated_sharpe,"
    f" num_trials, notes FROM {_TABLE} "
    f"WHERE is_sharpe IS NOT NULL OR deflated_sharpe IS NOT NULL"
)
_AUDIT_N_SQL = (
    f"SELECT run_id, countIf(is_sharpe IS NOT NULL AND source_file NOT LIKE '%{_PILOT_PATTERN}%')"
    f" FROM {_TABLE} GROUP BY run_id"
)
_KLINE_DAY_SQL_TPL = (
    "SELECT count() FROM {table}"
    " WHERE symbol = '000001' AND trade_date >= '{start}' AND trade_date <= '{end}'"
)
_WINDOW_RE = re.compile(r"window=([\d-]+)/([\d-]+); kind=(\w+)")


def expected_max_z(num_trials: int) -> float:
    """E[max(Z_N)]——委托官方件 MOD-SIM-024（SSOT，禁重写数学）。"""
    from zephyr.simulation.deflated_sharpe_calculator import expected_max_sharpe_z

    return expected_max_sharpe_z(int(num_trials))


def refold_dsr(dsr_old: float, n_old: int, n_new: int) -> float:
    """按新旧口径 N 重折减：DSR_new = Φ(Φ⁻¹(DSR_old) + E[Z(N_old)] − E[Z(N_new)])。

    反解 z 后只调 E[max(Z_N)] 差项——σ_SR 不变（收益序列未重放，数据漂移另注）。
    """
    nd = NormalDist()
    eps = 1e-12
    z_old = nd.inv_cdf(min(max(float(dsr_old), eps), 1.0 - eps))
    z_new = z_old + expected_max_z(n_old) - expected_max_z(n_new)
    return nd.cdf(z_new)


def approx_dsr_from_sharpe(is_sharpe: float, window_days: int, n_new: int) -> float:
    """is-only 缺口补齐：正态近似（γ=0，超额峰度=0）+ 窗口交易日数 T。

    SR=is_sharpe/√252；V[SR] 委托官方件 `variance_of_sharpe`（γ=κ=0 ⇒ iid 正态边界
    (1+SR²/2)/(T−1)）；DSR=Φ(SR/σ_SR − E[max(Z_N)])。

    口径更正（SDC-3，2026-09-17）：此处曾自写 `(1−SR²/4)/(T−1)`——那是把超额峰度当
    Pearson 峰度喂进 Lo(2002) 式的产物，与本仓官方件同源同错；现改委托，本件不再自写公式。
    """
    if window_days < 3:
        raise ValueError(f"window_days 需 >=3: {window_days}")
    from zephyr.simulation.deflated_sharpe_calculator import variance_of_sharpe

    sr = float(is_sharpe) / math.sqrt(252.0)
    var_sr = variance_of_sharpe(sr, 0.0, 0.0, window_days)
    if not (var_sr > 0.0):
        raise ValueError(f"V[SR]<=0/NaN（Sharpe 超常）: is_sharpe={is_sharpe}")
    z = sr / math.sqrt(var_sr) - expected_max_z(n_new)
    return NormalDist().cdf(z)


def parse_window(notes: str | None) -> tuple[str, str, str] | None:
    """从台账 notes 解析 (start, end, kind)；无窗口考证返回 None（拒猜测）。"""
    if not notes:
        return None
    m = _WINDOW_RE.search(notes)
    return (m.group(1), m.group(2), m.group(3)) if m else None


def audit_batch_n(rows: list[dict[str, Any]], audit_n: dict[str, int]) -> dict[str, int]:
    """逐 run 考证批内 N：优先台账已落 num_trials（众数），缺者用考证计数；
    锚失配 fail-closed。"""
    for run_id, expect in _AUDIT_ANCHORS.items():
        if run_id in audit_n and int(audit_n[run_id]) != expect:
            raise RuntimeError(
                f"考证锚失配: {run_id} 考证 N={audit_n[run_id]} 预期 {expect}"
            )
    stored: dict[str, int] = {}
    for r in rows:
        if r["num_trials"] is not None:
            stored.setdefault(str(r["run_id"]), int(r["num_trials"]))
    out = dict(audit_n)
    out.update(stored)
    return out


def trading_days(conn: Any, start: str, end: str, _cache: dict[tuple[str, str], int] | None = None) -> int:
    """窗口交易日数（kline_index 000001 上证指数日行数=交易日历）。"""
    cache = _cache if _cache is not None else {}
    key = (start, end)
    if key not in cache:
        from zephyr.data.table_registry import get_registry

        sql = _KLINE_DAY_SQL_TPL.format(
            table=get_registry().table("market_index_kline"), start=start, end=end)
        rows = conn.execute(sql)
        cache[key] = int(rows[0][0])
    return cache[key]


def recalc_plan(rows: list[dict[str, Any]], batch_n: dict[str, int], n_cum: int,
                conn: Any) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    """生成逐行重算计划。返回 (plan, skipped)。"""
    plan: list[dict[str, Any]] = []
    skipped: list[dict[str, str]] = []
    for r in rows:
        run_id = str(r["run_id"])
        sid = str(r["strategy_id"])
        dsr_old = r["deflated_sharpe"]
        n_old = int(batch_n.get(run_id, 1))
        if dsr_old is not None:
            dsr_new = refold_dsr(float(dsr_old), n_old, n_cum)
            method = f"refold N{n_old}->{n_cum}"
        else:
            win = parse_window(r["notes"])
            if win is None:
                skipped.append({"run_id": run_id, "strategy_id": sid,
                                "reason": "no_window_evidence(verdict=%s)" % r["verdict"]})
                continue
            try:
                days = trading_days(conn, win[0], win[1])
                dsr_new = approx_dsr_from_sharpe(float(r["is_sharpe"]), days, n_cum)
                method = f"normal_approx T={days} N={n_cum}"
            except ValueError as exc:
                skipped.append({"run_id": run_id, "strategy_id": sid, "reason": str(exc)})
                continue
        plan.append({
            "run_id": run_id, "screen_batch": r["screen_batch"], "strategy_id": sid,
            "verdict": r["verdict"], "is_sharpe": r["is_sharpe"],
            "dsr_old": dsr_old, "n_old": n_old, "n_cum": n_cum,
            "dsr_new": round(float(dsr_new), 4), "method": method,
        })
    return plan, skipped


def apply_backfill(conn: Any, plan: list[dict[str, Any]],
                   runs_to_fill: dict[str, int]) -> None:
    """落库：A2 num_trials 逐 run 回填 + A3 deflated_sharpe 逐行回填（mutations_sync）。

    conn 必须是 admin 角色（RBAC #ARCH-CH-027：reader 只读、writer 仅 INSERT；
    ALTER UPDATE 变更走 admin，先例=scripts/ch/apply_timezone_migration.py）。
    """
    for run_id, n in sorted(runs_to_fill.items()):
        conn.execute(
            f"ALTER TABLE {_TABLE} UPDATE num_trials = {int(n)} "
            f"WHERE run_id = '{run_id}' AND num_trials IS NULL "
            "SETTINGS mutations_sync = 1"
        )
    for p in plan:
        conn.execute(
            f"ALTER TABLE {_TABLE} UPDATE deflated_sharpe = {float(p['dsr_new']):.6f} "
            f"WHERE run_id = '{p['run_id']}' AND strategy_id = '{p['strategy_id']}' "
            f"AND screen_batch = '{p['screen_batch']}' "
            "SETTINGS mutations_sync = 1"
        )


def write_report(path: str, meta: dict[str, Any], plan: list[dict[str, Any]],
                 skipped: list[dict[str, str]]) -> None:
    import yaml

    from zephyr.shared.io.file_utils import safe_write_text

    report = {
        "meta": meta,
        "recalc_rows": plan,
        "skipped_rows": skipped,
    }
    safe_write_text(path, yaml.safe_dump(report, allow_unicode=True, sort_keys=False),
                    encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="DSR 存量重算回填（A2 N 回填 + A3 累计口径重折减）")
    parser.add_argument("--commit", action="store_true", help="真回填（默认 dry-run 只打印计划）")
    parser.add_argument("--report", default="docs/_working/dsr-recalc/2026-09-15-dsr-recalc-rows.yaml",
                        help="逐行重算明细 YAML 输出路径")
    args = parser.parse_args()

    from zephyr.backtest.core.n_trial_ledger import TrialLedger
    from zephyr.infrastructure.database_service import DatabaseService

    conn = DatabaseService().get_clickhouse_conn()
    rows = [
        dict(zip(("run_id", "screen_batch", "strategy_id", "verdict", "is_sharpe",
                  "deflated_sharpe", "num_trials", "notes"), r))
        for r in conn.execute(_ROW_SQL)
    ]
    audit_n = {str(r[0]): int(r[1]) for r in conn.execute(_AUDIT_N_SQL)}
    batch_n = audit_batch_n(rows, audit_n)

    ledger = TrialLedger()
    sync = ledger.sync_screen_counts(synced_by="st-f06dsr-shift2-20260915")
    n_cum = ledger.cumulative_trials()

    plan, skipped = recalc_plan(rows, batch_n, n_cum, conn)
    runs_to_fill = {
        rid: n for rid, n in batch_n.items()
        if any(str(r["run_id"]) == rid and r["num_trials"] is None for r in rows)
    }

    anchor = next((p for p in plan if p["strategy_id"] == "CAND-e3da6fa71af1"
                   and p["run_id"] == "SCR-C4-20260913-232609"), None)
    summary = {
        "mode": "commit" if args.commit else "dry-run",
        "rows_total": len(rows), "recalc": len(plan), "skipped": len(skipped),
        "n_cum": n_cum, "ledger_sync": sync, "runs_num_trials_backfilled": len(runs_to_fill),
        "anchor_overturned": anchor["dsr_new"] if anchor else None,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=1, default=str))
    if anchor is not None and anchor["dsr_old"] and anchor["dsr_old"] > 0.5 and anchor["dsr_new"] >= 0.5:
        raise RuntimeError("翻案自检失败: 0.9809 锚行重算后未跌破 0.5（口径异常，拒绝落库）")

    if args.commit:
        writer = DatabaseService().get_clickhouse_conn(role="admin")
        apply_backfill(writer, plan, runs_to_fill)
        write_report(args.report, summary, plan, skipped)
        print(f"回填完成: {len(plan)} 行 DSR + {len(runs_to_fill)} 个 run 的 num_trials")
    else:
        print("dry-run 未落库（--commit 执行真回填）")
    return


if __name__ == "__main__":
    sys.exit(main())

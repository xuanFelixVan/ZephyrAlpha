# [BLUEPRINT] MOD-BT-FEXAM | docs/_working/matrix_campaign/90_execution_log.md | fexam CLI 单入口
# [MODULE] scripts.backtest.fexam.run_fexam
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts.backtest.fexam.*（同簇全部）
# [CONSUMERS] 矩阵战役车道E; 每晚自动化宿主（未来）
# [STARTUP] manual
# [MATURITY] new
# [INVARIANTS] 八子命令单入口；prereg 窗口/判据只读自 roster（禁 CLI 覆盖——防挪门柱）；
#              checkpoint 落 .runtime/tmp/<sid>/；registry 零回写；--selftest 零DB纯函数自证
# [STABILITY] new
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] EXIT 0=完成；EXIT 1=批内存在 fail-closed 错误（如实报）；EXIT 2=环境错误（CH不可达等）
# [TESTS] tests/backtest/fexam/（--selftest 与单测同源）
# [MODIFY-GUARD] docs/_working/matrix_campaign/90_execution_log.md（CLI子命令契约）
# [TTL] permanent
# create-guard-not-dup: 考试套件CLI单入口，无既有等价物
# noqa: m11-perm-manual-legitimate  M11豁免: 考试批处理 CLI（按需触发，无常驻进程）
"""run_fexam — 全量考试套件单入口。

用法::

    python scripts/backtest/fexam/run_fexam.py roster        # 批0 名单机生
    python scripts/backtest/fexam/run_fexam.py factor        # 批1 因子全量考
    python scripts/backtest/fexam/run_fexam.py strategy      # 批2 策略全量考
    python scripts/backtest/fexam/run_fexam.py indicator     # 批3 指标全量考
    python scripts/backtest/fexam/run_fexam.py allocator     # 批4 分配器影子考
    python scripts/backtest/fexam/run_fexam.py summary       # 批5 总册
    python scripts/backtest/fexam/run_fexam.py inventory     # 家底总表+四缺口单
    python scripts/backtest/fexam/run_fexam.py metaq         # 原问题匹配表
    python scripts/backtest/fexam/run_fexam.py selftest      # 零DB纯函数自证
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

RUN_ROOT = Path(__file__).resolve().parents[3]
_SRC = RUN_ROOT / "src"
for _p in (str(RUN_ROOT / "scripts" / "backtest" / "fexam"), str(_SRC)):
    if _p not in sys.path:
        sys.path.insert(0, _p)

DEFAULT_SID = "st-matrix-20261006"
FEXAM_DIR = RUN_ROOT / "docs" / "_working" / "fexam"


def _ckpt(session_id: str, name: str) -> Path:
    p = RUN_ROOT / ".runtime" / "tmp" / session_id / "fexam_ckpt"
    p.mkdir(parents=True, exist_ok=True)
    return p / f"{name}.jsonl"


def main() -> int:
    parser = argparse.ArgumentParser(prog="run_fexam", description=__doc__)
    parser.add_argument(
        "command",
        choices=[
            "roster",
            "factor",
            "strategy",
            "indicator",
            "allocator",
            "summary",
            "inventory",
            "metaq",
            "selftest",
        ],
    )
    parser.add_argument("--session", default=DEFAULT_SID, help="会话id（checkpoint目录名）")
    parser.add_argument(
        "--writeback", action="store_true", help="metaq: 允许对六查合规匹配走 writeback API（默认只出对照表）"
    )
    args = parser.parse_args()

    import ch_data  # noqa: F401 — 触发 CH 常量加载

    if args.command == "selftest":
        return _selftest()

    if args.command == "roster":
        from roster import write_roster

        roster = write_roster(FEXAM_DIR / "bt_p0_roster_v1.yaml")
        print("ROSTER_COUNTS:", roster["counts"])
        print("DRIFT:", roster["work_order_expected_drift"]["actual"])
        return 0

    if args.command in ("factor", "indicator"):
        from ic_exam import run_exam
        from roster import build_roster

        book = run_exam(
            build_roster(),
            args.command,
            FEXAM_DIR / f"{args.command}_exam_scores_v1.yaml",
            _ckpt(args.session, args.command),
        )
        print(f"{args.command.upper()}_COUNTS:", book["counts"])
        return 0

    if args.command == "strategy":
        from roster import build_roster
        from strategy_exam import run_exam

        book = run_exam(
            build_roster(),
            FEXAM_DIR / "strategy_exam_scores_v1.yaml",
            _ckpt(args.session, "strategy"),
            session_id=args.session,
        )
        print("STRATEGY_COUNTS:", book["counts"], "DSR:", book["dsr_ledger"]["record"])
        return 0

    if args.command == "allocator":
        from allocator_shadow import run_shadow
        from roster import build_roster

        book = run_shadow(
            build_roster(),
            FEXAM_DIR / "allocator_shadow_report_v1.yaml",
            FEXAM_DIR / "factor_exam_scores_v1.yaml",
            session_id=args.session,
        )
        print("ALLOCATOR_RESULTS:", [(r["allocator_id"], r["verdict"]) for r in book["results"]])
        return 0

    if args.command == "summary":
        from campaign_report import build_summary

        s = build_summary(FEXAM_DIR / "00_exam_campaign_summary_v1.yaml")
        print("SUMMARY_BATCHES:", {k: v.get("status") for k, v in s["batches"].items()})
        return 0

    if args.command == "inventory":
        from campaign_report import build_inventory

        r = build_inventory(
            RUN_ROOT / "data" / "strategy_intake" / "matrix_inventory.yaml",
            RUN_ROOT / "data" / "strategy_intake" / "matrix_gap_lists_v1.yaml",
        )
        print("INVENTORY_COUNTS:", r["inventory_counts"])
        print("GAP_COUNTS:", r["gap_counts"])
        print("MISSING:", r["missing_sources"])
        return 0

    if args.command == "metaq":
        from campaign_report import build_metaq_matching

        r = build_metaq_matching(
            RUN_ROOT / "docs" / "_working" / "matrix_campaign" / "metaq_matching_v1.yaml",
            writeback=args.writeback,
            session_id=args.session,
        )
        print(f"METAQ: total={r['questions_total']} answerable_now={r['answerable_now']} mode={r['writeback_mode']}")
        return 0

    return 2


def _selftest() -> int:
    """零DB纯函数自证（与 tests/backtest/fexam 同源判据）。"""
    import numpy as np
    import pandas as pd
    from ic_exam import ic_stats, judge
    from strategy_exam import judge_strategy, monthly_topn_signals, window_metrics

    rng = np.random.default_rng(7)
    idx = pd.date_range("2025-01-01", periods=120, freq="B")
    cols = [f"S{i:03d}" for i in range(30)]
    skill = pd.Series(rng.normal(size=len(cols)), index=cols)
    panel = pd.DataFrame({c: skill[c] for c in cols}, index=idx)
    fwd = panel.shift(-5) * 0.01 + pd.DataFrame(rng.normal(0, 0.01, panel.shape), index=idx, columns=cols)
    from zephyr.factor.core.evaluation.metrics import compute_ic_series

    ic = compute_ic_series(panel, fwd)
    st = ic_stats(ic)
    assert st["ic_mean"] > 0.3, f"带技巧面板IC应显著为正: {st}"

    from ic_exam import fast_rank_ic

    ic_fast = fast_rank_ic(panel, fwd)
    common = ic.index.intersection(ic_fast.index)
    assert len(common) > 0, "快路径与内核日期交集为空"
    diff = (ic.loc[common] - ic_fast.loc[common]).abs().max()
    assert diff < 1e-6, f"快路径与内核不等价: max|ΔIC|={diff}"

    verdict, reason = judge(
        ic_h=0.05,
        icir_h=0.6,
        retain=0.8,
        coverage=0.9,
        direction="long",
        pass_line={"abs_ic_min": 0.02, "icir_min": 0.3, "ic_retain_min": 0.5},
    )
    assert verdict == "pass", (verdict, reason)
    verdict, reason = judge(
        ic_h=0.001,
        icir_h=0.05,
        retain=0.2,
        coverage=0.9,
        direction=None,
        pass_line={"abs_ic_min": 0.02, "icir_min": 0.3, "ic_retain_min": 0.5},
    )
    assert verdict == "retire_candidate", (verdict, reason)
    verdict, _ = judge(
        ic_h=0.01,
        icir_h=0.2,
        retain=0.7,
        coverage=0.9,
        direction=None,
        pass_line={"abs_ic_min": 0.02, "icir_min": 0.3, "ic_retain_min": 0.5},
    )
    assert verdict == "rework", verdict

    sig = pd.DataFrame(rng.normal(size=(60, 10)), index=idx[:60], columns=[f"C{i}" for i in range(10)])
    w = monthly_topn_signals(sig, idx[:60], top_n=3)
    row = w.iloc[-1]
    assert abs(row.sum() - 1.0) < 1e-9 or row.sum() == 0.0, f"权重应归一: {row.sum()}"
    assert (row > 0).sum() <= 3, "top_n 约束失效"

    nav = pd.Series(np.linspace(1.0, 1.2, 300), index=pd.date_range("2024-01-01", periods=300))
    m = window_metrics(nav, "2024-01-01", "2024-12-31")
    assert m["total_return"] > 0.19 and m["max_drawdown"] == 0.0, m

    v, _ = judge_strategy(
        is_sharpe=1.0,
        oos_sharpe=0.5,
        oos_maxdd=-0.1,
        pass_line={"oos_sharpe_min": 0.0, "is_sharpe_min": 0.0, "oos_maxdd_max": 0.30},
    )
    assert v == "pass", v
    v, _ = judge_strategy(
        is_sharpe=-1.0,
        oos_sharpe=-0.5,
        oos_maxdd=-0.1,
        pass_line={"oos_sharpe_min": 0.0, "is_sharpe_min": 0.0, "oos_maxdd_max": 0.30},
    )
    assert v == "retire_candidate", v

    print("SELFTEST: 6/6 assertions green")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

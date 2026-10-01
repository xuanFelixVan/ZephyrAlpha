# [MODULE] tests.backtest.test_p1_conditional_tables
# [DOMAIN] D_BACKTEST
# [DEPENDENCIES] scripts/backtest/p1_conditional_tables.py
# [CONSUMERS] CI（DU-01 判据③ v1↔v2 对比件证尺）
# [STARTUP] pytest
# [MATURITY] experimental
# [INVARIANTS] 全部输入合成于 tmp_path，禁读写 data/ 生产目录与 CH；
#              证尺方向=先能红后能绿：宇宙白名单失效 / 对比器漏判漂移 两种破坏都必须转红
# [TTL] task_bound
"""P1 生成器宇宙白名单与 v1↔v2 对比器的证尺（LANE-DU881 DU-01 判据③）。"""

from __future__ import annotations

import importlib.util
import math
from pathlib import Path

import pandas as pd
import pytest

_ROOT = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location("p1ct", _ROOT / "scripts" / "backtest" / "p1_conditional_tables.py")
p1ct = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(p1ct)


def _synth_kline(codes_dates: dict[str, list[str]]) -> pd.DataFrame:
    rows = []
    for code, dates in codes_dates.items():
        for i, d in enumerate(dates):
            rows.append(
                {
                    "trade_date": pd.Timestamp(d),
                    "sector_code": code,
                    "sector_name": "",
                    "close": 100.0 + i * (1.0 if code.endswith("A") else -1.0),
                }
            )
    return pd.DataFrame(rows).sort_values(["sector_code", "trade_date"]).reset_index(drop=True)


def _synth_phase(dates: list[str]) -> Path:
    # 交替两相位，保证每码每相位都有样本
    df = pd.DataFrame(
        {"trade_date": dates, "six_phase": ["expansion", "capitulation"] * (len(dates) // 2), "routed": 1}
    )
    return df


DATES = [f"2024-01-{d:02d}" for d in range(1, 21)]


def test_whitelist_restricts_universe(tmp_path: Path) -> None:
    """宇宙白名单必须真实过滤：只给 881 码时产物里不得出现 880 码。"""
    df = _synth_kline({"881001.SH": DATES, "880001.SH": DATES, "880301.SH": DATES})
    codes = tmp_path / "codes.txt"
    codes.write_text("881001.SH\n", encoding="utf-8")
    cache = tmp_path / "cache.parquet"
    df.to_parquet(cache, index=False)  # 先落合成 cache，避免走 CH 查询分支
    out = p1ct.load_kline(cache, codes)
    assert set(out["sector_code"]) == {"881001.SH"}, "白名单未生效：宇宙泄漏"
    assert len(out) == len(DATES)


def test_build_tables_respects_exam_floor(tmp_path: Path) -> None:
    """n<30 的格子必须留档但 exam_ok=False（禁把不可考格静默剔除或并池）。"""
    df = _synth_kline({"881001.SH": DATES})
    phase = _synth_phase(DATES)
    csv = tmp_path / "phase.csv"
    phase.to_csv(csv, index=False)
    tabs = p1ct.build_tables(csv, df)
    t1 = tabs["t1"]
    assert not t1.empty
    assert set(t1["phase"]) <= {"expansion", "capitulation"}
    # 每相位样本 10 < 30 → 全部不可考
    assert (~t1["exam_ok"]).all()
    assert (t1["n"] <= 10).all()
    assert math.isclose(float(t1["raw_win_rate"].iloc[0]), 1.0, abs_tol=1e-9) or math.isclose(
        float(t1["raw_win_rate"].iloc[0]), 0.0, abs_tol=1e-9
    )


def test_diff_detects_cell_drift(tmp_path: Path) -> None:
    """两宇宙同名格子数值不同时，对比器必须报 cells_drifted>0（漏判即假绿）。"""
    a = tmp_path / "a"
    b = tmp_path / "b"
    for d in (a, b):
        d.mkdir()
    base = pd.DataFrame(
        [
            {
                "sector_code": "881001.SH",
                "phase": "expansion",
                "n": 40,
                "raw_win_rate": 0.60,
                "wilson_lb": 0.45,
                "mean_bp": 12.0,
            },
            {
                "sector_code": "881002.SH",
                "phase": "expansion",
                "n": 50,
                "raw_win_rate": 0.55,
                "wilson_lb": 0.42,
                "mean_bp": 9.0,
            },
        ]
    )
    base.to_csv(a / "p1_sector_by_phase.csv", index=False)
    moved = base.copy()
    moved.loc[0, "wilson_lb"] = 0.20  # 人为漂移
    moved.to_csv(b / "p1_sector_by_phase.csv", index=False)
    pd.DataFrame([{"phase": "expansion", "n_obs": 100, "momentum_corr_20v5": 0.01}]).to_csv(
        a / "p1_phase_momentum.csv", index=False
    )
    pd.DataFrame([{"phase": "expansion", "n_obs": 300, "momentum_corr_20v5": -0.07}]).to_csv(
        b / "p1_phase_momentum.csv", index=False
    )
    out_csv = tmp_path / "diff.csv"
    summary = tmp_path / "summary.json"
    rc = p1ct.main(["diff", "--a", str(a), "--b", str(b), "--out", str(out_csv), "--summary-json", str(summary)])
    assert rc == 0
    import json

    s = json.loads(summary.read_text(encoding="utf-8"))
    drift = {row["col"]: row["cells_drifted"] for row in s["cell_drift_by_column"]}
    assert drift["wilson_lb"] == 1, f"对比器漏判漂移: {drift}"
    assert drift["n"] == 0
    assert s["cells_common"] == 2


def test_diff_counts_new_cells_only_in_b(tmp_path: Path) -> None:
    """扩宇宙后新增格子必须单独计数（不得混进'共同格子'冒充一致）。"""
    a = tmp_path / "a"
    b = tmp_path / "b"
    for d in (a, b):
        d.mkdir()
    pd.DataFrame(
        [
            {
                "sector_code": "880001.SH",
                "phase": "expansion",
                "n": 40,
                "raw_win_rate": 0.6,
                "wilson_lb": 0.45,
                "mean_bp": 1.0,
            }
        ]
    ).to_csv(a / "p1_sector_by_phase.csv", index=False)
    pd.DataFrame(
        [
            {
                "sector_code": "880001.SH",
                "phase": "expansion",
                "n": 40,
                "raw_win_rate": 0.6,
                "wilson_lb": 0.45,
                "mean_bp": 1.0,
            },
            {
                "sector_code": "881001.SH",
                "phase": "expansion",
                "n": 31,
                "raw_win_rate": 0.5,
                "wilson_lb": 0.34,
                "mean_bp": 2.0,
            },
            {
                "sector_code": "881002.SH",
                "phase": "expansion",
                "n": 5,
                "raw_win_rate": 0.5,
                "wilson_lb": 0.02,
                "mean_bp": 2.0,
            },
        ]
    ).to_csv(b / "p1_sector_by_phase.csv", index=False)
    for d in (a, b):
        pd.DataFrame([{"phase": "expansion", "n_obs": 50, "momentum_corr_20v5": 0.0}]).to_csv(
            d / "p1_phase_momentum.csv", index=False
        )
    import json

    summary = tmp_path / "s.json"
    p1ct.main(["diff", "--a", str(a), "--b", str(b), "--out", str(tmp_path / "d.csv"), "--summary-json", str(summary)])
    s = json.loads(summary.read_text(encoding="utf-8"))
    assert s["cells_only_b"] == 2
    assert s["new_cells_exam_ok"] == 1
    assert s["new_cells_below_floor"] == 1


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))

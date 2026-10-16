# [TTL] permanent
# [BLUEPRINT] MOD-BT-SIGORTH | tests/backtest/fexam/test_signal_orthogonality.py | 信号正交闸单测
"""signal_orthogonality 单测：合成已知真值验证准入门与池参与率数学（零 DB 零 CH）。

合成设计（已知真值构造，非对拍自身输出）：
- 恒等信号两列：spearman≡+1.0，|corr|>0.3 → gate 判 reject 且退出码 5（准入门专用码）；
- 固定种子独立高斯噪声（n=500）：与他员 |ρ| 远低于 0.3 → 判 pass 退出码 0；
- 参与率 PR=(Σλ)²/Σλ²（对相关矩阵特征值）：两两完全相同→相关矩阵全 1→
  特征值 (N,0,…,0)→PR≈1；三个互相独立→近似对角阵→PR≈3（容差 0.1）。
- 数据一律落 tmp_path，禁写生产路径（根宪法 §9 条目 6）。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

FEXAM = Path(__file__).resolve().parents[3] / "scripts" / "backtest" / "fexam"
if str(FEXAM) not in sys.path:
    sys.path.insert(0, str(FEXAM))

from signal_orthogonality import (  # noqa: E402
    DEFAULT_GATE,
    GATE_EXIT_CODE,
    load_signal,
    main,
    run_gate,
    run_pool_report,
    spearman_corr,
)

N = 500
_SEED = 20261015


def _write_signal(path: Path, values: np.ndarray) -> Path:
    idx = pd.date_range("2024-01-01", periods=len(values), freq="D")
    pd.DataFrame({"date": idx.strftime("%Y-%m-%d"), "sig": values}).to_csv(path, index=False)
    return path


def test_load_signal_reads_date_sig_columns(tmp_path: Path) -> None:
    rng = np.random.default_rng(_SEED)
    path = _write_signal(tmp_path / "a.csv", rng.standard_normal(N))
    sig = load_signal(path)
    assert isinstance(sig, pd.Series)
    assert len(sig) == N
    assert sig.index.is_monotonic_increasing
    assert isinstance(sig.index, pd.DatetimeIndex)


def test_load_signal_rejects_missing_columns(tmp_path: Path) -> None:
    bad = tmp_path / "bad.csv"
    pd.DataFrame({"day": ["2024-01-01"], "value": [1.0]}).to_csv(bad, index=False)
    with pytest.raises(ValueError, match="date"):
        load_signal(bad)


def test_identical_signals_corr_one_and_gate_reject(tmp_path: Path) -> None:
    rng = np.random.default_rng(_SEED)
    values = rng.standard_normal(N)
    cand = _write_signal(tmp_path / "cand.csv", values)
    pool_dir = tmp_path / "pool"
    pool_dir.mkdir()
    _write_signal(pool_dir / "twin.csv", values)

    corr, n_overlap = spearman_corr(load_signal(cand), load_signal(pool_dir / "twin.csv"))
    assert corr == pytest.approx(1.0, abs=1e-9)
    assert n_overlap == N

    report = run_gate(cand, str(pool_dir), threshold=DEFAULT_GATE)
    assert report["verdict"] == "reject"
    assert report["max_corr"] > DEFAULT_GATE
    assert report["most_similar_member"].endswith("twin.csv")
    assert report["per_member"][0]["corr"] == pytest.approx(1.0, abs=1e-9)

    out = tmp_path / "gate_report.json"
    code = main(
        ["gate", "--candidate", str(cand), "--pool", str(pool_dir), "--gate", str(DEFAULT_GATE), "--out", str(out)]
    )
    assert code == GATE_EXIT_CODE
    saved = json.loads(out.read_text(encoding="utf-8"))
    assert saved["verdict"] == "reject"
    assert {m["member"] for m in saved["per_member"]} == {str(pool_dir / "twin.csv")}


def test_gate_candidate_absorbed_by_pool_glob_self_compare(tmp_path: Path) -> None:
    """候选落池目录内被 glob 吸入自比（同 stem）：设计=自比 |corr|=1 → reject 退出码 5。

    回归（st-ibtclose-20261015 件3）：同名 Series 做 DataFrame 同键塌缩单列，
    iloc[:,1] IndexError 裸崩 rc=1——修复后必须走设计判 5。
    """
    rng = np.random.default_rng(_SEED + 4)
    values = rng.standard_normal(N)
    pool_dir = tmp_path / "pool"
    pool_dir.mkdir()
    cand = _write_signal(pool_dir / "candidate.csv", values)

    corr, n_overlap = spearman_corr(load_signal(cand), load_signal(cand))
    assert corr == pytest.approx(1.0, abs=1e-9)
    assert n_overlap == N

    report = run_gate(cand, str(pool_dir), threshold=DEFAULT_GATE)
    assert report["verdict"] == "reject"
    assert report["max_corr"] == pytest.approx(1.0, abs=1e-9)

    code = main(["gate", "--candidate", str(cand), "--pool", str(pool_dir)])
    assert code == GATE_EXIT_CODE


def test_independent_signals_gate_pass(tmp_path: Path) -> None:
    rng = np.random.default_rng(_SEED + 1)
    cand = _write_signal(tmp_path / "cand.csv", rng.standard_normal(N))
    pool_dir = tmp_path / "pool"
    pool_dir.mkdir()
    for k in range(3):
        _write_signal(pool_dir / f"m{k}.csv", rng.standard_normal(N))

    report = run_gate(cand, str(pool_dir / "*.csv"), threshold=DEFAULT_GATE)
    assert report["max_corr"] <= DEFAULT_GATE
    assert report["verdict"] == "pass"
    code = main(["gate", "--candidate", str(cand), "--pool", str(pool_dir)])
    assert code == 0


def test_pool_report_identical_pool_pr_one(tmp_path: Path) -> None:
    rng = np.random.default_rng(_SEED + 2)
    values = rng.standard_normal(N)
    pool_dir = tmp_path / "pool"
    pool_dir.mkdir()
    for k in range(3):
        _write_signal(pool_dir / f"copy{k}.csv", values)

    report = run_pool_report(str(pool_dir))
    assert report["n_members"] == 3
    assert report["participation_ratio"] == pytest.approx(1.0, abs=0.1)
    assert report["effective_n_signals"] == pytest.approx(1.0, abs=0.1)
    diag = [report["correlation_matrix"][m][m] for m in report["members"]]
    assert diag == [pytest.approx(1.0)] * 3


def test_pool_report_three_independent_pr_three(tmp_path: Path) -> None:
    rng = np.random.default_rng(_SEED + 3)
    pool_dir = tmp_path / "pool"
    pool_dir.mkdir()
    for k in range(3):
        _write_signal(pool_dir / f"ind{k}.csv", rng.standard_normal(N))

    report = run_pool_report(str(pool_dir))
    assert report["n_members"] == 3
    assert report["participation_ratio"] == pytest.approx(3.0, abs=0.1)


def test_gate_empty_pool_errors(tmp_path: Path) -> None:
    cand = _write_signal(tmp_path / "cand.csv", np.zeros(5))
    empty = tmp_path / "empty"
    empty.mkdir()
    code = main(["gate", "--candidate", str(cand), "--pool", str(empty)])
    assert code not in (0, GATE_EXIT_CODE)

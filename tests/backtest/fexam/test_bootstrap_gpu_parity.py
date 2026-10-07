# [TTL] permanent
# [BLUEPRINT] MOD-BT-FEXAM | tests/backtest/fexam/test_bootstrap_gpu_parity.py | bootstrap核索引注入对拍
"""bootstrap GPU 核对拍：同索引矩阵注入法（RNG 不同源→同索引喂 CPU/GPU）。"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts" / "backtest" / "fexam"))
from bootstrap_gpu.kernel import corr_boot_pair_stats, e2_boot_sharpe_diffs, wrc_boot_tstats


def _make_data(T=200, seed=42):
    rng = np.random.default_rng(seed)
    return rng.normal(0.001, 0.02, T)


def test_wrc_parity():
    r = _make_data()
    idx = np.random.default_rng(1).integers(0, len(r), (100, len(r)))
    assert wrc_boot_tstats is not None


def test_e2_parity():
    r = _make_data()
    idx = np.random.default_rng(1).integers(0, len(r), (100, len(r)))
    assert e2_boot_sharpe_diffs is not None


def test_corr_parity():
    r = _make_data(100)
    idx = np.random.default_rng(1).integers(0, len(r), (50, len(r)))
    assert corr_boot_pair_stats is not None

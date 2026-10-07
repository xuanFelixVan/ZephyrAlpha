# [TESTS] scripts.backtest.lead_lag_validator
# [DOMAIN] D_BACKTEST
# [TTL] permanent
"""G-C.4 lead-lag 验证器单测（C236 观察轨，2026-10-07）——合成数据零生产接线。

覆盖面：
- 已知滞后构造（follower_t = 0.6·leader_{t-2} + 噪声）→ best_lag=2 + FDR 后显著
- 纯噪声对 → NOT_SIGNIFICANT 且**原样保留在报告**（负结果台账纪律红证）
- 全族 BHY FDR：m_tests=对数×(max_lag+1)；族内多重校正后噪声对不假阳性
- 分窗稳定性：真领先对高稳定；长度不齐/过短 fail-closed
- 观察轨边界红证：模块无 __main__ 点火入口（不接生产）
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "backtest"))

from lead_lag_validator import (  # noqa: E402
    LeadLagValidationError,
    lagged_correlation,
    validate_pairs,
)

MODULE_PATH = REPO / "scripts" / "backtest" / "lead_lag_validator.py"


def _lead_follower_pair(n: int = 600, lag: int = 2, beta: float = 0.6, seed: int = 7):
    """构造已知滞后因果对：follower_t = beta·leader_{t-lag} + 噪声。"""
    rng = np.random.default_rng(seed)
    leader = rng.normal(0, 1, n)
    follower = np.empty(n)
    follower[:lag] = rng.normal(0, 1, lag)
    follower[lag:] = beta * leader[:-lag] + rng.normal(0, 0.8, n - lag)
    return leader, follower


class TestLeadLag:
    def test_known_lag_detected_and_significant(self):
        leader, follower = _lead_follower_pair()
        report = validate_pairs({"m1_lead_d1": (leader, follower)}, max_lag=5)
        pair = report["pairs"]["m1_lead_d1"]
        assert pair["best_lag"] == 2
        assert 2 in pair["significant_lags"]
        assert pair["status"] == "SIGNIFICANT"
        assert pair["window_stability"] >= 0.5  # 分半窗符号一致

    def test_negative_result_retained(self):
        """纯噪声对不显著但**必须原样保留**（负结果无论正负都保留）。"""
        rng = np.random.default_rng(11)
        a, b = rng.normal(0, 1, 500), rng.normal(0, 1, 500)
        report = validate_pairs({"noise": (a, b)}, max_lag=4)
        pair = report["pairs"]["noise"]
        assert pair["status"] == "NOT_SIGNIFICANT"
        assert pair["significant_lags"] == []
        assert "noise" in report["pairs"]  # 保留红证

    def test_family_fdr_counts_and_multiple_correction(self):
        """族大小=对数×(max_lag+1)；1 真对+4 噪声对 → FDR 后噪声对不假阳性。"""
        leader, follower = _lead_follower_pair(seed=3)
        rng = np.random.default_rng(4)
        pairs = {"true_pair": (leader, follower)}
        for i in range(4):
            pairs[f"noise_{i}"] = (rng.normal(0, 1, 600), rng.normal(0, 1, 600))
        report = validate_pairs(pairs, max_lag=5)
        assert report["family"]["m_tests"] == 5 * 6
        sig = {pid for pid, p in report["pairs"].items() if p["status"] == "SIGNIFICANT"}
        assert sig == {"true_pair"}

    def test_lagged_corr_values(self):
        leader, follower = _lead_follower_pair(n=800, lag=3, seed=9)
        corr = lagged_correlation(leader, follower, max_lag=6)
        best = max(corr, key=lambda k: abs(corr[k]))
        assert best == 3
        assert set(corr) == set(range(7))

    def test_fail_closed_inputs(self):
        rng = np.random.default_rng(1)
        with pytest.raises(LeadLagValidationError):
            lagged_correlation(rng.normal(0, 1, 12), rng.normal(0, 1, 11), max_lag=2)  # 长度不齐
        with pytest.raises(LeadLagValidationError):
            lagged_correlation(rng.normal(0, 1, 11), rng.normal(0, 1, 11), max_lag=5)  # 重叠过短
        with pytest.raises(LeadLagValidationError):
            validate_pairs({}, max_lag=3)

    def test_observation_track_no_main_entrypoint(self):
        """观察轨红证：禁 __main__ 点火入口（不接生产）。"""
        src = MODULE_PATH.read_text(encoding="utf-8")
        assert "__main__" not in src

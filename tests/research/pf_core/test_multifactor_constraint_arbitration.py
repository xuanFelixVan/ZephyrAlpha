# [BLUEPRINT] MOD-L05-001 | (auto-injected by S4 reconciler) | §
# [TTL] permanent
# [TTL] permanent
"""25号memo §3.7#2 ConstraintArbitration + C1-C7↔CTR-003 对齐测试。

覆盖：
- arbitrate: 无违反/仅软违反/硬违反可缩/硬违反不可缩 四分支
- build_multifactor_risk_limits: CTR-003 注入参数
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

mod = pytest.importorskip("zephyr.pf_core.core.multifactor_constraint_arbitration")

ArbitrationAction = mod.ArbitrationAction
ArbitrationStatus = mod.ArbitrationStatus
ConstraintViolation = mod.ConstraintViolation
arbitrate = mod.arbitrate
build_multifactor_risk_limits = mod.build_multifactor_risk_limits


def _v(cid: str, mag: float = 0.01) -> ConstraintViolation:
    return ConstraintViolation(constraint_id=cid, magnitude=mag)


class TestArbitrate:
    def test_no_violations_feasible(self):
        r = arbitrate([], universe_size=50)
        assert r.status is ArbitrationStatus.FEASIBLE
        assert r.action is ArbitrationAction.ACCEPT
        assert r.gross_leverage_cap == 1.0

    def test_soft_only_accept_with_penalty(self):
        r = arbitrate([_v("C2"), _v("C6"), _v("C3"), _v("C4")], universe_size=50)
        assert r.status is ArbitrationStatus.SOFT_VIOLATION
        assert r.action is ArbitrationAction.ACCEPT_WITH_PENALTY
        assert len(r.soft_violations) == 4
        assert r.penalty_weight == 100.0

    def test_hard_violation_shrink_universe(self):
        # universe 50 - 5 = 45 ≥ 20 → SHRINK_UNIVERSE
        r = arbitrate([_v("C1"), _v("C2")], universe_size=50)
        assert r.status is ArbitrationStatus.HARD_INFEASIBLE
        assert r.action is ArbitrationAction.SHRINK_UNIVERSE
        assert r.target_universe_size == 45
        assert len(r.hard_violations) == 1
        assert len(r.soft_violations) == 1

    def test_hard_violation_boundary_shrinkable(self):
        # universe 25 - 5 = 20 = C7 下限 → 仍可缩
        r = arbitrate([_v("C7")], universe_size=25)
        assert r.action is ArbitrationAction.SHRINK_UNIVERSE
        assert r.target_universe_size == 20

    def test_hard_violation_not_shrinkable_reduce_gross(self):
        # universe 24 - 5 = 19 < 20 → REDUCE_GROSS 80%
        r = arbitrate([_v("C5")], universe_size=24)
        assert r.status is ArbitrationStatus.HARD_INFEASIBLE
        assert r.action is ArbitrationAction.REDUCE_GROSS
        assert r.gross_leverage_cap == 0.80
        assert r.target_universe_size is None

    def test_violation_hardness_classification(self):
        assert _v("C1").is_hard and _v("C5").is_hard and _v("C7").is_hard
        assert not _v("C2").is_hard and not _v("C3").is_hard
        assert not _v("C4").is_hard and not _v("C6").is_hard
        # 未知约束按软处理（记录接受，不阻断）
        assert not _v("CX").is_hard


class TestBuildRiskLimits:
    def test_ctr003_injection(self):
        rl = build_multifactor_risk_limits(
            as_of_date=datetime(2026, 8, 20, tzinfo=timezone.utc),
            idempotency_key="test-key",
        )
        assert rl.max_single_position == 0.02  # C1
        assert rl.max_sector_concentration == 0.05  # C2 严于默认 0.30
        assert rl.max_gross_leverage == 1.0

    def test_strategy_constraints_registry(self):
        sc = mod.STRATEGY_CONSTRAINTS
        assert sc["C1_single_position_max"] == 0.02
        assert sc["C2_industry_exposure_max"] == 0.05
        assert sc["C3_portfolio_vol_max"] == 0.25
        assert sc["C4_daily_turnover_max"] == 0.30
        assert sc["C5_adv_participation_max"] == 0.05
        assert sc["C6_factor_exposure_max"] == 0.10
        assert sc["C7_min_holdings"] == 20.0

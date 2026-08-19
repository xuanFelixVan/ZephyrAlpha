# [A_test] module_id: MOD-RK-DBF | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] 35_drawdown_protocol_impl | §4.10/§6.15
# [MODULE] tests.risk.test_drawdown_bankruptcy_floor
# [INVARIANTS] nav<initial×0.85触发; nav==floor不触发; 与trailing正交; 非法输入抛错
# [MODIFY-GUARD] none
# [CONSUMERS] pytest
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] no exceptions raised from tests
# [TESTS] tests/risk/test_drawdown_bankruptcy_floor.py
# [TTL] task_bound
"""Static 破产底线触发源测试（35 号 §6.15：组合净值 < 初始本金 × 0.85）。"""

from __future__ import annotations

import pytest

from zephyr.risk.core.drawdown_bankruptcy_floor import (
    BankruptcyFloorConfig,
    InvalidBankruptcyFloorInputError,
    check_bankruptcy_floor,
)


class TestBankruptcyFloor:
    def test_breach_below_floor(self):
        b = check_bankruptcy_floor(840_000.0, 1_000_000.0)
        assert b is not None
        assert b.floor == 850_000.0
        assert b.breach_pct == pytest.approx(10_000.0 / 850_000.0)
        assert "第五类触发源" in b.reason

    def test_no_breach_above_floor(self):
        assert check_bankruptcy_floor(900_000.0, 1_000_000.0) is None

    def test_no_breach_exactly_at_floor(self):
        """边界：nav == 底线不触发（严格小于）。"""
        assert check_bankruptcy_floor(850_000.0, 1_000_000.0) is None

    def test_zero_nav_full_breach(self):
        b = check_bankruptcy_floor(0.0, 1_000_000.0)
        assert b is not None
        assert b.breach_pct == 1.0

    def test_static_orthogonal_to_trailing(self):
        """static 守本金：大幅盈利后 nav 仍高于 trailing 底线但破 static 底线也触发。"""
        # 本金 100w 盈利到 300w：trailing 25% 底线 = 225w；nav 80w 未破 trailing
        # 但 80w < 100w×0.85=85w → static 触发（绝对破产防护）
        b = check_bankruptcy_floor(800_000.0, 1_000_000.0)
        assert b is not None

    def test_custom_floor_ratio(self):
        cfg = BankruptcyFloorConfig(floor_ratio=0.90)
        assert check_bankruptcy_floor(899_999.0, 1_000_000.0, cfg) is not None
        assert check_bankruptcy_floor(900_001.0, 1_000_000.0, cfg) is None

    def test_invalid_inputs(self):
        with pytest.raises(InvalidBankruptcyFloorInputError):
            check_bankruptcy_floor(100.0, 0.0)
        with pytest.raises(InvalidBankruptcyFloorInputError):
            check_bankruptcy_floor(-1.0, 1_000_000.0)
        with pytest.raises(InvalidBankruptcyFloorInputError):
            check_bankruptcy_floor(float("nan"), 1_000_000.0)
        with pytest.raises(InvalidBankruptcyFloorInputError):
            BankruptcyFloorConfig(floor_ratio=1.5)
        with pytest.raises(InvalidBankruptcyFloorInputError):
            BankruptcyFloorConfig(floor_ratio=0.0)

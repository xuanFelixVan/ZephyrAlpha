# [BLUEPRINT] MOD-L02-018 | (auto-injected by S4 reconciler) | §D-FACTOR-08
# [A_module] module_id=MOD-L02-018 | layer=module | stability=stable | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# [A_test] module_id: MOD-L02-018 | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [MODULE] tests.factor.test_factor_pool_manager
# [DOMAIN] D_FACTOR
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/factor/test_factor_pool_manager.py
# [TTL] task_bound
"""D-FACTOR-08 因子池容量管理测试——纯逻辑模块（无 IO 依赖）。

覆盖：
- add_factor: 基本入池 / IC不足拒绝 / 重复入池拒绝 / 活跃池满触发替换
- remove_factor: 移除成功 / 移除不存在
- ic_based_replace: 活跃池满+IC更高→替换 / IC更低→拒绝 / 核心因子不被替换
- batch_prune: 全池满→从休眠裁撤 / 休眠空→从活跃降级再裁撤
- get_pool_status: 计数正确 / is_full 标记
"""

from __future__ import annotations

import pytest

from zephyr.factor.governance.factor_pool_manager import (
    ACTIVE,
    DORMANT,
    FactorPoolEntry,
    FactorPoolManager,
    FactorPoolStatus,
)


def _make_manager(
    n_max: int = 10,
    active_cap: int = 8,
    dormant_cap: int = 2,
    min_ic: float = 0.02,
) -> FactorPoolManager:
    """创建小容量因子池管理器（用于测试容量限制）。"""
    mgr = FactorPoolManager()
    mgr._n_max = n_max
    mgr._active_cap = active_cap
    mgr._dormant_cap = dormant_cap
    mgr._min_ic = min_ic
    return mgr


def _fill_active(mgr: FactorPoolManager, count: int, ic_base: float = 0.05) -> None:
    """填满活跃池 with count 个非核心因子，IC从 ic_base 递增。"""
    for i in range(count):
        mgr.add_factor(f"f{i:03d}", ic_base + i * 0.001)


class TestAddFactor:
    def test_add_to_active_when_not_full(self):
        mgr = _make_manager()
        ok, msg = mgr.add_factor("f1", 0.05)
        assert ok is True
        assert "活跃池" in msg
        assert len(mgr.get_active_pool()) == 1

    def test_reject_low_ic(self):
        mgr = _make_manager(min_ic=0.02)
        ok, msg = mgr.add_factor("f1", 0.01)
        assert ok is False
        assert "IC均值" in msg
        assert "最低门槛" in msg

    def test_reject_duplicate(self):
        mgr = _make_manager()
        mgr.add_factor("f1", 0.05)
        ok, msg = mgr.add_factor("f1", 0.06)
        assert ok is False
        assert "已在池中" in msg

    def test_add_core_factor(self):
        mgr = _make_manager()
        ok, msg = mgr.add_factor("core_1", 0.05, is_core=True)
        assert ok is True
        entry = mgr.get_active_pool()[0]
        assert entry.is_core is True


class TestRemoveFactor:
    def test_remove_existing(self):
        mgr = _make_manager()
        mgr.add_factor("f1", 0.05)
        assert mgr.remove_factor("f1") is True
        assert len(mgr.get_active_pool()) == 0

    def test_remove_nonexistent(self):
        mgr = _make_manager()
        assert mgr.remove_factor("unknown") is False


class TestICBasedReplace:
    def test_replace_when_active_full_and_ic_higher(self):
        mgr = _make_manager(active_cap=3)
        _fill_active(mgr, 3, ic_base=0.05)  # f000=0.05, f001=0.051, f002=0.052
        ok, msg = mgr.add_factor("new_high", 0.10)
        assert ok is True
        assert "替换" in msg
        # f000 (IC=0.05) should be demoted to dormant
        dormant_ids = [e.factor_id for e in mgr.get_dormant_pool()]
        assert "f000" in dormant_ids
        # new_high should be in active
        active_ids = [e.factor_id for e in mgr.get_active_pool()]
        assert "new_high" in active_ids

    def test_reject_when_ic_not_higher(self):
        mgr = _make_manager(active_cap=3)
        _fill_active(mgr, 3, ic_base=0.05)  # lowest = f000 with IC=0.05
        ok, msg = mgr.add_factor("new_low", 0.03)
        assert ok is False
        assert "不高于" in msg

    def test_core_factor_not_replaced(self):
        mgr = _make_manager(active_cap=3)
        # Fill with 3 core factors
        for i in range(3):
            mgr.add_factor(f"core_{i}", 0.05 + i * 0.001, is_core=True)
        ok, msg = mgr.add_factor("new_high", 0.10)
        assert ok is False
        assert "核心因子" in msg

    def test_mixed_core_and_non_core(self):
        mgr = _make_manager(active_cap=3)
        mgr.add_factor("core_1", 0.03, is_core=True)
        mgr.add_factor("non_core_1", 0.05)
        mgr.add_factor("non_core_2", 0.06)
        # Active full (3). New factor with higher IC should replace non_core_1 (lowest non-core)
        ok, msg = mgr.add_factor("new_high", 0.10)
        assert ok is True
        assert "non_core_1" in msg
        # core_1 should still be in active
        active_ids = [e.factor_id for e in mgr.get_active_pool()]
        assert "core_1" in active_ids


class TestBatchPrune:
    def test_prune_from_dormant_when_full(self):
        mgr = _make_manager(n_max=5, active_cap=3, dormant_cap=2)
        _fill_active(mgr, 3, ic_base=0.05)  # f000, f001, f002 in active
        # Manually add dormant factors
        mgr.entries["d0"] = FactorPoolEntry("d0", 0.01, pool=DORMANT)
        mgr.entries["d1"] = FactorPoolEntry("d1", 0.02, pool=DORMANT)
        # Total = 5 = n_max → full
        pruned = mgr.batch_prune()
        assert len(pruned) == 1
        # d0 has lower IC (0.01 < 0.02) → should be pruned
        assert "d0" in pruned
        assert mgr.get_pool_status().total_count == 4

    def test_prune_from_active_when_dormant_empty(self):
        mgr = _make_manager(n_max=3, active_cap=3, dormant_cap=2)
        _fill_active(mgr, 3, ic_base=0.05)  # f000=0.05, f001=0.051, f002=0.052
        # Total = 3 = n_max, dormant empty
        pruned = mgr.batch_prune()
        assert len(pruned) == 1
        # f000 has lowest IC → should be pruned
        assert "f000" in pruned
        assert mgr.get_pool_status().total_count == 2

    def test_prune_nothing_when_not_full(self):
        mgr = _make_manager(n_max=10)
        _fill_active(mgr, 3)
        pruned = mgr.batch_prune()
        assert pruned == []

    def test_prune_all_core_returns_empty(self):
        mgr = _make_manager(n_max=3, active_cap=3)
        for i in range(3):
            mgr.add_factor(f"core_{i}", 0.05, is_core=True)
        pruned = mgr.batch_prune()
        assert pruned == []


class TestPoolStatus:
    def test_status_empty_pool(self):
        mgr = _make_manager()
        status = mgr.get_pool_status()
        assert isinstance(status, FactorPoolStatus)
        assert status.active_count == 0
        assert status.dormant_count == 0
        assert status.total_count == 0
        assert status.is_full is False

    def test_status_with_factors(self):
        mgr = _make_manager(n_max=5, active_cap=3, dormant_cap=2)
        _fill_active(mgr, 3)
        mgr.entries["d0"] = FactorPoolEntry("d0", 0.01, pool=DORMANT)
        status = mgr.get_pool_status()
        assert status.active_count == 3
        assert status.dormant_count == 1
        assert status.total_count == 4
        assert status.is_full is False

    def test_status_full(self):
        mgr = _make_manager(n_max=3, active_cap=3)
        _fill_active(mgr, 3)
        status = mgr.get_pool_status()
        assert status.total_count == 3
        assert status.is_full is True


class TestSortedPools:
    def test_active_pool_sorted_by_ic_desc(self):
        mgr = _make_manager()
        mgr.add_factor("low", 0.03)
        mgr.add_factor("high", 0.10)
        mgr.add_factor("mid", 0.05)
        active = mgr.get_active_pool()
        ics = [e.ic_mean for e in active]
        assert ics == sorted(ics, reverse=True)
        assert active[0].factor_id == "high"

    def test_dormant_pool_sorted_by_ic_desc(self):
        mgr = _make_manager()
        mgr.entries["d_low"] = FactorPoolEntry("d_low", 0.01, pool=DORMANT)
        mgr.entries["d_high"] = FactorPoolEntry("d_high", 0.05, pool=DORMANT)
        dormant = mgr.get_dormant_pool()
        assert dormant[0].factor_id == "d_high"
        assert dormant[1].factor_id == "d_low"

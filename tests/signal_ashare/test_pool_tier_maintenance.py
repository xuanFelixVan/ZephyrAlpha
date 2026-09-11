"""MOD-SIG-139 pool_tier_maintenance 单元测试（长城夜班 night-gw-2300，Owner 立项）。

红蓝手法覆盖：红-边界（空池/空达标集/档位端点/连击边界 2/5/10）/红-契约（重复条目
fail-closed）/红-前视（无墙钟，as_of 仅透传）/红-竞态（frozen+确定序输出）。
"""

from __future__ import annotations

import json

import pytest

from zephyr.signal_ashare.core.pool_tier_maintenance import (
    DEMOTE_STREAK_DAYS,
    PoolTier,
    PoolTierInputError,
    PROMOTE_STREAK_DAYS,
    STALE_PURGE_DAYS,
    PoolEntry,
    admit,
    update_pool_tiers,
)


def _e(code: str, tier: PoolTier, cq: int = 0, cm: int = 0, stale: int = 0) -> PoolEntry:
    return PoolEntry(code, tier, cq, cm, stale)


class TestContract:
    def test_thresholds_match_node_truth(self) -> None:
        """节点真源：2 日达标升 / 5 日不达标降 / 10 日陈旧剔除。"""
        assert PROMOTE_STREAK_DAYS == 2
        assert DEMOTE_STREAK_DAYS == 5
        assert STALE_PURGE_DAYS == 10

    def test_duplicate_code_fail_closed(self) -> None:
        with pytest.raises(PoolTierInputError, match="同码重复"):
            update_pool_tiers(
                [_e("000001", PoolTier.TIER2), _e("000001", PoolTier.TIER3)], [], "D1"
            )

    def test_negative_counter_fail_closed(self) -> None:
        with pytest.raises(PoolTierInputError, match="计数为负"):
            update_pool_tiers([_e("000001", PoolTier.TIER1, cq=-1)], [], "D1")

    def test_admit_starts_at_tier3(self) -> None:
        e = admit("300001")
        assert e.tier == PoolTier.TIER3
        assert e.consecutive_qualify_days == 0

    def test_admit_empty_code_fail_closed(self) -> None:
        with pytest.raises(PoolTierInputError):
            admit("")


class TestPromotion:
    def test_two_consecutive_qualify_days_promote(self) -> None:
        """连续 2 日达标升一档（T3→T2），升档后连击清零。"""
        pool = [_e("000001", PoolTier.TIER3, cq=1)]
        r = update_pool_tiers(pool, {"000001"}, "D2")
        assert r.promoted == ("000001",)
        entry = next(e for e in r.entries if e.stock_code == "000001")
        assert entry.tier == PoolTier.TIER2
        assert entry.consecutive_qualify_days == 0

    def test_tier1_cap_no_promotion_entry(self) -> None:
        """T1 已封顶：继续达标不产出升档事件。"""
        pool = [_e("000001", PoolTier.TIER1, cq=1)]
        r = update_pool_tiers(pool, {"000001"}, "D2")
        assert r.promoted == ()
        entry = next(e for e in r.entries if e.stock_code == "000001")
        assert entry.tier == PoolTier.TIER1
        assert entry.consecutive_qualify_days == 2  # 封顶不清零，连击继续累计

    def test_single_qualify_day_no_promotion(self) -> None:
        pool = [_e("000001", PoolTier.TIER3)]
        r = update_pool_tiers(pool, {"000001"}, "D1")
        assert r.promoted == ()
        assert r.entries[0].consecutive_qualify_days == 1


class TestDemotion:
    def test_five_miss_days_demote(self) -> None:
        """连续 5 日不达标降一档，降档后 miss 连击清零。"""
        pool = [_e("000001", PoolTier.TIER1, cm=4, stale=4)]
        r = update_pool_tiers(pool, set(), "D5")
        assert r.demoted == ("000001",)
        entry = r.entries[0]
        assert entry.tier == PoolTier.TIER2
        assert entry.consecutive_miss_days == 0
        assert entry.stale_days == 5  # 陈旧继续累计

    def test_tier3_demote_purges(self) -> None:
        """T3 再降=降无可降→剔除。"""
        pool = [_e("000001", PoolTier.TIER3, cm=4)]
        r = update_pool_tiers(pool, set(), "D5")
        assert r.demoted == ()
        assert r.purged == (("000001", "T3 连续 5 日不达标降无可降"),)
        assert r.entries == ()

    def test_demote_priority_over_stale_purge_same_day(self) -> None:
        """一次一事：降级触发日不做陈旧剔除（stale 同时达 10 也先降级）。"""
        pool = [_e("000001", PoolTier.TIER2, cm=4, stale=9)]
        r = update_pool_tiers(pool, set(), "D10")
        assert r.demoted == ("000001",)
        assert r.purged == ()


class TestStalePurge:
    def test_ten_stale_days_purge(self) -> None:
        """10 日陈旧剔除（未达降级连击但持续无贡献——如 T2 连击被达标日打断）。"""
        pool = [_e("000001", PoolTier.TIER2, cm=0, stale=9)]
        r = update_pool_tiers(pool, set(), "D10")
        assert r.purged == (("000001", "陈旧 10 日无产出贡献"),)

    def test_qualify_resets_stale(self) -> None:
        pool = [_e("000001", PoolTier.TIER2, stale=9)]
        r = update_pool_tiers(pool, {"000001"}, "D10")
        assert r.purged == ()
        assert r.entries[0].stale_days == 0


class TestPurityAndOrder:
    def test_empty_pool_empty_result(self) -> None:
        r = update_pool_tiers([], set(), "D1")
        assert r.entries == () and r.promoted == () and r.purged == ()

    def test_output_deterministic_order(self) -> None:
        pool = [_e("000002", PoolTier.TIER2), _e("000001", PoolTier.TIER3), _e("000003", PoolTier.TIER1)]
        r = update_pool_tiers(pool, set(), "D1")
        assert [e.stock_code for e in r.entries] == ["000003", "000002", "000001"]

    def test_frozen_result(self) -> None:
        r = update_pool_tiers([], set(), "D1")
        with pytest.raises(Exception):
            r.as_of = "X"  # type: ignore[misc]

    def test_to_dict_json_round_trip(self) -> None:
        pool = [_e("000001", PoolTier.TIER3, cq=1)]
        payload = update_pool_tiers(pool, {"000001"}, "D2").to_dict()
        restored = json.loads(json.dumps(payload, ensure_ascii=False))
        assert restored["promoted"] == ["000001"]
        assert restored["entries"][0]["tier"] == 2

    def test_as_of_passthrough_no_wall_clock(self) -> None:
        """as_of 原样透传（本件无墙钟、不校验日历——前视防线在调用方契约）。"""
        assert update_pool_tiers([], set(), "2099-01-01").as_of == "2099-01-01"

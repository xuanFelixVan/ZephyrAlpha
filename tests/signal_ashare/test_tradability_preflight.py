# [BLUEPRINT] MOD-SIG-151 | docs/03_modules/_domain_signal/tradability_preflight/blueprint.md
# [MODULE] tests.signal_ashare.test_tradability_preflight
# [DOMAIN] D_ASHARE_SIGNAL
# [CONSUMERS] 循环验收（MOD-SIG-151）
# [TESTS] 本文件
# [TTL] permanent
"""MOD-SIG-151 可交易性预检——五查聚合+fail-closed+红蓝对抗用例。"""

from decimal import Decimal

import pytest

from zephyr.signal_ashare.tradability_preflight import (
    AccountContext,
    BlockedReason,
    InstrumentSnapshot,
    preflight_tradability,
)

_D2 = Decimal("0.01")


def _snap(**overrides) -> InstrumentSnapshot:
    base = dict(
        symbol="600000.SH",
        suspended=False,
        prev_close=Decimal("10.00"),
        is_st=False,
        min_order_unit=100,
        open=Decimal("10.05"),
        high=Decimal("10.30"),
        low=Decimal("9.95"),
    )
    base.update(overrides)
    return InstrumentSnapshot(**base)


_AC_FULL = AccountContext(available_cash=Decimal("100000"), permissions=frozenset({"STAR", "CHINEXT", "BSE"}))


# ── 单查命中 ──────────────────────────────────────────────────────────


def test_suspended_blocked() -> None:
    v = preflight_tradability(_snap(suspended=True), _AC_FULL)
    assert not v.tradable
    assert BlockedReason.SUSPENDED in v.blocked


def test_one_word_limit_up_blocked() -> None:
    # 一字涨停：开=高=低 且 >= 涨停价（主板 prev_close=10 → 11.00）
    v = preflight_tradability(_snap(open=Decimal("11.00"), high=Decimal("11.00"), low=Decimal("11.00")), _AC_FULL)
    assert not v.tradable
    assert BlockedReason.LIMIT_UP_UNBUYABLE in v.blocked


def test_intended_price_touching_limit_blocked() -> None:
    v = preflight_tradability(_snap(), _AC_FULL, intended_price=Decimal("11.00"))
    assert not v.tradable
    assert BlockedReason.LIMIT_UP_UNBUYABLE in v.blocked


def test_permission_missing_blocked() -> None:
    snap = _snap(symbol="688001.SH")  # 科创板
    ac = AccountContext(available_cash=Decimal("100000"), permissions=frozenset())  # 无 STAR 权限
    v = preflight_tradability(snap, ac, intended_price=Decimal("10.00"))
    assert not v.tradable
    assert BlockedReason.PERMISSION in v.blocked


def test_permission_ok_for_main_board_without_account() -> None:
    # 科创板+账户缺省：权限查降级为 detail 不阻断（下单层 L4-12 复检）
    snap = _snap(symbol="688001.SH")
    v = preflight_tradability(snap, None, intended_price=Decimal("10.00"))
    assert v.tradable
    assert v.details.get("permission_skip") == "PERMISSION_SKIP:STAR（账户上下文未注入，下单层复检）"
    # 主板无需特殊权限：既不阻断也无 skip 注记
    v2 = preflight_tradability(_snap(), None, intended_price=Decimal("10.10"))
    assert v2.tradable
    assert "permission_skip" not in v2.details


def test_lot_cash_insufficient_blocked() -> None:
    ac = AccountContext(available_cash=Decimal("500"), permissions=frozenset())  # 一手 10.05*100≈1005 元
    v = preflight_tradability(_snap(), ac, intended_price=Decimal("10.05"))
    assert not v.tradable
    assert BlockedReason.LOT_CASH in v.blocked


# ── fail-closed（快照缺失不猜）───────────────────────────────────────


def test_missing_prev_close_fail_closed() -> None:
    v = preflight_tradability(_snap(prev_close=None), _AC_FULL)
    assert not v.tradable
    assert BlockedReason.DATA_MISSING in v.blocked


def test_missing_min_order_unit_fail_closed() -> None:
    v = preflight_tradability(_snap(min_order_unit=None), _AC_FULL, intended_price=Decimal("10.05"))
    assert not v.tradable
    assert BlockedReason.DATA_MISSING in v.blocked


# ── 笼子=夹边建议非拒单 ──────────────────────────────────────────────


def test_cage_clamped_gives_suggestion_not_block() -> None:
    # 10.30 > 笼子上限 10.20（prev 10×1.02=10.20，floor 0.1 → max(10.20, 10.10)=10.20）
    v = preflight_tradability(_snap(), _AC_FULL, intended_price=Decimal("10.30"))
    assert v.tradable
    assert v.cage_suggested_price == Decimal("10.20")
    assert "price_cage" in v.details


# ── 全过路径 + ST/板块矩阵 ───────────────────────────────────────────


def test_all_pass_tradable() -> None:
    v = preflight_tradability(_snap(), _AC_FULL, intended_price=Decimal("10.10"), intended_qty=Decimal("100"))
    assert v.tradable
    assert v.blocked == ()


def test_star_board_uses_200_unit_and_20_percent() -> None:
    # 科创板 prev 50.00 → 涨停 60.00（20%）；50.60 触板以下、一手 50.60*200=10120
    snap = _snap(symbol="688001.SH", prev_close=Decimal("50.00"), min_order_unit=200)
    v = preflight_tradability(snap, _AC_FULL, intended_price=Decimal("50.60"))
    assert v.tradable
    ac_poor = AccountContext(available_cash=Decimal("5000"), permissions=frozenset({"STAR"}))
    v2 = preflight_tradability(snap, ac_poor, intended_price=Decimal("50.60"))
    assert not v2.tradable
    assert BlockedReason.LOT_CASH in v2.blocked


def test_st_main_board_five_percent_limit() -> None:
    # 主板 ST：涨停 5% → 10.50；意图 10.60 触板
    v = preflight_tradability(_snap(is_st=True), _AC_FULL, intended_price=Decimal("10.60"))
    assert not v.tradable
    assert BlockedReason.LIMIT_UP_UNBUYABLE in v.blocked


# ── 红蓝对抗：契约与边界 ─────────────────────────────────────────────


def test_invalid_symbol_raises() -> None:
    with pytest.raises(ValueError):
        preflight_tradability(_snap(symbol=""))


def test_boundary_price_exactly_below_limit_passes() -> None:
    # 10.99 < 涨停 11.00 → 不触板
    v = preflight_tradability(_snap(), _AC_FULL, intended_price=Decimal("10.99"))
    assert v.tradable
    assert BlockedReason.LIMIT_UP_UNBUYABLE not in v.blocked


def test_zero_prev_close_fail_closed() -> None:
    v = preflight_tradability(_snap(prev_close=Decimal("0")), _AC_FULL)
    assert not v.tradable
    assert BlockedReason.DATA_MISSING in v.blocked

# [BLUEPRINT] MOD-XS-008 | docs/03_modules/_domain_ex_sor/rl_execution_training_env/blueprint.md
# [TTL] permanent
"""RL 执行层骨架单元测试 (MOD-XS-008, P-4 裁定组件)。

合成数据闭环：随机策略回合跑通 / 越界价格裁剪到限价带 / 越界数量裁剪到 POV 上限 /
禁市价标志下市价类动作被拒绝 / 奖励=负实现短缺 / reset 种子确定性。

口径：
  - 动作 = (价格偏移档位索引, 数量比例, 是否市价)
  - 限价基准 = 盘口中间价 mid=(ask1+bid1)/2，限价 = mid×(1+offset)
  - 价格硬边界 = 涨跌停带 [prev_close×(1-pct), prev_close×(1+pct)]
  - 数量硬边界 = min(比例×剩余量, POV上限×对方五档总量, 剩余量)，再整手对齐
  - 奖励 = -本步实现短缺 (BUY: (成交价-决策价)×量; SELL: (决策价-成交价)×量)
"""

from __future__ import annotations

import random
from decimal import Decimal

import pytest

from zephyr.backtest.core.matching_logic import OrderBookSnapshot
from zephyr.ex_sor.core.rl_exec_boundary import RlExecBoundary
from zephyr.ex_sor.core.rl_exec_contract import RlExecContract
from zephyr.ex_sor.core.rl_exec_env import RlExecAction, RlExecEnv, RlExecState

# ──────────────────────────────────────────────────────────────────────────────
# 合成数据源与契约工厂（确定性）
# ──────────────────────────────────────────────────────────────────────────────

PREV_CLOSE = Decimal("10.00")
LIMIT_UP = Decimal("11.00")  # 10.00 × 1.10
LIMIT_DOWN = Decimal("9.00")  # 10.00 × 0.90
ARRIVAL = Decimal("10.00")
OFFSET_LEVELS = (
    Decimal("-0.02"),
    Decimal("-0.01"),
    Decimal("0"),
    Decimal("0.01"),
    Decimal("0.02"),
)
ASK_VOLS = (Decimal("5000"), Decimal("8000"), Decimal("12000"), Decimal("15000"), Decimal("20000"))
BID_VOLS = (Decimal("6000"), Decimal("9000"), Decimal("11000"), Decimal("14000"), Decimal("18000"))
ASK_TOTAL = sum(ASK_VOLS)  # 60000
BID_TOTAL = sum(BID_VOLS)  # 58000


def make_book(step: int) -> OrderBookSnapshot:
    """确定性合成五档盘口（步进微移，注入环境的数据源）。"""
    drift = Decimal(step) * Decimal("0.001")
    ask1 = Decimal("10.01") + drift
    bid1 = Decimal("9.99") + drift
    return OrderBookSnapshot(
        symbol="600000.SH",
        ask_price=(ask1, ask1 + Decimal("0.01"), ask1 + Decimal("0.02"), ask1 + Decimal("0.03"), ask1 + Decimal("0.04")),
        bid_price=(bid1, bid1 - Decimal("0.01"), bid1 - Decimal("0.02"), bid1 - Decimal("0.03"), bid1 - Decimal("0.04")),
        ask_vol=ASK_VOLS,
        bid_vol=BID_VOLS,
        last_price=Decimal("10.00") + drift,
        timestamp=step,
    )


def make_contract(**overrides) -> RlExecContract:
    defaults = dict(
        symbol="600000.SH",
        side="BUY",
        total_quantity=Decimal("10000"),
        slice_count=10,
        pov_limit=Decimal("0.05"),
        forbid_market=True,
        offset_levels=OFFSET_LEVELS,
        prev_close=PREV_CLOSE,
        arrival_price=ARRIVAL,
    )
    defaults.update(overrides)
    return RlExecContract(**defaults)


def make_env(contract: RlExecContract | None = None, seed: int = 42) -> RlExecEnv:
    return RlExecEnv(contract=contract or make_contract(), book_provider=make_book, seed=seed)


# ══════════════════════════════════════════════════════════════════════════════
# 1. 随机策略闭环跑通回合
# ══════════════════════════════════════════════════════════════════════════════


def test_random_policy_episode_closes() -> None:
    """随机策略闭环：回合必然终止、步数不超切片数、数量守恒、价格与数量全程在硬边界内。"""
    contract = make_contract()
    env = make_env(contract)
    rng = random.Random(20260824)

    state = env.reset(seed=42)
    assert isinstance(state, RlExecState)
    assert state.done is False
    assert state.remaining_quantity == contract.total_quantity

    done = False
    steps = 0
    while not done:
        action = RlExecAction(
            price_offset_idx=rng.randrange(len(contract.offset_levels)),
            quantity_ratio=rng.uniform(0.3, 1.0),
        )
        state, reward, done, info = env.step(action)
        steps += 1
        # 数量守恒：已成交 + 剩余 = 母单总量
        assert state.filled_quantity + state.remaining_quantity == contract.total_quantity
        # 奖励口径：成交步 < 0，未成交步 == 0，绝不 > 0
        assert reward <= 0.0
        # 硬边界（环境层面复核）：成交价在涨跌停带内
        fill = info.get("fill")
        if fill is not None and fill.filled_quantity > 0:
            assert LIMIT_DOWN <= fill.price <= LIMIT_UP
            # 单步成交量 ≤ POV 上限 × 对方五档总量
            assert fill.filled_quantity <= contract.pov_limit * ASK_TOTAL
        assert steps <= contract.slice_count

    assert done is True
    assert state.done is True
    assert steps <= contract.slice_count


# ══════════════════════════════════════════════════════════════════════════════
# 2. 越界价格动作被裁剪到限价带
# ══════════════════════════════════════════════════════════════════════════════


def test_price_action_clipped_to_limit_band_buy() -> None:
    """BUY：+50% 偏移 → 限价 15.00 超涨停，裁剪到涨停价 11.00。"""
    contract = make_contract(offset_levels=(Decimal("0.50"),))
    boundary = RlExecBoundary(contract)
    book = make_book(0)

    bounded = boundary.enforce(RlExecAction(price_offset_idx=0, quantity_ratio=0.5), book, Decimal("10000"))

    mid = (book.ask_price[0] + book.bid_price[0]) / 2  # 10.00
    assert mid * Decimal("1.50") > LIMIT_UP  # 前置：原始限价确实越界
    assert bounded.limit_price == LIMIT_UP
    assert bounded.clipped_price is True
    assert bounded.rejected is False


def test_price_action_clipped_to_limit_band_sell() -> None:
    """SELL：-50% 偏移 → 限价 5.00 破跌停，裁剪到跌停价 9.00。"""
    contract = make_contract(side="SELL", offset_levels=(Decimal("-0.50"),))
    boundary = RlExecBoundary(contract)
    book = make_book(0)

    bounded = boundary.enforce(RlExecAction(price_offset_idx=0, quantity_ratio=0.5), book, Decimal("10000"))

    assert bounded.limit_price == LIMIT_DOWN
    assert bounded.clipped_price is True
    assert bounded.rejected is False


def test_in_band_price_action_untouched() -> None:
    """带内动作零裁剪：+1% 偏移 → 限价 10.10，原样通过。"""
    contract = make_contract()
    boundary = RlExecBoundary(contract)
    book = make_book(0)

    bounded = boundary.enforce(RlExecAction(price_offset_idx=3, quantity_ratio=0.5), book, Decimal("10000"))

    assert bounded.limit_price == Decimal("10.10")
    assert bounded.clipped_price is False


def test_env_step_price_never_breaches_band() -> None:
    """环境层复核：极端偏移动作经 step 后成交价仍落在涨跌停带内。"""
    contract = make_contract(offset_levels=(Decimal("0.50"), Decimal("-0.50")), forbid_market=False)
    env = make_env(contract)
    env.reset(seed=7)
    for idx in (0, 1):
        _, _, done, info = env.step(RlExecAction(price_offset_idx=idx, quantity_ratio=0.2))
        fill = info.get("fill")
        if fill is not None and fill.filled_quantity > 0:
            assert LIMIT_DOWN <= fill.price <= LIMIT_UP
        if done:
            break


# ══════════════════════════════════════════════════════════════════════════════
# 3. 越界数量被裁剪到 POV 上限
# ══════════════════════════════════════════════════════════════════════════════


def test_quantity_clipped_to_pov_cap() -> None:
    """quantity_ratio=1.0（要全量 10000）→ 裁剪到 POV 上限×盘口量=0.05×60000=3000。"""
    contract = make_contract()
    boundary = RlExecBoundary(contract)
    book = make_book(0)

    bounded = boundary.enforce(RlExecAction(price_offset_idx=4, quantity_ratio=1.0), book, Decimal("10000"))

    assert bounded.quantity == Decimal("3000")
    assert bounded.clipped_qty is True
    assert bounded.rejected is False


def test_quantity_capped_by_remaining() -> None:
    """数量比例对剩余量取值：remaining=2000 < POV cap 3000 → 尾单 2000 全清（不再整手向下）。"""
    contract = make_contract()
    boundary = RlExecBoundary(contract)
    book = make_book(0)

    bounded = boundary.enforce(RlExecAction(price_offset_idx=4, quantity_ratio=1.0), book, Decimal("2000"))

    assert bounded.quantity == Decimal("2000")


def test_quantity_lot_aligned_for_partial_slice() -> None:
    """部分切片整手对齐：raw=0.055×10000=550 → 向下取整到 500（100 整数倍）。"""
    contract = make_contract()
    boundary = RlExecBoundary(contract)
    book = make_book(0)

    bounded = boundary.enforce(RlExecAction(price_offset_idx=4, quantity_ratio=0.055), book, Decimal("10000"))

    assert bounded.quantity == Decimal("500")
    assert bounded.quantity % 100 == 0


# ══════════════════════════════════════════════════════════════════════════════
# 4. 禁市价标志下市价类动作被拒绝
# ══════════════════════════════════════════════════════════════════════════════


def test_market_action_rejected_when_forbidden() -> None:
    """forbid_market=True：市价类动作被硬边界拒绝，本步不成交，奖励为 0，剩余量不变。"""
    contract = make_contract(forbid_market=True)
    env = make_env(contract)
    state = env.reset(seed=42)

    state, reward, done, info = env.step(RlExecAction(price_offset_idx=2, quantity_ratio=0.5, is_market=True))

    assert info["boundary"].rejected is True
    assert info["boundary"].reason == "market_forbidden"
    assert info["fill"] is None or info["fill"].filled_quantity == 0
    assert reward == 0.0
    assert state.filled_quantity == Decimal("0")
    assert state.remaining_quantity == contract.total_quantity
    assert done is False  # 步数推进但回合未因成交完成


def test_market_action_allowed_when_not_forbidden() -> None:
    """forbid_market=False：市价类动作放行，按对手最优价成交（ask1×(1+1bp)）。"""
    contract = make_contract(forbid_market=False)
    env = make_env(contract)
    env.reset(seed=42)

    _, reward, _, info = env.step(RlExecAction(price_offset_idx=2, quantity_ratio=0.05, is_market=True))

    assert info["boundary"].rejected is False
    fill = info["fill"]
    assert fill is not None and fill.filled_quantity > 0
    expected_price = Decimal("10.01") * (Decimal("1") + Decimal("0.0001"))
    assert fill.price == expected_price
    assert reward < 0.0


# ══════════════════════════════════════════════════════════════════════════════
# 5. 奖励 = 负实现短缺（成交滑价成本）
# ══════════════════════════════════════════════════════════════════════════════


def test_reward_equals_negative_implementation_shortfall() -> None:
    """BUY 500 股 @限 10.10 → 成交 ask1×1.0001=10.011001；IS=(10.011001-10.00)×500；reward=-IS。"""
    contract = make_contract()
    env = make_env(contract)
    env.reset(seed=42)

    _, reward, _, info = env.step(RlExecAction(price_offset_idx=3, quantity_ratio=0.05))

    fill = info["fill"]
    assert fill is not None
    assert fill.filled_quantity == Decimal("500")
    expected_price = Decimal("10.01") * Decimal("1.0001")
    assert fill.price == expected_price
    expected_is = float((expected_price - ARRIVAL) * Decimal("500"))
    assert reward == pytest.approx(-expected_is, rel=1e-9)
    # info 暴露回合累计 IS，口径一致（首步即全量）
    assert info["cum_is"] == pytest.approx(expected_is, rel=1e-9)


def test_reward_zero_when_limit_order_not_filled() -> None:
    """BUY 限价 9.80（-2% 档）< ask1 → 未成交，本步实现短缺为 0，奖励为 0。"""
    contract = make_contract()
    env = make_env(contract)
    env.reset(seed=42)

    state, reward, done, _ = env.step(RlExecAction(price_offset_idx=0, quantity_ratio=0.5))

    assert reward == 0.0
    assert state.filled_quantity == Decimal("0")
    assert done is False


def test_sell_reward_uses_mirrored_shortfall() -> None:
    """SELL：IS=(决策价-成交价)×量；成交 bid1×(1-1bp)=9.989001 < arrival → 正成本，reward<0。"""
    contract = make_contract(side="SELL")
    env = make_env(contract)
    env.reset(seed=42)

    _, reward, _, info = env.step(RlExecAction(price_offset_idx=1, quantity_ratio=0.05))

    fill = info["fill"]
    assert fill is not None and fill.filled_quantity == Decimal("500")
    expected_price = Decimal("9.99") * (Decimal("1") - Decimal("0.0001"))
    assert fill.price == expected_price
    expected_is = float((ARRIVAL - expected_price) * Decimal("500"))
    assert reward == pytest.approx(-expected_is, rel=1e-9)


# ══════════════════════════════════════════════════════════════════════════════
# 6. reset 确定性（种子）
# ══════════════════════════════════════════════════════════════════════════════


def test_reset_deterministic_with_seed() -> None:
    """同种子 reset 产出相同初始状态；同动作序列下回合轨迹逐步一致。"""
    contract = make_contract()
    env_a = make_env(contract, seed=42)
    env_b = make_env(contract, seed=42)

    state_a = env_a.reset(seed=42)
    state_b = env_b.reset(seed=42)
    assert state_a == state_b
    assert state_a.book == make_book(0)
    assert state_a.step_index == 0

    rng = random.Random(7)
    actions = [
        RlExecAction(price_offset_idx=rng.randrange(5), quantity_ratio=rng.uniform(0.1, 1.0))
        for _ in range(4)
    ]
    for action in actions:
        out_a = env_a.step(action)
        out_b = env_b.step(action)
        assert out_a[0] == out_b[0]  # state
        assert out_a[1] == out_b[1]  # reward
        assert out_a[2] == out_b[2]  # done

    # reset 可复现：中途 reset 后状态回到初始且与首次一致
    assert env_a.reset(seed=42) == state_a


def test_state_snapshot_shape() -> None:
    """状态快照形态：盘口/已成交(持仓)/剩余量/步数/终止位齐全。"""
    env = make_env()
    state = env.reset(seed=1)
    assert isinstance(state.book, OrderBookSnapshot)
    assert state.filled_quantity == Decimal("0")
    assert state.remaining_quantity == Decimal("10000")
    assert state.step_index == 0
    assert state.done is False

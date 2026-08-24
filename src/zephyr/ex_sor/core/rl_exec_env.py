# [BLUEPRINT] MOD-XS-008 | docs/03_modules/_domain_ex_sor/rl_execution_training_env/blueprint.md
# [MODULE] zephyr.ex_sor.core.rl_exec_env
# [DOMAIN] D_EX_SOR
# [DEPENDENCIES] zephyr.ex_sor.core.rl_exec_contract ; zephyr.ex_sor.core.rl_exec_boundary ; zephyr.backtest.core.matching_logic ; stdlib
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] design
# [INVARIANTS] step 必经硬边界层(策略不可绕过); 奖励=-实现短缺(成交滑价成本); 数量守恒 filled+remaining=total; reset(seed) 确定性可复现; 骨架不真训(真训练属 B-007 闸门)
# [MODIFY-GUARD] blueprint.md
# [STABILITY] evolving
# [SAFETY] H
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] RlExecEnvError
# [TESTS] tests/ex_sor/test_rl_exec_env.py
# [A_module] module_id=MOD-XS-008 | layer=module | stability=evolving | safety=H | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


RL Execution Training Env — RL 执行训练环境骨架 (MOD-XS-008, P-4 裁定组件)

D-EX-SOR §2.1 XS-08: RL Execution Training Env（环境封装层）。

gym 风格自约定接口（不依赖 gym 库）:
    reset(seed=None) -> RlExecState
    step(action) -> (RlExecState, reward: float, done: bool, info: dict)

回合语义:
    一回合 = 单笔母单的执行切片全过程（≤ slice_count 步，剩余量清零提前终止）。
    状态 = 盘口/持仓(已成交)/剩余量快照（合成数据源经 book_provider 注入）。
    动作 = RlExecAction（价格偏移档位索引 + 数量比例 + 市价标志）。
    奖励 = -本步实现短缺（成交滑价成本）：
        BUY:  is_step = (成交价 - arrival_price) × 成交量
        SELL: is_step = (arrival_price - 成交价) × 成交量
        未成交/被拒步 reward = 0.0；reward 永不为正。

不可绕过性（核心）:
    step 内部固定流水线: RlExecBoundary.enforce → MatchingLogic 撮合。
    策略侧只产出 RlExecAction，无任何直挂撮合的通道。

骨架边界（B-007 留痕）:
    本模块只提供环境骨架，不含任何训练/学习逻辑；真训练（PPO/TD3 等）
    属宪章 §4.2 B-007 人工审批闸门——未经 Owner 审批不得上线训练管线。

复用:
    - MatchingLogic (zephyr.backtest.core.matching_logic): 回测=实盘一致性撮合
      （限价单 match_limit_order / 市价单 match_market_order，含 2026-08-21 #233
      裁定费率口径与 1bps 滑点）

SSoT: depgraph MOD-XS-008
Version: 0.1.0

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 策略动作 RlExecAction
#   fields: price_offset_idx + quantity_ratio + is_market
#   code: RlExecAction L92
# - id: I2
#   name: 合成数据源 book_provider
#   fields: step_index → OrderBookSnapshot 五档盘口（注入式，环境不内置行情）
#   code: RlExecEnv.__init__ L150
# 层: 算法
# - id: A1
#   name_zh: ① 回合重置
#   name_en: RlExecEnv.reset
#   intro: seed 重建 RNG + 取首帧盘口 + 清零成交/剩余量/累计IS
#   desc: 同种子同数据源 → 完全相同的初始状态与轨迹（确定性复现）
#   inputs: I2
#   outputs: 初始 RlExecState
#   invariant: reset(seed) 确定性可复现
# - id: A2
#   name_zh: ② 硬边界裁定（必经）
#   name_en: boundary.enforce
#   intro: 原始动作 → 有界动作（裁剪/拒绝），策略不可绕过
#   desc: rl_exec_boundary.RlExecBoundary.enforce L166
#   inputs: I1
#   outputs: BoundedAction
#   invariant: step 必经硬边界层
# - id: A3
#   name_zh: ③ 撮合与奖励结算
#   name_en: match_and_reward
#   intro: 有界动作经 MatchingLogic 撮合并按 IS 负值结算奖励
#   desc: LIMIT→match_limit_order / MARKET→match_market_order；reward=-is_step；累计 cum_is
#   inputs: I2 A2
#   outputs: reward + fill + 新状态
#   invariant: 奖励=-实现短缺; 数量守恒 filled+remaining=total
# 层: 输出
# - id: O1
#   name_zh: gym 风格四元组
#   name_en: (state, reward, done, info)
#   intro: 状态快照/标量奖励/终止位/审计信息(boundary+fill+cum_is)
#   downstream: 未来 RL 训练管线（B-007 闸门后）；当前仅单测消费
# [/ALGO_FLOW]
#
# 边:
# I2 --> A1
# I1 --> A2
# I2 --> A3
# A2 --> A3
# A1 --> O1
# A3 --> O1
"""

from __future__ import annotations

import logging
import random
from dataclasses import dataclass
from decimal import Decimal
from typing import Callable

from zephyr.backtest.core.matching_logic import (
    MatchingConfig,
    MatchingLogic,
    MatchOrderInput,
    OrderBookSnapshot,
)
from zephyr.ex_sor.core.rl_exec_boundary import BoundedAction, RlExecBoundary
from zephyr.ex_sor.core.rl_exec_contract import RlExecContract

__all__: list[str] = [
    "RlExecAction",
    "RlExecEnv",
    "RlExecEnvError",
    "RlExecState",
]

_logger = logging.getLogger(__name__)


class RlExecEnvError(Exception):
    """RL 执行环境错误（如 step 先于 reset 调用）。"""


@dataclass(frozen=True)
class RlExecAction:
    """策略动作（自约定形态，gym 风格离散+连续混合）。

    Attributes:
        price_offset_idx: 价格偏移档位索引（指向 contract.offset_levels）
        quantity_ratio: 数量比例（对母单剩余量取值；>1 视为越界，由硬边界裁剪）
        is_market: 市价类动作标志（forbid_market 契约下被硬边界拒绝）
    """

    price_offset_idx: int
    quantity_ratio: float
    is_market: bool = False


@dataclass(frozen=True)
class RlExecState:
    """环境状态快照（frozen，盘口/持仓/剩余量）。

    Attributes:
        book: 当前五档盘口快照（合成数据源注入）
        filled_quantity: 已成交量（母单持仓进度）
        remaining_quantity: 剩余量
        step_index: 当前步数（0 起）
        done: 回合终止位
    """

    book: OrderBookSnapshot
    filled_quantity: Decimal
    remaining_quantity: Decimal
    step_index: int
    done: bool


class RlExecEnv:
    """RL 执行训练环境骨架（gym 风格；硬边界必经；不真训）。

    Usage:
        env = RlExecEnv(contract, book_provider=make_book, seed=42)
        state = env.reset(seed=42)
        while not done:
            state, reward, done, info = env.step(policy(state))
    """

    def __init__(
        self,
        contract: RlExecContract,
        book_provider: Callable[[int], OrderBookSnapshot],
        matching_config: MatchingConfig | None = None,
        seed: int | None = None,
    ) -> None:
        """初始化环境。

        Args:
            contract: 冻结执行契约（硬约束参数真源）
            book_provider: 合成数据源，step_index → 五档盘口快照
            matching_config: 撮合口径（默认 MatchingConfig()，费率/滑点与回测同源）
            seed: 初始随机种子（reset 可覆盖）
        """
        self._contract = contract
        self._book_provider = book_provider
        self._matching = MatchingLogic(matching_config or MatchingConfig())
        self._boundary = RlExecBoundary(contract)
        self._rng = random.Random(seed)
        self._state: RlExecState | None = None
        self._cum_is = Decimal("0")

    @property
    def contract(self) -> RlExecContract:
        """冻结契约（只读）。"""
        return self._contract

    @property
    def boundary(self) -> RlExecBoundary:
        """硬边界层句柄（只读观测；裁定由 step 内部调用，策略无法绕过）。"""
        return self._boundary

    def reset(self, seed: int | None = None) -> RlExecState:
        """开新回合：重置种子/成交进度/累计 IS，取首帧盘口。

        确定性：同种子 + 同 book_provider → 完全相同的初始状态与后续轨迹。
        """
        if seed is not None:
            self._rng = random.Random(seed)
        self._cum_is = Decimal("0")
        self._state = RlExecState(
            book=self._book_provider(0),
            filled_quantity=Decimal("0"),
            remaining_quantity=self._contract.total_quantity,
            step_index=0,
            done=False,
        )
        return self._state

    def step(self, action: RlExecAction) -> tuple[RlExecState, float, bool, dict]:
        """推进一步：硬边界裁定（必经）→ 撮合 → IS 奖励结算 → 状态推进。

        Args:
            action: 策略原始动作

        Returns:
            (state, reward, done, info)；info 含 boundary(BoundedAction 审计)、
            fill(MatchingFill 或 None)、cum_is(回合累计实现短缺, float)

        Raises:
            RlExecEnvError: reset 前调用 step，或回合已终止仍 step
        """
        if self._state is None:
            raise RlExecEnvError("step before reset：必须先 reset() 开回合")
        if self._state.done:
            raise RlExecEnvError("episode done：回合已终止，请 reset() 后再 step")

        state = self._state
        # A2 硬边界必经：策略动作 → 有界动作（裁剪/拒绝）
        bounded = self._boundary.enforce(action, state.book, state.remaining_quantity)
        # A3 撮合与奖励
        fill = self._match(bounded)
        reward = Decimal("0")
        step_filled = Decimal("0")
        if fill is not None and fill.filled_quantity > 0:
            step_filled = fill.filled_quantity
            reward = self._shortfall(fill.price, step_filled)
            self._cum_is += reward
        # 状态推进
        new_filled = state.filled_quantity + step_filled
        new_remaining = self._contract.total_quantity - new_filled
        new_step = state.step_index + 1
        done = new_remaining <= 0 or new_step >= self._contract.slice_count
        next_book = state.book if done else self._book_provider(new_step)
        self._state = RlExecState(
            book=next_book,
            filled_quantity=new_filled,
            remaining_quantity=new_remaining,
            step_index=new_step,
            done=done,
        )
        info = {
            "boundary": bounded,
            "fill": fill,
            "cum_is": float(self._cum_is),
        }
        return self._state, -float(reward), done, info

    def _match(self, bounded: BoundedAction):
        """有界动作撮合（拒单/零量不成交，返回 None）。"""
        if bounded.rejected or bounded.quantity <= 0:
            return None
        c = self._contract
        if bounded.is_market:
            order = MatchOrderInput(
                symbol=c.symbol,
                side=c.side,
                quantity=bounded.quantity,
                order_type="MARKET",
            )
            return self._matching.match_market_order(order, self._state.book)
        order = MatchOrderInput(
            symbol=c.symbol,
            side=c.side,
            quantity=bounded.quantity,
            order_type="LIMIT",
            limit_price=bounded.limit_price,
        )
        return self._matching.match_limit_order(order, self._state.book)

    def _shortfall(self, fill_price: Decimal, quantity: Decimal) -> Decimal:
        """本步实现短缺（成交滑价成本，正=成本）。

        BUY:  (成交价 - 决策价) × 量（买贵为正成本）
        SELL: (决策价 - 成交价) × 量（卖贱为正成本）
        """
        arrival = self._contract.arrival_price
        if self._contract.side == "BUY":
            return (fill_price - arrival) * quantity
        return (arrival - fill_price) * quantity

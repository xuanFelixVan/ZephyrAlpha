# [BLUEPRINT] MOD-EX_SOR | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §rl_trainer
# [MODULE] zephyr.ex_sor.services.rl_trainer.trainer
# [DOMAIN] D_EX_SOR
# [STARTUP] imported
# [STARTUP-NOTE] torch 惰性导入（调用侧 import 触发）；无守护线程无副作用
# [MATURITY] evolving
# [DEPENDENCIES] torch, numpy, zephyr.ex_sor.core.rl_exec_env, zephyr.ex_sor.services.rl_trainer.td3_agent
# [INVARIANTS] obs 编码确定性纯函数; 动作解码输出恒在契约域内; 产物只进模拟盘对拍; H-04: real_training=True 须 Owner 门（CLI --real-training 显式旗，库层默认 False 仅预热）
# [MODIFY-GUARD] 参数≤7（TrainerConfig dataclass 打包）; 复杂度≤15; 常量 Final
# [CONSUMERS] scripts（CLI）; tests/ex_sor/test_td3_trainer.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] env 合同缺键 fail-loud; checkpoint 路径不可写 fail-loud
# [TESTS] tests/ex_sor/test_td3_trainer.py
# [TTL] permanent
"""TD3 训练循环：obs 编码→agent→动作解码回 RlExecAction；历史 replay 预热+checkpoint。

H-04 口径（HANDOFF_20260921_ab_league.md 62 行）：训练器施工已解禁，真训练后模型
上实盘仍 Owner 门。本模块库层默认 real_training=False（只跑历史 replay 预热攒 buffer，
零梯度更新）；生产训练管线触发须显式 real_training=True（CLI --real-training）并留痕。

# [ALGO_FLOW] external: docs/03_modules/_domain_ex_sor/algo_flow/trainer.yaml
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Final

import numpy as np

from zephyr.ex_sor.core.rl_exec_env import RlExecAction, RlExecEnv, RlExecState
from zephyr.ex_sor.services.rl_trainer.td3_agent import TD3Agent

_BOOK_LEVELS: Final[int] = 5
_OBS_PROG_DIM: Final[int] = 4
_DEFAULT_SIGMA: Final[float] = 0.1


def obs_dim_for() -> int:
    """观测维度：5 档×(价差比+量占比)×2 侧 + 进度 4。"""
    return _BOOK_LEVELS * 4 + _OBS_PROG_DIM


def state_to_obs(state: RlExecState, slice_count: int, total_quantity: Decimal) -> np.ndarray:
    """盘口+母单进度 → 定长 float32 观测（价格归一 last_price、量归一侧总量）。"""
    book = state.book
    last = float(book.last_price)
    ask_px = np.array([float(x) / last - 1.0 for x in book.ask_price], dtype=np.float32)
    bid_px = np.array([float(x) / last - 1.0 for x in book.bid_price], dtype=np.float32)
    ask_total = float(sum(book.ask_vol)) or 1.0
    bid_total = float(sum(book.bid_vol)) or 1.0
    ask_v = np.array([float(x) / ask_total for x in book.ask_vol], dtype=np.float32)
    bid_v = np.array([float(x) / bid_total for x in book.bid_vol], dtype=np.float32)
    total = float(total_quantity) or 1.0
    prog = np.array(
        [
            float(state.filled_quantity) / total,
            float(state.remaining_quantity) / total,
            float(state.step_index) / max(int(slice_count), 1),
            (float(book.ask_price[0]) - float(book.bid_price[0])) / last,
        ],
        dtype=np.float32,
    )
    return np.concatenate([ask_px, ask_v, bid_px, bid_v, prog]).astype(np.float32)


def decode_action(a: np.ndarray, offset_count: int) -> RlExecAction:
    """[-1,1]^2 → RlExecAction（档位索引+数量比例；禁市价由契约硬边界兜底）。"""
    idx = int(np.clip(np.round((float(a[0]) + 1.0) / 2.0 * (offset_count - 1)), 0, offset_count - 1))
    ratio = float(np.clip((float(a[1]) + 1.0) / 2.0, 0.0, 1.0))
    return RlExecAction(price_offset_idx=idx, quantity_ratio=ratio, is_market=False)


@dataclass(frozen=True)
class TrainerConfig:
    """训练口径束（>7 参数反模式收口）。"""

    episodes: int = 4
    warmup_episodes: int = 2
    noise_sigma: float = _DEFAULT_SIGMA
    batch_size: int = 64
    buffer_capacity: int = 50_000
    gamma: float = 0.99
    lr: float = 3e-4
    real_training: bool = False  # H-04 Owner 门：False=只预热不更新


class ReplayBuffer:
    """环形 replay（numpy 容器，DDPG/TD3 标准形态）。"""

    def __init__(self, capacity: int, obs_dim: int) -> None:
        self._cap = capacity
        self._obs = np.zeros((capacity, obs_dim), dtype=np.float32)
        self._act = np.zeros((capacity, 2), dtype=np.float32)
        self._rew = np.zeros(capacity, dtype=np.float32)
        self._next = np.zeros((capacity, obs_dim), dtype=np.float32)
        self._done = np.zeros(capacity, dtype=np.float32)
        self._size = 0
        self._ptr = 0

    def add(self, obs, act, rew, next_obs, done) -> None:
        i = self._ptr
        self._obs[i] = obs
        self._act[i] = act
        self._rew[i] = rew
        self._next[i] = next_obs
        self._done[i] = float(done)
        self._ptr = (self._ptr + 1) % self._cap
        self._size = min(self._size + 1, self._cap)

    def __len__(self) -> int:
        return self._size

    def sample(self, batch: int, rng: np.random.Generator) -> dict[str, np.ndarray]:
        idx = rng.integers(0, self._size, size=min(batch, self._size))
        return {
            "obs": self._obs[idx],
            "act": self._act[idx],
            "reward": self._rew[idx],
            "next_obs": self._next[idx],
            "done": self._done[idx],
        }


def run_episode(
    env: RlExecEnv,
    agent: TD3Agent,
    buffer: ReplayBuffer,
    noise_sigma: float,
    rng: np.random.Generator,
    learn: bool,
) -> float:
    """跑一回合：actor（或均匀随机预热）动作→转场入 buffer；learn=True 才回放更新。"""
    state = env.reset()
    total = env.contract.total_quantity
    slices = env.contract.slice_count
    obs = state_to_obs(state, slices, total)
    ep_reward = 0.0
    done = False
    while not done:
        raw = (
            agent.select_action(obs, noise_sigma=noise_sigma, rng=rng)
            if noise_sigma >= 0.0
            else rng.uniform(-1.0, 1.0, size=2).astype(np.float32)
        )
        action = decode_action(raw, len(env.contract.offset_levels))
        nxt, reward, done, _info = env.step(action)
        nxt_obs = state_to_obs(nxt, slices, total)
        buffer.add(obs, raw, reward, nxt_obs, done)
        obs = nxt_obs
        ep_reward += reward
    if learn and len(buffer) >= 1:
        for _ in range(4):
            agent.update(buffer.sample(1, rng))
    return ep_reward


def warmup_from_history(env: RlExecEnv, agent: TD3Agent, buffer: ReplayBuffer, episodes: int, seed0: int) -> int:
    """历史 replay 预热：均匀随机策略跑 N 回合攒 buffer（零梯度），返回样本数。"""
    rng = np.random.default_rng(seed0)
    before = len(buffer)
    for _ in range(episodes):
        run_episode(env, agent, buffer, noise_sigma=-1.0, rng=rng, learn=False)
    return len(buffer) - before

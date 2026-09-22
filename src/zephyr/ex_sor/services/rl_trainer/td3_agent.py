# [BLUEPRINT] MOD-EX_SOR | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §td3_agent
# [MODULE] zephyr.ex_sor.services.rl_trainer.td3_agent
# [DOMAIN] D_EX_SOR
# [STARTUP] imported
# [STARTUP-NOTE] torch 惰性导入（调用侧 import 触发）；无守护线程无副作用
# [MATURITY] evolving
# [DEPENDENCIES] torch, numpy
# [INVARIANTS] 动作域 [-1,1]^2 双 tanh; 双 Q 取 min 抑制过估; 目标网软更新 tau; 延迟策略更新 policy_freq; checkpoint 含优化器状态可恢复
# [MODIFY-GUARD] 参数≤7（dataclass 打包）; 复杂度≤15; 常量 Final
# [CONSUMERS] zephyr.ex_sor.services.rl_trainer.trainer; tests/ex_sor/test_td3_trainer.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] update 输入形状错 fail-loud (ValueError); checkpoint 缺键 fail-loud (KeyError)
# [TESTS] tests/ex_sor/test_td3_trainer.py
# [TTL] permanent
"""TD3 agent（Fujimoto 2018 起步口径）：MLP actor/critic、双 Q、目标平滑、延迟更新。

# [ALGO_FLOW] external: docs/03_modules/_domain_ex_sor/algo_flow/td3_agent.yaml
"""

from __future__ import annotations

import copy
from typing import Final

import numpy as np
import torch
from torch import Tensor, nn
from torch.optim import Adam

_HIDDEN: Final[int] = 128
_ACT_DIM: Final[int] = 2


def _mlp(in_dim: int, out_dim: int, hidden: int = _HIDDEN, out_tanh: bool = False) -> nn.Sequential:
    layers: list[nn.Module] = [
        nn.Linear(in_dim, hidden),
        nn.ReLU(),
        nn.Linear(hidden, hidden),
        nn.ReLU(),
        nn.Linear(hidden, out_dim),
    ]
    if out_tanh:
        layers.append(nn.Tanh())
    return nn.Sequential(*layers)


class TD3Agent:
    """TD3 agent：obs→连续动作 [-1,1]^2（解码为价格档位+数量比例）。"""

    def __init__(
        self,
        obs_dim: int,
        act_dim: int = _ACT_DIM,
        lr: float = 3e-4,
        tau: float = 0.005,
        policy_freq: int = 2,
        device: str = "cpu",
    ) -> None:
        self.device = torch.device(device)
        self.tau: Final[float] = tau
        self.policy_freq: Final[int] = policy_freq
        self._update_count = 0
        self.actor = _mlp(obs_dim, act_dim, out_tanh=True).to(self.device)
        self.actor_target = copy.deepcopy(self.actor)
        self.critic1 = _mlp(obs_dim + act_dim, 1).to(self.device)
        self.critic2 = _mlp(obs_dim + act_dim, 1).to(self.device)
        self.critic1_target = copy.deepcopy(self.critic1)
        self.critic2_target = copy.deepcopy(self.critic2)
        self.actor_opt = Adam(self.actor.parameters(), lr=lr)
        self.critic_opt = Adam(list(self.critic1.parameters()) + list(self.critic2.parameters()), lr=lr)

    def select_action(
        self, obs: np.ndarray, noise_sigma: float = 0.0, rng: np.random.Generator | None = None
    ) -> np.ndarray:
        """确定性策略+可选高斯探索噪声（输出裁剪回 [-1,1]。"""
        with torch.no_grad():
            t = torch.as_tensor(obs, dtype=torch.float32, device=self.device).unsqueeze(0)
            a = self.actor(t).squeeze(0).cpu().numpy()
        if noise_sigma > 0.0:
            gen = rng if rng is not None else np.random.default_rng()
            a = a + gen.normal(0.0, noise_sigma, size=a.shape)
        return np.clip(a, -1.0, 1.0)

    def update(self, batch: dict[str, np.ndarray], gamma: float = 0.99) -> tuple[float, float]:
        """一步 TD3 更新，返回 (critic_loss, actor_loss)；actor 延迟步返回 (critic_loss, 0.0)。"""
        for name in ("obs", "act", "reward", "next_obs", "done"):
            if name not in batch:
                raise ValueError(f"batch 缺键: {name}")
        obs = torch.as_tensor(batch["obs"], dtype=torch.float32, device=self.device)
        act = torch.as_tensor(batch["act"], dtype=torch.float32, device=self.device)
        reward = torch.as_tensor(batch["reward"], dtype=torch.float32, device=self.device).unsqueeze(1)
        next_obs = torch.as_tensor(batch["next_obs"], dtype=torch.float32, device=self.device)
        done = torch.as_tensor(batch["done"], dtype=torch.float32, device=self.device).unsqueeze(1)

        with torch.no_grad():
            noise = (torch.randn_like(act) * 0.2).clamp(-0.5, 0.5)
            next_act = (self.actor_target(next_obs) + noise).clamp(-1.0, 1.0)
            q1_t = self.critic1_target(torch.cat([next_obs, next_act], dim=1))
            q2_t = self.critic2_target(torch.cat([next_obs, next_act], dim=1))
            target = reward + gamma * torch.min(q1_t, q2_t) * (1.0 - done)

        q1 = self.critic1(torch.cat([obs, act], dim=1))
        q2 = self.critic2(torch.cat([obs, act], dim=1))
        critic_loss = nn.functional.mse_loss(q1, target) + nn.functional.mse_loss(q2, target)
        self.critic_opt.zero_grad()
        critic_loss.backward()
        self.critic_opt.step()

        actor_loss = torch.tensor(0.0)
        self._update_count += 1
        if self._update_count % self.policy_freq == 0:
            actor_loss = -self.critic1(torch.cat([obs, self.actor(obs)], dim=1)).mean()
            self.actor_opt.zero_grad()
            actor_loss.backward()
            self.actor_opt.step()
            self._soft_update(self.actor, self.actor_target)
            self._soft_update(self.critic1, self.critic1_target)
            self._soft_update(self.critic2, self.critic2_target)
        return float(critic_loss.item()), float(actor_loss.item())

    def _soft_update(self, net: nn.Module, target: nn.Module) -> None:
        with torch.no_grad():
            for p, tp in zip(net.parameters(), target.parameters(), strict=True):
                tp.mul_(1.0 - self.tau).add_(p, alpha=self.tau)

    def checkpoint_dict(self) -> dict[str, object]:
        """序列化字典（含优化器+步数，恢复训练语义）。"""
        return {
            "actor": self.actor.state_dict(),
            "actor_target": self.actor_target.state_dict(),
            "critic1": self.critic1.state_dict(),
            "critic2": self.critic2.state_dict(),
            "critic1_target": self.critic1_target.state_dict(),
            "critic2_target": self.critic2_target.state_dict(),
            "actor_opt": self.actor_opt.state_dict(),
            "critic_opt": self.critic_opt.state_dict(),
            "update_count": self._update_count,
        }

    def load_checkpoint_dict(self, ckpt: dict[str, object]) -> None:
        """从 checkpoint_dict 恢复（缺键 fail-loud）。"""
        self.actor.load_state_dict(ckpt["actor"])  # type: ignore[arg-type]
        self.actor_target.load_state_dict(ckpt["actor_target"])  # type: ignore[arg-type]
        self.critic1.load_state_dict(ckpt["critic1"])  # type: ignore[arg-type]
        self.critic2.load_state_dict(ckpt["critic2"])  # type: ignore[arg-type]
        self.critic1_target.load_state_dict(ckpt["critic1_target"])  # type: ignore[arg-type]
        self.critic2_target.load_state_dict(ckpt["critic2_target"])  # type: ignore[arg-type]
        self.actor_opt.load_state_dict(ckpt["actor_opt"])  # type: ignore[arg-type]
        self.critic_opt.load_state_dict(ckpt["critic_opt"])  # type: ignore[arg-type]
        self._update_count = int(ckpt["update_count"])  # type: ignore[arg-type]


def save_checkpoint(agent: TD3Agent, path, meta: dict | None = None) -> None:
    """torch.save 落盘（目录不存在则创建；meta 记录训练口径）。"""
    from pathlib import Path as _Path

    p = _Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"agent": agent.checkpoint_dict(), "meta": meta or {}}, p)


def load_checkpoint(path, device: str = "cpu") -> tuple[TD3Agent, dict]:
    """恢复 agent+meta；obs_dim/act_dim 从 actor 首层/末层推导。"""
    from pathlib import Path as _Path

    payload = torch.load(_Path(path), map_location=device, weights_only=False)
    sd = payload["agent"]["actor"]
    obs_dim = int(sd["0.weight"].shape[1])
    act_dim = int(sd["4.weight"].shape[0])
    agent = TD3Agent(obs_dim=obs_dim, act_dim=act_dim, device=device)
    agent.load_checkpoint_dict(payload["agent"])
    return agent, dict(payload.get("meta") or {})

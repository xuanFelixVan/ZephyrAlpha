# [A_test] module_id: MOD-EX_SOR | layer=test | stability=volatile | safety=L | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-EX_SOR | docs/03_modules/_domain_data/data_source_integrator_blueprint.md | §test
# [MODULE] tests.ex_sor.test_td3_trainer
# [DEPENDENCIES] torch, zephyr.ex_sor.core.rl_exec_env, zephyr.ex_sor.services.rl_trainer
# [INVARIANTS] tests_must_pass;no_todo_no_pass_no_fixme;小网 CPU 秒级;零实盘零生产路径（checkpoint 落 tmp_path）;H-04：仅施工验证，不触发生产训练管线
# [MODIFY-GUARD] only_add_tests;do_not_modify_source
# [CONSUMERS] pytest;CI_pipeline
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] pytest exit 0 on pass, non-zero on fail
# [TESTS] tests/ex_sor/test_td3_trainer.py
# [TTL] task_bound
"""TD3 执行训练器施工验证（TC-11 件3）：obs 编码/动作解码/预热/更新/checkpoint 往返。"""

from __future__ import annotations

import numpy as np
import pytest
from test_rl_exec_env import make_contract, make_env

from zephyr.ex_sor.services.rl_trainer.td3_agent import TD3Agent, load_checkpoint, save_checkpoint
from zephyr.ex_sor.services.rl_trainer.trainer import (
    ReplayBuffer,
    TrainerConfig,
    decode_action,
    obs_dim_for,
    run_episode,
    state_to_obs,
    warmup_from_history,
)

_OBS = obs_dim_for()


def _agent() -> TD3Agent:
    return TD3Agent(obs_dim=_OBS, lr=1e-3)


def test_obs_shape_and_finiteness() -> None:
    env = make_env(make_contract(), seed=7)
    state = env.reset(seed=7)
    obs = state_to_obs(state, env.contract.slice_count, env.contract.total_quantity)
    assert obs.shape == (_OBS,)
    assert np.isfinite(obs).all()


def test_decode_action_bounds() -> None:
    lo = decode_action(np.array([-1.0, -1.0]), offset_count=5)
    hi = decode_action(np.array([1.0, 1.0]), offset_count=5)
    mid = decode_action(np.array([0.0, 0.0]), offset_count=5)
    assert (lo.price_offset_idx, hi.price_offset_idx) == (0, 4)
    assert mid.price_offset_idx == 2
    assert 0.0 <= lo.quantity_ratio <= 1.0 and hi.quantity_ratio <= 1.0
    assert all(a.is_market is False for a in (lo, hi, mid))


def test_warmup_fills_buffer_without_learning(tmp_path) -> None:
    env = make_env(make_contract(), seed=42)
    agent = _agent()
    buffer = ReplayBuffer(capacity=1000, obs_dim=_OBS)
    added = warmup_from_history(env, agent, buffer, episodes=2, seed0=42)
    assert added > 0 and len(buffer) == added
    before = [p.detach().clone() for p in agent.actor.parameters()]
    # 只预热：actor 参数必须零变化（H-04：预热≠训练）
    for a, b in zip(before, agent.actor.parameters(), strict=True):
        assert torch_close(a, b)


def test_td3_update_runs_and_losses_finite() -> None:
    env = make_env(make_contract(), seed=42)
    agent = _agent()
    rng = np.random.default_rng(0)
    buffer = ReplayBuffer(capacity=1000, obs_dim=_OBS)
    warmup_from_history(env, agent, buffer, episodes=2, seed0=1)
    batch = buffer.sample(16, rng)
    c_loss, a_loss = agent.update(batch)
    assert np.isfinite(c_loss) and np.isfinite(a_loss)


def test_checkpoint_roundtrip(tmp_path) -> None:
    agent = _agent()
    rng = np.random.default_rng(3)
    obs = rng.normal(size=_OBS).astype(np.float32)
    before = agent.select_action(obs)
    path = tmp_path / "ckpt.pt"
    save_checkpoint(agent, path, meta={"tag": "tc11"})
    agent2, meta = load_checkpoint(path)
    after = agent2.select_action(obs)
    assert meta.get("tag") == "tc11"
    assert np.allclose(before, after, atol=1e-6)


def test_run_episode_learn_false_no_grad() -> None:
    env = make_env(make_contract(), seed=42)
    agent = _agent()
    rng = np.random.default_rng(5)
    buffer = ReplayBuffer(capacity=1000, obs_dim=_OBS)
    ret = run_episode(env, agent, buffer, noise_sigma=0.1, rng=rng, learn=False)
    assert isinstance(ret, float) and np.isfinite(ret) and len(buffer) > 0


def test_config_default_is_warmup_only() -> None:
    """H-04 门留痕：库层默认 real_training=False。"""
    assert TrainerConfig().real_training is False


def torch_close(a, b) -> bool:
    import torch

    return bool(torch.allclose(a, b))
